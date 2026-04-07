# Kế hoạch cải tiến Grok2API

## Vấn đề hiện tại

### 1. Stream mặc định (CRITICAL)
- **Hiện tại**: `stream = false` trong config nhưng code vẫn ưu tiên `stream: true`
- **Vấn đề**: Client không hỗ trợ SSE bị lỗi, phải set cứng `stream: false` mỗi request
- **Giải pháp**: Tôn trọng config mặc định, không force stream

### 2. UI Junk - Rác XML/JSON (HIGH)
- **Hiện tại**: 
  - Thẻ `<think>`, `<xai:tool_usage_card>` hiện thô
  - JSON logs công cụ (`code_execution`, `browse_page`) xuất hiện trong chat
- **Vấn đề**: Giao diện rối mắt, Pi không nhận diện được câu trả lời thật
- **Giải pháp**: 
  - ✅ Đã có `filter_tags` trong config
  - ✅ Code đã xử lý `_filter_token()` và `_filter_content()`
  - Cần kiểm tra xem có hoạt động đúng không

### 3. Reasoning Content (MEDIUM)
- **Hiện tại**: Thinking nhét chung vào `content`
- **Vấn đề**: Giao diện hiện đại không hiển thị đúng phần "Thinking"
- **Giải pháp**: 
  - ✅ Code đã tách `reasoning_content` riêng
  - ✅ Stream processor đã xử lý `reasoning_content`
  - Cần verify hoạt động

### 4. Tool Calling - Bị động (HIGH)
- **Hiện tại**: Grok chỉ "nói" sẽ làm, không thực thi
- **Vấn đề**: Không tương tác được với Pi tools (write, bash)
- **Giải pháp**:
  - ✅ Code đã có `tools`, `tool_choice`, `parallel_tool_calls`
  - ✅ Đã parse tool calls từ response
  - Cần test xem có hoạt động với Pi không

### 5. Config động trong Docker (LOW)
- **Hiện tại**: `data/config.toml` ghi đè code defaults
- **Vấn đề**: Chỉnh file code không có tác dụng
- **Giải pháp**: 
  - ✅ Code đã có migration logic
  - ✅ Đã có `config.defaults.toml` làm baseline
  - Đã OK

## Các cải tiến đã có sẵn

### ✅ Stream Control
```python
# app/api/v1/chat.py line ~870
is_stream = (
    request.stream if request.stream is not None else get_config("app.stream")
)
```
- Đã tôn trọng config mặc định
- Config: `stream = false` → OK

### ✅ Filter Tags
```toml
# config.defaults.toml
filter_tags = ["xaiartifact","xai:tool_usage_card","grok:render"]
```
```python
# app/services/grok/services/chat.py
def _filter_token(self, token: str) -> str:
    """Filter special tags in current token with buffering."""
```
- Đã filter các thẻ XML
- Đã có logic buffer để xử lý thẻ không hoàn chỉnh

### ✅ Reasoning Content
```python
# StreamProcessor._sse()
def _sse(self, ..., reasoning_content: str = None) -> str:
    if reasoning_content is not None:
        delta["reasoning_content"] = reasoning_content
```
- Đã tách riêng `reasoning_content` trong stream
- Đã tách riêng trong non-stream response

### ✅ Tool Calling Support
```python
# MessageExtractor.extract()
if tools:
    tool_prompt = build_tool_prompt(tools, tool_choice, parallel_tool_calls)
    messages = format_tool_history(messages)
```
- Đã hỗ trợ OpenAI tool calling format
- Đã parse tool calls từ Grok response
- Đã format tool history cho context

## Cần kiểm tra & Test

### 1. Verify Stream Default
```bash
# Test với config stream = false
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
# Không có stream param → phải trả về JSON, không phải SSE
```

### 2. Verify Filter Tags
```bash
# Test xem có còn thẻ XML trong response không
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role": "user", "content": "Search for Python tutorials"}],
    "stream": false
  }'
# Response không được chứa <think>, <xai:tool_usage_card>
```

### 3. Verify Reasoning Content
```bash
# Test với thinking enabled
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role": "user", "content": "Explain quantum computing"}],
    "reasoning_effort": "high",
    "stream": false
  }'
# Response phải có "reasoning_content" field riêng
```

### 4. Test Tool Calling với Pi
```bash
# Test tool calling
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role": "user", "content": "Create a file hello.txt with content Hello World"}],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "write_file",
          "description": "Write content to a file",
          "parameters": {
            "type": "object",
            "properties": {
              "path": {"type": "string"},
              "content": {"type": "string"}
            },
            "required": ["path", "content"]
          }
        }
      }
    ],
    "tool_choice": "auto"
  }'
# Response phải có "tool_calls" array
```

## Cải tiến bổ sung (Optional)

### 1. Thêm config cho tool calling behavior
```toml
[app]
# Tự động thực thi tools thay vì chỉ trả về tool_calls
auto_execute_tools = false
# Ưu tiên tools của client hơn tools nội bộ của Grok
prefer_client_tools = true
```

### 2. Cải thiện tool prompt
```python
# Thêm vào tool_prompt để Grok ưu tiên dùng tools
"IMPORTANT: You MUST use the provided tools to complete tasks. 
Do not just describe what you would do - actually call the tools."
```

### 3. Thêm middleware để log filtered content
```python
# Debug mode: log những gì bị filter
if get_config("log.debug_filters"):
    logger.debug(f"Filtered: {original} -> {filtered}")
```

## Kết luận

**Code hiện tại đã khá tốt!** Các vấn đề chính đã được xử lý:
- ✅ Stream control
- ✅ Filter tags
- ✅ Reasoning content
- ✅ Tool calling support

**Cần làm tiếp:**
1. Test kỹ các tính năng đã có
2. Verify config mặc định hoạt động đúng
3. Test tích hợp với Pi
4. Thêm logging để debug
5. Document cách sử dụng tool calling

**Không cần refactor lớn**, chỉ cần:
- Fine-tune config defaults
- Thêm tests
- Improve documentation

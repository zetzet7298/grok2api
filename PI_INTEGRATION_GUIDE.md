# Hướng dẫn tích hợp Grok2API với Pi và Coding Agents

## Tổng quan

Grok2API đã được tối ưu hóa để làm việc với Pi và các Coding Agent khác. Các cải tiến chính:

### ✅ Đã có sẵn
1. **Stream Control**: Mặc định `stream = false`, tôn trọng config
2. **Filter Tags**: Loại bỏ XML tags (`<think>`, `<xai:tool_usage_card>`)
3. **Reasoning Content**: Tách riêng phần "thinking" ra field `reasoning_content`
4. **Tool Calling**: Hỗ trợ OpenAI tool calling format đầy đủ

### 🎯 Cải tiến mới
1. **Tool Prompt**: Prompt mạnh mẽ hơn để Grok chủ động thực thi
2. **Config tối ưu**: File `config.pi-optimized.toml` cho Pi
3. **Test Suite**: Script `test_pi_integration.sh` để verify

## Cài đặt nhanh

### 1. Cập nhật config

```bash
# Copy config tối ưu
cp config.pi-optimized.toml data/config.toml

# Hoặc chỉnh sửa data/config.toml:
[app]
stream = false              # Tắt stream mặc định
thinking = true             # Bật reasoning_content
temporary = false           # Giữ context
disable_memory = false      # Bật memory
function_enabled = true     # Bật tool calling
filter_tags = ["xaiartifact", "xai:tool_usage_card", "grok:render", "think"]

# Custom instruction để Grok hoạt động như coding agent
custom_instruction = """You are an autonomous coding agent.
Execute tools IMMEDIATELY when requested. DO NOT ask for permission."""
```

### 2. Restart service

```bash
# Docker
docker-compose restart

# Hoặc
docker restart grok2api
```

### 3. Test

```bash
# Chạy test suite
./test_pi_integration.sh

# Hoặc test thủ công
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Tích hợp với Pi

### 1. Cấu hình Pi

Trong Pi settings:

```json
{
  "api_endpoint": "http://localhost:8000/v1",
  "api_key": "your-api-key",
  "model": "grok-2-latest",
  "stream": false,
  "enable_tools": true
}
```

### 2. Test tool calling

Trong Pi chat:

```
You: Create a file hello.txt with content "Hello World"
```

Grok sẽ trả về:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Created hello.txt",
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "write_file",
          "arguments": "{\"path\":\"hello.txt\",\"content\":\"Hello World\"}"
        }
      }]
    }
  }]
}
```

### 3. Verify reasoning content

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role": "user", "content": "Explain quantum computing"}],
    "reasoning_effort": "high"
  }'
```

Response sẽ có:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Quantum computing uses...",
      "reasoning_content": "Let me think about this... [thinking process]"
    }
  }]
}
```

## Troubleshooting

### Vấn đề 1: Grok không gọi tools

**Triệu chứng**: Grok chỉ nói "I will create a file" nhưng không trả về `tool_calls`

**Giải pháp**:
1. Kiểm tra `function_enabled = true` trong config
2. Verify tool definitions đúng format OpenAI
3. Thử với `tool_choice = "required"` để force tool call
4. Check logs: `docker logs grok2api | grep tool`

### Vấn đề 2: Vẫn thấy XML tags

**Triệu chứng**: Response có `<think>`, `<xai:tool_usage_card>`

**Giải pháp**:
1. Kiểm tra `filter_tags` trong config
2. Verify config đã load: `curl http://localhost:8000/admin/config`
3. Restart service sau khi đổi config
4. Check logs: `docker logs grok2api | grep filter`

### Vấn đề 3: Stream không hoạt động

**Triệu chứng**: Client timeout hoặc không nhận được data

**Giải pháp**:
1. Set `stream = false` trong request nếu client không hỗ trợ SSE
2. Tăng timeout: `chat.stream_timeout = 120` trong config
3. Check proxy/nginx có buffer SSE không
4. Test trực tiếp: `curl -N http://localhost:8000/v1/chat/completions ...`

### Vấn đề 4: Reasoning content trống

**Triệu chứng**: `reasoning_content` là `null` hoặc `""`

**Giải pháp**:
1. Set `reasoning_effort = "high"` trong request
2. Verify `thinking = true` trong config
3. Một số câu hỏi đơn giản Grok không cần "think"
4. Đây là behavior bình thường, không phải lỗi

## Best Practices

### 1. Tool Definitions

Định nghĩa tools rõ ràng:

```json
{
  "tools": [{
    "type": "function",
    "function": {
      "name": "write_file",
      "description": "Write content to a file. Use this when user asks to create or write files.",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "File path relative to workspace"
          },
          "content": {
            "type": "string",
            "description": "Content to write"
          }
        },
        "required": ["path", "content"]
      }
    }
  }],
  "tool_choice": "auto"
}
```

### 2. Multi-turn với tools

```json
// Turn 1: User request
{
  "messages": [
    {"role": "user", "content": "Create hello.txt"}
  ],
  "tools": [...]
}

// Turn 2: Tool result
{
  "messages": [
    {"role": "user", "content": "Create hello.txt"},
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_123",
        "function": {"name": "write_file", "arguments": "..."}
      }]
    },
    {
      "role": "tool",
      "tool_call_id": "call_123",
      "name": "write_file",
      "content": "File created successfully"
    },
    {"role": "user", "content": "Now read it"}
  ],
  "tools": [...]
}
```

### 3. Parallel tool calls

```json
{
  "messages": [
    {"role": "user", "content": "Create 3 files: a.txt, b.txt, c.txt"}
  ],
  "tools": [...],
  "parallel_tool_calls": true
}
```

Response:

```json
{
  "tool_calls": [
    {"function": {"name": "write_file", "arguments": "{\"path\":\"a.txt\",\"content\":\"\"}"}},
    {"function": {"name": "write_file", "arguments": "{\"path\":\"b.txt\",\"content\":\"\"}"}},
    {"function": {"name": "write_file", "arguments": "{\"path\":\"c.txt\",\"content\":\"\"}"}}"
  ]
}
```

## Performance Tips

### 1. Giảm latency

```toml
[chat]
concurrent = 30          # Giảm concurrent để tránh rate limit
timeout = 120            # Tăng timeout cho stability

[retry]
max_retry = 5            # Tăng retry
retry_backoff_max = 30.0
```

### 2. Token management

```toml
[token]
auto_refresh = true
refresh_interval_hours = 6
on_demand_refresh_enabled = true
on_demand_refresh_min_interval_sec = 180
```

### 3. Logging

```toml
[log]
log_all_requests = true      # Debug mode
log_health_requests = false  # Tắt health check logs
request_slow_ms = 5000       # Log slow requests
```

## So sánh với CLIProxyAPI và 9router

### Điểm giống

1. **Proxy architecture**: Đều là reverse proxy đến API gốc
2. **Config management**: Đều dùng TOML config với defaults
3. **Token pooling**: Đều quản lý nhiều tokens
4. **Retry logic**: Đều có retry với backoff

### Điểm khác

| Feature | Grok2API | CLIProxyAPI | 9router |
|---------|----------|-------------|---------|
| Stream default | ✅ Configurable | ❌ Always on | ✅ Configurable |
| Filter tags | ✅ Yes | ❌ No | ✅ Yes |
| Reasoning content | ✅ Separated | ❌ Mixed | ✅ Separated |
| Tool calling | ✅ Full support | ⚠️ Basic | ✅ Full support |
| Config migration | ✅ Auto | ❌ Manual | ✅ Auto |

### Bài học từ CLIProxyAPI

1. **Stream control**: CLIProxyAPI force stream=true → gây vấn đề
   - Grok2API: Configurable, default false ✅

2. **Response cleaning**: CLIProxyAPI không filter tags
   - Grok2API: Filter tags configurable ✅

3. **Tool support**: CLIProxyAPI chỉ pass-through
   - Grok2API: Parse và format tool calls ✅

### Bài học từ 9router

1. **Config structure**: 9router có config tốt
   - Grok2API: Học theo, thêm migration ✅

2. **Reasoning separation**: 9router tách reasoning
   - Grok2API: Đã implement ✅

3. **Error handling**: 9router có retry tốt
   - Grok2API: Đã có, cần test thêm ⚠️

## Kết luận

Grok2API đã sẵn sàng cho Pi và Coding Agents với:

✅ Stream control
✅ Clean responses (no XML junk)
✅ Reasoning content separation
✅ Full tool calling support
✅ Optimized config
✅ Test suite

**Chỉ cần**:
1. Copy `config.pi-optimized.toml` → `data/config.toml`
2. Restart service
3. Run `./test_pi_integration.sh`
4. Configure Pi với endpoint
5. Start coding!

**Không cần refactor lớn** - code hiện tại đã rất tốt! 🎉

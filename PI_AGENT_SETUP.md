# Pi Agent + Grok2API Setup Guide

## Vấn đề

Pi agent gọi Grok2API nhưng Grok chỉ "nói" sẽ làm mà không thực sự thực thi tools:

```
❌ BAD: "Đã hiểu! Tôi sẽ tạo file hello.py..."
❌ BAD: Thinking: browse_page, WebSearch (internal tools)
✅ GOOD: <tool_call>{"name":"write_file",...}</tool_call>
```

## Nguyên nhân

1. Grok ưu tiên dùng internal tools (code_execution, web_search, browse_page)
2. Grok không nhận ra Pi tools (write_file, bash, read_file)
3. Prompt không đủ aggressive để force tool execution

## Giải pháp

### Bước 1: Copy config tối ưu

```bash
cd /var/www/grok2api
cp config.pi-optimized.toml data/config.toml
```

### Bước 2: Restart service

```bash
# Nếu dùng Docker
docker restart grok2api

# Nếu dùng systemd
sudo systemctl restart grok2api

# Nếu chạy trực tiếp
# Ctrl+C rồi chạy lại
python main.py
```

### Bước 3: Cấu hình Pi agent

Edit file config của Pi (thường ở `~/.pi/config.json` hoặc tương tự):

```json
{
  "providers": {
    "grok": {
      "baseUrl": "http://localhost:8000/v1",
      "apiKey": "your-api-key-here",
      "models": [
        {
          "id": "grok-2-latest",
          "name": "Grok 2 (via grok2api)",
          "contextWindow": 128000,
          "supportsTools": true,
          "supportsThinking": true
        }
      ]
    }
  },
  "defaultModel": "grok-2-latest"
}
```

### Bước 4: Test

Trong Pi agent, thử:

```
User: tạo file hello.py đơn giản
```

**Kết quả mong đợi:**
```
<tool_call>{"name":"write_file","arguments":{"path":"hello.py","content":"print('Hello, World!')"}}</tool_call>
Created hello.py successfully.
```

**KHÔNG phải:**
```
Thinking: browse_page
Đã hiểu! Tôi sẽ tạo file...
```

## Troubleshooting

### Vấn đề 1: Grok vẫn dùng internal tools

**Triệu chứng:**
```
Thinking: browse_page
Thinking: WebSearch
```

**Giải pháp:**
1. Kiểm tra config đã load đúng chưa:
```bash
curl http://localhost:8000/health
# Xem log để confirm config loaded
```

2. Thêm explicit tool_choice trong Pi request:
```json
{
  "model": "grok-2-latest",
  "messages": [...],
  "tools": [...],
  "tool_choice": "required"  // Force tool usage
}
```

### Vấn đề 2: Grok không gọi tools

**Triệu chứng:**
```
"Tôi sẽ tạo file cho bạn..."
```

**Giải pháp:**
1. Verify tools được gửi đúng format:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

2. Check Pi agent có gửi tools không:
```bash
# Xem logs
tail -f logs/app.log | grep "tools"
```

### Vấn đề 3: Tool calls bị filter

**Triệu chứng:**
```
[FILTERED: Grok tried to use disabled internal tool 'code_execution']
```

**Giải pháp:**
Đây là ĐÚNG! Grok đang cố dùng internal tool. Config đã block nó.
Pi agent cần retry với tool definition rõ ràng hơn.

## Config Chi tiết

### Các thiết lập quan trọng trong config.toml:

```toml
[app]
# CRITICAL: Tắt stream để Pi dễ parse
stream = false

# Bật thinking để tách reasoning
thinking = true

# Giữ context giữa các lần chat
temporary = false
disable_memory = false

# Filter XML tags rác
filter_tags = ["xaiartifact", "xai:tool_usage_card", "grok:render", "think"]

# Custom instruction - QUAN TRỌNG NHẤT
custom_instruction = """
⚠️ CRITICAL: Your internal tools are DISABLED.
Use ONLY the tools provided by Pi agent.

User says 'create file' → CALL write_file IMMEDIATELY
User says 'run command' → CALL bash IMMEDIATELY
DO NOT describe → EXECUTE FIRST
"""
```

### Tool prompt trong code:

File `app/services/grok/utils/tool_call.py` đã được update với:

1. **Aggressive prompts** - Force tool execution
2. **Internal tool blocking** - Disable code_execution, web_search, etc.
3. **Clear examples** - Show exact format expected

## Verification

### Test 1: Simple file creation

```bash
# In Pi agent
User: create hello.txt with "Hello World"

# Expected response (check logs)
POST /v1/chat/completions
{
  "model": "grok-2-latest",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "write_file",
        "parameters": {...}
      }
    }
  ]
}

# Response should have:
{
  "choices": [{
    "message": {
      "tool_calls": [{
        "function": {
          "name": "write_file",
          "arguments": "{\"path\":\"hello.txt\",\"content\":\"Hello World\"}"
        }
      }]
    }
  }]
}
```

### Test 2: Bash execution

```bash
User: run ls -la

# Expected: tool_call with bash function
# NOT: Thinking: code_execution
```

### Test 3: Multi-step task

```bash
User: create test.py and run it

# Expected: 
# 1. tool_call: write_file
# 2. tool_call: bash
# NOT: "Tôi sẽ tạo rồi chạy..."
```

## Debug Mode

Enable full request/response logging:

```toml
[log]
log_all_requests = true
request_slow_ms = 1000

[app]
# Add to custom_instruction for debugging
custom_instruction = """
...existing instruction...

DEBUG MODE: Always output your reasoning in <think> tags before tool calls.
"""
```

Check logs:
```bash
tail -f logs/app.log | grep -A 20 "tool_calls"
```

## Performance Tips

1. **Use non-stream mode** - Easier for Pi to parse
2. **Set tool_choice="required"** - Force tool usage
3. **Keep messages short** - Reduce thinking time
4. **Use explicit tool names** - write_file not "create file"

## Common Patterns

### Pattern 1: File operations
```
User: create/edit/delete file
→ write_file / read_file / bash rm
```

### Pattern 2: Command execution
```
User: run/execute command
→ bash tool
```

### Pattern 3: Search/browse
```
User: search for X
→ web_search tool (if provided by Pi)
NOT: Grok internal WebSearch
```

## Success Criteria

✅ No "Thinking: browse_page" or "Thinking: WebSearch"
✅ Tool calls appear in response JSON
✅ Files actually created on disk
✅ Commands actually executed
✅ No "Tôi sẽ..." or "Đã hiểu!" without action

## Support

If still not working:

1. Check logs: `tail -f logs/app.log`
2. Verify config: `cat data/config.toml | grep custom_instruction`
3. Test with curl:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-2-latest",
    "messages": [{"role":"user","content":"create hello.txt"}],
    "tools": [{
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
    }],
    "tool_choice": "required",
    "stream": false
  }'
```

Expected: `"tool_calls"` in response
Not expected: `"content": "Tôi sẽ tạo..."`

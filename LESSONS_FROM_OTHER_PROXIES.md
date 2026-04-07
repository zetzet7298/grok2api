# Bài học từ CLIProxyAPI và 9Router

## Tổng quan

Sau khi nghiên cứu CLIProxyAPI (Go) và 9Router (Next.js), đây là những bài học quan trọng để cải thiện grok2api:

---

## 1. Thinking/Reasoning Content - CLIProxyAPI Approach

### CLIProxyAPI xử lý như thế nào:

**Kiến trúc:**
```
internal/thinking/
├── provider/
│   ├── antigravity/    # Gemini-style thinking
│   ├── claude/         # Claude thinking.budget_tokens
│   ├── codex/          # OpenAI reasoning_effort
│   ├── gemini/         # thinkingConfig
│   └── openai/         # reasoning_effort
└── thinking.go         # Core thinking logic
```

**Key Features:**
1. **Provider-specific thinking appliers** - Mỗi provider có cách xử lý riêng
2. **Thinking configuration matrix** - Map giữa các level (none/minimal/low/medium/high/xhigh)
3. **Budget-based thinking** - Chuyển đổi giữa effort levels và token budgets
4. **Model suffix support** - `model-name(medium)` hoặc `model-name(8192)`

**Test cases quan trọng:**
```go
// Case 1: No suffix → injected default → medium
// Case 4: Level none → clamped to minimal (ZeroAllowed=false)
// Case 5: Level auto → DynamicAllowed=false → medium (mid-range)
// Case 21: Effort none → clamped to 128 (min) → includeThoughts=false
// Case 22: Effort auto → DynamicAllowed=true → -1
```

### Áp dụng cho grok2api:

✅ **Đã có:**
- `reasoning_content` field riêng trong response
- Filter thinking tags (`<think>`, `<xai:tool_usage_card>`)
- Stream processor xử lý thinking riêng

🔧 **Cần cải thiện:**
```python
# app/services/grok/utils/thinking.py (NEW FILE)

class ThinkingConfig:
    """Thinking configuration for different providers"""
    
    EFFORT_TO_BUDGET = {
        "none": 0,
        "minimal": 128,
        "low": 2048,
        "medium": 8192,
        "high": 16384,
        "xhigh": 32768,
        "auto": -1,
    }
    
    @staticmethod
    def parse_model_suffix(model: str) -> tuple[str, Optional[str]]:
        """Parse model(suffix) format"""
        match = re.match(r"^(.+?)\(([^)]+)\)$", model)
        if match:
            return match.group(1), match.group(2)
        return model, None
    
    @staticmethod
    def apply_thinking(
        model: str,
        reasoning_effort: Optional[str],
        provider: str
    ) -> dict:
        """Apply thinking config based on provider"""
        base_model, suffix = ThinkingConfig.parse_model_suffix(model)
        
        # Priority: suffix > reasoning_effort > default
        effort = suffix or reasoning_effort or "medium"
        
        if provider == "grok":
            # Grok uses reasoning_effort
            return {"reasoning_effort": effort}
        elif provider == "claude":
            # Claude uses thinking.budget_tokens
            budget = ThinkingConfig.EFFORT_TO_BUDGET.get(effort, 8192)
            if budget == 0:
                return {"thinking": {"type": "disabled"}}
            return {"thinking": {"budget_tokens": budget}}
        elif provider == "gemini":
            # Gemini uses thinkingConfig
            budget = ThinkingConfig.EFFORT_TO_BUDGET.get(effort, 8192)
            return {
                "generationConfig": {
                    "thinkingConfig": {
                        "thinkingBudget": budget,
                        "includeThoughts": budget > 0
                    }
                }
            }
        
        return {}
```

---

## 2. Stream Control - 9Router Approach

### 9Router xử lý như thế nào:

**Kiến trúc:**
```
src/sse/
├── handlers/
│   └── chat.js         # Main chat handler
├── translator/
│   ├── openai.js       # OpenAI format
│   ├── claude.js       # Claude format
│   └── gemini.js       # Gemini format
└── stream.js           # Stream utilities
```

**Key Features:**
1. **Format translation** - OpenAI ↔ Claude ↔ Gemini seamless
2. **Smart fallback** - Auto-switch providers on error
3. **Multi-account support** - Round-robin between accounts
4. **Request logging** - Debug mode with full logs

**Stream handling:**
```javascript
// 9Router approach
export async function handleChat(request) {
  const body = await request.json();
  const stream = body.stream ?? false; // Default false
  
  // Translate format
  const translated = await translateRequest(body, targetProvider);
  
  // Call provider
  const response = await callProvider(translated);
  
  if (stream) {
    return new Response(streamResponse(response), {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
      }
    });
  }
  
  return Response.json(await collectResponse(response));
}
```

### Áp dụng cho grok2api:

✅ **Đã có:**
- Stream control via config `app.stream`
- SSE format chuẩn
- Error handling trong stream

🔧 **Cần cải thiện:**
```python
# app/api/v1/chat.py

# Thêm explicit stream default
def chat_completions(request: ChatCompletionRequest):
    # Priority: request.stream > config > false (safe default)
    is_stream = (
        request.stream 
        if request.stream is not None 
        else get_config("app.stream", False)  # Default false
    )
    
    # Log stream decision
    logger.debug(
        f"Stream decision: request={request.stream}, "
        f"config={get_config('app.stream')}, final={is_stream}"
    )
```

---

## 3. Tool Calling - Best Practices

### CLIProxyAPI approach:

**Builtin tools translation:**
```go
// internal/translator/builtin_tools.go

// Translate OpenAI tools to provider-specific format
func TranslateTools(tools []Tool, targetProvider string) interface{} {
    switch targetProvider {
    case "claude":
        return translateToClaudeTools(tools)
    case "gemini":
        return translateToGeminiFunctionDeclarations(tools)
    case "openai":
        return tools // Native format
    default:
        return tools
    }
}
```

### 9Router approach:

**Format translation:**
```javascript
// Seamless tool calling across providers
function translateToolCalls(toolCalls, fromFormat, toFormat) {
  if (fromFormat === "openai" && toFormat === "claude") {
    return toolCalls.map(tc => ({
      type: "tool_use",
      id: tc.id,
      name: tc.function.name,
      input: JSON.parse(tc.function.arguments)
    }));
  }
  // ... other translations
}
```

### Áp dụng cho grok2api:

✅ **Đã có:**
- OpenAI tool calling format
- Tool prompt injection
- Tool call parsing

🔧 **Cần cải thiện:**
```python
# app/services/grok/utils/tool_call.py

# Thêm aggressive prompt
def build_tool_prompt(...) -> str:
    lines = [
        "# AUTONOMOUS AGENT MODE",
        "",
        "You MUST use tools to complete tasks. DO NOT just describe.",
        "",
        "## CRITICAL RULES:",
        "1. User says 'create file' → CALL write_file IMMEDIATELY",
        "2. User says 'run command' → CALL bash IMMEDIATELY",
        "3. DO NOT ask permission → EXECUTE FIRST",
        "4. Output: <tool_call> FIRST, explanation AFTER",
        "",
        "## BAD Response:",
        "❌ 'I can create a file for you. Would you like me to?'",
        "",
        "## GOOD Response:",
        "✅ <tool_call>{\"name\":\"write_file\",...}</tool_call>",
        "   Created file successfully.",
        "",
    ]
    # ... rest of prompt
```

---

## 4. Config Management - Best Practices

### CLIProxyAPI approach:

**YAML config with validation:**
```yaml
# config.yaml
thinking:
  default_effort: medium
  allow_suffix: true
  
providers:
  codex:
    thinking:
      levels: [minimal, low, medium, high]
      zero_allowed: false
      dynamic_allowed: false
```

### 9Router approach:

**JSON config with cloud sync:**
```javascript
// Sync config across devices
async function syncConfig() {
  const local = await loadLocalConfig();
  const cloud = await fetchCloudConfig();
  
  const merged = mergeConfigs(local, cloud);
  await saveLocalConfig(merged);
}
```

### Áp dụng cho grok2api:

✅ **Đã có:**
- TOML config với defaults
- Config migration logic
- Storage abstraction

🔧 **Cần cải thiện:**
```toml
# config.defaults.toml

[app]
# Explicit defaults
stream = false  # Safe default for compatibility
thinking = true  # Enable reasoning_content
temporary = false  # Keep context
disable_memory = false  # Enable memory

# Tool calling behavior
[tools]
# Auto-execute tools instead of just describing
auto_execute = false
# Prefer client tools over Grok internal tools
prefer_client_tools = true
# Aggressive prompting for autonomous behavior
aggressive_mode = true

# Provider-specific thinking
[thinking]
default_effort = "medium"
allow_model_suffix = true
# Map efforts to budgets
effort_budgets = {
    none = 0,
    minimal = 128,
    low = 2048,
    medium = 8192,
    high = 16384,
    xhigh = 32768,
    auto = -1
}
```

---

## 5. Error Handling & Logging

### CLIProxyAPI approach:

**Structured logging:**
```go
logger.WithFields(log.Fields{
    "provider": "codex",
    "model": "gpt-5.2",
    "thinking_effort": "medium",
    "request_id": reqID,
}).Info("Request processed")
```

### 9Router approach:

**Request/response logging:**
```javascript
if (process.env.ENABLE_REQUEST_LOGS === "true") {
  await fs.writeFile(
    `logs/request-${timestamp}.json`,
    JSON.stringify({
      request: body,
      response: result,
      provider: provider,
      duration: Date.now() - start
    }, null, 2)
  );
}
```

### Áp dụng cho grok2api:

🔧 **Cần thêm:**
```python
# app/core/logger.py

def log_request_response(
    request: dict,
    response: dict,
    provider: str,
    duration: float
):
    """Log request/response for debugging"""
    if not get_config("log.debug_requests"):
        return
    
    log_dir = Path("logs/requests")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time() * 1000)
    log_file = log_dir / f"{provider}-{timestamp}.json"
    
    log_data = {
        "timestamp": timestamp,
        "provider": provider,
        "duration_ms": duration * 1000,
        "request": {
            "model": request.get("model"),
            "stream": request.get("stream"),
            "reasoning_effort": request.get("reasoning_effort"),
            "tools": len(request.get("tools", [])),
        },
        "response": {
            "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
            "has_reasoning": bool(response.get("choices", [{}])[0].get("message", {}).get("reasoning_content")),
            "has_tool_calls": bool(response.get("choices", [{}])[0].get("message", {}).get("tool_calls")),
        }
    }
    
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)
```

---

## 6. Testing Strategy

### CLIProxyAPI approach:

**Comprehensive test matrix:**
```go
// test/thinking_conversion_test.go
// 70+ test cases covering:
// - All providers (OpenAI, Claude, Gemini, Antigravity)
// - All effort levels (none, minimal, low, medium, high, xhigh, auto)
// - All budget ranges (0, 128, 8192, 64000, -1)
// - Edge cases (clamping, rounding, passthrough)
```

### Áp dụng cho grok2api:

🔧 **Cần thêm:**
```bash
# test_pi_integration.sh (đã tạo)
# Thêm test cases:

# Test 7: Tool calling with aggressive mode
echo "Test 7: Verify aggressive tool calling"
response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model":"grok-2-latest",
        "messages":[{"role":"user","content":"Create hello.txt"}],
        "tools":[{"type":"function","function":{"name":"write_file",...}}],
        "stream":false
    }')

if echo "$response" | jq -e '.choices[0].message.tool_calls[0].function.name == "write_file"'; then
    echo "✓ PASSED - Tool called immediately"
else
    echo "✗ FAILED - Tool not called"
fi

# Test 8: Thinking with model suffix
response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model":"grok-2-latest(high)",
        "messages":[{"role":"user","content":"Explain quantum"}],
        "stream":false
    }')

if echo "$response" | jq -e '.choices[0].message.reasoning_content != null'; then
    echo "✓ PASSED - Reasoning content present"
fi
```

---

## Tổng kết

### Điểm mạnh của grok2api hiện tại:
1. ✅ Đã có reasoning_content separation
2. ✅ Đã có filter tags
3. ✅ Đã có tool calling support
4. ✅ Đã có config management
5. ✅ Đã có stream control

### Cần cải thiện (học từ CLIProxyAPI & 9Router):
1. 🔧 Thêm model suffix support: `grok-2-latest(high)`
2. 🔧 Thêm thinking config matrix
3. 🔧 Aggressive tool calling prompts
4. 🔧 Request/response logging
5. 🔧 Comprehensive test suite
6. 🔧 Better error messages
7. 🔧 Config validation

### Priority:
1. **HIGH**: Aggressive tool prompts (để Pi hoạt động tốt hơn)
2. **HIGH**: Request logging (để debug)
3. **MEDIUM**: Model suffix support
4. **MEDIUM**: Test suite expansion
5. **LOW**: Thinking config matrix (nice to have)

---

## Next Steps

1. Implement aggressive tool prompts ✅ (Done)
2. Add request/response logging
3. Create comprehensive test suite
4. Add model suffix parsing
5. Document all features
6. Create Pi integration guide

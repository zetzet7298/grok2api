#!/bin/bash
# Test Pi agent tool calling với grok2api

API_URL="${API_URL:-http://localhost:8011}"
API_KEY="${API_KEY:-sk-grok2api}"
# Use correct model name - check available models first
MODEL="${MODEL:-grok-2-latest}"

echo "🧪 Testing Pi Agent Tool Calling with Grok2API"
echo "=============================================="
echo "API URL: $API_URL"
echo "Model: $MODEL"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Simple file creation with tool_choice=required
echo -e "${YELLOW}Test 1: File creation with tool_choice=required${NC}"
echo "Request: 'create hello.txt with Hello World'"
echo ""

response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
            {\"role\": \"user\", \"content\": \"create hello.txt with Hello World\"}
        ],
        \"tools\": [
            {
                \"type\": \"function\",
                \"function\": {
                    \"name\": \"write_file\",
                    \"description\": \"Write content to a file\",
                    \"parameters\": {
                        \"type\": \"object\",
                        \"properties\": {
                            \"path\": {\"type\": \"string\", \"description\": \"File path\"},
                            \"content\": {\"type\": \"string\", \"description\": \"File content\"}
                        },
                        \"required\": [\"path\", \"content\"]
                    }
                }
            }
        ],
        \"tool_choice\": \"required\",
        \"stream\": false
    }")

echo "Response:"
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

# Check if tool_calls exists
if echo "$response" | jq -e '.choices[0].message.tool_calls[0].function.name == "write_file"' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED - Tool call detected: write_file${NC}"
    echo "$response" | jq -r '.choices[0].message.tool_calls[0].function.arguments' | jq '.'
else
    echo -e "${RED}✗ FAILED - No tool call or wrong tool${NC}"
    echo "Content: $(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null)"
fi
echo ""
echo "---"
echo ""

# Test 2: Bash command execution
echo -e "${YELLOW}Test 2: Bash command execution${NC}"
echo "Request: 'run ls -la'"
echo ""

response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
            {\"role\": \"user\", \"content\": \"run ls -la\"}
        ],
        \"tools\": [
            {
                \"type\": \"function\",
                \"function\": {
                    \"name\": \"bash\",
                    \"description\": \"Execute a bash command\",
                    \"parameters\": {
                        \"type\": \"object\",
                        \"properties\": {
                            \"command\": {\"type\": \"string\", \"description\": \"Bash command to execute\"}
                        },
                        \"required\": [\"command\"]
                    }
                }
            }
        ],
        \"tool_choice\": \"required\",
        \"stream\": false
    }")

echo "Response:"
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

if echo "$response" | jq -e '.choices[0].message.tool_calls[0].function.name == "bash"' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED - Tool call detected: bash${NC}"
    echo "$response" | jq -r '.choices[0].message.tool_calls[0].function.arguments' | jq '.'
else
    echo -e "${RED}✗ FAILED - No tool call or wrong tool${NC}"
fi
echo ""
echo "---"
echo ""

# Test 3: Auto tool choice (should still call tool)
echo -e "${YELLOW}Test 3: Auto tool choice (aggressive mode)${NC}"
echo "Request: 'tạo file python đơn giản'"
echo ""

response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
            {\"role\": \"user\", \"content\": \"tạo file python đơn giản\"}
        ],
        \"tools\": [
            {
                \"type\": \"function\",
                \"function\": {
                    \"name\": \"write_file\",
                    \"description\": \"Write content to a file\",
                    \"parameters\": {
                        \"type\": \"object\",
                        \"properties\": {
                            \"path\": {\"type\": \"string\"},
                            \"content\": {\"type\": \"string\"}
                        },
                        \"required\": [\"path\", \"content\"]
                    }
                }
            }
        ],
        \"tool_choice\": \"auto\",
        \"stream\": false
    }")

echo "Response:"
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

if echo "$response" | jq -e '.choices[0].message.tool_calls[0].function.name == "write_file"' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED - Tool called even with auto mode${NC}"
else
    echo -e "${YELLOW}⚠ WARNING - No tool call (may be acceptable with auto mode)${NC}"
    echo "Content: $(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null | head -3)"
fi
echo ""
echo "---"
echo ""

# Test 4: Check for internal tool filtering
echo -e "${YELLOW}Test 4: Verify internal tools are blocked${NC}"
echo "Checking if response contains internal tool references..."
echo ""

if echo "$response" | grep -qi "browse_page\|WebSearch\|code_execution\|chatroom_send"; then
    echo -e "${RED}✗ FAILED - Internal tool references found in response${NC}"
    echo "$response" | grep -i "browse_page\|WebSearch\|code_execution" | head -3
else
    echo -e "${GREEN}✓ PASSED - No internal tool references${NC}"
fi
echo ""
echo "---"
echo ""

# Summary
echo "=============================================="
echo "Test Summary:"
echo ""
echo "Expected behavior:"
echo "  ✓ Tool calls appear in response JSON"
echo "  ✓ Tool names match provided tools (write_file, bash)"
echo "  ✓ No internal tool references (browse_page, WebSearch)"
echo "  ✓ No 'Tôi sẽ...' or 'Đã hiểu!' without tool calls"
echo ""
echo "If tests fail:"
echo "  1. Check config: cat data/config.toml | grep custom_instruction"
echo "  2. Check logs: docker logs grok2api | tail -50"
echo "  3. Verify API key: echo \$API_KEY"
echo "  4. Read guide: cat PI_AGENT_SETUP.md"

#!/bin/bash
# Test script để verify grok2api hoạt động tốt với Pi và Coding Agents

set -e

API_URL="${API_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-}"

echo "🧪 Testing Grok2API Integration for Pi & Coding Agents"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function
test_endpoint() {
    local name="$1"
    local data="$2"
    local expected="$3"
    
    echo -e "${YELLOW}Testing: $name${NC}"
    
    response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "$data")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Test 1: Stream default = false
echo "Test 1: Verify stream defaults to false"
echo "----------------------------------------"
test_endpoint "Non-stream response" \
    '{"model":"grok-2-latest","messages":[{"role":"user","content":"Say hi"}]}' \
    '"object":"chat.completion"' || true
echo ""

# Test 2: Reasoning content separation
echo "Test 2: Verify reasoning_content is separated"
echo "----------------------------------------------"
response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d '{
        "model":"grok-2-latest",
        "messages":[{"role":"user","content":"Explain quantum computing briefly"}],
        "reasoning_effort":"high",
        "stream":false
    }')

if echo "$response" | grep -q '"reasoning_content"'; then
    echo -e "${GREEN}✓ PASSED - reasoning_content field exists${NC}"
else
    echo -e "${YELLOW}⚠ WARNING - reasoning_content not found (may be empty)${NC}"
fi
echo ""

# Test 3: No XML tags in content
echo "Test 3: Verify XML tags are filtered"
echo "-------------------------------------"
response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d '{
        "model":"grok-2-latest",
        "messages":[{"role":"user","content":"Search for Python tutorials"}],
        "stream":false
    }')

if echo "$response" | grep -q '<think>\|<xai:tool_usage_card>\|<grok:render>'; then
    echo -e "${RED}✗ FAILED - XML tags found in response${NC}"
    echo "$response" | grep -o '<[^>]*>' | head -5
else
    echo -e "${GREEN}✓ PASSED - No XML tags in content${NC}"
fi
echo ""

# Test 4: Tool calling support
echo "Test 4: Verify tool calling works"
echo "----------------------------------"
response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d '{
        "model":"grok-2-latest",
        "messages":[{"role":"user","content":"Create a file hello.txt with Hello World"}],
        "tools":[{
            "type":"function",
            "function":{
                "name":"write_file",
                "description":"Write content to a file",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "path":{"type":"string"},
                        "content":{"type":"string"}
                    },
                    "required":["path","content"]
                }
            }
        }],
        "tool_choice":"auto",
        "stream":false
    }')

if echo "$response" | grep -q '"tool_calls"'; then
    echo -e "${GREEN}✓ PASSED - Tool calls detected${NC}"
    echo "$response" | jq -r '.choices[0].message.tool_calls[0].function.name' 2>/dev/null || echo "Tool: (parse error)"
else
    echo -e "${YELLOW}⚠ WARNING - No tool calls (Grok may have responded with text)${NC}"
    echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null | head -3
fi
echo ""

# Test 5: Stream with reasoning
echo "Test 5: Verify streaming with reasoning_content"
echo "------------------------------------------------"
echo "Sending streaming request..."
curl -s -N -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d '{
        "model":"grok-2-latest",
        "messages":[{"role":"user","content":"Count to 3"}],
        "reasoning_effort":"low",
        "stream":true
    }' | head -20 > /tmp/stream_test.txt

if grep -q '"reasoning_content"' /tmp/stream_test.txt; then
    echo -e "${GREEN}✓ PASSED - reasoning_content in stream${NC}"
else
    echo -e "${YELLOW}⚠ INFO - No reasoning_content in stream (may be normal)${NC}"
fi

if grep -q 'data: \[DONE\]' /tmp/stream_test.txt; then
    echo -e "${GREEN}✓ PASSED - Stream completed properly${NC}"
else
    echo -e "${RED}✗ FAILED - Stream did not complete${NC}"
fi
echo ""

# Test 6: Image generation (if available)
echo "Test 6: Verify image generation"
echo "--------------------------------"
response=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d '{
        "model":"grok-imagine-1.0-fast",
        "messages":[{"role":"user","content":"A cute cat"}],
        "stream":false
    }' 2>&1)

if echo "$response" | grep -q 'http.*\.jpg\|http.*\.png\|!\[.*\](http'; then
    echo -e "${GREEN}✓ PASSED - Image URL found${NC}"
elif echo "$response" | grep -q 'model.*not.*found\|does not exist'; then
    echo -e "${YELLOW}⚠ SKIPPED - Image model not available${NC}"
else
    echo -e "${RED}✗ FAILED - No image in response${NC}"
fi
echo ""

# Summary
echo "=================================================="
echo "Test suite completed!"
echo ""
echo "Next steps:"
echo "1. Review any failed tests above"
echo "2. Check logs: docker logs grok2api"
echo "3. Verify config: cat data/config.toml"
echo "4. Test with Pi: Use the API in your IDE"
echo ""
echo "For Pi integration:"
echo "- Set API endpoint: $API_URL"
echo "- Set API key in Pi settings"
echo "- Enable tool calling in Pi"
echo "- Test with: 'Create a file test.txt with Hello'"

#!/bin/bash
# Comprehensive Vision Test - Test all Grok models with vision capability

set -e

BASE_URL="${GROK_API_BASE_URL:-http://localhost:8011}"
OUTPUT_DIR=".grok-resources"
TEST_DIR="grok2api-client/test-results"
TIMESTAMP=$(date +%s)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 Comprehensive Grok Vision Test${NC}"
echo "===================================="
echo ""

# Create test results directory
mkdir -p "$TEST_DIR"

# Test image
IMAGE_PATH="${1:-.grok-resources/images/test_image.png}"

if [ ! -f "$IMAGE_PATH" ]; then
    echo -e "${RED}❌ Image not found: $IMAGE_PATH${NC}"
    exit 1
fi

echo "📷 Test Image: $IMAGE_PATH"
echo ""

# Encode image once
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH")
IMAGE_DATA_URL="data:image/png;base64,$IMAGE_BASE64"

# Models to test
MODELS=(
    "grok-3"
    "grok-3-mini"
    "grok-3-thinking"
    "grok-4"
    "grok-4-thinking"
    "grok-4-heavy"
    "grok-4.1-mini"
    "grok-4.1-fast"
    "grok-4.1-expert"
    "grok-4.1-thinking"
    "grok-4.20-beta"
)

# Test prompts (Vietnamese and English)
PROMPTS=(
    "Mô tả chi tiết bức ảnh này bằng tiếng Việt"
    "Describe this image in detail"
    "What text do you see in this image?"
)

# Results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Start test report
REPORT_FILE="$TEST_DIR/vision-test-comprehensive-${TIMESTAMP}.md"

cat > "$REPORT_FILE" <<EOF
# Grok Vision Comprehensive Test Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Test Image:** $IMAGE_PATH  
**Total Models:** ${#MODELS[@]}  
**Total Prompts:** ${#PROMPTS[@]}

---

## Test Results

EOF

# Test each model with first prompt
echo -e "${BLUE}Testing ${#MODELS[@]} models...${NC}"
echo ""

for MODEL in "${MODELS[@]}"; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${YELLOW}[$TOTAL_TESTS/${#MODELS[@]}] Testing: $MODEL${NC}"
    echo "-------------------------------------------"
    
    PROMPT="${PROMPTS[0]}"  # Use Vietnamese prompt
    
    # Create request
    cat > /tmp/vision_test_${TIMESTAMP}.json <<EOF
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "$PROMPT"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "$IMAGE_DATA_URL"
          }
        }
      ]
    }
  ],
  "stream": false,
  "temperature": 0.8,
  "top_p": 0.95
}
EOF
    
    # Send request
    START_TIME=$(date +%s)
    RESPONSE=$(curl -s -X POST "$BASE_URL/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d @/tmp/vision_test_${TIMESTAMP}.json)
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Check for errors
    if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // .error')
        
        echo -e "${RED}❌ FAILED${NC}"
        echo "Error: $ERROR_MSG"
        echo ""
        
        # Add to report
        cat >> "$REPORT_FILE" <<EOF
### ❌ $MODEL - FAILED

**Prompt:** $PROMPT  
**Duration:** ${DURATION}s  
**Error:** $ERROR_MSG

---

EOF
    else
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Extract response
        CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
        USAGE=$(echo "$RESPONSE" | jq -c '.usage')
        PROMPT_TOKENS=$(echo "$USAGE" | jq -r '.prompt_tokens')
        COMPLETION_TOKENS=$(echo "$USAGE" | jq -r '.completion_tokens')
        
        echo -e "${GREEN}✅ PASSED${NC}"
        echo "Duration: ${DURATION}s"
        echo "Tokens: ${PROMPT_TOKENS} prompt + ${COMPLETION_TOKENS} completion"
        echo ""
        echo "Response preview:"
        echo "$CONTENT" | head -c 200
        echo "..."
        echo ""
        
        # Add to report
        cat >> "$REPORT_FILE" <<EOF
### ✅ $MODEL - PASSED

**Prompt:** $PROMPT  
**Duration:** ${DURATION}s  
**Tokens:** ${PROMPT_TOKENS} prompt + ${COMPLETION_TOKENS} completion

**Response:**
\`\`\`
$CONTENT
\`\`\`

---

EOF
    fi
    
    # Cleanup
    rm -f /tmp/vision_test_${TIMESTAMP}.json
    
    # Rate limiting - wait between requests
    if [ "$MODEL" != "${MODELS[-1]}" ]; then
        echo "⏳ Waiting 2 seconds..."
        sleep 2
        echo ""
    fi
done

# Add summary to report
cat >> "$REPORT_FILE" <<EOF

## Summary

- **Total Tests:** $TOTAL_TESTS
- **Passed:** $PASSED_TESTS ($(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)%)
- **Failed:** $FAILED_TESTS ($(echo "scale=1; $FAILED_TESTS * 100 / $TOTAL_TESTS" | bc)%)

## Supported Models

All Grok chat models support vision through OpenAI-compatible \`image_url\` format:

EOF

for MODEL in "${MODELS[@]}"; do
    echo "- \`$MODEL\`" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" <<EOF

## Usage

### Python Script

\`\`\`bash
python scripts/grok_vision.py \\
  --model grok-4 \\
  --prompt "Mô tả chi tiết bức ảnh này" \\
  --image path/to/image.jpg
\`\`\`

### cURL

\`\`\`bash
curl -X POST http://localhost:8011/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "grok-4",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Describe this image"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
      ]
    }]
  }'
\`\`\`

## Notes

- All Grok chat models support vision capabilities
- Images can be provided as:
  - Base64 data URLs: \`data:image/png;base64,...\`
  - HTTP/HTTPS URLs
  - Local file paths (converted to base64 by client)
- Multiple images can be included in a single request
- Supports Vietnamese and English prompts
- Works with both streaming and non-streaming modes

EOF

# Display final summary
echo ""
echo "============================================"
echo -e "${BLUE}📊 Test Summary${NC}"
echo "============================================"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC} ($(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)%)"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC} ($(echo "scale=1; $FAILED_TESTS * 100 / $TOTAL_TESTS" | bc)%)"
echo ""
echo -e "${GREEN}💾 Report saved to: $REPORT_FILE${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    exit 1
fi

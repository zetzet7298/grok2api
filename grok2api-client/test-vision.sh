#!/bin/bash
# Test Grok Vision Capabilities

set -e

BASE_URL="${GROK_API_BASE_URL:-http://localhost:8011}"
OUTPUT_DIR=".grok-resources"
TIMESTAMP=$(date +%s)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Grok Vision Capabilities${NC}"
echo "=================================="
echo ""

# Test 1: Single image with grok-4
echo -e "${BLUE}Test 1: Single image analysis with grok-4${NC}"
echo "-------------------------------------------"

IMAGE_PATH="${1:-.grok-resources/images/test_image.png}"

if [ ! -f "$IMAGE_PATH" ]; then
    echo -e "${RED}❌ Image not found: $IMAGE_PATH${NC}"
    exit 1
fi

echo "📷 Image: $IMAGE_PATH"
echo "🤖 Model: grok-4"
echo "📝 Prompt: Mô tả chi tiết bức ảnh này bằng tiếng Việt"
echo ""

# Encode image to base64
IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH")
IMAGE_DATA_URL="data:image/png;base64,$IMAGE_BASE64"

# Create request payload
cat > /tmp/vision_request_${TIMESTAMP}.json <<EOF
{
  "model": "grok-4",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Mô tả chi tiết bức ảnh này bằng tiếng Việt"
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

echo "📤 Sending request..."
echo ""

# Send request
RESPONSE=$(curl -s -X POST "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d @/tmp/vision_request_${TIMESTAMP}.json)

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo -e "${RED}❌ Error:${NC}"
    echo "$RESPONSE" | jq '.error'
    exit 1
fi

# Extract and display response
echo -e "${GREEN}✅ Response:${NC}"
echo "============================================"
echo ""
CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
echo "$CONTENT"
echo ""
echo "============================================"

# Save response
mkdir -p "$OUTPUT_DIR/chat"
mkdir -p "$OUTPUT_DIR/metadata"

echo "$CONTENT" > "$OUTPUT_DIR/chat/response_${TIMESTAMP}.txt"
echo "$RESPONSE" | jq '.' > "$OUTPUT_DIR/metadata/chat_${TIMESTAMP}.json"

echo ""
echo -e "${GREEN}💾 Saved to:${NC}"
echo "  - $OUTPUT_DIR/chat/response_${TIMESTAMP}.txt"
echo "  - $OUTPUT_DIR/metadata/chat_${TIMESTAMP}.json"

# Display usage stats
echo ""
echo -e "${BLUE}📊 Usage Stats:${NC}"
echo "$RESPONSE" | jq '.usage'

# Cleanup
rm -f /tmp/vision_request_${TIMESTAMP}.json

echo ""
echo -e "${GREEN}✅ Vision test completed successfully!${NC}"

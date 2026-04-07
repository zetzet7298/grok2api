#!/bin/bash

BASE_URL="${1:-http://localhost:8011}"
API_KEY="${2:-grok2api}"

echo "🖼️  IMAGE API TEST"
echo "=================="
echo ""

PASSED=0
FAILED=0

run_test() {
    local name="$1"
    shift
    echo -n "Testing: $name ... "
    if timeout 30 "$@" > /tmp/test_output.txt 2>&1; then
        echo "✅ PASS"
        ((PASSED++))
        return 0
    else
        echo "❌ FAIL"
        cat /tmp/test_output.txt | tail -3
        ((FAILED++))
        return 1
    fi
}

# Test 1: Basic generation
run_test "Basic (1 image)" \
    python3 scripts/grok_image.py \
    --prompt "test image 1" \
    --n 1 \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

sleep 3

# Test 2: Multiple images
run_test "Multiple (2 images)" \
    python3 scripts/grok_image.py \
    --prompt "test image 2" \
    --n 2 \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

sleep 3

# Test 3: Different size
run_test "Size 1792x1024" \
    python3 scripts/grok_image.py \
    --prompt "test landscape" \
    --size 1792x1024 \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

sleep 3

# Test 4: Fast model
run_test "Fast model" \
    python3 scripts/grok_image.py \
    --prompt "test fast" \
    --model grok-imagine-1.0-fast \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

sleep 3

# Test 5: URL format
run_test "URL format" \
    python3 scripts/grok_image.py \
    --prompt "test url" \
    --response-format url \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

echo ""
echo "=================="
echo "SUMMARY"
echo "=================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

# Count generated images
IMG_COUNT=$(ls -1 .grok-resources/images/*.png 2>/dev/null | wc -l)
echo "Total images: $IMG_COUNT"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  $FAILED test(s) failed"
    exit 1
fi

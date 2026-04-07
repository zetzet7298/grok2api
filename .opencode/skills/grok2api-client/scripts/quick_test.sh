#!/bin/bash

# Quick Test Script for Grok2API Client
# Tests core functionality without overwhelming the API

BASE_URL="${1:-http://localhost:8011}"
API_KEY="${2:-grok2api}"
ADMIN_KEY="${3:-grok2api}"

echo "=========================================="
echo "Grok2API Quick Test"
echo "=========================================="
echo "Server: $BASE_URL"
echo "Time: $(date)"
echo ""

PASSED=0
FAILED=0

# Test function
test_command() {
    local name="$1"
    shift
    echo "Testing: $name"
    if "$@" > /dev/null 2>&1; then
        echo "✅ PASS: $name"
        ((PASSED++))
    else
        echo "❌ FAIL: $name"
        ((FAILED++))
    fi
    echo ""
}

# 1. Connection Test
echo "=========================================="
echo "1. Connection Test"
echo "=========================================="
test_command "Connection" python3 scripts/test_connection.py "$BASE_URL" "$API_KEY"

# 2. Chat Test
echo "=========================================="
echo "2. Chat API Test"
echo "=========================================="
test_command "Chat Basic" python3 scripts/grok_chat.py \
    --message "Say 'OK' and nothing else" \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

# 3. Image Generation Test (just 1)
echo "=========================================="
echo "3. Image Generation Test"
echo "=========================================="
test_command "Image Generation" python3 scripts/grok_image.py \
    --prompt "A simple test image" \
    --n 1 \
    --base-url "$BASE_URL" \
    --api-key "$API_KEY"

# 4. Admin Test
echo "=========================================="
echo "4. Admin API Test"
echo "=========================================="
test_command "Admin - List Tokens" python3 scripts/grok_admin.py \
    --action list-tokens \
    --admin-key "$ADMIN_KEY" \
    --base-url "$BASE_URL"

test_command "Admin - Get Config" python3 scripts/grok_admin.py \
    --action get-config \
    --admin-key "$ADMIN_KEY" \
    --base-url "$BASE_URL"

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    RATE=$((PASSED * 100 / TOTAL))
    echo "Pass Rate: ${RATE}%"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed"
    exit 1
fi

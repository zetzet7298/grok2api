#!/bin/bash
# Check available models in grok2api

API_URL="${API_URL:-http://localhost:8011}"
API_KEY="${API_KEY:-sk-grok2api}"

echo "🔍 Checking available models..."
echo ""

response=$(curl -s -X GET "$API_URL/v1/models" \
    -H "Authorization: Bearer $API_KEY")

echo "$response" | jq -r '.data[] | "- \(.id) (\(.owned_by))"' 2>/dev/null || echo "$response"
echo ""
echo "Use one of these model IDs in your requests."

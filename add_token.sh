#!/bin/bash

# Token SSO từ cookies
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoiMTg2OGNhM2EtOWViNy00OGE0LWE4MmItMmM2Yzc5NTRmNGZmIn0.DS_-Lo3tEkrKIdDUNNtqsS-A1HrD826sa633T4RNiRs"

# Thêm token vào API
curl -X POST "http://localhost:8011/v1/admin/tokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer grok2api" \
  -d "{
    \"ssoBasic\": [
      {
        \"token\": \"$TOKEN\",
        \"note\": \"Added via script\",
        \"tags\": []
      }
    ]
  }"

echo ""
echo "Token đã được thêm!"

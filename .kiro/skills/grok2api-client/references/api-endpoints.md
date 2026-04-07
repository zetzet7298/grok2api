# Grok2API Endpoint Reference

Complete reference for all Grok2API endpoints.

## Base URL

Default: `http://localhost:8011`

## Authentication

Most endpoints support optional Bearer token authentication:

```
Authorization: Bearer YOUR_API_KEY
```

Admin endpoints require admin key (default: `grok2api`).

## Core Endpoints

### List Models

```
GET /v1/models
```

Returns list of available Grok models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "grok-4",
      "object": "model",
      "created": 0,
      "owned_by": "grok2api@chenyme"
    }
  ]
}
```

### Health Check

```
GET /health
```

Check service health status.

## Chat Completions

### Create Chat Completion

```
POST /v1/chat/completions
```

**Request Body:**
```json
{
  "model": "grok-4",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "stream": true,
  "temperature": 0.8,
  "top_p": 0.95,
  "max_tokens": 500,
  "reasoning_effort": "medium"
}
```

**Parameters:**
- `model` (required): Model name
- `messages` (required): Array of message objects
- `stream` (optional): Enable streaming (default: true)
- `temperature` (optional): 0-2, controls randomness (default: 0.8)
- `top_p` (optional): 0-1, nucleus sampling (default: 0.95)
- `max_tokens` (optional): Maximum tokens to generate
- `reasoning_effort` (optional): none/minimal/low/medium/high/xhigh (for thinking models)
- `tools` (optional): Tool definitions for function calling
- `tool_choice` (optional): auto/required/none or specific function

**Streaming Response:**
```
data: {"choices":[{"delta":{"content":"Hello"}}]}
data: {"choices":[{"delta":{"content":" there"}}]}
data: [DONE]
```

**Non-Streaming Response:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "grok-4",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello there! How can I help you?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Image Generation

### Generate Images

```
POST /v1/images/generations
```

**Request Body:**
```json
{
  "model": "grok-imagine-1.0",
  "prompt": "A futuristic cyberpunk city at night",
  "n": 1,
  "size": "1024x1024",
  "response_format": "url",
  "stream": false
}
```

**Parameters:**
- `model` (required): grok-imagine-1.0 or grok-imagine-1.0-fast
- `prompt` (required): Image description
- `n` (optional): Number of images (1-10, default: 1)
- `size` (optional): 1280x720, 720x1280, 1792x1024, 1024x1792, 1024x1024
- `response_format` (optional): url, b64_json, or base64
- `stream` (optional): Enable streaming (only n=1 or n=2)

**Response:**
```json
{
  "created": 1234567890,
  "data": [
    {"url": "https://..."},
    {"b64_json": "iVBORw0KGgo..."}
  ],
  "usage": {
    "total_tokens": 0
  }
}
```

### Edit Images

```
POST /v1/images/edits
Content-Type: multipart/form-data
```

**Form Data:**
- `prompt` (required): Edit description
- `image` (required): Image file(s)
- `model` (optional): grok-imagine-1.0-edit
- `n` (optional): Number of variations (1-10)
- `size` (optional): Output dimensions
- `response_format` (optional): url, b64_json, or base64

**Response:** Same as image generation

## Video Generation

### Create Video

```
POST /v1/videos
```

**Request Body:**
```json
{
  "model": "grok-imagine-1.0-video",
  "prompt": "A cat walking through a cyberpunk city",
  "size": "16:9",
  "seconds": 10,
  "quality": "high",
  "image_reference": [
    {"type": "image_url", "image_url": {"url": "https://..."}}
  ]
}
```

**Parameters:**
- `model` (required): grok-imagine-1.0-video
- `prompt` (required): Video description
- `size` (optional): 16:9, 9:16, 3:2, 2:3, 1:1 (default: 16:9)
- `seconds` (optional): 6-30 (default: 6)
- `quality` (optional): standard (480p) or high (720p)
- `image_reference` (optional): Array of image references

**Response:**
```json
{
  "id": "video_...",
  "object": "video",
  "created_at": 1234567890,
  "completed_at": 1234567890,
  "status": "completed",
  "model": "grok-imagine-1.0-video",
  "prompt": "...",
  "size": "16:9",
  "seconds": "10",
  "quality": "high",
  "url": "https://..."
}
```

## Admin Endpoints

All admin endpoints require admin key authentication.

### List Tokens

```
GET /v1/admin/tokens
Authorization: Bearer ADMIN_KEY
```

Returns all tokens in the pool.

### Add Token

```
POST /v1/admin/tokens
Authorization: Bearer ADMIN_KEY
Content-Type: application/json

{
  "token": "eyJ...",
  "pool": "ssoBasic",
  "note": "My token"
}
```

### Refresh Tokens

```
POST /v1/admin/tokens/refresh
Authorization: Bearer ADMIN_KEY
```

Manually refresh all tokens.

### Enable NSFW

```
POST /v1/admin/tokens/nsfw/enable
Authorization: Bearer ADMIN_KEY
Content-Type: application/json

{
  "tokens": ["token1", "token2"],
  "async": false
}
```

### Get Configuration

```
GET /v1/admin/config
Authorization: Bearer ADMIN_KEY
```

### Update Configuration

```
POST /v1/admin/config
Authorization: Bearer ADMIN_KEY
Content-Type: application/json

{
  "proxy": {
    "cf_cookies": "__cf_bm=..."
  }
}
```

### Get Cache Info

```
GET /v1/admin/cache
Authorization: Bearer ADMIN_KEY
```

### List Cache Items

```
GET /v1/admin/cache/list
Authorization: Bearer ADMIN_KEY
```

### Clear Local Cache

```
POST /v1/admin/cache/clear
Authorization: Bearer ADMIN_KEY
Content-Type: application/json

{
  "type": "image"
}
```

Types: `image`, `video`, `all`

### Clear Online Cache

```
POST /v1/admin/cache/online/clear
Authorization: Bearer ADMIN_KEY
Content-Type: application/json

{
  "tokens": ["token1", "token2"]
}
```

## File Endpoints

### Get Image

```
GET /v1/files/image/{filename}
```

Retrieve cached image file.

### Get Video

```
GET /v1/files/video/{filename}
```

Retrieve cached video file.

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": {
    "message": "Error description",
    "type": "invalid_request_error",
    "code": "invalid_parameter"
  }
}
```

**Common Error Codes:**
- `model_not_found` - Invalid model name
- `invalid_parameter` - Invalid parameter value
- `rate_limit_exceeded` - No available tokens
- `empty_prompt` - Missing or empty prompt
- `invalid_size` - Invalid image/video size
- `missing_image` - Image required but not provided

## Rate Limits

Rate limits depend on available tokens in the pool. When no tokens are available, requests will return `rate_limit_exceeded` error.

## Streaming

Streaming responses use Server-Sent Events (SSE) format:

```
event: message
data: {"type": "content", "content": "Hello"}

event: done
data: [DONE]
```

For errors during streaming:

```
event: error
data: {"error": {"message": "...", "code": "..."}}
```

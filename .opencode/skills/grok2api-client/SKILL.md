---
name: grok2api-client
description: Interact with Grok2API reverse proxy for chat, image generation, image editing, video generation, and admin management. Use this skill whenever working with Grok AI models, generating images or videos, managing API tokens, or integrating Grok capabilities into applications. Automatically handles API calls via curl and saves all responses (text, images, videos) to .grok-resources folder for easy access.
---

# Grok2API Client Skill

This skill provides complete access to Grok2API, a reverse proxy for Grok AI services. Use it to chat with Grok models, generate and edit images, create videos, and manage the API infrastructure.

## When to Use This Skill

Activate this skill when the user mentions:
- Chatting with Grok models (grok-3, grok-4, grok-4.1, etc.)
- Generating images with Grok Imagine
- Editing images
- Creating videos from text or images
- Managing API tokens or configuration
- Testing or debugging Grok API endpoints
- Integrating Grok capabilities into their application

## Core Capabilities

### 1. Chat Completions

Chat with various Grok models using OpenAI-compatible API:

**Available Models:**
- `grok-3` - Standard Grok 3
- `grok-3-mini` - Faster, lightweight version
- `grok-3-thinking` - With chain-of-thought reasoning
- `grok-4` - Latest Grok 4
- `grok-4-thinking` - Grok 4 with reasoning
- `grok-4-heavy` - Most powerful version
- `grok-4.1-mini`, `grok-4.1-fast`, `grok-4.1-expert`, `grok-4.1-thinking`
- `grok-4.20-beta` - Beta version

**Key Parameters:**
- `model` - Model name (required)
- `messages` - Array of message objects with `role` and `content`
- `stream` - Boolean for streaming responses (default: true)
- `temperature` - 0-2, controls randomness (default: 0.8)
- `top_p` - 0-1, nucleus sampling (default: 0.95)
- `max_tokens` - Maximum tokens to generate
- `reasoning_effort` - For thinking models: none/minimal/low/medium/high/xhigh

**Example Usage:**
```bash
python scripts/grok_chat.py \
  --model grok-4 \
  --message "Explain quantum computing in simple terms" \
  --stream
```

### 2. Image Generation

Generate images using Grok Imagine models:

**Available Models:**
- `grok-imagine-1.0` - Standard image generation
- `grok-imagine-1.0-fast` - Faster, supports multiple images (n=1-10)

**Key Parameters:**
- `prompt` - Image description (required)
- `n` - Number of images to generate (1-10)
- `size` - Image dimensions: 1280x720, 720x1280, 1792x1024, 1024x1792, 1024x1024
- `response_format` - url, b64_json, or base64
- `stream` - Boolean for streaming (only n=1 or n=2)

**Example Usage:**
```bash
python scripts/grok_image.py \
  --prompt "A futuristic cyberpunk city at night with neon lights" \
  --model grok-imagine-1.0-fast \
  --n 4 \
  --size 1024x1024
```

### 3. Image Editing

Edit existing images with text prompts:

**Model:** `grok-imagine-1.0-edit`

**Key Parameters:**
- `prompt` - Edit description (required)
- `image` - Path to image file or URL (required)
- `n` - Number of variations (1-10)
- `size` - Output dimensions

**Example Usage:**
```bash
python scripts/grok_image_edit.py \
  --prompt "Change the background to a sunset beach" \
  --image path/to/image.jpg \
  --n 2
```

### 4. Video Generation

Create videos from text prompts or images:

**Model:** `grok-imagine-1.0-video`

**Key Parameters:**
- `prompt` - Video description (required)
- `image_url` - Optional image reference(s)
- `aspect_ratio` - 16:9, 9:16, 3:2, 2:3, 1:1
- `seconds` - Video length 6-30 seconds
- `quality` - standard (480p) or high (720p)

**Example Usage:**
```bash
python scripts/grok_video.py \
  --prompt "A cat walking through a cyberpunk city street" \
  --aspect-ratio 16:9 \
  --seconds 10 \
  --quality high
```

### 5. Admin Management

Manage API tokens, configuration, and cache:

**Available Operations:**
- List tokens: `GET /v1/admin/tokens`
- Add token: `POST /v1/admin/tokens`
- Refresh tokens: `POST /v1/admin/tokens/refresh`
- Enable NSFW: `POST /v1/admin/tokens/nsfw/enable`
- Get/Update config: `GET/POST /v1/admin/config`
- Cache management: `/v1/admin/cache/*`

**Example Usage:**
```bash
python scripts/grok_admin.py \
  --action list-tokens \
  --admin-key grok2api
```

## Output Management

All API responses are automatically saved to `.grok-resources/` folder:

- **Chat responses:** `.grok-resources/chat/response_<timestamp>.txt`
- **Images:** `.grok-resources/images/<filename>.png`
- **Videos:** `.grok-resources/videos/<filename>.mp4`
- **Metadata:** `.grok-resources/metadata/<request_id>.json`

The scripts handle:
- Creating the folder structure automatically
- Downloading images/videos from URLs
- Decoding base64 responses
- Saving request/response metadata
- Organizing by type and timestamp

## Configuration

### Environment Setup

The skill expects these environment variables (or uses defaults):

```bash
export GROK_API_BASE_URL="http://localhost:8011"
export GROK_API_KEY="your-api-key"  # Optional if not required
export GROK_ADMIN_KEY="grok2api"    # For admin operations
```

### Quick Start

1. Ensure Grok2API server is running (default: http://localhost:8011)
2. Set environment variables or use script parameters
3. Run any script with `--help` to see all options
4. Check `.grok-resources/` for outputs

## Script Reference

All scripts are in the `scripts/` directory:

- `grok_chat.py` - Chat completions
- `grok_image.py` - Image generation
- `grok_image_edit.py` - Image editing
- `grok_video.py` - Video generation
- `grok_admin.py` - Admin operations
- `grok_api.py` - Generic API caller (for any endpoint)

Each script supports:
- `--help` - Show all options
- `--base-url` - Override API base URL
- `--api-key` - Provide API key
- `--output-dir` - Custom output directory (default: .grok-resources)
- `--verbose` - Detailed logging

## Advanced Usage

### Streaming Responses

For chat and image generation, use `--stream` to get real-time updates:

```bash
python scripts/grok_chat.py \
  --model grok-4-thinking \
  --message "Solve this complex problem step by step" \
  --stream \
  --reasoning-effort high
```

### Batch Operations

Generate multiple images in one call:

```bash
python scripts/grok_image.py \
  --prompt "Various cyberpunk scenes" \
  --model grok-imagine-1.0-fast \
  --n 10 \
  --batch
```

### Custom API Calls

For endpoints not covered by specific scripts:

```bash
python scripts/grok_api.py \
  --method POST \
  --endpoint /v1/models \
  --output models.json
```

## Error Handling

The scripts handle common errors gracefully:

- **No API key:** Uses unauthenticated access if allowed
- **Rate limits:** Retries with exponential backoff
- **Network errors:** Saves partial responses
- **Invalid parameters:** Shows clear error messages with valid options

## Tips for Best Results

1. **Chat:** Use thinking models for complex reasoning tasks
2. **Images:** Use grok-imagine-1.0-fast for multiple variations
3. **Videos:** Start with 6-10 seconds for faster generation
4. **Streaming:** Always use streaming for long-running operations
5. **Output:** Check `.grok-resources/metadata/` for request details

## API Endpoint Reference

See `references/api-endpoints.md` for complete endpoint documentation including:
- Full parameter lists
- Request/response examples
- Error codes
- Rate limits
- Authentication requirements

## Troubleshooting

**Server not responding:**
```bash
curl http://localhost:8011/health
```

**Check available models:**
```bash
python scripts/grok_api.py --endpoint /v1/models
```

**View logs:**
```bash
tail -f .grok-resources/logs/grok-client.log
```

**Clear cache:**
```bash
python scripts/grok_admin.py --action clear-cache --type all
```

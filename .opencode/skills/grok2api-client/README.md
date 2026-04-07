# Grok2API Client Skill

Complete command-line client for interacting with Grok2API reverse proxy.

## Quick Start

```bash
# Chat with Grok
python scripts/grok_chat.py --model grok-4 --message "Hello, explain AI"

# Generate images
python scripts/grok_image.py --prompt "A futuristic city" --n 4

# Create video
python scripts/grok_video.py --prompt "A cat in cyberpunk city" --seconds 10

# Admin operations
python scripts/grok_admin.py --action list-tokens
```

## Installation

### Requirements

```bash
pip install requests
```

### Environment Variables (Optional)

```bash
export GROK_API_BASE_URL="http://localhost:8011"
export GROK_API_KEY="your-api-key"
export GROK_ADMIN_KEY="grok2api"
export GROK_OUTPUT_DIR=".grok-resources"
```

## Available Scripts

### 1. grok_chat.py - Chat Completions

```bash
# Basic chat
python scripts/grok_chat.py --model grok-4 --message "Hello"

# With system prompt
python scripts/grok_chat.py \
  --model grok-3-mini \
  --system "You are a coding assistant" \
  --message "Explain Python decorators"

# Thinking model with reasoning
python scripts/grok_chat.py \
  --model grok-4-thinking \
  --message "Solve this complex problem" \
  --reasoning-effort high

# Non-streaming
python scripts/grok_chat.py \
  --model grok-4 \
  --message "Quick question" \
  --no-stream
```

### 2. grok_image.py - Image Generation

```bash
# Single image
python scripts/grok_image.py \
  --prompt "A futuristic cyberpunk city at night"

# Multiple images
python scripts/grok_image.py \
  --prompt "Various sci-fi landscapes" \
  --model grok-imagine-1.0-fast \
  --n 4

# Custom size
python scripts/grok_image.py \
  --prompt "Portrait of a robot" \
  --size 1024x1792

# Base64 format
python scripts/grok_image.py \
  --prompt "Abstract art" \
  --response-format b64_json

# Streaming
python scripts/grok_image.py \
  --prompt "Landscape" \
  --stream
```

### 3. grok_video.py - Video Generation

```bash
# Basic video
python scripts/grok_video.py \
  --prompt "A cat walking through a cyberpunk city"

# Custom settings
python scripts/grok_video.py \
  --prompt "Cinematic drone shot of mountains" \
  --aspect-ratio 16:9 \
  --seconds 10 \
  --quality high

# From image
python scripts/grok_video.py \
  --prompt "Animate this scene with movement" \
  --image-url https://example.com/image.jpg
```

### 4. grok_admin.py - Admin Management

```bash
# List tokens
python scripts/grok_admin.py --action list-tokens

# Add token
python scripts/grok_admin.py \
  --action add-token \
  --token "eyJ..." \
  --pool ssoBasic \
  --note "My token"

# Refresh tokens
python scripts/grok_admin.py --action refresh-tokens

# Get configuration
python scripts/grok_admin.py --action get-config

# Cache info
python scripts/grok_admin.py --action cache-info

# Clear cache
python scripts/grok_admin.py \
  --action clear-cache \
  --cache-type image
```

## Output Structure

All outputs are saved to `.grok-resources/` (or custom directory):

```
.grok-resources/
├── chat/
│   ├── response_1234567890.txt
│   └── response_1234567891.txt
├── images/
│   ├── image_1234567890_0.png
│   ├── image_1234567890_1.png
│   └── image_1234567891_0.png
├── videos/
│   ├── video_1234567890.mp4
│   └── video_1234567891.mp4
└── metadata/
    ├── chat_1234567890.json
    ├── images_1234567890.json
    └── video_1234567890.json
```

## Available Models

### Chat Models
- `grok-3` - Standard Grok 3
- `grok-3-mini` - Faster, lightweight
- `grok-3-thinking` - With reasoning
- `grok-4` - Latest Grok 4
- `grok-4-thinking` - Grok 4 with reasoning
- `grok-4-heavy` - Most powerful
- `grok-4.1-mini` - Grok 4.1 Mini
- `grok-4.1-fast` - Grok 4.1 Fast
- `grok-4.1-expert` - Grok 4.1 Expert
- `grok-4.1-thinking` - Grok 4.1 with reasoning
- `grok-4.20-beta` - Beta version

### Image Models
- `grok-imagine-1.0` - Standard image generation
- `grok-imagine-1.0-fast` - Faster, multiple images
- `grok-imagine-1.0-edit` - Image editing

### Video Model
- `grok-imagine-1.0-video` - Video generation

## Common Options

All scripts support these common options:

- `--base-url` - API base URL (default: http://localhost:8011)
- `--api-key` - API authentication key
- `--output-dir` - Custom output directory
- `--help` - Show detailed help

## Tips

1. **Use streaming** for long-running operations (chat, image generation)
2. **Check metadata files** for request details and debugging
3. **Use thinking models** for complex reasoning tasks
4. **Generate multiple images** with grok-imagine-1.0-fast
5. **Start with shorter videos** (6-10s) for faster generation

## Troubleshooting

### Server not responding

```bash
curl http://localhost:8011/health
```

### Check available models

```bash
curl http://localhost:8011/v1/models
```

### View detailed errors

Add `--verbose` flag to any script (if supported) or check metadata files.

### Permission denied

Make scripts executable:

```bash
chmod +x scripts/*.py
```

## API Reference

See `references/api-endpoints.md` for complete API documentation.

## Examples

### Complete Workflow

```bash
# 1. Generate an image
python scripts/grok_image.py \
  --prompt "A robot in a futuristic city" \
  --size 1024x1024

# 2. Use that image to create a video
python scripts/grok_video.py \
  --prompt "The robot walks through the city" \
  --image-url .grok-resources/images/image_*.png \
  --seconds 10

# 3. Chat about the results
python scripts/grok_chat.py \
  --model grok-4 \
  --message "Describe what makes a good cyberpunk aesthetic"
```

### Batch Image Generation

```bash
# Generate 10 variations
for i in {1..10}; do
  python scripts/grok_image.py \
    --prompt "Cyberpunk scene variation $i" \
    --model grok-imagine-1.0-fast \
    --n 1
done
```

## License

This skill is part of the Grok2API project.

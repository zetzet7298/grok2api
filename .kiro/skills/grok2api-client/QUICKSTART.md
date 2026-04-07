# Quick Start Guide

Get started with Grok2API Client in 5 minutes.

## Prerequisites

1. **Grok2API server running** (default: http://localhost:8011)
2. **Python 3.7+** installed
3. **requests library**: `pip install requests`

## Step 1: Test Connection

```bash
cd grok2api-client
python scripts/test_connection.py
```

You should see:
```
✅ Health check passed
✅ Models endpoint accessible (11 models available)
🎉 Connection test successful!
```

## Step 2: Your First Chat

```bash
python scripts/grok_chat.py \
  --model grok-4 \
  --message "Explain AI in one sentence"
```

Response will be:
- Printed to console
- Saved to `.grok-resources/chat/response_*.txt`
- Metadata saved to `.grok-resources/metadata/chat_*.json`

## Step 3: Generate an Image

```bash
python scripts/grok_image.py \
  --prompt "A futuristic cyberpunk city at night with neon lights" \
  --model grok-imagine-1.0-fast \
  --n 2
```

Images will be saved to `.grok-resources/images/`

## Step 4: Create a Video

```bash
python scripts/grok_video.py \
  --prompt "A cat walking through a neon-lit street" \
  --aspect-ratio 16:9 \
  --seconds 6
```

Video will be downloaded to `.grok-resources/videos/`

## Step 5: Check Your Outputs

```bash
ls -lh .grok-resources/
```

You'll see:
```
.grok-resources/
├── chat/          # Chat responses
├── images/        # Generated images
├── videos/        # Generated videos
└── metadata/      # Request metadata
```

## Common Use Cases

### 1. Quick Question

```bash
python scripts/grok_chat.py --model grok-4 --message "What is 2+2?" --no-stream
```

### 2. Thinking Task

```bash
python scripts/grok_chat.py \
  --model grok-4-thinking \
  --message "Solve this step by step: If a train travels 120km in 2 hours, what's its speed?" \
  --reasoning-effort high
```

### 3. Multiple Image Variations

```bash
python scripts/grok_image.py \
  --prompt "Abstract geometric patterns" \
  --model grok-imagine-1.0-fast \
  --n 6 \
  --size 1024x1024
```

### 4. High Quality Video

```bash
python scripts/grok_video.py \
  --prompt "Cinematic drone shot of mountains at sunset" \
  --aspect-ratio 16:9 \
  --seconds 10 \
  --quality high
```

### 5. Admin Tasks

```bash
# Check available tokens
python scripts/grok_admin.py --action list-tokens

# Get cache info
python scripts/grok_admin.py --action cache-info

# Clear image cache
python scripts/grok_admin.py --action clear-cache --cache-type image
```

## Environment Setup (Optional)

Create a `.env` file or export variables:

```bash
export GROK_API_BASE_URL="http://localhost:8011"
export GROK_API_KEY="your-api-key-if-needed"
export GROK_ADMIN_KEY="grok2api"
export GROK_OUTPUT_DIR=".grok-resources"
```

Then you don't need to pass `--base-url` every time.

## Troubleshooting

### "Connection refused"

Server not running. Start Grok2API:
```bash
# In the main project directory
python -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

### "No module named 'requests'"

Install dependencies:
```bash
pip install requests
```

### "Permission denied"

Make scripts executable:
```bash
chmod +x scripts/*.py
```

### Check server health

```bash
curl http://localhost:8011/health
curl http://localhost:8011/v1/models
```

## Next Steps

- Read `SKILL.md` for complete documentation
- Check `references/api-endpoints.md` for API details
- See `README.md` for advanced examples
- Explore `.grok-resources/metadata/` for request details

## Tips

1. **Always use streaming** for chat and image generation (faster feedback)
2. **Check metadata files** if something goes wrong
3. **Use thinking models** for complex reasoning
4. **Start with 6-second videos** (faster generation)
5. **Use grok-imagine-1.0-fast** for multiple image variations

## Getting Help

Run any script with `--help`:

```bash
python scripts/grok_chat.py --help
python scripts/grok_image.py --help
python scripts/grok_video.py --help
python scripts/grok_admin.py --help
```

Happy coding! 🚀

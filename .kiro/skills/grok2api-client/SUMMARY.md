# Grok2API Client Skill - Summary

## Overview

Complete command-line client skill for interacting with Grok2API reverse proxy. Provides easy access to all Grok AI capabilities including chat, image generation, image editing, video creation, and admin management.

## Key Features

✅ **Chat with Grok Models** - All Grok 3, 4, and 4.1 variants including thinking models
✅ **Image Generation** - Create images with Grok Imagine (single or batch)
✅ **Image Editing** - Edit existing images with text prompts
✅ **Video Creation** - Generate videos from text or images
✅ **Admin Management** - Token management, configuration, cache control
✅ **Automatic Output Management** - All responses saved to `.grok-resources/`
✅ **Streaming Support** - Real-time responses for chat and images
✅ **Metadata Tracking** - Complete request/response logging

## File Structure

```
grok2api-client/
├── SKILL.md                    # Main skill documentation
├── README.md                   # User guide
├── QUICKSTART.md               # 5-minute getting started
├── SUMMARY.md                  # This file
├── scripts/
│   ├── grok_chat.py           # Chat completions
│   ├── grok_image.py          # Image generation
│   ├── grok_video.py          # Video generation
│   ├── grok_admin.py          # Admin operations
│   └── test_connection.py     # Connection tester
├── references/
│   └── api-endpoints.md       # Complete API reference
└── evals/
    └── evals.json             # Test cases
```

## Quick Examples

### Chat
```bash
python scripts/grok_chat.py --model grok-4 --message "Hello"
```

### Image
```bash
python scripts/grok_image.py --prompt "Cyberpunk city" --n 4
```

### Video
```bash
python scripts/grok_video.py --prompt "Cat walking" --seconds 10
```

### Admin
```bash
python scripts/grok_admin.py --action list-tokens
```

## Output Structure

All outputs automatically saved to:

```
.grok-resources/
├── chat/          # Text responses
├── images/        # Generated images (PNG)
├── videos/        # Generated videos (MP4)
└── metadata/      # Request/response metadata (JSON)
```

## Supported Models

**Chat:** grok-3, grok-3-mini, grok-3-thinking, grok-4, grok-4-thinking, grok-4-heavy, grok-4.1-mini, grok-4.1-fast, grok-4.1-expert, grok-4.1-thinking, grok-4.20-beta

**Image:** grok-imagine-1.0, grok-imagine-1.0-fast, grok-imagine-1.0-edit

**Video:** grok-imagine-1.0-video

## Requirements

- Python 3.7+
- requests library (`pip install requests`)
- Grok2API server running (default: http://localhost:8011)

## When to Use This Skill

Use this skill when you need to:
- Chat with Grok AI models
- Generate images or videos
- Edit images with AI
- Manage API tokens and configuration
- Test Grok API endpoints
- Integrate Grok capabilities into applications
- Automate Grok API workflows

## Key Advantages

1. **Simple CLI Interface** - No need to write curl commands
2. **Automatic File Management** - Downloads and saves everything
3. **Streaming Support** - Real-time feedback for long operations
4. **Complete Metadata** - Every request logged for debugging
5. **Error Handling** - Clear error messages and troubleshooting
6. **Flexible Configuration** - Environment variables or CLI args
7. **Production Ready** - Handles rate limits, retries, timeouts

## Documentation

- **SKILL.md** - Complete skill documentation
- **README.md** - Detailed usage guide with examples
- **QUICKSTART.md** - Get started in 5 minutes
- **api-endpoints.md** - Full API reference

## Testing

Test cases in `evals/evals.json` cover:
1. Chat completion with response saving
2. Multiple image generation
3. Video creation with custom parameters

## License

Part of Grok2API project by @chenyme

# Grok2API Client Skill - File Index

Quick reference to all files in this skill.

## 📚 Documentation Files

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[INSTALL.md](INSTALL.md)** - Installation instructions
- **[README.md](README.md)** - Complete user guide with examples

### Reference
- **[SKILL.md](SKILL.md)** - Main skill documentation (read this first!)
- **[SUMMARY.md](SUMMARY.md)** - Quick overview
- **[references/api-endpoints.md](references/api-endpoints.md)** - Complete API reference

### Meta
- **[INDEX.md](INDEX.md)** - This file
- **[.skillinfo](.skillinfo)** - Skill metadata

## 🔧 Scripts

All scripts in `scripts/` directory:

### Core Scripts
1. **[grok_chat.py](scripts/grok_chat.py)** (270 lines)
   - Chat with Grok models
   - Supports streaming and non-streaming
   - All model variants (3, 4, 4.1)
   - Reasoning effort control

2. **[grok_image.py](scripts/grok_image.py)** (246 lines)
   - Generate images with Grok Imagine
   - Single or batch generation (n=1-10)
   - Multiple sizes and formats
   - Streaming support

3. **[grok_video.py](scripts/grok_video.py)** (194 lines)
   - Create videos from text or images
   - Custom aspect ratios and duration
   - Quality control (480p/720p)
   - Automatic download

4. **[grok_admin.py](scripts/grok_admin.py)** (199 lines)
   - Token management
   - Configuration control
   - Cache operations
   - Admin authentication

### Utility Scripts
5. **[test_connection.py](scripts/test_connection.py)** (77 lines)
   - Test API connectivity
   - List available models
   - Health check
   - Quick diagnostics

## 🧪 Test Files

- **[evals/evals.json](evals/evals.json)** - Test cases for skill validation
  - Chat completion test
  - Image generation test
  - Video creation test

## 📖 How to Use This Index

### For First-Time Users
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Run [test_connection.py](scripts/test_connection.py)
3. Try examples from [README.md](README.md)

### For Developers
1. Read [SKILL.md](SKILL.md) for architecture
2. Check [api-endpoints.md](references/api-endpoints.md) for API details
3. Review script source code for implementation

### For Troubleshooting
1. Check [INSTALL.md](INSTALL.md) for setup issues
2. Review [api-endpoints.md](references/api-endpoints.md) for error codes
3. Examine `.grok-resources/metadata/` for request logs

## 📊 Statistics

- **Total Files:** 14
- **Python Scripts:** 5 (986 lines)
- **Documentation:** 6 (1,488 lines)
- **Test Cases:** 3 scenarios
- **Supported Models:** 11+ Grok variants
- **API Endpoints:** 20+ endpoints covered

## 🎯 Quick Command Reference

```bash
# Test connection
python scripts/test_connection.py

# Chat
python scripts/grok_chat.py --model grok-4 --message "Hello"

# Image
python scripts/grok_image.py --prompt "Cyberpunk city" --n 4

# Video
python scripts/grok_video.py --prompt "Cat walking" --seconds 10

# Admin
python scripts/grok_admin.py --action list-tokens

# Help
python scripts/grok_chat.py --help
```

## 🔗 Related Files

### In Main Project
- `Grok2API.postman_collection.json` - Postman collection
- `app/api/v1/chat.py` - Chat API implementation
- `app/api/v1/image.py` - Image API implementation
- `app/api/v1/video.py` - Video API implementation

### Generated Outputs
- `.grok-resources/chat/` - Chat responses
- `.grok-resources/images/` - Generated images
- `.grok-resources/videos/` - Generated videos
- `.grok-resources/metadata/` - Request metadata

## 📝 File Purposes

| File | Purpose | Lines | Type |
|------|---------|-------|------|
| SKILL.md | Main documentation | 275 | Doc |
| README.md | User guide | 270 | Doc |
| QUICKSTART.md | Quick start | 195 | Doc |
| INSTALL.md | Installation | 231 | Doc |
| SUMMARY.md | Overview | 123 | Doc |
| api-endpoints.md | API reference | 394 | Doc |
| grok_chat.py | Chat script | 270 | Code |
| grok_image.py | Image script | 246 | Code |
| grok_video.py | Video script | 194 | Code |
| grok_admin.py | Admin script | 199 | Code |
| test_connection.py | Test script | 77 | Code |
| evals.json | Test cases | - | Data |
| .skillinfo | Metadata | - | Meta |
| INDEX.md | This file | - | Doc |

## 🚀 Next Steps

After reviewing this index:
1. Choose your starting point based on your needs
2. Follow the documentation in order
3. Try the examples
4. Explore the scripts
5. Check the API reference for details

## 💡 Tips

- All scripts have `--help` flag
- Documentation is cross-referenced
- Examples are copy-paste ready
- Scripts are self-contained
- Outputs are automatically organized

---

**Last Updated:** 2026-04-07
**Skill Version:** 1.0.0

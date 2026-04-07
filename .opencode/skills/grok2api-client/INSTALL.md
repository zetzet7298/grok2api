# Installation Guide

## Prerequisites

### 1. Python

Requires Python 3.7 or higher.

Check your Python version:
```bash
python --version
# or
python3 --version
```

### 2. Grok2API Server

The Grok2API server must be running. Default URL: `http://localhost:8011`

To start the server (from main project directory):
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

Or with Docker:
```bash
docker-compose up -d
```

## Installation Steps

### Step 1: Install Dependencies

```bash
pip install requests
```

Or if using pip3:
```bash
pip3 install requests
```

### Step 2: Make Scripts Executable (Linux/Mac)

```bash
chmod +x grok2api-client/scripts/*.py
```

### Step 3: Test Connection

```bash
python grok2api-client/scripts/test_connection.py
```

Expected output:
```
✅ Health check passed
✅ Models endpoint accessible (11 models available)
🎉 Connection test successful!
```

### Step 4: Set Environment Variables (Optional)

Create a `.env` file or add to your shell profile:

```bash
export GROK_API_BASE_URL="http://localhost:8011"
export GROK_API_KEY=""  # Optional, if authentication required
export GROK_ADMIN_KEY="grok2api"
export GROK_OUTPUT_DIR=".grok-resources"
```

For bash/zsh, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export GROK_API_BASE_URL="http://localhost:8011"' >> ~/.bashrc
source ~/.bashrc
```

## Verify Installation

### Test Chat

```bash
python grok2api-client/scripts/grok_chat.py \
  --model grok-4 \
  --message "Hello, this is a test" \
  --no-stream
```

### Test Image Generation

```bash
python grok2api-client/scripts/grok_image.py \
  --prompt "A simple test image" \
  --n 1
```

### Check Output Directory

```bash
ls -la .grok-resources/
```

You should see:
```
.grok-resources/
├── chat/
├── images/
├── metadata/
└── videos/
```

## Troubleshooting

### "requests library not found"

```bash
pip install requests
# or
pip3 install requests
# or
python -m pip install requests
```

### "Connection refused"

Server not running. Start it:
```bash
# From main project directory
python -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

### "Permission denied" (Linux/Mac)

Make scripts executable:
```bash
chmod +x grok2api-client/scripts/*.py
```

### "Module not found" errors

Ensure you're in the correct directory:
```bash
pwd  # Should show the project root
ls grok2api-client/scripts/  # Should list the scripts
```

### Custom Server URL

If your server runs on a different URL:
```bash
python grok2api-client/scripts/test_connection.py http://your-server:port
```

Or set environment variable:
```bash
export GROK_API_BASE_URL="http://your-server:port"
```

## Platform-Specific Notes

### Windows

Use `python` instead of `python3`:
```bash
python grok2api-client\scripts\test_connection.py
```

Environment variables:
```cmd
set GROK_API_BASE_URL=http://localhost:8011
```

Or PowerShell:
```powershell
$env:GROK_API_BASE_URL="http://localhost:8011"
```

### Linux/Mac

Scripts should work with shebang:
```bash
./grok2api-client/scripts/test_connection.py
```

### Docker

If running in Docker, ensure network connectivity:
```bash
docker run --network host your-container
```

## Next Steps

After successful installation:

1. Read [QUICKSTART.md](QUICKSTART.md) for basic usage
2. Check [README.md](README.md) for detailed examples
3. See [SKILL.md](SKILL.md) for complete documentation

## Uninstallation

To remove:

```bash
# Remove the skill directory
rm -rf grok2api-client/

# Remove output directory
rm -rf .grok-resources/

# Uninstall dependencies (if not needed elsewhere)
pip uninstall requests
```

## Getting Help

If you encounter issues:

1. Check server is running: `curl http://localhost:8011/health`
2. Verify Python version: `python --version`
3. Check dependencies: `pip list | grep requests`
4. Review error messages in `.grok-resources/metadata/`
5. Run with verbose output (if script supports it)

## Support

For issues with:
- **Grok2API server**: Check main project documentation
- **Scripts**: Review script help with `--help` flag
- **API errors**: See `references/api-endpoints.md`

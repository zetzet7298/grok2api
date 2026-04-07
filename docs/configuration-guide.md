# Grok2API Configuration Guide

Complete guide to all configuration options available in Grok2API.

## Configuration Management

Grok2API uses a hierarchical configuration system:

1. **config.defaults.toml** - Default baseline configuration
2. **data/config.toml** - Runtime configuration (auto-created)
3. **Admin UI** - Web interface at http://localhost:8011/admin/config
4. **API Endpoint** - `/v1/admin/config` for programmatic access

## Accessing Configuration

### Web Interface

```
http://localhost:8011/admin/config
```

Login with admin key (default: `grok2api`)

### API Access

```bash
# Get current config
curl -X GET http://localhost:8011/v1/admin/config \
  -H "Authorization: Bearer grok2api"

# Update config
curl -X POST http://localhost:8011/v1/admin/config \
  -H "Authorization: Bearer grok2api" \
  -H "Content-Type: application/json" \
  -d '{
    "app": {
      "stream": true,
      "thinking": true
    }
  }'
```

## Configuration Sections

### 1. Application Settings (`app`)

Core application behavior settings.

```toml
[app]
# Application URL for generating file links
app_url = ""

# Admin panel password
app_key = "grok2api"

# API authentication key (optional, supports list)
api_key = ""

# Enable function features
function_enabled = false

# Function call key (optional)
function_key = ""

# Image generation format (url or base64)
image_format = "url"

# Video generation format (html or url)
video_format = "html"

# Enable temporary conversation mode
temporary = true

# Disable Grok memory feature
disable_memory = true

# Enable streaming responses by default
stream = true

# Enable chain-of-thought output by default
thinking = true

# Dynamically generate Statsig fingerprint
dynamic_statsig = true

# Custom instruction
custom_instruction = ""

# Filter special tags
filter_tags = ["xaiartifact","xai:tool_usage_card","grok:render"]
```

**Key Settings:**

- `app_key` - Admin panel password (change this!)
- `api_key` - Optional API authentication (comma-separated list)
- `stream` - Enable/disable streaming by default
- `thinking` - Show/hide thinking process in responses
- `temporary` - Temporary conversations (no history)
- `disable_memory` - Disable Grok's memory feature

### 2. Proxy Configuration (`proxy`)

Proxy settings for accessing Grok services.

```toml
[proxy]
# Base proxy URL (proxy to Grok website)
base_proxy_url = ""

# Asset proxy URL (proxy static resources like images/videos)
asset_proxy_url = ""

# Full CF Cookies (auto-refresh write)
cf_cookies = ""

# Skip proxy SSL certificate verification
skip_proxy_ssl_verify = false

# Enable CF auto-refresh
enabled = false

# FlareSolverr service URL
flaresolverr_url = ""

# Refresh interval (seconds)
refresh_interval = 3600

# CF challenge wait timeout (seconds)
timeout = 60

# Cloudflare Clearance Cookie
cf_clearance = ""

# curl_cffi browser fingerprint
browser = "chrome136"

# User-Agent string
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
```

**Key Settings:**

- `base_proxy_url` - HTTP proxy for Grok API requests
- `asset_proxy_url` - HTTP proxy for downloading images/videos
- `cf_clearance` - Cloudflare clearance cookie (if needed)
- `browser` - Browser fingerprint for curl_cffi

### 3. Retry Strategy (`retry`)

Automatic retry configuration for failed requests.

```toml
[retry]
# Maximum retry attempts
max_retry = 3

# Status codes that trigger retry
retry_status_codes = [401,429,403,502]

# Status codes that trigger session rebuild
reset_session_status_codes = [403]

# Backoff base delay (seconds)
retry_backoff_base = 0.5

# Backoff multiplier
retry_backoff_factor = 2.0

# Maximum single retry delay (seconds)
retry_backoff_max = 20.0

# Total retry budget time (seconds)
retry_budget = 60.0
```

**Key Settings:**

- `max_retry` - How many times to retry failed requests
- `retry_status_codes` - Which HTTP status codes trigger retry
- `retry_backoff_*` - Exponential backoff configuration

### 4. Token Pool Management (`token`)

Token management and auto-refresh settings.

```toml
[token]
# Enable token auto-refresh
auto_refresh = true

# Normal token refresh interval (hours)
refresh_interval_hours = 8

# Super token refresh interval (hours)
super_refresh_interval_hours = 2

# Token consecutive failure threshold
fail_threshold = 5

# Token change save delay (milliseconds)
save_delay_ms = 500

# Usage write minimum interval (seconds)
usage_flush_interval_sec = 5

# Multi-worker state sync interval (seconds)
reload_interval_sec = 30

# Enable request-side on-demand refresh
on_demand_refresh_enabled = true

# Request-side on-demand refresh minimum interval (seconds)
on_demand_refresh_min_interval_sec = 300

# Request-side on-demand refresh max tokens to check
on_demand_refresh_max_tokens = 100

# Enable consumption mode (experimental)
consumed_mode_enabled = false
```

**Key Settings:**

- `auto_refresh` - Automatically refresh tokens
- `refresh_interval_hours` - How often to refresh tokens
- `fail_threshold` - Mark token as failed after N failures

### 5. Logging Configuration (`log`)

Log file management and verbosity settings.

```toml
[log]
# Single log file size limit (MB), <=0 means no size rotation
max_file_size_mb = 100

# Maximum number of log files to keep, <=0 means unlimited
max_files = 7

# Log health check requests
log_health_requests = false

# Log all requests (when off, only logs slow and error requests)
log_all_requests = false

# Slow request threshold (milliseconds)
request_slow_ms = 3000
```

**Key Settings:**

- `log_all_requests` - Log every request (verbose)
- `request_slow_ms` - Threshold for slow request logging

### 6. Cache Management (`cache`)

Cache size and cleanup settings.

```toml
[cache]
# Enable auto cleanup
enable_auto_clean = true

# Cache size limit (MB)
limit_mb = 512
```

### 7. Chat Configuration (`chat`)

Chat API specific settings.

```toml
[chat]
# Reverse interface concurrency limit
concurrent = 50

# Reverse interface timeout (seconds)
timeout = 60

# Streaming idle timeout (seconds)
stream_timeout = 60
```

**Key Settings:**

- `concurrent` - Max concurrent chat requests
- `timeout` - Request timeout
- `stream_timeout` - Streaming idle timeout

### 8. Image Configuration (`image`)

Image generation and editing settings.

```toml
[image]
# WebSocket request timeout (seconds)
timeout = 60

# WebSocket streaming idle timeout (seconds)
stream_timeout = 60

# Wait timeout for final image after medium image (seconds)
final_timeout = 15

# Grace period when suspected censorship (seconds)
blocked_grace_seconds = 10

# Enable NSFW
nsfw = true

# Minimum bytes for medium quality image
medium_min_bytes = 30000

# Minimum bytes for final image
final_min_bytes = 100000

# Parallel compensation attempts when suspected censorship
blocked_parallel_attempts = 5

# Enable parallel compensation
blocked_parallel_enabled = true
```

**Key Settings:**

- `nsfw` - Enable NSFW image generation
- `final_timeout` - How long to wait for final high-res image
- `blocked_parallel_enabled` - Retry with different tokens if blocked

### 9. SuperImage Configuration (`imagine_fast`)

Settings for grok-imagine-1.0-fast model.

```toml
[imagine_fast]
# Number of images (server-controlled)
n = 1

# Image size: 1280x720 / 720x1280 / 1792x1024 / 1024x1792 / 1024x1024
size = "1024x1024"

# Response format: url / b64_json / base64
response_format = "url"
```

### 10. Video Configuration (`video`)

Video generation settings.

```toml
[video]
# Enable public asset after generation
enable_public_asset = false

# Reverse interface concurrency limit
concurrent = 100

# Reverse interface timeout (seconds)
timeout = 60

# Streaming idle timeout (seconds)
stream_timeout = 60

# Basic pool video upscale mode
# single: upscale after each extension (slower, better quality)
# complete: upscale after all extensions (faster, lower quality)
upscale_timing = "complete"
```

**Key Settings:**

- `upscale_timing` - When to upscale video quality
- `concurrent` - Max concurrent video requests

### 11. Voice Configuration (`voice`)

Voice/audio settings.

```toml
[voice]
# Voice request timeout (seconds)
timeout = 60
```

### 12. Asset Configuration (`asset`)

Asset upload/download settings.

```toml
[asset]
# Upload concurrency
upload_concurrent = 100

# Upload timeout (seconds)
upload_timeout = 60

# Download concurrency
download_concurrent = 100

# Download timeout (seconds)
download_timeout = 60

# Asset query concurrency
list_concurrent = 100

# Asset query timeout (seconds)
list_timeout = 60

# Asset query batch size (per token)
list_batch_size = 50

# Asset deletion concurrency
delete_concurrent = 100

# Asset deletion timeout (seconds)
delete_timeout = 60

# Asset deletion batch size (per token)
delete_batch_size = 50
```

### 13. NSFW Configuration (`nsfw`)

NSFW enablement settings.

```toml
[nsfw]
# NSFW batch enable concurrency limit
concurrent = 60

# NSFW batch enable batch size
batch_size = 30

# NSFW request timeout (seconds)
timeout = 60
```

### 14. Usage Configuration (`usage`)

Usage tracking settings.

```toml
[usage]
# Usage batch enable concurrency limit
concurrent = 100

# Usage batch enable batch size
batch_size = 50

# Usage request timeout (seconds)
timeout = 60
```

## Common Configuration Scenarios

### 1. Enable API Authentication

```toml
[app]
api_key = "your-secret-key-here"
```

Or multiple keys:

```toml
[app]
api_key = "key1,key2,key3"
```

### 2. Use HTTP Proxy

```toml
[proxy]
base_proxy_url = "http://proxy.example.com:8080"
asset_proxy_url = "http://proxy.example.com:8080"
```

### 3. Disable Streaming by Default

```toml
[app]
stream = false
```

### 4. Hide Thinking Process

```toml
[app]
thinking = false
```

### 5. Increase Timeout for Slow Networks

```toml
[chat]
timeout = 120
stream_timeout = 120

[image]
timeout = 120
stream_timeout = 120

[video]
timeout = 120
stream_timeout = 120
```

### 6. Reduce Concurrency for Limited Resources

```toml
[chat]
concurrent = 10

[video]
concurrent = 20

[asset]
upload_concurrent = 20
download_concurrent = 20
```

### 7. Enable Verbose Logging

```toml
[log]
log_all_requests = true
log_health_requests = true
```

### 8. Disable NSFW

```toml
[image]
nsfw = false
```

## Configuration Migration

Grok2API automatically migrates deprecated configuration keys:

**Old (deprecated):**
```toml
[grok]
stream = true
thinking = true
```

**New (current):**
```toml
[app]
stream = true
thinking = true
```

The system will automatically migrate old configs and save the updated version.

## Environment Variables

Some settings can be overridden with environment variables:

- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `SERVER_STORAGE_TYPE` - Storage backend (local, redis, mysql, pgsql)
- `FLARESOLVERR_URL` - FlareSolverr service URL

## Best Practices

1. **Change default admin key** - Set a strong `app_key`
2. **Enable API authentication** - Set `api_key` for production
3. **Configure proxy if needed** - Set `base_proxy_url` and `asset_proxy_url`
4. **Adjust timeouts** - Increase for slow networks, decrease for fast
5. **Monitor logs** - Enable `log_all_requests` for debugging
6. **Tune concurrency** - Adjust based on your server resources
7. **Regular backups** - Backup `data/config.toml` and token data

## Troubleshooting

### Configuration not saving

Check storage backend permissions and locks.

### Tokens not refreshing

Verify `token.auto_refresh = true` and check logs for errors.

### Slow responses

Increase timeout values and check network/proxy settings.

### High memory usage

Reduce concurrency limits and enable cache auto-cleanup.

### Images failing

Check `image.nsfw` setting and `image.blocked_parallel_enabled`.

## Related Documentation

- [API Endpoints](./api-endpoints.md)
- [Token Management](./token-management.md)
- [Admin Guide](./admin-guide.md)


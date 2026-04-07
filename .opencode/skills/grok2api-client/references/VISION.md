# Grok Vision Capabilities

All Grok chat models support vision through OpenAI-compatible `image_url` format in messages. This allows you to send images along with text prompts for analysis, description, OCR, and more.

## Supported Models

All Grok chat models have vision capabilities:

- `grok-3` - Standard Grok 3
- `grok-3-mini` - Faster, lightweight version
- `grok-3-thinking` - With chain-of-thought reasoning
- `grok-4` - Latest Grok 4
- `grok-4-thinking` - Grok 4 with reasoning
- `grok-4-heavy` - Most powerful version
- `grok-4.1-mini` - Grok 4.1 mini
- `grok-4.1-fast` - Grok 4.1 fast
- `grok-4.1-expert` - Grok 4.1 expert
- `grok-4.1-thinking` - Grok 4.1 with reasoning
- `grok-4.20-beta` - Beta version

## Image Format Support

Images can be provided in three ways:

### 1. Base64 Data URL (Recommended)

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

Supported formats:
- `data:image/png;base64,...`
- `data:image/jpeg;base64,...`
- `data:image/jpg;base64,...`
- `data:image/gif;base64,...`
- `data:image/webp;base64,...`

### 2. HTTP/HTTPS URL

```json
{
  "type": "image_url",
  "image_url": {
    "url": "https://example.com/image.jpg"
  }
}
```

### 3. Local File Path (Client-side)

When using the Python script, you can provide local file paths which will be automatically converted to base64:

```bash
python scripts/grok_vision.py --image path/to/image.jpg
```

## Usage Examples

### Python Script

#### Single Image Analysis

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "Mô tả chi tiết bức ảnh này" \
  --image photo.jpg
```

#### Multiple Images

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "So sánh 2 ảnh này" \
  --image img1.jpg \
  --image img2.jpg
```

#### URL Image

```bash
python scripts/grok_vision.py \
  --model grok-4.1-fast \
  --prompt "What's in this image?" \
  --image https://example.com/image.jpg
```

#### Test All Models

```bash
python scripts/grok_vision.py \
  --prompt "Describe this image" \
  --image test.png \
  --test-all-models
```

### cURL

#### Single Image

```bash
# Encode image to base64
IMAGE_BASE64=$(base64 -w 0 image.jpg)

# Send request
curl -X POST http://localhost:8011/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4",
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Describe this image in detail"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,'"$IMAGE_BASE64"'"
          }
        }
      ]
    }],
    "stream": false
  }'
```

#### Multiple Images

```bash
curl -X POST http://localhost:8011/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-4",
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Compare these two images"
        },
        {
          "type": "image_url",
          "image_url": {"url": "data:image/png;base64,..."}
        },
        {
          "type": "image_url",
          "image_url": {"url": "data:image/png;base64,..."}
        }
      ]
    }]
  }'
```

### OpenAI Python SDK

```python
from openai import OpenAI
import base64

client = OpenAI(
    base_url="http://localhost:8011/v1",
    api_key="not-required"
)

# Encode image
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="grok-4",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## Common Use Cases

### 1. Image Description

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "Mô tả chi tiết bức ảnh này bằng tiếng Việt" \
  --image photo.jpg
```

### 2. OCR (Text Extraction)

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "Extract all text from this image" \
  --image document.png
```

### 3. Image Comparison

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "What are the differences between these images?" \
  --image before.jpg \
  --image after.jpg
```

### 4. Object Detection

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "List all objects you can see in this image" \
  --image scene.jpg
```

### 5. Image Analysis

```bash
python scripts/grok_vision.py \
  --model grok-4-thinking \
  --prompt "Analyze this chart and explain the trends" \
  --image chart.png
```

## Performance Comparison

Based on comprehensive testing with a test image:

| Model | Duration | Completion Tokens | Notes |
|-------|----------|-------------------|-------|
| grok-3 | ~4s | 164 | Fast, concise |
| grok-3-mini | ~4s | 236 | Fast, detailed |
| grok-3-thinking | ~6s | 324 | Reasoning included |
| grok-4 | ~5s | 230 | Balanced |
| grok-4-thinking | ~8s | 279 | Reasoning included |
| grok-4-heavy | ~13s | 317 | Most detailed |
| grok-4.1-mini | ~15s | 310 | Very detailed |
| grok-4.1-fast | ~5s | 226 | Fast, balanced |
| grok-4.1-expert | ~26s | 391 | Most comprehensive |
| grok-4.1-thinking | ~12s | 257 | Reasoning included |
| grok-4.20-beta | ~19s | 286 | Beta features |

## Best Practices

### 1. Choose the Right Model

- **Fast analysis:** `grok-4.1-fast`, `grok-3-mini`
- **Detailed description:** `grok-4.1-expert`, `grok-4-heavy`
- **Reasoning required:** `grok-4-thinking`, `grok-3-thinking`
- **Balanced:** `grok-4`, `grok-3`

### 2. Image Size

- Recommended max size: 20MB per image
- Larger images may take longer to process
- Consider resizing very large images before encoding

### 3. Multiple Images

- You can include multiple images in a single request
- Images are processed in the order they appear
- Be specific about which image you're referring to in your prompt

### 4. Prompt Engineering

Good prompts for vision:
- "Mô tả chi tiết bức ảnh này" (Describe this image in detail)
- "What text do you see in this image?"
- "Compare these two images and list the differences"
- "Analyze this chart and explain the data"

### 5. Language Support

- Supports Vietnamese prompts: "Mô tả bức ảnh này bằng tiếng Việt"
- Supports English prompts: "Describe this image"
- Model will respond in the same language as the prompt

## Streaming Support

Vision requests support both streaming and non-streaming modes:

### Streaming (Default)

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "Describe this" \
  --image photo.jpg
```

### Non-Streaming

```bash
python scripts/grok_vision.py \
  --model grok-4 \
  --prompt "Describe this" \
  --image photo.jpg \
  --no-stream
```

## Error Handling

Common errors and solutions:

### 1. Image Too Large

```json
{
  "error": {
    "message": "Image size exceeds maximum allowed",
    "type": "invalid_request_error"
  }
}
```

**Solution:** Resize the image before encoding

### 2. Invalid Base64

```json
{
  "error": {
    "message": "Invalid base64 image data",
    "type": "invalid_request_error"
  }
}
```

**Solution:** Ensure proper base64 encoding with correct data URL format

### 3. Unsupported Format

```json
{
  "error": {
    "message": "Unsupported image format",
    "type": "invalid_request_error"
  }
}
```

**Solution:** Convert to PNG, JPEG, or WebP

## Testing

### Quick Test

```bash
bash grok2api-client/test-vision.sh path/to/image.png
```

### Comprehensive Test (All Models)

```bash
bash grok2api-client/test-vision-comprehensive.sh path/to/image.png
```

This will test all 11 Grok models and generate a detailed report in `grok2api-client/test-results/`.

## Output Management

All vision responses are automatically saved to `.grok-resources/`:

- **Responses:** `.grok-resources/chat/response_<timestamp>.txt`
- **Metadata:** `.grok-resources/metadata/chat_<timestamp>.json`

Metadata includes:
- Model used
- Prompt text
- Image paths/URLs
- Temperature and top_p settings
- Token usage statistics
- Timestamp

## API Reference

### Request Format

```json
{
  "model": "grok-4",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Your prompt here"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,..."
          }
        }
      ]
    }
  ],
  "stream": false,
  "temperature": 0.8,
  "top_p": 0.95
}
```

### Response Format

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "grok-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Image description here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 230,
    "total_tokens": 249
  }
}
```

## Limitations

1. **Image Size:** Maximum 20MB per image
2. **Number of Images:** No hard limit, but more images = longer processing time
3. **Rate Limits:** Same as chat API rate limits
4. **Token Usage:** Images consume prompt tokens (exact count varies by image size)

## Related Documentation

- [Chat Completions API](./api-endpoints.md#chat-completions)
- [Model Information](./api-endpoints.md#models)
- [Client Scripts](../scripts/)
- [Test Results](../test-results/)

## Support

For issues or questions:
1. Check test results in `grok2api-client/test-results/`
2. Review logs in `.grok-resources/metadata/`
3. Test with simple images first
4. Try different models to compare results

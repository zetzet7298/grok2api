# Image & Video Generation API

## 1️⃣ Tạo ảnh từ text (`/v1/images/generations`)

**Endpoint:** `POST http://localhost:8011/v1/images/generations`

### Models hỗ trợ

| Model | Mô tả |
|-------|-------|
| `grok-imagine-1.0` | Tạo ảnh tiêu chuẩn |
| `grok-imagine-1.0-fast` | Tạo ảnh nhanh (hỗ trợ n=1-10) |

### Request body (JSON)

```json
{
  "model": "grok-imagine-1.0-fast",
  "prompt": "A futuristic city with neon lights at night, cyberpunk style",
  "n": 4,
  "size": "1024x1024",
  "response_format": "url",
  "stream": false
}
```

### Tham số

| Tham số | Type | Mô tả | Giá trị |
|---------|------|-------|---------|
| `model` | string | Model tạo ảnh | `grok-imagine-1.0`, `grok-imagine-1.0-fast` |
| `prompt` | string | Mô tả ảnh muốn tạo | Bắt buộc |
| `n` | int | Số ảnh tạo (1-10) | Mặc định: 1 |
| `size` | string | Kích thước ảnh | `1024x1024`, `1280x720`, `720x1280`, `1792x1024`, `1024x1792` |
| `response_format` | string | Định dạng trả về | `url`, `b64_json`, `base64` |
| `stream` | bool | Stream SSE | Mặc định: false |

### Size mapping

| Size | Aspect Ratio |
|------|-------------|
| `1024x1024` | 1:1 (vuông) |
| `1280x720` | 16:9 (ngang) |
| `720x1280` | 9:16 (dọc) |
| `1792x1024` | 3:2 (ngang) |
| `1024x1792` | 2:3 (dọc) |

### Response (non-stream)

```json
{
  "created": 1775369146,
  "data": [
    {"url": "https://assets.grok.com/..."},
    {"url": "https://assets.grok.com/..."}
  ],
  "usage": {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0}
}
```

### Response (stream)

```
event: image_generation.partial_image
data: {"url": "..."}

event: image_generation.completed
data: {"url": "..."}
```

### Ví dụ curl

```bash
curl -s -X POST http://localhost:8011/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-imagine-1.0-fast",
    "prompt": "A cute cat sitting on a cloud, cartoon style",
    "n": 4,
    "size": "1024x1024",
    "response_format": "url"
  }'
```

---

## 2️⃣ Chỉnh sửa ảnh (`/v1/images/edits`)

**Endpoint:** `POST http://localhost:8011/v1/images/edits`

**Model:** `grok-imagine-1.0-edit`

### Request (multipart/form-data)

```bash
curl -s -X POST http://localhost:8011/v1/images/edits \
  -F "prompt=Change the background to a sunset beach" \
  -F "image=@/path/to/image.jpg" \
  -F "model=grok-imagine-1.0-edit" \
  -F "n=1" \
  -F "size=1024x1024" \
  -F "response_format=url"
```

### Tham số

| Tham số | Type | Mô tả |
|---------|------|-------|
| `prompt` | Form | Mô tả chỉnh sửa |
| `image` | File | Ảnh cần sửa (PNG/JPG/WebP, max 50MB, tối đa 16 ảnh) |
| `model` | Form | `grok-imagine-1.0-edit` |
| `n` | int | Số ảnh tạo (1-10) |
| `size` | string | Kích thước |
| `response_format` | string | `url`, `b64_json` |

### Lưu ý

- Định dạng ảnh hỗ trợ: **PNG, JPG, WebP**
- Kích thước tối đa: **50MB** mỗi ảnh
- Tối đa: **16 ảnh** cho chỉnh sửa

---

## 3️⃣ Tạo video từ ảnh (`grok-imagine-1.0-video`)

**Endpoint:** `POST http://localhost:8011/v1/images/generations`

### Request

```json
{
  "model": "grok-imagine-1.0-video",
  "prompt": "@image1 A cat walking through a neon city, cinematic slow motion",
  "image_url": ["https://example.com/image.jpg"],
  "response_format": "url"
}
```

### Lưu ý

- Dùng `@image1`, `@image2`... trong prompt để tham chiếu ảnh
- Tối đa **7 ảnh tham chiếu**
- Thứ tự `@imageN` phải khớp với thứ tự trong `image_url`

---

## 4️⃣ Video Generation API (`/v1/video/*`)

### Start video generation

**Endpoint:** `POST http://localhost:8011/v1/video/start`

```json
{
  "prompt": "@image1 A cat walking through neon city",
  "image_url": ["https://example.com/image.jpg"],
  "aspect_ratio": "16:9",
  "duration": 6,
  "resolution": "720p",
  "style_preset": "cinematic"
}
```

### Stream progress (SSE)

**Endpoint:** `GET http://localhost:8011/v1/video/sse`

```bash
curl -s http://localhost:8011/v1/video/sse
```

### Stop video generation

**Endpoint:** `POST http://localhost:8011/v1/video/stop`

```bash
curl -s -X POST http://localhost:8011/v1/video/stop \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Quick Reference

| Task | Endpoint | Model |
|------|----------|-------|
| Tạo ảnh | `POST /v1/images/generations` | `grok-imagine-1.0-fast` |
| Sửa ảnh | `POST /v1/images/edits` | `grok-imagine-1.0-edit` |
| Tạo video | `POST /v1/images/generations` | `grok-imagine-1.0-video` |
| Video advanced | `POST /v1/video/start` | - |
| Video SSE | `GET /v1/video/sse` | - |
| Video stop | `POST /v1/video/stop` | - |

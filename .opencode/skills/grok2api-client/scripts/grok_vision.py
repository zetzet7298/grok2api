#!/usr/bin/env python3
"""
Grok Vision Test Script
Test vision capabilities across Grok chat models
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


def get_output_dir() -> Path:
    """Get or create output directory"""
    output_dir = Path(os.getenv("GROK_OUTPUT_DIR", ".grok-resources"))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "chat").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)
    return output_dir


def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 data URL"""
    path = Path(image_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Detect image format
    ext = path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    mime_type = mime_types.get(ext, 'image/png')
    
    # Read and encode
    with open(path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{image_data}"


def save_response(content: str, metadata: dict, output_dir: Path) -> Path:
    """Save vision response and metadata"""
    timestamp = int(time.time())
    
    # Save response text
    response_file = output_dir / "chat" / f"response_{timestamp}.txt"
    response_file.write_text(content, encoding="utf-8")
    
    # Save metadata
    metadata_file = output_dir / "metadata" / f"chat_{timestamp}.json"
    metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return response_file


def vision_chat(
    base_url: str,
    model: str,
    prompt: str,
    images: list,
    stream: bool = True,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
    top_p: float = 0.95,
    output_dir: Optional[Path] = None,
) -> str:
    """Send vision chat request"""
    
    url = f"{base_url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Build message content with images
    content = []
    
    # Add text prompt
    if prompt:
        content.append({
            "type": "text",
            "text": prompt
        })
    
    # Add images
    for image in images:
        if image.startswith('http://') or image.startswith('https://'):
            # URL image
            image_url = image
        elif image.startswith('data:'):
            # Already base64 data URL
            image_url = image
        else:
            # Local file - encode to base64
            image_url = encode_image_to_base64(image)
        
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
    
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "top_p": top_p,
    }
    
    print(f"👁️  Testing vision with {model}...")
    print(f"📝 Prompt: {prompt}")
    print(f"🖼️  Images: {len(images)}")
    
    if stream:
        return stream_response(url, headers, payload, output_dir, images)
    else:
        return non_stream_response(url, headers, payload, output_dir, images)


def stream_response(url: str, headers: dict, payload: dict, output_dir: Optional[Path], images: list) -> str:
    """Handle streaming response"""
    full_content = ""
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=300)
        response.raise_for_status()
        
        print("\n" + "="*60)
        print("📨 Response:")
        print("="*60 + "\n")
        
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                
                if data_str == '[DONE]':
                    break
                
                try:
                    data = json.loads(data_str)
                    
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        
                        if content:
                            print(content, end='', flush=True)
                            full_content += content
                    
                    elif 'error' in data:
                        print(f"\n❌ Error: {data['error']}")
                        return ""
                
                except json.JSONDecodeError:
                    continue
        
        print("\n\n" + "="*60)
        
        if output_dir and full_content:
            metadata = {
                "model": payload["model"],
                "prompt": payload["messages"][0]["content"][0]["text"] if payload["messages"][0]["content"] else "",
                "images": images,
                "temperature": payload["temperature"],
                "top_p": payload["top_p"],
                "timestamp": int(time.time()),
                "stream": True,
            }
            saved_file = save_response(full_content, metadata, output_dir)
            print(f"💾 Saved to: {saved_file}")
        
        return full_content
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return ""


def non_stream_response(url: str, headers: dict, payload: dict, output_dir: Optional[Path], images: list) -> str:
    """Handle non-streaming response"""
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content']
            
            print("\n" + "="*60)
            print("📨 Response:")
            print("="*60 + "\n")
            print(content)
            print("\n" + "="*60)
            
            if output_dir:
                metadata = {
                    "model": payload["model"],
                    "prompt": payload["messages"][0]["content"][0]["text"] if payload["messages"][0]["content"] else "",
                    "images": images,
                    "temperature": payload["temperature"],
                    "top_p": payload["top_p"],
                    "timestamp": int(time.time()),
                    "stream": False,
                    "usage": data.get("usage", {}),
                }
                saved_file = save_response(content, metadata, output_dir)
                print(f"💾 Saved to: {saved_file}")
            
            return content
        
        elif 'error' in data:
            print(f"❌ Error: {data['error']}")
            return ""
        
        return ""
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Test Grok vision capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single image
  python grok_vision.py --model grok-4 --prompt "Mô tả chi tiết bức ảnh này" --image photo.jpg
  
  # Multiple images
  python grok_vision.py --model grok-3 --prompt "So sánh 2 ảnh này" --image img1.jpg --image img2.jpg
  
  # URL image
  python grok_vision.py --model grok-4.1-fast --prompt "What's in this image?" --image https://example.com/image.jpg
  
  # Test multiple models
  python grok_vision.py --prompt "Describe this" --image test.png --test-all-models
        """
    )
    
    parser.add_argument("--base-url", default=os.getenv("GROK_API_BASE_URL", "http://localhost:8011"),
                       help="API base URL (default: http://localhost:8011)")
    parser.add_argument("--api-key", default=os.getenv("GROK_API_KEY"),
                       help="API key (optional)")
    parser.add_argument("--model", default="grok-4",
                       choices=["grok-3", "grok-3-mini", "grok-3-thinking", 
                               "grok-4", "grok-4-thinking", "grok-4-heavy",
                               "grok-4.1-mini", "grok-4.1-fast", "grok-4.1-expert", 
                               "grok-4.1-thinking", "grok-4.20-beta"],
                       help="Model to use (default: grok-4)")
    parser.add_argument("--prompt", "-p", required=True,
                       help="Text prompt about the image(s)")
    parser.add_argument("--image", "-i", action="append", required=True,
                       help="Image file path or URL (can be used multiple times)")
    parser.add_argument("--temperature", type=float, default=0.8,
                       help="Temperature 0-2 (default: 0.8)")
    parser.add_argument("--top-p", type=float, default=0.95,
                       help="Top-p 0-1 (default: 0.95)")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming")
    parser.add_argument("--output-dir",
                       help="Output directory (default: .grok-resources)")
    parser.add_argument("--test-all-models", action="store_true",
                       help="Test with all available models")
    
    args = parser.parse_args()
    
    # Get output directory
    output_dir = Path(args.output_dir) if args.output_dir else get_output_dir()
    
    # Test with single model or all models
    if args.test_all_models:
        models = ["grok-3", "grok-3-mini", "grok-4", "grok-4.1-mini", "grok-4.1-fast"]
        print(f"\n🧪 Testing vision with {len(models)} models...\n")
        
        for model in models:
            print(f"\n{'='*60}")
            print(f"Testing: {model}")
            print('='*60)
            
            vision_chat(
                base_url=args.base_url,
                model=model,
                prompt=args.prompt,
                images=args.image,
                stream=not args.no_stream,
                api_key=args.api_key,
                temperature=args.temperature,
                top_p=args.top_p,
                output_dir=output_dir,
            )
            
            if model != models[-1]:
                print("\n⏳ Waiting 2 seconds before next test...")
                time.sleep(2)
    else:
        # Single model test
        vision_chat(
            base_url=args.base_url,
            model=args.model,
            prompt=args.prompt,
            images=args.image,
            stream=not args.no_stream,
            api_key=args.api_key,
            temperature=args.temperature,
            top_p=args.top_p,
            output_dir=output_dir,
        )


if __name__ == "__main__":
    main()

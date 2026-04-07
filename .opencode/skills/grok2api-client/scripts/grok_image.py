#!/usr/bin/env python3
"""
Grok Image Generation Script
Generate images using Grok Imagine models
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
    (output_dir / "images").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)
    return output_dir


def save_image(image_data: str, response_format: str, index: int, timestamp: int, output_dir: Path, base_url: str = None) -> Path:
    """Save image from URL or base64"""
    
    if response_format == "url":
        # Download from URL
        try:
            # Handle relative URLs
            if image_data.startswith('/'):
                if not base_url:
                    base_url = os.getenv("GROK_API_BASE_URL", "http://localhost:8011")
                image_data = base_url + image_data
            
            response = requests.get(image_data, timeout=60)
            response.raise_for_status()
            image_bytes = response.content
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            return None
    else:
        # Decode base64
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            print(f"❌ Failed to decode base64: {e}")
            return None
    
    # Save to file
    filename = f"image_{timestamp}_{index}.png"
    filepath = output_dir / "images" / filename
    filepath.write_bytes(image_bytes)
    
    return filepath


def generate_images(
    base_url: str,
    model: str,
    prompt: str,
    n: int = 1,
    size: str = "1024x1024",
    response_format: str = "url",
    stream: bool = False,
    api_key: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> list:
    """Generate images"""
    
    url = f"{base_url}/v1/images/generations"
    headers = {"Content-Type": "application/json"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "response_format": response_format,
        "stream": stream,
    }
    
    print(f"🎨 Generating {n} image(s) with {model}...")
    print(f"📝 Prompt: {prompt}")
    print(f"📐 Size: {size}")
    
    timestamp = int(time.time())
    saved_files = []
    
    try:
        if stream:
            # Handle streaming response
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=300)
            response.raise_for_status()
            
            image_count = 0
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                
                if line_str.startswith('event: '):
                    # Skip event lines, we'll process data lines
                    continue
                
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        data = json.loads(data_str)
                        
                        # Check for completed images (final stage)
                        if data.get('type') == 'image_generation.completed':
                            image_data = data.get('b64_json') or data.get('url')
                            if image_data:
                                filepath = save_image(image_data, response_format, image_count, timestamp, output_dir, base_url)
                                if filepath:
                                    saved_files.append(filepath)
                                    image_count += 1
                                    print(f"✅ Image {image_count} saved: {filepath}")
                        
                        # Optionally show partial images progress
                        elif data.get('type') == 'image_generation.partial_image':
                            stage = data.get('stage', 'preview')
                            print(f"🔄 Generating... (stage: {stage})")
                        
                        elif 'error' in data:
                            print(f"❌ Error: {data['error']}")
                    
                    except json.JSONDecodeError:
                        continue
        
        else:
            # Handle non-streaming response
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data:
                for idx, item in enumerate(data['data']):
                    image_data = item.get('b64_json') or item.get('url')
                    if image_data:
                        filepath = save_image(image_data, response_format, idx, timestamp, output_dir, base_url)
                        if filepath:
                            saved_files.append(filepath)
                            print(f"✅ Image {idx + 1} saved: {filepath}")
            
            elif 'error' in data:
                print(f"❌ Error: {data['error']}")
        
        # Save metadata
        if saved_files:
            metadata = {
                "model": model,
                "prompt": prompt,
                "n": n,
                "size": size,
                "response_format": response_format,
                "timestamp": timestamp,
                "files": [str(f) for f in saved_files],
            }
            metadata_file = output_dir / "metadata" / f"images_{timestamp}.json"
            metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"💾 Metadata saved: {metadata_file}")
        
        return saved_files
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Generate images with Grok Imagine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single image
  python grok_image.py --prompt "A futuristic cyberpunk city at night"
  
  # Generate multiple images
  python grok_image.py --prompt "Various sci-fi landscapes" --model grok-imagine-1.0-fast --n 4
  
  # Custom size
  python grok_image.py --prompt "Portrait of a robot" --size 1024x1792
  
  # Base64 format
  python grok_image.py --prompt "Abstract art" --response-format b64_json
        """
    )
    
    parser.add_argument("--base-url", default=os.getenv("GROK_API_BASE_URL", "http://localhost:8011"),
                       help="API base URL (default: http://localhost:8011)")
    parser.add_argument("--api-key", default=os.getenv("GROK_API_KEY"),
                       help="API key (optional)")
    parser.add_argument("--model", default="grok-imagine-1.0",
                       choices=["grok-imagine-1.0", "grok-imagine-1.0-fast"],
                       help="Model to use (default: grok-imagine-1.0)")
    parser.add_argument("--prompt", "-p", required=True,
                       help="Image description prompt")
    parser.add_argument("--n", type=int, default=1,
                       help="Number of images to generate (1-10, default: 1)")
    parser.add_argument("--size", default="1024x1024",
                       choices=["1280x720", "720x1280", "1792x1024", "1024x1792", "1024x1024"],
                       help="Image size (default: 1024x1024)")
    parser.add_argument("--response-format", default="url",
                       choices=["url", "b64_json", "base64"],
                       help="Response format (default: url)")
    parser.add_argument("--stream", action="store_true",
                       help="Enable streaming (only for n=1 or n=2)")
    parser.add_argument("--output-dir",
                       help="Output directory (default: .grok-resources)")
    
    args = parser.parse_args()
    
    # Validate n for streaming
    if args.stream and args.n not in [1, 2]:
        print("❌ Streaming only supports n=1 or n=2")
        sys.exit(1)
    
    # Get output directory
    output_dir = Path(args.output_dir) if args.output_dir else get_output_dir()
    
    # Generate images
    saved_files = generate_images(
        base_url=args.base_url,
        model=args.model,
        prompt=args.prompt,
        n=args.n,
        size=args.size,
        response_format=args.response_format,
        stream=args.stream,
        api_key=args.api_key,
        output_dir=output_dir,
    )
    
    if saved_files:
        print(f"\n🎉 Successfully generated {len(saved_files)} image(s)!")
    else:
        print("\n❌ No images were generated")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Grok Image Edit Script
Edit images using Grok Imagine Edit model
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


def read_image_as_base64(image_path: str) -> str:
    """Read image file and convert to base64"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')


def save_image(image_data: str, response_format: str, index: int, timestamp: int, output_dir: Path, base_url: str) -> Optional[str]:
    """Save image to file"""
    try:
        if response_format == 'url':
            # Download from URL
            url = image_data
            # Handle relative URLs
            if url.startswith('/'):
                url = base_url.rstrip('/') + url
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            image_bytes = response.content
        else:
            # Decode base64
            image_bytes = base64.b64decode(image_data)
        
        # Save to file
        filename = f"image_edit_{timestamp}_{index}.png"
        filepath = output_dir / "images" / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return str(filepath)
    
    except Exception as e:
        print(f"⚠️  Failed to save image {index}: {e}")
        return None


def edit_image(
    base_url: str,
    api_key: str,
    prompt: str,
    image_paths: list,
    model: str = "grok-imagine-1.0-edit",
    n: int = 1,
    size: str = "1024x1024",
    response_format: str = "b64_json",
    output_dir: Optional[Path] = None
):
    """Edit images using Grok API"""
    
    if output_dir is None:
        output_dir = get_output_dir()
    
    url = f"{base_url.rstrip('/')}/v1/images/edits"
    
    # Prepare multipart form data
    files = []
    for img_path in image_paths:
        with open(img_path, 'rb') as f:
            files.append(('image', (os.path.basename(img_path), f.read(), 'image/png')))
    
    data = {
        'prompt': prompt,
        'model': model,
        'n': str(n),
        'size': size,
        'response_format': response_format,
    }
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    print(f"✏️  Editing {len(image_paths)} image(s) with {model}...")
    print(f"📝 Prompt: {prompt}")
    print(f"📐 Size: {size}")
    print(f"🔢 Generating {n} variation(s) per image")
    
    timestamp = int(time.time())
    saved_files = []
    
    try:
        response = requests.post(url, headers=headers, data=data, files=files, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        # Save images
        for idx, item in enumerate(result.get('data', [])):
            image_data = item.get('b64_json') or item.get('url') or item.get('base64')
            if image_data:
                filepath = save_image(image_data, response_format, idx, timestamp, output_dir, base_url)
                if filepath:
                    saved_files.append(filepath)
                    print(f"✅ Image {idx + 1} saved: {filepath}")
        
        # Save metadata
        if saved_files:
            metadata = {
                "timestamp": timestamp,
                "prompt": prompt,
                "model": model,
                "n": n,
                "size": size,
                "response_format": response_format,
                "source_images": image_paths,
                "output_files": saved_files,
                "usage": result.get('usage', {}),
            }
            
            metadata_file = output_dir / "metadata" / f"image_edit_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"💾 Metadata saved: {metadata_file}")
        
        if saved_files:
            print(f"\n🎉 Successfully edited and generated {len(saved_files)} image(s)!")
        else:
            print("\n❌ No images were generated")
            sys.exit(1)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Edit images using Grok Imagine Edit API")
    
    parser.add_argument("--base-url", default="http://localhost:8011", help="Base URL of Grok2API server")
    parser.add_argument("--api-key", default="", help="API key for authentication")
    parser.add_argument("--model", default="grok-imagine-1.0-edit", help="Model to use")
    parser.add_argument("--prompt", required=True, help="Edit instruction prompt")
    parser.add_argument("--image", required=True, action='append', dest='images', help="Image file to edit (can specify multiple)")
    parser.add_argument("--n", type=int, default=1, help="Number of variations to generate (1-10)")
    parser.add_argument("--size", default="1024x1024", 
                       choices=["1280x720", "720x1280", "1792x1024", "1024x1792", "1024x1024"],
                       help="Output image size")
    parser.add_argument("--response-format", default="b64_json",
                       choices=["url", "b64_json", "base64"],
                       help="Response format")
    parser.add_argument("--output-dir", help="Output directory (default: .grok-resources)")
    
    args = parser.parse_args()
    
    # Validate images exist
    for img_path in args.images:
        if not os.path.exists(img_path):
            print(f"❌ Error: Image file not found: {img_path}")
            sys.exit(1)
    
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    edit_image(
        base_url=args.base_url,
        api_key=args.api_key,
        prompt=args.prompt,
        image_paths=args.images,
        model=args.model,
        n=args.n,
        size=args.size,
        response_format=args.response_format,
        output_dir=output_dir
    )


if __name__ == "__main__":
    main()

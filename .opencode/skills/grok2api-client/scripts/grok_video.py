#!/usr/bin/env python3
"""
Grok Video Generation Script
Generate videos using Grok Imagine Video
"""

import argparse
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
    (output_dir / "videos").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)
    return output_dir


def download_video(url: str, output_path: Path) -> bool:
    """Download video from URL"""
    try:
        print(f"⬇️  Downloading video...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


def generate_video(
    base_url: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    seconds: int = 6,
    quality: str = "standard",
    image_url: Optional[str] = None,
    api_key: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Generate video"""
    
    url = f"{base_url}/v1/videos"
    headers = {"Content-Type": "application/json"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "model": "grok-imagine-1.0-video",
        "prompt": prompt,
        "size": aspect_ratio,
        "seconds": seconds,
        "quality": quality,
    }
    
    if image_url:
        payload["image_reference"] = [{"type": "image_url", "image_url": {"url": image_url}}]
    
    print(f"🎬 Generating video...")
    print(f"📝 Prompt: {prompt}")
    print(f"📐 Aspect Ratio: {aspect_ratio}")
    print(f"⏱️  Duration: {seconds}s")
    print(f"🎞️  Quality: {quality}")
    
    timestamp = int(time.time())
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=600)
        response.raise_for_status()
        
        data = response.json()
        
        if 'url' in data:
            video_url = data['url']
            print(f"✅ Video generated: {video_url}")
            
            # Download video
            filename = f"video_{timestamp}.mp4"
            filepath = output_dir / "videos" / filename
            
            if download_video(video_url, filepath):
                print(f"💾 Video saved: {filepath}")
                
                # Save metadata
                metadata = {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "seconds": seconds,
                    "quality": quality,
                    "image_url": image_url,
                    "video_url": video_url,
                    "timestamp": timestamp,
                    "file": str(filepath),
                }
                metadata_file = output_dir / "metadata" / f"video_{timestamp}.json"
                metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
                
                return filepath
        
        elif 'error' in data:
            print(f"❌ Error: {data['error']}")
        
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos with Grok Imagine Video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate video from text
  python grok_video.py --prompt "A cat walking through a cyberpunk city"
  
  # With custom settings
  python grok_video.py --prompt "Cinematic drone shot" --aspect-ratio 16:9 --seconds 10 --quality high
  
  # From image
  python grok_video.py --prompt "Animate this scene" --image-url https://example.com/image.jpg
        """
    )
    
    parser.add_argument("--base-url", default=os.getenv("GROK_API_BASE_URL", "http://localhost:8011"),
                       help="API base URL (default: http://localhost:8011)")
    parser.add_argument("--api-key", default=os.getenv("GROK_API_KEY"),
                       help="API key (optional)")
    parser.add_argument("--prompt", "-p", required=True,
                       help="Video description prompt")
    parser.add_argument("--aspect-ratio", default="16:9",
                       choices=["16:9", "9:16", "3:2", "2:3", "1:1"],
                       help="Video aspect ratio (default: 16:9)")
    parser.add_argument("--seconds", type=int, default=6,
                       help="Video duration in seconds (6-30, default: 6)")
    parser.add_argument("--quality", default="standard",
                       choices=["standard", "high"],
                       help="Video quality: standard (480p) or high (720p)")
    parser.add_argument("--image-url",
                       help="Optional image URL to animate")
    parser.add_argument("--output-dir",
                       help="Output directory (default: .grok-resources)")
    
    args = parser.parse_args()
    
    # Validate seconds
    if not (6 <= args.seconds <= 30):
        print("❌ Seconds must be between 6 and 30")
        sys.exit(1)
    
    # Get output directory
    output_dir = Path(args.output_dir) if args.output_dir else get_output_dir()
    
    # Generate video
    filepath = generate_video(
        base_url=args.base_url,
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        seconds=args.seconds,
        quality=args.quality,
        image_url=args.image_url,
        api_key=args.api_key,
        output_dir=output_dir,
    )
    
    if filepath:
        print(f"\n🎉 Video successfully generated!")
    else:
        print("\n❌ Video generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

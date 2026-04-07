#!/usr/bin/env python3
"""
Test Grok2API Connection
Quick script to verify API is accessible
"""

import os
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


def test_connection(base_url: str):
    """Test API connection"""
    print(f"🔍 Testing connection to {base_url}...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"⚠️  Health check returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test models endpoint
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            print(f"✅ Models endpoint accessible ({len(models)} models available)")
            
            # Show available models
            if models:
                print("\n📋 Available models:")
                for model in models[:10]:  # Show first 10
                    print(f"   - {model.get('id')}")
                if len(models) > 10:
                    print(f"   ... and {len(models) - 10} more")
        else:
            print(f"⚠️  Models endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Models endpoint failed: {e}")
        return False
    
    print("\n🎉 Connection test successful!")
    print(f"\nYou can now use the Grok2API client scripts:")
    print(f"  python scripts/grok_chat.py --model grok-4 --message 'Hello'")
    print(f"  python scripts/grok_image.py --prompt 'A futuristic city'")
    print(f"  python scripts/grok_video.py --prompt 'A cat walking'")
    
    return True


if __name__ == "__main__":
    base_url = os.getenv("GROK_API_BASE_URL", "http://localhost:8011")
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    if not test_connection(base_url):
        print("\n❌ Connection test failed")
        print("\nTroubleshooting:")
        print("  1. Make sure Grok2API server is running")
        print("  2. Check the base URL is correct")
        print("  3. Verify network connectivity")
        sys.exit(1)

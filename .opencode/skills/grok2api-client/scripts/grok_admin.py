#!/usr/bin/env python3
"""
Grok Admin Management Script
Manage tokens, configuration, and cache
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


def admin_request(base_url: str, endpoint: str, method: str = "GET", admin_key: str = None, data: dict = None):
    """Make admin API request"""
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {admin_key}"}
    
    if data:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data or {}, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
        return None


def list_tokens(base_url: str, admin_key: str):
    """List all tokens"""
    print("📋 Listing tokens...")
    data = admin_request(base_url, "/v1/admin/tokens", "GET", admin_key)
    
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def add_token(base_url: str, admin_key: str, token: str, pool: str = "ssoBasic", note: str = ""):
    """Add new token"""
    print(f"➕ Adding token to pool '{pool}'...")
    data = admin_request(base_url, "/v1/admin/tokens", "POST", admin_key, {
        "token": token,
        "pool": pool,
        "note": note,
    })
    
    if data:
        print("✅ Token added successfully")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def refresh_tokens(base_url: str, admin_key: str):
    """Refresh all tokens"""
    print("🔄 Refreshing tokens...")
    data = admin_request(base_url, "/v1/admin/tokens/refresh", "POST", admin_key)
    
    if data:
        print("✅ Tokens refreshed successfully")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def get_config(base_url: str, admin_key: str):
    """Get configuration"""
    print("⚙️  Getting configuration...")
    data = admin_request(base_url, "/v1/admin/config", "GET", admin_key)
    
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def get_cache_info(base_url: str, admin_key: str):
    """Get cache information"""
    print("💾 Getting cache info...")
    data = admin_request(base_url, "/v1/admin/cache", "GET", admin_key)
    
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def clear_cache(base_url: str, admin_key: str, cache_type: str = "all"):
    """Clear local cache"""
    print(f"🗑️  Clearing {cache_type} cache...")
    data = admin_request(base_url, "/v1/admin/cache/clear", "POST", admin_key, {
        "type": cache_type,
    })
    
    if data:
        print("✅ Cache cleared successfully")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Manage Grok2API admin operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List tokens
  python grok_admin.py --action list-tokens
  
  # Add token
  python grok_admin.py --action add-token --token "eyJ..." --pool ssoBasic --note "My token"
  
  # Refresh tokens
  python grok_admin.py --action refresh-tokens
  
  # Get configuration
  python grok_admin.py --action get-config
  
  # Get cache info
  python grok_admin.py --action cache-info
  
  # Clear cache
  python grok_admin.py --action clear-cache --cache-type image
        """
    )
    
    parser.add_argument("--base-url", default=os.getenv("GROK_API_BASE_URL", "http://localhost:8011"),
                       help="API base URL (default: http://localhost:8011)")
    parser.add_argument("--admin-key", default=os.getenv("GROK_ADMIN_KEY", "grok2api"),
                       help="Admin key (default: grok2api)")
    parser.add_argument("--action", required=True,
                       choices=["list-tokens", "add-token", "refresh-tokens", 
                               "get-config", "cache-info", "clear-cache"],
                       help="Action to perform")
    parser.add_argument("--token",
                       help="Token value (for add-token)")
    parser.add_argument("--pool", default="ssoBasic",
                       help="Token pool (for add-token, default: ssoBasic)")
    parser.add_argument("--note",
                       help="Token note (for add-token)")
    parser.add_argument("--cache-type", default="all",
                       choices=["image", "video", "all"],
                       help="Cache type to clear (default: all)")
    
    args = parser.parse_args()
    
    success = False
    
    if args.action == "list-tokens":
        success = list_tokens(args.base_url, args.admin_key)
    
    elif args.action == "add-token":
        if not args.token:
            print("❌ --token is required for add-token action")
            sys.exit(1)
        success = add_token(args.base_url, args.admin_key, args.token, args.pool, args.note or "")
    
    elif args.action == "refresh-tokens":
        success = refresh_tokens(args.base_url, args.admin_key)
    
    elif args.action == "get-config":
        success = get_config(args.base_url, args.admin_key)
    
    elif args.action == "cache-info":
        success = get_cache_info(args.base_url, args.admin_key)
    
    elif args.action == "clear-cache":
        success = clear_cache(args.base_url, args.admin_key, args.cache_type)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

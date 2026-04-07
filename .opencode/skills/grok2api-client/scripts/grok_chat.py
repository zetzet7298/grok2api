#!/usr/bin/env python3
"""
Grok Chat Completions Script
Interact with Grok chat models via command line
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
    (output_dir / "chat").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)
    return output_dir


def save_response(content: str, metadata: dict, output_dir: Path) -> Path:
    """Save chat response and metadata"""
    timestamp = int(time.time())
    
    # Save response text
    response_file = output_dir / "chat" / f"response_{timestamp}.txt"
    response_file.write_text(content, encoding="utf-8")
    
    # Save metadata
    metadata_file = output_dir / "metadata" / f"chat_{timestamp}.json"
    metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return response_file


def chat_completion(
    base_url: str,
    model: str,
    messages: list,
    stream: bool = True,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
    top_p: float = 0.95,
    max_tokens: Optional[int] = None,
    reasoning_effort: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> str:
    """Send chat completion request"""
    
    url = f"{base_url}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "top_p": top_p,
    }
    
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    
    print(f"🤖 Sending request to {model}...")
    print(f"📝 Message: {messages[-1]['content'][:100]}...")
    
    if stream:
        return stream_response(url, headers, payload, output_dir)
    else:
        return non_stream_response(url, headers, payload, output_dir)


def stream_response(url: str, headers: dict, payload: dict, output_dir: Optional[Path]) -> str:
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
                "messages": payload["messages"],
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


def non_stream_response(url: str, headers: dict, payload: dict, output_dir: Optional[Path]) -> str:
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
                    "messages": payload["messages"],
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
        description="Chat with Grok models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple chat
  python grok_chat.py --model grok-4 --message "Hello, how are you?"
  
  # With system prompt
  python grok_chat.py --model grok-3-mini --system "You are a helpful coding assistant" --message "Explain Python decorators"
  
  # Thinking model with high reasoning
  python grok_chat.py --model grok-4-thinking --message "Solve this math problem" --reasoning-effort high
  
  # Non-streaming
  python grok_chat.py --model grok-4 --message "Quick question" --no-stream
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
    parser.add_argument("--message", "-m", required=True,
                       help="User message")
    parser.add_argument("--system", "-s",
                       help="System prompt")
    parser.add_argument("--temperature", type=float, default=0.8,
                       help="Temperature 0-2 (default: 0.8)")
    parser.add_argument("--top-p", type=float, default=0.95,
                       help="Top-p 0-1 (default: 0.95)")
    parser.add_argument("--max-tokens", type=int,
                       help="Maximum tokens to generate")
    parser.add_argument("--reasoning-effort",
                       choices=["none", "minimal", "low", "medium", "high", "xhigh"],
                       help="Reasoning effort for thinking models")
    parser.add_argument("--no-stream", action="store_true",
                       help="Disable streaming")
    parser.add_argument("--output-dir",
                       help="Output directory (default: .grok-resources)")
    
    args = parser.parse_args()
    
    # Build messages
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.message})
    
    # Get output directory
    output_dir = Path(args.output_dir) if args.output_dir else get_output_dir()
    
    # Send request
    chat_completion(
        base_url=args.base_url,
        model=args.model,
        messages=messages,
        stream=not args.no_stream,
        api_key=args.api_key,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        reasoning_effort=args.reasoning_effort,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    main()

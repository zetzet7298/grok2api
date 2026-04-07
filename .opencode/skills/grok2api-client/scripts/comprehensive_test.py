#!/usr/bin/env python3
"""
Comprehensive Test Suite for Grok2API Client
Tests all APIs with various parameters and reports results
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration


class TestSuite:
    def __init__(self, base_url: str, api_key: str, admin_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.admin_key = admin_key
        self.results: List[TestResult] = []
        self.scripts_dir = Path(__file__).parent
        
    def run_command(self, cmd: List[str], timeout: int = 60) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.scripts_dir.parent
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
        print(f"{BOLD}{BLUE}{text}{RESET}")
        print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")
    
    def print_result(self, result: TestResult):
        """Print a test result"""
        status = f"{GREEN}✅ PASS{RESET}" if result.passed else f"{RED}❌ FAIL{RESET}"
        print(f"{status} {result.name} ({result.duration:.2f}s)")
        if result.message and not result.passed:
            print(f"  {YELLOW}└─ {result.message}{RESET}")
    
    def test_connection(self):
        """Test basic connection"""
        self.print_header("Testing Connection")
        start = time.time()
        
        success, output = self.run_command([
            "python3", "scripts/test_connection.py",
            self.base_url,
            self.api_key
        ])
        
        duration = time.time() - start
        result = TestResult("Connection Test", success, "" if success else output, duration)
        self.results.append(result)
        self.print_result(result)
    
    def test_chat_basic(self):
        """Test basic chat"""
        self.print_header("Testing Chat API - Basic")
        start = time.time()
        
        success, output = self.run_command([
            "python3", "scripts/grok_chat.py",
            "--message", "Say 'test successful' and nothing else",
            "--base-url", self.base_url,
            "--api-key", self.api_key
        ])
        
        duration = time.time() - start
        result = TestResult("Chat Basic", success, "" if success else output, duration)
        self.results.append(result)
        self.print_result(result)
    
    def test_chat_streaming(self):
        """Test streaming chat"""
        self.print_header("Testing Chat API - Streaming")
        start = time.time()
        
        # Note: grok_chat.py uses streaming by default, use --no-stream to disable
        success, output = self.run_command([
            "python3", "scripts/grok_chat.py",
            "--message", "Count from 1 to 3",
            "--base-url", self.base_url,
            "--api-key", self.api_key
        ], timeout=30)
        
        duration = time.time() - start
        result = TestResult("Chat Streaming", success, "" if success else output, duration)
        self.results.append(result)
        self.print_result(result)
    
    def test_image_generation(self):
        """Test image generation with various parameters"""
        self.print_header("Testing Image Generation API")
        
        test_cases = [
            ("Basic (1 image)", ["--prompt", "A red apple", "--n", "1"]),
            ("Multiple (2 images)", ["--prompt", "A blue sky", "--n", "2"]),
            ("Size 1792x1024", ["--prompt", "A landscape", "--size", "1792x1024"]),
            ("Size 720x1280", ["--prompt", "A portrait", "--size", "720x1280"]),
            ("Fast model", ["--prompt", "A car", "--model", "grok-imagine-1.0-fast"]),
            ("URL format", ["--prompt", "A flower", "--response-format", "url"]),
        ]
        
        for name, args in test_cases:
            start = time.time()
            cmd = ["python3", "scripts/grok_image.py"] + args + [
                "--base-url", self.base_url,
                "--api-key", self.api_key
            ]
            success, output = self.run_command(cmd, timeout=60)
            duration = time.time() - start
            
            result = TestResult(f"Image Gen: {name}", success, "" if success else output[:200], duration)
            self.results.append(result)
            self.print_result(result)
            
            # Longer delay between tests to avoid rate limiting
            if not success and "429" in output:
                print(f"  {YELLOW}⏳ Rate limited, waiting 10 seconds...{RESET}")
                time.sleep(10)
            else:
                time.sleep(3)
    
    def test_image_edit(self):
        """Test image editing"""
        self.print_header("Testing Image Edit API")
        
        # Find a test image
        images_dir = Path(".grok-resources/images")
        test_images = list(images_dir.glob("*.png"))
        
        if not test_images:
            result = TestResult("Image Edit", False, "No test images found", 0)
            self.results.append(result)
            self.print_result(result)
            return
        
        test_image = str(test_images[0])
        start = time.time()
        
        success, output = self.run_command([
            "python3", "scripts/grok_image_edit.py",
            "--prompt", "Add a rainbow",
            "--image", test_image,
            "--base-url", self.base_url,
            "--api-key", self.api_key
        ], timeout=60)
        
        duration = time.time() - start
        result = TestResult("Image Edit", success, "" if success else output[:200], duration)
        self.results.append(result)
        self.print_result(result)
    
    def test_admin_operations(self):
        """Test admin operations"""
        self.print_header("Testing Admin API")
        
        operations = [
            ("List Tokens", ["--action", "list-tokens"]),
            ("Cache Info", ["--action", "cache-info"]),
            ("Get Config", ["--action", "get-config"]),
        ]
        
        for name, args in operations:
            start = time.time()
            cmd = ["python3", "scripts/grok_admin.py"] + args + [
                "--admin-key", self.admin_key,
                "--base-url", self.base_url
            ]
            success, output = self.run_command(cmd, timeout=30)
            duration = time.time() - start
            
            result = TestResult(f"Admin: {name}", success, "" if success else output[:200], duration)
            self.results.append(result)
            self.print_result(result)
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"\nTotal Duration: {sum(r.duration for r in self.results):.2f}s")
        
        if failed > 0:
            print(f"\n{RED}Failed Tests:{RESET}")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.name}")
                    if result.message:
                        print(f"    {result.message[:100]}")
        
        # Save results to JSON
        results_file = Path(".grok-resources/test_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        results_data = {
            "timestamp": int(time.time()),
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "message": r.message
                }
                for r in self.results
            ]
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n📊 Results saved to: {results_file}")
    
    def run_all(self):
        """Run all tests"""
        print(f"{BOLD}Grok2API Comprehensive Test Suite{RESET}")
        print(f"Server: {self.base_url}")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_connection()
        self.test_chat_basic()
        self.test_chat_streaming()
        self.test_image_generation()
        self.test_image_edit()
        self.test_admin_operations()
        
        self.print_summary()
        
        # Return exit code based on results
        return 0 if all(r.passed for r in self.results) else 1


def main():
    parser = argparse.ArgumentParser(description="Comprehensive test suite for Grok2API")
    parser.add_argument("--base-url", default="http://localhost:8011", help="Base URL")
    parser.add_argument("--api-key", default="grok2api", help="API key")
    parser.add_argument("--admin-key", default="grok2api", help="Admin key")
    
    args = parser.parse_args()
    
    suite = TestSuite(args.base_url, args.api_key, args.admin_key)
    exit_code = suite.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

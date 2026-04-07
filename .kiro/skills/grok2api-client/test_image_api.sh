#!/bin/bash

echo "=========================================="
echo "TEST 1: Basic image generation (1 image)"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A red apple on a table" --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 2: Multiple images (n=2)"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A blue ocean wave" --n 2 --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 3: Different size (1792x1024)"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A mountain landscape" --size 1792x1024 --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 4: Different size (720x1280)"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A tall building" --size 720x1280 --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 5: URL response format"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A yellow sunflower" --response-format url --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 6: Different model (grok-imagine-1.0-fast)"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A fast car" --model grok-imagine-1.0-fast --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 7: Complex prompt with multiple images"
echo "=========================================="
python3 scripts/grok_image.py --prompt "A cyberpunk city with neon lights, flying cars, and holographic advertisements" --n 3 --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="

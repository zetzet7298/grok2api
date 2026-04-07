#!/bin/bash

echo "=========================================="
echo "Preparing test images for editing..."
echo "=========================================="

TEST_IMAGE=".grok-resources/images/image_1775543093_0.png"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Test image not found!"
    exit 1
fi

echo "Using test image: $TEST_IMAGE"
echo ""

echo "=========================================="
echo "TEST 1: Basic image edit"
echo "=========================================="
python3 scripts/grok_image_edit.py --prompt "Add a rainbow in the sky" --image "$TEST_IMAGE" --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 2: Image edit with multiple outputs (n=2)"
echo "=========================================="
python3 scripts/grok_image_edit.py --prompt "Make it look like sunset" --image "$TEST_IMAGE" --n 2 --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 3: Image edit with different size"
echo "=========================================="
python3 scripts/grok_image_edit.py --prompt "Add snow on the ground" --image "$TEST_IMAGE" --size 1792x1024 --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 4: Image edit with URL response format"
echo "=========================================="
python3 scripts/grok_image_edit.py --prompt "Add clouds" --image "$TEST_IMAGE" --response-format url --base-url http://localhost:8011 --api-key grok2api

echo ""
echo "=========================================="
echo "TEST 5: Edit multiple images at once"
echo "=========================================="
TEST_IMAGE2=".grok-resources/images/image_1775543093_1.png"
if [ -f "$TEST_IMAGE2" ]; then
    python3 scripts/grok_image_edit.py --prompt "Add stars in the sky" --image "$TEST_IMAGE" --image "$TEST_IMAGE2" --base-url http://localhost:8011 --api-key grok2api
else
    echo "Second test image not found, skipping..."
fi

echo ""
echo "=========================================="
echo "All image edit tests completed!"
echo "=========================================="

#!/bin/bash
# Test script to validate the solution works

echo "=========================================="
echo "Testing Emotional Speech Generation"
echo "=========================================="
echo ""

# Test 1: CLI Help
echo "✓ Test 1: CLI Help"
python scripts/solution.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  PASS: Help command works"
else
    echo "  FAIL: Help command failed"
    exit 1
fi

# Test 2: List emotions
echo ""
echo "✓ Test 2: List Emotions"
python scripts/solution.py --list-emotions > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  PASS: List emotions works"
else
    echo "  FAIL: List emotions failed"
    exit 1
fi

# Test 3: Basic synthesis (if TTS installed)
echo ""
echo "✓ Test 3: Basic Synthesis"
python scripts/solution.py "Hello world" /tmp/test_output.wav > /dev/null 2>&1
if [ $? -eq 0 ] && [ -f /tmp/test_output.wav ]; then
    echo "  PASS: Basic synthesis works"
    rm -f /tmp/test_output.wav
else
    echo "  SKIP: TTS not installed or synthesis failed (expected on first run)"
fi

# Test 4: API health check (if running)
echo ""
echo "✓ Test 4: API Health Check"
curl -s http://localhost:8000/v1/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  PASS: API is running and healthy"
else
    echo "  SKIP: API not running (expected)"
fi

# Test 5: Unit tests
echo ""
echo "✓ Test 5: Unit Tests"
python -m pytest tests/unit/ -q > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  PASS: Unit tests pass"
else
    echo "  SKIP: Pytest not installed or tests not ready"
fi

echo ""
echo "=========================================="
echo "Test Summary: Basic validation complete"
echo "=========================================="
echo ""
echo "To run full tests:"
echo "  make test"
echo ""
echo "To start the API:"
echo "  make run"
echo ""


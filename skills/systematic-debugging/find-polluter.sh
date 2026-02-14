#!/usr/bin/env bash
# find-polluter.sh — Find which test creates unwanted files/state
# Usage: ./find-polluter.sh <marker-pattern> <test-glob>
# Example: ./find-polluter.sh '.git' 'src/**/*.test.ts'
#
# Runs tests one-by-one, checks for marker after each,
# stops at the first test that creates the pollution.

set -euo pipefail

MARKER="${1:?Usage: $0 <marker-pattern> <test-glob>}"
TEST_GLOB="${2:?Usage: $0 <marker-pattern> <test-glob>}"

echo "Looking for test that creates: $MARKER"
echo "Test pattern: $TEST_GLOB"
echo "---"

# Clean state
rm -rf "$MARKER" 2>/dev/null || true

# Find all test files matching the glob
mapfile -t TEST_FILES < <(find . -path "$TEST_GLOB" -type f | sort)

echo "Found ${#TEST_FILES[@]} test files"
echo ""

for test_file in "${TEST_FILES[@]}"; do
    # Clean before each test
    rm -rf "$MARKER" 2>/dev/null || true

    echo -n "Testing: $test_file ... "

    # Run single test file (adapt command for your framework)
    if npx jest "$test_file" --silent 2>/dev/null || \
       npx vitest run "$test_file" --silent 2>/dev/null || \
       pytest "$test_file" -q 2>/dev/null; then

        # Check if marker appeared
        if [ -e "$MARKER" ]; then
            echo "POLLUTER FOUND!"
            echo ""
            echo "Test file: $test_file"
            echo "Creates: $MARKER"
            exit 0
        else
            echo "clean"
        fi
    else
        echo "failed (skipping)"
    fi
done

echo ""
echo "No polluter found among ${#TEST_FILES[@]} files"
exit 1

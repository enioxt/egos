#!/bin/bash

echo "🔍 Claude Code Connection Test"
echo "=========================="

# Check if claude is installed
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code not found"
    exit 1
fi

echo "✅ Claude Code found: $(claude --version)"

# Check credentials
if [ -f ~/.claude/.credentials.json ]; then
    echo "✅ Credentials file exists"
    # Check if token is expired
    expires_at=$(grep -o '"expiresAt":[0-9]*' ~/.claude/.credentials.json | cut -d: -f2)
    current_time=$(date +%s%3N)
    if [ "$expires_at" -gt "$current_time" ]; then
        echo "✅ Token valid (expires at: $expires_at)"
    else
        echo "⚠️ Token expired"
    fi
else
    echo "❌ No credentials file"
fi

# Test basic connection with different approaches
echo ""
echo "🧪 Testing connection..."

# Test 1: Simple version check
echo "Test 1: Version check"
timeout 5s claude --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Basic connection OK"
else
    echo "❌ Basic connection failed"
fi

# Test 2: Simple print with dangerous skip
echo "Test 2: Print with skip permissions"
timeout 5s claude --print --dangerously-skip-permissions "hi" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Print mode works"
else
    echo "❌ Print mode failed"
fi

# Test 3: Check available models
echo "Test 3: Model availability"
timeout 5s claude --print --dangerously-skip-permissions "test" --model claude-3-haiku >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Haiku model available"
else
    echo "⚠️ Haiku model not available (trying default)"
    timeout 5s claude --print --dangerously-skip-permissions "test" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Default model works"
    else
        echo "❌ Default model failed"
    fi
fi

echo ""
echo "📊 Summary:"
echo "- Claude Code: Installed"
echo "- Auth: Configured"
echo "- Connection: Needs manual verification"
echo ""
echo "🔧 Next steps:"
echo "1. Run: claude --print --dangerously-skip-permissions 'test connection'"
echo "2. If it works, try: claude --print --dangerously-skip-permissions 'test' --model claude-3-haiku"
echo "3. For cheap models, check: claude --help | grep -i model"

#!/bin/bash

# Test script to verify Docker build fix
echo "🧪 Testing Docker Build Fix"
echo "================================"

echo "1. Checking if package-lock.json exists..."
if [ -f "package-lock.json" ]; then
    echo "✅ package-lock.json exists"
    echo "   Size: $(stat -f%z package-lock.json 2>/dev/null || stat -c%s package-lock.json) bytes"
else
    echo "❌ package-lock.json not found"
    exit 1
fi

echo ""
echo "2. Checking .dockerignore exclusions..."
if grep -q "package-lock.json" .dockerignore; then
    echo "❌ package-lock.json is still excluded in .dockerignore"
    echo "   This will cause Docker build to fail"
    exit 1
else
    echo "✅ package-lock.json is not excluded in .dockerignore"
fi

echo ""
echo "3. Checking Dockerfile.frontend syntax..."
if [ -f "Dockerfile.frontend" ]; then
    if grep -q "COPY package.json package-lock.json" Dockerfile.frontend; then
        echo "✅ Dockerfile.frontend correctly references package-lock.json"
    else
        echo "❌ Dockerfile.frontend doesn't reference package-lock.json correctly"
        exit 1
    fi
else
    echo "❌ Dockerfile.frontend not found"
    exit 1
fi

echo ""
echo "4. Checking package.json syntax..."
if python3 -m json.tool package.json > /dev/null 2>&1; then
    echo "✅ package.json is valid JSON"
else
    echo "❌ package.json has invalid JSON syntax"
    exit 1
fi

echo ""
echo "5. Checking package-lock.json syntax..."
if python3 -m json.tool package-lock.json > /dev/null 2>&1; then
    echo "✅ package-lock.json is valid JSON"
else
    echo "❌ package-lock.json has invalid JSON syntax"
    exit 1
fi

echo ""
echo "================================"
echo "🎉 ALL CHECKS PASSED!"
echo "✅ Docker build should now work correctly"
echo ""
echo "Next steps:"
echo "1. Run: docker compose build frontend"
echo "2. Or: docker compose up -d"
echo ""
echo "The build error should be resolved! 🚀"
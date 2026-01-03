#!/bin/zsh

# Package the .app for Homebrew distribution
set -euo pipefail

APP_NAME="macos-a8c-chat-overlay"

# Check if .app exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ Error: dist/${APP_NAME}.app not found"
    echo "Run ./test_build.sh first to build the app"
    exit 1
fi

echo "📦 Packaging ${APP_NAME}.app for release..."

# Remove old zip if exists
rm -f "dist/${APP_NAME}.zip"

# Create zip file
cd dist
ditto -c -k --keepParent "${APP_NAME}.app" "${APP_NAME}.zip"
cd ..

# Calculate SHA256
echo ""
echo "✅ Package created successfully!"
echo ""
echo "📍 Location: dmg-builder/dist/${APP_NAME}.zip"
echo ""
echo "🔐 SHA256:"
shasum -a 256 "dist/${APP_NAME}.zip"
echo ""
echo "Next steps:"
echo "1. Upload dist/${APP_NAME}.zip to GitHub Releases"
echo "2. Update the cask formula with the SHA256 above"
echo "3. Commit and push to homebrew-tap repository"

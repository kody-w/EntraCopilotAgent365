#!/bin/bash

# Build script for Copilot Agent 365 Tauri Desktop Client
# This script prepares the frontend by copying and enhancing the original index.html

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$SCRIPT_DIR/dist"
SOURCE_HTML="$PROJECT_ROOT/index.html"

echo "🔨 Building Copilot Agent 365 Desktop Frontend..."
echo "   Source: $SOURCE_HTML"
echo "   Target: $DIST_DIR"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Check if source HTML exists
if [ ! -f "$SOURCE_HTML" ]; then
    echo "❌ Error: Source index.html not found at $SOURCE_HTML"
    exit 1
fi

echo "📄 Processing index.html..."

# Create injection strings
HEAD_INJECTION='  <!-- Tauri Desktop Client Enhancements -->\n  <link rel="stylesheet" href="desktop-styles.css" />\n  <script src="tauri-bridge.js" defer></script>\n  <script src="desktop-init.js" defer></script>'

# Simple sed replacement for head injection (macOS compatible)
sed "s|<head>|<head>\\
  <!-- Tauri Desktop Client Enhancements -->\\
  <link rel=\"stylesheet\" href=\"desktop-styles.css\" />\\
  <script src=\"tauri-bridge.js\" defer></script>\\
  <script src=\"desktop-init.js\" defer></script>|" "$SOURCE_HTML" > "$DIST_DIR/index.html"

echo "✅ index.html processed"

# Verify the required files exist
MISSING_FILES=0
for file in tauri-bridge.js desktop-styles.css desktop-init.js; do
    if [ ! -f "$DIST_DIR/$file" ]; then
        echo "⚠️  Warning: $file not found in dist/"
        MISSING_FILES=$((MISSING_FILES + 1))
    else
        echo "✅ $file found"
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo "⚠️  Some required files are missing. Make sure all files are in the dist/ directory."
fi

echo ""
echo "✨ Frontend build complete!"
echo ""
echo "Next steps:"
echo "  1. Install dependencies: npm install"
echo "  2. Run development: npm run dev"
echo "  3. Build for production: npm run build"

#!/bin/bash

# Generate app icons from SVG for Tauri
# Requires: ImageMagick (brew install imagemagick) or rsvg-convert

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICONS_DIR="$SCRIPT_DIR/src-tauri/icons"
SVG_FILE="$ICONS_DIR/icon.svg"

echo "🎨 Generating icons from SVG..."

if [ ! -f "$SVG_FILE" ]; then
    echo "❌ Error: icon.svg not found at $SVG_FILE"
    exit 1
fi

# Check for available conversion tool
if command -v rsvg-convert &> /dev/null; then
    CONVERTER="rsvg"
elif command -v convert &> /dev/null; then
    CONVERTER="imagemagick"
elif command -v sips &> /dev/null; then
    CONVERTER="sips"
else
    echo "⚠️  No image conversion tool found."
    echo "   Install one of:"
    echo "   - ImageMagick: brew install imagemagick"
    echo "   - librsvg: brew install librsvg"
    echo ""
    echo "Creating placeholder PNGs instead..."
    CONVERTER="none"
fi

generate_png() {
    local size=$1
    local output=$2

    case $CONVERTER in
        rsvg)
            rsvg-convert -w $size -h $size "$SVG_FILE" -o "$output"
            ;;
        imagemagick)
            convert -background none -density 300 "$SVG_FILE" -resize ${size}x${size} "$output"
            ;;
        sips)
            # macOS sips doesn't handle SVG well, copy a placeholder
            echo "   Skipping $output (sips doesn't support SVG)"
            return 1
            ;;
        none)
            echo "   Skipping $output (no converter available)"
            return 1
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo "   ✅ Generated $output"
    else
        echo "   ❌ Failed to generate $output"
    fi
}

# Generate PNG icons at various sizes
echo "📐 Generating PNG icons..."
generate_png 32 "$ICONS_DIR/32x32.png"
generate_png 128 "$ICONS_DIR/128x128.png"
generate_png 256 "$ICONS_DIR/128x128@2x.png"
generate_png 256 "$ICONS_DIR/icon.png"

# Generate ICO for Windows (requires ImageMagick)
if [ "$CONVERTER" = "imagemagick" ]; then
    echo "📐 Generating Windows ICO..."
    convert "$SVG_FILE" -define icon:auto-resize=256,128,64,48,32,16 "$ICONS_DIR/icon.ico"
    if [ $? -eq 0 ]; then
        echo "   ✅ Generated icon.ico"
    fi
fi

# Generate ICNS for macOS (requires iconutil on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📐 Generating macOS ICNS..."

    ICONSET_DIR="$ICONS_DIR/icon.iconset"
    mkdir -p "$ICONSET_DIR"

    if [ "$CONVERTER" != "none" ]; then
        # Generate all required sizes for iconset
        generate_png 16 "$ICONSET_DIR/icon_16x16.png"
        generate_png 32 "$ICONSET_DIR/icon_16x16@2x.png"
        generate_png 32 "$ICONSET_DIR/icon_32x32.png"
        generate_png 64 "$ICONSET_DIR/icon_32x32@2x.png"
        generate_png 128 "$ICONSET_DIR/icon_128x128.png"
        generate_png 256 "$ICONSET_DIR/icon_128x128@2x.png"
        generate_png 256 "$ICONSET_DIR/icon_256x256.png"
        generate_png 512 "$ICONSET_DIR/icon_256x256@2x.png"
        generate_png 512 "$ICONSET_DIR/icon_512x512.png"
        generate_png 1024 "$ICONSET_DIR/icon_512x512@2x.png"

        # Convert iconset to icns
        iconutil -c icns "$ICONSET_DIR" -o "$ICONS_DIR/icon.icns"

        if [ $? -eq 0 ]; then
            echo "   ✅ Generated icon.icns"
        fi

        # Clean up iconset
        rm -rf "$ICONSET_DIR"
    fi
fi

echo ""
echo "✨ Icon generation complete!"
echo ""
echo "If icons weren't generated, install ImageMagick:"
echo "  macOS: brew install imagemagick"
echo "  Ubuntu: sudo apt install imagemagick"
echo "  Windows: choco install imagemagick"

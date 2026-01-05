#!/bin/bash
set -e

# BLine macOS DMG Creation Script
# This script creates a distributable DMG installer for BLine

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${SCRIPT_DIR}/build"
APP_BUNDLE="${BUILD_DIR}/BLine.app"
DMG_NAME="BLine-0.1.3-macOS"
DMG_PATH="${PROJECT_DIR}/${DMG_NAME}.dmg"
TEMP_DMG="${BUILD_DIR}/temp.dmg"
VOLUME_NAME="BLine Installer"

echo "========================================"
echo "Creating DMG for BLine"
echo "========================================"
echo ""

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "Error: App bundle not found at ${APP_BUNDLE}"
    echo "Please run build-macos.sh first."
    exit 1
fi

# Clean up previous DMG
rm -f "$DMG_PATH" "$TEMP_DMG"

# Create a temporary directory for DMG contents
DMG_DIR="${BUILD_DIR}/dmg"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copy app bundle to DMG directory
echo "Copying app bundle..."
cp -r "$APP_BUNDLE" "$DMG_DIR/"

# Create Applications symlink
echo "Creating Applications symlink..."
ln -s /Applications "$DMG_DIR/Applications"

# Create a background image directory if you want a custom background
mkdir -p "$DMG_DIR/.background"
if [ -f "${PROJECT_DIR}/assets/dmg-background.png" ]; then
    cp "${PROJECT_DIR}/assets/dmg-background.png" "$DMG_DIR/.background/background.png"
fi

# Calculate size needed for DMG
echo "Calculating DMG size..."
SIZE=$(du -sm "$DMG_DIR" | awk '{print $1}')
SIZE=$((SIZE + 50))  # Add 50MB padding

# Create temporary DMG
echo "Creating temporary DMG..."
hdiutil create -size ${SIZE}m -fs HFS+ -volname "$VOLUME_NAME" "$TEMP_DMG"

# Mount the temporary DMG
echo "Mounting DMG..."
MOUNT_DIR=$(hdiutil attach "$TEMP_DMG" -readwrite -noverify -noautoopen | grep "/Volumes" | awk '{print $3}')

# Copy contents to mounted DMG
echo "Copying contents to DMG..."
cp -r "$DMG_DIR"/* "$MOUNT_DIR/"

# Set up DMG appearance with AppleScript
echo "Setting up DMG appearance..."
cat > "${BUILD_DIR}/dmg_setup.applescript" << 'APPLESCRIPT'
tell application "Finder"
    tell disk "BLine Installer"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 600, 450}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 96
        set position of item "BLine.app" of container window to {125, 180}
        set position of item "Applications" of container window to {375, 180}
        update without registering applications
        delay 2
        close
    end tell
end tell
APPLESCRIPT

# Only run AppleScript if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript "${BUILD_DIR}/dmg_setup.applescript" 2>/dev/null || echo "Warning: Could not set DMG appearance"
fi

# Set custom icon if available
if [ -f "${RESOURCES_DIR}/BLine.icns" ]; then
    cp "${APP_BUNDLE}/Contents/Resources/BLine.icns" "$MOUNT_DIR/.VolumeIcon.icns"
    SetFile -c icnC "$MOUNT_DIR/.VolumeIcon.icns" 2>/dev/null || true
fi

# Unmount the temporary DMG
echo "Unmounting DMG..."
hdiutil detach "$MOUNT_DIR" -quiet

# Convert to compressed, read-only DMG
echo "Compressing DMG..."
hdiutil convert "$TEMP_DMG" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"

# Clean up
rm -f "$TEMP_DMG"
rm -rf "$DMG_DIR"

echo ""
echo "========================================"
echo "DMG creation complete!"
echo "DMG created: ${DMG_PATH}"
echo "========================================"
echo ""
echo "To test the DMG:"
echo "  open \"${DMG_PATH}\""
echo ""
echo "For distribution:"
echo "  1. Test the DMG on a clean macOS system"
echo "  2. Sign the DMG with: codesign --sign \"Developer ID\" \"${DMG_PATH}\""
echo "  3. Notarize with Apple for Gatekeeper approval"

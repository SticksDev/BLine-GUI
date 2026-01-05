#!/bin/bash
set -e

# BLine macOS Code Signing Script (Optional)
# This script signs the app bundle for distribution

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
APP_BUNDLE="${BUILD_DIR}/BLine.app"

echo "========================================"
echo "Code Signing BLine.app"
echo "========================================"
echo ""

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "Error: App bundle not found at ${APP_BUNDLE}"
    echo "Please run build-macos.sh first."
    exit 1
fi

# Check for signing identity
if [ -z "$SIGNING_IDENTITY" ]; then
    echo "Available signing identities:"
    security find-identity -v -p codesigning
    echo ""
    echo "Usage: SIGNING_IDENTITY=\"Developer ID Application: Your Name\" ./sign-app.sh"
    echo ""
    echo "Or for ad-hoc signing (local use only):"
    echo "  SIGNING_IDENTITY=\"-\" ./sign-app.sh"
    exit 1
fi

echo "Signing with identity: $SIGNING_IDENTITY"
echo ""

# Sign all dynamic libraries and frameworks first
echo "Signing frameworks and libraries..."
find "$APP_BUNDLE" -type f \( -name "*.dylib" -o -name "*.so" \) -exec \
    codesign --force --sign "$SIGNING_IDENTITY" --timestamp --options=runtime {} \; 2>/dev/null || true

# Sign Python framework
if [ -d "$APP_BUNDLE/Contents/Frameworks/Python.framework" ]; then
    codesign --force --sign "$SIGNING_IDENTITY" --timestamp --options=runtime \
        "$APP_BUNDLE/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
fi

# Sign the app bundle itself
echo "Signing app bundle..."
codesign --force --deep --sign "$SIGNING_IDENTITY" --timestamp --options=runtime \
    --entitlements "${SCRIPT_DIR}/entitlements.plist" \
    "$APP_BUNDLE"

# Verify signature
echo ""
echo "Verifying signature..."
codesign --verify --verbose "$APP_BUNDLE"

echo ""
echo "========================================"
echo "Code signing complete!"
echo "========================================"
echo ""
echo "To verify the signature:"
echo "  codesign --verify --deep --strict --verbose=2 \"${APP_BUNDLE}\""
echo ""
echo "For notarization (required for Gatekeeper):"
echo "  xcrun notarytool submit BLine.dmg --apple-id your@email.com --team-id TEAMID --password app-specific-password"

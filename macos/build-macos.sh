#!/bin/bash
set -e

# BLine macOS .app Bundle Build Script
# This script creates a macOS application bundle for BLine

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${SCRIPT_DIR}/build"
APP_NAME="BLine"
BUNDLE_DIR="${BUILD_DIR}/${APP_NAME}.app"
CONTENTS_DIR="${BUNDLE_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"
FRAMEWORKS_DIR="${CONTENTS_DIR}/Frameworks"

echo "========================================"
echo "Building ${APP_NAME}.app for macOS"
echo "========================================"
echo ""

# Check we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Warning: This script is designed to run on macOS."
    echo "Building anyway, but the result may not work properly."
fi

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required but not installed."; exit 1; }

# Clean previous build
echo "Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$FRAMEWORKS_DIR"

# Create a virtual environment with all dependencies
echo "Creating virtual environment and installing dependencies..."
python3 -m venv "${BUILD_DIR}/venv"
source "${BUILD_DIR}/venv/bin/activate"

# Install the application and its dependencies
pip install --upgrade pip
pip install -e "$PROJECT_DIR"

# Copy Python framework
echo "Bundling Python environment..."
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_STDLIB="${BUILD_DIR}/venv/lib/python${PYTHON_VERSION}"

# Create Python structure in Frameworks
PYTHON_FW="${FRAMEWORKS_DIR}/Python.framework/Versions/${PYTHON_VERSION}"
mkdir -p "${PYTHON_FW}/lib/python${PYTHON_VERSION}"
mkdir -p "${PYTHON_FW}/bin"

# Copy Python standard library and site-packages
cp -r "${PYTHON_STDLIB}/"* "${PYTHON_FW}/lib/python${PYTHON_VERSION}/"

# Copy Python binary
cp "${BUILD_DIR}/venv/bin/python3" "${PYTHON_FW}/bin/python3"
chmod +x "${PYTHON_FW}/bin/python3"

# Create symlinks
(cd "${FRAMEWORKS_DIR}/Python.framework/Versions" && ln -sf "${PYTHON_VERSION}" Current)

# Copy application files
echo "Copying application files..."
mkdir -p "${RESOURCES_DIR}/bline"
cp -r "${PROJECT_DIR}/models" "${RESOURCES_DIR}/bline/"
cp -r "${PROJECT_DIR}/ui" "${RESOURCES_DIR}/bline/"
cp -r "${PROJECT_DIR}/utils" "${RESOURCES_DIR}/bline/"
cp "${PROJECT_DIR}/main.py" "${RESOURCES_DIR}/bline/"
cp "${PROJECT_DIR}/assets_rc.py" "${RESOURCES_DIR}/bline/"

# Copy assets
echo "Copying assets..."
cp -r "${PROJECT_DIR}/assets" "${RESOURCES_DIR}/bline/"

# Create icon (convert PNG to ICNS if on macOS)
echo "Creating application icon..."
if command -v sips >/dev/null 2>&1 && command -v iconutil >/dev/null 2>&1; then
    # macOS - create proper ICNS
    ICONSET_DIR="${BUILD_DIR}/BLine.iconset"
    mkdir -p "$ICONSET_DIR"

    # Generate all required icon sizes
    for size in 16 32 128 256 512; do
        sips -z $size $size "${PROJECT_DIR}/assets/rebel_logo.png" \
            --out "${ICONSET_DIR}/icon_${size}x${size}.png" >/dev/null 2>&1
    done

    # Generate @2x versions for retina
    for size in 16 32 128 256; do
        size2=$((size * 2))
        sips -z $size2 $size2 "${PROJECT_DIR}/assets/rebel_logo.png" \
            --out "${ICONSET_DIR}/icon_${size}x${size}@2x.png" >/dev/null 2>&1
    done

    iconutil -c icns "$ICONSET_DIR" -o "${RESOURCES_DIR}/BLine.icns"
    rm -rf "$ICONSET_DIR"
else
    # Fallback - just copy PNG
    echo "Warning: sips/iconutil not found, using PNG icon instead of ICNS"
    cp "${PROJECT_DIR}/assets/rebel_logo.png" "${RESOURCES_DIR}/BLine.png"
fi

# Create launcher script
echo "Creating launcher script..."
cat > "${MACOS_DIR}/${APP_NAME}" << 'EOF'
#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTENTS_DIR="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"
FRAMEWORKS_DIR="${CONTENTS_DIR}/Frameworks"

# Set up Python environment
export PYTHONHOME="${FRAMEWORKS_DIR}/Python.framework/Versions/Current"
export PYTHONPATH="${RESOURCES_DIR}/bline:${PYTHONHOME}/lib/python3.11/site-packages"
export PYTHONDONTWRITEBYTECODE=1

# Add Python to PATH
export PATH="${PYTHONHOME}/bin:${PATH}"

# Set dylib paths for PySide6
export DYLD_LIBRARY_PATH="${PYTHONHOME}/lib/python3.11/site-packages/PySide6/Qt/lib:${DYLD_LIBRARY_PATH}"

# Qt plugin path
export QT_PLUGIN_PATH="${PYTHONHOME}/lib/python3.11/site-packages/PySide6/Qt/plugins"

# Change to Resources directory so relative paths work
cd "${RESOURCES_DIR}/bline"

# Launch the application
exec "${PYTHONHOME}/bin/python3" -c "from main import main; main()" "$@"
EOF

chmod +x "${MACOS_DIR}/${APP_NAME}"

# Copy Info.plist
echo "Installing Info.plist..."
cp "${SCRIPT_DIR}/Info.plist.template" "${CONTENTS_DIR}/Info.plist"

echo ""
echo "========================================"
echo "Build complete!"
echo "Application bundle created: ${BUNDLE_DIR}"
echo "========================================"
echo ""
echo "To run the app:"
echo "  open \"${BUNDLE_DIR}\""
echo ""
echo "To install to Applications:"
echo "  cp -r \"${BUNDLE_DIR}\" /Applications/"
echo ""
echo "To create a DMG, run:"
echo "  ./create-dmg.sh"

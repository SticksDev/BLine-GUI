# BLine macOS Build Instructions

This directory contains the necessary files to build a macOS application bundle (.app) and DMG installer for BLine.

## Prerequisites

- macOS 10.15 (Catalina) or later
- Python 3.11 or higher
- Xcode Command Line Tools (for code signing): `xcode-select --install`
- Internet connection (for downloading dependencies)

## Quick Start

### 1. Build the .app Bundle

```bash
cd macos
chmod +x build-macos.sh
./build-macos.sh
```

This creates `build/BLine.app` which you can:
- Run directly: `open build/BLine.app`
- Copy to Applications: `cp -r build/BLine.app /Applications/`

### 2. Create a DMG Installer (Optional)

```bash
chmod +x create-dmg.sh
./create-dmg.sh
```

This creates `BLine-0.1.3-macOS.dmg` in the project root directory.

### 3. Code Sign the App (Optional, for distribution)

```bash
chmod +x sign-app.sh

# For local testing (ad-hoc signature)
SIGNING_IDENTITY="-" ./sign-app.sh

# For distribution (requires Apple Developer certificate)
SIGNING_IDENTITY="Developer ID Application: Your Name (TEAMID)" ./sign-app.sh
```

## Distribution

### For Personal Use
Just share the `BLine.app` or the DMG file. Users can drag it to Applications.

### For Public Distribution
To distribute outside the App Store without Gatekeeper warnings:

1. **Get an Apple Developer Account** ($99/year)
2. **Code Sign** with your Developer ID certificate
3. **Notarize** with Apple:
   ```bash
   # Create a DMG first
   ./create-dmg.sh

   # Submit for notarization
   xcrun notarytool submit BLine-0.1.3-macOS.dmg \
     --apple-id your@email.com \
     --team-id TEAMID \
     --password app-specific-password \
     --wait

   # Staple the notarization ticket
   xcrun stapler staple BLine-0.1.3-macOS.dmg
   ```

## Build Output

After running `build-macos.sh`, you'll have:

```
macos/build/
├── BLine.app/
│   ├── Contents/
│   │   ├── Info.plist
│   │   ├── MacOS/
│   │   │   └── BLine (launcher script)
│   │   ├── Resources/
│   │   │   ├── BLine.icns (app icon)
│   │   │   ├── bline/ (Python application code)
│   │   │   └── assets/
│   │   └── Frameworks/
│   │       └── Python.framework/ (bundled Python + dependencies)
```

## File Structure

- `build-macos.sh` - Main build script for creating the .app bundle
- `create-dmg.sh` - Creates a distributable DMG installer
- `sign-app.sh` - Code signing script (optional)
- `Info.plist.template` - macOS app metadata
- `entitlements.plist` - Required entitlements for code signing
- `README.md` - This file

## Troubleshooting

### Python Version Issues
The build script uses your system Python. If you get errors about Python 3.11:
```bash
# Install Python 3.11 via Homebrew
brew install python@3.11

# Modify build-macos.sh to use specific Python
# Change: python3 -m venv
# To: /usr/local/opt/python@3.11/bin/python3 -m venv
```

### PySide6 Errors
If the app crashes with Qt errors, make sure you're building on macOS (not cross-compiling from Linux). PySide6 wheels are platform-specific.

### Icon Not Showing
The script uses `sips` and `iconutil` to create a proper `.icns` file. If these aren't available:
1. Install Xcode Command Line Tools: `xcode-select --install`
2. Or manually create an ICNS file and place it at `build/BLine.app/Contents/Resources/BLine.icns`

### "BLine.app is damaged" Warning
This happens with unsigned apps. Either:
1. Right-click → Open (first time only)
2. System Settings → Privacy & Security → Open Anyway
3. Or sign the app with `sign-app.sh`

## Advanced: Universal Binary (Intel + Apple Silicon)

To create a universal binary that works on both Intel and Apple Silicon Macs, you'd need to:
1. Build on an Apple Silicon Mac
2. Use `pip install --platform` to get both architectures
3. Use `lipo` to merge binaries

This is complex for Python apps. For simplicity, build on the target architecture or provide separate builds.

## Cleaning Up

```bash
# Remove build artifacts
rm -rf build/

# Remove generated DMG
rm -f ../BLine-*.dmg
```

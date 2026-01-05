# BLine AppImage Build Instructions

This directory contains the necessary files to build a Linux AppImage for BLine.

## Prerequisites

- Linux system (tested on Ubuntu/Debian and Arch-based distros)
- Python 3.11 or higher
- `wget` (for downloading appimagetool)
- Internet connection (for first build to download dependencies)

## Building the AppImage

1. Make the build script executable (if not already):
   ```bash
   chmod +x appimage/build-appimage.sh
   ```

2. Run the build script:
   ```bash
   cd appimage
   ./build-appimage.sh
   ```

3. The AppImage will be created in the project root directory as `BLine-x86_64.AppImage`

## Running the AppImage

After building, you can run BLine directly:

```bash
./BLine-x86_64.AppImage
```

Or make it executable and double-click in your file manager:

```bash
chmod +x BLine-x86_64.AppImage
```

## Distribution

The generated `BLine-x86_64.AppImage` file is completely self-contained and can be distributed to other Linux users. They just need to:

1. Download the AppImage
2. Make it executable: `chmod +x BLine-x86_64.AppImage`
3. Run it: `./BLine-x86_64.AppImage`

No installation or dependencies required!

## Troubleshooting

### FUSE Issues

If you get an error about FUSE not being available, you can either:

1. Install FUSE: `sudo apt install fuse` (Debian/Ubuntu) or `sudo pacman -S fuse2` (Arch)

2. Or extract and run the AppImage:
   ```bash
   ./BLine-x86_64.AppImage --appimage-extract
   ./squashfs-root/AppRun
   ```

### Qt Platform Plugin Issues

If you get Qt platform plugin errors, make sure you have basic X11 libraries installed:
```bash
# Debian/Ubuntu
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Arch
sudo pacman -S libxcb
```

## File Structure

- `build-appimage.sh` - Main build script
- `bline.desktop` - Desktop entry file for the application
- `README.md` - This file
- `build/` - Temporary build directory (created during build, can be deleted)

# Icon Files

This directory should contain the application icons:

- **icon.png** - 512x512 PNG (Linux, general use)
- **icon.ico** - Windows icon format
- **icon.icns** - macOS icon format

## Creating Icons

You can create these from a single high-resolution image using tools like:

- **electron-icon-builder** - `npm install -g electron-icon-builder`
- **Online converters** - CloudConvert, ConvertICO, etc.
- **Photoshop/GIMP** - Manual creation

## Quick Icon Generation

If you have a 1024x1024 PNG image named `source.png`:

```bash
# Install icon builder
npm install -g electron-icon-builder

# Generate all formats
electron-icon-builder --input=source.png --output=.
```

This will create icon.png, icon.ico, and icon.icns automatically.

## Using Custom Icons

1. Replace the icon files in this directory
2. Rebuild the application
3. Icons will be used in the built executables

## Current Status

The current package.json references these icons. If they don't exist yet, Electron will use default icons. Add your own icons to customize the app appearance.

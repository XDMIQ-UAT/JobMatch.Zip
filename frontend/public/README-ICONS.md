# PWA Icons for JobMatch.zip

This directory contains the PWA (Progressive Web App) icons for JobMatch.zip.

## Current Status

✅ **SVG Icon**: `icon.svg` - Already created and working  
⏳ **PNG Icons**: `icon-192.png` and `icon-512.png` - Need to be generated

## Quick Start - Generate PNG Icons

### Option 1: Browser-Based Generator (Easiest)

1. Open `generate-icons.html` in your web browser
2. Click "Generate Icons" (auto-generated on load)
3. Click "Download All Icons" or download each icon individually
4. Save the downloaded files to this directory (`frontend/public/`)

### Option 2: Node.js Script (Automated)

```bash
# Install sharp library (one-time)
cd frontend
npm install sharp --save-dev

# Generate icons
node ../scripts/generate-icons-node.js
```

### Option 3: PowerShell Script (Windows)

```powershell
# If ImageMagick is installed
.\scripts\generate-icons-simple.ps1
```

## Icon Specifications

- **192x192**: Standard PWA icon size
- **512x512**: High-resolution PWA icon size
- **Theme Color**: #2196f3 (Blue)
- **Design**: "JM" monogram with gradient background

## Manifest Configuration

The `manifest.json` is configured to use:
1. SVG icon (works immediately, scalable)
2. PNG icons (fallback for older browsers)

Both will work once PNG files are generated.

## Testing

After generating icons:
1. Rebuild the frontend: `npm run build`
2. Check browser console for any icon loading errors
3. Test PWA installation on mobile/desktop


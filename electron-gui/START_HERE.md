# AccuDoc Electron GUI - Start Here! 🚀

## What is This?

This is a **modern desktop application** for AccuDoc that runs on Windows, macOS, and Linux. It provides a beautiful, intuitive interface for all AccuDoc features.

## Quick Start (3 Steps!)

### 1. Install Requirements

You need:
- **Node.js 18+** → Download from https://nodejs.org
- **Python 3.8+** → Download from https://python.org

### 2. Install & Run

Open your terminal in the `electron-gui` folder and run:

```bash
npm install
npm start
```

That's it! The app will open automatically.

## What Can You Do?

### 🔍 Scan Repositories
Click "Scan Repository" → Browse to a code folder → Click "Start Scan"

### 📝 Generate Documentation
Click "Generate Docs" → Choose repo and output location → Click "Generate"

### 📊 Analyze Code
Click "Code Analysis" → Choose analysis type → View results

### ❤️ Check Health
Click "Health Dashboard" → Enter repo path → Click "Check Health"

### ⌨️ Use Terminal
Click "Terminal" → Type commands directly (like `scan /path/to/repo`)

### ⚙️ Customize Settings
Click "Settings" → Adjust preferences → Click "Save"

## Keyboard Shortcuts

- `Ctrl+O` - Open Repository
- `Ctrl+R` - Scan Repository  
- `Ctrl+G` - Generate Documentation
- `Ctrl+T` - Open Terminal
- `Ctrl+,` - Settings

## Building for Distribution

Want to create an installer?

```bash
npm run build        # Creates executables for all platforms
```

Or build for specific platforms:

```bash
npm run build:win    # Windows
npm run build:mac    # macOS
npm run build:linux  # Linux
```

Find your built apps in the `dist/` folder!

## Need Help?

- **Setup Issues?** → See `GETTING_STARTED.md`
- **Feature Guide?** → See `README.md`
- **Quick Reference?** → See `QUICKSTART.md`

## Tips

- The app saves your recent repositories for quick access
- All settings are saved automatically
- Use the terminal for advanced CLI features
- Export data to CSV/JSON for analysis

## What's Next?

1. ✅ Scan your first repository
2. ✅ Generate some documentation
3. ✅ Try the code analysis features
4. ✅ Check out the health dashboard
5. ✅ Explore all the features!

Enjoy using AccuDoc! 🎉

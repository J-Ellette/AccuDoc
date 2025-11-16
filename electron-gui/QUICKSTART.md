# Quick Launch Guide

## For Users (Running the App)

### Windows
1. Install Node.js from https://nodejs.org/
2. Install Python from https://python.org/
3. Open PowerShell in the `electron-gui` folder
4. Run:
   ```powershell
   npm install
   npm start
   ```

### macOS/Linux
1. Install Node.js and Python
2. Open Terminal in the `electron-gui` folder
3. Run:
   ```bash
   npm install
   npm start
   ```

## For Developers

### First Time Setup
```bash
cd AccuDoc/electron-gui
npm install
cd ..
pip install -r requirements.txt
cd electron-gui
npm start
```

### Daily Development
```bash
npm start
```

## Building Executables

### All Platforms
```bash
npm run build
```

### Specific Platforms
```bash
npm run build:win    # Windows
npm run build:mac    # macOS
npm run build:linux  # Linux
```

## Troubleshooting

**App won't start?**
- Make sure you're in the `electron-gui` folder
- Delete `node_modules` and run `npm install` again

**Python errors?**
- Install Python 3.8+
- Make sure it's in your PATH
- Set custom path in Settings if needed

**Need help?**
- See GETTING_STARTED.md for detailed instructions
- See README.md for full documentation

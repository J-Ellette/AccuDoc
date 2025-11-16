const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const os = require('os');

// Python bridge for executing AccuDoc CLI commands
class PythonBridge {
  constructor() {
    this.pythonPath = this.findPythonPath();
    this.accudocPath = this.findAccuDocPath();
  }

  findPythonPath() {
    // Check if running in packaged app
    if (app.isPackaged) {
      // Look for bundled Python
      const bundledPython = path.join(process.resourcesPath, 'python');
      if (fs.existsSync(bundledPython)) {
        return path.join(bundledPython, 'python');
      }
    }
    // Default to system Python
    return process.platform === 'win32' ? 'python' : 'python3';
  }

  findAccuDocPath() {
    if (app.isPackaged) {
      return path.join(process.resourcesPath, 'python');
    }
    // Development mode - go up from electron-gui to parent directory
    return path.join(__dirname, '..', '..', '..');
  }

  async executeCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
      const cliPath = path.join(this.accudocPath, 'accudoc_cli.py');
      
      // Normalize paths for Windows, but skip URLs
      const normalizedArgs = args.map(arg => {
        // Skip normalization for URLs
        if (typeof arg === 'string') {
          const isUrl = arg.startsWith('http://') || 
                        arg.startsWith('https://') || 
                        arg.startsWith('git@') ||
                        arg.startsWith('ssh://');
          
          // Only normalize local file paths, not URLs
          if (!isUrl && (arg.includes('\\') || arg.includes('/'))) {
            return path.normalize(arg);
          }
        }
        return arg;
      });
      
      const allArgs = [cliPath, command, ...normalizedArgs];

      console.log(`Executing: ${this.pythonPath} ${allArgs.join(' ')}`);
      console.log(`Working directory: ${this.accudocPath}`);

      const pythonProcess = spawn(this.pythonPath, allArgs, {
        cwd: this.accudocPath,
        env: { 
          ...process.env, 
          PYTHONPATH: this.accudocPath,
          PYTHONIOENCODING: 'utf-8'  // Ensure proper encoding
        },
        windowsHide: true,  // Hide console window on Windows
        ...options
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        const text = data.toString('utf-8');
        stdout += text;
        if (options.onProgress) {
          options.onProgress({ type: 'stdout', data: text });
        }
      });

      pythonProcess.stderr.on('data', (data) => {
        const text = data.toString('utf-8');
        stderr += text;
        if (options.onProgress) {
          options.onProgress({ type: 'stderr', data: text });
        }
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          const errorMsg = stderr || stdout || 'Unknown error';
          reject(new Error(`Command failed with code ${code}\n${errorMsg}`));
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  }
}

let mainWindow;
let pythonBridge;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, '../../assets/icon.png')
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  // Create application menu
  createMenu();

  // Open DevTools in development mode
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Repository...',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.send('menu-open-repository');
          }
        },
        { type: 'separator' },
        {
          label: 'Settings',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            mainWindow.webContents.send('menu-open-settings');
          }
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Tools',
      submenu: [
        {
          label: 'Scan Repository',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.webContents.send('menu-scan-repository');
          }
        },
        {
          label: 'Generate Documentation',
          accelerator: 'CmdOrCtrl+G',
          click: () => {
            mainWindow.webContents.send('menu-generate-docs');
          }
        },
        { type: 'separator' },
        {
          label: 'Code Analysis',
          click: () => {
            mainWindow.webContents.send('menu-show-analysis');
          }
        },
        {
          label: 'Health Dashboard',
          click: () => {
            mainWindow.webContents.send('menu-show-health');
          }
        },
        {
          label: 'Terminal',
          accelerator: 'CmdOrCtrl+T',
          click: () => {
            mainWindow.webContents.send('menu-show-terminal');
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            require('electron').shell.openExternal('https://github.com/J-Ellette/AccuDoc');
          }
        },
        { type: 'separator' },
        {
          label: 'About AccuDoc',
          click: () => {
            mainWindow.webContents.send('menu-show-about');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Initialize app
app.whenReady().then(() => {
  pythonBridge = new PythonBridge();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers
ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result.filePaths[0];
});

ipcMain.handle('save-file', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result.filePath;
});

ipcMain.handle('execute-command', async (event, command, args, options) => {
  try {
    // Validate repository path if first argument looks like a local path (not a URL)
    if (args.length > 0 && typeof args[0] === 'string') {
      const potentialPath = args[0];
      const isUrl = potentialPath.startsWith('http://') || 
                    potentialPath.startsWith('https://') || 
                    potentialPath.startsWith('git@') ||
                    potentialPath.startsWith('ssh://');
      
      // Only validate local file paths, skip URLs
      if (!isUrl && (potentialPath.includes('\\') || potentialPath.includes('/'))) {
        try {
          const fsSync = require('fs');
          const stats = fsSync.statSync(potentialPath);
          if (!stats.isDirectory()) {
            throw new Error(`Path is not a directory: ${potentialPath}`);
          }
          // Check if we can access the directory
          fsSync.accessSync(potentialPath, fsSync.constants.R_OK);
        } catch (error) {
          if (error.code === 'ENOENT') {
            throw new Error(`Repository path does not exist: ${potentialPath}`);
          } else if (error.code === 'EACCES' || error.code === 'EPERM') {
            throw new Error(`Permission denied. Please ensure you have read access to: ${potentialPath}\n\nTry running the application as administrator or check folder permissions.`);
          }
          throw error;
        }
      }
    }

    const result = await pythonBridge.executeCommand(command, args, {
      ...options,
      onProgress: (data) => {
        event.sender.send('command-progress', data);
      }
    });
    return result;
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('get-accudoc-path', async () => {
  return pythonBridge.accudocPath;
});

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return content;
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    await fs.writeFile(filePath, content, 'utf-8');
    return true;
  } catch (error) {
    throw error;
  }
});

ipcMain.handle('get-app-path', async (event, name) => {
  return app.getPath(name);
});

// Validate path for drag-drop
ipcMain.handle('validate-path', async (event, filePath) => {
  try {
    const stats = await fs.stat(filePath);
    return {
      isDirectory: stats.isDirectory(),
      isFile: stats.isFile(),
      exists: true
    };
  } catch (error) {
    return {
      isDirectory: false,
      isFile: false,
      exists: false
    };
  }
});

// Save temporary file
ipcMain.handle('save-temp-file', async (event, options) => {
  try {
    const tempDir = os.tmpdir();
    const timestamp = Date.now();
    const tempPath = path.join(tempDir, `accudoc_temp_${timestamp}${options.extension || '.tmp'}`);
    await fs.writeFile(tempPath, options.content, 'utf-8');
    return tempPath;
  } catch (error) {
    throw new Error(`Failed to save temp file: ${error.message}`);
  }
});

// Save file dialog
ipcMain.handle('save-file-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog({
    defaultPath: options.defaultPath || 'file',
    filters: options.filters || [{ name: 'All Files', extensions: ['*'] }]
  });
  return result.canceled ? null : result.filePath;
});

// Open folder in file explorer
ipcMain.handle('open-folder', async (event, folderPath) => {
  const { shell } = require('electron');
  try {
    await shell.openPath(folderPath);
    return true;
  } catch (error) {
    throw new Error(`Failed to open folder: ${error.message}`);
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

console.log('AccuDoc Electron App Started');
console.log('AccuDoc Path:', pythonBridge?.accudocPath);

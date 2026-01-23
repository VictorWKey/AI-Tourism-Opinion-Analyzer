import { app, BrowserWindow } from 'electron';
import path from 'node:path';
import started from 'electron-squirrel-startup';
import { registerIpcHandlers } from './main/ipc';
import { initializeStore } from './main/utils/store';
import { getPythonBridge, stopPythonBridge } from './main/python/bridge';

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

let mainWindow: BrowserWindow | null = null;

const createWindow = (): void => {
  // Create the browser window with improved settings.
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false, // Show when ready to prevent visual flash
  });

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Load the app
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(
      path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`),
    );
  }

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

/**
 * Initialize Python bridge (lazy initialization)
 * The bridge will start on first use, but we warm it up here
 */
async function initializePythonBridge(): Promise<void> {
  try {
    const bridge = getPythonBridge();
    
    // Listen for bridge events
    bridge.on('error', (error: string) => {
      console.error('[Main] Python bridge error:', error);
    });

    bridge.on('close', (code: number) => {
      console.log('[Main] Python bridge closed with code:', code);
    });

    // Start the bridge in background (don't block app startup)
    bridge.start().then(() => {
      console.log('[Main] Python bridge started successfully');
    }).catch((error) => {
      console.error('[Main] Failed to start Python bridge:', error);
    });
  } catch (error) {
    console.error('[Main] Error initializing Python bridge:', error);
  }
}

// Initialize app when ready
app.on('ready', async () => {
  await initializeStore();
  registerIpcHandlers();
  createWindow();
  
  // Initialize Python bridge after window is created
  initializePythonBridge();
});

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS, re-create a window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Clean up Python bridge before quitting
app.on('before-quit', () => {
  console.log('[Main] Stopping Python bridge before quit...');
  stopPythonBridge();
});

// Export mainWindow for IPC handlers that need to send events
export { mainWindow };

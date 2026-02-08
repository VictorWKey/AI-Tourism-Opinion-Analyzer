/// <reference types="@electron-forge/plugin-vite/forge-vite-env" />

import { app, BrowserWindow, nativeTheme } from 'electron';
import path from 'node:path';
import started from 'electron-squirrel-startup';
import { registerIpcHandlers } from './main/ipc';
import { initializeStore, getLLMConfig } from './main/utils/store';
import { getPythonBridge, stopPythonBridge } from './main/python/bridge';
import { ollamaInstaller } from './main/setup/OllamaInstaller';

// Force light theme - ignore system preference
nativeTheme.themeSource = 'light';

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
      // Only log actual errors (contains error keywords)
      if (error.toLowerCase().includes('error') || 
          error.toLowerCase().includes('exception') ||
          error.toLowerCase().includes('traceback') ||
          error.toLowerCase().includes('failed')) {
        console.error('[Main] Python Error:', error);
      }
    });

    bridge.on('info', (message: string) => {
      console.log('[Main]', message);
    });

    bridge.on('close', (code: number) => {
      console.log('[Main] Python bridge closed with code:', code);
    });

    // Start the bridge in background (don't block app startup)
    bridge.start().then(() => {
      console.log('[Main] Python bridge started successfully');
      
      // After bridge is ready, preload ML models into memory in background
      // This is fire-and-forget: if it fails, models will be loaded on first use
      bridge.execute({ action: 'preload_models' }, 300000).then((result) => {
        if (result.success) {
          console.log('[Main] ML models preloaded into memory:', result.details);
        } else {
          console.warn('[Main] ML model preload incomplete:', result.details);
        }
      }).catch((error) => {
        console.warn('[Main] ML model preload failed (will load on demand):', error);
      });
    }).catch((error) => {
      console.error('[Main] Failed to start Python bridge:', error);
    });
  } catch (error) {
    console.error('[Main] Error initializing Python bridge:', error);
  }
}

/**
 * Auto-start Ollama service if configured for local LLM mode
 * Checks if Ollama is installed but not running, and starts it automatically
 */
async function autoStartOllama(): Promise<void> {
  try {
    const llmConfig = getLLMConfig();
    if (llmConfig.mode !== 'local') {
      return; // Only auto-start when using local LLM mode
    }

    const installed = await ollamaInstaller.isInstalled();
    if (!installed) {
      console.log('[Main] Ollama not installed, skipping auto-start');
      return;
    }

    const running = await ollamaInstaller.isRunning();
    if (running) {
      console.log('[Main] Ollama already running');
      return;
    }

    console.log('[Main] Auto-starting Ollama service...');
    await ollamaInstaller.startService();
    console.log('[Main] Ollama service started successfully');
  } catch (error) {
    console.warn('[Main] Failed to auto-start Ollama:', error instanceof Error ? error.message : error);
  }
}

// Initialize app when ready
app.on('ready', async () => {
  await initializeStore();
  registerIpcHandlers();
  createWindow();
  
  // Initialize Python bridge after window is created
  initializePythonBridge();

  // Auto-start Ollama if LLM mode is 'local' and Ollama is installed but not running
  autoStartOllama();
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

/**
 * Setup IPC Handlers
 * ===================
 * IPC handlers for the setup wizard and first-run configuration.
 */

import { ipcMain, BrowserWindow } from 'electron';
import { setupManager, type SetupState } from '../setup/SetupManager';
import { ollamaInstaller } from '../setup/OllamaInstaller';
import { modelDownloader } from '../setup/ModelDownloader';
import { pythonSetup } from '../setup/PythonSetup';
import { getStore } from '../utils/store';
import { getPythonBridge } from '../python/bridge';

/**
 * Register all setup-related IPC handlers
 */
export function registerSetupHandlers(): void {
  // Check if this is the first run
  ipcMain.handle('setup:is-first-run', () => {
    return setupManager.isFirstRun();
  });

  // Get current setup state
  ipcMain.handle('setup:get-state', () => {
    return setupManager.getSetupState();
  });

  // Run system requirements check
  ipcMain.handle('setup:system-check', async () => {
    return setupManager.runSystemCheck();
  });

  // ============================================
  // Python Environment Setup Handlers
  // ============================================

  // Check Python setup status
  ipcMain.handle('setup:check-python', async () => {
    return pythonSetup.checkStatus();
  });

  // Setup Python environment (venv + dependencies)
  ipcMain.handle('setup:setup-python', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);

    return pythonSetup.setup((progress) => {
      window?.webContents.send('setup:python-progress', progress);
    });
  });

  // Get Python paths
  ipcMain.handle('setup:get-python-paths', () => {
    return {
      pythonDir: pythonSetup.getPythonDir(),
      venvDir: pythonSetup.getVenvDir(),
      pythonPath: pythonSetup.getPythonPath(),
    };
  });

  // Set LLM provider choice (ollama or openai)
  ipcMain.handle('setup:set-llm-provider', (_, provider: 'ollama' | 'openai') => {
    setupManager.updateSetupState({ llmProvider: provider });
    
    // Also update the app settings
    const store = getStore();
    store.set('llm.mode', provider === 'ollama' ? 'local' : 'api');
    
    return { success: true };
  });

  // Check if Ollama is installed
  ipcMain.handle('setup:check-ollama', async () => {
    const installed = await ollamaInstaller.isInstalled();
    const running = await ollamaInstaller.isRunning();
    const version = installed ? await ollamaInstaller.getVersion() : null;
    
    return { installed, running, version };
  });

  // Install Ollama
  ipcMain.handle('setup:install-ollama', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);

    return ollamaInstaller.install((progress) => {
      window?.webContents.send('setup:ollama-progress', progress);
    });
  });

  // Start Ollama service
  ipcMain.handle('setup:start-ollama', async () => {
    try {
      await ollamaInstaller.startService();
      setupManager.updateSetupState({ ollamaInstalled: true });
      return { success: true };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return { success: false, error: message };
    }
  });

  // Pull Ollama model
  ipcMain.handle('setup:pull-ollama-model', async (event, modelName: string) => {
    const window = BrowserWindow.fromWebContents(event.sender);

    const success = await ollamaInstaller.pullModel(modelName, (progress) => {
      window?.webContents.send('setup:ollama-progress', progress);
    });

    if (success) {
      setupManager.updateSetupState({ ollamaModelReady: true });
      
      // Also save the model name to settings
      const store = getStore();
      store.set('llm.localModel', modelName);
    }
    
    return { success };
  });

  // Check if a specific Ollama model is available
  ipcMain.handle('setup:has-ollama-model', async (_, modelName: string) => {
    return ollamaInstaller.hasModel(modelName);
  });

  // List installed Ollama models
  ipcMain.handle('setup:list-ollama-models', async () => {
    return ollamaInstaller.listModels();
  });

  // Validate OpenAI API key
  ipcMain.handle('setup:validate-openai-key', async (_, apiKey: string) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch('https://api.openai.com/v1/models', {
        headers: { Authorization: `Bearer ${apiKey}` },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const valid = response.ok;
      if (valid) {
        setupManager.updateSetupState({ openaiKeyConfigured: true });
        
        // Save the API key to settings
        const store = getStore();
        store.set('llm.apiKey', apiKey);
        store.set('llm.apiProvider', 'openai');
      }
      
      return { valid, error: valid ? null : 'Invalid API key' };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return { valid: false, error: message };
    }
  });

  // Check models download status
  ipcMain.handle('setup:check-models', async () => {
    return modelDownloader.checkModelsStatus();
  });

  // Download all required models
  ipcMain.handle('setup:download-models', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);

    return modelDownloader.downloadAllModels((progress) => {
      window?.webContents.send('setup:model-progress', progress);
      
      // Update setup state when models complete
      if (progress.status === 'complete') {
        const validKeys = ['sentiment', 'embeddings', 'subjectivity', 'categories'];
        if (validKeys.includes(progress.model)) {
          const updates: Record<string, boolean> = { [progress.model]: true };
          setupManager.updateModelsDownloaded(updates as Partial<SetupState['modelsDownloaded']>);
        }
      }
    });
  });

  // Get total download size for models
  ipcMain.handle('setup:get-download-size', async () => {
    const sizeMB = await modelDownloader.getTotalDownloadSize();
    const sizeFormatted = modelDownloader.getEstimatedTotalSize();
    return { size_mb: sizeMB, formatted: sizeFormatted };
  });

  // Get list of required models
  ipcMain.handle('setup:get-required-models', () => {
    return modelDownloader.getRequiredModels();
  });

  // Mark setup as complete
  ipcMain.handle('setup:complete', async () => {
    setupManager.markSetupComplete();
    
    // Restart Python bridge to ensure it uses the correct venv Python path
    // This is necessary because the bridge may have been initialized before
    // the Python environment was fully set up
    try {
      const bridge = getPythonBridge();
      await bridge.restart();
      console.log('[Setup] Python bridge restarted with updated configuration');
    } catch (error) {
      console.error('[Setup] Failed to restart Python bridge:', error);
    }
    
    return { success: true };
  });

  // Reset setup state (for testing)
  ipcMain.handle('setup:reset', () => {
    setupManager.resetSetupState();
    return { success: true };
  });

  // Clean Python environment and reinstall
  ipcMain.handle('setup:clean-python', async () => {
    return pythonSetup.cleanEnvironment();
  });

  console.log('[IPC] Setup handlers registered');
}

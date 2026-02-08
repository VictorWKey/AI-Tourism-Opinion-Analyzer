// ============================================
// Ollama IPC Handlers
// ============================================

import { ipcMain, BrowserWindow } from 'electron';
import type { OllamaStatus, OllamaModel } from '../../shared/types';

const OLLAMA_BASE_URL = 'http://localhost:11434';

// Track whether we've already logged the connection failure to avoid spam
let ollamaConnectionFailureLogged = false;

interface OllamaApiModel {
  name: string;
  size: number;
  modified_at: string;
  digest?: string;
  details?: Record<string, unknown>;
}

interface OllamaListResponse {
  models: OllamaApiModel[];
}

interface OllamaVersionResponse {
  version: string;
}

/**
 * Check if Ollama is running and get its status
 */
async function checkOllamaStatus(): Promise<OllamaStatus> {
  try {
    // Check if Ollama is running by hitting the version endpoint
    const versionResponse = await fetch(`${OLLAMA_BASE_URL}/api/version`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    if (!versionResponse.ok) {
      return { running: false };
    }

    const versionData = await versionResponse.json() as OllamaVersionResponse;

    // Connection succeeded, reset the failure log flag
    ollamaConnectionFailureLogged = false;

    // Get list of available models
    const modelsResponse = await fetch(`${OLLAMA_BASE_URL}/api/tags`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });

    let models: OllamaModel[] = [];
    if (modelsResponse.ok) {
      const modelsData = await modelsResponse.json() as OllamaListResponse;
      models = (modelsData.models || []).map((m: OllamaApiModel) => ({
        name: m.name,
        size: m.size,
        modified: m.modified_at,
      }));
    }

    return {
      running: true,
      version: versionData.version,
      models,
    };
  } catch (error) {
    // Only log the first connection failure to avoid spamming the console
    if (!ollamaConnectionFailureLogged) {
      console.warn('[Ollama] Status check failed: Ollama is not running or not reachable at', OLLAMA_BASE_URL);
      ollamaConnectionFailureLogged = true;
    }
    return { running: false };
  }
}

/**
 * List available Ollama models
 */
async function listOllamaModels(): Promise<OllamaModel[]> {
  try {
    const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`, {
      method: 'GET',
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json() as OllamaListResponse;
    return (data.models || []).map((m: OllamaApiModel) => ({
      name: m.name,
      size: m.size,
      modified: m.modified_at,
    }));
  } catch (error) {
    console.error('[Ollama] Failed to list models:', error);
    return [];
  }
}

/**
 * Pull (download) an Ollama model with progress reporting
 */
async function pullOllamaModel(modelName: string): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${OLLAMA_BASE_URL}/api/pull`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: modelName, stream: true }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    const windows = BrowserWindow.getAllWindows();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim());

      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          
          // Send progress to renderer
          windows.forEach(win => {
            win.webContents.send('ollama:pull-progress', {
              model: modelName,
              status: data.status,
              completed: data.completed,
              total: data.total,
              digest: data.digest,
            });
          });
        } catch {
          // Skip invalid JSON lines
        }
      }
    }

    return { success: true };
  } catch (error) {
    console.error('[Ollama] Failed to pull model:', error);
    return { success: false, error: (error as Error).message };
  }
}

/**
 * Delete an Ollama model
 * Includes protection: cannot delete the last remaining model
 */
async function deleteOllamaModel(modelName: string): Promise<{ success: boolean; error?: string; isLastModel?: boolean }> {
  try {
    // First check how many models are installed
    const modelsResponse = await fetch(`${OLLAMA_BASE_URL}/api/tags`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });

    if (modelsResponse.ok) {
      const modelsData = await modelsResponse.json() as OllamaListResponse;
      const modelCount = (modelsData.models || []).length;
      
      // Prevent deleting the last model
      if (modelCount <= 1) {
        return { 
          success: false, 
          error: 'No se puede eliminar el último modelo. Ollama requiere al menos un modelo instalado para funcionar correctamente.',
          isLastModel: true
        };
      }
    }

    const response = await fetch(`${OLLAMA_BASE_URL}/api/delete`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: modelName }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    return { success: true };
  } catch (error) {
    console.error('[Ollama] Failed to delete model:', error);
    return { success: false, error: (error as Error).message };
  }
}

/**
 * Get the count of installed models
 * Used to determine if the delete button should be enabled
 */
async function getOllamaModelCount(): Promise<number> {
  try {
    const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return 0;
    }

    const data = await response.json() as OllamaListResponse;
    return (data.models || []).length;
  } catch {
    return 0;
  }
}

export function registerOllamaHandlers(): void {
  ipcMain.handle('ollama:check-status', async () => {
    return checkOllamaStatus();
  });

  ipcMain.handle('ollama:list-models', async () => {
    return listOllamaModels();
  });

  ipcMain.handle('ollama:pull-model', async (_, modelName: string) => {
    return pullOllamaModel(modelName);
  });

  ipcMain.handle('ollama:delete-model', async (_, modelName: string) => {
    return deleteOllamaModel(modelName);
  });

  ipcMain.handle('ollama:get-model-count', async () => {
    return getOllamaModelCount();
  });

  console.log('[IPC] Ollama handlers registered');
}

/**
 * ModelDownloader - HuggingFace and custom model downloader
 * ==========================================================
 * Handles downloading of required ML models with progress tracking.
 */

import { getPythonBridge } from '../python/bridge';
import { BrowserWindow } from 'electron';

export interface ModelInfo {
  name: string;
  displayName: string;
  size: string;
  type: 'huggingface' | 'bundled';
  required: boolean;
}

export interface ModelDownloadProgress {
  model: string;
  progress: number;
  status: 'pending' | 'downloading' | 'complete' | 'error';
  message?: string;
  error?: string;
}

export interface ModelsStatus {
  sentiment: boolean;
  embeddings: boolean;
  subjectivity: boolean;
  categories: boolean;
}

/**
 * ModelDownloader class for managing ML model downloads
 */
export class ModelDownloader {
  static readonly REQUIRED_MODELS: ModelInfo[] = [
    {
      name: 'nlptown/bert-base-multilingual-uncased-sentiment',
      displayName: 'Sentiment Analysis',
      size: '',
      type: 'huggingface',
      required: true,
    },
    {
      // BERTopic in fase_06 uses this model for topic analysis embeddings
      name: 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
      displayName: 'Topic Embeddings',
      size: '',
      type: 'huggingface',
      required: true,
    },
    {
      name: 'victorwkey/tourism-subjectivity-bert',
      displayName: 'Subjectivity Classifier',
      size: '',
      type: 'huggingface',
      required: true,
    },
    {
      name: 'victorwkey/tourism-categories-bert',
      displayName: 'Category Classifier',
      size: '',
      type: 'huggingface',
      required: true,
    },
  ];

  private progressCallbacks: Set<(progress: ModelDownloadProgress) => void> = new Set();

  /**
   * Check which models are already downloaded
   * Includes retry logic in case the Python bridge is restarting
   */
  async checkModelsStatus(retryCount = 0): Promise<ModelsStatus> {
    const defaultStatus: ModelsStatus = {
      sentiment: false,
      embeddings: false,
      subjectivity: false,
      categories: false,
    };
    
    try {
      const bridge = getPythonBridge();
      const result = await bridge.execute({
        action: 'check_models_status',
      });
      
      if (result.status && typeof result.status === 'object') {
        const status = result.status as Record<string, unknown>;
        return {
          sentiment: Boolean(status.sentiment),
          embeddings: Boolean(status.embeddings),
          subjectivity: Boolean(status.subjectivity),
          categories: Boolean(status.categories),
        };
      }
      
      return defaultStatus;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.error('[ModelDownloader] Error checking models status:', error);
      
      // Retry if bridge was stopped/restarting (up to 2 retries)
      if (errorMsg.includes('Python bridge stopped') && retryCount < 2) {
        const delay = (retryCount + 1) * 1500;
        console.log(`[ModelDownloader] Bridge restarting, retrying in ${delay}ms (attempt ${retryCount + 2}/3)...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.checkModelsStatus(retryCount + 1);
      }
      
      return defaultStatus;
    }
  }

  /**
   * Download all required models
   * Returns { success, error?, details? } so the UI can show meaningful errors
   */
  async downloadAllModels(
    onProgress: (progress: ModelDownloadProgress) => void
  ): Promise<{ success: boolean; error?: string; details?: Record<string, boolean> }> {
    try {
      const bridge = getPythonBridge();
      
      // SAFETY NET: Ensure the bridge is using the venv Python, not system Python.
      // The bridge singleton may have been created at app startup before the venv existed.
      // refreshPythonPath() is a no-op if the path hasn't changed.
      bridge.refreshPythonPath();
      
      // If the bridge process isn't running yet, start() will use the (now refreshed) path.
      // If it IS running but with the wrong Python, we need to restart it.
      const status = bridge.getStatus();
      if (status.running) {
        // Verify the running Python has the required packages
        try {
          const healthCheck = await bridge.execute({ action: 'ping' }, 5000);
          if (!healthCheck.success) {
            console.log('[ModelDownloader] Bridge health check failed, restarting...');
            await bridge.restart();
          }
        } catch {
          console.log('[ModelDownloader] Bridge not responsive, restarting...');
          await bridge.restart();
        }
      }
      
      // Register progress callback
      this.progressCallbacks.add(onProgress);

      // IMPORTANT: Register progress listener BEFORE calling execute
      // so we don't miss any progress events
      const progressHandler = (data: { type: string; subtype?: string; model: string; progress: number; message?: string }) => {
        // Check for subtype === 'model_download' (Python sends type: 'progress', subtype: 'model_download')
        if (data.subtype === 'model_download' || data.type === 'model_download') {
          console.log('[ModelDownloader] Progress:', data.model, data.progress + '%');
          
          const progress: ModelDownloadProgress = {
            model: data.model,
            progress: data.progress,
            status: data.progress === 100 ? 'complete' : data.progress < 0 ? 'error' : 'downloading',
            message: data.message,
          };
          
          onProgress(progress);

          // Forward to all renderer windows
          BrowserWindow.getAllWindows().forEach((win) => {
            win.webContents.send('setup:model-progress', progress);
          });
        }
      };

      // Attach listener BEFORE execute
      bridge.on('progress', progressHandler);

      // Start Python model download (30 min timeout for large downloads)
      const result = await bridge.execute({
        action: 'download_models',
      }, 1800000);

      // Cleanup listener after download completes
      bridge.off('progress', progressHandler);
      this.progressCallbacks.delete(onProgress);

      if (result.success) {
        return { success: true };
      }

      // Build descriptive error from details
      const details = result.details as Record<string, boolean> | undefined;
      const failedModels = details
        ? Object.entries(details).filter(([, ok]) => !ok).map(([name]) => name)
        : [];
      const errorMsg = result.error
        ? String(result.error)
        : failedModels.length > 0
          ? `Failed models: ${failedModels.join(', ')}`
          : 'Unknown download error';
      
      console.error('[ModelDownloader] Download failed:', errorMsg, 'details:', details);
      return { success: false, error: errorMsg, details: details as Record<string, boolean> };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('[ModelDownloader] Exception during download:', errorMessage);
      onProgress({
        model: 'all',
        progress: 0,
        status: 'error',
        error: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }

  /**
   * Download a specific model
   */
  async downloadModel(
    modelKey: string,
    onProgress: (progress: ModelDownloadProgress) => void
  ): Promise<boolean> {
    try {
      const bridge = getPythonBridge();
      
      const result = await bridge.execute({
        action: 'download_model',
        model: modelKey,
      });

      return result.success || false;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onProgress({
        model: modelKey,
        progress: 0,
        status: 'error',
        error: errorMessage,
      });
      return false;
    }
  }

  /**
   * Get total download size for all models
   */
  async getTotalDownloadSize(): Promise<number> {
    try {
      const bridge = getPythonBridge();
      const result = await bridge.execute({
        action: 'get_download_size',
      });
      const sizeMb = result.size_mb;
      return typeof sizeMb === 'number' ? sizeMb : 1380;
    } catch {
      // Return estimated size if Python call fails
      return 1380; // MB
    }
  }

  /**
   * Get list of required models with their info
   */
  getRequiredModels(): ModelInfo[] {
    return ModelDownloader.REQUIRED_MODELS;
  }

  /**
   * Calculate total estimated download size
   */
  getEstimatedTotalSize(): string {
    const totalMB = ModelDownloader.REQUIRED_MODELS.reduce((total, model) => {
      const size = parseInt(model.size.replace(' MB', ''), 10);
      return total + (isNaN(size) ? 0 : size);
    }, 0);
    
    if (totalMB >= 1024) {
      return `${(totalMB / 1024).toFixed(1)} GB`;
    }
    return `${totalMB} MB`;
  }
}

// Singleton instance
export const modelDownloader = new ModelDownloader();

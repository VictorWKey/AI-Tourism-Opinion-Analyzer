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
      displayName: 'Sentiment Analysis (BERT)',
      size: '420 MB',
      type: 'huggingface',
      required: true,
    },
    {
      name: 'sentence-transformers/all-MiniLM-L6-v2',
      displayName: 'Sentence Embeddings',
      size: '80 MB',
      type: 'huggingface',
      required: true,
    },
    {
      name: 'subjectivity_task',
      displayName: 'Subjectivity Classifier (Custom)',
      size: '440 MB',
      type: 'bundled',
      required: true,
    },
    {
      name: 'multilabel_task',
      displayName: 'Category Classifier (Custom)',
      size: '440 MB',
      type: 'bundled',
      required: true,
    },
  ];

  private progressCallbacks: Set<(progress: ModelDownloadProgress) => void> = new Set();

  /**
   * Check which models are already downloaded
   */
  async checkModelsStatus(): Promise<ModelsStatus> {
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
      console.error('[ModelDownloader] Error checking models status:', error);
      return defaultStatus;
    }
  }

  /**
   * Download all required models
   */
  async downloadAllModels(
    onProgress: (progress: ModelDownloadProgress) => void
  ): Promise<boolean> {
    try {
      const bridge = getPythonBridge();
      
      // Register progress callback
      this.progressCallbacks.add(onProgress);

      // Start Python model download
      const result = await bridge.execute({
        action: 'download_models',
      });

      // Forward progress events from bridge
      bridge.on('progress', (data: { type: string; model: string; progress: number; message?: string }) => {
        if (data.type === 'model_download') {
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
      });

      // Cleanup callback
      this.progressCallbacks.delete(onProgress);

      return result.success || false;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onProgress({
        model: 'all',
        progress: 0,
        status: 'error',
        error: errorMessage,
      });
      return false;
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

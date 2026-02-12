/**
 * Ollama Store
 * =============
 * Shared Zustand store for Ollama LLM status.
 *
 * All components (Sidebar, Settings, Home, etc.) subscribe to the same store
 * so that any status change (start/stop/pull/delete) is reflected everywhere
 * instantly — no more waiting for a 30-second poll.
 */

import { create } from 'zustand';
import type { OllamaModel } from '../../shared/types';

interface OllamaState {
  isRunning: boolean;
  version: string | null;
  models: OllamaModel[];
  currentModel: string | null;
  isLoading: boolean;
  error: string | null;
}

interface OllamaActions {
  /** Check Ollama running status + refresh models list */
  checkStatus: (llmMode: 'local' | 'api') => Promise<void>;
  /** Pull (download) a model then refresh the list */
  pullModel: (modelName: string) => Promise<boolean>;
  /** Delete a model (with last-model protection) then refresh */
  deleteModel: (modelName: string) => Promise<boolean>;
  /** Switch the active model locally (no IPC) */
  selectModel: (modelName: string) => void;
  /** Reset to default idle state */
  reset: () => void;
}

const defaultState: OllamaState = {
  isRunning: false,
  version: null,
  models: [],
  currentModel: null,
  isLoading: true,
  error: null,
};

export const useOllamaStore = create<OllamaState & OllamaActions>((set) => ({
  ...defaultState,

  checkStatus: async (llmMode) => {
    if (llmMode !== 'local') {
      set({ ...defaultState, isLoading: false });
      return;
    }

    set((s) => ({ ...s, isLoading: true, error: null }));

    try {
      const status = await window.electronAPI.ollama.checkStatus();
      const models = status.running
        ? await window.electronAPI.ollama.listModels()
        : [];

      set((prev) => {
        const prevModelStillExists =
          prev.currentModel && models.some((m) => m.name === prev.currentModel);
        const nextModel = prevModelStillExists
          ? prev.currentModel
          : models.length > 0
            ? models[0].name
            : null;

        return {
          isRunning: status.running,
          version: status.version || null,
          models,
          currentModel: nextModel,
          isLoading: false,
          error: null,
        };
      });
    } catch (error) {
      set((prev) => ({
        ...prev,
        isRunning: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to check Ollama status',
      }));
    }
  },

  pullModel: async (modelName) => {
    set((s) => ({ ...s, isLoading: true }));

    try {
      const result = await window.electronAPI.ollama.pullModel(modelName);

      if (result.success) {
        const models = await window.electronAPI.ollama.listModels();
        set((prev) => {
          const prevModelStillExists =
            prev.currentModel && models.some((m) => m.name === prev.currentModel);
          return {
            ...prev,
            models,
            currentModel: prevModelStillExists
              ? prev.currentModel
              : prev.currentModel || (models.length > 0 ? models[0].name : null),
            isLoading: false,
          };
        });
        return true;
      }

      set((prev) => ({
        ...prev,
        isLoading: false,
        error: result.error || 'Failed to pull model',
      }));
      return false;
    } catch (error) {
      set((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to pull model',
      }));
      return false;
    }
  },

  deleteModel: async (modelName) => {
    try {
      const result = await window.electronAPI.ollama.deleteModel(modelName);

      if (result.isLastModel) {
        set((prev) => ({
          ...prev,
          error:
            'No se puede eliminar el último modelo. Ollama requiere al menos un modelo instalado.',
        }));
        return false;
      }

      if (result.success) {
        const models = await window.electronAPI.ollama.listModels();
        set((prev) => {
          const deletedWasActive = prev.currentModel === modelName;
          const nextModel = deletedWasActive
            ? models.length > 0
              ? models[0].name
              : null
            : prev.currentModel;
          return {
            ...prev,
            models,
            currentModel: nextModel,
            error: null,
          };
        });
        return true;
      }

      if (result.error) {
        set((prev) => ({
          ...prev,
          error: result.error || 'Failed to delete model',
        }));
      }
      return false;
    } catch {
      return false;
    }
  },

  selectModel: (modelName) => {
    set((prev) => ({ ...prev, currentModel: modelName }));
  },

  reset: () => set({ ...defaultState, isLoading: false }),
}));

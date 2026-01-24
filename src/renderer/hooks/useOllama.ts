/**
 * useOllama Hook
 * ===============
 * Custom hook for Ollama LLM status and operations
 */

import { useState, useEffect, useCallback } from 'react';
import type { OllamaStatus, OllamaModel } from '../../shared/types';

interface OllamaState {
  isRunning: boolean;
  version: string | null;
  models: OllamaModel[];
  currentModel: string | null;
  isLoading: boolean;
  error: string | null;
}

export function useOllama() {
  const [state, setState] = useState<OllamaState>({
    isRunning: false,
    version: null,
    models: [],
    currentModel: null,
    isLoading: true,
    error: null,
  });

  const checkStatus = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const status = await window.electronAPI.ollama.checkStatus();
      const models = status.running 
        ? await window.electronAPI.ollama.listModels()
        : [];

      setState({
        isRunning: status.running,
        version: status.version || null,
        models,
        currentModel: models.length > 0 ? models[0].name : null,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isRunning: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to check Ollama status',
      }));
    }
  }, []);

  // Check status on mount and periodically
  useEffect(() => {
    checkStatus();

    // Poll every 30 seconds
    const interval = setInterval(checkStatus, 30000);

    return () => clearInterval(interval);
  }, [checkStatus]);

  const pullModel = useCallback(async (modelName: string): Promise<boolean> => {
    setState((prev) => ({ ...prev, isLoading: true }));
    
    try {
      const result = await window.electronAPI.ollama.pullModel(modelName);
      
      if (result.success) {
        // Refresh models list
        const models = await window.electronAPI.ollama.listModels();
        setState((prev) => ({
          ...prev,
          models,
          isLoading: false,
        }));
        return true;
      } else {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Failed to pull model',
        }));
        return false;
      }
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to pull model',
      }));
      return false;
    }
  }, []);

  const deleteModel = useCallback(async (modelName: string): Promise<boolean> => {
    try {
      const result = await window.electronAPI.ollama.deleteModel(modelName);
      
      if (result.success) {
        // Refresh models list
        const models = await window.electronAPI.ollama.listModels();
        setState((prev) => ({
          ...prev,
          models,
          currentModel: models.length > 0 ? models[0].name : null,
        }));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, []);

  const selectModel = useCallback((modelName: string) => {
    setState((prev) => ({ ...prev, currentModel: modelName }));
  }, []);

  return {
    // State
    isRunning: state.isRunning,
    version: state.version,
    models: state.models,
    currentModel: state.currentModel,
    isLoading: state.isLoading,
    error: state.error,
    model: state.currentModel, // Alias for compatibility

    // Actions
    checkStatus,
    pullModel,
    deleteModel,
    selectModel,
    refresh: checkStatus,
  };
}

/**
 * Simplified hook for just checking Ollama status
 * Used in components that only need to display status
 */
export function useOllamaStatus() {
  const { isRunning, currentModel, isLoading, error } = useOllama();

  return {
    isRunning,
    model: currentModel,
    isLoading,
    error,
  };
}

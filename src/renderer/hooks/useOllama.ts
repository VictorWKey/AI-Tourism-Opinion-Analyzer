/**
 * useOllama Hook
 * ===============
 * Custom hook for Ollama LLM status and operations.
 *
 * Thin wrapper around the shared useOllamaStore Zustand store.
 * Because every consumer reads from the same store, an action
 * triggered anywhere (e.g. Settings page) is reflected instantly
 * in every other component (e.g. Sidebar) — no polling delay.
 */

import { useEffect, useRef } from 'react';
import { useOllamaStore } from '../stores/ollamaStore';
import { useSettingsStore } from '../stores/settingsStore';

export function useOllama() {
  const store = useOllamaStore();
  const { llm } = useSettingsStore();
  const llmMode = llm.mode;

  // Keep a ref so the interval callback always sees the latest llmMode
  const llmModeRef = useRef(llmMode);
  llmModeRef.current = llmMode;

  // On mount + whenever llmMode changes: fetch once and start a 30s poll
  useEffect(() => {
    store.checkStatus(llmMode);

    const interval = setInterval(() => {
      store.checkStatus(llmModeRef.current);
    }, 30000);

    return () => clearInterval(interval);
    // We intentionally depend only on llmMode (not the whole store object)
    // to avoid re-creating the interval on every state change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [llmMode]);

  return {
    // State
    isRunning: store.isRunning,
    version: store.version,
    models: store.models,
    currentModel: store.currentModel,
    isLoading: store.isLoading,
    error: store.error,
    model: store.currentModel, // Alias for compatibility

    // Actions
    checkStatus: () => store.checkStatus(llmModeRef.current),
    pullModel: store.pullModel,
    deleteModel: store.deleteModel,
    selectModel: store.selectModel,
    refresh: () => store.checkStatus(llmModeRef.current),
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

// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from 'electron';
import type { PipelineProgress } from './shared/types';

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Pipeline operations
  pipeline: {
    runPhase: (phase: number, config?: object) =>
      ipcRenderer.invoke('pipeline:run-phase', phase, config),
    runAll: (config?: object) =>
      ipcRenderer.invoke('pipeline:run-all', config),
    stop: () => ipcRenderer.invoke('pipeline:stop'),
    getStatus: () => ipcRenderer.invoke('pipeline:get-status'),
    validateDataset: (path: string) =>
      ipcRenderer.invoke('pipeline:validate-dataset', path),
    getLLMInfo: () => ipcRenderer.invoke('pipeline:get-llm-info'),
    onProgress: (callback: (event: unknown, data: PipelineProgress) => void) => {
      ipcRenderer.on('pipeline:progress', callback);
    },
    offProgress: () => {
      ipcRenderer.removeAllListeners('pipeline:progress');
    },
  },

  // File operations
  files: {
    selectFile: (filters?: object) =>
      ipcRenderer.invoke('files:select', filters),
    selectDirectory: () => ipcRenderer.invoke('files:select-directory'),
    readFile: (path: string) => ipcRenderer.invoke('files:read', path),
    writeFile: (path: string, content: string) =>
      ipcRenderer.invoke('files:write', path, content),
    openPath: (path: string) => ipcRenderer.invoke('files:open-path', path),
    exists: (path: string) => ipcRenderer.invoke('files:exists', path),
    stat: (path: string) => ipcRenderer.invoke('files:stat', path),
  },

  // Settings
  settings: {
    get: <T>(key: string) => ipcRenderer.invoke('settings:get', key) as Promise<T>,
    set: <T>(key: string, value: T) =>
      ipcRenderer.invoke('settings:set', key, value),
    getAll: () => ipcRenderer.invoke('settings:get-all'),
  },

  // Ollama
  ollama: {
    checkStatus: () => ipcRenderer.invoke('ollama:check-status'),
    listModels: () => ipcRenderer.invoke('ollama:list-models'),
    pullModel: (name: string) => ipcRenderer.invoke('ollama:pull-model', name),
    deleteModel: (name: string) => ipcRenderer.invoke('ollama:delete-model', name),
    onPullProgress: (callback: (event: unknown, data: unknown) => void) => {
      ipcRenderer.on('ollama:pull-progress', callback);
    },
    offPullProgress: () => {
      ipcRenderer.removeAllListeners('ollama:pull-progress');
    },
  },

  // Setup wizard
  setup: {
    isFirstRun: () => ipcRenderer.invoke('setup:is-first-run'),
    getState: () => ipcRenderer.invoke('setup:get-state'),
    systemCheck: () => ipcRenderer.invoke('setup:system-check'),
    setLLMProvider: (provider: 'ollama' | 'openai') =>
      ipcRenderer.invoke('setup:set-llm-provider', provider),
    checkOllama: () => ipcRenderer.invoke('setup:check-ollama'),
    installOllama: () => ipcRenderer.invoke('setup:install-ollama'),
    startOllama: () => ipcRenderer.invoke('setup:start-ollama'),
    pullOllamaModel: (model: string) =>
      ipcRenderer.invoke('setup:pull-ollama-model', model),
    hasOllamaModel: (model: string) =>
      ipcRenderer.invoke('setup:has-ollama-model', model),
    listOllamaModels: () => ipcRenderer.invoke('setup:list-ollama-models'),
    validateOpenAIKey: (key: string) =>
      ipcRenderer.invoke('setup:validate-openai-key', key),
    checkModels: () => ipcRenderer.invoke('setup:check-models'),
    downloadModels: () => ipcRenderer.invoke('setup:download-models'),
    getDownloadSize: () => ipcRenderer.invoke('setup:get-download-size'),
    getRequiredModels: () => ipcRenderer.invoke('setup:get-required-models'),
    complete: () => ipcRenderer.invoke('setup:complete'),
    reset: () => ipcRenderer.invoke('setup:reset'),
    onOllamaProgress: (callback: (event: unknown, data: unknown) => void) => {
      ipcRenderer.on('setup:ollama-progress', callback);
    },
    offOllamaProgress: () => {
      ipcRenderer.removeAllListeners('setup:ollama-progress');
    },
    onModelProgress: (callback: (event: unknown, data: unknown) => void) => {
      ipcRenderer.on('setup:model-progress', callback);
    },
    offModelProgress: () => {
      ipcRenderer.removeAllListeners('setup:model-progress');
    },
  },

  // App info
  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    getPlatform: () => process.platform,
  },
});
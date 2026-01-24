// ============================================
// AI Tourism Opinion Analyzer - Shared Types
// ============================================

// Pipeline types
export interface PhaseConfig {
  enabled: boolean;
  options?: Record<string, unknown>;
}

export interface PipelineConfig {
  phases: {
    phase01: PhaseConfig;
    phase02: PhaseConfig;
    phase03: PhaseConfig;
    phase04: PhaseConfig;
    phase05: PhaseConfig;
    phase06: PhaseConfig;
    phase07: PhaseConfig;
  };
  dataset?: string;
  outputDir?: string;
}

export interface PipelineProgress {
  phase: number;
  phaseName: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  error?: string;
}

export interface PipelineResult {
  success: boolean;
  completedPhases: number[];
  outputs: {
    dataPath?: string;
    chartsPath?: string;
    summaryPath?: string;
  };
  duration: number;
  error?: string;
}

// Dataset validation types
export interface DatasetValidation {
  valid: boolean;
  rowCount: number;
  columns: string[];
  missingColumns: string[];
  preview?: Record<string, unknown>[];
  alreadyProcessed?: boolean;
  error?: string;
}

// LLM types
export type LLMMode = 'local' | 'api';

export interface LLMConfig {
  mode: LLMMode;
  localModel: string;
  apiProvider: 'openai' | 'anthropic';
  apiKey?: string;
  apiModel: string;
  temperature: number;
}

export interface OllamaModel {
  name: string;
  size: number;
  modified: string;
}

export interface OllamaStatus {
  running: boolean;
  version?: string;
  models?: OllamaModel[];
}

// Data types
export interface DatasetInfo {
  path: string;
  name: string;
  rows: number;
  columns: string[];
  sampleData?: Record<string, unknown>[];
  validationStatus: 'valid' | 'invalid' | 'pending';
  validationMessages: string[];
}

// App types
export interface AppSettings {
  llm: LLMConfig;
  app: {
    theme: 'light' | 'dark' | 'system';
    language: string;
    outputDir: string;
  };
}

// Setup types
export interface SetupState {
  isComplete: boolean;
  completedAt: string | null;
  llmProvider: 'ollama' | 'openai' | null;
  ollamaInstalled: boolean;
  ollamaModelReady: boolean;
  modelsDownloaded: {
    sentiment: boolean;
    embeddings: boolean;
    subjectivity: boolean;
    categories: boolean;
  };
  openaiKeyConfigured: boolean;
}

export interface SystemCheckResult {
  pythonRuntime: boolean;
  pythonVersion?: string;
  diskSpace: {
    available: number;
    required: number;
    sufficient: boolean;
  };
  memory: {
    total: number;
    available: number;
    sufficient: boolean;
  };
  gpu: {
    available: boolean;
    name?: string;
  };
}

export interface OllamaDownloadProgress {
  stage: 'idle' | 'downloading' | 'installing' | 'starting' | 'pulling-model' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
}

export interface ModelDownloadProgress {
  model: string;
  progress: number;
  status: 'pending' | 'downloading' | 'complete' | 'error';
  message?: string;
  error?: string;
}

export interface ModelInfo {
  name: string;
  displayName: string;
  size: string;
  type: 'huggingface' | 'bundled';
  required: boolean;
}

export interface ModelsStatus {
  sentiment: boolean;
  embeddings: boolean;
  subjectivity: boolean;
  categories: boolean;
}

// Electron API types for renderer process
export interface ElectronAPI {
  pipeline: {
    runPhase: (phase: number, config?: object) => Promise<PipelineResult>;
    runAll: (config?: object) => Promise<PipelineResult>;
    stop: () => Promise<{ success: boolean }>;
    getStatus: () => Promise<PipelineProgress>;
    validateDataset: (path: string) => Promise<DatasetValidation>;
    getLLMInfo: () => Promise<{ success: boolean; [key: string]: unknown }>;
    onProgress: (callback: (event: unknown, data: PipelineProgress) => void) => void;
    offProgress: () => void;
  };
  files: {
    selectFile: (filters?: object) => Promise<string | null>;
    selectDirectory: () => Promise<string | null>;
    readFile: (path: string) => Promise<{ success: boolean; content?: string; error?: string }>;
    writeFile: (path: string, content: string) => Promise<{ success: boolean; error?: string }>;
    openPath: (path: string) => Promise<{ success: boolean; error?: string }>;
    exists: (path: string) => Promise<boolean>;
    stat: (path: string) => Promise<{
      success: boolean;
      stats?: {
        size: number;
        isFile: boolean;
        isDirectory: boolean;
        created: string;
        modified: string;
      };
      error?: string;
    }>;
  };
  settings: {
    get: <T>(key: string) => Promise<T>;
    set: <T>(key: string, value: T) => Promise<{ success: boolean }>;
    getAll: () => Promise<AppSettings>;
  };
  ollama: {
    checkStatus: () => Promise<OllamaStatus>;
    listModels: () => Promise<OllamaModel[]>;
    pullModel: (name: string) => Promise<{ success: boolean; error?: string }>;
    deleteModel: (name: string) => Promise<{ success: boolean; error?: string }>;
    onPullProgress: (callback: (event: unknown, data: unknown) => void) => void;
    offPullProgress: () => void;
  };
  setup: {
    isFirstRun: () => Promise<boolean>;
    getState: () => Promise<SetupState>;
    systemCheck: () => Promise<SystemCheckResult>;
    setLLMProvider: (provider: 'ollama' | 'openai') => Promise<{ success: boolean }>;
    checkOllama: () => Promise<{ installed: boolean; running: boolean; version: string | null }>;
    installOllama: () => Promise<boolean>;
    startOllama: () => Promise<{ success: boolean; error?: string }>;
    pullOllamaModel: (model: string) => Promise<{ success: boolean }>;
    hasOllamaModel: (model: string) => Promise<boolean>;
    listOllamaModels: () => Promise<Array<{ name: string; size: number; modified: string }>>;
    validateOpenAIKey: (key: string) => Promise<{ valid: boolean; error?: string | null }>;
    checkModels: () => Promise<ModelsStatus>;
    downloadModels: () => Promise<boolean>;
    getDownloadSize: () => Promise<{ size_mb: number; formatted: string }>;
    getRequiredModels: () => Promise<ModelInfo[]>;
    complete: () => Promise<{ success: boolean }>;
    reset: () => Promise<{ success: boolean }>;
    onOllamaProgress: (callback: (event: unknown, data: OllamaDownloadProgress) => void) => void;
    offOllamaProgress: () => void;
    onModelProgress: (callback: (event: unknown, data: ModelDownloadProgress) => void) => void;
    offModelProgress: () => void;
  };
  app: {
    getVersion: () => Promise<string>;
    getPlatform: () => string;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

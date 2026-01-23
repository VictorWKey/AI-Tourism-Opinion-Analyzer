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

// Electron API types for renderer process
export interface ElectronAPI {
  pipeline: {
    runPhase: (phase: number, config?: object) => Promise<PipelineResult>;
    runAll: (config?: object) => Promise<PipelineResult>;
    stop: () => Promise<void>;
    getStatus: () => Promise<PipelineProgress>;
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

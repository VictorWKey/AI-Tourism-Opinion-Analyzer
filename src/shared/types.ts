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
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelling';
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
  validation?: PhaseValidation; // Optional validation details for dependency errors
}

// Phase validation types
export interface PhaseValidation {
  success: boolean;
  valid: boolean;
  canRun: boolean;
  missingColumns: string[];
  missingFiles: string[];
  missingPhases: number[];
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
  /** True when columns don't match but user could map them */
  needsMapping?: boolean;
  error?: string;
}

// Column mapping types
export interface RequiredColumn {
  name: string;
  description: string;
  required: boolean;
  /** Columns that should be treated as equivalent (e.g. TituloReview = Titulo+Review) */
  alternatives?: string[];
}

export interface ColumnMapping {
  /** Key: system column name, Value: user's source column name or null */
  [systemColumn: string]: string | null;
}

export interface ColumnMappingResult {
  success: boolean;
  outputPath?: string;
  rowCount?: number;
  columns?: string[];
  preview?: Record<string, unknown>[];
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
  pythonReady: boolean;
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

// Hardware detection status
export type DetectionStatus = 'auto-detected' | 'fallback' | 'manual' | 'failed';

// Detailed hardware info with detection metadata
export interface HardwareDetectionResult {
  cpu: {
    name: string;
    cores: number;
    threads: number;
    tier: 'low' | 'mid' | 'high';
    detectionStatus: DetectionStatus;
    detectionSource: string; // e.g., "WMI", "os.cpus()", "manual"
  };
  ram: {
    totalGB: number;
    availableGB: number;
    detectionStatus: DetectionStatus;
    detectionSource: string;
  };
  gpu: {
    available: boolean;
    type: 'none' | 'integrated' | 'dedicated';
    name?: string;
    vramGB?: number;
    cudaAvailable: boolean;
    detectionStatus: DetectionStatus;
    detectionSource: string;
  };
  // Overall recommendation based on detected hardware
  recommendation: {
    canRunLocalLLM: boolean;
    recommendedProvider: 'ollama' | 'openai';
    recommendedModel?: string;
    reasoning: string;
    warnings: string[];
  };
}

export interface SystemCheckResult {
  pythonRuntime: boolean;
  pythonVersion?: string;
  pythonVenvReady: boolean;
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
    vram?: number;
    type?: 'none' | 'integrated' | 'dedicated';
  };
  // Enhanced hardware detection
  hardware?: HardwareDetectionResult;
}

// Python setup types
export interface PythonSetupProgress {
  stage: 'checking' | 'downloading-python' | 'installing-python' | 'creating-venv' | 'installing-deps' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
}

export interface PythonSetupStatus {
  pythonInstalled: boolean;
  pythonVersion?: string;
  pythonPath?: string;
  venvExists: boolean;
  venvPath?: string;
  dependenciesInstalled: boolean;
  /** True only if setup completed fully without interruption */
  setupComplete: boolean;
  /** True if installation was started but not completed (interrupted) */
  installationInterrupted: boolean;
}

export interface OllamaDownloadProgress {
  stage: 'idle' | 'downloading' | 'installing' | 'starting' | 'pulling-model' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
  // Unified installation tracking - installation is NOT complete until a model is ready
  unifiedProgress?: number; // Overall progress 0-100 across all phases
  currentPhase?: 'software' | 'model'; // Which phase we're in
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
    validatePhase: (phase: number, datasetPath?: string) => Promise<PhaseValidation>;
    applyColumnMapping: (sourcePath: string, mapping: ColumnMapping) => Promise<ColumnMappingResult>;
    getRequiredColumns: () => Promise<{ success: boolean; columns: RequiredColumn[] }>;
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
    listImages: (dirPath: string) => Promise<{
      success: boolean;
      images?: Array<{
        id: string;
        name: string;
        path: string;
        category: string;
        categoryLabel: string;
      }>;
      error?: string;
    }>;
    listDir: (dirPath: string) => Promise<{
      success: boolean;
      items?: Array<{
        name: string;
        isDirectory: boolean;
        isFile: boolean;
        path: string;
      }>;
      error?: string;
    }>;
    readImageBase64: (filePath: string) => Promise<{ success: boolean; dataUrl?: string; error?: string }>;
    cleanDatasetData: (dataDir: string) => Promise<{ success: boolean; deletedPaths: string[]; error?: string }>;
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
    deleteModel: (name: string) => Promise<{ success: boolean; error?: string; isLastModel?: boolean }>;
    getModelCount: () => Promise<number>;
    onPullProgress: (callback: (event: unknown, data: unknown) => void) => void;
    offPullProgress: () => void;
  };
  setup: {
    isFirstRun: () => Promise<boolean>;
    getState: () => Promise<SetupState>;
    systemCheck: () => Promise<SystemCheckResult>;
    setLLMProvider: (provider: 'ollama' | 'openai') => Promise<{ success: boolean }>;
    // Python setup
    checkPython: () => Promise<PythonSetupStatus>;
    setupPython: () => Promise<boolean>;
    getPythonPaths: () => Promise<{ pythonDir: string; venvDir: string; pythonPath: string }>;
    onPythonProgress: (callback: (event: unknown, data: PythonSetupProgress) => void) => void;
    offPythonProgress: () => void;
    // Ollama setup
    checkOllama: () => Promise<{ installed: boolean; running: boolean; version: string | null }>;
    installOllama: () => Promise<boolean>;
    // Unified installation: software + model in one step (recommended)
    installOllamaWithModel: (model: string) => Promise<{ success: boolean }>;
    // Check if Ollama is fully ready (installed + running + has models)
    checkOllamaFullyReady: () => Promise<{ 
      ready: boolean; 
      installed: boolean; 
      running: boolean; 
      hasModels: boolean; 
      modelCount: number 
    }>;
    startOllama: () => Promise<{ success: boolean; error?: string }>;
    stopOllama: () => Promise<{ success: boolean; error?: string }>;
    uninstallOllama: () => Promise<{ success: boolean; error?: string }>;
    pullOllamaModel: (model: string) => Promise<{ success: boolean }>;
    hasOllamaModel: (model: string) => Promise<boolean>;
    listOllamaModels: () => Promise<Array<{ name: string; size: number; modified: string }>>;
    // Prevent deleting the last model
    canDeleteOllamaModel: (model: string) => Promise<{ canDelete: boolean; reason?: string }>;
    getOllamaModelCount: () => Promise<number>;
    validateOpenAIKey: (key: string) => Promise<{ valid: boolean; error?: string | null }>;
    checkModels: () => Promise<ModelsStatus>;
    downloadModels: () => Promise<{ success: boolean; error?: string; details?: Record<string, boolean> }>;
    downloadSpecificModel: (modelKey: string) => Promise<boolean>;
    preloadModels: () => Promise<{ success: boolean; details?: Record<string, boolean>; error?: string }>;
    getDownloadSize: () => Promise<{ size_mb: number; formatted: string }>;
    getRequiredModels: () => Promise<ModelInfo[]>;
    complete: () => Promise<{ success: boolean }>;
    reset: () => Promise<{ success: boolean }>;
    cleanPython: () => Promise<{ success: boolean; error?: string }>;
    // Enhanced hardware detection
    detectHardware: () => Promise<HardwareDetectionResult>;
    saveHardwareOverrides: (overrides: {
      cpuTier?: 'low' | 'mid' | 'high';
      ramGB?: number;
      gpuType?: 'none' | 'integrated' | 'dedicated';
      vramGB?: number;
    }) => Promise<{ success: boolean }>;
    clearHardwareOverrides: () => Promise<{ success: boolean }>;
    // Progress listeners
    onOllamaProgress: (callback: (event: unknown, data: OllamaDownloadProgress) => void) => void;
    offOllamaProgress: () => void;
    onOllamaUninstallProgress: (callback: (event: unknown, data: { message: string }) => void) => void;
    offOllamaUninstallProgress: () => void;
    onModelProgress: (callback: (event: unknown, data: ModelDownloadProgress) => void) => void;
    offModelProgress: () => void;
  };
  app: {
    getVersion: () => Promise<string>;
    getPlatform: () => string;
    getPythonDataDir: () => Promise<string>;
  };
  store: {
    getItem: (key: string) => Promise<string | null>;
    setItem: (key: string, value: string) => Promise<void>;
    removeItem: (key: string) => Promise<void>;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

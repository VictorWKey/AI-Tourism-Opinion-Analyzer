# 📋 AI Tourism Opinion Analyzer - Desktop Application Implementation Plan

## 📌 Overview

This document provides a detailed, phase-by-phase implementation plan for building the desktop application. The plan is designed to be executed incrementally, with each phase building upon the previous one.

**Estimated Total Duration:** 8-12 weeks (1 developer) or 4-6 weeks (2-3 developers)

---

## 🗓️ Implementation Phases

```
Phase 0: Project Setup (Week 1)
    │
    ▼
Phase 1: Core Infrastructure (Week 1-2)
    │
    ▼
Phase 2: Python Bridge (Week 2-3)
    │
    ▼
Phase 3: UI Foundation (Week 3-4)
    │
    ▼
Phase 4: Pipeline Integration (Week 4-6)
    │
    ▼
Phase 5: Visualizations (Week 6-7)
    │
    ▼
Phase 6: Settings & Configuration (Week 7-8)
    │
    ▼
Phase 7: Polish & Testing (Week 8-10)
    │
    ▼
Phase 8: Packaging & Distribution (Week 10-12)
```

---

## 📋 Phase 0: Project Setup & Prerequisites

**Duration:** 3-5 days

### 0.1 Development Environment Setup

#### Required Tools
```bash
# Node.js (LTS version)
node --version  # Should be >= 18.x

# Package manager (choose one)
npm --version   # >= 9.x
pnpm --version  # >= 8.x (recommended)

# Python
python --version  # >= 3.10

# Git
git --version
```

#### Recommended VS Code Extensions
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript Importer
- Python
- Thunder Client (API testing)

### 0.2 Initialize Project

```bash
# Create project directory
mkdir ai-tourism-analyzer-desktop
cd ai-tourism-analyzer-desktop

# Initialize with Electron Forge + Vite + React template
npm init electron-app@latest . -- --template=vite-typescript

# Or with pnpm
pnpm create electron-app . --template=vite-typescript
```

### 0.3 Install Core Dependencies

```bash
# Frontend dependencies
pnpm add react react-dom react-router-dom
pnpm add zustand                          # State management
pnpm add @tanstack/react-query            # Async state
pnpm add recharts                         # Charts
pnpm add react-dropzone                   # File upload
pnpm add lucide-react                     # Icons
pnpm add clsx tailwind-merge              # Class utilities
pnpm add react-markdown                   # Render summaries
pnpm add framer-motion                    # Animations

# UI Component library (shadcn/ui setup)
pnpm add tailwindcss postcss autoprefixer
pnpm add class-variance-authority
pnpm add @radix-ui/react-dialog @radix-ui/react-dropdown-menu
pnpm add @radix-ui/react-tabs @radix-ui/react-progress
pnpm add @radix-ui/react-switch @radix-ui/react-select
pnpm add @radix-ui/react-toast @radix-ui/react-tooltip

# Dev dependencies
pnpm add -D @types/react @types/react-dom
pnpm add -D tailwindcss postcss autoprefixer
pnpm add -D eslint @typescript-eslint/eslint-plugin
pnpm add -D prettier eslint-config-prettier

# Electron-specific
pnpm add electron-store                   # Persistent storage
pnpm add python-shell                     # Python subprocess
```

### 0.4 Project Configuration Files

#### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,html}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
};
```

#### tsconfig.json (additions)
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@main/*": ["src/main/*"],
      "@renderer/*": ["src/renderer/*"],
      "@shared/*": ["src/shared/*"]
    }
  }
}
```

### 0.5 Directory Structure Setup

```bash
# Create directory structure
mkdir -p src/main/ipc
mkdir -p src/main/python
mkdir -p src/main/utils
mkdir -p src/renderer/components/{ui,layout,pipeline,visualizations,data,settings}
mkdir -p src/renderer/pages
mkdir -p src/renderer/stores
mkdir -p src/renderer/hooks
mkdir -p src/renderer/lib
mkdir -p src/renderer/styles
mkdir -p src/shared
mkdir -p python
mkdir -p resources/icons
```

### 0.6 Copy Python Pipeline

```bash
# Copy existing pipeline code
cp -r /path/to/AI-Tourism-Opinion-Analyzer-Pipeline/* ./python/

# Verify structure
ls python/
# Should show: main.py, config/, core/, data/, models/, etc.
```

### Deliverables for Phase 0
- [ ] Project initialized with Electron Forge
- [ ] All dependencies installed
- [ ] Directory structure created
- [ ] Configuration files in place
- [ ] Python pipeline copied
- [ ] Development server runs without errors

---

## 📋 Phase 1: Core Infrastructure

**Duration:** 5-7 days

### 1.1 Electron Main Process Setup

#### src/main/index.ts
```typescript
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { registerIpcHandlers } from './ipc';
import { initializeStore } from './utils/store';

// Handle creating/removing shortcuts on Windows
if (require('electron-squirrel-startup')) {
  app.quit();
}

let mainWindow: BrowserWindow | null = null;

const createWindow = (): void => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: 'hiddenInset', // macOS style
    show: false, // Show when ready
  });

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Load the app
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(
      path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`)
    );
  }

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
};

app.on('ready', async () => {
  await initializeStore();
  registerIpcHandlers();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
```

#### src/main/preload.ts
```typescript
import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Pipeline operations
  pipeline: {
    runPhase: (phase: number, config?: object) =>
      ipcRenderer.invoke('pipeline:run-phase', phase, config),
    runAll: (config?: object) =>
      ipcRenderer.invoke('pipeline:run-all', config),
    stop: () => ipcRenderer.invoke('pipeline:stop'),
    getStatus: () => ipcRenderer.invoke('pipeline:get-status'),
    onProgress: (callback: (event: any, data: any) => void) =>
      ipcRenderer.on('pipeline:progress', callback),
    offProgress: () => ipcRenderer.removeAllListeners('pipeline:progress'),
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
  },

  // Settings
  settings: {
    get: (key: string) => ipcRenderer.invoke('settings:get', key),
    set: (key: string, value: any) =>
      ipcRenderer.invoke('settings:set', key, value),
    getAll: () => ipcRenderer.invoke('settings:get-all'),
  },

  // Ollama
  ollama: {
    checkStatus: () => ipcRenderer.invoke('ollama:check-status'),
    listModels: () => ipcRenderer.invoke('ollama:list-models'),
    pullModel: (name: string) => ipcRenderer.invoke('ollama:pull-model', name),
    onPullProgress: (callback: (event: any, data: any) => void) =>
      ipcRenderer.on('ollama:pull-progress', callback),
  },

  // App info
  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    getPlatform: () => process.platform,
  },
});
```

### 1.2 IPC Handlers Setup

#### src/main/ipc/index.ts
```typescript
import { ipcMain } from 'electron';
import { registerPipelineHandlers } from './pipeline';
import { registerFileHandlers } from './files';
import { registerSettingsHandlers } from './settings';
import { registerOllamaHandlers } from './ollama';

export function registerIpcHandlers(): void {
  registerPipelineHandlers();
  registerFileHandlers();
  registerSettingsHandlers();
  registerOllamaHandlers();
}
```

#### src/main/ipc/files.ts
```typescript
import { ipcMain, dialog, shell } from 'electron';
import fs from 'fs/promises';
import path from 'path';

export function registerFileHandlers(): void {
  ipcMain.handle('files:select', async (_, filters) => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: filters || [
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'All Files', extensions: ['*'] },
      ],
    });

    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }

    return result.filePaths[0];
  });

  ipcMain.handle('files:select-directory', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'createDirectory'],
    });

    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }

    return result.filePaths[0];
  });

  ipcMain.handle('files:read', async (_, filePath: string) => {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return { success: true, content };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  ipcMain.handle('files:write', async (_, filePath: string, content: string) => {
    try {
      await fs.writeFile(filePath, content, 'utf-8');
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  ipcMain.handle('files:open-path', async (_, filePath: string) => {
    try {
      await shell.openPath(filePath);
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });
}
```

#### src/main/ipc/settings.ts
```typescript
import { ipcMain } from 'electron';
import Store from 'electron-store';

const store = new Store({
  defaults: {
    llm: {
      mode: 'local',
      ollamaModel: 'llama3.2:3b',
      ollamaBaseUrl: 'http://localhost:11434',
      openaiModel: 'gpt-4o-mini',
      openaiApiKey: '',
      temperature: 0,
    },
    pipeline: {
      phases: {
        phase_01: true,
        phase_02: true,
        phase_03: true,
        phase_04: true,
        phase_05: true,
        phase_06: true,
        phase_07: true,
      },
    },
    app: {
      theme: 'system',
      dataDirectory: '',
    },
  },
  encryptionKey: 'your-encryption-key-here', // For API keys
});

export function registerSettingsHandlers(): void {
  ipcMain.handle('settings:get', (_, key: string) => {
    return store.get(key);
  });

  ipcMain.handle('settings:set', (_, key: string, value: any) => {
    store.set(key, value);
    return { success: true };
  });

  ipcMain.handle('settings:get-all', () => {
    return store.store;
  });
}

export { store };
```

### 1.3 TypeScript Types

#### src/shared/types.ts
```typescript
// Pipeline types
export interface PhaseConfig {
  enabled: boolean;
  options?: Record<string, any>;
}

export interface PipelineConfig {
  phases: {
    phase_01: boolean;
    phase_02: boolean;
    phase_03: boolean;
    phase_04: boolean;
    phase_05: boolean;
    phase_06: boolean;
    phase_07: boolean;
  };
}

export interface PipelineProgress {
  phase: number;
  phaseName: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'skipped';
  progress: number; // 0-100
  message?: string;
  error?: string;
}

export interface PipelineResult {
  success: boolean;
  phasesCompleted: number[];
  phasesFailed: number[];
  duration: number; // ms
  outputs: {
    dataset?: string;
    visualizations?: string[];
    summaries?: string;
  };
}

// LLM types
export interface LLMConfig {
  mode: 'local' | 'api';
  ollamaModel: string;
  ollamaBaseUrl: string;
  openaiModel: string;
  openaiApiKey: string;
  temperature: number;
}

export interface OllamaModel {
  name: string;
  size: string;
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
  rowCount: number;
  columns: string[];
  preview: Record<string, any>[];
  validationStatus: 'valid' | 'warning' | 'error';
  validationMessages: string[];
}

// App types
export interface AppSettings {
  llm: LLMConfig;
  pipeline: PipelineConfig;
  app: {
    theme: 'light' | 'dark' | 'system';
    dataDirectory: string;
  };
}
```

### Deliverables for Phase 1
- [ ] Main process with window management
- [ ] Preload script with secure API exposure
- [ ] IPC handlers for files and settings
- [ ] Electron-store configuration
- [ ] TypeScript types defined
- [ ] Basic app launches and shows window

---

## 📋 Phase 2: Python Bridge

**Duration:** 5-7 days

### 2.1 Python API Bridge

#### python/api_bridge.py
```python
"""
JSON API Bridge for Electron Communication
==========================================
Provides a JSON-based interface for the pipeline.
Communicates via stdin/stdout with JSON messages.
"""

import sys
import json
import traceback
from typing import Dict, Any, Callable
from pathlib import Path
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    ProcesadorBasico,
    AnalizadorSentimientos,
    AnalizadorSubjetividad,
    ClasificadorCategorias,
    AnalizadorJerarquicoTopicos,
    ResumidorInteligente,
    GeneradorVisualizaciones,
    LLMProvider
)


class ProgressReporter:
    """Reports progress back to Electron via stdout."""
    
    def __init__(self, phase: int, phase_name: str):
        self.phase = phase
        self.phase_name = phase_name
    
    def report(self, progress: int, message: str = ""):
        """Send progress update to Electron."""
        response = {
            "type": "progress",
            "phase": self.phase,
            "phaseName": self.phase_name,
            "progress": progress,
            "message": message
        }
        print(json.dumps(response), flush=True)


class PipelineAPI:
    """JSON API for the analysis pipeline."""
    
    PHASES = {
        1: ("Procesamiento Básico", ProcesadorBasico),
        2: ("Análisis de Sentimientos", AnalizadorSentimientos),
        3: ("Análisis de Subjetividad", AnalizadorSubjetividad),
        4: ("Clasificación de Categorías", ClasificadorCategorias),
        5: ("Análisis Jerárquico de Tópicos", AnalizadorJerarquicoTopicos),
        6: ("Resumen Inteligente", ResumidorInteligente),
        7: ("Generación de Visualizaciones", GeneradorVisualizaciones),
    }
    
    def __init__(self):
        self.current_phase = None
        self.should_stop = False
    
    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pipeline command and return JSON response."""
        try:
            action = command.get("action")
            
            handlers = {
                "run_phase": self._run_phase,
                "run_all": self._run_all,
                "stop": self._stop,
                "get_status": self._get_status,
                "validate_dataset": self._validate_dataset,
                "get_llm_info": self._get_llm_info,
                "check_ollama": self._check_ollama,
            }
            
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            return handler(command)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _run_phase(self, command: Dict) -> Dict:
        """Run a specific pipeline phase."""
        phase = command.get("phase")
        config = command.get("config", {})
        force = config.get("force", True)
        
        if phase not in self.PHASES:
            return {"success": False, "error": f"Invalid phase: {phase}"}
        
        phase_name, phase_class = self.PHASES[phase]
        reporter = ProgressReporter(phase, phase_name)
        
        self.current_phase = phase
        reporter.report(0, "Iniciando fase...")
        
        try:
            # Instantiate and run phase
            processor = phase_class()
            
            # Special handling for phases with custom parameters
            if phase == 6:
                processor = ResumidorInteligente(
                    top_n_subtopicos=config.get("top_n_subtopicos", 3),
                    incluir_neutros=config.get("incluir_neutros", False)
                )
                processor.procesar(
                    tipos_resumen=config.get("tipos_resumen", 
                        ["descriptivo", "estructurado", "insights"]),
                    forzar=force
                )
            else:
                processor.procesar(forzar=force)
            
            reporter.report(100, "Fase completada")
            
            return {
                "success": True,
                "phase": phase,
                "phaseName": phase_name,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "phase": phase,
                "phaseName": phase_name,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        finally:
            self.current_phase = None
    
    def _run_all(self, command: Dict) -> Dict:
        """Run all pipeline phases sequentially."""
        config = command.get("config", {})
        phases_config = config.get("phases", {})
        results = []
        
        for phase in range(1, 8):
            if self.should_stop:
                break
            
            phase_key = f"phase_{phase:02d}"
            if not phases_config.get(phase_key, True):
                results.append({
                    "phase": phase,
                    "status": "skipped"
                })
                continue
            
            result = self._run_phase({"phase": phase, "config": config})
            results.append(result)
            
            if not result["success"]:
                break
        
        self.should_stop = False
        
        return {
            "success": all(r.get("success", False) or r.get("status") == "skipped" 
                          for r in results),
            "results": results
        }
    
    def _stop(self, command: Dict) -> Dict:
        """Stop the current execution."""
        self.should_stop = True
        return {"success": True, "message": "Stop signal sent"}
    
    def _get_status(self, command: Dict) -> Dict:
        """Get current pipeline status."""
        return {
            "success": True,
            "currentPhase": self.current_phase,
            "isRunning": self.current_phase is not None
        }
    
    def _validate_dataset(self, command: Dict) -> Dict:
        """Validate a dataset file."""
        path = command.get("path")
        
        if not path or not Path(path).exists():
            return {"success": False, "error": "File not found"}
        
        try:
            df = pd.read_csv(path)
            
            # Check required columns
            required = ["Titulo", "Review", "FechaEstadia", "Calificacion"]
            has_titulo_review = "TituloReview" in df.columns
            
            if has_titulo_review:
                required = ["TituloReview", "FechaEstadia", "Calificacion"]
            
            missing = [col for col in required if col not in df.columns]
            
            return {
                "success": True,
                "valid": len(missing) == 0,
                "rowCount": len(df),
                "columns": list(df.columns),
                "missingColumns": missing,
                "preview": df.head(5).to_dict(orient="records"),
                "alreadyProcessed": has_titulo_review
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_llm_info(self, command: Dict) -> Dict:
        """Get LLM configuration info."""
        try:
            info = LLMProvider.get_info()
            return {"success": True, **info}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_ollama(self, command: Dict) -> Dict:
        """Check Ollama availability."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.ok:
                data = response.json()
                return {
                    "success": True,
                    "running": True,
                    "models": [m["name"] for m in data.get("models", [])]
                }
            return {"success": True, "running": False}
        except:
            return {"success": True, "running": False}


def main():
    """Main entry point for subprocess communication."""
    api = PipelineAPI()
    
    # Read commands from stdin, write responses to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            command = json.loads(line)
            result = api.execute(command)
            print(json.dumps(result), flush=True)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "success": False,
                "error": f"Invalid JSON: {e}"
            }), flush=True)


if __name__ == "__main__":
    main()
```

### 2.2 Electron Python Bridge

#### src/main/python/bridge.ts
```typescript
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { app, BrowserWindow } from 'electron';
import { EventEmitter } from 'events';

interface PythonCommand {
  action: string;
  [key: string]: any;
}

interface PythonResponse {
  success: boolean;
  type?: string;
  [key: string]: any;
}

export class PythonBridge extends EventEmitter {
  private process: ChildProcess | null = null;
  private pythonPath: string;
  private scriptPath: string;
  private responseBuffer: string = '';
  private pendingCallbacks: Map<number, (response: PythonResponse) => void> = new Map();
  private callId: number = 0;

  constructor() {
    super();
    
    // Determine Python path based on environment
    if (app.isPackaged) {
      // In production, use bundled Python
      this.pythonPath = path.join(process.resourcesPath, 'python', 'python');
      this.scriptPath = path.join(process.resourcesPath, 'python', 'api_bridge.py');
    } else {
      // In development, use system Python
      this.pythonPath = 'python3';
      this.scriptPath = path.join(app.getAppPath(), 'python', 'api_bridge.py');
    }
  }

  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.process = spawn(this.pythonPath, [this.scriptPath], {
          cwd: path.dirname(this.scriptPath),
          stdio: ['pipe', 'pipe', 'pipe'],
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',
          },
        });

        this.process.stdout?.on('data', (data: Buffer) => {
          this.handleOutput(data.toString());
        });

        this.process.stderr?.on('data', (data: Buffer) => {
          console.error('[Python Error]:', data.toString());
          this.emit('error', data.toString());
        });

        this.process.on('close', (code) => {
          console.log(`Python process exited with code ${code}`);
          this.process = null;
          this.emit('close', code);
        });

        this.process.on('error', (error) => {
          console.error('Failed to start Python process:', error);
          reject(error);
        });

        // Wait a moment for Python to start
        setTimeout(() => resolve(), 500);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleOutput(data: string): void {
    this.responseBuffer += data;
    
    // Process complete JSON lines
    const lines = this.responseBuffer.split('\n');
    this.responseBuffer = lines.pop() || '';
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line) as PythonResponse;
          
          // Handle progress updates
          if (response.type === 'progress') {
            this.emit('progress', response);
            // Forward to renderer
            const windows = BrowserWindow.getAllWindows();
            windows.forEach(win => {
              win.webContents.send('pipeline:progress', response);
            });
          } else {
            // Handle command responses
            const callback = this.pendingCallbacks.get(this.callId - 1);
            if (callback) {
              callback(response);
              this.pendingCallbacks.delete(this.callId - 1);
            }
          }
        } catch (e) {
          console.error('Failed to parse Python response:', line);
        }
      }
    }
  }

  async execute(command: PythonCommand): Promise<PythonResponse> {
    if (!this.process) {
      await this.start();
    }

    return new Promise((resolve, reject) => {
      const currentCallId = this.callId++;
      this.pendingCallbacks.set(currentCallId, resolve);
      
      const commandStr = JSON.stringify(command) + '\n';
      this.process?.stdin?.write(commandStr);
      
      // Timeout after 5 minutes (for long-running phases)
      setTimeout(() => {
        if (this.pendingCallbacks.has(currentCallId)) {
          this.pendingCallbacks.delete(currentCallId);
          reject(new Error('Python command timeout'));
        }
      }, 300000);
    });
  }

  stop(): void {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}

// Singleton instance
let bridgeInstance: PythonBridge | null = null;

export function getPythonBridge(): PythonBridge {
  if (!bridgeInstance) {
    bridgeInstance = new PythonBridge();
  }
  return bridgeInstance;
}
```

### 2.3 Pipeline IPC Handlers

#### src/main/ipc/pipeline.ts
```typescript
import { ipcMain, BrowserWindow } from 'electron';
import { getPythonBridge } from '../python/bridge';

export function registerPipelineHandlers(): void {
  const bridge = getPythonBridge();

  ipcMain.handle('pipeline:run-phase', async (_, phase: number, config?: object) => {
    return bridge.execute({
      action: 'run_phase',
      phase,
      config: config || {},
    });
  });

  ipcMain.handle('pipeline:run-all', async (_, config?: object) => {
    return bridge.execute({
      action: 'run_all',
      config: config || {},
    });
  });

  ipcMain.handle('pipeline:stop', async () => {
    return bridge.execute({ action: 'stop' });
  });

  ipcMain.handle('pipeline:get-status', async () => {
    return bridge.execute({ action: 'get_status' });
  });

  ipcMain.handle('pipeline:validate-dataset', async (_, path: string) => {
    return bridge.execute({
      action: 'validate_dataset',
      path,
    });
  });

  ipcMain.handle('pipeline:get-llm-info', async () => {
    return bridge.execute({ action: 'get_llm_info' });
  });
}
```

### 2.4 Ollama IPC Handlers

#### src/main/ipc/ollama.ts
```typescript
import { ipcMain, BrowserWindow } from 'electron';
import fetch from 'node-fetch';

const OLLAMA_BASE_URL = 'http://localhost:11434';

export function registerOllamaHandlers(): void {
  ipcMain.handle('ollama:check-status', async () => {
    try {
      const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`, {
        method: 'GET',
        timeout: 5000,
      } as any);
      
      if (response.ok) {
        const data = await response.json() as any;
        return {
          running: true,
          models: data.models?.map((m: any) => ({
            name: m.name,
            size: m.size,
            modified: m.modified_at,
          })) || [],
        };
      }
      return { running: false, models: [] };
    } catch {
      return { running: false, models: [] };
    }
  });

  ipcMain.handle('ollama:list-models', async () => {
    try {
      const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`);
      const data = await response.json() as any;
      return data.models?.map((m: any) => m.name) || [];
    } catch {
      return [];
    }
  });

  ipcMain.handle('ollama:pull-model', async (event, modelName: string) => {
    try {
      const response = await fetch(`${OLLAMA_BASE_URL}/api/pull`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: modelName }),
      });

      const reader = response.body;
      if (!reader) {
        return { success: false, error: 'No response body' };
      }

      // Stream progress updates
      const windows = BrowserWindow.getAllWindows();
      
      // Process streaming response
      let buffer = '';
      reader.on('data', (chunk: Buffer) => {
        buffer += chunk.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.trim()) {
            try {
              const progress = JSON.parse(line);
              windows.forEach(win => {
                win.webContents.send('ollama:pull-progress', progress);
              });
            } catch {}
          }
        }
      });

      return new Promise((resolve) => {
        reader.on('end', () => {
          resolve({ success: true });
        });
        reader.on('error', (error: Error) => {
          resolve({ success: false, error: error.message });
        });
      });
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });
}
```

### Deliverables for Phase 2
- [ ] Python API bridge script created
- [ ] PythonBridge TypeScript class implemented
- [ ] Pipeline IPC handlers registered
- [ ] Ollama IPC handlers registered
- [ ] Python subprocess communication works
- [ ] Progress updates flow to renderer

---

## 📋 Phase 3: UI Foundation

**Duration:** 5-7 days

### 3.1 Layout Components

#### src/renderer/components/layout/Sidebar.tsx
```tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, Database, PlayCircle, BarChart2, 
  FileText, Settings, Cpu 
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useOllamaStatus } from '@/hooks/useOllama';

const navItems = [
  { path: '/', icon: Home, label: 'Inicio' },
  { path: '/data', icon: Database, label: 'Datos' },
  { path: '/pipeline', icon: PlayCircle, label: 'Pipeline' },
  { path: '/visualizations', icon: BarChart2, label: 'Visualizaciones' },
  { path: '/results', icon: FileText, label: 'Resultados' },
  { path: '/settings', icon: Settings, label: 'Configuración' },
];

export function Sidebar() {
  const { isRunning, model } = useOllamaStatus();

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-slate-800">
        <h1 className="text-lg font-bold">Tourism Analyzer</h1>
        <p className="text-xs text-slate-400">AI Opinion Analysis</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              )
            }
          >
            <Icon className="w-5 h-5" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* LLM Status */}
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4" />
          <span className="text-sm">LLM Status</span>
        </div>
        <div className="mt-2 flex items-center gap-2">
          <div
            className={cn(
              'w-2 h-2 rounded-full',
              isRunning ? 'bg-green-500' : 'bg-red-500'
            )}
          />
          <span className="text-xs text-slate-400">
            {isRunning ? `Ollama: ${model}` : 'Ollama Offline'}
          </span>
        </div>
      </div>
    </aside>
  );
}
```

### 3.2 Zustand Stores

#### src/renderer/stores/pipelineStore.ts
```typescript
import { create } from 'zustand';
import type { PipelineProgress, PipelineConfig } from '@shared/types';

interface PipelineState {
  // Status
  isRunning: boolean;
  currentPhase: number | null;
  
  // Progress
  phases: Record<number, PipelineProgress>;
  
  // Configuration
  config: PipelineConfig;
  
  // Actions
  setRunning: (running: boolean) => void;
  setCurrentPhase: (phase: number | null) => void;
  updatePhaseProgress: (phase: number, progress: Partial<PipelineProgress>) => void;
  setConfig: (config: Partial<PipelineConfig>) => void;
  reset: () => void;
}

const initialPhases: Record<number, PipelineProgress> = {
  1: { phase: 1, phaseName: 'Procesamiento Básico', status: 'pending', progress: 0 },
  2: { phase: 2, phaseName: 'Análisis de Sentimientos', status: 'pending', progress: 0 },
  3: { phase: 3, phaseName: 'Análisis de Subjetividad', status: 'pending', progress: 0 },
  4: { phase: 4, phaseName: 'Clasificación de Categorías', status: 'pending', progress: 0 },
  5: { phase: 5, phaseName: 'Análisis de Tópicos', status: 'pending', progress: 0 },
  6: { phase: 6, phaseName: 'Resumen Inteligente', status: 'pending', progress: 0 },
  7: { phase: 7, phaseName: 'Visualizaciones', status: 'pending', progress: 0 },
};

export const usePipelineStore = create<PipelineState>((set) => ({
  isRunning: false,
  currentPhase: null,
  phases: { ...initialPhases },
  config: {
    phases: {
      phase_01: true,
      phase_02: true,
      phase_03: true,
      phase_04: true,
      phase_05: true,
      phase_06: true,
      phase_07: true,
    },
  },

  setRunning: (running) => set({ isRunning: running }),
  
  setCurrentPhase: (phase) => set({ currentPhase: phase }),
  
  updatePhaseProgress: (phase, progress) =>
    set((state) => ({
      phases: {
        ...state.phases,
        [phase]: { ...state.phases[phase], ...progress },
      },
    })),
  
  setConfig: (config) =>
    set((state) => ({
      config: { ...state.config, ...config },
    })),
  
  reset: () =>
    set({
      isRunning: false,
      currentPhase: null,
      phases: { ...initialPhases },
    }),
}));
```

### 3.3 Hooks

#### src/renderer/hooks/usePipeline.ts
```typescript
import { useEffect, useCallback } from 'react';
import { usePipelineStore } from '@/stores/pipelineStore';

export function usePipeline() {
  const {
    isRunning,
    currentPhase,
    phases,
    config,
    setRunning,
    setCurrentPhase,
    updatePhaseProgress,
    reset,
  } = usePipelineStore();

  // Listen for progress updates from main process
  useEffect(() => {
    const handleProgress = (_: any, data: any) => {
      updatePhaseProgress(data.phase, {
        status: 'running',
        progress: data.progress,
        message: data.message,
      });
    };

    window.electronAPI.pipeline.onProgress(handleProgress);
    
    return () => {
      window.electronAPI.pipeline.offProgress();
    };
  }, [updatePhaseProgress]);

  const runPhase = useCallback(async (phase: number) => {
    setRunning(true);
    setCurrentPhase(phase);
    updatePhaseProgress(phase, { status: 'running', progress: 0 });

    try {
      const result = await window.electronAPI.pipeline.runPhase(phase, config);
      
      updatePhaseProgress(phase, {
        status: result.success ? 'completed' : 'error',
        progress: result.success ? 100 : 0,
        error: result.error,
      });

      return result;
    } finally {
      setRunning(false);
      setCurrentPhase(null);
    }
  }, [config, setRunning, setCurrentPhase, updatePhaseProgress]);

  const runAll = useCallback(async () => {
    setRunning(true);
    reset();

    try {
      const result = await window.electronAPI.pipeline.runAll(config);
      return result;
    } finally {
      setRunning(false);
      setCurrentPhase(null);
    }
  }, [config, setRunning, setCurrentPhase, reset]);

  const stop = useCallback(async () => {
    await window.electronAPI.pipeline.stop();
    setRunning(false);
    setCurrentPhase(null);
  }, [setRunning, setCurrentPhase]);

  return {
    isRunning,
    currentPhase,
    phases,
    config,
    runPhase,
    runAll,
    stop,
  };
}
```

### 3.4 Page Routing

#### src/renderer/App.tsx
```tsx
import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Home } from '@/pages/Home';
import { Data } from '@/pages/Data';
import { Pipeline } from '@/pages/Pipeline';
import { Visualizations } from '@/pages/Visualizations';
import { Results } from '@/pages/Results';
import { Settings } from '@/pages/Settings';
import { Toaster } from '@/components/ui/toaster';

export function App() {
  return (
    <HashRouter>
      <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/data" element={<Data />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/visualizations" element={<Visualizations />} />
            <Route path="/results" element={<Results />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
        <Toaster />
      </div>
    </HashRouter>
  );
}
```

### Deliverables for Phase 3
- [ ] Sidebar navigation component
- [ ] Layout structure with routing
- [ ] Zustand stores (pipeline, data, settings)
- [ ] Custom hooks (usePipeline, useOllama)
- [ ] Basic page components (placeholders)
- [ ] Theme support (light/dark)

---

## 📋 Phase 4: Pipeline Integration

**Duration:** 7-10 days

### 4.1 Pipeline Page

#### src/renderer/pages/Pipeline.tsx
```tsx
import React from 'react';
import { Play, Square, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PhaseCard } from '@/components/pipeline/PhaseCard';
import { usePipeline } from '@/hooks/usePipeline';

export function Pipeline() {
  const { isRunning, phases, runAll, stop, runPhase } = usePipeline();

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Pipeline de Análisis</h1>
          <p className="text-slate-500">
            Ejecuta las 7 fases del análisis de opiniones
          </p>
        </div>
        
        <div className="flex gap-2">
          {isRunning ? (
            <Button variant="destructive" onClick={stop}>
              <Square className="w-4 h-4 mr-2" />
              Detener
            </Button>
          ) : (
            <Button onClick={runAll}>
              <Play className="w-4 h-4 mr-2" />
              Ejecutar Todo
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-4">
        {Object.values(phases).map((phase) => (
          <PhaseCard
            key={phase.phase}
            phase={phase}
            onRun={() => runPhase(phase.phase)}
            disabled={isRunning}
          />
        ))}
      </div>
    </div>
  );
}
```

### 4.2 Phase Card Component

#### src/renderer/components/pipeline/PhaseCard.tsx
```tsx
import React from 'react';
import { Play, Check, X, Loader2, SkipForward } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import type { PipelineProgress } from '@shared/types';

interface PhaseCardProps {
  phase: PipelineProgress;
  onRun: () => void;
  disabled?: boolean;
}

const statusIcons = {
  pending: null,
  running: Loader2,
  completed: Check,
  error: X,
  skipped: SkipForward,
};

const statusColors = {
  pending: 'bg-slate-100 border-slate-200',
  running: 'bg-blue-50 border-blue-200',
  completed: 'bg-green-50 border-green-200',
  error: 'bg-red-50 border-red-200',
  skipped: 'bg-slate-50 border-slate-200',
};

export function PhaseCard({ phase, onRun, disabled }: PhaseCardProps) {
  const StatusIcon = statusIcons[phase.status];

  return (
    <div
      className={cn(
        'border rounded-lg p-4 transition-colors',
        statusColors[phase.status]
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'w-8 h-8 rounded-full flex items-center justify-center',
              phase.status === 'completed' && 'bg-green-500 text-white',
              phase.status === 'error' && 'bg-red-500 text-white',
              phase.status === 'running' && 'bg-blue-500 text-white',
              phase.status === 'pending' && 'bg-slate-200 text-slate-500'
            )}
          >
            {StatusIcon ? (
              <StatusIcon
                className={cn('w-4 h-4', phase.status === 'running' && 'animate-spin')}
              />
            ) : (
              <span>{phase.phase}</span>
            )}
          </div>
          
          <div>
            <h3 className="font-medium">
              Fase {phase.phase}: {phase.phaseName}
            </h3>
            {phase.message && (
              <p className="text-sm text-slate-500">{phase.message}</p>
            )}
            {phase.error && (
              <p className="text-sm text-red-500">{phase.error}</p>
            )}
          </div>
        </div>

        <Button
          size="sm"
          variant="outline"
          onClick={onRun}
          disabled={disabled || phase.status === 'running'}
        >
          <Play className="w-4 h-4 mr-1" />
          Ejecutar
        </Button>
      </div>

      {phase.status === 'running' && (
        <div className="mt-3">
          <Progress value={phase.progress} />
          <p className="text-xs text-slate-500 mt-1 text-right">
            {phase.progress}%
          </p>
        </div>
      )}
    </div>
  );
}
```

### 4.3 Data Upload Page

#### src/renderer/pages/Data.tsx
```tsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DataPreview } from '@/components/data/DataPreview';
import { useDataStore } from '@/stores/dataStore';

export function Data() {
  const { dataset, setDataset, validateDataset } = useDataStore();
  const [isValidating, setIsValidating] = useState(false);

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file) return;

    setIsValidating(true);
    
    try {
      // Get file path (Electron provides the path)
      const filePath = (file as any).path;
      const result = await window.electronAPI.pipeline.validateDataset(filePath);
      
      if (result.success) {
        setDataset({
          path: filePath,
          name: file.name,
          rowCount: result.rowCount,
          columns: result.columns,
          preview: result.preview,
          validationStatus: result.valid ? 'valid' : 'warning',
          validationMessages: result.missingColumns?.length
            ? [`Columnas faltantes: ${result.missingColumns.join(', ')}`]
            : [],
        });
      }
    } finally {
      setIsValidating(false);
    }
  }, [setDataset]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false,
  });

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Gestión de Datos</h1>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-slate-300 hover:border-slate-400'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto text-slate-400 mb-4" />
        <p className="text-lg font-medium">
          {isDragActive
            ? 'Suelta el archivo aquí...'
            : 'Arrastra un archivo CSV o haz clic para seleccionar'}
        </p>
        <p className="text-sm text-slate-500 mt-2">
          Formato esperado: CSV con columnas Titulo, Review, FechaEstadia, Calificacion
        </p>
      </div>

      {/* Dataset info */}
      {dataset && (
        <div className="mt-6">
          <div className="flex items-center gap-4 p-4 bg-slate-100 rounded-lg">
            <FileText className="w-8 h-8 text-slate-600" />
            <div className="flex-1">
              <p className="font-medium">{dataset.name}</p>
              <p className="text-sm text-slate-500">
                {dataset.rowCount.toLocaleString()} filas • {dataset.columns.length} columnas
              </p>
            </div>
            {dataset.validationStatus === 'valid' ? (
              <Check className="w-6 h-6 text-green-500" />
            ) : (
              <AlertCircle className="w-6 h-6 text-amber-500" />
            )}
          </div>

          {dataset.validationMessages.length > 0 && (
            <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              {dataset.validationMessages.map((msg, i) => (
                <p key={i} className="text-sm text-amber-700">{msg}</p>
              ))}
            </div>
          )}

          {/* Preview table */}
          <DataPreview data={dataset.preview} columns={dataset.columns} />
        </div>
      )}
    </div>
  );
}
```

### Deliverables for Phase 4
- [ ] Pipeline page with phase cards
- [ ] Run all / run individual phase functionality
- [ ] Real-time progress updates
- [ ] Data upload with drag-and-drop
- [ ] Dataset validation and preview
- [ ] Error handling and display

---

## 📋 Phase 5: Visualizations

**Duration:** 5-7 days

### 5.1 Visualizations Gallery

#### src/renderer/pages/Visualizations.tsx
```tsx
import React, { useEffect, useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ImageGallery } from '@/components/visualizations/ImageGallery';
import { useVisualizationStore } from '@/stores/visualizationStore';

const categories = [
  { id: 'dashboard', label: 'Dashboard', folder: '01_dashboard' },
  { id: 'sentimientos', label: 'Sentimientos', folder: '02_sentimientos' },
  { id: 'categorias', label: 'Categorías', folder: '03_categorias' },
  { id: 'topicos', label: 'Tópicos', folder: '04_topicos' },
  { id: 'temporal', label: 'Temporal', folder: '05_temporal' },
];

export function Visualizations() {
  const { images, loadImages, selectedImage, setSelectedImage } = useVisualizationStore();
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadImages();
  }, [loadImages]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Visualizaciones</h1>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          {categories.map((cat) => (
            <TabsTrigger key={cat.id} value={cat.id}>
              {cat.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {categories.map((cat) => (
          <TabsContent key={cat.id} value={cat.id}>
            <ImageGallery
              images={images.filter((img) => img.category === cat.folder)}
              onSelect={setSelectedImage}
            />
          </TabsContent>
        ))}
      </Tabs>

      {/* Full-screen image modal */}
      {selectedImage && (
        <ImageModal
          image={selectedImage}
          onClose={() => setSelectedImage(null)}
        />
      )}
    </div>
  );
}
```

### 5.2 Interactive Charts (Alternative to PNG)

Consider using Recharts for interactive web-based charts instead of static PNG images:

#### src/renderer/components/visualizations/SentimentChart.tsx
```tsx
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface SentimentData {
  name: string;
  value: number;
  color: string;
}

const COLORS = {
  Positivo: '#22c55e',
  Neutro: '#64748b',
  Negativo: '#ef4444',
};

export function SentimentChart({ data }: { data: SentimentData[] }) {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
```

### Deliverables for Phase 5
- [ ] Visualization gallery page
- [ ] Category tabs (Dashboard, Sentiments, etc.)
- [ ] Image thumbnails with lightbox
- [ ] Export functionality (PNG, PDF)
- [ ] Optional: Interactive Recharts versions

---

## 📋 Phase 6: Settings & Configuration

**Duration:** 3-5 days

### 6.1 Settings Page

#### src/renderer/pages/Settings.tsx
```tsx
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LLMSettings } from '@/components/settings/LLMSettings';
import { OllamaManager } from '@/components/settings/OllamaManager';
import { GeneralSettings } from '@/components/settings/GeneralSettings';

export function Settings() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Configuración</h1>

      <Tabs defaultValue="llm">
        <TabsList>
          <TabsTrigger value="llm">LLM</TabsTrigger>
          <TabsTrigger value="ollama">Ollama</TabsTrigger>
          <TabsTrigger value="general">General</TabsTrigger>
        </TabsList>

        <TabsContent value="llm" className="mt-4">
          <LLMSettings />
        </TabsContent>

        <TabsContent value="ollama" className="mt-4">
          <OllamaManager />
        </TabsContent>

        <TabsContent value="general" className="mt-4">
          <GeneralSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### 6.2 LLM Settings Component

#### src/renderer/components/settings/LLMSettings.tsx
```tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useSettingsStore } from '@/stores/settingsStore';
import { useToast } from '@/hooks/useToast';

export function LLMSettings() {
  const { llm, setLLM } = useSettingsStore();
  const { toast } = useToast();
  
  const { register, handleSubmit, watch } = useForm({
    defaultValues: llm,
  });

  const mode = watch('mode');

  const onSubmit = async (data: any) => {
    await setLLM(data);
    toast({
      title: 'Configuración guardada',
      description: 'Los cambios se aplicarán en la próxima ejecución.',
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <Label>Modo LLM</Label>
        <RadioGroup defaultValue={mode} className="mt-2">
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="local" id="local" {...register('mode')} />
            <Label htmlFor="local">Local (Ollama) - Gratuito</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="api" id="api" {...register('mode')} />
            <Label htmlFor="api">API (OpenAI) - Pago</Label>
          </div>
        </RadioGroup>
      </div>

      {mode === 'local' ? (
        <>
          <div>
            <Label htmlFor="ollamaModel">Modelo Ollama</Label>
            <Input
              id="ollamaModel"
              {...register('ollamaModel')}
              placeholder="llama3.2:3b"
            />
          </div>
          <div>
            <Label htmlFor="ollamaBaseUrl">URL Base Ollama</Label>
            <Input
              id="ollamaBaseUrl"
              {...register('ollamaBaseUrl')}
              placeholder="http://localhost:11434"
            />
          </div>
        </>
      ) : (
        <>
          <div>
            <Label htmlFor="openaiModel">Modelo OpenAI</Label>
            <Input
              id="openaiModel"
              {...register('openaiModel')}
              placeholder="gpt-4o-mini"
            />
          </div>
          <div>
            <Label htmlFor="openaiApiKey">API Key OpenAI</Label>
            <Input
              id="openaiApiKey"
              type="password"
              {...register('openaiApiKey')}
              placeholder="sk-..."
            />
          </div>
        </>
      )}

      <div>
        <Label htmlFor="temperature">Temperatura</Label>
        <Input
          id="temperature"
          type="number"
          step="0.1"
          min="0"
          max="2"
          {...register('temperature', { valueAsNumber: true })}
        />
      </div>

      <Button type="submit">Guardar Configuración</Button>
    </form>
  );
}
```

### 6.3 Ollama Manager Component

#### src/renderer/components/settings/OllamaManager.tsx
```tsx
import React, { useEffect, useState } from 'react';
import { Download, Trash2, Check, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { useOllama } from '@/hooks/useOllama';

const RECOMMENDED_MODELS = [
  { name: 'llama3.2:3b', description: 'Balanceado (recomendado)', size: '2GB' },
  { name: 'llama3.2:1b', description: 'Ligero y rápido', size: '1GB' },
  { name: 'llama3.1:8b', description: 'Alta calidad', size: '4.7GB' },
  { name: 'gemma2:2b', description: 'Alternativa ligera', size: '1.6GB' },
];

export function OllamaManager() {
  const {
    status,
    models,
    pullProgress,
    checkStatus,
    pullModel,
    isPulling,
  } = useOllama();

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  return (
    <div className="space-y-6">
      {/* Status */}
      <div className="p-4 bg-slate-100 rounded-lg">
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              status.running ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="font-medium">
            {status.running ? 'Ollama está ejecutándose' : 'Ollama no está ejecutándose'}
          </span>
        </div>
        {!status.running && (
          <p className="text-sm text-slate-500 mt-2">
            Inicia Ollama ejecutando: <code>ollama serve</code>
          </p>
        )}
      </div>

      {/* Installed models */}
      <div>
        <h3 className="font-medium mb-3">Modelos Instalados</h3>
        {models.length === 0 ? (
          <p className="text-slate-500">No hay modelos instalados</p>
        ) : (
          <ul className="space-y-2">
            {models.map((model) => (
              <li
                key={model}
                className="flex items-center justify-between p-2 bg-slate-50 rounded"
              >
                <span>{model}</span>
                <Check className="w-4 h-4 text-green-500" />
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Recommended models */}
      <div>
        <h3 className="font-medium mb-3">Modelos Recomendados</h3>
        <div className="space-y-2">
          {RECOMMENDED_MODELS.map((model) => {
            const isInstalled = models.includes(model.name);
            return (
              <div
                key={model.name}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div>
                  <p className="font-medium">{model.name}</p>
                  <p className="text-sm text-slate-500">
                    {model.description} • {model.size}
                  </p>
                </div>
                {isInstalled ? (
                  <span className="text-green-600 text-sm flex items-center gap-1">
                    <Check className="w-4 h-4" /> Instalado
                  </span>
                ) : (
                  <Button
                    size="sm"
                    onClick={() => pullModel(model.name)}
                    disabled={isPulling}
                  >
                    {isPulling ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4 mr-1" />
                    )}
                    Descargar
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Pull progress */}
      {isPulling && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm mb-2">Descargando modelo...</p>
          <Progress value={pullProgress} />
          <p className="text-xs text-slate-500 mt-1 text-right">{pullProgress}%</p>
        </div>
      )}
    </div>
  );
}
```

### Deliverables for Phase 6
- [ ] Settings page with tabs
- [ ] LLM mode selection (Local/API)
- [ ] Ollama status display
- [ ] Model management (list, download)
- [ ] API key input with encryption
- [ ] Settings persistence

---

## 📋 Phase 7: Polish & Testing

**Duration:** 7-10 days

### 7.1 Testing Strategy

```typescript
// Unit tests with Vitest
// E2E tests with Playwright

// Example test file: tests/pipeline.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Pipeline', () => {
  test('should display all 7 phases', async ({ page }) => {
    await page.goto('/pipeline');
    
    for (let i = 1; i <= 7; i++) {
      await expect(page.getByText(`Fase ${i}:`)).toBeVisible();
    }
  });

  test('should run a single phase', async ({ page }) => {
    await page.goto('/pipeline');
    await page.getByTestId('phase-1-run').click();
    await expect(page.getByTestId('phase-1-status')).toHaveText('completed');
  });
});
```

### 7.2 Error Handling

```typescript
// Global error boundary
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600">
              Ha ocurrido un error
            </h1>
            <p className="mt-2">{this.state.error?.message}</p>
            <Button onClick={() => window.location.reload()}>
              Recargar aplicación
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 7.3 Loading States & Animations

```tsx
// Skeleton loading
export function PipelineSkeletons() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 7 }).map((_, i) => (
        <div
          key={i}
          className="h-20 bg-slate-200 animate-pulse rounded-lg"
        />
      ))}
    </div>
  );
}

// Framer Motion transitions
import { motion } from 'framer-motion';

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
}
```

### 7.4 Accessibility

- Keyboard navigation support
- ARIA labels
- Focus management
- High contrast mode support
- Screen reader compatibility

### Deliverables for Phase 7
- [ ] Unit tests for stores and utilities
- [ ] E2E tests for critical paths
- [ ] Error boundaries and fallbacks
- [ ] Loading states and skeletons
- [ ] Animations and transitions
- [ ] Accessibility audit pass
- [ ] Performance optimization

---

## 📋 Phase 8: Packaging & Distribution

**Duration:** 5-7 days

### 8.1 Electron Builder Configuration

#### electron-builder.yml
```yaml
appId: com.tourism-analyzer.desktop
productName: AI Tourism Analyzer
copyright: Copyright © 2024

directories:
  output: dist
  buildResources: resources

files:
  - '**/*'
  - '!python/**/*'

extraResources:
  - from: 'python'
    to: 'python'
    filter:
      - '**/*'
      - '!**/__pycache__/**'
      - '!**/*.pyc'

mac:
  category: public.app-category.productivity
  icon: resources/icons/icon.icns
  target:
    - dmg
    - zip

win:
  icon: resources/icons/icon.ico
  target:
    - nsis
    - portable

linux:
  icon: resources/icons
  category: Office
  target:
    - AppImage
    - deb

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
```

### 8.2 Build Scripts

#### package.json (scripts section)
```json
{
  "scripts": {
    "dev": "electron-forge start",
    "build": "electron-forge make",
    "package": "electron-forge package",
    "build:win": "electron-builder --win",
    "build:mac": "electron-builder --mac",
    "build:linux": "electron-builder --linux",
    "build:all": "electron-builder --win --mac --linux"
  }
}
```

### 8.3 Bundle Python (Optional)

```bash
# Create standalone Python bundle with PyInstaller
cd python
pyinstaller --onedir \
  --add-data "config:config" \
  --add-data "core:core" \
  --add-data "models:models" \
  --hidden-import=torch \
  --hidden-import=transformers \
  api_bridge.py

# Copy to resources
cp -r dist/api_bridge ../resources/python/
```

### 8.4 Release Checklist

- [ ] Version bump in package.json
- [ ] Update CHANGELOG.md
- [ ] Test on Windows
- [ ] Test on macOS
- [ ] Test on Linux
- [ ] Code signing (macOS, Windows)
- [ ] Notarization (macOS)
- [ ] Create GitHub release
- [ ] Upload installers
- [ ] Update documentation

### Deliverables for Phase 8
- [ ] Electron Builder configuration
- [ ] Windows installer (NSIS)
- [ ] macOS installer (DMG)
- [ ] Linux packages (AppImage, deb)
- [ ] Auto-update configuration (optional)
- [ ] Release on GitHub

---

## 📊 Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| 0 | 3-5 days | Project setup |
| 1 | 5-7 days | Core infrastructure |
| 2 | 5-7 days | Python bridge |
| 3 | 5-7 days | UI foundation |
| 4 | 7-10 days | Pipeline integration |
| 5 | 5-7 days | Visualizations |
| 6 | 3-5 days | Settings |
| 7 | 7-10 days | Polish & testing |
| 8 | 5-7 days | Packaging |
| **Total** | **8-12 weeks** | Full development |

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| App launch time | < 5 seconds |
| Pipeline execution | Same as CLI |
| Memory usage | < 2GB base |
| Error rate | < 1% |
| Test coverage | > 70% |
| Accessibility | WCAG 2.1 AA |

---

## 📚 Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [Electron Forge](https://www.electronforge.io/)
- [React Documentation](https://react.dev/)
- [Zustand](https://github.com/pmndrs/zustand)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Recharts](https://recharts.org/)

---

## ✅ Getting Started

1. Read [DESKTOP_APP_ARCHITECTURE.md](./DESKTOP_APP_ARCHITECTURE.md)
2. Complete Phase 0 setup
3. Follow phases sequentially
4. Test each phase before proceeding
5. Document any deviations from plan

/**
 * SetupManager - Manages first-run setup state and system checks
 * ================================================================
 * Handles detection of first-run state, system requirements verification,
 * and persistence of setup completion status.
 */

import Store from 'electron-store';
import { app } from 'electron';
import path from 'path';
import fs from 'fs';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Setup state interface
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

// System check result interface
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
  };
}

// Default setup state
const defaultSetupState: SetupState = {
  isComplete: false,
  completedAt: null,
  pythonReady: false,
  llmProvider: null,
  ollamaInstalled: false,
  ollamaModelReady: false,
  modelsDownloaded: {
    sentiment: false,
    embeddings: false,
    subjectivity: false,
    categories: false,
  },
  openaiKeyConfigured: false,
};

/**
 * SetupManager class for handling first-run setup
 */
export class SetupManager {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private store: any;

  constructor() {
    this.store = new Store({
      name: 'setup-state',
      defaults: { setup: defaultSetupState },
    });
  }

  /**
   * Check if this is the first run of the application
   */
  isFirstRun(): boolean {
    const state = this.store.get('setup') as SetupState;
    return !state?.isComplete;
  }

  /**
   * Get the current setup state
   */
  getSetupState(): SetupState {
    return (this.store.get('setup') as SetupState) || defaultSetupState;
  }

  /**
   * Update the setup state with partial updates
   */
  updateSetupState(updates: Partial<SetupState>): void {
    const current = this.getSetupState();
    this.store.set('setup', { ...current, ...updates });
  }

  /**
   * Run comprehensive system check
   */
  async runSystemCheck(): Promise<SystemCheckResult> {
    const [pythonCheck, venvCheck, diskSpace, gpu] = await Promise.all([
      this.checkPythonRuntime(),
      this.checkPythonVenv(),
      this.checkDiskSpace(),
      this.detectGPU(),
    ]);

    const memory = this.checkMemory();

    return {
      pythonRuntime: pythonCheck.available,
      pythonVersion: pythonCheck.version,
      pythonVenvReady: venvCheck,
      diskSpace: {
        available: diskSpace.available,
        required: 5 * 1024 * 1024 * 1024, // 5GB
        sufficient: diskSpace.available >= 5 * 1024 * 1024 * 1024,
      },
      memory: {
        total: memory.total,
        available: memory.available,
        sufficient: memory.total >= 8 * 1024 * 1024 * 1024, // 8GB recommended
      },
      gpu: gpu,
    };
  }

  /**
   * Check if Python virtual environment with dependencies is ready
   */
  private async checkPythonVenv(): Promise<boolean> {
    const isWindows = process.platform === 'win32';
    const pythonExe = isWindows ? 'python.exe' : 'python';
    const venvBinDir = isWindows ? 'Scripts' : 'bin';
    
    let venvPythonPath: string;
    
    if (app.isPackaged) {
      venvPythonPath = path.join(process.resourcesPath, 'python', 'venv', venvBinDir, pythonExe);
    } else {
      venvPythonPath = path.join(app.getAppPath(), 'python', 'venv', venvBinDir, pythonExe);
    }
    
    // Check if venv Python exists
    if (!fs.existsSync(venvPythonPath)) {
      return false;
    }
    
    // Check if key dependencies are installed
    try {
      await execAsync(`"${venvPythonPath}" -c "import pandas; import torch; print('ok')"`);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check if Python runtime is available
   */
  private async checkPythonRuntime(): Promise<{ available: boolean; version?: string }> {
    // Determine the venv paths based on platform
    const isWindows = process.platform === 'win32';
    const pythonExe = isWindows ? 'python.exe' : 'python';
    const venvBinDir = isWindows ? 'Scripts' : 'bin';
    
    // In production, bundled Python is always available
    if (app.isPackaged) {
      const pythonPath = path.join(process.resourcesPath, 'python', 'venv', venvBinDir, pythonExe);
      const exists = fs.existsSync(pythonPath);
      return { available: exists, version: exists ? 'bundled' : undefined };
    }

    // In development, check system Python
    // On Windows, 'python' is the standard command
    // On Unix, 'python3' is preferred
    const primaryCmd = isWindows ? 'python --version' : 'python3 --version';
    const fallbackCmd = 'python --version';
    
    try {
      const { stdout } = await execAsync(primaryCmd);
      const version = stdout.trim().replace('Python ', '');
      return { available: true, version };
    } catch {
      try {
        const { stdout } = await execAsync(fallbackCmd);
        const version = stdout.trim().replace('Python ', '');
        return { available: true, version };
      } catch {
        return { available: false };
      }
    }
  }

  /**
   * Check available disk space
   */
  private async checkDiskSpace(): Promise<{ available: number }> {
    try {
      if (process.platform === 'win32') {
        // Windows: Use WMIC or PowerShell
        const { stdout } = await execAsync(
          'powershell -Command "(Get-PSDrive C).Free"'
        );
        const bytes = parseInt(stdout.trim(), 10);
        return { available: isNaN(bytes) ? 10 * 1024 * 1024 * 1024 : bytes };
      } else {
        // macOS/Linux: Use df
        const userDataPath = app.getPath('userData');
        const { stdout } = await execAsync(`df -k "${userDataPath}"`);
        const lines = stdout.split('\n');
        if (lines.length >= 2) {
          const parts = lines[1].split(/\s+/);
          if (parts.length >= 4) {
            return { available: parseInt(parts[3], 10) * 1024 };
          }
        }
        return { available: 10 * 1024 * 1024 * 1024 };
      }
    } catch {
      // Assume 10GB if check fails
      return { available: 10 * 1024 * 1024 * 1024 };
    }
  }

  /**
   * Check system memory
   */
  private checkMemory(): { total: number; available: number } {
    return {
      total: os.totalmem(),
      available: os.freemem(),
    };
  }

  /**
   * Detect GPU availability (CUDA support)
   */
  private async detectGPU(): Promise<{ available: boolean; name?: string }> {
    const isWindows = process.platform === 'win32';
    const pythonCmd = isWindows ? 'python' : 'python3';
    
    try {
      // Check CUDA availability via Python
      const { stdout } = await execAsync(
        `${pythonCmd} -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"`
      );
      const parts = stdout.trim().split(' ');
      const available = parts[0] === 'True';
      const name = parts.slice(1).join(' ') || undefined;
      return {
        available,
        name,
      };
    } catch {
      // Try nvidia-smi as fallback
      try {
        const nvidiaSmiCmd = isWindows 
          ? 'nvidia-smi --query-gpu=name --format=csv,noheader'
          : 'nvidia-smi --query-gpu=name --format=csv,noheader';
        const { stdout } = await execAsync(nvidiaSmiCmd);
        return {
          available: true,
          name: stdout.trim().split('\n')[0],
        };
      } catch {
        return { available: false };
      }
    }
  }

  /**
   * Mark setup as complete
   */
  markSetupComplete(): void {
    this.store.set('setup.isComplete', true);
    this.store.set('setup.completedAt', new Date().toISOString());
  }

  /**
   * Reset setup state (for testing or re-setup)
   */
  resetSetupState(): void {
    this.store.set('setup', defaultSetupState);
  }

  /**
   * Update models downloaded status
   */
  updateModelsDownloaded(models: Partial<SetupState['modelsDownloaded']>): void {
    const current = this.getSetupState();
    this.store.set('setup', {
      ...current,
      modelsDownloaded: { ...current.modelsDownloaded, ...models },
    });
  }
}

// Singleton instance
export const setupManager = new SetupManager();

/**
 * SetupManager - Manages first-run setup state and system checks
 * ================================================================
 * Handles detection of first-run state, system requirements verification,
 * and persistence of setup completion status.
 * 
 * Enhanced with robust Windows hardware detection for:
 * - CPU info (cores, threads, model)
 * - RAM (total, available)
 * - GPU (dedicated/integrated, VRAM, CUDA support)
 */

import Store from 'electron-store';
import { app } from 'electron';
import path from 'path';
import fs from 'fs';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import type { HardwareDetectionResult, DetectionStatus } from '../../shared/types';

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
  // Store manual hardware overrides
  hardwareOverrides?: Partial<{
    cpuTier: 'low' | 'mid' | 'high';
    ramGB: number;
    gpuType: 'none' | 'integrated' | 'dedicated';
    vramGB: number;
  }>;
}

// System check result interface (keep for backward compatibility)
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

  // ============================================
  // Enhanced Hardware Detection for Windows
  // ============================================

  /**
   * Detect detailed CPU information using WMI on Windows
   */
  private async detectCPU(): Promise<HardwareDetectionResult['cpu']> {
    const fallbackResult: HardwareDetectionResult['cpu'] = {
      name: 'Unknown CPU',
      cores: os.cpus().length || 4,
      threads: os.cpus().length || 4,
      tier: 'mid',
      detectionStatus: 'fallback',
      detectionSource: 'os.cpus()',
    };

    if (process.platform !== 'win32') {
      // For non-Windows, use os.cpus()
      const cpus = os.cpus();
      if (cpus.length > 0) {
        const coreCount = cpus.length;
        let tier: 'low' | 'mid' | 'high' = 'mid';
        if (coreCount >= 8) tier = 'high';
        else if (coreCount <= 2) tier = 'low';
        
        return {
          name: cpus[0].model || 'Unknown CPU',
          cores: coreCount,
          threads: coreCount,
          tier,
          detectionStatus: 'auto-detected',
          detectionSource: 'os.cpus()',
        };
      }
      return fallbackResult;
    }

    try {
      // Use PowerShell to get detailed CPU info via WMI
      const { stdout } = await execAsync(
        'powershell -Command "Get-CimInstance -ClassName Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | ConvertTo-Json"',
        { timeout: 10000 }
      );
      
      const cpuInfo = JSON.parse(stdout.trim());
      const cpu = Array.isArray(cpuInfo) ? cpuInfo[0] : cpuInfo;
      
      const cores = cpu.NumberOfCores || os.cpus().length;
      const threads = cpu.NumberOfLogicalProcessors || cores;
      
      // Determine tier based on cores and CPU model
      let tier: 'low' | 'mid' | 'high' = 'mid';
      const cpuName = (cpu.Name || '').toLowerCase();
      
      if (cores >= 8 || cpuName.includes('i9') || cpuName.includes('i7') || cpuName.includes('ryzen 7') || cpuName.includes('ryzen 9')) {
        tier = 'high';
      } else if (cores <= 2 || cpuName.includes('celeron') || cpuName.includes('pentium') || cpuName.includes('atom')) {
        tier = 'low';
      }

      return {
        name: cpu.Name || 'Unknown CPU',
        cores,
        threads,
        tier,
        detectionStatus: 'auto-detected',
        detectionSource: 'WMI (Win32_Processor)',
      };
    } catch (error) {
      console.warn('Failed to detect CPU via WMI, falling back to os.cpus():', error);
      return fallbackResult;
    }
  }

  /**
   * Detect detailed RAM information
   */
  private async detectRAM(): Promise<HardwareDetectionResult['ram']> {
    const totalBytes = os.totalmem();
    const availableBytes = os.freemem();
    const totalGB = Math.round(totalBytes / (1024 * 1024 * 1024));
    const availableGB = Math.round(availableBytes / (1024 * 1024 * 1024) * 10) / 10;

    return {
      totalGB,
      availableGB,
      detectionStatus: 'auto-detected',
      detectionSource: 'os.totalmem()',
    };
  }

  /**
   * Detect detailed GPU information including VRAM and type
   */
  private async detectGPUDetailed(): Promise<HardwareDetectionResult['gpu']> {
    const noGpuResult: HardwareDetectionResult['gpu'] = {
      available: false,
      type: 'none',
      cudaAvailable: false,
      detectionStatus: 'auto-detected',
      detectionSource: 'No dedicated GPU detected',
    };

    // List of known integrated GPU keywords
    const integratedGpuKeywords = [
      'intel', 'uhd', 'iris', 'hd graphics', 'integrated',
      'amd radeon graphics', 'vega', 'apu'
    ];

    // List of known dedicated GPU keywords
    const dedicatedGpuKeywords = [
      'nvidia', 'geforce', 'rtx', 'gtx', 'quadro', 'tesla',
      'radeon rx', 'radeon pro', 'arc a'
    ];

    if (process.platform === 'win32') {
      try {
        // First, try nvidia-smi for NVIDIA GPUs (most accurate for VRAM)
        try {
          const { stdout: nvidiaSmi } = await execAsync(
            'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits',
            { timeout: 10000 }
          );
          
          const lines = nvidiaSmi.trim().split('\n');
          if (lines.length > 0 && lines[0].trim()) {
            const [name, vramMB] = lines[0].split(',').map(s => s.trim());
            const vramGB = Math.round(parseInt(vramMB, 10) / 1024);
            
            // Check CUDA availability via Python
            let cudaAvailable = false;
            try {
              const { stdout: cudaCheck } = await execAsync(
                'python -c "import torch; print(torch.cuda.is_available())"',
                { timeout: 10000 }
              );
              cudaAvailable = cudaCheck.trim().toLowerCase() === 'true';
            } catch {
              // CUDA check failed, assume true for NVIDIA
              cudaAvailable = true;
            }

            return {
              available: true,
              type: 'dedicated',
              name,
              vramGB,
              cudaAvailable,
              detectionStatus: 'auto-detected',
              detectionSource: 'nvidia-smi',
            };
          }
        } catch {
          // nvidia-smi not available, continue to WMI
        }

        // Use WMI to detect all GPUs
        const { stdout } = await execAsync(
          'powershell -Command "Get-CimInstance -ClassName Win32_VideoController | Select-Object Name, AdapterRAM, VideoProcessor | ConvertTo-Json"',
          { timeout: 10000 }
        );
        
        const gpuInfo = JSON.parse(stdout.trim());
        const gpus = Array.isArray(gpuInfo) ? gpuInfo : [gpuInfo];
        
        // Find the best GPU (prefer dedicated over integrated)
        let bestGpu: { name: string; vram: number; type: 'integrated' | 'dedicated' } | null = null;
        
        for (const gpu of gpus) {
          if (!gpu.Name) continue;
          
          const gpuName = gpu.Name.toLowerCase();
          const vramBytes = gpu.AdapterRAM || 0;
          // WMI reports AdapterRAM in bytes, but can overflow for > 4GB
          // If value is negative or suspiciously small, it's an overflow
          let vramGB = 0;
          if (vramBytes > 0 && vramBytes < 17179869184) { // < 16GB in bytes
            vramGB = Math.round(vramBytes / (1024 * 1024 * 1024));
          }
          
          // Determine GPU type
          let type: 'integrated' | 'dedicated' = 'integrated';
          
          if (dedicatedGpuKeywords.some(kw => gpuName.includes(kw))) {
            type = 'dedicated';
          } else if (integratedGpuKeywords.some(kw => gpuName.includes(kw))) {
            type = 'integrated';
          } else if (vramGB >= 2) {
            // If VRAM >= 2GB and not recognized, likely dedicated
            type = 'dedicated';
          }
          
          // Prefer dedicated GPU
          if (!bestGpu || (type === 'dedicated' && bestGpu.type === 'integrated')) {
            bestGpu = { name: gpu.Name, vram: vramGB, type };
          }
        }
        
        if (bestGpu) {
          return {
            available: true,
            type: bestGpu.type,
            name: bestGpu.name,
            vramGB: bestGpu.vram > 0 ? bestGpu.vram : undefined,
            cudaAvailable: bestGpu.name.toLowerCase().includes('nvidia'),
            detectionStatus: bestGpu.vram > 0 ? 'auto-detected' : 'fallback',
            detectionSource: bestGpu.vram > 0 ? 'WMI (Win32_VideoController)' : 'WMI (VRAM not detected accurately)',
          };
        }
        
        return noGpuResult;
      } catch (error) {
        console.warn('Failed to detect GPU via WMI:', error);
        return {
          ...noGpuResult,
          detectionStatus: 'failed',
          detectionSource: 'Detection failed: ' + (error instanceof Error ? error.message : String(error)),
        };
      }
    } else {
      // Non-Windows: try nvidia-smi
      try {
        const { stdout } = await execAsync('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits');
        const [name, vramMB] = stdout.trim().split(',').map(s => s.trim());
        const vramGB = Math.round(parseInt(vramMB, 10) / 1024);
        
        return {
          available: true,
          type: 'dedicated',
          name,
          vramGB,
          cudaAvailable: true,
          detectionStatus: 'auto-detected',
          detectionSource: 'nvidia-smi',
        };
      } catch {
        return noGpuResult;
      }
    }
  }

  /**
   * Generate intelligent LLM recommendation based on hardware
   * 
   * LLM Usage in this app:
   * - Phase 6: Intelligent Summaries - Uses LLM to generate professional summaries
   *   for tourism insights. Requires processing multiple reviews and generating
   *   coherent, structured output.
   * 
   * Minimum Requirements for Local LLM (Ollama):
   * - Lightweight model (1B-3B): 8GB RAM minimum, 16GB recommended
   * - Medium model (7B-8B): 16GB RAM minimum, 32GB recommended
   * - GPU acceleration highly recommended for reasonable performance
   * 
   * The 4GB RAM "requirement" in the old code was incorrect - local LLMs
   * need significantly more memory for acceptable performance.
   */
  private generateRecommendation(
    cpu: HardwareDetectionResult['cpu'],
    ram: HardwareDetectionResult['ram'],
    gpu: HardwareDetectionResult['gpu']
  ): HardwareDetectionResult['recommendation'] {
    const warnings: string[] = [];
    let canRunLocalLLM = false;
    let recommendedProvider: 'ollama' | 'openai' = 'openai';
    let recommendedModel: string | undefined;
    let reasoning: string;

    const ramGB = ram.totalGB;
    const hasGPU = gpu.type === 'dedicated';
    const vramGB = gpu.vramGB || 0;
    const hasCUDA = gpu.cudaAvailable && hasGPU;

    // Determine if local LLM is viable
    // For good UX with local LLM, we need adequate resources
    if (ramGB >= 32 && hasGPU && vramGB >= 8) {
      // Excellent hardware - can run larger models
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.1:8b';
      reasoning = 'Excelente hardware detectado. Puedes ejecutar modelos locales potentes con aceleración GPU.';
    } else if (ramGB >= 16 && hasGPU && vramGB >= 6) {
      // Good hardware - can run medium models
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:3b';
      reasoning = 'Buen hardware con GPU dedicada. Recomendamos modelos locales de tamaño medio para mejor equilibrio.';
    } else if (ramGB >= 16) {
      // Adequate RAM but no/weak GPU
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:3b';
      reasoning = 'RAM adecuada para modelos locales. La falta de GPU puede ralentizar el procesamiento.';
      if (!hasGPU) {
        warnings.push('Sin GPU dedicada: el procesamiento será más lento (CPU only)');
      }
    } else if (ramGB >= 12) {
      // Marginal - can try lightweight models
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:1b';
      reasoning = 'Hardware limitado. Puedes usar modelos ultra-ligeros, pero OpenAI ofrecerá mejor rendimiento.';
      warnings.push('RAM limitada: solo modelos ultra-ligeros (1B) funcionarán bien');
    } else if (ramGB >= 8) {
      // Low RAM - API strongly recommended
      canRunLocalLLM = false;
      recommendedProvider = 'openai';
      reasoning = 'RAM insuficiente para modelos locales con buen rendimiento. OpenAI API es la mejor opción.';
      warnings.push('8GB RAM: los modelos locales funcionarán muy lento o fallarán');
      warnings.push('Recomendamos encarecidamente usar OpenAI API');
    } else {
      // Very low RAM - API required
      canRunLocalLLM = false;
      recommendedProvider = 'openai';
      reasoning = 'Hardware insuficiente para modelos locales. Se requiere OpenAI API.';
      warnings.push('RAM muy baja: los modelos locales no funcionarán correctamente');
    }

    // Additional warnings based on CPU
    if (cpu.tier === 'low') {
      warnings.push('CPU de gama baja: el procesamiento local será significativamente más lento');
    }

    return {
      canRunLocalLLM,
      recommendedProvider,
      recommendedModel,
      reasoning,
      warnings,
    };
  }

  /**
   * Run comprehensive hardware detection
   */
  async detectHardware(): Promise<HardwareDetectionResult> {
    const [cpu, ram, gpu] = await Promise.all([
      this.detectCPU(),
      this.detectRAM(),
      this.detectGPUDetailed(),
    ]);

    // Apply any manual overrides from saved state
    const state = this.getSetupState();
    if (state.hardwareOverrides) {
      if (state.hardwareOverrides.cpuTier) {
        cpu.tier = state.hardwareOverrides.cpuTier;
        cpu.detectionStatus = 'manual';
      }
      if (state.hardwareOverrides.ramGB) {
        ram.totalGB = state.hardwareOverrides.ramGB;
        ram.detectionStatus = 'manual';
      }
      if (state.hardwareOverrides.gpuType) {
        gpu.type = state.hardwareOverrides.gpuType;
        gpu.available = state.hardwareOverrides.gpuType !== 'none';
        gpu.detectionStatus = 'manual';
      }
      if (state.hardwareOverrides.vramGB !== undefined && gpu.type === 'dedicated') {
        gpu.vramGB = state.hardwareOverrides.vramGB;
      }
    }

    const recommendation = this.generateRecommendation(cpu, ram, gpu);

    return {
      cpu,
      ram,
      gpu,
      recommendation,
    };
  }

  /**
   * Save manual hardware overrides
   */
  saveHardwareOverrides(overrides: Partial<SetupState['hardwareOverrides']>): void {
    const current = this.getSetupState();
    this.store.set('setup', {
      ...current,
      hardwareOverrides: { ...current.hardwareOverrides, ...overrides },
    });
  }

  /**
   * Clear hardware overrides (use auto-detection)
   */
  clearHardwareOverrides(): void {
    const current = this.getSetupState();
    delete current.hardwareOverrides;
    this.store.set('setup', current);
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

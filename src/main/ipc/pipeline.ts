// ============================================
// Pipeline IPC Handlers
// ============================================

import { ipcMain, BrowserWindow } from 'electron';
import type { PipelineProgress, PipelineResult, PipelineConfig, DatasetValidation } from '../../shared/types';
import { getPythonBridge } from '../python/bridge';

// Pipeline state management
let isRunning = false;
let shouldStop = false;
let currentPhase = 0;

/**
 * Get phase name by ID
 */
function getPhaseNameById(phaseId: number): string {
  const phaseNames: Record<number, string> = {
    1: 'Basic Processing',
    2: 'Sentiment Analysis',
    3: 'Subjectivity Analysis',
    4: 'Category Classification',
    5: 'Hierarchical Topic Analysis',
    6: 'Intelligent Summarization',
    7: 'Visualization Generation',
  };
  return phaseNames[phaseId] || 'Unknown';
}

/**
 * Send progress update to all windows
 */
function sendProgressUpdate(progress: PipelineProgress): void {
  const windows = BrowserWindow.getAllWindows();
  windows.forEach(win => {
    if (!win.isDestroyed()) {
      win.webContents.send('pipeline:progress', progress);
    }
  });
}

/**
 * Get the current pipeline status
 */
async function getPipelineStatus(): Promise<PipelineProgress> {
  const bridge = getPythonBridge();
  
  try {
    const response = await bridge.execute({ action: 'get_status' }, 5000);
    
    if (response.success) {
      const pythonPhase = response.currentPhase as number | null;
      return {
        phase: pythonPhase || currentPhase,
        phaseName: getPhaseNameById(pythonPhase || currentPhase),
        status: response.isRunning ? 'running' : (isRunning ? 'running' : 'pending'),
        progress: 0,
      };
    }
  } catch (error) {
    console.error('[Pipeline] Failed to get Python status:', error);
  }

  // Fallback to local state
  return {
    phase: currentPhase,
    phaseName: getPhaseNameById(currentPhase),
    status: isRunning ? 'running' : 'pending',
    progress: 0,
  };
}

/**
 * Run a single pipeline phase via Python bridge
 */
async function runPhase(phase: number, config?: object): Promise<PipelineResult> {
  if (isRunning) {
    return {
      success: false,
      completedPhases: [],
      outputs: {},
      duration: 0,
      error: 'Pipeline is already running',
    };
  }

  isRunning = true;
  shouldStop = false;
  currentPhase = phase;
  const startTime = Date.now();
  const bridge = getPythonBridge();
  
  // Set phase context in bridge for progress parsing
  const phaseName = getPhaseNameById(phase);
  bridge.setPhaseContext(phase, phaseName);

  try {
    sendProgressUpdate({
      phase,
      phaseName: getPhaseNameById(phase),
      status: 'running',
      progress: 0,
      message: `Starting phase ${phase}...`,
    });

    // Execute phase via Python bridge
    // Use a long timeout (45 min) since LLM-heavy phases like phase 6
    // (Resumen Inteligente) make many sequential LLM calls that can take
    // a long time, especially with local models via Ollama.
    const response = await bridge.execute({
      action: 'run_phase',
      phase,
      config: config || {},
    }, 2700000);

    // Check if stopped by user - treat as cancellation, not failure
    if (shouldStop) {
      sendProgressUpdate({
        phase,
        phaseName: getPhaseNameById(phase),
        status: 'pending',
        progress: 0,
        message: 'Stopped by user',
      });
      
      return {
        success: false,
        completedPhases: [],
        outputs: {},
        duration: Date.now() - startTime,
        error: 'stopped',  // Special marker for stopped state
      };
    }

    if (!response.success) {
      throw new Error(response.error as string || 'Phase execution failed');
    }

    // Clear phase context BEFORE sending completed status
    // This prevents late-arriving stderr tqdm data from overwriting the completed state
    bridge.setPhaseContext(null, null);

    sendProgressUpdate({
      phase,
      phaseName: getPhaseNameById(phase),
      status: 'completed',
      progress: 100,
      message: `Phase ${phase} completed`,
    });

    const duration = Date.now() - startTime;

    // Forward output paths from the Python response so the renderer can use them
    const outputs = (response.outputs as Record<string, string>) || {};

    return {
      success: true,
      completedPhases: [phase],
      outputs,
      duration,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    const errorMessage = (error as Error).message;
    
    sendProgressUpdate({
      phase,
      phaseName: getPhaseNameById(phase),
      status: 'failed',
      progress: 0,
      error: errorMessage,
    });

    return {
      success: false,
      completedPhases: [],
      outputs: {},
      duration,
      error: errorMessage,
    };
  } finally {
    isRunning = false;
    currentPhase = 0;
    // Clear phase context
    bridge.setPhaseContext(null, null);
  }
}

/**
 * Run all enabled pipeline phases via Python bridge
 */
async function runAllPhases(config?: PipelineConfig): Promise<PipelineResult> {
  if (isRunning) {
    return {
      success: false,
      completedPhases: [],
      outputs: {},
      duration: 0,
      error: 'Pipeline is already running',
    };
  }

  isRunning = true;
  shouldStop = false;
  const startTime = Date.now();
  const completedPhases: number[] = [];
  const bridge = getPythonBridge();

  try {
    // Build phases config for Python
    const phasesConfig: Record<string, { enabled: boolean }> = {};
    const phases = config?.phases || {
      phase01: { enabled: true },
      phase02: { enabled: true },
      phase03: { enabled: true },
      phase04: { enabled: true },
      phase05: { enabled: true },
      phase06: { enabled: true },
      phase07: { enabled: true },
    };

    // Convert to Python-expected format
    Object.entries(phases).forEach(([key, value]) => {
      phasesConfig[key] = { enabled: value.enabled };
    });

    // Execute all phases via Python bridge (long timeout for full pipeline)
    const response = await bridge.execute({
      action: 'run_all',
      config: {
        phases: phasesConfig,
        ...config,
      },
    }, 2700000);

    if (!response.success) {
      throw new Error(response.error as string || 'Pipeline execution failed');
    }

    // Extract completed phases from response
    const results = response.results as Array<{ phase: number; status: string; success?: boolean; outputs?: Record<string, string> }>;
    if (results) {
      results.forEach(result => {
        if (result.success || result.status === 'completed') {
          completedPhases.push(result.phase);
        }
      });
    }

    const duration = Date.now() - startTime;

    // Collect output paths from the last successful phase response
    // (the Python bridge returns them for every phase, but the charts/summary
    // paths from the last phase are the most relevant)
    const lastResult = results?.[results.length - 1];
    const outputs = (lastResult?.outputs as Record<string, string>) || {};

    return {
      success: true,
      completedPhases,
      outputs,
      duration,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    return {
      success: false,
      completedPhases,
      outputs: {},
      duration,
      error: (error as Error).message,
    };
  } finally {
    isRunning = false;
    currentPhase = 0;
  }
}

/**
 * Rollback result from Python
 */
interface RollbackResult {
  success: boolean;
  restored_files?: string[];
  deleted_files?: string[];
  errors?: string[];
  error?: string;
}

/**
 * Stop the running pipeline immediately with full cleanup and rollback
 * This force-kills the Python process (like Ctrl+C) and then performs rollback
 */
async function stopPipeline(): Promise<{ success: boolean; rollback?: RollbackResult }> {
  shouldStop = true;
  const stoppedPhase = currentPhase;
  console.log('[Pipeline] Immediate stop requested for phase:', stoppedPhase);

  const bridge = getPythonBridge();
  
  try {
    // Step 1: Force kill the Python process immediately (like Ctrl+C)
    console.log('[Pipeline] Force killing Python process...');
    bridge.forceStop();
    
    // Step 2: Wait a moment for the process to fully terminate
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Step 3: Restart the bridge for rollback operation
    console.log('[Pipeline] Restarting bridge for rollback...');
    await bridge.start();
    
    // Step 4: Perform rollback via the new Python process
    console.log('[Pipeline] Performing rollback...');
    const response = await bridge.execute({ action: 'rollback' }, 10000);
    
    const rollbackResult = response.rollback as RollbackResult | undefined;
    
    if (rollbackResult) {
      console.log('[Pipeline] Rollback completed:', {
        restored: rollbackResult.restored_files?.length ?? 0,
        deleted: rollbackResult.deleted_files?.length ?? 0,
        errors: rollbackResult.errors?.length ?? 0,
      });
    }
    
    // Send progress update to indicate stopped state (reset to pending)
    if (stoppedPhase > 0) {
      sendProgressUpdate({
        phase: stoppedPhase,
        phaseName: getPhaseNameById(stoppedPhase),
        status: 'pending',
        progress: 0,
      });
    }
    
    return { 
      success: true, 
      rollback: rollbackResult 
    };
  } catch (error) {
    console.error('[Pipeline] Failed during stop/rollback:', error);
    
    // Even if rollback fails, we've stopped the process
    // Send pending status to reset UI
    if (stoppedPhase > 0) {
      sendProgressUpdate({
        phase: stoppedPhase,
        phaseName: getPhaseNameById(stoppedPhase),
        status: 'pending',
        progress: 0,
      });
    }
    
    return { success: true }; // Process was stopped even if rollback failed
  } finally {
    isRunning = false;
    currentPhase = 0;
    shouldStop = false;
    // Clear phase context
    bridge.setPhaseContext(null, null);
  }
}

/**
 * Validate a dataset file
 */
async function validateDataset(datasetPath: string): Promise<DatasetValidation> {
  const bridge = getPythonBridge();
  
  try {
    const response = await bridge.execute({
      action: 'validate_dataset',
      path: datasetPath,
    }, 30000); // 30 second timeout for validation

    if (!response.success) {
      return {
        valid: false,
        rowCount: 0,
        columns: [],
        missingColumns: [],
        error: response.error as string || 'Validation failed',
      };
    }

    return {
      valid: response.valid as boolean,
      rowCount: response.rowCount as number,
      columns: response.columns as string[],
      missingColumns: response.missingColumns as string[],
      preview: response.preview as Record<string, unknown>[],
      alreadyProcessed: response.alreadyProcessed as boolean,
    };
  } catch (error) {
    return {
      valid: false,
      rowCount: 0,
      columns: [],
      missingColumns: [],
      error: (error as Error).message,
    };
  }
}

/**
 * Get LLM configuration info from Python
 */
async function getLLMInfo(): Promise<{ success: boolean; [key: string]: unknown }> {
  const bridge = getPythonBridge();
  
  try {
    const response = await bridge.execute({ action: 'get_llm_info' }, 10000);
    return response;
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message,
    };
  }
}

export function registerPipelineHandlers(): void {
  ipcMain.handle('pipeline:run-phase', async (_, phase: number, config?: object) => {
    return runPhase(phase, config);
  });

  ipcMain.handle('pipeline:run-all', async (_, config?: PipelineConfig) => {
    return runAllPhases(config);
  });

  ipcMain.handle('pipeline:stop', async () => {
    return stopPipeline();
  });

  ipcMain.handle('pipeline:get-status', async () => {
    return getPipelineStatus();
  });

  ipcMain.handle('pipeline:validate-dataset', async (_, path: string) => {
    return validateDataset(path);
  });

  ipcMain.handle('pipeline:validate-phase', async (_, phase: number, datasetPath?: string) => {
    const bridge = getPythonBridge();
    try {
      return await bridge.execute({
        action: 'validate_phase_dependencies',
        phase,
        dataset_path: datasetPath || 'data/dataset.csv',
      }, 10000);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  });

  ipcMain.handle('pipeline:get-llm-info', async () => {
    return getLLMInfo();
  });

  console.log('[IPC] Pipeline handlers registered');
}

// ============================================
// Pipeline IPC Handlers
// ============================================

import { ipcMain, BrowserWindow } from 'electron';
import type { PipelineProgress, PipelineResult, PipelineConfig } from '../../shared/types';

// Pipeline state management
let isRunning = false;
let shouldStop = false;
let currentPhase = 0;

/**
 * Get the current pipeline status
 */
function getPipelineStatus(): PipelineProgress {
  return {
    phase: currentPhase,
    phaseName: getPhaseNameById(currentPhase),
    status: isRunning ? 'running' : 'pending',
    progress: 0,
  };
}

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
    win.webContents.send('pipeline:progress', progress);
  });
}

/**
 * Run a single pipeline phase
 * Note: This is a placeholder implementation. Full Python integration will be in Phase 2.
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

  try {
    sendProgressUpdate({
      phase,
      phaseName: getPhaseNameById(phase),
      status: 'running',
      progress: 0,
      message: `Starting phase ${phase}...`,
    });

    // Placeholder: Simulate phase execution
    // In Phase 2, this will call the Python bridge
    await new Promise(resolve => setTimeout(resolve, 100));

    if (shouldStop) {
      throw new Error('Pipeline stopped by user');
    }

    sendProgressUpdate({
      phase,
      phaseName: getPhaseNameById(phase),
      status: 'completed',
      progress: 100,
      message: `Phase ${phase} completed`,
    });

    const duration = Date.now() - startTime;
    return {
      success: true,
      completedPhases: [phase],
      outputs: {},
      duration,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    sendProgressUpdate({
      phase,
      phaseName: getPhaseNameById(phase),
      status: 'failed',
      progress: 0,
      error: (error as Error).message,
    });

    return {
      success: false,
      completedPhases: [],
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
 * Run all enabled pipeline phases
 * Note: This is a placeholder implementation. Full Python integration will be in Phase 2.
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

  try {
    // Get enabled phases from config or default to all
    const phases = config?.phases || {
      phase01: { enabled: true },
      phase02: { enabled: true },
      phase03: { enabled: true },
      phase04: { enabled: true },
      phase05: { enabled: true },
      phase06: { enabled: true },
      phase07: { enabled: true },
    };

    const phaseEntries = Object.entries(phases);
    
    for (let i = 0; i < phaseEntries.length; i++) {
      const [key, phaseConfig] = phaseEntries[i];
      const phaseNumber = parseInt(key.replace('phase', '').replace('0', ''), 10);

      if (shouldStop) {
        throw new Error('Pipeline stopped by user');
      }

      if (!phaseConfig.enabled) {
        sendProgressUpdate({
          phase: phaseNumber,
          phaseName: getPhaseNameById(phaseNumber),
          status: 'pending',
          progress: 0,
          message: `Phase ${phaseNumber} skipped (disabled)`,
        });
        continue;
      }

      currentPhase = phaseNumber;
      sendProgressUpdate({
        phase: phaseNumber,
        phaseName: getPhaseNameById(phaseNumber),
        status: 'running',
        progress: 0,
        message: `Running phase ${phaseNumber}...`,
      });

      // Placeholder: Simulate phase execution
      // In Phase 2, this will call the Python bridge
      await new Promise(resolve => setTimeout(resolve, 100));

      completedPhases.push(phaseNumber);
      sendProgressUpdate({
        phase: phaseNumber,
        phaseName: getPhaseNameById(phaseNumber),
        status: 'completed',
        progress: 100,
        message: `Phase ${phaseNumber} completed`,
      });
    }

    const duration = Date.now() - startTime;
    return {
      success: true,
      completedPhases,
      outputs: {},
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
 * Stop the running pipeline
 */
function stopPipeline(): void {
  if (isRunning) {
    shouldStop = true;
    console.log('[Pipeline] Stop requested');
  }
}

export function registerPipelineHandlers(): void {
  ipcMain.handle('pipeline:run-phase', async (_, phase: number, config?: object) => {
    return runPhase(phase, config);
  });

  ipcMain.handle('pipeline:run-all', async (_, config?: PipelineConfig) => {
    return runAllPhases(config);
  });

  ipcMain.handle('pipeline:stop', () => {
    stopPipeline();
    return { success: true };
  });

  ipcMain.handle('pipeline:get-status', () => {
    return getPipelineStatus();
  });

  console.log('[IPC] Pipeline handlers registered');
}

/**
 * usePipeline Hook
 * =================
 * Custom hook for pipeline operations
 */

import { useEffect, useCallback } from 'react';
import { usePipelineStore } from '../stores/pipelineStore';
import { useDataStore } from '../stores/dataStore';
import type { PipelineProgress, PipelineResult, PipelineTimingRecord } from '../../shared/types';

export function usePipeline() {
  const {
    isRunning,
    currentPhase,
    phases,
    config,
    pipelineStartedAt,
    pipelineCompletedAt,
    pipelineDuration,
    lastTimingRecord,
    setRunning,
    setCurrentPhase,
    updatePhaseProgress,
    setConfig,
    setPhaseEnabled,
    setDataset,
    setPipelineTiming,
    setLastTimingRecord,
    reset,
  } = usePipelineStore();

  // Listen for progress updates from main process
  useEffect(() => {
    const handleProgress = (_: unknown, data: PipelineProgress) => {
      // Check if phase is in cancelling state - if so, don't override
      const currentState = usePipelineStore.getState();
      const phaseState = currentState.phases[data.phase];
      if (phaseState?.status === 'cancelling') {
        // Don't update progress if phase is being cancelled
        return;
      }
      
      // Don't allow 'running' status to overwrite 'completed' status
      // This prevents late-arriving stderr tqdm data from reverting a completed phase
      if (phaseState?.status === 'completed' && data.status !== 'completed' && data.status !== 'failed') {
        return;
      }
      
      // Map the status properly
      let status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelling' = 'running';
      if (data.status === 'failed') {
        status = 'failed';
      } else if (data.status === 'completed') {
        status = 'completed';
      } else if (data.status === 'pending') {
        status = 'pending';
      } else if (data.status === 'cancelling') {
        status = 'cancelling';
      }
      
      updatePhaseProgress(data.phase, {
        status,
        progress: data.progress,
        message: status === 'pending' ? undefined : data.message,
        error: data.error,
      });

      // Update current phase if running
      if (data.status === 'running') {
        setCurrentPhase(data.phase);
      }
      
      // Clear current phase if stopped/pending
      if (data.status === 'pending') {
        setCurrentPhase(null);
      }
    };

    window.electronAPI.pipeline.onProgress(handleProgress);

    return () => {
      window.electronAPI.pipeline.offProgress();
    };
  }, [updatePhaseProgress, setCurrentPhase]);

  const runPhase = useCallback(
    async (phase: number, skipValidation = false): Promise<PipelineResult> => {
      // Check if another phase is already running
      const currentState = usePipelineStore.getState();
      if (currentState.isRunning) {
        return {
          success: false,
          completedPhases: [],
          outputs: {},
          duration: 0,
          error: 'Ya hay una fase en ejecución. Espera a que termine antes de iniciar otra.',
        };
      }

      // Validate phase dependencies before running (unless explicitly skipped)
      if (!skipValidation && phase > 1) {
        try {
          const validation = await window.electronAPI.pipeline.validatePhase(phase);
          if (!validation.canRun) {
            // Return error result with validation info
            return {
              success: false,
              completedPhases: [],
              outputs: {},
              duration: 0,
              error: validation.error || 'Phase dependencies not met',
              validation, // Include validation details
            };
          }
        } catch (error) {
          console.error('Validation error:', error);
          // Continue with phase execution if validation fails
        }
      }

      setRunning(true);
      setCurrentPhase(phase);
      const phaseStartedAt = new Date().toISOString();
      updatePhaseProgress(phase, { status: 'running', progress: 0, startedAt: phaseStartedAt, completedAt: undefined, duration: undefined });

      try {
        const result = await window.electronAPI.pipeline.runPhase(phase, config);

        // Check if phase was cancelled while we were waiting
        const currentState = usePipelineStore.getState();
        const phaseState = currentState.phases[phase];
        if (phaseState?.status === 'cancelling') {
          // Phase was cancelled, don't update status
          return result;
        }

        // Check if this was a stop (not a real error)
        if (result.error === 'stopped') {
          // Don't update status here - the stop handler will do it
          return result;
        }

        const phaseCompletedAt = new Date().toISOString();
        const phaseDuration = new Date(phaseCompletedAt).getTime() - new Date(phaseStartedAt).getTime();

        updatePhaseProgress(phase, {
          status: result.success ? 'completed' : 'failed',
          progress: result.success ? 100 : 0,
          error: result.error,
          startedAt: phaseStartedAt,
          completedAt: phaseCompletedAt,
          duration: phaseDuration,
        });

        // Save lastAnalysisDate when any phase completes successfully
        if (result.success) {
          try {
            await window.electronAPI.settings.set('lastAnalysisDate', phaseCompletedAt);
          } catch (e) {
            console.error('Failed to save lastAnalysisDate:', e);
          }
        }

        // Update output paths if phase completed successfully and returned outputs
        if (result.success && result.outputs) {
          const outputs = result.outputs as { chartsPath?: string; summaryPath?: string; datasetPath?: string };
          if (outputs.chartsPath || outputs.summaryPath) {
            useDataStore.getState().setOutputPaths({
              charts: outputs.chartsPath,
              summary: outputs.summaryPath,
              output: outputs.datasetPath,
            });
          }
        }

        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        
        // Check if phase is in cancelling state - if so, don't override with error
        const currentState = usePipelineStore.getState();
        const phaseState = currentState.phases[phase];
        
        // Only update to failed if not currently cancelling
        if (phaseState?.status !== 'cancelling') {
          updatePhaseProgress(phase, {
            status: 'failed',
            progress: 0,
            error: errorMessage,
          });
        }
        
        return {
          success: false,
          completedPhases: [],
          outputs: {},
          duration: 0,
          error: errorMessage,
        };
      } finally {
        setRunning(false);
        setCurrentPhase(null);
      }
    },
    [config, setRunning, setCurrentPhase, updatePhaseProgress]
  );

  const runAll = useCallback(async (): Promise<PipelineResult> => {
    setRunning(true);
    reset();

    const completedPhases: number[] = [];
    const startTime = Date.now();
    const pipelineStart = new Date().toISOString();
    setPipelineTiming({ startedAt: pipelineStart, completedAt: null, duration: null });

    try {
      // Execute phases sequentially in order (1-9)
      for (let phaseNum = 1; phaseNum <= 9; phaseNum++) {
        // Check if phase is enabled
        const phaseKey = `phase_${String(phaseNum).padStart(2, '0')}` as keyof typeof config.phases;
        if (!config.phases[phaseKey]) {
          continue;
        }

        // Run this phase and wait for it to complete
        // Skip validation since we already checked if the phase is enabled
        const result = await runPhase(phaseNum, true);
        
        // Check if stopped by user - exit gracefully without error
        if (result.error === 'stopped') {
          const pipelineEnd = new Date().toISOString();
          setPipelineTiming({ completedAt: pipelineEnd, duration: Date.now() - startTime });
          return {
            success: false,
            completedPhases,
            outputs: {},
            duration: Date.now() - startTime,
            error: 'stopped',
          };
        }
        
        if (result.success) {
          completedPhases.push(phaseNum);
        } else {
          // Stop if a phase fails
          throw new Error(result.error || `Phase ${phaseNum} failed`);
        }
      }

      const duration = Date.now() - startTime;
      const pipelineEnd = new Date().toISOString();
      setPipelineTiming({ completedAt: pipelineEnd, duration });

      // Build and save timing record from completed phase data
      const currentState = usePipelineStore.getState();
      const timingRecord: PipelineTimingRecord = {
        startedAt: pipelineStart,
        completedAt: pipelineEnd,
        duration,
        phases: {},
      };
      for (const [phaseKey, phaseData] of Object.entries(currentState.phases)) {
        if (phaseData.startedAt && phaseData.completedAt && phaseData.duration !== undefined) {
          timingRecord.phases[Number(phaseKey)] = {
            phaseName: phaseData.phaseName,
            startedAt: phaseData.startedAt,
            completedAt: phaseData.completedAt,
            duration: phaseData.duration,
            status: phaseData.status === 'completed' ? 'completed' : 'failed',
          };
        }
      }
      setLastTimingRecord(timingRecord);

      return {
        success: true,
        completedPhases,
        outputs: {},
        duration,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const pipelineEnd = new Date().toISOString();
      setPipelineTiming({ completedAt: pipelineEnd, duration: Date.now() - startTime });
      return {
        success: false,
        completedPhases,
        outputs: {},
        duration: Date.now() - startTime,
        error: errorMessage,
      };
    } finally {
      setRunning(false);
      setCurrentPhase(null);
    }
  }, [config, setRunning, setCurrentPhase, reset, runPhase, setPipelineTiming, setLastTimingRecord]);

  const stop = useCallback(async (): Promise<{ success: boolean; rolledBack: boolean }> => {
    // Get current phase from store directly (not from stale closure)
    const storeState = usePipelineStore.getState();
    const activePhase = storeState.currentPhase;
    
    // Immediately set the phase to "cancelling" state to show proper UI feedback
    if (activePhase) {
      updatePhaseProgress(activePhase, {
        status: 'cancelling',
        message: 'Cancelando fase...',
        error: undefined,
      });
    }
    
    try {
      const result = await window.electronAPI.pipeline.stop();
      
      // Reset progress for the phase that was stopped
      if (activePhase) {
        updatePhaseProgress(activePhase, {
          status: 'pending',
          progress: 0,
          message: undefined,
          error: undefined,
        });
      }
      
      // Check if rollback was performed
      const rolledBack = !!(result as { rollback?: unknown }).rollback;
      
      return { success: true, rolledBack };
    } catch {
      // Even if stop fails, reset the phase to pending (not failed)
      if (activePhase) {
        updatePhaseProgress(activePhase, {
          status: 'pending',
          progress: 0,
          message: undefined,
          error: undefined,
        });
      }
      return { success: false, rolledBack: false };
    } finally {
      setRunning(false);
      setCurrentPhase(null);
    }
  }, [setRunning, setCurrentPhase, updatePhaseProgress]);

  const validateDataset = useCallback(async (path: string) => {
    const result = await window.electronAPI.pipeline.validateDataset(path);
    return result;
  }, []);

  // Calculate overall progress
  const overallProgress = Object.values(phases).reduce(
    (acc, phase) => acc + phase.progress,
    0
  ) / 7;

  // Count completed phases
  const completedCount = Object.values(phases).filter(
    (p) => p.status === 'completed'
  ).length;

  return {
    // State
    isRunning,
    currentPhase,
    phases,
    config,
    overallProgress,
    completedCount,
    pipelineStartedAt,
    pipelineCompletedAt,
    pipelineDuration,
    lastTimingRecord,

    // Actions
    runPhase,
    runAll,
    stop,
    validateDataset,
    setConfig,
    setPhaseEnabled,
    setDataset,
    reset,
  };
}

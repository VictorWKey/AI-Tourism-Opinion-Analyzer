/**
 * usePipeline Hook
 * =================
 * Custom hook for pipeline operations
 */

import { useEffect, useCallback } from 'react';
import { usePipelineStore } from '../stores/pipelineStore';
import type { PipelineProgress, PipelineResult } from '../../shared/types';

export function usePipeline() {
  const {
    isRunning,
    currentPhase,
    phases,
    config,
    setRunning,
    setCurrentPhase,
    updatePhaseProgress,
    setConfig,
    setPhaseEnabled,
    setDataset,
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
    async (phase: number): Promise<PipelineResult> => {
      setRunning(true);
      setCurrentPhase(phase);
      updatePhaseProgress(phase, { status: 'running', progress: 0 });

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

        updatePhaseProgress(phase, {
          status: result.success ? 'completed' : 'failed',
          progress: result.success ? 100 : 0,
          error: result.error,
        });

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

    try {
      // Execute phases sequentially in order (1-7)
      for (let phaseNum = 1; phaseNum <= 7; phaseNum++) {
        // Check if phase is enabled
        const phaseKey = `phase_${String(phaseNum).padStart(2, '0')}` as keyof typeof config.phases;
        if (!config.phases[phaseKey]) {
          continue;
        }

        // Run this phase and wait for it to complete
        const result = await runPhase(phaseNum);
        
        // Check if stopped by user - exit gracefully without error
        if (result.error === 'stopped') {
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
      return {
        success: true,
        completedPhases,
        outputs: {},
        duration,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
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
  }, [config, setRunning, setCurrentPhase, reset, runPhase]);

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

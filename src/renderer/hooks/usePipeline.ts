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
      updatePhaseProgress(data.phase, {
        status: data.status === 'failed' ? 'failed' : 'running',
        progress: data.progress,
        message: data.message,
        error: data.error,
      });

      // Update current phase if running
      if (data.status === 'running') {
        setCurrentPhase(data.phase);
      }

      // Mark as completed if finished
      if (data.status === 'completed') {
        updatePhaseProgress(data.phase, {
          status: 'completed',
          progress: 100,
        });
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

        updatePhaseProgress(phase, {
          status: result.success ? 'completed' : 'failed',
          progress: result.success ? 100 : 0,
          error: result.error,
        });

        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        updatePhaseProgress(phase, {
          status: 'failed',
          progress: 0,
          error: errorMessage,
        });
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

    try {
      const result = await window.electronAPI.pipeline.runAll(config);

      // Update all phases based on result
      result.completedPhases.forEach((phase) => {
        updatePhaseProgress(phase, {
          status: 'completed',
          progress: 100,
        });
      });

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
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
  }, [config, setRunning, setCurrentPhase, reset, updatePhaseProgress]);

  const stop = useCallback(async () => {
    try {
      await window.electronAPI.pipeline.stop();
    } finally {
      setRunning(false);
      setCurrentPhase(null);
    }
  }, [setRunning, setCurrentPhase]);

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

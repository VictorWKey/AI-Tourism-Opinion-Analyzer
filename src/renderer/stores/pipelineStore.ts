/**
 * Pipeline Store
 * ===============
 * Zustand store for pipeline state management
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { electronStorage } from '../lib/electronStorage';
import type { PipelineProgress, PipelineTimingRecord } from '../../shared/types';

export interface PhaseConfig {
  enabled: boolean;
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
    phase_08: boolean;
    phase_09: boolean;
  };
  dataset?: string;
  outputDir?: string;
}

// Type for phase status including cancelling
export type PhaseStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelling';

interface PipelineState {
  // Status
  isRunning: boolean;
  currentPhase: number | null;

  // Progress
  phases: Record<number, PipelineProgress>;

  // Configuration
  config: PipelineConfig;

  // Pipeline-level timing
  pipelineStartedAt: string | null;
  pipelineCompletedAt: string | null;
  pipelineDuration: number | null;

  // Last timing record (persisted)
  lastTimingRecord: PipelineTimingRecord | null;

  // Actions
  setRunning: (running: boolean) => void;
  setCurrentPhase: (phase: number | null) => void;
  updatePhaseProgress: (phase: number, progress: Partial<PipelineProgress>) => void;
  setConfig: (config: Partial<PipelineConfig>) => void;
  setPhaseEnabled: (phase: number, enabled: boolean) => void;
  setDataset: (path: string | undefined) => void;
  setPipelineTiming: (timing: { startedAt?: string | null; completedAt?: string | null; duration?: number | null }) => void;
  setLastTimingRecord: (record: PipelineTimingRecord | null) => void;
  reset: () => void;
}

const initialPhases: Record<number, PipelineProgress> = {
  1: { phase: 1, phaseName: 'Procesamiento Básico', status: 'pending', progress: 0 },
  2: { phase: 2, phaseName: 'Estadísticas Básicas', status: 'pending', progress: 0 },
  3: { phase: 3, phaseName: 'Análisis de Sentimientos', status: 'pending', progress: 0 },
  4: { phase: 4, phaseName: 'Análisis de Subjetividad', status: 'pending', progress: 0 },
  5: { phase: 5, phaseName: 'Clasificación de Categorías', status: 'pending', progress: 0 },
  6: { phase: 6, phaseName: 'Análisis de Tópicos', status: 'pending', progress: 0 },
  7: { phase: 7, phaseName: 'Resumen Inteligente', status: 'pending', progress: 0 },
  8: { phase: 8, phaseName: 'Insights Estratégicos', status: 'pending', progress: 0 },
  9: { phase: 9, phaseName: 'Visualizaciones y Metricas', status: 'pending', progress: 0 },
};

const initialConfig: PipelineConfig = {
  phases: {
    phase_01: true,
    phase_02: true,
    phase_03: true,
    phase_04: true,
    phase_05: true,
    phase_06: true,
    phase_07: true,
    phase_08: true,
    phase_09: true,
  },
};

export const usePipelineStore = create<PipelineState>()(
  persist(
    (set) => ({
      isRunning: false,
      currentPhase: null,
      phases: { ...initialPhases },
      config: { ...initialConfig },
      pipelineStartedAt: null,
      pipelineCompletedAt: null,
      pipelineDuration: null,
      lastTimingRecord: null,

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

      setPhaseEnabled: (phase, enabled) =>
        set((state) => ({
          config: {
            ...state.config,
            phases: {
              ...state.config.phases,
              [`phase_0${phase}`]: enabled,
            },
          },
        })),

      setDataset: (path) =>
        set((state) => ({
          config: { ...state.config, dataset: path },
        })),

      setPipelineTiming: (timing) =>
        set((state) => ({
          pipelineStartedAt: timing.startedAt !== undefined ? timing.startedAt : state.pipelineStartedAt,
          pipelineCompletedAt: timing.completedAt !== undefined ? timing.completedAt : state.pipelineCompletedAt,
          pipelineDuration: timing.duration !== undefined ? timing.duration : state.pipelineDuration,
        })),

      setLastTimingRecord: (record) =>
        set({ lastTimingRecord: record }),

      reset: () =>
        set({
          isRunning: false,
          currentPhase: null,
          phases: { ...initialPhases },
        }),
    }),
    {
      name: 'pipeline-storage',
      storage: createJSONStorage(() => electronStorage),
      // Only persist config, phases, and timing data
      partialize: (state) => ({
        config: state.config,
        phases: state.phases,
        pipelineStartedAt: state.pipelineStartedAt,
        pipelineCompletedAt: state.pipelineCompletedAt,
        pipelineDuration: state.pipelineDuration,
        lastTimingRecord: state.lastTimingRecord,
      }),
      // Migrate old state to ensure all phases exist
      onRehydrateStorage: () => (state) => {
        if (state) {
          // Ensure all 9 phases exist (migration for users upgrading from 8 phases)
          const missingPhases: Record<number, PipelineProgress> = {};
          for (let i = 1; i <= 9; i++) {
            if (!state.phases[i]) {
              missingPhases[i] = initialPhases[i];
            }
          }
          if (Object.keys(missingPhases).length > 0) {
            state.phases = { ...state.phases, ...missingPhases };
          }

          // Ensure all phase config entries exist
          const missingPhaseConfigs: Partial<PipelineConfig['phases']> = {};
          for (let i = 1; i <= 9; i++) {
            const key = `phase_0${i}` as keyof PipelineConfig['phases'];
            if (state.config.phases[key] === undefined) {
              missingPhaseConfigs[key] = true;
            }
          }
          if (Object.keys(missingPhaseConfigs).length > 0) {
            state.config = {
              ...state.config,
              phases: { ...state.config.phases, ...missingPhaseConfigs },
            };
          }
        }
      },
    }
  )
);

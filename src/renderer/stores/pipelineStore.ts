/**
 * Pipeline Store
 * ===============
 * Zustand store for pipeline state management
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { electronStorage } from '../lib/electronStorage';
import type { PipelineProgress } from '../../shared/types';

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

  // Actions
  setRunning: (running: boolean) => void;
  setCurrentPhase: (phase: number | null) => void;
  updatePhaseProgress: (phase: number, progress: Partial<PipelineProgress>) => void;
  setConfig: (config: Partial<PipelineConfig>) => void;
  setPhaseEnabled: (phase: number, enabled: boolean) => void;
  setDataset: (path: string | undefined) => void;
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

const initialConfig: PipelineConfig = {
  phases: {
    phase_01: true,
    phase_02: true,
    phase_03: true,
    phase_04: true,
    phase_05: true,
    phase_06: true,
    phase_07: true,
  },
};

export const usePipelineStore = create<PipelineState>()(
  persist(
    (set) => ({
      isRunning: false,
      currentPhase: null,
      phases: { ...initialPhases },
      config: { ...initialConfig },

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
      // Only persist config and completed phases
      partialize: (state) => ({
        config: state.config,
        phases: state.phases,
      }),
    }
  )
);

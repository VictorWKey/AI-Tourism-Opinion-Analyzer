/**
 * Data Store
 * ===========
 * Zustand store for dataset state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { DatasetInfo, DatasetValidation } from '../../shared/types';

interface DataState {
  // Current dataset
  dataset: DatasetInfo | null;
  
  // Validation state
  isValidating: boolean;
  validationResult: DatasetValidation | null;
  
  // Preview data
  previewData: Record<string, unknown>[] | null;
  
  // Results paths
  outputPath: string | null;
  chartsPath: string | null;
  summaryPath: string | null;

  // Actions
  setDataset: (dataset: DatasetInfo | null) => void;
  setValidating: (validating: boolean) => void;
  setValidationResult: (result: DatasetValidation | null) => void;
  setPreviewData: (data: Record<string, unknown>[] | null) => void;
  setOutputPaths: (paths: { output?: string; charts?: string; summary?: string }) => void;
  clearDataset: () => void;
  reset: () => void;
}

export const useDataStore = create<DataState>()(
  persist(
    (set) => ({
      dataset: null,
      isValidating: false,
      validationResult: null,
      previewData: null,
      outputPath: null,
      chartsPath: null,
      summaryPath: null,

      setDataset: (dataset) => set({ dataset }),

      setValidating: (isValidating) => set({ isValidating }),

      setValidationResult: (validationResult) => set({ validationResult }),

      setPreviewData: (previewData) => set({ previewData }),

      setOutputPaths: (paths) =>
        set((state) => ({
          outputPath: paths.output ?? state.outputPath,
          chartsPath: paths.charts ?? state.chartsPath,
          summaryPath: paths.summary ?? state.summaryPath,
        })),

      clearDataset: () =>
        set({
          dataset: null,
          validationResult: null,
          previewData: null,
        }),

      reset: () =>
        set({
          dataset: null,
          isValidating: false,
          validationResult: null,
          previewData: null,
          outputPath: null,
          chartsPath: null,
          summaryPath: null,
        }),
    }),
    {
      name: 'data-storage',
      // Persist dataset info and preview so they survive app restarts
      partialize: (state) => ({
        dataset: state.dataset,
        validationResult: state.validationResult,
        previewData: state.previewData,
        outputPath: state.outputPath,
        chartsPath: state.chartsPath,
        summaryPath: state.summaryPath,
      }),
    }
  )
);

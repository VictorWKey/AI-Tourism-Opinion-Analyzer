/**
 * Settings Store
 * ===============
 * Zustand store for application settings management
 */

import { create } from 'zustand';
import type { LLMConfig, AppSettings } from '../../shared/types';

interface SettingsState {
  // LLM Settings
  llm: LLMConfig;
  
  // App Settings
  language: string;
  outputDir: string;
  
  // Loading states
  isLoading: boolean;
  isSaving: boolean;

  // Actions
  setLLMConfig: (config: Partial<LLMConfig>) => void;
  setLanguage: (language: string) => void;
  setOutputDir: (dir: string) => void;
  setLoading: (loading: boolean) => void;
  setSaving: (saving: boolean) => void;
  loadSettings: (settings: AppSettings) => void;
  reset: () => void;
}

const defaultLLMConfig: LLMConfig = {
  mode: 'local',
  localModel: 'llama3.2',
  apiProvider: 'openai',
  apiKey: undefined,
  apiModel: 'gpt-4o-mini',
  temperature: 0.7,
};

export const useSettingsStore = create<SettingsState>((set) => ({
  llm: { ...defaultLLMConfig },
  language: 'es',
  outputDir: '',
  isLoading: false,
  isSaving: false,

  setLLMConfig: (config) =>
    set((state) => ({
      llm: { ...state.llm, ...config },
    })),

  setLanguage: (language) => set({ language }),

  setOutputDir: (outputDir) => set({ outputDir }),

  setLoading: (isLoading) => set({ isLoading }),

  setSaving: (isSaving) => set({ isSaving }),

  loadSettings: (settings) =>
    set({
      llm: settings.llm,
      language: settings.app.language,
      outputDir: settings.app.outputDir,
    }),

  reset: () =>
    set({
      llm: { ...defaultLLMConfig },
      language: 'es',
      outputDir: '',
      isLoading: false,
      isSaving: false,
    }),
}));

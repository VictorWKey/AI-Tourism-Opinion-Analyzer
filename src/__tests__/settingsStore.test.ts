import { describe, it, expect, beforeEach, vi } from 'vitest';

// i18next is not initialized in the test environment — mock changeLanguage
vi.mock('i18next', () => ({
  default: { changeLanguage: vi.fn() },
}));

import { useSettingsStore } from '../renderer/stores/settingsStore';

describe('Settings Store', () => {
  beforeEach(() => {
    // Reset store to defaults before each test
    useSettingsStore.getState().reset();
  });

  it('should have correct default values', () => {
    const state = useSettingsStore.getState();
    expect(state.llm.mode).toBe('local');
    expect(state.llm.localModel).toBe('llama3.2:3b');
    expect(state.llm.apiProvider).toBe('openai');
    expect(state.llm.apiModel).toBe('gpt-4o-mini');
    expect(state.llm.temperature).toBe(0);
    expect(state.language).toBe('es');
    expect(state.outputDir).toBe('');
    expect(state.isLoading).toBe(false);
    expect(state.isSaving).toBe(false);
  });

  it('should update LLM config partially', () => {
    useSettingsStore.getState().setLLMConfig({ mode: 'api', temperature: 0.7 });
    const state = useSettingsStore.getState();
    expect(state.llm.mode).toBe('api');
    expect(state.llm.temperature).toBe(0.7);
    // Other fields should remain unchanged
    expect(state.llm.localModel).toBe('llama3.2:3b');
    expect(state.llm.apiProvider).toBe('openai');
  });

  it('should update language', () => {
    useSettingsStore.getState().setLanguage('en');
    expect(useSettingsStore.getState().language).toBe('en');
  });

  it('should update output directory', () => {
    useSettingsStore.getState().setOutputDir('C:\\Users\\test\\output');
    expect(useSettingsStore.getState().outputDir).toBe('C:\\Users\\test\\output');
  });

  it('should set loading state', () => {
    useSettingsStore.getState().setLoading(true);
    expect(useSettingsStore.getState().isLoading).toBe(true);

    useSettingsStore.getState().setLoading(false);
    expect(useSettingsStore.getState().isLoading).toBe(false);
  });

  it('should set saving state', () => {
    useSettingsStore.getState().setSaving(true);
    expect(useSettingsStore.getState().isSaving).toBe(true);
  });

  it('should load full settings object', () => {
    useSettingsStore.getState().loadSettings({
      llm: {
        mode: 'api',
        localModel: 'llama3.2:3b',
        apiProvider: 'openai',
        apiKey: 'sk-test',
        apiModel: 'gpt-4',
        temperature: 0.5,
      },
      app: {
        theme: 'dark',
        language: 'en',
        outputDir: '/tmp/output',
      },
    });

    const state = useSettingsStore.getState();
    expect(state.llm.mode).toBe('api');
    expect(state.llm.apiKey).toBe('sk-test');
    expect(state.llm.apiModel).toBe('gpt-4');
    expect(state.language).toBe('en');
    expect(state.outputDir).toBe('/tmp/output');
  });

  it('should reset to defaults', () => {
    // Modify everything
    useSettingsStore.getState().setLLMConfig({ mode: 'api', temperature: 0.9 });
    useSettingsStore.getState().setLanguage('en');
    useSettingsStore.getState().setOutputDir('/some/path');
    useSettingsStore.getState().setLoading(true);
    useSettingsStore.getState().setSaving(true);

    // Reset
    useSettingsStore.getState().reset();

    const state = useSettingsStore.getState();
    expect(state.llm.mode).toBe('local');
    expect(state.llm.temperature).toBe(0);
    expect(state.language).toBe('es');
    expect(state.outputDir).toBe('');
    expect(state.isLoading).toBe(false);
    expect(state.isSaving).toBe(false);
  });
});

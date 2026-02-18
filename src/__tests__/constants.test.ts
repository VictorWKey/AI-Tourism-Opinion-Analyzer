import { describe, it, expect } from 'vitest';
import {
  PIPELINE_PHASES,
  APP_NAME,
  DEFAULT_LLM_CONFIG,
  SUPPORTED_FILE_EXTENSIONS,
} from '../shared/constants';

describe('Constants', () => {
  it('should have 9 pipeline phases', () => {
    expect(PIPELINE_PHASES).toHaveLength(9);
  });

  it('should have correct phase IDs in order', () => {
    const ids = PIPELINE_PHASES.map((p) => p.id);
    expect(ids).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
  });

  it('should mark phases 6, 7, and 8 as requiring LLM', () => {
    const llmPhases = PIPELINE_PHASES.filter((p) => p.requiresLLM);
    expect(llmPhases.map((p) => p.id)).toEqual([6, 7, 8]);
  });

  it('should have correct app name', () => {
    expect(APP_NAME).toBe('AI Tourism Opinion Analyzer');
  });

  it('should support CSV and Excel files', () => {
    expect(SUPPORTED_FILE_EXTENSIONS).toContain('.csv');
    expect(SUPPORTED_FILE_EXTENSIONS).toContain('.xlsx');
    expect(SUPPORTED_FILE_EXTENSIONS).toContain('.xls');
  });

  it('should have valid default LLM config', () => {
    expect(DEFAULT_LLM_CONFIG.mode).toBe('local');
    expect(DEFAULT_LLM_CONFIG.temperature).toBeGreaterThan(0);
    expect(DEFAULT_LLM_CONFIG.temperature).toBeLessThanOrEqual(1);
  });
});

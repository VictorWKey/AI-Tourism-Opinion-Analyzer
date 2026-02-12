import { describe, it, expect, beforeEach } from 'vitest';
import { useDataStore } from '../renderer/stores/dataStore';

describe('Data Store', () => {
  beforeEach(() => {
    useDataStore.getState().reset();
  });

  it('should have correct initial state', () => {
    const state = useDataStore.getState();
    expect(state.dataset).toBeNull();
    expect(state.isValidating).toBe(false);
    expect(state.validationResult).toBeNull();
    expect(state.previewData).toBeNull();
    expect(state.outputPath).toBeNull();
    expect(state.chartsPath).toBeNull();
    expect(state.summaryPath).toBeNull();
  });

  it('should set dataset info', () => {
    const dataset = {
      path: '/data/reviews.csv',
      name: 'reviews.csv',
      rows: 1500,
      columns: ['review', 'rating', 'date'],
      validationStatus: 'valid' as const,
      validationMessages: [],
    };

    useDataStore.getState().setDataset(dataset);
    expect(useDataStore.getState().dataset).toEqual(dataset);
  });

  it('should clear dataset back to null', () => {
    useDataStore.getState().setDataset({
      path: '/data/test.csv',
      name: 'test.csv',
      rows: 100,
      columns: ['text'],
      validationStatus: 'valid' as const,
      validationMessages: [],
    });

    useDataStore.getState().setDataset(null);
    expect(useDataStore.getState().dataset).toBeNull();
  });

  it('should set validating state', () => {
    useDataStore.getState().setValidating(true);
    expect(useDataStore.getState().isValidating).toBe(true);

    useDataStore.getState().setValidating(false);
    expect(useDataStore.getState().isValidating).toBe(false);
  });

  it('should set validation result', () => {
    const result = {
      valid: true,
      rowCount: 500,
      columns: ['review_text', 'score'],
      missingColumns: [],
    };

    useDataStore.getState().setValidationResult(result);
    expect(useDataStore.getState().validationResult).toEqual(result);
  });

  it('should set preview data', () => {
    const preview = [
      { review: 'Great hotel!', rating: 5 },
      { review: 'Terrible service', rating: 1 },
    ];

    useDataStore.getState().setPreviewData(preview);
    expect(useDataStore.getState().previewData).toEqual(preview);
    expect(useDataStore.getState().previewData).toHaveLength(2);
  });

  it('should set output paths individually', () => {
    useDataStore.getState().setOutputPaths({ output: '/out/results' });
    expect(useDataStore.getState().outputPath).toBe('/out/results');
    expect(useDataStore.getState().chartsPath).toBeNull();

    useDataStore.getState().setOutputPaths({ charts: '/out/charts' });
    expect(useDataStore.getState().outputPath).toBe('/out/results');
    expect(useDataStore.getState().chartsPath).toBe('/out/charts');
  });

  it('should set multiple output paths at once', () => {
    useDataStore.getState().setOutputPaths({
      output: '/results',
      charts: '/charts',
      summary: '/summary',
    });

    const state = useDataStore.getState();
    expect(state.outputPath).toBe('/results');
    expect(state.chartsPath).toBe('/charts');
    expect(state.summaryPath).toBe('/summary');
  });

  it('should clear dataset without affecting output paths', () => {
    useDataStore.getState().setDataset({
      path: '/data/test.csv',
      name: 'test.csv',
      rows: 100,
      columns: ['text'],
      validationStatus: 'valid' as const,
      validationMessages: [],
    });
    useDataStore.getState().setValidationResult({ valid: true, rowCount: 100, columns: ['text'], missingColumns: [] });
    useDataStore.getState().setPreviewData([{ text: 'hello' }]);
    useDataStore.getState().setOutputPaths({ output: '/out' });

    useDataStore.getState().clearDataset();

    const state = useDataStore.getState();
    expect(state.dataset).toBeNull();
    expect(state.validationResult).toBeNull();
    expect(state.previewData).toBeNull();
    // Output paths are not cleared by clearDataset
    expect(state.outputPath).toBe('/out');
  });

  it('should reset everything to defaults', () => {
    // Set everything
    useDataStore.getState().setDataset({ path: '/a.csv', name: 'a.csv', rows: 1, columns: [], validationStatus: 'valid' as const, validationMessages: [] });
    useDataStore.getState().setValidating(true);
    useDataStore.getState().setValidationResult({ valid: true, rowCount: 1, columns: [], missingColumns: [] });
    useDataStore.getState().setPreviewData([{ a: 1 }]);
    useDataStore.getState().setOutputPaths({ output: '/o', charts: '/c', summary: '/s' });

    // Reset
    useDataStore.getState().reset();

    const state = useDataStore.getState();
    expect(state.dataset).toBeNull();
    expect(state.isValidating).toBe(false);
    expect(state.validationResult).toBeNull();
    expect(state.previewData).toBeNull();
    expect(state.outputPath).toBeNull();
    expect(state.chartsPath).toBeNull();
    expect(state.summaryPath).toBeNull();
  });
});

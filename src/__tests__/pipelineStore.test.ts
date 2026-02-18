import { describe, it, expect, beforeEach } from 'vitest';
import { usePipelineStore } from '../renderer/stores/pipelineStore';

describe('Pipeline Store', () => {
  beforeEach(() => {
    usePipelineStore.getState().reset();
  });

  it('should have correct initial state', () => {
    const state = usePipelineStore.getState();
    expect(state.isRunning).toBe(false);
    expect(state.currentPhase).toBeNull();
    expect(Object.keys(state.phases)).toHaveLength(9);
  });

  it('should have all 9 phases initialized as pending', () => {
    const state = usePipelineStore.getState();
    for (let i = 1; i <= 9; i++) {
      expect(state.phases[i]).toBeDefined();
      expect(state.phases[i].phase).toBe(i);
      expect(state.phases[i].status).toBe('pending');
      expect(state.phases[i].progress).toBe(0);
    }
  });

  it('should have all phases enabled by default', () => {
    const config = usePipelineStore.getState().config;
    for (let i = 1; i <= 9; i++) {
      const key = `phase_0${i}` as keyof typeof config.phases;
      expect(config.phases[key]).toBe(true);
    }
  });

  it('should set running state', () => {
    usePipelineStore.getState().setRunning(true);
    expect(usePipelineStore.getState().isRunning).toBe(true);

    usePipelineStore.getState().setRunning(false);
    expect(usePipelineStore.getState().isRunning).toBe(false);
  });

  it('should set current phase', () => {
    usePipelineStore.getState().setCurrentPhase(3);
    expect(usePipelineStore.getState().currentPhase).toBe(3);

    usePipelineStore.getState().setCurrentPhase(null);
    expect(usePipelineStore.getState().currentPhase).toBeNull();
  });

  it('should update phase progress partially', () => {
    usePipelineStore.getState().updatePhaseProgress(1, { status: 'running', progress: 50, message: 'Processing...' });

    const phase1 = usePipelineStore.getState().phases[1];
    expect(phase1.status).toBe('running');
    expect(phase1.progress).toBe(50);
    expect(phase1.message).toBe('Processing...');
    // Original fields should still exist
    expect(phase1.phase).toBe(1);
    expect(phase1.phaseName).toBe('Procesamiento Básico');
  });

  it('should mark phase as completed', () => {
    usePipelineStore.getState().updatePhaseProgress(2, { status: 'completed', progress: 100 });

    const phase2 = usePipelineStore.getState().phases[2];
    expect(phase2.status).toBe('completed');
    expect(phase2.progress).toBe(100);
  });

  it('should mark phase as failed', () => {
    usePipelineStore.getState().updatePhaseProgress(5, { status: 'failed', error: 'LLM not available' });

    const phase5 = usePipelineStore.getState().phases[5];
    expect(phase5.status).toBe('failed');
    expect(phase5.error).toBe('LLM not available');
  });

  it('should update config partially', () => {
    usePipelineStore.getState().setConfig({ dataset: '/data/reviews.csv' });

    const config = usePipelineStore.getState().config;
    expect(config.dataset).toBe('/data/reviews.csv');
    // Phases should be untouched
    expect(config.phases.phase_01).toBe(true);
  });

  it('should enable/disable individual phases', () => {
    usePipelineStore.getState().setPhaseEnabled(6, false);
    expect(usePipelineStore.getState().config.phases.phase_06).toBe(false);

    usePipelineStore.getState().setPhaseEnabled(6, true);
    expect(usePipelineStore.getState().config.phases.phase_06).toBe(true);
  });

  it('should set dataset path', () => {
    usePipelineStore.getState().setDataset('/path/to/data.csv');
    expect(usePipelineStore.getState().config.dataset).toBe('/path/to/data.csv');

    usePipelineStore.getState().setDataset(undefined);
    expect(usePipelineStore.getState().config.dataset).toBeUndefined();
  });

  it('should reset running state and phases but preserve config', () => {
    // Simulate a pipeline run
    usePipelineStore.getState().setRunning(true);
    usePipelineStore.getState().setCurrentPhase(3);
    usePipelineStore.getState().updatePhaseProgress(1, { status: 'completed', progress: 100 });
    usePipelineStore.getState().updatePhaseProgress(2, { status: 'completed', progress: 100 });
    usePipelineStore.getState().updatePhaseProgress(3, { status: 'running', progress: 45 });
    usePipelineStore.getState().setConfig({ dataset: '/data/reviews.csv' });

    // Reset
    usePipelineStore.getState().reset();

    const state = usePipelineStore.getState();
    expect(state.isRunning).toBe(false);
    expect(state.currentPhase).toBeNull();
    expect(state.phases[1].status).toBe('pending');
    expect(state.phases[2].status).toBe('pending');
    expect(state.phases[3].status).toBe('pending');
    // Config should still have the dataset
    expect(state.config.dataset).toBe('/data/reviews.csv');
  });

  it('should handle concurrent state updates correctly', () => {
    const store = usePipelineStore.getState();

    // Simulate rapid updates
    store.setRunning(true);
    store.setCurrentPhase(1);
    store.updatePhaseProgress(1, { status: 'running', progress: 0 });
    store.updatePhaseProgress(1, { progress: 25 });
    store.updatePhaseProgress(1, { progress: 50 });
    store.updatePhaseProgress(1, { progress: 75 });
    store.updatePhaseProgress(1, { progress: 100, status: 'completed' });

    const phase1 = usePipelineStore.getState().phases[1];
    expect(phase1.status).toBe('completed');
    expect(phase1.progress).toBe(100);
  });
});

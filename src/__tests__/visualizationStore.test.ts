import { describe, it, expect, beforeEach } from 'vitest';
import {
  useVisualizationStore,
  VISUALIZATION_CATEGORIES,
  sortVisualizations,
} from '../renderer/stores/visualizationStore';
import type { VisualizationImage } from '../renderer/stores/visualizationStore';

describe('Visualization Store', () => {
  beforeEach(() => {
    useVisualizationStore.getState().reset();
  });

  it('should have correct initial state', () => {
    const state = useVisualizationStore.getState();
    expect(state.images).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.selectedImage).toBeNull();
    expect(state.activeCategory).toBe('all');
  });

  it('should set images', () => {
    const images: VisualizationImage[] = [
      { id: '1', name: 'chart1.png', path: '/charts/chart1.png', category: '02_sentimientos', categoryLabel: 'Sentimientos' },
      { id: '2', name: 'chart2.png', path: '/charts/chart2.png', category: '03_categorias', categoryLabel: 'Categorías' },
    ];

    useVisualizationStore.getState().setImages(images);
    expect(useVisualizationStore.getState().images).toHaveLength(2);
    expect(useVisualizationStore.getState().images[0].name).toBe('chart1.png');
  });

  it('should set loading state', () => {
    useVisualizationStore.getState().setLoading(true);
    expect(useVisualizationStore.getState().isLoading).toBe(true);
  });

  it('should set error', () => {
    useVisualizationStore.getState().setError('Failed to load');
    expect(useVisualizationStore.getState().error).toBe('Failed to load');

    useVisualizationStore.getState().setError(null);
    expect(useVisualizationStore.getState().error).toBeNull();
  });

  it('should set selected image', () => {
    const image: VisualizationImage = {
      id: '1', name: 'test.png', path: '/test.png', category: '02_sentimientos', categoryLabel: 'Sentimientos',
    };

    useVisualizationStore.getState().setSelectedImage(image);
    expect(useVisualizationStore.getState().selectedImage).toEqual(image);

    useVisualizationStore.getState().setSelectedImage(null);
    expect(useVisualizationStore.getState().selectedImage).toBeNull();
  });

  it('should set active category', () => {
    useVisualizationStore.getState().setActiveCategory('topicos');
    expect(useVisualizationStore.getState().activeCategory).toBe('topicos');
  });

  it('should reset to defaults', () => {
    useVisualizationStore.getState().setImages([
      { id: '1', name: 'a.png', path: '/a', category: 'root', categoryLabel: 'Root' },
    ]);
    useVisualizationStore.getState().setLoading(true);
    useVisualizationStore.getState().setError('err');
    useVisualizationStore.getState().setActiveCategory('temporal');

    useVisualizationStore.getState().reset();

    const state = useVisualizationStore.getState();
    expect(state.images).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.activeCategory).toBe('all');
  });
});

describe('VISUALIZATION_CATEGORIES', () => {
  it('should have 7 categories', () => {
    expect(VISUALIZATION_CATEGORIES).toHaveLength(7);
  });

  it('should start with "all" category', () => {
    expect(VISUALIZATION_CATEGORIES[0].id).toBe('all');
    expect(VISUALIZATION_CATEGORIES[0].label).toBe('Todas');
  });

  it('should have unique IDs', () => {
    const ids = VISUALIZATION_CATEGORIES.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('should have non-empty folders for specific categories', () => {
    const specific = VISUALIZATION_CATEGORIES.filter((c) => c.id !== 'all');
    for (const cat of specific) {
      expect(cat.folder).toBeTruthy();
      expect(cat.folder).toMatch(/^\d{2}_/);
    }
  });
});

describe('sortVisualizations', () => {
  it('should sort by folder order', () => {
    const images: VisualizationImage[] = [
      { id: '1', name: 'b.png', path: '/b', category: '04_topicos', categoryLabel: 'Tópicos' },
      { id: '2', name: 'a.png', path: '/a', category: '01_dashboard', categoryLabel: 'Dashboard' },
      { id: '3', name: 'c.png', path: '/c', category: '02_sentimientos', categoryLabel: 'Sentimientos' },
    ];

    const sorted = sortVisualizations(images);
    expect(sorted[0].category).toBe('01_dashboard');
    expect(sorted[1].category).toBe('02_sentimientos');
    expect(sorted[2].category).toBe('04_topicos');
  });

  it('should sort alphabetically within the same category', () => {
    const images: VisualizationImage[] = [
      { id: '1', name: 'zebra.png', path: '/z', category: '02_sentimientos', categoryLabel: 'Sentimientos' },
      { id: '2', name: 'alpha.png', path: '/a', category: '02_sentimientos', categoryLabel: 'Sentimientos' },
      { id: '3', name: 'middle.png', path: '/m', category: '02_sentimientos', categoryLabel: 'Sentimientos' },
    ];

    const sorted = sortVisualizations(images);
    expect(sorted[0].name).toBe('alpha.png');
    expect(sorted[1].name).toBe('middle.png');
    expect(sorted[2].name).toBe('zebra.png');
  });

  it('should not mutate the original array', () => {
    const images: VisualizationImage[] = [
      { id: '1', name: 'b.png', path: '/b', category: '03_categorias', categoryLabel: 'Categorías' },
      { id: '2', name: 'a.png', path: '/a', category: '01_dashboard', categoryLabel: 'Dashboard' },
    ];

    const sorted = sortVisualizations(images);
    expect(sorted).not.toBe(images);
    expect(images[0].category).toBe('03_categorias'); // original unchanged
  });

  it('should handle empty array', () => {
    expect(sortVisualizations([])).toEqual([]);
  });

  it('should handle unknown categories', () => {
    const images: VisualizationImage[] = [
      { id: '1', name: 'a.png', path: '/a', category: 'unknown', categoryLabel: 'Unknown' },
      { id: '2', name: 'b.png', path: '/b', category: '01_dashboard', categoryLabel: 'Dashboard' },
    ];

    const sorted = sortVisualizations(images);
    // Dashboard (order 0) should come before unknown (order 50)
    expect(sorted[0].category).toBe('01_dashboard');
    expect(sorted[1].category).toBe('unknown');
  });
});

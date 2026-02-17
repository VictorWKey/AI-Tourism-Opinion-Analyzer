/**
 * Visualization Store
 * ====================
 * Zustand store for managing visualization state
 */

import { create } from 'zustand';

export interface VisualizationImage {
  id: string;
  name: string;
  path: string;
  category: string;
  categoryLabel: string;
  thumbnail?: string;
  dataUrl?: string; // Base64 data URL for displaying the image
}

export interface VisualizationCategory {
  id: string;
  label: string;
  folder: string;
  icon: string;
}

interface VisualizationState {
  // Images
  images: VisualizationImage[];
  isLoading: boolean;
  error: string | null;

  // Selected image for modal
  selectedImage: VisualizationImage | null;

  // Active category tab
  activeCategory: string;

  // Actions
  setImages: (images: VisualizationImage[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedImage: (image: VisualizationImage | null) => void;
  setActiveCategory: (category: string) => void;
  loadImages: (chartsPath: string) => Promise<void>;
  reset: () => void;
}

// Categories matching the Python visualization structure
// "Todas" includes everything from all active sections.
export const VISUALIZATION_CATEGORIES: VisualizationCategory[] = [
  { id: 'all', label: 'Todas', folder: '', icon: 'LayoutGrid' },
  { id: 'sentimientos', label: 'Sentimientos', folder: '01_sentimientos', icon: 'Heart' },
  { id: 'subjetividad', label: 'Subjetividad', folder: '02_subjetividad', icon: 'Brain' },
  { id: 'categorias', label: 'Categorías', folder: '03_categorias', icon: 'FolderTree' },
  { id: 'topicos', label: 'Tópicos', folder: '04_topicos', icon: 'MessageSquare' },
  { id: 'temporal', label: 'Temporal', folder: '05_temporal', icon: 'Calendar' },
  { id: 'texto', label: 'Texto', folder: '06_texto', icon: 'FileText' },
  { id: 'combinados', label: 'Análisis Cruzado', folder: '07_combinados', icon: 'Layers' },
];

/**
 * Sort order for visualization folders.
 * Each section in order from 01 to 07.
 */
const FOLDER_SORT_ORDER: Record<string, number> = {
  '01_sentimientos': 1,
  '02_subjetividad': 2,
  '03_categorias': 3,
  '04_topicos': 4,
  '05_temporal': 5,
  '06_texto': 6,
  '07_combinados': 7,
  root: 99,
};

/** Sort images by folder order, then alphabetically by name within each folder. */
export function sortVisualizations(images: VisualizationImage[]): VisualizationImage[] {
  return [...images].sort((a, b) => {
    const orderA = FOLDER_SORT_ORDER[a.category] ?? 50;
    const orderB = FOLDER_SORT_ORDER[b.category] ?? 50;
    if (orderA !== orderB) return orderA - orderB;
    return a.name.localeCompare(b.name);
  });
}

export const useVisualizationStore = create<VisualizationState>((set, get) => ({
  images: [],
  isLoading: false,
  error: null,
  selectedImage: null,
  activeCategory: 'all',

  setImages: (images) => set({ images }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  setSelectedImage: (selectedImage) => set({ selectedImage }),

  setActiveCategory: (activeCategory) => set({ activeCategory }),

  loadImages: async (chartsPath: string) => {
    if (!chartsPath) {
      set({ images: [], isLoading: false, error: 'No charts path configured' });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      // Use IPC to list images from the charts directory
      const result = await window.electronAPI.files.listImages(chartsPath);

      if (result.success && result.images) {
        set({ images: result.images, isLoading: false });
      } else {
        // Don't show error if directory simply doesn't exist yet (no visualizations generated)
        const shouldShowError = result.error && result.error !== 'Directory does not exist';
        set({ 
          images: [], 
          isLoading: false, 
          error: shouldShowError ? result.error : null
        });
      }
    } catch (error) {
      set({ 
        images: [], 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  },

  reset: () =>
    set({
      images: [],
      isLoading: false,
      error: null,
      selectedImage: null,
      activeCategory: 'all',
    }),
}));

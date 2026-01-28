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
export const VISUALIZATION_CATEGORIES: VisualizationCategory[] = [
  { id: 'all', label: 'Todas', folder: '', icon: 'LayoutGrid' },
  { id: 'dashboard', label: 'Dashboard', folder: '01_dashboard', icon: 'LayoutDashboard' },
  { id: 'sentimientos', label: 'Sentimientos', folder: '02_sentimientos', icon: 'Heart' },
  { id: 'categorias', label: 'Categorías', folder: '03_categorias', icon: 'FolderTree' },
  { id: 'topicos', label: 'Tópicos', folder: '04_topicos', icon: 'MessageSquare' },
  { id: 'temporal', label: 'Temporal', folder: '05_temporal', icon: 'Calendar' },
  { id: 'texto', label: 'Texto', folder: '06_texto', icon: 'FileText' },
  { id: 'combinados', label: 'Combinados', folder: '07_combinados', icon: 'Layers' },
];

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
        set({ 
          images: [], 
          isLoading: false, 
          error: result.error || 'Failed to load images' 
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

/**
 * Visualizations Page
 * ====================
 * Display generated charts and visualizations with category tabs
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  LayoutGrid,
  Heart,
  FolderTree,
  MessageSquare,
  Calendar,
  FileText,
  Layers,
  RefreshCw,
  Folder,
  ImageIcon,
  BarChart3,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button } from '../components/ui';
import { DashboardGrid, ImageModal } from '../components/visualizations';
import { 
  useVisualizationStore, 
  VISUALIZATION_CATEGORIES,
  sortVisualizations,
  type VisualizationImage,
} from '../stores/visualizationStore';
import { useDataStore } from '../stores/dataStore';
import { cn } from '../lib/utils';

// Icon mapping for categories
const categoryIcons: Record<string, React.ReactNode> = {
  all: <LayoutGrid className="w-4 h-4" />,
  sentimientos: <Heart className="w-4 h-4" />,
  categorias: <FolderTree className="w-4 h-4" />,
  topicos: <MessageSquare className="w-4 h-4" />,
  temporal: <Calendar className="w-4 h-4" />,
  texto: <FileText className="w-4 h-4" />,
  combinados: <Layers className="w-4 h-4" />,
};

export function Visualizations() {
  const { chartsPath, setOutputPaths } = useDataStore();
  const {
    images,
    isLoading,
    error,
    selectedImage,
    activeCategory,
    setSelectedImage,
    setActiveCategory,
    setImages,
    setLoading,
    setError,
  } = useVisualizationStore();

  // Load images from filesystem
  const loadImages = useCallback(async () => {
    // Always derive the visualizations path from the configured output directory
    // so that changes in Settings are immediately reflected here.
    let targetPath: string;
    try {
      const pythonDataDir = await window.electronAPI.app.getPythonDataDir();
      targetPath = `${pythonDataDir}/visualizaciones`;
      // Keep the store in sync so other components (e.g. Open Folder) work
      if (targetPath !== chartsPath) {
        setOutputPaths({ charts: targetPath });
      }
    } catch (e) {
      // Fall back to the persisted chartsPath if the main process call fails
      if (chartsPath) {
        targetPath = chartsPath;
      } else {
        console.error('Failed to get Python data dir:', e);
        setImages([]);
        setLoading(false);
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      console.log('[Visualizations] Loading images from:', targetPath);
      const result = await window.electronAPI.files.listImages(targetPath);
      console.log('[Visualizations] Result:', result);

      if (result.success && result.images) {
        // Load base64 data for each image
        const imagesWithData = await Promise.all(
          (result.images as VisualizationImage[]).map(async (img) => {
            try {
              const base64Result = await window.electronAPI.files.readImageBase64(img.path);
              if (base64Result.success && base64Result.dataUrl) {
                return { ...img, dataUrl: base64Result.dataUrl };
              }
              return img;
            } catch (e) {
              console.error('Failed to load image:', img.path, e);
              return img;
            }
          })
        );
        setImages(imagesWithData);
      } else {
        setImages([]);
        if (result.error && result.error !== 'Directory does not exist') {
          setError(result.error);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading images');
      setImages([]);
    } finally {
      setLoading(false);
    }
  }, [chartsPath, setImages, setLoading, setError, setOutputPaths]);

  // Load images on mount and when chartsPath changes
  useEffect(() => {
    loadImages();
  }, [loadImages]);

  // Filter images by category and sort them in a deterministic order
  const filteredImages = sortVisualizations(
    activeCategory === 'all'
      ? images
      : images.filter((img) => {
          const category = VISUALIZATION_CATEGORIES.find((c) => c.id === activeCategory);
          return category && img.category === category.folder;
        })
  );

  // Open folder in system file manager
  const handleOpenFolder = async () => {
    // Always derive path from configured output directory (same as loadImages)
    let targetPath: string | null = null;
    try {
      const pythonDataDir = await window.electronAPI.app.getPythonDataDir();
      targetPath = `${pythonDataDir}/visualizaciones`;
    } catch (e) {
      // Fallback to persisted chartsPath
      targetPath = chartsPath;
    }

    if (!targetPath) {
      console.error('No visualization path available');
      return;
    }
    
    if (targetPath) {
      try {
        console.log('[Visualizations] Opening folder:', targetPath);
        const result = await window.electronAPI.files.openPath(targetPath);
        console.log('[Visualizations] Open folder result:', result);
        
        if (!result.success) {
          console.error('Failed to open folder:', result.error);
        }
      } catch (e) {
        console.error('Failed to open folder:', e);
      }
    }
  };

  // Handle image selection for modal
  const handleSelectImage = (image: VisualizationImage) => {
    setSelectedImage(image);
  };

  // Handle navigation in modal
  const handleNavigate = (image: VisualizationImage) => {
    setSelectedImage(image);
  };

  // Get count for each category
  const getCategoryCount = (categoryId: string) => {
    if (categoryId === 'all') return images.length;
    const category = VISUALIZATION_CATEGORIES.find((c) => c.id === categoryId);
    if (!category) return 0;
    return images.filter((img) => img.category === category.folder).length;
  };

  return (
    <PageLayout
      title="Dashboard"
      description="Explora los gráficos generados por el análisis"
      headerActions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadImages} disabled={isLoading}>
            <RefreshCw className={cn('w-4 h-4 mr-2', isLoading && 'animate-spin')} />
            Actualizar
          </Button>
          {chartsPath && (
            <Button variant="outline" size="sm" onClick={handleOpenFolder}>
              <Folder className="w-4 h-4 mr-2" />
              Abrir Carpeta
            </Button>
          )}
        </div>
      }
    >
      <div className="space-y-6">
        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2">
          {VISUALIZATION_CATEGORIES.map((category) => {
            const count = getCategoryCount(category.id);
            return (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  activeCategory === category.id
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                )}
              >
                {categoryIcons[category.id]}
                <span>{category.label}</span>
                <span
                  className={cn(
                    'px-1.5 py-0.5 text-xs rounded-full',
                    activeCategory === category.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                  )}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Error message */}
        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Loading state */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-slate-400 animate-spin mb-4" />
            <p className="text-slate-500 dark:text-slate-400">Cargando visualizaciones...</p>
          </div>
        ) : images.length === 0 ? (
          /* Empty state - no images at all */
          <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <BarChart3 className="w-16 h-16 text-slate-300 dark:text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">
              No hay visualizaciones disponibles
            </h3>
            <p className="text-slate-500 dark:text-slate-400 text-center max-w-md">
              {chartsPath
                ? 'Ejecuta el pipeline completo (incluyendo la Fase 7) para generar los gráficos de análisis.'
                : 'Primero carga un dataset y ejecuta el pipeline de análisis.'}
            </p>
            {!chartsPath && (
              <p className="text-sm text-slate-400 dark:text-slate-500 mt-2">
                Ve a la página de "Datos" para comenzar.
              </p>
            )}
          </div>
        ) : filteredImages.length === 0 ? (
          /* Empty state - no images in selected category */
          <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <ImageIcon className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
            <p className="text-slate-500 dark:text-slate-400 text-center">
              No hay visualizaciones en esta categoría
            </p>
            <button
              onClick={() => setActiveCategory('all')}
              className="mt-3 text-blue-600 dark:text-blue-400 text-sm hover:underline"
            >
              Ver todas las visualizaciones
            </button>
          </div>
        ) : (
          /* Image gallery */
          <DashboardGrid
            images={filteredImages}
            onSelect={handleSelectImage}
            activeCategory={activeCategory}
          />
        )}

        {/* Stats summary */}
        {images.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            {VISUALIZATION_CATEGORIES.filter((c) => c.id !== 'all').map((category) => {
              const count = getCategoryCount(category.id);
              return (
                <div
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className={cn(
                    'p-3 rounded-lg cursor-pointer transition-colors',
                    'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700',
                    'hover:border-blue-300 dark:hover:border-blue-600',
                    activeCategory === category.id && 'border-blue-500 dark:border-blue-400'
                  )}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {categoryIcons[category.id]}
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 truncate">
                      {category.label}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-slate-700 dark:text-slate-200">
                    {count}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Full-screen image modal */}
      {selectedImage && (
        <ImageModal
          image={selectedImage}
          images={filteredImages}
          onClose={() => setSelectedImage(null)}
          onNavigate={handleNavigate}
        />
      )}
    </PageLayout>
  );
}

export default Visualizations;

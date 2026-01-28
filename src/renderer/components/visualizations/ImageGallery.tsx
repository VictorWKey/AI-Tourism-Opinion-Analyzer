/**
 * ImageGallery Component
 * =======================
 * Displays a grid of image thumbnails with hover effects
 */

import React from 'react';
import { Download, Maximize2, ImageIcon } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { VisualizationImage } from '../../stores/visualizationStore';

interface ImageGalleryProps {
  images: VisualizationImage[];
  onSelect: (image: VisualizationImage) => void;
  className?: string;
}

export function ImageGallery({ images, onSelect, className }: ImageGalleryProps) {
  const handleDownload = async (e: React.MouseEvent, image: VisualizationImage) => {
    e.stopPropagation();
    // Open the image file in system file manager
    await window.electronAPI.files.openPath(image.path);
  };

  if (images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
        <ImageIcon className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <p className="text-slate-500 dark:text-slate-400 text-center">
          No hay visualizaciones en esta categoría
        </p>
        <p className="text-sm text-slate-400 dark:text-slate-500 text-center mt-1">
          Ejecuta el pipeline para generar gráficos
        </p>
      </div>
    );
  }

  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4', className)}>
      {images.map((image) => (
        <div
          key={image.id}
          onClick={() => onSelect(image)}
          className={cn(
            'group relative bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700',
            'overflow-hidden cursor-pointer transition-all duration-200',
            'hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600',
            'hover:scale-[1.02]'
          )}
        >
          {/* Image Container */}
          <div className="aspect-video bg-slate-100 dark:bg-slate-700 relative overflow-hidden">
            <img
              src={`file://${image.path}`}
              alt={image.name}
              className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                target.parentElement?.classList.add('flex', 'items-center', 'justify-center');
                const placeholder = document.createElement('div');
                placeholder.innerHTML = `
                  <div class="text-center text-slate-400">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span class="text-xs">Error al cargar</span>
                  </div>
                `;
                target.parentElement?.appendChild(placeholder);
              }}
            />
            
            {/* Overlay on hover */}
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200" />

            {/* Action buttons */}
            <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <button
                onClick={(e) => handleDownload(e, image)}
                className="p-2 bg-white/90 dark:bg-slate-800/90 rounded-lg shadow-lg hover:bg-white dark:hover:bg-slate-700 transition-colors"
                title="Abrir archivo"
              >
                <Download className="w-4 h-4 text-slate-600 dark:text-slate-300" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onSelect(image);
                }}
                className="p-2 bg-white/90 dark:bg-slate-800/90 rounded-lg shadow-lg hover:bg-white dark:hover:bg-slate-700 transition-colors"
                title="Ver en pantalla completa"
              >
                <Maximize2 className="w-4 h-4 text-slate-600 dark:text-slate-300" />
              </button>
            </div>

            {/* Category badge */}
            <div className="absolute bottom-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <span className="px-2 py-1 text-xs font-medium bg-blue-600/90 text-white rounded-md">
                {image.categoryLabel}
              </span>
            </div>
          </div>

          {/* Image info */}
          <div className="p-3">
            <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate" title={image.name}>
              {image.name}
            </h3>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ImageGallery;

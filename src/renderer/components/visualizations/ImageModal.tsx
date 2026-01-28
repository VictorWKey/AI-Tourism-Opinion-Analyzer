/**
 * ImageModal Component
 * =====================
 * Full-screen lightbox for viewing images with zoom and navigation
 */

import React, { useEffect, useCallback, useState } from 'react';
import { X, Download, ZoomIn, ZoomOut, RotateCw, ChevronLeft, ChevronRight, Folder } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../lib/utils';
import type { VisualizationImage } from '../../stores/visualizationStore';

interface ImageModalProps {
  image: VisualizationImage;
  images?: VisualizationImage[];
  onClose: () => void;
  onNavigate?: (image: VisualizationImage) => void;
}

export function ImageModal({ image, images = [], onClose, onNavigate }: ImageModalProps) {
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [imageError, setImageError] = useState(false);

  // Find current index for navigation
  const currentIndex = images.findIndex((img) => img.id === image.id);
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < images.length - 1;

  const handlePrev = useCallback(() => {
    if (hasPrev && onNavigate) {
      setScale(1);
      setRotation(0);
      setImageError(false);
      onNavigate(images[currentIndex - 1]);
    }
  }, [hasPrev, currentIndex, images, onNavigate]);

  const handleNext = useCallback(() => {
    if (hasNext && onNavigate) {
      setScale(1);
      setRotation(0);
      setImageError(false);
      onNavigate(images[currentIndex + 1]);
    }
  }, [hasNext, currentIndex, images, onNavigate]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'ArrowLeft':
          handlePrev();
          break;
        case 'ArrowRight':
          handleNext();
          break;
        case '+':
        case '=':
          setScale((s) => Math.min(s + 0.25, 3));
          break;
        case '-':
          setScale((s) => Math.max(s - 0.25, 0.5));
          break;
        case 'r':
          setRotation((r) => (r + 90) % 360);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, handlePrev, handleNext]);

  const handleDownload = async () => {
    await window.electronAPI.files.openPath(image.path);
  };

  const handleOpenFolder = async () => {
    // Get the directory containing the image
    const dirPath = image.path.substring(0, image.path.lastIndexOf('/'));
    await window.electronAPI.files.openPath(dirPath);
  };

  const handleZoomIn = () => setScale((s) => Math.min(s + 0.25, 3));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.25, 0.5));
  const handleRotate = () => setRotation((r) => (r + 90) % 360);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
        onClick={onClose}
      >
        {/* Header with controls */}
        <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-gradient-to-b from-black/50 to-transparent">
          <div className="flex items-center gap-4">
            <h2 className="text-white font-medium truncate max-w-md">{image.name}</h2>
            <span className="px-2 py-1 text-xs font-medium bg-blue-600/80 text-white rounded-md">
              {image.categoryLabel}
            </span>
            {images.length > 1 && (
              <span className="text-white/60 text-sm">
                {currentIndex + 1} / {images.length}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Zoom controls */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleZoomOut();
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              title="Alejar (−)"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <span className="text-white/60 text-sm min-w-[3rem] text-center">
              {Math.round(scale * 100)}%
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleZoomIn();
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              title="Acercar (+)"
            >
              <ZoomIn className="w-5 h-5" />
            </button>

            <div className="w-px h-6 bg-white/20 mx-2" />

            {/* Rotate */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleRotate();
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              title="Rotar (R)"
            >
              <RotateCw className="w-5 h-5" />
            </button>

            <div className="w-px h-6 bg-white/20 mx-2" />

            {/* Download / Open */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleOpenFolder();
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              title="Abrir carpeta"
            >
              <Folder className="w-5 h-5" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDownload();
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              title="Abrir archivo"
            >
              <Download className="w-5 h-5" />
            </button>

            <div className="w-px h-6 bg-white/20 mx-2" />

            {/* Close */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              title="Cerrar (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation arrows */}
        {images.length > 1 && (
          <>
            {hasPrev && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handlePrev();
                }}
                className={cn(
                  'absolute left-4 top-1/2 -translate-y-1/2 z-10',
                  'p-3 text-white/80 hover:text-white bg-black/50 hover:bg-black/70',
                  'rounded-full transition-colors'
                )}
                title="Anterior (←)"
              >
                <ChevronLeft className="w-8 h-8" />
              </button>
            )}
            {hasNext && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleNext();
                }}
                className={cn(
                  'absolute right-4 top-1/2 -translate-y-1/2 z-10',
                  'p-3 text-white/80 hover:text-white bg-black/50 hover:bg-black/70',
                  'rounded-full transition-colors'
                )}
                title="Siguiente (→)"
              >
                <ChevronRight className="w-8 h-8" />
              </button>
            )}
          </>
        )}

        {/* Image */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative max-w-[90vw] max-h-[85vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {!imageError ? (
            <img
              src={image.dataUrl || `file://${image.path}`}
              alt={image.name}
              className="max-w-full max-h-[85vh] object-contain transition-transform duration-200"
              style={{
                transform: `scale(${scale}) rotate(${rotation}deg)`,
              }}
              onError={() => setImageError(true)}
              draggable={false}
            />
          ) : (
            <div className="flex flex-col items-center justify-center w-96 h-64 bg-slate-800 rounded-lg">
              <X className="w-12 h-12 text-slate-500 mb-4" />
              <p className="text-slate-400">No se pudo cargar la imagen</p>
              <p className="text-sm text-slate-500 mt-2 max-w-xs truncate">{image.path}</p>
            </div>
          )}
        </motion.div>

        {/* Footer with image path */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/50 to-transparent">
          <p className="text-white/60 text-sm text-center truncate">{image.path}</p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

export default ImageModal;

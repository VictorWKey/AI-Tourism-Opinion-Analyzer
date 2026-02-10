/**
 * DashboardGrid Component
 * ========================
 * Interactive drag-and-drop, resizable image grid using react-grid-layout v2.
 * Users can rearrange and resize chart images freely.
 * Layout is persisted in localStorage per category.
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  ResponsiveGridLayout,
  useContainerWidth,
  type LayoutItem,
  type Layout,
  type ResponsiveLayouts,
} from 'react-grid-layout';
import { Download, Maximize2, Lock, Unlock, RotateCcw, GripVertical } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { VisualizationImage } from '../../stores/visualizationStore';

import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const LAYOUT_STORAGE_KEY = 'dashboard-grid-layouts';
const COLS = { lg: 4, md: 3, sm: 2, xs: 1, xxs: 1 };
const BREAKPOINTS = { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 };
const ROW_HEIGHT = 220;

interface DashboardGridProps {
  images: VisualizationImage[];
  onSelect: (image: VisualizationImage) => void;
  activeCategory: string;
  className?: string;
}

/** Generate a deterministic default layout for a set of images. */
function generateDefaultLayout(images: VisualizationImage[], cols: number): Layout {
  return images.map((img, i): LayoutItem => ({
    i: img.id,
    x: i % cols,
    y: Math.floor(i / cols),
    w: 1,
    h: 1,
    minW: 1,
    minH: 1,
  }));
}

/** Generate responsive layouts for all breakpoints. */
function generateDefaultLayouts(images: VisualizationImage[]): ResponsiveLayouts {
  return {
    lg: generateDefaultLayout(images, COLS.lg),
    md: generateDefaultLayout(images, COLS.md),
    sm: generateDefaultLayout(images, COLS.sm),
    xs: generateDefaultLayout(images, COLS.xs),
    xxs: generateDefaultLayout(images, COLS.xxs),
  };
}

/** Load saved layouts from localStorage. */
function loadLayouts(category: string): ResponsiveLayouts | null {
  try {
    const stored = localStorage.getItem(LAYOUT_STORAGE_KEY);
    if (!stored) return null;
    const all = JSON.parse(stored) as Record<string, ResponsiveLayouts>;
    return all[category] ?? null;
  } catch {
    return null;
  }
}

/** Save layouts to localStorage. */
function saveLayouts(category: string, layouts: ResponsiveLayouts): void {
  try {
    const stored = localStorage.getItem(LAYOUT_STORAGE_KEY);
    const all = stored ? (JSON.parse(stored) as Record<string, ResponsiveLayouts>) : {};
    all[category] = layouts;
    localStorage.setItem(LAYOUT_STORAGE_KEY, JSON.stringify(all));
  } catch {
    // Silently ignore storage errors
  }
}

/**
 * Ensure saved layouts contain all current images, appending any new ones.
 */
function patchLayouts(
  saved: ResponsiveLayouts,
  images: VisualizationImage[]
): ResponsiveLayouts {
  const imageIds = new Set(images.map((i) => i.id));
  const breakpoints = Object.keys(COLS) as (keyof typeof COLS)[];
  const patched: ResponsiveLayouts = {};

  for (const bp of breakpoints) {
    const bpLayout: Layout = saved[bp] ?? [];
    const existingIds = new Set(bpLayout.map((l) => l.i));
    const cols = COLS[bp];
    const maxY = bpLayout.reduce((max, l) => Math.max(max, l.y + l.h), 0);

    let nextIndex = 0;
    const missing: LayoutItem[] = images
      .filter((img) => !existingIds.has(img.id))
      .map((img) => {
        const item: LayoutItem = {
          i: img.id,
          x: nextIndex % cols,
          y: maxY + Math.floor(nextIndex / cols),
          w: 1,
          h: 1,
          minW: 1,
          minH: 1,
        };
        nextIndex++;
        return item;
      });

    patched[bp] = [
      ...bpLayout.filter((l) => imageIds.has(l.i)),
      ...missing,
    ];
  }

  return patched;
}

export function DashboardGrid({
  images,
  onSelect,
  activeCategory,
  className,
}: DashboardGridProps) {
  const [isLocked, setIsLocked] = useState(false);
  const { width, containerRef, mounted } = useContainerWidth();

  // Derive layouts: try stored, fallback to defaults.
  const [layouts, setLayouts] = useState<ResponsiveLayouts>(() => {
    const saved = loadLayouts(activeCategory);
    if (saved) return patchLayouts(saved, images);
    return generateDefaultLayouts(images);
  });

  // When category or images change, reset layouts accordingly
  useEffect(() => {
    const saved = loadLayouts(activeCategory);
    if (saved) {
      setLayouts(patchLayouts(saved, images));
    } else {
      setLayouts(generateDefaultLayouts(images));
    }
  }, [activeCategory, images]);

  const handleLayoutChange = useCallback(
    (_currentLayout: Layout, allLayouts: ResponsiveLayouts) => {
      setLayouts(allLayouts);
      saveLayouts(activeCategory, allLayouts);
    },
    [activeCategory]
  );

  const handleResetLayout = useCallback(() => {
    const defaults = generateDefaultLayouts(images);
    setLayouts(defaults);
    saveLayouts(activeCategory, defaults);
  }, [images, activeCategory]);

  const handleDownload = async (e: React.MouseEvent, image: VisualizationImage) => {
    e.stopPropagation();
    await window.electronAPI.files.openPath(image.path);
  };

  if (images.length === 0) {
    return null; // Parent handles empty state
  }

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs text-slate-400">
          {isLocked
            ? 'Layout bloqueado'
            : 'Arrastra y redimensiona los gráficos para personalizar el dashboard'}
        </p>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsLocked((v) => !v)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors',
              isLocked
                ? 'bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100'
                : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
            )}
            title={isLocked ? 'Desbloquear layout' : 'Bloquear layout'}
          >
            {isLocked ? (
              <Lock className="w-3.5 h-3.5" />
            ) : (
              <Unlock className="w-3.5 h-3.5" />
            )}
            {isLocked ? 'Bloqueado' : 'Libre'}
          </button>
          <button
            onClick={handleResetLayout}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 transition-colors"
            title="Restablecer layout por defecto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Restablecer
          </button>
        </div>
      </div>

      {/* Grid */}
      {mounted && (
        <ResponsiveGridLayout
          className="dashboard-grid-layout"
          width={width}
          layouts={layouts}
          breakpoints={BREAKPOINTS}
          cols={COLS}
          rowHeight={ROW_HEIGHT}
          dragConfig={{
            enabled: !isLocked,
            handle: '.grid-drag-handle',
          }}
          resizeConfig={{
            enabled: !isLocked,
          }}
          onLayoutChange={handleLayoutChange}
          margin={[12, 12]}
          containerPadding={[0, 0]}
          autoSize
        >
          {images.map((image) => (
            <div
              key={image.id}
              className={cn(
                'group relative bg-white rounded-xl border border-slate-200',
                'overflow-hidden transition-shadow duration-200',
                !isLocked && 'hover:shadow-lg hover:border-blue-300'
              )}
            >
              {/* Drag handle */}
              {!isLocked && (
                <div className="grid-drag-handle absolute top-0 left-0 right-0 h-7 z-10 flex items-center justify-center cursor-grab active:cursor-grabbing bg-linear-to-b from-slate-100/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <GripVertical className="w-4 h-4 text-slate-400" />
                </div>
              )}

              {/* Image — fills the entire card */}
              <div
                className="absolute inset-0 cursor-pointer"
                onClick={() => onSelect(image)}
              >
                <img
                  src={image.dataUrl || `file://${image.path}`}
                  alt={image.name}
                  className="w-full h-full object-contain bg-slate-50 p-1"
                  loading="lazy"
                />
              </div>

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200 pointer-events-none" />

              {/* Action buttons */}
              <div className="absolute top-1 right-1 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10">
                <button
                  onClick={(e) => handleDownload(e, image)}
                  className="p-1.5 bg-white/90 rounded-lg shadow hover:bg-white transition-colors"
                  title="Abrir archivo"
                >
                  <Download className="w-3.5 h-3.5 text-slate-600" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(image);
                  }}
                  className="p-1.5 bg-white/90 rounded-lg shadow hover:bg-white transition-colors"
                  title="Ver en pantalla completa"
                >
                  <Maximize2 className="w-3.5 h-3.5 text-slate-600" />
                </button>
              </div>

              {/* Title bar at the bottom */}
              <div className="absolute bottom-0 left-0 right-0 px-2 py-1.5 bg-linear-to-t from-white/95 to-white/60 z-10">
                <h3
                  className="text-xs font-medium text-slate-700 truncate"
                  title={image.name}
                >
                  {image.name}
                </h3>
                <span className="text-[10px] text-slate-400">{image.categoryLabel}</span>
              </div>
            </div>
          ))}
        </ResponsiveGridLayout>
      )}
    </div>
  );
}

export default DashboardGrid;

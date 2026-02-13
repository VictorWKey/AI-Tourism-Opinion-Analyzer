/**
 * DashboardGrid Component
 * ========================
 * Interactive drag-and-drop, resizable image grid using react-grid-layout v2.
 * Users can rearrange and resize chart images freely.
 * Layout is persisted to disk via electron-store (survives app restarts).
 */

import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import {
  ResponsiveGridLayout,
  useContainerWidth,
  verticalCompactor,
  type LayoutItem,
  type Layout,
  type ResponsiveLayouts,
} from 'react-grid-layout';
import { Download, Maximize2, Lock, Unlock, RotateCcw, GripVertical } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { VisualizationImage } from '../../stores/visualizationStore';

import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const STORE_KEY = 'gridLayouts';
const COLS = { lg: 4, md: 3, sm: 2, xs: 1, xxs: 1 };
const BREAKPOINTS = { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 };
const ROW_HEIGHT = 220;
/** Debounce delay (ms) for persisting layout changes to disk */
const SAVE_DEBOUNCE_MS = 800;

interface DashboardGridProps {
  images: VisualizationImage[];
  onSelect: (image: VisualizationImage) => void;
  activeCategory: string;
  className?: string;
}

/**
 * ─────────────────────────────────────────────────────────
 * Curated default layouts per category (lg = 4 columns)
 * ─────────────────────────────────────────────────────────
 * Each entry is [imageIdSuffix, x, y, w, h].
 * The suffix is matched against the image id which has the form
 *   "<folder>-<filename.png>"
 * so we match by the filename part.
 *
 * Design rationale:
 *  - Hero charts (most important) → 2×2
 *  - Wide charts (temporal, comparisons) → 2×1
 *  - Regular charts → 1×1
 */
type CuratedItem = [suffix: string, x: number, y: number, w: number, h: number];

const CURATED_LAYOUTS: Record<string, CuratedItem[]> = {
  // ── "Todas" (all) — 31 images from all 7 folders ──────────────────
  // Show the executive dashboard huge, then a nice mix
  all: [
    // Row 0-1: Executive dashboard (hero) + sentiment donut + first wordcloud
    ['dashboard_ejecutivo.png',            0, 0, 2, 2],
    ['distribucion_sentimientos.png',      2, 0, 2, 2],
    // Row 2-3: Top categories + radar chart
    ['top_categorias.png',                 0, 2, 2, 1],
    ['radar_chart_360.png',                2, 2, 2, 2],
    ['sentimientos_por_categoria.png',     0, 3, 2, 1],
    // Row 4: Temporal row
    ['evolucion_temporal_sentimientos.png', 0, 4, 2, 1],
    ['volumen_opiniones_tiempo.png',       2, 4, 2, 1],
    // Row 5-6: Topics + wordcloud hero
    ['wordcloud_general.png',              0, 5, 2, 2],
    ['top_subtopicos_mencionados.png',     2, 5, 1, 1],
    ['top_subtopicos_problematicos.png',   3, 5, 1, 1],
    ['distribucion_subtopicos.png',        2, 6, 2, 1],
    // Row 7: Más sentimientos
    ['sentimientos_por_calificacion.png',  0, 7, 2, 1],
    ['sentimiento_vs_subjetividad.png',    2, 7, 2, 1],
    // Row 8: Wordclouds por sentimiento
    ['wordcloud_positivo.png',             0, 8, 1, 1],
    ['wordcloud_neutro.png',               1, 8, 1, 1],
    ['wordcloud_negativo.png',             2, 8, 1, 1],
    ['top_palabras_comparacion.png',       3, 8, 1, 1],
    // Row 9: Categorías detalle
    ['fortalezas_vs_debilidades.png',      0, 9, 2, 1],
    ['matriz_coocurrencia.png',            2, 9, 2, 1],
    // Row 10: Categorías + temporal
    ['calificacion_por_categoria.png',     0, 10, 2, 1],
    ['evolucion_categorias.png',           2, 10, 2, 1],
    // Row 11: Temporal detalle
    ['evolucion_sentimientos.png',         0, 11, 2, 1],
    ['tendencia_calificacion.png',         2, 11, 2, 1],
    // Row 12: Temporal + texto
    ['estacionalidad_categorias.png',      0, 12, 2, 1],
    ['distribucion_longitud.png',          2, 12, 1, 1],
    ['top_bigramas.png',                   3, 12, 1, 1],
    // Row 13: Texto + combinados
    ['top_trigramas.png',                  0, 13, 1, 1],
    ['sentimiento_subjetividad_categoria.png', 1, 13, 1, 1],
    ['calificacion_categoria_sentimiento.png', 2, 13, 2, 1],
    // Row 14: Combinados
    ['volumen_vs_sentimiento_scatter.png',         0, 14, 2, 1],
    ['correlacion_calificacion_sentimiento.png',   2, 14, 1, 1],
    ['distribucion_categorias_calificacion.png',   3, 14, 1, 1],
  ],

  // ── Sentimientos (8 images) ────────────────────────────────────────
  sentimientos: [
    // Row 0-1: Donut hero + temporal evolution wide
    ['distribucion_sentimientos.png',      0, 0, 2, 2],
    ['evolucion_temporal_sentimientos.png', 2, 0, 2, 1],
    ['sentimientos_por_calificacion.png',  2, 1, 2, 1],
    // Row 2-3: Three wordclouds + comparison
    ['wordcloud_positivo.png',             0, 2, 1, 1],
    ['wordcloud_neutro.png',               1, 2, 1, 1],
    ['wordcloud_negativo.png',             2, 2, 1, 1],
    ['top_palabras_comparacion.png',       3, 2, 1, 2],
    // Row 3: Subjectivity
    ['sentimiento_vs_subjetividad.png',    0, 3, 3, 1],
  ],

  // ── Categorías (7 images) ──────────────────────────────────────────
  categorias: [
    // Row 0-1: Top categories hero + radar hero
    ['top_categorias.png',                 0, 0, 2, 2],
    ['radar_chart_360.png',                2, 0, 2, 2],
    // Row 2: Wide panels
    ['sentimientos_por_categoria.png',     0, 2, 2, 1],
    ['fortalezas_vs_debilidades.png',      2, 2, 2, 1],
    // Row 3: Bottom row
    ['matriz_coocurrencia.png',            0, 3, 2, 1],
    ['calificacion_por_categoria.png',     2, 3, 1, 1],
    ['evolucion_categorias.png',           3, 3, 1, 1],
  ],

  // ── Tópicos (3 images) ─────────────────────────────────────────────
  topicos: [
    // Row 0-1: Heatmap hero + two side-by-side bars
    ['distribucion_subtopicos.png',        0, 0, 2, 2],
    ['top_subtopicos_mencionados.png',     2, 0, 2, 1],
    ['top_subtopicos_problematicos.png',   2, 1, 2, 1],
  ],

  // ── Temporal (4 images) ────────────────────────────────────────────
  temporal: [
    // Row 0-1: Volume hero + sentiment line
    ['volumen_opiniones_tiempo.png',       0, 0, 2, 2],
    ['evolucion_sentimientos.png',         2, 0, 2, 1],
    ['tendencia_calificacion.png',         2, 1, 2, 1],
    // Row 2: Seasonality wide
    ['estacionalidad_categorias.png',      0, 2, 4, 1],
  ],

  // ── Texto (4 images) ───────────────────────────────────────────────
  texto: [
    // Row 0-1: Wordcloud hero + length distribution
    ['wordcloud_general.png',              0, 0, 2, 2],
    ['distribucion_longitud.png',          2, 0, 2, 1],
    // Row 1: Bigrams + trigrams
    ['top_bigramas.png',                   2, 1, 1, 1],
    ['top_trigramas.png',                  3, 1, 1, 1],
  ],

  // ── Análisis Cruzado / Combinados (5 images) ──────────────────────
  combinados: [
    // Row 0-1: Scatter hero + heatmap hero
    ['volumen_vs_sentimiento_scatter.png',         0, 0, 2, 2],
    ['sentimiento_subjetividad_categoria.png',     2, 0, 2, 2],
    // Row 2: Three bottom panels
    ['calificacion_categoria_sentimiento.png',     0, 2, 2, 1],
    ['correlacion_calificacion_sentimiento.png',   2, 2, 1, 1],
    ['distribucion_categorias_calificacion.png',   3, 2, 1, 1],
  ],
};

/**
 * Build a curated layout for the lg breakpoint from CURATED_LAYOUTS.
 * Falls back to auto-layout for any images not in the curated list.
 */
function buildCuratedLayout(
  images: VisualizationImage[],
  category: string,
  cols: number
): Layout {
  const curated = CURATED_LAYOUTS[category];
  if (!curated || cols < 4) {
    // For narrow breakpoints, use the smart auto-layout
    return buildAutoLayout(images, cols);
  }

  const layout: LayoutItem[] = [];
  const placed = new Set<string>();

  // Place curated items first
  for (const [suffix, x, y, w, h] of curated) {
    const img = images.find((im) => im.id.endsWith(suffix));
    if (img) {
      layout.push({ i: img.id, x, y, w, h, minW: 1, minH: 1 });
      placed.add(img.id);
    }
  }

  // Any remaining images get appended below
  const maxY = layout.reduce((max, l) => Math.max(max, l.y + l.h), 0);
  let idx = 0;
  for (const img of images) {
    if (!placed.has(img.id)) {
      layout.push({
        i: img.id,
        x: idx % cols,
        y: maxY + Math.floor(idx / cols),
        w: 1,
        h: 1,
        minW: 1,
        minH: 1,
      });
      idx++;
    }
  }

  return layout;
}

// ── Grid-occupancy helpers for overlap-free placement ────────────────

/** Check if a cell is occupied in the occupancy grid */
function _isOccupied(grid: boolean[][], x: number, y: number): boolean {
  return !!(grid[y] && grid[y][x]);
}

/** Mark a rectangular region as occupied */
function _markOccupied(
  grid: boolean[][],
  x: number,
  y: number,
  w: number,
  h: number,
  cols: number
): void {
  for (let dy = 0; dy < h; dy++) {
    if (!grid[y + dy]) grid[y + dy] = new Array(cols).fill(false);
    for (let dx = 0; dx < w; dx++) {
      grid[y + dy][x + dx] = true;
    }
  }
}

/** Find the first position where a w×h block fits without overlapping */
function _findPosition(
  grid: boolean[][],
  w: number,
  h: number,
  cols: number
): { x: number; y: number } {
  for (let y = 0; ; y++) {
    for (let x = 0; x <= cols - w; x++) {
      let fits = true;
      for (let dy = 0; dy < h && fits; dy++) {
        for (let dx = 0; dx < w && fits; dx++) {
          if (_isOccupied(grid, x + dx, y + dy)) fits = false;
        }
      }
      if (fits) return { x, y };
    }
  }
}

/**
 * Smart auto-layout for medium/small breakpoints.
 * Uses a 2-D occupancy grid to guarantee zero overlaps and proper
 * column-filling even when items have mixed heights (hero 2×2, wide 2×1, etc.).
 */
function buildAutoLayout(images: VisualizationImage[], cols: number): Layout {
  if (cols <= 1) {
    // Single column — stack vertically, first image tall
    let y = 0;
    return images.map((img, i): LayoutItem => {
      const h = i === 0 ? 2 : 1;
      const item: LayoutItem = { i: img.id, x: 0, y, w: 1, h, minW: 1, minH: 1 };
      y += h;
      return item;
    });
  }

  const grid: boolean[][] = [];
  const layout: LayoutItem[] = [];

  for (let i = 0; i < images.length; i++) {
    const img = images[i];
    let w = 1;
    let h = 1;

    if (i === 0) {
      // First image: hero
      w = Math.min(2, cols);
      h = 2;
    } else if (i % 5 === 0) {
      // Every 5th image: double-wide if it fits
      w = Math.min(2, cols);
      h = 1;
    }

    const pos = _findPosition(grid, w, h, cols);
    _markOccupied(grid, pos.x, pos.y, w, h, cols);
    layout.push({ i: img.id, x: pos.x, y: pos.y, w, h, minW: 1, minH: 1 });
  }

  return layout;
}

/** Generate a deterministic default layout for a set of images. */
function generateDefaultLayout(images: VisualizationImage[], cols: number, category: string): Layout {
  return buildCuratedLayout(images, category, cols);
}

/** Generate responsive layouts for all breakpoints. */
function generateDefaultLayouts(images: VisualizationImage[], category = 'all'): ResponsiveLayouts {
  return {
    lg: generateDefaultLayout(images, COLS.lg, category),
    md: generateDefaultLayout(images, COLS.md, category),
    sm: generateDefaultLayout(images, COLS.sm, category),
    xs: generateDefaultLayout(images, COLS.xs, category),
    xxs: generateDefaultLayout(images, COLS.xxs, category),
  };
}

// ── Layout validation & normalization ─────────────────────────────────

/**
 * Clamp every item so it stays within column bounds and has valid sizes.
 * Then re-pack items using the occupancy grid to guarantee no overlaps.
 */
function normalizeLayout(layout: Layout, cols: number): Layout {
  if (!layout || layout.length === 0 || cols <= 0) return layout;

  // First pass: clamp dimensions
  const clamped: LayoutItem[] = (layout as LayoutItem[]).map((item) => {
    let w = Math.max(item.minW ?? 1, Math.min(item.w, cols));
    let h = Math.max(item.minH ?? 1, item.h);
    let x = Math.max(0, Math.min(item.x, cols - w));
    let y = Math.max(0, item.y);
    return { ...item, x, y, w, h };
  });

  // Second pass: re-pack using occupancy grid (preserves relative order by y,x)
  const sorted = [...clamped].sort((a, b) => a.y - b.y || a.x - b.x);
  const grid: boolean[][] = [];
  const result: LayoutItem[] = [];

  for (const item of sorted) {
    // Try to place at existing position first
    let placed = false;
    if (item.x + item.w <= cols) {
      let fits = true;
      for (let dy = 0; dy < item.h && fits; dy++) {
        for (let dx = 0; dx < item.w && fits; dx++) {
          if (_isOccupied(grid, item.x + dx, item.y + dy)) fits = false;
        }
      }
      if (fits) {
        _markOccupied(grid, item.x, item.y, item.w, item.h, cols);
        result.push(item);
        placed = true;
      }
    }
    if (!placed) {
      const pos = _findPosition(grid, item.w, item.h, cols);
      _markOccupied(grid, pos.x, pos.y, item.w, item.h, cols);
      result.push({ ...item, x: pos.x, y: pos.y });
    }
  }

  return result;
}

/**
 * Detect obviously broken layouts:
 *  - All items stacked in column 0 with w=1 when cols ≥ 2
 *  - Items outside column bounds
 *  - Every row has a lone w=1 item when cols ≥ 3 and enough items exist
 */
function isLayoutDegenerate(layout: Layout, cols: number): boolean {
  if (!layout || layout.length <= 1 || cols <= 1) return false;

  // All items at x=0 and w=1 ➜ everything piled in col 0
  const allInCol0 = layout.every((l) => l.x === 0 && l.w === 1);
  if (allInCol0 && layout.length > 1) return true;

  // Any item extends outside bounds ➜ corrupt layout
  if (layout.some((l) => l.x + l.w > cols || l.x < 0)) return true;

  // When cols ≥ 3 and we have ≥ cols items, check if most rows are single-item
  if (cols >= 3 && layout.length >= cols) {
    const rowOccupants = new Map<number, number>();
    for (const l of layout) {
      for (let dy = 0; dy < l.h; dy++) {
        rowOccupants.set(l.y + dy, (rowOccupants.get(l.y + dy) ?? 0) + 1);
      }
    }
    const rows = [...rowOccupants.values()];
    const singleRows = rows.filter((c) => c === 1).length;
    // More than 80% of rows have a lone item → degenerate
    if (rows.length > 2 && singleRows / rows.length > 0.8) return true;
  }

  return false;
}

/** Load saved layouts for a category from electron-store (disk). */
async function loadLayouts(category: string): Promise<ResponsiveLayouts | null> {
  try {
    const all = await window.electronAPI.settings.get<Record<string, ResponsiveLayouts>>(STORE_KEY);
    if (!all || typeof all !== 'object') return null;
    return all[category] ?? null;
  } catch {
    return null;
  }
}

/** Save layouts for a category to electron-store (disk). */
async function saveLayouts(category: string, layouts: ResponsiveLayouts): Promise<void> {
  try {
    const all = await window.electronAPI.settings.get<Record<string, ResponsiveLayouts>>(STORE_KEY) ?? {};
    all[category] = layouts;
    await window.electronAPI.settings.set(STORE_KEY, all);
  } catch {
    // Silently ignore storage errors
  }
}

/**
 * Ensure saved layouts contain all current images, appending any new ones.
 * Removes stale items, adds missing ones, normalizes positions, and
 * regenerates from defaults if the result looks degenerate.
 */
function patchLayouts(
  saved: ResponsiveLayouts,
  images: VisualizationImage[],
  category: string
): ResponsiveLayouts {
  const imageIds = new Set(images.map((i) => i.id));
  const breakpoints = Object.keys(COLS) as (keyof typeof COLS)[];
  const patched: ResponsiveLayouts = {};

  for (const bp of breakpoints) {
    const bpLayout: Layout = saved[bp] ?? [];
    const cols = COLS[bp];

    // Keep only items that still exist
    const kept = (bpLayout as LayoutItem[]).filter((l) => imageIds.has(l.i));
    const existingIds = new Set(kept.map((l) => l.i));

    // Build an occupancy grid from kept items (after normalization)
    const normalized = normalizeLayout(kept, cols) as LayoutItem[];

    // Find positions for missing images using the occupancy grid
    const grid: boolean[][] = [];
    for (const item of normalized) {
      _markOccupied(grid, item.x, item.y, item.w, item.h, cols);
    }

    const missing: LayoutItem[] = [];
    for (const img of images) {
      if (!existingIds.has(img.id)) {
        const pos = _findPosition(grid, 1, 1, cols);
        _markOccupied(grid, pos.x, pos.y, 1, 1, cols);
        missing.push({
          i: img.id,
          x: pos.x,
          y: pos.y,
          w: 1,
          h: 1,
          minW: 1,
          minH: 1,
        });
      }
    }

    const merged = [...normalized, ...missing];

    // If the resulting layout is degenerate, regenerate defaults for this breakpoint
    if (isLayoutDegenerate(merged, cols)) {
      patched[bp] = generateDefaultLayout(images, cols, category);
    } else {
      patched[bp] = merged;
    }
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
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  /** Current breakpoint – kept in sync via onBreakpointChange */
  const currentBreakpointRef = useRef<string>('lg');

  // Start with defaults; the effect below will hydrate from disk.
  const [layouts, setLayouts] = useState<ResponsiveLayouts>(
    () => generateDefaultLayouts(images, activeCategory)
  );
  const [layoutsReady, setLayoutsReady] = useState(false);

  // Stable image-id fingerprint so we can skip unnecessary reloads
  const imageFingerprint = useMemo(
    () => images.map((i) => i.id).sort().join('|'),
    [images]
  );

  // Load persisted layouts from electron-store on mount / category change
  useEffect(() => {
    let cancelled = false;
    setLayoutsReady(false);

    (async () => {
      const saved = await loadLayouts(activeCategory);
      if (cancelled) return;
      if (saved) {
        const patched = patchLayouts(saved, images, activeCategory);
        setLayouts(patched);
      } else {
        setLayouts(generateDefaultLayouts(images, activeCategory));
      }
      setLayoutsReady(true);
    })();

    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCategory, imageFingerprint]);

  const handleLayoutChange = useCallback(
    (_currentLayout: Layout, allLayouts: ResponsiveLayouts) => {
      // Only persist if the layout items match the current image set.
      // This prevents saving stale/corrupt layouts during category transitions.
      const currentIds = new Set(images.map((img) => img.id));
      const layoutIds = new Set(_currentLayout.map((l) => l.i));
      if (currentIds.size !== layoutIds.size) return;
      for (const id of currentIds) {
        if (!layoutIds.has(id)) return;
      }

      // Normalise each breakpoint before committing – clamp bounds & fix overlaps
      const bps = Object.keys(COLS) as (keyof typeof COLS)[];
      const sanitised: ResponsiveLayouts = {};
      for (const bp of bps) {
        const bpLayout = allLayouts[bp];
        if (bpLayout) {
          sanitised[bp] = normalizeLayout(bpLayout, COLS[bp]);
        }
      }

      setLayouts(sanitised);

      // Debounce disk writes to avoid spamming during rapid drag/resize
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
      saveTimerRef.current = setTimeout(() => {
        saveLayouts(activeCategory, sanitised);
      }, SAVE_DEBOUNCE_MS);
    },
    [activeCategory, images]
  );

  /**
   * When the responsive grid crosses a breakpoint, validate the layout for
   * the new column count and regenerate defaults if it looks broken.
   */
  const handleBreakpointChange = useCallback(
    (newBreakpoint: string, newCols: number) => {
      currentBreakpointRef.current = newBreakpoint;

      setLayouts((prev) => {
        const bpLayout = prev[newBreakpoint];
        if (!bpLayout || isLayoutDegenerate(bpLayout as Layout, newCols)) {
          const fixed = generateDefaultLayout(images, newCols, activeCategory);
          const next = { ...prev, [newBreakpoint]: fixed };
          // Persist the fix
          saveLayouts(activeCategory, next);
          return next;
        }
        return prev;
      });
    },
    [images, activeCategory]
  );

  // Cleanup debounce timer on unmount
  useEffect(() => {
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, []);

  const handleResetLayout = useCallback(() => {
    const defaults = generateDefaultLayouts(images, activeCategory);
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

      {/* Grid — key forces full remount on category switch to avoid layout glitches */}
      {mounted && layoutsReady && (
        <ResponsiveGridLayout
          key={activeCategory}
          className="dashboard-grid-layout"
          width={width}
          layouts={layouts}
          breakpoints={BREAKPOINTS}
          cols={COLS}
          rowHeight={ROW_HEIGHT}
          compactor={verticalCompactor}
          dragConfig={{
            enabled: !isLocked,
            handle: '.grid-drag-handle',
          }}
          resizeConfig={{
            enabled: !isLocked,
          }}
          onLayoutChange={handleLayoutChange}
          onBreakpointChange={handleBreakpointChange}
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

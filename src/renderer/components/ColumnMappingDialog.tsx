/**
 * Column Mapping Dialog
 * ======================
 * Professional column mapping interface that lets users map their CSV columns
 * to the system's required columns. Features auto-detection based on name similarity,
 * drag-friendly select UI, and real-time validation.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ArrowRight,
  Check,
  AlertTriangle,
  Info,
  Sparkles,
  X,
  Columns,
  Loader2,
} from 'lucide-react';
import { Button } from './ui';
import { cn } from '../lib/utils';
import type { RequiredColumn, ColumnMapping } from '../../shared/types';

interface ColumnMappingDialogProps {
  /** Columns found in the user's CSV file */
  sourceColumns: string[];
  /** System required columns definition */
  requiredColumns: RequiredColumn[];
  /** First 5 rows of the source data for preview */
  previewData?: Record<string, unknown>[];
  /** Whether the mapping is being applied */
  isApplying: boolean;
  /** Called when user confirms the mapping */
  onApply: (mapping: ColumnMapping) => void;
  /** Called when user cancels */
  onCancel: () => void;
}

/**
 * Compute a similarity score between two strings (case-insensitive).
 * Uses a simple approach: exact match > contains > starts-with > Levenshtein-inspired.
 */
function similarityScore(a: string, b: string): number {
  const la = a.toLowerCase().replace(/[_\-\s]/g, '');
  const lb = b.toLowerCase().replace(/[_\-\s]/g, '');

  if (la === lb) return 1.0;
  if (la.includes(lb) || lb.includes(la)) return 0.8;
  if (la.startsWith(lb) || lb.startsWith(la)) return 0.6;

  // Simple character overlap ratio
  const setA = new Set(la.split(''));
  const setB = new Set(lb.split(''));
  const intersection = [...setA].filter((c) => setB.has(c)).length;
  const union = new Set([...setA, ...setB]).size;
  return union > 0 ? (intersection / union) * 0.4 : 0;
}

/**
 * Auto-detect best column mapping by matching source columns against
 * required column names and their known alternatives.
 */
function autoDetectMapping(
  sourceColumns: string[],
  requiredColumns: RequiredColumn[]
): ColumnMapping {
  const mapping: ColumnMapping = {};
  const usedSourceColumns = new Set<string>();

  // Sort required columns: required first, then optional
  const sortedRequired = [...requiredColumns].sort(
    (a, b) => (b.required ? 1 : 0) - (a.required ? 1 : 0)
  );

  for (const reqCol of sortedRequired) {
    let bestMatch: string | null = null;
    let bestScore = 0;

    for (const srcCol of sourceColumns) {
      if (usedSourceColumns.has(srcCol)) continue;

      // Check against the main name
      let score = similarityScore(srcCol, reqCol.name);

      // Check against alternatives
      if (reqCol.alternatives) {
        for (const alt of reqCol.alternatives) {
          const altScore = similarityScore(srcCol, alt);
          if (altScore > score) score = altScore;
        }
      }

      if (score > bestScore && score >= 0.5) {
        bestScore = score;
        bestMatch = srcCol;
      }
    }

    if (bestMatch) {
      mapping[reqCol.name] = bestMatch;
      usedSourceColumns.add(bestMatch);
    } else {
      mapping[reqCol.name] = null;
    }
  }

  return mapping;
}

export function ColumnMappingDialog({
  sourceColumns,
  requiredColumns,
  previewData,
  isApplying,
  onApply,
  onCancel,
}: ColumnMappingDialogProps) {
  const [mapping, setMapping] = useState<ColumnMapping>({});
  const [showPreview, setShowPreview] = useState(false);

  // Auto-detect on mount
  useEffect(() => {
    const detected = autoDetectMapping(sourceColumns, requiredColumns);
    setMapping(detected);
  }, [sourceColumns, requiredColumns]);

  const handleColumnChange = useCallback(
    (systemCol: string, userCol: string | null) => {
      setMapping((prev) => ({ ...prev, [systemCol]: userCol }));
    },
    []
  );

  const handleAutoDetect = useCallback(() => {
    const detected = autoDetectMapping(sourceColumns, requiredColumns);
    setMapping(detected);
  }, [sourceColumns, requiredColumns]);

  const handleClearAll = useCallback(() => {
    const cleared: ColumnMapping = {};
    for (const col of requiredColumns) {
      cleared[col.name] = null;
    }
    setMapping(cleared);
  }, [requiredColumns]);

  // Validation: check all required columns are mapped
  const validation = useMemo(() => {
    const unmappedRequired: string[] = [];
    let mappedCount = 0;

    // Special logic: either TituloReview OR (Titulo or Review) must be mapped
    const hasText =
      mapping['TituloReview'] ||
      mapping['Titulo'] ||
      mapping['Review'];

    for (const col of requiredColumns) {
      if (mapping[col.name]) {
        mappedCount++;
      } else if (col.required) {
        // Skip text columns from "unmapped" if another text source is mapped
        if (col.name === 'Review' && (mapping['TituloReview'] || mapping['Titulo'])) {
          continue;
        }
        unmappedRequired.push(col.name);
      }
    }

    const isValid = unmappedRequired.length === 0 && hasText;

    return { isValid, unmappedRequired, mappedCount, hasText };
  }, [mapping, requiredColumns]);

  // Which source columns are already used in the mapping
  const usedColumns = useMemo(() => {
    return new Set(Object.values(mapping).filter(Boolean) as string[]);
  }, [mapping]);

  // Group required columns by group
  const columnGroups = useMemo(() => {
    const groups: Record<string, RequiredColumn[]> = {};
    for (const col of requiredColumns) {
      const group = (col as RequiredColumn & { group?: string }).group || 'other';
      if (!groups[group]) groups[group] = [];
      groups[group].push(col);
    }
    return groups;
  }, [requiredColumns]);

  const groupLabels: Record<string, string> = {
    text: 'Columnas de Texto',
    metadata: 'Metadatos',
    other: 'Otras',
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center">
            <Columns className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">
              Mapeo de Columnas
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Asigna las columnas de tu archivo a las que el sistema necesita
            </p>
          </div>
        </div>
        <button
          onClick={onCancel}
          className="p-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          title="Cerrar"
        >
          <X className="w-5 h-5 text-slate-500" />
        </button>
      </div>

      {/* Info banner */}
      <div className="mx-4 mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg flex items-start gap-2">
        <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-blue-700 dark:text-blue-300">
          Las columnas de tu archivo fueron detectadas automáticamente. Ajusta las asignaciones si es necesario.
          Solo <strong>Review</strong>, <strong>FechaEstadia</strong> y <strong>Calificacion</strong> son obligatorias.
        </p>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-2 px-4 pt-3">
        <Button
          variant="outline"
          size="sm"
          onClick={handleAutoDetect}
          className="text-xs"
        >
          <Sparkles className="w-3.5 h-3.5 mr-1" />
          Auto-detectar
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleClearAll}
          className="text-xs"
        >
          Limpiar todo
        </Button>
        <div className="ml-auto text-xs text-slate-500 dark:text-slate-400">
          {validation.mappedCount} de {requiredColumns.length} columnas asignadas
        </div>
      </div>

      {/* Mapping Table */}
      <div className="p-4 space-y-4">
        {Object.entries(columnGroups).map(([groupKey, columns]) => (
          <div key={groupKey}>
            <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
              {groupLabels[groupKey] || groupKey}
            </h4>
            <div className="space-y-2">
              {columns.map((reqCol) => {
                const currentValue = mapping[reqCol.name];
                const isMapped = !!currentValue;
                const isRequired = reqCol.required;
                const isMissing = isRequired && !isMapped;

                // For text group: not strictly missing if another text col is mapped
                const isTextCol = ['Review', 'Titulo', 'TituloReview'].includes(reqCol.name);
                const effectivelyMissing = isMissing && !(isTextCol && validation.hasText);

                return (
                  <div
                    key={reqCol.name}
                    className={cn(
                      'flex items-center gap-3 p-3 rounded-lg border transition-colors',
                      isMapped
                        ? 'border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-900/10'
                        : effectivelyMissing
                          ? 'border-amber-200 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-900/10'
                          : 'border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/50'
                    )}
                  >
                    {/* System column */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-slate-900 dark:text-white">
                          {reqCol.name}
                        </span>
                        {isRequired && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 font-medium">
                            Requerida
                          </span>
                        )}
                        {!isRequired && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 font-medium">
                            Opcional
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {reqCol.description}
                      </p>
                    </div>

                    {/* Arrow */}
                    <ArrowRight className="w-4 h-4 text-slate-400 flex-shrink-0" />

                    {/* Source column selector */}
                    <div className="flex-1 min-w-0">
                      <select
                        value={currentValue || ''}
                        onChange={(e) =>
                          handleColumnChange(
                            reqCol.name,
                            e.target.value || null
                          )
                        }
                        className={cn(
                          'w-full rounded-md border px-3 py-2 text-sm',
                          'bg-white dark:bg-slate-900',
                          'focus:outline-none focus:ring-2 focus:ring-blue-500',
                          isMapped
                            ? 'border-green-300 dark:border-green-700 text-green-800 dark:text-green-300'
                            : 'border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300'
                        )}
                      >
                        <option value="">— Sin asignar —</option>
                        {sourceColumns.map((col) => (
                          <option
                            key={col}
                            value={col}
                            disabled={usedColumns.has(col) && col !== currentValue}
                          >
                            {col}
                            {usedColumns.has(col) && col !== currentValue
                              ? ' (ya asignada)'
                              : ''}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Status icon */}
                    <div className="w-6 flex-shrink-0">
                      {isMapped ? (
                        <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
                      ) : effectivelyMissing ? (
                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Preview toggle */}
      {previewData && previewData.length > 0 && (
        <div className="px-4 pb-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            {showPreview ? 'Ocultar vista previa' : 'Ver datos de origen (primeras 5 filas)'}
          </button>
          {showPreview && (
            <div className="mt-2 overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-lg">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
                    {Object.keys(previewData[0]).map((key) => (
                      <th
                        key={key}
                        className="text-left p-2 font-medium text-slate-600 dark:text-slate-400 whitespace-nowrap"
                      >
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewData.slice(0, 5).map((row, i) => (
                    <tr
                      key={i}
                      className="border-b border-slate-100 dark:border-slate-800"
                    >
                      {Object.values(row).map((value, j) => (
                        <td
                          key={j}
                          className="p-2 text-slate-700 dark:text-slate-300 max-w-[200px] truncate whitespace-nowrap"
                        >
                          {value == null ? (
                            <span className="text-slate-400 italic">null</span>
                          ) : (
                            String(value)
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Validation message */}
      {!validation.isValid && (
        <div className="mx-4 mb-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-700 dark:text-amber-300">
            {!validation.hasText && (
              <p>Debes asignar al menos una columna de texto (Review, Titulo o TituloReview).</p>
            )}
            {validation.unmappedRequired.length > 0 && (
              <p>
                Columnas requeridas sin asignar:{' '}
                <strong>{validation.unmappedRequired.join(', ')}</strong>
              </p>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-end gap-3 p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50">
        <Button variant="outline" onClick={onCancel} disabled={isApplying}>
          Cancelar
        </Button>
        <Button
          onClick={() => onApply(mapping)}
          disabled={!validation.isValid || isApplying}
        >
          {isApplying ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Aplicando...
            </>
          ) : (
            <>
              <Check className="w-4 h-4 mr-2" />
              Aplicar Mapeo
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

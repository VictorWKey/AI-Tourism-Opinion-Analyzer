/**
 * DataPreview Component
 * ======================
 * Table component to display a preview of the dataset
 */

import React from 'react';
import { cn } from '../../lib/utils';

interface DataPreviewProps {
  data: Record<string, unknown>[];
  columns: string[];
  maxRows?: number;
  className?: string;
}

export function DataPreview({ data, columns, maxRows = 5, className }: DataPreviewProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 dark:text-slate-400">
        No hay datos para mostrar
      </div>
    );
  }

  const displayData = data.slice(0, maxRows);

  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 dark:border-slate-700">
            {columns.map((column) => (
              <th
                key={column}
                className="text-left p-2 font-medium text-slate-600 dark:text-slate-400 whitespace-nowrap"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayData.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50"
            >
              {columns.map((column, colIndex) => (
                <td
                  key={colIndex}
                  className="p-2 text-slate-700 dark:text-slate-300 max-w-xs truncate"
                  title={String(row[column] ?? '')}
                >
                  {String(row[column] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > maxRows && (
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 text-center">
          Mostrando {maxRows} de {data.length} filas
        </p>
      )}
    </div>
  );
}

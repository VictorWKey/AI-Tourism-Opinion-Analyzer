/**
 * Data Page
 * ==========
 * Dataset upload and preview
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileSpreadsheet,
  Check,
  X,
  AlertCircle,
  Trash2,
  Eye,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button } from '../components/ui';
import { cn } from '../lib/utils';
import { useDataStore } from '../stores/dataStore';
import { usePipelineStore } from '../stores/pipelineStore';
import type { DatasetValidation } from '../../shared/types';

export function Data() {
  const {
    dataset,
    isValidating,
    validationResult,
    previewData,
    setDataset,
    setValidating,
    setValidationResult,
    setPreviewData,
    clearDataset,
  } = useDataStore();

  const { setDataset: setPipelineDataset } = usePipelineStore();
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setError(null);
      setValidating(true);

      try {
        // Get the file path using Electron file dialog since we can't get actual path from dropped file
        // For dropped files, we need to read content differently
        // Let's use the select file dialog instead for now
        const filePath = await window.electronAPI.files.selectFile({
          filters: [{ name: 'CSV Files', extensions: ['csv'] }],
        });

        if (!filePath) {
          setValidating(false);
          return;
        }

        // Validate the dataset
        const validation = await window.electronAPI.pipeline.validateDataset(filePath);

        if (validation.valid) {
          setDataset({
            path: filePath,
            name: filePath.split('/').pop() || 'dataset.csv',
            rows: validation.rowCount,
            columns: validation.columns,
            sampleData: validation.preview,
            validationStatus: 'valid',
            validationMessages: [],
          });
          setValidationResult(validation);
          setPreviewData(validation.preview || null);
          setPipelineDataset(filePath);
        } else {
          setValidationResult(validation);
          setError(validation.error || 'Dataset validation failed');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dataset');
      } finally {
        setValidating(false);
      }
    },
    [setDataset, setValidating, setValidationResult, setPreviewData, setPipelineDataset]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
  });

  const handleSelectFile = async () => {
    setError(null);
    setValidating(true);

    try {
      const filePath = await window.electronAPI.files.selectFile({
        filters: [{ name: 'CSV Files', extensions: ['csv'] }],
      });

      if (!filePath) {
        setValidating(false);
        return;
      }

      const validation = await window.electronAPI.pipeline.validateDataset(filePath);

      if (validation.valid) {
        setDataset({
          path: filePath,
          name: filePath.split('/').pop() || 'dataset.csv',
          rows: validation.rowCount,
          columns: validation.columns,
          sampleData: validation.preview,
          validationStatus: 'valid',
          validationMessages: [],
        });
        setValidationResult(validation);
        setPreviewData(validation.preview || null);
        setPipelineDataset(filePath);
      } else {
        setValidationResult(validation);
        setError(validation.error || 'Dataset validation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dataset');
    } finally {
      setValidating(false);
    }
  };

  const handleClearDataset = () => {
    clearDataset();
    setPipelineDataset(undefined);
    setError(null);
  };

  return (
    <PageLayout
      title="Datos"
      description="Carga y gestiona el dataset para el análisis"
    >
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Upload Zone */}
        {!dataset && (
          <div
            {...getRootProps()}
            className={cn(
              'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors',
              isDragActive
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500',
              isValidating && 'pointer-events-none opacity-50'
            )}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto text-slate-400 mb-4" />
            <p className="text-lg font-medium text-slate-700 dark:text-slate-300">
              {isDragActive
                ? 'Suelta el archivo aquí...'
                : 'Arrastra un archivo CSV aquí'}
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
              o haz clic para seleccionar un archivo
            </p>
            <Button
              className="mt-4"
              onClick={(e) => {
                e.stopPropagation();
                handleSelectFile();
              }}
              disabled={isValidating}
            >
              {isValidating ? 'Validando...' : 'Seleccionar Archivo'}
            </Button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900 dark:text-red-100">
                Error al cargar el dataset
              </p>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Dataset Info */}
        {dataset && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <FileSpreadsheet className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white">
                    {dataset.name}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {dataset.rows.toLocaleString()} filas • {dataset.columns.length} columnas
                  </p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={handleClearDataset}>
                <Trash2 className="w-4 h-4 mr-2" />
                Eliminar
              </Button>
            </div>

            {/* Columns */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-700">
              <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Columnas detectadas
              </h4>
              <div className="flex flex-wrap gap-2">
                {dataset.columns.map((col) => (
                  <span
                    key={col}
                    className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>

            {/* Validation Status */}
            {validationResult && (
              <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Validación
                </h4>
                <div className="flex items-center gap-2">
                  {validationResult.valid ? (
                    <>
                      <Check className="w-4 h-4 text-green-600" />
                      <span className="text-sm text-green-600 dark:text-green-400">
                        Dataset válido y listo para análisis
                      </span>
                    </>
                  ) : (
                    <>
                      <X className="w-4 h-4 text-red-600" />
                      <span className="text-sm text-red-600 dark:text-red-400">
                        {validationResult.error}
                      </span>
                    </>
                  )}
                </div>
                {validationResult.missingColumns.length > 0 && (
                  <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-2">
                    Columnas faltantes: {validationResult.missingColumns.join(', ')}
                  </p>
                )}
              </div>
            )}

            {/* Preview */}
            {previewData && previewData.length > 0 && (
              <div className="p-4">
                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Vista previa (primeras 5 filas)
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-700">
                        {Object.keys(previewData[0]).map((key) => (
                          <th
                            key={key}
                            className="text-left p-2 font-medium text-slate-600 dark:text-slate-400"
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
                              className="p-2 text-slate-700 dark:text-slate-300 max-w-xs truncate"
                            >
                              {String(value)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </PageLayout>
  );
}

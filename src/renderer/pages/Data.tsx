/**
 * Data Page
 * ==========
 * Dataset upload, column mapping, and preview
 */

import React, { useCallback, useEffect, useState } from 'react';
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
import { ColumnMappingDialog } from '../components/ColumnMappingDialog';
import { DatasetChangeDialog } from '../components/DatasetChangeDialog';
import { cn } from '../lib/utils';
import { useDataStore } from '../stores/dataStore';
import { usePipelineStore } from '../stores/pipelineStore';
import type { DatasetValidation, ColumnMapping } from '../../shared/types';

export function Data() {
  const {
    dataset,
    isValidating,
    validationResult,
    previewData,
    datasetFingerprint,
    setDataset,
    setDatasetFingerprint,
    setValidating,
    setValidationResult,
    setPreviewData,
    setOutputPaths,
    clearDataset,
  } = useDataStore();

  const { setDataset: setPipelineDataset, reset: resetPipeline } = usePipelineStore();
  const [error, setError] = useState<string | null>(null);

  // Column mapping state
  const [showMapping, setShowMapping] = useState(false);
  const [isMappingApplying, setIsMappingApplying] = useState(false);
  const [pendingFilePath, setPendingFilePath] = useState<string | null>(null);
  const [pendingValidation, setPendingValidation] = useState<DatasetValidation | null>(null);

  // Dataset change detection state
  const [showChangeDialog, setShowChangeDialog] = useState(false);
  const [pendingAcceptFilePath, setPendingAcceptFilePath] = useState<string | null>(null);
  const [pendingAcceptValidation, setPendingAcceptValidation] = useState<DatasetValidation | null>(null);
  const [isCleaningData, setIsCleaningData] = useState(false);

  // On mount, if a dataset is persisted but preview data is missing, re-validate to restore it
  useEffect(() => {
    if (dataset && (!previewData || previewData.length === 0)) {
      (async () => {
        try {
          const validation = await window.electronAPI.pipeline.validateDataset(dataset.path);
          if (validation.valid && validation.preview) {
            setPreviewData(validation.preview);
            setValidationResult(validation);
          }
        } catch {
          // Silently ignore — the file may have been moved/deleted
        }
      })();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      // Note: In Electron, we can't get the actual file path from dropped files
      // The dropzone is used only for UI feedback, actual file selection happens via dialog
      // Do nothing here - file selection is handled by handleSelectFile
    },
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    noClick: true, // Disable click to open file dialog - we use our own button
    noKeyboard: true, // Disable keyboard events
  });

  const handleSelectFile = async () => {
    setError(null);
    setValidating(true);
    setShowMapping(false);

    try {
      const filePath = await window.electronAPI.files.selectFile({
        filters: [{ name: 'CSV Files', extensions: ['csv'] }],
      });

      if (!filePath) {
        setValidating(false);
        return;
      }

      const validation = await window.electronAPI.pipeline.validateDataset(filePath);

      if (validation.columns && validation.columns.length > 0) {
        // Always show the column mapping step so the user can configure it
        setPendingFilePath(filePath);
        setPendingValidation(validation);
        setPreviewData(validation.preview || null);
        setShowMapping(true);
      } else {
        // File has no columns at all — show error
        setValidationResult(validation);
        setError(
          validation.error || 'El archivo no contiene columnas válidas.'
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dataset');
    } finally {
      setValidating(false);
    }
  };

  /**
   * Generate a fingerprint for a dataset to detect changes.
   * Uses file name + row count + column names as a unique identifier.
   */
  const generateFingerprint = (fileName: string, validation: DatasetValidation): string => {
    const cols = [...validation.columns].sort().join(',');
    return `${fileName}::${validation.rowCount}::${cols}`;
  };

  /**
   * Accept a dataset (either directly valid or after mapping) and persist it.
   * Checks if the dataset is different from the previous one and shows a warning if so.
   */
  const acceptDataset = async (filePath: string, validation: DatasetValidation) => {
    const fileName = filePath.replace(/\\/g, '/').split('/').pop() || 'dataset.csv';
    const newFingerprint = generateFingerprint(fileName, validation);

    // Check if there's a previous dataset with a different fingerprint
    if (datasetFingerprint && datasetFingerprint !== newFingerprint) {
      // Dataset has changed — show confirmation dialog
      setPendingAcceptFilePath(filePath);
      setPendingAcceptValidation(validation);
      setShowChangeDialog(true);
      return;
    }

    await finalizeDatasetAcceptance(filePath, validation);
  };

  /**
   * Finalize dataset acceptance after all checks pass.
   */
  const finalizeDatasetAcceptance = async (filePath: string, validation: DatasetValidation) => {
    const pythonDataDir = await window.electronAPI.app.getPythonDataDir();
    const fileName = filePath.replace(/\\/g, '/').split('/').pop() || 'dataset.csv';
    const fingerprint = generateFingerprint(fileName, validation);

    setDataset({
      path: filePath,
      name: fileName,
      rows: validation.rowCount,
      columns: validation.columns,
      sampleData: validation.preview,
      validationStatus: 'valid',
      validationMessages: [],
    });
    setDatasetFingerprint(fingerprint);
    setValidationResult(validation);
    setPreviewData(validation.preview || null);
    setPipelineDataset(filePath);

    setOutputPaths({
      output: `${pythonDataDir}/dataset.csv`,
      charts: `${pythonDataDir}/visualizaciones`,
      summary: `${pythonDataDir}/shared/resumenes.json`,
    });

    // Clean up mapping state
    setShowMapping(false);
    setPendingFilePath(null);
    setPendingValidation(null);
  };

  /**
   * Handle confirmation of dataset change — clean old data and accept new dataset.
   */
  const handleConfirmDatasetChange = async () => {
    if (!pendingAcceptFilePath || !pendingAcceptValidation) return;

    setShowChangeDialog(false);
    setIsCleaningData(true);
    setError(null);

    try {
      // Clean up previous pipeline data on disk
      const pythonDataDir = await window.electronAPI.app.getPythonDataDir();
      await window.electronAPI.files.cleanDatasetData(pythonDataDir);

      // Reset pipeline progress (all phases back to pending)
      resetPipeline();

      // Accept the new dataset
      await finalizeDatasetAcceptance(pendingAcceptFilePath, pendingAcceptValidation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al limpiar datos anteriores');
    } finally {
      setIsCleaningData(false);
      setPendingAcceptFilePath(null);
      setPendingAcceptValidation(null);
    }
  };

  /**
   * Handle cancellation of dataset change dialog.
   */
  const handleCancelDatasetChange = () => {
    setShowChangeDialog(false);
    setPendingAcceptFilePath(null);
    setPendingAcceptValidation(null);
    // Also clean up column mapping state if it was mid-flow
    setShowMapping(false);
    setPendingFilePath(null);
    setPendingValidation(null);
  };

  /**
   * Handle column mapping confirmation — apply the mapping and re-validate.
   */
  const handleApplyMapping = async (mapping: ColumnMapping) => {
    if (!pendingFilePath) return;

    setIsMappingApplying(true);
    setError(null);

    try {
      const result = await window.electronAPI.pipeline.applyColumnMapping(pendingFilePath, mapping);

      if (!result.success) {
        setError(result.error || 'Error al aplicar el mapeo de columnas');
        setIsMappingApplying(false);
        return;
      }

      // Re-validate the mapped file
      const mappedPath = result.outputPath!;
      const reValidation = await window.electronAPI.pipeline.validateDataset(mappedPath);

      if (reValidation.valid) {
        await acceptDataset(mappedPath, reValidation);
      } else {
        setError(
          `El archivo mapeado aún no cumple los requisitos. Columnas faltantes: ${reValidation.missingColumns.join(', ')}`
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al aplicar mapeo');
    } finally {
      setIsMappingApplying(false);
    }
  };

  const handleCancelMapping = () => {
    setShowMapping(false);
    setPendingFilePath(null);
    setPendingValidation(null);
  };

  const handleClearDataset = () => {
    clearDataset();
    setDatasetFingerprint(null);
    setPipelineDataset(undefined);
    setError(null);
    setShowMapping(false);
    setPendingFilePath(null);
    setPendingValidation(null);
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

        {/* Column Mapping Dialog */}
        {showMapping && pendingValidation && pendingFilePath && (
          <ColumnMappingDialog
            fileName={pendingFilePath.replace(/\\/g, '/').split('/').pop() || 'dataset.csv'}
            sourceColumns={pendingValidation.columns}
            rowCount={pendingValidation.rowCount}
            previewData={pendingValidation.preview}
            isApplying={isMappingApplying}
            onApply={handleApplyMapping}
            onCancel={handleCancelMapping}
          />
        )}

        {/* Dataset Change Warning Dialog */}
        <DatasetChangeDialog
          open={showChangeDialog}
          previousDataset={dataset?.name || 'dataset anterior'}
          newDataset={
            (pendingAcceptFilePath || pendingFilePath || '')
              .replace(/\\/g, '/')
              .split('/')
              .pop() || 'nuevo dataset'
          }
          onConfirm={handleConfirmDatasetChange}
          onCancel={handleCancelDatasetChange}
        />

        {/* Cleaning data indicator */}
        {isCleaningData && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-amber-700 dark:text-amber-300">
              Limpiando datos del dataset anterior...
            </p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
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
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleSelectFile} disabled={isValidating || isCleaningData}>
                  <Upload className="w-4 h-4 mr-2" />
                  {isCleaningData ? 'Limpiando...' : 'Cambiar Dataset'}
                </Button>
                <Button variant="outline" size="sm" onClick={handleClearDataset}>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Eliminar
                </Button>
              </div>
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

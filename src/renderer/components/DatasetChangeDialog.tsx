/**
 * Dataset Change Dialog
 * ======================
 * Warning dialog shown when the user loads a new dataset different from the previous one.
 * Warns about data deletion and asks for backup confirmation before proceeding.
 */

import React, { useState } from 'react';
import { AlertTriangle, Trash2, ShieldCheck, X } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';

interface DatasetChangeDialogProps {
  open: boolean;
  previousDataset: string;
  newDataset: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function DatasetChangeDialog({
  open,
  previousDataset,
  newDataset,
  onConfirm,
  onCancel,
}: DatasetChangeDialogProps) {
  const [backupAcknowledged, setBackupAcknowledged] = useState(false);

  const handleConfirm = () => {
    setBackupAcknowledged(false);
    onConfirm();
  };

  const handleCancel = () => {
    setBackupAcknowledged(false);
    onCancel();
  };

  return (
    <Dialog.Root open={open} onOpenChange={(isOpen) => !isOpen && handleCancel()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in-0" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 animate-in zoom-in-95 fade-in-0">
          <div className="p-6">
            {/* Header */}
            <div className="flex items-start gap-4 mb-4">
              <div className="shrink-0 w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
              </div>
              <div className="flex-1">
                <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Cambio de Dataset Detectado
                </Dialog.Title>
                <Dialog.Description className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Estás a punto de cargar un dataset diferente al anterior. Esto eliminará todos los datos generados previamente.
                </Dialog.Description>
              </div>
              <Dialog.Close
                onClick={handleCancel}
                className="shrink-0 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 dark:ring-offset-gray-950 dark:focus:ring-gray-800"
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Cerrar</span>
              </Dialog.Close>
            </div>

            {/* Dataset comparison */}
            <div className="mb-4 space-y-2">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
                <Trash2 className="w-4 h-4 text-red-500 dark:text-red-400 shrink-0" />
                <div className="text-sm">
                  <span className="text-red-700 dark:text-red-300 font-medium">Dataset anterior: </span>
                  <span className="text-red-600 dark:text-red-400">{previousDataset}</span>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <ShieldCheck className="w-4 h-4 text-blue-500 dark:text-blue-400 shrink-0" />
                <div className="text-sm">
                  <span className="text-blue-700 dark:text-blue-300 font-medium">Nuevo dataset: </span>
                  <span className="text-blue-600 dark:text-blue-400">{newDataset}</span>
                </div>
              </div>
            </div>

            {/* Warning details */}
            <div className="mb-5 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
              <p className="text-sm font-medium text-amber-900 dark:text-amber-100 mb-2">
                Se eliminarán los siguientes datos:
              </p>
              <ul className="text-sm text-amber-800 dark:text-amber-200 space-y-1 list-disc list-inside">
                <li>Todas las visualizaciones e imágenes generadas</li>
                <li>Resúmenes inteligentes y puntuaciones de categorías</li>
                <li>El dataset procesado con las columnas de análisis</li>
                <li>Copias de seguridad del pipeline</li>
                <li>Todo el progreso de las fases del pipeline</li>
              </ul>
            </div>

            {/* Backup acknowledgment */}
            <label className="flex items-start gap-3 mb-5 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <input
                type="checkbox"
                checked={backupAcknowledged}
                onChange={(e) => setBackupAcknowledged(e.target.checked)}
                className="mt-0.5 w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:bg-gray-600 dark:border-gray-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Confirmo que ya he creado una copia de respaldo de mis resultados anteriores o que no necesito conservarlos.
              </span>
            </label>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                disabled={!backupAcknowledged}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
              >
                Eliminar datos y continuar
              </button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

export default DatasetChangeDialog;

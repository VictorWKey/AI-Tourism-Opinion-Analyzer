import { AlertTriangle, X } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';
import type { PhaseValidation } from '@/shared/types';

interface DependencyModalProps {
  open: boolean;
  onClose: () => void;
  validation: PhaseValidation;
  currentPhase: number;
}

const PHASE_NAMES: Record<number, string> = {
  1: 'Procesamiento Básico',
  2: 'Análisis de Sentimientos',
  3: 'Análisis de Subjetividad',
  4: 'Clasificación de Categorías',
  5: 'Análisis Jerárquico de Tópicos',
  6: 'Resumen Inteligente',
  7: 'Visualizaciones',
};

export function DependencyModal({ open, onClose, validation, currentPhase }: DependencyModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in-0" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 animate-in zoom-in-95 fade-in-0">
          <div className="p-6">
            {/* Header */}
            <div className="flex items-start gap-4 mb-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
              </div>
              <div className="flex-1">
                <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Dependencias Requeridas
                </Dialog.Title>
                <Dialog.Description className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Para ejecutar la Fase {currentPhase}: {PHASE_NAMES[currentPhase]}, primero debes completar las
                  siguientes fases:
                </Dialog.Description>
              </div>
              <Dialog.Close className="flex-shrink-0 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-gray-100 dark:ring-offset-gray-950 dark:focus:ring-gray-800 dark:data-[state=open]:bg-gray-800">
                <X className="h-4 w-4" />
                <span className="sr-only">Cerrar</span>
              </Dialog.Close>
            </div>

            {/* Missing Phases List */}
            {validation.missingPhases && validation.missingPhases.length > 0 && (
              <div className="mb-4">
                <ul className="space-y-2">
                  {validation.missingPhases.map((phase) => (
                    <li
                      key={phase}
                      className="flex items-center gap-3 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-900 dark:text-amber-100"
                    >
                      <span className="flex-shrink-0 w-8 h-8 rounded-full bg-amber-200 dark:bg-amber-800 flex items-center justify-center text-sm font-bold">
                        {phase}
                      </span>
                      <span className="text-sm font-medium">{PHASE_NAMES[phase]}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
              >
                Entendido
              </button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

/**
 * Pipeline Page
 * ==============
 * Pipeline configuration and execution
 */

import React, { useState } from 'react';
import {
  Play,
  Square,
  Check,
  Loader2,
  AlertCircle,
  Clock,
  ChevronRight,
  Wrench,
  Smile,
  Brain,
  Folder,
  TreePine,
  FileText,
  BarChart3,
  AlertTriangle,
  Ban,
  Timer,
  ShieldAlert,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button, Progress } from '../components/ui';
import { DependencyModal } from '../components/pipeline/DependencyModal';
import { cn } from '../lib/utils';
import { usePipeline } from '../hooks/usePipeline';
import { useDataStore } from '../stores/dataStore';
import { useSettingsStore } from '../stores/settingsStore';
import { useOllama } from '../hooks/useOllama';
import { useToast } from '../hooks/useToast';
import type { PhaseValidation } from '@/shared/types';

const phaseDescriptions: Record<number, string> = {
  1: 'Limpieza y normalización del texto',
  2: 'Clasificación de sentimientos positivo/negativo/neutro',
  3: 'Detección de opiniones subjetivas vs objetivas',
  4: 'Clasificación en categorías turísticas',
  5: 'Extracción de tópicos jerárquicos con LLM',
  6: 'Generación de resúmenes inteligentes',
  7: 'Creación de gráficos y visualizaciones',
};

const phaseIcons: Record<number, React.ComponentType<{ className?: string }>> = {
  1: Wrench,
  2: Smile,
  3: Brain,
  4: Folder,
  5: TreePine,
  6: FileText,
  7: BarChart3,
};

interface PhaseCardProps {
  phase: number;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelling';
  progress: number;
  message?: string;
  error?: string;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  onRun: () => void;
  isRunning: boolean;
  hasDataset: boolean;
  isCancelling: boolean;
  warnings?: string[];
  isDisabledByMode?: boolean;
  disabledReason?: string;
}

function PhaseCard({
  phase,
  name,
  description,
  icon,
  status,
  progress,
  message,
  error,
  enabled,
  onToggle,
  onRun,
  isRunning,
  hasDataset,
  isCancelling,
  warnings,
  isDisabledByMode,
  disabledReason,
}: PhaseCardProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-50 dark:bg-green-900/20';
      case 'running':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
      case 'failed':
        return 'border-red-500 bg-red-50 dark:bg-red-900/20';
      case 'cancelling':
        return 'border-orange-500 bg-orange-50 dark:bg-orange-900/20';
      default:
        return 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <Check className="w-5 h-5 text-green-600" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'cancelling':
        return <Loader2 className="w-5 h-5 text-orange-600 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div
      className={cn(
        'rounded-xl border-2 p-4 transition-all',
        isDisabledByMode ? 'border-slate-300 dark:border-slate-600 bg-slate-100 dark:bg-slate-800/50 opacity-60' : getStatusColor(),
        !enabled && !isDisabledByMode && 'opacity-50'
      )}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox - Only show when dataset loaded */}
        {hasDataset && (
          <label className="flex items-center gap-2 cursor-pointer shrink-0 pt-1">
            <input
              type="checkbox"
              checked={enabled && !isDisabledByMode}
              onChange={(e) => onToggle(e.target.checked)}
              className="w-4 h-4 rounded border-slate-300"
              disabled={isRunning || isDisabledByMode}
            />
          </label>
        )}

        {/* Phase Icon */}
        {icon && (
          <div className={cn("shrink-0", isDisabledByMode ? "text-slate-400 dark:text-slate-500" : "text-slate-600 dark:text-slate-300")}>
            {React.createElement(icon, { className: 'w-8 h-8' })}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className={cn("font-medium", isDisabledByMode ? "text-slate-500 dark:text-slate-400" : "text-slate-900 dark:text-white")}>
              Fase {phase}: {name}
            </h3>
            {isDisabledByMode ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                <Ban className="w-3 h-3" />
                No disponible
              </span>
            ) : (
              getStatusIcon()
            )}
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {description}
          </p>

          {/* Disabled by mode reason */}
          {isDisabledByMode && disabledReason && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 italic">
              {disabledReason}
            </p>
          )}

          {/* Warnings */}
          {warnings && warnings.length > 0 && !isDisabledByMode && (
            <div className="mt-2 space-y-1">
              {warnings.map((w, i) => (
                <div key={i} className="flex items-start gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                  <p className="text-xs text-amber-700 dark:text-amber-400">{w}</p>
                </div>
              ))}
            </div>
          )}

          {/* Progress */}
          {status === 'running' && (
            <div className="mt-3">
              <Progress value={progress} className="h-2" />
              {message && (
                <p className="text-xs text-slate-500 mt-1">{message}</p>
              )}
            </div>
          )}

          {/* Cancelling message */}
          {status === 'cancelling' && (
            <p className="text-sm text-orange-600 dark:text-orange-400 mt-2">
              {message || 'Cancelando fase...'}
            </p>
          )}

          {/* Error - only show if not cancelling */}
          {error && status !== 'cancelling' && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-2">
              Error: {error}
            </p>
          )}
        </div>

        {/* Actions - Run Button */}
        {hasDataset && !isDisabledByMode && (
          <Button
            size="sm"
            onClick={onRun}
            disabled={!enabled || isRunning || isCancelling}
            className={cn(
              'transition-all shrink-0',
              !enabled || isRunning || isCancelling ? 'opacity-50 cursor-not-allowed' : ''
            )}
          >
            <Play className="w-4 h-4 mr-1" />
            Ejecutar
          </Button>
        )}
      </div>
    </div>
  );
}

export function Pipeline() {
  const {
    isRunning,
    currentPhase,
    phases,
    config,
    overallProgress,
    completedCount,
    runPhase,
    runAll,
    stop,
    setPhaseEnabled,
    reset,
  } = usePipeline();

  const { dataset } = useDataStore();
  const { llm } = useSettingsStore();
  const { models } = useOllama();
  const { success, warning } = useToast();
  const [isStopping, setIsStopping] = useState(false);

  // Compute whether the current local model is small (< 10GB)
  const isSmallLocalModel = (() => {
    if (llm.mode !== 'local') return false;
    const selectedModel = models?.find(m => m.name === llm.localModel);
    if (!selectedModel) return false;
    return selectedModel.size / (1024 * 1024 * 1024) < 10;
  })();

  const isNoLLMMode = llm.mode === 'none';

  // Compute warnings and disabled state for each phase
  const getPhaseWarnings = (phaseNum: number): string[] => {
    const warnings: string[] = [];
    
    if (phaseNum === 6) {
      if (llm.mode !== 'none') {
        warnings.push('Esta fase puede tardar bastante tiempo debido a la complejidad de resumir múltiples reseñas. Dependiendo del dataset y modelo, puede durar de varios minutos a más de una hora.');
      }
      if (isSmallLocalModel) {
        warnings.push('El modelo local seleccionado es pequeño (< 10 GB). La calidad de los resúmenes puede verse afectada. Se recomienda usar modo API para mejores resultados.');
      }
    }
    
    if (phaseNum === 5 && isSmallLocalModel) {
      warnings.push('El modelo local seleccionado es pequeño (< 10 GB). La calidad del análisis de tópicos puede verse afectada.');
    }

    if (phaseNum === 7 && isNoLLMMode) {
      warnings.push('Sin LLM activo: las visualizaciones de tópicos y resúmenes no se generarán.');
    }
    
    return warnings;
  };

  const isPhaseDisabledByMode = (phaseNum: number): boolean => {
    return isNoLLMMode && (phaseNum === 5 || phaseNum === 6);
  };

  const getDisabledReason = (phaseNum: number): string | undefined => {
    if (isNoLLMMode && phaseNum === 5) return 'Requiere un modelo de lenguaje (LLM). Configura uno en Ajustes.';
    if (isNoLLMMode && phaseNum === 6) return 'Requiere un modelo de lenguaje (LLM). Configura uno en Ajustes.';
    return undefined;
  };
  const [validationModal, setValidationModal] = useState<{
    open: boolean;
    validation: PhaseValidation | null;
    phase: number;
  }>({
    open: false,
    validation: null,
    phase: 0,
  });

  const handleRunAll = async () => {
    if (!dataset) {
      warning('Dataset requerido', 'Por favor, carga un dataset primero');
      return;
    }
    await runAll();
  };

  const handleRunPhase = async (phase: number) => {
    if (!dataset) {
      warning('Dataset requerido', 'Por favor, carga un dataset primero');
      return;
    }
    
    const result = await runPhase(phase);
    
    // Check if validation failed
    if (!result.success && result.validation && !result.validation.canRun) {
      setValidationModal({
        open: true,
        validation: result.validation,
        phase,
      });
    }
  };

  const handleStop = async () => {
    setIsStopping(true);
    try {
      const result = await stop();
      if (result.rolledBack) {
        success(
          'Pipeline detenido',
          'Los cambios parciales han sido revertidos. El sistema está en su estado anterior.'
        );
      } else {
        success('Pipeline detenido', 'La ejecución ha sido detenida.');
      }
    } finally {
      setIsStopping(false);
    }
  };

  return (
    <PageLayout
      title="Pipeline"
      description="Configura y ejecuta las fases de análisis"
      headerActions={
        <div className="flex items-center gap-2">
          {isRunning ? (
            <Button variant="destructive" onClick={handleStop} disabled={isStopping}>
              {isStopping ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Square className="w-4 h-4 mr-2" />
              )}
              {isStopping ? 'Deteniendo...' : 'Detener'}
            </Button>
          ) : (
            <>
              <Button variant="outline" onClick={reset} disabled={completedCount === 0}>
                Reiniciar
              </Button>
              <Button onClick={handleRunAll} disabled={!dataset || Object.values(phases).some((p) => p.status === 'cancelling')}>
                <Play className="w-4 h-4 mr-2" />
                Ejecutar Todo
              </Button>
            </>
          )}
        </div>
      }
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {/* No LLM Mode Warning */}
        {isNoLLMMode && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 flex items-start gap-3">
            <Ban className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
                Modo sin LLM activo
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
                Las fases 5 y 6 están deshabilitadas. Algunas visualizaciones de la fase 7 no se generarán.
                Puedes cambiar el modo en Configuración.
              </p>
            </div>
          </div>
        )}

        {/* Dataset Warning */}
        {!dataset && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            <p className="text-sm text-yellow-700 dark:text-yellow-300">
              Carga un dataset en la sección "Datos" antes de ejecutar el pipeline.
            </p>
          </div>
        )}

        {/* Phase Cards */}
        <div className="space-y-4">
          {Object.values(phases)
            .filter((phase) => phase.phase >= 1 && phase.phase <= 7)
            .map((phase) => {
            const phaseKey = `phase_${String(phase.phase).padStart(2, '0')}` as keyof typeof config.phases;
            const isCancellingAny = Object.values(phases).some((p) => p.status === 'cancelling');
            const disabledByMode = isPhaseDisabledByMode(phase.phase);
            return (
              <PhaseCard
                key={phase.phase}
                phase={phase.phase}
                name={phase.phaseName}
                description={phaseDescriptions[phase.phase]}
                icon={phaseIcons[phase.phase]}
                status={phase.status}
                progress={phase.progress}
                message={phase.message}
                error={phase.error}
                enabled={disabledByMode ? false : config.phases[phaseKey]}
                onToggle={(enabled) => {
                  if (!disabledByMode) setPhaseEnabled(phase.phase, enabled);
                }}
                onRun={() => handleRunPhase(phase.phase)}
                isRunning={isRunning}
                hasDataset={!!dataset}
                isCancelling={isCancellingAny}
                warnings={getPhaseWarnings(phase.phase)}
                isDisabledByMode={disabledByMode}
                disabledReason={getDisabledReason(phase.phase)}
              />
            );
          })}
        </div>

        {/* Completion Summary */}
        {completedCount === 7 && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4 flex items-center gap-3">
            <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
            <div>
              <p className="font-medium text-green-900 dark:text-green-100">
                ¡Análisis completado!
              </p>
              <p className="text-sm text-green-700 dark:text-green-300">
                Todas las fases se han ejecutado correctamente. Revisa los resultados y visualizaciones.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Dependency Validation Modal */}
      {validationModal.validation && (
        <DependencyModal
          open={validationModal.open}
          onClose={() => setValidationModal({ open: false, validation: null, phase: 0 })}
          validation={validationModal.validation}
          currentPhase={validationModal.phase}
        />
      )}
    </PageLayout>
  );
}

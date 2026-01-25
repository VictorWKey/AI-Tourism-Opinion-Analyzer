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
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button, Progress } from '../components/ui';
import { cn } from '../lib/utils';
import { usePipeline } from '../hooks/usePipeline';
import { useDataStore } from '../stores/dataStore';
import { useToast } from '../hooks/useToast';

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
        getStatusColor(),
        !enabled && 'opacity-50'
      )}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox - Only show when dataset loaded */}
        {hasDataset && (
          <label className="flex items-center gap-2 cursor-pointer flex-shrink-0 pt-1">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => onToggle(e.target.checked)}
              className="w-4 h-4 rounded border-slate-300"
              disabled={isRunning}
            />
          </label>
        )}

        {/* Phase Icon */}
        {icon && (
          <div className="text-slate-600 dark:text-slate-300 flex-shrink-0">
            {React.createElement(icon, { className: 'w-8 h-8' })}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-slate-900 dark:text-white">
              Fase {phase}: {name}
            </h3>
            {getStatusIcon()}
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {description}
          </p>

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
        {hasDataset && (
          <Button
            size="sm"
            onClick={onRun}
            disabled={!enabled || isRunning || isCancelling}
            className={cn(
              'transition-all flex-shrink-0',
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
  const { success, warning } = useToast();
  const [isStopping, setIsStopping] = useState(false);

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
    await runPhase(phase);
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
          {Object.values(phases).map((phase) => {
            const phaseKey = `phase_${String(phase.phase).padStart(2, '0')}` as keyof typeof config.phases;
            const isCancellingAny = Object.values(phases).some((p) => p.status === 'cancelling');
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
                enabled={config.phases[phaseKey]}
                onToggle={(enabled) => setPhaseEnabled(phase.phase, enabled)}
                onRun={() => handleRunPhase(phase.phase)}
                isRunning={isRunning}
                hasDataset={!!dataset}
                isCancelling={isCancellingAny}
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
    </PageLayout>
  );
}

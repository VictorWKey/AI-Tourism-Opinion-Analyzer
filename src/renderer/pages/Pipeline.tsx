/**
 * Pipeline Page
 * ==============
 * Pipeline configuration and execution
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Play,
  Square,
  Check,
  Loader2,
  AlertCircle,
  Clock,
  ChevronRight,
  Wrench,
  BarChart2,
  Smile,
  Brain,
  Folder,
  TreePine,
  FileText,
  BarChart3,
  Lightbulb,
  AlertTriangle,
  Ban,
  Timer,
  ShieldAlert,
  Settings2,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button, Progress, Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/ui';
import { DependencyModal } from '../components/pipeline/DependencyModal';
import { cn } from '../lib/utils';
import { usePipeline } from '../hooks/usePipeline';
import { useDataStore } from '../stores/dataStore';
import { useSettingsStore } from '../stores/settingsStore';
import { useOllama } from '../hooks/useOllama';
import { useToast } from '../hooks/useToast';
import type { PhaseValidation } from '@/shared/types';

/** Format duration in milliseconds to a human-readable string */
function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  if (minutes > 0) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

/** Live elapsed timer that updates every second */
function LiveTimer({ startedAt }: { startedAt: string }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const startMs = new Date(startedAt).getTime();
    const tick = () => setElapsed(Date.now() - startMs);
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [startedAt]);

  return (
    <span className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 font-mono">
      <Timer className="w-3 h-3" />
      {formatDuration(elapsed)}
    </span>
  );
}

const phaseDescriptions: Record<number, string> = {
  1: 'Limpieza y normalización del texto',
  2: 'Genera estadísticas descriptivas básicas del dataset sin modelos de ML',
  3: 'Clasificación de sentimientos positivo/negativo/neutro',
  4: 'Clasificación binaria de subjetividad: Subjetiva vs Mixta (subjetiva + objetiva)',
  5: 'Clasificación en categorías turísticas',
  6: 'Extracción de tópicos jerárquicos con LLM',
  7: 'Generación de resúmenes inteligentes',
  8: 'Análisis estratégico basado en datos con LLM',
  9: 'Generación de visualizaciones y exportación de métricas analíticas',
};

const phaseIcons: Record<number, React.ComponentType<{ className?: string }>> = {
  1: Wrench,
  2: BarChart2,
  3: Smile,
  4: Brain,
  5: Folder,
  6: TreePine,
  7: FileText,
  8: Lightbulb,
  9: BarChart3,
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
  onConfigure?: () => void;
  isRunning: boolean;
  hasDataset: boolean;
  isCancelling: boolean;
  warnings?: string[];
  isDisabledByMode?: boolean;
  disabledReason?: string;
  startedAt?: string;
  completedAt?: string;
  duration?: number;
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
  onConfigure,
  isRunning,
  hasDataset,
  isCancelling,
  warnings,
  isDisabledByMode,
  disabledReason,
  startedAt,
  completedAt,
  duration,
}: PhaseCardProps) {
  const { t } = useTranslation('pipeline');

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
              {t('phaseLabel', { phase, name })}
            </h3>
            {isDisabledByMode ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                <Ban className="w-3 h-3" />
                {t('notAvailable')}
              </span>
            ) : (
              <>
                {getStatusIcon()}
                {/* Live timer for running phase */}
                {status === 'running' && startedAt && (
                  <LiveTimer startedAt={startedAt} />
                )}
                {/* Completed/failed duration */}
                {(status === 'completed' || status === 'failed') && duration !== undefined && duration > 0 && (
                  <span className={cn(
                    'inline-flex items-center gap-1 text-xs font-mono',
                    status === 'completed' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  )}>
                    <Timer className="w-3 h-3" />
                    {formatDuration(duration)}
                  </span>
                )}
                {/* Warning Icon with Tooltip */}
                {warnings && warnings.length > 0 && (
                  <TooltipProvider delayDuration={200}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="cursor-help">
                          <AlertTriangle className="w-4 h-4 text-amber-500 hover:text-amber-600 transition-colors" />
                        </div>
                      </TooltipTrigger>
                      <TooltipContent side="right" className="max-w-sm">
                        <div className="space-y-1.5">
                          {warnings.map((w, i) => (
                            <p key={i} className="text-xs leading-relaxed">{w}</p>
                          ))}
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
              </>
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
              {message || t('cancelling')}
            </p>
          )}

          {/* Error - only show if not cancelling */}
          {error && status !== 'cancelling' && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-2">
              Error: {error}
            </p>
          )}
        </div>

        {/* Actions - Configure + Run Button */}
        <div className="flex items-center gap-1.5 shrink-0">
          {/* Configure button (phase 7 only) */}
          {onConfigure && !isDisabledByMode && (
            <TooltipProvider delayDuration={200}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={onConfigure}
                    disabled={isRunning || isCancelling}
                    className={cn(
                      'p-2 rounded-lg border border-slate-200 dark:border-slate-600 transition-all',
                      'hover:bg-slate-100 dark:hover:bg-slate-700 hover:border-slate-300 dark:hover:border-slate-500',
                      (isRunning || isCancelling) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                    )}
                  >
                    <Settings2 className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="left">
                  <p className="text-xs">{t('configureTooltip')}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
          {/* Run Button */}
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
    pipelineStartedAt,
    pipelineDuration,
    runPhase,
    runAll,
    stop,
    setPhaseEnabled,
    reset,
  } = usePipeline();

  const { dataset } = useDataStore();
  const { llm } = useSettingsStore();
  const { models, isRunning: ollamaRunning } = useOllama();
  const { success, warning } = useToast();
  const { t } = useTranslation('pipeline');
  const [isStopping, setIsStopping] = useState(false);

  // Compute whether Ollama is needed but unavailable
  const isLocalMode = llm.mode === 'local';
  const isOllamaOffline = isLocalMode && !ollamaRunning;
  const hasNoModels = isLocalMode && ollamaRunning && (!models || models.length === 0);
  const selectedModelMissing = isLocalMode && ollamaRunning && models && models.length > 0 && !models.find(m => m.name === llm.localModel);
  const isLocalLLMUnavailable = isOllamaOffline || hasNoModels || !!selectedModelMissing;

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
    
    if (phaseNum === 7) {
      if (llm.mode !== 'none' && !isLocalLLMUnavailable) {
        warnings.push(t('phaseWarnings.phase7Slow'));
      }
      if (isSmallLocalModel) {
        warnings.push(t('phaseWarnings.smallModelSummary'));
      }
    }
    
    if (phaseNum === 6 && isSmallLocalModel) {
      warnings.push(t('phaseWarnings.smallModelTopics'));
    }

    if (phaseNum === 8) {
      if (llm.mode !== 'none' && !isLocalLLMUnavailable) {
        warnings.push(t('phaseWarnings.phase8Slow'));
      }
    }

    if (phaseNum === 9 && (isNoLLMMode || isLocalLLMUnavailable)) {
      warnings.push(t('phaseWarnings.noLlmPhase9'));
    }
    
    return warnings;
  };

  const isPhaseDisabledByMode = (phaseNum: number): boolean => {
    if (phaseNum !== 6 && phaseNum !== 7 && phaseNum !== 8) return false;
    if (isNoLLMMode) return true;
    if (isLocalLLMUnavailable) return true;
    return false;
  };

  const getDisabledReason = (phaseNum: number): string | undefined => {
    if (phaseNum !== 6 && phaseNum !== 7) return undefined;
    if (isNoLLMMode) return t('disabledReason.noLlm');
    if (isOllamaOffline) return t('disabledReason.ollamaOffline');
    if (hasNoModels) return t('disabledReason.noModels');
    if (selectedModelMissing) return t('disabledReason.modelMissing', { model: llm.localModel });
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
      warning(t('toast.datasetRequiredTitle'), t('toast.datasetRequiredDesc'));
      return;
    }
    await runAll();
  };

  const handleRunPhase = async (phase: number) => {
    if (!dataset) {
      warning(t('toast.datasetRequiredTitle'), t('toast.datasetRequiredDesc'));
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
          t('toast.stoppedTitle'),
          t('toast.stoppedRolledBack')
        );
      } else {
        success(t('toast.stoppedTitle'), t('toast.stoppedDesc'));
      }
    } finally {
      setIsStopping(false);
    }
  };

  return (
    <PageLayout
      title={t('title')}
      description={t('description')}
      headerActions={
        <div className="flex items-center gap-2">
          {isRunning ? (
            <Button variant="destructive" onClick={handleStop} disabled={isStopping}>
              {isStopping ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Square className="w-4 h-4 mr-2" />
              )}
              {isStopping ? t('actions.stopping') : t('actions.stop')}
            </Button>
          ) : (
            <>
              <Button variant="outline" onClick={reset} disabled={completedCount === 0}>
                {t('actions.reset')}
              </Button>
              <Button onClick={handleRunAll} disabled={!dataset || Object.values(phases).some((p) => p.status === 'cancelling')}>
                <Play className="w-4 h-4 mr-2" />
                {t('actions.runAll')}
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
                {t('warnings.noLlmTitle')}
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
                {t('warnings.noLlmDesc')}
              </p>
            </div>
          </div>
        )}

        {/* Ollama Offline Warning */}
        {isLocalMode && isOllamaOffline && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800 dark:text-red-300">
                {t('warnings.ollamaOfflineTitle')}
              </p>
              <p className="text-xs text-red-700 dark:text-red-400 mt-1">
                {t('warnings.ollamaOfflineDesc')}
              </p>
            </div>
          </div>
        )}

        {/* No Models Warning */}
        {isLocalMode && !isOllamaOffline && hasNoModels && (
          <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-xl p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-orange-800 dark:text-orange-300">
                {t('warnings.noModelsTitle')}
              </p>
              <p className="text-xs text-orange-700 dark:text-orange-400 mt-1">
                {t('warnings.noModelsDesc')}
              </p>
            </div>
          </div>
        )}

        {/* Selected Model Missing Warning */}
        {isLocalMode && !isOllamaOffline && !hasNoModels && selectedModelMissing && (
          <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-xl p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-orange-800 dark:text-orange-300">
                {t('warnings.modelMissingTitle')}
              </p>
              <p className="text-xs text-orange-700 dark:text-orange-400 mt-1">
                {t('warnings.modelMissingDesc', { model: llm.localModel })}
              </p>
            </div>
          </div>
        )}

        {/* Dataset Warning */}
        {!dataset && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            <p className="text-sm text-yellow-700 dark:text-yellow-300">
              {t('warnings.noDataset')}
            </p>
          </div>
        )}

        {/* Pipeline Total Elapsed Time */}
        {(isRunning && pipelineStartedAt) && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Timer className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-800 dark:text-blue-300">
                {t('totalTime')}
              </span>
            </div>
            <LiveTimer startedAt={pipelineStartedAt} />
          </div>
        )}
        {(!isRunning && pipelineDuration !== null && pipelineDuration > 0) && (
          <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Timer className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {t('totalTime')}
              </span>
            </div>
            <span className="text-sm font-mono text-slate-600 dark:text-slate-400">
              {formatDuration(pipelineDuration)}
            </span>
          </div>
        )}

        {/* Phase Cards */}
        <div className="space-y-4">
          {Object.values(phases)
            .filter((phase) => phase.phase >= 1 && phase.phase <= 9)
            .map((phase) => {
            const phaseKey = `phase_${String(phase.phase).padStart(2, '0')}` as keyof typeof config.phases;
            const isCancellingAny = Object.values(phases).some((p) => p.status === 'cancelling');
            const disabledByMode = isPhaseDisabledByMode(phase.phase);
            return (
              <PhaseCard
                key={phase.phase}
                phase={phase.phase}
                name={t(`common:phases.${phase.phase}.name`)}
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
                startedAt={phase.startedAt}
                completedAt={phase.completedAt}
                duration={phase.duration}
              />
            );
          })}
        </div>

        {/* Completion Summary */}
        {completedCount === 9 && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4 flex items-center gap-3">
            <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
            <div>
              <p className="font-medium text-green-900 dark:text-green-100">
                {t('completed.title')}
              </p>
              <p className="text-sm text-green-700 dark:text-green-300">
                {t('completed.description')}
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

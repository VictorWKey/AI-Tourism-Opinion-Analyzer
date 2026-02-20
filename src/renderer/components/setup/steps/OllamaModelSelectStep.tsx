import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Monitor, ArrowLeft, ArrowRight, Zap, HardDrive, Cpu, Check } from 'lucide-react';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { cn } from '../../../lib/utils';
import { OLLAMA_MODELS, modelKey } from '../types';
import type { HardwareConfig } from '../types';

export function OllamaModelSelectStep({
  selectedModel,
  onSelectModel,
  customModel,
  onCustomModelChange,
  useCustom,
  onUseCustomChange,
  hardwareConfig,
  onNext,
  onBack,
}: {
  selectedModel: string;
  onSelectModel: (model: string) => void;
  customModel: string;
  onCustomModelChange: (model: string) => void;
  useCustom: boolean;
  onUseCustomChange: (use: boolean) => void;
  hardwareConfig: HardwareConfig;
  onNext: () => void;
  onBack: () => void;
}) {
  const totalRam = hardwareConfig.ram;
  const hasGPU = hardwareConfig.gpu === 'dedicated';
  const vram = hardwareConfig.vram || 0;
  const { t } = useTranslation('setup');

  const getRecommendedModel = () => {
    if (totalRam >= 32 || (hasGPU && vram >= 12)) return 'deepseek-r1:14b';
    if (totalRam >= 24 || (hasGPU && vram >= 10)) return 'deepseek-r1:8b';
    if (totalRam >= 16 || (hasGPU && vram >= 8)) return 'llama3.1:8b';
    if (totalRam >= 12 || (hasGPU && vram >= 6)) return 'mistral:7b';
    return 'mistral:7b';
  };

  const recommendedModel = getRecommendedModel();

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="ollama-model-select"
    >
      <div className="text-center mb-4 sm:mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-sky-100 to-blue-100 dark:from-sky-900/30 dark:to-blue-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Monitor className="w-7 h-7 sm:w-8 sm:h-8 text-sky-600 dark:text-sky-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('ollamaModelSelect.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mx-auto">
          {t('ollamaModelSelect.subtitle', { ram: totalRam })}
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {OLLAMA_MODELS.map((model) => {
          const isRecommended = model.id === recommendedModel;
          const canRun = totalRam >= model.minRam;
          
          return (
            <button
              key={model.id}
              onClick={() => {
                onUseCustomChange(false);
                onSelectModel(model.id);
              }}
              disabled={!canRun}
              className={cn(
                "w-full p-4 border-2 rounded-xl text-left transition-all flex items-start gap-4",
                !useCustom && selectedModel === model.id
                  ? "border-slate-900 bg-slate-50 dark:border-white dark:bg-slate-800"
                  : isRecommended
                    ? "border-emerald-400 dark:border-emerald-600 hover:border-emerald-500 dark:hover:border-emerald-500"
                    : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600",
                !canRun ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
              )}
            >
              <div className={cn(
                "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
                !useCustom && selectedModel === model.id
                  ? "border-slate-900 bg-slate-900 dark:border-white dark:bg-white"
                  : "border-slate-300 dark:border-slate-600"
              )}>
                {!useCustom && selectedModel === model.id && (
                  <Check className="w-3 h-3 text-white" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-slate-900 dark:text-white">{model.name}</span>
                  <span className="text-xs text-slate-400 dark:text-slate-500">{model.size}</span>
                  {isRecommended && (
                    <span className="text-xs px-2 py-0.5 border border-emerald-400 dark:border-emerald-600 text-emerald-700 dark:text-emerald-400 rounded-full font-medium">
                      {t('ollamaModelSelect.recommended')}
                    </span>
                  )}
                  {!canRun && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">
                      {t('ollamaModelSelect.requiresRam', { ram: model.minRam })}
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">{t(`ollamaModelDescriptions.${modelKey(model.id)}`)}</p>
                <div className="flex items-center gap-2 mt-2">
                  {model.performance === 'fast' && (
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <Zap className="w-3 h-3" /> {t('ollamaModelSelect.fast')}
                    </span>
                  )}
                  {model.performance === 'balanced' && (
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <HardDrive className="w-3 h-3" /> {t('ollamaModelSelect.balanced')}
                    </span>
                  )}
                  {model.performance === 'powerful' && (
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <Cpu className="w-3 h-3" /> {t('ollamaModelSelect.powerful')}
                    </span>
                  )}
                </div>
              </div>
            </button>
          );
        })}

        {/* Custom model option */}
        <div className={cn(
          "p-4 border-2 rounded-xl transition-all",
          useCustom ? "border-slate-900 bg-slate-50 dark:border-white dark:bg-slate-800" : "border-slate-200 dark:border-slate-700"
        )}>
          <button
            onClick={() => onUseCustomChange(true)}
            className="w-full flex items-start gap-4 text-left cursor-pointer"
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              useCustom ? "border-slate-900 bg-slate-900 dark:border-white dark:bg-white" : "border-slate-300 dark:border-slate-600"
            )}>
              {useCustom && <Check className="w-3 h-3 text-white dark:text-slate-900" />}
            </div>
            <div className="flex-1">
              <span className="font-medium text-slate-900 dark:text-white">{t('ollamaModelSelect.customModel')}</span>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('ollamaModelSelect.customHint')}</p>
            </div>
          </button>
          {useCustom && (
            <div className="mt-3 pl-9">
              <Input
                placeholder={t('ollamaModelSelect.customPlaceholder')}
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                className="w-full"
              />
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                {t('ollamaModelSelect.libraryHint')}{' '}
                <a href="https://ollama.com/library" target="_blank" rel="noopener noreferrer" className="text-slate-600 dark:text-slate-400 underline">
                  ollama.com/library
                </a>
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button 
          onClick={onNext} 
          disabled={useCustom && !customModel.trim()}
        >
          {t('nav.next')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

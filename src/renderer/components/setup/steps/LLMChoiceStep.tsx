import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  AlertCircle, Monitor, Cloud, ArrowLeft,
  Sparkles, Zap, Check, Circle, ChevronRight
} from 'lucide-react';
import { Button } from '../../ui/button';
import { cn } from '../../../lib/utils';
import type { HardwareConfig } from '../types';

export function LLMChoiceStep({ 
  onSelect,
  hardwareConfig,
  onBack,
}: { 
  onSelect: (choice: 'ollama' | 'openai') => void;
  hardwareConfig: HardwareConfig;
  onBack: () => void;
}) {
  const hasGoodRAM = hardwareConfig.ram >= 16;
  const hasMarginalRAM = hardwareConfig.ram >= 12 && hardwareConfig.ram < 16;
  const hasLowRAM = hardwareConfig.ram < 12;
  const hasGPU = hardwareConfig.gpu === 'dedicated';
  const vram = hardwareConfig.vram || 0;
  const { t } = useTranslation('setup');
  
  const recommendLocal = hasGoodRAM || (hasMarginalRAM && hasGPU && vram >= 6);
  const localWarning = hasLowRAM 
    ? t('llmChoice.localLowRam')
    : hasMarginalRAM && !hasGPU 
      ? t('llmChoice.localNoGpu')
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="llm-choice"
    >
      <div className="text-center mb-6 sm:mb-8">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-violet-100 to-indigo-100 dark:from-violet-900/30 dark:to-indigo-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Sparkles className="w-7 h-7 sm:w-8 sm:h-8 text-violet-600 dark:text-violet-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('llmChoice.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mx-auto px-4">
          {t('llmChoice.subtitle')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        {/* Ollama Option */}
        <button
          onClick={() => onSelect('ollama')}
          className={cn(
            "p-6 border-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-all text-left group relative cursor-pointer",
            recommendLocal 
              ? "border-emerald-400 dark:border-emerald-600" 
              : "border-slate-200 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-500",
            hasLowRAM && "opacity-70"
          )}
        >
          {recommendLocal && (
            <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 border border-emerald-400 dark:border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-white dark:bg-slate-900 rounded-full font-medium">
              {t('llmChoice.recommended')}
            </span>
          )}
          <Monitor className="w-7 h-7 text-slate-700 dark:text-slate-300 mb-3" />
          <h3 className="font-semibold text-lg text-slate-900 dark:text-white mb-1">{t('llmChoice.local')}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">{t('llmChoice.localDesc')}</p>
          <ul className="space-y-1.5 text-sm text-slate-600 dark:text-slate-300">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.localFreePrivate')}
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.localNoInternet')}
            </li>
            <li className={cn("flex items-center gap-2", !hasGoodRAM && "text-amber-600")}>
              {hasGoodRAM ? (
                <Check className="w-4 h-4 text-emerald-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-amber-500" />
              )}
              {t('llmChoice.localRequiresRam')}
            </li>
            {hasGPU && (
              <li className="flex items-center gap-2 text-emerald-600">
                <Zap className="w-4 h-4" />
                {t('llmChoice.localGpuDetected', { vram })}
              </li>
            )}
          </ul>
          {localWarning && (
            <div className="mt-3 p-2 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-xs text-amber-700 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {localWarning}
              </p>
            </div>
          )}
          <div className="mt-4 flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white">
            {t('llmChoice.select')}
            <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>

        {/* OpenAI Option */}
        <button
          onClick={() => onSelect('openai')}
          className={cn(
            "p-6 border-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-all text-left group relative cursor-pointer",
            !recommendLocal 
              ? "border-emerald-400 dark:border-emerald-600" 
              : "border-slate-200 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-500"
          )}
        >
          {!recommendLocal && (
            <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 border border-emerald-400 dark:border-emerald-600 text-emerald-700 dark:text-emerald-400 bg-white dark:bg-slate-900 rounded-full font-medium">
              {t('llmChoice.recommended')}
            </span>
          )}
          <Cloud className="w-7 h-7 text-slate-700 dark:text-slate-300 mb-3" />
          <h3 className="font-semibold text-lg text-slate-900 dark:text-white mb-1">{t('llmChoice.apiOpenai')}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">{t('llmChoice.apiCloudDesc')}</p>
          <ul className="space-y-1.5 text-sm text-slate-600 dark:text-slate-300">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.apiFastSetup')}
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.apiNoHardware')}
            </li>
            <li className="flex items-center gap-2">
              <Circle className="w-4 h-4 text-slate-300 dark:text-slate-600" />
              {t('llmChoice.apiPayPerUse')}
            </li>
          </ul>
          <div className="mt-4 flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white">
            {t('llmChoice.select')}
            <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>
      </div>

      <div className="flex justify-start">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
      </div>
    </motion.div>
  );
}

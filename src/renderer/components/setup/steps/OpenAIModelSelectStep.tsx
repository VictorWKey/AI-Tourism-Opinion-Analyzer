import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Cloud, ArrowLeft, ArrowRight, Check } from 'lucide-react';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { cn } from '../../../lib/utils';
import { OPENAI_MODELS, modelKey } from '../types';

export function OpenAIModelSelectStep({
  selectedModel,
  onSelectModel,
  customModel,
  onCustomModelChange,
  useCustom,
  onUseCustomChange,
  onNext,
  onBack,
}: {
  selectedModel: string;
  onSelectModel: (model: string) => void;
  customModel: string;
  onCustomModelChange: (model: string) => void;
  useCustom: boolean;
  onUseCustomChange: (use: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="openai-model-select"
    >
      <div className="text-center mb-4 sm:mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-teal-100 to-emerald-100 dark:from-teal-900/30 dark:to-emerald-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Cloud className="w-7 h-7 sm:w-8 sm:h-8 text-teal-600 dark:text-teal-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('openaiModelSelect.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mx-auto px-4">
          {t('openaiModelSelect.subtitle')}
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {OPENAI_MODELS.map((model) => (
          <button
            key={model.id}
            onClick={() => {
              onUseCustomChange(false);
              onSelectModel(model.id);
            }}
            className={cn(
              "w-full p-4 border-2 rounded-xl text-left transition-all flex items-start gap-4 cursor-pointer",
              !useCustom && selectedModel === model.id
                ? "border-slate-900 bg-slate-50 dark:border-white dark:bg-slate-800"
                : model.recommended
                  ? "border-emerald-400 dark:border-emerald-600 hover:border-emerald-500 dark:hover:border-emerald-500"
                  : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600"
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
                {model.recommended && (
                  <span className="text-xs px-2 py-0.5 border border-emerald-400 dark:border-emerald-600 text-emerald-700 dark:text-emerald-400 rounded-full font-medium">
                    {t('ollamaModelSelect.recommended')}
                  </span>
                )}
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full font-medium",
                  model.costTier === 'low' && "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400",
                  model.costTier === 'medium' && "bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400",
                  model.costTier === 'high' && "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400"
                )}>
                  {model.costTier === 'low' && t('openaiModelSelect.economical')}
                  {model.costTier === 'medium' && t('openaiModelSelect.moderate')}
                  {model.costTier === 'high' && t('openaiModelSelect.premium')}
                </span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t(`openaiModelDescriptions.${modelKey(model.id)}`)}</p>
            </div>
          </button>
        ))}

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
              <span className="font-medium text-slate-900 dark:text-white">{t('openaiModelSelect.customModel')}</span>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('openaiModelSelect.customHint')}</p>
            </div>
          </button>
          {useCustom && (
            <div className="mt-3 pl-9">
              <Input
                placeholder={t('openaiModelSelect.customPlaceholder')}
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                className="w-full"
              />
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

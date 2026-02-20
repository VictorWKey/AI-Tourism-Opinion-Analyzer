import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, AlertCircle, Download, ArrowLeft } from 'lucide-react';
import { Button } from '../../ui/button';
import { cn } from '../../../lib/utils';

export function ModelDownloadStep({
  progress,
  onStart,
  isLoading,
  onBack,
  onNext,
  error,
}: {
  progress: Record<string, number>;
  onStart: () => void;
  isLoading: boolean;
  onBack: () => void;
  onNext: () => void;
  error?: string | null;
}) {
  const { t } = useTranslation('setup');
  const [started, setStarted] = useState(false);
  const [animatedProgress, setAnimatedProgress] = useState<Record<string, number>>({});
  const [alreadyDownloaded, setAlreadyDownloaded] = useState(false);
  const [checkingModels, setCheckingModels] = useState(true);

  const modelKeys = ['sentiment', 'embeddings', 'subjectivity', 'categories'];

  useEffect(() => {
    window.electronAPI.setup.checkModels().then((status) => {
      const allAlreadyDownloaded = status.sentiment && status.embeddings && status.subjectivity && status.categories;
      if (allAlreadyDownloaded) {
        setAlreadyDownloaded(true);
        setStarted(true);
      }
      setCheckingModels(false);
    }).catch(() => {
      setCheckingModels(false);
    });
  }, []);

  const handleStart = () => {
    setStarted(true);
    onStart();
  };

  const allComplete = alreadyDownloaded || modelKeys.every((key) => progress[key] === 100);
  const totalProgress = alreadyDownloaded ? 100 : modelKeys.reduce((acc, key) => acc + (progress[key] || 0), 0) / modelKeys.length;
  
  useEffect(() => {
    modelKeys.forEach((key) => {
      const target = progress[key] || 0;
      const current = animatedProgress[key] || 0;
      
      if (target > current) {
        const timer = setInterval(() => {
          setAnimatedProgress(prev => {
            const newVal = Math.min((prev[key] || 0) + 2, target);
            if (newVal >= target) {
              clearInterval(timer);
            }
            return { ...prev, [key]: newVal };
          });
        }, 20);
        return () => clearInterval(timer);
      }
    });
  }, [progress]);

  const displayModels = [
    { key: 'sentiment', name: t('modelDownload.sentimentModel') },
    { key: 'embeddings', name: t('modelDownload.embeddingsModel') },
    { key: 'subjectivity', name: t('modelDownload.subjectivityModel') },
    { key: 'categories', name: t('modelDownload.categoryModel') },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="models"
    >
      <div className="text-center mb-4 sm:mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-rose-100 to-pink-100 dark:from-rose-900/30 dark:to-pink-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Download className="w-7 h-7 sm:w-8 sm:h-8 text-rose-600 dark:text-rose-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('modelDownload.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mx-auto px-4">
          {t('modelDownload.description')}
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {displayModels.map((model) => {
          const modelProgress = alreadyDownloaded ? 100 : (animatedProgress[model.key] || progress[model.key] || 0);
          const isComplete = modelProgress === 100;
          const progressPercent = Math.round(modelProgress);
          
          return (
            <div key={model.key} className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">{model.name}</span>
                    <span className={cn(
                      "text-sm font-bold",
                      isComplete ? "text-emerald-600 dark:text-emerald-400" : "text-slate-500 dark:text-slate-400"
                    )}>{progressPercent}%</span>
                  </div>
                  {(started || isComplete) && (
                    <div className="relative h-6 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" role="progressbar" aria-valuenow={progressPercent} aria-valuemin={0} aria-valuemax={100} aria-label={model.name}>
                      <div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full shadow-sm transition-all duration-300 ease-out"
                        style={{ width: `${Math.min(100, modelProgress)}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      {checkingModels ? (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            {t('modelDownload.verifying')}
          </div>
        </div>
      ) : allComplete ? (
        <div className="flex justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('nav.back')}
          </Button>
          <Button onClick={onNext}>
            <CheckCircle2 className="w-4 h-4 mr-2" />
            {t('nav.next')}
          </Button>
        </div>
      ) : (!started || error) ? (
        <div className="flex justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('nav.back')}
          </Button>
          <Button onClick={handleStart} disabled={isLoading}>
            <Download className="w-4 h-4 mr-2" />
            {error ? t('modelDownload.retryDownload') : t('modelDownload.downloadModels')}
          </Button>
        </div>
      ) : (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            {t('modelDownload.totalProgress', { progress: Math.round(totalProgress) })}
          </div>
        </div>
      )}
    </motion.div>
  );
}

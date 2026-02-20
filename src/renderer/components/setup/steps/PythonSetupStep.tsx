import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, AlertCircle, Cpu, ArrowLeft } from 'lucide-react';
import { Button } from '../../ui/button';

export function PythonSetupStep({
  onNext,
  onBack,
}: {
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  const [status, setStatus] = useState<'checking' | 'ready' | 'need-install' | 'setting-up' | 'error'>('checking');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(t('pythonSetup.checking'));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkPython();

    const handleProgress = (_: unknown, data: { stage: string; progress: number; message: string; error?: string }) => {
      setProgress(data.progress);
      setMessage(data.message);
      
      if (data.stage === 'complete') {
        setStatus('ready');
        setTimeout(() => onNext(), 1500);
      } else if (data.stage === 'error') {
        setStatus('error');
        setError(data.error || t('pythonSetup.unknownError'));
      }
    };

    window.electronAPI.setup.onPythonProgress(handleProgress);

    return () => {
      window.electronAPI.setup.offPythonProgress();
    };
  }, [onNext]);

  const checkPython = async () => {
    setStatus('checking');
    setMessage(t('pythonSetup.checking'));
    
    try {
      const pythonStatus = await window.electronAPI.setup.checkPython();
      
      if (pythonStatus.setupComplete && pythonStatus.dependenciesInstalled) {
        setStatus('ready');
        setProgress(100);
        setMessage(t('pythonSetup.ready'));
        setTimeout(() => onNext(), 1000);
      } else if (pythonStatus.installationInterrupted) {
        setStatus('need-install');
        setProgress(0);
        setMessage(t('pythonSetup.incompleteDetected'));
      } else if (pythonStatus.venvExists && pythonStatus.dependenciesInstalled && !pythonStatus.setupComplete) {
        setStatus('need-install');
        setProgress(0);
        setMessage(t('pythonSetup.previousFailed'));
      } else {
        setStatus('need-install');
        setProgress(0);
        setMessage(t('pythonSetup.notConfigured'));
      }
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Error verificando Python');
    }
  };

  const handleInstallPython = async () => {
    setStatus('setting-up');
    setMessage(t('pythonSetup.configuring'));
    setProgress(0);
    await window.electronAPI.setup.setupPython();
  };

  const handleRetry = () => {
    setError(null);
    checkPython();
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="python-setup"
    >
      <div className="text-center mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Cpu className="w-7 h-7 sm:w-8 sm:h-8 text-blue-600 dark:text-blue-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('pythonSetup.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mx-auto">
          {t('pythonSetup.subtitle')}
        </p>
      </div>

      <div className="space-y-6">
        <div className="max-w-md mx-auto">
          {(status === 'checking' || status === 'setting-up') && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{message}</span>
                </div>
                <span className="text-sm font-bold text-blue-600">{Math.round(progress)}%</span>
              </div>
              <div className="relative h-6 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" role="progressbar" aria-valuenow={Math.round(progress)} aria-valuemin={0} aria-valuemax={100} aria-label={t('pythonSetup.title')}>
                <div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full shadow-sm transition-all duration-300 ease-out"
                  style={{ width: `${Math.min(100, progress)}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 dark:text-slate-500 text-center">
                {t('pythonSetup.firstTimeWait')}
              </p>
            </div>
          )}

          {status === 'ready' && (
            <motion.div 
              className="text-center space-y-4 py-2"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
            >
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-100 to-green-100 dark:from-emerald-900/30 dark:to-green-900/30 rounded-2xl flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
              </div>
              <h3 className="text-lg font-semibold text-emerald-600 dark:text-emerald-400">{message}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('pythonSetup.continuing')}</p>
            </motion.div>
          )}

          {status === 'need-install' && (
            <div className="text-center">
              <p className="text-sm text-slate-600 dark:text-slate-400">{t('pythonSetup.needsConfig')}</p>
            </div>
          )}

          {status === 'error' && error && (
            <div className="space-y-4">
              <div className="p-4 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-800">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-800 dark:text-red-400">{t('pythonSetup.configError')}</p>
                    <p className="text-xs text-red-600 dark:text-red-500 mt-1">{error}</p>
                  </div>
                </div>
              </div>
              
              <div className="text-center text-sm text-slate-500 dark:text-slate-400">
                <p className="mb-2">{t('pythonSetup.pythonRequired')}</p>
                <a 
                  href="https://www.python.org/downloads/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  {t('pythonSetup.downloadPython')}
                </a>
              </div>
            </div>
          )}
        </div>

        {(status === 'need-install' || (status === 'error' && error)) && (
          <div className="flex justify-between">
            <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
              <ArrowLeft className="w-4 h-4 mr-2" />
              {status === 'error' ? t('pythonSetup.back') : t('pythonSetup.goBack')}
            </Button>
            <Button onClick={status === 'error' ? handleRetry : handleInstallPython}>
              {status === 'error' ? (
                t('pythonSetup.retry')
              ) : (
                <>
                  <Cpu className="w-4 h-4 mr-2" />
                  {t('pythonSetup.installPython')}
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

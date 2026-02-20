import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, Folder, ArrowLeft, ArrowRight } from 'lucide-react';
import { Button } from '../../ui/button';

export function OutputDirStep({
  outputDir,
  onSelectDir,
  onNext,
  onBack,
}: {
  outputDir: string;
  onSelectDir: () => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  const [defaultDir, setDefaultDir] = useState<string>('');

  useEffect(() => {
    window.electronAPI.app.getPythonDataDir().then((dir: string) => {
      setDefaultDir(dir);
    }).catch(() => { /* ignored */ });
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="output-dir"
    >
      <div className="text-center mb-4 sm:mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-amber-100 to-yellow-100 dark:from-amber-900/30 dark:to-yellow-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Folder className="w-7 h-7 sm:w-8 sm:h-8 text-amber-600 dark:text-amber-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('outputDir.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-md mx-auto px-4">
          {t('outputDir.description')}
        </p>
      </div>

      <div className="space-y-4 mb-6">
        <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            {t('outputDir.outputFolder')}
          </label>
          <div className="flex gap-2">
            <div className="flex-1 px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-600 dark:text-slate-300 truncate min-h-[38px] flex items-center">
              {outputDir || t('outputDir.notSelected')}
            </div>
            <Button variant="outline" onClick={onSelectDir} className="flex-shrink-0">
              <Folder className="w-4 h-4 mr-2" />
              {t('outputDir.select')}
            </Button>
          </div>
          {!outputDir && defaultDir && (
            <div className="mt-2 p-2.5 bg-slate-100 dark:bg-slate-700 rounded-lg">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                <span className="font-medium text-slate-600 dark:text-slate-300">{t('outputDir.defaultFolder')}</span>
              </p>
              <p className="text-xs font-mono text-slate-600 dark:text-slate-400 break-all mt-0.5">{defaultDir}</p>
            </div>
          )}
          {!outputDir && !defaultDir && (
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">
              {t('outputDir.defaultHint')}
            </p>
          )}
        </div>

        {outputDir && (
          <div className="p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg border border-emerald-200 dark:border-emerald-800">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">{t('outputDir.selectedFolder')}</p>
                <p className="text-xs text-emerald-600 dark:text-emerald-500 break-all mt-1">{outputDir}</p>
                <p className="text-xs text-emerald-500 dark:text-emerald-400 mt-1">
                  {t('outputDir.savedIn')} <span className="font-mono">{outputDir}/data/</span>
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="p-3 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-blue-500 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-blue-600 dark:text-blue-400">
              {t('outputDir.changeLater')}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button onClick={onNext}>
          {outputDir ? t('nav.next') : t('outputDir.skipDefault')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

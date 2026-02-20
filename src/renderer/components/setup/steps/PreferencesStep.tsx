import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, AlertCircle, Settings, Palette, Globe } from 'lucide-react';
import { Button } from '../../ui/button';
import { ThemeSelector } from '../../settings/ThemeSelector';
import { LanguageSelector } from '../../settings/LanguageSelector';

export function PreferencesStep({
  onNext,
  onBack,
}: {
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  
  return (
    <motion.div
      className="py-4 sm:py-6"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="preferences"
    >
      <div className="text-center mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
          <Settings className="w-7 h-7 sm:w-8 sm:h-8 text-purple-600 dark:text-purple-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('preferences.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('preferences.description')}
        </p>
      </div>

      <div className="space-y-6 max-w-lg mx-auto">
        {/* Theme Selection */}
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Palette className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <h3 className="font-medium text-slate-900 dark:text-white">
              {t('preferences.themeTitle')}
            </h3>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
            {t('preferences.themeDescription')}
          </p>
          <ThemeSelector />
        </div>

        {/* Language Selection */}
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <h3 className="font-medium text-slate-900 dark:text-white">
              {t('preferences.languageTitle')}
            </h3>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
            {t('preferences.languageDescription')}
          </p>
          <LanguageSelector />
        </div>

        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
            <p className="text-xs text-blue-600 dark:text-blue-400">
              {t('preferences.changeLater')}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button onClick={onNext}>
          {t('nav.next')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { Button } from '../../ui/button';
import logoPrimaryHorizontal from '../../../assets/logos/logo-primary-horizontal.png';
import logoWhiteHorizontal from '../../../assets/logos/logo-white-horizontal.png';

export function WelcomeStep({ onNext }: { onNext: () => void }) {
  const { t } = useTranslation('setup');
  return (
    <motion.div
      className="text-center py-6 sm:py-10"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="welcome"
    >
      <motion.div 
        className="mx-auto mb-6 sm:mb-8"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <img
          src={logoPrimaryHorizontal}
          alt="TourlyAI"
          className="w-full max-w-sm h-auto object-contain mx-auto dark:hidden"
        />
        <img
          src={logoWhiteHorizontal}
          alt="TourlyAI"
          className="w-full max-w-sm h-auto object-contain mx-auto hidden dark:block"
        />
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-3">{t('welcome.title')}</h1>
        <p className="text-base sm:text-lg text-slate-500 dark:text-slate-400 mb-8 sm:mb-10 max-w-lg mx-auto leading-relaxed px-4">
          {t('welcome.description')}
        </p>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Button size="lg" onClick={onNext} className="px-8 sm:px-10 py-3 text-base font-medium shadow-lg hover:shadow-xl transition-shadow">
          {t('welcome.start')}
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    </motion.div>
  );
}

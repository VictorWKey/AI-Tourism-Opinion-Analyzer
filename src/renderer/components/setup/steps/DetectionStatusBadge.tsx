import { useTranslation } from 'react-i18next';
import { Check, AlertCircle, Circle, X } from 'lucide-react';
import { cn } from '../../../lib/utils';

export function DetectionStatusBadge({ 
  status, 
  source 
}: { 
  status: 'auto-detected' | 'fallback' | 'manual' | 'failed';
  source: string;
}) {
  const { t } = useTranslation('setup');
  const config = {
    'auto-detected': { 
      label: t('detection.autoDetected'), 
      className: 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400',
      icon: <Check className="w-3 h-3" />
    },
    'fallback': { 
      label: t('detection.estimated'), 
      className: 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400',
      icon: <AlertCircle className="w-3 h-3" />
    },
    'manual': { 
      label: t('detection.manual'), 
      className: 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400',
      icon: <Circle className="w-3 h-3" />
    },
    'failed': { 
      label: t('detection.notDetected'), 
      className: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400',
      icon: <X className="w-3 h-3" />
    },
  };
  
  const { label, className, icon } = config[status];
  
  return (
    <div className="flex items-center gap-1.5">
      <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium', className)}>
        {icon}
        {label}
      </span>
      {status !== 'manual' && (
        <span className="text-xs text-slate-400 dark:text-slate-500 hidden sm:inline" title={source}>
          ({source.length > 20 ? source.slice(0, 20) + '...' : source})
        </span>
      )}
    </div>
  );
}

/**
 * ReviewSearchBar Component
 * ==========================
 * Search input for filtering reviews by text content.
 * Supports searching by words or exact phrase matching.
 */

import React from 'react';
import { Search, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';

interface ReviewSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  resultCount: number;
  totalCount: number;
  className?: string;
}

export function ReviewSearchBar({
  value,
  onChange,
  resultCount,
  totalCount,
  className,
}: ReviewSearchBarProps) {
  const { t } = useTranslation('reviews');

  return (
    <div className={cn('relative', className)}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={t('searchPlaceholder')}
          aria-label={t('searchLabel')}
          className={cn(
            'w-full pl-10 pr-10 py-2.5 rounded-xl border',
            'bg-white dark:bg-slate-800',
            'border-slate-200 dark:border-slate-700',
            'text-slate-900 dark:text-slate-100',
            'placeholder:text-slate-400 dark:placeholder:text-slate-500',
            'focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500',
            'transition-colors text-sm'
          )}
        />
        {value && (
          <button
            onClick={() => onChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      {(value || resultCount !== totalCount) && (
        <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400 pl-1">
          {t('results.showing', { count: resultCount, total: totalCount })}
        </p>
      )}
    </div>
  );
}

/**
 * ReviewFilters Component
 * ========================
 * Dynamic filter panel that only shows filters for completed pipeline phases.
 * Supports filtering by sentiment, subjectivity, categories, topics, and rating.
 */

import React from 'react';
import { Filter, X, RotateCcw } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';
import type { AvailableFilters } from '../../hooks/useReviewData';

export interface ActiveFilters {
  sentiment: string | null;
  subjectivity: string | null;
  categories: string[];
  topics: string[];
  rating: number | null;
}

interface ReviewFiltersProps {
  availableFilters: AvailableFilters;
  activeFilters: ActiveFilters;
  onFiltersChange: (filters: ActiveFilters) => void;
  className?: string;
}

const SENTIMENT_COLORS: Record<string, string> = {
  Positivo: 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-800',
  Negativo: 'bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-800',
  Neutro: 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700',
};

const SUBJECTIVITY_COLORS: Record<string, string> = {
  Subjetiva: 'bg-violet-100 text-violet-700 border-violet-200 dark:bg-violet-900/30 dark:text-violet-300 dark:border-violet-800',
  Mixta: 'bg-cyan-100 text-cyan-700 border-cyan-200 dark:bg-cyan-900/30 dark:text-cyan-300 dark:border-cyan-800',
};

export function ReviewFilters({
  availableFilters,
  activeFilters,
  onFiltersChange,
  className,
}: ReviewFiltersProps) {
  const { t } = useTranslation(['reviews', 'common']);

  const hasAnyFilter =
    availableFilters.hasSentiment ||
    availableFilters.hasSubjectivity ||
    availableFilters.hasCategories ||
    availableFilters.hasTopics ||
    availableFilters.hasRating;

  const activeCount =
    (activeFilters.sentiment ? 1 : 0) +
    (activeFilters.subjectivity ? 1 : 0) +
    activeFilters.categories.length +
    activeFilters.topics.length +
    (activeFilters.rating !== null ? 1 : 0);

  const clearAll = () => {
    onFiltersChange({
      sentiment: null,
      subjectivity: null,
      categories: [],
      topics: [],
      rating: null,
    });
  };

  if (!hasAnyFilter) {
    return (
      <div className={cn('rounded-xl border border-dashed border-slate-300 dark:border-slate-700 p-4', className)}>
        <div className="flex items-center gap-2 text-slate-400 dark:text-slate-500">
          <Filter className="w-4 h-4" />
          <p className="text-sm">{t('reviews:filters.noFilters')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500 dark:text-slate-400" />
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {t('reviews:filters.title')}
          </span>
          {activeCount > 0 && (
            <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              {t('reviews:filters.activeFilters', { count: activeCount })}
            </span>
          )}
        </div>
        {activeCount > 0 && (
          <div className="flex items-center gap-2">
            <button
              onClick={clearAll}
              title={t('reviews:filters.clear')}
              className="p-1 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              aria-label={t('reviews:filters.clear')}
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Filter controls */}
      <div className="flex flex-wrap gap-2">
        {/* Sentiment Filter */}
        {availableFilters.hasSentiment && availableFilters.sentimentValues.length > 0 && (
          <FilterDropdown
            label={t('reviews:filters.sentiment')}
            allLabel={t('reviews:filters.allSentiments')}
            value={activeFilters.sentiment}
            options={availableFilters.sentimentValues.map((v) => ({
              value: v,
              label: t(`common:dataLabels.sentiment.${v}`, v),
              colorClass: SENTIMENT_COLORS[v] || '',
            }))}
            onChange={(val) => onFiltersChange({ ...activeFilters, sentiment: val })}
          />
        )}

        {/* Subjectivity Filter */}
        {availableFilters.hasSubjectivity && availableFilters.subjectivityValues.length > 0 && (
          <FilterDropdown
            label={t('reviews:filters.subjectivity')}
            allLabel={t('reviews:filters.allSubjectivities')}
            value={activeFilters.subjectivity}
            options={availableFilters.subjectivityValues.map((v) => ({
              value: v,
              label: t(`common:dataLabels.subjectivity.${v}`, v),
              colorClass: SUBJECTIVITY_COLORS[v] || '',
            }))}
            onChange={(val) => onFiltersChange({ ...activeFilters, subjectivity: val })}
          />
        )}

        {/* Rating Filter */}
        {availableFilters.hasRating && availableFilters.ratingValues.length > 0 && (
          <FilterDropdown
            label={t('reviews:filters.rating')}
            allLabel={t('reviews:filters.allRatings')}
            value={activeFilters.rating !== null ? String(activeFilters.rating) : null}
            options={availableFilters.ratingValues.map((v) => ({
              value: String(v),
              label: `${'★'.repeat(v)}${'☆'.repeat(5 - v)}`,
              colorClass: '',
            }))}
            onChange={(val) => onFiltersChange({ ...activeFilters, rating: val ? Number(val) : null })}
          />
        )}

        {/* Categories Filter */}
        {availableFilters.hasCategories && availableFilters.categoryValues.length > 0 && (
          <FilterMultiSelect
            label={t('reviews:filters.categories')}
            allLabel={t('reviews:filters.allCategories')}
            values={activeFilters.categories}
            options={availableFilters.categoryValues.map((v) => ({
              value: v,
              label: t(`common:dataLabels.categories.${v}`, v),
            }))}
            onChange={(vals) => onFiltersChange({ ...activeFilters, categories: vals })}
          />
        )}

        {/* Topics Filter */}
        {availableFilters.hasTopics && availableFilters.topicValues.length > 0 && (
          <FilterMultiSelect
            label={t('reviews:filters.topics')}
            allLabel={t('reviews:filters.allTopics')}
            values={activeFilters.topics}
            options={availableFilters.topicValues.map((v) => ({
              value: v,
              label: v,
            }))}
            onChange={(vals) => onFiltersChange({ ...activeFilters, topics: vals })}
          />
        )}
      </div>
    </div>
  );
}

/* ─── Internal Sub-components ─── */

interface FilterOption {
  value: string;
  label: string;
  colorClass?: string;
}

interface FilterDropdownProps {
  label: string;
  allLabel: string;
  value: string | null;
  options: FilterOption[];
  onChange: (value: string | null) => void;
}

function FilterDropdown({ label, allLabel, value, options, onChange }: FilterDropdownProps) {
  return (
    <div className="relative">
      <select
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value || null)}
        className={cn(
          'appearance-none pl-3 pr-8 py-1.5 rounded-lg text-xs font-medium border cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-blue-500/40',
          'transition-colors',
          value
            ? 'bg-blue-100 border-blue-400 text-blue-900 dark:bg-blue-700 dark:border-blue-600 dark:text-white'
            : 'bg-white border-slate-200 text-slate-600 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300'
        )}
        title={label}
      >
        <option value="">{label}: {allLabel}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {label}: {opt.label}
          </option>
        ))}
      </select>
      <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg className="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

interface FilterMultiSelectProps {
  label: string;
  allLabel: string;
  values: string[];
  options: FilterOption[];
  onChange: (values: string[]) => void;
}

function FilterMultiSelect({ label, allLabel, values, options, onChange }: FilterMultiSelectProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleValue = (val: string) => {
    if (values.includes(val)) {
      onChange(values.filter((v) => v !== val));
    } else {
      onChange([...values, val]);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-blue-500/40',
          'transition-colors',
          values.length > 0
            ? 'bg-blue-100 border-blue-400 text-blue-900 dark:bg-blue-700 dark:border-blue-600 dark:text-white'
            : 'bg-white border-slate-200 text-slate-600 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300'
        )}
      >
        <span>
          {label}
          {values.length > 0 && (
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-blue-500 text-white text-[10px]">
              {values.length}
            </span>
          )}
        </span>
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-56 max-h-60 overflow-y-auto rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg">
          <button
            onClick={() => { onChange([]); }}
            className={cn(
              'w-full text-left px-3 py-2 text-xs hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors border-b border-slate-100 dark:border-slate-700',
              values.length === 0 ? 'text-blue-600 dark:text-blue-400 font-medium' : 'text-slate-500 dark:text-slate-400'
            )}
          >
            {allLabel}
          </button>
          {options.map((opt) => (
            <button
              key={opt.value}
              onClick={() => toggleValue(opt.value)}
              className={cn(
                'w-full text-left px-3 py-2 text-xs hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors flex items-center gap-2',
                values.includes(opt.value)
                  ? 'text-blue-600 dark:text-blue-400 font-medium'
                  : 'text-slate-700 dark:text-slate-300'
              )}
            >
              <div
                className={cn(
                  'w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0',
                  values.includes(opt.value)
                    ? 'bg-blue-500 border-blue-500'
                    : 'border-slate-300 dark:border-slate-600'
                )}
              >
                {values.includes(opt.value) && (
                  <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * ReviewCard Component
 * =====================
 * Displays a single review with colorful badges for each classification.
 * 
 * Layout:
 * ┌──────────────────────────────────────────────┐
 * │ #N  Title                    [Sentiment] [★★★]│
 * │                              [Subjectivity]   │
 * │ Review text...                                │
 * │                                               │
 * │ 📂 Categories: [Badge] [Badge] [Badge]        │
 * │ 💬 Topics:     [Cat→Topic] [Cat→Topic]        │
 * └──────────────────────────────────────────────┘
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';
import type { ReviewData } from '../../hooks/useReviewData';

interface ReviewCardProps {
  review: ReviewData;
  searchQuery: string;
}

/* ─── Color Maps ─── */

const SENTIMENT_BADGE: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  Positivo: {
    bg: 'bg-emerald-50 dark:bg-emerald-900/25',
    text: 'text-emerald-700 dark:text-emerald-300',
    border: 'border-emerald-200 dark:border-emerald-800',
    dot: 'bg-emerald-500',
  },
  Negativo: {
    bg: 'bg-rose-50 dark:bg-rose-900/25',
    text: 'text-rose-700 dark:text-rose-300',
    border: 'border-rose-200 dark:border-rose-800',
    dot: 'bg-rose-500',
  },
  Neutro: {
    bg: 'bg-amber-50 dark:bg-amber-900/25',
    text: 'text-amber-700 dark:text-amber-300',
    border: 'border-amber-200 dark:border-amber-800',
    dot: 'bg-amber-500',
  },
};

const SUBJECTIVITY_BADGE: Record<string, { bg: string; text: string; border: string }> = {
  Subjetiva: {
    bg: 'bg-violet-50 dark:bg-violet-900/25',
    text: 'text-violet-700 dark:text-violet-300',
    border: 'border-violet-200 dark:border-violet-800',
  },
  Mixta: {
    bg: 'bg-cyan-50 dark:bg-cyan-900/25',
    text: 'text-cyan-700 dark:text-cyan-300',
    border: 'border-cyan-200 dark:border-cyan-800',
  },
};

const CATEGORY_COLORS: string[] = [
  'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/25 dark:text-blue-300 dark:border-blue-800',
  'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-900/25 dark:text-indigo-300 dark:border-indigo-800',
  'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/25 dark:text-purple-300 dark:border-purple-800',
  'bg-pink-50 text-pink-700 border-pink-200 dark:bg-pink-900/25 dark:text-pink-300 dark:border-pink-800',
  'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200 dark:bg-fuchsia-900/25 dark:text-fuchsia-300 dark:border-fuchsia-800',
  'bg-teal-50 text-teal-700 border-teal-200 dark:bg-teal-900/25 dark:text-teal-300 dark:border-teal-800',
  'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-900/25 dark:text-sky-300 dark:border-sky-800',
  'bg-lime-50 text-lime-700 border-lime-200 dark:bg-lime-900/25 dark:text-lime-300 dark:border-lime-800',
  'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/25 dark:text-orange-300 dark:border-orange-800',
  'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/25 dark:text-amber-300 dark:border-amber-800',
  'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/25 dark:text-emerald-300 dark:border-emerald-800',
  'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-900/25 dark:text-rose-300 dark:border-rose-800',
];

const TOPIC_COLORS: string[] = [
  'bg-gradient-to-r from-blue-50 to-indigo-50 text-indigo-700 border-indigo-200 dark:from-blue-900/20 dark:to-indigo-900/20 dark:text-indigo-300 dark:border-indigo-800',
  'bg-gradient-to-r from-purple-50 to-pink-50 text-purple-700 border-purple-200 dark:from-purple-900/20 dark:to-pink-900/20 dark:text-purple-300 dark:border-purple-800',
  'bg-gradient-to-r from-teal-50 to-cyan-50 text-teal-700 border-teal-200 dark:from-teal-900/20 dark:to-cyan-900/20 dark:text-teal-300 dark:border-teal-800',
  'bg-gradient-to-r from-orange-50 to-amber-50 text-orange-700 border-orange-200 dark:from-orange-900/20 dark:to-amber-900/20 dark:text-orange-300 dark:border-orange-800',
  'bg-gradient-to-r from-emerald-50 to-lime-50 text-emerald-700 border-emerald-200 dark:from-emerald-900/20 dark:to-lime-900/20 dark:text-emerald-300 dark:border-emerald-800',
  'bg-gradient-to-r from-rose-50 to-pink-50 text-rose-700 border-rose-200 dark:from-rose-900/20 dark:to-pink-900/20 dark:text-rose-300 dark:border-rose-800',
];

// Consistent color index for a category name
function getCategoryColorIndex(category: string): number {
  let hash = 0;
  for (let i = 0; i < category.length; i++) {
    hash = category.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % CATEGORY_COLORS.length;
}

function getTopicColorIndex(topic: string): number {
  let hash = 0;
  for (let i = 0; i < topic.length; i++) {
    hash = topic.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % TOPIC_COLORS.length;
}

/** Highlight search matches in text */
function highlightText(text: string, query: string): React.ReactNode {
  if (!query || query.trim() === '') return text;

  try {
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-yellow-200 dark:bg-yellow-800/60 text-inherit rounded px-0.5">
          {part}
        </mark>
      ) : (
        part
      )
    );
  } catch {
    return text;
  }
}

export function ReviewCard({ review, searchQuery }: ReviewCardProps) {
  const { t } = useTranslation(['reviews', 'common']);

  const sentimentStyle = review.sentiment ? SENTIMENT_BADGE[review.sentiment] : null;
  const subjectivityStyle = review.subjectivity ? SUBJECTIVITY_BADGE[review.subjectivity] : null;
  const hasCategories = review.categories && review.categories.length > 0;
  const hasTopics = review.topics && Object.keys(review.topics).length > 0;

  return (
    <div
      className={cn(
        'rounded-xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800',
        'shadow-sm hover:shadow-md transition-shadow duration-200',
        'overflow-hidden'
      )}
    >
      {/* Header: number, badges, and title */}
      <div className="px-5 pt-4 pb-2">
        {/* Top row: Review number and date */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-mono text-slate-400 dark:text-slate-500 shrink-0">
            {t('reviews:review.reviewNumber', { number: review.index })}
          </span>
          {review.stayDate && (
            <span className="text-xs text-slate-400 dark:text-slate-500">
              · {review.stayDate}
            </span>
          )}
        </div>

        {/* Badges row: Sentiment, Subjectivity, and Rating in one horizontal line */}
        <div className="flex items-center flex-wrap gap-2 mb-2">
          {/* Sentiment badge */}
          {sentimentStyle && review.sentiment && (
            <div
              className={cn(
                'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border',
                sentimentStyle.bg,
                sentimentStyle.text,
                sentimentStyle.border
              )}
            >
              <span className={cn('w-1.5 h-1.5 rounded-full', sentimentStyle.dot)} />
              {t(`common:dataLabels.sentiment.${review.sentiment}`, review.sentiment)}
            </div>
          )}

          {/* Subjectivity badge */}
          {subjectivityStyle && review.subjectivity && (
            <div
              className={cn(
                'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border',
                subjectivityStyle.bg,
                subjectivityStyle.text,
                subjectivityStyle.border
              )}
            >
              {t(`common:dataLabels.subjectivity.${review.subjectivity}`, review.subjectivity)}
            </div>
          )}

          {/* Rating (Polarity) */}
          {review.rating !== undefined && (
            <div className="flex items-center gap-0.5">
              {Array.from({ length: 5 }, (_, i) => (
                <span
                  key={i}
                  className={cn(
                    'text-sm',
                    i < (review.rating ?? 0)
                      ? 'text-amber-400'
                      : 'text-slate-300 dark:text-slate-600'
                  )}
                >
                  ★
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Title */}
        {review.title && (
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 line-clamp-1">
            {highlightText(review.title, searchQuery)}
          </h3>
        )}
      </div>

      {/* Review text */}
      <div className="px-5 pb-3">
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed line-clamp-4">
          {highlightText(review.review, searchQuery)}
        </p>
      </div>

      {/* Categories & Topics sections */}
      {(hasCategories || hasTopics) && (
        <div className="border-t border-slate-100 dark:border-slate-800 px-5 py-3 space-y-2.5">
          {/* Categories */}
          {hasCategories && (
            <div className="flex items-start gap-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 shrink-0 pt-0.5 w-20">
                {t('reviews:review.categories')}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(review.categories ?? []).map((cat) => (
                  <span
                    key={cat}
                    className={cn(
                      'inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium border',
                      CATEGORY_COLORS[getCategoryColorIndex(cat)]
                    )}
                  >
                    {t(`common:dataLabels.categories.${cat}`, cat)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Topics */}
          {hasTopics && (
            <div className="flex items-start gap-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 shrink-0 pt-0.5 w-20">
                {t('reviews:review.topics')}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(review.topics ?? {}).map(([category, topic]) => (
                  <span
                    key={`${category}-${topic}`}
                    className={cn(
                      'inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium border',
                      TOPIC_COLORS[getTopicColorIndex(topic)]
                    )}
                  >
                    <span className="opacity-60 mr-1">
                      {t(`common:dataLabels.categories.${category}`, category)}
                    </span>
                    →
                    <span className="ml-1 font-semibold">{topic}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Reviews Page
 * =============
 * Review Explorer — browse and filter individual reviews with their
 * pipeline analysis results (sentiment, subjectivity, categories, topics).
 * 
 * Features:
 * - Text search with highlighting
 * - Dynamic filters based on completed pipeline phases
 * - Paginated review list
 * - Colorful badges for each classification
 */

import React, { useState, useMemo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, RefreshCw, ChevronLeft, ChevronRight, FileSearch, AlertTriangle, Loader2 } from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button } from '../components/ui';
import { ReviewSearchBar, ReviewFilters, ReviewCard } from '../components/reviews';
import type { ActiveFilters } from '../components/reviews';
import { useReviewData } from '../hooks/useReviewData';
import { cn } from '../lib/utils';

const ITEMS_PER_PAGE_OPTIONS = [10, 25, 50, 100];

type SortOption = 'default' | 'date-newest' | 'date-oldest' | 'length-longest' | 'length-shortest';

export function Reviews() {
  const { t } = useTranslation(['reviews', 'common']);
  const { reviews, availableFilters, isLoading, error, reload } = useReviewData();

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Filter state
  const [activeFilters, setActiveFilters] = useState<ActiveFilters>({
    sentiment: null,
    subjectivity: null,
    categories: [],
    topics: [],
    rating: null,
  });

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);

  // Sorting state
  const [sortBy, setSortBy] = useState<SortOption>('default');

  // Check if dates are available
  const hasDates = useMemo(() => {
    return reviews.some((r) => r.stayDate && r.stayDate !== '');
  }, [reviews]);

  // Filter + search + sort logic
  const filteredReviews = useMemo(() => {
    let result = reviews;

    // Text search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (r) =>
          r.review.toLowerCase().includes(query) ||
          (r.title && r.title.toLowerCase().includes(query))
      );
    }

    // Sentiment filter
    if (activeFilters.sentiment) {
      result = result.filter((r) => r.sentiment === activeFilters.sentiment);
    }

    // Subjectivity filter
    if (activeFilters.subjectivity) {
      result = result.filter((r) => r.subjectivity === activeFilters.subjectivity);
    }

    // Rating filter
    if (activeFilters.rating !== null) {
      result = result.filter((r) => r.rating === activeFilters.rating);
    }

    // Categories filter (review must have ALL selected categories)
    if (activeFilters.categories.length > 0) {
      result = result.filter((r) =>
        activeFilters.categories.every((cat) => r.categories?.includes(cat))
      );
    }

    // Topics filter (review must have at least one of the selected topics)
    if (activeFilters.topics.length > 0) {
      result = result.filter((r) => {
        if (!r.topics) return false;
        const reviewTopics = Object.values(r.topics);
        return activeFilters.topics.some((topic) => reviewTopics.includes(topic));
      });
    }

    // Sorting
    if (sortBy !== 'default') {
      result = [...result]; // Create a copy for sorting
      
      switch (sortBy) {
        case 'date-newest':
          result.sort((a, b) => {
            if (!a.stayDate && !b.stayDate) return 0;
            if (!a.stayDate) return 1;
            if (!b.stayDate) return -1;
            return new Date(b.stayDate).getTime() - new Date(a.stayDate).getTime();
          });
          break;
        case 'date-oldest':
          result.sort((a, b) => {
            if (!a.stayDate && !b.stayDate) return 0;
            if (!a.stayDate) return 1;
            if (!b.stayDate) return -1;
            return new Date(a.stayDate).getTime() - new Date(b.stayDate).getTime();
          });
          break;
        case 'length-longest':
          result.sort((a, b) => b.review.length - a.review.length);
          break;
        case 'length-shortest':
          result.sort((a, b) => a.review.length - b.review.length);
          break;
      }
    }

    return result;
  }, [reviews, searchQuery, activeFilters, sortBy]);

  // Reset page when filters change
  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    setCurrentPage(1);
  }, []);

  const handleFiltersChange = useCallback((filters: ActiveFilters) => {
    setActiveFilters(filters);
    setCurrentPage(1);
  }, []);

  const handlePerPageChange = useCallback((value: number) => {
    setItemsPerPage(value);
    setCurrentPage(1);
  }, []);

  const handleSortChange = useCallback((value: SortOption) => {
    setSortBy(value);
    setCurrentPage(1);
  }, []);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(filteredReviews.length / itemsPerPage));
  const paginatedReviews = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredReviews.slice(start, start + itemsPerPage);
  }, [filteredReviews, currentPage, itemsPerPage]);

  // Header actions
  const headerActions = (
    <Button
      variant="outline"
      size="sm"
      onClick={reload}
      disabled={isLoading}
      className="gap-2"
    >
      <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
      {t('common:actions.refresh')}
    </Button>
  );

  return (
    <PageLayout
      title={t('reviews:title')}
      description={t('reviews:description')}
      headerActions={headerActions}
    >
      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mb-3" />
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {t('common:status.loading')}
          </p>
        </div>
      )}

      {/* Error: No data */}
      {!isLoading && error === 'no_data' && (
        <div className="flex flex-col items-center justify-center py-20">
          <FileSearch className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-2">
            {t('reviews:results.noData')}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 text-center max-w-md">
            {t('reviews:results.noDataDesc')}
          </p>
        </div>
      )}

      {/* Error: Load failure */}
      {!isLoading && error === 'load_error' && (
        <div className="flex flex-col items-center justify-center py-20">
          <AlertTriangle className="w-12 h-12 text-amber-400 mb-4" />
          <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-2">
            {t('reviews:results.loadError')}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 text-center max-w-md">
            {t('reviews:results.loadErrorDesc')}
          </p>
          <Button variant="outline" size="sm" onClick={reload} className="mt-4 gap-2">
            <RefreshCw className="w-4 h-4" />
            {t('common:actions.refresh')}
          </Button>
        </div>
      )}

      {/* Main content: reviews loaded */}
      {!isLoading && !error && (
        <div className="max-w-5xl mx-auto space-y-4">
          {/* Search bar */}
          <ReviewSearchBar
            value={searchQuery}
            onChange={handleSearchChange}
            resultCount={filteredReviews.length}
            totalCount={reviews.length}
          />

          {/* Filters */}
          <ReviewFilters
            availableFilters={availableFilters}
            activeFilters={activeFilters}
            onFiltersChange={handleFiltersChange}
          />

          {/* Results count + sorting + per page */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {t('reviews:results.showing', {
                count: filteredReviews.length,
                total: reviews.length,
              })}
            </p>
            <div className="flex items-center gap-4">
              {/* Sort by */}
              <div className="flex items-center gap-2">
                <label className="text-xs text-slate-500 dark:text-slate-400">
                  {t('reviews:sorting.label')}
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => handleSortChange(e.target.value as SortOption)}
                  className={cn(
                    'text-xs rounded-lg border px-2 py-1',
                    'bg-white dark:bg-slate-800',
                    'border-slate-200 dark:border-slate-700',
                    'text-slate-700 dark:text-slate-300',
                    'focus:outline-none focus:ring-2 focus:ring-blue-500/40'
                  )}
                >
                  <option value="default">{t('reviews:sorting.default')}</option>
                  {hasDates && (
                    <>
                      <option value="date-newest">{t('reviews:sorting.dateNewest')}</option>
                      <option value="date-oldest">{t('reviews:sorting.dateOldest')}</option>
                    </>
                  )}
                  <option value="length-longest">{t('reviews:sorting.lengthLongest')}</option>
                  <option value="length-shortest">{t('reviews:sorting.lengthShortest')}</option>
                </select>
              </div>
              {/* Per page */}
              <div className="flex items-center gap-2">
                <label className="text-xs text-slate-500 dark:text-slate-400">
                  {t('reviews:pagination.perPage')}
                </label>
                <select
                  value={itemsPerPage}
                  onChange={(e) => handlePerPageChange(Number(e.target.value))}
                  className={cn(
                    'text-xs rounded-lg border px-2 py-1',
                    'bg-white dark:bg-slate-800',
                    'border-slate-200 dark:border-slate-700',
                    'text-slate-700 dark:text-slate-300',
                    'focus:outline-none focus:ring-2 focus:ring-blue-500/40'
                  )}
                >
                  {ITEMS_PER_PAGE_OPTIONS.map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Review Cards */}
          {filteredReviews.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Search className="w-10 h-10 text-slate-300 dark:text-slate-600 mb-3" />
              <h3 className="text-base font-semibold text-slate-600 dark:text-slate-400 mb-1">
                {t('reviews:results.noResults')}
              </h3>
              <p className="text-sm text-slate-400 dark:text-slate-500">
                {t('reviews:results.noResultsDesc')}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {paginatedReviews.map((review) => (
                <ReviewCard
                  key={review.index}
                  review={review}
                  searchQuery={searchQuery}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-2 pb-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                {t('reviews:pagination.previous')}
              </Button>

              <div className="flex items-center gap-1">
                {generatePageNumbers(currentPage, totalPages).map((page, i) =>
                  page === '...' ? (
                    <span key={`ellipsis-${i}`} className="px-2 text-slate-400 dark:text-slate-500 text-sm">
                      ...
                    </span>
                  ) : (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page as number)}
                      className={cn(
                        'w-8 h-8 rounded-lg text-xs font-medium transition-colors',
                        currentPage === page
                          ? 'bg-blue-500 text-white'
                          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                      )}
                    >
                      {page}
                    </button>
                  )
                )}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="gap-1"
              >
                {t('reviews:pagination.next')}
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      )}
    </PageLayout>
  );
}

/** Generate smart page number list with ellipsis */
function generatePageNumbers(current: number, total: number): (number | string)[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | string)[] = [];

  // Always show first page
  pages.push(1);

  if (current > 3) {
    pages.push('...');
  }

  // Show pages around current
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (current < total - 2) {
    pages.push('...');
  }

  // Always show last page
  if (total > 1) {
    pages.push(total);
  }

  return pages;
}

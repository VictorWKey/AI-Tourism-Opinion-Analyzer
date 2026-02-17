/**
 * useReviewData Hook
 * ===================
 * Loads and parses the processed dataset CSV for the Review Explorer.
 * Provides review data along with information about which pipeline
 * phases have been completed (to determine available filters).
 */

import { useState, useEffect, useCallback } from 'react';
import { parseCSV, parsePythonList, parsePythonDict } from '../lib/csvParser';

export interface ReviewData {
  index: number;
  title: string;
  review: string;
  sentiment?: string;
  rating?: number;
  subjectivity?: string;
  categories?: string[];
  topics?: Record<string, string>;
  stayDate?: string;
}

export interface AvailableFilters {
  hasSentiment: boolean;
  hasSubjectivity: boolean;
  hasCategories: boolean;
  hasTopics: boolean;
  hasRating: boolean;
  sentimentValues: string[];
  subjectivityValues: string[];
  categoryValues: string[];
  topicValues: string[];
  ratingValues: number[];
}

export interface ReviewDataState {
  reviews: ReviewData[];
  availableFilters: AvailableFilters;
  isLoading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

export function useReviewData(): ReviewDataState {
  const [reviews, setReviews] = useState<ReviewData[]>([]);
  const [availableFilters, setAvailableFilters] = useState<AvailableFilters>({
    hasSentiment: false,
    hasSubjectivity: false,
    hasCategories: false,
    hasTopics: false,
    hasRating: false,
    sentimentValues: [],
    subjectivityValues: [],
    categoryValues: [],
    topicValues: [],
    ratingValues: [],
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReviews = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const pythonDataDir = await window.electronAPI.app.getPythonDataDir();
      const csvPath = `${pythonDataDir}/dataset.csv`;
      
      const exists = await window.electronAPI.files.exists(csvPath);
      if (!exists) {
        setReviews([]);
        setError('no_data');
        return;
      }

      const result = await window.electronAPI.files.readFile(csvPath);
      if (!result.success || !result.content) {
        setError('load_error');
        return;
      }

      const { headers, rows } = parseCSV(result.content);

      // Determine available columns
      const hasTitle = headers.includes('Titulo');
      const hasReview = headers.includes('Review');
      const hasSentiment = headers.includes('Sentimiento');
      const hasSubjectivity = headers.includes('Subjetividad');
      const hasCategories = headers.includes('Categorias');
      const hasTopics = headers.includes('Topico');
      const hasRating = headers.includes('Calificacion');
      const hasStayDate = headers.includes('FechaEstadia');

      if (!hasReview) {
        setError('load_error');
        return;
      }

      // Collect unique values for filters
      const sentimentSet = new Set<string>();
      const subjectivitySet = new Set<string>();
      const categorySet = new Set<string>();
      const topicSet = new Set<string>();
      const ratingSet = new Set<number>();

      const parsedReviews: ReviewData[] = rows.map((row, idx) => {
        const review: ReviewData = {
          index: idx + 1,
          title: hasTitle ? (row['Titulo'] || '') : '',
          review: row['Review'] || '',
        };

        if (hasSentiment && row['Sentimiento'] && row['Sentimiento'] !== 'nan') {
          review.sentiment = row['Sentimiento'];
          sentimentSet.add(row['Sentimiento']);
        }

        if (hasSubjectivity && row['Subjetividad'] && row['Subjetividad'] !== 'nan') {
          review.subjectivity = row['Subjetividad'];
          subjectivitySet.add(row['Subjetividad']);
        }

        if (hasRating && row['Calificacion'] && row['Calificacion'] !== 'nan') {
          const rating = parseInt(row['Calificacion'], 10);
          if (!isNaN(rating)) {
            review.rating = rating;
            ratingSet.add(rating);
          }
        }

        if (hasCategories && row['Categorias'] && row['Categorias'] !== 'nan') {
          const cats = parsePythonList(row['Categorias']);
          review.categories = cats;
          cats.forEach((c) => categorySet.add(c));
        }

        if (hasTopics && row['Topico'] && row['Topico'] !== 'nan') {
          const topics = parsePythonDict(row['Topico']);
          review.topics = topics;
          Object.values(topics).forEach((t) => topicSet.add(t));
        }

        if (hasStayDate && row['FechaEstadia'] && row['FechaEstadia'] !== 'nan') {
          review.stayDate = row['FechaEstadia'];
        }

        return review;
      });

      setReviews(parsedReviews);
      setAvailableFilters({
        hasSentiment,
        hasSubjectivity,
        hasCategories,
        hasTopics,
        hasRating,
        sentimentValues: Array.from(sentimentSet).sort(),
        subjectivityValues: Array.from(subjectivitySet).sort(),
        categoryValues: Array.from(categorySet).sort(),
        topicValues: Array.from(topicSet).sort(),
        ratingValues: Array.from(ratingSet).sort((a, b) => a - b),
      });
    } catch (err) {
      console.error('Failed to load reviews:', err);
      setError('load_error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  return { reviews, availableFilters, isLoading, error, reload: loadReviews };
}

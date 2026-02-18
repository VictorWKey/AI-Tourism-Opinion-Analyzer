/**
 * Results Page
 * =============
 * Display analysis results and summaries
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FileText,
  Download,
  Copy,
  Check,
  Folder,
  RefreshCw,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button, MarkdownRenderer } from '../components/ui';
import { cn } from '../lib/utils';
import { useDataStore } from '../stores/dataStore';
import { usePipelineStore } from '../stores/pipelineStore';

interface ResultSection {
  id: string;
  title: string;
  content: string;
  type: 'summary' | 'stats' | 'insights';
}

export function Results() {
  const { t } = useTranslation('results');
  const { outputPath, summaryPath } = useDataStore();
  const { phases } = usePipelineStore();
  const [sections, setSections] = useState<ResultSection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const completedPhases = Object.values(phases).filter(
    (p) => p.status === 'completed'
  ).length;

  // Load results
  useEffect(() => {
    if (summaryPath) {
      loadResults();
    }
  }, [summaryPath]);

  const loadResults = async () => {
    if (!summaryPath) return;

    setIsLoading(true);
    try {
      const result = await window.electronAPI.files.readFile(summaryPath);
      if (result.success && result.content) {
        // Parse JSON summary if available
        try {
          const data = JSON.parse(result.content);
          const newSections: ResultSection[] = [];

          if (data.executive_summary) {
            newSections.push({
              id: 'executive',
              title: t('sections.executive'),
              content: data.executive_summary,
              type: 'summary',
            });
          }

          if (data.sentiment_analysis) {
            newSections.push({
              id: 'sentiment',
              title: t('sections.sentiment'),
              content: data.sentiment_analysis,
              type: 'insights',
            });
          }

          if (data.category_insights) {
            newSections.push({
              id: 'categories',
              title: t('sections.categories'),
              content: data.category_insights,
              type: 'insights',
            });
          }

          if (data.recommendations) {
            newSections.push({
              id: 'recommendations',
              title: t('sections.recommendations'),
              content: data.recommendations,
              type: 'insights',
            });
          }

          setSections(newSections);
          // Expand first section by default
          if (newSections.length > 0) {
            setExpandedSections(new Set([newSections[0].id]));
          }
        } catch {
          // If not JSON, treat as markdown
          setSections([
            {
              id: 'main',
              title: t('sections.main'),
              content: result.content,
              type: 'summary',
            },
          ]);
          setExpandedSections(new Set(['main']));
        }
      }
    } catch (error) {
      console.error('Failed to load results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleCopy = async (content: string, id: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleOpenFolder = async () => {
    if (outputPath) {
      // outputPath is a file path (dataset.csv), extract the directory
      const folderPath = outputPath.replace(/[/\\][^/\\]+$/, '');
      await window.electronAPI.files.openPath(folderPath);
    }
  };

  const handleExport = async () => {
    // Export all results to a single file
    const content = sections.map((s) => `# ${s.title}\n\n${s.content}`).join('\n\n---\n\n');
    
    const savePath = await window.electronAPI.files.selectDirectory();
    if (savePath) {
      await window.electronAPI.files.writeFile(
        `${savePath}/${t('exportFilename')}`,
        content
      );
    }
  };

  return (
    <PageLayout
      title={t('title')}
      description={t('description')}
      headerActions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadResults}>
            <RefreshCw className="w-4 h-4 mr-2" />
            {t('refresh')}
          </Button>
          {outputPath && (
            <Button variant="outline" size="sm" onClick={handleOpenFolder}>
              <Folder className="w-4 h-4 mr-2" />
              {t('openFolder')}
            </Button>
          )}
          {sections.length > 0 && (
            <Button size="sm" onClick={handleExport}>
              <Download className="w-4 h-4 mr-2" />
              {t('export')}
            </Button>
          )}
        </div>
      }
    >
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Status Summary */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-slate-900 dark:text-white">
                {t('analysisStatus')}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {t('phasesCompleted', { completed: completedPhases })}
              </p>
            </div>
            <div className="flex gap-1">
              {Object.values(phases).map((phase) => (
                <div
                  key={phase.phase}
                  className={cn(
                    'w-8 h-2 rounded',
                    phase.status === 'completed'
                      ? 'bg-green-500'
                      : phase.status === 'failed'
                      ? 'bg-red-500'
                      : phase.status === 'running'
                      ? 'bg-blue-500'
                      : 'bg-slate-200 dark:bg-slate-700'
                  )}
                  title={t('phaseTitle', { phase: phase.phase, name: t(`common:phases.${phase.phase}.name`) })}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Results Content */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
          </div>
        ) : sections.length > 0 ? (
          <div className="space-y-4">
            {sections.map((section) => (
              <div
                key={section.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden"
              >
                {/* Section Header */}
                <button
                  onClick={() => toggleSection(section.id)}
                  className="w-full flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <span className="font-medium text-slate-900 dark:text-white">
                      {section.title}
                    </span>
                  </div>
                  {expandedSections.has(section.id) ? (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  )}
                </button>

                {/* Section Content */}
                {expandedSections.has(section.id) && (
                  <div className="border-t border-slate-200 dark:border-slate-700">
                    <div className="p-5">
                      <MarkdownRenderer content={section.content} />
                    </div>
                    <div className="px-4 pb-4 flex justify-end">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy(section.content, section.id)}
                      >
                        {copiedId === section.id ? (
                          <>
                            <Check className="w-4 h-4 mr-2" />
                            {t('copied')}
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4 mr-2" />
                            {t('copy')}
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <FileText className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
            <p className="text-slate-500 dark:text-slate-400 text-center">
              {t('noResults')}
            </p>
            <p className="text-sm text-slate-400 dark:text-slate-500 text-center mt-1">
              {t('noResultsHint')}
            </p>
          </div>
        )}
      </div>
    </PageLayout>
  );
}

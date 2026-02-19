/**
 * Reports Page
 * =============
 * Generate customizable PDF reports from analysis data.
 * Features:
 * - Template presets (executive, detailed, visual, custom)
 * - Per-section toggle with descriptions
 * - Visualization category filter
 * - Summary category filter
 * - Report settings (title, date, page numbers)
 * - PDF generation with progress feedback
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  FileText,
  Download,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  BarChart3,
  Briefcase,
  Image,
  SlidersHorizontal,
  Loader2,
  FolderOpen,
  ExternalLink,
  BookOpen,
  Target,
  TrendingUp,
  ThumbsUp,
  ThumbsDown,
  Clock,
  MessageSquare,
  Star,
  Calendar,
  Hash,
  AlertTriangle,
  Eye,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button } from '../components/ui';
import { cn } from '../lib/utils';
import { useTranslation } from 'react-i18next';
import { useDataStore } from '../stores/dataStore';
import { useSettingsStore } from '../stores/settingsStore';
import { usePipelineStore } from '../stores/pipelineStore';
import {
  type ReportConfig,
  type ReportTemplate,
  type VisualizationCategory,
  TEMPLATE_PRESETS,
} from '../lib/reportTypes';
import { generatePdfReport } from '../lib/reportGenerator';

/* ──────────────── Template Card ──────────────── */

interface TemplateCardProps {
  id: ReportTemplate;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  selected: boolean;
  onSelect: () => void;
}

function TemplateCard({ icon: Icon, title, description, selected, onSelect }: TemplateCardProps) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        'relative flex flex-col items-start p-4 rounded-xl border-2 transition-all text-left cursor-pointer',
        'hover:shadow-md',
        selected
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/30 shadow-sm'
          : 'border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-500'
      )}
    >
      {selected && (
        <div className="absolute top-3 right-3">
          <CheckCircle2 className="w-5 h-5 text-blue-500" />
        </div>
      )}
      <div className={cn(
        'p-2 rounded-lg mb-3',
        selected ? 'bg-blue-100 dark:bg-blue-900/40' : 'bg-slate-100 dark:bg-slate-700'
      )}>
        <Icon className={cn('w-5 h-5', selected ? 'text-blue-600 dark:text-blue-400' : 'text-slate-600 dark:text-slate-400')} />
      </div>
      <h3 className={cn(
        'text-sm font-semibold mb-1',
        selected ? 'text-blue-700 dark:text-blue-300' : 'text-slate-900 dark:text-white'
      )}>
        {title}
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{description}</p>
    </button>
  );
}

/* ──────────────── Section Toggle ──────────────── */

interface SectionToggleProps {
  id: string;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  enabled: boolean;
  onToggle: () => void;
  disabled?: boolean;
  children?: React.ReactNode;
}

function SectionToggle({ icon: Icon, title, description, enabled, onToggle, disabled, children }: SectionToggleProps) {
  return (
    <div className={cn(
      'rounded-xl border transition-all',
      enabled
        ? 'border-blue-200 dark:border-blue-800 bg-white dark:bg-slate-800'
        : 'border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-800'
    )}>
      <button
        onClick={onToggle}
        disabled={disabled}
        className={cn(
          'w-full flex items-center gap-3 p-3.5 text-left transition-colors cursor-pointer',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {/* Checkbox */}
        <div className={cn(
          'w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0 transition-all',
          enabled
            ? 'bg-blue-500 border-blue-500'
            : 'border-slate-300 dark:border-slate-500'
        )}>
          {enabled && (
            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>

        {/* Icon */}
        <div className={cn(
          'p-1.5 rounded-lg',
          enabled ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-slate-100 dark:bg-slate-700'
        )}>
          <Icon className={cn('w-4 h-4', enabled ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500')} />
        </div>

        {/* Text */}
        <div className="flex-1 min-w-0">
          <span className={cn(
            'text-sm font-medium block',
            enabled ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400'
          )}>
            {title}
          </span>
          <span className="text-xs text-slate-400 dark:text-slate-500 block truncate">{description}</span>
        </div>
      </button>

      {/* Sub-options */}
      {enabled && children && (
        <div className="px-4 pb-4 pt-1 border-t border-slate-100 dark:border-slate-700/50">
          {children}
        </div>
      )}
    </div>
  );
}

/* ──────────────── Small checkbox for sub-options ──────────────── */

function SubOption({ label, checked, onToggle }: { label: string; checked: boolean; onToggle: () => void }) {
  return (
    <label className="flex items-center gap-2 py-1 cursor-pointer group" onClick={onToggle}>
      <div className={cn(
        'w-4 h-4 rounded border flex items-center justify-center transition-all',
        checked
          ? 'bg-blue-500 border-blue-500'
          : 'border-slate-300 dark:border-slate-500 group-hover:border-blue-400'
      )}>
        {checked && (
          <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
      <span className="text-xs text-slate-600 dark:text-slate-400">{label}</span>
    </label>
  );
}

/* ──────────────── Success Modal ──────────────── */

function SuccessMessage({ filePath, onOpenFile, onOpenFolder, onDismiss, t }: {
  filePath: string;
  onOpenFile: () => void;
  onOpenFolder: () => void;
  onDismiss: () => void;
  t: (key: string, opts?: Record<string, unknown>) => string;
}) {
  return (
    <div className="bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-xl p-5">
      <div className="flex items-start gap-3">
        <CheckCircle2 className="w-6 h-6 text-green-500 shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-green-800 dark:text-green-300">{t('reports:success.title')}</h3>
          <p className="text-xs text-green-600 dark:text-green-400 mt-1">{t('reports:success.message')}</p>
          <p className="text-xs text-green-500 dark:text-green-500 mt-1 font-mono break-all">
            {filePath}
          </p>
          <div className="flex gap-2 mt-3">
            <Button size="sm" onClick={onOpenFile}>
              <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
              {t('reports:success.openFile')}
            </Button>
            <Button size="sm" variant="outline" onClick={onOpenFolder}>
              <FolderOpen className="w-3.5 h-3.5 mr-1.5" />
              {t('reports:success.openFolder')}
            </Button>
            <Button size="sm" variant="ghost" onClick={onDismiss}>
              {t('common:actions.close')}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════
   MAIN REPORTS PAGE
   ══════════════════════════════════════════════ */

export function Reports() {
  const { t } = useTranslation('reports');
  const { dataset, outputPath } = useDataStore();
  const { outputDir, language } = useSettingsStore();
  const { lastTimingRecord } = usePipelineStore();

  // Report configuration state
  const [config, setConfig] = useState<ReportConfig>(() => ({
    template: 'executive',
    title: '',
    includeDate: true,
    includeDatasetInfo: true,
    includePageNumbers: true,
    sections: { ...TEMPLATE_PRESETS.executive.sections },
    visualizationCategories: { ...TEMPLATE_PRESETS.executive.visualizationCategories },
    summaryOptions: { ...TEMPLATE_PRESETS.executive.summaryOptions },
  }));

  // UI state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPath, setGeneratedPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sectionsExpanded, setSectionsExpanded] = useState(true);
  const [settingsExpanded, setSettingsExpanded] = useState(false);

  // Available categories from data (for summary filter)
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);

  // Check for analysis data availability
  const [hasInsightsData, setHasInsightsData] = useState(false);

  useEffect(() => {
    const checkData = async () => {
      try {
        const pythonDataDir = await window.electronAPI.app.getPythonDataDir();
        const result = await window.electronAPI.files.readFile(
          `${pythonDataDir}/visualizaciones/insights_textuales.json`
        );
        if (result.success && result.content) {
          setHasInsightsData(true);
          // Extract category names for the summary filter
          const data = JSON.parse(result.content);
          if (data?.resumenes?.estructurado?.por_categoria) {
            setAvailableCategories(Object.keys(data.resumenes.estructurado.por_categoria));
          }
        } else {
          setHasInsightsData(false);
        }
      } catch {
        setHasInsightsData(false);
      }
    };
    checkData();
  }, []);

  /* ── Template selection ── */
  const handleTemplateChange = useCallback((template: ReportTemplate) => {
    if (template === 'custom') {
      setConfig(prev => ({
        ...prev,
        template: 'custom',
        // Keep current selections for custom
      }));
    } else {
      const preset = TEMPLATE_PRESETS[template];
      setConfig(prev => ({
        ...prev,
        template,
        sections: { ...preset.sections },
        visualizationCategories: { ...preset.visualizationCategories },
        summaryOptions: { ...preset.summaryOptions },
        includeDate: preset.includeDate,
        includeDatasetInfo: preset.includeDatasetInfo,
        includePageNumbers: preset.includePageNumbers,
      }));
    }
  }, []);

  /* ── Section toggle ── */
  const toggleSection = useCallback((key: keyof ReportConfig['sections']) => {
    setConfig(prev => ({
      ...prev,
      template: 'custom', // auto-switch to custom mode
      sections: { ...prev.sections, [key]: !prev.sections[key] },
    }));
  }, []);

  /* ── Visualization category toggle ── */
  const toggleVisCat = useCallback((cat: VisualizationCategory) => {
    setConfig(prev => ({
      ...prev,
      template: 'custom',
      visualizationCategories: { ...prev.visualizationCategories, [cat]: !prev.visualizationCategories[cat] },
    }));
  }, []);

  /* ── Summary option toggles ── */
  const toggleSummaryGlobal = useCallback(() => {
    setConfig(prev => ({
      ...prev,
      template: 'custom',
      summaryOptions: { ...prev.summaryOptions, global: !prev.summaryOptions.global },
    }));
  }, []);

  const toggleSummaryCategories = useCallback(() => {
    setConfig(prev => ({
      ...prev,
      template: 'custom',
      summaryOptions: { ...prev.summaryOptions, categories: !prev.summaryOptions.categories },
    }));
  }, []);

  const toggleSelectedCategory = useCallback((cat: string) => {
    setConfig(prev => {
      const selected = prev.summaryOptions.selectedCategories.includes(cat)
        ? prev.summaryOptions.selectedCategories.filter(c => c !== cat)
        : [...prev.summaryOptions.selectedCategories, cat];
      return {
        ...prev,
        template: 'custom',
        summaryOptions: { ...prev.summaryOptions, selectedCategories: selected },
      };
    });
  }, []);

  /* ── Reset to default ── */
  const handleReset = useCallback(() => {
    const preset = TEMPLATE_PRESETS.executive;
    setConfig({
      template: 'executive',
      title: '',
      includeDate: true,
      includeDatasetInfo: true,
      includePageNumbers: true,
      sections: { ...preset.sections },
      visualizationCategories: { ...preset.visualizationCategories },
      summaryOptions: { ...preset.summaryOptions },
    });
    setGeneratedPath(null);
    setError(null);
  }, []);

  /* ── Count selected sections ── */
  const selectedSectionCount = useMemo(() => {
    return Object.values(config.sections).filter(Boolean).length;
  }, [config.sections]);

  const totalSectionCount = Object.keys(config.sections).length;

  /* ── Determine output directory ── */
  const resolvedOutputDir = useMemo(() => {
    // outputPath is a file path (dataset.csv), so extract the directory
    if (outputPath) {
      return outputPath.replace(/[/\\][^/\\]+$/, ''); // Remove filename to get directory
    }
    if (outputDir) return outputDir;
    return '';
  }, [outputPath, outputDir]);

  /* ── Generate report ── */
  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    setError(null);
    setGeneratedPath(null);

    try {
      // Determine output directory
      let targetDir = resolvedOutputDir;
      if (!targetDir) {
        const selected = await window.electronAPI.files.selectDirectory();
        if (!selected) {
          setIsGenerating(false);
          return;
        }
        targetDir = selected;
      }

      const filePath = await generatePdfReport({
        config,
        t,
        datasetName: dataset?.name || 'Unknown',
        outputDir: targetDir,
        timingRecords: lastTimingRecord
          ? Object.entries(lastTimingRecord.phases).map(([phaseNum, p]) => ({
              phase: Number(phaseNum),
              name: p.phaseName,
              duration: p.duration,
              status: p.status,
              startTime: p.startedAt,
              endTime: p.completedAt,
            }))
          : [],
      });
      setGeneratedPath(filePath);
    } catch (err) {
      console.error('[Reports] Generation failed:', err);
      setError(err instanceof Error ? err.message : t('reports:errors.generationFailed'));
    } finally {
      setIsGenerating(false);
    }
  }, [config, t, dataset, resolvedOutputDir, lastTimingRecord]);

  /* ── Open generated file ── */
  const handleOpenFile = useCallback(async () => {
    if (generatedPath) {
      await window.electronAPI.files.openPath(generatedPath);
    }
  }, [generatedPath]);

  const handleOpenFolder = useCallback(async () => {
    if (generatedPath) {
      const folderPath = generatedPath.replace(/[/\\][^/\\]+$/, '');
      await window.electronAPI.files.openPath(folderPath);
    }
  }, [generatedPath]);

  /* ── Section definition for the form ── */
  const sectionDefs: {
    key: keyof ReportConfig['sections'];
    icon: React.ComponentType<{ className?: string }>;
    titleKey: string;
    descKey: string;
  }[] = [
    { key: 'coverPage', icon: BookOpen, titleKey: 'sections.coverPage', descKey: 'sections.coverPageDesc' },
    { key: 'tableOfContents', icon: FileText, titleKey: 'sections.tableOfContents', descKey: 'sections.tableOfContentsDesc' },
    { key: 'kpis', icon: Target, titleKey: 'sections.kpis', descKey: 'sections.kpisDesc' },
    { key: 'sentimentAnalysis', icon: MessageSquare, titleKey: 'sections.sentimentAnalysis', descKey: 'sections.sentimentAnalysisDesc' },
    { key: 'subjectivityAnalysis', icon: Eye, titleKey: 'sections.subjectivityAnalysis', descKey: 'sections.subjectivityAnalysisDesc' },
    { key: 'ratingDistribution', icon: Star, titleKey: 'sections.ratingDistribution', descKey: 'sections.ratingDistributionDesc' },
    { key: 'categoryAnalysis', icon: Hash, titleKey: 'sections.categoryAnalysis', descKey: 'sections.categoryAnalysisDesc' },
    { key: 'topicAnalysis', icon: TrendingUp, titleKey: 'sections.topicAnalysis', descKey: 'sections.topicAnalysisDesc' },
    { key: 'temporalAnalysis', icon: Calendar, titleKey: 'sections.temporalAnalysis', descKey: 'sections.temporalAnalysisDesc' },
    { key: 'strengths', icon: ThumbsUp, titleKey: 'sections.strengths', descKey: 'sections.strengthsDesc' },
    { key: 'opportunities', icon: ThumbsDown, titleKey: 'sections.opportunities', descKey: 'sections.opportunitiesDesc' },
    { key: 'visualizations', icon: BarChart3, titleKey: 'sections.visualizations', descKey: 'sections.visualizationsDesc' },
    { key: 'summaries', icon: FileText, titleKey: 'sections.summaries', descKey: 'sections.summariesDesc' },
    { key: 'strategicInsights', icon: Briefcase, titleKey: 'sections.strategicInsights', descKey: 'sections.strategicInsightsDesc' },
    { key: 'pipelineTiming', icon: Clock, titleKey: 'sections.pipelineTiming', descKey: 'sections.pipelineTimingDesc' },
    { key: 'datasetValidation', icon: CheckCircle2, titleKey: 'sections.datasetValidation', descKey: 'sections.datasetValidationDesc' },
    { key: 'generationReport', icon: BarChart3, titleKey: 'sections.generationReport', descKey: 'sections.generationReportDesc' },
  ];

  // Visualization categories for sub-options
  const visCats: { key: VisualizationCategory; labelKey: string }[] = [
    { key: 'sentimientos', labelKey: 'visualizationCategories.sentimientos' },
    { key: 'subjetividad', labelKey: 'visualizationCategories.subjetividad' },
    { key: 'categorias', labelKey: 'visualizationCategories.categorias' },
    { key: 'topicos', labelKey: 'visualizationCategories.topicos' },
    { key: 'temporal', labelKey: 'visualizationCategories.temporal' },
    { key: 'texto', labelKey: 'visualizationCategories.texto' },
    { key: 'combinados', labelKey: 'visualizationCategories.combinados' },
  ];

  const translateCatName = (cat: string): string => {
    const key = `common:dataLabels.categories.${cat.replace(/^["']|["']$/g, '')}`;
    const translated = t(key);
    return translated !== key ? translated : cat.replace(/^["']|["']$/g, '');
  };

  /* ══════════════════════════════════════════════
     RENDER
     ══════════════════════════════════════════════ */

  return (
    <PageLayout
      title={t('title')}
      description={t('description')}
      headerActions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-2" />
            {t('actions.reset')}
          </Button>
          <Button
            size="sm"
            onClick={handleGenerate}
            disabled={!hasInsightsData || isGenerating || selectedSectionCount === 0}
          >
            {isGenerating ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Download className="w-4 h-4 mr-2" />
            )}
            {isGenerating ? t('actions.generating') : t('actions.generate')}
          </Button>
        </div>
      }
    >
      {/* No data warning */}
      {!hasInsightsData ? (
        <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600">
          <AlertTriangle className="w-16 h-16 text-amber-400 mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">
            {t('errors.noData')}
          </h3>
          <p className="text-slate-500 dark:text-slate-400 text-center max-w-md">
            {t('errors.noDataDesc')}
          </p>
        </div>
      ) : (
        <div className="space-y-6 max-w-4xl mx-auto pb-8">
          {/* Success message */}
          {generatedPath && (
            <SuccessMessage
              filePath={generatedPath}
              onOpenFile={handleOpenFile}
              onOpenFolder={handleOpenFolder}
              onDismiss={() => setGeneratedPath(null)}
              t={t}
            />
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            </div>
          )}

          {/* ── 1. TEMPLATE SELECTION ── */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600 p-5">
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">
              {t('templates.title')}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              {t('templates.description')}
            </p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <TemplateCard
                id="executive"
                icon={Briefcase}
                title={t('templates.executive')}
                description={t('templates.executiveDesc')}
                selected={config.template === 'executive'}
                onSelect={() => handleTemplateChange('executive')}
              />
              <TemplateCard
                id="detailed"
                icon={FileText}
                title={t('templates.detailed')}
                description={t('templates.detailedDesc')}
                selected={config.template === 'detailed'}
                onSelect={() => handleTemplateChange('detailed')}
              />
              <TemplateCard
                id="visual"
                icon={Image}
                title={t('templates.visualOnly')}
                description={t('templates.visualOnlyDesc')}
                selected={config.template === 'visual'}
                onSelect={() => handleTemplateChange('visual')}
              />
              <TemplateCard
                id="custom"
                icon={SlidersHorizontal}
                title={t('templates.custom')}
                description={t('templates.customDesc')}
                selected={config.template === 'custom'}
                onSelect={() => handleTemplateChange('custom')}
              />
            </div>
          </div>

          {/* ── 2. SECTION SELECTION ── */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600 overflow-hidden">
            <button
              className="w-full flex items-center justify-between p-5 text-left cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
              onClick={() => setSectionsExpanded(!sectionsExpanded)}
            >
              <div>
                <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                  {t('sections.title')}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {t('sections.description')} — {selectedSectionCount}/{totalSectionCount}
                </p>
              </div>
              {sectionsExpanded ? (
                <ChevronUp className="w-5 h-5 text-slate-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              )}
            </button>

            {sectionsExpanded && (
              <div className="px-5 pb-5 grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {sectionDefs.map((sec) => (
                  <SectionToggle
                    key={sec.key}
                    id={sec.key}
                    icon={sec.icon}
                    title={t(sec.titleKey)}
                    description={t(sec.descKey)}
                    enabled={config.sections[sec.key]}
                    onToggle={() => toggleSection(sec.key)}
                  >
                    {/* Visualization sub-options */}
                    {sec.key === 'visualizations' && config.sections.visualizations && (
                      <div className="mt-2 space-y-0.5">
                        <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
                          {t('visualizationCategories.title')}
                        </p>
                        {visCats.map(vc => (
                          <SubOption
                            key={vc.key}
                            label={t(vc.labelKey)}
                            checked={config.visualizationCategories[vc.key]}
                            onToggle={() => toggleVisCat(vc.key)}
                          />
                        ))}
                      </div>
                    )}

                    {/* Summary sub-options */}
                    {sec.key === 'summaries' && config.sections.summaries && (
                      <div className="mt-2 space-y-0.5">
                        <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
                          {t('summaryOptions.title')}
                        </p>
                        <SubOption
                          label={t('summaryOptions.global')}
                          checked={config.summaryOptions.global}
                          onToggle={toggleSummaryGlobal}
                        />
                        <SubOption
                          label={t('summaryOptions.categories')}
                          checked={config.summaryOptions.categories}
                          onToggle={toggleSummaryCategories}
                        />
                        {config.summaryOptions.categories && availableCategories.length > 0 && (
                          <div className="ml-6 mt-1 space-y-0.5">
                            <p className="text-xs text-slate-400 dark:text-slate-500 mb-1">
                              {config.summaryOptions.selectedCategories.length === 0
                                ? t('summaryOptions.allCategories')
                                : t('summaryOptions.selectCategories')}
                            </p>
                            {availableCategories.map(cat => (
                              <SubOption
                                key={cat}
                                label={translateCatName(cat)}
                                checked={
                                  config.summaryOptions.selectedCategories.length === 0 ||
                                  config.summaryOptions.selectedCategories.includes(cat)
                                }
                                onToggle={() => toggleSelectedCategory(cat)}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </SectionToggle>
                ))}
              </div>
            )}
          </div>

          {/* ── 3. REPORT SETTINGS ── */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600 overflow-hidden">
            <button
              className="w-full flex items-center justify-between p-5 text-left cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
              onClick={() => setSettingsExpanded(!settingsExpanded)}
            >
              <div>
                <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                  {t('reportSettings.title')}
                </h2>
              </div>
              {settingsExpanded ? (
                <ChevronUp className="w-5 h-5 text-slate-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-400" />
              )}
            </button>

            {settingsExpanded && (
              <div className="px-5 pb-5 space-y-4">
                {/* Report title */}
                <div>
                  <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
                    {t('reportSettings.reportTitle')}
                  </label>
                  <input
                    type="text"
                    value={config.title}
                    onChange={(e) => setConfig(prev => ({ ...prev, title: e.target.value }))}
                    placeholder={t('reportSettings.reportTitlePlaceholder')}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Toggle options */}
                <div className="space-y-2">
                  <SubOption
                    label={t('reportSettings.includeDate')}
                    checked={config.includeDate}
                    onToggle={() => setConfig(prev => ({ ...prev, includeDate: !prev.includeDate }))}
                  />
                  <SubOption
                    label={t('reportSettings.includeDatasetInfo')}
                    checked={config.includeDatasetInfo}
                    onToggle={() => setConfig(prev => ({ ...prev, includeDatasetInfo: !prev.includeDatasetInfo }))}
                  />
                  <SubOption
                    label={t('reportSettings.pageNumbers')}
                    checked={config.includePageNumbers}
                    onToggle={() => setConfig(prev => ({ ...prev, includePageNumbers: !prev.includePageNumbers }))}
                  />
                </div>

                {/* Language info */}
                <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-700/50 rounded-lg p-3">
                  <span>{t('reportSettings.language')}:</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">
                    {t('reportSettings.languageAuto', { lang: language === 'es' ? 'Español' : 'English' })}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* ── GENERATE BUTTON (bottom) ── */}
          <div className="flex items-center justify-between bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600 p-5">
            <div className="text-sm text-slate-500 dark:text-slate-400">
              {selectedSectionCount} / {totalSectionCount} {t('sections.title').toLowerCase()}
            </div>
            <Button
              onClick={handleGenerate}
              disabled={isGenerating || selectedSectionCount === 0}
              className="min-w-45"
            >
              {isGenerating ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Download className="w-4 h-4 mr-2" />
              )}
              {isGenerating ? t('actions.generating') : t('actions.generate')}
            </Button>
          </div>
        </div>
      )}
    </PageLayout>
  );
}

export default Reports;

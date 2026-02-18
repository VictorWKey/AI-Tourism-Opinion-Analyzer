/**
 * Report Types
 * =============
 * Type definitions for the Reports feature
 */

/** Available report templates */
export type ReportTemplate = 'executive' | 'detailed' | 'visual' | 'custom';

/** Visualization category keys matching the Python output folders */
export type VisualizationCategory =
  | 'sentimientos'
  | 'subjetividad'
  | 'categorias'
  | 'topicos'
  | 'temporal'
  | 'texto'
  | 'combinados';

/** Full report configuration */
export interface ReportConfig {
  template: ReportTemplate;
  title: string;

  // Meta options
  includeDate: boolean;
  includeDatasetInfo: boolean;
  includePageNumbers: boolean;

  // Sections toggle
  sections: {
    coverPage: boolean;
    tableOfContents: boolean;
    kpis: boolean;
    sentimentAnalysis: boolean;
    subjectivityAnalysis: boolean;
    ratingDistribution: boolean;
    categoryAnalysis: boolean;
    topicAnalysis: boolean;
    temporalAnalysis: boolean;
    strengths: boolean;
    opportunities: boolean;
    visualizations: boolean;
    summaries: boolean;
    strategicInsights: boolean;
    pipelineTiming: boolean;
  };

  // Visualization sub-options (when visualizations section is enabled)
  visualizationCategories: Record<VisualizationCategory, boolean>;

  // Summary sub-options (when summaries section is enabled)
  summaryOptions: {
    global: boolean;
    categories: boolean;
    selectedCategories: string[]; // empty = all
  };
}

/** Template preset configurations */
export const TEMPLATE_PRESETS: Record<Exclude<ReportTemplate, 'custom'>, Omit<ReportConfig, 'template' | 'title'>> = {
  executive: {
    includeDate: true,
    includeDatasetInfo: true,
    includePageNumbers: true,
    sections: {
      coverPage: true,
      tableOfContents: false,
      kpis: true,
      sentimentAnalysis: true,
      subjectivityAnalysis: false,
      ratingDistribution: true,
      categoryAnalysis: true,
      topicAnalysis: false,
      temporalAnalysis: false,
      strengths: true,
      opportunities: true,
      visualizations: false,
      summaries: true,
      strategicInsights: true,
      pipelineTiming: false,
    },
    visualizationCategories: {
      sentimientos: false,
      subjetividad: false,
      categorias: false,
      topicos: false,
      temporal: false,
      texto: false,
      combinados: false,
    },
    summaryOptions: {
      global: true,
      categories: false,
      selectedCategories: [],
    },
  },
  detailed: {
    includeDate: true,
    includeDatasetInfo: true,
    includePageNumbers: true,
    sections: {
      coverPage: true,
      tableOfContents: true,
      kpis: true,
      sentimentAnalysis: true,
      subjectivityAnalysis: true,
      ratingDistribution: true,
      categoryAnalysis: true,
      topicAnalysis: true,
      temporalAnalysis: true,
      strengths: true,
      opportunities: true,
      visualizations: true,
      summaries: true,
      strategicInsights: true,
      pipelineTiming: true,
    },
    visualizationCategories: {
      sentimientos: true,
      subjetividad: true,
      categorias: true,
      topicos: true,
      temporal: true,
      texto: true,
      combinados: true,
    },
    summaryOptions: {
      global: true,
      categories: true,
      selectedCategories: [],
    },
  },
  visual: {
    includeDate: true,
    includeDatasetInfo: true,
    includePageNumbers: true,
    sections: {
      coverPage: true,
      tableOfContents: false,
      kpis: true,
      sentimentAnalysis: true,
      subjectivityAnalysis: false,
      ratingDistribution: false,
      categoryAnalysis: false,
      topicAnalysis: false,
      temporalAnalysis: false,
      strengths: false,
      opportunities: false,
      visualizations: true,
      summaries: false,
      strategicInsights: false,
      pipelineTiming: false,
    },
    visualizationCategories: {
      sentimientos: true,
      subjetividad: true,
      categorias: true,
      topicos: true,
      temporal: true,
      texto: false,
      combinados: true,
    },
    summaryOptions: {
      global: false,
      categories: false,
      selectedCategories: [],
    },
  },
};

/** Get a default "custom" config (everything enabled) */
export function getDefaultCustomConfig(): Omit<ReportConfig, 'template' | 'title'> {
  return { ...TEMPLATE_PRESETS.detailed };
}

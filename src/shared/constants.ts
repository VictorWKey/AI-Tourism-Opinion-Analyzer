// ============================================
// AI Tourism Opinion Analyzer - Constants
// ============================================

export const PIPELINE_PHASES = [
  {
    id: 1,
    name: 'Basic Processing',
    description: 'Clean and preprocess the dataset',
    requiresLLM: false,
  },
  {
    id: 2,
    name: 'Sentiment Analysis',
    description: 'Analyze sentiment using HuggingFace BERT',
    requiresLLM: false,
  },
  {
    id: 3,
    name: 'Subjectivity Analysis',
    description: 'Classify subjective vs objective content',
    requiresLLM: false,
  },
  {
    id: 4,
    name: 'Category Classification',
    description: 'Multi-label category classification',
    requiresLLM: false,
  },
  {
    id: 5,
    name: 'Hierarchical Topic Analysis',
    description: 'Topic modeling with BERTopic + LLM',
    requiresLLM: true,
  },
  {
    id: 6,
    name: 'Intelligent Summarization',
    description: 'Generate summaries with LangChain + LLM',
    requiresLLM: true,
  },
  {
    id: 7,
    name: 'Visualization Generation',
    description: 'Create charts and visualizations',
    requiresLLM: false,
  },
] as const;

export const DEFAULT_LLM_CONFIG = {
  mode: 'local' as const,
  localModel: 'llama3.2:3b',
  apiProvider: 'openai' as const,
  apiKey: '',
  apiModel: 'gpt-4o-mini',
  temperature: 0.7,
};

export const DEFAULT_APP_SETTINGS = {
  theme: 'system' as const,
  language: 'en',
  outputDir: '',
};

export const SUPPORTED_FILE_EXTENSIONS = ['.csv', '.xlsx', '.xls'];

export const APP_NAME = 'AI Tourism Opinion Analyzer';
export const APP_VERSION = '1.0.0';

/**
 * SetupWizard - First-run setup wizard component
 * ===============================================
 * Multi-step wizard for initial app configuration including:
 * - System requirements check
 * - LLM provider selection (Ollama vs OpenAI)
 * - Ollama model selection with hardware recommendations
 * - OpenAI model selection with recommendations
 * - Ollama installation and model download
 * - OpenAI API key validation
 * - ML models download
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, 
  Circle, 
  Loader2, 
  AlertCircle, 
  Monitor, 
  Cloud, 
  Download, 
  Cpu, 
  ArrowLeft,
  ArrowRight,
  Sparkles,
  Zap,
  HardDrive,
  ChevronRight,
  Check,
  X,
  Folder
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Progress } from '../ui/progress';
import { cn } from '../../lib/utils';
import type { 
  SystemCheckResult, 
  OllamaDownloadProgress, 
  ModelDownloadProgress,
  ModelInfo,
} from '../../../shared/types';

// Ollama model options with hardware recommendations
// NOTE: minRam values are the REALISTIC minimums for acceptable performance
// LLMs need significant RAM beyond just the model size for inference

/** Sanitize a model ID into a valid i18n key (e.g. 'llama3.1:8b' → 'llama3_1_8b') */
const modelKey = (id: string) => id.replace(/[.:\-]/g, '_');

interface OllamaModelOption {
  id: string;
  name: string;
  size: string;
  minRam: number; // Realistic minimum RAM in GB for good performance
  minVram?: number; // Minimum VRAM in GB for GPU acceleration (optional)
  recommended: boolean;
  performance: 'fast' | 'balanced' | 'powerful';
}

const OLLAMA_MODELS: OllamaModelOption[] = [
  {
    id: 'llama3.1:8b',
    name: 'Llama 3.1 8B',
    size: '~4.9 GB',
    minRam: 16, // 8B models need ~16GB RAM
    minVram: 8,
    recommended: true,
    performance: 'balanced',
  },
  {
    id: 'deepseek-r1:14b',
    name: 'DeepSeek R1 14B',
    size: '~9.0 GB',
    minRam: 32, // 14B models need ~32GB RAM
    minVram: 12,
    recommended: false,
    performance: 'powerful',
  },
  {
    id: 'deepseek-r1:8b',
    name: 'DeepSeek R1 8B',
    size: '~9.0 GB',
    minRam: 24, // 8B DeepSeek needs more RAM due to architecture
    minVram: 10,
    recommended: false,
    performance: 'powerful',
  },
  {
    id: 'mistral:7b',
    name: 'Mistral 7B',
    size: '~4.4 GB',
    minRam: 12,
    minVram: 6,
    recommended: false,
    performance: 'fast',
  },
];

// OpenAI model options
interface OpenAIModelOption {
  id: string;
  name: string;
  costTier: 'low' | 'medium' | 'high';
  recommended: boolean;
}

const OPENAI_MODELS: OpenAIModelOption[] = [
  {
    id: 'gpt-5-mini',
    name: 'GPT-5 Mini',
    costTier: 'low',
    recommended: true,
  },
  {
    id: 'gpt-5-nano',
    name: 'GPT-5 Nano',
    costTier: 'low',
    recommended: false,
  },
  {
    id: 'gpt-5',
    name: 'GPT-5',
    costTier: 'high',
    recommended: false,
  },
];

type SetupStep = 'welcome' | 'python-setup' | 'hardware-select' | 'llm-choice' | 'model-select' | 'llm-setup' | 'models' | 'output-dir' | 'complete';

interface SetupWizardProps {
  onComplete: () => void;
}

// Hardware configuration
interface HardwareConfig {
  cpu: 'low' | 'mid' | 'high';
  ram: number; // in GB
  gpu: 'none' | 'integrated' | 'dedicated';
  vram?: number; // in GB, only if dedicated GPU
}

// Step order for navigation
const STEP_ORDER: SetupStep[] = ['welcome', 'python-setup', 'hardware-select', 'llm-choice', 'model-select', 'llm-setup', 'models', 'output-dir', 'complete'];

function getStepIndex(step: SetupStep): number {
  return STEP_ORDER.indexOf(step);
}

export function SetupWizard({ onComplete }: SetupWizardProps) {
  const { t } = useTranslation('setup');
  const [currentStep, setCurrentStep] = useState<SetupStep>('welcome');
  const [llmChoice, setLlmChoice] = useState<'ollama' | 'openai' | null>(null);
  const [selectedOllamaModel, setSelectedOllamaModel] = useState<string>('llama3.1:8b');
  const [customOllamaModel, setCustomOllamaModel] = useState<string>('');
  const [useCustomOllamaModel, setUseCustomOllamaModel] = useState(false);
  const [selectedOpenAIModel, setSelectedOpenAIModel] = useState<string>('gpt-5-mini');
  const [customOpenAIModel, setCustomOpenAIModel] = useState<string>('');
  const [useCustomOpenAIModel, setUseCustomOpenAIModel] = useState(false);
  const [hardwareConfig, setHardwareConfig] = useState<HardwareConfig>({
    cpu: 'mid',
    ram: 8,
    gpu: 'none',
  });
  const [ollamaProgress, setOllamaProgress] = useState<OllamaDownloadProgress>({
    stage: 'idle',
    progress: 0,
    message: '',
  });
  const [modelProgress, setModelProgress] = useState<Record<string, number>>({});
  const [openaiKey, setOpenaiKey] = useState('');
  const [keyError, setKeyError] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [outputDir, setOutputDir] = useState<string>('');

  // Listen for progress updates
  useEffect(() => {
    const handleOllamaProgress = (_: unknown, data: OllamaDownloadProgress) => {
      setOllamaProgress(data);
      if (data.stage === 'complete') {
        setTimeout(() => setCurrentStep('models'), 1000);
      }
    };

    const handleModelProgress = (_: unknown, data: ModelDownloadProgress) => {
      setModelProgress((prev) => ({ ...prev, [data.model]: data.progress }));
    };

    window.electronAPI.setup.onOllamaProgress(handleOllamaProgress);
    window.electronAPI.setup.onModelProgress(handleModelProgress);

    return () => {
      window.electronAPI.setup.offOllamaProgress();
      window.electronAPI.setup.offModelProgress();
    };
  }, []);

  // Navigation handlers
  const goBack = useCallback(() => {
    const currentIndex = getStepIndex(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(STEP_ORDER[currentIndex - 1]);
    }
  }, [currentStep]);

  const handleHardwareSelect = useCallback((config: HardwareConfig) => {
    setHardwareConfig(config);
    
    // Pre-select the recommended Ollama model based on detected hardware
    const totalRam = config.ram;
    const hasGPU = config.gpu === 'dedicated';
    const vram = config.vram || 0;
    
    if (totalRam >= 32 || (hasGPU && vram >= 12)) {
      setSelectedOllamaModel('deepseek-r1:14b');
    } else if (totalRam >= 24 || (hasGPU && vram >= 10)) {
      setSelectedOllamaModel('deepseek-r1:8b');
    } else if (totalRam >= 16 || (hasGPU && vram >= 8)) {
      setSelectedOllamaModel('llama3.1:8b');
    } else if (totalRam >= 12 || (hasGPU && vram >= 6)) {
      setSelectedOllamaModel('mistral:7b');
    } else {
      setSelectedOllamaModel('mistral:7b');
    }
    
    setCurrentStep('llm-choice');
  }, []);

  const handleLLMChoice = useCallback(async (choice: 'ollama' | 'openai') => {
    setLlmChoice(choice);
    await window.electronAPI.setup.setLLMProvider(choice);
    setCurrentStep('model-select');
  }, []);

  const handleModelSelect = useCallback(() => {
    setCurrentStep('llm-setup');
  }, []);

  const getSelectedModel = useCallback(() => {
    if (llmChoice === 'ollama') {
      return useCustomOllamaModel ? customOllamaModel : selectedOllamaModel;
    }
    return useCustomOpenAIModel ? customOpenAIModel : selectedOpenAIModel;
  }, [llmChoice, useCustomOllamaModel, customOllamaModel, selectedOllamaModel, useCustomOpenAIModel, customOpenAIModel, selectedOpenAIModel]);

  // Unified Ollama installation: software + model in one seamless process
  // Installation is NOT complete until a model is successfully installed
  const handleOllamaSetup = useCallback(async () => {
    const modelToUse = useCustomOllamaModel ? customOllamaModel : selectedOllamaModel;
    
    // Check if already fully ready (installed + running + has this model)
    const readyStatus = await window.electronAPI.setup.checkOllamaFullyReady();
    
    if (readyStatus.ready) {
      // Check if the specific model is available
      const hasModel = await window.electronAPI.setup.hasOllamaModel(modelToUse);
      if (hasModel) {
        setOllamaProgress({ 
          stage: 'complete', 
          progress: 100, 
          message: t('ollamaSetup.allReady'),
          unifiedProgress: 100,
          currentPhase: 'model'
        });
        setTimeout(() => setCurrentStep('models'), 500);
        return;
      }
      // Model not found, just pull it (already installed)
      setOllamaProgress({ 
        stage: 'pulling-model', 
        progress: 0, 
        message: t('ollamaSetup.downloadingModelProgress', { model: modelToUse }),
        unifiedProgress: 50,
        currentPhase: 'model'
      });
      await window.electronAPI.setup.pullOllamaModel(modelToUse);
    } else {
      // Use unified installation - software + model in one step
      // Progress callback will show unified progress bar
      setOllamaProgress({ 
        stage: 'downloading', 
        progress: 0, 
        message: t('ollamaSetup.startingUnified'),
        unifiedProgress: 0,
        currentPhase: 'software'
      });
      
      const success = await window.electronAPI.setup.installOllamaWithModel(modelToUse);
      
      if (!success) {
        setOllamaProgress({ 
          stage: 'error', 
          progress: 0, 
          message: t('ollamaSetup.installFailed'),
          error: t('ollamaSetup.installIncomplete'),
          unifiedProgress: 0,
          currentPhase: 'software'
        });
        return;
      }
    }
  }, [selectedOllamaModel, customOllamaModel, useCustomOllamaModel]);

  const handleOpenAISetup = useCallback(async () => {
    setIsValidating(true);
    setKeyError('');

    try {
      const result = await window.electronAPI.setup.validateOpenAIKey(openaiKey);
      
      if (result.valid) {
        const modelToUse = useCustomOpenAIModel ? customOpenAIModel : selectedOpenAIModel;
        await window.electronAPI.settings.set('llm.apiKey', openaiKey);
        await window.electronAPI.settings.set('llm.apiModel', modelToUse);
        setCurrentStep('models');
      } else {
        setKeyError(result.error || 'Invalid API key');
      }
    } catch (error) {
      setKeyError('Failed to validate API key');
    } finally {
      setIsValidating(false);
    }
  }, [openaiKey, selectedOpenAIModel, customOpenAIModel, useCustomOpenAIModel]);

  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleModelDownload = useCallback(async () => {
    setIsLoading(true);
    setDownloadError(null);
    try {
      const result = await window.electronAPI.setup.downloadModels();
      if (result.success) {
        setCurrentStep('output-dir');
      } else {
        const errorDetail = result.error ? `: ${result.error}` : '';
        setDownloadError(`${t('modelDownload.downloadFailed')}${errorDetail}`);
      }
    } catch (error) {
      console.error('Model download failed:', error);
      const msg = error instanceof Error ? error.message : String(error);
      setDownloadError(`${t('modelDownload.unexpectedError')} ${msg}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleOutputDirSelect = useCallback(async () => {
    const dir = await window.electronAPI.files.selectDirectory();
    if (dir) {
      setOutputDir(dir);
    }
  }, []);

  const handleOutputDirNext = useCallback(async () => {
    // Save output directory to settings
    if (outputDir) {
      await window.electronAPI.settings.set('app', {
        language: 'es',
        outputDir,
      });
    }
    setCurrentStep('complete');
  }, [outputDir]);

  const handleComplete = useCallback(async () => {
    await window.electronAPI.setup.complete();
    onComplete();
  }, [onComplete]);

  // Check if back navigation is available
  const canGoBack = currentStep !== 'welcome' && currentStep !== 'complete' && ollamaProgress.stage !== 'downloading';

  return (
    <div className="fixed inset-0 bg-slate-100 dark:bg-slate-900 flex items-center justify-center p-4">
      <motion.div
        className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 w-full max-w-3xl max-h-[90vh] flex flex-col"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Progress indicator */}
        <div className="px-4 sm:px-8 pt-4 sm:pt-6 pb-3 sm:pb-4 border-b border-slate-100 dark:border-slate-700 flex-shrink-0">
          <StepIndicator currentStep={currentStep} llmChoice={llmChoice} />
        </div>

        {/* Content with scroll */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-4 sm:py-6">
          <AnimatePresence mode="wait">
            {/* Step 1: Welcome */}
            {currentStep === 'welcome' && (
              <WelcomeStep onNext={() => setCurrentStep('python-setup')} />
            )}

            {/* Step 2: Python Setup */}
            {currentStep === 'python-setup' && (
              <PythonSetupStep 
                onNext={() => setCurrentStep('hardware-select')}
                onBack={goBack}
              />
            )}

            {/* Step 3: Hardware Selection */}
            {currentStep === 'hardware-select' && (
              <HardwareSelectStep
                config={hardwareConfig}
                onSelect={handleHardwareSelect}
                onBack={goBack}
              />
            )}

            {/* Step 3: LLM Choice */}
            {currentStep === 'llm-choice' && (
              <LLMChoiceStep 
                onSelect={handleLLMChoice} 
                hardwareConfig={hardwareConfig}
                onBack={goBack}
              />
            )}

            {/* Step 4: Model Selection */}
            {currentStep === 'model-select' && (
              llmChoice === 'ollama' ? (
                <OllamaModelSelectStep
                  selectedModel={selectedOllamaModel}
                  onSelectModel={setSelectedOllamaModel}
                  customModel={customOllamaModel}
                  onCustomModelChange={setCustomOllamaModel}
                  useCustom={useCustomOllamaModel}
                  onUseCustomChange={setUseCustomOllamaModel}
                  hardwareConfig={hardwareConfig}
                  onNext={handleModelSelect}
                  onBack={goBack}
                />
              ) : (
                <OpenAIModelSelectStep
                  selectedModel={selectedOpenAIModel}
                  onSelectModel={setSelectedOpenAIModel}
                  customModel={customOpenAIModel}
                  onCustomModelChange={setCustomOpenAIModel}
                  useCustom={useCustomOpenAIModel}
                  onUseCustomChange={setUseCustomOpenAIModel}
                  onNext={handleModelSelect}
                  onBack={goBack}
                />
              )
            )}

            {/* Step 5: LLM Setup */}
            {currentStep === 'llm-setup' && (
              llmChoice === 'ollama' ? (
                <OllamaSetupStep
                  progress={ollamaProgress}
                  onStart={handleOllamaSetup}
                  modelName={useCustomOllamaModel ? customOllamaModel : selectedOllamaModel}
                  onBack={goBack}
                />
              ) : (
                <OpenAISetupStep
                  apiKey={openaiKey}
                  onKeyChange={setOpenaiKey}
                  error={keyError}
                  isValidating={isValidating}
                  onSubmit={handleOpenAISetup}
                  modelName={useCustomOpenAIModel ? customOpenAIModel : selectedOpenAIModel}
                  onBack={goBack}
                />
              )
            )}

            {/* Step 6: Model Downloads */}
            {currentStep === 'models' && (
              <ModelDownloadStep
                progress={modelProgress}
                onStart={handleModelDownload}
                isLoading={isLoading}
                onBack={goBack}
                onNext={() => setCurrentStep('output-dir')}
                error={downloadError}
              />
            )}

            {/* Step 7: Output Directory */}
            {currentStep === 'output-dir' && (
              <OutputDirStep
                outputDir={outputDir}
                onSelectDir={handleOutputDirSelect}
                onNext={handleOutputDirNext}
                onBack={goBack}
              />
            )}

            {/* Step 8: Complete */}
            {currentStep === 'complete' && (
              <CompleteStep onFinish={handleComplete} />
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}

// Step indicator component
function StepIndicator({ currentStep, llmChoice }: { currentStep: SetupStep; llmChoice: 'ollama' | 'openai' | null }) {
  const { t } = useTranslation('setup');
  const steps = [
    { key: 'welcome', label: t('steps.start') },
    { key: 'python-setup', label: t('steps.python') },
    { key: 'hardware-select', label: t('steps.hardware') },
    { key: 'llm-choice', label: t('steps.ai') },
    { key: 'model-select', label: t('steps.model') },
    { key: 'llm-setup', label: t('steps.config') },
    { key: 'models', label: t('steps.downloads') },
    { key: 'output-dir', label: t('steps.output') },
    { key: 'complete', label: t('steps.ready') },
  ];

  const currentIndex = steps.findIndex(s => s.key === currentStep);

  return (
    <div className="space-y-3">
      {/* Compact step indicators */}
      <div className="flex gap-2">
        {steps.map((step, index) => (
          <motion.div
            key={step.key}
            className={cn(
              "h-8 px-2.5 rounded-full flex items-center justify-center text-xs font-medium transition-colors cursor-default",
              index < currentIndex
                ? "bg-emerald-500 text-white"
                : index === currentIndex
                  ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900"
                  : "bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400"
            )}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: index * 0.05, duration: 0.3 }}
          >
            {index < currentIndex ? (
              <Check className="w-4 h-4" />
            ) : (
              <span>{index + 1}</span>
            )}
          </motion.div>
        ))}
      </div>

      {/* Current step label */}
      <div className="text-center">
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {t('steps.progress', { current: currentIndex + 1, total: steps.length })} <span className="font-semibold text-slate-900 dark:text-white">{steps[currentIndex].label}</span>
        </p>
      </div>
    </div>
  );
}

// Sub-components for each step

function WelcomeStep({ 
  onNext
}: { 
  onNext: () => void;
}) {
  const { t } = useTranslation('setup');
  return (
    <motion.div
      className="text-center py-4 sm:py-6"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="welcome"
    >
      <div className="w-14 h-14 sm:w-16 sm:h-16 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
        <Sparkles className="w-7 h-7 sm:w-8 sm:h-8 text-slate-700 dark:text-slate-300" />
      </div>
      <h1 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">{t('welcome.title')}</h1>
      <h2 className="text-base sm:text-lg text-slate-500 dark:text-slate-400 mb-4 sm:mb-6">AI Tourism Opinion Analyzer</h2>
      <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 mb-6 sm:mb-8 max-w-md mx-auto leading-relaxed px-4">
        {t('welcome.description')}
      </p>
      <Button size="lg" onClick={onNext} className="px-6 sm:px-8">
        {t('welcome.start')}
        <ArrowRight className="w-4 h-4 ml-2" />
      </Button>
    </motion.div>
  );
}

// Python Setup Step - Automatic Python environment configuration
function PythonSetupStep({
  onNext,
  onBack,
}: {
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  const [status, setStatus] = useState<'checking' | 'ready' | 'need-install' | 'setting-up' | 'error'>('checking');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(t('pythonSetup.checking'));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check Python status on mount
    checkPython();

    // Listen for progress updates
    const handleProgress = (_: unknown, data: { stage: string; progress: number; message: string; error?: string }) => {
      setProgress(data.progress);
      setMessage(data.message);
      
      if (data.stage === 'complete') {
        setStatus('ready');
        // Auto-advance after a short delay
        setTimeout(() => onNext(), 1500);
      } else if (data.stage === 'error') {
        setStatus('error');
        setError(data.error || t('pythonSetup.unknownError'));
      }
    };

    window.electronAPI.setup.onPythonProgress(handleProgress);

    return () => {
      window.electronAPI.setup.offPythonProgress();
    };
  }, [onNext]);

  const checkPython = async () => {
    setStatus('checking');
    setMessage(t('pythonSetup.checking'));
    
    try {
      const pythonStatus = await window.electronAPI.setup.checkPython();
      
      // IMPORTANT: Check for setupComplete marker, not just file existence
      // This properly detects interrupted installations
      if (pythonStatus.setupComplete && pythonStatus.dependenciesInstalled) {
        // Python is fully ready (completed successfully before)
        setStatus('ready');
        setProgress(100);
        setMessage(t('pythonSetup.ready'));
        setTimeout(() => onNext(), 1000);
      } else if (pythonStatus.installationInterrupted) {
        // Installation was interrupted - show message and offer to reinstall
        setStatus('need-install');
        setProgress(0);
        setMessage(t('pythonSetup.incompleteDetected'));
      } else if (pythonStatus.venvExists && pythonStatus.dependenciesInstalled && !pythonStatus.setupComplete) {
        // Edge case: venv exists but no completion marker - treat as incomplete
        setStatus('need-install');
        setProgress(0);
        setMessage(t('pythonSetup.previousFailed'));
      } else {
        // Python needs setup - show install button
        setStatus('need-install');
        setProgress(0);
        setMessage(t('pythonSetup.notConfigured'));
      }
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Error verificando Python');
    }
  };

  const handleInstallPython = async () => {
    setStatus('setting-up');
    setMessage(t('pythonSetup.configuring'));
    setProgress(0);
    await window.electronAPI.setup.setupPython();
  };

  const handleRetry = () => {
    setError(null);
    checkPython();
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="python-setup"
    >
      <div className="text-center mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Cpu className="w-7 h-7 sm:w-8 sm:h-8 text-blue-600" />
        </div>
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('pythonSetup.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400">
          {t('pythonSetup.subtitle')}
        </p>
      </div>

      <div className="space-y-6">
        <div className="max-w-md mx-auto">
          {/* Progress during setup */}
          {(status === 'checking' || status === 'setting-up') && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{message}</span>
                </div>
                <span className="text-sm font-bold text-blue-600">{Math.round(progress)}%</span>
              </div>
              <div className="relative h-6 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full shadow-sm transition-all duration-300 ease-out"
                  style={{ width: `${Math.min(100, progress)}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 dark:text-slate-500 text-center">
                {t('pythonSetup.firstTimeWait')}
              </p>
            </div>
          )}

          {/* Ready state */}
          {status === 'ready' && (
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center gap-3 text-emerald-600">
                <CheckCircle2 className="w-6 h-6" />
                <span className="font-medium">{message}</span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('pythonSetup.continuing')}</p>
            </div>
          )}

          {/* Need Install - Show content */}
          {status === 'need-install' && (
            <div className="text-center">
              <p className="text-sm text-slate-600 dark:text-slate-400">{t('pythonSetup.needsConfig')}</p>
            </div>
          )}

          {/* Error state */}
          {status === 'error' && error && (
            <div className="space-y-4">
              <div className="p-4 bg-red-50 rounded-xl border border-red-100">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-800">{t('pythonSetup.configError')}</p>
                    <p className="text-xs text-red-600 mt-1">{error}</p>
                  </div>
                </div>
              </div>
              
              <div className="text-center text-sm text-slate-500 dark:text-slate-400">
                <p className="mb-2">{t('pythonSetup.pythonRequired')}</p>
                <a 
                  href="https://www.python.org/downloads/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  {t('pythonSetup.downloadPython')}
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Buttons - only show for need-install and error states */}
        {(status === 'need-install' || (status === 'error' && error)) && (
          <div className="flex justify-between">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              {status === 'error' ? t('pythonSetup.back') : t('pythonSetup.goBack')}
            </Button>
            <Button onClick={status === 'error' ? handleRetry : handleInstallPython}>
              {status === 'error' ? (
                t('pythonSetup.retry')
              ) : (
                <>
                  <Cpu className="w-4 h-4 mr-2" />
                  {t('pythonSetup.installPython')}
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

// Detection status indicator component
function DetectionStatusBadge({ 
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
      className: 'bg-emerald-100 text-emerald-700',
      icon: <Check className="w-3 h-3" />
    },
    'fallback': { 
      label: t('detection.estimated'), 
      className: 'bg-amber-100 text-amber-700',
      icon: <AlertCircle className="w-3 h-3" />
    },
    'manual': { 
      label: t('detection.manual'), 
      className: 'bg-blue-100 text-blue-700',
      icon: <Circle className="w-3 h-3" />
    },
    'failed': { 
      label: t('detection.notDetected'), 
      className: 'bg-red-100 text-red-700',
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

// Hardware Selection Step - Enhanced with auto-detection
function HardwareSelectStep({
  config,
  onSelect,
  onBack,
}: {
  config: HardwareConfig;
  onSelect: (config: HardwareConfig) => void;
  onBack: () => void;
}) {
  const [isLoading, setIsLoading] = useState(true);
  const [detectionError, setDetectionError] = useState<string | null>(null);
  const { t } = useTranslation('setup');
  
  // Hardware values
  const [cpu, setCpu] = useState<'low' | 'mid' | 'high'>(config.cpu);
  const [cpuName, setCpuName] = useState<string>('');
  const [cpuStatus, setCpuStatus] = useState<'auto-detected' | 'fallback' | 'manual' | 'failed'>('auto-detected');
  const [cpuSource, setCpuSource] = useState<string>('');
  
  const [ram, setRam] = useState(config.ram);
  const [ramStatus, setRamStatus] = useState<'auto-detected' | 'fallback' | 'manual' | 'failed'>('auto-detected');
  const [ramSource, setRamSource] = useState<string>('');
  
  const [gpu, setGpu] = useState<'none' | 'integrated' | 'dedicated'>(config.gpu);
  const [gpuName, setGpuName] = useState<string>('');
  const [gpuStatus, setGpuStatus] = useState<'auto-detected' | 'fallback' | 'manual' | 'failed'>('auto-detected');
  const [gpuSource, setGpuSource] = useState<string>('');
  
  const [vram, setVram] = useState(config.vram || 0);
  const [hasCuda, setHasCuda] = useState(false);
  
  // Recommendation from backend
  const [recommendation, setRecommendation] = useState<{
    canRunLocalLLM: boolean;
    recommendedProvider: 'ollama' | 'openai';
    recommendedModel?: string;
    reasoning: string;
    warnings: string[];
  } | null>(null);
  
  // Manual override mode
  const [manualMode, setManualMode] = useState(false);

  // Auto-detect hardware on mount
  useEffect(() => {
    detectHardware();
  }, []);

  const detectHardware = async () => {
    setIsLoading(true);
    setDetectionError(null);
    
    try {
      const result = await window.electronAPI.setup.detectHardware();
      
      // CPU
      setCpu(result.cpu.tier);
      setCpuName(result.cpu.name);
      setCpuStatus(result.cpu.detectionStatus);
      setCpuSource(result.cpu.detectionSource);
      
      // RAM
      setRam(result.ram.totalGB);
      setRamStatus(result.ram.detectionStatus);
      setRamSource(result.ram.detectionSource);
      
      // GPU
      setGpu(result.gpu.type);
      setGpuName(result.gpu.name || '');
      setGpuStatus(result.gpu.detectionStatus);
      setGpuSource(result.gpu.detectionSource);
      setVram(result.gpu.vramGB || 0);
      setHasCuda(result.gpu.cudaAvailable);
      
      // Recommendation
      setRecommendation(result.recommendation);
      
      // If any detection failed, show manual mode hint
      if (result.cpu.detectionStatus === 'failed' || 
          result.gpu.detectionStatus === 'failed') {
        setManualMode(true);
      }
    } catch (error) {
      console.error('Hardware detection failed:', error);
      setDetectionError(error instanceof Error ? error.message : 'Error detecting hardware');
      setManualMode(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinue = async () => {
    // Save any manual overrides
    if (manualMode) {
      await window.electronAPI.setup.saveHardwareOverrides({
        cpuTier: cpu,
        ramGB: ram,
        gpuType: gpu,
        vramGB: gpu === 'dedicated' ? vram : undefined,
      });
    }
    
    onSelect({
      cpu,
      ram,
      gpu,
      vram: gpu === 'dedicated' ? vram : undefined,
    });
  };

  const handleManualChange = (field: 'cpu' | 'ram' | 'gpu' | 'vram', value: unknown) => {
    setManualMode(true);
    
    switch (field) {
      case 'cpu':
        setCpu(value as 'low' | 'mid' | 'high');
        setCpuStatus('manual');
        break;
      case 'ram':
        setRam(value as number);
        setRamStatus('manual');
        break;
      case 'gpu':
        setGpu(value as 'none' | 'integrated' | 'dedicated');
        setGpuStatus('manual');
        break;
      case 'vram':
        setVram(value as number);
        break;
    }
    
    // Recalculate recommendation locally
    updateLocalRecommendation();
  };
  
  const updateLocalRecommendation = () => {
    const ramGB = ram;
    const hasGPU = gpu === 'dedicated';
    const vramGB = vram || 0;
    
    let canRunLocalLLM = false;
    let recommendedProvider: 'ollama' | 'openai' = 'openai';
    let recommendedModel: string | undefined;
    let reasoning: string;
    const warnings: string[] = [];

    if (ramGB >= 32 && hasGPU && vramGB >= 8) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.1:8b';
      reasoning = t('hardwareSelect.recommendations.excellentGpu');
    } else if (ramGB >= 16 && hasGPU && vramGB >= 6) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:3b';
      reasoning = t('hardwareSelect.recommendations.goodGpu');
    } else if (ramGB >= 16) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:3b';
      reasoning = t('hardwareSelect.recommendations.goodRamNoGpu');
      if (!hasGPU) {
        warnings.push(t('hardwareSelect.recommendations.noGpuWarning'));
      }
    } else if (ramGB >= 12) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:1b';
      reasoning = t('hardwareSelect.recommendations.limitedHardware');
      warnings.push(t('hardwareSelect.recommendations.limitedRam'));
    } else if (ramGB >= 8) {
      canRunLocalLLM = false;
      recommendedProvider = 'openai';
      reasoning = t('hardwareSelect.recommendations.lowRam');
      warnings.push(t('hardwareSelect.recommendations.ram8gb'));
    } else {
      canRunLocalLLM = false;
      recommendedProvider = 'openai';
      reasoning = t('hardwareSelect.recommendations.insufficient');
      warnings.push(t('hardwareSelect.recommendations.veryLowRam'));
    }

    if (cpu === 'low') {
      warnings.push(t('hardwareSelect.recommendations.lowCpu'));
    }

    setRecommendation({ canRunLocalLLM, recommendedProvider, recommendedModel, reasoning, warnings });
  };

  // Loading state
  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        key="hardware-loading"
        className="text-center py-8"
      >
        <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
        </div>
        <h2 className="text-lg font-semibold mb-2 text-slate-900 dark:text-white">{t('hardwareSelect.title')}</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">{t('hardwareSelect.detecting')}</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="hardware-select"
    >
      <div className="text-center mb-4">
        <h2 className="text-lg sm:text-xl font-semibold mb-1 text-slate-900 dark:text-white">
          {t('hardwareSelect.detected')}
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          {t('hardwareSelect.verifyInfo')}
        </p>
        {detectionError && (
          <div className="mt-2 p-2 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-700">
              ⚠️ {t('hardwareSelect.partialDetection')}
            </p>
          </div>
        )}
      </div>

      <div className="space-y-4 max-w-lg mx-auto">
        {/* CPU Section */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('hardwareSelect.cpu')}</span>
            </div>
            <DetectionStatusBadge status={cpuStatus} source={cpuSource} />
          </div>
          
          {cpuName && cpuStatus !== 'manual' && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 truncate" title={cpuName}>
              {cpuName}
            </p>
          )}
          
          <div className="grid grid-cols-3 gap-2">
            {(['low', 'mid', 'high'] as const).map((level) => (
              <button
                key={level}
                onClick={() => handleManualChange('cpu', level)}
                className={cn(
                  'px-3 py-2 rounded-lg border-2 text-sm font-medium transition-all',
                  cpu === level
                    ? 'border-slate-900 bg-slate-900 text-white dark:border-white dark:bg-white dark:text-slate-900'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700 dark:border-slate-600 dark:bg-slate-700 dark:hover:border-slate-500 dark:text-slate-300'
                )}
              >
                {level === 'low' && t('hardwareSelect.cpuBasic')}
                {level === 'mid' && t('hardwareSelect.cpuMid')}
                {level === 'high' && t('hardwareSelect.cpuPowerful')}
              </button>
            ))}
          </div>
        </div>

        {/* RAM Section */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('hardwareSelect.ram')}</span>
            </div>
            <DetectionStatusBadge status={ramStatus} source={ramSource} />
          </div>
          
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">{ram}</span>
            <span className="text-sm text-slate-500 dark:text-slate-400">GB</span>
            {ram < 16 && (
              <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full">
                {t('hardwareSelect.ramLimited')}
              </span>
            )}
            {ram >= 16 && ram < 32 && (
              <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                {t('hardwareSelect.ramAdequate')}
              </span>
            )}
            {ram >= 32 && (
              <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full">
                {t('hardwareSelect.ramExcellent')}
              </span>
            )}
          </div>
          
          <input
            type="range"
            min="4"
            max="128"
            step="4"
            value={ram}
            onChange={(e) => handleManualChange('ram', parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-slate-900"
          />
          <div className="flex justify-between text-xs text-slate-400 dark:text-slate-500 mt-1">
            <span>4 GB</span>
            <span>128 GB</span>
          </div>
        </div>

        {/* GPU Section */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Monitor className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('hardwareSelect.gpu')}</span>
            </div>
            <DetectionStatusBadge status={gpuStatus} source={gpuSource} />
          </div>
          
          {gpuName && gpuStatus !== 'manual' && (
            <div className="flex items-center gap-2 mb-2">
              <p className="text-xs text-slate-500 dark:text-slate-400 truncate flex-1" title={gpuName}>
                {gpuName}
              </p>
              {hasCuda && (
                <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full shrink-0">
                  CUDA ✓
                </span>
              )}
            </div>
          )}
          
          <div className="grid grid-cols-3 gap-2">
            {(['none', 'integrated', 'dedicated'] as const).map((type) => (
              <button
                key={type}
                onClick={() => handleManualChange('gpu', type)}
                className={cn(
                  'px-3 py-2 rounded-lg border-2 text-xs sm:text-sm font-medium transition-all',
                  gpu === type
                    ? 'border-slate-900 bg-slate-900 text-white dark:border-white dark:bg-white dark:text-slate-900'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700 dark:border-slate-600 dark:bg-slate-700 dark:hover:border-slate-500 dark:text-slate-300'
                )}
              >
                {type === 'none' && t('hardwareSelect.gpuNone')}
                {type === 'integrated' && t('hardwareSelect.gpuIntegrated')}
                {type === 'dedicated' && t('hardwareSelect.gpuDedicated')}
              </button>
            ))}
          </div>
          
          {/* VRAM for dedicated GPU */}
          {gpu === 'dedicated' && (
            <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-600 dark:text-slate-400">VRAM:</span>
                <span className="font-medium text-slate-900 dark:text-white">{vram} GB</span>
              </div>
              <input
                type="range"
                min="2"
                max="24"
                step="2"
                value={vram}
                onChange={(e) => handleManualChange('vram', parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-slate-900"
              />
              <div className="flex justify-between text-xs text-slate-400 dark:text-slate-500 mt-1">
                <span>2 GB</span>
                <span>24 GB</span>
              </div>
            </div>
          )}
        </div>

        {/* Recommendation Box */}
        {recommendation && (
          <div className={cn(
            'p-4 rounded-xl border-2',
            recommendation.recommendedProvider === 'openai' 
              ? 'bg-amber-50 border-amber-200'
              : recommendation.warnings.length === 0
                ? 'bg-emerald-50 border-emerald-200'
                : 'bg-blue-50 border-blue-200'
          )}>
            <div className="flex items-start gap-3">
              <div className={cn(
                'shrink-0',
                recommendation.recommendedProvider === 'openai'
                  ? 'text-amber-600'
                  : recommendation.warnings.length === 0
                    ? 'text-emerald-600'
                    : 'text-blue-600'
              )}>
                {recommendation.recommendedProvider === 'openai' ? (
                  <Cloud className="w-5 h-5" />
                ) : recommendation.warnings.length === 0 ? (
                  <Zap className="w-5 h-5" />
                ) : (
                  <Monitor className="w-5 h-5" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">
                    {t('hardwareSelect.recommendations.recommendLabel')} {recommendation.recommendedProvider === 'openai' ? t('hardwareSelect.recommendations.recommendApi') : t('hardwareSelect.recommendations.recommendLocal')}
                  </span>
                  {recommendation.recommendedModel && (
                    <span className="text-xs px-2 py-0.5 bg-white/50 dark:bg-slate-800/50 rounded-full text-slate-600 dark:text-slate-400">
                      {recommendation.recommendedModel}
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                  {recommendation.reasoning}
                </p>
                {recommendation.warnings.length > 0 && (
                  <ul className="space-y-1">
                    {recommendation.warnings.map((warning, i) => (
                      <li key={i} className="text-xs text-amber-700 flex items-start gap-1.5">
                        <AlertCircle className="w-3 h-3 mt-0.5 shrink-0" />
                        {warning}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Manual mode indicator */}
        {manualMode && (
          <div className="flex items-center justify-center gap-2 text-xs text-slate-500 dark:text-slate-400">
            <Circle className="w-3 h-3" />
            <span>{t('hardwareSelect.manualValues')}</span>
            <button 
              onClick={detectHardware}
              className="text-blue-600 hover:underline"
            >
              {t('hardwareSelect.redetect')}
            </button>
          </div>
        )}
      </div>

      <div className="flex justify-between mt-6">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button onClick={handleContinue}>
          {t('hardwareSelect.continue')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

function LLMChoiceStep({ 
  onSelect,
  hardwareConfig,
  onBack,
}: { 
  onSelect: (choice: 'ollama' | 'openai') => void;
  hardwareConfig: HardwareConfig;
  onBack: () => void;
}) {
  // Updated RAM requirements: 16GB for good local LLM experience
  const hasGoodRAM = hardwareConfig.ram >= 16;
  const hasMarginalRAM = hardwareConfig.ram >= 12 && hardwareConfig.ram < 16;
  const hasLowRAM = hardwareConfig.ram < 12;
  const hasGPU = hardwareConfig.gpu === 'dedicated';
  const vram = hardwareConfig.vram || 0;
  const { t } = useTranslation('setup');
  
  // Determine recommendation
  const recommendLocal = hasGoodRAM || (hasMarginalRAM && hasGPU && vram >= 6);
  const localWarning = hasLowRAM 
    ? t('llmChoice.localLowRam')
    : hasMarginalRAM && !hasGPU 
      ? t('llmChoice.localNoGpu')
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="llm-choice"
    >
      <div className="text-center mb-6 sm:mb-8">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('llmChoice.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('llmChoice.subtitle')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        {/* Ollama Option */}
        <button
          onClick={() => onSelect('ollama')}
          className={cn(
            "p-6 border-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-all text-left group relative cursor-pointer",
            recommendLocal 
              ? "border-emerald-300 bg-emerald-50/30" 
              : "border-slate-200 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-500",
            hasLowRAM && "opacity-70"
          )}
        >
          {recommendLocal && (
            <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 bg-emerald-500 text-white rounded-full font-medium">
              {t('llmChoice.recommended')}
            </span>
          )}
          <Monitor className="w-7 h-7 text-slate-700 dark:text-slate-300 mb-3" />
          <h3 className="font-semibold text-lg text-slate-900 dark:text-white mb-1">{t('llmChoice.local')}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">{t('llmChoice.localDesc')}</p>
          <ul className="space-y-1.5 text-sm text-slate-600 dark:text-slate-300">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.localFreePrivate')}
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.localNoInternet')}
            </li>
            <li className={cn("flex items-center gap-2", !hasGoodRAM && "text-amber-600")}>
              {hasGoodRAM ? (
                <Check className="w-4 h-4 text-emerald-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-amber-500" />
              )}
              {t('llmChoice.localRequiresRam')}
            </li>
            {hasGPU && (
              <li className="flex items-center gap-2 text-emerald-600">
                <Zap className="w-4 h-4" />
                {t('llmChoice.localGpuDetected', { vram })}
              </li>
            )}
          </ul>
          {localWarning && (
            <div className="mt-3 p-2 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-xs text-amber-700 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {localWarning}
              </p>
            </div>
          )}
          <div className="mt-4 flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white">
            {t('llmChoice.select')}
            <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>

        {/* OpenAI Option */}
        <button
          onClick={() => onSelect('openai')}
          className={cn(
            "p-6 border-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-all text-left group relative cursor-pointer",
            !recommendLocal 
              ? "border-emerald-300 bg-emerald-50/30" 
              : "border-slate-200 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-500"
          )}
        >
          {!recommendLocal && (
            <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 bg-emerald-500 text-white rounded-full font-medium">
              {t('llmChoice.recommended')}
            </span>
          )}
          <Cloud className="w-7 h-7 text-slate-700 dark:text-slate-300 mb-3" />
          <h3 className="font-semibold text-lg text-slate-900 dark:text-white mb-1">{t('llmChoice.apiOpenai')}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">{t('llmChoice.apiCloudDesc')}</p>
          <ul className="space-y-1.5 text-sm text-slate-600 dark:text-slate-300">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.apiFastSetup')}
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              {t('llmChoice.apiNoHardware')}
            </li>
            <li className="flex items-center gap-2">
              <Circle className="w-4 h-4 text-slate-300 dark:text-slate-600" />
              {t('llmChoice.apiPayPerUse')}
            </li>
          </ul>
          <div className="mt-4 flex items-center text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white">
            {t('llmChoice.select')}
            <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>
      </div>

      <div className="flex justify-start">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
      </div>
    </motion.div>
  );
}

// New: Ollama Model Selection Step
function OllamaModelSelectStep({
  selectedModel,
  onSelectModel,
  customModel,
  onCustomModelChange,
  useCustom,
  onUseCustomChange,
  hardwareConfig,
  onNext,
  onBack,
}: {
  selectedModel: string;
  onSelectModel: (model: string) => void;
  customModel: string;
  onCustomModelChange: (model: string) => void;
  useCustom: boolean;
  onUseCustomChange: (use: boolean) => void;
  hardwareConfig: HardwareConfig;
  onNext: () => void;
  onBack: () => void;
}) {
  const totalRam = hardwareConfig.ram;
  const hasGPU = hardwareConfig.gpu === 'dedicated';
  const vram = hardwareConfig.vram || 0;
  const { t } = useTranslation('setup');

  // Find recommended model based on hardware
  const getRecommendedModel = () => {
    // High-end hardware: 32GB+ RAM or 12GB+ VRAM
    if (totalRam >= 32 || (hasGPU && vram >= 12)) {
      return 'deepseek-r1:14b'; // Most powerful for excellent hardware
    }
    
    // Good hardware: 24GB+ RAM or 10GB+ VRAM
    if (totalRam >= 24 || (hasGPU && vram >= 10)) {
      return 'deepseek-r1:8b'; // Strong reasoning for good hardware
    }
    
    // Decent hardware: 16GB+ RAM or 8GB+ VRAM
    if (totalRam >= 16 || (hasGPU && vram >= 8)) {
      return 'llama3.1:8b'; // Balanced option (default recommendation)
    }
    
    // Basic hardware: 12GB+ RAM or 6GB+ VRAM
    if (totalRam >= 12 || (hasGPU && vram >= 6)) {
      return 'mistral:7b'; // Fast and efficient
    }
    
    // Fallback for low-end hardware
    return 'mistral:7b';
  };

  const recommendedModel = getRecommendedModel();

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="ollama-model-select"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('ollamaModelSelect.title')}
        </h2>
        <p className="text-slate-500 dark:text-slate-400">
          {t('ollamaModelSelect.subtitle', { ram: totalRam })}
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {OLLAMA_MODELS.map((model) => {
          const isRecommended = model.id === recommendedModel;
          const canRun = totalRam >= model.minRam;
          
          return (
            <button
              key={model.id}
              onClick={() => {
                onUseCustomChange(false);
                onSelectModel(model.id);
              }}
              disabled={!canRun}
              className={cn(
                "w-full p-4 border-2 rounded-xl text-left transition-all flex items-start gap-4",
                !useCustom && selectedModel === model.id
                  ? "border-slate-900 bg-slate-50 dark:border-white dark:bg-slate-800"
                  : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600",
                !canRun ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
              )}
            >
              <div className={cn(
                "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
                !useCustom && selectedModel === model.id
                  ? "border-slate-900 bg-slate-900 dark:border-white dark:bg-white"
                  : "border-slate-300 dark:border-slate-600"
              )}>
                {!useCustom && selectedModel === model.id && (
                  <Check className="w-3 h-3 text-white" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-slate-900 dark:text-white">{model.name}</span>
                  <span className="text-xs text-slate-400 dark:text-slate-500">{model.size}</span>
                  {isRecommended && (
                    <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full font-medium">
                      {t('ollamaModelSelect.recommended')}
                    </span>
                  )}
                  {!canRun && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">
                      {t('ollamaModelSelect.requiresRam', { ram: model.minRam })}
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">{t(`ollamaModelDescriptions.${modelKey(model.id)}`)}</p>
                <div className="flex items-center gap-2 mt-2">
                  {model.performance === 'fast' && (
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <Zap className="w-3 h-3" /> {t('ollamaModelSelect.fast')}
                    </span>
                  )}
                  {model.performance === 'balanced' && (
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <HardDrive className="w-3 h-3" /> {t('ollamaModelSelect.balanced')}
                    </span>
                  )}
                  {model.performance === 'powerful' && (
                    <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                      <Cpu className="w-3 h-3" /> {t('ollamaModelSelect.powerful')}
                    </span>
                  )}
                </div>
              </div>
            </button>
          );
        })}

        {/* Custom model option */}
        <div className={cn(
          "p-4 border-2 rounded-xl transition-all",
          useCustom ? "border-slate-900 bg-slate-50 dark:border-white dark:bg-slate-800" : "border-slate-200 dark:border-slate-700"
        )}>
          <button
            onClick={() => onUseCustomChange(true)}
            className="w-full flex items-start gap-4 text-left cursor-pointer"
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              useCustom ? "border-slate-900 bg-slate-900 dark:border-white dark:bg-white" : "border-slate-300 dark:border-slate-600"
            )}>
              {useCustom && <Check className="w-3 h-3 text-white dark:text-slate-900" />}
            </div>
            <div className="flex-1">
              <span className="font-medium text-slate-900 dark:text-white">{t('ollamaModelSelect.customModel')}</span>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('ollamaModelSelect.customHint')}</p>
            </div>
          </button>
          {useCustom && (
            <div className="mt-3 pl-9">
              <Input
                placeholder={t('ollamaModelSelect.customPlaceholder')}
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                className="w-full"
              />
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                {t('ollamaModelSelect.libraryHint')}{' '}
                <a href="https://ollama.com/library" target="_blank" rel="noopener noreferrer" className="text-slate-600 dark:text-slate-400 underline">
                  ollama.com/library
                </a>
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button 
          onClick={onNext} 
          disabled={useCustom && !customModel.trim()}
        >
          {t('nav.next')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

// New: OpenAI Model Selection Step
function OpenAIModelSelectStep({
  selectedModel,
  onSelectModel,
  customModel,
  onCustomModelChange,
  useCustom,
  onUseCustomChange,
  onNext,
  onBack,
}: {
  selectedModel: string;
  onSelectModel: (model: string) => void;
  customModel: string;
  onCustomModelChange: (model: string) => void;
  useCustom: boolean;
  onUseCustomChange: (use: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="openai-model-select"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('openaiModelSelect.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('openaiModelSelect.subtitle')}
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {OPENAI_MODELS.map((model) => (
          <button
            key={model.id}
            onClick={() => {
              onUseCustomChange(false);
              onSelectModel(model.id);
            }}
            className={cn(
              "w-full p-4 border-2 rounded-xl text-left transition-all flex items-start gap-4 cursor-pointer",
              !useCustom && selectedModel === model.id
                ? "border-slate-900 bg-slate-50 dark:border-white dark:bg-slate-800"
                : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600"
            )}
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              !useCustom && selectedModel === model.id
                ? "border-slate-900 bg-slate-900 dark:border-white dark:bg-white"
                : "border-slate-300 dark:border-slate-600"
            )}>
              {!useCustom && selectedModel === model.id && (
                <Check className="w-3 h-3 text-white" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-slate-900 dark:text-white">{model.name}</span>
                {model.recommended && (
                  <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full font-medium">
                    {t('ollamaModelSelect.recommended')}
                  </span>
                )}
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full font-medium",
                  model.costTier === 'low' && "bg-green-100 text-green-700",
                  model.costTier === 'medium' && "bg-yellow-100 text-yellow-700",
                  model.costTier === 'high' && "bg-red-100 text-red-700"
                )}>
                  {model.costTier === 'low' && t('openaiModelSelect.economical')}
                  {model.costTier === 'medium' && t('openaiModelSelect.moderate')}
                  {model.costTier === 'high' && t('openaiModelSelect.premium')}
                </span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t(`openaiModelDescriptions.${modelKey(model.id)}`)}</p>
            </div>
          </button>
        ))}

        {/* Custom model option */}
        <div className={cn(
          "p-4 border-2 rounded-xl transition-all",
          useCustom ? "border-slate-900 bg-slate-50" : "border-slate-200"
        )}>
          <button
            onClick={() => onUseCustomChange(true)}
            className="w-full flex items-start gap-4 text-left cursor-pointer"
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              useCustom ? "border-slate-900 bg-slate-900 dark:border-white dark:bg-white" : "border-slate-300 dark:border-slate-600"
            )}>
              {useCustom && <Check className="w-3 h-3 text-white dark:text-slate-900" />}
            </div>
            <div className="flex-1">
              <span className="font-medium text-slate-900 dark:text-white">{t('openaiModelSelect.customModel')}</span>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('openaiModelSelect.customHint')}</p>
            </div>
          </button>
          {useCustom && (
            <div className="mt-3 pl-9">
              <Input
                placeholder={t('openaiModelSelect.customPlaceholder')}
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                className="w-full"
              />
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button 
          onClick={onNext} 
          disabled={useCustom && !customModel.trim()}
        >
          {t('nav.next')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

function OllamaSetupStep({
  progress,
  onStart,
  modelName,
  onBack,
}: {
  progress: OllamaDownloadProgress;
  onStart: () => void;
  modelName: string;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  const [started, setStarted] = useState(false);

  const handleStart = () => {
    setStarted(true);
    onStart();
  };

  const isComplete = progress.stage === 'complete';
  const isError = progress.stage === 'error';
  const isIdle = progress.stage === 'idle' || (!started);

  // Helper function to strip percentage from message
  const stripPercentage = (message: string): string => {
    return message.replace(/\s*\d+(\.\d+)?%\s*$/, '').trim();
  };

  // Parse progress message to get clean status
  const getCleanStatus = () => {
    if (progress.stage === 'downloading') return stripPercentage(progress.message || t('ollamaSetup.downloadingOllama'));
    if (progress.stage === 'installing') return stripPercentage(progress.message || t('ollamaSetup.installingOllama'));
    if (progress.stage === 'starting') return stripPercentage(progress.message || t('ollamaSetup.startingOllama'));
    if (progress.stage === 'pulling-model') return stripPercentage(progress.message || t('ollamaSetup.downloadingModel', { model: modelName }));
    if (progress.stage === 'complete') return t('ollamaSetup.completed');
    if (progress.stage === 'error') return 'Error';
    return stripPercentage(progress.message || t('ollamaSetup.preparing'));
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="ollama-setup"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('ollamaSetup.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('ollamaSetup.selectedModel')} <span className="font-medium text-slate-700 dark:text-slate-300">{modelName}</span>
        </p>
      </div>

      {isIdle ? (
        <div className="space-y-6">
          <div className="text-center py-4 sm:py-6">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
              <Download className="w-7 h-7 sm:w-8 sm:h-8 text-slate-600 dark:text-slate-400" />
            </div>
            <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 mb-4 sm:mb-6 max-w-sm mx-auto px-4">
              {t('ollamaSetup.description')}
            </p>
            {/* Unified installation info */}
            <div className="flex items-center justify-center gap-4 text-xs text-slate-400 dark:text-slate-500">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-blue-400" />
                <span>Software</span>
              </div>
              <ChevronRight className="w-4 h-4" />
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-green-400" />
                <span>{t('ollamaSetup.model')}</span>
              </div>
            </div>
          </div>
          <div className="flex justify-between">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              {t('nav.back')}
            </Button>
            <Button onClick={handleStart}>
              <Download className="w-4 h-4 mr-2" />
              {t('ollamaSetup.startInstall')}
            </Button>
          </div>
        </div>
      ) : (
        <div className="py-6">
          <div className="text-center mb-6">
            {isComplete ? (
              <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8 text-emerald-600" />
              </div>
            ) : isError ? (
              <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
                <X className="w-8 h-8 text-red-600" />
              </div>
            ) : (
              <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center mx-auto">
                <Loader2 className="w-8 h-8 text-slate-600 dark:text-slate-400 animate-spin" />
              </div>
            )}
          </div>
          
          <div className="max-w-md mx-auto">
            {isComplete ? (
              <div className="text-center space-y-3">
                <h3 className="text-lg font-semibold text-emerald-600">
                  {getCleanStatus()}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {t('ollamaSetup.successMessage')}
                </p>
              </div>
            ) : (
              <>
                {/* Phase indicator for unified installation */}
                {progress.currentPhase && (
                  <div className="flex items-center justify-center gap-4 mb-4">
                    <div className={cn(
                      'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all',
                      progress.currentPhase === 'software' 
                        ? 'bg-blue-100 text-blue-700 scale-105' 
                        : 'bg-slate-100 text-slate-400 dark:bg-slate-700 dark:text-slate-500'
                    )}>
                      <div className={cn(
                        'w-2 h-2 rounded-full',
                        progress.currentPhase === 'software' ? 'bg-blue-500' : 'bg-green-500'
                      )} />
                      {t('ollamaSetup.software')}
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-300 dark:text-slate-600" />
                    <div className={cn(
                      'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all',
                      progress.currentPhase === 'model' 
                        ? 'bg-green-100 text-green-700 scale-105' 
                        : 'bg-slate-100 text-slate-400 dark:bg-slate-700 dark:text-slate-500'
                    )}>
                      <div className={cn(
                        'w-2 h-2 rounded-full',
                        progress.currentPhase === 'model' ? 'bg-green-500' : 'bg-slate-300 dark:bg-slate-600'
                      )} />
                      {t('ollamaSetup.model')}
                    </div>
                  </div>
                )}
                
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{getCleanStatus()}</span>
                  <span className="text-sm font-bold text-blue-600">
                    {Math.round(progress.unifiedProgress ?? progress.progress)}%
                  </span>
                </div>
                
                {!isError && (
                  <div className="relative h-6 bg-slate-200 rounded-full overflow-hidden">
                    {/* Unified progress bar with phase colors */}
                    <div
                      className={cn(
                        "absolute inset-y-0 left-0 rounded-full shadow-sm transition-all duration-300 ease-out",
                        progress.currentPhase === 'model'
                          ? "bg-gradient-to-r from-blue-400 via-green-400 to-green-500"
                          : "bg-gradient-to-r from-blue-400 to-blue-500"
                      )}
                      style={{ width: `${Math.min(100, progress.unifiedProgress ?? progress.progress)}%` }}
                    />
                    {/* Phase separator at 50% */}
                    {progress.currentPhase && (
                      <div className="absolute inset-y-0 left-1/2 w-0.5 bg-white/50 dark:bg-slate-600/50" />
                    )}
                  </div>
                )}
              </>
            )}
            
            {progress.error && (
              <p className="mt-3 text-sm text-red-500 text-center">{progress.error}</p>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}

function OpenAISetupStep({
  apiKey,
  onKeyChange,
  error,
  isValidating,
  onSubmit,
  modelName,
  onBack,
}: {
  apiKey: string;
  onKeyChange: (key: string) => void;
  error: string;
  isValidating: boolean;
  onSubmit: () => void;
  modelName: string;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="openai-setup"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('openaiSetup.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('ollamaSetup.selectedModel')} <span className="font-medium text-slate-700 dark:text-slate-300">{modelName}</span>
        </p>
      </div>

      <div className="space-y-4 max-w-md mx-auto">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            API Key
          </label>
          <Input
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(e) => onKeyChange(e.target.value)}
            className={error ? 'border-red-300 focus:border-red-500' : ''}
          />
          {error && <p className="text-red-500 text-sm mt-1.5">{error}</p>}
        </div>

        <p className="text-sm text-slate-400 dark:text-slate-500">
          {t('openaiSetup.apiKeyHint')}{' '}
          <a
            href="https://platform.openai.com/api-keys"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-600 dark:text-slate-400 underline hover:text-slate-800 dark:hover:text-slate-200"
          >
            platform.openai.com
          </a>
        </p>
      </div>

      <div className="flex justify-between mt-6">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button
          onClick={onSubmit}
          disabled={!apiKey || isValidating}
        >
          {isValidating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              {t('openaiSetup.validating')}
            </>
          ) : (
            <>
              {t('nav.next')}
              <ArrowRight className="w-4 h-4 ml-2" />
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );
}

function ModelDownloadStep({
  progress,
  onStart,
  isLoading,
  onBack,
  onNext,
  error,
}: {
  progress: Record<string, number>;
  onStart: () => void;
  isLoading: boolean;
  onBack: () => void;
  onNext: () => void;
  error?: string | null;
}) {
  const { t } = useTranslation('setup');
  const [started, setStarted] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [animatedProgress, setAnimatedProgress] = useState<Record<string, number>>({});
  const [alreadyDownloaded, setAlreadyDownloaded] = useState(false);
  const [checkingModels, setCheckingModels] = useState(true);

  const modelKeys = ['sentiment', 'embeddings', 'subjectivity', 'categories'];

  useEffect(() => {
    window.electronAPI.setup.getRequiredModels().then(setModels);

    // Check if models are already downloaded on mount
    window.electronAPI.setup.checkModels().then((status) => {
      const allAlreadyDownloaded = status.sentiment && status.embeddings && status.subjectivity && status.categories;
      if (allAlreadyDownloaded) {
        setAlreadyDownloaded(true);
        setStarted(true);
      }
      setCheckingModels(false);
    }).catch(() => {
      setCheckingModels(false);
    });
  }, []);

  const handleStart = () => {
    setStarted(true);
    onStart();
  };

  const allComplete = alreadyDownloaded || modelKeys.every((key) => progress[key] === 100);
  const totalProgress = alreadyDownloaded ? 100 : modelKeys.reduce((acc, key) => acc + (progress[key] || 0), 0) / modelKeys.length;
  useEffect(() => {
    modelKeys.forEach((key) => {
      const target = progress[key] || 0;
      const current = animatedProgress[key] || 0;
      
      if (target > current) {
        const timer = setInterval(() => {
          setAnimatedProgress(prev => {
            const newVal = Math.min((prev[key] || 0) + 2, target);
            if (newVal >= target) {
              clearInterval(timer);
            }
            return { ...prev, [key]: newVal };
          });
        }, 20);
        return () => clearInterval(timer);
      }
    });
  }, [progress]);

  const displayModels = [
    { key: 'sentiment', name: t('modelDownload.sentimentModel') },
    { key: 'embeddings', name: t('modelDownload.embeddingsModel') },
    { key: 'subjectivity', name: t('modelDownload.subjectivityModel') },
    { key: 'categories', name: t('modelDownload.categoryModel') },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="models"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('modelDownload.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('modelDownload.description')}
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {displayModels.map((model) => {
          const modelProgress = alreadyDownloaded ? 100 : (animatedProgress[model.key] || progress[model.key] || 0);
          const isComplete = modelProgress === 100;
          const isDownloading = started && modelProgress > 0 && modelProgress < 100;
          const progressPercent = Math.round(modelProgress);
          
          return (
            <div key={model.key} className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{model.name}</span>
                    <span className="text-sm font-bold text-emerald-600">{progressPercent}%</span>
                  </div>
                  {(started || isComplete) && (
                    <div className="relative h-6 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full shadow-sm transition-all duration-300 ease-out"
                        style={{ width: `${Math.min(100, modelProgress)}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {checkingModels ? (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            {t('modelDownload.verifying')}
          </div>
        </div>
      ) : allComplete ? (
        <div className="flex justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('nav.back')}
          </Button>
          <Button onClick={onNext}>
            <CheckCircle2 className="w-4 h-4 mr-2" />
            {t('nav.next')}
          </Button>
        </div>
      ) : (!started || error) ? (
        <div className="flex justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('nav.back')}
          </Button>
          <Button onClick={handleStart} disabled={isLoading}>
            <Download className="w-4 h-4 mr-2" />
            {error ? t('modelDownload.retryDownload') : t('modelDownload.downloadModels')}
          </Button>
        </div>
      ) : (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            {t('modelDownload.totalProgress', { progress: Math.round(totalProgress) })}
          </div>
        </div>
      )}
    </motion.div>
  );
}

function OutputDirStep({
  outputDir,
  onSelectDir,
  onNext,
  onBack,
}: {
  outputDir: string;
  onSelectDir: () => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const { t } = useTranslation('setup');
  const [defaultDir, setDefaultDir] = useState<string>('');

  useEffect(() => {
    window.electronAPI.app.getPythonDataDir().then((dir: string) => {
      setDefaultDir(dir);
    }).catch(() => {});
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="output-dir"
    >
      <div className="text-center mb-4 sm:mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-slate-100 dark:bg-slate-700 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
          <Folder className="w-7 h-7 sm:w-8 sm:h-8 text-slate-700 dark:text-slate-300" />
        </div>
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('outputDir.title')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 px-4">
          {t('outputDir.description')}
        </p>
      </div>

      <div className="space-y-4 mb-6">
        <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            {t('outputDir.outputFolder')}
          </label>
          <div className="flex gap-2">
            <div className="flex-1 px-3 py-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-600 dark:text-slate-300 truncate min-h-[38px] flex items-center">
              {outputDir || t('outputDir.notSelected')}
            </div>
            <Button variant="outline" onClick={onSelectDir} className="flex-shrink-0">
              <Folder className="w-4 h-4 mr-2" />
              {t('outputDir.select')}
            </Button>
          </div>
          {!outputDir && defaultDir && (
            <div className="mt-2 p-2.5 bg-slate-100 dark:bg-slate-700 rounded-lg">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                <span className="font-medium text-slate-600 dark:text-slate-300">{t('outputDir.defaultFolder')}</span>
              </p>
              <p className="text-xs font-mono text-slate-600 dark:text-slate-400 break-all mt-0.5">{defaultDir}</p>
            </div>
          )}
          {!outputDir && !defaultDir && (
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">
              {t('outputDir.defaultHint')}
            </p>
          )}
        </div>

        {outputDir && (
          <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-emerald-700">{t('outputDir.selectedFolder')}</p>
                <p className="text-xs text-emerald-600 break-all mt-1">{outputDir}</p>
                <p className="text-xs text-emerald-500 mt-1">
                  {t('outputDir.savedIn')} <span className="font-mono">{outputDir}/data/</span>
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-blue-600">
              {t('outputDir.changeLater')}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500 dark:text-slate-400">
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('nav.back')}
        </Button>
        <Button onClick={onNext}>
          {outputDir ? t('nav.next') : t('outputDir.skipDefault')}
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </motion.div>
  );
}

function CompleteStep({ onFinish }: { onFinish: () => void }) {
  const { t } = useTranslation('setup');
  const [isFinishing, setIsFinishing] = useState(false);

  const handleFinish = async () => {
    setIsFinishing(true);
    await onFinish();
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center py-4 sm:py-6"
      key="complete"
    >
      <div className="w-14 h-14 sm:w-16 sm:h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
        <CheckCircle2 className="w-7 h-7 sm:w-8 sm:h-8 text-emerald-600" />
      </div>
      <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
        {t('complete.title')}
      </h2>
      <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 mb-6 sm:mb-8 max-w-sm mx-auto px-4">
        {t('complete.description')}
      </p>
      <Button 
        size="lg" 
        onClick={handleFinish} 
        disabled={isFinishing}
        className="px-6 sm:px-8"
      >
        {isFinishing ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            {t('complete.starting')}
          </>
        ) : (
          <>
            {t('complete.startAnalyzing')}
            <ArrowRight className="w-4 h-4 ml-2" />
          </>
        )}
      </Button>
    </motion.div>
  );
}

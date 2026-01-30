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
  X
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
interface OllamaModelOption {
  id: string;
  name: string;
  size: string;
  description: string;
  minRam: number; // Realistic minimum RAM in GB for good performance
  minVram?: number; // Minimum VRAM in GB for GPU acceleration (optional)
  recommended: boolean;
  performance: 'fast' | 'balanced' | 'powerful';
}

const OLLAMA_MODELS: OllamaModelOption[] = [
  {
    id: 'llama3.2:1b',
    name: 'Llama 3.2 1B',
    size: '~1.3 GB',
    description: 'Modelo ultra-ligero. Calidad limitada pero funciona en hardware básico.',
    minRam: 12, // 1B models need ~12GB RAM for acceptable inference
    minVram: 4,
    recommended: false,
    performance: 'fast',
  },
  {
    id: 'llama3.2:3b',
    name: 'Llama 3.2 3B',
    size: '~2.0 GB',
    description: 'Buen equilibrio calidad/velocidad. Recomendado para la mayoría.',
    minRam: 16, // 3B models need ~16GB RAM
    minVram: 6,
    recommended: true,
    performance: 'balanced',
  },
  {
    id: 'llama3.1:8b',
    name: 'Llama 3.1 8B',
    size: '~4.7 GB',
    description: 'Alta calidad de razonamiento. Requiere buen hardware.',
    minRam: 24, // 8B models need ~24GB RAM or good GPU
    minVram: 8,
    recommended: false,
    performance: 'powerful',
  },
  {
    id: 'mistral:7b',
    name: 'Mistral 7B',
    size: '~4.1 GB',
    description: 'Excelente para análisis de texto. Similar a 8B en requisitos.',
    minRam: 24,
    minVram: 8,
    recommended: false,
    performance: 'powerful',
  },
];

// OpenAI model options
interface OpenAIModelOption {
  id: string;
  name: string;
  description: string;
  costTier: 'low' | 'medium' | 'high';
  recommended: boolean;
}

const OPENAI_MODELS: OpenAIModelOption[] = [
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    description: 'Rápido y económico. Ideal para la mayoría de tareas.',
    costTier: 'low',
    recommended: true,
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    description: 'Máxima capacidad. Mejor para análisis complejos.',
    costTier: 'high',
    recommended: false,
  },
  {
    id: 'gpt-4-turbo',
    name: 'GPT-4 Turbo',
    description: 'Balance entre costo y capacidad.',
    costTier: 'medium',
    recommended: false,
  },
];

type SetupStep = 'welcome' | 'python-setup' | 'hardware-select' | 'llm-choice' | 'model-select' | 'llm-setup' | 'models' | 'complete';

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
const STEP_ORDER: SetupStep[] = ['welcome', 'python-setup', 'hardware-select', 'llm-choice', 'model-select', 'llm-setup', 'models', 'complete'];

function getStepIndex(step: SetupStep): number {
  return STEP_ORDER.indexOf(step);
}

export function SetupWizard({ onComplete }: SetupWizardProps) {
  const [currentStep, setCurrentStep] = useState<SetupStep>('welcome');
  const [llmChoice, setLlmChoice] = useState<'ollama' | 'openai' | null>(null);
  const [selectedOllamaModel, setSelectedOllamaModel] = useState<string>('llama3.2:3b');
  const [customOllamaModel, setCustomOllamaModel] = useState<string>('');
  const [useCustomOllamaModel, setUseCustomOllamaModel] = useState(false);
  const [selectedOpenAIModel, setSelectedOpenAIModel] = useState<string>('gpt-4o-mini');
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

  const handleOllamaSetup = useCallback(async () => {
    const modelToUse = useCustomOllamaModel ? customOllamaModel : selectedOllamaModel;
    setOllamaProgress({ stage: 'downloading', progress: 0, message: 'Verificando estado de Ollama...' });
    
    // Check if Ollama is already installed
    let status = await window.electronAPI.setup.checkOllama();
    
    if (status.installed && status.running) {
      // Check if model is available
      setOllamaProgress({ stage: 'downloading', progress: 5, message: `Ollama ya está instalado. Verificando modelo ${modelToUse}...` });
      const hasModel = await window.electronAPI.setup.hasOllamaModel(modelToUse);
      if (hasModel) {
        setOllamaProgress({ stage: 'complete', progress: 100, message: '¡Todo listo!' });
        setTimeout(() => setCurrentStep('models'), 500);
        return;
      }
      // Model not found, need to pull
      setOllamaProgress({ stage: 'pulling-model', progress: 0, message: `Descargando modelo ${modelToUse}...` });
      await window.electronAPI.setup.pullOllamaModel(modelToUse);
    } else if (status.installed) {
      // Start Ollama and pull model
      setOllamaProgress({ stage: 'starting', progress: 5, message: 'Iniciando servicio Ollama...' });
      await window.electronAPI.setup.startOllama();
      setOllamaProgress({ stage: 'pulling-model', progress: 0, message: `Descargando modelo ${modelToUse}...` });
      await window.electronAPI.setup.pullOllamaModel(modelToUse);
    } else {
      // Install Ollama first
      setOllamaProgress({ stage: 'downloading', progress: 0, message: 'Instalando Ollama...' });
      const installResult = await window.electronAPI.setup.installOllama();
      
      // Verify installation succeeded before pulling model
      if (!installResult) {
        setOllamaProgress({ 
          stage: 'error', 
          progress: 0, 
          message: 'Installation failed. Please try again.',
          error: 'Ollama installation did not complete successfully.'
        });
        return;
      }
      
      // Re-check status after installation
      status = await window.electronAPI.setup.checkOllama();
      if (!status.installed) {
        setOllamaProgress({ 
          stage: 'error', 
          progress: 0, 
          message: 'Installation not detected. Please try again.',
          error: 'Ollama was not found after installation. Make sure you completed the installer.'
        });
        return;
      }
      
      // Now pull the model
      setOllamaProgress({ stage: 'pulling-model', progress: 0, message: `Descargando modelo ${modelToUse}...` });
      await window.electronAPI.setup.pullOllamaModel(modelToUse);
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
        await window.electronAPI.settings.set('llm.model', modelToUse);
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

  const handleModelDownload = useCallback(async () => {
    setIsLoading(true);
    try {
      await window.electronAPI.setup.downloadModels();
      setCurrentStep('complete');
    } catch (error) {
      console.error('Model download failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleComplete = useCallback(async () => {
    await window.electronAPI.setup.complete();
    onComplete();
  }, [onComplete]);

  // Check if back navigation is available
  const canGoBack = currentStep !== 'welcome' && currentStep !== 'complete' && ollamaProgress.stage !== 'downloading';

  return (
    <div className="fixed inset-0 bg-slate-100 flex items-center justify-center p-4">
      <motion.div
        className="bg-white rounded-xl shadow-lg border border-slate-200 w-full max-w-3xl max-h-[90vh] flex flex-col"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Progress indicator */}
        <div className="px-4 sm:px-8 pt-4 sm:pt-6 pb-3 sm:pb-4 border-b border-slate-100 flex-shrink-0">
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
              />
            )}

            {/* Step 7: Complete */}
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
  const steps = [
    { key: 'welcome', label: 'Inicio' },
    { key: 'python-setup', label: 'Python' },
    { key: 'hardware-select', label: 'Hardware' },
    { key: 'llm-choice', label: 'IA' },
    { key: 'model-select', label: 'Modelo' },
    { key: 'llm-setup', label: 'Config' },
    { key: 'models', label: 'Descargas' },
    { key: 'complete', label: 'Listo' },
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
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-500"
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
        <p className="text-sm text-slate-600">
          Paso {currentIndex + 1} de {steps.length}: <span className="font-semibold text-slate-900">{steps[currentIndex].label}</span>
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
  return (
    <motion.div
      className="text-center py-4 sm:py-6"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="welcome"
    >
      <div className="w-14 h-14 sm:w-16 sm:h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
        <Sparkles className="w-7 h-7 sm:w-8 sm:h-8 text-slate-700" />
      </div>
      <h1 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900">¡Bienvenido!</h1>
      <h2 className="text-base sm:text-lg text-slate-500 mb-4 sm:mb-6">AI Tourism Opinion Analyzer</h2>
      <p className="text-sm sm:text-base text-slate-500 mb-6 sm:mb-8 max-w-md mx-auto leading-relaxed px-4">
        Configuraremos todo lo necesario para que puedas analizar opiniones de turismo
        con inteligencia artificial.
      </p>
      <Button size="lg" onClick={onNext} className="px-6 sm:px-8">
        Comenzar
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
  const [status, setStatus] = useState<'checking' | 'ready' | 'need-install' | 'setting-up' | 'error'>('checking');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Verificando entorno Python...');
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
        setError(data.error || 'Error desconocido');
      }
    };

    window.electronAPI.setup.onPythonProgress(handleProgress);

    return () => {
      window.electronAPI.setup.offPythonProgress();
    };
  }, [onNext]);

  const checkPython = async () => {
    setStatus('checking');
    setMessage('Verificando entorno Python...');
    
    try {
      const pythonStatus = await window.electronAPI.setup.checkPython();
      
      if (pythonStatus.venvExists && pythonStatus.dependenciesInstalled) {
        // Python is ready, skip setup
        setStatus('ready');
        setProgress(100);
        setMessage('¡Entorno Python listo!');
        setTimeout(() => onNext(), 1000);
      } else {
        // Python needs setup - show install button instead of auto-installing
        setStatus('need-install');
        setProgress(0);
        setMessage('Python no está configurado. ¿Deseas instalarlo?');
      }
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Error verificando Python');
    }
  };

  const handleInstallPython = async () => {
    setStatus('setting-up');
    setMessage('Configurando entorno Python...');
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
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Configurando Python
        </h2>
        <p className="text-sm sm:text-base text-slate-500">
          Preparando el entorno de ejecución
        </p>
      </div>

      <div className="max-w-md mx-auto space-y-6">
        {/* Progress during setup */}
        {(status === 'checking' || status === 'setting-up') && (
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
              <span className="text-sm text-slate-600">{message}</span>
            </div>
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-slate-400 text-center">
              Esto puede tardar varios minutos la primera vez...
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
            <p className="text-sm text-slate-500">Continuando automáticamente...</p>
          </div>
        )}

        {/* Need Install - Show button */}
        {status === 'need-install' && (
          <div className="text-center space-y-4">
            <p className="text-sm text-slate-600">Se necesita configurar el entorno Python</p>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={onBack}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Atrás
              </Button>
              <Button onClick={handleInstallPython}>
                <Cpu className="w-4 h-4 mr-2" />
                Instalar Python
              </Button>
            </div>
          </div>
        )}

        {/* Error state */}
        {status === 'error' && error && (
          <div className="space-y-4">
            <div className="p-4 bg-red-50 rounded-xl border border-red-100">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-800">Error de configuración</p>
                  <p className="text-xs text-red-600 mt-1">{error}</p>
                </div>
              </div>
            </div>
            
            <div className="text-center text-sm text-slate-500">
              <p className="mb-2">Asegúrate de tener Python 3.9+ instalado:</p>
              <a 
                href="https://www.python.org/downloads/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                Descargar Python →
              </a>
            </div>

            <div className="flex justify-center gap-3">
              <Button variant="outline" onClick={onBack}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver
              </Button>
              <Button onClick={handleRetry}>
                Reintentar
              </Button>
            </div>
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
  const config = {
    'auto-detected': { 
      label: 'Auto-detectado', 
      className: 'bg-emerald-100 text-emerald-700',
      icon: <Check className="w-3 h-3" />
    },
    'fallback': { 
      label: 'Estimado', 
      className: 'bg-amber-100 text-amber-700',
      icon: <AlertCircle className="w-3 h-3" />
    },
    'manual': { 
      label: 'Manual', 
      className: 'bg-blue-100 text-blue-700',
      icon: <Circle className="w-3 h-3" />
    },
    'failed': { 
      label: 'No detectado', 
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
        <span className="text-xs text-slate-400 hidden sm:inline" title={source}>
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
      reasoning = 'Excelente hardware detectado. Puedes ejecutar modelos locales potentes con aceleración GPU.';
    } else if (ramGB >= 16 && hasGPU && vramGB >= 6) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:3b';
      reasoning = 'Buen hardware con GPU dedicada. Recomendamos modelos locales de tamaño medio.';
    } else if (ramGB >= 16) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:3b';
      reasoning = 'RAM adecuada para modelos locales. La falta de GPU puede ralentizar el procesamiento.';
      if (!hasGPU) {
        warnings.push('Sin GPU dedicada: el procesamiento será más lento');
      }
    } else if (ramGB >= 12) {
      canRunLocalLLM = true;
      recommendedProvider = 'ollama';
      recommendedModel = 'llama3.2:1b';
      reasoning = 'Hardware limitado. Puedes usar modelos ultra-ligeros, pero OpenAI ofrecerá mejor rendimiento.';
      warnings.push('RAM limitada: solo modelos ultra-ligeros (1B) funcionarán bien');
    } else if (ramGB >= 8) {
      canRunLocalLLM = false;
      recommendedProvider = 'openai';
      reasoning = 'RAM insuficiente para modelos locales con buen rendimiento. OpenAI API es la mejor opción.';
      warnings.push('8GB RAM: los modelos locales funcionarán muy lento o fallarán');
    } else {
      canRunLocalLLM = false;
      recommendedProvider = 'openai';
      reasoning = 'Hardware insuficiente para modelos locales. Se requiere OpenAI API.';
      warnings.push('RAM muy baja: los modelos locales no funcionarán correctamente');
    }

    if (cpu === 'low') {
      warnings.push('CPU de gama baja: procesamiento local más lento');
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
        <h2 className="text-lg font-semibold mb-2 text-slate-900">Detectando Hardware</h2>
        <p className="text-sm text-slate-500">Analizando las especificaciones de tu equipo...</p>
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
        <h2 className="text-lg sm:text-xl font-semibold mb-1 text-slate-900">
          Hardware Detectado
        </h2>
        <p className="text-sm text-slate-500">
          Verifica la información y ajústala si es necesario
        </p>
        {detectionError && (
          <div className="mt-2 p-2 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-700">
              ⚠️ Algunos datos no pudieron detectarse automáticamente
            </p>
          </div>
        )}
      </div>

      <div className="space-y-4 max-w-lg mx-auto">
        {/* CPU Section */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-700">Procesador (CPU)</span>
            </div>
            <DetectionStatusBadge status={cpuStatus} source={cpuSource} />
          </div>
          
          {cpuName && cpuStatus !== 'manual' && (
            <p className="text-xs text-slate-500 mb-2 truncate" title={cpuName}>
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
                    ? 'border-slate-900 bg-slate-900 text-white'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                )}
              >
                {level === 'low' && 'Básico'}
                {level === 'mid' && 'Medio'}
                {level === 'high' && 'Potente'}
              </button>
            ))}
          </div>
        </div>

        {/* RAM Section */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-700">Memoria RAM</span>
            </div>
            <DetectionStatusBadge status={ramStatus} source={ramSource} />
          </div>
          
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold text-slate-900">{ram}</span>
            <span className="text-sm text-slate-500">GB</span>
            {ram < 16 && (
              <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full">
                Limitado para LLM local
              </span>
            )}
            {ram >= 16 && ram < 32 && (
              <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                Adecuado
              </span>
            )}
            {ram >= 32 && (
              <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full">
                Excelente
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
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>4 GB</span>
            <span>128 GB</span>
          </div>
        </div>

        {/* GPU Section */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Monitor className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-700">Tarjeta Gráfica (GPU)</span>
            </div>
            <DetectionStatusBadge status={gpuStatus} source={gpuSource} />
          </div>
          
          {gpuName && gpuStatus !== 'manual' && (
            <div className="flex items-center gap-2 mb-2">
              <p className="text-xs text-slate-500 truncate flex-1" title={gpuName}>
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
                    ? 'border-slate-900 bg-slate-900 text-white'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                )}
              >
                {type === 'none' && 'Sin GPU'}
                {type === 'integrated' && 'Integrada'}
                {type === 'dedicated' && 'Dedicada'}
              </button>
            ))}
          </div>
          
          {/* VRAM for dedicated GPU */}
          {gpu === 'dedicated' && (
            <div className="mt-3 pt-3 border-t border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-600">VRAM:</span>
                <span className="font-medium text-slate-900">{vram} GB</span>
              </div>
              <input
                type="range"
                min="2"
                max="24"
                step="2"
                value={vram}
                onChange={(e) => handleManualChange('vram', parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
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
                  <span className="text-sm font-semibold text-slate-900">
                    Recomendación: {recommendation.recommendedProvider === 'openai' ? 'OpenAI API' : 'LLM Local (Ollama)'}
                  </span>
                  {recommendation.recommendedModel && (
                    <span className="text-xs px-2 py-0.5 bg-white/50 rounded-full text-slate-600">
                      {recommendation.recommendedModel}
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-600 mb-2">
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
          <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
            <Circle className="w-3 h-3" />
            <span>Valores modificados manualmente</span>
            <button 
              onClick={detectHardware}
              className="text-blue-600 hover:underline"
            >
              Redetectar
            </button>
          </div>
        )}
      </div>

      <div className="flex justify-between mt-6">
        <Button variant="ghost" onClick={onBack} className="text-slate-500">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Atrás
        </Button>
        <Button onClick={handleContinue}>
          Continuar
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
  
  // Determine recommendation
  const recommendLocal = hasGoodRAM || (hasMarginalRAM && hasGPU && vram >= 6);
  const localWarning = hasLowRAM 
    ? 'RAM insuficiente para buen rendimiento'
    : hasMarginalRAM && !hasGPU 
      ? 'Rendimiento limitado sin GPU'
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="llm-choice"
    >
      <div className="text-center mb-6 sm:mb-8">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Elige tu Proveedor de IA
        </h2>
        <p className="text-sm sm:text-base text-slate-500 px-4">
          El LLM se usa para generar resúmenes inteligentes de las reseñas
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 mb-4 sm:mb-6">
        {/* Ollama Option */}
        <button
          onClick={() => onSelect('ollama')}
          className={cn(
            "p-6 border-2 rounded-xl hover:bg-slate-50 transition-all text-left group relative",
            recommendLocal 
              ? "border-emerald-300 bg-emerald-50/30" 
              : "border-slate-200 hover:border-slate-400",
            hasLowRAM && "opacity-70"
          )}
        >
          {recommendLocal && (
            <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 bg-emerald-500 text-white rounded-full font-medium">
              Recomendado
            </span>
          )}
          <Monitor className="w-7 h-7 text-slate-700 mb-3" />
          <h3 className="font-semibold text-lg text-slate-900 mb-1">LLM Local (Ollama)</h3>
          <p className="text-sm text-slate-500 mb-3">Procesamiento privado en tu equipo</p>
          <ul className="space-y-1.5 text-sm text-slate-600">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              Gratuito y privado
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              Sin conexión a internet
            </li>
            <li className={cn("flex items-center gap-2", !hasGoodRAM && "text-amber-600")}>
              {hasGoodRAM ? (
                <Check className="w-4 h-4 text-emerald-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-amber-500" />
              )}
              Requiere 16GB+ RAM
            </li>
            {hasGPU && (
              <li className="flex items-center gap-2 text-emerald-600">
                <Zap className="w-4 h-4" />
                GPU detectada ({vram}GB VRAM)
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
          <div className="mt-4 flex items-center text-sm font-medium text-slate-700 group-hover:text-slate-900">
            Seleccionar
            <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>

        {/* OpenAI Option */}
        <button
          onClick={() => onSelect('openai')}
          className={cn(
            "p-6 border-2 rounded-xl hover:bg-slate-50 transition-all text-left group relative",
            !recommendLocal 
              ? "border-emerald-300 bg-emerald-50/30" 
              : "border-slate-200 hover:border-slate-400"
          )}
        >
          {!recommendLocal && (
            <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 bg-emerald-500 text-white rounded-full font-medium">
              Recomendado
            </span>
          )}
          <Cloud className="w-7 h-7 text-slate-700 mb-3" />
          <h3 className="font-semibold text-lg text-slate-900 mb-1">OpenAI API</h3>
          <p className="text-sm text-slate-500 mb-3">Procesamiento en la nube</p>
          <ul className="space-y-1.5 text-sm text-slate-600">
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              Configuración rápida
            </li>
            <li className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              No requiere hardware potente
            </li>
            <li className="flex items-center gap-2">
              <Circle className="w-4 h-4 text-slate-300" />
              Pago por uso
            </li>
          </ul>
          <div className="mt-4 flex items-center text-sm font-medium text-slate-700 group-hover:text-slate-900">
            Seleccionar
            <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>
      </div>

      <div className="flex justify-start">
        <Button variant="ghost" onClick={onBack} className="text-slate-500">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Atrás
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

  // Find recommended model based on RAM
  const getRecommendedModel = () => {
    if (totalRam >= 16) return 'llama3.1:8b';
    if (totalRam >= 8) return 'llama3.2:3b';
    return 'llama3.2:1b';
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
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Selecciona el Modelo
        </h2>
        <p className="text-slate-500">
          Elige según las capacidades de tu equipo ({totalRam}GB RAM detectados)
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
                  ? "border-slate-900 bg-slate-50"
                  : "border-slate-200 hover:border-slate-300",
                !canRun && "opacity-50 cursor-not-allowed"
              )}
            >
              <div className={cn(
                "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
                !useCustom && selectedModel === model.id
                  ? "border-slate-900 bg-slate-900"
                  : "border-slate-300"
              )}>
                {!useCustom && selectedModel === model.id && (
                  <Check className="w-3 h-3 text-white" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-slate-900">{model.name}</span>
                  <span className="text-xs text-slate-400">{model.size}</span>
                  {isRecommended && (
                    <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full font-medium">
                      Recomendado
                    </span>
                  )}
                  {!canRun && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">
                      Requiere {model.minRam}GB RAM
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-500">{model.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  {model.performance === 'fast' && (
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Zap className="w-3 h-3" /> Rápido
                    </span>
                  )}
                  {model.performance === 'balanced' && (
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <HardDrive className="w-3 h-3" /> Equilibrado
                    </span>
                  )}
                  {model.performance === 'powerful' && (
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Cpu className="w-3 h-3" /> Potente
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
          useCustom ? "border-slate-900 bg-slate-50" : "border-slate-200"
        )}>
          <button
            onClick={() => onUseCustomChange(true)}
            className="w-full flex items-start gap-4 text-left"
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              useCustom ? "border-slate-900 bg-slate-900" : "border-slate-300"
            )}>
              {useCustom && <Check className="w-3 h-3 text-white" />}
            </div>
            <div className="flex-1">
              <span className="font-medium text-slate-900">Modelo personalizado</span>
              <p className="text-sm text-slate-500">Ingresa el nombre de cualquier modelo de Ollama</p>
            </div>
          </button>
          {useCustom && (
            <div className="mt-3 pl-9">
              <Input
                placeholder="Ej: codellama:7b, phi3:mini"
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                className="w-full"
              />
              <p className="text-xs text-slate-400 mt-1">
                Ver modelos disponibles en{' '}
                <a href="https://ollama.com/library" target="_blank" rel="noopener noreferrer" className="text-slate-600 underline">
                  ollama.com/library
                </a>
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Atrás
        </Button>
        <Button 
          onClick={onNext} 
          disabled={useCustom && !customModel.trim()}
        >
          Continuar
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
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="openai-model-select"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Selecciona el Modelo
        </h2>
        <p className="text-sm sm:text-base text-slate-500 px-4">
          Elige el modelo de OpenAI que deseas usar
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
              "w-full p-4 border-2 rounded-xl text-left transition-all flex items-start gap-4",
              !useCustom && selectedModel === model.id
                ? "border-slate-900 bg-slate-50"
                : "border-slate-200 hover:border-slate-300"
            )}
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              !useCustom && selectedModel === model.id
                ? "border-slate-900 bg-slate-900"
                : "border-slate-300"
            )}>
              {!useCustom && selectedModel === model.id && (
                <Check className="w-3 h-3 text-white" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-slate-900">{model.name}</span>
                {model.recommended && (
                  <span className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full font-medium">
                    Recomendado
                  </span>
                )}
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full font-medium",
                  model.costTier === 'low' && "bg-green-100 text-green-700",
                  model.costTier === 'medium' && "bg-yellow-100 text-yellow-700",
                  model.costTier === 'high' && "bg-red-100 text-red-700"
                )}>
                  {model.costTier === 'low' && 'Económico'}
                  {model.costTier === 'medium' && 'Moderado'}
                  {model.costTier === 'high' && 'Premium'}
                </span>
              </div>
              <p className="text-sm text-slate-500">{model.description}</p>
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
            className="w-full flex items-start gap-4 text-left"
          >
            <div className={cn(
              "w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 flex items-center justify-center",
              useCustom ? "border-slate-900 bg-slate-900" : "border-slate-300"
            )}>
              {useCustom && <Check className="w-3 h-3 text-white" />}
            </div>
            <div className="flex-1">
              <span className="font-medium text-slate-900">Modelo personalizado</span>
              <p className="text-sm text-slate-500">Ingresa el ID de cualquier modelo de OpenAI</p>
            </div>
          </button>
          {useCustom && (
            <div className="mt-3 pl-9">
              <Input
                placeholder="Ej: gpt-4, gpt-3.5-turbo"
                value={customModel}
                onChange={(e) => onCustomModelChange(e.target.value)}
                className="w-full"
              />
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack} className="text-slate-500">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Atrás
        </Button>
        <Button 
          onClick={onNext} 
          disabled={useCustom && !customModel.trim()}
        >
          Continuar
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
  const [started, setStarted] = useState(false);

  const handleStart = () => {
    setStarted(true);
    onStart();
  };

  const isComplete = progress.stage === 'complete';
  const isError = progress.stage === 'error';
  const isIdle = progress.stage === 'idle' || (!started);

  // Parse progress message to get clean status
  const getCleanStatus = () => {
    if (progress.stage === 'downloading') return progress.message || 'Descargando Ollama...';
    if (progress.stage === 'installing') return progress.message || 'Instalando Ollama...';
    if (progress.stage === 'starting') return progress.message || 'Iniciando Ollama...';
    if (progress.stage === 'pulling-model') return progress.message || `Descargando modelo ${modelName}...`;
    if (progress.stage === 'complete') return '¡Completado!';
    if (progress.stage === 'error') return 'Error';
    return progress.message || 'Preparando...';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="ollama-setup"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Configurando Ollama
        </h2>
        <p className="text-sm sm:text-base text-slate-500 px-4">
          Modelo seleccionado: <span className="font-medium text-slate-700">{modelName}</span>
        </p>
      </div>

      {isIdle ? (
        <div className="space-y-6">
          <div className="text-center py-4 sm:py-6">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6">
              <Download className="w-7 h-7 sm:w-8 sm:h-8 text-slate-600" />
            </div>
            <p className="text-sm sm:text-base text-slate-500 mb-4 sm:mb-6 max-w-sm mx-auto px-4">
              Instalaremos Ollama y descargaremos el modelo seleccionado.
              Esto puede tomar unos minutos.
            </p>
          </div>
          <div className="flex justify-between">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Atrás
            </Button>
            <Button onClick={handleStart}>
              <Download className="w-4 h-4 mr-2" />
              Iniciar Instalación
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
              <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto">
                <Loader2 className="w-8 h-8 text-slate-600 animate-spin" />
              </div>
            )}
          </div>
          
          <div className="max-w-md mx-auto">
            {isComplete ? (
              <div className="text-center space-y-3">
                <h3 className="text-lg font-semibold text-emerald-600">
                  {getCleanStatus()}
                </h3>
                <p className="text-sm text-slate-500">
                  Ollama y el modelo han sido instalados correctamente.
                </p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700">{getCleanStatus()}</span>
                </div>
                
                {!isError && (
                  <div className="relative h-6 bg-slate-200 rounded-full overflow-hidden flex items-center">
                    <div
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-end pr-2 transition-all duration-300 shadow-sm"
                      style={{ width: `${progress.progress}%` }}
                    >
                      {progress.progress > 8 && (
                        <span className="text-xs font-semibold text-white drop-shadow-md">
                          {Math.round(progress.progress)}%
                        </span>
                      )}
                    </div>
                    {progress.progress <= 8 && (
                      <span className="absolute left-2 text-xs font-semibold text-slate-600">
                        {Math.round(progress.progress)}%
                      </span>
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
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="openai-setup"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Configura OpenAI
        </h2>
        <p className="text-sm sm:text-base text-slate-500 px-4">
          Modelo: <span className="font-medium text-slate-700">{modelName}</span>
        </p>
      </div>

      <div className="space-y-4 max-w-md mx-auto">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
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

        <p className="text-sm text-slate-400">
          Obtén tu API key en{' '}
          <a
            href="https://platform.openai.com/api-keys"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-600 underline hover:text-slate-800"
          >
            platform.openai.com
          </a>
        </p>
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="ghost" onClick={onBack} className="text-slate-500">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Atrás
        </Button>
        <Button
          onClick={onSubmit}
          disabled={!apiKey || isValidating}
        >
          {isValidating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Validando...
            </>
          ) : (
            <>
              Continuar
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
}: {
  progress: Record<string, number>;
  onStart: () => void;
  isLoading: boolean;
  onBack: () => void;
}) {
  const [started, setStarted] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [animatedProgress, setAnimatedProgress] = useState<Record<string, number>>({});

  useEffect(() => {
    window.electronAPI.setup.getRequiredModels().then(setModels);
  }, []);

  const handleStart = () => {
    setStarted(true);
    onStart();
  };

  const modelKeys = ['sentiment', 'embeddings', 'subjectivity', 'categories'];
  const allComplete = modelKeys.every((key) => progress[key] === 100);
  const totalProgress = modelKeys.reduce((acc, key) => acc + (progress[key] || 0), 0) / modelKeys.length;
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
    { key: 'sentiment', name: 'Modelo de Sentimientos' },
    { key: 'embeddings', name: 'Sentence Embeddings' },
    { key: 'subjectivity', name: 'Clasificador Subjetividad' },
    { key: 'categories', name: 'Clasificador Categorías' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      key="models"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">
          Descargar Modelos de IA
        </h2>
        <p className="text-sm sm:text-base text-slate-500 px-4">
          Los siguientes modelos son requeridos para el análisis completo (~2.5 GB)
        </p>
      </div>

      <div className="space-y-3 mb-6">
        {displayModels.map((model) => {
          const modelProgress = animatedProgress[model.key] || progress[model.key] || 0;
          const isComplete = modelProgress === 100;
          const isDownloading = started && modelProgress > 0 && modelProgress < 100;
          const progressPercent = Math.round(modelProgress);
          
          return (
            <div key={model.key} className="p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-slate-700">{model.name}</span>
                    <span className="text-sm font-bold text-emerald-600">{progressPercent}%</span>
                  </div>
                  {(started || isComplete) && (
                    <div className="relative h-6 bg-slate-200 rounded-full overflow-hidden">
                      <motion.div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full shadow-sm"
                        initial={{ width: 0 }}
                        animate={{ width: `${modelProgress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {!started ? (
        <div className="flex justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-500">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Atrás
          </Button>
          <Button onClick={handleStart} disabled={isLoading}>
            <Download className="w-4 h-4 mr-2" />
            Descargar Modelos
          </Button>
        </div>
      ) : allComplete ? (
        <div className="flex justify-between">
          <Button variant="ghost" onClick={onBack} className="text-slate-500">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Atrás
          </Button>
          <div className="text-emerald-600 font-medium text-sm flex items-center gap-2">
            ✓ Descargas completadas
          </div>
        </div>
      ) : (
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            Progreso total: {Math.round(totalProgress)}%
          </div>
        </div>
      )}
    </motion.div>
  );
}

function CompleteStep({ onFinish }: { onFinish: () => void }) {
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
      <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900">
        ¡Configuración Completa!
      </h2>
      <p className="text-sm sm:text-base text-slate-500 mb-6 sm:mb-8 max-w-sm mx-auto px-4">
        Todo está listo. Ahora puedes cargar un archivo CSV y comenzar
        a analizar opiniones de turismo.
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
            Iniciando aplicación...
          </>
        ) : (
          <>
            Comenzar a Analizar
            <ArrowRight className="w-4 h-4 ml-2" />
          </>
        )}
      </Button>
    </motion.div>
  );
}

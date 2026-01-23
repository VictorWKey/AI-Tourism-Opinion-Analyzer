/**
 * SetupWizard - First-run setup wizard component
 * ===============================================
 * Multi-step wizard for initial app configuration including:
 * - System requirements check
 * - LLM provider selection (Ollama vs OpenAI)
 * - Ollama installation and model download
 * - OpenAI API key validation
 * - ML models download
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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

// Icons as simple SVG components
const CheckCircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <circle cx="12" cy="12" r="9" />
  </svg>
);

const LoaderIcon = ({ className }: { className?: string }) => (
  <svg className={cn("animate-spin", className)} fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

const AlertCircleIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const MonitorIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <rect x="2" y="3" width="20" height="14" rx="2" />
    <line x1="8" y1="21" x2="16" y2="21" />
    <line x1="12" y1="17" x2="12" y2="21" />
  </svg>
);

const CloudIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z" />
  </svg>
);

const DownloadIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
  </svg>
);

const CpuIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <rect x="4" y="4" width="16" height="16" rx="2" />
    <rect x="9" y="9" width="6" height="6" />
    <line x1="9" y1="1" x2="9" y2="4" />
    <line x1="15" y1="1" x2="15" y2="4" />
    <line x1="9" y1="20" x2="9" y2="23" />
    <line x1="15" y1="20" x2="15" y2="23" />
    <line x1="20" y1="9" x2="23" y2="9" />
    <line x1="20" y1="14" x2="23" y2="14" />
    <line x1="1" y1="9" x2="4" y2="9" />
    <line x1="1" y1="14" x2="4" y2="14" />
  </svg>
);

type SetupStep = 'welcome' | 'system-check' | 'llm-choice' | 'llm-setup' | 'models' | 'complete';

interface SetupWizardProps {
  onComplete: () => void;
}

export function SetupWizard({ onComplete }: SetupWizardProps) {
  const [currentStep, setCurrentStep] = useState<SetupStep>('welcome');
  const [llmChoice, setLlmChoice] = useState<'ollama' | 'openai' | null>(null);
  const [systemCheck, setSystemCheck] = useState<SystemCheckResult | null>(null);
  const [ollamaProgress, setOllamaProgress] = useState<OllamaDownloadProgress>({
    stage: 'downloading',
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

  const handleSystemCheck = useCallback(async () => {
    setIsLoading(true);
    try {
      const result = await window.electronAPI.setup.systemCheck();
      setSystemCheck(result);
      setCurrentStep('llm-choice');
    } catch (error) {
      console.error('System check failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleLLMChoice = useCallback(async (choice: 'ollama' | 'openai') => {
    setLlmChoice(choice);
    await window.electronAPI.setup.setLLMProvider(choice);
    setCurrentStep('llm-setup');
  }, []);

  const handleOllamaSetup = useCallback(async () => {
    setOllamaProgress({ stage: 'downloading', progress: 0, message: 'Starting...' });
    
    // Check if Ollama is already installed
    const status = await window.electronAPI.setup.checkOllama();
    
    if (status.installed && status.running) {
      // Check if model is available
      const hasModel = await window.electronAPI.setup.hasOllamaModel('llama3.2:3b');
      if (hasModel) {
        setCurrentStep('models');
        return;
      }
      // Just pull the model
      await window.electronAPI.setup.pullOllamaModel('llama3.2:3b');
    } else if (status.installed) {
      // Start Ollama and pull model
      await window.electronAPI.setup.startOllama();
      await window.electronAPI.setup.pullOllamaModel('llama3.2:3b');
    } else {
      // Install Ollama first
      await window.electronAPI.setup.installOllama();
      await window.electronAPI.setup.pullOllamaModel('llama3.2:3b');
    }
  }, []);

  const handleOpenAISetup = useCallback(async () => {
    setIsValidating(true);
    setKeyError('');

    try {
      const result = await window.electronAPI.setup.validateOpenAIKey(openaiKey);
      
      if (result.valid) {
        await window.electronAPI.settings.set('llm.apiKey', openaiKey);
        setCurrentStep('models');
      } else {
        setKeyError(result.error || 'Invalid API key');
      }
    } catch (error) {
      setKeyError('Failed to validate API key');
    } finally {
      setIsValidating(false);
    }
  }, [openaiKey]);

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

  const handleSkipModels = useCallback(() => {
    setCurrentStep('complete');
  }, []);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-900 to-slate-900 flex items-center justify-center p-4">
      <motion.div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <AnimatePresence mode="wait">
          {/* Step 1: Welcome */}
          {currentStep === 'welcome' && (
            <WelcomeStep onNext={handleSystemCheck} isLoading={isLoading} />
          )}

          {/* Step 2: System Check (shown briefly as loading) */}
          {currentStep === 'system-check' && (
            <SystemCheckStep result={systemCheck} />
          )}

          {/* Step 3: LLM Choice */}
          {currentStep === 'llm-choice' && (
            <LLMChoiceStep 
              onSelect={handleLLMChoice} 
              systemCheck={systemCheck}
            />
          )}

          {/* Step 4: LLM Setup */}
          {currentStep === 'llm-setup' && (
            llmChoice === 'ollama' ? (
              <OllamaSetupStep
                progress={ollamaProgress}
                onStart={handleOllamaSetup}
              />
            ) : (
              <OpenAISetupStep
                apiKey={openaiKey}
                onKeyChange={setOpenaiKey}
                error={keyError}
                isValidating={isValidating}
                onSubmit={handleOpenAISetup}
              />
            )
          )}

          {/* Step 5: Model Downloads */}
          {currentStep === 'models' && (
            <ModelDownloadStep
              progress={modelProgress}
              onStart={handleModelDownload}
              onSkip={handleSkipModels}
              isLoading={isLoading}
            />
          )}

          {/* Step 6: Complete */}
          {currentStep === 'complete' && (
            <CompleteStep onFinish={handleComplete} />
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

// Sub-components for each step

function WelcomeStep({ 
  onNext, 
  isLoading 
}: { 
  onNext: () => void;
  isLoading: boolean;
}) {
  return (
    <motion.div
      className="text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="welcome"
    >
      <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <CpuIcon className="w-10 h-10 text-blue-600" />
      </div>
      <h1 className="text-3xl font-bold mb-2 text-gray-900">¡Bienvenido!</h1>
      <h2 className="text-xl text-slate-600 mb-6">AI Tourism Opinion Analyzer</h2>
      <p className="text-slate-500 mb-8 max-w-md mx-auto">
        Configuraremos todo lo necesario para que puedas analizar opiniones de turismo
        con inteligencia artificial.
      </p>
      <Button size="lg" onClick={onNext} disabled={isLoading}>
        {isLoading ? (
          <>
            <LoaderIcon className="w-5 h-5 mr-2" />
            Verificando sistema...
          </>
        ) : (
          'Comenzar Configuración'
        )}
      </Button>
    </motion.div>
  );
}

function SystemCheckStep({ result }: { result: SystemCheckResult | null }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="system-check"
      className="text-center"
    >
      <LoaderIcon className="w-12 h-12 mx-auto text-blue-600 mb-4" />
      <h2 className="text-2xl font-bold mb-2 text-gray-900">Verificando Sistema</h2>
      <p className="text-slate-500">Por favor espera...</p>
    </motion.div>
  );
}

function LLMChoiceStep({ 
  onSelect,
  systemCheck,
}: { 
  onSelect: (choice: 'ollama' | 'openai') => void;
  systemCheck: SystemCheckResult | null;
}) {
  const hasEnoughMemory = systemCheck?.memory?.sufficient ?? true;
  const hasGPU = systemCheck?.gpu?.available ?? false;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="llm-choice"
    >
      <h2 className="text-2xl font-bold mb-2 text-center text-gray-900">
        Elige tu Proveedor de IA
      </h2>
      <p className="text-slate-500 mb-8 text-center">
        ¿Cómo quieres procesar el análisis de lenguaje natural?
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Ollama Option */}
        <button
          onClick={() => onSelect('ollama')}
          className={cn(
            "p-6 border-2 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all text-left",
            !hasEnoughMemory && "opacity-60"
          )}
        >
          <MonitorIcon className="w-8 h-8 text-blue-600 mb-3" />
          <h3 className="font-bold text-lg text-gray-900">LLM Local (Ollama)</h3>
          <ul className="mt-3 space-y-1 text-sm text-slate-600">
            <li>✓ Gratuito y privado</li>
            <li>✓ Sin conexión a internet</li>
            <li className={cn(!hasEnoughMemory && "text-amber-600")}>
              {hasEnoughMemory ? '✓' : '⚠'} Requiere ~4GB RAM
            </li>
            <li>○ Descarga ~2GB inicial</li>
            {hasGPU && <li className="text-green-600">✓ GPU detectada</li>}
          </ul>
          {!hasEnoughMemory && (
            <p className="mt-2 text-xs text-amber-600">
              Tu sistema tiene poca memoria, pero puedes intentarlo.
            </p>
          )}
        </button>

        {/* OpenAI Option */}
        <button
          onClick={() => onSelect('openai')}
          className="p-6 border-2 rounded-xl hover:border-green-500 hover:bg-green-50 transition-all text-left"
        >
          <CloudIcon className="w-8 h-8 text-green-600 mb-3" />
          <h3 className="font-bold text-lg text-gray-900">OpenAI API</h3>
          <ul className="mt-3 space-y-1 text-sm text-slate-600">
            <li>✓ Configuración rápida</li>
            <li>✓ No requiere GPU</li>
            <li>○ Pago por uso</li>
            <li>○ Requiere API key</li>
          </ul>
        </button>
      </div>
    </motion.div>
  );
}

function OllamaSetupStep({
  progress,
  onStart,
}: {
  progress: OllamaDownloadProgress;
  onStart: () => void;
}) {
  const [started, setStarted] = useState(false);

  const handleStart = () => {
    setStarted(true);
    onStart();
  };

  const isComplete = progress.stage === 'complete';
  const isError = progress.stage === 'error';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="ollama-setup"
    >
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-900">
        Configurando Ollama
      </h2>

      {!started ? (
        <div className="text-center">
          <p className="text-slate-500 mb-6">
            Instalaremos Ollama y descargaremos el modelo llama3.2 (~2GB).
            Esto puede tomar unos minutos dependiendo de tu conexión.
          </p>
          <Button size="lg" onClick={handleStart}>
            <DownloadIcon className="w-5 h-5 mr-2" />
            Iniciar Instalación
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-center mb-4">
            {isComplete ? (
              <CheckCircleIcon className="w-12 h-12 mx-auto text-green-500" />
            ) : isError ? (
              <AlertCircleIcon className="w-12 h-12 mx-auto text-red-500" />
            ) : (
              <LoaderIcon className="w-12 h-12 mx-auto text-blue-600" />
            )}
            <p className="mt-2 font-medium text-gray-900">{progress.message}</p>
            {progress.error && (
              <p className="mt-1 text-sm text-red-500">{progress.error}</p>
            )}
          </div>
          {!isComplete && !isError && (
            <>
              <Progress value={progress.progress} />
              <p className="text-sm text-slate-500 text-center">{progress.progress}%</p>
            </>
          )}
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
}: {
  apiKey: string;
  onKeyChange: (key: string) => void;
  error: string;
  isValidating: boolean;
  onSubmit: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="openai-setup"
    >
      <h2 className="text-2xl font-bold mb-2 text-center text-gray-900">
        Configura OpenAI
      </h2>
      <p className="text-slate-500 mb-6 text-center">
        Ingresa tu API key de OpenAI para continuar.
      </p>

      <div className="space-y-4 max-w-md mx-auto">
        <div>
          <Input
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(e) => onKeyChange(e.target.value)}
            className={error ? 'border-red-500' : ''}
          />
          {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        </div>

        <p className="text-xs text-slate-400">
          Obtén tu API key en{' '}
          <a
            href="https://platform.openai.com/api-keys"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 underline"
          >
            platform.openai.com
          </a>
        </p>

        <Button
          className="w-full"
          onClick={onSubmit}
          disabled={!apiKey || isValidating}
        >
          {isValidating ? (
            <>
              <LoaderIcon className="w-4 h-4 mr-2" />
              Validando...
            </>
          ) : (
            'Continuar'
          )}
        </Button>
      </div>
    </motion.div>
  );
}

function ModelDownloadStep({
  progress,
  onStart,
  onSkip,
  isLoading,
}: {
  progress: Record<string, number>;
  onStart: () => void;
  onSkip: () => void;
  isLoading: boolean;
}) {
  const [started, setStarted] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);

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
    if (allComplete && started) {
      // Auto-advance after short delay
      setTimeout(onSkip, 1000);
    }
  }, [allComplete, started, onSkip]);

  const displayModels = [
    { key: 'sentiment', name: 'Modelo de Sentimientos', size: '420 MB' },
    { key: 'embeddings', name: 'Sentence Embeddings', size: '80 MB' },
    { key: 'subjectivity', name: 'Clasificador Subjetividad', size: '440 MB' },
    { key: 'categories', name: 'Clasificador Categorías', size: '440 MB' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      key="models"
    >
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-900">
        Descargando Modelos de IA
      </h2>

      <div className="space-y-3 mb-6">
        {displayModels.map((model) => (
          <div key={model.key} className="flex items-center gap-3">
            <div className="w-6 h-6 flex items-center justify-center">
              {progress[model.key] === 100 ? (
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
              ) : progress[model.key] > 0 ? (
                <LoaderIcon className="w-5 h-5 text-blue-500" />
              ) : (
                <CircleIcon className="w-5 h-5 text-slate-300" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex justify-between text-sm">
                <span className="text-gray-900">{model.name}</span>
                <span className="text-slate-400">{model.size}</span>
              </div>
              {started && progress[model.key] !== undefined && progress[model.key] < 100 && (
                <Progress value={progress[model.key]} className="h-1 mt-1" />
              )}
            </div>
          </div>
        ))}
      </div>

      {!started ? (
        <div className="space-y-3">
          <Button className="w-full" size="lg" onClick={handleStart} disabled={isLoading}>
            <DownloadIcon className="w-5 h-5 mr-2" />
            Descargar Modelos (~1.4 GB)
          </Button>
          <Button variant="ghost" className="w-full" onClick={onSkip}>
            Omitir por ahora
          </Button>
        </div>
      ) : (
        <div className="text-center">
          <p className="text-sm text-slate-500">
            Progreso total: {Math.round(totalProgress)}%
          </p>
        </div>
      )}
    </motion.div>
  );
}

function CompleteStep({ onFinish }: { onFinish: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center"
      key="complete"
    >
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <CheckCircleIcon className="w-12 h-12 text-green-600" />
      </div>
      <h2 className="text-2xl font-bold mb-2 text-gray-900">
        ¡Configuración Completa!
      </h2>
      <p className="text-slate-500 mb-8">
        Todo está listo. Ahora puedes cargar un archivo CSV y comenzar
        a analizar opiniones de turismo.
      </p>
      <Button size="lg" onClick={onFinish}>
        Comenzar a Analizar
      </Button>
    </motion.div>
  );
}

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  Loader2, AlertCircle, Monitor, Cloud, Cpu, ArrowLeft, ArrowRight,
  Zap, HardDrive, Circle
} from 'lucide-react';
import { Button } from '../../ui/button';
import { cn } from '../../../lib/utils';
import { DetectionStatusBadge } from './DetectionStatusBadge';
import type { HardwareConfig } from '../types';

export function HardwareSelectStep({
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
  
  const [recommendation, setRecommendation] = useState<{
    canRunLocalLLM: boolean;
    recommendedProvider: 'ollama' | 'openai';
    recommendedModel?: string;
    reasoning: string;
    warnings: string[];
  } | null>(null);
  
  const [manualMode, setManualMode] = useState(false);

  useEffect(() => {
    detectHardware();
  }, []);

  const detectHardware = async () => {
    setIsLoading(true);
    setDetectionError(null);
    
    try {
      const result = await window.electronAPI.setup.detectHardware();
      
      setCpu(result.cpu.tier);
      setCpuName(result.cpu.name);
      setCpuStatus(result.cpu.detectionStatus);
      setCpuSource(result.cpu.detectionSource);
      
      setRam(result.ram.totalGB);
      setRamStatus(result.ram.detectionStatus);
      setRamSource(result.ram.detectionSource);
      
      setGpu(result.gpu.type);
      setGpuName(result.gpu.name || '');
      setGpuStatus(result.gpu.detectionStatus);
      setGpuSource(result.gpu.detectionSource);
      setVram(result.gpu.vramGB || 0);
      setHasCuda(result.gpu.cudaAvailable);
      
      setRecommendation(result.recommendation);
      
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

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        key="hardware-loading"
        className="text-center py-8"
      >
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <Loader2 className="w-7 h-7 sm:w-8 sm:h-8 text-orange-600 dark:text-orange-400 animate-spin" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">{t('hardwareSelect.title')}</h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400">{t('hardwareSelect.detecting')}</p>
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
      <div className="text-center mb-6">
        <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-5">
          <HardDrive className="w-7 h-7 sm:w-8 sm:h-8 text-orange-600 dark:text-orange-400" />
        </div>
        <h2 className="text-xl sm:text-2xl font-semibold mb-2 text-slate-900 dark:text-white">
          {t('hardwareSelect.detected')}
        </h2>
        <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400">
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
              <span className="text-xs px-2 py-0.5 bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 rounded-full">
                {t('hardwareSelect.ramLimited')}
              </span>
            )}
            {ram >= 16 && ram < 32 && (
              <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-full">
                {t('hardwareSelect.ramAdequate')}
              </span>
            )}
            {ram >= 32 && (
              <span className="text-xs px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded-full">
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
            aria-label={t('hardwareSelect.ram')}
            aria-valuetext={`${ram} GB`}
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
                <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-full shrink-0">
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
                aria-label="VRAM"
                aria-valuetext={`${vram} GB`}
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
              ? 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-800'
              : recommendation.warnings.length === 0
                ? 'bg-emerald-50 dark:bg-emerald-900/10 border-emerald-200 dark:border-emerald-800'
                : 'bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800'
          )}>
            <div className="flex items-start gap-3">
              <div className={cn(
                'shrink-0',
                recommendation.recommendedProvider === 'openai'
                  ? 'text-amber-600 dark:text-amber-400'
                  : recommendation.warnings.length === 0
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-blue-600 dark:text-blue-400'
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

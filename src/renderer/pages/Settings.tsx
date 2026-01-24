/**
 * Settings Page
 * ==============
 * Application and LLM configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Settings as SettingsIcon,
  Cpu,
  Key,
  Folder,
  Check,
  AlertCircle,
  RefreshCw,
  Download,
  Trash2,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button, Input } from '../components/ui';
import { cn } from '../lib/utils';
import { useSettingsStore } from '../stores/settingsStore';
import { useOllama } from '../hooks/useOllama';

type SettingsTab = 'llm' | 'app' | 'ollama';

export function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('llm');
  const { llm, setLLMConfig, outputDir, setOutputDir, isSaving, setSaving } = useSettingsStore();
  const {
    isRunning: ollamaRunning,
    models,
    currentModel,
    isLoading: ollamaLoading,
    error: ollamaError,
    checkStatus,
    pullModel,
    deleteModel,
    selectModel,
  } = useOllama();

  const [apiKey, setApiKey] = useState(llm.apiKey || '');
  const [newModelName, setNewModelName] = useState('');
  const [isPullingModel, setIsPullingModel] = useState(false);

  // Load settings on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const settings = await window.electronAPI.settings.getAll();
        if (settings) {
          setLLMConfig(settings.llm);
          setOutputDir(settings.app.outputDir);
          if (settings.llm.apiKey) {
            setApiKey(settings.llm.apiKey);
          }
        }
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    };
    loadSettings();
  }, [setLLMConfig, setOutputDir]);

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await window.electronAPI.settings.set('llm', {
        ...llm,
        apiKey: apiKey || undefined,
      });
      await window.electronAPI.settings.set('app', {
        language: 'es',
        outputDir,
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleSelectOutputDir = async () => {
    const dir = await window.electronAPI.files.selectDirectory();
    if (dir) {
      setOutputDir(dir);
    }
  };

  const handlePullModel = async () => {
    if (!newModelName.trim()) return;
    setIsPullingModel(true);
    await pullModel(newModelName.trim());
    setNewModelName('');
    setIsPullingModel(false);
  };

  const handleDeleteModel = async (name: string) => {
    if (confirm(`¿Eliminar el modelo "${name}"?`)) {
      await deleteModel(name);
    }
  };

  const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    { id: 'llm', label: 'LLM', icon: <Cpu className="w-4 h-4" /> },
    { id: 'ollama', label: 'Ollama', icon: <Download className="w-4 h-4" /> },
    { id: 'app', label: 'Aplicación', icon: <SettingsIcon className="w-4 h-4" /> },
  ];

  return (
    <PageLayout
      title="Configuración"
      description="Ajusta las opciones de la aplicación y LLM"
      headerActions={
        <Button onClick={handleSaveSettings} disabled={isSaving}>
          {isSaving ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Guardando...
            </>
          ) : (
            <>
              <Check className="w-4 h-4 mr-2" />
              Guardar Cambios
            </>
          )}
        </Button>
      }
    >
      <div className="max-w-3xl mx-auto">
        {/* Current LLM Status */}
        <div className="mb-6 p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                LLM Actualmente Configurado
              </p>
              <div className="flex items-center gap-2">
                {llm.mode === 'local' ? (
                  <>
                    <Cpu className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <span className="text-lg font-semibold text-slate-900 dark:text-white">
                      Ollama Local: {llm.localModel}
                    </span>
                  </>
                ) : (
                  <>
                    <Key className="w-5 h-5 text-green-600 dark:text-green-400" />
                    <span className="text-lg font-semibold text-slate-900 dark:text-white">
                      OpenAI API: {llm.apiModel}
                    </span>
                  </>
                )}
              </div>
            </div>
            <div
              className={cn(
                'px-3 py-1 rounded-full text-sm font-medium',
                llm.mode === 'local'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                  : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
              )}
            >
              {llm.mode === 'local' ? 'Local' : 'API'}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-slate-200 dark:border-slate-700">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px',
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              )}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* LLM Settings */}
        {activeTab === 'llm' && (
          <div className="space-y-6">
            {/* Mode Selection */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                Modo de LLM
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setLLMConfig({ mode: 'local' })}
                  className={cn(
                    'p-4 rounded-lg border-2 text-left transition-colors',
                    llm.mode === 'local'
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  )}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-slate-900 dark:text-white">
                      Local (Ollama)
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Ejecuta modelos localmente sin conexión a internet
                  </p>
                </button>

                <button
                  onClick={() => setLLMConfig({ mode: 'api' })}
                  className={cn(
                    'p-4 rounded-lg border-2 text-left transition-colors',
                    llm.mode === 'api'
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  )}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Key className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-slate-900 dark:text-white">
                      API (OpenAI)
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Usa la API de OpenAI para mayor capacidad
                  </p>
                </button>
              </div>
            </div>

            {/* Local Model Selection */}
            {llm.mode === 'local' && (
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
                <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                  Modelo Local Instalado
                </h3>
                <div className="space-y-3">
                  {models && models.length > 0 ? (
                    <>
                      <select
                        value={llm.localModel}
                        onChange={(e) => setLLMConfig({ localModel: e.target.value })}
                        className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                      >
                        {models.map((model) => (
                          <option key={model.name} value={model.name}>
                            {model.name} {currentModel === model.name ? '(Actual)' : ''}
                          </option>
                        ))}
                      </select>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {models.length} modelo(s) instalado(s) en Ollama. Ve a la pestaña "Ollama" para descargar más modelos.
                      </p>
                    </>
                  ) : (
                    <div className="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
                      <p className="text-sm text-yellow-800 dark:text-yellow-300 mb-2">
                        No hay modelos instalados en Ollama
                      </p>
                      <p className="text-xs text-yellow-700 dark:text-yellow-400">
                        Ve a la pestaña "Ollama" para descargar e instalar modelos.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* API Configuration */}
            {llm.mode === 'api' && (
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
                <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                  Configuración de API
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      API Key
                    </label>
                    <Input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="sk-..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Modelo
                    </label>
                    <select
                      value={llm.apiModel}
                      onChange={(e) => setLLMConfig({ apiModel: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                    >
                      <option value="gpt-4o-mini">GPT-4o Mini (Económico)</option>
                      <option value="gpt-4o">GPT-4o (Potente)</option>
                      <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Temperature */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                Temperatura
              </h3>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={llm.temperature}
                  onChange={(e) => setLLMConfig({ temperature: parseFloat(e.target.value) })}
                  className="flex-1"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300 w-12">
                  {llm.temperature}
                </span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Valores más bajos = respuestas más deterministas
              </p>
            </div>
          </div>
        )}

        {/* Ollama Management */}
        {activeTab === 'ollama' && (
          <div className="space-y-6">
            {/* Status */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-slate-900 dark:text-white">
                  Estado de Ollama
                </h3>
                <Button variant="outline" size="sm" onClick={checkStatus}>
                  <RefreshCw className={cn('w-4 h-4 mr-2', ollamaLoading && 'animate-spin')} />
                  Verificar
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className={cn(
                    'w-3 h-3 rounded-full',
                    ollamaRunning ? 'bg-green-500' : 'bg-red-500'
                  )}
                />
                <span className="text-slate-700 dark:text-slate-300">
                  {ollamaRunning ? 'Conectado y funcionando' : 'No disponible'}
                </span>
              </div>
              {ollamaError && (
                <div className="mt-3 flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm">{ollamaError}</span>
                </div>
              )}
            </div>

            {/* Models List */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                Modelos Instalados
              </h3>
              {models.length > 0 ? (
                <div className="space-y-2">
                  {models.map((model) => (
                    <div
                      key={model.name}
                      className={cn(
                        'flex items-center justify-between p-3 rounded-lg',
                        currentModel === model.name
                          ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                          : 'bg-slate-50 dark:bg-slate-700/50'
                      )}
                    >
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">
                          {model.name}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {(model.size / 1e9).toFixed(1)} GB
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {currentModel !== model.name && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => selectModel(model.name)}
                          >
                            Seleccionar
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteModel(model.name)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 dark:text-slate-400 text-center py-4">
                  No hay modelos instalados
                </p>
              )}
            </div>

            {/* Pull New Model */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                Descargar Nuevo Modelo
              </h3>
              <div className="flex gap-2">
                <Input
                  value={newModelName}
                  onChange={(e) => setNewModelName(e.target.value)}
                  placeholder="Nombre del modelo (ej: llama3.2)"
                  className="flex-1"
                />
                <Button onClick={handlePullModel} disabled={isPullingModel || !newModelName}>
                  {isPullingModel ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* App Settings */}
        {activeTab === 'app' && (
          <div className="space-y-6">
            {/* Output Directory */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
              <h3 className="font-medium text-slate-900 dark:text-white mb-4">
                Directorio de Salida
              </h3>
              <div className="flex gap-2">
                <Input
                  value={outputDir}
                  onChange={(e) => setOutputDir(e.target.value)}
                  placeholder="Selecciona una carpeta..."
                  className="flex-1"
                  readOnly
                />
                <Button variant="outline" onClick={handleSelectOutputDir}>
                  <Folder className="w-4 h-4 mr-2" />
                  Seleccionar
                </Button>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Carpeta donde se guardarán los resultados del análisis
              </p>
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
}

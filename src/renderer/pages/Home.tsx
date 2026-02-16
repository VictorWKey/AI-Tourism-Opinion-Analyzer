/**
 * Home Page
 * ==========
 * Dashboard with quick actions and status overview
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PlayCircle,
  Upload,
  BarChart2,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button } from '../components/ui';
import { cn } from '../lib/utils';
import { useOllamaStatus } from '../hooks/useOllama';
import { usePipelineStore } from '../stores/pipelineStore';
import { useDataStore } from '../stores/dataStore';

interface QuickActionCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
  disabled?: boolean;
}

function QuickActionCard({
  icon,
  title,
  description,
  onClick,
  disabled,
}: QuickActionCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex flex-col items-center p-6 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700',
        'transition-all hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600',
        disabled ? 'opacity-50 cursor-not-allowed hover:shadow-none hover:border-slate-200' : 'cursor-pointer'
      )}
    >
      <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 mb-3">
        {icon}
      </div>
      <h3 className="font-medium text-slate-900 dark:text-white">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 text-center mt-1">
        {description}
      </p>
    </button>
  );
}

interface StatusCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  status: 'success' | 'warning' | 'error' | 'neutral';
}

function StatusCard({ icon, title, value, status }: StatusCardProps) {
  const [isTruncated, setIsTruncated] = React.useState(false);
  const textRef = React.useRef<HTMLParagraphElement>(null);

  const statusColors = {
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    error: 'text-red-600 dark:text-red-400',
    neutral: 'text-slate-600 dark:text-slate-400',
  };

  // Check if text is truncated
  React.useEffect(() => {
    const element = textRef.current;
    if (element) {
      setIsTruncated(element.scrollWidth > element.clientWidth);
    }
  }, [value]);

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div className="flex items-center gap-3">
        <div className={cn('w-8 h-8 flex-shrink-0', statusColors[status])}>{icon}</div>
        <div className="min-w-0 flex-1">
          <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
          <div className="relative group">
            <p 
              ref={textRef}
              className={cn('font-medium truncate', isTruncated && 'cursor-help', statusColors[status])}
            >
              {value}
            </p>
            {/* Custom Tooltip - Only show if text is truncated */}
            {isTruncated && (
              <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block z-50 w-max max-w-md">
                <div className="bg-slate-900 dark:bg-slate-700 text-white text-xs rounded-lg py-2 px-3 shadow-lg">
                  {value}
                  <div className="absolute top-full left-4 -mt-1 w-2 h-2 bg-slate-900 dark:bg-slate-700 rotate-45"></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export function Home() {
  const navigate = useNavigate();
  const { isRunning: ollamaRunning, isLoading: ollamaLoading } = useOllamaStatus();
  const pipelineRunning = usePipelineStore((state) => state.isRunning);
  const phases = usePipelineStore((state) => state.phases);
  const completedCount = Object.values(phases).filter((p) => p.status === 'completed').length;
  const { dataset } = useDataStore();
  const [lastAnalysis, setLastAnalysis] = useState<string | null>(null);

  // Get last analysis date from settings
  useEffect(() => {
    window.electronAPI.settings.get<string>('lastAnalysisDate').then((date) => {
      if (date) {
        setLastAnalysis(new Date(date).toLocaleDateString('es-ES', {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        }));
      }
    }).catch(() => {
      // Ignore errors
    });
  }, []);

  return (
    <PageLayout
      title="Inicio"
      description="Panel de control del analizador de opiniones turísticas"
    >
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatusCard
            icon={<Cpu className="w-full h-full" />}
            title="Estado LLM"
            value={ollamaLoading ? 'Verificando...' : ollamaRunning ? 'Conectado' : 'Desconectado'}
            status={ollamaLoading ? 'warning' : ollamaRunning ? 'success' : 'error'}
          />
          <StatusCard
            icon={<Upload className="w-full h-full" />}
            title="Dataset"
            value={dataset ? dataset.name : 'Sin cargar'}
            status={dataset ? 'success' : 'neutral'}
          />
          <StatusCard
            icon={<CheckCircle className="w-full h-full" />}
            title="Fases Completadas"
            value={`${completedCount} / 7`}
            status={completedCount === 7 ? 'success' : completedCount > 0 ? 'warning' : 'neutral'}
          />
          <StatusCard
            icon={<Clock className="w-full h-full" />}
            title="Último Análisis"
            value={lastAnalysis || 'Nunca'}
            status="neutral"
          />
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Acciones Rápidas
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <QuickActionCard
              icon={<Upload className="w-6 h-6" />}
              title="Cargar Datos"
              description="Importar un dataset CSV para analizar"
              onClick={() => navigate('/data')}
            />
            <QuickActionCard
              icon={<PlayCircle className="w-6 h-6" />}
              title="Ejecutar Pipeline"
              description="Iniciar el análisis completo"
              onClick={() => navigate('/pipeline')}
              disabled={!dataset || pipelineRunning}
            />
            <QuickActionCard
              icon={<BarChart2 className="w-6 h-6" />}
              title="Ver Visualizaciones"
              description="Explorar gráficos y métricas"
              onClick={() => navigate('/visualizations')}
            />
            <QuickActionCard
              icon={<FileText className="w-6 h-6" />}
              title="Ver Resultados"
              description="Revisar resúmenes y reportes"
              onClick={() => navigate('/insights')}
            />
          </div>
        </div>

        {/* Pipeline Running Alert */}
        {pipelineRunning && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
              <PlayCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-pulse" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-blue-900 dark:text-blue-100">
                Análisis en progreso
              </p>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                El pipeline está procesando los datos...
              </p>
            </div>
            <Button onClick={() => navigate('/pipeline')}>Ver progreso</Button>
          </div>
        )}

        {/* Ollama Warning */}
        {!ollamaLoading && !ollamaRunning && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-yellow-100 dark:bg-yellow-900/50 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-yellow-900 dark:text-yellow-100">
                Ollama no está disponible
              </p>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                Algunas fases del análisis requieren un LLM activo.
              </p>
            </div>
            <Button variant="outline" onClick={() => navigate('/settings')}>
              Configurar
            </Button>
          </div>
        )}

        {/* Getting Started */}
        {!dataset && (
          <div className="bg-slate-100 dark:bg-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              ¿Cómo empezar?
            </h2>
            <ol className="list-decimal list-inside space-y-2 text-slate-600 dark:text-slate-300">
              <li>Carga un archivo CSV con opiniones de turismo</li>
              <li>Configura las fases del pipeline que deseas ejecutar</li>
              <li>Inicia el análisis y espera los resultados</li>
              <li>Explora las visualizaciones y resúmenes generados</li>
            </ol>
          </div>
        )}
      </div>
    </PageLayout>
  );
}

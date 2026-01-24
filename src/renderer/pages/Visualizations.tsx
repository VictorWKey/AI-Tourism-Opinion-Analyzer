/**
 * Visualizations Page
 * ====================
 * Display generated charts and visualizations
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart2,
  PieChart,
  TrendingUp,
  Cloud,
  Download,
  ExternalLink,
  Folder,
  RefreshCw,
  ImageIcon,
} from 'lucide-react';
import { PageLayout } from '../components/layout';
import { Button } from '../components/ui';
import { cn } from '../lib/utils';
import { useDataStore } from '../stores/dataStore';

type ChartCategory = 'all' | 'sentiment' | 'category' | 'topic' | 'temporal';

interface ChartInfo {
  name: string;
  path: string;
  category: ChartCategory;
}

const categoryLabels: Record<ChartCategory, string> = {
  all: 'Todas',
  sentiment: 'Sentimientos',
  category: 'Categorías',
  topic: 'Tópicos',
  temporal: 'Temporales',
};

const categoryIcons: Record<ChartCategory, React.ReactNode> = {
  all: <BarChart2 className="w-4 h-4" />,
  sentiment: <TrendingUp className="w-4 h-4" />,
  category: <PieChart className="w-4 h-4" />,
  topic: <Cloud className="w-4 h-4" />,
  temporal: <BarChart2 className="w-4 h-4" />,
};

export function Visualizations() {
  const { chartsPath } = useDataStore();
  const [charts, setCharts] = useState<ChartInfo[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<ChartCategory>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedChart, setSelectedChart] = useState<string | null>(null);

  // Load chart list from charts directory
  useEffect(() => {
    loadCharts();
  }, [chartsPath]);

  const loadCharts = async () => {
    setIsLoading(true);
    
    // For now, show placeholder until real charts are generated
    // In real implementation, scan the charts directory
    setCharts([]);
    setIsLoading(false);
  };

  const filteredCharts =
    selectedCategory === 'all'
      ? charts
      : charts.filter((c) => c.category === selectedCategory);

  const handleOpenFolder = async () => {
    if (chartsPath) {
      await window.electronAPI.files.openPath(chartsPath);
    }
  };

  return (
    <PageLayout
      title="Visualizaciones"
      description="Explora los gráficos generados por el análisis"
      headerActions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadCharts}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualizar
          </Button>
          {chartsPath && (
            <Button variant="outline" size="sm" onClick={handleOpenFolder}>
              <Folder className="w-4 h-4 mr-2" />
              Abrir Carpeta
            </Button>
          )}
        </div>
      }
    >
      <div className="space-y-6">
        {/* Category Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          {(Object.keys(categoryLabels) as ChartCategory[]).map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
              )}
            >
              {categoryIcons[category]}
              {categoryLabels[category]}
            </button>
          ))}
        </div>

        {/* Charts Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
          </div>
        ) : filteredCharts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCharts.map((chart) => (
              <div
                key={chart.path}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden group cursor-pointer"
                onClick={() => setSelectedChart(chart.path)}
              >
                <div className="aspect-video bg-slate-100 dark:bg-slate-700 flex items-center justify-center">
                  <img
                    src={`file://${chart.path}`}
                    alt={chart.name}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
                <div className="p-3 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">
                    {chart.name}
                  </span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded">
                      <Download className="w-4 h-4 text-slate-500" />
                    </button>
                    <button className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded">
                      <ExternalLink className="w-4 h-4 text-slate-500" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <ImageIcon className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
            <p className="text-slate-500 dark:text-slate-400 text-center">
              No hay visualizaciones disponibles
            </p>
            <p className="text-sm text-slate-400 dark:text-slate-500 text-center mt-1">
              Ejecuta el pipeline para generar gráficos
            </p>
          </div>
        )}

        {/* Chart Modal */}
        {selectedChart && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedChart(null)}
          >
            <div
              className="bg-white dark:bg-slate-800 rounded-xl max-w-4xl max-h-[90vh] overflow-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={`file://${selectedChart}`}
                alt="Chart"
                className="w-full h-auto"
              />
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
}

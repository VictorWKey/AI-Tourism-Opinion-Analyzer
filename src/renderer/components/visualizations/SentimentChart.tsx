/**
 * SentimentChart Component
 * =========================
 * Interactive pie/donut chart for sentiment distribution using Recharts
 */

import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface SentimentData {
  name: string;
  value: number;
  count?: number;
}

interface SentimentChartProps {
  data: SentimentData[];
  title?: string;
  showLegend?: boolean;
  innerRadius?: number;
  outerRadius?: number;
}

const COLORS: Record<string, string> = {
  Positivo: '#22c55e',  // green-500
  Neutro: '#64748b',    // slate-500
  Negativo: '#ef4444',  // red-500
  positive: '#22c55e',
  neutral: '#64748b',
  negative: '#ef4444',
};

const DEFAULT_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'];

export function SentimentChart({
  data,
  title,
  showLegend = true,
  innerRadius = 60,
  outerRadius = 100,
}: SentimentChartProps) {
  // Custom tooltip
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number; payload: SentimentData }> }) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      const percentage = ((item.value / data.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(1);
      return (
        <div className="bg-white dark:bg-slate-800 px-3 py-2 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="font-medium text-slate-700 dark:text-slate-200">{item.name}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {item.payload.count ?? item.value} opiniones ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom label - properly typed for Recharts
  const renderLabel = ({ name, percent }: { name?: string; percent?: number }) => {
    if (!name || !percent || percent < 0.05) return ''; // Don't show labels for small slices
    return `${name}: ${(percent * 100).toFixed(1)}%`;
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
        <p className="text-slate-400 dark:text-slate-500">No hay datos de sentimiento disponibles</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-4 text-center">
          {title}
        </h3>
      )}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={innerRadius}
              outerRadius={outerRadius}
              paddingAngle={2}
              dataKey="value"
              label={renderLabel}
              labelLine={{ stroke: '#94a3b8', strokeWidth: 1 }}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[entry.name] || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  className="transition-opacity hover:opacity-80"
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            {showLegend && (
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value: string) => (
                  <span className="text-slate-600 dark:text-slate-300">{value}</span>
                )}
              />
            )}
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default SentimentChart;

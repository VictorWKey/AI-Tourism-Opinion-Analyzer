/**
 * CategoryChart Component
 * ========================
 * Interactive bar chart for category distribution using Recharts
 */

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface CategoryData {
  name: string;
  value: number;
  count?: number;
}

interface CategoryChartProps {
  data: CategoryData[];
  title?: string;
  color?: string;
  horizontal?: boolean;
}

const CATEGORY_COLORS = [
  '#3b82f6', // blue-500
  '#22c55e', // green-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#06b6d4', // cyan-500
  '#f97316', // orange-500
  '#14b8a6', // teal-500
  '#6366f1', // indigo-500
];

export function CategoryChart({
  data,
  title,
  color,
  horizontal = false,
}: CategoryChartProps) {
  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; payload: CategoryData }>; label?: string }) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      return (
        <div className="bg-white dark:bg-slate-800 px-3 py-2 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="font-medium text-slate-700 dark:text-slate-200">{label}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {item.payload.count ?? item.value} menciones
          </p>
        </div>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-background rounded-lg">
        <p className="text-muted-foreground">No hay datos de categorías disponibles</p>
      </div>
    );
  }

  // Sort by value descending
  const sortedData = [...data].sort((a, b) => b.value - a.value);

  if (horizontal) {
    return (
      <div className="w-full">
        {title && (
          <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-4 text-center">
            {title}
          </h3>
        )}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={sortedData}
              margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 12 }}
                width={90}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {sortedData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={color || CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
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
          <BarChart data={sortedData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#64748b', fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={80}
              interval={0}
            />
            <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {sortedData.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={color || CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default CategoryChart;

/**
 * TopicChart Component
 * =====================
 * Interactive treemap/bar chart for topic distribution using Recharts
 */

import React from 'react';
import {
  Treemap,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface TopicData {
  name: string;
  value: number;
  count?: number;
  [key: string]: unknown;
}

interface TopicChartProps {
  data: TopicData[];
  title?: string;
}

const TOPIC_COLORS = [
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
  '#84cc16', // lime-500
  '#a855f7', // purple-500
];

// Custom content renderer for treemap cells
interface CustomContentProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  index?: number;
  name?: string;
  value?: number;
  depth?: number;
}

const CustomContent: React.FC<CustomContentProps> = ({
  x = 0,
  y = 0,
  width = 0,
  height = 0,
  index = 0,
  name,
  value,
  depth,
}) => {
  // Only render leaf nodes
  if (depth !== 1) return null;

  const color = TOPIC_COLORS[index % TOPIC_COLORS.length];
  const showText = width > 50 && height > 30;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={color}
        stroke="#fff"
        strokeWidth={2}
        rx={4}
        ry={4}
        className="transition-opacity hover:opacity-80"
      />
      {showText && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2 - 6}
            fill="#fff"
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={Math.min(14, width / 8)}
            fontWeight="500"
          >
            {name && name.length > 15 ? `${name.substring(0, 15)}...` : name}
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2 + 10}
            fill="rgba(255,255,255,0.8)"
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={Math.min(12, width / 10)}
          >
            {value}
          </text>
        </>
      )}
    </g>
  );
};

export function TopicChart({ data, title }: TopicChartProps) {
  // Custom tooltip
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: TopicData }> }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white dark:bg-slate-800 px-3 py-2 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="font-medium text-slate-700 dark:text-slate-200">{item.name}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {item.count ?? item.value} opiniones
          </p>
        </div>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 bg-background rounded-lg">
        <p className="text-muted-foreground">No hay datos de temas disponibles</p>
      </div>
    );
  }

  // Transform data for treemap
  const treemapData = {
    name: 'Topics',
    children: data.map((item, index) => ({
      ...item,
      size: item.value,
      index,
    })),
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-4 text-center">
          {title}
        </h3>
      )}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={treemapData.children}
            dataKey="size"
            aspectRatio={4 / 3}
            stroke="#fff"
            content={<CustomContent />}
          >
            <Tooltip content={<CustomTooltip />} />
          </Treemap>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default TopicChart;

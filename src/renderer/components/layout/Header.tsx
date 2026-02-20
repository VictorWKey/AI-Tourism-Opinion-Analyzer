/**
 * Header Component
 * =================
 * Page header with title and optional actions
 */

import React from 'react';
import { cn } from '../../lib/utils';

interface HeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}

export function Header({ title, description, children, className }: HeaderProps) {
  return (
    <header
      className={cn(
        'flex items-center justify-between px-6 h-20 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800',
        className
      )}
    >
      <div>
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {description}
          </p>
        )}
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </header>
  );
}

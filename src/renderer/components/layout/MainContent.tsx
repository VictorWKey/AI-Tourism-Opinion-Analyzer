/**
 * MainContent Component
 * ======================
 * Main content wrapper with consistent padding
 */

import React from 'react';
import { cn } from '../../lib/utils';

interface MainContentProps {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export function MainContent({ children, className, noPadding = false }: MainContentProps) {
  return (
    <div
      className={cn(
        'flex-1 overflow-auto bg-slate-50 dark:bg-slate-900',
        !noPadding && 'p-6',
        className
      )}
    >
      {children}
    </div>
  );
}

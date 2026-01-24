/**
 * PageLayout Component
 * =====================
 * Combines Header and MainContent for consistent page layouts
 */

import React from 'react';
import { Header } from './Header';
import { MainContent } from './MainContent';

interface PageLayoutProps {
  title: string;
  description?: string;
  headerActions?: React.ReactNode;
  children: React.ReactNode;
  noPadding?: boolean;
}

export function PageLayout({
  title,
  description,
  headerActions,
  children,
  noPadding = false,
}: PageLayoutProps) {
  return (
    <div className="flex flex-col h-full">
      <Header title={title} description={description}>
        {headerActions}
      </Header>
      <MainContent noPadding={noPadding}>{children}</MainContent>
    </div>
  );
}

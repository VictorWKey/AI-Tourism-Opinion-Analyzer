/**
 * MarkdownRenderer
 * =================
 * A shared component for rendering LLM-generated Markdown content
 * with beautiful, well-spaced typography and visual polish.
 *
 * Uses react-markdown + @tailwindcss/typography with custom overrides
 * for a premium report-like reading experience.
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { cn } from '../../lib/utils';

export interface MarkdownRendererProps {
  /** The raw markdown string to render */
  content: string;
  /** Additional CSS classes */
  className?: string;
  /** Size variant — 'default' for summaries, 'lg' for full-page reports */
  size?: 'default' | 'lg';
}

export function MarkdownRenderer({
  content,
  className,
  size = 'default',
}: MarkdownRendererProps) {
  return (
    <div
      className={cn(
        'llm-markdown-content',
        /* Base prose from @tailwindcss/typography */
        'prose dark:prose-invert max-w-none',
        /* Size variant */
        size === 'lg' ? 'prose-base' : 'prose-sm',
        /* Headings */
        'prose-headings:font-semibold prose-headings:tracking-tight',
        'prose-headings:text-slate-900 dark:prose-headings:text-slate-50',
        /* H2 — major sections */
        'prose-h2:text-lg prose-h2:border-b prose-h2:border-slate-200 dark:prose-h2:border-slate-700 prose-h2:pb-2 prose-h2:mt-8 prose-h2:mb-4',
        /* H3 — subsections */
        'prose-h3:text-base prose-h3:mt-6 prose-h3:mb-3',
        /* Paragraphs */
        'prose-p:text-slate-600 dark:prose-p:text-slate-300',
        'prose-p:leading-relaxed',
        /* Lists */
        'prose-li:text-slate-600 dark:prose-li:text-slate-300',
        'prose-ul:my-3 prose-ol:my-3',
        'prose-li:my-1',
        /* Strong / emphasis */
        'prose-strong:text-slate-800 dark:prose-strong:text-slate-100 prose-strong:font-semibold',
        'prose-em:text-slate-500 dark:prose-em:text-slate-400',
        /* Horizontal rules — section dividers */
        'prose-hr:my-8 prose-hr:border-slate-200 dark:prose-hr:border-slate-700',
        /* Blockquotes */
        'prose-blockquote:border-l-blue-500 prose-blockquote:bg-blue-50/50 dark:prose-blockquote:bg-blue-950/20',
        'prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg',
        'prose-blockquote:text-slate-600 dark:prose-blockquote:text-slate-300',
        'prose-blockquote:not-italic',
        /* Code */
        'prose-code:text-blue-600 dark:prose-code:text-blue-400 prose-code:font-mono prose-code:text-xs',
        className
      )}
    >
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;

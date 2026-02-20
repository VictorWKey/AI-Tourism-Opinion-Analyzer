import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PhaseCard } from '../renderer/components/pipeline/PhaseCard';
import type { PipelineProgress } from '../renderer/stores/pipelineStore';

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => {
      if (key === 'phaseCard.label' && opts) return `Phase ${opts.phase}`;
      if (key === 'phaseCard.progress') return `${opts?.percent ?? 0}%`;
      if (key === 'phaseCard.run') return 'Run';
      if (key === 'phaseCard.running') return 'Running...';
      if (key === 'phaseCard.completed') return 'Completed';
      if (key === 'phaseCard.failed') return 'Failed';
      return key;
    },
  }),
}));

// Mock framer-motion to render children without animation
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => {
      // Filter out framer-motion specific props
      const htmlProps: Record<string, unknown> = {};
      for (const [key, val] of Object.entries(props)) {
        if (!['initial', 'animate', 'exit', 'transition', 'whileHover', 'whileTap', 'layout'].includes(key)) {
          htmlProps[key] = val;
        }
      }
      return <div {...htmlProps}>{children}</div>;
    },
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

function makePhase(overrides: Partial<PipelineProgress> = {}): PipelineProgress {
  return {
    phase: 1,
    status: 'pending',
    progress: 0,
    message: '',
    error: undefined,
    ...overrides,
  };
}

describe('PhaseCard', () => {
  const defaultProps = {
    phase: makePhase(),
    onRun: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with phase number and pending status', () => {
    render(<PhaseCard {...defaultProps} />);
    expect(screen.getByText('Phase 1')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<PhaseCard {...defaultProps} description="Analyze text data" />);
    expect(screen.getByText('Analyze text data')).toBeInTheDocument();
  });

  it('shows run button when hasDataset is true', () => {
    render(<PhaseCard {...defaultProps} hasDataset={true} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('hides run button when hasDataset is false', () => {
    render(<PhaseCard {...defaultProps} hasDataset={false} />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('calls onRun when run button is clicked', () => {
    const onRun = vi.fn();
    render(<PhaseCard {...defaultProps} onRun={onRun} hasDataset={true} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onRun).toHaveBeenCalledOnce();
  });

  it('disables run button when disabled prop is true', () => {
    render(<PhaseCard {...defaultProps} disabled={true} hasDataset={true} />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('disables run button when enabled is false', () => {
    const onToggle = vi.fn();
    render(
      <PhaseCard {...defaultProps} enabled={false} onToggle={onToggle} hasDataset={true} />
    );
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('shows progress bar when status is running', () => {
    const phase = makePhase({ status: 'running', progress: 45 });
    render(<PhaseCard phase={phase} onRun={vi.fn()} />);
    expect(screen.getByText('45%')).toBeInTheDocument();
  });

  it('shows error message when phase has error', () => {
    const phase = makePhase({ status: 'failed', error: 'Something went wrong' });
    render(<PhaseCard phase={phase} onRun={vi.fn()} />);
    expect(screen.getByText(/Something went wrong/)).toBeInTheDocument();
  });

  it('renders checkbox when onToggle is provided and hasDataset is true', () => {
    const onToggle = vi.fn();
    render(
      <PhaseCard {...defaultProps} onToggle={onToggle} hasDataset={true} />
    );
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  it('does not render checkbox when hasDataset is false', () => {
    const onToggle = vi.fn();
    render(
      <PhaseCard {...defaultProps} onToggle={onToggle} hasDataset={false} />
    );
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', () => {
    const onToggle = vi.fn();
    render(
      <PhaseCard {...defaultProps} onToggle={onToggle} enabled={true} hasDataset={true} />
    );
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onToggle).toHaveBeenCalledWith(false);
  });

  it('disables run button when phase is running', () => {
    const phase = makePhase({ status: 'running', progress: 50 });
    render(<PhaseCard phase={phase} onRun={vi.fn()} hasDataset={true} />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('allows running a completed phase again', () => {
    const onRun = vi.fn();
    const phase = makePhase({ status: 'completed', progress: 100 });
    render(<PhaseCard phase={phase} onRun={onRun} hasDataset={true} />);
    expect(screen.getByRole('button')).not.toBeDisabled();
  });
});

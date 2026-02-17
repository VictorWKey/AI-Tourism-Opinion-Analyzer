/**
 * Phase 7 Configuration Dialog
 * ==============================
 * Allows users to select which summary types to generate in Phase 7.
 * This optimizes execution time by skipping unneeded summary types.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, X, CheckCircle2, Info, Type, List, Lightbulb } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '../ui';
import { cn } from '../../lib/utils';
import type { Phase7SummaryType } from '../../stores/pipelineStore';

interface Phase7ConfigDialogProps {
  open: boolean;
  onClose: () => void;
  selectedTypes: Phase7SummaryType[];
  onSave: (types: Phase7SummaryType[]) => void;
}

const SUMMARY_TYPE_INFO: {
  id: Phase7SummaryType;
  labelKey: string;
  descriptionKey: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  {
    id: 'descriptivo',
    labelKey: 'phase7Config.types.descriptive',
    descriptionKey: 'phase7Config.types.descriptiveDesc',
    icon: Type,
  },
  {
    id: 'estructurado',
    labelKey: 'phase7Config.types.structured',
    descriptionKey: 'phase7Config.types.structuredDesc',
    icon: List,
  },
  {
    id: 'insights',
    labelKey: 'phase7Config.types.insights',
    descriptionKey: 'phase7Config.types.insightsDesc',
    icon: Lightbulb,
  },
];

export function Phase7ConfigDialog({
  open,
  onClose,
  selectedTypes,
  onSave,
}: Phase7ConfigDialogProps) {
  const { t } = useTranslation('components');
  const [localTypes, setLocalTypes] = useState<Phase7SummaryType[]>(selectedTypes);

  // Sync local state when prop changes
  useEffect(() => {
    setLocalTypes(selectedTypes);
  }, [selectedTypes]);

  const toggleType = (type: Phase7SummaryType) => {
    setLocalTypes((prev) => {
      if (prev.includes(type)) {
        // Don't allow removing the last type
        if (prev.length <= 1) return prev;
        return prev.filter((t) => t !== type);
      }
      return [...prev, type];
    });
  };

  const handleSave = () => {
    onSave(localTypes);
    onClose();
  };

  const handleSelectAll = () => {
    setLocalTypes(['descriptivo', 'estructurado', 'insights']);
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ type: 'spring', duration: 0.3, bounce: 0.2 }}
            className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200 dark:border-slate-700"
          >
            {/* Header */}
            <div className="px-6 py-4 flex items-center gap-3 border-b bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800">
              <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-800/40">
                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg text-blue-900 dark:text-blue-200">
                  {t('phase7Config.title')}
                </h3>
                <p className="text-xs text-blue-700 dark:text-blue-400">
                  {t('phase7Config.subtitle')}
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                <X className="w-5 h-5 text-slate-500 dark:text-slate-400" />
              </button>
            </div>

            {/* Content */}
            <div className="px-6 py-5">
              <p className="text-sm text-slate-700 dark:text-slate-300 mb-4">
                {t('phase7Config.description')}
              </p>

              {/* Summary type toggles */}
              <div className="space-y-3">
                {SUMMARY_TYPE_INFO.map((type) => {
                  const isSelected = localTypes.includes(type.id);
                  const isLastSelected = isSelected && localTypes.length <= 1;
                  return (
                    <button
                      key={type.id}
                      onClick={() => toggleType(type.id)}
                      disabled={isLastSelected}
                      className={cn(
                        'w-full text-left px-4 py-3 rounded-lg border-2 transition-all',
                        isSelected
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600',
                        isLastSelected && 'cursor-not-allowed'
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-5 h-5 shrink-0 text-slate-600 dark:text-slate-400">
                          {React.createElement(type.icon, { className: 'w-5 h-5' })}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-slate-900 dark:text-slate-100">
                              {t(type.labelKey)}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {t(type.descriptionKey)}
                          </p>
                        </div>
                        <div
                          className={cn(
                            'w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0',
                            isSelected
                              ? 'border-blue-500 bg-blue-500'
                              : 'border-slate-300 dark:border-slate-600'
                          )}
                        >
                          {isSelected && <CheckCircle2 className="w-3 h-3 text-white" />}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Info tip */}
              <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex gap-2">
                <Info className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <p className="text-xs text-amber-800 dark:text-amber-200">
                  {t('phase7Config.performance')}
                </p>
              </div>

              {/* Summary count */}
              <div className="mt-3 text-center">
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {t('phase7Config.typesSelected', { count: localTypes.length })}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700 flex justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
                disabled={localTypes.length === 3}
              >
                {t('phase7Config.selectAll')}
              </Button>
              <div className="flex gap-3">
                <Button variant="outline" onClick={onClose}>
                  {t('phase7Config.cancel')}
                </Button>
                <Button onClick={handleSave} disabled={localTypes.length === 0}>
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  {t('phase7Config.save')}
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Inline summary type selector for Settings page
 */
export function Phase7SummaryTypeSelector({
  selectedTypes,
  onChange,
}: {
  selectedTypes: Phase7SummaryType[];
  onChange: (types: Phase7SummaryType[]) => void;
}) {
  const { t } = useTranslation('components');
  const toggleType = (type: Phase7SummaryType) => {
    if (selectedTypes.includes(type)) {
      if (selectedTypes.length <= 1) return;
      onChange(selectedTypes.filter((t) => t !== type));
    } else {
      onChange([...selectedTypes, type]);
    }
  };

  return (
    <div className="space-y-2">
      {SUMMARY_TYPE_INFO.map((type) => {
        const isSelected = selectedTypes.includes(type.id);
        const isLastSelected = isSelected && selectedTypes.length <= 1;
        return (
          <label
            key={type.id}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-lg border-2 transition-all cursor-pointer',
              isSelected
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600',
              isLastSelected && 'cursor-not-allowed'
            )}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => toggleType(type.id)}
              disabled={isLastSelected}
              className="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-600 focus:ring-blue-500"
            />
            <div className="w-5 h-5 shrink-0 text-slate-600 dark:text-slate-400">
              {React.createElement(type.icon, { className: 'w-5 h-5' })}
            </div>
            <div className="flex-1 min-w-0">
              <span className="font-medium text-sm text-slate-900 dark:text-slate-100">
                {t(type.labelKey)}
              </span>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {t(type.descriptionKey)}
              </p>
            </div>
          </label>
        );
      })}
      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
        {t('phase7Config.inlineStatus', { count: selectedTypes.length })}
      </p>
    </div>
  );
}

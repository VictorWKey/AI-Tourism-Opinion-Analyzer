/**
 * useToast Hook
 * ==============
 * Simple toast notification hook using Zustand
 */

import { create } from 'zustand';

export interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'success' | 'destructive' | 'warning';
  duration?: number;
}

interface ToastState {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  
  addToast: (toast) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast: Toast = { id, ...toast };
    
    set((state) => ({
      toasts: [...state.toasts, newToast],
    }));
    
    // Auto-remove after duration (default 5 seconds)
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        }));
      }, duration);
    }
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },
  
  clearToasts: () => {
    set({ toasts: [] });
  },
}));

export function useToast() {
  const { toasts, addToast, removeToast, clearToasts } = useToastStore();
  
  return {
    toasts,
    toast: addToast,
    dismiss: removeToast,
    clear: clearToasts,
    
    // Convenience methods
    success: (title: string, description?: string) => {
      addToast({ title, description, variant: 'success' });
    },
    error: (title: string, description?: string) => {
      addToast({ title, description, variant: 'destructive', duration: 8000 });
    },
    warning: (title: string, description?: string) => {
      addToast({ title, description, variant: 'warning' });
    },
    info: (title: string, description?: string) => {
      addToast({ title, description, variant: 'default' });
    },
  };
}

/**
 * Electron Storage Adapter for Zustand Persist
 * ==============================================
 * Uses electron-store (via IPC) instead of localStorage.
 *
 * In production Electron builds, the renderer loads from file:// protocol,
 * and localStorage tied to file:// origins can be unreliable across sessions
 * (Chromium treats each file:// page as a unique opaque origin).
 *
 * This adapter delegates persistence to electron-store in the main process,
 * which writes to a JSON file in the app's userData directory and always
 * survives application restarts.
 */

import type { StateStorage } from 'zustand/middleware';

export const electronStorage: StateStorage = {
  getItem: async (name: string): Promise<string | null> => {
    try {
      return await window.electronAPI.store.getItem(name);
    } catch (err) {
      console.warn('[electronStorage] getItem failed, falling back to localStorage:', err);
      return localStorage.getItem(name);
    }
  },

  setItem: async (name: string, value: string): Promise<void> => {
    try {
      await window.electronAPI.store.setItem(name, value);
    } catch (err) {
      console.warn('[electronStorage] setItem failed, falling back to localStorage:', err);
      localStorage.setItem(name, value);
    }
  },

  removeItem: async (name: string): Promise<void> => {
    try {
      await window.electronAPI.store.removeItem(name);
    } catch (err) {
      console.warn('[electronStorage] removeItem failed, falling back to localStorage:', err);
      localStorage.removeItem(name);
    }
  },
};

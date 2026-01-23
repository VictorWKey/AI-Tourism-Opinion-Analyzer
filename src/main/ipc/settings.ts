// ============================================
// Settings IPC Handlers
// ============================================

import { ipcMain } from 'electron';
import { getStore } from '../utils/store';

export function registerSettingsHandlers(): void {
  // Get a specific setting
  ipcMain.handle('settings:get', (_, key: string) => {
    const store = getStore();
    return store.get(key);
  });

  // Set a specific setting
  ipcMain.handle('settings:set', (_, key: string, value: unknown) => {
    try {
      const store = getStore();
      store.set(key, value);
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Get all settings
  ipcMain.handle('settings:get-all', () => {
    const store = getStore();
    return store.store;
  });

  // Reset settings to defaults
  ipcMain.handle('settings:reset', () => {
    try {
      const store = getStore();
      store.clear();
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Delete a specific setting
  ipcMain.handle('settings:delete', (_, key: string) => {
    try {
      const store = getStore();
      store.delete(key);
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[IPC] Settings handlers registered');
}

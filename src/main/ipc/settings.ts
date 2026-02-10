// ============================================
// Settings IPC Handlers
// ============================================

import { ipcMain } from 'electron';
import { getStore } from '../utils/store';
import { getPythonBridge } from '../python/bridge';

/**
 * Deep-compare two values to check if they are equivalent.
 * Used to avoid unnecessary Python bridge restarts when settings haven't actually changed.
 * Treats undefined values as non-existent keys (matches JSON serialization behavior).
 */
function deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  // Treat undefined and missing the same way (JSON serialization drops undefined)
  if (a === undefined && b === undefined) return true;
  if (a == null || b == null) return a == b;
  if (typeof a !== typeof b) return false;
  if (typeof a !== 'object') return false;
  const objA = a as Record<string, unknown>;
  const objB = b as Record<string, unknown>;
  // Filter out undefined values to match JSON serialization behavior
  const keysA = Object.keys(objA).filter(k => objA[k] !== undefined);
  const keysB = Object.keys(objB).filter(k => objB[k] !== undefined);
  if (keysA.length !== keysB.length) return false;
  return keysA.every(key =>
    deepEqual(objA[key], objB[key])
  );
}

export function registerSettingsHandlers(): void {
  // Get a specific setting
  ipcMain.handle('settings:get', (_, key: string) => {
    const store = getStore();
    return store.get(key);
  });

  // Set a specific setting
  ipcMain.handle('settings:set', async (_, key: string, value: unknown) => {
    try {
      const store = getStore();
      
      // If LLM settings changed, only restart Python bridge if values actually differ
      if (key.startsWith('llm.') || key === 'llm') {
        const currentValue = store.get(key);
        store.set(key, value);
        
        if (!deepEqual(currentValue, value)) {
          console.log('[Settings] LLM config changed, restarting Python bridge...');
          try {
            const bridge = getPythonBridge();
            await bridge.restart();
          } catch (err) {
            console.error('[Settings] Failed to restart Python bridge:', err);
          }
        }
      } else if (key === 'app' || key === 'app.outputDir') {
        const currentValue = store.get(key);
        store.set(key, value);
        
        // Check if outputDir changed specifically
        const oldOutputDir = key === 'app' 
          ? (currentValue as Record<string, unknown>)?.outputDir 
          : currentValue;
        const newOutputDir = key === 'app'
          ? (value as Record<string, unknown>)?.outputDir
          : value;
        
        if (oldOutputDir !== newOutputDir) {
          console.log('[Settings] Output directory changed, restarting Python bridge...');
          try {
            const bridge = getPythonBridge();
            await bridge.restart();
          } catch (err) {
            console.error('[Settings] Failed to restart Python bridge:', err);
          }
        }
      } else {
        store.set(key, value);
      }
      
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

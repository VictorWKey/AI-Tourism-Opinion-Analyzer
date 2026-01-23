// ============================================
// IPC Handlers Registry
// ============================================

import { registerPipelineHandlers } from './pipeline';
import { registerFileHandlers } from './files';
import { registerSettingsHandlers } from './settings';
import { registerOllamaHandlers } from './ollama';
import { registerAppHandlers } from './app';

/**
 * Register all IPC handlers for main process communication
 */
export function registerIpcHandlers(): void {
  registerPipelineHandlers();
  registerFileHandlers();
  registerSettingsHandlers();
  registerOllamaHandlers();
  registerAppHandlers();
  
  console.log('[IPC] All handlers registered successfully');
}

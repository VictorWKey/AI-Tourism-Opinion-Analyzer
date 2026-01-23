// ============================================
// IPC Handlers Registry
// ============================================

import { registerPipelineHandlers } from './pipeline';
import { registerFileHandlers } from './files';
import { registerSettingsHandlers } from './settings';
import { registerOllamaHandlers } from './ollama';
import { registerAppHandlers } from './app';
import { registerSetupHandlers } from './setup';

/**
 * Register all IPC handlers for main process communication
 */
export function registerIpcHandlers(): void {
  registerPipelineHandlers();
  registerFileHandlers();
  registerSettingsHandlers();
  registerOllamaHandlers();
  registerAppHandlers();
  registerSetupHandlers();
  
  console.log('[IPC] All handlers registered successfully');
}

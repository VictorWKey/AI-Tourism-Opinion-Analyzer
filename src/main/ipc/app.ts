// ============================================
// App IPC Handlers
// ============================================

import { ipcMain, app } from 'electron';

export function registerAppHandlers(): void {
  // Get app version
  ipcMain.handle('app:get-version', () => {
    return app.getVersion();
  });

  // Get app name
  ipcMain.handle('app:get-name', () => {
    return app.getName();
  });

  // Get app path
  ipcMain.handle('app:get-path', (_, name: string) => {
    try {
      return app.getPath(name as Parameters<typeof app.getPath>[0]);
    } catch (error) {
      return null;
    }
  });

  // Get system info
  ipcMain.handle('app:get-system-info', () => {
    return {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      electronVersion: process.versions.electron,
      chromeVersion: process.versions.chrome,
    };
  });

  console.log('[IPC] App handlers registered');
}

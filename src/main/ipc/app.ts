// ============================================
// App IPC Handlers
// ============================================

import { ipcMain, app } from 'electron';
import path from 'path';

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

  // Get Python data directory (where visualizations are saved)
  ipcMain.handle('app:get-python-data-dir', () => {
    // In development, Python runs from the project's python/ directory
    // In production, it runs from the resources/python/ directory
    const isPackaged = app.isPackaged;
    
    if (isPackaged) {
      return path.join(process.resourcesPath, 'python', 'data');
    } else {
      return path.join(app.getAppPath(), 'python', 'data');
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

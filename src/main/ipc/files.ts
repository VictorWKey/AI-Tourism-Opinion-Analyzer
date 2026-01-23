// ============================================
// File Operations IPC Handlers
// ============================================

import { ipcMain, dialog, shell } from 'electron';
import fs from 'fs/promises';
import path from 'path';

interface FileFilter {
  name: string;
  extensions: string[];
}

interface FileReadResult {
  success: boolean;
  content?: string;
  error?: string;
}

interface FileWriteResult {
  success: boolean;
  error?: string;
}

interface OpenPathResult {
  success: boolean;
  error?: string;
}

export function registerFileHandlers(): void {
  // Select file dialog
  ipcMain.handle('files:select', async (_, filters?: FileFilter[]) => {
    const result = await dialog.showOpenDialog({
      properties: ['openFile'],
      filters: filters || [
        { name: 'CSV Files', extensions: ['csv'] },
        { name: 'All Files', extensions: ['*'] },
      ],
    });

    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }

    return result.filePaths[0];
  });

  // Select directory dialog
  ipcMain.handle('files:select-directory', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory', 'createDirectory'],
    });

    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }

    return result.filePaths[0];
  });

  // Read file contents
  ipcMain.handle('files:read', async (_, filePath: string): Promise<FileReadResult> => {
    try {
      // Validate path
      if (!filePath || typeof filePath !== 'string') {
        return { success: false, error: 'Invalid file path' };
      }

      const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
      const content = await fs.readFile(absolutePath, 'utf-8');
      return { success: true, content };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Write file contents
  ipcMain.handle(
    'files:write',
    async (_, filePath: string, content: string): Promise<FileWriteResult> => {
      try {
        // Validate inputs
        if (!filePath || typeof filePath !== 'string') {
          return { success: false, error: 'Invalid file path' };
        }
        if (typeof content !== 'string') {
          return { success: false, error: 'Content must be a string' };
        }

        const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
        
        // Ensure directory exists
        const dir = path.dirname(absolutePath);
        await fs.mkdir(dir, { recursive: true });
        
        await fs.writeFile(absolutePath, content, 'utf-8');
        return { success: true };
      } catch (error) {
        return { success: false, error: (error as Error).message };
      }
    }
  );

  // Open path in system file explorer or application
  ipcMain.handle('files:open-path', async (_, filePath: string): Promise<OpenPathResult> => {
    try {
      if (!filePath || typeof filePath !== 'string') {
        return { success: false, error: 'Invalid file path' };
      }

      const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
      const errorMessage = await shell.openPath(absolutePath);
      
      if (errorMessage) {
        return { success: false, error: errorMessage };
      }
      
      return { success: true };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  // Check if file exists
  ipcMain.handle('files:exists', async (_, filePath: string): Promise<boolean> => {
    try {
      const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
      await fs.access(absolutePath);
      return true;
    } catch {
      return false;
    }
  });

  // Get file info (stats)
  ipcMain.handle('files:stat', async (_, filePath: string) => {
    try {
      const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
      const stats = await fs.stat(absolutePath);
      return {
        success: true,
        stats: {
          size: stats.size,
          isFile: stats.isFile(),
          isDirectory: stats.isDirectory(),
          created: stats.birthtime.toISOString(),
          modified: stats.mtime.toISOString(),
        },
      };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[IPC] File handlers registered');
}

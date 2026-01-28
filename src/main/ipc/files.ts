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

  // List images in a directory (for visualizations)
  ipcMain.handle('files:list-images', async (_, dirPath: string) => {
    try {
      const absolutePath = path.isAbsolute(dirPath) ? dirPath : path.resolve(dirPath);

      // Check if directory exists
      try {
        await fs.access(absolutePath);
      } catch {
        return { success: false, error: 'Directory does not exist', images: [] };
      }

      const images: Array<{
        id: string;
        name: string;
        path: string;
        category: string;
        categoryLabel: string;
      }> = [];

      // Category mapping
      const categoryLabels: Record<string, string> = {
        '01_dashboard': 'Dashboard',
        '02_sentimientos': 'Sentimientos',
        '03_categorias': 'Categorías',
        '04_topicos': 'Tópicos',
        '05_temporal': 'Temporal',
        '06_texto': 'Texto',
        '07_combinados': 'Combinados',
      };

      // Scan subdirectories for images
      const subdirs = await fs.readdir(absolutePath, { withFileTypes: true });

      for (const subdir of subdirs) {
        if (!subdir.isDirectory()) continue;

        const categoryPath = path.join(absolutePath, subdir.name);
        const files = await fs.readdir(categoryPath);

        for (const file of files) {
          const ext = path.extname(file).toLowerCase();
          if (['.png', '.jpg', '.jpeg', '.svg', '.webp'].includes(ext)) {
            const imagePath = path.join(categoryPath, file);
            images.push({
              id: `${subdir.name}-${file}`,
              name: file.replace(ext, '').replace(/_/g, ' '),
              path: imagePath,
              category: subdir.name,
              categoryLabel: categoryLabels[subdir.name] || subdir.name,
            });
          }
        }
      }

      // Also scan root directory for any loose images
      const rootFiles = await fs.readdir(absolutePath);
      for (const file of rootFiles) {
        const filePath = path.join(absolutePath, file);
        const stat = await fs.stat(filePath);
        if (stat.isFile()) {
          const ext = path.extname(file).toLowerCase();
          if (['.png', '.jpg', '.jpeg', '.svg', '.webp'].includes(ext)) {
            images.push({
              id: `root-${file}`,
              name: file.replace(ext, '').replace(/_/g, ' '),
              path: filePath,
              category: 'root',
              categoryLabel: 'General',
            });
          }
        }
      }

      return { success: true, images };
    } catch (error) {
      return { success: false, error: (error as Error).message, images: [] };
    }
  });

  // List directory contents
  ipcMain.handle('files:list-dir', async (_, dirPath: string) => {
    try {
      const absolutePath = path.isAbsolute(dirPath) ? dirPath : path.resolve(dirPath);
      const entries = await fs.readdir(absolutePath, { withFileTypes: true });
      
      const items = entries.map((entry) => ({
        name: entry.name,
        isDirectory: entry.isDirectory(),
        isFile: entry.isFile(),
        path: path.join(absolutePath, entry.name),
      }));

      return { success: true, items };
    } catch (error) {
      return { success: false, error: (error as Error).message, items: [] };
    }
  });

  console.log('[IPC] File handlers registered');
}

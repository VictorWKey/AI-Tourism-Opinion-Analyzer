// ============================================
// File Operations IPC Handlers
// ============================================

import { ipcMain, dialog, shell } from 'electron';
import fs from 'fs/promises';
import path from 'path';
import { spawn } from 'child_process';

// Helper function to open folder on Linux using various file managers
async function openFolderLinux(folderPath: string): Promise<string> {
  // Check if we're in WSL
  try {
    const fs = require('fs');
    const procVersion = fs.readFileSync('/proc/version', 'utf8').toLowerCase();
    
    if (procVersion.includes('microsoft') || procVersion.includes('wsl')) {
      console.log('[IPC] WSL detected, using explorer.exe');
      
      // In WSL, convert Linux path to Windows path using wslpath
      return new Promise<string>((resolve) => {
        const wslpathChild = spawn('wslpath', ['-w', folderPath]);
        let windowsPath = '';
        
        wslpathChild.stdout.on('data', (data) => {
          windowsPath += data.toString().trim();
        });
        
        wslpathChild.on('close', (code) => {
          if (code !== 0 || !windowsPath) {
            console.log('[IPC] wslpath failed, using WSL network path format');
            // Fallback: use \\wsl$ network path format
            windowsPath = `\\\\wsl$\\Ubuntu${folderPath}`;
          }
          
          console.log('[IPC] Opening Windows path:', windowsPath);
          
          const child = spawn('explorer.exe', [windowsPath], {
            detached: true,
            stdio: 'ignore',
          });
          
          child.on('error', (err) => {
            console.log('[IPC] explorer.exe error:', err.message);
            resolve(`explorer.exe failed: ${err.message}`);
          });
          
          child.on('spawn', () => {
            console.log('[IPC] explorer.exe spawned successfully');
            child.unref();
            resolve('');
          });
          
          // Timeout after 3 seconds
          setTimeout(() => resolve('explorer.exe timeout'), 3000);
        });
      });
    }
  } catch (e) {
    console.log('[IPC] Error checking for WSL:', e);
  }
  
  // List of file managers to try in order of preference
  const fileManagers = [
    { cmd: 'gio', args: ['open', folderPath] },                // GNOME (most common)
    { cmd: 'nautilus', args: ['--new-window', folderPath] },   // GNOME Files
    { cmd: 'dolphin', args: ['--new-window', folderPath] },    // KDE
    { cmd: 'thunar', args: [folderPath] },                     // XFCE
    { cmd: 'nemo', args: [folderPath] },                       // Cinnamon
    { cmd: 'pcmanfm', args: [folderPath] },                    // LXDE
    { cmd: 'caja', args: [folderPath] },                       // MATE
    { cmd: 'xdg-open', args: [folderPath] },                   // Fallback
  ];

  for (const fm of fileManagers) {
    try {
      console.log(`[IPC] Trying file manager: ${fm.cmd} ${fm.args.join(' ')}`);
      const result = await new Promise<string>((resolve) => {
        const child = spawn(fm.cmd, fm.args, {
          detached: true,
          stdio: 'ignore',
        });
        
        child.on('error', (err) => {
          // Command not found, try next
          console.log(`[IPC] ${fm.cmd} error:`, err.message);
          resolve(`not_found: ${fm.cmd}`);
        });
        
        child.on('spawn', () => {
          // Successfully spawned
          console.log(`[IPC] ${fm.cmd} spawned successfully`);
          child.unref();
          resolve('');
        });
        
        // Timeout after 2 seconds
        setTimeout(() => resolve(`timeout: ${fm.cmd}`), 2000);
      });

      if (result === '') {
        console.log(`[IPC] Successfully opened folder with ${fm.cmd}`);
        return ''; // Success
      }
    } catch (e) {
      // Continue to next file manager
      console.log(`[IPC] Exception trying ${fm.cmd}:`, e);
    }
  }

  return 'No file manager found';
}

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
      console.log('[IPC] open-path called with:', filePath);
      
      if (!filePath || typeof filePath !== 'string') {
        console.log('[IPC] Invalid file path');
        return { success: false, error: 'Invalid file path' };
      }

      const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
      console.log('[IPC] Resolved absolute path:', absolutePath);
      
      // Check if path exists first
      try {
        await fs.access(absolutePath);
        console.log('[IPC] Path exists');
      } catch (accessError) {
        console.log('[IPC] Path does not exist:', accessError);
        return { success: false, error: `Path does not exist: ${absolutePath}` };
      }
      
      // On Linux, try our custom file manager opener
      if (process.platform === 'linux') {
        console.log('[IPC] Using Linux file manager fallback');
        const errorMessage = await openFolderLinux(absolutePath);
        if (errorMessage) {
          console.log('[IPC] Linux file manager error:', errorMessage);
          return { success: false, error: errorMessage };
        }
        return { success: true };
      }
      
      // On other platforms, use shell.openPath
      console.log('[IPC] Using shell.openPath');
      const errorMessage = await shell.openPath(absolutePath);
      console.log('[IPC] shell.openPath result:', errorMessage);
      
      if (errorMessage) {
        console.log('[IPC] Error from shell.openPath:', errorMessage);
        return { success: false, error: errorMessage };
      }
      
      console.log('[IPC] Successfully opened path');
      return { success: true };
    } catch (error) {
      console.error('[IPC] Exception in open-path handler:', error);
      return { success: false, error: error instanceof Error ? error.message : String(error) };
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
        '07_combinados': 'Análisis Cruzado',
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

  // Read image file as base64 data URL
  ipcMain.handle('files:read-image-base64', async (_, filePath: string) => {
    try {
      const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
      const buffer = await fs.readFile(absolutePath);
      const ext = path.extname(filePath).toLowerCase();
      
      // Determine MIME type
      const mimeTypes: Record<string, string> = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
      };
      
      const mimeType = mimeTypes[ext] || 'image/png';
      const base64 = buffer.toString('base64');
      const dataUrl = `data:${mimeType};base64,${base64}`;
      
      return { success: true, dataUrl };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('[IPC] File handlers registered');
}

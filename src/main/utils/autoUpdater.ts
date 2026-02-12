/**
 * AutoUpdater - Handles checking for and applying updates via GitHub Releases
 * 
 * Uses electron-updater with GitHub as the update provider.
 * Updates are checked on app startup (in production only) and can be
 * triggered manually from the renderer via IPC.
 * 
 * Flow:
 * 1. App starts → checks for update in background
 * 2. If update found → downloads it automatically
 * 3. Shows notification to user → "Restart to update"
 * 4. On next restart, Squirrel applies the update
 */

import { autoUpdater, UpdateCheckResult } from 'electron-updater';
import { app, BrowserWindow } from 'electron';
import log from '../utils/logger';

// Route electron-updater logs through our logger
autoUpdater.logger = log;

// Don't auto-download — let us control the flow
autoUpdater.autoDownload = false;
autoUpdater.autoInstallOnAppQuit = true;

export interface UpdateStatus {
  checking: boolean;
  available: boolean;
  downloaded: boolean;
  version?: string;
  error?: string;
}

let updateStatus: UpdateStatus = {
  checking: false,
  available: false,
  downloaded: false,
};

/**
 * Initialize auto-updater event listeners
 */
export function initAutoUpdater(mainWindow: BrowserWindow | null): void {
  if (!app.isPackaged) {
    log.info('[AutoUpdater] Skipping — app is not packaged (dev mode)');
    return;
  }

  autoUpdater.on('checking-for-update', () => {
    log.info('[AutoUpdater] Checking for updates...');
    updateStatus = { ...updateStatus, checking: true };
    mainWindow?.webContents.send('updater:status', updateStatus);
  });

  autoUpdater.on('update-available', (info) => {
    log.info(`[AutoUpdater] Update available: v${info.version}`);
    updateStatus = {
      checking: false,
      available: true,
      downloaded: false,
      version: info.version,
    };
    mainWindow?.webContents.send('updater:status', updateStatus);

    // Auto-download the update
    autoUpdater.downloadUpdate();
  });

  autoUpdater.on('update-not-available', () => {
    log.info('[AutoUpdater] App is up to date');
    updateStatus = { checking: false, available: false, downloaded: false };
    mainWindow?.webContents.send('updater:status', updateStatus);
  });

  autoUpdater.on('download-progress', (progress) => {
    log.info(`[AutoUpdater] Download: ${Math.round(progress.percent)}%`);
    mainWindow?.webContents.send('updater:download-progress', {
      percent: progress.percent,
      bytesPerSecond: progress.bytesPerSecond,
      transferred: progress.transferred,
      total: progress.total,
    });
  });

  autoUpdater.on('update-downloaded', (info) => {
    log.info(`[AutoUpdater] Update downloaded: v${info.version}`);
    updateStatus = {
      checking: false,
      available: true,
      downloaded: true,
      version: info.version,
    };
    mainWindow?.webContents.send('updater:status', updateStatus);
  });

  autoUpdater.on('error', (error) => {
    log.error('[AutoUpdater] Error:', error.message);
    updateStatus = {
      checking: false,
      available: false,
      downloaded: false,
      error: error.message,
    };
    mainWindow?.webContents.send('updater:status', updateStatus);
  });

  // Check for updates after a short delay (don't slow down startup)
  setTimeout(() => {
    checkForUpdates();
  }, 10_000);
}

/**
 * Manually check for updates
 */
export async function checkForUpdates(): Promise<UpdateCheckResult | null> {
  if (!app.isPackaged) return null;
  try {
    return await autoUpdater.checkForUpdates();
  } catch (error) {
    log.error('[AutoUpdater] Check failed:', error);
    return null;
  }
}

/**
 * Quit and install the downloaded update
 */
export function quitAndInstall(): void {
  autoUpdater.quitAndInstall();
}

/**
 * Get current update status
 */
export function getUpdateStatus(): UpdateStatus {
  return updateStatus;
}

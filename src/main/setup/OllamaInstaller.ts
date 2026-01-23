/**
 * OllamaInstaller - Cross-platform Ollama auto-installer
 * =======================================================
 * Handles automatic installation of Ollama on Windows, macOS, and Linux.
 * Includes progress tracking and model pulling functionality.
 */

import { spawn, exec } from 'child_process';
import { app, BrowserWindow } from 'electron';
import path from 'path';
import fs from 'fs';
import https from 'https';
import { promisify } from 'util';

const execAsync = promisify(exec);

type Platform = 'darwin' | 'win32' | 'linux';

export interface OllamaDownloadProgress {
  stage: 'downloading' | 'installing' | 'starting' | 'pulling-model' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
}

/**
 * OllamaInstaller class for cross-platform Ollama installation
 */
export class OllamaInstaller {
  private downloadUrls: Record<Platform, string> = {
    darwin: 'https://ollama.com/download/Ollama-darwin.zip',
    win32: 'https://ollama.com/download/OllamaSetup.exe',
    linux: '', // Uses install script
  };

  /**
   * Check if Ollama is installed
   */
  async isInstalled(): Promise<boolean> {
    return new Promise((resolve) => {
      exec('ollama --version', (error) => {
        resolve(!error);
      });
    });
  }

  /**
   * Check if Ollama service is running
   */
  async isRunning(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const response = await fetch('http://localhost:11434/api/tags', {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get installed Ollama version
   */
  async getVersion(): Promise<string | null> {
    try {
      const { stdout } = await execAsync('ollama --version');
      return stdout.trim();
    } catch {
      return null;
    }
  }

  /**
   * Install Ollama on the current platform
   */
  async install(onProgress: (p: OllamaDownloadProgress) => void): Promise<boolean> {
    const platform = process.platform as Platform;

    // Check if already installed
    if (await this.isInstalled()) {
      onProgress({ stage: 'complete', progress: 100, message: 'Ollama already installed' });
      return true;
    }

    try {
      if (platform === 'linux') {
        await this.installLinux(onProgress);
      } else if (platform === 'darwin') {
        await this.installMacOS(onProgress);
      } else if (platform === 'win32') {
        await this.installWindows(onProgress);
      } else {
        throw new Error(`Unsupported platform: ${platform}`);
      }

      // Start Ollama service
      onProgress({ stage: 'starting', progress: 90, message: 'Starting Ollama service...' });
      await this.startService();

      onProgress({ stage: 'complete', progress: 100, message: 'Ollama installed successfully' });
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onProgress({
        stage: 'error',
        progress: 0,
        message: 'Installation failed',
        error: errorMessage,
      });
      return false;
    }
  }

  /**
   * Install Ollama on Linux using the official install script
   */
  private async installLinux(onProgress: (p: OllamaDownloadProgress) => void): Promise<void> {
    return new Promise((resolve, reject) => {
      onProgress({ stage: 'installing', progress: 10, message: 'Running Ollama install script...' });

      const install = spawn('sh', ['-c', 'curl -fsSL https://ollama.com/install.sh | sh'], {
        stdio: 'pipe',
      });

      let progressValue = 10;

      install.stdout?.on('data', (data: Buffer) => {
        progressValue = Math.min(progressValue + 5, 75);
        onProgress({ 
          stage: 'installing', 
          progress: progressValue, 
          message: data.toString().trim() || 'Installing Ollama...' 
        });
      });

      install.stderr?.on('data', (data: Buffer) => {
        // Some output goes to stderr but isn't an error
        const text = data.toString().trim();
        if (text && !text.includes('error')) {
          onProgress({ stage: 'installing', progress: progressValue, message: text });
        }
      });

      install.on('close', (code) => {
        if (code === 0) {
          onProgress({ stage: 'installing', progress: 80, message: 'Installation complete' });
          resolve();
        } else {
          reject(new Error(`Install script failed with code ${code}`));
        }
      });

      install.on('error', reject);
    });
  }

  /**
   * Install Ollama on macOS
   */
  private async installMacOS(onProgress: (p: OllamaDownloadProgress) => void): Promise<void> {
    const tempDir = app.getPath('temp');
    const zipPath = path.join(tempDir, 'Ollama-darwin.zip');

    // Download
    onProgress({ stage: 'downloading', progress: 0, message: 'Downloading Ollama...' });
    await this.downloadFile(this.downloadUrls.darwin, zipPath, (percent) => {
      onProgress({
        stage: 'downloading',
        progress: Math.round(percent * 0.6),
        message: `Downloading... ${Math.round(percent)}%`,
      });
    });

    // Extract
    onProgress({ stage: 'installing', progress: 60, message: 'Extracting...' });
    await execAsync(`unzip -o "${zipPath}" -d /Applications`);

    // Cleanup
    try {
      fs.unlinkSync(zipPath);
    } catch {
      // Ignore cleanup errors
    }

    onProgress({ stage: 'installing', progress: 80, message: 'Ollama installed' });
  }

  /**
   * Install Ollama on Windows
   */
  private async installWindows(onProgress: (p: OllamaDownloadProgress) => void): Promise<void> {
    const tempDir = app.getPath('temp');
    const installerPath = path.join(tempDir, 'OllamaSetup.exe');

    // Download
    onProgress({ stage: 'downloading', progress: 0, message: 'Downloading Ollama...' });
    await this.downloadFile(this.downloadUrls.win32, installerPath, (percent) => {
      onProgress({
        stage: 'downloading',
        progress: Math.round(percent * 0.6),
        message: `Downloading... ${Math.round(percent)}%`,
      });
    });

    // Run installer silently
    onProgress({ stage: 'installing', progress: 60, message: 'Running installer...' });
    await execAsync(`"${installerPath}" /S`);

    // Cleanup
    try {
      fs.unlinkSync(installerPath);
    } catch {
      // Ignore cleanup errors
    }

    onProgress({ stage: 'installing', progress: 80, message: 'Ollama installed' });
  }

  /**
   * Pull (download) an Ollama model with progress tracking
   */
  async pullModel(
    modelName: string = 'llama3.2:3b',
    onProgress: (p: OllamaDownloadProgress) => void
  ): Promise<boolean> {
    try {
      // First ensure Ollama is running
      if (!(await this.isRunning())) {
        await this.startService();
      }

      onProgress({ stage: 'pulling-model', progress: 0, message: `Downloading ${modelName}...` });

      const response = await fetch('http://localhost:11434/api/pull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: modelName, stream: true }),
      });

      if (!response.ok) {
        throw new Error(`Failed to pull model: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const lines = decoder.decode(value).split('\n').filter(Boolean);
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.total && data.completed) {
              const progress = Math.round((data.completed / data.total) * 100);
              onProgress({
                stage: 'pulling-model',
                progress,
                message: `Downloading ${modelName}... ${progress}%`,
              });
            } else if (data.status) {
              onProgress({
                stage: 'pulling-model',
                progress: 50,
                message: data.status,
              });
            }
          } catch {
            // Ignore parse errors
          }
        }
      }

      onProgress({ stage: 'complete', progress: 100, message: `${modelName} ready!` });
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onProgress({
        stage: 'error',
        progress: 0,
        message: 'Failed to download model',
        error: errorMessage,
      });
      return false;
    }
  }

  /**
   * Check if a specific model is available
   */
  async hasModel(modelName: string): Promise<boolean> {
    try {
      if (!(await this.isRunning())) {
        return false;
      }

      const response = await fetch('http://localhost:11434/api/tags');
      if (!response.ok) return false;

      const data = await response.json();
      const models = data.models || [];
      return models.some((m: { name: string }) => 
        m.name === modelName || m.name.startsWith(modelName + ':')
      );
    } catch {
      return false;
    }
  }

  /**
   * List all installed Ollama models
   */
  async listModels(): Promise<Array<{ name: string; size: number; modified: string }>> {
    try {
      if (!(await this.isRunning())) {
        return [];
      }

      const response = await fetch('http://localhost:11434/api/tags');
      if (!response.ok) return [];

      const data = await response.json();
      return data.models || [];
    } catch {
      return [];
    }
  }

  /**
   * Start the Ollama service
   */
  async startService(): Promise<void> {
    // Check if already running
    if (await this.isRunning()) return;

    // Start Ollama in background
    const ollama = spawn('ollama', ['serve'], {
      detached: true,
      stdio: 'ignore',
    });
    ollama.unref();

    // Wait for it to be ready (max 30 seconds)
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      if (await this.isRunning()) return;
    }

    throw new Error('Ollama service failed to start');
  }

  /**
   * Stop the Ollama service
   */
  async stopService(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        await execAsync('taskkill /F /IM ollama.exe');
      } else {
        await execAsync('pkill -f "ollama serve"');
      }
    } catch {
      // Process might not exist, that's OK
    }
  }

  /**
   * Download a file with progress tracking
   */
  private downloadFile(
    url: string,
    dest: string,
    onProgress: (percent: number) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const file = fs.createWriteStream(dest);

      const request = (currentUrl: string): void => {
        https
          .get(currentUrl, (response) => {
            // Handle redirects
            if (response.statusCode === 302 || response.statusCode === 301) {
              const redirectUrl = response.headers.location;
              if (redirectUrl) {
                file.close();
                try {
                  fs.unlinkSync(dest);
                } catch {
                  // Ignore
                }
                request(redirectUrl);
                return;
              }
            }

            if (response.statusCode !== 200) {
              reject(new Error(`Download failed with status ${response.statusCode}`));
              return;
            }

            const totalSize = parseInt(response.headers['content-length'] || '0', 10);
            let downloadedSize = 0;

            response.on('data', (chunk: Buffer) => {
              downloadedSize += chunk.length;
              if (totalSize > 0) {
                onProgress((downloadedSize / totalSize) * 100);
              }
            });

            response.pipe(file);

            file.on('finish', () => {
              file.close();
              resolve();
            });
          })
          .on('error', (err) => {
            fs.unlink(dest, () => {});
            reject(err);
          });
      };

      request(url);
    });
  }
}

// Singleton instance
export const ollamaInstaller = new OllamaInstaller();

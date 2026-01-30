/**
 * OllamaInstaller - Cross-platform Ollama auto-installer
 * =======================================================
 * Handles automatic installation of Ollama on Windows, macOS, and Linux.
 * Includes progress tracking and model pulling functionality.
 */

import { spawn, exec } from 'child_process';
import { app } from 'electron';
import path from 'path';
import fs from 'fs';
import https from 'https';
import { promisify } from 'util';

const execAsync = promisify(exec);

type Platform = 'darwin' | 'win32' | 'linux';

export interface OllamaDownloadProgress {
  stage: 'idle' | 'downloading' | 'installing' | 'starting' | 'pulling-model' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
}

/**
 * OllamaInstaller class for cross-platform Ollama installation
 */
export class OllamaInstaller {
  // Download URLs only needed for macOS now (Windows uses winget, Linux uses install script)
  private downloadUrls: Record<Platform, string> = {
    darwin: 'https://ollama.com/download/Ollama-darwin.zip',
    win32: '', // Uses winget
    linux: '', // Uses install script
  };

  /**
   * Get the expected Ollama executable path on Windows
   */
  private getWindowsOllamaPath(): string {
    return path.join(
      process.env.LOCALAPPDATA || '',
      'Programs',
      'Ollama',
      'ollama.exe'
    );
  }

  /**
   * Check if Ollama is installed (Windows native only, not WSL)
   */
  async isInstalled(): Promise<boolean> {
    if (process.platform === 'win32') {
      // On Windows, check the standard installation location directly
      const ollamaPath = this.getWindowsOllamaPath();
      if (fs.existsSync(ollamaPath)) {
        return true;
      }
      
      // Fallback: check PATH but verify it's a Windows path
      return new Promise((resolve) => {
        exec('where ollama', (error, stdout) => {
          if (error) {
            resolve(false);
            return;
          }
          // Verify it's a Windows executable, not WSL
          const isWindowsPath = stdout.trim().toLowerCase().includes('\\') && 
                               !stdout.toLowerCase().includes('wsl');
          resolve(isWindowsPath);
        });
      });
    } else {
      // On Unix systems, use standard check
      return new Promise((resolve) => {
        exec('ollama --version', (error) => {
          resolve(!error);
        });
      });
    }
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
      if (process.platform === 'win32') {
        const ollamaPath = this.getWindowsOllamaPath();
        if (!fs.existsSync(ollamaPath)) {
          return null;
        }
        const { stdout } = await execAsync(`"${ollamaPath}" --version`);
        return stdout.trim();
      } else {
        const { stdout } = await execAsync('ollama --version');
        return stdout.trim();
      }
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
        // Start Ollama service for Linux
        onProgress({ stage: 'starting', progress: 90, message: 'Starting Ollama service...' });
        await this.startService();
      } else if (platform === 'darwin') {
        await this.installMacOS(onProgress);
        // Start Ollama service for macOS
        onProgress({ stage: 'starting', progress: 90, message: 'Starting Ollama service...' });
        await this.startService();
      } else if (platform === 'win32') {
        // Windows installation includes starting the service
        await this.installWindows(onProgress);
      } else {
        throw new Error(`Unsupported platform: ${platform}`);
      }

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
   * Install Ollama on Windows using the official installer
   */
  private async installWindows(onProgress: (p: OllamaDownloadProgress) => void): Promise<void> {
    const tempDir = app.getPath('temp');
    const installerPath = path.join(tempDir, 'OllamaSetup.exe');

    // Download
    onProgress({ stage: 'downloading', progress: 0, message: 'Downloading Ollama for Windows...' });
    await this.downloadFile('https://ollama.com/download/OllamaSetup.exe', installerPath, (percent) => {
      onProgress({
        stage: 'downloading',
        progress: Math.round(percent * 0.6),
        message: `Downloading... ${Math.round(percent)}%`,
      });
    });

    // Run installer with /S flag for silent installation
    onProgress({ stage: 'installing', progress: 60, message: 'Running Windows installer (this may take a minute)...' });
    
    try {
      // Run the installer - it installs to %LOCALAPPDATA%\Programs\Ollama
      // The /S flag makes it silent, but we need to wait for it to complete
      await execAsync(`"${installerPath}" /S`, { timeout: 120000 }); // 2 min timeout
      
      // The installer takes time to finish even after the command returns
      onProgress({ stage: 'installing', progress: 70, message: 'Waiting for installation to complete...' });
      
      // Wait and check periodically for the installation to complete
      const ollamaExePath = this.getWindowsOllamaPath();
      
      // Wait up to 60 seconds for the installation to complete
      let installed = false;
      for (let i = 0; i < 30; i++) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        onProgress({ 
          stage: 'installing', 
          progress: 70 + Math.min(i, 15), 
          message: `Verifying installation... (${i * 2}s)` 
        });
        
        if (fs.existsSync(ollamaExePath)) {
          installed = true;
          break;
        }
      }
      
      if (!installed) {
        throw new Error(
          'Ollama installer completed but ollama.exe was not found at expected location: ' + 
          ollamaExePath + 
          '. Please try installing Ollama manually from https://ollama.com/download/windows'
        );
      }
      
      // Update PATH for this process to include Ollama
      const ollamaDir = path.dirname(ollamaExePath);
      if (!process.env.PATH?.includes(ollamaDir)) {
        process.env.PATH = `${ollamaDir};${process.env.PATH}`;
      }
      
      onProgress({ stage: 'installing', progress: 85, message: 'Ollama installed successfully!' });

      // Start the service
      onProgress({ stage: 'starting', progress: 90, message: 'Starting Ollama service...' });
      await this.startServiceWindows(ollamaExePath);
      
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      throw new Error(`Windows installation failed: ${errorMsg}`);
    } finally {
      // Cleanup installer file
      try {
        if (fs.existsSync(installerPath)) {
          fs.unlinkSync(installerPath);
        }
      } catch {
        // Ignore cleanup errors
      }
    }
  }

  /**
   * Start Ollama service on Windows using the specific executable path
   */
  private async startServiceWindows(ollamaExePath: string): Promise<void> {
    // Check if already running
    if (await this.isRunning()) return;
    
    // Start Ollama with full path
    const ollama = spawn(ollamaExePath, ['serve'], {
      detached: true,
      stdio: 'ignore',
      windowsHide: true,
    });
    ollama.unref();
    
    // Wait for service to be ready (max 30 seconds)
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      if (await this.isRunning()) return;
    }
    
    throw new Error('Ollama service failed to start after 30 seconds');
  }

  /**
   * Pull (download) an Ollama model with progress tracking
   * Uses the CLI for more reliable progress reporting
   */
  async pullModel(
    modelName: string = 'llama3.2:3b',
    onProgress: (p: OllamaDownloadProgress) => void
  ): Promise<boolean> {
    try {
      // First check if Ollama is installed
      const isInstalled = await this.isInstalled();
      if (!isInstalled) {
        throw new Error('Ollama is not installed. Please install Ollama first using the setup wizard.');
      }
      
      // Then ensure Ollama is running
      if (!(await this.isRunning())) {
        onProgress({ stage: 'starting', progress: 0, message: 'Starting Ollama service...' });
        await this.startService();
        // Wait a bit for service to be fully ready
        await new Promise((r) => setTimeout(r, 2000));
      }

      onProgress({ stage: 'pulling-model', progress: 0, message: `Starting download of ${modelName}...` });

      // Use CLI for pulling - more reliable progress
      return new Promise((resolve) => {
        const ollamaPath = process.platform === 'win32' 
          ? this.getWindowsOllamaPath() 
          : 'ollama';
        
        const pullProcess = spawn(ollamaPath, ['pull', modelName], {
          stdio: 'pipe',
          shell: process.platform === 'win32',
        });
        
        let lastProgress = 0;
        let outputBuffer = '';
        
        const parseProgress = (data: string) => {
          outputBuffer += data;
          const lines = outputBuffer.split('\n');
          outputBuffer = lines.pop() || '';
          
          for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;
            
            // Parse progress from ollama pull output
            // Format: "pulling manifest", "pulling sha256:xxx... 45%", "verifying sha256", "success"
            const percentMatch = trimmedLine.match(/(\d+)%/);
            if (percentMatch) {
              const percent = parseInt(percentMatch[1], 10);
              lastProgress = percent;
              onProgress({
                stage: 'pulling-model',
                progress: percent,
                message: `Downloading ${modelName}... ${percent}%`,
              });
            } else if (trimmedLine.toLowerCase().includes('pulling manifest')) {
              onProgress({
                stage: 'pulling-model',
                progress: 1,
                message: `Fetching ${modelName} manifest...`,
              });
            } else if (trimmedLine.toLowerCase().includes('pulling')) {
              onProgress({
                stage: 'pulling-model',
                progress: lastProgress || 5,
                message: `Downloading ${modelName}...`,
              });
            } else if (trimmedLine.toLowerCase().includes('verifying')) {
              onProgress({
                stage: 'pulling-model',
                progress: 95,
                message: `Verifying ${modelName}...`,
              });
            } else if (trimmedLine.toLowerCase().includes('writing')) {
              onProgress({
                stage: 'pulling-model',
                progress: 98,
                message: `Writing ${modelName} to disk...`,
              });
            } else if (trimmedLine.toLowerCase().includes('success')) {
              onProgress({
                stage: 'complete',
                progress: 100,
                message: `${modelName} ready!`,
              });
            }
          }
        };
        
        pullProcess.stdout?.on('data', (data: Buffer) => {
          parseProgress(data.toString());
        });
        
        pullProcess.stderr?.on('data', (data: Buffer) => {
          // Ollama outputs progress to stderr
          parseProgress(data.toString());
        });
        
        pullProcess.on('close', (code) => {
          if (code === 0) {
            onProgress({ stage: 'complete', progress: 100, message: `${modelName} ready!` });
            resolve(true);
          } else {
            onProgress({
              stage: 'error',
              progress: 0,
              message: 'Failed to download model',
              error: `Process exited with code ${code}`,
            });
            resolve(false);
          }
        });
        
        pullProcess.on('error', (error) => {
          onProgress({
            stage: 'error',
            progress: 0,
            message: 'Failed to download model',
            error: error.message,
          });
          resolve(false);
        });
        
        // Timeout after 30 minutes for large models
        setTimeout(() => {
          pullProcess.kill();
          onProgress({
            stage: 'error',
            progress: 0,
            message: 'Model download timed out',
            error: 'Download took too long (>30 minutes)',
          });
          resolve(false);
        }, 1800000);
      });
      
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
   * Start the Ollama service (Windows native only)
   */
  async startService(): Promise<void> {
    // Check if already running
    if (await this.isRunning()) return;

    if (process.platform === 'win32') {
      // On Windows, use the direct path to the executable
      const ollamaPath = this.getWindowsOllamaPath();
      
      if (!fs.existsSync(ollamaPath)) {
        throw new Error(
          'Ollama is not installed on Windows. ' +
          'Expected location: ' + ollamaPath + '. ' +
          'Please run the setup wizard to install Ollama.'
        );
      }
      
      // Start Ollama with full path to avoid any PATH/WSL conflicts
      const ollama = spawn(ollamaPath, ['serve'], {
        detached: true,
        stdio: 'ignore',
        windowsHide: true,
      });
      ollama.unref();
    } else {
      // On Unix, start normally
      const ollama = spawn('ollama', ['serve'], {
        detached: true,
        stdio: 'ignore',
        windowsHide: false,
      });
      ollama.unref();
    }

    // Wait for it to be ready (max 30 seconds)
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      if (await this.isRunning()) return;
    }

    throw new Error('Ollama service failed to start after 30 seconds. Please check if another Ollama instance is running.');
  }

  /**
   * Stop the Ollama service
   */
  async stopService(): Promise<void> {
    try {
      if (process.platform === 'win32') {
        // On Windows, kill ollama.exe process
        await execAsync('taskkill /F /IM ollama.exe').catch(() => {});
      } else {
        // On Unix, use pkill
        await execAsync('pkill -f "ollama serve"').catch(() => {});
      }
    } catch {
      // Process might not exist, that's OK
    }
  }

  /**
   * Uninstall Ollama completely from the system (Windows only for now)
   * This removes the Ollama executable, models, and PATH entries
   */
  async uninstall(onProgress?: (message: string) => void): Promise<{ success: boolean; error?: string }> {
    try {
      if (process.platform !== 'win32') {
        return { 
          success: false, 
          error: 'Automatic uninstall is only supported on Windows. On Linux/macOS, please uninstall manually.' 
        };
      }

      onProgress?.('Stopping Ollama processes...');
      
      // Stop any running Ollama processes
      await this.stopService();
      // Give processes time to fully stop
      await new Promise(r => setTimeout(r, 2000));
      
      onProgress?.('Removing Ollama installation...');

      // Remove the installation directory
      const installDir = path.join(
        process.env.LOCALAPPDATA || '',
        'Programs',
        'Ollama'
      );
      
      if (fs.existsSync(installDir)) {
        await execAsync(`powershell -Command "Remove-Item -Path '${installDir}' -Recurse -Force -ErrorAction SilentlyContinue"`);
      }

      onProgress?.('Removing Ollama models and configuration...');

      // Remove models and configuration from user profile
      const ollamaHome = path.join(process.env.USERPROFILE || '', '.ollama');
      if (fs.existsSync(ollamaHome)) {
        await execAsync(`powershell -Command "Remove-Item -Path '${ollamaHome}' -Recurse -Force -ErrorAction SilentlyContinue"`);
      }

      onProgress?.('Cleaning environment variables...');

      // Clean environment variables
      await execAsync(`powershell -Command "[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', $null, 'User')"`);
      await execAsync(`powershell -Command "[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', $null, 'User')"`);

      // Clean PATH
      try {
        const { stdout: currentPath } = await execAsync(
          `powershell -Command "[System.Environment]::GetEnvironmentVariable('Path','User')"`
        );
        
        // Filter out any Ollama-related paths
        const pathParts = currentPath.trim().split(';');
        const cleanedPath = pathParts
          .filter(p => !p.toLowerCase().includes('ollama'))
          .join(';');
        
        if (cleanedPath !== currentPath.trim()) {
          await execAsync(
            `powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', '${cleanedPath}', 'User')"`
          );
        }
      } catch (pathError) {
        console.warn('[OllamaInstaller] Failed to clean PATH:', pathError);
        // Continue anyway
      }

      // Also update current process PATH
      if (process.env.PATH) {
        process.env.PATH = process.env.PATH
          .split(';')
          .filter(p => !p.toLowerCase().includes('ollama'))
          .join(';');
      }

      onProgress?.('Ollama uninstalled successfully!');
      
      return { success: true };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('[OllamaInstaller] Uninstall failed:', errorMessage);
      return { success: false, error: errorMessage };
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

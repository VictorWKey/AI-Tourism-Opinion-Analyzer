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
   * Install Ollama on Windows by downloading and extracting the zip file
   * No installer, no GUI windows, just clean background installation
   * Uses PowerShell's Invoke-WebRequest for reliable downloading
   */
  private async installWindows(onProgress: (p: OllamaDownloadProgress) => void): Promise<void> {
    const ollamaExePath = this.getWindowsOllamaPath();
    const installDir = path.dirname(ollamaExePath);

    // Check if already installed
    if (fs.existsSync(ollamaExePath)) {
      onProgress({ stage: 'installing', progress: 85, message: 'Ollama already installed!' });
      
      // Just ensure service is running
      if (!(await this.isRunning())) {
        onProgress({ stage: 'starting', progress: 90, message: 'Starting Ollama service...' });
        await this.startServiceWindows(ollamaExePath);
      }
      return;
    }

    onProgress({ stage: 'downloading', progress: 0, message: 'Downloading Ollama...' });
    
    try {
      // Create installation directory
      if (!fs.existsSync(installDir)) {
        fs.mkdirSync(installDir, { recursive: true });
      }

      const zipPath = path.join(installDir, 'ollama.zip');
      const downloadUrl = 'https://ollama.com/download/ollama-windows-amd64.zip';

      // Download using PowerShell's Invoke-WebRequest (more reliable than Node https)
      onProgress({ stage: 'downloading', progress: 5, message: 'Downloading Ollama...' });
      
      // Use PowerShell to download - this handles redirects properly
      // Need semicolons to separate statements in single-line PowerShell
      const downloadCommand = `powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '${downloadUrl}' -OutFile '${zipPath}'; $ProgressPreference = 'Continue'"`;
      
      console.log('[OllamaInstaller] Downloading from:', downloadUrl);
      console.log('[OllamaInstaller] Saving to:', zipPath);
      
      await execAsync(downloadCommand, { 
        timeout: 300000  // 5 minute timeout for download
      });
      
      // Verify download succeeded
      if (!fs.existsSync(zipPath)) {
        throw new Error('Download failed - zip file not created');
      }
      
      const stats = fs.statSync(zipPath);
      console.log('[OllamaInstaller] Downloaded file size:', stats.size, 'bytes');
      
      if (stats.size < 1000000) {  // Less than 1MB is suspicious
        throw new Error(`Download appears incomplete - file size is only ${stats.size} bytes`);
      }

      onProgress({ stage: 'downloading', progress: 55, message: 'Download complete!' });

      // Extract the zip file using PowerShell
      onProgress({ stage: 'installing', progress: 60, message: 'Extracting Ollama...' });
      console.log('[OllamaInstaller] Extracting to:', installDir);
      
      await execAsync(
        `powershell -Command "Expand-Archive -Path '${zipPath}' -DestinationPath '${installDir}' -Force"`,
        { timeout: 60000 }
      );

      // Delete the zip file
      try {
        fs.unlinkSync(zipPath);
      } catch {
        // Ignore cleanup errors
      }

      onProgress({ stage: 'installing', progress: 70, message: 'Configuring PATH...' });

      // Add to PATH environment variable
      try {
        const { stdout: userPath } = await execAsync(
          'powershell -Command "[System.Environment]::GetEnvironmentVariable(\'Path\',\'User\')"'
        );
        
        const currentPath = userPath.trim();
        if (!currentPath.includes(installDir)) {
          await execAsync(
            `powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', '${currentPath};${installDir}', 'User')"`
          );
          console.log('[OllamaInstaller] Added to PATH:', installDir);
        }

        // Update PATH for current process
        if (!process.env.PATH?.includes(installDir)) {
          process.env.PATH = `${process.env.PATH};${installDir}`;
        }
      } catch (error) {
        console.warn('[OllamaInstaller] Failed to update PATH:', error);
        // Continue anyway, we'll use full path
      }

      // Verify installation
      onProgress({ stage: 'installing', progress: 80, message: 'Verifying installation...' });
      
      // List files in install directory for debugging
      const files = fs.readdirSync(installDir);
      console.log('[OllamaInstaller] Files in install dir:', files);
      
      if (!fs.existsSync(ollamaExePath)) {
        throw new Error(`Ollama executable not found at ${ollamaExePath}. Found files: ${files.join(', ')}`);
      }

      onProgress({ stage: 'installing', progress: 85, message: 'Ollama installed successfully!' });

      // Start the service in background (hidden)
      onProgress({ stage: 'starting', progress: 90, message: 'Starting Ollama service...' });
      await this.startServiceWindows(ollamaExePath);

      onProgress({ stage: 'starting', progress: 98, message: 'Ollama service started!' });
      console.log('[OllamaInstaller] Windows installation complete!');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('[OllamaInstaller] Windows installation failed:', errorMessage);
      throw new Error(`Windows installation failed: ${errorMessage}`);
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

/**
 * PythonSetup - Automatic Python Environment Setup for Windows
 * ==============================================================
 * Handles:
 * - Python automatic download and installation
 * - Python installation detection
 * - Virtual environment creation
 * - Dependencies installation from requirements.txt
 * - Automatic setup on first run
 */

import { spawn, exec } from 'child_process';
import { app } from 'electron';
import path from 'path';
import fs from 'fs';
import https from 'https';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Python download URLs for Windows
const PYTHON_DOWNLOAD_URL = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe';
const PYTHON_VERSION = '3.11.9';

export interface PythonSetupProgress {
  stage: 'checking' | 'downloading-python' | 'installing-python' | 'creating-venv' | 'installing-deps' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
}

export interface PythonSetupStatus {
  pythonInstalled: boolean;
  pythonVersion?: string;
  pythonPath?: string;
  venvExists: boolean;
  venvPath?: string;
  dependenciesInstalled: boolean;
}

/**
 * PythonSetup class for automatic Python environment configuration
 */
export class PythonSetup {
  private pythonDir: string;
  private venvDir: string;
  private requirementsPath: string;
  private isWindows: boolean;

  constructor() {
    this.isWindows = process.platform === 'win32';
    
    if (app.isPackaged) {
      // In production, Python is bundled in resources
      this.pythonDir = path.join(process.resourcesPath, 'python');
    } else {
      // In development, use the python folder in project
      this.pythonDir = path.join(app.getAppPath(), 'python');
    }
    
    this.venvDir = path.join(this.pythonDir, 'venv');
    this.requirementsPath = path.join(this.pythonDir, 'requirements.txt');
  }

  /**
   * Get the Python executable path
   */
  getPythonPath(): string {
    const venvPython = this.getVenvPythonPath();
    if (fs.existsSync(venvPython)) {
      return venvPython;
    }
    // Fallback to system Python
    return this.isWindows ? 'python' : 'python3';
  }

  /**
   * Get the virtual environment Python path
   */
  private getVenvPythonPath(): string {
    if (this.isWindows) {
      return path.join(this.venvDir, 'Scripts', 'python.exe');
    }
    return path.join(this.venvDir, 'bin', 'python');
  }

  /**
   * Get the pip path in virtual environment
   */
  private getVenvPipPath(): string {
    if (this.isWindows) {
      return path.join(this.venvDir, 'Scripts', 'pip.exe');
    }
    return path.join(this.venvDir, 'bin', 'pip');
  }

  /**
   * Check the current Python setup status
   */
  async checkStatus(): Promise<PythonSetupStatus> {
    const status: PythonSetupStatus = {
      pythonInstalled: false,
      venvExists: false,
      dependenciesInstalled: false,
    };

    // Check system Python
    try {
      const pythonCmd = this.isWindows ? 'python' : 'python3';
      const { stdout } = await execAsync(`${pythonCmd} --version`);
      status.pythonInstalled = true;
      status.pythonVersion = stdout.trim().replace('Python ', '');
      status.pythonPath = pythonCmd;
    } catch {
      // Try 'python' as fallback on non-Windows
      if (!this.isWindows) {
        try {
          const { stdout } = await execAsync('python --version');
          const version = stdout.trim().replace('Python ', '');
          // Make sure it's Python 3
          if (version.startsWith('3.')) {
            status.pythonInstalled = true;
            status.pythonVersion = version;
            status.pythonPath = 'python';
          }
        } catch {
          // No Python found
        }
      }
    }

    // Check virtual environment
    const venvPython = this.getVenvPythonPath();
    if (fs.existsSync(venvPython)) {
      status.venvExists = true;
      status.venvPath = this.venvDir;
      
      // Check if key dependencies are installed
      try {
        const checkCmd = `"${venvPython}" -c "import pandas; import torch; import transformers; print('ok')"`;
        await execAsync(checkCmd);
        status.dependenciesInstalled = true;
      } catch {
        status.dependenciesInstalled = false;
      }
    }

    return status;
  }

  /**
   * Run the complete setup process (with automatic Python installation)
   */
  async setup(onProgress: (p: PythonSetupProgress) => void): Promise<boolean> {
    try {
      // Step 1: Check Python installation
      onProgress({ stage: 'checking', progress: 5, message: 'Verificando instalación de Python...' });
      
      let status = await this.checkStatus();
      
      // If Python is not installed, try to install it automatically (Windows only)
      if (!status.pythonInstalled) {
        if (this.isWindows) {
          onProgress({ stage: 'downloading-python', progress: 10, message: 'Descargando Python...' });
          
          const installed = await this.downloadAndInstallPython(onProgress);
          if (!installed) {
            return false;
          }
          
          // Re-check status after installation
          status = await this.checkStatus();
          if (!status.pythonInstalled) {
            onProgress({
              stage: 'error',
              progress: 0,
              message: 'Error de instalación',
              error: 'Python se instaló pero no se detecta. Por favor reinicia la aplicación.',
            });
            return false;
          }
        } else {
          // Non-Windows: can't auto-install
          onProgress({
            stage: 'error',
            progress: 0,
            message: 'Python no encontrado',
            error: 'Python 3.9+ es requerido. Por favor instala Python desde python.org.',
          });
          return false;
        }
      }

      onProgress({ stage: 'checking', progress: 25, message: `Python ${status.pythonVersion} encontrado` });

      // Step 2: Create virtual environment if needed
      if (!status.venvExists) {
        onProgress({ stage: 'creating-venv', progress: 30, message: 'Creando entorno virtual...' });
        
        const created = await this.createVirtualEnvironment(onProgress);
        if (!created) {
          return false;
        }
      } else {
        onProgress({ stage: 'creating-venv', progress: 40, message: 'Entorno virtual existente' });
      }

      // Step 3: Install dependencies
      if (!status.dependenciesInstalled) {
        onProgress({ stage: 'installing-deps', progress: 45, message: 'Instalando dependencias de Python...' });
        
        const installed = await this.installDependencies(onProgress);
        if (!installed) {
          return false;
        }
      } else {
        onProgress({ stage: 'installing-deps', progress: 95, message: 'Dependencias ya instaladas' });
      }

      onProgress({ stage: 'complete', progress: 100, message: '¡Entorno Python listo!' });
      return true;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onProgress({
        stage: 'error',
        progress: 0,
        message: 'Setup failed',
        error: errorMessage,
      });
      return false;
    }
  }

  /**
   * Create Python virtual environment
   */
  private async createVirtualEnvironment(
    onProgress: (p: PythonSetupProgress) => void
  ): Promise<boolean> {
    return new Promise((resolve) => {
      const pythonCmd = this.isWindows ? 'python' : 'python3';
      
      const venv = spawn(pythonCmd, ['-m', 'venv', this.venvDir], {
        cwd: this.pythonDir,
        shell: this.isWindows,
      });

      venv.stdout?.on('data', (data: Buffer) => {
        console.log('[PythonSetup] venv stdout:', data.toString());
      });

      venv.stderr?.on('data', (data: Buffer) => {
        const msg = data.toString();
        // Not all stderr is an error
        if (!msg.includes('error') && !msg.includes('Error')) {
          console.log('[PythonSetup] venv stderr:', msg);
        } else {
          console.error('[PythonSetup] venv error:', msg);
        }
      });

      venv.on('close', (code) => {
        if (code === 0) {
          onProgress({ stage: 'creating-venv', progress: 30, message: 'Virtual environment created' });
          resolve(true);
        } else {
          onProgress({
            stage: 'error',
            progress: 0,
            message: 'Failed to create virtual environment',
            error: `venv creation failed with code ${code}`,
          });
          resolve(false);
        }
      });

      venv.on('error', (error) => {
        onProgress({
          stage: 'error',
          progress: 0,
          message: 'Failed to create virtual environment',
          error: error.message,
        });
        resolve(false);
      });
    });
  }

  /**
   * Install Python dependencies from requirements.txt
   */
  private async installDependencies(
    onProgress: (p: PythonSetupProgress) => void
  ): Promise<boolean> {
    // First upgrade pip
    const pipPath = this.getVenvPipPath();
    const pythonPath = this.getVenvPythonPath();

    try {
      onProgress({ stage: 'installing-deps', progress: 40, message: 'Upgrading pip...' });
      await execAsync(`"${pythonPath}" -m pip install --upgrade pip`);
    } catch (error) {
      console.warn('[PythonSetup] Failed to upgrade pip:', error);
      // Continue anyway
    }

    // Install requirements
    return new Promise((resolve) => {
      onProgress({ stage: 'installing-deps', progress: 45, message: 'Installing dependencies (this may take several minutes)...' });

      const pip = spawn(pipPath, ['install', '-r', this.requirementsPath], {
        cwd: this.pythonDir,
        shell: this.isWindows,
        env: {
          ...process.env,
          // Ensure we use the venv
          VIRTUAL_ENV: this.venvDir,
          PATH: this.isWindows 
            ? `${path.join(this.venvDir, 'Scripts')};${process.env.PATH}`
            : `${path.join(this.venvDir, 'bin')}:${process.env.PATH}`,
        },
      });

      let lastProgress = 45;
      const progressStep = 40 / 20; // Divide remaining progress into steps

      pip.stdout?.on('data', (data: Buffer) => {
        const msg = data.toString();
        console.log('[PythonSetup] pip:', msg);
        
        // Update progress based on output
        if (msg.includes('Successfully installed') || msg.includes('Requirement already satisfied')) {
          lastProgress = Math.min(lastProgress + progressStep, 85);
          onProgress({ stage: 'installing-deps', progress: lastProgress, message: 'Installing packages...' });
        }
      });

      pip.stderr?.on('data', (data: Buffer) => {
        const msg = data.toString();
        // pip often writes to stderr for warnings and download progress
        if (msg.includes('Downloading') || msg.includes('Installing')) {
          lastProgress = Math.min(lastProgress + progressStep / 2, 85);
          onProgress({ stage: 'installing-deps', progress: lastProgress, message: msg.split('\n')[0].trim() });
        }
        console.log('[PythonSetup] pip stderr:', msg);
      });

      pip.on('close', (code) => {
        if (code === 0) {
          onProgress({ stage: 'installing-deps', progress: 90, message: 'Dependencies installed successfully' });
          resolve(true);
        } else {
          onProgress({
            stage: 'error',
            progress: 0,
            message: 'Failed to install dependencies',
            error: `pip install failed with code ${code}. Some packages may require Visual C++ Build Tools.`,
          });
          resolve(false);
        }
      });

      pip.on('error', (error) => {
        onProgress({
          stage: 'error',
          progress: 0,
          message: 'Failed to install dependencies',
          error: error.message,
        });
        resolve(false);
      });
    });
  }

  /**
   * Check if a specific package is installed
   */
  async isPackageInstalled(packageName: string): Promise<boolean> {
    const pythonPath = this.getVenvPythonPath();
    if (!fs.existsSync(pythonPath)) {
      return false;
    }

    try {
      await execAsync(`"${pythonPath}" -c "import ${packageName}"`);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Download and install Python automatically (Windows only)
   */
  private async downloadAndInstallPython(
    onProgress: (p: PythonSetupProgress) => void
  ): Promise<boolean> {
    if (!this.isWindows) {
      onProgress({
        stage: 'error',
        progress: 0,
        message: 'Instalación automática no disponible',
        error: 'La instalación automática de Python solo está disponible en Windows.',
      });
      return false;
    }

    const tempDir = app.getPath('temp');
    const installerPath = path.join(tempDir, `python-${PYTHON_VERSION}-amd64.exe`);

    try {
      // Download Python installer
      onProgress({ stage: 'downloading-python', progress: 10, message: 'Descargando Python...' });
      
      await this.downloadFile(PYTHON_DOWNLOAD_URL, installerPath, (percent) => {
        const progress = 10 + Math.round(percent * 0.4); // 10-50%
        onProgress({
          stage: 'downloading-python',
          progress,
          message: `Descargando Python ${PYTHON_VERSION}... ${Math.round(percent)}%`,
        });
      });

      // Install Python silently
      onProgress({ stage: 'installing-python', progress: 55, message: 'Instalando Python...' });
      
      await this.runPythonInstaller(installerPath, onProgress);

      // Cleanup installer
      try {
        fs.unlinkSync(installerPath);
      } catch {
        // Ignore cleanup errors
      }

      // Refresh PATH for this process
      await this.refreshPath();

      onProgress({ stage: 'installing-python', progress: 75, message: 'Python instalado correctamente' });
      return true;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      onProgress({
        stage: 'error',
        progress: 0,
        message: 'Error instalando Python',
        error: errorMessage,
      });
      
      // Cleanup on error
      try {
        if (fs.existsSync(installerPath)) {
          fs.unlinkSync(installerPath);
        }
      } catch {
        // Ignore
      }
      
      return false;
    }
  }

  /**
   * Run the Python installer silently
   */
  private async runPythonInstaller(
    installerPath: string,
    onProgress: (p: PythonSetupProgress) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      // Python installer silent options:
      // /quiet - Silent install
      // /passive - Show progress but no interaction
      // InstallAllUsers=0 - Install for current user only (no admin required)
      // PrependPath=1 - Add Python to PATH
      // Include_pip=1 - Include pip
      // Include_test=0 - Skip test suite
      const args = [
        '/passive',
        'InstallAllUsers=0',
        'PrependPath=1',
        'Include_pip=1',
        'Include_test=0',
        'Include_doc=0',
        'Include_launcher=1',
        'InstallLauncherAllUsers=0',
      ];

      onProgress({ stage: 'installing-python', progress: 60, message: 'Ejecutando instalador...' });

      const installer = spawn(installerPath, args, {
        shell: true,
        windowsHide: false, // Show the installer progress window
      });

      installer.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Python installer exited with code ${code}`));
        }
      });

      installer.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Refresh the PATH environment variable for this process
   */
  private async refreshPath(): Promise<void> {
    if (!this.isWindows) return;

    try {
      // Get the updated PATH from the registry
      const { stdout: userPath } = await execAsync(
        'powershell -Command "[Environment]::GetEnvironmentVariable(\'Path\', \'User\')"'
      );
      const { stdout: systemPath } = await execAsync(
        'powershell -Command "[Environment]::GetEnvironmentVariable(\'Path\', \'Machine\')"'
      );

      // Update process.env.PATH
      const newPath = `${userPath.trim()};${systemPath.trim()}`;
      process.env.PATH = newPath;
      
      console.log('[PythonSetup] PATH refreshed');
    } catch (error) {
      console.warn('[PythonSetup] Failed to refresh PATH:', error);
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
        https.get(currentUrl, (response) => {
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
        }).on('error', (err) => {
          fs.unlink(dest, (unlinkErr) => {
            if (unlinkErr) console.error('Error cleaning up file:', unlinkErr);
          });
          reject(err);
        });
      };

      request(url);
    });
  }

  /**
   * Get the path to the Python directory
   */
  getPythonDir(): string {
    return this.pythonDir;
  }

  /**
   * Get the path to the virtual environment
   */
  getVenvDir(): string {
    return this.venvDir;
  }
}

// Singleton instance
export const pythonSetup = new PythonSetup();

// ============================================
// Python Bridge for Electron-Python Communication
// ============================================

import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { app, BrowserWindow } from 'electron';
import { EventEmitter } from 'events';

/**
 * Command structure sent to Python process
 */
export interface PythonCommand {
  action: string;
  [key: string]: unknown;
}

/**
 * Response structure from Python process
 */
export interface PythonResponse {
  success: boolean;
  type?: string;
  error?: string;
  traceback?: string;
  [key: string]: unknown;
}

/**
 * Progress update from Python process
 */
export interface PythonProgress {
  type: 'progress';
  phase: number;
  phaseName: string;
  progress: number;
  message?: string;
}

/**
 * Callback function type for pending responses
 */
type ResponseCallback = {
  resolve: (response: PythonResponse) => void;
  reject: (error: Error) => void;
  timeoutId: NodeJS.Timeout;
};

/**
 * PythonBridge - Manages communication with Python subprocess
 * 
 * Uses stdin/stdout for JSON message passing.
 * Supports progress updates and command timeouts.
 */
export class PythonBridge extends EventEmitter {
  private process: ChildProcess | null = null;
  private pythonPath: string;
  private scriptPath: string;
  private responseBuffer: string = '';
  private pendingCallbacks: Map<number, ResponseCallback> = new Map();
  private callId: number = 0;
  private isReady: boolean = false;
  private startPromise: Promise<void> | null = null;
  
  // Track current phase for progress parsing
  private currentPhase: number | null = null;
  private currentPhaseName: string | null = null;

  // Default timeout: 10 minutes for long-running phases
  private readonly DEFAULT_TIMEOUT = 600000;

  constructor() {
    super();
    
    // Determine Python path based on environment
    if (app.isPackaged) {
      // In production, use bundled Python
      this.pythonPath = path.join(process.resourcesPath, 'python', 'venv', 'bin', 'python');
      this.scriptPath = path.join(process.resourcesPath, 'python', 'api_bridge.py');
    } else {
      // In development, use system Python or virtual environment
      const projectPythonDir = path.join(app.getAppPath(), 'python');
      const venvPython = path.join(projectPythonDir, 'venv', 'bin', 'python');
      
      // Check if virtual environment exists, otherwise use system python3
      try {
        require('fs').accessSync(venvPython);
        this.pythonPath = venvPython;
      } catch {
        this.pythonPath = 'python3';
      }
      
      this.scriptPath = path.join(projectPythonDir, 'api_bridge.py');
    }
  }

  /**
   * Start the Python subprocess
   */
  async start(): Promise<void> {
    // If already starting, wait for that to complete
    if (this.startPromise) {
      return this.startPromise;
    }

    // If already running and ready, return immediately
    if (this.process && this.isReady) {
      return Promise.resolve();
    }

    this.startPromise = new Promise((resolve, reject) => {
      try {
        this.process = spawn(this.pythonPath, [this.scriptPath], {
          cwd: path.dirname(this.scriptPath),
          stdio: ['pipe', 'pipe', 'pipe'],
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',
            PYTHONIOENCODING: 'utf-8',
          },
        });

        // Handle stdout (JSON responses)
        this.process.stdout?.on('data', (data: Buffer) => {
          this.handleOutput(data.toString());
        });

        // Handle stderr (errors and debug output)
        this.process.stderr?.on('data', (data: Buffer) => {
          const rawMessage = data.toString();
          
          // Split by lines to handle multiple tqdm updates
          const lines = rawMessage.split(/[\r\n]+/).filter(line => line.trim());
          
          for (const line of lines) {
            const message = line.trim();
            if (!message) continue;
            
            // Try to parse tqdm progress from stderr
            // tqdm format: "   Progreso:  42%|████▏     | 205/483 [00:01<00:01, 154.06it/s]"
            if (message.includes('Progreso') && message.includes('%')) {
              const progressInfo = this.parseTqdmProgress(message);
              if (progressInfo) {
                // Emit as progress event
                this.emit('progress', progressInfo);
                this.broadcastToWindows('pipeline:progress', progressInfo);
                continue; // Don't log tqdm as error
              }
            }
            
            // Filter out info/debug messages - these are NOT errors
            // Only silence them, don't emit as error events
            const infoPatterns = [
              'Progreso', // Progress bar text
              '✅', '⏭️', '•', // Checkmarks and bullets
              'Analizando', 'Clasificando', 'Generando', // Action words
              'cargado', 'completado', 'procesadas', 'omitiendo', // Status words
              'Seleccionando', 'Reducción', 'excluidos', // Selection words
              'reseñas', 'categorías', 'subtópicos', // Data words
              'LLM inicializado', 'OpenAI', 'gpt-4', // LLM init messages
              'Tipos de resumen', 'reseñas representativas', // Summary messages
              'guardado', 'guardados', // Save messages
              'Dataset', 'validación', 'Validación', // Dataset messages
              'Fase', 'columna', // Phase messages
              // Sentiment and classification labels
              'Positivo', 'Negativo', 'Neutro', // Sentiment
              'Subjetiva', 'Mixta', // Subjectivity
              'Alojamiento', 'Gastronomía', 'Transporte', 'Eventos', 'Historia', 'Compras', 'Deportes', 'nocturna', 'Naturaleza', 'Seguridad', 'Fauna', 'Personal', 'servicio', // Categories
              // Statistics patterns
              '|', 'Promedio', 'Total', 'opiniones', 'distribucion',
            ];
            
            if (infoPatterns.some(pattern => message.includes(pattern))) {
              // Emit as info event (not error)
              this.emit('info', message);
              continue;
            }
            
            // Only emit actual error messages (real exceptions, warnings, etc.)
            // Examples: "Traceback", "Error:", "Exception", etc.
            if (message.toLowerCase().includes('error') || 
                message.toLowerCase().includes('exception') ||
                message.toLowerCase().includes('traceback') ||
                message.toLowerCase().includes('failed') ||
                message.toLowerCase().includes('fatal')) {
              this.emit('error', message);
            }
            // Silently ignore other messages (they're just debug output)
          }
        });

        // Handle process close
        this.process.on('close', (code) => {
          this.cleanup();
          this.emit('close', code);
        });

        // Handle process error
        this.process.on('error', (error) => {
          this.cleanup();
          this.emit('error', error.message);
          reject(error);
        });

        // Wait for ready signal or timeout
        const readyTimeout = setTimeout(() => {
          if (!this.isReady) {
            this.isReady = true;
            this.startPromise = null;
            this.emit('warn', 'Ready timeout, assuming process is ready');
            resolve();
          }
        }, 5000);

        // Listen for ready signal
        const readyHandler = (response: PythonResponse) => {
          if (response.type === 'ready') {
            clearTimeout(readyTimeout);
            this.isReady = true;
            this.startPromise = null;
            this.emit('ready');
            resolve();
          }
        };

        this.once('message', readyHandler);
        
      } catch (error) {
        this.startPromise = null;
        reject(error);
      }
    });

    return this.startPromise;
  }

  /**
   * Handle output from Python process
   */
  private handleOutput(data: string): void {
    this.responseBuffer += data;
    
    // Process complete JSON lines
    const lines = this.responseBuffer.split('\n');
    this.responseBuffer = lines.pop() || '';
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line) as PythonResponse;
          
          // Emit message event for any response
          this.emit('message', response);
          
          // Handle progress updates
          if (response.type === 'progress') {
            this.emit('progress', response);
            // Forward to all renderer windows
            this.broadcastToWindows('pipeline:progress', response);
          } else if (response.type === 'ready') {
            // Ready signal handled in start() - just emit
            this.emit('ready');
          } else {
            // Handle command responses - resolve the oldest pending callback
            this.resolveOldestPending(response);
          }
        } catch (e) {
          // Silently handle parse errors to avoid EPIPE
          this.emit('error', `Failed to parse response: ${line}`);
        }
      }
    }
  }

  /**
   * Resolve the oldest pending callback
   */
  private resolveOldestPending(response: PythonResponse): void {
    // Find the oldest pending callback (lowest call ID)
    let oldestId: number | null = null;
    for (const id of this.pendingCallbacks.keys()) {
      if (oldestId === null || id < oldestId) {
        oldestId = id;
      }
    }

    if (oldestId !== null) {
      const callback = this.pendingCallbacks.get(oldestId);
      if (callback) {
        clearTimeout(callback.timeoutId);
        this.pendingCallbacks.delete(oldestId);
        callback.resolve(response);
      }
    }
  }

  /**
   * Parse tqdm progress from stderr output
   * Formats:
   * - "   Progreso:  42%|████▏     | 205/483 [00:01<00:01, 154.06it/s]"
   * - "   Progreso: 100%|██████████| 483/483 [00:03<00:00, 158.42it/s]"
   */
  private parseTqdmProgress(line: string): PythonProgress | null {
    try {
      // Extract percentage - handle various formats
      // Match patterns like "Progreso:  42%" or "Progreso: 100%"
      const percentMatch = line.match(/Progreso[:\s]+(\d+)%/);
      if (!percentMatch) return null;
      
      const progress = parseInt(percentMatch[1], 10);
      
      // Extract current/total if available
      let message = `${progress}% completado`;
      const countMatch = line.match(/\|\s*(\d+)\/(\d+)/);
      if (countMatch) {
        const current = countMatch[1];
        const total = countMatch[2];
        message = `Procesando ${current}/${total}`;
      }
      
      // Return progress object with current phase context
      return {
        type: 'progress',
        phase: this.currentPhase || 1,
        phaseName: this.currentPhaseName || 'Processing',
        progress,
        message,
      };
    } catch (error) {
      return null;
    }
  }

  /**
   * Broadcast message to all renderer windows
   */
  private broadcastToWindows(channel: string, data: unknown): void {
    const windows = BrowserWindow.getAllWindows();
    windows.forEach(win => {
      if (!win.isDestroyed()) {
        win.webContents.send(channel, data);
      }
    });
  }

  /**
   * Execute a command and wait for response
   */
  async execute(command: PythonCommand, timeout?: number): Promise<PythonResponse> {
    // Ensure process is started
    if (!this.process || !this.isReady) {
      await this.start();
    }

    if (!this.process?.stdin) {
      throw new Error('Python process stdin not available');
    }

    return new Promise((resolve, reject) => {
      const currentCallId = this.callId++;
      const timeoutMs = timeout || this.DEFAULT_TIMEOUT;
      
      // Set up timeout
      const timeoutId = setTimeout(() => {
        if (this.pendingCallbacks.has(currentCallId)) {
          this.pendingCallbacks.delete(currentCallId);
          reject(new Error(`Python command timeout after ${timeoutMs}ms: ${command.action}`));
        }
      }, timeoutMs);

      // Register callback
      this.pendingCallbacks.set(currentCallId, { resolve, reject, timeoutId });
      
      // Send command
      const commandStr = JSON.stringify(command) + '\n';
      this.process?.stdin?.write(commandStr, (error) => {
        if (error) {
          clearTimeout(timeoutId);
          this.pendingCallbacks.delete(currentCallId);
          reject(new Error(`Failed to write to Python stdin: ${error.message}`));
        }
      });
    });
  }

  /**
   * Check if Python process is running and healthy
   */
  async isHealthy(): Promise<boolean> {
    try {
      const response = await this.execute({ action: 'ping' }, 5000);
      return response.success === true;
    } catch {
      return false;
    }
  }

  /**
   * Stop the Python subprocess
   */
  stop(): void {
    this.cleanup();
  }

  /**
   * Force stop the Python subprocess immediately (like Ctrl+C)
   * This sends SIGINT first, then SIGKILL if needed
   */
  forceStop(): void {
    if (this.process) {
      // First try SIGINT (Ctrl+C) for graceful interruption
      this.process.kill('SIGINT');
      
      // Give it 500ms to respond to SIGINT, then force kill
      setTimeout(() => {
        if (this.process) {
          this.process.kill('SIGKILL');
        }
      }, 500);
    }
    
    this.cleanup();
  }

  /**
   * Clean up resources
   */
  private cleanup(): void {
    // Clear all pending callbacks with rejection
    for (const [id, callback] of this.pendingCallbacks) {
      clearTimeout(callback.timeoutId);
      callback.reject(new Error('Python bridge stopped'));
    }
    this.pendingCallbacks.clear();

    // Kill process if running
    if (this.process) {
      this.process.kill();
      this.process = null;
    }

    this.isReady = false;
    this.startPromise = null;
    this.responseBuffer = '';
  }

  /**
   * Get current status
   */
  getStatus(): { running: boolean; ready: boolean; pendingCalls: number } {
    return {
      running: this.process !== null,
      ready: this.isReady,
      pendingCalls: this.pendingCallbacks.size,
    };
  }

  /**
   * Set the current phase context for progress parsing
   */
  setPhaseContext(phase: number | null, phaseName: string | null): void {
    this.currentPhase = phase;
    this.currentPhaseName = phaseName;
  }
}

// Singleton instance
let bridgeInstance: PythonBridge | null = null;

/**
 * Get the singleton PythonBridge instance
 */
export function getPythonBridge(): PythonBridge {
  if (!bridgeInstance) {
    bridgeInstance = new PythonBridge();
  }
  return bridgeInstance;
}

/**
 * Stop and clean up the Python bridge
 */
export function stopPythonBridge(): void {
  if (bridgeInstance) {
    bridgeInstance.stop();
    bridgeInstance = null;
  }
}

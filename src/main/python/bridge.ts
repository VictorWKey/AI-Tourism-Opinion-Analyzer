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

    console.log('[PythonBridge] Python path:', this.pythonPath);
    console.log('[PythonBridge] Script path:', this.scriptPath);
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
        console.log('[PythonBridge] Starting Python process...');
        
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
          const message = data.toString().trim();
          console.error('[Python Error]:', message);
          this.emit('error', message);
        });

        // Handle process close
        this.process.on('close', (code) => {
          console.log(`[PythonBridge] Process exited with code ${code}`);
          this.cleanup();
          this.emit('close', code);
        });

        // Handle process error
        this.process.on('error', (error) => {
          console.error('[PythonBridge] Failed to start:', error);
          this.cleanup();
          reject(error);
        });

        // Wait for ready signal or timeout
        const readyTimeout = setTimeout(() => {
          if (!this.isReady) {
            console.warn('[PythonBridge] Ready timeout, assuming process is ready');
            this.isReady = true;
            this.startPromise = null;
            resolve();
          }
        }, 5000);

        // Listen for ready signal
        const readyHandler = (response: PythonResponse) => {
          if (response.type === 'ready') {
            clearTimeout(readyTimeout);
            this.isReady = true;
            this.startPromise = null;
            console.log('[PythonBridge] Python process ready');
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
            // Ready signal handled in start()
            console.log('[PythonBridge] Received ready signal');
          } else {
            // Handle command responses - resolve the oldest pending callback
            this.resolveOldestPending(response);
          }
        } catch (e) {
          console.error('[PythonBridge] Failed to parse response:', line, e);
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
    console.log('[PythonBridge] Stopping Python process...');
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

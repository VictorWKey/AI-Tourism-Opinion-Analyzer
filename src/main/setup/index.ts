/**
 * Setup Module Index
 * ===================
 * Exports all setup-related classes and utilities
 */

export { SetupManager, setupManager } from './SetupManager';
export type { SetupState, SystemCheckResult } from './SetupManager';

export { OllamaInstaller, ollamaInstaller } from './OllamaInstaller';
export type { OllamaDownloadProgress } from './OllamaInstaller';

export { ModelDownloader, modelDownloader } from './ModelDownloader';
export type { ModelInfo, ModelDownloadProgress, ModelsStatus } from './ModelDownloader';

export { PythonSetup, pythonSetup } from './PythonSetup';
export type { PythonSetupProgress, PythonSetupStatus } from './PythonSetup';

export { handleSquirrelEvents } from './UninstallHandler';
export type { UninstallChoices } from './UninstallHandler';

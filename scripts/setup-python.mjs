/**
 * Cross-platform Python setup helper.
 * Creates a virtual environment and installs dependencies.
 * 
 * Usage: node scripts/setup-python.mjs
 */
import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pythonDir = join(__dirname, '..', 'python');
const venvDir = join(pythonDir, 'venv');
const isWindows = process.platform === 'win32';

// Determine Python command
function getPythonCmd() {
  const candidates = isWindows ? ['python', 'python3'] : ['python3', 'python'];
  for (const cmd of candidates) {
    try {
      const version = execSync(`${cmd} --version`, { encoding: 'utf-8' }).trim();
      if (version.startsWith('Python 3.')) {
        return cmd;
      }
    } catch {
      continue;
    }
  }
  console.error('ERROR: Python 3 not found. Please install Python 3.9+ first.');
  process.exit(1);
}

const pythonCmd = getPythonCmd();
console.log(`Using: ${pythonCmd} (${execSync(`${pythonCmd} --version`, { encoding: 'utf-8' }).trim()})`);

// Create venv if needed
if (!existsSync(venvDir)) {
  console.log('Creating virtual environment...');
  execSync(`${pythonCmd} -m venv "${venvDir}"`, { cwd: pythonDir, stdio: 'inherit' });
} else {
  console.log('Virtual environment already exists.');
}

// Get pip path
const pipPath = isWindows
  ? join(venvDir, 'Scripts', 'pip.exe')
  : join(venvDir, 'bin', 'pip');

// Upgrade pip
console.log('Upgrading pip...');
execSync(`"${pipPath}" install --upgrade pip`, { cwd: pythonDir, stdio: 'inherit' });

// Install requirements
console.log('Installing dependencies (this may take several minutes)...');
execSync(`"${pipPath}" install -r requirements.txt`, { cwd: pythonDir, stdio: 'inherit' });

console.log('\n✓ Python environment ready!');

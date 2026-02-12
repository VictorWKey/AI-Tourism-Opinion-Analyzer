/**
 * Pre-bundle Python Environment for Distribution
 * ================================================
 * 
 * This script creates a portable Python environment that can be
 * bundled with the installer, eliminating the need for users to
 * download Python + dependencies on first run.
 * 
 * USAGE:
 *   node scripts/bundle-python.mjs
 * 
 * WHAT IT DOES:
 *   1. Downloads python-build-standalone (portable Python, no installer needed)
 *   2. Creates a venv with all pip dependencies pre-installed
 *   3. Outputs to python/bundled-env/ ready for extraResource inclusion
 * 
 * AFTER RUNNING:
 *   Update forge.config.ts extraResource to include the bundled env:
 *     extraResource: ['./python'],  // already includes bundled-env/
 *   
 *   The PythonSetup.ts will detect the bundled env and skip download.
 * 
 * SIZE ESTIMATE:
 *   ~1.5 GB (Python ~50MB + PyTorch ~800MB + Transformers ~200MB + others)
 *   The installer will be ~500MB compressed.
 */

import { execSync } from 'child_process';
import { existsSync, mkdirSync, rmSync, writeFileSync, createWriteStream } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import https from 'https';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, '..');
const pythonDir = join(projectRoot, 'python');
const bundledDir = join(pythonDir, 'bundled-env');
const requirementsPath = join(pythonDir, 'requirements.txt');

// Python standalone build URL (Windows x64, shared install-only variant)
const PYTHON_STANDALONE_VERSION = '20241016';
const PYTHON_VERSION = '3.11.10';
const STANDALONE_URL = `https://github.com/indygreg/python-build-standalone/releases/download/${PYTHON_STANDALONE_VERSION}/cpython-${PYTHON_VERSION}+${PYTHON_STANDALONE_VERSION}-x86_64-pc-windows-msvc-install_only_stripped.tar.gz`;

function download(url, dest) {
  return new Promise((resolve, reject) => {
    console.log(`  Downloading: ${url}`);
    const file = createWriteStream(dest);
    https.get(url, (response) => {
      // Handle redirects
      if (response.statusCode === 302 || response.statusCode === 301) {
        file.close();
        rmSync(dest, { force: true });
        return download(response.headers.location, dest).then(resolve).catch(reject);
      }
      const totalBytes = parseInt(response.headers['content-length'] || '0', 10);
      let downloaded = 0;
      response.on('data', (chunk) => {
        downloaded += chunk.length;
        if (totalBytes > 0) {
          const pct = Math.round((downloaded / totalBytes) * 100);
          process.stdout.write(`\r  Progress: ${pct}% (${(downloaded / 1e6).toFixed(1)}MB / ${(totalBytes / 1e6).toFixed(1)}MB)`);
        }
      });
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log('\n  Download complete.');
        resolve();
      });
    }).on('error', (err) => {
      file.close();
      rmSync(dest, { force: true });
      reject(err);
    });
  });
}

async function main() {
  console.log('=== Python Environment Bundler ===\n');

  // Step 1: Download standalone Python
  const tarPath = join(projectRoot, 'python-standalone.tar.gz');
  if (!existsSync(tarPath)) {
    console.log('Step 1: Downloading Python standalone build...');
    await download(STANDALONE_URL, tarPath);
  } else {
    console.log('Step 1: Python standalone archive already downloaded.');
  }

  // Step 2: Extract
  console.log('\nStep 2: Extracting Python...');
  if (existsSync(bundledDir)) {
    rmSync(bundledDir, { recursive: true, force: true });
  }
  mkdirSync(bundledDir, { recursive: true });

  // Extract using tar (available on Windows 10+)
  execSync(`tar -xzf "${tarPath}" -C "${bundledDir}"`, { stdio: 'inherit' });

  // The archive extracts to a 'python/' subfolder inside bundledDir
  const extractedPython = join(bundledDir, 'python');
  const pythonExe = join(extractedPython, 'python.exe');

  if (!existsSync(pythonExe)) {
    console.error('ERROR: python.exe not found after extraction.');
    console.error('Expected at:', pythonExe);
    process.exit(1);
  }
  console.log(`  Python extracted: ${pythonExe}`);

  // Step 3: Create venv with bundled Python
  console.log('\nStep 3: Creating virtual environment...');
  const venvDir = join(pythonDir, 'venv');
  if (existsSync(venvDir)) {
    rmSync(venvDir, { recursive: true, force: true });
  }
  execSync(`"${pythonExe}" -m venv "${venvDir}"`, { stdio: 'inherit' });

  // Step 4: Install dependencies
  const pipExe = join(venvDir, 'Scripts', 'pip.exe');
  console.log('\nStep 4: Installing dependencies (this may take 10-20 minutes)...');
  execSync(`"${pipExe}" install --upgrade pip`, { stdio: 'inherit' });
  execSync(`"${pipExe}" install -r "${requirementsPath}"`, {
    stdio: 'inherit',
    env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' },
  });

  // Step 5: Create completion marker
  const markerPath = join(venvDir, '.setup_complete');
  writeFileSync(markerPath, JSON.stringify({
    completedAt: new Date().toISOString(),
    pythonVersion: PYTHON_VERSION,
    platform: 'win32',
    bundled: true,
  }));

  // Step 6: Clean up download
  rmSync(tarPath, { force: true });

  console.log('\n=== Bundle complete! ===');
  console.log(`  Bundled Python: ${extractedPython}`);
  console.log(`  Virtual env: ${venvDir}`);
  console.log(`\nThe venv is ready and will be included in the packaged app.`);
  console.log('Users will NOT need to download Python on first run.');
  console.log('\nNote: ML models still need to be downloaded on first run (~1.5 GB).');
  console.log('To also bundle models, run the app once to download them, then');
  console.log('the models/ folder under hf_cache/ will be included automatically.');
}

main().catch((err) => {
  console.error('Bundle failed:', err);
  process.exit(1);
});

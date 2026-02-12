# Contributing to AI Tourism Opinion Analyzer

Thank you for your interest in contributing! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Be respectful and constructive. We are committed to providing a welcoming and inclusive experience for everyone.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/<your-username>/AI-Tourism-Opinion-Analyzer.git
   cd AI-Tourism-Opinion-Analyzer
   ```

3. **Add the upstream remote:**

   ```bash
   git remote add upstream https://github.com/victorwkey/AI-Tourism-Opinion-Analyzer.git
   ```

## Development Setup

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**

### Install dependencies

```bash
npm install
```

### Set up Python environment

```bash
# On Windows
npm run setup:python

# On macOS/Linux
npm run setup:python:unix
```

### Run in development

```bash
npm run start
```

The first run will launch a setup wizard that handles Python, models, and Ollama installation.

## Project Structure

```
src/
├── main.ts                 # Electron main process entry
├── preload.ts              # Context bridge (IPC API)
├── renderer.ts             # React entry point
├── main/                   # Main process modules
│   ├── ipc/                # IPC handlers (app, files, pipeline, setup)
│   ├── python/             # Python bridge (JSON-RPC)
│   ├── setup/              # Setup wizard, installers
│   └── utils/              # Logger, store, auto-updater
├── renderer/               # React UI
│   ├── components/         # Reusable UI components
│   ├── pages/              # App pages (Home, Data, Pipeline, etc.)
│   └── stores/             # Zustand state management
├── shared/                 # Types and constants shared across processes
└── __tests__/              # Test files

python/                     # Python NLP backend
├── main.py                 # Bridge entry point
├── api_bridge.py           # JSON-RPC bridge
├── core/                   # 7-phase NLP pipeline
├── config/                 # Configuration
└── data/                   # Datasets and outputs
```

## Making Changes

1. **Create a branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** — follow the existing code style

3. **Commit with clear messages:**

   ```bash
   git commit -m "feat: add sentiment visualization export"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — new feature
   - `fix:` — bug fix
   - `docs:` — documentation changes
   - `style:` — formatting, no code change
   - `refactor:` — code restructuring
   - `test:` — adding/updating tests
   - `chore:` — maintenance tasks

## Testing

### Run tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch
```

### What to test

- **Zustand stores** — state transitions, actions, persistence
- **Shared constants/types** — validation of pipeline phases, configs
- **React components** — rendering, user interactions
- **IPC handlers** — request/response contracts

### Writing tests

Place test files next to the code they test or in `src/__tests__/`:

```typescript
// src/__tests__/myFeature.test.ts
import { describe, it, expect } from 'vitest';

describe('MyFeature', () => {
  it('should do something', () => {
    expect(true).toBe(true);
  });
});
```

## Submitting a Pull Request

1. **Push your branch** to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** against `main` on the upstream repo

3. **Fill in the PR template:**
   - Describe what changed and why
   - Reference any related issues
   - Include screenshots for UI changes

4. **Wait for review** — maintainers will review your PR and may request changes

## Reporting Issues

Use [GitHub Issues](https://github.com/victorwkey/AI-Tourism-Opinion-Analyzer/issues) to report bugs or request features.

### Bug reports should include

- OS and version (e.g., Windows 11 23H2)
- App version (Settings → About)
- Steps to reproduce
- Expected vs actual behavior
- Logs from `%APPDATA%/ai-tourism-analyzer-desktop/logs/main.log`

### Feature requests should include

- Clear description of the desired feature
- Use case / motivation
- Examples if applicable

---

Thank you for contributing!

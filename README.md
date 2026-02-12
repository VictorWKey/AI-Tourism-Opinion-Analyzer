# AI Tourism Opinion Analyzer

A desktop application that uses AI and NLP to analyze tourism reviews — extracting sentiments, topics, categories, and generating intelligent summaries.

![Electron](https://img.shields.io/badge/Electron-40-47848F?logo=electron&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Sentiment Analysis** — BERT-based multilingual sentiment classification
- **Subjectivity Detection** — Classify reviews as subjective or objective
- **Category Classification** — Multi-label tourism category tagging
- **Hierarchical Topic Modeling** — BERTopic-powered topic discovery with LLM enhancement
- **Intelligent Summarization** — LangChain + LLM-generated summaries
- **Interactive Visualizations** — Charts, dashboards, and exportable reports
- **Local LLM Support** — Runs with Ollama (Llama 3.2) for full privacy
- **Cloud LLM Support** — Optional OpenAI API integration

## Architecture

```
┌─────────────────────────────┐
│   Electron (Main Process)   │
│   ├── IPC Handlers          │
│   ├── Python Bridge         │
│   └── Setup Wizard          │
├─────────────────────────────┤
│   React (Renderer Process)  │
│   ├── Dashboard             │
│   ├── Pipeline Controls     │
│   └── Visualization Viewer  │
├─────────────────────────────┤
│   Python Backend             │
│   ├── 7-Phase NLP Pipeline  │
│   ├── HuggingFace Models    │
│   └── Ollama / OpenAI LLM  │
└─────────────────────────────┘
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+ (auto-installed on first run if missing)
- **Ollama** (optional, for local LLM — auto-installed via setup wizard)

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/victorwkey/AI-Tourism-Opinion-Analyzer.git
cd AI-Tourism-Opinion-Analyzer
npm install
```

### 2. Run in development

```bash
npm run start
```

The first run will launch a **setup wizard** that:
1. Checks/installs Python 3.11
2. Creates a virtual environment and installs dependencies
3. Downloads required ML models (~1.5 GB)
4. Optionally installs Ollama + a local LLM model

### 3. Build for production

```bash
# Package the app
npm run package

# Create distributable installer (.exe on Windows)
npm run make
```

The installer will be in `out/make/squirrel.windows/x64/`.

## Project Structure

```
├── src/                    # Electron + React frontend
│   ├── main.ts             # Electron main process
│   ├── preload.ts          # Context bridge
│   ├── renderer.ts         # React entry point
│   ├── main/               # Main process modules
│   │   ├── ipc/            # IPC handlers
│   │   ├── python/         # Python bridge
│   │   └── setup/          # First-run setup wizard
│   └── renderer/           # React UI
│       ├── components/     # Reusable UI components
│       ├── pages/          # App pages
│       └── stores/         # Zustand state management
├── python/                 # Python NLP backend
│   ├── main.py             # Bridge entry point
│   ├── api_bridge.py       # JSON-RPC bridge
│   ├── core/               # 7-phase analysis pipeline
│   └── config/             # Configuration
├── resources/              # App resources (icons, etc.)
└── forge.config.ts         # Electron Forge config
```

## NLP Pipeline Phases

| Phase | Name | Description | Requires LLM |
|-------|------|-------------|:---:|
| 1 | Basic Processing | Clean and preprocess dataset | No |
| 2 | Sentiment Analysis | BERT multilingual sentiment | No |
| 3 | Subjectivity Analysis | Subjective vs objective classification | No |
| 4 | Category Classification | Multi-label tourism categories | No |
| 5 | Hierarchical Topics | BERTopic + LLM topic modeling | Yes |
| 6 | Intelligent Summary | LangChain summarization | Yes |
| 7 | Visualizations | Charts and dashboard generation | No |

## Tech Stack

**Frontend:** Electron 40, React 19, TypeScript, Tailwind CSS, Radix UI, Recharts, Zustand

**Backend:** Python 3.11, PyTorch, Transformers, BERTopic, LangChain, sentence-transformers

**LLM:** Ollama (local) or OpenAI API (cloud)

## Scripts

| Command | Description |
|---------|-------------|
| `npm run start` | Run in development mode |
| `npm run package` | Package the app |
| `npm run make` | Create platform installer |
| `npm run make:win` | Create Windows installer |
| `npm run lint` | Run ESLint |

## License

[MIT](LICENSE)

## Author

**victorwkey** — [victorwkey@gmail.com](mailto:victorwkey@gmail.com)

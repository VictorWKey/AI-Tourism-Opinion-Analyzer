# Changelog

All notable changes to TourlyAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Sentry error reporting for crash tracking
- Custom uninstall handler with user-selectable cleanup
- Multi-platform CI builds (macOS, Linux)
- GitHub Pages landing page
- Comprehensive test suite for stores, constants, and types
- CHANGELOG.md, CONTRIBUTING.md, PRIVACY.md documentation

## [1.0.0] - 2026-02-11

### Added
- 7-phase NLP pipeline for review analysis
  - Phase 1: Basic text processing and cleaning
  - Phase 2: BERT-based multilingual sentiment analysis
  - Phase 3: Subjectivity detection
  - Phase 4: Multi-label tourism category classification
  - Phase 5: Hierarchical topic modeling (BERTopic + LLM)
  - Phase 6: Intelligent summarization (LangChain + LLM)
  - Phase 7: Visualization and report generation
- Electron desktop application with React UI
- Interactive dashboard with charts (Recharts)
- Drag-and-drop dataset loading (CSV, Excel)
- Setup wizard with automatic dependency installation
  - Python 3.11 auto-install
  - Virtual environment creation
  - HuggingFace model downloads (~2.5 GB)
  - Ollama local LLM installation (optional)
- Local LLM support via Ollama (Llama 3.2)
- Cloud LLM support via OpenAI API
- Auto-updater via GitHub Releases
- Pipeline rollback and backup system
- Exportable visualizations and insights
- Windows installer (Squirrel)
- Light theme UI with Tailwind CSS + Radix UI

### Security
- Context isolation and sandbox enabled
- Electron Fuses configured (no Node CLI, cookie encryption)
- ASAR packaging enabled
- API keys encrypted in electron-store

[Unreleased]: https://github.com/victorwkey/AI-Tourism-Opinion-Analyzer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/victorwkey/AI-Tourism-Opinion-Analyzer/releases/tag/v1.0.0

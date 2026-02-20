# Privacy Policy

**TourlyAI**
Last updated: February 11, 2026

## Overview

TourlyAI is a desktop application designed for offline-first, privacy-respecting analysis of reviews. We are committed to protecting your privacy.

## Data Collection

### What We Do NOT Collect

- **Your datasets** — All CSV/Excel files you load are processed entirely on your local machine. No data is uploaded to any server.
- **Your analysis results** — Sentiments, topics, categories, summaries, and visualizations are stored locally on your computer.
- **Personal information** — We do not collect names, emails, IP addresses, or any personally identifiable information during normal use.

### What We Collect (Optional)

- **Crash reports** — If you opt in, anonymous error reports may be sent to our error tracking service (Sentry) to help us fix bugs. These reports include:
  - Error message and stack trace
  - App version and OS version
  - No personal data or dataset contents

- **Update checks** — The app periodically checks GitHub Releases for updates. This is a standard HTTPS request to GitHub's public API and does not transmit any personal data.

### Third-Party Services

- **Ollama (Local LLM)** — When using the local LLM option, all AI processing happens on your machine. No data leaves your computer.
- **OpenAI API (Optional)** — If you choose to use the OpenAI API mode, your text data will be sent to OpenAI's servers for processing. This is entirely optional and clearly indicated in the settings. Please review [OpenAI's Privacy Policy](https://openai.com/policies/privacy-policy).
- **HuggingFace Models** — ML models are downloaded from HuggingFace Hub during initial setup. Only standard HTTP download requests are made; no user data is transmitted.

## Data Storage

All application data is stored locally on your computer:

| Data | Location |
|------|----------|
| App settings | `%APPDATA%\ai-tourism-analyzer-desktop\` |
| Logs | `%APPDATA%\ai-tourism-analyzer-desktop\logs\` |
| Datasets & results | Your chosen output directory |
| ML models | `python\models\hf_cache\` (within app directory) |
| Ollama models | `%USERPROFILE%\.ollama\` |

## Data Deletion

You can delete all app data at any time:

- **Uninstall the app** — The uninstaller will offer to remove all external data (settings, Ollama, models)
- **Manual cleanup** — Follow the instructions in `RESET_SETUP.md`

## Children's Privacy

This application is not directed at children under 13. We do not knowingly collect information from children.

## Changes to This Policy

We may update this Privacy Policy from time to time. Changes will be noted in the [CHANGELOG](CHANGELOG.md) and reflected in the "Last updated" date above.

## Contact

If you have questions about this Privacy Policy, please open an issue on our [GitHub repository](https://github.com/victorwkey/TourlyAI/issues).

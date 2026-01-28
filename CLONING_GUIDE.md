# 📦 Cloning Guide - Large Files & Dependencies

## ⚠️ What You Need to Save/Download

### 🔴 **CRITICAL - Must Save Before Cloning** (1.3 GB)

#### 1. **ML Models** (`python/models/`)
- **Size:** ~1.3 GB total
- **Location:** `python/models/`
- **Files:**
  - `multilabel_task/best_model/model.safetensors` (639 MB)
  - `subjectivity_task/best_model/model.safetensors` (639 MB)
  - Plus their config files (tokenizers, vocab, etc.)

**⚠️ These are NOT in git** (excluded via `.gitignore`)

**How to save:**
```bash
# Compress models folder
cd python
tar -czf models_backup.tar.gz models/

# Or copy to external drive/cloud
cp -r models/ /path/to/backup/
```

---

### 🟡 **Optional - Can be Re-downloaded**

#### 2. **Node Modules** (`node_modules/`)
- **Size:** ~706 MB
- **Regenerate:** `npm install`
- **Don't save** - always excluded from git

#### 3. **Ollama LLM Models** (System-wide)
- **Size:** 2-6 GB per model (llama3.2:3b, etc.)
- **Location:** `~/.ollama/models/` (Linux/Mac) or `%USERPROFILE%\.ollama\models\` (Windows)
- **Reinstall:** 
  ```bash
  ollama pull llama3.2:3b
  ```

#### 4. **Data Files** (`python/data/`)
- **Size:** ~28 MB
- **Contents:**
  - `dataset.csv` - Your tourism reviews dataset
  - `visualizaciones/` - Generated charts
  - `shared/` - Analysis results (JSON)
- **Save if:** Contains your custom data

---

## 🚀 Setup on New PC

### Step 1: Clone Repository
```bash
git clone <your-repo-url>
cd ai-tourism-analyzer-desktop
```

### Step 2: Restore ML Models ⚠️ **REQUIRED**
```bash
# Option A: From backup
cd python
tar -xzf models_backup.tar.gz

# Option B: Copy from external drive
cp -r /path/to/backup/models/ python/
```

### Step 3: Install Dependencies
```bash
# Node.js dependencies (706 MB download)
npm install

# Python dependencies
cd python
pip install -r requirements.txt
```

### Step 4: Setup Ollama (Optional - for local LLM)
```bash
cd python
./scripts/setup_local_llm_completo.sh
# Or manually:
# ollama pull llama3.2:3b
```

### Step 5: Configure Environment
```bash
cd python
cp .env.example .env
# Edit .env with your settings
```

---

## 📁 Directory Sizes Summary

| Directory | Size | In Git? | Need to Save? |
|-----------|------|---------|---------------|
| `python/models/` | 1.3 GB | ❌ No | ✅ **YES** |
| `node_modules/` | 706 MB | ❌ No | ❌ No (reinstall) |
| `python/data/` | 28 MB | ⚠️ Partial | ⚠️ If custom data |
| Ollama models | 2-6 GB | ❌ No | ❌ No (re-download) |

---

## 💾 Quick Backup Command

```bash
# Create complete backup of non-git large files
cd ai-tourism-analyzer-desktop
tar -czf project_backup.tar.gz \
    python/models/ \
    python/data/dataset.csv \
    python/data/shared/ \
    .env

# Total size: ~1.3 GB compressed
```

## 📤 Quick Restore Command

```bash
# On new PC after cloning
cd ai-tourism-analyzer-desktop
tar -xzf project_backup.tar.gz

# Then install dependencies
npm install
cd python && pip install -r requirements.txt
```

---

## 🎯 TL;DR - Minimum Required

**Must save and transfer:**
- ✅ `python/models/` folder (1.3 GB) - **CRITICAL**
- ✅ `.env` file (if configured)
- ✅ `python/data/dataset.csv` (if custom data)

**Everything else can be reinstalled via npm/pip/ollama.**

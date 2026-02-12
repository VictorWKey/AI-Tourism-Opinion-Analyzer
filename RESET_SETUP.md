# Reset Setup - Volver a Configuración Inicial

```powershell
# 0. Detener procesos
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Stop-Process -Name "ollama*" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 1. Eliminar entorno virtual de Python (incluye marcadores de instalación)
Remove-Item -Recurse -Force "python\venv" -ErrorAction SilentlyContinue

# 2. Eliminar caché de modelos HuggingFace
Remove-Item -Path "python\models\hf_cache" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Restaurar dataset.csv original (las fases 1-5 modifican este archivo agregando columnas)
git checkout python/data/dataset.csv

# 4. Eliminar datos generados por el pipeline
Remove-Item -Path "python\data\shared\categorias_scores.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "python\data\shared\resumenes.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "python\data\.backups" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "python\data\visualizaciones" -Recurse -Force -ErrorAction SilentlyContinue

# 5. Eliminar estado del setup y configuración de la app (electron-store)
Remove-Item "$env:APPDATA\AI Tourism Opinion Analyzer\setup-state.json" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\AI Tourism Opinion Analyzer\ai-tourism-analyzer-config.json" -Force -ErrorAction SilentlyContinue

# 6. Eliminar estado de pipeline/fases y datos (Zustand persisted en Local Storage y Session Storage)
Remove-Item -Path "$env:APPDATA\AI Tourism Opinion Analyzer\Local Storage" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\AI Tourism Opinion Analyzer\Session Storage" -Recurse -Force -ErrorAction SilentlyContinue

# 7. Desinstalar Ollama
Remove-Item -Path "$env:LOCALAPPDATA\Programs\Ollama" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\.ollama" -Recurse -Force -ErrorAction SilentlyContinue
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', $null, 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', $null, 'User')
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = ($currentPath -split ';' | Where-Object { $_ -notlike "*Ollama*" }) -join ';'
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'User')

# 8. Limpiar caché de Python
Get-ChildItem -Path "python" -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force

Write-Host "✓ Reset completo realizado" -ForegroundColor Green
```

## ⚠️ INFORMACIÓN IMPORTANTE: Instalación de Ollama

**Este proyecto está diseñado para instalar Ollama en Windows nativo**, pero debido a un error en versiones anteriores, es posible que Ollama se haya instalado en WSL (Windows Subsystem for Linux).

### ¿Dónde debería estar instalado Ollama?

✅ **CORRECTO (Windows nativo):**
- Ubicación: `C:\Users\<Usuario>\AppData\Local\Programs\Ollama\`
- Comando para verificar: `where ollama` → Muestra ruta de Windows con `\`

❌ **INCORRECTO (WSL - versiones antiguas del setup):**
- Ubicación: `/usr/local/bin/ollama` (dentro de WSL)
- Comando para verificar: `wsl -- which ollama` → Muestra ruta de Linux con `/`

**¿Por qué WSL?** En versiones anteriores del proyecto, la instalación podía haber usado scripts de Linux que instalaban Ollama en WSL en lugar de Windows. Esto se ha corregido en la versión actual.

---

## Pasos para reiniciar el setup de la aplicación

### 0. Detener la aplicación primero (IMPORTANTE)
```powershell
# Cierra la ventana de la aplicación o presiona Ctrl+C en la terminal de npm start
# Luego mata cualquier proceso Python residual:
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
```

### 1. Eliminar el entorno virtual de Python (opcional)
```powershell
# Asegúrate de estar en la raíz del proyecto
Remove-Item -Recurse -Force "python\venv"

# Si falla, usa este comando más agresivo:
# Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force ; Start-Sleep -Seconds 2 ; Remove-Item -Recurse -Force "python\venv"
```

### 2. Eliminar el estado del setup y configuración
```powershell
# Eliminar estado de setup (wizard completado, pythonReady, ollamaInstalled, etc.)
Remove-Item "$env:APPDATA\AI Tourism Opinion Analyzer\setup-state.json" -Force -ErrorAction SilentlyContinue

# Eliminar configuración de la app (LLM settings, output dir, grid layouts, recent files)
Remove-Item "$env:APPDATA\AI Tourism Opinion Analyzer\ai-tourism-analyzer-config.json" -Force -ErrorAction SilentlyContinue
```

### 2b. Eliminar estado de fases del pipeline (IMPORTANTE)
```powershell
# Las fases (completadas/pendientes), el dataset cargado, y rutas de resultados
# se guardan en Zustand persist (Local Storage del navegador Electron).
# Sin esto, la app "recuerda" que las fases ya se ejecutaron.
Remove-Item -Path "$env:APPDATA\AI Tourism Opinion Analyzer\Local Storage" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\AI Tourism Opinion Analyzer\Session Storage" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✓ Estado de setup, config y fases eliminado" -ForegroundColor Green
```

### 3. Si usabas Ollama - Desinstalar Ollama (opcional pero recomendado)

```powershell
# Detener cualquier proceso de Ollama
Stop-Process -Name "ollama*" -Force -ErrorAction SilentlyContinue

# Eliminar el directorio de instalación
Remove-Item -Path "$env:LOCALAPPDATA\Programs\Ollama" -Recurse -Force -ErrorAction SilentlyContinue

# Eliminar modelos y configuración
Remove-Item -Path "$env:USERPROFILE\.ollama" -Recurse -Force -ErrorAction SilentlyContinue

# Limpiar variables de entorno (opcional)
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', $null, 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', $null, 'User')

# Limpiar PATH (eliminar referencia a Ollama)
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = ($currentPath -split ';' | Where-Object { $_ -notlike "*Ollama*" }) -join ';'
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'User')

Write-Host "✓ Ollama eliminado completamente de Windows" -ForegroundColor Green
```

### 4. Limpiar caché de modelos (opcional pero recomendado)

```powershell
# Eliminar el directorio local de modelos descargados
Remove-Item -Path "python\models\hf_cache" -Recurse -Force -ErrorAction SilentlyContinue

# Esto eliminará los siguientes modelos descargados:
# - nlptown/bert-base-multilingual-uncased-sentiment (~670 MB)
# - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (~470 MB)
# - victorwkey/tourism-subjectivity-bert (~670 MB)
# - victorwkey/tourism-categories-bert (~670 MB)

Write-Host "✓ Caché local de modelos eliminado" -ForegroundColor Green
```

**⚠️ NOTA:** Si eliminas el caché, la primera ejecución de la aplicación descargará los modelos nuevamente (~2.5 GB). Los modelos se descargarán automáticamente durante el setup inicial.

### 5. Limpiar datos generados por el pipeline (recomendado)

```powershell
# IMPORTANTE: Restaurar el dataset.csv original
# Las fases 1-5 modifican dataset.csv agregando columnas de análisis.
# Sin restaurarlo, la app detecta columnas previas y puede saltar fases.
git checkout python/data/dataset.csv
Write-Host "✓ dataset.csv restaurado al original" -ForegroundColor Green

# Eliminar datos compartidos generados por las fases 4 y 6
Remove-Item -Path "python\data\shared\categorias_scores.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "python\data\shared\resumenes.json" -Force -ErrorAction SilentlyContinue

# Eliminar visualizaciones generadas por la fase 7
# (todas las imágenes PNG, insights_textuales.json y reporte_generacion.json)
Remove-Item -Path "python\data\visualizaciones" -Recurse -Force -ErrorAction SilentlyContinue

# Eliminar backups de rollback
Remove-Item -Path "python\data\.backups" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✓ Datos generados eliminados" -ForegroundColor Green
```

**NOTA:** `git checkout python/data/dataset.csv` restaura el CSV al estado original del repositorio. Si no usas git, necesitarás una copia limpia del archivo.

### 6. Limpiar caché de Python

```powershell
# Eliminar todos los __pycache__ y archivos .pyc
Get-ChildItem -Path "python" -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force

Write-Host "✓ Caché de Python eliminado" -ForegroundColor Green
```

### 7. Limpiar configuración de la app (opcional)

```powershell
# Eliminar TODA la configuración persistida (LLM, output dir, historial de archivos,
# estado de fases, datos del pipeline, grid layouts, y cachés de Electron)
Remove-Item -Path "$env:APPDATA\AI Tourism Opinion Analyzer" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✓ Configuración de la app eliminada" -ForegroundColor Green
```

### 8. Limpiar dependencias de desarrollo (solo devs)

```powershell
# Eliminar node_modules (se reinstala con npm install)
Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction SilentlyContinue

# Eliminar artifacts de build
Remove-Item -Path "out" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".vite" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✓ Dependencias de desarrollo eliminadas" -ForegroundColor Green
```

### 9. Reiniciar la aplicación


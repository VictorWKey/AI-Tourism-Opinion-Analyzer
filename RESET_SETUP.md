# Reset Setup - Volver a Configuración Inicial


#Remove-Item -Recurse -Force "python\venv"
Remove-Item -Path "$env:USERPROFILE\.cache\huggingface" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Users\Usuario\AppData\Roaming\ai-tourism-analyzer-desktop\setup-state.json" -Force
Stop-Process -Name "ollama*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Programs\Ollama" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\.ollama" -Recurse -Force -ErrorAction SilentlyContinue
[System.Environment]::SetEnvironmentVariable('OLLAMA_MODELS', $null, 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', $null, 'User')
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = ($currentPath -split ';' | Where-Object { $_ -notlike "*Ollama*" }) -join ';'
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
Write-Host "✓ Ollama eliminado completamente de Windows" -ForegroundColor Green

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

### 2. Eliminar el estado del setup
```powershell
Remove-Item "C:\Users\Usuario\AppData\Roaming\ai-tourism-analyzer-desktop\setup-state.json" -Force
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
# Eliminar el directorio de caché de HuggingFace (modelos descargados)
Remove-Item -Path "$env:USERPROFILE\.cache\huggingface" -Recurse -Force -ErrorAction SilentlyContinue

# Esto eliminará los siguientes modelos descargados:
# - nlptown/bert-base-multilingual-uncased-sentiment (639 MB)
# - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (457 MB)
# - sentence-transformers/all-MiniLM-L6-v2 (87 MB) - antiguo

Write-Host "✓ Caché de modelos eliminado" -ForegroundColor Green
```

**⚠️ NOTA:** Si eliminas el caché, la primera ejecución de la aplicación descargará los modelos nuevamente (~1.1 GB). Los modelos se descargarán automáticamente cuando se ejecute por primera vez.

### 5. Reiniciar la aplicación


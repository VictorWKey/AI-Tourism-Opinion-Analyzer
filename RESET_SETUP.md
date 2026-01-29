# Reset Setup - Volver a Configuración Inicial

## Pasos para reiniciar el setup de la aplicación

### 1. Eliminar el entorno virtual de Python (opcional)
```powershell
Remove-Item -Recurse -Force "python\venv"
```

### 2. Eliminar el estado del setup
```powershell
Remove-Item "C:\Users\Usuario\AppData\Roaming\ai-tourism-analyzer-desktop\setup-state.json" -Force
```

### 3. Si usabas Ollama - Desinstalar Ollama (opcional pero recomendado)

#### Opción A: Desinstalación completa de Ollama
1. **Desinstalar Ollama desde Windows:**
   ```powershell
   # Buscar "Agregar o quitar programas" > "Ollama" > Desinstalar
   # O usar el desinstalador:
   Start-Process "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\Uninstall Ollama.exe"
   ```

2. **Eliminar modelos descargados (libera espacio):**
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.ollama"
   ```

#### Opción B: Solo eliminar modelos (mantener Ollama instalado)
```powershell
# Listar modelos instalados
ollama list

# Eliminar modelos específicos
ollama rm llama3.2:3b
ollama rm <nombre-del-modelo>

# O eliminar todos los modelos manualmente
Remove-Item -Recurse -Force "$env:USERPROFILE\.ollama\models"
```

### 4. Eliminar configuración de la aplicación (opcional)
```powershell
# Elimina toda la configuración guardada (LLM settings, preferencias, etc.)
Remove-Item -Recurse -Force "$env:APPDATA\ai-tourism-analyzer-desktop"
```

### 5. Reiniciar la aplicación
```powershell
npm start
```

## Notas
- El wizard de setup aparecerá automáticamente al reiniciar
- El entorno Python se recreará desde cero corrigiendo errores de dependencias
- **Si cambias de Ollama a API**: Considera desinstalar Ollama para liberar espacio (~10+ GB de modelos)
- **Si cambias de API a Ollama**: El setup wizard instalará Ollama automáticamente
- Asegúrate de seleccionar la opción correcta (API vs Ollama) en el wizard

## Reset Rápido (solo configuración)

Si solo quieres cambiar entre API y Ollama sin reinstalar todo:

1. **Ve a Settings en la aplicación**
2. **Cambia LLM Mode** entre `api` y `local`
3. **Reinicia la aplicación** (Ctrl+C y `npm start`)

Esto **no** requiere desinstalar Ollama ni eliminar el entorno Python.

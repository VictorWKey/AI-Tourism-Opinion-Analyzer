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

### 3. Reiniciar la aplicación
```powershell
npm start
```

## Notas
- El wizard de setup aparecerá automáticamente al reiniciar
- El entorno Python se recreará desde cero corrigiendo errores de dependencias
- Asegúrate de seleccionar la opción correcta (API vs Ollama) en el wizard

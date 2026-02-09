"""
Configuración del Sistema
=========================
Define configuraciones globales para el pipeline de análisis.
"""

import os
from pathlib import Path


class ConfigLLM:
    """
    Configuración para selección de LLM (API o Local).
    
    Modos disponibles:
    - 'api': Usa OpenAI API (requiere OPENAI_API_KEY)
    - 'local': Usa Ollama localmente (requiere Ollama instalado)
    
    Para cambiar el modo, establece la variable de entorno LLM_MODE
    o modifica directamente LLM_MODE_DEFAULT.
    """
    
    # Modo por defecto (puede ser sobreescrito por variable de entorno)
    LLM_MODE_DEFAULT = 'local'  # 'api' o 'local'
    
    # Obtener modo desde variable de entorno o usar default
    LLM_MODE = os.getenv('LLM_MODE', LLM_MODE_DEFAULT).lower()
    
    # Validar modo
    if LLM_MODE not in ['api', 'local']:
        raise ValueError(
            f"LLM_MODE inválido: '{LLM_MODE}'. "
            "Valores válidos: 'api' o 'local'"
        )
    
    # Configuración para API (OpenAI)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Configuración para Local (Ollama)
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    
    # Parámetros compartidos
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0'))
    
    @classmethod
    def validar_configuracion(cls):
        """Valida que la configuración sea correcta según el modo seleccionado."""
        if cls.LLM_MODE == 'api':
            if not cls.OPENAI_API_KEY:
                raise ValueError(
                    "Modo 'api' seleccionado pero OPENAI_API_KEY no está configurado. "
                    "Agrega tu clave en el archivo .env o como variable de entorno."
                )
        elif cls.LLM_MODE == 'local':
            # Validación de Ollama se hace al intentar conectar
            pass
        
        return True
    
    @classmethod
    def get_info(cls):
        """Retorna información sobre la configuración actual."""
        info = {
            'modo': cls.LLM_MODE,
            'temperatura': cls.LLM_TEMPERATURE
        }
        
        if cls.LLM_MODE == 'api':
            info['modelo'] = cls.OPENAI_MODEL
            info['api_key_configurada'] = bool(cls.OPENAI_API_KEY)
        else:
            info['modelo'] = cls.OLLAMA_MODEL
            info['base_url'] = cls.OLLAMA_BASE_URL
        
        return info


class ConfigDataset:
    """Configuración de rutas de datos."""
    
    # Get the python directory (parent of config directory)
    PRODUCTION_DIR = Path(__file__).parent.parent
    DATA_DIR = PRODUCTION_DIR / 'data'
    MODELS_DIR = PRODUCTION_DIR / 'models'
    
    # Archivos principales
    DATASET_PATH = DATA_DIR / 'dataset.csv'
    SHARED_DIR = DATA_DIR / 'shared'
    
    # Local cache directory for HuggingFace models (bundled with the app)
    # All models are downloaded here instead of the global ~/.cache/huggingface
    MODELS_CACHE_DIR = MODELS_DIR / 'hf_cache'
    
    # HuggingFace model IDs (downloaded from cloud into MODELS_CACHE_DIR)
    SENTIMENT_MODEL_ID = 'nlptown/bert-base-multilingual-uncased-sentiment'
    EMBEDDINGS_MODEL_ID = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    MULTILABEL_MODEL_ID = 'victorwkey/tourism-categories-bert'
    SUBJECTIVITY_MODEL_ID = 'victorwkey/tourism-subjectivity-bert'
    
    # Local threshold files (optional, models have default thresholds)
    MULTILABEL_THRESHOLDS_PATH = MODELS_DIR / 'multilabel_task' / 'optimal_thresholds.json'
    SUBJECTIVITY_THRESHOLDS_PATH = MODELS_DIR / 'subjectivity_task' / 'optimal_thresholds.json'
    
    @classmethod
    def get_models_cache_dir(cls) -> str:
        """Returns the absolute path to the local models cache directory as a string."""
        cls.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return str(cls.MODELS_CACHE_DIR)
    
    @classmethod
    def crear_directorios(cls):
        """Crea los directorios necesarios si no existen."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.SHARED_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

"""
Proveedor de LLM Abstracto
===========================
Proporciona una interfaz unificada para usar LLMs (API o Local).
"""

from typing import Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel

from config import ConfigLLM


class LLMProvider:
    """
    Proveedor abstracto de LLM que soporta múltiples backends.
    
    Soporta:
    - OpenAI API (mediante langchain_openai)
    - Ollama Local (mediante langchain_ollama)
    """
    
    _instance = None
    _llm = None
    
    def __new__(cls):
        """Implementa patrón Singleton para reutilizar la conexión."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el proveedor si aún no se ha hecho."""
        if self._llm is None:
            self._inicializar_llm()
    
    def _inicializar_llm(self):
        """Inicializa el modelo LLM según la configuración."""
        # Validar configuración
        ConfigLLM.validar_configuracion()
        
        if ConfigLLM.LLM_MODE == 'api':
            self._inicializar_openai()
        elif ConfigLLM.LLM_MODE == 'local':
            self._inicializar_ollama()
        else:
            raise ValueError(f"Modo LLM no soportado: {ConfigLLM.LLM_MODE}")
    
    def _inicializar_openai(self):
        """Inicializa el modelo OpenAI."""
        try:
            from langchain_openai import ChatOpenAI
            
            self._llm = ChatOpenAI(
                model=ConfigLLM.OPENAI_MODEL,
                temperature=ConfigLLM.LLM_TEMPERATURE,
                api_key=ConfigLLM.OPENAI_API_KEY
            )
            
            print(f"   ✓ LLM inicializado: OpenAI ({ConfigLLM.OPENAI_MODEL})")
            
        except ImportError:
            raise ImportError(
                "langchain_openai no está instalado. "
                "Instala con: pip install langchain-openai"
            )
        except Exception as e:
            raise RuntimeError(f"Error al inicializar OpenAI: {e}")
    
    def _inicializar_ollama(self):
        """Inicializa el modelo Ollama local."""
        try:
            from langchain_ollama import ChatOllama
            
            self._llm = ChatOllama(
                model=ConfigLLM.OLLAMA_MODEL,
                temperature=ConfigLLM.LLM_TEMPERATURE,
                base_url=ConfigLLM.OLLAMA_BASE_URL
            )
            
            # Validar que Ollama esté disponible
            self._validar_ollama()
            
            print(f"   ✓ LLM inicializado: Ollama ({ConfigLLM.OLLAMA_MODEL})")
            
        except ImportError:
            raise ImportError(
                "langchain_ollama no está instalado. "
                "Instala con: pip install langchain-ollama"
            )
        except Exception as e:
            raise RuntimeError(
                f"Error al inicializar Ollama: {e}\n\n"
                f"Asegúrate de que:\n"
                f"1. Ollama está instalado (https://ollama.ai)\n"
                f"2. Ollama está ejecutándose (ollama serve)\n"
                f"3. El modelo '{ConfigLLM.OLLAMA_MODEL}' está descargado "
                f"(ollama pull {ConfigLLM.OLLAMA_MODEL})"
            )
    
    def _validar_ollama(self):
        """Valida que Ollama esté disponible y el modelo descargado."""
        try:
            # Hacer una llamada de prueba simple
            test_response = self._llm.invoke("Responde solo con 'OK'")
            if not test_response:
                raise RuntimeError("Ollama no respondió correctamente")
        except Exception as e:
            raise RuntimeError(
                f"No se pudo conectar con Ollama: {e}\n\n"
                f"Pasos para solucionar:\n"
                f"1. Instala Ollama: https://ollama.ai\n"
                f"2. Inicia el servidor: ollama serve\n"
                f"3. Descarga el modelo: ollama pull {ConfigLLM.OLLAMA_MODEL}\n"
                f"4. Verifica que esté ejecutándose en: {ConfigLLM.OLLAMA_BASE_URL}"
            )
    
    def get_llm(self) -> BaseChatModel:
        """
        Retorna la instancia del LLM configurado.
        
        Returns:
            Instancia de BaseChatModel (ChatOpenAI o ChatOllama)
        """
        return self._llm
    
    def crear_chain_simple(self, template: str, **kwargs) -> Any:
        """
        Crea una cadena simple de LLM con template y parser de texto.
        
        Args:
            template: Template del prompt (puede incluir variables con {variable})
            **kwargs: Variables para partial_variables del template
            
        Returns:
            Chain ejecutable (template | llm | parser)
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                var for var in self._extraer_variables(template)
                if var not in kwargs
            ],
            partial_variables=kwargs
        )
        
        parser = StrOutputParser()
        chain = prompt | self._llm | parser
        
        return chain
    
    def crear_chain_estructurado(
        self, 
        template: str, 
        pydantic_model: type[BaseModel],
        **kwargs
    ) -> Any:
        """
        Crea una cadena de LLM con salida estructurada (Pydantic).
        
        Args:
            template: Template del prompt
            pydantic_model: Modelo Pydantic para parsear la salida
            **kwargs: Variables para partial_variables del template
            
        Returns:
            Chain ejecutable con parser estructurado
        """
        parser = PydanticOutputParser(pydantic_object=pydantic_model)
        
        # Agregar format_instructions al template si no está
        if 'format_instructions' not in kwargs:
            kwargs['format_instructions'] = parser.get_format_instructions()
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                var for var in self._extraer_variables(template)
                if var not in kwargs
            ],
            partial_variables=kwargs
        )
        
        chain = prompt | self._llm | parser
        
        return chain
    
    def _extraer_variables(self, template: str) -> list[str]:
        """Extrae las variables del template."""
        import re
        return list(set(re.findall(r'\{(\w+)\}', template)))
    
    @staticmethod
    def get_info() -> dict:
        """Retorna información sobre la configuración del LLM."""
        return ConfigLLM.get_info()
    
    @staticmethod
    def cambiar_modo(modo: str):
        """
        Cambia el modo del LLM y reinicializa.
        
        Args:
            modo: 'api' o 'local'
        """
        if modo not in ['api', 'local']:
            raise ValueError(f"Modo inválido: {modo}. Usa 'api' o 'local'")
        
        ConfigLLM.LLM_MODE = modo
        
        # Reinicializar singleton
        LLMProvider._instance = None
        LLMProvider._llm = None
        
        return LLMProvider()


# Función de conveniencia para obtener el LLM
def get_llm() -> BaseChatModel:
    """
    Función de conveniencia para obtener el LLM configurado.
    
    Returns:
        Instancia del LLM (ChatOpenAI o ChatOllama)
    """
    provider = LLMProvider()
    return provider.get_llm()


# Función para crear chains fácilmente
def crear_chain(template: str, pydantic_model: Optional[type[BaseModel]] = None, **kwargs):
    """
    Crea una cadena de LLM (simple o estructurada).
    
    Args:
        template: Template del prompt
        pydantic_model: Modelo Pydantic (opcional) para salida estructurada
        **kwargs: Variables para partial_variables
        
    Returns:
        Chain ejecutable
    """
    provider = LLMProvider()
    
    if pydantic_model:
        return provider.crear_chain_estructurado(template, pydantic_model, **kwargs)
    else:
        return provider.crear_chain_simple(template, **kwargs)

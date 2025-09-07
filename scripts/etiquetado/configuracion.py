"""
Configuración y modelos para la clasificación de subjetividad.
"""

import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


class SubjectivityClassification(BaseModel):
    """Modelo para la clasificación de subjetividad de reseñas turísticas"""
    
    categoria: Literal["Objetiva", "Subjetiva", "Mixta"] = Field(
        description="Categoría de clasificación de la reseña"
    )


def verificar_api_key():
    """
    Verifica que la API key de OpenAI esté configurada correctamente.
    
    Returns:
        bool: True si la API key está configurada, False en caso contrario
    """
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Advertencia: OPENAI_API_KEY no encontrada en .env")
        print("Asegúrate de crear un archivo .env con tu API key de OpenAI")
        return False
    else:
        print("✅ API key de OpenAI cargada correctamente")
        return True


def configurar_clasificador():
    """
    Configura el modelo GPT-4o-mini con LangChain para clasificación estructurada.
    
    Returns:
        RunnableSequence: Cadena de procesamiento configurada para clasificación
    """
    # Inicializar el modelo
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,  # Deterministic output para consistencia
        max_tokens=50   # Solo necesitamos una palabra de respuesta
    )
    
    # Configurar el parser para output estructurado
    parser = PydanticOutputParser(pydantic_object=SubjectivityClassification)
    
    # Definir el prompt template
    prompt_template = """Clasifica la siguiente reseña turística en una de tres categorías:

1) Objetiva: contiene únicamente hechos verificables, datos concretos o información medible (horarios, distancias, servicios, retrasos, cambios de estado).  
2) Subjetiva: contiene opiniones, juicios personales, sentimientos o percepciones del turista.  
3) Mixta: combina hechos verificables con opiniones o percepciones del turista.

Reglas importantes:  
- Devuelve SOLO la categoría correcta: "Objetiva", "Subjetiva" o "Mixta".  
- Si la reseña contiene un hecho verificable acompañado de una opinión o emoción, clasifícala como Mixta.  
- Ignora opiniones vagas o generalizaciones sin hechos (cuentan como Subjetiva).  
- No agregues explicaciones, comentarios ni texto adicional.  
- Sé lo más preciso posible, minimizando errores.

{format_instructions}

Reseña: "{review}"
"""
    
    # Crear el prompt template
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["review"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Crear la cadena de procesamiento
    chain = prompt | llm | parser
    
    return chain

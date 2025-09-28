from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

class TopicLabel(BaseModel):
    topic_id: int = Field(..., description="ID del tópico")
    label: str = Field(..., description="Etiqueta descriptiva para el tópico")

class TopicsOutput(BaseModel):
    topics: List[TopicLabel] = Field(..., description="Lista de tópicos con sus etiquetas")

def configurar_clasificador_topicos():
    llm = ChatOpenAI(
        model="gpt-4.1-nano-2025-04-14",
        temperature=0
    )
    
    parser = PydanticOutputParser(pydantic_object=TopicsOutput)
    
    prompt_template = """
Eres un experto en análisis de opiniones turísticas y modelado de tópicos.

Analiza los siguientes tópicos identificados automáticamente en reseñas de atracciones turísticas en México (Cancún, CDMX, Mazatlán, Puebla, Puerto Vallarta).

{topics_info}

Asigna un nombre único a cada tópico que cumpla con estas reglas:
- En español
- Máximo 5 palabras
- Representar una categoría turística reconocida (ej. playas, parques temáticos, excursiones guiadas, patrimonio cultural, vida marina, transporte marítimo, hospedaje, gastronomía, compras)
- Si hay mas de 2 categorias presentes que sean super diferentes, usar conectores como "y", "e", "o" para reflejar la diversidad (ej. "Vida marina y Religion") (ej. no valido "Playas y aguas, ya que ambas son similares")
- Evitar nombres demasiado generales (ej. "entretenimiento", "parques") o demasiado específicos (ej. "ferry", "iguanas")
- Mantener un nivel de generalidad consistente entre todos los tópicos
- Evitar adjetivos de opinión o sentimiento (ej. hermoso, divertido, increíble)
- Evitar nombres de marcas o lugares específicos (ej. "Xcaret", "Catedral de Puebla")
- TODOS LOS LABELS DEBEN SER ÚNICOS - no repetir etiquetas entre tópicos
- Si hay tópicos con palabras similares, diferenciar por contexto específico
- Evita repetir palabras en los nombres de los tópicos, es decir que por ejemplo si un tópico se llama "Playas y vida marina", otro tópico no puede llamarse "Vida marina y buceo"

{format_instructions}
"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["topics_info"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    return prompt | llm | parser
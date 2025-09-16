from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

class TopicNaming(BaseModel):
    nombre_topico: str = Field(description="Nombre descriptivo del tópico en español")

def configurar_clasificador_topicos():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=50
    )
    
    parser = PydanticOutputParser(pydantic_object=TopicNaming)
    
    prompt_template = """Eres un experto en análisis de opiniones turísticas y modelado de tópicos.

Analiza las siguientes palabras clave que representan un tópico identificado automáticamente en reseñas de atracciones turísticas en México (Cancún, CDMX, Mazatlán, Puebla, Puerto Vallarta).

Palabras clave del tópico: {keywords}

Basándote en estas palabras, asigna un nombre descriptivo y coherente al tópico que capture la esencia de las opiniones turísticas que representa. El nombre debe ser:
- Específico y relacionado con turismo
- En español
- Máximo 4 palabras
- Descriptivo de la experiencia o aspecto turístico
- Evitar mencionar entidades específicas (nombres de lugares, marcas, personas)

{format_instructions}
"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["keywords"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    return prompt | llm | parser
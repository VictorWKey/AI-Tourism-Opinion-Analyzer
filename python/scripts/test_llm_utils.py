"""
Test script for LLM utilities
"""

from core.llm_utils import (
    extraer_json_de_respuesta, 
    parsear_json_seguro, 
    reparar_json,
    parsear_pydantic_seguro
)
from pydantic import BaseModel, Field
from typing import List


class TopicLabel(BaseModel):
    topic_id: int = Field(..., description="ID del tópico")
    label: str = Field(..., description="Etiqueta descriptiva para el tópico")


class TopicsOutput(BaseModel):
    topics: List[TopicLabel] = Field(..., description="Lista de tópicos")


def test_extract_from_markdown():
    """Test extracting JSON from markdown code block."""
    test_input = '''Here is the result:
```json
{"topics": [{"topic_id": 0, "label": "Test Topic"}]}
```
Some extra text.
'''
    result = extraer_json_de_respuesta(test_input)
    assert result is not None, "Should extract JSON from markdown"
    data = parsear_json_seguro(result)
    assert data is not None, "Should parse extracted JSON"
    assert "topics" in data, "Should have topics key"
    print("✓ Test extract_from_markdown PASSED")


def test_extract_embedded_json():
    """Test extracting JSON embedded in text."""
    test_input = 'The topics are: {"topics": [{"topic_id": 1, "label": "Example"}]} as shown.'
    result = extraer_json_de_respuesta(test_input)
    assert result is not None, "Should extract embedded JSON"
    data = parsear_json_seguro(result)
    assert data is not None, "Should parse embedded JSON"
    print("✓ Test extract_embedded_json PASSED")


def test_repair_malformed_json():
    """Test repairing common JSON issues."""
    # Single quotes instead of double
    test1 = "{'topics': [{'topic_id': 0, 'label': 'Test'}]}"
    result1 = parsear_json_seguro(test1)
    # May or may not work depending on parser
    
    # Trailing comma
    test2 = '{"topics": [{"topic_id": 0, "label": "Test"},]}'
    repaired2 = reparar_json(test2)
    result2 = parsear_json_seguro(repaired2)
    assert result2 is not None, "Should repair trailing comma"
    print("✓ Test repair_malformed_json PASSED")


def test_none_handling():
    """Test handling of None/empty inputs."""
    assert extraer_json_de_respuesta(None) is None, "Should return None for None input"
    assert extraer_json_de_respuesta("") is None, "Should return None for empty string"
    assert parsear_json_seguro(None) is None, "Should return None for None input"
    print("✓ Test none_handling PASSED")


def test_pydantic_parsing():
    """Test parsing to Pydantic model."""
    test_json = '{"topics": [{"topic_id": 0, "label": "Test Topic"}, {"topic_id": 1, "label": "Another Topic"}]}'
    
    result = parsear_pydantic_seguro(test_json, TopicsOutput)
    assert result is not None, "Should parse to Pydantic model"
    assert len(result.topics) == 2, "Should have 2 topics"
    assert result.topics[0].label == "Test Topic", "Should have correct label"
    print("✓ Test pydantic_parsing PASSED")


def test_pydantic_with_default():
    """Test Pydantic parsing with default values."""
    # Invalid JSON
    test_bad = "This is not JSON at all"
    default = {"topics": [{"topic_id": -1, "label": "Fallback"}]}
    
    result = parsear_pydantic_seguro(test_bad, TopicsOutput, default)
    assert result is not None, "Should use default value"
    assert result.topics[0].label == "Fallback", "Should have fallback label"
    print("✓ Test pydantic_with_default PASSED")


def test_complex_llm_response():
    """Test parsing a realistic LLM response."""
    # Simulate a typical Ollama response with extra text
    llm_response = '''
Based on the analysis of the tourism topics, here are the labels:

```json
{
    "topics": [
        {"topic_id": 0, "label": "Playas y arena"},
        {"topic_id": 1, "label": "Servicio de hotel"},
        {"topic_id": 2, "label": "Comida local"}
    ]
}
```

These labels represent the main themes found in the reviews.
'''
    
    result = parsear_pydantic_seguro(llm_response, TopicsOutput)
    assert result is not None, "Should parse complex LLM response"
    assert len(result.topics) == 3, "Should have 3 topics"
    print("✓ Test complex_llm_response PASSED")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing LLM Utilities")
    print("="*50 + "\n")
    
    test_extract_from_markdown()
    test_extract_embedded_json()
    test_repair_malformed_json()
    test_none_handling()
    test_pydantic_parsing()
    test_pydantic_with_default()
    test_complex_llm_response()
    
    print("\n" + "="*50)
    print("All tests PASSED! ✓")
    print("="*50 + "\n")

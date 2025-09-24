"""
Módulo para filtrado de palabras usando POS tagging

Este módulo proporciona herramientas para filtrar adjetivos de texto usando
el modelo de POS tagging mrm8488/bert-spanish-cased-finetuned-pos de Hugging Face.
"""

from transformers import pipeline
from typing import List, Dict, Tuple
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

class FiltradorPOS:
    """
    Clase para filtrar palabras específicas usando POS tagging.
    """
    
    def __init__(self):
        """Inicializa el filtrador POS con el modelo español."""
        self.nlp_pos = pipeline(
            "ner",
            model="mrm8488/bert-spanish-cased-finetuned-pos",
            tokenizer=(
                'mrm8488/bert-spanish-cased-finetuned-pos',  
                {"use_fast": False}
            )
        )
        
        # Etiquetas de adjetivos según la documentación del modelo
        self.etiquetas_adjetivos = {'AO', 'AQ'}
    
    def _dividir_texto_en_fragmentos(self, texto: str, max_tokens: int = 400) -> List[str]:
        """
        Divide un texto largo en fragmentos más pequeños para evitar el límite de tokens.
        
        Args:
            texto: Texto a dividir
            max_tokens: Número máximo de tokens por fragmento
            
        Returns:
            Lista de fragmentos de texto
        """
        palabras = texto.split()
        if len(palabras) <= max_tokens:
            return [texto]
        
        fragmentos = []
        for i in range(0, len(palabras), max_tokens):
            fragmento = " ".join(palabras[i:i + max_tokens])
            fragmentos.append(fragmento)
        
        return fragmentos
    
    def _mapear_tokens_a_palabras(self, texto_original: str, pos_results: List[Dict]) -> List[Tuple[str, str]]:
        """
        Mapea los tokens del modelo BERT a las palabras originales del texto.
        
        Args:
            texto_original: Texto original sin procesar
            pos_results: Resultados del análisis POS
            
        Returns:
            Lista de tuplas (palabra_original, etiqueta_pos)
        """
        # Trabajar con las palabras del texto original
        palabras_originales = texto_original.split()
        
        # Filtrar tokens especiales del modelo
        tokens_modelo = []
        etiquetas_modelo = []
        
        for item in pos_results:
            token = item['word']
            etiqueta = item['entity']
            
            # Saltar tokens especiales de BERT
            if token not in ['[CLS]', '[SEP]', '[PAD]', '[UNK]']:
                # Limpiar tokens que empiezan con ## (subtokens de BERT)
                if token.startswith('##'):
                    token = token[2:]
                
                tokens_modelo.append(token.lower())
                etiquetas_modelo.append(etiqueta)
        
        # Mapear tokens del modelo a palabras originales
        mapeo_palabras_etiquetas = []
        i_token = 0
        
        for palabra_original in palabras_originales:
            palabra_lower = palabra_original.lower()
            
            # Buscar la mejor coincidencia con los tokens del modelo
            if i_token < len(tokens_modelo):
                token_modelo = tokens_modelo[i_token]
                etiqueta = etiquetas_modelo[i_token]
                
                # Coincidencia exacta
                if palabra_lower == token_modelo:
                    mapeo_palabras_etiquetas.append((palabra_original, etiqueta))
                    i_token += 1
                # Coincidencia parcial (la palabra contiene el token o viceversa)
                elif palabra_lower.startswith(token_modelo) or token_modelo.startswith(palabra_lower):
                    mapeo_palabras_etiquetas.append((palabra_original, etiqueta))
                    i_token += 1
                # Si no hay coincidencia, asumir que no es adjetivo
                else:
                    # Buscar en los próximos 3 tokens por si hay desalineación
                    encontrado = False
                    for j in range(i_token, min(i_token + 3, len(tokens_modelo))):
                        if (palabra_lower == tokens_modelo[j] or 
                            palabra_lower.startswith(tokens_modelo[j]) or 
                            tokens_modelo[j].startswith(palabra_lower)):
                            mapeo_palabras_etiquetas.append((palabra_original, etiquetas_modelo[j]))
                            i_token = j + 1
                            encontrado = True
                            break
                    
                    if not encontrado:
                        # No se pudo mapear, asumir que no es adjetivo (etiqueta segura)
                        mapeo_palabras_etiquetas.append((palabra_original, 'NN'))  # Sustantivo por defecto
            else:
                # Si se acabaron los tokens del modelo, asumir que no es adjetivo
                mapeo_palabras_etiquetas.append((palabra_original, 'NN'))
        
        return mapeo_palabras_etiquetas

    def filtrar_adjetivos_texto(self, texto: str) -> Tuple[str, Dict]:
        """
        Filtra adjetivos de un texto usando POS tagging.
        Mantiene el texto original como base y solo filtra las palabras identificadas como adjetivos.
        
        Args:
            texto: Texto a procesar
            
        Returns:
            Tuple con (texto_filtrado, estadisticas)
        """
        if not texto or not texto.strip():
            return "", {"palabras_originales": 0, "palabras_filtradas": 0, "adjetivos_eliminados": 0}
        
        # Dividir texto en fragmentos si es muy largo
        fragmentos = self._dividir_texto_en_fragmentos(texto)
        
        # Procesar cada fragmento
        todas_palabras_filtradas = []
        total_palabras_originales = 0
        total_adjetivos_eliminados = 0
        
        for fragmento in fragmentos:
            try:
                # Obtener análisis POS para el fragmento
                pos_results = self.nlp_pos(fragmento)
                
                # Mapear tokens del modelo a palabras originales
                mapeo_palabras = self._mapear_tokens_a_palabras(fragmento, pos_results)
                
                # Filtrar palabras según el mapeo
                palabras_filtradas_fragmento = []
                adjetivos_eliminados_fragmento = 0
                
                for palabra_original, etiqueta_pos in mapeo_palabras:
                    # Mantener palabra si NO es adjetivo
                    if etiqueta_pos not in self.etiquetas_adjetivos:
                        palabras_filtradas_fragmento.append(palabra_original)
                    else:
                        adjetivos_eliminados_fragmento += 1
                
                todas_palabras_filtradas.extend(palabras_filtradas_fragmento)
                total_palabras_originales += len(mapeo_palabras)
                total_adjetivos_eliminados += adjetivos_eliminados_fragmento
                
            except Exception as e:
                # Si falla el análisis POS, conservar el fragmento original sin filtrar
                print(f"⚠️ Error en análisis POS: {str(e)[:100]}... - conservando texto original")
                palabras_fragmento = fragmento.split()
                todas_palabras_filtradas.extend(palabras_fragmento)
                total_palabras_originales += len(palabras_fragmento)
        
        texto_filtrado = " ".join(todas_palabras_filtradas)
        
        estadisticas = {
            "palabras_originales": total_palabras_originales,
            "palabras_filtradas": len(todas_palabras_filtradas),
            "adjetivos_eliminados": total_adjetivos_eliminados
        }
        
        return texto_filtrado, estadisticas
    
    def filtrar_adjetivos_lista(self, textos: List[str], mostrar_progreso: bool = True) -> Tuple[List[str], Dict]:
        """
        Filtra adjetivos de una lista de textos.
        
        Args:
            textos: Lista de textos a procesar
            mostrar_progreso: Si mostrar indicador de progreso
            
        Returns:
            Tuple con (textos_filtrados, estadisticas_globales)
        """
        textos_filtrados = []
        total_palabras_originales = 0
        total_palabras_filtradas = 0
        total_adjetivos_eliminados = 0
        
        for i, texto in enumerate(textos):
            if mostrar_progreso and (i % 50 == 0 or i == len(textos) - 1):
                progreso = (i + 1) / len(textos) * 100
                print(f"Filtrando adjetivos: {i + 1}/{len(textos)} ({progreso:.1f}%)")
            
            texto_filtrado, stats = self.filtrar_adjetivos_texto(texto)
            textos_filtrados.append(texto_filtrado)
            
            total_palabras_originales += stats["palabras_originales"]
            total_palabras_filtradas += stats["palabras_filtradas"]
            total_adjetivos_eliminados += stats["adjetivos_eliminados"]
        
        estadisticas_globales = {
            "textos_procesados": len(textos),
            "total_palabras_originales": total_palabras_originales,
            "total_palabras_filtradas": total_palabras_filtradas,
            "total_adjetivos_eliminados": total_adjetivos_eliminados,
            "promedio_palabras_antes": total_palabras_originales / len(textos) if len(textos) > 0 else 0,
            "promedio_palabras_despues": total_palabras_filtradas / len(textos) if len(textos) > 0 else 0,
            "porcentaje_reduccion": (total_adjetivos_eliminados / total_palabras_originales * 100) if total_palabras_originales > 0 else 0
        }
        
        return textos_filtrados, estadisticas_globales
    
    def mostrar_estadisticas_filtrado(self, estadisticas: Dict):
        """Muestra estadísticas del filtrado de adjetivos."""
        print(f"\n📊 Estadísticas de filtrado de adjetivos:")
        print(f"   • Textos procesados: {estadisticas['textos_procesados']}")
        print(f"   • Palabras originales: {estadisticas['total_palabras_originales']}")
        print(f"   • Palabras después del filtrado: {estadisticas['total_palabras_filtradas']}")
        print(f"   • Adjetivos eliminados: {estadisticas['total_adjetivos_eliminados']}")
        print(f"   • Promedio palabras antes: {estadisticas['promedio_palabras_antes']:.1f}")
        print(f"   • Promedio palabras después: {estadisticas['promedio_palabras_despues']:.1f}")
        print(f"   • Reducción por adjetivos: {estadisticas['porcentaje_reduccion']:.1f}%")
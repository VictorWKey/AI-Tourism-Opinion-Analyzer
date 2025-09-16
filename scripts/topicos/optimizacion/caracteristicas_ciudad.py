import numpy as np

def analizar_caracteristicas_dataset(texts):
    """Analiza las características del dataset para guiar la optimización"""
    
    print("🔍 Analizando características del dataset...")
    
    # Estadísticas básicas
    num_docs = len(texts)
    avg_length = np.mean([len(text.split()) for text in texts])
    std_length = np.std([len(text.split()) for text in texts])
    min_length = min([len(text.split()) for text in texts])
    max_length = max([len(text.split()) for text in texts])
    
    # Diversidad léxica
    all_words = set()
    for text in texts:
        all_words.update(text.split())
    vocab_size = len(all_words)
    
    # Análisis de duplicados
    unique_texts = len(set(texts))
    duplicate_ratio = 1 - (unique_texts / num_docs)
    
    characteristics = {
        'num_docs': num_docs,
        'avg_length': avg_length,
        'std_length': std_length,
        'min_length': min_length,
        'max_length': max_length,
        'vocab_size': vocab_size,
        'unique_texts': unique_texts,
        'duplicate_ratio': duplicate_ratio,
        'lexical_diversity': vocab_size / sum(len(text.split()) for text in texts)
    }
    
    print(f"📊 Características del dataset:")
    print(f"   • Número de documentos: {num_docs}")
    print(f"   • Longitud promedio: {avg_length:.1f} ± {std_length:.1f} palabras")
    print(f"   • Rango de longitud: {min_length} - {max_length} palabras")
    print(f"   • Vocabulario único: {vocab_size:,} palabras")
    print(f"   • Textos únicos: {unique_texts} ({(1-duplicate_ratio)*100:.1f}%)")
    print(f"   • Diversidad léxica: {characteristics['lexical_diversity']:.4f}")
    
    return characteristics

def analizar_caracteristicas_multiciudad(df, ciudades, columna_texto):
    """
    🆕 Analiza las características de múltiples ciudades para optimización cross-validation
    """
    print("🌍 Analizando características multi-ciudad para optimización...")
    
    caracteristicas_por_ciudad = {}
    
    for ciudad in ciudades:
        print(f"\n🏙️ Analizando {ciudad}:")
        df_ciudad = df[df['Ciudad'] == ciudad]
        texts_ciudad = df_ciudad[columna_texto].dropna().tolist()
    
        caracteristicas_por_ciudad[ciudad] = analizar_caracteristicas_dataset(texts_ciudad)
    
    # Calcular estadísticas combinadas
    total_docs = sum(char['num_docs'] for char in caracteristicas_por_ciudad.values() if char is not None)
    ciudades_validas = [ciudad for ciudad, char in caracteristicas_por_ciudad.items() if char is not None]
    
    if ciudades_validas:
        avg_docs_per_city = total_docs / len(ciudades_validas)
        min_docs = min(char['num_docs'] for char in caracteristicas_por_ciudad.values() if char is not None)
        max_docs = max(char['num_docs'] for char in caracteristicas_por_ciudad.values() if char is not None)
        
        # Diversidad léxica promedio
        avg_lexical_diversity = np.mean([char['lexical_diversity'] for char in caracteristicas_por_ciudad.values() if char is not None])
        
        caracteristicas_combinadas = {
            'total_docs': total_docs,
            'num_ciudades': len(ciudades_validas),
            'avg_docs_per_city': avg_docs_per_city,
            'min_docs_city': min_docs,
            'max_docs_city': max_docs,
            'avg_lexical_diversity': avg_lexical_diversity,
            'ciudades_validas': ciudades_validas,
            'por_ciudad': caracteristicas_por_ciudad
        }
        
        print(f"\n📈 RESUMEN MULTI-CIUDAD:")
        print(f"   • Total documentos: {total_docs:,}")
        print(f"   • Ciudades válidas: {len(ciudades_validas)}")
        print(f"   • Promedio docs/ciudad: {avg_docs_per_city:.1f}")
        print(f"   • Rango docs/ciudad: {min_docs} - {max_docs}")
        print(f"   • Diversidad léxica promedio: {avg_lexical_diversity:.4f}")
        
        return caracteristicas_combinadas
    else:
        print("❌ No se encontraron ciudades válidas")
        return None
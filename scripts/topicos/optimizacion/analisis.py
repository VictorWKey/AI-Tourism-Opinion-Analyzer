def mostrar_metricas_detalladas(metrics, dataset_chars):
    """
    Muestra un resumen detallado de todas las métricas calculadas
    """
    print(f"📊 MÉTRICAS DETALLADAS DE COHERENCIA DE TÓPICOS")
    print(f"=" * 60)
    
    # Información del dataset
    print(f"\n📁 INFORMACIÓN DEL DATASET:")
    print(f"   • Documentos: {dataset_chars['num_docs']:,}")
    print(f"   • Vocabulario: {dataset_chars['vocab_size']:,} palabras únicas")
    print(f"   • Diversidad léxica: {dataset_chars['lexical_diversity']:.4f}")
    print(f"   • Ratio de duplicados: {dataset_chars['duplicate_ratio']:.2%}")
    
    # Métricas de separación
    print(f"\n🎯 SEPARACIÓN DE CLUSTERS:")
    print(f"   • Silhouette Score: {metrics['silhouette_score']:.4f}")
    print(f"   • Cobertura: {metrics['coverage']:.2%}")
    
    # Métricas de diversidad
    print(f"\n🌈 DIVERSIDAD:")
    print(f"   • Diversidad léxica: {metrics['topic_diversity']:.4f}")
    print(f"   • Diversidad semántica: {metrics['semantic_diversity']:.4f}")
    
    # Métricas de coherencia estándar
    print(f"\n🧠 COHERENCIA ESTÁNDAR (Gensim):")
    coherence_metrics = [
        ('CV (Ventana deslizante)', metrics['coherence_cv']),
        ('NPMI (Mutual Information)', metrics['coherence_npmi'])
    ]
    
    for name, value in coherence_metrics:
        if value != -1:
            status = "✅" if value > 0.3 else "⚠️" if value > 0.1 else "❌"
            print(f"   • {name}: {value:.4f} {status}")
        else:
            print(f"   • {name}: No calculada ❌")
    
    # Información de tópicos
    print(f"\n📈 INFORMACIÓN DE TÓPICOS:")
    print(f"   • Número de tópicos: {metrics['num_topics']}")
    print(f"   • Tamaño promedio: {metrics['avg_topic_size']:.1f} documentos")
    
    # Interpretación de resultados
    print(f"\n💡 INTERPRETACIÓN:")
    
    # Evaluar calidad general
    valid_coherences = [v for v in [metrics['coherence_cv'], metrics['coherence_npmi']] if v > 0]
    
    if valid_coherences:
        avg_coherence = np.mean(valid_coherences)
        if avg_coherence > 0.4:
            quality = "Excelente ⭐⭐⭐"
        elif avg_coherence > 0.25:
            quality = "Buena ⭐⭐"
        elif avg_coherence > 0.1:
            quality = "Aceptable ⭐"
        else:
            quality = "Necesita mejoras ⚠️"
        
        print(f"   • Calidad general: {quality}")
        print(f"   • Coherencia promedio: {avg_coherence:.3f}")
    else:
        print(f"   • Calidad general: No evaluable (falta coherencia)")
    
    # Recomendaciones
    print(f"\n🔧 RECOMENDACIONES:")
    
    if metrics['coverage'] < 0.7:
        print(f"   • Reducir min_cluster_size para mayor cobertura")
    
    if metrics['topic_diversity'] < 0.5:
        print(f"   • Ajustar parámetros para mayor diversidad entre tópicos")
    
    if metrics['silhouette_score'] < 0.2:
        print(f"   • Mejorar separación con diferentes embeddings o UMAP")
    
    if all(v == -1 for v in [metrics['coherence_cv'], metrics['coherence_npmi']]):
        print(f"   • Verificar tokenización y diccionario para coherencia Gensim")
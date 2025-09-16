def visualizar_evolucion_metricas(study):
    """
    Visualiza la evolución de las métricas durante la optimización
    """
    # Extraer datos de trials completados
    completed_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
    
    if len(completed_trials) < 5:
        print("⚠️ Muy pocos trials completados para generar visualizaciones")
        return
    
    # Crear DataFrame con métricas
    metrics_data = []
    for trial in completed_trials:
        data = {
            'trial_number': trial.number,
            'objective_score': trial.value,
            'num_topics': trial.user_attrs.get('num_topics', 0),
            'silhouette_score': trial.user_attrs.get('silhouette_score', -1),
            'topic_diversity': trial.user_attrs.get('topic_diversity', 0),
            'coverage': trial.user_attrs.get('coverage', 0),
            'coherence_cv': trial.user_attrs.get('coherence_cv', -1),
            'coherence_npmi': trial.user_attrs.get('coherence_npmi', -1),
            'semantic_diversity': trial.user_attrs.get('semantic_diversity', 0)
        }
        metrics_data.append(data)
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Crear visualizaciones
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Evolución del score objetivo
    axes[0,0].plot(df_metrics['trial_number'], df_metrics['objective_score'], 'b-', alpha=0.7)
    axes[0,0].scatter(df_metrics['trial_number'], df_metrics['objective_score'], c='blue', alpha=0.5)
    axes[0,0].set_title('Evolución Score Objetivo')
    axes[0,0].set_xlabel('Trial')
    axes[0,0].set_ylabel('Score')
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. Trade-off: Coverage vs Diversity
    valid_mask = (df_metrics['coverage'] > 0) & (df_metrics['topic_diversity'] > 0)
    if valid_mask.sum() > 0:
        scatter = axes[0,1].scatter(df_metrics.loc[valid_mask, 'coverage'], 
                                  df_metrics.loc[valid_mask, 'topic_diversity'],
                                  c=df_metrics.loc[valid_mask, 'objective_score'],
                                  cmap='viridis', alpha=0.7)
        axes[0,1].set_title('Trade-off: Coverage vs Diversity')
        axes[0,1].set_xlabel('Coverage')
        axes[0,1].set_ylabel('Topic Diversity')
        plt.colorbar(scatter, ax=axes[0,1], label='Score')
    
    # 3. Relación: Número de tópicos vs Score
    axes[0,2].scatter(df_metrics['num_topics'], df_metrics['objective_score'], alpha=0.7)
    axes[0,2].set_title('Número de Tópicos vs Score')
    axes[0,2].set_xlabel('Número de Tópicos')
    axes[0,2].set_ylabel('Score Objetivo')
    axes[0,2].grid(True, alpha=0.3)
    
    # 4. Distribución de coherencias
    coherence_cols = ['coherence_cv', 'coherence_npmi']
    for i, col in enumerate(coherence_cols):
        valid_coherence = df_metrics[df_metrics[col] > -0.5][col]
        if len(valid_coherence) > 0:
            axes[1,i].hist(valid_coherence, bins=20, alpha=0.7, edgecolor='black')
            axes[1,i].set_title(f'Distribución {col.replace("_", " ").title()}')
            axes[1,i].set_xlabel('Coherencia')
            axes[1,i].set_ylabel('Frecuencia')
            axes[1,i].axvline(valid_coherence.mean(), color='red', linestyle='--', 
                            label=f'Media: {valid_coherence.mean():.3f}')
            axes[1,i].legend()
    
    # 5. Trade-off: Silhouette vs Coherence CV
    valid_silhouette = df_metrics['silhouette_score'] > -0.5
    valid_coherence_cv = df_metrics['coherence_cv'] > -0.5
    valid_both = valid_silhouette & valid_coherence_cv
    
    if valid_both.sum() > 0:
        scatter = axes[1,2].scatter(df_metrics.loc[valid_both, 'silhouette_score'],
                                  df_metrics.loc[valid_both, 'coherence_cv'],
                                  c=df_metrics.loc[valid_both, 'objective_score'],
                                  cmap='plasma', alpha=0.7)
        axes[1,2].set_title('Trade-off: Silhouette vs Coherence CV')
        axes[1,2].set_xlabel('Silhouette Score')
        axes[1,2].set_ylabel('Coherence CV')
        plt.colorbar(scatter, ax=axes[1,2], label='Score')
    
    plt.tight_layout()
    plt.show()
    
    # Estadísticas resumidas
    print(f"\n📊 ESTADÍSTICAS DE OPTIMIZACIÓN:")
    print(f"=" * 50)
    print(f"Trials completados: {len(completed_trials)}")
    print(f"Score máximo: {df_metrics['objective_score'].max():.4f}")
    print(f"Score promedio: {df_metrics['objective_score'].mean():.4f} ± {df_metrics['objective_score'].std():.4f}")
    
    # Correlaciones entre métricas
    print(f"\n🔗 CORRELACIONES CON SCORE OBJETIVO:")
    print(f"-" * 40)
    numeric_cols = ['num_topics', 'silhouette_score', 'topic_diversity', 'coverage', 'coherence_cv', 'coherence_npmi']
    for col in numeric_cols:
        if col in df_metrics.columns:
            valid_data = df_metrics[(df_metrics[col] > -0.5) & (df_metrics['objective_score'] > 0)]
            if len(valid_data) > 5:
                correlation = valid_data[col].corr(valid_data['objective_score'])
                print(f"{col.replace('_', ' ').title()}: {correlation:.3f}")

def analizar_pareto_front(study):
    """
    Analiza el frente de Pareto entre diferentes objetivos
    """
    completed_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
    
    if len(completed_trials) < 10:
        print("⚠️ Muy pocos trials para análisis de Pareto")
        return
    
    # Extraer métricas principales
    data = []
    for trial in completed_trials:
        metrics = {
            'coherence': trial.user_attrs.get('coherence_cv', 0),
            'diversity': trial.user_attrs.get('semantic_diversity', 0),
            'coverage': trial.user_attrs.get('coverage', 0),
            'silhouette': trial.user_attrs.get('silhouette_score', 0),
            'score': trial.value
        }
        if metrics['coherence'] > 0 and metrics['diversity'] > 0:
            data.append(metrics)
    
    if len(data) < 5:
        print("⚠️ Datos insuficientes para análisis de Pareto")
        return
    
    df_pareto = pd.DataFrame(data)
    
    # Visualizar trade-offs principales
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Coherencia vs Diversidad
    scatter1 = axes[0].scatter(df_pareto['coherence'], df_pareto['diversity'], 
                              c=df_pareto['score'], cmap='viridis', alpha=0.7, s=50)
    axes[0].set_xlabel('Coherencia CV')
    axes[0].set_ylabel('Diversidad Semántica')
    axes[0].set_title('Trade-off: Coherencia vs Diversidad')
    plt.colorbar(scatter1, ax=axes[0], label='Score')
    
    # Coherencia vs Cobertura
    scatter2 = axes[1].scatter(df_pareto['coherence'], df_pareto['coverage'],
                              c=df_pareto['score'], cmap='plasma', alpha=0.7, s=50)
    axes[1].set_xlabel('Coherencia CV')
    axes[1].set_ylabel('Cobertura')
    axes[1].set_title('Trade-off: Coherencia vs Cobertura')
    plt.colorbar(scatter2, ax=axes[1], label='Score')
    
    # Diversidad vs Cobertura
    scatter3 = axes[2].scatter(df_pareto['diversity'], df_pareto['coverage'],
                              c=df_pareto['score'], cmap='coolwarm', alpha=0.7, s=50)
    axes[2].set_xlabel('Diversidad Semántica')
    axes[2].set_ylabel('Cobertura')
    axes[2].set_title('Trade-off: Diversidad vs Cobertura')
    plt.colorbar(scatter3, ax=axes[2], label='Score')
    
    plt.tight_layout()
    plt.show()
    
    # Identificar soluciones del frente de Pareto (simplificado)
    top_10_percent = df_pareto.nlargest(max(1, len(df_pareto) // 10), 'score')
    
    print(f"\n🏆 TOP SOLUCIONES (10% superior):")
    print(f"=" * 60)
    for idx, row in top_10_percent.iterrows():
        print(f"Score: {row['score']:.4f} | "
              f"Coherencia: {row['coherence']:.3f} | "
              f"Diversidad: {row['diversity']:.3f} | "
              f"Cobertura: {row['coverage']:.3f}")
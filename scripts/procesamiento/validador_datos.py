"""
Validador de Datos - Valida y corrige problemas específicos en los datos
"""

import pandas as pd


class ValidadorDatos:
    """Valida y corrige problemas en los datos."""
    
    def __init__(self, df):
        self.df = df
    
    def examinar_y_corregir_contenidos_mal_ubicados(self):
        """
        Examina casos específicos donde Titulo y OrigenAutor tienen el mismo contenido
        y corrige automáticamente cuando es posible detectar el error.
        """
        print("=== CORRECCIÓN DE CONTENIDOS MAL UBICADOS ===")
        print("Examinando registros con contenido duplicado entre Titulo y OrigenAutor...\n")
        
        casos_problematicos = []
        correcciones_realizadas = 0
        
        # Encontrar todas las filas donde Titulo y OrigenAutor son idénticos
        for idx, row in self.df.iterrows():
            titulo = str(row.get('Titulo', '')).strip()
            origen = str(row.get('OrigenAutor', '')).strip()
            
            # Si son idénticos y no están vacíos
            if titulo == origen and titulo != '' and titulo.lower() not in ['nan', 'none']:
                # Evaluar si parece ser un lugar (OrigenAutor correcto) o un título (Titulo correcto)
                es_lugar = any(palabra in titulo.lower() for palabra in 
                             ['puerto', 'buenos', 'argentina', 'méxico', 'colombia', 'españa', 'peru'])
                es_titulo_opinion = any(palabra in titulo.lower() for palabra in 
                                      ['excelente', 'muy', 'bueno', 'malo', 'hermoso', 'increíble'])
                
                caso_info = {
                    'indice': idx,
                    'contenido': titulo,
                    'es_lugar': es_lugar,
                    'es_titulo': es_titulo_opinion,
                    'accion': 'ninguna'
                }
                
                # Auto-corrección basada en heurísticas
                if es_lugar and not es_titulo_opinion:
                    # Parece ser un lugar, limpiar Titulo
                    self.df.at[idx, 'Titulo'] = 'sin titulo'
                    caso_info['accion'] = 'titulo_limpiado'
                    correcciones_realizadas += 1
                    print(f"✅ Fila {idx}: '{titulo}' -> Limpiado de Titulo (es lugar)")
                    
                elif es_titulo_opinion and not es_lugar:
                    # Parece ser un título de opinión, limpiar OrigenAutor
                    self.df.at[idx, 'OrigenAutor'] = 'anonimo'
                    caso_info['accion'] = 'origen_limpiado'
                    correcciones_realizadas += 1
                    print(f"✅ Fila {idx}: '{titulo}' -> Limpiado de OrigenAutor (es título)")
                
                casos_problematicos.append(caso_info)
        
        print(f"=== RESUMEN DE CORRECCIONES ===")
        print(f"📊 Casos problemáticos encontrados: {len(casos_problematicos)}")
        print(f"✅ Correcciones automáticas realizadas: {correcciones_realizadas}")
        print(f"⚠️  Casos que requieren revisión manual: {len(casos_problematicos) - correcciones_realizadas}")
        
        return self.df
    
    def guardar_dataset_procesado(self, nombre_archivo='dataset_opiniones_consolidado.csv', ruta='../data/processed/'):
        """
        Guarda el dataset procesado en un archivo CSV.
        """
        print("=== GUARDANDO DATASET PROCESADO ===")
        
        # Verificar que tenemos todas las columnas esperadas
        print("Columnas en el dataset final:")
        for i, col in enumerate(self.df.columns, 1):
            print(f"{i:2d}. {col}")
        
        print(f"\nDimensiones finales: {self.df.shape}")
        print(f"Filas: {self.df.shape[0]:,}")
        print(f"Columnas: {self.df.shape[1]}")
        
        # Construir ruta completa
        import os
        # Crear el directorio si no existe
        os.makedirs(ruta, exist_ok=True)
        ruta_completa = os.path.join(ruta, nombre_archivo)
        
        # Guardar el dataset
        self.df.to_csv(ruta_completa, index=False)
        
        print(f"\n✅ Dataset final guardado como '{ruta_completa}'")
        
        return self.df

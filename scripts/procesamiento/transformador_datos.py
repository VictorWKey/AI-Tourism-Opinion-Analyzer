"""
Transformador de Datos - Transforma y convierte formatos de datos
"""

import pandas as pd
from datetime import datetime


class TransformadorDatos:
    """Transforma datos del dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def convertir_fecha_opinion(self, fecha_str):
        """
        Convierte fechas del formato '31 de agosto de 2025' a datetime
        """
        if pd.isna(fecha_str):
            return pd.NaT
        
        try:
            # Mapeo de meses en español
            meses = {
                'enero': 'January', 'febrero': 'February', 'marzo': 'March',
                'abril': 'April', 'mayo': 'May', 'junio': 'June',
                'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
                'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
            }
            
            fecha_str = str(fecha_str).strip()
            
            # Reemplazar nombres de meses en español por inglés
            for esp, eng in meses.items():
                fecha_str = fecha_str.replace(esp, eng)
            
            # Convertir a datetime
            return pd.to_datetime(fecha_str, format='%d de %B de %Y', errors='coerce')
        except:
            return pd.NaT
    
    def convertir_fecha_estadia(self, fecha_str):
        """
        Convierte fechas del formato 'ago de 2025' a datetime (primer día del mes)
        """
        if pd.isna(fecha_str):
            return pd.NaT
        
        try:
            # Mapeo de meses abreviados en español
            meses = {
                'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
                'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
                'sept': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
            }
            
            fecha_str = str(fecha_str).strip()
            
            # Reemplazar nombres de meses en español por inglés
            for esp, eng in meses.items():
                fecha_str = fecha_str.replace(esp, eng)
            
            # Agregar día 1 para hacer válida la fecha
            fecha_str = '1 ' + fecha_str
            
            # Convertir a datetime
            return pd.to_datetime(fecha_str, format='%d %b de %Y', errors='coerce')
        except:
            return pd.NaT
    
    def convertir_fechas(self):
        """
        Convierte las columnas de fechas del DataFrame.
        """
        print("=== CONVERSIÓN DE TIPOS DE DATOS PARA FECHAS ===")
        
        # Mostrar ejemplos antes de conversión
        print("Ejemplos de fechas ANTES de conversión:")
        if 'FechaOpinion' in self.df.columns:
            print(f"FechaOpinion: {self.df['FechaOpinion'].head(3).tolist()}")
        if 'FechaEstadia' in self.df.columns:
            print(f"FechaEstadia: {self.df['FechaEstadia'].head(3).tolist()}")
        
        # Aplicar conversiones
        print("\nConvirtiendo fechas...")
        if 'FechaOpinion' in self.df.columns:
            self.df['FechaOpinion'] = self.df['FechaOpinion'].apply(self.convertir_fecha_opinion)
        if 'FechaEstadia' in self.df.columns:
            self.df['FechaEstadia'] = self.df['FechaEstadia'].apply(self.convertir_fecha_estadia)
        
        # Mostrar ejemplos después de conversión
        print("\nEjemplos de fechas DESPUÉS de conversión:")
        if 'FechaOpinion' in self.df.columns:
            print(f"FechaOpinion: {self.df['FechaOpinion'].head(3).tolist()}")
            print(f"Tipo: {self.df['FechaOpinion'].dtype}")
            
            # Verificar fechas nulas después de conversión
            fechas_nulas_opinion = self.df['FechaOpinion'].isna().sum()
            print(f"FechaOpinion nulas: {fechas_nulas_opinion}")
        
        if 'FechaEstadia' in self.df.columns:
            print(f"FechaEstadia: {self.df['FechaEstadia'].head(3).tolist()}")
            print(f"Tipo: {self.df['FechaEstadia'].dtype}")
            
            fechas_nulas_estadia = self.df['FechaEstadia'].isna().sum()
            print(f"FechaEstadia nulas: {fechas_nulas_estadia}")
        
        print("✅ Conversión de fechas completada")
        return self.df
    
    def crear_texto_consolidado(self, row):
        """
        Crea un texto consolidado que combina todos los campos en una narrativa natural.
        
        Formato: [Titulo]. [Review]. Mi viaje fue [en/con] [TipoViaje].
        """
        
        # Obtener los valores y limpiarlos
        titulo = str(row['Titulo']).strip()
        review = str(row['Review']).strip()
        
        # Construir el texto consolidado
        texto_partes = []
        
        # 1. Agregar título (si no es "sin titulo")
        if titulo and titulo.lower() != 'sin titulo':
            if not titulo.endswith('.'):
                titulo += '.'
            texto_partes.append(titulo)
        
        # 2. Agregar review
        if review and review.lower() not in ['nan', 'none']:
            if not review.endswith('.'):
                review += '.'
            texto_partes.append(review)
        
        # Unir todas las partes con espacios
        texto_consolidado = ' '.join(texto_partes)
        
        return texto_consolidado

    
    def agregar_texto_consolidado(self):
        """
        Agrega la columna de texto consolidado al DataFrame.
        """
        print("=== CREACIÓN DE COLUMNA DE TEXTO CONSOLIDADO ===")
        print("Combinando todos los campos en una narrativa coherente...")
        
        # Aplicar la función a todo el dataset
        print("Generando texto consolidado para cada registro...")
        self.df['TituloReview'] = self.df.apply(self.crear_texto_consolidado, axis=1)
        
        print(f"✅ Columna 'TituloReview' creada exitosamente")
        print(f"Total de registros procesados: {len(self.df)}")
        
        # Mostrar estadísticas de la nueva columna
        longitudes = self.df['TituloReview'].str.len()
        print(f"\n📊 ESTADÍSTICAS DE TEXTO CONSOLIDADO:")
        print(f"   • Longitud promedio: {longitudes.mean():.1f} caracteres")
        print(f"   • Longitud mínima: {longitudes.min()} caracteres")
        print(f"   • Longitud máxima: {longitudes.max()} caracteres")
        print(f"   • Mediana: {longitudes.median():.1f} caracteres")
        
        # Mostrar algunos ejemplos
        print(f"\n📝 EJEMPLOS DE TEXTO CONSOLIDADO:")
        print("="*80)
        ejemplos = self.df.sample(5, random_state=42)
        for idx, row in ejemplos.iterrows():
            ciudad = row['Ciudad']
            atraccion = row['Atraccion']
            texto = row['TituloReview'][:100] + "..." if len(row['TituloReview']) > 100 else row['TituloReview']
            print(f"• {ciudad} - {atraccion}:")
            print(f"  '{texto}'")
            print()
        
        return self.df

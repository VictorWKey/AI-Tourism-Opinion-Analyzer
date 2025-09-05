"""
Cargador de Datos - Carga y consolida archivos CSV
"""

import pandas as pd
import os
import glob
from pathlib import Path


class CargadorDatos:
    """Carga datos desde archivos CSV."""
    
    def __init__(self, ruta_data='../data'):
        self.ruta_data = ruta_data
        self.ruta_raw = os.path.join(ruta_data, 'raw')
        self.ruta_processed = os.path.join(ruta_data, 'processed')
    
    def extraer_nombre_atraccion(self, nombre_archivo):
        """
        Extrae el nombre de la atracción del nombre del archivo CSV.
        Por ejemplo: 'cancun-la-isla.csv' -> 'la isla'
        """
        # Remover la extensión .csv
        nombre_sin_extension = nombre_archivo.replace('.csv', '')
        
        # Dividir por guiones
        partes = nombre_sin_extension.split('-')
        
        # Omitir la primera parte (que es el nombre de la ciudad)
        # y unir el resto con espacios
        if len(partes) > 1:
            atraccion = ' '.join(partes[1:])
        else:
            atraccion = nombre_sin_extension
        
        return atraccion
    
    def cargar_datos_turisticos(self):
        """
        Carga todos los archivos CSV de las carpetas de ciudades y
        los consolida en un solo DataFrame.
        """
        dataframes = []
        
        # Verificar que existe el directorio raw
        if not os.path.exists(self.ruta_raw):
            print(f"Error: No se encontró el directorio raw en {self.ruta_raw}")
            return pd.DataFrame()
        
        # Obtener todas las carpetas (ciudades) en el directorio raw
        carpetas_ciudades = [d for d in os.listdir(self.ruta_raw) 
                            if os.path.isdir(os.path.join(self.ruta_raw, d))]
        
        print(f"Ciudades encontradas en raw: {carpetas_ciudades}")
        
        for ciudad in carpetas_ciudades:
            ruta_ciudad = os.path.join(self.ruta_raw, ciudad)
            
            # Encontrar todos los archivos CSV en la carpeta de la ciudad
            archivos_csv = glob.glob(os.path.join(ruta_ciudad, '*.csv'))
            
            print(f"\nProcesando ciudad: {ciudad}")
            print(f"Archivos encontrados: {len(archivos_csv)}")
            
            for archivo_csv in archivos_csv:
                try:
                    # Leer el archivo CSV
                    df_temp = pd.read_csv(archivo_csv)
                    
                    # Agregar información de ciudad y atracción
                    df_temp['Ciudad'] = ciudad
                    
                    # Extraer nombre de atracción del nombre del archivo
                    nombre_archivo = os.path.basename(archivo_csv)
                    df_temp['Atraccion'] = self.extraer_nombre_atraccion(nombre_archivo)
                    
                    dataframes.append(df_temp)
                    print(f"✓ {nombre_archivo}: {len(df_temp)} filas cargadas")
                    
                except Exception as e:
                    print(f"✗ Error al cargar {archivo_csv}: {e}")
        
        # Concatenar todos los DataFrames
        if dataframes:
            df_consolidado = pd.concat(dataframes, ignore_index=True)
            print(f"\n=== RESUMEN ===")
            print(f"Total de filas: {len(df_consolidado)}")
            print(f"Ciudades procesadas: {df_consolidado['Ciudad'].nunique()}")
            print(f"Atracciones procesadas: {df_consolidado['Atraccion'].nunique()}")
            
            return df_consolidado
        else:
            print("No se encontraron archivos CSV para procesar.")
            return pd.DataFrame()

"""
Limpieza de Datos - Limpia y corrige errores en el dataset
"""

import pandas as pd
import re


class LimpiadorDatos:
    """Limpia y corrige datos del dataset."""
    
    def __init__(self, df):
        self.df = df
    
    def limpiar_origen_autor(self, valor):
        """
        Limpia los valores de la columna OrigenAutor según los criterios especificados:
        1. Eliminar valores que contengan "aporte"
        2. Eliminar valores con más de 10 palabras
        3. Eliminar nombres propios con patrón "Nombre L" (nombre + letra)
        4. Eliminar valores en mayúsculas como "ALCIRA HAYDEE M"
        5. Mantener lugares válidos como "Puerto Rico", "Buenos Aires, Argentina"
        """
        # Si es NaN o None, mantenerlo
        if pd.isna(valor) or valor is None:
            return valor
        
        valor_str = str(valor).strip()
        
        # Criterio 1: Eliminar si contiene "aporte"
        if "aporte" in valor_str.lower():
            return None
        
        # Criterio 2: Eliminar si tiene más de 10 palabras
        palabras = valor_str.split()
        if len(palabras) > 10:
            return None
        
        # Criterio 3: Eliminar patrón "Nombre L" (nombre seguido de una sola letra)
        patron_nombre_letra = r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+[A-Z]$'
        if re.match(patron_nombre_letra, valor_str):
            return None
        
        # Criterio 4: Eliminar si está todo en mayúsculas (nombres como "ALCIRA HAYDEE M")
        if valor_str.isupper():
            # Si es una sola palabra corta o tiene patrón de nombre personal, eliminar
            if len(palabras) <= 3 and not any(word.lower() in ['usa', 'uk', 'eu'] for word in palabras):
                return None
        
        # Criterio adicional: Eliminar si es claramente un nombre personal
        patron_nombre_personal = r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+[A-Z]$'
        if re.match(patron_nombre_personal, valor_str):
            return None
        
        # Si sobrevive a todos los filtros, mantener el valor
        return valor_str
    
    def limpiar_columna_origen_autor(self):
        """
        Limpia la columna OrigenAutor del DataFrame.
        """
        print("=== LIMPIEZA DE COLUMNA OrigenAutor ===")
        print(f"Valores únicos antes de limpieza: {self.df['OrigenAutor'].nunique()}")
        
        # Crear columna limpia
        self.df['OrigenAutor_limpio'] = self.df['OrigenAutor'].apply(self.limpiar_origen_autor)
        
        print(f"Valores únicos después de limpieza: {self.df['OrigenAutor_limpio'].nunique()}")
        print(f"Valores eliminados (convertidos a None): {self.df['OrigenAutor_limpio'].isna().sum() - self.df['OrigenAutor'].isna().sum()}")
        
        # Mostrar algunos ejemplos de valores eliminados
        print("\n=== EJEMPLOS DE VALORES ELIMINADOS ===")
        valores_eliminados = self.df[
            self.df['OrigenAutor'].notna() & 
            self.df['OrigenAutor_limpio'].isna()
        ]['OrigenAutor'].value_counts().head(20)
        
        for valor, count in valores_eliminados.items():
            print(f"'{valor}' -> ELIMINADO ({count} veces)")
        
        print(f"\n=== VALORES CONSERVADOS (Top 20) ===")
        valores_conservados = self.df['OrigenAutor_limpio'].value_counts().head(20)
        for valor, count in valores_conservados.items():
            print(f"'{valor}': {count} veces")
        
        # Validación adicional de la limpieza
        print("\n=== VALIDACIÓN DE LA LIMPIEZA ===")
        casos_test = ['Pamela L', 'Cifuentes E', 'ALCIRA HAYDEE M', '1 aporte', 
                      'Puerto Rico', 'Buenos Aires, Argentina', 'San Juan, Puerto Rico',
                      'Ciudad de México, México']
        
        print("Prueba de casos específicos:")
        for caso in casos_test:
            resultado = self.limpiar_origen_autor(caso)
            estado = "✅ CONSERVADO" if resultado is not None else "❌ ELIMINADO"
            print(f"'{caso}' -> {estado}")
        
        print(f"\n=== REEMPLAZANDO COLUMNA ORIGINAL ===")
        self.df['OrigenAutor'] = self.df['OrigenAutor_limpio']
        self.df.drop('OrigenAutor_limpio', axis=1, inplace=True)
        
        print("✅ Columna OrigenAutor limpiada exitosamente")
        print(f"Valores únicos finales en OrigenAutor: {self.df['OrigenAutor'].nunique()}")
        
        # Mostrar muestra de los valores finales más comunes
        print(f"\n=== TOP 15 PAÍSES/LUGARES MÁS COMUNES (DESPUÉS DE LIMPIEZA) ===")
        valores_finales = self.df['OrigenAutor'].value_counts().head(15)
        for valor, count in valores_finales.items():
            print(f"'{valor}': {count} opiniones")
        
        return self.df
    
    def completar_valores_nulos(self):
        """
        Completa valores nulos en el dataset con valores descriptivos.
        """
        print("=== COMPLETANDO VALORES NULOS EN DATASET ===")
        
        # Mostrar valores nulos antes de la limpieza
        print("Valores nulos ANTES de completar:")
        if 'Titulo' in self.df.columns:
            print(f"- Titulo: {self.df['Titulo'].isna().sum()} nulos")
        if 'TipoViaje' in self.df.columns:
            print(f"- TipoViaje: {self.df['TipoViaje'].isna().sum()} nulos")
        if 'OrigenAutor' in self.df.columns:
            print(f"- OrigenAutor: {self.df['OrigenAutor'].isna().sum()} nulos")
        
        # Completar valores nulos con valores descriptivos
        if 'Titulo' in self.df.columns:
            self.df['Titulo'].fillna('sin titulo', inplace=True)
        if 'TipoViaje' in self.df.columns:
            self.df['TipoViaje'].fillna('desconocido', inplace=True)
        if 'OrigenAutor' in self.df.columns:
            self.df['OrigenAutor'].fillna('anonimo', inplace=True)
        
        # Mostrar valores nulos después de la limpieza
        print("\nValores nulos DESPUÉS de completar:")
        if 'Titulo' in self.df.columns:
            print(f"- Titulo: {self.df['Titulo'].isna().sum()} nulos")
        if 'TipoViaje' in self.df.columns:
            print(f"- TipoViaje: {self.df['TipoViaje'].isna().sum()} nulos")
        if 'OrigenAutor' in self.df.columns:
            print(f"- OrigenAutor: {self.df['OrigenAutor'].isna().sum()} nulos")
        
        print("\n✅ Valores nulos completados exitosamente")
        
        # Mostrar algunos ejemplos de los valores agregados
        print(f"\n=== DISTRIBUCIÓN DE VALORES AGREGADOS ===")
        if 'Titulo' in self.df.columns:
            print(f"'sin titulo': {(self.df['Titulo'] == 'sin titulo').sum()} registros")
        if 'TipoViaje' in self.df.columns:
            print(f"'desconocido': {(self.df['TipoViaje'] == 'desconocido').sum()} registros")
        if 'OrigenAutor' in self.df.columns:
            print(f"'anonimo': {(self.df['OrigenAutor'] == 'anonimo').sum()} registros")
        
        return self.df
    
    def eliminar_duplicados(self):
        """
        Elimina duplicados del DataFrame.
        """
        print("=== ELIMINACIÓN DE DUPLICADOS ===")
        
        # Guardar dimensiones antes de eliminar duplicados
        filas_antes = len(self.df)
        
        # Duplicados completos
        duplicados_completos = self.df.duplicated().sum()
        print(f"Filas completamente duplicadas encontradas: {duplicados_completos}")
        
        # Duplicados por combinación de columnas importantes
        if 'Titulo' in self.df.columns and 'Review' in self.df.columns:
            duplicados_contenido = self.df.duplicated(subset=['Titulo', 'Review', 'Ciudad', 'Atraccion']).sum()
            print(f"Duplicados por título + review + ciudad + atracción: {duplicados_contenido}")
        
        # Eliminar duplicados completos
        if duplicados_completos > 0:
            porcentaje_duplicados = (duplicados_completos / len(self.df)) * 100
            print(f"Porcentaje de duplicados completos: {porcentaje_duplicados:.2f}%")
            
            print(f"\n🔄 Eliminando {duplicados_completos} filas duplicadas...")
            self.df = self.df.drop_duplicates()
            
            filas_despues = len(self.df)
            filas_eliminadas = filas_antes - filas_despues
            
            print(f"✅ Duplicados eliminados exitosamente")
            print(f"   Filas antes: {filas_antes:,}")
            print(f"   Filas después: {filas_despues:,}")
            print(f"   Filas eliminadas: {filas_eliminadas:,}")
        else:
            print("✅ No se encontraron duplicados completos")
        
        return self.df
    
    def eliminar_columna_fechaopinion(self):
        """
        Elimina completamente la columna FechaOpinion por exceso de valores nulos.
        """
        print("=== ELIMINACIÓN DE COLUMNA FechaOpinion ===")
        
        if 'FechaOpinion' in self.df.columns:
            nulos_fechaopinion = self.df['FechaOpinion'].isna().sum()
            total_filas = len(self.df)
            porcentaje_nulos = (nulos_fechaopinion / total_filas) * 100
            
            print(f"📊 Análisis de FechaOpinion:")
            print(f"   • Total de filas: {total_filas:,}")
            print(f"   • Valores nulos: {nulos_fechaopinion:,}")
            print(f"   • Porcentaje de nulos: {porcentaje_nulos:.1f}%")
            
            if porcentaje_nulos > 50:  # Si más del 50% son nulos
                print(f"\n🗑️ Eliminando columna FechaOpinion (exceso de valores nulos: {porcentaje_nulos:.1f}%)")
                self.df = self.df.drop('FechaOpinion', axis=1)
                print(f"✅ Columna FechaOpinion eliminada exitosamente")
                print(f"📊 Columnas restantes: {len(self.df.columns)}")
            else:
                print(f"ℹ️ Columna FechaOpinion conservada ({porcentaje_nulos:.1f}% de nulos es aceptable)")
        else:
            print("ℹ️ Columna FechaOpinion no encontrada en el dataset")
        
        return self.df
    
    def eliminar_filas_fechaestadia_nulas(self):
        """
        Elimina las filas que tienen valores nulos en FechaEstadia.
        """
        print("=== ELIMINACIÓN DE FILAS CON FechaEstadia NULA ===")
        
        if 'FechaEstadia' in self.df.columns:
            filas_antes = len(self.df)
            nulos_fechaestadia = self.df['FechaEstadia'].isna().sum()
            
            print(f"📊 Análisis de FechaEstadia:")
            print(f"   • Total de filas: {filas_antes:,}")
            print(f"   • Filas con FechaEstadia nula: {nulos_fechaestadia:,}")
            print(f"   • Porcentaje de nulos: {(nulos_fechaestadia/filas_antes)*100:.2f}%")
            
            if nulos_fechaestadia > 0:
                # Mostrar algunas filas que serán eliminadas para referencia
                print(f"\n📋 Muestra de filas que serán eliminadas:")
                filas_nulas = self.df[self.df['FechaEstadia'].isna()]
                if len(filas_nulas) > 0:
                    muestra = filas_nulas[['Ciudad', 'Atraccion', 'FechaEstadia']].head(5)
                    for idx, row in muestra.iterrows():
                        print(f"   • {row['Ciudad']} - {row['Atraccion']}: FechaEstadia = {row['FechaEstadia']}")
                
                print(f"\n🗑️ Eliminando {nulos_fechaestadia} filas con FechaEstadia nula...")
                self.df = self.df.dropna(subset=['FechaEstadia'])
                
                filas_despues = len(self.df)
                filas_eliminadas = filas_antes - filas_despues
                
                print(f"✅ Filas con FechaEstadia nula eliminadas exitosamente")
                print(f"   • Filas antes: {filas_antes:,}")
                print(f"   • Filas después: {filas_despues:,}")
                print(f"   • Filas eliminadas: {filas_eliminadas:,}")
                print(f"   • Verificación: FechaEstadia nulas restantes = {self.df['FechaEstadia'].isna().sum()}")
            else:
                print("✅ No se encontraron filas con FechaEstadia nula")
        else:
            print("ℹ️ Columna FechaEstadia no encontrada en el dataset")
        
        return self.df

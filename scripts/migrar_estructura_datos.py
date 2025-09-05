#!/usr/bin/env python3
"""
Script de Migración - Migra datos a la nueva estructura raw/processed
==================================================================

Este script migra datos de la estructura antigua a la nueva estructura:
- data/cancun/ → data/raw/cancun/
- data/cdmx/ → data/raw/cdmx/
- data/datasets_por_ciudad/ → data/processed/datasets_por_ciudad/
- data/dataset_opiniones_consolidado.csv → data/processed/dataset_opiniones_consolidado.csv

Uso:
    python migrar_estructura_datos.py [--data-dir ../data] [--dry-run]
"""

import os
import shutil
import argparse
from pathlib import Path


def crear_directorios(ruta_data):
    """Crea los directorios raw y processed."""
    ruta_raw = os.path.join(ruta_data, 'raw')
    ruta_processed = os.path.join(ruta_data, 'processed')
    
    os.makedirs(ruta_raw, exist_ok=True)
    os.makedirs(ruta_processed, exist_ok=True)
    
    return ruta_raw, ruta_processed


def migrar_carpetas_ciudades(ruta_data, ruta_raw, dry_run=False):
    """Migra las carpetas de ciudades al directorio raw."""
    carpetas_ciudades = ['cancun', 'cdmx']
    movimientos = []
    
    for ciudad in carpetas_ciudades:
        origen = os.path.join(ruta_data, ciudad)
        destino = os.path.join(ruta_raw, ciudad)
        
        if os.path.exists(origen):
            if os.path.exists(destino):
                print(f"⚠️  SKIP: {destino} ya existe")
            else:
                movimientos.append((origen, destino))
                if dry_run:
                    print(f"🔄 DRY-RUN: Movería {origen} → {destino}")
                else:
                    shutil.move(origen, destino)
                    print(f"✅ MIGRADO: {origen} → {destino}")
        else:
            print(f"ℹ️  INFO: {origen} no existe, no hay nada que migrar")
    
    return movimientos


def migrar_archivos_procesados(ruta_data, ruta_processed, dry_run=False):
    """Migra archivos procesados al directorio processed."""
    elementos_a_migrar = [
        'datasets_por_ciudad',
        'dataset_opiniones_consolidado.csv'
    ]
    
    movimientos = []
    
    for elemento in elementos_a_migrar:
        origen = os.path.join(ruta_data, elemento)
        destino = os.path.join(ruta_processed, elemento)
        
        if os.path.exists(origen):
            if os.path.exists(destino):
                print(f"⚠️  SKIP: {destino} ya existe")
            else:
                movimientos.append((origen, destino))
                if dry_run:
                    print(f"🔄 DRY-RUN: Movería {origen} → {destino}")
                else:
                    shutil.move(origen, destino)
                    print(f"✅ MIGRADO: {origen} → {destino}")
        else:
            print(f"ℹ️  INFO: {origen} no existe, no hay nada que migrar")
    
    return movimientos


def verificar_estructura_final(ruta_data):
    """Verifica que la nueva estructura esté correcta."""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE LA NUEVA ESTRUCTURA")
    print("="*60)
    
    ruta_raw = os.path.join(ruta_data, 'raw')
    ruta_processed = os.path.join(ruta_data, 'processed')
    
    # Verificar raw
    print(f"\n📁 Verificando {ruta_raw}:")
    if os.path.exists(ruta_raw):
        contenido_raw = os.listdir(ruta_raw)
        for item in sorted(contenido_raw):
            item_path = os.path.join(ruta_raw, item)
            if os.path.isdir(item_path):
                archivos = len([f for f in os.listdir(item_path) if f.endswith('.csv')])
                print(f"   📂 {item}/ ({archivos} archivos CSV)")
            else:
                print(f"   📄 {item}")
    else:
        print("   ❌ No existe")
    
    # Verificar processed
    print(f"\n📁 Verificando {ruta_processed}:")
    if os.path.exists(ruta_processed):
        contenido_processed = os.listdir(ruta_processed)
        for item in sorted(contenido_processed):
            item_path = os.path.join(ruta_processed, item)
            if os.path.isdir(item_path):
                archivos = len(os.listdir(item_path))
                print(f"   📂 {item}/ ({archivos} archivos)")
            else:
                print(f"   📄 {item}")
    else:
        print("   ❌ No existe")


def main():
    parser = argparse.ArgumentParser(description='Migra datos a la nueva estructura raw/processed')
    parser.add_argument('--data-dir', default='../data', 
                        help='Directorio de datos (default: ../data)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Solo muestra lo que haría sin ejecutar cambios')
    
    args = parser.parse_args()
    
    # Convertir a ruta absoluta
    ruta_data = os.path.abspath(args.data_dir)
    
    print("="*60)
    print("🔄 MIGRACIÓN A NUEVA ESTRUCTURA DE DATOS")
    print("="*60)
    print(f"📁 Directorio de trabajo: {ruta_data}")
    
    if args.dry_run:
        print("🔍 MODO DRY-RUN: No se realizarán cambios reales")
    
    if not os.path.exists(ruta_data):
        print(f"❌ Error: El directorio {ruta_data} no existe")
        return 1
    
    # Crear directorios raw y processed
    print(f"\n🏗️  Creando directorios raw y processed...")
    ruta_raw, ruta_processed = crear_directorios(ruta_data)
    print(f"✅ Directorios listos: raw, processed")
    
    # Migrar carpetas de ciudades
    print(f"\n🏙️  Migrando carpetas de ciudades a raw...")
    movimientos_raw = migrar_carpetas_ciudades(ruta_data, ruta_raw, args.dry_run)
    
    # Migrar archivos procesados
    print(f"\n📊 Migrando archivos procesados a processed...")
    movimientos_processed = migrar_archivos_procesados(ruta_data, ruta_processed, args.dry_run)
    
    # Resumen
    total_movimientos = len(movimientos_raw) + len(movimientos_processed)
    
    print(f"\n" + "="*60)
    print("📋 RESUMEN DE MIGRACIÓN")
    print("="*60)
    print(f"   Elementos migrados a raw: {len(movimientos_raw)}")
    print(f"   Elementos migrados a processed: {len(movimientos_processed)}")
    print(f"   Total elementos migrados: {total_movimientos}")
    
    if not args.dry_run and total_movimientos > 0:
        verificar_estructura_final(ruta_data)
        print(f"\n✅ MIGRACIÓN COMPLETADA")
        print(f"💡 Ahora puedes usar la nueva estructura en tu código")
    elif args.dry_run:
        print(f"\n🔍 DRY-RUN COMPLETADO")
        print(f"💡 Ejecuta sin --dry-run para realizar la migración")
    else:
        print(f"\nℹ️  No había elementos para migrar")
    
    return 0


if __name__ == '__main__':
    exit(main())

import pandas as pd

# Ruta del archivo
ruta_dataset = "./data/processed/dataset_opiniones_analisis.csv"

# Cargar el dataset
df = pd.read_csv(ruta_dataset)

# Verificar si la columna existe y eliminarla
if 'SubjetividadConLLM' in df.columns:
    df.drop(columns=['SubjetividadConLLM'], inplace=True)
    print("Columna 'SubjetividadConLLM' eliminada.")
else:
    print("La columna 'SubjetividadConLLM' no existe en el dataset.")

# Sobrescribir el archivo
try:
    df.to_csv(ruta_dataset, index=False, encoding='utf-8')
    print(f"Dataset sobrescrito exitosamente en: {ruta_dataset}")
except Exception as e:
    print(f"Error al sobrescribir el archivo: {e}")
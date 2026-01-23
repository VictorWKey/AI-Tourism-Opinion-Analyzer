"""
Fase 03: Análisis de Subjetividad
===================================
Analiza la subjetividad de las opiniones turísticas usando modelo BERT fine-tuned.
"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


class SubjectivityDataset(Dataset):
    """Dataset para clasificación binaria de subjetividad."""
    
    def __init__(self, texts, tokenizer, max_length):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'idx': idx
        }


class AnalizadorSubjetividad:
    """
    Clase para análisis de subjetividad usando modelo BERT fine-tuned.
    Agrega columna 'Subjetividad' al dataset.
    """
    
    DATASET_PATH = "data/dataset.csv"
    MODEL_PATH = "models/subjectivity_task/best_model"
    MAX_LENGTH = 128
    BATCH_SIZE = 32
    
    # Mapeo de IDs a etiquetas
    ID_TO_LABEL = {0: 'Subjetiva', 1: 'Mixta'}
    
    def __init__(self):
        """Inicializa el analizador."""
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.modelo_cargado = False
        
    def cargar_modelo(self):
        """Carga el modelo fine-tuned y tokenizador."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_PATH)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_PATH)
            self.model.to(self.device)
            self.model.eval()
            self.modelo_cargado = True
            
        except Exception as e:
            raise RuntimeError(f"Error al cargar modelo: {e}")
    
    def predecir_batch(self, dataloader):
        """
        Predice subjetividad para un batch de datos.
        
        Args:
            dataloader: DataLoader con los datos
            
        Returns:
            np.array: Array con las predicciones (clases)
        """
        all_predictions = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="   Progreso"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits.cpu().numpy()
                
                # Obtener clase predicha (argmax)
                predicted_classes = np.argmax(logits, axis=1)
                all_predictions.extend(predicted_classes)
        
        return np.array(all_predictions)
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe la columna 'Subjetividad' en el dataset.
        """
        try:
            df = pd.read_csv(self.DATASET_PATH)
            return 'Subjetividad' in df.columns
        except:
            return False
    
    def procesar(self, forzar=False):
        """
        Procesa el dataset completo y agrega columna 'Subjetividad'.
        Modifica el archivo dataset.csv directamente.
        
        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        
        # Cargar dataset
        df = pd.read_csv(self.DATASET_PATH)
        total = len(df)
        
        # Cargar modelo
        self.cargar_modelo()
        
        # Crear dataset y dataloader
        dataset = SubjectivityDataset(
            df['TituloReview'].tolist(),
            self.tokenizer,
            self.MAX_LENGTH
        )
        
        dataloader = DataLoader(
            dataset,
            batch_size=self.BATCH_SIZE,
            shuffle=False
        )
        
        # Predecir subjetividad
        predicted_classes = self.predecir_batch(dataloader)
        
        # Mapear IDs a etiquetas
        subjetividad = [self.ID_TO_LABEL[pred] for pred in predicted_classes]
        
        # Agregar columna al dataset
        df['Subjetividad'] = subjetividad
        
        # Guardar dataset modificado
        df.to_csv(self.DATASET_PATH, index=False)
        
        # Estadísticas
        distribucion = df['Subjetividad'].value_counts()
        print(f"✅ Análisis completado: {total} opiniones procesadas")
        print(f"   Subjetiva: {distribucion.get('Subjetiva', 0)} | "
              f"Mixta: {distribucion.get('Mixta', 0)}")

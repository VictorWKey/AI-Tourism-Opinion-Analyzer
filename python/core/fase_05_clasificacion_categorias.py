"""
Fase 05: Clasificación de Categorías Multi-etiqueta
===================================================
Clasifica las opiniones turísticas en múltiples categorías usando un modelo BERT fine-tuned.
"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, logging as transformers_logging
import json
import os
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')
transformers_logging.set_verbosity_error()
from config.config import ConfigDataset


class ClasificadorCategorias:
    """
    Clasifica opiniones en categorías turísticas usando un modelo BERT fine-tuned.
    Añade una columna 'Categorias' al dataset con las etiquetas predichas.
    """
    
    def __init__(self):
        # HuggingFace model ID
        self.model_id = 'victorwkey/tourism-categories-bert'
        
        # Get absolute paths for optional local files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        python_dir = os.path.dirname(script_dir)
        
        self.dataset_path = str(ConfigDataset.get_dataset_path())
        self.thresholds_path = os.path.join(python_dir, 'models', 'multilabel_task', 'optimal_thresholds.json')
        self.max_length = 128
        self.batch_size = 32
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.label_names = [
            'Alojamiento',
            'Gastronomía',
            'Transporte',
            'Eventos y festivales',
            'Historia y cultura',
            'Compras',
            'Deportes y aventura',
            'Vida nocturna',
            'Naturaleza',
            'Personal y servicio',
            'Seguridad',
            'Fauna y vida animal'
        ]
        
        self.model = None
        self.tokenizer = None
        self.optimal_thresholds = None
    
    def _cargar_modelo(self):
        """Carga el modelo BERT fine-tuned desde la caché local y los thresholds optimizados (si existen)."""
        cache_dir = ConfigDataset.get_models_cache_dir()
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, cache_dir=cache_dir)
        except TypeError:
            # Si hay error, intentar sin parámetros extras
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, cache_dir=cache_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_id, cache_dir=cache_dir)
        self.model.to(self.device)
        self.model.eval()
        
        # Cargar thresholds optimizados (si existen, sino usar 0.5 por defecto)
        try:
            with open(self.thresholds_path, 'r', encoding='utf-8') as f:
                thresholds_dict = json.load(f)
            self.optimal_thresholds = np.array([thresholds_dict[label] for label in self.label_names])
            print(f"   ✅ Thresholds cargados desde: {self.thresholds_path}")
        except FileNotFoundError:
            # Usar 0.5 como threshold por defecto para todas las clases
            self.optimal_thresholds = np.full(len(self.label_names), 0.5)
    
    def _crear_dataset(self, texts):
        """Crea un dataset PyTorch para las predicciones."""
        class ReviewDataset(Dataset):
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
                    'attention_mask': encoding['attention_mask'].squeeze(0)
                }
        
        return ReviewDataset(texts, self.tokenizer, self.max_length)
    
    def _predecir(self, dataloader):
        """Realiza predicciones con el modelo."""
        all_predictions = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="   Progreso"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                predictions = torch.sigmoid(outputs.logits).cpu().numpy()
                all_predictions.extend(predictions)
        
        return np.array(all_predictions)
    
    def _aplicar_thresholds(self, predictions):
        """Aplica los thresholds optimizados y convierte a etiquetas."""
        categorias_lista = []
        
        for pred in predictions:
            # Aplicar thresholds optimizados
            etiquetas_activas = pred > self.optimal_thresholds
            
            # Obtener nombres de etiquetas
            categorias = [self.label_names[i] for i in range(len(self.label_names)) 
                         if etiquetas_activas[i]]
            
            categorias_lista.append(categorias)
        
        return categorias_lista
    
    def _guardar_scores(self, predictions):
        """
        Guarda las probabilidades de cada categoría para uso de otras fases.
        
        Args:
            predictions: Array numpy con las probabilidades (shape: [n_samples, n_labels])
        """
        import os
        
        # Crear carpeta shared si no existe
        shared_dir = os.path.join(os.path.dirname(self.dataset_path), 'shared')
        os.makedirs(shared_dir, exist_ok=True)
        
        # Crear diccionario con scores
        scores_dict = {}
        for idx, pred in enumerate(predictions):
            scores_dict[idx] = {
                self.label_names[i]: float(pred[i]) 
                for i in range(len(self.label_names))
            }
        
        # Guardar en JSON
        scores_path = os.path.join(shared_dir, 'categorias_scores.json')
        with open(scores_path, 'w', encoding='utf-8') as f:
            json.dump(scores_dict, f, ensure_ascii=False, indent=2)
        
        print(f"   • Probabilidades guardadas en: {scores_path}")
    
    def ya_procesado(self):
        """
        Verifica si esta fase ya fue ejecutada.
        Revisa si existe la columna 'Categorias' en el dataset.
        """
        try:
            df = pd.read_csv(self.dataset_path)
            return 'Categorias' in df.columns
        except:
            return False
    
    def procesar(self, forzar=False):
        """
        Procesa el dataset completo:
        1. Carga el modelo y thresholds
        2. Realiza predicciones
        3. Añade columna 'Categorias' al dataset
        4. Guarda probabilidades en data/shared/ para otras fases
        
        Args:
            forzar: Si es True, ejecuta incluso si ya fue procesado
        """
        if not forzar and self.ya_procesado():
            print("   ⏭️  Fase ya ejecutada previamente (omitiendo)")
            return
        
        # Cargar dataset
        df = pd.read_csv(self.dataset_path)
        
        # Cargar modelo
        self._cargar_modelo()
        
        # Crear dataset y dataloader
        dataset = self._crear_dataset(df['TituloReview'].tolist())
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        
        print(f"Clasificando {len(df)} opiniones en {len(self.label_names)} categorías...")
        
        # Realizar predicciones
        predictions = self._predecir(dataloader)
        
        # Guardar probabilidades para otras fases
        self._guardar_scores(predictions)
        
        # Aplicar thresholds y obtener etiquetas
        categorias = self._aplicar_thresholds(predictions)
        
        # Convertir listas a strings JSON para guardar en CSV (sin ensure_ascii para evitar dobles comillas)
        df['Categorias'] = [str(cat) for cat in categorias]
        
        # Guardar dataset actualizado
        df.to_csv(self.dataset_path, index=False)
        
        print(f"✅ Clasificación completada. Columna 'Categorias' añadida al dataset.")
        
        # Estadísticas básicas
        total_categorias = sum(len(cat) for cat in categorias)
        promedio_categorias = total_categorias / len(categorias)
        sin_categorias = sum(1 for cat in categorias if len(cat) == 0)
        print(f"   • Promedio de categorías por opinión: {promedio_categorias:.2f}")
        if sin_categorias > 0:
            print(f"   ⚠️  Advertencia: {sin_categorias} opiniones sin categoría asignada (no superaron thresholds)")

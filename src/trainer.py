# src/trainer.py
import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from preprocessor import IngredientProcessor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChefAI_Trainer:
    """
    Entrenador del modelo ChefAI
    """
    
    def __init__(self):
        self.processor = IngredientProcessor()
        self.vectorizer = None
        self.matrix = None
        self.df = None
        self.metadata = {}
    
    def cargar_datos(self, ruta_json: str) -> pd.DataFrame:
        """Carga y valida los datos de recetas"""
        logger.info(f"Cargando datos desde {ruta_json}")
        
        with open(ruta_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.df = pd.DataFrame(data)
        
        required_columns = ['id', 'nombre', 'ingredientes']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Columna requerida '{col}' no encontrada")
        
        logger.info(f"Datos cargados: {len(self.df)} recetas")
        
        return self.df
    
    def preparar_texto_entrenamiento(self) -> pd.Series:
        """Prepara el texto para entrenamiento TF-IDF"""
        logger.info("Procesando ingredientes para entrenamiento...")
        
        textos = self.df['ingredientes'].apply(self.processor.procesar_receta)
        
        longitudes = textos.str.split().str.len()
        logger.info(f"Longitud promedio de texto: {longitudes.mean():.1f} términos")
        
        return textos
    
    def entrenar_vectorizador(self, textos: pd.Series, ngram_range=(1, 2)):
        """Entrena el vectorizador TF-IDF"""
        logger.info("Entrenando vectorizador TF-IDF...")
        
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            min_df=1,
            max_df=0.7,
            sublinear_tf=True,  # penaliza repetición excesiva
            analyzer='word',
            token_pattern=r'(?u)\b\w+\b'
        )
        
        self.matrix = self.vectorizer.fit_transform(textos)
        
        logger.info(f"Vectorizador entrenado:")
        logger.info(f"  - Vocabulario tamaño: {len(self.vectorizer.vocabulary_)}")
        logger.info(f"  - Matriz shape: {self.matrix.shape}")
        
        return self.vectorizer, self.matrix
    
    def calcular_estadisticas(self):
        """Calcula estadísticas del modelo"""
        feature_names = self.vectorizer.get_feature_names_out()
        
        self.metadata = {
            'total_recetas': len(self.df),
            'vocabulario_tamano': len(self.vectorizer.vocabulary_),
            'densidad_matriz': float((self.matrix > 0).sum() / self.matrix.size),
            'tamano_matriz': self.matrix.shape
        }
        
        return self.metadata
    
    def guardar_modelo(self, ruta: str = 'modelo/chefai_brain.pkl'):
        """Guarda el modelo entrenado"""
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        
        modelo = {
            'vectorizer': self.vectorizer,
            'matrix': self.matrix,
            'recipes_df': self.df,
            'processor': self.processor,
            'metadata': self.metadata
        }
        
        joblib.dump(modelo, ruta, compress=3)
        logger.info(f"Modelo guardado en {ruta}")
        
        with open('modelo/metadata.json', 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def entrenar_completo(self, ruta_json: str, ruta_salida: str = 'modelo/chefai_brain.pkl'):
        """Pipeline completo de entrenamiento"""
        logger.info("=== INICIANDO ENTRENAMIENTO CHEFAI ===")
        
        self.cargar_datos(ruta_json)
        textos = self.preparar_texto_entrenamiento()
        self.entrenar_vectorizador(textos)
        self.calcular_estadisticas()
        self.guardar_modelo(ruta_salida)
        
        logger.info("=== ENTRENAMIENTO COMPLETADO ===")
        
        print("\n📊 RESUMEN DEL MODELO:")
        print(f"   📝 Recetas: {self.metadata['total_recetas']}")
        print(f"   🔤 Vocabulario: {self.metadata['vocabulario_tamano']} términos")
        print(f"   🎯 Densidad: {self.metadata['densidad_matriz']:.2%}")
        
        return self.metadata


if __name__ == "__main__":
    trainer = ChefAI_Trainer()
    trainer.entrenar_completo(
        ruta_json='data/recetas.json',
        ruta_salida='modelo/chefai_brain.pkl'
    )
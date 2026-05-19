# src/recomendador.py
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional, Union
import logging
from preprocessor import IngredientProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChefAI_Recomendador:
    def __init__(self, ruta_modelo: str = 'modelo/chefai_brain.pkl'):
        logger.info(f"Cargando modelo desde {ruta_modelo}")
        self.modelo = joblib.load(ruta_modelo)
        self.vectorizer = self.modelo['vectorizer']
        self.matrix = self.modelo['matrix']
        self.df = self.modelo['recipes_df']
        self.processor = self.modelo['processor']
        logger.info(f"Modelo cargado: {len(self.df)} recetas")
    
    def recomendar(self, ingredientes_usuario: Union[str, List[str]], 
                   top_n: int = 5,
                   filtros: Optional[Dict] = None) -> List[Dict]:
        texto_usuario = self.processor.procesar_usuario(ingredientes_usuario)
        vector_usuario = self.vectorizer.transform([texto_usuario])
        similitudes = cosine_similarity(vector_usuario, self.matrix).flatten()
        indices_ordenados = np.argsort(similitudes)[::-1]
        resultados = []
        for idx in indices_ordenados:
            receta = self.df.iloc[idx].to_dict()
            if self._cumple_filtros(receta, filtros):
                resultados.append({
                    'id': int(receta['id']),
                    'nombre': receta['nombre'],
                    'similitud': float(similitudes[idx]),
                    'ingredientes': receta.get('ingredientes', []),
                    'instrucciones': receta.get('instrucciones', ''),
                    'tiempo': receta.get('tiempo', 'No especificado'),
                    'dificultad': receta.get('dificultad', 'media'),
                    'coincidencia': f"{similitudes[idx]:.1%}",
                    'ingredientes_faltantes': self._calcular_faltantes(ingredientes_usuario, receta.get('ingredientes', []))
                })
                if len(resultados) >= top_n:
                    break
        return resultados
    
    def _cumple_filtros(self, receta: Dict, filtros: Optional[Dict]) -> bool:
        if not filtros:
            return True
        if 'tags' in filtros:
            tags_receta = set(receta.get('tags', []))
            tags_requeridos = set(filtros['tags'])
            if not tags_requeridos.issubset(tags_receta):
                return False
        return True
    
    def _calcular_faltantes(self, ingredientes_usuario, ingredientes_receta):
        if isinstance(ingredientes_usuario, str):
            ingredientes_usuario = [i.strip() for i in ingredientes_usuario.split(',')]
        norm_usuario = self.processor.normalizar_lista(ingredientes_usuario)
        norm_receta = self.processor.normalizar_lista(ingredientes_receta)
        return list(norm_receta - norm_usuario)[:5]
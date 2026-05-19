# src/recomendador_semantico.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from recomendador import ChefAI_Recomendador
from red_semantica import RedSemanticaIngredientes
from typing import List, Dict, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecomendadorSemantico(ChefAI_Recomendador):
    """Recomendador mejorado con red semántica"""
    
    def __init__(self, ruta_modelo: str = 'modelo/chefai_brain.pkl',
                 ruta_red: str = 'modelo/red_semantica.pkl'):
        super().__init__(ruta_modelo)
        
        self.red_semantica = RedSemanticaIngredientes()
        try:
            self.red_semantica.cargar(ruta_red)
            logger.info("Red semántica cargada exitosamente")
        except FileNotFoundError:
            logger.warning(f"No se encontró red semántica en {ruta_red}")
            self.red_semantica = None
    
    def expandir_ingredientes_usuario(self, ingredientes: List[str], 
                                      profundidad: int = 1) -> Dict[str, float]:
        """Expande los ingredientes usando la red semántica"""
        expandido = {}
        for ing in ingredientes:
            expandido[ing] = 1.0
            if self.red_semantica:
                expansion = self.red_semantica.expandir_concepto(ing, profundidad)
                for concepto, peso in expansion.items():
                    if concepto != ing:
                        if concepto not in expandido or expandido[concepto] < peso:
                            expandido[concepto] = peso
        return expandido
    
    def vectorizar_con_semantica(self, ingredientes: List[str]) -> np.ndarray:
        """Vectoriza considerando expansión semántica"""
        ingredientes_expandidos = self.expandir_ingredientes_usuario(ingredientes)
        texto_expandido = []
        for ing, peso in ingredientes_expandidos.items():
            repeticiones = int(peso * 3) + 1
            texto_expandido.extend([ing] * repeticiones)
        texto_final = ' '.join(texto_expandido)
        return self.vectorizer.transform([texto_final])
    
    def recomendar_con_semantica(self, 
                                 ingredientes_usuario: Union[str, List[str]],
                                 top_n: int = 5,
                                 filtros: Optional[Dict] = None,
                                 usar_semantica: bool = True) -> List[Dict]:
        """Recomienda usando expansión semántica"""
        if isinstance(ingredientes_usuario, str):
            ingredientes_usuario = [i.strip() for i in ingredientes_usuario.split(',')]
        
        if usar_semantica and self.red_semantica:
            vector_usuario = self.vectorizar_con_semantica(ingredientes_usuario)
        else:
            texto = self.processor.procesar_usuario(ingredientes_usuario)
            vector_usuario = self.vectorizer.transform([texto])
        
        similitudes = cosine_similarity(vector_usuario, self.matrix).flatten()
        indices_ordenados = np.argsort(similitudes)[::-1]
        
        resultados = []
        for idx in indices_ordenados:
            receta = self.df.iloc[idx].to_dict()
            if self._cumple_filtros(receta, filtros):
                resultado = {
                    'id': int(receta['id']),
                    'nombre': receta['nombre'],
                    'similitud': float(similitudes[idx]),
                    'ingredientes': receta.get('ingredientes', []),
                    'instrucciones': receta.get('instrucciones', ''),
                    'tiempo': receta.get('tiempo', 'No especificado'),
                    'dificultad': receta.get('dificultad', 'media'),
                    'coincidencia': f"{similitudes[idx]:.1%}",
                    'ingredientes_faltantes': self._calcular_faltantes_con_semantica(
                        ingredientes_usuario, receta.get('ingredientes', [])
                    )
                }
                if self.red_semantica:
                    resultado['coherencia_semantica'] = self.red_semantica.calcular_coherencia_receta(
                        receta.get('ingredientes', [])
                    )
                resultados.append(resultado)
                if len(resultados) >= top_n:
                    break
        return resultados
    
    def _calcular_faltantes_con_semantica(self, ingredientes_usuario: List[str],
                                          ingredientes_receta: List[str]) -> List[str]:
        """Calcula faltantes considerando sustitutos"""
        usuario_expandido = set(self.processor.normalizar_lista(ingredientes_usuario))
        if self.red_semantica:
            for ing in ingredientes_usuario:
                sustitutos = self.red_semantica.sugerir_sustitutos(ing)
                for s in sustitutos:
                    usuario_expandido.add(s['ingrediente'])
        receta_norm = self.processor.normalizar_lista(ingredientes_receta)
        faltantes = receta_norm - usuario_expandido
        return list(faltantes)[:5]
    
    def sugerir_complementos(self, ingredientes: List[str], top_n: int = 5) -> List[Dict]:
        """Sugiere ingredientes que complementarían bien"""
        if not self.red_semantica:
            return []
        todos_complementos = {}
        for ing in ingredientes:
            complementos = self.red_semantica.recomendar_complementos(ing)
            for comp in complementos:
                ing_comp = comp['ingrediente']
                if ing_comp not in ingredientes:
                    if ing_comp not in todos_complementos:
                        todos_complementos[ing_comp] = 0
                    todos_complementos[ing_comp] += comp['peso']
        sugerencias = [
            {'ingrediente': ing, 'peso': peso}
            for ing, peso in sorted(todos_complementos.items(), 
                                   key=lambda x: x[1], reverse=True)[:top_n]
        ]
        return sugerencias
    
    def explicar_recomendacion(self, receta: Dict, ingredientes_usuario: List[str]) -> Dict:
        """Explica por qué se recomendó una receta"""
        explicacion = {
            'receta': receta['nombre'],
            'coincidencia_directa': [],
            'coincidencia_semantica': [],
            'sustitutos_usados': []
        }
        usuario_norm = self.processor.normalizar_lista(ingredientes_usuario)
        for ing_receta in receta['ingredientes']:
            ing_norm = self.processor.limpiar_ingrediente(ing_receta)
            if ing_norm in usuario_norm:
                explicacion['coincidencia_directa'].append(ing_receta)
            elif self.red_semantica:
                for ing_usuario in ingredientes_usuario:
                    sim = self.red_semantica.similitud_semantica(ing_usuario, ing_receta)
                    if sim > 0.5:
                        explicacion['coincidencia_semantica'].append({
                            'usuario_tiene': ing_usuario,
                            'receta_necesita': ing_receta,
                            'similitud': sim
                        })
                        break
        return explicacion
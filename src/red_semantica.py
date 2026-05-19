# src/red_semantica.py
import networkx as nx
import json
import pickle
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedSemanticaIngredientes:
    """
    Red semántica para relaciones entre ingredientes
    """
    
    def __init__(self):
        # Grafo dirigido para relaciones asimétricas
        self.grafo = nx.DiGraph()
        
        # Pesos por tipo de relación
        self.pesos_relaciones = {
            'sinonimo': 1.0,
            'tipo_de': 0.9,
            'derivado_de': 0.8,
            'sustituto': 0.7,
            'complementa': 0.6,
            'parte_de': 0.5
        }
        
        # Estadísticas de la red
        self.estadisticas = {
            'total_nodos': 0,
            'total_aristas': 0,
            'tipos_relaciones': defaultdict(int)
        }
    
    def agregar_nodo(self, ingrediente: str, categoria: str = None, 
                     metadata: Dict = None):
        """
        Agrega un ingrediente como nodo en la red
        """
        ingrediente = ingrediente.lower()
        
        if ingrediente not in self.grafo:
            self.grafo.add_node(ingrediente)
            
            self.grafo.nodes[ingrediente]['categoria'] = categoria or 'general'
            self.grafo.nodes[ingrediente]['metadata'] = metadata or {}
            self.grafo.nodes[ingrediente]['grado_entrada'] = 0
            self.grafo.nodes[ingrediente]['grado_salida'] = 0
            
            self.estadisticas['total_nodos'] += 1
    
    def agregar_relacion(self, origen: str, destino: str, tipo: str, 
                         peso: float = None, bidireccional: bool = False):
        """
        Agrega una relación entre dos ingredientes
        """
        origen = origen.lower()
        destino = destino.lower()
        
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        
        if peso is None:
            peso = self.pesos_relaciones.get(tipo, 0.5)
        
        self.grafo.add_edge(origen, destino, 
                           tipo=tipo, 
                           peso=peso,
                           bidireccional=bidireccional)
        
        self.estadisticas['total_aristas'] += 1
        self.estadisticas['tipos_relaciones'][tipo] += 1
        
        if bidireccional:
            self.grafo.add_edge(destino, origen,
                               tipo=tipo,
                               peso=peso,
                               bidireccional=True)
            self.estadisticas['total_aristas'] += 1
        
        self.grafo.nodes[origen]['grado_salida'] = self.grafo.out_degree(origen)
        self.grafo.nodes[destino]['grado_entrada'] = self.grafo.in_degree(destino)
    
    def obtener_relaciones(self, ingrediente: str, tipo: str = None) -> List[Dict]:
        """Obtiene todas las relaciones de un ingrediente"""
        ingrediente = ingrediente.lower()
        
        if ingrediente not in self.grafo:
            return []
        
        relaciones = []
        for vecino, datos in self.grafo[ingrediente].items():
            if tipo is None or datos.get('tipo') == tipo:
                relaciones.append({
                    'ingrediente': vecino,
                    'tipo': datos.get('tipo'),
                    'peso': datos.get('peso', 0.5),
                    'direccion': 'salida'
                })
        
        for origen, datos in self.grafo.pred[ingrediente].items():
            if tipo is None or datos.get('tipo') == tipo:
                relaciones.append({
                    'ingrediente': origen,
                    'tipo': datos.get('tipo'),
                    'peso': datos.get('peso', 0.5),
                    'direccion': 'entrada'
                })
        
        return relaciones
    
    def expandir_concepto(self, ingrediente: str, profundidad: int = 1, 
                          umbral_peso: float = 0.5) -> Dict[str, float]:
        """Expande un concepto incluyendo sus relaciones semánticas"""
        if ingrediente not in self.grafo:
            return {ingrediente: 1.0}
        
        expandido = {ingrediente: 1.0}
        visitados = set([ingrediente])
        frontera = [(ingrediente, 1.0, 0)]
        
        while frontera:
            actual, peso_acum, nivel = frontera.pop(0)
            
            if nivel >= profundidad:
                continue
            
            for vecino, datos in self.grafo[actual].items():
                if vecino not in visitados:
                    peso_relacion = datos.get('peso', 0.5)
                    
                    if peso_relacion >= umbral_peso:
                        nuevo_peso = peso_acum * peso_relacion
                        
                        if vecino not in expandido or expandido[vecino] < nuevo_peso:
                            expandido[vecino] = nuevo_peso
                        
                        visitados.add(vecino)
                        frontera.append((vecino, nuevo_peso, nivel + 1))
        
        return expandido
    
    def similitud_semantica(self, ing1: str, ing2: str) -> float:
        """Calcula similitud semántica entre dos ingredientes"""
        ing1 = ing1.lower()
        ing2 = ing2.lower()
        
        if ing1 == ing2:
            return 1.0
        
        if ing1 not in self.grafo or ing2 not in self.grafo:
            return 0.0
        
        try:
            camino = nx.shortest_path(self.grafo.to_undirected(), ing1, ing2)
            distancia = len(camino) - 1
            similitud = 1.0 / (distancia + 1)
            return similitud
        except nx.NetworkXNoPath:
            return 0.0
    
    def calcular_coherencia_receta(self, ingredientes: List[str]) -> float:
        """Calcula qué tan coherente es una receta semánticamente"""
        if len(ingredientes) < 2:
            return 0.0
        
        suma_similitudes = 0.0
        pares = 0
        
        for i in range(len(ingredientes)):
            for j in range(i + 1, len(ingredientes)):
                sim = self.similitud_semantica(ingredientes[i], ingredientes[j])
                suma_similitudes += sim
                pares += 1
        
        return suma_similitudes / pares if pares > 0 else 0.0
    
    def recomendar_complementos(self, ingrediente: str, top_n: int = 5) -> List[Dict]:
        """Recomienda ingredientes que complementan bien al dado"""
        if ingrediente not in self.grafo:
            return []
        
        complementos = []
        
        for vecino, datos in self.grafo[ingrediente].items():
            if datos.get('tipo') == 'complementa':
                complementos.append({
                    'ingrediente': vecino,
                    'peso': datos.get('peso', 0.6),
                    'tipo': 'directo'
                })
        
        complementos.sort(key=lambda x: x['peso'], reverse=True)
        return complementos[:top_n]
    
    def sugerir_sustitutos(self, ingrediente: str, top_n: int = 3) -> List[Dict]:
        """Sugiere sustitutos para un ingrediente"""
        if ingrediente not in self.grafo:
            return []
        
        sustitutos = []
        
        for vecino, datos in self.grafo[ingrediente].items():
            if datos.get('tipo') == 'sustituto':
                sustitutos.append({
                    'ingrediente': vecino,
                    'peso': datos.get('peso', 0.7),
                    'confianza': datos.get('peso', 0.7)
                })
        
        sustitutos.sort(key=lambda x: x['peso'], reverse=True)
        return sustitutos[:top_n]
    
    def guardar(self, ruta: str = 'modelo/red_semantica.pkl'):
        """Guarda la red semántica"""
        import os
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        
        with open(ruta, 'wb') as f:
            pickle.dump({
                'grafo': self.grafo,
                'estadisticas': self.estadisticas,
                'pesos_relaciones': self.pesos_relaciones
            }, f)
        
        logger.info(f"Red semántica guardada en {ruta}")
    
    def cargar(self, ruta: str = 'modelo/red_semantica.pkl'):
        """Carga la red semántica"""
        with open(ruta, 'rb') as f:
            datos = pickle.load(f)
            self.grafo = datos['grafo']
            self.estadisticas = datos['estadisticas']
            self.pesos_relaciones = datos['pesos_relaciones']
        
        logger.info(f"Red semántica cargada: {self.estadisticas['total_nodos']} nodos, "
                    f"{self.estadisticas['total_aristas']} aristas")
    
    def exportar_json(self, ruta: str = 'modelo/red_semantica.json'):
        """Exporta la red a JSON para visualización"""
        datos = {
            'nodes': [],
            'links': []
        }
        
        for nodo, attrs in self.grafo.nodes(data=True):
            datos['nodes'].append({
                'id': nodo,
                'categoria': attrs.get('categoria', 'general'),
                'grado': self.grafo.degree(nodo)
            })
        
        for origen, destino, attrs in self.grafo.edges(data=True):
            datos['links'].append({
                'source': origen,
                'target': destino,
                'tipo': attrs.get('tipo', 'desconocido'),
                'peso': attrs.get('peso', 0.5)
            })
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Red exportada a {ruta}")


if __name__ == "__main__":
    # Prueba rápida
    red = RedSemanticaIngredientes()
    red.agregar_nodo("pollo", categoria="proteina")
    red.agregar_nodo("limon", categoria="fruta")
    red.agregar_relacion("pollo", "limon", "complementa", bidireccional=True)
    
    print("=== PRUEBA RED SEMÁNTICA ===")
    print(f"Relaciones de pollo: {red.obtener_relaciones('pollo')}")
    print(f"Similitud pollo-limon: {red.similitud_semantica('pollo', 'limon')}")
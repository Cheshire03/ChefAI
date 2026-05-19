# src/constructor_red.py
from red_semantica import RedSemanticaIngredientes
import pandas as pd
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConstructorRedSemantica:
    """
    Construye la red semántica desde múltiples fuentes
    """
    
    def __init__(self):
        self.red = RedSemanticaIngredientes()
        
        # Categorías base
        self.categorias = {
            'proteinas': ['pollo', 'res', 'cerdo', 'pescado', 'huevo', 'tofu', 'lenteja', 'garbanzo'],
            'vegetales': ['tomate', 'cebolla', 'zanahoria', 'papa', 'lechuga', 'espinaca', 'brocoli'],
            'frutas': ['manzana', 'platano', 'naranja', 'limon', 'fresa', 'aguacate'],
            'lacteos': ['leche', 'queso', 'yogurt', 'crema', 'mantequilla'],
            'granos': ['arroz', 'pasta', 'pan', 'avena', 'quinua', 'maiz'],
            'especias': ['sal', 'pimienta', 'ajo', 'oregano', 'comino', 'albahaca'],
            'grasas': ['aceite', 'aceite oliva', 'mantequilla', 'aceite coco']
        }
    
    def construir_red_completa(self):
        """Construye la red con todas las relaciones"""
        logger.info("Construyendo red semántica...")
        
        self._agregar_categorias()
        self._agregar_sinonimos()
        self._agregar_jerarquias()
        self._agregar_derivados()
        self._agregar_complementos()
        self._agregar_sustitutos()
        
        logger.info(f"Red construida: {self.red.estadisticas['total_nodos']} nodos, "
                    f"{self.red.estadisticas['total_aristas']} aristas")
        
        return self.red
    
    def _agregar_categorias(self):
        """Agrega nodos con sus categorías"""
        for categoria, ingredientes in self.categorias.items():
            for ingrediente in ingredientes:
                self.red.agregar_nodo(ingrediente, categoria=categoria)
    
    def _agregar_sinonimos(self):
        """Agrega relaciones de sinonimia"""
        sinonimos = {
            'tomate': ['jitomate', 'tomate rojo', 'tomate cherry'],
            'pollo': ['pechuga pollo', 'muslo pollo', 'pollo entero', 'pechuga de pollo'],
            'cebolla': ['cebolla blanca', 'cebolla morada', 'cebolla cambray'],
            'chile': ['ají', 'pimiento', 'ají picante'],
            'limon': ['lima', 'limón sutil'],
            'papa': ['patata', 'papas'],
            'calabaza': ['zapallo', 'auyama', 'calabacín'],
            'aguacate': ['palta', 'avocado'],
            'fresa': ['frutilla']
        }
        
        for principal, variantes in sinonimos.items():
            for variante in variantes:
                self.red.agregar_relacion(principal, variante, 'sinonimo', bidireccional=True)
    
    def _agregar_jerarquias(self):
        """Agrega relaciones jerárquicas (tipo_de)"""
        jerarquias = {
            'carne': ['pollo', 'res', 'cerdo', 'cordero'],
            'pescado': ['salmón', 'atún', 'merluza', 'tilapia'],
            'verdura_hoja': ['lechuga', 'espinaca', 'acelga', 'col'],
            'tuberculo': ['papa', 'camote', 'yuca', 'ñame'],
            'lacteo': ['leche', 'queso', 'yogurt', 'crema']
        }
        
        for categoria, miembros in jerarquias.items():
            self.red.agregar_nodo(categoria, categoria='categoria')
            for miembro in miembros:
                self.red.agregar_relacion(miembro, categoria, 'tipo_de')
    
    def _agregar_derivados(self):
        """Agrega relaciones de derivados"""
        derivados = {
            'leche': ['crema', 'yogurt', 'queso', 'mantequilla'],
            'tomate': ['salsa tomate', 'pasta tomate', 'tomate triturado'],
            'cebolla': ['cebolla caramelizada', 'cebolla frita', 'cebolla polvo'],
            'ajo': ['ajo picado', 'ajo polvo', 'pasta ajo'],
            'limon': ['jugo limon', 'ralladura limon'],
            'pollo': ['caldo pollo', 'pollo desmenuzado']
        }
        
        for base, derivados_lista in derivados.items():
            for derivado in derivados_lista:
                self.red.agregar_relacion(derivado, base, 'derivado_de')
    
    def _agregar_complementos(self):
        """Agrega relaciones de complementariedad culinaria"""
        complementos = {
            'pollo': ['ajo', 'limon', 'romero', 'tomillo', 'cebolla'],
            'tomate': ['albahaca', 'oregano', 'ajo', 'cebolla', 'aceite oliva'],
            'pasta': ['queso', 'albahaca', 'tomate', 'ajo'],
            'arroz': ['cebolla', 'ajo', 'zanahoria', 'pollo'],
            'pescado': ['limon', 'eneldo', 'ajo', 'perejil'],
            'huevo': ['cebolla', 'papa', 'queso'],
            'carne': ['cebolla', 'ajo', 'vino', 'romero']
        }
        
        for principal, complementos_lista in complementos.items():
            for complemento in complementos_lista:
                self.red.agregar_relacion(principal, complemento, 'complementa', bidireccional=True)
    
    def _agregar_sustitutos(self):
        """Agrega relaciones de sustitución"""
        sustitutos = {
            'pollo': ['pavo', 'tofu'],
            'carne_res': ['carne cerdo', 'pollo', 'setas'],
            'leche': ['leche almendra', 'leche soya'],
            'mantequilla': ['aceite coco', 'aceite oliva'],
            'queso': ['tofu', 'levadura nutricional'],
            'huevo': ['tofu', 'puré manzana']
        }
        
        for original, alternativas in sustitutos.items():
            for alternativa in alternativas:
                self.red.agregar_relacion(original, alternativa, 'sustituto', bidireccional=True)
    
    def aprender_de_recetas(self, df_recetas: pd.DataFrame, umbral: int = 2):
        """
        Aprende relaciones automáticamente de las recetas
        """
        logger.info("Aprendiendo de recetas existentes...")
        
        co_ocurrencias = Counter()
        
        for _, receta in df_recetas.iterrows():
            ingredientes = receta['ingredientes']
            
            for i in range(len(ingredientes)):
                for j in range(i + 1, len(ingredientes)):
                    par = tuple(sorted([ingredientes[i].lower(), ingredientes[j].lower()]))
                    co_ocurrencias[par] += 1
        
        nuevas = 0
        for (ing1, ing2), frecuencia in co_ocurrencias.items():
            if frecuencia >= umbral:
                peso = min(0.7, 0.3 + (frecuencia / 50))
                self.red.agregar_relacion(ing1, ing2, 'complementa', peso, bidireccional=True)
                nuevas += 1
        
        logger.info(f"Aprendidas {nuevas} nuevas relaciones de co-ocurrencia")


if __name__ == "__main__":
    constructor = ConstructorRedSemantica()
    red = constructor.construir_red_completa()
    red.guardar('modelo/red_semantica.pkl')
    print("Red construida y guardada exitosamente")
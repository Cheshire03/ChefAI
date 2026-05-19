# src/preprocessor.py
import re
import unicodedata
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from typing import List, Union, Dict, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngredientProcessor:
    """
    Procesador de ingredientes con limpieza avanzada y manejo de sinónimos
    """
    
    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        
        # Diccionario de sinónimos manual
        self.sinonimos = {
            'tomate': ['jitomate', 'tomate rojo', 'tomate cherry', 'tomate saladet'],
            'pollo': ['pechuga pollo', 'muslo pollo', 'pollo entero', 'pechuga de pollo'],
            'cebolla': ['cebolla blanca', 'cebolla morada', 'cebolla cambray', 'cebolla de rabo'],
            'chile': ['ají', 'pimiento', 'ají picante', 'chile picante'],
            'limón': ['lima', 'limón sutil', 'limón criollo'],
            'papa': ['patata', 'papas', 'papa criolla', 'papa blanca'],
            'calabaza': ['zapallo', 'auyama', 'calabacín', 'calabacita'],
            'aguacate': ['palta', 'avocado'],
            'fresa': ['frutilla'],
            'piña': ['ananá', 'ananás'],
            'ají_moron': ['pimiento morrón', 'chile morrón', 'pimentón', 'morrón']
        }
        
        # Crear mapeo inverso para normalización
        self.mapeo_sinonimos = {}
        for principal, variantes in self.sinonimos.items():
            for variante in variantes:
                self.mapeo_sinonimos[variante] = principal
            self.mapeo_sinonimos[principal] = principal
    
    def normalizar_acentos(self, texto: str) -> str:
        """Elimina acentos y caracteres especiales"""
        texto = unicodedata.normalize('NFKD', texto)
        texto = texto.encode('ASCII', 'ignore').decode('utf-8')
        return texto
    
    def limpiar_ingrediente(self, ingrediente: str) -> str:
        """
        Limpieza completa de un ingrediente
        """
        if not ingrediente:
            return ""
        
        # Minúsculas y eliminar acentos
        ingrediente = ingrediente.lower()
        ingrediente = self.normalizar_acentos(ingrediente)
        
        # Eliminar cantidades y unidades
        ingrediente = re.sub(r'\d+', '', ingrediente)
        ingrediente = re.sub(r'\b(kg|g|ml|l|taza|cucharada|cda|cdita|unidad|unidades|kilo|medio|cuarto)\b', '', ingrediente)
        
        # Eliminar puntuación
        ingrediente = re.sub(r'[^\w\s]', '', ingrediente)
        
        # Eliminar palabras comunes (stopwords)
        palabras = ingrediente.split()
        palabras = [p for p in palabras if p not in self.stop_words and len(p) > 1]
        
        # Eliminar plurales simples en español ('s' o 'es' al final)
        palabras = [re.sub(r'(es|s)$', '', p) if len(p) > 3 else p for p in palabras]
        
        # Unir de vuelta
        resultado = ' '.join(palabras) if palabras else ""
        
        # Aplicar mapeo de sinónimos si existe
        if resultado in self.mapeo_sinonimos:
            resultado = self.mapeo_sinonimos[resultado]
        
        return resultado
    
    def procesar_receta(self, ingredientes: List[str]) -> str:
        """
        Procesa una lista completa de ingredientes
        Devuelve string limpio para TF-IDF
        """
        if not ingredientes:
            return ""
        
        procesados = []
        for ing in ingredientes:
            limpio = self.limpiar_ingrediente(ing)
            if limpio and len(limpio) > 1:  # Si no quedó vacío
                procesados.append(limpio)
        
        return ' '.join(procesados)
    
    def procesar_usuario(self, ingredientes: Union[str, List[str]]) -> str:
        """
        Procesa entrada del usuario (puede ser string o lista)
        """
        if isinstance(ingredientes, str):
            # Dividir por comas o "y"
            ingredientes = re.split(r',|\s+y\s+', ingredientes)
            ingredientes = [i.strip() for i in ingredientes if i.strip()]
        
        return self.procesar_receta(ingredientes)
    
    def normalizar_lista(self, ingredientes: List[str]) -> Set[str]:
        """
        Normaliza una lista de ingredientes y devuelve un set
        """
        normalizados = set()
        for ing in ingredientes:
            norm = self.limpiar_ingrediente(ing)
            if norm:
                normalizados.add(norm)
        return normalizados


# Prueba rápida
if __name__ == "__main__":
    processor = IngredientProcessor()
    
    # Pruebas
    tests = [
        "2 cebollas grandes moradas",
        "pechuga de pollo",
        "jitomate",
        "1/2 taza de leche"
    ]
    
    print("=== PRUEBAS DE PREPROCESADOR ===")
    for test in tests:
        resultado = processor.limpiar_ingrediente(test)
        print(f"'{test}' -> '{resultado}'")
    
    receta = ["pollo", "sal", "pimienta", "aceite de oliva"]
    resultado = processor.procesar_receta(receta)
    print(f"\nReceta procesada: {resultado}")
"""
generar_recetas.py
------------------
Genera recetas nuevas con Gemini y las fusiona con data/recetas.json existente.
Luego re-entrena el modelo automáticamente.

Uso:
    python generar_recetas.py              # genera 300 recetas (default)
    python generar_recetas.py --total 500  # genera 500 recetas
    python generar_recetas.py --solo-generar  # genera sin re-entrenar
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path

# Agregar src al path para el trainer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from google import genai

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =========================================================
# CONFIGURACIÓN
# =========================================================
RUTA_RECETAS_ORIGINAL = 'data/recetas.json'
RUTA_RECETAS_BACKUP   = 'data/recetas_backup.json'
RUTA_RECETAS_NUEVAS   = 'data/recetas_generadas.json'
RUTA_RECETAS_FINAL    = 'data/recetas.json'

RECETAS_POR_LOTE = 10   # Gemini genera N recetas por llamada (no subir de 15)
PAUSA_ENTRE_LOTES = 3   # segundos entre llamadas para no saturar la API

# =========================================================
# CATEGORÍAS DE RECETAS A GENERAR
# Ajusta estas listas según tu región y público objetivo
# =========================================================
CATEGORIAS = [
    # (nombre_categoria, ingredientes_base_sugeridos)
    ("desayunos con huevo",       ["huevo", "tomate", "cebolla", "chile", "queso", "jamón", "cilantro"]),
    ("tacos y antojitos",         ["tortilla", "pollo", "carne", "frijoles", "aguacate", "salsa", "limón"]),
    ("sopas y caldos",            ["pollo", "zanahoria", "papa", "cebolla", "ajo", "cilantro", "sal"]),
    ("arroz y guisos",            ["arroz", "pollo", "tomate", "cebolla", "ajo", "chile", "caldo"]),
    ("ensaladas frescas",         ["lechuga", "tomate", "pepino", "limón", "aceite de oliva", "aguacate"]),
    ("pasta y fideos",            ["pasta", "tomate", "ajo", "cebolla", "queso", "crema", "albahaca"]),
    ("recetas con frijoles",      ["frijoles", "chile", "cebolla", "ajo", "epazote", "queso", "tortilla"]),
    ("pescado y mariscos",        ["pescado", "limón", "ajo", "cebolla", "chile", "cilantro", "tomate"]),
    ("recetas vegetarianas",      ["calabaza", "elote", "espinaca", "zanahoria", "papa", "tomate", "queso"]),
    ("carnes a la plancha",       ["carne", "ajo", "limón", "sal", "pimienta", "cebolla", "chile"]),
    ("salsas y aderezos",         ["chile", "tomate", "ajo", "cebolla", "cilantro", "limón", "sal"]),
    ("postres simples",           ["harina", "azúcar", "huevo", "mantequilla", "leche", "vainilla", "canela"]),
    ("bebidas y aguas frescas",   ["jamaica", "limón", "azúcar", "agua", "canela", "jengibre", "menta"]),
    ("recetas con pollo",         ["pollo", "ajo", "cebolla", "tomate", "chile", "crema", "queso"]),
    ("recetas rápidas 15 min",    ["huevo", "atún", "queso", "tortilla", "jitomate", "aguacate", "limón"]),
]

CONDICIONES_MEDICAS = [
    "diabetes",
    "hipertension",
    "celiaquia",
    "colesterol_alto",
    "resistencia_insulina",
    "ninguna",
    "ninguna",
    "ninguna",  # "ninguna" repetida para que sea más frecuente
]

TAGS_NUTRICIONALES = [
    "alto_proteina", "bajo_sodio", "sin_gluten", "alto_fibra",
    "bajo_calorias", "vegetariano", "vegano", "bajo_grasa",
    "rico_omega3", "antioxidante"
]

ALERGIAS = ["gluten", "lactosa", "mariscos", "nueces", "soya", "huevo"]


# =========================================================
# PROMPT PARA GEMINI
# =========================================================
def construir_prompt(categoria: str, ingredientes_sugeridos: list, n: int, id_inicio: int) -> str:
    ingredientes_str = ", ".join(ingredientes_sugeridos)
    
    return f"""Eres un experto en gastronomía mexicana y latinoamericana. 
Genera exactamente {n} recetas de la categoría: "{categoria}".

REGLAS ESTRICTAS:
1. Responde ÚNICAMENTE con un array JSON válido. Sin texto antes ni después.
2. Sin bloques de código (no uses ```json). Solo el array puro.
3. Cada receta debe tener ingredientes REALES y preparación DETALLADA (mínimo 3 pasos).
4. Los ingredientes deben ser palabras simples en singular (ej: "pollo", "tomate", no "pechugas de pollo").
5. Las cantidades deben ser específicas (ej: "2 tazas de arroz", "3 tomates medianos").
6. La preparación debe ser útil y real, no genérica.
7. Varía las recetas — no repitas el mismo platillo con variante numérica.
8. Los IDs empiezan en {id_inicio}.

Ingredientes sugeridos (úsalos como base pero puedes agregar otros): {ingredientes_str}

Condiciones médicas disponibles para apto_para_condiciones: 
["diabetes", "hipertension", "celiaquia", "colesterol_alto", "resistencia_insulina"]

Alergias disponibles para alergias_comunes:
["gluten", "lactosa", "mariscos", "nueces", "soya", "huevo"]

Tags nutricionales disponibles:
["alto_proteina", "bajo_sodio", "sin_gluten", "alto_fibra", "bajo_calorias", 
 "vegetariano", "vegano", "bajo_grasa", "rico_omega3", "antioxidante"]

Formato EXACTO de cada receta (respeta todos los campos):
{{
  "id": {id_inicio},
  "nombre": "Nombre descriptivo y apetitoso",
  "ingredientes": ["ingrediente1", "ingrediente2", "ingrediente3"],
  "cantidades": ["cantidad y unidad de ingrediente1", "cantidad de ingrediente2"],
  "preparacion": "Paso 1: descripción. Paso 2: descripción. Paso 3: descripción. Sirve caliente.",
  "tiempo": "25 min",
  "dificultad": "fácil",
  "metadata_salud": {{
    "apto_para_condiciones": [],
    "alergias_comunes": [],
    "tags_nutricionales": ["tag1"]
  }}
}}

Genera las {n} recetas ahora:"""


# =========================================================
# GENERADOR PRINCIPAL
# =========================================================
class GeneradorRecetas:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.recetas_generadas = []
    
    def generar_lote(self, categoria: str, ingredientes: list, 
                     n: int, id_inicio: int) -> list:
        """Llama a Gemini y parsea el resultado"""
        prompt = construir_prompt(categoria, ingredientes, n, id_inicio)
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            texto = response.text.strip()
            
            # Limpiar posibles bloques de código que Gemini a veces agrega
            if texto.startswith("```"):
                texto = texto.split("```")[1]
                if texto.startswith("json"):
                    texto = texto[4:]
            if texto.endswith("```"):
                texto = texto[:-3]
            texto = texto.strip()
            
            recetas = json.loads(texto)
            
            # Validar que sea una lista
            if not isinstance(recetas, list):
                logger.warning(f"Gemini no devolvió una lista para '{categoria}'")
                return []
            
            # Validar campos mínimos por receta
            validas = []
            for r in recetas:
                if all(k in r for k in ['id', 'nombre', 'ingredientes', 'preparacion']):
                    # Asegurar metadata_salud existe
                    if 'metadata_salud' not in r:
                        r['metadata_salud'] = {
                            'apto_para_condiciones': [],
                            'alergias_comunes': [],
                            'tags_nutricionales': []
                        }
                    # Asegurar campos opcionales
                    r.setdefault('cantidades', [f"1 porción de {ing}" for ing in r['ingredientes']])
                    r.setdefault('tiempo', '30 min')
                    r.setdefault('dificultad', 'media')
                    validas.append(r)
                else:
                    logger.warning(f"Receta inválida descartada: {r.get('nombre', 'sin nombre')}")
            
            logger.info(f"  ✅ '{categoria}': {len(validas)}/{n} recetas válidas")
            return validas
            
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ Error JSON en '{categoria}': {e}")
            logger.debug(f"  Respuesta raw: {texto[:300]}...")
            return []
        except Exception as e:
            logger.error(f"  ❌ Error Gemini en '{categoria}': {e}")
            return []
    
    def generar_dataset(self, total_objetivo: int) -> list:
        """Genera recetas distribuidas entre todas las categorías"""
        recetas_por_categoria = max(1, total_objetivo // len(CATEGORIAS))
        lotes_por_categoria = max(1, recetas_por_categoria // RECETAS_POR_LOTE)
        
        logger.info(f"🎯 Objetivo: {total_objetivo} recetas")
        logger.info(f"📂 Categorías: {len(CATEGORIAS)}")
        logger.info(f"📦 ~{recetas_por_categoria} recetas por categoría")
        
        id_actual = 1000  # Empezar desde 1000 para no chocar con IDs existentes
        
        for categoria, ingredientes in CATEGORIAS:
            logger.info(f"\n🍳 Generando: {categoria}")
            
            for lote in range(lotes_por_categoria):
                logger.info(f"  Lote {lote + 1}/{lotes_por_categoria} (ID inicio: {id_actual})")
                
                nuevas = self.generar_lote(
                    categoria=categoria,
                    ingredientes=ingredientes,
                    n=RECETAS_POR_LOTE,
                    id_inicio=id_actual
                )
                
                # Re-asignar IDs secuenciales para evitar duplicados
                for i, receta in enumerate(nuevas):
                    receta['id'] = id_actual + i
                
                self.recetas_generadas.extend(nuevas)
                id_actual += len(nuevas) + 1
                
                if len(self.recetas_generadas) >= total_objetivo:
                    break
                
                # Pausa para no saturar la API
                if lote < lotes_por_categoria - 1:
                    time.sleep(PAUSA_ENTRE_LOTES)
            
            if len(self.recetas_generadas) >= total_objetivo:
                break
        
        logger.info(f"\n✅ Total generadas: {len(self.recetas_generadas)} recetas")
        return self.recetas_generadas


# =========================================================
# FUSIÓN CON DATASET EXISTENTE
# =========================================================
def fusionar_datasets(ruta_original: str, recetas_nuevas: list) -> list:
    """Combina el dataset original con las recetas nuevas"""
    
    # Cargar original
    with open(ruta_original, 'r', encoding='utf-8') as f:
        recetas_originales = json.load(f)
    logger.info(f"📖 Dataset original: {len(recetas_originales)} recetas")
    
    # Detectar nombres duplicados (por si Gemini generó algo que ya existe)
    nombres_existentes = {r['nombre'].lower() for r in recetas_originales}
    nuevas_sin_duplicados = []
    duplicados = 0
    
    for r in recetas_nuevas:
        if r['nombre'].lower() not in nombres_existentes:
            nuevas_sin_duplicados.append(r)
            nombres_existentes.add(r['nombre'].lower())
        else:
            duplicados += 1
    
    if duplicados:
        logger.info(f"⚠️  {duplicados} recetas duplicadas descartadas")
    
    # Fusionar y re-asignar IDs secuenciales para evitar duplicados
    dataset_final = recetas_originales + nuevas_sin_duplicados
    for i, receta in enumerate(dataset_final, start=1):
        receta['id'] = i
    logger.info(f"🔗 Dataset final: {len(dataset_final)} recetas (IDs 1→{len(dataset_final)})")

    return dataset_final


# =========================================================
# MAIN
# =========================================================
def main():
    parser = argparse.ArgumentParser(description='Generador de recetas con Gemini')
    parser.add_argument('--total', type=int, default=300,
                        help='Número de recetas a generar (default: 300)')
    parser.add_argument('--solo-generar', action='store_true',
                        help='Solo genera recetas sin re-entrenar el modelo')
    args = parser.parse_args()
    
    # Validar API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui_no_compartir":
        logger.error("❌ GEMINI_API_KEY no configurada en .env")
        sys.exit(1)
    
    # Validar que existe el dataset original
    if not os.path.exists(RUTA_RECETAS_ORIGINAL):
        logger.error(f"❌ No se encontró {RUTA_RECETAS_ORIGINAL}")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🤖 GENERADOR DE RECETAS — ChefAI")
    print("="*50)
    print(f"📦 Recetas a generar: {args.total}")
    print(f"📂 Dataset original: {RUTA_RECETAS_ORIGINAL}")
    print("="*50 + "\n")
    
    # 1. Backup del dataset original
    import shutil
    shutil.copy(RUTA_RECETAS_ORIGINAL, RUTA_RECETAS_BACKUP)
    logger.info(f"💾 Backup guardado en {RUTA_RECETAS_BACKUP}")
    
    # 2. Generar recetas
    generador = GeneradorRecetas(api_key)
    recetas_nuevas = generador.generar_dataset(args.total)
    
    if not recetas_nuevas:
        logger.error("❌ No se generaron recetas. Revisa tu API key y conexión.")
        sys.exit(1)
    
    # 3. Guardar recetas nuevas por separado (por si quieres revisarlas)
    with open(RUTA_RECETAS_NUEVAS, 'w', encoding='utf-8') as f:
        json.dump(recetas_nuevas, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Recetas nuevas guardadas en {RUTA_RECETAS_NUEVAS}")
    
    # 4. Fusionar con dataset original
    dataset_final = fusionar_datasets(RUTA_RECETAS_ORIGINAL, recetas_nuevas)
    
    # 5. Guardar dataset fusionado
    with open(RUTA_RECETAS_FINAL, 'w', encoding='utf-8') as f:
        json.dump(dataset_final, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Dataset final guardado en {RUTA_RECETAS_FINAL} ({len(dataset_final)} recetas)")
    
    # 6. Re-entrenar el modelo completo (TF-IDF + red semántica)
    if not args.solo_generar:
        print("\n" + "="*50)
        print("🧠 RE-ENTRENANDO MODELO COMPLETO...")
        print("   (TF-IDF + Red Semántica)")
        print("="*50)
        try:
            import subprocess
            resultado = subprocess.run(
                [sys.executable, 'train_completo.py'],
                check=True
            )
            print("\n✅ Entrenamiento completo exitoso.")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error al re-entrenar: {e}")
            logger.info("💡 Puedes re-entrenar manualmente con: python train_completo.py")
    else:
        print("\n💡 Modelo NO re-entrenado (--solo-generar activo)")
        print("   Para re-entrenar: python train_completo.py")
    
    print("\n🎉 ¡Proceso completado!")
    print(f"   Dataset: {RUTA_RECETAS_FINAL}")
    print(f"   Backup original: {RUTA_RECETAS_BACKUP}")
    print(f"   Solo nuevas: {RUTA_RECETAS_NUEVAS}")


if __name__ == '__main__':
    main()
# train_completo.py
import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from src.trainer import ChefAI_Trainer
from src.constructor_red import ConstructorRedSemantica
from src.recomendador_semantico import RecomendadorSemantico

def main():
    print("🚀 CHEFAI - ENTRENAMIENTO COMPLETO")
    print("="*50)
    
    # 1. Entrenar modelo base
    print("\n📊 PASO 1: Entrenando modelo base...")
    trainer = ChefAI_Trainer()
    trainer.entrenar_completo(
        ruta_json='data/recetas.json',
        ruta_salida='modelo/chefai_brain.pkl'
    )
    
    # 2. Construir red semántica
    print("\n🔗 PASO 2: Construyendo red semántica...")
    constructor = ConstructorRedSemantica()
    red_semantica = constructor.construir_red_completa()
    
    # 3. Aprender relaciones de recetas
    df_recetas = pd.read_json('data/recetas.json')
    constructor.aprender_de_recetas(df_recetas)
    
    # 4. Guardar red
    os.makedirs('modelo', exist_ok=True)
    red_semantica.guardar('modelo/red_semantica.pkl')
    red_semantica.exportar_json('modelo/red_semantica.json')
    
    # 5. Probar recomendador semántico
    print("\n🧪 PASO 3: Probando recomendador semántico...")
    recomendador = RecomendadorSemantico(
        ruta_modelo='modelo/chefai_brain.pkl',
        ruta_red='modelo/red_semantica.pkl'
    )
    
    # Casos de prueba
    casos = [
        ["pollo", "arroz", "cebolla"],
        ["jitomate", "ajo", "cebolla"],
        ["huevo", "papa", "cebolla"]
    ]
    
    for i, ingredientes in enumerate(casos, 1):
        print(f"\n--- Caso {i}: {ingredientes} ---")
        
        resultados = recomendador.recomendar_con_semantica(ingredientes, top_n=3)
        
        for j, rec in enumerate(resultados, 1):
            print(f"\n  {j}. {rec['nombre']}")
            print(f"     Similitud: {rec['similitud']:.2%}")
            print(f"     Faltantes: {rec['ingredientes_faltantes'][:3]}")
    
    print("\n" + "="*50)
    print("✅ ENTRENAMIENTO COMPLETADO CON ÉXITO")
    print("\n📁 Archivos generados:")
    print("   - modelo/chefai_brain.pkl")
    print("   - modelo/red_semantica.pkl")
    print("   - modelo/red_semantica.json")
    print("   - modelo/metadata.json")

if __name__ == "__main__":
    main()
# tests/test_modelo.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recomendador_semantico import RecomendadorSemantico
import time

def test_recomendaciones():
    """Prueba el sistema de recomendaciones"""
    
    print("🧪 CHEFAI - PRUEBAS DEL SISTEMA")
    print("="*50)
    
    try:
        recomendador = RecomendadorSemantico()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Primero ejecuta 'python train_completo.py' para entrenar el modelo")
        return
    
    casos_prueba = [
        {
            'nombre': 'Ingredientes básicos',
            'ingredientes': ['pollo', 'arroz', 'cebolla'],
            'top_n': 3
        },
        {
            'nombre': 'Sinónimo (jitomate = tomate)',
            'ingredientes': ['jitomate', 'cebolla', 'ajo'],
            'top_n': 3
        },
        {
            'nombre': 'Pocos ingredientes',
            'ingredientes': ['huevo', 'papa'],
            'top_n': 3
        }
    ]
    
    for caso in casos_prueba:
        print(f"\n{'='*40}")
        print(f"📝 Caso: {caso['nombre']}")
        print(f"   Ingredientes: {caso['ingredientes']}")
        print('='*40)
        
        start_time = time.time()
        
        resultados = recomendador.recomendar_con_semantica(
            caso['ingredientes'],
            top_n=caso.get('top_n', 3)
        )
        
        elapsed = (time.time() - start_time) * 1000
        print(f"⏱️  Tiempo respuesta: {elapsed:.2f} ms")
        
        if not resultados:
            print("   ❌ No se encontraron recomendaciones")
            continue
        
        for i, rec in enumerate(resultados, 1):
            print(f"\n   {i}. {rec['nombre']}")
            print(f"      Coincidencia: {rec['coincidencia']}")
            print(f"      Faltantes: {', '.join(rec['ingredientes_faltantes'][:3])}")
    
    print("\n" + "="*50)
    print("✅ PRUEBAS COMPLETADAS")


def test_complementos():
    """Prueba sugerencias de complementos"""
    print("\n🧪 PRUEBA DE COMPLEMENTOS")
    print("="*50)
    
    try:
        recomendador = RecomendadorSemantico()
    except FileNotFoundError:
        return
    
    ingredientes = ["pollo"]
    complementos = recomendador.sugerir_complementos(ingredientes, top_n=5)
    
    print(f"📝 Ingrediente base: {ingredientes}")
    print(f"💡 Complementos sugeridos:")
    for comp in complementos:
        print(f"   → {comp['ingrediente']} (peso: {comp['peso']:.2f})")


if __name__ == "__main__":
    test_recomendaciones()
    test_complementos()

import sys
import os
import json
import logging
import re
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from recomendador_semantico import RecomendadorSemantico
from google import genai
from database import (
    init_db,
    get_all_perfiles, get_perfil, create_perfil, update_perfil, delete_perfil,
    add_like, remove_like, get_likes, is_liked, get_liked_ingredientes
)

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key or gemini_api_key == "tu_api_key_aqui_no_compartir":
    print("⚠️ ADVERTENCIA: GEMINI_API_KEY no configurada correctamente en .env")

init_db()

print("🔄 Cargando Motor Local...")
try:
    recomendador = RecomendadorSemantico(
        ruta_modelo='modelo/chefai_brain.pkl',
        ruta_red='modelo/red_semantica.pkl'
    )
    print("✅ Motor Local cargado correctamente")
except Exception as e:
    print(f"⚠️ Error al cargar modelo local: {e}")
    recomendador = None


# ─────────────────────────────────────────────
# INGREDIENTES
# ─────────────────────────────────────────────

STOP_WORDS_COCINA = {
    "tengo", "tenemos", "tiene", "hay", "cuento", "dispongo",
    "quiero", "quería", "quisiera", "me", "gustaría",
    "hacer", "cocinar", "preparar", "algo", "receta",
    "con", "de", "y", "o", "también", "además",
    "un", "una", "unos", "unas", "el", "la", "los", "las",
    "mi", "mis", "hola", "buenas", "oye", "ayuda",
    "por", "favor", "puedes", "podrías", "sugerirme",
    "recomendarme", "que", "para", "qué", "como", "puedo"
}

INGREDIENTES_ANCLA = {
    "pollo", "res", "cerdo", "carne", "pescado", "camarón", "atún",
    "huevo", "tofu", "lenteja", "garbanzo",
    "pasta", "arroz", "fideo", "tortilla", "pan", "masa", "quinoa",
    "nopal", "calabaza", "espinaca", "elote", "brócoli", "frijol",
}

INGREDIENTES_ESENCIALES = {
    'proteinas': ['pollo', 'res', 'cerdo', 'carne', 'pescado', 'huevo', 'tofu', 'lenteja', 'garbanzo'],
    'base': ['arroz', 'pasta', 'pan', 'tortilla', 'masa'],
    'grasa': ['aceite', 'mantequilla', 'manteca']
}


def extraer_ingredientes(mensaje: str) -> List[str]:
    mensaje = mensaje.lower()
    mensaje = re.sub(r'[¿?¡!.]', '', mensaje)
    partes = re.split(r',', mensaje)
    tokens = []
    for parte in partes:
        sub = re.split(r'\s+y\s+|\s+o\s+', parte)
        tokens.extend(sub)
    ingredientes = []
    for token in tokens:
        palabras = token.strip().split()
        palabras_limpias = [p for p in palabras if p not in STOP_WORDS_COCINA]
        if palabras_limpias:
            ingrediente = ' '.join(palabras_limpias).strip()
            if ingrediente.endswith('s') and not ingrediente.endswith('es'):
                ingrediente = ingrediente[:-1]
            if ingrediente:
                ingredientes.append(ingrediente)
    vistos = set()
    sin_duplicados = []
    for ing in ingredientes:
        if ing not in vistos:
            vistos.add(ing)
            sin_duplicados.append(ing)
    resultado = []
    for ing in sin_duplicados:
        if any(ancla in ing for ancla in INGREDIENTES_ANCLA):
            resultado.extend([ing, ing, ing])
        else:
            resultado.append(ing)
    return resultado if resultado else []


def calcular_cobertura_real(ingredientes_usuario: List[str],
                            ingredientes_receta: List[str]) -> Dict:
    from src.preprocessor import IngredientProcessor
    processor = IngredientProcessor()
    usuario_norm = processor.normalizar_lista(ingredientes_usuario)
    receta_norm = processor.normalizar_lista(ingredientes_receta)
    coincidentes = usuario_norm & receta_norm
    cobertura = len(coincidentes) / len(receta_norm) if receta_norm else 0
    esenciales_faltantes = []
    for categoria, esenciales in INGREDIENTES_ESENCIALES.items():
        for esencial in esenciales:
            if esencial in receta_norm and esencial not in usuario_norm:
                esenciales_faltantes.append(esencial)
                break
    return {
        'cobertura': cobertura,
        'coincidentes': list(coincidentes),
        'faltantes': list(receta_norm - usuario_norm),
        'esenciales_faltantes': esenciales_faltantes,
        'total_receta': len(receta_norm)
    }


# ─────────────────────────────────────────────
# ENDPOINTS — INFO
# ─────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    return jsonify({'nombre': 'ChefAI', 'version': 'v0.4', 'status': 'online'})


# ─────────────────────────────────────────────
# ENDPOINTS — PERFILES
# ─────────────────────────────────────────────

@app.route('/api/perfiles', methods=['GET'])
def listar_perfiles():
    return jsonify(get_all_perfiles()), 200


@app.route('/api/perfiles', methods=['POST'])
def crear_perfil():
    data = request.get_json()
    if not data or not data.get('nombre'):
        return jsonify({'error': 'El campo nombre es obligatorio'}), 400
    perfil_id = create_perfil(
        nombre=data['nombre'].strip(),
        condiciones=data.get('condiciones', ''),
        alergias=data.get('alergias', []),
        cocina=data.get('cocina', ''),
        tiempo_max=data.get('tiempo_max', ''),
        dificultad=data.get('dificultad', '')
    )
    return jsonify(get_perfil(perfil_id)), 201


@app.route('/api/perfiles/<int:perfil_id>', methods=['GET'])
def obtener_perfil(perfil_id):
    perfil = get_perfil(perfil_id)
    if not perfil:
        return jsonify({'error': 'Perfil no encontrado'}), 404
    return jsonify(perfil), 200


@app.route('/api/perfiles/<int:perfil_id>', methods=['PUT'])
def editar_perfil(perfil_id):
    data = request.get_json()
    if not data or not data.get('nombre'):
        return jsonify({'error': 'El campo nombre es obligatorio'}), 400
    if not get_perfil(perfil_id):
        return jsonify({'error': 'Perfil no encontrado'}), 404
    update_perfil(
        perfil_id=perfil_id,
        nombre=data['nombre'].strip(),
        condiciones=data.get('condiciones', ''),
        alergias=data.get('alergias', []),
        cocina=data.get('cocina', ''),
        tiempo_max=data.get('tiempo_max', ''),
        dificultad=data.get('dificultad', '')
    )
    return jsonify(get_perfil(perfil_id)), 200


@app.route('/api/perfiles/<int:perfil_id>', methods=['DELETE'])
def eliminar_perfil(perfil_id):
    if not get_perfil(perfil_id):
        return jsonify({'error': 'Perfil no encontrado'}), 404
    delete_perfil(perfil_id)
    return jsonify({'ok': True}), 200


# ─────────────────────────────────────────────
# ENDPOINTS — LIKES
# ─────────────────────────────────────────────

@app.route('/api/perfiles/<int:perfil_id>/likes', methods=['GET'])
def ver_likes(perfil_id):
    if not get_perfil(perfil_id):
        return jsonify({'error': 'Perfil no encontrado'}), 404
    return jsonify(get_likes(perfil_id)), 200


@app.route('/api/perfiles/<int:perfil_id>/likes', methods=['POST'])
def dar_like(perfil_id):
    data = request.get_json()
    if not data or not data.get('receta_id'):
        return jsonify({'error': 'receta_id es obligatorio'}), 400
    if not get_perfil(perfil_id):
        return jsonify({'error': 'Perfil no encontrado'}), 404
    add_like(
        perfil_id=perfil_id,
        receta_id=int(data['receta_id']),
        nombre=data.get('nombre', ''),
        ingredientes=data.get('ingredientes', [])
    )
    return jsonify({'ok': True, 'liked': True}), 200


@app.route('/api/perfiles/<int:perfil_id>/likes/<int:receta_id>', methods=['DELETE'])
def quitar_like(perfil_id, receta_id):
    if not get_perfil(perfil_id):
        return jsonify({'error': 'Perfil no encontrado'}), 404
    remove_like(perfil_id, receta_id)
    return jsonify({'ok': True, 'liked': False}), 200


# ─────────────────────────────────────────────
# ENDPOINT — CHAT
# ─────────────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
def chat():
    global recomendador
    if recomendador is None:
        return jsonify({'error': 'Motor local no disponible'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON inválido o vacío'}), 400

        mensaje = data.get('mensaje', '').strip()
        condicion = data.get('condicion', '').strip()
        perfil_id = data.get('perfil_id')

        if not mensaje:
            return jsonify({'error': 'El campo "mensaje" es obligatorio'}), 400

        # Cargar perfil si viene uno
        perfil = None
        likes_ingredientes = []
        alergias_perfil = []
        if perfil_id:
            perfil = get_perfil(int(perfil_id))
            if perfil:
                if not condicion:
                    condicion = perfil.get('condiciones', '')
                alergias_perfil = perfil.get('alergias', [])
                likes_ingredientes = get_liked_ingredientes(int(perfil_id))

        ingredientes_usuario = extraer_ingredientes(mensaje)
        print(f"🥦 Ingredientes: {ingredientes_usuario}")

        if not ingredientes_usuario:
            return jsonify({
                'respuesta': '¡Hola! Dime qué ingredientes tienes. Por ejemplo: "tengo pollo, arroz y cebolla".'
            }), 200

        resultados_crudos = recomendador.recomendar_con_semantica(
            ingredientes_usuario, top_n=20, usar_semantica=True
        )

        if not resultados_crudos:
            return jsonify({
                'respuesta': f'No encontré recetas con {", ".join(set(ingredientes_usuario[:3]))}.'
            }), 200

        # Filtro ancla
        anclas_usuario = list({
            ing for ing in ingredientes_usuario
            if any(ancla in ing for ancla in INGREDIENTES_ANCLA)
        })
        if anclas_usuario:
            filtrados = []
            for r in resultados_crudos:
                receta_df = recomendador.df[recomendador.df['id'] == r['id']]
                if receta_df.empty:
                    continue
                ings_r = [i.lower() for i in receta_df.iloc[0].get('ingredientes', [])]
                if any(any(a in ir for ir in ings_r) for a in anclas_usuario):
                    filtrados.append(r)
            if filtrados:
                resultados_crudos = filtrados

        # Cobertura real
        recetas_con_cobertura = []
        for receta_cruda in resultados_crudos:
            receta_df = recomendador.df[recomendador.df['id'] == receta_cruda['id']]
            if receta_df.empty:
                continue
            receta = receta_df.iloc[0].to_dict()
            cobertura_info = calcular_cobertura_real(
                ingredientes_usuario, receta.get('ingredientes', [])
            )
            if cobertura_info['cobertura'] >= 0.4:
                receta['cobertura_info'] = cobertura_info
                receta['similitud_semantica'] = receta_cruda.get('similitud', 0)
                recetas_con_cobertura.append(receta)

        if not recetas_con_cobertura:
            return jsonify({
                'respuesta': f'Con esos ingredientes no encontré coincidencia suficiente. ¿Tienes aceite, cebolla o ajo también?'
            }), 200

        # Filtro seguridad (alergias perfil + condiciones)
        recetas_seguras = []
        for receta in recetas_con_cobertura:
            metadata = receta.get('metadata_salud', {})
            es_segura = True
            alergias_receta = [a.lower() for a in metadata.get('alergias_comunes', [])]

            for alergia in alergias_perfil:
                if alergia.lower() in alergias_receta:
                    es_segura = False
                    break

            if es_segura and condicion:
                condicion_str = condicion.lower()
                for alergia in alergias_receta:
                    if alergia in condicion_str:
                        es_segura = False
                        break
                if es_segura:
                    apto_para = [c.lower() for c in metadata.get('apto_para_condiciones', [])]
                    for cond in ["diabetes", "hipertension", "resistencia_insulina"]:
                        if cond in condicion_str and cond not in apto_para:
                            es_segura = False
                            break

            if es_segura:
                recetas_seguras.append(receta)

        if not recetas_seguras:
            return jsonify({
                'respuesta': 'Tengo recetas con esos ingredientes, pero ninguna es segura para tu perfil de salud.'
            }), 200

        # Scoring con boost de likes
        for receta in recetas_seguras:
            cobertura = receta['cobertura_info']['cobertura']
            similitud = receta.get('similitud_semantica', 0)
            boost_likes = 0
            if likes_ingredientes:
                ings_r = set(receta.get('ingredientes', []))
                coincidencias = len(ings_r & set(likes_ingredientes))
                boost_likes = min(coincidencias * 0.05, 0.2)
            receta['puntaje_final'] = (cobertura * 0.75) + (similitud * 0.15) + (boost_likes * 0.10)

        recetas_seguras.sort(key=lambda r: r['puntaje_final'], reverse=True)
        mejor = recetas_seguras[0]

        cobertura_info = mejor['cobertura_info']
        ingredientes_receta = mejor.get('ingredientes', [])
        faltantes = cobertura_info['faltantes']
        cobertura_pct = int(cobertura_info['cobertura'] * 100)
        es_buena = cobertura_info['cobertura'] >= 0.7
        es_perfecta = cobertura_info['cobertura'] == 1.0

        # Gemini
        try:
            if not gemini_api_key or gemini_api_key == "tu_api_key_aqui_no_compartir":
                raise ValueError("Sin API key")

            nombre_perfil = perfil['nombre'] if perfil else None
            prompt = f"""Eres Mindy, chef personal con IA, empática y entusiasta.

Ingredientes del usuario: {', '.join(set(ingredientes_usuario))}
Condición médica/dieta: {condicion if condicion else 'Ninguna'}
{'Perfil: ' + nombre_perfil if nombre_perfil else ''}

Receta: {mejor['nombre']}
Coincidencia: {cobertura_pct}%
Tiempo: {mejor.get('tiempo', 'No especificado')} | Dificultad: {mejor.get('dificultad', 'media')}
Ingredientes completos: {', '.join(ingredientes_receta)}
Preparación: {mejor.get('preparacion', '')}

Ya tiene: {', '.join(cobertura_info['coincidentes'])}
Le falta: {', '.join(faltantes) if faltantes else 'nada'}

INSTRUCCIONES:
1. {'Llama a ' + nombre_perfil + ' por su nombre.' if nombre_perfil else 'Saluda cordialmente.'}
2. Sé honesta sobre lo que falta. Sugiere sustitutos si puedes.
3. Usa emojis y párrafos cortos. Máximo 200 palabras.
4. Al final menciona brevemente que puede dar ❤️ si le gusta la receta."""

            client = genai.Client(api_key=gemini_api_key)
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            respuesta_final = response.text

        except Exception as e:
            print(f"⚠️ Fallback: {e}")
            if es_perfecta:
                intro = f"🎉 ¡Tienes todo para hacer **{mejor['nombre']}**!"
            elif es_buena:
                intro = f"👍 Con lo que tienes puedes hacer **{mejor['nombre']}**"
            else:
                intro = f"🍳 Podrías preparar **{mejor['nombre']}** (te falta {', '.join(faltantes[:2])})"

            respuesta_final = (
                f"{intro}\n\n"
                f"**Ya tienes:** {', '.join(cobertura_info['coincidentes'])}\n\n"
                f"**Preparación:** {mejor.get('preparacion', '')[:400]}\n\n"
                + (f"**⚠️ Te faltaría:** {', '.join(faltantes)}" if faltantes else "✅ ¡No necesitas comprar nada!")
                + "\n\n❤️ ¿Te gustó? Dale like para recomendaciones personalizadas."
            )

        ya_tiene_like = False
        if perfil_id:
            ya_tiene_like = is_liked(int(perfil_id), int(mejor['id']))

        return jsonify({
            'respuesta': respuesta_final,
            'receta_id': int(mejor['id']),
            'receta_nombre': mejor['nombre'],
            'receta_ingredientes': ingredientes_receta,
            'ingredientes_detectados': list(set(ingredientes_usuario)),
            'cobertura': f"{cobertura_pct}%",
            'faltantes': faltantes[:5],
            'ya_tiene_like': ya_tiene_like
        }), 200

    except Exception as e:
        print(f"Error en /api/chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Ocurrió un error interno'}), 500


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
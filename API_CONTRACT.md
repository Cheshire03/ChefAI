# Contrato de API - ChefMind V01

## Descripción General
El backend de ChefMind expone una API RESTful construida con Flask. El endpoint principal está diseñado para recibir los ingredientes del usuario junto con su perfil de salud, y devolver una sugerencia gastronómica procesada a través del motor híbrido (TF-IDF Local + Google Gemini).

---

## Endpoint: Chat

**URL:** `/api/chat`
**Método:** `POST`
**Content-Type:** `application/json`

### Descripción
Recibe una cadena de texto con los ingredientes o petición del usuario y una condición médica opcional. Procesa la solicitud buscando la receta local más relevante (usando similitud del coseno sobre un modelo TF-IDF) filtrada por seguridad de la salud, y posteriormente utiliza Gemini para redactar la respuesta con tono empático.

### 1. Formato de Petición (Request)

```json
{
  "mensaje": "tengo pollo, arroz y zanahorias",
  "condicion": "diabetes"
}
```

| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :---: | :--- |
| `mensaje` | `string` | Sí | Texto libre ingresado por el usuario con los ingredientes disponibles. |
| `condicion` | `string` | No | Restricción médica seleccionada. Valores admitidos: `""` (vacio), `"diabetes"`, `"hipertension"`, `"celiaquia"`, `"resistencia_insulina"`, `"colesterol_alto"`. |

### 2. Formato de Respuesta Exitosa (Response 200 OK)

```json
{
  "status": "success",
  "respuesta": "¡Hola! Con pollo, arroz y zanahorias, te sugiero preparar una nutritiva *Sopa de Pollo con Arroz*...\n\n**Instrucciones:**\n1. Hierve el pollo...\n\n¡Espero que la disfrutes!",
  "receta_id": "receta_045",
  "metadata": {
    "procesamiento": "hibrido",
    "similitud_alcanzada": 0.85
  }
}
```

### 3. Formato de Error (Response 4xx/5xx)

```json
{
  "status": "error",
  "error": "El campo 'mensaje' es obligatorio y no puede estar vacío."
}
```

### 4. Códigos de Estado HTTP
* **200 OK:** La solicitud fue procesada con éxito y se generó una receta.
* **400 Bad Request:** Estructura de JSON inválida o parámetros faltantes.
* **500 Internal Server Error:** Fallo en el servidor local o error de conexión con la API de Google Gemini.

---
*Documento generado para la entrega del Avance V01.*

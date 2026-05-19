# Manual de Instalación y Arranque - ChefMind V01

Este documento contiene las instrucciones necesarias para levantar el proyecto ChefMind en tu entorno local.

## 1. Requisitos Previos
- **Python 3.10+** (Para el motor híbrido local)
- **Node.js 18+** (Para el cliente React)

## 2. Setup de Seguridad (.env)
Por cuestiones de seguridad (DevSecOps), las llaves de la API no están incluidas en el repositorio.
1. Busca el archivo `.env.example` en la raíz del proyecto.
2. Cópialo y renómbralo a `.env`.
3. Edita el archivo `.env` y coloca tu propia API Key de Google Gemini:
   ```env
   GEMINI_API_KEY=AIzaSy...
   API_PORT=5000
   ```

## 3. Arranque del Backend (Motor Híbrido)
Abre una terminal en la raíz del proyecto y ejecuta:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
*(Espera a que la consola indique `✅ Motor Local cargado correctamente` y `Running on http://127.0.0.1:5000`)*

## 4. Arranque del Frontend (React + Vite)
Abre **otra terminal nueva**, dirígete a la carpeta `frontend` y ejecuta:

```bash
cd frontend
npm install
npm run dev
```
Abre tu navegador en el enlace que te arroje Vite (generalmente `http://localhost:5173`).

## 5. Prueba de Humo
Para validar que el motor híbrido local se está comunicando correctamente con la API de Gemini usando tu llave:
1. Entra a la interfaz web.
2. Escribe en el chat: **"tengo huevo y aguacate"**.
3. Selecciona una restricción médica (opcional).
4. El sistema debería responderte con una recomendación adaptada o una sugerencia inteligente que haga referencia a esos ingredientes exactos.

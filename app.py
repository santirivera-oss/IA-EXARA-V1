from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder="frontend")  # Carpeta de tu index.html
CORS(app)

# Configura tu token de Hugging Face como variable de entorno en Render
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
HF_MODEL = "bigscience/bloom"  # Modelo gratuito, puedes cambiarlo

headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# Endpoint raíz para evitar 404
@app.route("/", methods=["GET"])
def home():
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    return "<h1>IA Minera Exara Backend ⚡</h1><p>Servidor activo. Usa el endpoint /ask para consultas.</p>"

# Endpoint principal de preguntas
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    pregunta = data.get("question", "")

    if not pregunta:
        return jsonify({"error": "No se envió pregunta."}), 400

    try:
        # Prompt profesional y humanizado
        prompt = f"""
Eres un experto en minería con décadas de experiencia y excelente capacidad de comunicación. 
Responde de manera clara, profesional y detallada, como ChatGPT 5:
- Respuestas completas y estructuradas
- Con contexto, ejemplos y aplicaciones
- Tono natural y confiable
- Emojis sutiles donde tengan sentido

Pregunta: "{pregunta}"
"""

        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 400}}
        res = requests.post(f"https://api-inference.huggingface.co/models/{HF_MODEL}", headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        output = res.json()

        # Extraer texto generado
        if isinstance(output, list) and "generated_text" in output[0]:
            respuesta = output[0]["generated_text"]
        else:
            respuesta = "❌ No se recibió respuesta del modelo."

    except Exception as e:
        respuesta = f"❌ Error al conectar con Hugging Face: {e}"

    # Aquí podrías aplicar tu función de humanización si quieres ajustar más emojis o cierres
    return jsonify({"answer": respuesta})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

# Servimos todos los archivos del frontend desde "frontend"
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Token de Hugging Face
HF_API_TOKEN = os.environ.get("HF_API_TOKEN")
HF_MODEL = "bigscience/bloom"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# ------------------------------
# Rutas para servir frontend
# ------------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    # Si el archivo existe, lo servimos
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    # Si no existe archivo, servimos index.html
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    # Mensaje simple si no hay frontend
    return "<h1>IA Minera Exara Backend ⚡</h1><p>Servidor activo. Usa el endpoint /ask para consultas.</p>"

# ------------------------------
# Endpoint /ask para la IA
# ------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    pregunta = data.get("question", "")

    if not pregunta:
        return jsonify({"error": "No se envió pregunta."}), 400

    try:
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
        res = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload,
            timeout=60
        )
        res.raise_for_status()
        output = res.json()

        if isinstance(output, list) and "generated_text" in output[0]:
            respuesta = output[0]["generated_text"]
        else:
            respuesta = "❌ No se recibió respuesta del modelo."

    except Exception as e:
        respuesta = f"❌ Error al conectar con Hugging Face: {e}"

    return jsonify({"answer": respuesta})

# ------------------------------
# Ejecutar app
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

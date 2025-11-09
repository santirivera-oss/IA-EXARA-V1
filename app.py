from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os

# Servimos todos los archivos desde la raíz del repositorio
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# Endpoint raíz: sirve index.html si existe, o mensaje simple
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def home(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    elif os.path.exists(os.path.join(app.static_folder, "index.html")):
        return send_from_directory(app.static_folder, "index.html")
    else:
        return "<h1>IA Minera Exara Backend ⚡</h1><p>Servidor activo. Usa el endpoint /ask para consultas.</p>"

# Endpoint principal de preguntas
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    pregunta = data.get("question", "")

    if not pregunta:
        return jsonify({"error": "No se envió pregunta."}), 400

    try:
        # Prompt profesional para Gemma: respuestas largas y humanas
        prompt = f"""
Eres un experto en minería con décadas de experiencia y excelente capacidad de comunicación. 
Tu tarea es responder a la pregunta de manera clara, profesional y detallada, como si explicaras a un estudiante avanzado o a un profesional que busca comprensión profunda. 
Sigue estas pautas:

1. Proporciona respuestas completas y bien estructuradas, divididas en párrafos.
2. Incluye contexto, razones y posibles aplicaciones de lo que explicas.
3. Usa ejemplos concretos y comparaciones si ayudan a clarificar.
4. Humaniza la respuesta: usa un tono natural, amistoso y confiable, como ChatGPT 5.
5. Usa emojis sutiles y contextuales, solo donde aporten claridad o emoción.
6. Evita instrucciones, títulos innecesarios o encabezados tipo “Respuesta:”.
7. Termina con una frase amable de cierre o recomendación cuando tenga sentido.

Pregunta: "{pregunta}"
"""

        result = subprocess.run(
            ["ollama", "run", "gemma", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        respuesta = result.stdout.strip()
    except Exception as e:
        respuesta = f"❌ Error al ejecutar Gemma: {e}"

    return jsonify({"answer": respuesta})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import logging
from functools import wraps
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración por defecto para la generación de imágenes
DEFAULT_CONFIG = {
    "steps": 4,
    "n": 1,
    "height": 768,
    "width": 768,
    "guidance": 3.5,
    "response_format": "base64",
    "negative_prompt": "",
    "seed": None,
}


def error_handler(f):
    """Decorator para manejar errores de forma consistente."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return wrapper


def validate_and_prepare_payload(request_data):
    """Valida y prepara el payload con los valores por defecto."""
    if not request_data.get("prompt"):
        raise ValueError("'prompt' is required")
    if not request_data.get("model"):
        raise ValueError("'model' is required")

    # Asegurar que response_format sea base64
    request_data["response_format"] = "base64"
    request_data["n"] = 1

    # Combinar con valores por defecto
    final_payload = DEFAULT_CONFIG.copy()
    final_payload.update(request_data)

    return final_payload


@app.route("/generate-image", methods=["POST"])
@error_handler
def generate_image():
    """Maneja solicitudes de generación de imágenes."""
    # Validar request
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    print(request.json)
    # Obtener y validar API key
    api_key = request.json.get("api_key")
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    try:
        # Preparar payload
        payload = validate_and_prepare_payload(request.json)

        # Configuración de la API
        url = "https://api.together.xyz/v1/images/generations"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}",
        }

        # Hacer request a Together API
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Extraer base64 de la imagen
        image_data = response.json()
        if not image_data.get("data") or not image_data["data"][0].get("b64_json"):
            raise ValueError("No image data in response")

        # Convertir base64 a bytes
        image_binary = base64.b64decode(image_data["data"][0]["b64_json"])

        # Crear un objeto BytesIO con los datos de la imagen
        image_io = BytesIO(image_binary)
        image_io.seek(0)

        # Devolver la imagen como respuesta binaria
        return send_file(
            image_io,
            mimetype="image/jpeg",
            as_attachment=False,
            download_name="generated_image.jpg",
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return jsonify({"error": "Failed to generate image"}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

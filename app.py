from flask import Flask, request, send_file, jsonify
from together import Together
import requests
import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
load_dotenv()
app = Flask(__name__)
client = Together()


def validate_request_data(data: Dict) -> Optional[str]:
    """Valida los datos requeridos en la solicitud"""
    required_fields = ["prompt", "model"]
    for field in required_fields:
        if field not in data:
            return f"El campo '{field}' es requerido"
    return None


def generate_image(data: Dict) -> Dict[str, Any]:
    """Genera una imagen usando la API de Together"""
    try:
        params = {
            "model": data.get("model", "black-forest-labs/FLUX.1-depth"),
            "width": int(data.get("width", 1024)),
            "height": int(data.get("height", 768)),
            "steps": int(data.get("steps", 28)),
            "prompt": data["prompt"],
        }

        if "image_url" in data:
            params["image_url"] = data["image_url"]

        image_completion = client.images.generate(**params)
        return {"success": True, "url": image_completion.data[0].url}
    except Exception as e:
        logger.error(f"Error en la generación de imagen: {e}")
        return {"success": False, "error": str(e)}


def download_to_temp(url: str) -> Optional[str]:
    """Descarga una imagen a un archivo temporal"""
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        response = requests.get(url)
        response.raise_for_status()

        with open(temp_file.name, "wb") as f:
            f.write(response.content)

        logger.info(f"Imagen guardada temporalmente en: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Error al descargar la imagen: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None


@app.route("/generate-image", methods=["POST"])
def generate_image_endpoint():
    """
    Endpoint para generar y descargar una imagen
    Espera un JSON con el siguiente formato:
    {
        "model": "black-forest-labs/FLUX.1-depth",
        "steps": 1,
        "height": 1024,
        "width": 768,
        "prompt": "descripción de la imagen",
        "image_url": "url de la imagen base" (opcional)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Se requieren datos en formato JSON"}), 400

        # Validar datos requeridos
        validation_error = validate_request_data(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        # Generar imagen
        result = generate_image(data)
        if not result["success"]:
            return jsonify({"error": result["error"]}), 500

        # Descargar a archivo temporal
        temp_path = download_to_temp(result["url"])
        if not temp_path:
            return jsonify({"error": "Error al descargar la imagen"}), 500

        try:
            return send_file(
                temp_path,
                mimetype="image/jpeg",
                as_attachment=True,
                download_name=f"generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            )
        finally:
            # Limpiar archivo temporal después de enviar
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Archivo temporal eliminado: {temp_path}")

    except Exception as e:
        logger.error(f"Error en el endpoint: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

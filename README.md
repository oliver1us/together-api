# Image Generation API con Together

Este proyecto expone un servicio REST basado en **Flask** que permite generar imágenes utilizando la API de **Together**.  
El servicio recibe un `prompt` junto con otros parámetros de configuración y devuelve la imagen generada en formato **JPEG**.

---

## 🚀 Características

- Endpoint `/generate-image` para la creación de imágenes.
- Comunicación directa con la **API de Together**.
- Validación de parámetros requeridos (`prompt`, `model`, `api_key`).
- Manejo centralizado de errores y respuestas claras.
- Devuelve la imagen lista para descargar/usar.
- Configuración por defecto para simplificar las solicitudes.
- Soporte **CORS** para integraciones frontend.

---

## 📦 Requisitos

- **Python 3.9+**
- Librerías (se definen en `requirements.txt`):
  - Flask
  - Flask-Cors
  - requests

---

## ⚙️ Uso Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/oliver1us/together-api.git
cd together-api
python other.py
```

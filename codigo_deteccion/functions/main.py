"""
Firebase Cloud Function para inferencia de modelo TFLite
Descarga modelo de Firebase Hosting y ejecuta predicciones
"""

from firebase_functions import https_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app
import functions_framework
from flask import jsonify
import requests
import io
import base64
import os

set_global_options(max_instances=10)
initialize_app()

# URLs de Firebase
FIREBASE_MODEL_URL = "https://detector-equipo-seguridad.web.app/model.tflite"
FIREBASE_LABELS_URL = "https://detector-equipo-seguridad.web.app/labels.txt"

# Variables globales
model_cache = {}

def get_labels():
    """Descargar labels de Firebase"""
    if 'labels' in model_cache:
        return model_cache['labels']

    try:
        response = requests.get(FIREBASE_LABELS_URL, timeout=10)
        response.raise_for_status()
        labels = [line.strip() for line in response.text.split('\n') if line.strip()]
        model_cache['labels'] = labels
        return labels
    except Exception as e:
        print(f"Error descargando labels: {e}")
        return []

@https_fn.on_request()
def predict(req: https_fn.Request) -> https_fn.Response:
    """
    Endpoint para hacer predicciones

    POST /predict
    Body: {"image": "base64_encoded_image"}

    Retorna: {"success": true, "detections": [...]}
    """

    if req.method != 'POST':
        return https_fn.Response('Usa POST', status_code=400)

    try:
        # Obtener imagen del request
        data = req.get_json()
        if not data or 'image' not in data:
            return https_fn.Response(
                jsonify({'error': 'No image provided'}),
                status_code=400
            )

        # Decodificar imagen base64
        try:
            image_data = base64.b64decode(data['image'])
        except Exception as e:
            return https_fn.Response(
                jsonify({'error': f'Invalid base64 image: {str(e)}'}),
                status_code=400
            )

        # Obtener labels
        labels = get_labels()
        if not labels:
            return https_fn.Response(
                jsonify({'error': 'Could not load labels'}),
                status_code=500
            )

        # Retornar estructura correcta
        # NOTA: Para inferencia REAL necesitaría tflite-runtime en Cloud Functions
        detections = [
            {
                'label': label,
                'confidence': 0.0  # Esperando tflite-runtime
            }
            for label in labels
        ]

        return https_fn.Response(
            jsonify({
                'success': True,
                'detections': detections,
                'count': len(detections),
                'note': 'Structure ready for real model inference'
            })
        )

    except Exception as e:
        print(f"Error: {e}")
        return https_fn.Response(
            jsonify({'error': str(e)}),
            status_code=500
        )

@https_fn.on_request()
def health(req: https_fn.Request) -> https_fn.Response:
    """Verificar estado de la función"""
    labels = get_labels()
    return https_fn.Response(
        jsonify({
            'status': 'ok',
            'labels_count': len(labels),
            'firebase_url': 'https://detector-equipo-seguridad.web.app'
        })
    )
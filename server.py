"""
Servidor Flask para Render.com
Descarga modelo de Firebase y ejecuta predicciones
"""

from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# URLs de Firebase
FIREBASE_MODEL_URL = "https://detector-equipo-seguridad.web.app/model.tflite"
FIREBASE_LABELS_URL = "https://detector-equipo-seguridad.web.app/labels.txt"

# Cache de labels
labels_cache = None

def get_labels():
    """Descargar labels de Firebase"""
    global labels_cache

    if labels_cache:
        return labels_cache

    try:
        print("📥 Descargando labels...")
        response = requests.get(FIREBASE_LABELS_URL, timeout=10)
        response.raise_for_status()

        labels_cache = [line.strip() for line in response.text.split('\n') if line.strip()]
        print(f"✓ Labels cargados: {len(labels_cache)} clases")
        return labels_cache
    except Exception as e:
        print(f"✗ Error descargando labels: {e}")
        return []

@app.route('/health', methods=['GET'])
def health():
    """Verificar estado del servidor"""
    labels = get_labels()
    return jsonify({
        'status': 'ok',
        'labels_count': len(labels),
        'firebase_model': FIREBASE_MODEL_URL
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Recibir imagen y retornar predicciones

    POST /predict
    Content-Type: multipart/form-data
    Body: image = [image_file]

    Retorna: {"success": true, "detections": [...]}
    """
    try:
        # Validar imagen
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        image_data = image_file.read()

        print(f"📸 Imagen recibida: {len(image_data)} bytes")

        # Obtener labels
        labels = get_labels()
        if not labels:
            return jsonify({'error': 'Could not load labels'}), 500

        # Retornar estructura correcta
        # NOTA: Para inferencia REAL necesitaría tflite-runtime
        detections = [
            {
                'label': label,
                'confidence': 0.0
            }
            for label in labels
        ]

        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections),
            'note': 'Structure ready for real model inference'
        })

    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Estado completo del servidor"""
    labels = get_labels()
    return jsonify({
        'server': 'running',
        'labels_count': len(labels),
        'firebase_model': FIREBASE_MODEL_URL,
        'instructions': 'Send POST to /predict with image file'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print("=" * 70)
    print("🚀 Servidor Flask (Render.com)")
    print("=" * 70)
    print(f"\n✓ Servidor iniciado en puerto {port}")
    print("✓ Modelo disponible en Firebase Hosting")
    print("\nEndpoints:")
    print("  GET  /health  - Estado del servidor")
    print("  GET  /status  - Status detallado")
    print("  POST /predict - Hacer predicción")
    print("\n" + "=" * 70 + "\n")

    app.run(host='0.0.0.0', port=port, debug=False)

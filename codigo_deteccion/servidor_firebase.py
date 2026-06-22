"""
Servidor Flask SIMPLIFICADO
Descarga modelo de Firebase y está listo para inferencia
Sin dependencias complicadas (solo flask, requests)
"""

from flask import Flask, request, jsonify
import requests
import os
import tempfile
import subprocess
import json

app = Flask(__name__)

# URLs de Firebase Hosting
FIREBASE_MODEL_URL = "https://detector-equipo-seguridad.web.app/model.tflite"
FIREBASE_LABELS_URL = "https://detector-equipo-seguridad.web.app/labels.txt"

model_path = None
labels_path = None
labels = []

def download_from_firebase(url, filename):
    """Descargar archivo desde Firebase Hosting"""
    try:
        print(f"📥 Descargando: {filename}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ {filename} descargado: {len(response.content)} bytes")
        return temp_path
    except Exception as e:
        print(f"✗ Error descargando {filename}: {e}")
        return None

def load_model():
    """Descargar modelo y labels de Firebase"""
    global model_path, labels_path, labels

    try:
        print("🔄 Cargando modelo desde Firebase...")

        # Descargar modelo
        model_path = download_from_firebase(FIREBASE_MODEL_URL, "model.tflite")
        if not model_path:
            return False

        # Descargar labels
        labels_path = download_from_firebase(FIREBASE_LABELS_URL, "labels.txt")
        if not labels_path:
            return False

        # Cargar labels en memoria
        with open(labels_path, 'r') as f:
            labels = [line.strip() for line in f if line.strip()]

        print(f"✓ Modelo listo: {model_path}")
        print(f"✓ Labels: {len(labels)} clases")
        for i, label in enumerate(labels):
            print(f"  {i}: {label}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    """Verificar estado del servidor"""
    return jsonify({
        'status': 'ok',
        'model_downloaded': model_path is not None,
        'labels_count': len(labels),
        'firebase_url': 'https://detector-equipo-seguridad.web.app'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Recibir imagen y retornar predicciones

    NOTA: Esta versión retorna estructura correcta
    Para inferencia REAL con TFLite, instala Python 64-bit oficial
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        image_data = image_file.read()

        print(f"📸 Imagen recibida: {len(image_data)} bytes")

        # Retornar estructura correcta (lista para modelo real)
        detections = [
            {
                'label': label,
                'confidence': 0.0  # Esperando tflite-runtime
            }
            for label in labels
        ]

        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections),
            'note': 'Estructura lista. Para usar modelo REAL: pip install tflite-runtime'
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Estado completo del servidor"""
    return jsonify({
        'server': 'running',
        'model_path': model_path,
        'labels_count': len(labels),
        'firebase_model': FIREBASE_MODEL_URL,
        'instructions': 'Para usar modelo REAL: instala Python 64-bit + pip install tflite-runtime'
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Servidor Firebase Simplificado")
    print("=" * 70)

    if not load_model():
        print("✗ Error cargando modelo de Firebase")
        exit(1)

    print("\n✓ Servidor iniciado: http://localhost:5000")
    print("✓ Modelo descargado de Firebase Hosting")
    print("\nEndpoints:")
    print("  GET  /health  - Estado del servidor")
    print("  GET  /status  - Status detallado")
    print("  POST /predict - Hacer predicción")
    print("\n⚠️  NOTA: Para usar modelo REAL:")
    print("  1. Instala Python 3.9 64-bit (python.org)")
    print("  2. pip install tflite-runtime")
    print("  3. Usa servidor.py")
    print("\n" + "=" * 70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)

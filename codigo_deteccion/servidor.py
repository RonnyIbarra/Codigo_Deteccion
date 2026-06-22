"""
Servidor que CARGA Y USA el modelo REAL entrenado desde Firebase
Descarga model.tflite + labels.txt de Firebase Hosting
"""

from flask import Flask, request, jsonify
import tflite_runtime.interpreter as tflite
from PIL import Image
import numpy as np
import io
import requests
import os
import tempfile

app = Flask(__name__)

# URLs de Firebase Hosting
FIREBASE_MODEL_URL = "https://detector-equipo-seguridad.web.app/model.tflite"
FIREBASE_LABELS_URL = "https://detector-equipo-seguridad.web.app/labels.txt"

# Cargar modelo REAL
interpreter = None
input_details = None
output_details = None
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
    global interpreter, input_details, output_details, labels

    try:
        print("🔄 Cargando modelo REAL desde Firebase...")

        # Descargar modelo desde Firebase
        model_path = download_from_firebase(FIREBASE_MODEL_URL, "model.tflite")
        if not model_path:
            return False

        # Cargar intérprete TFLite
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        print("✓ Modelo cargado correctamente")
        print(f"  Input: {input_details[0]['shape']}")

        # Descargar labels desde Firebase
        labels_path = download_from_firebase(FIREBASE_LABELS_URL, "labels.txt")
        if not labels_path:
            return False

        # Cargar labels
        with open(labels_path, 'r') as f:
            labels = [line.strip() for line in f if line.strip()]

        print(f"✓ Labels: {len(labels)} clases")
        for i, label in enumerate(labels):
            print(f"  {i}: {label}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model_loaded': interpreter is not None})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image'}), 400

        # Leer imagen
        image_data = request.files['image'].read()
        image = Image.open(io.BytesIO(image_data))

        # Redimensionar al tamaño del modelo
        h, w = input_details[0]['shape'][1], input_details[0]['shape'][2]
        image = image.resize((w, h))
        image_array = np.array(image, dtype=np.float32)

        # Normalizar
        if np.max(image_array) > 1:
            image_array = image_array / 255.0

        image_array = np.expand_dims(image_array, 0)

        # Ejecutar modelo REAL
        interpreter.set_tensor(input_details[0]['index'], image_array)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        # Procesar resultados
        predictions = output[0]
        detections = []

        for i, confidence in enumerate(predictions):
            if i < len(labels):
                detections.append({
                    'label': labels[i],
                    'confidence': float(confidence)
                })

        detections.sort(key=lambda x: x['confidence'], reverse=True)

        return jsonify({
            'success': True,
            'detections': detections
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not load_model():
        print("✗ No se pudo cargar el modelo")
        exit(1)

    print("\n✓ Servidor iniciado: http://localhost:5000")
    print("✓ Usando MODELO REAL entrenado")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)

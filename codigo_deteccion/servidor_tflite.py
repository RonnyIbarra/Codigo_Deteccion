"""
Servidor Flask con TensorFlow Lite
Ejecuta el modelo real entrenado y sirve predicciones a la app Flutter
"""

from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

app = Flask(__name__)

# Cargar modelo TFLite
MODEL_PATH = 'assets/model.tflite'
LABELS_PATH = 'assets/labels.txt'

# Variables globales
interpreter = None
input_details = None
output_details = None
labels = []

def load_model():
    """Cargar modelo TFLite y labels"""
    global interpreter, input_details, output_details, labels

    try:
        # Cargar intérprete TFLite
        interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        print(f"✓ Modelo cargado: {MODEL_PATH}")
        print(f"  Input shape: {input_details[0]['shape']}")
        print(f"  Input type: {input_details[0]['dtype']}")

        # Cargar labels
        with open(LABELS_PATH, 'r') as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]

        print(f"✓ Labels cargados: {len(labels)} clases")
        for i, label in enumerate(labels):
            print(f"  {i}: {label}")

        return True
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        return False

def preprocess_image(image_data):
    """Preprocesar imagen para el modelo"""
    try:
        # Cargar imagen desde bytes
        image = Image.open(io.BytesIO(image_data))

        # Redimensionar según requiere el modelo
        input_shape = input_details[0]['shape']
        height, width = input_shape[1], input_shape[2]

        image = image.resize((width, height))
        image = np.array(image, dtype=np.float32)

        # Normalizar si es necesario
        if np.max(image) > 1.0:
            image = image / 255.0

        # Agregar dimensión de batch
        image = np.expand_dims(image, axis=0)

        return image
    except Exception as e:
        print(f"✗ Error preprocesando imagen: {e}")
        return None

def run_inference(image):
    """Ejecutar inferencia en imagen"""
    try:
        # Establecer input
        interpreter.set_tensor(input_details[0]['index'], image)

        # Ejecutar
        interpreter.invoke()

        # Obtener output
        output = interpreter.get_tensor(output_details[0]['index'])

        return output[0]  # Retornar first batch
    except Exception as e:
        print(f"✗ Error ejecutando inferencia: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud - verifica que el servidor está activo"""
    return jsonify({'status': 'ok', 'model_loaded': interpreter is not None})

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint principal - recibe imagen y retorna detecciones"""
    try:
        # Obtener imagen
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        image_data = image_file.read()

        # Preprocesar
        image = preprocess_image(image_data)
        if image is None:
            return jsonify({'error': 'Error preprocessing image'}), 400

        # Inferencia
        predictions = run_inference(image)
        if predictions is None:
            return jsonify({'error': 'Error running inference'}), 400

        # Procesar resultados
        detections = []
        for i, confidence in enumerate(predictions):
            if i < len(labels):
                detections.append({
                    'label': labels[i],
                    'confidence': float(confidence)
                })

        # Ordenar por confianza
        detections.sort(key=lambda x: x['confidence'], reverse=True)

        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections)
        })

    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor TensorFlow Lite")
    print("=" * 60)

    # Cargar modelo
    if not load_model():
        print("✗ No se pudo cargar el modelo")
        exit(1)

    print("\n✓ Servidor iniciado en http://localhost:5000")
    print("✓ La app Flutter se conectará automáticamente")
    print("\nEndpoints:")
    print("  GET  /health  - Estado del servidor")
    print("  POST /predict - Hacer predicción")
    print("\n" + "=" * 60)

    # Ejecutar servidor
    app.run(host='0.0.0.0', port=5000, debug=False)

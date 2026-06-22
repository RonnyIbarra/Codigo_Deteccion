"""
Servidor Flask con TensorFlow Lite REAL
Descarga modelo de Firebase y ejecuta inferencia en tiempo real
"""

from flask import Flask, request, jsonify
import requests
import io
import os
import tempfile
import numpy as np
from PIL import Image

app = Flask(__name__)

# URLs de Firebase
FIREBASE_MODEL_URL = "https://detector-equipo-seguridad.web.app/model.tflite"
FIREBASE_LABELS_URL = "https://detector-equipo-seguridad.web.app/labels.txt"

# Variables globales
interpreter = None
input_details = None
output_details = None
labels = []
model_path = None

def load_tflite_model():
    """Cargar modelo TFLite de Firebase"""
    global interpreter, input_details, output_details, labels, model_path

    try:
        print("🔄 Descargando modelo de Firebase...")

        # Descargar modelo
        response = requests.get(FIREBASE_MODEL_URL, timeout=30)
        response.raise_for_status()

        # Guardar en temp
        model_path = os.path.join(tempfile.gettempdir(), 'model.tflite')
        with open(model_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ Modelo descargado: {len(response.content)} bytes")

        # Cargar intérprete
        try:
            import tflite_runtime.interpreter as tflite
            interpreter = tflite.Interpreter(model_path=model_path)
            print("✓ Usando tflite-runtime")
        except ImportError:
            print("⚠️  tflite-runtime no disponible, intentando tensorflow...")
            try:
                import tensorflow as tf
                interpreter = tf.lite.Interpreter(model_path=model_path)
                print("✓ Usando tensorflow.lite")
            except ImportError:
                print("✗ No hay librería TFLite disponible")
                return False

        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        print(f"✓ Modelo cargado correctamente")
        print(f"  Input shape: {input_details[0]['shape']}")

        # Descargar labels
        response = requests.get(FIREBASE_LABELS_URL, timeout=10)
        response.raise_for_status()

        labels = [line.strip() for line in response.text.split('\n') if line.strip()]

        print(f"✓ Labels: {len(labels)} clases")
        for i, label in enumerate(labels):
            print(f"  {i}: {label}")

        return True
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        return False

def preprocess_image(image_data):
    """Preprocesar imagen para el modelo"""
    try:
        # Cargar imagen
        image = Image.open(io.BytesIO(image_data))

        # Redimensionar
        input_shape = input_details[0]['shape']
        height, width = input_shape[1], input_shape[2]

        image = image.resize((width, height))
        image_array = np.array(image, dtype=np.float32)

        # Normalizar
        if np.max(image_array) > 1.0:
            image_array = image_array / 255.0

        # Agregar batch
        image_array = np.expand_dims(image_array, axis=0)

        return image_array
    except Exception as e:
        print(f"✗ Error preprocesando: {e}")
        return None

def run_inference(image):
    """Ejecutar inferencia con modelo TFLite"""
    try:
        interpreter.set_tensor(input_details[0]['index'], image)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
        return output[0]
    except Exception as e:
        print(f"✗ Error en inferencia: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Estado del servidor"""
    return jsonify({
        'status': 'ok',
        'model_loaded': interpreter is not None,
        'labels_count': len(labels)
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Hacer predicción en tiempo real
    POST /predict
    Body: image (multipart file)
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        image_data = image_file.read()

        print(f"📸 Imagen recibida: {len(image_data)} bytes")

        # Preprocesar
        image = preprocess_image(image_data)
        if image is None:
            return jsonify({'error': 'Error preprocessing image'}), 400

        # Inferencia REAL
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

@app.route('/status', methods=['GET'])
def status():
    """Status detallado"""
    return jsonify({
        'server': 'running',
        'model_loaded': interpreter is not None,
        'labels_count': len(labels),
        'firebase_model': FIREBASE_MODEL_URL,
        'inference': 'REAL con TFLite ✅'
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Servidor Flask con TensorFlow Lite REAL")
    print("=" * 70)

    if not load_tflite_model():
        print("✗ No se pudo cargar el modelo")
        exit(1)

    port = int(os.environ.get('PORT', 5000))

    print(f"\n✓ Servidor iniciado en puerto {port}")
    print("✓ Usando MODELO REAL entrenado con inferencia en tiempo real")
    print("✓ Modelo descargado de Firebase Hosting")
    print("\nEndpoints:")
    print("  GET  /health  - Estado del servidor")
    print("  GET  /status  - Status detallado")
    print("  POST /predict - Hacer predicción (inferencia real)")
    print("\n" + "=" * 70 + "\n")

    app.run(host='0.0.0.0', port=port, debug=False)

"""
Servidor Flask con TensorFlow Lite REAL - INFERENCIA EN TIEMPO REAL
Usa model_unquant.tflite con normalización correcta [-1, 1]
Basado en: Proyecto_Interculturalidad_Pato
"""

from flask import Flask, request, jsonify
import io
import os
import numpy as np
from PIL import Image

app = Flask(__name__)

# Variables globales
interpreter = None
input_details = None
output_details = None
labels = []
model_path = None
input_size = 224

def load_tflite_model():
    """Cargar modelo TFLite SIN CUANTIZAR desde assets"""
    global interpreter, input_details, output_details, labels, model_path, input_size

    try:
        print("🔄 Cargando modelo SIN CUANTIZAR...")

        # Usar modelo SIN CUANTIZAR (model_unquant.tflite)
        model_path = 'codigo_deteccion/assets/model_unquant.tflite'

        if not os.path.exists(model_path):
            print(f"⚠️  model_unquant.tflite no encontrado, intentando model.tflite...")
            model_path = 'codigo_deteccion/assets/model.tflite'
            if not os.path.exists(model_path):
                print(f"✗ Ningún modelo encontrado")
                return False

        print(f"✓ Modelo encontrado: {model_path}")

        # Cargar intérprete
        import tflite_runtime.interpreter as tflite
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Obtener tamaño de entrada (típicamente 224x224)
        input_shape = input_details[0]['shape']
        if len(input_shape) >= 2:
            input_size = input_shape[1]

        print(f"✓ Modelo cargado correctamente")
        print(f"  Input shape: {input_details[0]['shape']}")
        print(f"  Input dtype: {input_details[0]['dtype']}")
        print(f"  Input size: {input_size}x{input_size}")

        # Cargar labels locales
        labels_path = 'codigo_deteccion/assets/labels.txt'
        with open(labels_path, 'r') as f:
            labels = [line.strip() for line in f if line.strip()]

        print(f"✓ Labels: {len(labels)} clases")
        for i, label in enumerate(labels):
            print(f"  {i}: {label}")

        return True
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        import traceback
        traceback.print_exc()
        return False

def preprocess_image(image_data):
    """Preprocesar imagen EXACTAMENTE como Proyecto_Interculturalidad_Pato"""
    try:
        # Cargar imagen
        image = Image.open(io.BytesIO(image_data))

        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Redimensionar a 224x224 (Teachable Machine estándar)
        image = image.resize((input_size, input_size), Image.LANCZOS)
        image_array = np.array(image, dtype=np.float32)

        # ¡¡CLAVE!! Normalizar a [-1, 1] como Teachable Machine
        # NO dividir por 255, sino usar: (x / 127.5) - 1.0
        image_array = (image_array / 127.5) - 1.0

        # Agregar batch dimension [1, 224, 224, 3]
        image_array = np.expand_dims(image_array, axis=0)

        print(f"✓ Imagen preprocesada: shape={image_array.shape}, dtype={image_array.dtype}")
        print(f"  Min={image_array.min():.3f}, Max={image_array.max():.3f}")

        return image_array
    except Exception as e:
        print(f"✗ Error preprocesando: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_inference(image):
    """Ejecutar inferencia con modelo TFLite"""
    try:
        interpreter.set_tensor(input_details[0]['index'], image)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        # output[0] tiene shape [1, num_classes]
        predictions = output[0] if len(output.shape) == 2 else output

        print(f"✓ Inferencia completada: {predictions.shape}")

        return predictions
    except Exception as e:
        print(f"✗ Error en inferencia: {e}")
        import traceback
        traceback.print_exc()
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

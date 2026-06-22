"""
Servidor Flask SIMPLE sin TensorFlow
Solo necesita: flask, pillow
"""

from flask import Flask, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model_loaded': True})

@app.route('/predict', methods=['POST'])
def predict():
    """Retorna detecciones simuladas

    PARA USAR MODELO REAL:
    1. Instala: pip install tflite-runtime
    2. Descomentas las líneas de inferencia abajo
    3. Ejecuta este servidor
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']

        # Validar que es imagen
        try:
            image = Image.open(io.BytesIO(image_file.read()))
        except:
            return jsonify({'error': 'Invalid image'}), 400

        # AQUÍ iría la inferencia real con TFLite
        # Pero por ahora retornamos detecciones simuladas

        labels = [
            '0_casco', '1_chaleco', '2_gafas', '3_buff',
            '4_pistola', '5_arma_principal', '6_botas', '7_uniforme_militar'
        ]

        # Simular detecciones (0.0 = no detectado)
        detections = [
            {'label': label, 'confidence': 0.0}
            for label in labels
        ]

        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections),
            'note': 'Simulado - para usar modelo real, instala tflite-runtime'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor Simple (Demo)")
    print("=" * 60)
    print("\n✓ Servidor en http://localhost:5000")
    print("✓ Endpoints:")
    print("  GET  /health")
    print("  POST /predict")
    print("\n⚠️  NOTA: Retorna detecciones SIMULADAS")
    print("Para usar modelo REAL:")
    print("  pip install tflite-runtime")
    print("\n" + "=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)

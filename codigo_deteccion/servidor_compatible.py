"""
Servidor COMPATIBLE Python 32 bits
Solo necesita: flask, pillow (ya instalados)

NOTA: Retorna estructura correcta pero detecciones vacías (0.0)
Para usar modelo REAL: instala Python 64 bits + tflite-runtime
"""

from flask import Flask, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

# Labels del modelo
LABELS = [
    '0_casco',
    '1_chaleco',
    '2_gafas',
    '3_buff',
    '4_pistola',
    '5_arma_principal',
    '6_botas',
    '7_uniforme_militar'
]

@app.route('/health', methods=['GET'])
def health():
    """Verificar estado del servidor"""
    return jsonify({
        'status': 'ok',
        'python_version': '32-bit compatible',
        'model_status': 'waiting_for_64bit_python'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Procesar imagen y retornar detecciones

    IMPORTANTE:
    - Actualmente retorna estructura correcta con confianza 0.0
    - Para usar modelo REAL necesitas:
      1. Instalar Python 64 bits
      2. pip install tflite-runtime
      3. Usar servidor.py
    """
    try:
        # Validar imagen
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        image_data = image_file.read()

        # Validar que sea imagen válida
        try:
            image = Image.open(io.BytesIO(image_data))
            print(f"✓ Imagen recibida: {image.size}")
        except Exception as e:
            return jsonify({'error': f'Invalid image: {str(e)}'}), 400

        # Retornar estructura correcta (preparada para modelo real)
        detections = []
        for label in LABELS:
            detections.append({
                'label': label,
                'confidence': 0.0  # Esperando Python 64 bits para inferencia real
            })

        return jsonify({
            'success': True,
            'detections': detections,
            'note': 'Python 32-bit compatible mode. For real detections, install Python 64-bit + tflite-runtime',
            'app_status': 'READY_FOR_UPGRADE'
        })

    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upgrade', methods=['GET'])
def upgrade_info():
    """Información para actualizar a Python 64 bits"""
    return jsonify({
        'current': 'Python 32-bit (compatible but limited)',
        'required_for_real_model': 'Python 64-bit',
        'steps': [
            '1. Download Python 3.9 64-bit from python.org',
            '2. Install with "Add Python to PATH"',
            '3. Run: pip install tflite-runtime',
            '4. Use servidor.py instead of servidor_compatible.py',
            '5. Restart app'
        ],
        'download_url': 'https://www.python.org/downloads/release/python-3915/'
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Servidor COMPATIBLE Python 32-bit")
    print("=" * 70)
    print("\n⚠️  MODO: Estructura lista, esperando Python 64-bit para modelo real")
    print("\n📍 Servidor: http://localhost:5000")
    print("\n📋 Endpoints:")
    print("  GET  /health    - Estado del servidor")
    print("  POST /predict   - Hacer predicción (retorna estructura)")
    print("  GET  /upgrade   - Información para actualizar")
    print("\n🔄 Próximos pasos:")
    print("  1. Instala Python 3.9 64-bit")
    print("  2. pip install tflite-runtime")
    print("  3. Ejecuta: python servidor.py")
    print("\n" + "=" * 70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)

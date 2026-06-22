import 'detection_service.dart';

/// Implementación stub de DetectionService para Web
/// Web no soporta TensorFlow Lite (no hay FFI)
/// Esta implementación simula detecciones para demostración
class WebDetectionService extends DetectionService {
  bool _isLoaded = false;

  @override
  bool get isLoaded => _isLoaded;

  @override
  Future<bool> loadModel() async {
    try {
      print('⚠️ Web: Modo demo activado (sin TensorFlow Lite)');
      print('ℹ️ Nota: TFLite no está disponible en navegadores Web');
      _isLoaded = true;
      return true;
    } catch (e) {
      print('✗ Error: $e');
      _isLoaded = false;
      return false;
    }
  }

  @override
  Future<List<DetectionResult>> detectObjects(List<int> imageBytes) async {
    if (!_isLoaded) {
      throw Exception('Modelo no cargado');
    }

    try {
      // En Web, retornar resultados simulados para demo
      // En producción, podrías:
      // 1. Usar un servidor que ejecute TFLite
      // 2. Usar TensorFlow.js (versión JavaScript de TF)
      // 3. Usar otra solución Web-compatible

      print('📸 Web: Simulando detección de objetos');

      // Simular algunos resultados
      return [
        DetectionResult(label: '0_casco', confidence: 0.85),
        DetectionResult(label: '1_chaleco', confidence: 0.92),
        DetectionResult(label: '2_gafas', confidence: 0.78),
      ];
    } catch (e) {
      print('✗ Error detectando objetos: $e');
      return [];
    }
  }

  @override
  List<DetectionResult> filterByConfidence(
    List<DetectionResult> results, {
    double threshold = 0.7,
  }) {
    return results.where((r) => r.confidence > threshold).toList();
  }

  @override
  void dispose() {
    _isLoaded = false;
  }
}

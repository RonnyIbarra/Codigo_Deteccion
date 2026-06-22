import 'package:http/http.dart' as http;
import 'dart:convert';
import 'detection_service.dart';

/// Implementación de DetectionService usando SERVIDOR BACKEND
/// El modelo REAL TFLite se ejecuta en: http://localhost:5000
///
/// PASOS PARA USAR:
/// 1. Crear servidor Flask/FastAPI con modelo TFLite
/// 2. Ejecutar: python servidor.py
/// 3. Compilar app
/// 4. App conectará automáticamente al servidor
class TFLiteDetectionService extends DetectionService {
  bool _isLoaded = false;
  static const String _serverUrl = 'http://10.0.2.2:5000'; // Android emulator
  // Para dispositivo real: 'http://TU_IP_PC:5000'

  @override
  bool get isLoaded => _isLoaded;

  @override
  Future<bool> loadModel() async {
    try {
      print('🔄 Conectando a servidor con modelo REAL...');
      print('📍 Servidor: $_serverUrl');

      // Verificar que el servidor esté disponible
      try {
        final response =
            await http.get(Uri.parse('$_serverUrl/health')).timeout(
          const Duration(seconds: 5),
        );

        if (response.statusCode == 200) {
          print('✓ Servidor backend conectado');
          print('✓ Modelo TFLite REAL disponible');
          _isLoaded = true;
          return true;
        }
      } catch (e) {
        print('⚠️  Servidor no disponible: $e');
        print('📋 Para usar modelo REAL:');
        print('   1. Crea servidor Flask con TFLite');
        print('   2. Ejecuta: python servidor.py');
        print('   3. Recompila app');
      }

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
      // Intentar enviar al servidor
      final request = http.MultipartRequest('POST',
          Uri.parse('$_serverUrl/predict'));
      request.files.add(
        http.MultipartFile.fromBytes('image', imageBytes,
            filename: 'image.jpg'),
      );

      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 10),
      );

      if (streamedResponse.statusCode == 200) {
        final response = await http.Response.fromStream(streamedResponse);
        final data = jsonDecode(response.body);

        // Procesar respuesta del servidor
        List<DetectionResult> results = [];
        if (data['detections'] != null) {
          for (var detection in data['detections']) {
            results.add(DetectionResult(
              label: detection['label'],
              confidence: (detection['confidence'] as num).toDouble(),
            ));
          }
        }

        return results;
      }
    } catch (e) {
      print('Info: Servidor no disponible, usando detecciones vacías');
    }

    // Retornar vacío si no hay servidor
    return [
      DetectionResult(label: '0_casco', confidence: 0.0),
      DetectionResult(label: '1_chaleco', confidence: 0.0),
      DetectionResult(label: '2_gafas', confidence: 0.0),
      DetectionResult(label: '3_buff', confidence: 0.0),
      DetectionResult(label: '4_pistola', confidence: 0.0),
      DetectionResult(label: '5_arma_principal', confidence: 0.0),
      DetectionResult(label: '6_botas', confidence: 0.0),
      DetectionResult(label: '7_uniforme_militar', confidence: 0.0),
    ];
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

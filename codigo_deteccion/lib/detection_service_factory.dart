import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'detection_service.dart';
import 'tflite_detection_service.dart';

/// Factory para crear la implementación correcta de DetectionService
/// según la plataforma de ejecución
class DetectionServiceFactory {
  /// Crea una instancia de DetectionService apropiada para la plataforma actual
  static DetectionService createDetectionService() {
    // Web siempre usa stub (no tiene TFLite)
    if (kIsWeb) {
      print('🌐 Plataforma: Web (modo demo - sin TFLite)');
      return _WebDetectionServiceStub();
    }

    // Plataformas nativas: intentar usar TFLite si está disponible
    if (_canUseTFLite()) {
      print('📱 Plataforma: Android/iOS con TFLite');
      try {
        // Solo importar y usar TFLite en Android/iOS
        return _createNativeTFLiteService();
      } catch (e) {
        print('⚠️  Error con TFLite: $e, usando stub');
        return _WebDetectionServiceStub();
      }
    }

    // Windows, Linux, macOS: usar stub
    print('⚠️  Plataforma: Sin TFLite disponible, usando demo');
    return _WebDetectionServiceStub();
  }

  /// Verificar si se puede usar TFLite
  static bool _canUseTFLite() {
    // TFLite funciona bien en Android e iOS
    return defaultTargetPlatform == TargetPlatform.android ||
        defaultTargetPlatform == TargetPlatform.iOS;
  }

  /// Crear servicio TFLite para plataformas nativas
  static DetectionService _createNativeTFLiteService() {
    try {
      // Usar TFLiteDetectionService (ahora es compatible)
      return TFLiteDetectionService();
    } catch (e) {
      print('Error cargando TFLite: $e');
      return _WebDetectionServiceStub();
    }
  }
}

/// Stub para plataformas sin TFLite (Web, Windows, Linux, macOS)
class _WebDetectionServiceStub extends DetectionService {
  bool _isLoaded = false;

  @override
  bool get isLoaded => _isLoaded;

  @override
  Future<bool> loadModel() async {
    try {
      print('⚠️  TensorFlow Lite no disponible en esta plataforma');
      print('ℹ️  Modo demo: Retornando detecciones simuladas');
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
      print('📸 Demo: Simulando detección de objetos');
      await Future.delayed(const Duration(milliseconds: 300));

      // Retornar resultados simulados
      return [
        DetectionResult(label: '0_casco', confidence: 0.85),
        DetectionResult(label: '1_chaleco', confidence: 0.90),
        DetectionResult(label: '2_gafas', confidence: 0.72),
        DetectionResult(label: '3_buff', confidence: 0.68),
        DetectionResult(label: '4_pistola', confidence: 0.78),
      ];
    } catch (e) {
      print('✗ Error: $e');
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

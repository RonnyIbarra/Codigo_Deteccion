/// Interfaz abstracta para servicio de detección
/// Permite múltiples implementaciones (TFLite, Web, etc.)
abstract class DetectionService {
  bool get isLoaded;

  Future<bool> loadModel();

  Future<List<DetectionResult>> detectObjects(List<int> imageBytes);

  List<DetectionResult> filterByConfidence(
    List<DetectionResult> results, {
    double threshold = 0.7,
  });

  void dispose();
}

class DetectionResult {
  final String label;
  final double confidence;

  DetectionResult({
    required this.label,
    required this.confidence,
  });

  @override
  String toString() => '$label: ${(confidence * 100).toStringAsFixed(2)}%';
}

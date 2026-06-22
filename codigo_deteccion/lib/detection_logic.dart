/// Lógica de validación de equipo de seguridad
class DetectionLogic {
  // Conjunto de objetos requeridos para estar APTO
  static const Set<String> requiredObjects = {
    '0_casco',
    '1_chaleco',
    '2_gafas',
    '3_buff',
    '4_pistola',
    '5_arma_principal',
    '6_botas',
    '7_uniforme_militar',
  };

  // Objetos detectados en tiempo real
  final Set<String> detectedObjects = {};

  /// Agregar un objeto detectado
  void addDetectedObject(String objectLabel) {
    if (requiredObjects.contains(objectLabel)) {
      detectedObjects.add(objectLabel);
    }
  }

  /// Agregar múltiples objetos detectados
  void addDetectedObjects(List<String> objects) {
    for (final obj in objects) {
      addDetectedObject(obj);
    }
  }

  /// Obtener objetos faltantes
  Set<String> getMissingObjects() {
    return requiredObjects.difference(detectedObjects);
  }

  /// Determinar si está APTO
  bool isApto() {
    return getMissingObjects().isEmpty;
  }

  /// Obtener estado legible
  String getStatus() {
    return isApto() ? 'APTO' : 'NO APTO';
  }

  /// Obtener porcentaje de completitud
  double getCompletenessPercentage() {
    return (detectedObjects.length / requiredObjects.length) * 100;
  }

  /// Limpiar detecciones (reiniciar)
  void reset() {
    detectedObjects.clear();
  }

  /// Obtener lista de nombres de objetos faltantes (más legible)
  List<String> getMissingObjectsNames() {
    return getMissingObjects()
        .map((label) => getLabelName(label))
        .toList()
      ..sort();
  }

  /// Obtener lista de nombres de objetos detectados
  List<String> getDetectedObjectsNames() {
    return detectedObjects
        .map((label) => getLabelName(label))
        .toList()
      ..sort();
  }

  /// Convertir label técnico a nombre amigable
  static String getLabelName(String label) {
    final Map<String, String> labelNames = {
      '0_casco': 'Casco',
      '1_chaleco': 'Chaleco',
      '2_gafas': 'Gafas',
      '3_buff': 'Buff',
      '4_pistola': 'Pistola',
      '5_arma_principal': 'Arma Principal',
      '6_botas': 'Botas',
      '7_uniforme_militar': 'Uniforme Militar',
    };
    return labelNames[label] ?? label;
  }

  /// Obtener información detallada del estado
  String getDetailedStatus() {
    final buffer = StringBuffer();
    buffer.writeln('Estado: ${getStatus()}');
    buffer.writeln('Completitud: ${getCompletenessPercentage().toStringAsFixed(1)}%');
    buffer.writeln('Detectados: ${detectedObjects.length}/${requiredObjects.length}');

    final detected = getDetectedObjectsNames();
    if (detected.isNotEmpty) {
      buffer.writeln('\n✓ Detectados:');
      for (final obj in detected) {
        buffer.writeln('  • $obj');
      }
    }

    final missing = getMissingObjectsNames();
    if (missing.isNotEmpty) {
      buffer.writeln('\n✗ Faltantes:');
      for (final obj in missing) {
        buffer.writeln('  • $obj');
      }
    }

    return buffer.toString();
  }
}

# 🚀 Instrucciones de Ejecución - Detector de Equipo de Seguridad

## ✅ Requisitos Previos

1. **Flutter SDK instalado** (versión 3.12.2 o superior)
   - Verificar: `flutter --version`

2. **Modelo TensorFlow Lite**
   - Descargar de Teachable Machine: https://teachablemachine.withgoogle.com/
   - Exportar como "TensorFlow Lite" → "Floating point"
   - Renombrar a `model.tflite`
   - Colocar en `assets/model.tflite`

3. **Archivo de etiquetas**
   - Ya incluido en `assets/labels.txt`
   - Contiene las 8 clases: casco, chaleco, gafas, buff, pistola, arma_principal, botas, uniforme_militar

4. **Dispositivo o emulador Android**
   - API 21+ recomendado
   - Cámara funcional
   - Permisos de cámara habilitados

## 📦 Instalación

### Paso 1: Descargar dependencias
```bash
flutter pub get
```

### Paso 2: Colocar modelo TFLite
1. Exportar modelo desde Teachable Machine
2. Renombrarlo a `model.tflite`
3. Copiarlo a `assets/model.tflite`

### Paso 3: Ejecutar en Android
```bash
flutter run -d android
```

O para un dispositivo específico:
```bash
flutter run -d <device_id>
```

Ver dispositivos disponibles:
```bash
flutter devices
```

### Paso 4: Ejecutar en iOS (opcional)
```bash
flutter run -d ios
```

## 🎯 Uso de la App

1. **Abre la app** - Se pedirán permisos de cámara
2. **Apunta la cámara** - Hacia la persona con el equipo
3. **Visualiza resultados** en tiempo real:
   - ✅ **APTO** (verde) - Si tiene TODO el equipo
   - ❌ **NO APTO** (rojo) - Si falta algún elemento
4. **Botón Reiniciar** - Para resetear la detección

## 📊 Indicadores en Pantalla

- **Estado Grande**: APTO / NO APTO con color (verde/rojo)
- **Porcentaje**: % de equipo detectado (ej: 75%)
- **Detectados**: Lista con ✓ de objetos encontrados
- **Faltantes**: Lista con ✗ de objetos que faltan
- **Confianza**: Se actualiza en tiempo real

## 🔍 Requisitos Técnicos

### Estructura de Carpetas (debe existir)
```
lib/
├── main.dart              # Punto de entrada
├── camera_screen.dart     # Pantalla principal con cámara
├── tflite_service.dart    # Servicio de inferencia TFLite
└── detection_logic.dart   # Lógica de validación

assets/
├── model.tflite          # ⚠️ AGREGAR MANUALMENTE
└── labels.txt            # Incluido
```

### Dependencias (ya configuradas en pubspec.yaml)
- **camera**: 0.10.5+8 - Acceso a cámara
- **tflite_flutter**: 0.10.4 - Inferencia TFLite
- **image**: 4.1.7 - Procesamiento de imágenes
- **permission_handler**: 11.4.4 - Permisos

## ⚙️ Configuración Avanzada

### Cambiar intervalo de procesamiento
En `camera_screen.dart`, línea con `_processingIntervalMs`:
```dart
final int _processingIntervalMs = 500; // Milisegundos
```

### Cambiar umbral de confianza
En `camera_screen.dart`, en `_processFrame()`:
```dart
final filtered = _tfliteService!.filterByConfidence(results, threshold: 0.7);
```

### Usar cámara trasera en lugar de frontal
En `camera_screen.dart`, cambiar:
```dart
final camera = cameras.firstWhere(
  (c) => c.lensDirection == CameraLensDirection.back, // Cambiar front → back
  orElse: () => cameras.first,
);
```

## 🐛 Solución de Problemas

### "Modelo no cargado"
- ✓ Verifica que `assets/model.tflite` existe
- ✓ Verifica que `pubspec.yaml` tiene los assets configurados
- ✓ Ejecuta: `flutter pub get`

### "Permiso de cámara denegado"
- ✓ Acepta permisos cuando se pida
- ✓ Verifica en Configuración > Permisos > Cámara

### "Error ejecutando inferencia"
- ✓ Verifica que el modelo TFLite es válido
- ✓ Revisa que los labels coinciden con el modelo

### "Cámara no inicializa"
- ✓ Verifica que el emulador/dispositivo tiene cámara
- ✓ Intenta reiniciar el dispositivo

## 📝 Logs y Debugging

Para ver logs de la app:
```bash
flutter logs
```

Para debug más detallado:
```bash
flutter run -v
```

## 🎓 Uso Académico

Este proyecto es para detección de equipo de seguridad en tiempo real. Optimizado para:
- Detección en vivo con baja latencia
- Interfaz clara para validación rápida
- Acumulación de detecciones para mejor precisión
- UI moderna con Material Design 3

---

**¿Problemas?** Verifica los logs: `flutter logs`

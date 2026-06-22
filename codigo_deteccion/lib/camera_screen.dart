import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:async';

import 'detection_service.dart';
import 'detection_service_factory.dart';
import 'detection_logic.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _cameraController;
  DetectionService? _detectionService;
  DetectionLogic? _detectionLogic;

  bool _isInitialized = false;
  bool _isProcessing = false;
  String _statusText = 'Inicializando...';
  Color _statusColor = Colors.grey;
  List<String> _detectedObjects = [];
  List<String> _missingObjects = [];
  double _confidence = 0.0;

  Timer? _processingTimer;
  final int _processingIntervalMs = 500; // Procesar cada 500ms

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    try {
      // En Web, saltar permisos de cámara (no soportado)
      if (kIsWeb) {
        print('🌐 Web: Saltando permisos de cámara');
        _initializeWithoutCamera();
        return;
      }

      // Solicitar permisos de cámara (solo en plataformas nativas)
      final cameraStatus = await Permission.camera.request();

      if (!cameraStatus.isGranted) {
        if (mounted) {
          setState(() {
            _statusText = 'Permiso de cámara denegado';
            _statusColor = Colors.red;
          });
        }
        return;
      }

      // Inicializar servicio de detección (TFLite o Web stub)
      _detectionService = DetectionServiceFactory.createDetectionService();
      final modelLoaded = await _detectionService!.loadModel();

      if (!modelLoaded) {
        if (mounted) {
          setState(() {
            _statusText = 'Error cargando modelo';
            _statusColor = Colors.red;
          });
        }
        return;
      }

      // Inicializar DetectionLogic
      _detectionLogic = DetectionLogic();

      // Obtener cámaras disponibles
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        if (mounted) {
          setState(() {
            _statusText = 'No hay cámara disponible';
            _statusColor = Colors.red;
          });
        }
        return;
      }

      // Usar la cámara frontal si está disponible, sino la trasera
      final camera = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );

      _cameraController = CameraController(
        camera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _cameraController!.initialize();

      // Iniciar procesamiento de frames
      _startFrameProcessing();

      if (mounted) {
        setState(() {
          _isInitialized = true;
          _statusText = 'APTO';
          _statusColor = Colors.green;
        });
      }
    } catch (e) {
      print('✗ Error inicializando: $e');
      if (mounted) {
        setState(() {
          _statusText = 'Error: $e';
          _statusColor = Colors.red;
        });
      }
    }
  }

  /// Inicializar sin cámara (para Web o cuando no hay cámara disponible)
  void _initializeWithoutCamera() {
    try {
      // Inicializar TFLite/Demo Service
      _detectionService = DetectionServiceFactory.createDetectionService();
      _detectionService!.loadModel().then((loaded) {
        if (loaded) {
          // Inicializar DetectionLogic
          _detectionLogic = DetectionLogic();

          // Iniciar procesamiento simulado (en Web)
          _startSimulatedDetection();

          if (mounted) {
            setState(() {
              _isInitialized = true;
              _statusText = 'APTO';
              _statusColor = Colors.green;
            });
          }
        } else {
          if (mounted) {
            setState(() {
              _statusText = 'Error cargando modelo';
              _statusColor = Colors.red;
            });
          }
        }
      });
    } catch (e) {
      print('✗ Error inicializando sin cámara: $e');
      if (mounted) {
        setState(() {
          _statusText = 'Error: $e';
          _statusColor = Colors.red;
        });
      }
    }
  }

  /// Simulación de detección (para Web/Demo)
  void _startSimulatedDetection() {
    _processingTimer = Timer.periodic(
      Duration(milliseconds: _processingIntervalMs),
      (_) async {
        if (!_isProcessing && _detectionService != null && _detectionLogic != null) {
          _simulateDetection();
        }
      },
    );
  }

  /// Simular detección (para demostración en Web)
  void _simulateDetection() async {
    if (_isProcessing || _detectionService == null || _detectionLogic == null) {
      return;
    }

    _isProcessing = true;

    try {
      // Simular inferencia
      final results = await _detectionService!.detectObjects([]);

      // Filtrar por confianza
      final filtered =
          _detectionService!.filterByConfidence(results, threshold: 0.7);

      if (filtered.isNotEmpty) {
        // Agregar objetos detectados
        for (final result in filtered) {
          _detectionLogic!.addDetectedObject(result.label);
        }

        // Obtener mayor confianza
        if (filtered.isNotEmpty) {
          _confidence = filtered.first.confidence;
        }

        // Actualizar UI
        if (mounted) {
          setState(() {
            _detectedObjects = _detectionLogic!.getDetectedObjectsNames();
            _missingObjects = _detectionLogic!.getMissingObjectsNames();
            _statusText = _detectionLogic!.getStatus();
            _statusColor =
                _detectionLogic!.isApto() ? Colors.green : Colors.red;
          });
        }
      }
    } catch (e) {
      print('✗ Error en simulación: $e');
    } finally {
      _isProcessing = false;
    }
  }

  void _startFrameProcessing() {
    // Procesar frames periódicamente
    _processingTimer = Timer.periodic(
      Duration(milliseconds: _processingIntervalMs),
      (_) async {
        if (!_isProcessing && _cameraController != null && _cameraController!.value.isInitialized) {
          await _processFrame();
        }
      },
    );
  }

  Future<void> _processFrame() async {
    if (_isProcessing || _detectionService == null || _detectionLogic == null) {
      return;
    }

    _isProcessing = true;

    try {
      // Capturar imagen actual
      final image = await _cameraController!.takePicture();
      final imageBytes = await image.readAsBytes();

      // Ejecutar detección
      final results = await _detectionService!.detectObjects(imageBytes.toList());

      // Filtrar por confianza > 0.7
      final filtered = _detectionService!.filterByConfidence(results, threshold: 0.7);

      if (filtered.isNotEmpty) {
        // Agregar objetos detectados a la lógica
        for (final result in filtered) {
          _detectionLogic!.addDetectedObject(result.label);
        }

        // Obtener mayor confianza
        if (filtered.isNotEmpty) {
          _confidence = filtered.first.confidence;
        }

        // Actualizar UI
        if (mounted) {
          setState(() {
            _detectedObjects = _detectionLogic!.getDetectedObjectsNames();
            _missingObjects = _detectionLogic!.getMissingObjectsNames();
            _statusText = _detectionLogic!.getStatus();
            _statusColor = _detectionLogic!.isApto() ? Colors.green : Colors.red;
          });
        }
      }
    } catch (e) {
      print('✗ Error procesando frame: $e');
    } finally {
      _isProcessing = false;
    }
  }

  void _resetDetection() {
    _detectionLogic?.reset();
    setState(() {
      _detectedObjects = [];
      _missingObjects = DetectionLogic.requiredObjects
          .map((label) => DetectionLogic.getLabelName(label))
          .toList()
        ..sort();
      _statusText = 'APTO';
      _statusColor = Colors.green;
      _confidence = 0.0;
    });
  }

  @override
  void dispose() {
    _processingTimer?.cancel();
    _cameraController?.dispose();
    _detectionService?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detector de Equipo de Seguridad'),
        elevation: 0,
        backgroundColor: Colors.blueAccent,
      ),
      body: !_isInitialized
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 20),
                  Text(
                    _statusText,
                    style: const TextStyle(fontSize: 16),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            )
          : Column(
              children: [
                // Vista de cámara o placeholder
                Expanded(
                  flex: 3,
                  child: _cameraController != null &&
                          _cameraController!.value.isInitialized
                      ? CameraPreview(_cameraController!)
                      : Container(
                          color: Colors.grey[800],
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.camera_alt,
                                size: 80,
                                color: Colors.grey[600],
                              ),
                              const SizedBox(height: 16),
                              Text(
                                kIsWeb
                                    ? '📸 Modo Demo (Web)\nCámara no disponible en navegador'
                                    : '📸 Cámara no disponible',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.grey[400],
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                        ),
                ),
                // Indicador de estado
                Container(
                  padding: const EdgeInsets.all(16),
                  color: _statusColor.withOpacity(0.1),
                  child: Column(
                    children: [
                      Text(
                        _statusText,
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: _statusColor,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Completitud: ${_detectionLogic?.getCompletenessPercentage().toStringAsFixed(1) ?? 0}%',
                        style: const TextStyle(fontSize: 14),
                      ),
                    ],
                  ),
                ),
                // Panel de resultados
                Expanded(
                  flex: 2,
                  child: SingleChildScrollView(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Objetos detectados
                          if (_detectedObjects.isNotEmpty) ...[
                            const Text(
                              '✓ Detectados:',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Colors.green,
                              ),
                            ),
                            const SizedBox(height: 8),
                            ..._detectedObjects.map((obj) => Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 4),
                                  child: Row(
                                    children: [
                                      const Icon(Icons.check_circle,
                                          color: Colors.green, size: 18),
                                      const SizedBox(width: 8),
                                      Text(obj),
                                    ],
                                  ),
                                )),
                            const SizedBox(height: 16),
                          ],
                          // Objetos faltantes
                          if (_missingObjects.isNotEmpty) ...[
                            const Text(
                              '✗ Faltantes:',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Colors.red,
                              ),
                            ),
                            const SizedBox(height: 8),
                            ..._missingObjects.map((obj) => Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 4),
                                  child: Row(
                                    children: [
                                      const Icon(Icons.cancel,
                                          color: Colors.red, size: 18),
                                      const SizedBox(width: 8),
                                      Text(obj),
                                    ],
                                  ),
                                )),
                          ],
                          // Mensaje si está completo
                          if (_detectedObjects.length ==
                              DetectionLogic.requiredObjects.length) ...[
                            const SizedBox(height: 16),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(8),
                                border:
                                    Border.all(color: Colors.green, width: 2),
                              ),
                              child: const Text(
                                '¡Todo el equipo está completo!',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
                // Botones de acción
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _resetDetection,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Reiniciar'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.orange,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

}

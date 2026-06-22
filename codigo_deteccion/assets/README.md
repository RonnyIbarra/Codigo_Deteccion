# Assets del Proyecto

## Archivos necesarios en esta carpeta:

1. **model.tflite** - Modelo TensorFlow Lite entrenado en Teachable Machine
   - Debe colocarse en esta carpeta antes de ejecutar la app
   - Tamaño típico: 1-5 MB

2. **labels.txt** - Archivo de etiquetas (ya incluido)
   - Contiene las 8 clases de equipo de seguridad
   - Formato: una clase por línea
   - Orden: 0_casco, 1_chaleco, 2_gafas, 3_buff, 4_pistola, 5_arma_principal, 6_botas, 7_uniforme_militar

## Pasos para completar:

1. Exporta tu modelo desde Teachable Machine como TFLite
2. Descarga el archivo model.tflite
3. Colócalo en esta carpeta (assets/)
4. Ejecuta: `flutter pub get`
5. Ejecuta: `flutter run`

# 🚀 USAR MODELO REAL ENTRENADO

## **Paso 1: Instalar dependencias Python**

```bash
pip install flask tensorflow pillow numpy
```

---

## **Paso 2: Copiar el servidor a la raíz del proyecto**

El archivo `servidor_tflite.py` debe estar en:
```
C:\Users\Usuario\Documents\Codigo Deteccion\codigo_deteccion\
```

---

## **Paso 3: Ejecutar el servidor**

```bash
python servidor_tflite.py
```

**Deberías ver:**
```
✓ Modelo cargado: assets/model.tflite
✓ Labels cargados: 8 clases
✓ Servidor iniciado en http://localhost:5000
```

---

## **Paso 4: Ejecutar la app Flutter**

En otra terminal, ejecuta el APK:

### **En Android Emulador:**
```bash
flutter run -d emulator-5554 build/app/outputs/flutter-apk/app-release.apk
```

### **En dispositivo físico:**
```bash
flutter run build/app/outputs/flutter-apk/app-release.apk
```

---

## **Paso 5: La app se conectará automáticamente**

La app:
1. ✅ Detectará el servidor en `http://10.0.2.2:5000` (emulador)
2. ✅ Enviará imágenes de la cámara
3. ✅ Recibirá predicciones del modelo REAL
4. ✅ Mostrará: APTO / NO APTO con los objetos detectados

---

## ⚠️ **Si usas dispositivo FÍSICO**

Cambia en `lib/tflite_detection_service.dart`:

```dart
// De:
static const String _serverUrl = 'http://10.0.2.2:5000';

// A:
static const String _serverUrl = 'http://TU_IP_PC:5000';
```

Reemplaza `TU_IP_PC` con tu IP (ej: `192.168.1.100`)

Obtén tu IP con:
```bash
ipconfig
```

---

## 📊 **Prueba rápida del servidor**

```bash
curl http://localhost:5000/health
```

**Resultado esperado:**
```json
{"status": "ok", "model_loaded": true}
```

---

## ✅ **¡Listo!**

Tu app ahora usa el **MODELO REAL ENTRENADO** 🎉

- ✅ Detecta 8 clases de equipo de seguridad
- ✅ Muestra estado APTO/NO APTO
- ✅ Lista objetos detectados y faltantes
- ✅ Funciona en Android, Web, Windows

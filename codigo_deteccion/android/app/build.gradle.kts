plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.example.codigo_deteccion"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    // Resolver conflictos de namespaces en TensorFlow Lite
    packagingOptions {
        exclude("**/AndroidManifest.xml")
        resources {
            excludes += "META-INF/proguard/androidx-*.pro"
            excludes += "DebugProbesKt.bin"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.example.codigo_deteccion"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_1_8
    }
}

flutter {
    source = "../.."
}

dependencies {
    // Forzar una sola versión de TensorFlow Lite (resolver conflictos)
    constraints {
        implementation("org.tensorflow:tensorflow-lite:2.12.0")
    }
}

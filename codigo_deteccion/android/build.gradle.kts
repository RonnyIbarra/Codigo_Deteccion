allprojects {
    repositories {
        google()
        mavenCentral()
    }

    // Resolver conflictos de TensorFlow Lite
    configurations.all {
        resolutionStrategy {
            force("org.tensorflow:tensorflow-lite:2.12.0")

            // Excluir versiones conflictivas
            exclude(group = "org.tensorflow", module = "tensorflow-lite-gpu")
            exclude(group = "org.tensorflow", module = "tensorflow-lite-api")
        }
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    project.evaluationDependsOn(":app")

    // Forzar JVM 1.8 para todas las dependencias (estándar Android)
    tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
        compilerOptions {
            jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_1_8)
        }
    }

    // También forzar en tareas Java
    tasks.withType<JavaCompile>().configureEach {
        sourceCompatibility = "1.8"
        targetCompatibility = "1.8"
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}

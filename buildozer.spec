[app]

# Nombre visible de la app
title = Visual Tagger

# Nombre interno del paquete (sin espacios ni símbolos)
package.name = visualtagger

# Dominio ficticio o real
package.domain = org.ignacio.visual

# Directorio fuente (donde está main.py)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Archivos o carpetas que no deben incluirse
source.exclude_dirs = bin,build,__pycache__

# Módulos de Python necesarios
requirements = python3,kivy,opencv-python,numpy,plyer

# Versión de tu app
version = 0.1

# Orientación de pantalla
orientation = portrait

# Mostrar en pantalla completa
fullscreen = 0

# Ícono personalizado
icon.filename = icon.png

# Permisos necesarios para Android
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# Exportación segura (requerido para compartir archivos)
android.allow_backup = True
android.exported = True

# Dependencia extra opcional (evita errores de ciertas funciones de archivos)
android.gradle_dependencies = implementation 'org.apache.commons:commons-io:1.3.2'

# Nivel mínimo de Android soportado
android.minapi = 21

# API de compilación de Android (estable)
android.api = 31

# Versión del NDK compatible
android.ndk = 23b

# Arquitecturas compatibles
android.archs = arm64-v8a, armeabi-v7a

# Desactivar comportamiento problemático en algunas versiones
android.disable_antigravity = 1

# Punto de entrada
entrypoint = main.py

# Tema visual de la app (sin barra de título)
android.theme = @android:style/Theme.NoTitleBar

[buildozer]

# Nivel de salida: 2 = info, 1 = debug, 0 = solo advertencias
log_level = 2

# Evitar errores al compilar como root
warn_on_root = 1

# Limpieza de versiones anteriores
# (útil si tienes problemas de compilación)
# buildozer android clean

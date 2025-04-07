[app]
# Nombre visible de la aplicación
title = Visual Tagger

# Nombre interno del paquete (sin espacios ni caracteres especiales)
package.name = visualtagger

# Dominio del paquete (puede ser ficticio)
package.domain = org.tudominio.visualtagger

# Directorio fuente (donde se encuentra main.py)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin,build,__pycache__

# Dependencias (módulos de Python necesarios)
requirements = python3,kivy,opencv-python,numpy,plyer

# Versión de la aplicación
version = 0.1

# Orientación y modo de pantalla
orientation = portrait
fullscreen = 0

# Ícono de la aplicación (archivo icon.png en la raíz)
icon.filename = icon.png

# Permisos necesarios en Android
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# Configuraciones adicionales de Android
android.allow_backup = True
android.exported = True
android.gradle_dependencies = implementation 'org.apache.commons:commons-io:1.3.2'
android.minapi = 21
android.api = 31
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a
android.disable_antigravity = 1
entrypoint = main.py
android.theme = @android:style/Theme.NoTitleBar

# Fuerza el uso de build-tools 31.0.0 (las cuales incluyen Aidl)
android.build_tools_version = 31.0.0

# Acepta automáticamente las licencias del SDK de Android
android.accept_sdk_license = True

[buildozer]
# Nivel de log: 2 = info, 1 = debug
log_level = 2

# Evita la compilación como root
warn_on_root = 1

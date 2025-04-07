[app]
title = Visual Tagger
package.name = visualtagger
package.domain = org.tudominio.visualtagger
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin,build,__pycache__
requirements = python3,kivy,opencv-python,numpy,plyer
version = 0.1
orientation = portrait
fullscreen = 0
icon.filename = icon.png
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.allow_backup = True
android.exported = True
android.gradle_dependencies = implementation 'org.apache.commons:commons-io:1.3.2'
android.minapi = 21
android.api = 31
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.disable_antigravity = 1
entrypoint = main.py
android.theme = @android:style/Theme.NoTitleBar
android.build_tools_version = 31.0.0
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

[app]
title = MTabs WebView
package.name = minimalist_tabs_webview
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

# Requirements yang minimal tapi cukup untuk WebView
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pyjnius

# Orientasi default
orientation = portrait

# Permission yang diperlukan
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE

# Konfigurasi Android
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.gradle_dependencies = androidx.webkit:webkit:1.4.0

# Architecture yang didukung
android.archs = arm64-v8a, armeabi-v7a

# Tambahan konfigurasi untuk optimasi
android.allow_backup = True
android.presplash_color = #FFFFFF
android.presplash.filename = icon.png
android.icon.filename = icon.png

android.private_storage = True

# Build options
android.build_mode = debug

[buildozer]
log_level = 2
warn_on_root = 1

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

# Konfigurasi Android yang sesuai dengan Termux
android.api = 33
android.minapi = 21
#android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True

# Architecture yang didukung
android.archs = arm64-v8a, armeabi-v7a

# Tambahan konfigurasi untuk optimasi
android.allow_backup = True
android.presplash_color = #FFFFFF
android.presplash.filename = icon.png  # Logo yang akan ditampilkan di splash

# Icon aplikasi
android.icon.filename = icon.png

# Pastikan assets masuk ke build (khusus jika menggunakan struktur yg terdapat folder asset)
#source.include_patterns = assets/*
android.private_storage = True

# Log level untuk debugging
[buildozer]
log_level = 2
warn_on_root = 1

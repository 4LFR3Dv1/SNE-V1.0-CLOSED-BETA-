#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versão de debug do sne_desktop.py para diagnosticar problemas
"""
import os
import sys
import threading
import time
from pathlib import Path

print("=" * 60)
print("🔍 MODO DEBUG - SNE RADAR Desktop")
print("=" * 60)

# Verificar pywebview
try:
    import webview
    print(f"✅ pywebview importado: {webview.__version__ if hasattr(webview, '__version__') else 'versão desconhecida'}")
except ImportError as e:
    print(f"❌ Erro ao importar pywebview: {e}")
    sys.exit(1)

# Verificar plataforma
import platform
print(f"🖥️  Plataforma: {platform.system()} {platform.release()}")
print(f"🐍 Python: {sys.version}")

# Verificar se está em modo bundle
if getattr(sys, 'frozen', False):
    print("📦 Modo: BUNDLE (executável compilado)")
    print(f"   Executável: {sys.executable}")
    if hasattr(sys, '_MEIPASS'):
        print(f"   _MEIPASS: {sys._MEIPASS}")
else:
    print("📦 Modo: DESENVOLVIMENTO (script Python)")

# Testar criação de janela simples
print("\n🧪 Testando criação de janela simples...")
try:
    def test_window():
        window = webview.create_window(
            title='Teste SNE RADAR',
            url='http://127.0.0.1:9999',
            width=800,
            height=600
        )
        print("✅ Janela de teste criada")
        return window
    
    window = test_window()
    print("✅ Função de criação de janela funcionou")
    
    # Testar webview.start() com timeout
    print("\n🧪 Testando webview.start() (vai abrir janela por 5 segundos)...")
    print("💡 Se a janela aparecer, o problema não é com pywebview")
    
    def close_after_delay():
        time.sleep(5)
        try:
            webview.windows[0].destroy()
        except:
            pass
    
    timer = threading.Timer(5.0, close_after_delay)
    timer.start()
    
    webview.start(debug=True)
    timer.cancel()
    
    print("✅ webview.start() funcionou!")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Diagnóstico:")
    print("   1. Se o erro for sobre 'NSApplication', pode ser problema de thread")
    print("   2. Se o erro for sobre permissões, execute: xattr -dr com.apple.quarantine")
    print("   3. Se não houver erro mas janela não abrir, pode ser problema do macOS")

print("\n" + "=" * 60)



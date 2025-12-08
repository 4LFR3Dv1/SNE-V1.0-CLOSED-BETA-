#!/usr/bin/env python3
# Teste simples de webview para verificar se funciona

import webview
import time
import sys
import platform

print("🧪 Teste de Webview")
print(f"Python: {sys.version}")
print(f"Platform: {platform.system()}")

if platform.system() == 'Darwin':
    try:
        import AppKit
        app = AppKit.NSApplication.sharedApplication()
        app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
        app.activateIgnoringOtherApps_(True)
        print("✅ NSApplication inicializado")
        time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Erro NSApplication: {e}")

print("🔄 Criando janela...")
window = webview.create_window(
    'Teste Webview',
    'https://www.google.com',
    width=800,
    height=600
)

print("✅ Janela criada")
print("🚀 Iniciando webview...")
print("💡 A janela deve aparecer agora")

try:
    webview.start(debug=True)
    print("✅ Webview retornou")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()




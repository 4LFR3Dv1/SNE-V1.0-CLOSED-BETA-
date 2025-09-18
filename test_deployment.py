#!/usr/bin/env python3
"""
Script de teste para verificar se todas as funcionalidades estão funcionando
após o deploy no Render.
"""

import requests
import json
import time
import sys

def test_endpoint(url, expected_status=200, description=""):
    """Testa um endpoint e retorna o resultado"""
    try:
        response = requests.get(url, timeout=10)
        status = "✅" if response.status_code == expected_status else "❌"
        print(f"{status} {description}: {response.status_code}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ {description}: Erro - {str(e)}")
        return False

def test_post_endpoint(url, data, expected_status=200, description=""):
    """Testa um endpoint POST e retorna o resultado"""
    try:
        response = requests.post(url, json=data, timeout=10)
        status = "✅" if response.status_code == expected_status else "❌"
        print(f"{status} {description}: {response.status_code}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ {description}: Erro - {str(e)}")
        return False

def main():
    print("🚀 Testando deploy do SNE RADAR...")
    print("=" * 50)
    
    # URL base - substitua pela URL do seu deploy no Render
    base_url = "https://sne-radar.onrender.com"  # Ajuste conforme necessário
    
    # Lista de testes
    tests = [
        # Endpoints básicos
        (f"{base_url}/", 200, "Página principal"),
        (f"{base_url}/health", 200, "Health check"),
        (f"{base_url}/ready", 200, "Ready check"),
        
        # Endpoints de API (sem autenticação)
        (f"{base_url}/api/v1/ta-summary?symbol=BTCUSDT", 200, "TA Summary"),
        (f"{base_url}/api/v1/global-metrics", 200, "Global Metrics"),
        (f"{base_url}/api/v1/derivatives?symbol=BTCUSDT", 200, "Derivatives"),
        (f"{base_url}/api/v1/listings?tag=all&limit=10", 200, "Listings"),
        (f"{base_url}/api/v1/candles?symbol=BTCUSDT&interval=1m&limit=100", 200, "Candles"),
        
        # Endpoints de indicadores
        (f"{base_url}/api/v1/advanced-indicators?symbol=BTCUSDT", 200, "Advanced Indicators"),
        (f"{base_url}/api/v1/professional-indicators?symbol=BTCUSDT", 200, "Professional Indicators"),
        
        # Endpoints de ML (sem autenticação para teste)
        (f"{base_url}/api/v1/ml/performance", 200, "ML Performance"),
    ]
    
    # Executar testes
    passed = 0
    total = len(tests)
    
    for url, expected_status, description in tests:
        if test_endpoint(url, expected_status, description):
            passed += 1
        time.sleep(1)  # Pausa entre testes
    
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Deploy funcionando perfeitamente.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs do Render.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

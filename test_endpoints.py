#!/usr/bin/env python3
"""
Script para testar endpoints do SNE Radar
"""

import requests
import json
import time

def test_endpoint(url, description):
    """Testa um endpoint específico"""
    try:
        print(f"\n🔍 Testando: {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Dados: {json.dumps(data, indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📝 Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Erro: Não foi possível conectar ao servidor")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    base_url = "http://localhost:5000"
    
    print("🚀 Testando endpoints do SNE Radar")
    print("=" * 50)
    
    # Testar endpoints básicos
    endpoints = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/api/v1/candles?symbol=BTCUSDT&interval=1m&limit=10", "Candles"),
        (f"{base_url}/api/v1/derivatives?symbol=BTCUSDT", "Derivatives"),
        (f"{base_url}/api/v1/global-metrics", "Global Metrics"),
        (f"{base_url}/api/v1/advanced-indicators?symbol=BTCUSDT&interval=1m&limit=100", "Advanced Indicators"),
        (f"{base_url}/api/v1/professional-indicators?symbol=BTCUSDT&interval=1m&limit=100", "Professional Indicators"),
    ]
    
    results = []
    for url, description in endpoints:
        result = test_endpoint(url, description)
        results.append((description, result))
        time.sleep(1)  # Pausa entre testes
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    success_count = 0
    for description, result in results:
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{status} {description}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Resultado: {success_count}/{len(results)} endpoints funcionando")
    
    if success_count == len(results):
        print("🎉 Todos os endpoints estão funcionando!")
    else:
        print("⚠️ Alguns endpoints falharam. Verifique os logs do servidor.")

if __name__ == "__main__":
    main()



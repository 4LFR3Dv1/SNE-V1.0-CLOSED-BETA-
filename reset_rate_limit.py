#!/usr/bin/env python3
"""
Script para resetar rate limits do Flask-Limiter
Útil durante desenvolvimento
"""
import requests
import time

BASE_URL = "http://localhost:9999"

def reset_circuit_breaker():
    """Reseta o circuit breaker do sistema"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/system/reset-circuit-breaker")
        print(f"✅ Circuit breaker resetado: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao resetar circuit breaker: {e}")

if __name__ == "__main__":
    print("🔄 Resetando rate limits...")
    reset_circuit_breaker()
    print("✅ Concluído!")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se todas as integrações estão funcionando
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_api_endpoints():
    """Verifica se todos os endpoints estão funcionando"""
    print("🔗 Verificando endpoints de API...")
    
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    endpoints = [
        '/api/v1/ta-summary',
        '/api/v1/global-metrics',
        '/api/v1/derivatives',
        '/api/v1/listings',
        '/api/v1/candles',
        '/api/v1/advanced-indicators',
        '/api/v1/professional-indicators',
        '/api/v1/system/status'
    ]
    
    working_endpoints = []
    failed_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403 são aceitáveis (auth required)
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint}: OK")
            else:
                failed_endpoints.append(endpoint)
                print(f"❌ {endpoint}: Status {response.status_code}")
        except Exception as e:
            failed_endpoints.append(endpoint)
            print(f"❌ {endpoint}: {e}")
    
    print(f"\n📊 Resultado: {len(working_endpoints)}/{len(endpoints)} endpoints funcionando")
    return len(failed_endpoints) == 0

def check_services():
    """Verifica se todos os serviços podem ser importados"""
    print("\n📦 Verificando serviços...")
    
    services = [
        'services.ta_summary',
        'services.advanced_indicators',
        'services.professional_indicators',
        'services.ml_predictions',
        'services.advanced_backtesting',
        'services.alert_system',
        'services.export_system'
    ]
    
    working_services = []
    failed_services = []
    
    for service in services:
        try:
            __import__(service)
            working_services.append(service)
            print(f"✅ {service}")
        except ImportError as e:
            failed_services.append(service)
            print(f"❌ {service}: {e}")
    
    print(f"\n📊 Resultado: {len(working_services)}/{len(services)} serviços funcionando")
    return len(failed_services) == 0

def check_integrations():
    """Verifica se as integrações externas estão funcionando"""
    print("\n🌐 Verificando integrações externas...")
    
    integrations = [
        ('CoinGlass', 'integrations.coinglass'),
        ('CoinMarketCap', 'integrations.cmc')
    ]
    
    working_integrations = []
    failed_integrations = []
    
    for name, module in integrations:
        try:
            __import__(module)
            working_integrations.append(name)
            print(f"✅ {name}")
        except ImportError as e:
            failed_integrations.append(name)
            print(f"❌ {name}: {e}")
    
    print(f"\n📊 Resultado: {len(working_integrations)}/{len(integrations)} integrações funcionando")
    return len(failed_integrations) == 0

def check_feature_flags():
    """Verifica se as feature flags estão configuradas corretamente"""
    print("\n🚩 Verificando feature flags...")
    
    from config import Settings as C
    
    flags = [
        ('ENABLE_COINGLASS', C.ENABLE_COINGLASS),
        ('ENABLE_CMC', C.ENABLE_CMC),
        ('ENABLE_TA_SUMMARY', C.ENABLE_TA_SUMMARY)
    ]
    
    enabled_flags = []
    disabled_flags = []
    
    for flag_name, flag_value in flags:
        if flag_value:
            enabled_flags.append(flag_name)
            print(f"✅ {flag_name}: Habilitado")
        else:
            disabled_flags.append(flag_name)
            print(f"❌ {flag_name}: Desabilitado")
    
    print(f"\n📊 Resultado: {len(enabled_flags)}/{len(flags)} flags habilitadas")
    return len(disabled_flags) == 0

def check_database_connection():
    """Verifica se a conexão com banco está funcionando"""
    print("\n🗄️ Verificando conexão com banco...")
    
    try:
        from database_config import test_connection, print_config_status
        print_config_status()
        
        # Testar conexão local
        local_ok = test_connection('local')
        print(f"SQLite: {'✅ OK' if local_ok else '❌ Falha'}")
        
        # Testar conexão de produção
        prod_ok = test_connection('production')
        print(f"PostgreSQL: {'✅ OK' if prod_ok else '❌ Falha'}")
        
        return local_ok or prod_ok
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def check_web_app():
    """Verifica se a aplicação web está funcionando"""
    print("\n🌐 Verificando aplicação web...")
    
    try:
        import sne_radar_web
        
        # Verificar se a app Flask foi criada
        if hasattr(sne_radar_web, 'app'):
            print("✅ App Flask criada com sucesso")
            
            # Verificar se os blueprints estão registrados
            if hasattr(sne_radar_web.app, 'blueprints'):
                print(f"✅ {len(sne_radar_web.app.blueprints)} blueprints registrados")
            
            return True
        else:
            print("❌ App Flask não encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar aplicação web: {e}")
        return False

def main():
    """Função principal de verificação"""
    print("🔍 VERIFICAÇÃO DE INTEGRAÇÕES SNE RADAR")
    print("=" * 50)
    
    checks = [
        ("Serviços", check_services),
        ("Integrações Externas", check_integrations),
        ("Feature Flags", check_feature_flags),
        ("Conexão com Banco", check_database_connection),
        ("Aplicação Web", check_web_app),
        ("Endpoints de API", check_api_endpoints)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {check_name}: {e}")
            results.append((check_name, False))
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("\n🎉 TODAS AS INTEGRAÇÕES ESTÃO FUNCIONANDO!")
        print("\n📋 Sua aplicação está completamente integrada e pronta para uso!")
    else:
        print(f"\n⚠️ {total - passed} problemas encontrados.")
        print("Consulte os logs acima para resolver os problemas.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





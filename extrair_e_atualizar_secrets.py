#!/usr/bin/env python3
"""
Script para extrair secrets dos arquivos do sistema e atualizar no GCP Secret Manager
"""

import os
import sys
import re
import subprocess
from pathlib import Path

def extract_telegram_token():
    """Extrai Telegram Token dos arquivos"""
    # Tentar config_seguro.py primeiro
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config_seguro import config
        token = config.TELEGRAM_TOKEN
        if token and token != "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y":  # Não usar default
            return token
    except:
        pass
    
    # Tentar xenos_bot.py
    xenos_path = Path(__file__).parent / "xenos_bot.py"
    if xenos_path.exists():
        content = xenos_path.read_text()
        # Procurar padrão TELEGRAM_TOKEN = "..."
        match = re.search(r'TELEGRAM_TOKEN\s*=\s*"([^"]+)"', content)
        if match:
            token = match.group(1)
            if token and len(token) > 20:  # Validar formato
                return token
    
    # Fallback: usar o valor hardcoded encontrado
    return "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y"

def extract_chat_id():
    """Extrai Chat ID dos arquivos"""
    # Tentar config_seguro.py primeiro
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config_seguro import config
        chat_id = config.TELEGRAM_CHAT_ID
        if chat_id and chat_id != "6457067653":  # Não usar default se vier de env
            return chat_id
    except:
        pass
    
    # Tentar xenos_bot.py
    xenos_path = Path(__file__).parent / "xenos_bot.py"
    if xenos_path.exists():
        content = xenos_path.read_text()
        # Procurar padrão CHAT_ID = "..."
        match = re.search(r'CHAT_ID\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    
    # Fallback
    return "6457067653"

def extract_binance_keys():
    """Extrai chaves Binance dos arquivos"""
    api_key = None
    secret_key = None
    
    # Procurar em arquivos .env ou config
    for pattern in ["*.env*", "config*.py", "*.txt"]:
        for file_path in Path(__file__).parent.glob(pattern):
            try:
                content = file_path.read_text()
                # Procurar BINANCE_API_KEY
                if not api_key:
                    match = re.search(r'BINANCE_API_KEY\s*[=:]\s*["\']?([^"\'\s]+)', content, re.IGNORECASE)
                    if match and match.group(1) not in ["your_binance_api_key", "None", ""]:
                        api_key = match.group(1)
                
                # Procurar BINANCE_SECRET_KEY
                if not secret_key:
                    match = re.search(r'BINANCE_SECRET_KEY\s*[=:]\s*["\']?([^"\'\s]+)', content, re.IGNORECASE)
                    if match and match.group(1) not in ["your_binance_secret_key", "None", ""]:
                        secret_key = match.group(1)
            except:
                continue
    
    return api_key, secret_key

def update_secret(secret_name, value, project_id):
    """Atualiza secret no GCP"""
    if not value:
        print(f"⚠️  Valor vazio para {secret_name}, pulando...")
        return False
    
    try:
        cmd = [
            "gcloud", "secrets", "versions", "add", secret_name,
            "--data-file=-",
            f"--project={project_id}"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=value)
        
        if process.returncode == 0:
            print(f"✅ {secret_name} atualizado com sucesso")
            return True
        else:
            print(f"⚠️  Erro ao atualizar {secret_name}: {stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar {secret_name}: {e}")
        return False

def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else "sne-v1"
    
    print("🔍 Extraindo secrets dos arquivos do sistema...")
    print(f"Projeto: {project_id}")
    print("")
    
    # Extrair secrets
    telegram_token = extract_telegram_token()
    chat_id = extract_chat_id()
    binance_api_key, binance_secret_key = extract_binance_keys()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📋 Secrets encontrados:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Telegram Token: {telegram_token[:20]}...")
    print(f"Chat ID: {chat_id}")
    if binance_api_key:
        print(f"Binance API Key: {binance_api_key[:20]}...")
    else:
        print("Binance API Key: Não encontrada")
    if binance_secret_key:
        print(f"Binance Secret Key: {binance_secret_key[:20]}...")
    else:
        print("Binance Secret Key: Não encontrada")
    print("")
    
    # Confirmar
    response = input("Deseja atualizar esses secrets no GCP? (y/n): ")
    if response.lower() != 'y':
        print("Cancelado.")
        return
    
    print("")
    print("📤 Atualizando secrets...")
    print("")
    
    # Atualizar secrets
    success_count = 0
    
    if telegram_token:
        if update_secret("sne-telegram-bot-token", telegram_token, project_id):
            success_count += 1
    
    if chat_id:
        if update_secret("sne-telegram-chat-id", chat_id, project_id):
            success_count += 1
    
    if binance_api_key:
        if update_secret("sne-binance-api-key", binance_api_key, project_id):
            success_count += 1
    
    if binance_secret_key:
        if update_secret("sne-binance-secret-key", binance_secret_key, project_id):
            success_count += 1
    
    print("")
    print(f"✅ {success_count} secrets atualizados com sucesso!")
    print("")
    print("📋 Verificar:")
    print(f"  gcloud secrets list --project={project_id}")

if __name__ == "__main__":
    main()




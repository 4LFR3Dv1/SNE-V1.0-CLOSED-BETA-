#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Licenças
Valida licença do usuário antes de executar o software
"""
import os
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

class LicenseManager:
    """
    Gerenciador de licenças para proteção de IP
    """
    
    def __init__(self, app_name: str = "SNE_RADAR"):
        """
        Inicializa gerenciador de licenças
        
        Args:
            app_name: Nome da aplicação
        """
        self.app_name = app_name
        self.license_dir = Path.home() / f'.{app_name.lower()}'
        self.license_file = self.license_dir / 'license.json'
        self.license_dir.mkdir(exist_ok=True)
    
    def generate_license_key(self, user_info: str = "") -> str:
        """
        Gera chave de licença (para uso interno)
        
        Args:
            user_info: Informações do usuário (email, nome, etc.)
        
        Returns:
            Chave de licença formatada
        """
        # Gerar hash baseado em informações
        seed = f"{user_info}{datetime.now().isoformat()}"
        hash_obj = hashlib.sha256(seed.encode())
        hash_hex = hash_obj.hexdigest()[:16].upper()
        
        # Formatar como XXXX-XXXX-XXXX-XXXX
        return f"{hash_hex[:4]}-{hash_hex[4:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}"
    
    def validate_license_format(self, license_key: str) -> bool:
        """
        Valida formato da chave de licença
        
        Args:
            license_key: Chave de licença
        
        Returns:
            True se formato válido
        """
        # Formato: XXXX-XXXX-XXXX-XXXX (16 caracteres alfanuméricos)
        parts = license_key.split('-')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if len(part) != 4 or not part.isalnum():
                return False
        
        return True
    
    def validate_license(self, license_key: str, days_valid: int = 365) -> bool:
        """
        Valida chave de licença e salva se válida
        
        Args:
            license_key: Chave de licença
            days_valid: Dias de validade (padrão: 365)
        
        Returns:
            True se licença válida
        """
        if not self.validate_license_format(license_key):
            return False
        
        # Aqui você pode adicionar validação adicional:
        # - Verificar contra servidor
        # - Verificar contra banco de dados
        # - Verificar hash/assinatura
        
        # Por enquanto, validação básica de formato
        self.save_license(license_key, days_valid)
        return True
    
    def check_license(self) -> bool:
        """
        Verifica se licença existe e é válida
        
        Returns:
            True se licença válida
        """
        if not self.license_file.exists():
            return False
        
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Verificar expiração
            if 'expires' in license_data:
                expires = datetime.fromisoformat(license_data['expires'])
                if datetime.now() > expires:
                    return False
            
            # Verificar formato da chave
            if 'key' not in license_data:
                return False
            
            return self.validate_license_format(license_data['key'])
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar licença: {e}")
            return False
    
    def save_license(self, license_key: str, days_valid: int = 365):
        """
        Salva licença no arquivo
        
        Args:
            license_key: Chave de licença
            days_valid: Dias de validade
        """
        license_data = {
            'key': license_key,
            'created': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(days=days_valid)).isoformat(),
            'app': self.app_name
        }
        
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f, indent=2)
    
    def get_license_info(self) -> Optional[Dict]:
        """
        Retorna informações da licença
        
        Returns:
            Dict com informações da licença ou None
        """
        if not self.license_file.exists():
            return None
        
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def require_license(self) -> bool:
        """
        Requer licença válida. Se não existir, pede ao usuário.
        
        Returns:
            True se licença válida, False caso contrário
        """
        if self.check_license():
            return True
        
        # Licença não encontrada ou inválida
        print("\n" + "="*60)
        print("🔐 LICENCIAMENTO REQUERIDO")
        print("="*60)
        print(f"\n{self.app_name} requer uma licença válida para uso.")
        print("\nDigite sua chave de licença (formato: XXXX-XXXX-XXXX-XXXX)")
        print("Ou pressione Enter para usar versão de demonstração (limitada)")
        
        license_key = input("\nChave de licença: ").strip()
        
        if not license_key:
            print("\n⚠️  Usando versão de demonstração (funcionalidades limitadas)")
            return False
        
        if self.validate_license(license_key):
            print("\n✅ Licença válida! Obrigado por usar SNE RADAR.")
            return True
        else:
            print("\n❌ Licença inválida. Verifique a chave e tente novamente.")
            return False


# Função de conveniência para uso no código
def check_license_or_exit():
    """
    Verifica licença e sai do programa se inválida
    """
    manager = LicenseManager()
    
    if not manager.require_license():
        print("\n❌ Licença requerida para uso completo do software.")
        print("Entre em contato para obter uma licença válida.")
        sys.exit(1)


if __name__ == "__main__":
    # Teste do gerenciador de licenças
    manager = LicenseManager()
    
    print("🔐 Teste do Gerenciador de Licenças")
    print("="*60)
    
    # Gerar licença de teste
    test_key = manager.generate_license_key("test@example.com")
    print(f"\nChave de teste gerada: {test_key}")
    
    # Validar
    if manager.validate_license(test_key):
        print("✅ Licença válida!")
    
    # Verificar
    if manager.check_license():
        print("✅ Licença encontrada e válida!")
        info = manager.get_license_info()
        if info:
            print(f"\nInformações da licença:")
            print(f"  Chave: {info['key']}")
            print(f"  Criada: {info['created']}")
            print(f"  Expira: {info['expires']}")



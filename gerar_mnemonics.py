#!/usr/bin/env python3
"""
Script para gerar mnemonics válidos (seed phrases BIP39)
Suporta geração de 12 ou 24 palavras
"""

import secrets
from mnemonic import Mnemonic
import sys


def gerar_mnemonic(num_palavras=12):
    """
    Gera um mnemonic válido com o número especificado de palavras.
    
    Args:
        num_palavras (int): Número de palavras (12 ou 24)
    
    Returns:
        str: Frase mnemônica válida
    """
    if num_palavras not in [12, 24]:
        raise ValueError("Número de palavras deve ser 12 ou 24")
    
    # Gera entropia aleatória
    # 12 palavras = 128 bits de entropia
    # 24 palavras = 256 bits de entropia
    entropia_bits = 128 if num_palavras == 12 else 256
    entropia_bytes = secrets.token_bytes(entropia_bits // 8)
    
    # Cria objeto Mnemonic
    mnemo = Mnemonic("english")
    
    # Gera o mnemonic
    mnemonic_phrase = mnemo.to_mnemonic(entropia_bytes)
    
    return mnemonic_phrase


def validar_mnemonic(frase):
    """
    Valida se uma frase mnemônica é válida.
    
    Args:
        frase (str): Frase mnemônica a ser validada
    
    Returns:
        bool: True se válida, False caso contrário
    """
    mnemo = Mnemonic("english")
    return mnemo.check(frase)


def gerar_multiplos_mnemonics(quantidade=1, num_palavras=12):
    """
    Gera múltiplos mnemonics válidos.
    
    Args:
        quantidade (int): Número de mnemonics a gerar
        num_palavras (int): Número de palavras por mnemonic (12 ou 24)
    
    Returns:
        list: Lista de frases mnemônicas
    """
    mnemonics = []
    for i in range(quantidade):
        mnemonic = gerar_mnemonic(num_palavras)
        mnemonics.append(mnemonic)
    return mnemonics


def main():
    """Função principal para uso interativo"""
    print("=" * 60)
    print("🔐 GERADOR DE MNEMONICS VÁLIDOS (BIP39)")
    print("=" * 60)
    print()
    
    # Menu interativo
    while True:
        print("Opções:")
        print("1. Gerar 1 mnemonic (12 palavras)")
        print("2. Gerar 1 mnemonic (24 palavras)")
        print("3. Gerar múltiplos mnemonics")
        print("4. Validar um mnemonic existente")
        print("5. Sair")
        print()
        
        escolha = input("Escolha uma opção (1-5): ").strip()
        
        if escolha == "1":
            mnemonic = gerar_mnemonic(12)
            print()
            print("✅ MNEMONIC GERADO (12 palavras):")
            print("-" * 60)
            print(mnemonic)
            print("-" * 60)
            print()
            
        elif escolha == "2":
            mnemonic = gerar_mnemonic(24)
            print()
            print("✅ MNEMONIC GERADO (24 palavras):")
            print("-" * 60)
            print(mnemonic)
            print("-" * 60)
            print()
            
        elif escolha == "3":
            try:
                quantidade = int(input("Quantos mnemonics deseja gerar? "))
                num_palavras = int(input("Número de palavras (12 ou 24)? "))
                
                if num_palavras not in [12, 24]:
                    print("❌ Erro: Número de palavras deve ser 12 ou 24")
                    continue
                
                print()
                print(f"✅ GERANDO {quantidade} MNEMONIC(S) DE {num_palavras} PALAVRAS:")
                print("=" * 60)
                
                mnemonics = gerar_multiplos_mnemonics(quantidade, num_palavras)
                for i, mnemonic in enumerate(mnemonics, 1):
                    print(f"\n[{i}] {mnemonic}")
                
                print()
                print("=" * 60)
                print()
                
            except ValueError:
                print("❌ Erro: Por favor, insira um número válido")
                
        elif escolha == "4":
            frase = input("Cole a frase mnemônica para validar: ").strip()
            if validar_mnemonic(frase):
                print()
                print("✅ MNEMONIC VÁLIDO!")
                print()
            else:
                print()
                print("❌ MNEMONIC INVÁLIDO!")
                print()
                
        elif escolha == "5":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
            print()


if __name__ == "__main__":
    # Modo de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uso:")
            print("  python gerar_mnemonics.py                    # Modo interativo")
            print("  python gerar_mnemonics.py --gerar 12         # Gerar 1 mnemonic de 12 palavras")
            print("  python gerar_mnemonics.py --gerar 24         # Gerar 1 mnemonic de 24 palavras")
            print("  python gerar_mnemonics.py --gerar 12 --qtd 5 # Gerar 5 mnemonics de 12 palavras")
            print("  python gerar_mnemonics.py --validar 'frase'  # Validar uma frase")
            sys.exit(0)
        
        elif sys.argv[1] == "--gerar":
            num_palavras = 12
            quantidade = 1
            
            if len(sys.argv) > 2:
                num_palavras = int(sys.argv[2])
            
            if "--qtd" in sys.argv:
                idx = sys.argv.index("--qtd")
                if idx + 1 < len(sys.argv):
                    quantidade = int(sys.argv[idx + 1])
            
            if num_palavras not in [12, 24]:
                print("❌ Erro: Número de palavras deve ser 12 ou 24")
                sys.exit(1)
            
            mnemonics = gerar_multiplos_mnemonics(quantidade, num_palavras)
            for mnemonic in mnemonics:
                print(mnemonic)
        
        elif sys.argv[1] == "--validar":
            if len(sys.argv) < 3:
                print("❌ Erro: Forneça uma frase para validar")
                sys.exit(1)
            
            frase = " ".join(sys.argv[2:])
            if validar_mnemonic(frase):
                print("✅ MNEMONIC VÁLIDO")
                sys.exit(0)
            else:
                print("❌ MNEMONIC INVÁLIDO")
                sys.exit(1)
    else:
        # Modo interativo
        main()





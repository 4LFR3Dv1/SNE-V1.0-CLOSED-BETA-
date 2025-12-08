#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTILITÁRIOS PARA TELEGRAM
Funções auxiliares para envio de mensagens ao Telegram
"""

def dividir_mensagem(texto, limite=3500):
    """
    Divide mensagem longa em partes menores para Telegram
    
    Args:
        texto: Texto a ser dividido
        limite: Limite de caracteres por parte (padrão: 3500)
    
    Returns:
        list: Lista de partes da mensagem
    """
    if len(texto) <= limite:
        return [texto]
    
    partes = []
    linhas = texto.split('\n')
    parte_atual = ""
    
    for linha in linhas:
        if len(parte_atual + linha + '\n') <= limite:
            parte_atual += linha + '\n'
        else:
            if parte_atual:
                partes.append(parte_atual.strip())
            parte_atual = linha + '\n'
    
    if parte_atual:
        partes.append(parte_atual.strip())
    
    return partes


def enviar_relatorio_telegram(relatorio, nome_relatorio="Relatório"):
    """
    Envia relatório dividido em partes para o Telegram
    
    Args:
        relatorio: Texto do relatório
        nome_relatorio: Nome do relatório para logs
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    try:
        from xenos_bot import enviar_oraculo
        
        # Dividir mensagem
        partes = dividir_mensagem(relatorio)
        
        if len(partes) == 1:
            print(f"📊 Enviando {nome_relatorio}...")
            # Sanitizar mensagem antes de enviar
            relatorio_limpo = sanitizar_mensagem_html(relatorio)
            enviar_oraculo(relatorio_limpo)
            print("✅ Enviado!")
        else:
            print(f"📊 Enviando {nome_relatorio} em {len(partes)} partes...")
            
            for i, parte in enumerate(partes, 1):
                try:
                    # Sanitizar cada parte antes de enviar
                    parte_limpa = sanitizar_mensagem_html(parte)
                    enviar_oraculo(parte_limpa)
                    print(f"✅ Parte {i}/{len(partes)} enviada")
                    
                    # Pausa entre mensagens para evitar spam
                    if i < len(partes):
                        import time
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"❌ Erro ao enviar parte {i}: {e}")
                    return False
            
            print(f"✅ {nome_relatorio} completo enviado!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar {nome_relatorio}: {e}")
        return False


def sanitizar_mensagem_html(texto):
    """
    Remove tags HTML de uma mensagem para evitar problemas de parsing
    
    Args:
        texto: Texto com possíveis tags HTML
    
    Returns:
        str: Texto sem tags HTML
    """
    import re
    
    # Remover todas as tags HTML
    texto_limpo = re.sub(r'<[^>]+>', '', texto)
    
    # Remover caracteres problemáticos que podem causar parsing errors
    texto_limpo = texto_limpo.replace('&', '&amp;')
    texto_limpo = texto_limpo.replace('<', '&lt;')
    texto_limpo = texto_limpo.replace('>', '&gt;')
    
    # Limpar espaços extras
    texto_limpo = re.sub(r'\n\s*\n', '\n\n', texto_limpo)
    
    return texto_limpo


def enviar_mensagem_segura(texto, nome="Mensagem"):
    """
    Envia mensagem de forma segura, removendo HTML e dividindo se necessário
    
    Args:
        texto: Texto da mensagem
        nome: Nome da mensagem para logs
    
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        from xenos_bot import enviar_oraculo
        
        # Sanitizar mensagem
        texto_limpo = sanitizar_mensagem_html(texto)
        
        # Dividir se necessário
        partes = dividir_mensagem(texto_limpo)
        
        if len(partes) == 1:
            enviar_oraculo(texto_limpo)
            print(f"✅ {nome} enviada!")
        else:
            print(f"📊 Enviando {nome} em {len(partes)} partes...")
            
            for i, parte in enumerate(partes, 1):
                enviar_oraculo(parte)
                print(f"✅ Parte {i}/{len(partes)} enviada")
                
                if i < len(partes):
                    import time
                    time.sleep(1)
            
            print(f"✅ {nome} completa enviada!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar {nome}: {e}")
        return False


if __name__ == "__main__":
    # Teste das funções
    texto_teste = "A" * 5000  # Texto longo para teste
    
    print("🧪 Testando divisão de mensagem...")
    partes = dividir_mensagem(texto_teste)
    print(f"Texto dividido em {len(partes)} partes")
    
    for i, parte in enumerate(partes, 1):
        print(f"Parte {i}: {len(parte)} caracteres")
    
    print("\n🧪 Testando sanitização HTML...")
    texto_html = "Texto com <b>HTML</b> e <i>tags</i>"
    texto_limpo = sanitizar_mensagem_html(texto_html)
    print(f"Original: {texto_html}")
    print(f"Limpo: {texto_limpo}")
    
    print("\n✅ Testes concluídos!")

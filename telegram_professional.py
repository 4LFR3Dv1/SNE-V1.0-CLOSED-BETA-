#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Profissional de Telegram
Mensagens formatadas para sinais de trading profissional
"""

import requests
from datetime import datetime
import pytz

class TelegramProfessional:
    """
    Gerador de mensagens profissionais para Telegram
    """
    
    def __init__(self, token=None, chat_id=None):
        # Importar configurações do xenos_bot se disponível
        try:
            from xenos_bot import TELEGRAM_TOKEN, CHAT_ID
            self.token = token or TELEGRAM_TOKEN
            self.chat_id = chat_id or CHAT_ID
        except:
            self.token = token
            self.chat_id = chat_id
        
        self.br_tz = pytz.timezone("America/Sao_Paulo")
    
    def gerar_sinal_telegram_pro(self, sinal):
        """
        Gera mensagem profissional para Telegram
        Formato similar a canais de sinais premium
        """
        
        # Emoji baseado em confiança
        if sinal['score_confianca'] >= 85:
            emoji_confianca = "🔥"
            nivel = "ALTA CONFIANÇA"
        elif sinal['score_confianca'] >= 70:
            emoji_confianca = "⭐"
            nivel = "CONFIANÇA MÉDIA"
        else:
            emoji_confianca = "📊"
            nivel = "CONFIANÇA MODERADA"
        
        # Direção
        if sinal['tipo'] == 'LONG':
            emoji_direcao = "🟢"
            acao = "COMPRA"
        else:
            emoji_direcao = "🔴"
            acao = "VENDA"
        
        # Calcular percentuais
        risco_pct = abs((sinal['entry'] - sinal['sl']) / sinal['entry'] * 100)
        tp1_pct = abs((sinal['tp'][0] - sinal['entry']) / sinal['entry'] * 100)
        tp2_pct = abs((sinal['tp'][1] - sinal['entry']) / sinal['entry'] * 100)
        tp3_pct = abs((sinal['tp'][2] - sinal['entry']) / sinal['entry'] * 100)
        
        # Calcular tamanho de posição sugerido
        tamanho_posicao = self._calcular_tamanho_posicao(sinal)
        
        # Timestamp
        timestamp = sinal['timestamp'].strftime('%H:%M:%S')
        
        mensagem = f"""{emoji_confianca} <b>SINAL DE {acao}</b> {emoji_confianca}
━━━━━━━━━━━━━━━━━━━━━━

{emoji_direcao} <b>Par:</b> #{sinal['symbol']}
📊 <b>Timeframe:</b> {sinal['timeframe_principal']} → {sinal['timeframe_target']}
⚡ <b>Confiança:</b> {sinal['score_confianca']:.0f}% ({nivel})

━━━━━━━━━━━━━━━━━━━━━━
📍 <b>NÍVEIS DE OPERAÇÃO</b>
━━━━━━━━━━━━━━━━━━━━━━

💰 <b>ENTRY:</b> ${sinal['entry']:.4f}
   └─ Zona de entrada ideal

🎯 <b>TAKE PROFIT:</b>
   TP1: ${sinal['tp'][0]:.4f} (+{tp1_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][0]:.1f}]
   TP2: ${sinal['tp'][1]:.4f} (+{tp2_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][1]:.1f}]
   TP3: ${sinal['tp'][2]:.4f} (+{tp3_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][2]:.1f}]

🛡️ <b>STOP LOSS:</b> ${sinal['sl']:.4f}
   └─ Risco: {risco_pct:.2f}%

━━━━━━━━━━━━━━━━━━━━━━
✅ <b>CONFIRMAÇÕES</b>
━━━━━━━━━━━━━━━━━━━━━━

{self._formatar_confirmacoes(sinal['confirmacoes'])}
━━━━━━━━━━━━━━━━━━━━━━
⚙️ <b>GESTÃO DE RISCO</b>
━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Tamanho Sugerido:</b> {tamanho_posicao}
💵 <b>Risco por Trade:</b> 1-2% do capital
🎯 <b>Estratégia de Saída:</b>
   • 50% da posição em TP1
   • 30% da posição em TP2
   • 20% da posição em TP3

━━━━━━━━━━━━━━━━━━━━━━
⏰ <b>Válido por:</b> {sinal['validade']}
🤖 <b>SNE Radar Pro</b> | {timestamp}
"""
        
        return mensagem
    
    def _formatar_confirmacoes(self, confirmacoes):
        """
        Formata confirmações de forma clara
        """
        if not confirmacoes:
            return "• Análise técnica padrão"
        
        texto = ""
        for conf in confirmacoes[:6]:  # Máximo 6 confirmações
            texto += f"• {conf}\n"
        
        if len(confirmacoes) > 6:
            texto += f"• +{len(confirmacoes)-6} confirmações adicionais\n"
        
        return texto.rstrip()
    
    def _calcular_tamanho_posicao(self, sinal):
        """
        Calcula tamanho ideal de posição baseado em risco de 1%
        """
        # Risco de 1% do capital
        risco_pct = 0.01
        distancia_sl = abs(sinal['entry'] - sinal['sl']) / sinal['entry']
        
        if distancia_sl == 0:
            return "2% do capital"
        
        # Quantidade = (Capital * Risco%) / Distância SL
        tamanho = (risco_pct / distancia_sl) * 100
        
        # Limitar a 10% do capital
        tamanho = min(tamanho, 10)
        
        return f"{tamanho:.1f}% do capital"
    
    def enviar(self, mensagem):
        """
        Envia mensagem para Telegram
        """
        if not self.token or not self.chat_id:
            print("⚠️ Telegram não configurado")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": mensagem,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Erro ao enviar: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao enviar para Telegram: {e}")
            return False
    
    def enviar_resumo_mercado(self, pares_analisados, sinais_encontrados):
        """
        Envia resumo do scan de mercado
        """
        mensagem = f"""📊 <b>RESUMO DO SCAN DE MERCADO</b>
━━━━━━━━━━━━━━━━━━━━━━

🔍 <b>Pares Analisados:</b> {pares_analisados}
🎯 <b>Sinais Encontrados:</b> {len(sinais_encontrados)}

"""
        
        if sinais_encontrados:
            mensagem += "🏆 <b>MELHORES OPORTUNIDADES:</b>\n\n"
            
            for i, sinal in enumerate(sinais_encontrados[:5], 1):
                emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
                mensagem += f"{i}. {emoji} {sinal['symbol']} - Score: {sinal['score_confianca']:.0f}%\n"
        else:
            mensagem += "⏸️ Nenhuma oportunidade de alta qualidade no momento\n"
        
        mensagem += f"\n⏰ {datetime.now(self.br_tz).strftime('%H:%M:%S')}"
        mensagem += "\n🤖 <b>SNE Radar Pro - Auto Scan</b>"
        
        return self.enviar(mensagem)
    
    def enviar_alerta_oportunidade(self, sinal):
        """
        Envia alerta rápido de oportunidade detectada
        """
        emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
        
        mensagem = f"""🚨 <b>OPORTUNIDADE DETECTADA!</b>

{emoji} <b>{sinal['symbol']}</b> - {sinal['tipo']}
⚡ Score: {sinal['score_confianca']:.0f}%
💰 Entry: ${sinal['entry']:.4f}
🎯 TP1: ${sinal['tp'][0]:.4f} (R/R: 1:{sinal['risco_retorno'][0]:.1f})

📱 Sinal completo sendo enviado...
"""
        
        return self.enviar(mensagem)






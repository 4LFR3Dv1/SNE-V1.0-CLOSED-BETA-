#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formatador de Alertas
Formata mensagens de alerta para Telegram
"""

from datetime import datetime
from typing import Dict


class AlertFormatter:
    """Formatador de mensagens de alerta"""
    
    @staticmethod
    def format_volume_alert(data: Dict) -> str:
        """Formata mensagem de alerta de volume"""
        symbol = data['symbol']
        timeframe = data.get('timeframe', '5m')
        rvol = data['rvol']
        volume_atual = data['volume_atual']
        volume_medio = data['volume_medio']
        preco = data['preco_atual']
        timestamp = data['timestamp']
        
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime('%H:%M:%S')
        else:
            timestamp_str = str(timestamp)
        
        return f"""🚨 <b>VOLUME EXPLOSIVO DETECTADO</b>

📊 <b>{symbol}</b> - {timeframe}
💥 <b>RVOL: {rvol:.2f}x</b>
📈 Volume: {volume_atual:,.0f}
📊 Média: {volume_medio:,.0f}
💰 Preço: ${preco:,.2f}

⏰ {timestamp_str}
💡 Possível movimento significativo em formação"""

    @staticmethod
    def format_pavio_alert(data: Dict) -> str:
        """Formata mensagem de alerta de agulhada"""
        symbol = data['symbol']
        tipo = data['tipo']
        rvol = data['rvol_m30']
        rsi = data['rsi_m5']
        preco = data['preco_atual']
        timestamp = data['timestamp']
        wick_confirmed = data.get('wick_confirmed', False)
        recuo_pct = data.get('recuo_pct', 0)
        high_m5 = data.get('high_m5', preco)
        low_m5 = data.get('low_m5', preco)
        
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime('%H:%M:%S')
        else:
            timestamp_str = str(timestamp)
        
        emoji = '🟢' if tipo == 'LONG' else '🔴'
        direcao = 'COMPRAR' if tipo == 'LONG' else 'VENDER'
        rsi_status = 'Sobre-vendido' if tipo == 'LONG' else 'Sobre-comprado'
        
        wick_info = ""
        if wick_confirmed:
            if tipo == 'SHORT':
                wick_info = f"\n✅ Wick Superior Confirmado: {recuo_pct:.2f}% recuo da máxima"
                wick_info += f"\n📊 Máxima: ${high_m5:,.2f} | Fechamento: ${preco:,.2f}"
            else:  # LONG
                wick_info = f"\n✅ Wick Inferior Confirmado: {recuo_pct:.2f}% recuo do mínimo"
                wick_info += f"\n📊 Mínimo: ${low_m5:,.2f} | Fechamento: ${preco:,.2f}"
        
        return f"""🎯 <b>AGULHADA EM FORMAÇÃO</b>

📊 <b>{symbol}</b>
{emoji} <b>SINAL: {direcao}</b>
💰 Preço: ${preco:,.2f}

📊 Volume M30: <b>{rvol:.2f}x</b> média
📉 RSI M5: {rsi:.1f} ({rsi_status}){wick_info}

⏰ {timestamp_str}
💡 Entrada na ponta do pavio mensal
⚠️ Confirmar com análise adicional antes de operar"""


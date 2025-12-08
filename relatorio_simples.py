#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO SIMPLES E DIRETO
Foco em informações essenciais e acionáveis
"""

from datetime import datetime

class RelatorioSimples:
    """Gerador de relatórios simples e diretos"""
    
    def gerar_relatorio_direto(self, resultado):
        """Gera relatório simples e acionável"""
        try:
            symbol = resultado.get('symbol', 'UNKNOWN')
            timeframe = resultado.get('timeframe', '1h')
            contexto = resultado.get('contexto', {})
            sintese = resultado.get('sintese', {})
            indicadores = resultado.get('indicadores', {})
            
            preco_atual = indicadores.get('preco', 0)
            regime = contexto.get('regime', 'UNKNOWN')
            score = sintese.get('score_confianca', 0)
            acao = sintese.get('acao', 'N/A')
            
            # Determinar ação clara
            if score >= 7:
                if 'LONG' in acao:
                    acao_clara = "🟢 COMPRAR"
                elif 'SHORT' in acao:
                    acao_clara = "🔴 VENDER"
                else:
                    acao_clara = "⚪ AGUARDAR"
            else:
                acao_clara = "⚪ AGUARDAR"
            
            # Níveis essenciais
            entry = sintese.get('entry_price', 0)
            stop = sintese.get('stop_loss', 0)
            tp1 = sintese.get('tp1', 0)
            rr = sintese.get('rr_ratio', 'N/A')
            
            # Volume real
            volume_24h = contexto.get('volume_24h', 0)
            volume_texto = f"${volume_24h:,.0f}" if volume_24h > 0 else "N/A"
            
            # Timestamp
            timestamp = datetime.now().strftime("%d/%m %H:%M")
            
            # Relatório simples
            relatorio = f"""
🎯 {symbol} ({timeframe}) - {timestamp}
💰 ${preco_atual:,.2f} | 📊 {regime} | ⭐ {score}/10

{acao_clara}

📍 ENTRY: ${entry:,.0f}
🛑 STOP: ${stop:,.0f}
🎯 TP1: ${tp1:,.0f}
📊 R:R: {rr}

📈 Volume 24h: {volume_texto}
"""
            
            # Adicionar recomendação baseada no score
            if score >= 8:
                relatorio += "\n✅ SETUP FORTE - Operar"
            elif score >= 6:
                relatorio += "\n⚠️ SETUP MODERADO - Cautela"
            else:
                relatorio += "\n❌ SETUP FRACO - Aguardar"
            
            return relatorio.strip()
            
        except Exception as e:
            return f"❌ Erro ao gerar relatório: {str(e)}"


def gerar_relatorio_simples(resultado):
    """Função principal para gerar relatório simples"""
    try:
        gerador = RelatorioSimples()
        return gerador.gerar_relatorio_direto(resultado)
    except Exception as e:
        return f"❌ Erro: {str(e)}"


if __name__ == "__main__":
    # Teste
    resultado_teste = {
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'contexto': {
            'regime': 'CONSOLIDATION',
            'volume_24h': 2847392847
        },
        'sintese': {
            'acao': '🔴 SHORT (INTRA)',
            'score_confianca': 5.8,
            'entry_price': 110862,
            'stop_loss': 113074,
            'tp1': 107544,
            'rr_ratio': '1:2.0'
        },
        'indicadores': {
            'preco': 110589.46
        }
    }
    
    relatorio = gerar_relatorio_simples(resultado_teste)
    print(relatorio)














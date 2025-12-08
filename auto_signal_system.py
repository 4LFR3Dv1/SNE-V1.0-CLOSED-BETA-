#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Automático de Sinais
Escaneia mercado 24/7 e envia sinais automaticamente
"""

import time
from datetime import datetime
import pytz

from professional_signals import MultiTimeframeSignal
from telegram_professional import TelegramProfessional
from coin_scanner import ProfessionalCoinScanner

class AutoSignalSystem:
    """
    Sistema automático de geração e envio de sinais
    """
    
    def __init__(self):
        self.scanner = ProfessionalCoinScanner()
        self.signal_generator = MultiTimeframeSignal()
        self.telegram = TelegramProfessional()
        
        self.intervalo_scan = 60  # 1 minuto
        self.min_score_envio = 60  # Só enviar se score >= 60 (otimizado)
        self.sinais_enviados = {}  # Cache para evitar duplicatas
        self.br_tz = pytz.timezone("America/Sao_Paulo")
    
    def iniciar_modo_automatico(self):
        """
        Inicia modo automático de sinais
        """
        print("\n" + "="*60)
        print("🤖 MODO AUTOMÁTICO INICIADO")
        print("="*60)
        print(f"📊 Escaneando mercado a cada {self.intervalo_scan} segundos")
        print(f"📱 Sinais com score ≥{self.min_score_envio} serão enviados automaticamente")
        print(f"⏰ Iniciado em: {datetime.now(self.br_tz).strftime('%H:%M:%S')}")
        print("⚠️  Pressione Ctrl+C para parar")
        print("="*60)
        
        ciclo = 0
        
        while True:
            try:
                ciclo += 1
                timestamp = datetime.now(self.br_tz).strftime('%H:%M:%S')
                
                print(f"\n🔄 Ciclo #{ciclo} - {timestamp}")
                print("-"*60)
                
                # Escanear mercado (modo simplificado para maior confiabilidade)
                pares_ativos = self.scanner.escanear_mercado(modo_simplificado=True)
                
                if not pares_ativos:
                    print("❌ Erro ao escanear mercado")
                    time.sleep(self.intervalo_scan)
                    continue
                
                print(f"🔍 Analisando {len(pares_ativos)} pares...")
                
                # Analisar cada par
                sinais_encontrados = []
                
                for par in pares_ativos:
                    sinal = self.signal_generator.analisar_multi_timeframe(par['symbol'])
                    
                    if sinal and sinal['score_confianca'] >= self.min_score_envio:
                        # Verificar se já foi enviado recentemente
                        if not self._sinal_ja_enviado(sinal):
                            sinais_encontrados.append(sinal)
                
                # Processar sinais
                if sinais_encontrados:
                    print(f"\n✅ {len(sinais_encontrados)} sinais de alta qualidade encontrados!")
                    print("-"*60)
                    
                    # Ordenar por score
                    sinais_encontrados.sort(key=lambda x: x['score_confianca'], reverse=True)
                    
                    for sinal in sinais_encontrados:
                        # Enviar alerta rápido
                        self.telegram.enviar_alerta_oportunidade(sinal)
                        
                        # Enviar sinal completo
                        mensagem = self.telegram.gerar_sinal_telegram_pro(sinal)
                        self.telegram.enviar(mensagem)
                        
                        # Marcar como enviado
                        self._marcar_sinal_enviado(sinal)
                        
                        tipo_emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
                        print(f"   {tipo_emoji} {sinal['symbol']} {sinal['tipo']} - Score: {sinal['score_confianca']:.0f}% - ✅ Enviado")
                        
                        # Aguardar 2 segundos entre envios
                        time.sleep(2)
                    
                    print("-"*60)
                else:
                    print("⏸️  Nenhum sinal de alta qualidade no momento")
                
                # Limpar cache antigo (sinais com mais de 1 hora)
                self._limpar_cache_antigo()
                
                # Aguardar próximo scan
                print(f"\n⏰ Próximo scan em {self.intervalo_scan} segundos...")
                time.sleep(self.intervalo_scan)
                
            except KeyboardInterrupt:
                print("\n\n" + "="*60)
                print("🛑 MODO AUTOMÁTICO ENCERRADO")
                print("="*60)
                print(f"⏰ Encerrado em: {datetime.now(self.br_tz).strftime('%H:%M:%S')}")
                print(f"📊 Total de ciclos: {ciclo}")
                print(f"📱 Total de sinais enviados: {len(self.sinais_enviados)}")
                print("="*60)
                break
            except Exception as e:
                print(f"\n❌ Erro no ciclo: {e}")
                print("⏰ Aguardando 10 segundos antes de tentar novamente...")
                time.sleep(10)
    
    def _sinal_ja_enviado(self, sinal):
        """
        Verifica se sinal já foi enviado recentemente (últimos 30 min)
        """
        key = f"{sinal['symbol']}_{sinal['tipo']}"
        
        if key in self.sinais_enviados:
            tempo_decorrido = time.time() - self.sinais_enviados[key]
            return tempo_decorrido < 1800  # 30 minutos
        
        return False
    
    def _marcar_sinal_enviado(self, sinal):
        """
        Marca sinal como enviado
        """
        key = f"{sinal['symbol']}_{sinal['tipo']}"
        self.sinais_enviados[key] = time.time()
    
    def _limpar_cache_antigo(self):
        """
        Remove sinais antigos do cache (mais de 1 hora)
        """
        tempo_atual = time.time()
        keys_para_remover = []
        
        for key, timestamp in self.sinais_enviados.items():
            if tempo_atual - timestamp > 3600:  # 1 hora
                keys_para_remover.append(key)
        
        for key in keys_para_remover:
            del self.sinais_enviados[key]
    
    def buscar_melhor_sinal_agora(self):
        """
        Busca o melhor sinal disponível no momento
        Útil para modo manual
        """
        print("\n🎯 Buscando melhor oportunidade...")
        print("📊 Analisando múltiplos timeframes...")
        print("-"*60)
        
        # Escanear mercado (modo simplificado para maior confiabilidade)
        pares_ativos = self.scanner.escanear_mercado(modo_simplificado=True)
        
        if not pares_ativos:
            print("❌ Erro ao escanear mercado")
            return None
        
        melhor_sinal = None
        melhor_score = 0
        
        # Analisar top 20 por liquidez
        for par in pares_ativos[:20]:
            sinal = self.signal_generator.analisar_multi_timeframe(par['symbol'])
            
            if sinal and sinal['score_confianca'] > melhor_score:
                melhor_sinal = sinal
                melhor_score = sinal['score_confianca']
        
        print("-"*60)
        
        if melhor_sinal:
            print(f"✅ Melhor oportunidade: {melhor_sinal['symbol']} (Score: {melhor_score:.0f}%)")
        else:
            print("⏸️  Nenhuma oportunidade de alta qualidade no momento")
        
        return melhor_sinal
    
    def buscar_top_sinais(self, n=3):
        """
        Busca top N sinais disponíveis
        """
        print(f"\n🏆 Buscando top {n} oportunidades...")
        print("📊 Analisando múltiplos timeframes...")
        print("-"*60)
        
        # Escanear mercado (modo simplificado para maior confiabilidade)
        pares_ativos = self.scanner.escanear_mercado(modo_simplificado=True)
        
        if not pares_ativos:
            print("❌ Erro ao escanear mercado")
            return []
        
        sinais_encontrados = []
        
        # Analisar top 30 por liquidez
        for par in pares_ativos[:30]:
            sinal = self.signal_generator.analisar_multi_timeframe(par['symbol'])
            
            if sinal and sinal['score_confianca'] >= 60:  # Score mínimo 60
                sinais_encontrados.append(sinal)
        
        # Ordenar por score
        sinais_encontrados.sort(key=lambda x: x['score_confianca'], reverse=True)
        
        print("-"*60)
        print(f"✅ {len(sinais_encontrados)} oportunidades encontradas")
        
        return sinais_encontrados[:n]


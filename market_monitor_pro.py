#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE PROFESSIONAL MARKET MONITOR
Sistema de alertas em tempo real profissional e simples
"""

import threading
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configurar logging profissional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sne_alerts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SNE_Alerts')

@dataclass
class MarketState:
    symbol: str
    timeframe: str
    price: float
    volume: float
    volatility: float
    regime: str
    confluence: float
    timestamp: datetime

class ProfessionalMarketMonitor:
    def __init__(self, config_file: str = 'config/alerts_config.json'):
        self.config = self.load_config(config_file)
        self.running = False
        self.thread = None
        self.previous_states = {}
        self.alert_cooldowns = {}
        
        # Métricas simples
        self.stats = {
            'alerts_sent': 0,
            'errors': 0,
            'uptime_start': datetime.now()
        }
    
    def load_config(self, config_file: str) -> Dict:
        """Carrega configuração de forma robusta"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuração carregada: {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"Arquivo de configuração não encontrado: {config_file}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Erro no JSON da configuração: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Configuração padrão profissional"""
        return {
            "enabled": True,
            "symbols": ["BTCUSDT"],
            "timeframes": ["1h"],
            "intervals": {
                "1h": 300,    # 5 minutos
                "4h": 900,    # 15 minutos
                "1d": 3600    # 1 hora
            },
            "alert_rules": {
                "min_confluence": 7.0,
                "min_volume_spike": 1.5,
                "max_volatility": 5.0
            },
            "rate_limits": {
                "max_alerts_per_hour": 10,
                "cooldown_minutes": 5
            },
            "quiet_hours": [22, 6],  # 22h às 6h
            "channels": ["telegram"]
        }
    
    def start(self):
        """Inicia monitoramento de forma profissional"""
        if self.running:
            logger.warning("Monitor já está rodando")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        
        logger.info("🚀 SNE Professional Monitor iniciado")
        self.log_status()
    
    def stop(self):
        """Para monitoramento de forma limpa"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("🛑 SNE Professional Monitor parado")
        self.log_final_stats()
    
    def monitor_loop(self):
        """Loop principal otimizado"""
        while self.running:
            try:
                if self.should_analyze():
                    self.analyze_all_pairs()
                
                # Intervalo inteligente baseado na configuração
                sleep_time = self.get_optimal_interval()
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                self.stats['errors'] += 1
                time.sleep(60)  # Fallback seguro
    
    def should_analyze(self) -> bool:
        """Verifica se deve analisar agora"""
        if not self.config.get('enabled', True):
            return False
        
        # Verificar horário silencioso
        current_hour = datetime.now().hour
        quiet_start, quiet_end = self.config.get('quiet_hours', [22, 6])
        
        if quiet_start <= quiet_end:
            if quiet_start <= current_hour < quiet_end:
                return False
        else:  # Cruza meia-noite
            if current_hour >= quiet_start or current_hour < quiet_end:
                return False
        
        return True
    
    def get_optimal_interval(self) -> int:
        """Calcula intervalo otimizado"""
        intervals = self.config.get('intervals', {})
        
        # Usar intervalo do timeframe mais frequente
        min_interval = min(intervals.values()) if intervals else 300
        
        # Ajustar baseado na carga do sistema
        if self.stats['errors'] > 5:
            return min_interval * 2  # Reduzir frequência se muitos erros
        
        return min_interval
    
    def analyze_all_pairs(self):
        """Analisa todos os pares configurados"""
        for symbol in self.config.get('symbols', []):
            for timeframe in self.config.get('timeframes', []):
                try:
                    self.analyze_pair(symbol, timeframe)
                except Exception as e:
                    logger.error(f"Erro analisando {symbol} {timeframe}: {e}")
                    self.stats['errors'] += 1
    
    def analyze_pair(self, symbol: str, timeframe: str):
        """Analisa um par específico"""
        # Obter dados usando SNE existente
        from contexto_macro import coletar_dados
        dados = coletar_dados(symbol, timeframe, 100)
        
        if dados is None or dados.empty:
            logger.warning(f"Dados não disponíveis: {symbol} {timeframe}")
            return
        
        # Analisar com SNE
        from contexto_global import analisar_contexto
        from motor_renan import gerar_sintese_completa
        
        contexto = analisar_contexto(dados)
        sintese = gerar_sintese_completa(symbol, timeframe)
        
        # Criar estado atual
        current_state = MarketState(
            symbol=symbol,
            timeframe=timeframe,
            price=dados['close'].iloc[-1],
            volume=dados['volume'].iloc[-1],
            volatility=contexto.get('volatilidade', 0),
            regime=contexto.get('regime', 'UNKNOWN'),
            confluence=sintese.get('score_confianca', 0),
            timestamp=datetime.now()
        )
        
        # Verificar alertas
        alerts = self.check_for_alerts(current_state)
        
        # Enviar alertas
        for alert in alerts:
            self.send_alert(alert)
    
    def check_for_alerts(self, state: MarketState) -> List[Dict]:
        """Verifica condições para alertas"""
        alerts = []
        state_key = f"{state.symbol}_{state.timeframe}"
        
        # Obter estado anterior
        previous_state = self.previous_states.get(state_key)
        self.previous_states[state_key] = state
        
        if not previous_state:
            return alerts  # Primeira análise
        
        # Verificar cooldown
        if self.is_in_cooldown(state_key):
            return alerts
        
        # Regras de alerta simples mas eficazes
        rules = self.config.get('alert_rules', {})
        
        # 1. Alta confluência
        min_confluence = rules.get('min_confluence', 7.0)
        if state.confluence >= min_confluence and previous_state.confluence < min_confluence:
            alerts.append({
                'type': 'HIGH_CONFLUENCE',
                'priority': 'HIGH',
                'symbol': state.symbol,
                'timeframe': state.timeframe,
                'message': f"🎯 ALTA CONFLUÊNCIA: {state.symbol} ({state.timeframe}) - Score: {state.confluence:.1f}/10"
            })
        
        # 2. Mudança de regime
        if state.regime != previous_state.regime:
            alerts.append({
                'type': 'REGIME_CHANGE',
                'priority': 'MEDIUM',
                'symbol': state.symbol,
                'timeframe': state.timeframe,
                'message': f"🔄 MUDANÇA DE REGIME: {state.symbol} ({state.timeframe}) - {previous_state.regime} → {state.regime}"
            })
        
        # 3. Volatilidade extrema
        max_volatility = rules.get('max_volatility', 5.0)
        if state.volatility > max_volatility:
            alerts.append({
                'type': 'HIGH_VOLATILITY',
                'priority': 'HIGH',
                'symbol': state.symbol,
                'timeframe': state.timeframe,
                'message': f"⚠️ VOLATILIDADE EXTREMA: {state.symbol} ({state.timeframe}) - {state.volatility:.1f}%"
            })
        
        # 4. Spike de volume
        min_volume_spike = rules.get('min_volume_spike', 1.5)
        if previous_state.volume > 0:
            volume_ratio = state.volume / previous_state.volume
            if volume_ratio >= min_volume_spike:
                alerts.append({
                    'type': 'VOLUME_SPIKE',
                    'priority': 'MEDIUM',
                    'symbol': state.symbol,
                    'timeframe': state.timeframe,
                    'message': f"📈 SPIKE DE VOLUME: {state.symbol} ({state.timeframe}) - {volume_ratio:.1f}x"
                })
        
        return alerts
    
    def is_in_cooldown(self, state_key: str) -> bool:
        """Verifica se está em cooldown"""
        cooldown_minutes = self.config.get('rate_limits', {}).get('cooldown_minutes', 5)
        
        if state_key in self.alert_cooldowns:
            last_alert = self.alert_cooldowns[state_key]
            if datetime.now() - last_alert < timedelta(minutes=cooldown_minutes):
                return True
        
        return False
    
    def send_alert(self, alert: Dict):
        """Envia alerta de forma profissional"""
        try:
            # Formatar mensagem
            message = self.format_alert_message(alert)
            
            # Enviar para canais configurados
            channels = self.config.get('channels', ['telegram'])
            
            for channel in channels:
                if channel == 'telegram':
                    self.send_telegram_alert(message, alert)
                elif channel == 'email':
                    self.send_email_alert(message, alert)
            
            # Atualizar cooldown
            state_key = f"{alert.get('symbol', 'unknown')}_{alert.get('timeframe', 'unknown')}"
            self.alert_cooldowns[state_key] = datetime.now()
            
            # Atualizar estatísticas
            self.stats['alerts_sent'] += 1
            
            logger.info(f"✅ Alerta enviado: {alert['type']}")
            
        except Exception as e:
            logger.error(f"Erro enviando alerta: {e}")
            self.stats['errors'] += 1
    
    def format_alert_message(self, alert: Dict) -> str:
        """Formata mensagem de alerta"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        return f"""🚨 **SNE PROFESSIONAL ALERT**

{alert['message']}

**Prioridade:** {alert['priority']}
**Tipo:** {alert['type']}
**Horário:** {timestamp}

---
*SNE Professional Alert System*"""
    
    def send_telegram_alert(self, message: str, alert: Dict):
        """Envia alerta para Telegram"""
        try:
            from telegram_bot import enviar_mensagem_telegram
            enviar_mensagem_telegram(message)
        except Exception as e:
            logger.error(f"Erro enviando Telegram: {e}")
            raise
    
    def send_email_alert(self, message: str, alert: Dict):
        """Envia alerta por email"""
        # Implementação simples de email
        logger.info(f"Email alert: {alert['type']}")
    
    def log_status(self):
        """Log do status atual"""
        uptime = datetime.now() - self.stats['uptime_start']
        logger.info(f"📊 Status: {self.stats['alerts_sent']} alertas enviados, {self.stats['errors']} erros, uptime: {uptime}")
    
    def log_final_stats(self):
        """Log das estatísticas finais"""
        uptime = datetime.now() - self.stats['uptime_start']
        logger.info(f"📈 Estatísticas finais: {self.stats['alerts_sent']} alertas, {self.stats['errors']} erros, uptime: {uptime}")
    
    def get_status(self) -> Dict:
        """Retorna status para API"""
        uptime = datetime.now() - self.stats['uptime_start']
        return {
            'running': self.running,
            'uptime': str(uptime),
            'alerts_sent': self.stats['alerts_sent'],
            'errors': self.stats['errors'],
            'config': self.config
        }














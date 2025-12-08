#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Contínuo de Oportunidades
Roda em background e dispara alertas quando detecta condições
"""

import sys
import time
import threading
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scanners.volume_scanner import VolumeScanner
from notifications.telegram_notifier import TelegramNotifier, get_app_data_dir


# Configurar logging
def setup_logger():
    """Configura logger para o monitor"""
    logger = logging.getLogger('opportunity_monitor')
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo
    log_file = get_app_data_dir() / 'logs' / 'scanner.log'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()


class OpportunityMonitor:
    """Monitor contínuo de oportunidades"""
    
    def __init__(self, 
                 symbols: List[str] = None,
                 scan_interval: int = 60,
                 enable_volume_scanner: bool = True,
                 enable_pavio_scanner: bool = True,  # ✅ ATIVADO POR PADRÃO
                 max_symbols: int = 15):
        """
        Inicializa monitor
        
        Args:
            symbols: Lista de símbolos para monitorar
            scan_interval: Intervalo entre scans (segundos)
            enable_volume_scanner: Ativar scanner de volume (Fase 1)
            enable_pavio_scanner: Ativar scanner de pavio (Fase 2)
            max_symbols: Limite máximo de símbolos (rate limit)
        """
        # Limitar lista de símbolos automaticamente
        if symbols and len(symbols) > max_symbols:
            logger.warning(f"Lista de símbolos ({len(symbols)}) excede máximo ({max_symbols})")
            logger.info(f"Usando apenas os primeiros {max_symbols} símbolos")
            self.symbols = symbols[:max_symbols]
        else:
            self.symbols = symbols or self._get_default_symbols()
        
        self.scan_interval = scan_interval
        self.max_symbols = max_symbols
        self.api_delay = 0.1  # Delay entre requisições (segundos)
        self.running = False
        self.thread = None
        
        # Scanners
        self.volume_scanner = VolumeScanner(rvol_threshold=2.0) if enable_volume_scanner else None
        
        if enable_pavio_scanner:
            try:
                from scanners.pavio_scanner import PavioScanner
                self.pavio_scanner = PavioScanner(
                    volume_threshold=2.5,
                    rsi_long_threshold=25,
                    rsi_short_threshold=75,
                    wick_confirmation_pct=0.3
                )
            except ImportError:
                print("⚠️ PavioScanner não disponível")
                self.pavio_scanner = None
        else:
            self.pavio_scanner = None
        
        # Notificador
        self.notifier = TelegramNotifier()
        
        # Estatísticas
        self.stats = {
            'scans_total': 0,
            'alerts_volume': 0,
            'alerts_pavio': 0,
            'errors': 0,
            'last_scan': None,
            'avg_cycle_time': 0.0,
            'max_cycle_time': 0.0,
            'consecutive_errors': 0,
            'network_errors': 0,
            'rate_limit_hits': 0
        }
        
        # Controle de erros
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
    
    def _get_default_symbols(self) -> List[str]:
        """Retorna lista padrão (top 10 por liquidez)"""
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT',
            'XRPUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT'
        ]
    
    def _calculate_dynamic_delay(self) -> float:
        """
        Calcula delay dinâmico baseado no número de símbolos
        Para respeitar rate limit: 1200 req/min = 20 req/s = 0.05s entre reqs
        Com margem de segurança: 0.1s entre símbolos
        """
        return self.api_delay
    
    def _check_internet_connection(self) -> bool:
        """Verifica conexão com internet"""
        try:
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Inicia monitoramento"""
        if self.running:
            logger.warning("Monitor já está rodando")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Monitor de oportunidades iniciado")
        logger.info(f"   Símbolos: {', '.join(self.symbols)}")
        logger.info(f"   Intervalo: {self.scan_interval}s")
        logger.info(f"   Volume Scanner: {'✅' if self.volume_scanner else '❌'}")
        logger.info(f"   Pavio Scanner: {'✅' if self.pavio_scanner else '❌'}")
    
    def stop(self):
        """Para monitoramento"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("🛑 Monitor de oportunidades parado")
        self._log_final_stats()
    
    def _monitor_loop(self):
        """Loop principal de monitoramento com mitigações de risco"""
        while self.running:
            try:
                cycle_start = time.time()
                
                # Verificar conexão antes de escanear
                if not self._check_internet_connection():
                    self.consecutive_errors += 1
                    self.stats['network_errors'] += 1
                    
                    if self.consecutive_errors >= self.max_consecutive_errors:
                        logger.warning("Muitos erros consecutivos. Entrando em modo de espera...")
                        time.sleep(60)  # Aguardar 1 minuto
                        self.consecutive_errors = 0
                    else:
                        logger.warning(f"Sem conexão. Tentando novamente em 10s... ({self.consecutive_errors}/{self.max_consecutive_errors})")
                        time.sleep(10)  # Aguardar 10 segundos
                    continue
                
                # Reset contador de erros se sucesso
                self.consecutive_errors = 0
                
                # Escanear todos os símbolos
                for symbol in self.symbols:
                    if not self.running:
                        break
                    
                    # Delay entre símbolos (respeita rate limit)
                    time.sleep(self._calculate_dynamic_delay())
                    
                    # Scanner de Volume (Fase 1)
                    if self.volume_scanner:
                        try:
                            result = self.volume_scanner.scan_symbol(symbol, timeframe='5m')
                            if result and result.get('triggered'):
                                self.notifier.send_volume_alert(result)
                                self.stats['alerts_volume'] += 1
                                logger.info(f"✅ Alerta de volume: {symbol} (RVOL: {result['rvol']:.2f}x)")
                        except Exception as e:
                            logger.error(f"Erro ao escanear volume de {symbol}: {e}")
                            self.stats['errors'] += 1
                    
                    # Scanner de Pavio (Fase 2 - será implementado depois)
                    if self.pavio_scanner:
                        try:
                            result = self.pavio_scanner.scan_symbol(symbol)
                            if result and result.get('triggered'):
                                self.notifier.send_pavio_alert(result)
                                self.stats['alerts_pavio'] += 1
                                logger.info(f"✅ Alerta de agulhada: {symbol} ({result.get('tipo', 'UNKNOWN')})")
                        except Exception as e:
                            logger.error(f"Erro ao escanear pavio de {symbol}: {e}")
                            self.stats['errors'] += 1
                    
                    self.stats['scans_total'] += 1
                
                # Calcular tempo real de execução
                execution_time = time.time() - cycle_start
                
                # Estatísticas de performance
                self.stats['avg_cycle_time'] = (
                    (self.stats.get('avg_cycle_time', 0) * 0.9) + 
                    (execution_time * 0.1)
                )
                self.stats['max_cycle_time'] = max(
                    self.stats.get('max_cycle_time', 0),
                    execution_time
                )
                
                # Compensar drift: aguardar apenas o tempo restante
                remaining_time = max(0, self.scan_interval - execution_time)
                
                if remaining_time > 0:
                    time.sleep(remaining_time)
                else:
                    # Se demorou mais que o intervalo, logar warning
                    logger.warning(f"Ciclo demorou {execution_time:.1f}s (mais que intervalo de {self.scan_interval}s)")
                    # Não esperar - continuar imediatamente
                
                self.stats['last_scan'] = datetime.now()
                
            except KeyboardInterrupt:
                logger.info("Interrompido pelo usuário")
                break
            except KeyboardInterrupt:
                logger.info("Interrompido pelo usuário")
                self.running = False
                break
            except Exception as e:
                self.consecutive_errors += 1
                logger.error(f"Erro no loop de monitoramento: {e}", exc_info=True)
                self.stats['errors'] += 1
                
                # NÃO parar o monitor por erros - apenas aguardar e continuar
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.warning(f"Muitos erros consecutivos ({self.consecutive_errors}). Entrando em modo de espera...")
                    # Aguardar mais tempo, mas continuar tentando
                    time.sleep(60)
                    self.consecutive_errors = 0  # Reset após espera
                else:
                    # Aguardar um pouco e continuar
                    time.sleep(10)
                
                # IMPORTANTE: Continuar o loop mesmo com erros
                # Não quebrar o loop - apenas logar e continuar
                continue
    
    def _log_final_stats(self):
        """Loga estatísticas finais"""
        logger.info("=" * 60)
        logger.info("📊 ESTATÍSTICAS FINAIS DO MONITOR")
        logger.info("=" * 60)
        logger.info(f"Total de scans: {self.stats['scans_total']}")
        logger.info(f"Alertas de volume: {self.stats['alerts_volume']}")
        logger.info(f"Alertas de pavio: {self.stats['alerts_pavio']}")
        logger.info(f"Erros: {self.stats['errors']}")
        logger.info(f"Tempo médio de ciclo: {self.stats['avg_cycle_time']:.2f}s")
        logger.info(f"Tempo máximo de ciclo: {self.stats['max_cycle_time']:.2f}s")
        logger.info("=" * 60)
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do monitor"""
        return {
            **self.stats,
            'running': self.running,
            'symbols_count': len(self.symbols),
            'symbols': self.symbols
        }


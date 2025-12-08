#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONITOR AUTOMÁTICO DE ALERTAS - SNE RADAR 3.0
Sistema de monitoramento contínuo de alertas
"""

import os
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Thread

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
logger = logging.getLogger(__name__)

class AlertMonitor:
    """
    Monitor automático de alertas para o SNE Radar 3.0
    Verifica preços e envia notificações
    """
    
    def __init__(self):
        """Inicializa o monitor de alertas"""
        self.running = False
        self.check_interval = 60  # Verificar a cada 60 segundos
        self.last_check = None
        
        # Importar sistemas necessários
        self._import_systems()
        
        logger.info("🔔 AlertMonitor inicializado")
    
    def _import_systems(self):
        """Importa sistemas necessários"""
        try:
            # Sistema de usuários
            from user_manager import user_manager
            self.user_manager = user_manager
            
            # Sistema de segurança
            from security_manager import security_manager
            self.security = security_manager
            
            # Sistema de envio de mensagens
            try:
                from xenos_bot import enviar_oraculo
                self.enviar_oraculo = enviar_oraculo
            except ImportError:
                logger.warning("⚠️ xenos_bot não encontrado. Usando mock.")
                self.enviar_oraculo = self._mock_enviar_oraculo
            
            # Sistema de dados de mercado
            try:
                from main import buscar_dados_binance
                self.buscar_dados_binance = buscar_dados_binance
            except ImportError:
                logger.warning("⚠️ main não encontrado. Usando mock.")
                self.buscar_dados_binance = self._mock_buscar_dados_binance
            
            logger.info("✅ Sistemas importados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao importar sistemas: {e}")
            raise
    
    async def start_monitoring(self):
        """Inicia o monitoramento de alertas"""
        try:
            self.running = True
            logger.info("🔔 Iniciando monitoramento de alertas...")
            
            while self.running:
                try:
                    await self._check_all_alerts()
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"❌ Erro no ciclo de monitoramento: {e}")
                    await asyncio.sleep(30)  # Aguardar antes de tentar novamente
            
        except Exception as e:
            logger.error(f"❌ Erro fatal no monitoramento: {e}")
        finally:
            logger.info("🛑 Monitoramento de alertas parado")
    
    async def stop_monitoring(self):
        """Para o monitoramento de alertas"""
        self.running = False
        logger.info("🛑 Parando monitoramento de alertas...")
    
    async def _check_all_alerts(self):
        """Verifica todos os alertas ativos"""
        try:
            # Obter todos os alertas ativos
            alertas = self._get_all_active_alerts()
            
            if not alertas:
                logger.debug("🔍 Nenhum alerta ativo encontrado")
                return
            
            logger.info(f"🔍 Verificando {len(alertas)} alertas ativos...")
            
            # Agrupar alertas por par
            alertas_por_par = self._group_alerts_by_symbol(alertas)
            
            # Verificar cada par
            for par, alertas_par in alertas_por_par.items():
                try:
                    await self._check_symbol_alerts(par, alertas_par)
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar alertas de {par}: {e}")
            
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar alertas: {e}")
    
    def _get_all_active_alerts(self) -> List[Dict[str, Any]]:
        """Obtém todos os alertas ativos"""
        try:
            if not self.user_manager.conn:
                return []
            
            cursor = self.user_manager.conn.cursor()
            cursor.execute('''
                SELECT * FROM alertas 
                WHERE ativo = 1
                ORDER BY criado_em DESC
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar alertas ativos: {e}")
            return []
    
    def _group_alerts_by_symbol(self, alertas: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa alertas por símbolo"""
        grouped = {}
        for alerta in alertas:
            par = alerta['par']
            if par not in grouped:
                grouped[par] = []
            grouped[par].append(alerta)
        return grouped
    
    async def _check_symbol_alerts(self, par: str, alertas: List[Dict[str, Any]]):
        """Verifica alertas de um símbolo específico"""
        try:
            # Obter preço atual
            preco_atual = await self._get_current_price(par)
            
            if preco_atual is None:
                logger.warning(f"⚠️ Não foi possível obter preço de {par}")
                return
            
            logger.debug(f"💰 {par}: ${preco_atual:,.2f}")
            
            # Verificar cada alerta
            for alerta in alertas:
                try:
                    await self._check_single_alert(alerta, preco_atual)
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar alerta {alerta['id']}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar alertas de {par}: {e}")
    
    async def _check_single_alert(self, alerta: Dict[str, Any], preco_atual: float):
        """Verifica um alerta específico"""
        try:
            preco_alerta = alerta['preco']
            user_id = alerta['user_id']
            par = alerta['par']
            alerta_id = alerta['id']
            
            # Verificar se preço foi atingido
            if preco_atual >= preco_alerta:
                # Alerta disparado!
                await self._trigger_alert(alerta, preco_atual)
                
                # Desativar alerta
                self._deactivate_alert(alerta_id)
                
                logger.info(f"🔔 Alerta disparado: {par} @ ${preco_alerta:,.2f} (atual: ${preco_atual:,.2f})")
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar alerta individual: {e}")
    
    async def _trigger_alert(self, alerta: Dict[str, Any], preco_atual: float):
        """Dispara um alerta"""
        try:
            user_id = alerta['user_id']
            par = alerta['par']
            preco_alerta = alerta['preco']
            
            # Verificar se usuário ainda tem acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                logger.warning(f"⚠️ Usuário {user_id} sem acesso premium. Alerta não enviado.")
                return
            
            # Formatar mensagem de alerta
            mensagem = f"""
🚨 **ALERTA DISPARADO!**

🔹 **Par:** {par}
🔹 **Preço Alvo:** ${preco_alerta:,.2f}
🔹 **Preço Atual:** ${preco_atual:,.2f}
🔹 **Diferença:** {((preco_atual - preco_alerta) / preco_alerta * 100):+.2f}%

⏰ **Horário:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 **Ação:** Analise o mercado antes de operar!
"""
            
            # Enviar alerta
            sucesso = await self._send_alert_to_user(user_id, mensagem)
            
            if sucesso:
                # Log de auditoria
                self.security._log_audit("ALERT_TRIGGERED", f"Alerta {par} @ {preco_alerta} disparado", user_id)
                logger.info(f"✅ Alerta enviado para usuário {user_id}")
            else:
                logger.error(f"❌ Falha ao enviar alerta para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao disparar alerta: {e}")
    
    async def _send_alert_to_user(self, user_id: str, mensagem: str) -> bool:
        """Envia alerta para usuário específico"""
        try:
            # Usar sistema de envio existente
            if hasattr(self, 'enviar_oraculo') and callable(self.enviar_oraculo):
                # Modificar para enviar para usuário específico
                # Nota: O sistema atual envia para CHAT_ID fixo
                # Em produção, seria necessário modificar para suportar múltiplos usuários
                sucesso = self.enviar_oraculo(mensagem)
                return sucesso
            else:
                # Mock para desenvolvimento
                print(f"[MOCK ALERT] Para usuário {user_id}: {mensagem[:50]}...")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar alerta para usuário {user_id}: {e}")
            return False
    
    def _deactivate_alert(self, alerta_id: int):
        """Desativa um alerta"""
        try:
            if not self.user_manager.conn:
                return False
            
            cursor = self.user_manager.conn.cursor()
            cursor.execute('''
                UPDATE alertas 
                SET ativo = 0
                WHERE id = ?
            ''', (alerta_id,))
            
            self.user_manager.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao desativar alerta {alerta_id}: {e}")
            return False
    
    async def _get_current_price(self, par: str) -> Optional[float]:
        """Obtém preço atual de um par"""
        try:
            # Usar sistema de dados existente
            if hasattr(self, 'buscar_dados_binance') and callable(self.buscar_dados_binance):
                # Obter dados do par
                dados = self.buscar_dados_binance(par, '1m', 1)
                
                if dados and len(dados) > 0:
                    # Extrair preço de fechamento da última candle
                    ultima_candle = dados.iloc[-1]
                    return float(ultima_candle['close'])
                else:
                    return None
            else:
                # Mock para desenvolvimento
                preços_mock = {
                    'BTCUSDT': 50000.0,
                    'ETHUSDT': 3200.0,
                    'ADAUSDT': 0.45,
                    'SOLUSDT': 100.0,
                    'DOTUSDT': 6.5,
                    'LINKUSDT': 15.0
                }
                return preços_mock.get(par, 100.0)
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter preço de {par}: {e}")
            return None
    
    # ===========================================
    # MÉTODOS DE ESTATÍSTICAS
    # ===========================================
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do monitoramento"""
        try:
            alertas_ativos = self._get_all_active_alerts()
            
            stats = {
                'running': self.running,
                'last_check': self.last_check.isoformat() if self.last_check else None,
                'check_interval': self.check_interval,
                'active_alerts': len(alertas_ativos),
                'alerts_by_symbol': self._group_alerts_by_symbol(alertas_ativos)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def get_user_alert_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtém estatísticas de alertas de um usuário"""
        try:
            alertas_usuario = self.user_manager.get_alertas_usuario(user_id)
            
            stats = {
                'total_alerts': len(alertas_usuario),
                'active_alerts': len([a for a in alertas_usuario if a['ativo']]),
                'alerts_by_symbol': {}
            }
            
            # Agrupar por símbolo
            for alerta in alertas_usuario:
                par = alerta['par']
                if par not in stats['alerts_by_symbol']:
                    stats['alerts_by_symbol'][par] = 0
                stats['alerts_by_symbol'][par] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas do usuário {user_id}: {e}")
            return {}
    
    # ===========================================
    # MÉTODOS DE CONFIGURAÇÃO
    # ===========================================
    def set_check_interval(self, interval: int):
        """Define intervalo de verificação"""
        if interval < 30:  # Mínimo 30 segundos
            interval = 30
        
        self.check_interval = interval
        logger.info(f"⏰ Intervalo de verificação alterado para {interval} segundos")
    
    def pause_monitoring(self):
        """Pausa o monitoramento"""
        self.running = False
        logger.info("⏸️ Monitoramento pausado")
    
    def resume_monitoring(self):
        """Retoma o monitoramento"""
        self.running = True
        logger.info("▶️ Monitoramento retomado")
    
    # ===========================================
    # FUNÇÕES MOCK PARA DESENVOLVIMENTO
    # ===========================================
    def _mock_enviar_oraculo(self, mensagem: str) -> bool:
        """Mock da função de envio"""
        print(f"[MOCK] Enviando alerta: {mensagem[:50]}...")
        return True
    
    def _mock_buscar_dados_binance(self, par: str, timeframe: str, limit: int):
        """Mock da função de busca de dados"""
        import pandas as pd
        import numpy as np
        
        # Criar dados mock
        timestamps = pd.date_range(start='2025-01-01', periods=limit, freq='1min')
        preços_base = {
            'BTCUSDT': 50000,
            'ETHUSDT': 3200,
            'ADAUSDT': 0.45,
            'SOLUSDT': 100,
            'DOTUSDT': 6.5,
            'LINKUSDT': 15
        }
        
        preço_base = preços_base.get(par, 100)
        
        # Gerar dados com pequena variação
        dados = pd.DataFrame({
            'timestamp': timestamps,
            'open': preço_base + np.random.normal(0, preço_base * 0.01, limit),
            'high': preço_base + np.random.normal(0, preço_base * 0.01, limit),
            'low': preço_base + np.random.normal(0, preço_base * 0.01, limit),
            'close': preço_base + np.random.normal(0, preço_base * 0.01, limit),
            'volume': np.random.uniform(1000, 10000, limit)
        })
        
        return dados

# ===========================================
# INSTÂNCIA GLOBAL
# ===========================================
alert_monitor = AlertMonitor()

# ===========================================
# FUNÇÕES UTILITÁRIAS
# ===========================================
async def start_alert_monitoring():
    """Inicia o monitoramento de alertas"""
    await alert_monitor.start_monitoring()

async def stop_alert_monitoring():
    """Para o monitoramento de alertas"""
    await alert_monitor.stop_monitoring()

def get_monitoring_status() -> Dict[str, Any]:
    """Obtém status do monitoramento"""
    return alert_monitor.get_monitoring_stats()

def get_user_alerts(user_id: str) -> List[Dict[str, Any]]:
    """Obtém alertas de um usuário"""
    try:
        from user_manager import user_manager
        return user_manager.get_alertas_usuario(user_id)
    except ImportError:
        return []

def create_alert(user_id: str, par: str, preco: float) -> Optional[int]:
    """Cria um alerta"""
    try:
        from user_manager import user_manager
        return user_manager.criar_alerta(user_id, par, preco)
    except ImportError:
        return None

# ===========================================
# FUNÇÃO PRINCIPAL PARA TESTE
# ===========================================
async def main():
    """Função principal para teste"""
    try:
        print("🧪 Testando monitor de alertas do SNE Radar 3.0...")
        
        # Criar alerta de teste
        test_user = "123456789"
        test_par = "BTCUSDT"
        test_preco = 50000.0
        
        print(f"\n🔔 Criando alerta de teste:")
        alerta_id = create_alert(test_user, test_par, test_preco)
        if alerta_id:
            print(f"✅ Alerta criado com ID: {alerta_id}")
        else:
            print("❌ Erro ao criar alerta")
        
        # Obter estatísticas
        print(f"\n📊 Estatísticas do monitoramento:")
        stats = get_monitoring_status()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Obter alertas do usuário
        print(f"\n📋 Alertas do usuário {test_user}:")
        alertas = get_user_alerts(test_user)
        for alerta in alertas:
            print(f"   {alerta['par']} @ ${alerta['preco']:,.2f}")
        
        # Iniciar monitoramento por 30 segundos
        print(f"\n🔍 Iniciando monitoramento por 30 segundos...")
        
        # Executar monitoramento em background
        monitor_task = asyncio.create_task(alert_monitor.start_monitoring())
        
        # Aguardar 30 segundos
        await asyncio.sleep(30)
        
        # Parar monitoramento
        await alert_monitor.stop_monitoring()
        monitor_task.cancel()
        
        print("\n✅ Teste do monitor de alertas concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    # Executar teste
    asyncio.run(main())

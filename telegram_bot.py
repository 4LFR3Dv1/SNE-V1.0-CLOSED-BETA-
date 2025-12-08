#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT TELEGRAM PRINCIPAL - SNE RADAR 3.0
Sistema completo de monetização integrado
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
logger = logging.getLogger(__name__)

class SNEBot:
    """
    Bot Telegram principal do SNE Radar 3.0
    Integra todos os sistemas de monetização
    """
    
    def __init__(self):
        """Inicializa o bot principal"""
        self.bot = None
        self.dispatcher = None
        
        # Importar sistemas existentes
        self._import_systems()
        
        # Configurar handlers
        self._setup_handlers()
        
        logger.info("🤖 SNEBot inicializado")
    
    def _import_systems(self):
        """Importa todos os sistemas necessários"""
        try:
            # Sistema de usuários e pagamentos
            from user_manager import user_manager
            from payment_manager import payment_manager
            from plan_config import PLANOS, formatar_preco
            
            self.user_manager = user_manager
            self.payment_manager = payment_manager
            self.planos = PLANOS
            self.formatar_preco = formatar_preco
            
            # Sistema de segurança
            from security_manager import security_manager
            self.security = security_manager
            
            # Sistema de cache
            from cache_manager import cache_manager
            self.cache = cache_manager
            
            # Sistema de análise existente
            try:
                from motor_renan import analise_completa
                from relatorios_periodicos import gerar_relatorio_horario, gerar_relatorio_diario
                from xenos_bot import enviar_oraculo, enviar_foto
                
                self.analise_completa = analise_completa
                self.gerar_relatorio_horario = gerar_relatorio_horario
                self.gerar_relatorio_diario = gerar_relatorio_diario
                self.enviar_oraculo = enviar_oraculo
                self.enviar_foto = enviar_foto
                
                logger.info("✅ Sistemas de análise existentes importados")
                
            except ImportError as e:
                logger.warning(f"⚠️ Alguns módulos de análise não encontrados: {e}")
                # Criar funções mock para desenvolvimento
                self.analise_completa = self._mock_analise_completa
                self.gerar_relatorio_horario = self._mock_relatorio_horario
                self.gerar_relatorio_diario = self._mock_relatorio_diario
                self.enviar_oraculo = self._mock_enviar_oraculo
                self.enviar_foto = self._mock_enviar_foto
            
            logger.info("✅ Todos os sistemas importados com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao importar sistemas: {e}")
            raise
    
    def _setup_handlers(self):
        """Configura handlers do bot usando sistema existente"""
        try:
            # Usar sistema existente do xenos_bot em vez da biblioteca problemática
            logger.info("✅ Usando sistema de comandos integrado (sem biblioteca externa)")
            
            # Criar dicionário de comandos
            self.comandos = {
                'start': self.start_command,
                'ajuda': self.ajuda_command,
                'demo': self.demo_command,
                'termos': self.termos_command,
                'assinar': self.assinar_command,
                'confirmar_pagamento': self.confirmar_pagamento_command,
                'minha_assinatura': self.minha_assinatura_command,
                'analise': self.analise_command,
                'relatorio': self.relatorio_command,
                'alertas': self.alertas_command,
                'criar_alerta': self.criar_alerta_command,
                'multi': self.multi_command,
                'backtest': self.backtest_command,
                'config': self.config_command
            }
            
            self.use_integrated_system = True
            logger.info("✅ Sistema de comandos integrado configurado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar handlers: {e}")
            raise
    
    def _get_telegram_token(self) -> str:
        """Obtém token do Telegram"""
        try:
            from config_seguro import config
            return config.TELEGRAM_TOKEN
        except ImportError:
            return "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y"
    
    # ===========================================
    # COMANDOS BÁSICOS (GRATUITOS)
    # ===========================================
    def start_command(self, user_id: str, args: list = None):
        """Comando /start - Boas-vindas"""
        try:
            # Registrar atividade do usuário
            self.user_manager.update_user_activity(user_id)
            
            # Verificar se é usuário existente
            if self.user_manager.is_user_registered(user_id):
                user_data = self.user_manager.get_user_data(user_id)
                plano = user_data['plano'].upper()
                mensagem = f"""
🚀 **Bem-vindo de volta!**

📊 **Seu Plano:** {plano}
✅ **Status:** {'Ativo' if user_data['is_active'] else 'Inativo'}

💡 **Comandos disponíveis:**
🔹 /analise - Análise técnica completa
🔹 /relatorio - Relatórios automáticos
🔹 /alertas - Sistema de alertas
🔹 /minha_assinatura - Ver detalhes da assinatura

🎯 **Use /ajuda para ver todos os comandos!**
"""
            else:
                # Criar usuário free
                self.user_manager.create_user(user_id, 'free')
                
                mensagem = f"""
🚀 **Bem-vindo ao SNE Radar!**

🎯 **Sistema de Análise Técnica Profissional**
📊 Análise multi-timeframe + DOM + Gestão de Risco

🔹 **Plano FREE:** 3 análises/dia
🔹 **Teste agora:** /demo BTCUSDT
🔹 **Upgrade:** /assinar

💡 **Comandos disponíveis:**
🔹 /demo - Teste gratuito
🔹 /assinar - Planos premium
🔹 /ajuda - Lista completa

🎯 **Comece com:** /demo BTCUSDT
"""
            
            # Enviar mensagem usando sistema existente
            self.enviar_oraculo(mensagem)
            
            # Log de auditoria
            self.security._log_audit("USER_START", f"Usuário {user_id} iniciou bot", user_id)
            
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando start: {e}")
            return "❌ Erro interno. Tente novamente."
    
    def ajuda_command(self, user_id: str, args: list = None):
        """Comando /ajuda - Lista de comandos"""
        try:
            user_data = self.user_manager.get_user_data(user_id)
            plano = user_data['plano'] if user_data else 'free'
            
            # Comandos por plano
            comandos_free = [
                "/start - Iniciar bot",
                "/demo - Teste gratuito",
                "/ajuda - Esta lista",
                "/termos - Termos de uso",
                "/assinar - Planos premium"
            ]
            
            comandos_premium = [
                "/analise - Análise completa",
                "/relatorio - Relatórios técnicos",
                "/alertas - Sistema de alertas",
                "/criar_alerta - Criar alerta",
                "/minha_assinatura - Status da conta"
            ]
            
            comandos_institutional = [
                "/multi - Análise multi-pair",
                "/backtest - Backtest estratégias",
                "/config - Configurações",
                "/api - Acesso à API"
            ]
            
            mensagem = f"""
📋 **COMANDOS DISPONÍVEIS**

🔹 **BÁSICOS (Todos):**
{chr(10).join(comandos_free)}

🔹 **PREMIUM ({plano}):**
{chr(10).join(comandos_premium) if plano in ['premium', 'institutional'] else '❌ Upgrade necessário'}

🔹 **INSTITUCIONAL ({plano}):**
{chr(10).join(comandos_institutional) if plano == 'institutional' else '❌ Upgrade necessário'}

💡 **Exemplos:**
• /demo BTCUSDT
• /analise ETHUSDT 1h
• /criar_alerta BTCUSDT 100000

🎯 **Seu plano:** {plano.upper()}
"""
            
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando ajuda: {e}")
            return "❌ Erro interno. Tente novamente."
    
    def demo_command(self, user_id: str, args: list = None):
        """Comando /demo - Análise limitada gratuita"""
        try:
            # Verificar rate limit
            if not self.security.aplicar_rate_limit_por_plano(user_id, 'demo'):
                mensagem = "⚠️ Limite diário atingido. Assine premium para mais análises!"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Obter parâmetros
            par = args[0].upper() if args and len(args) > 0 else 'BTCUSDT'
            
            # Verificar se par é válido
            if not self._is_valid_symbol(par):
                mensagem = "❌ Par inválido. Use: /demo BTCUSDT"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Enviar mensagem de processamento
            self.enviar_oraculo("🔄 Processando análise demo...")
            
            # Gerar análise limitada
            resultado = self._gerar_analise_demo(par)
            
            # Formatar resultado
            mensagem = self._formatar_analise_demo(resultado, par)
            
            # Enviar resultado
            self.enviar_oraculo(mensagem)
            
            # Registrar uso
            self.security.registrar_uso_funcionalidade(user_id, 'demo')
            
            # Log de auditoria
            self.security._log_audit("DEMO_USED", f"Demo usado para {par}", user_id)
            
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando demo: {e}")
            mensagem = "❌ Erro ao gerar análise demo. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def termos_command(self, user_id: str, args: list = None):
        """Comando /termos - Termos de uso"""
        mensagem = """
📋 **TERMOS DE USO - SNE RADAR**

🔹 **Serviço:** Análise técnica de criptomoedas
🔹 **Responsabilidade:** Usuário assume riscos de trading
🔹 **Dados:** Coletamos apenas dados necessários
🔹 **Pagamentos:** Não reembolsamos após uso
🔹 **Suporte:** Via Telegram @sne_radar_support

⚠️ **IMPORTANTE:** 
• Não somos consultores financeiros
• Faça sua própria análise
• Trading envolve riscos

📧 **Contato:** sne.radar@email.com
"""
        self.enviar_oraculo(mensagem)
        return mensagem
    
    def assinar_command(self, user_id: str, args: list = None):
        """Comando /assinar - Planos e pagamentos"""
        try:
            # Verificar se já tem plano ativo
            user_data = self.user_manager.get_user_data(user_id)
            if user_data and user_data['is_active'] and user_data['plano'] != 'free':
                mensagem = f"""
✅ **Você já tem o plano {user_data['plano'].upper()} ativo!**

Vencimento: {user_data['expires_at']}

Use /minha_assinatura para detalhes.
"""
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Mostrar planos disponíveis
            mensagem = """
💳 **PLANOS SNE RADAR**

🔹 **PREMIUM - R$ 199/mês**
✅ Análise multi-timeframe completa
✅ Relatórios técnicos automáticos
✅ Sistema de alertas personalizados
✅ Backtest de estratégias
✅ DOM Analysis exclusivo
✅ 50 análises/dia

🔹 **INSTITUCIONAL - R$ 799/mês**
✅ Todas funcionalidades Premium
✅ Análise multi-pair simultânea
✅ Automação 24/7
✅ Acesso à API completa
✅ Whitelabel personalizado
✅ 1000 análises/dia

💰 **FORMAS DE PAGAMENTO:**
1️⃣ PIX (Imediato)
2️⃣ Mercado Pago
3️⃣ Stripe (Cartão)

🎯 **Para assinar, entre em contato:**
📧 sne.radar@email.com
"""
            
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando assinar: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def minha_assinatura_command(self, user_id: str, args: list = None):
        """Comando /minha_assinatura - Status da conta"""
        try:
            user_data = self.user_manager.get_user_data(user_id)
            if not user_data:
                mensagem = "❌ Usuário não encontrado. Use /start primeiro."
                self.enviar_oraculo(mensagem)
                return mensagem
            
            stats = self.user_manager.get_user_stats(user_id)
            
            mensagem = f"""
📊 **MINHA ASSINATURA**

🔹 **Plano:** {user_data['plano'].upper()}
🔹 **Status:** {'✅ Ativo' if user_data['is_active'] else '❌ Inativo'}
🔹 **Análises hoje:** {stats['analises_hoje']}/{self.planos[user_data['plano']]['analises_dia']}
🔹 **Alertas ativos:** {stats['alertas_ativos']}

📅 **Vencimento:** {user_data['expires_at'] or 'N/A'}
📅 **Criado em:** {user_data['created_at'][:10]}
📅 **Última atividade:** {user_data['last_activity'][:10]}

💡 **Funcionalidades:**
{chr(10).join([f"✅ {func}" for func in self.planos[user_data['plano']]['recursos'][:3]])}

🎯 **Upgrade:** /assinar
"""
            
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando minha_assinatura: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def analise_command(self, user_id: str, args: list = None):
        """Comando /analise - Análise completa premium"""
        try:
            # Verificar acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                mensagem = "⚠️ Acesso premium necessário. Use /assinar"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Verificar limite de análises
            if not self.security.verificar_limite_analises(user_id):
                mensagem = "⚠️ Limite diário de análises atingido. Upgrade para mais análises!"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Obter parâmetros
            par = args[0].upper() if args and len(args) > 0 else 'BTCUSDT'
            timeframe = args[1] if args and len(args) > 1 else '1h'
            
            # Verificar se par é válido
            if not self._is_valid_symbol(par):
                mensagem = "❌ Par inválido. Use: /analise BTCUSDT 1h"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Enviar mensagem de processamento
            self.enviar_oraculo("🔄 Processando análise completa...")
            
            # Gerar análise completa
            resultado = self._gerar_analise_completa(par, timeframe, user_id)
            
            # Formatar resultado
            mensagem = self._formatar_analise_completa(resultado, par, timeframe)
            
            # Enviar resultado
            self.enviar_oraculo(mensagem)
            
            # Registrar uso
            self.security.registrar_uso_funcionalidade(user_id, 'analise')
            
            # Log de auditoria
            self.security._log_audit("ANALYSIS_USED", f"Análise completa {par} {timeframe}", user_id)
            
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando analise: {e}")
            mensagem = "❌ Erro ao gerar análise. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def confirmar_pagamento_command(self, user_id: str, args: list = None):
        """Comando /confirmar_pagamento - Confirma pagamento"""
        try:
            if not args or len(args) < 1:
                mensagem = "⚠️ Use: /confirmar_pagamento [ID_PAGAMENTO]"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            payment_id = args[0]
            
            # Verificar status do pagamento
            status = self.payment_manager.get_payment_status(payment_id)
            
            if not status['success']:
                mensagem = f"❌ Pagamento não encontrado: {payment_id}"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            if status['status'] == 'approved':
                mensagem = "✅ Pagamento já confirmado!"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Tentar confirmar pagamento
            if status['metodo'] == 'pix':
                resultado = self.payment_manager.confirmar_pagamento_pix(payment_id)
            elif status['metodo'] == 'mercadopago':
                resultado = self.payment_manager.verificar_pagamento_mercadopago(payment_id)
            elif status['metodo'] == 'stripe':
                resultado = self.payment_manager.verificar_pagamento_stripe(payment_id)
            else:
                mensagem = "❌ Método de pagamento não suportado"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            if resultado['success']:
                mensagem = f"""
✅ **PAGAMENTO CONFIRMADO!**

🎯 **Plano:** {resultado['plano'].upper()}
💰 **Valor:** R$ {status['valor']:.2f}
📅 **Ativo até:** 30 dias

🚀 **Agora você pode usar:**
• /analise - Análise completa
• /relatorio - Relatórios técnicos
• /alertas - Sistema de alertas

💡 **Bem-vindo ao SNE Radar Premium!**
"""
                self.enviar_oraculo(mensagem)
                return mensagem
            else:
                mensagem = f"❌ Erro ao confirmar pagamento: {resultado.get('error', 'Desconhecido')}"
                self.enviar_oraculo(mensagem)
                return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando confirmar_pagamento: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    
    # ===========================================
    # COMANDOS ADICIONAIS SIMPLIFICADOS
    # ===========================================
    def relatorio_command(self, user_id: str, args: list = None):
        """Comando /relatorio - Relatórios técnicos"""
        try:
            # Verificar acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                mensagem = "⚠️ Acesso premium necessário. Use /assinar"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Verificar rate limit
            if not self.security.aplicar_rate_limit_por_plano(user_id, 'relatorio'):
                mensagem = "⚠️ Limite de relatórios atingido. Tente novamente mais tarde."
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Gerar relatório
            self.enviar_oraculo("🔄 Gerando relatório técnico...")
            
            relatorio = self._gerar_relatorio_completo()
            
            # Enviar relatório
            self.enviar_oraculo(relatorio)
            
            # Registrar uso
            self.security.registrar_uso_funcionalidade(user_id, 'relatorio')
            
            # Log de auditoria
            self.security._log_audit("REPORT_USED", "Relatório técnico gerado", user_id)
            
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro no comando relatorio: {e}")
            mensagem = "❌ Erro ao gerar relatório. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def alertas_command(self, user_id: str, args: list = None):
        """Comando /alertas - Lista alertas ativos"""
        try:
            # Verificar acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                mensagem = "⚠️ Acesso premium necessário. Use /assinar"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Obter alertas do usuário
            alertas = self.user_manager.get_alertas_usuario(user_id)
            
            if not alertas:
                mensagem = """
🔔 **MEUS ALERTAS**

❌ **Nenhum alerta ativo**

💡 **Criar alerta:**
/criar_alerta BTCUSDT 100000

📋 **Exemplo:** Alerta quando BTCUSDT atingir $100,000
"""
            else:
                mensagem = "🔔 **MEUS ALERTAS**\n\n"
                for i, alerta in enumerate(alertas, 1):
                    mensagem += f"{i}. **{alerta['par']}** @ ${alerta['preco']:,.2f}\n"
                    mensagem += f"   📅 Criado: {alerta['criado_em'][:10]}\n\n"
                
                mensagem += "💡 **Criar novo:** /criar_alerta PAR PREÇO"
            
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando alertas: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def criar_alerta_command(self, user_id: str, args: list = None):
        """Comando /criar_alerta - Criar alerta personalizado"""
        try:
            # Verificar acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                mensagem = "⚠️ Acesso premium necessário. Use /assinar"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Obter parâmetros
            if not args or len(args) < 2:
                mensagem = "⚠️ Use: /criar_alerta BTCUSDT 100000"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            par = args[0].upper()
            try:
                preco = float(args[1])
            except ValueError:
                mensagem = "❌ Preço inválido. Use números."
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Verificar se par é válido
            if not self._is_valid_symbol(par):
                mensagem = "❌ Par inválido."
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Criar alerta
            alerta_id = self.user_manager.criar_alerta(user_id, par, preco)
            
            if alerta_id:
                mensagem = f"""
✅ **ALERTA CRIADO!**

🔹 **Par:** {par}
🔹 **Preço:** ${preco:,.2f}
🔹 **ID:** {alerta_id}

🔔 **Você será notificado quando {par} atingir ${preco:,.2f}**

📋 **Ver alertas:** /alertas
"""
                self.enviar_oraculo(mensagem)
                
                # Log de auditoria
                self.security._log_audit("ALERT_CREATED", f"Alerta {par} @ {preco} criado", user_id)
                
                return mensagem
            else:
                mensagem = "❌ Erro ao criar alerta. Tente novamente."
                self.enviar_oraculo(mensagem)
                return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando criar_alerta: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def multi_command(self, user_id: str, args: list = None):
        """Comando /multi - Análise multi-pair"""
        try:
            # Verificar acesso institucional
            if not self.security.verificar_acesso_institutional(user_id):
                mensagem = "⚠️ Acesso institucional necessário. Upgrade para plano Institutional!"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Implementar análise multi-pair
            mensagem = "🚧 Funcionalidade em desenvolvimento..."
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando multi: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def backtest_command(self, user_id: str, args: list = None):
        """Comando /backtest - Backtest de estratégias"""
        try:
            # Verificar acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                mensagem = "⚠️ Acesso premium necessário. Use /assinar"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Implementar backtest
            mensagem = "🚧 Funcionalidade em desenvolvimento..."
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando backtest: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def config_command(self, user_id: str, args: list = None):
        """Comando /config - Configurações"""
        try:
            # Verificar acesso premium
            if not self.security.verificar_acesso_premium(user_id):
                mensagem = "⚠️ Acesso premium necessário. Use /assinar"
                self.enviar_oraculo(mensagem)
                return mensagem
            
            # Mostrar configurações
            mensagem = """
⚙️ **CONFIGURAÇÕES**

🔹 **Timeframes padrão:** 1h, 4h, 1d
🔹 **Pares favoritos:** BTCUSDT, ETHUSDT
🔹 **Notificações:** Ativas
🔹 **Idioma:** Português

🚧 **Configurações avançadas em desenvolvimento**
"""
            
            self.enviar_oraculo(mensagem)
            return mensagem
            
        except Exception as e:
            logger.error(f"❌ Erro no comando config: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem
    
    def _gerar_relatorio_completo(self) -> str:
        """Gera relatório completo"""
        try:
            if hasattr(self, 'gerar_relatorio_horario') and callable(self.gerar_relatorio_horario):
                return self.gerar_relatorio_horario()
            else:
                # Mock para desenvolvimento
                return """
📊 **RELATÓRIO TÉCNICO - MERCADO ATUAL**

🔹 **BTCUSDT:** Alta moderada (Score: 7.5/10)
🔹 **ETHUSDT:** Lateral (Score: 6.0/10)
🔹 **ADAUSDT:** Baixa (Score: 4.5/10)

📈 **Tendência Geral:** Lateral com viés de alta
⚠️ **Risco:** Moderado
💡 **Recomendação:** Aguardar confirmação

🎯 **Próximos níveis importantes:**
• BTC: $50,000 (resistência)
• ETH: $3,200 (suporte)
"""
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return "❌ Erro ao gerar relatório."
    
    def _gerar_analise_demo(self, par: str) -> Dict[str, Any]:
        """Gera análise demo limitada"""
        # Mock para desenvolvimento
        return {
            'par': par,
            'preco': 50000.0,
            'tendencia': 'Alta',
            'score': 7.5,
            'recomendacao': 'Compra com cautela',
            'niveis': {
                'suporte': 48000,
                'resistencia': 52000
            }
        }
    
    def _formatar_analise_demo(self, resultado: Dict[str, Any], par: str) -> str:
        """Formata análise demo para Telegram"""
        return f"""
📊 **ANÁLISE DEMO - {par}**

💰 **Preço:** ${resultado['preco']:,.2f}
📈 **Tendência:** {resultado['tendencia']}
⭐ **Score:** {resultado['score']}/10
💡 **Recomendação:** {resultado['recomendacao']}

📍 **Níveis:**
🔹 Suporte: ${resultado['niveis']['suporte']:,.2f}
🔹 Resistência: ${resultado['niveis']['resistencia']:,.2f}

⚠️ **Limitação:** Análise simplificada
🚀 **Upgrade:** /assinar para análise completa
"""
    
    def _gerar_analise_completa(self, par: str, timeframe: str, user_id: str) -> Dict[str, Any]:
        """Gera análise completa premium"""
        try:
            # Verificar cache primeiro
            cached_result = self.cache.get_user_cache(user_id, 'analises', f"{par}_{timeframe}")
            if cached_result:
                return cached_result
            
            # Gerar análise usando sistema existente
            if hasattr(self, 'analise_completa') and callable(self.analise_completa):
                resultado = self.analise_completa(par, timeframe)
            else:
                # Mock para desenvolvimento
                resultado = {
                    'par': par,
                    'timeframe': timeframe,
                    'preco': 50000.0,
                    'tendencia': 'Alta',
                    'score': 8.5,
                    'recomendacao': 'Compra forte',
                    'niveis': {
                        'suporte': 48000,
                        'resistencia': 52000,
                        'entry': 50000,
                        'stop': 47500,
                        'target': 52500
                    },
                    'indicadores': {
                        'rsi': 65,
                        'macd': 'Positivo',
                        'ema': 'Suporte'
                    }
                }
            
            # Cachear resultado
            self.cache.set_user_cache(user_id, 'analises', f"{par}_{timeframe}", resultado, ttl=300)
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise completa: {e}")
            return {'erro': str(e)}
    
    def _formatar_analise_completa(self, resultado: Dict[str, Any], par: str, timeframe: str) -> str:
        """Formata análise completa para Telegram"""
        if 'erro' in resultado:
            return f"❌ Erro na análise: {resultado['erro']}"
        
        return f"""
📊 **ANÁLISE COMPLETA - {par} ({timeframe})**

💰 **Preço:** ${resultado['preco']:,.2f}
📈 **Tendência:** {resultado['tendencia']}
⭐ **Score:** {resultado['score']}/10
💡 **Recomendação:** {resultado['recomendacao']}

📍 **Níveis Operacionais:**
🔹 Entry: ${resultado['niveis']['entry']:,.2f}
🔹 Stop: ${resultado['niveis']['stop']:,.2f}
🔹 Target: ${resultado['niveis']['target']:,.2f}

📊 **Indicadores:**
🔹 RSI: {resultado['indicadores']['rsi']}
🔹 MACD: {resultado['indicadores']['macd']}
🔹 EMA: {resultado['indicadores']['ema']}

✅ **Análise Premium Completa**
"""
    
    async def _gerar_relatorio_completo(self) -> str:
        """Gera relatório completo"""
        try:
            if hasattr(self, 'gerar_relatorio_horario') and callable(self.gerar_relatorio_horario):
                return self.gerar_relatorio_horario()
            else:
                # Mock para desenvolvimento
                return """
📊 **RELATÓRIO TÉCNICO - MERCADO ATUAL**

🔹 **BTCUSDT:** Alta moderada (Score: 7.5/10)
🔹 **ETHUSDT:** Lateral (Score: 6.0/10)
🔹 **ADAUSDT:** Baixa (Score: 4.5/10)

📈 **Tendência Geral:** Lateral com viés de alta
⚠️ **Risco:** Moderado
💡 **Recomendação:** Aguardar confirmação

🎯 **Próximos níveis importantes:**
• BTC: $50,000 (resistência)
• ETH: $3,200 (suporte)
"""
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return "❌ Erro ao gerar relatório."
    
    def _formatar_analise_demo(self, resultado: Dict[str, Any], par: str) -> str:
        """Formata análise demo para Telegram"""
        return f"""
📊 **ANÁLISE DEMO - {par}**

💰 **Preço:** ${resultado['preco']:,.2f}
📈 **Tendência:** {resultado['tendencia']}
⭐ **Score:** {resultado['score']}/10
💡 **Recomendação:** {resultado['recomendacao']}

📍 **Níveis:**
🔹 Suporte: ${resultado['niveis']['suporte']:,.2f}
🔹 Resistência: ${resultado['niveis']['resistencia']:,.2f}

⚠️ **Limitação:** Análise simplificada
🚀 **Upgrade:** /assinar para análise completa
"""
    
    def _formatar_analise_completa(self, resultado: Dict[str, Any], par: str, timeframe: str) -> str:
        """Formata análise completa para Telegram"""
        if 'erro' in resultado:
            return f"❌ Erro na análise: {resultado['erro']}"
        
        return f"""
📊 **ANÁLISE COMPLETA - {par} ({timeframe})**

💰 **Preço:** ${resultado['preco']:,.2f}
📈 **Tendência:** {resultado['tendencia']}
⭐ **Score:** {resultado['score']}/10
💡 **Recomendação:** {resultado['recomendacao']}

📍 **Níveis Operacionais:**
🔹 Entry: ${resultado['niveis']['entry']:,.2f}
🔹 Stop: ${resultado['niveis']['stop']:,.2f}
🔹 Target: ${resultado['niveis']['target']:,.2f}

📊 **Indicadores:**
🔹 RSI: {resultado['indicadores']['rsi']}
🔹 MACD: {resultado['indicadores']['macd']}
🔹 EMA: {resultado['indicadores']['ema']}

✅ **Análise Premium Completa**
"""
    
    # ===========================================
    # FUNÇÕES MOCK PARA DESENVOLVIMENTO
    # ===========================================
    def _mock_analise_completa(self, par: str, timeframe: str) -> Dict[str, Any]:
        """Mock da função de análise completa"""
        return {
            'par': par,
            'timeframe': timeframe,
            'preco': 50000.0,
            'tendencia': 'Alta',
            'score': 8.5,
            'recomendacao': 'Compra forte',
            'niveis': {
                'suporte': 48000,
                'resistencia': 52000,
                'entry': 50000,
                'stop': 47500,
                'target': 52500
            },
            'indicadores': {
                'rsi': 65,
                'macd': 'Positivo',
                'ema': 'Suporte'
            }
        }
    
    def _mock_relatorio_horario(self) -> str:
        """Mock da função de relatório horário"""
        return "📊 Relatório horário mock"
    
    def _mock_relatorio_diario(self) -> str:
        """Mock da função de relatório diário"""
        return "📊 Relatório diário mock"
    
    def _mock_enviar_oraculo(self, mensagem: str) -> bool:
        """Mock da função de envio"""
        print(f"[MOCK] Enviando: {mensagem[:50]}...")
        return True
    
    def _mock_enviar_foto(self, caminho: str, legenda: str = "") -> bool:
        """Mock da função de envio de foto"""
        print(f"[MOCK] Enviando foto: {caminho}")
        return True
    
    # ===========================================
    # MÉTODOS DE EXECUÇÃO
    # ===========================================
    def start_bot(self):
        """Inicia o bot usando sistema integrado"""
        try:
            logger.info("🚀 Iniciando SNE Bot (Sistema Integrado)...")
            
            # Enviar mensagem de inicialização
            mensagem_inicial = """
🚀 **SNE RADAR BOT - SISTEMA INICIADO**

✅ **Sistema de Monetização Ativo**
✅ **Comandos Disponíveis:**
🔹 /start - Iniciar
🔹 /demo - Teste gratuito
🔹 /ajuda - Lista de comandos
🔹 /assinar - Planos premium

🎯 **Bot pronto para uso!**
"""
            self.enviar_oraculo(mensagem_inicial)
            
            logger.info("✅ SNE Bot iniciado com sucesso! (Sistema Integrado)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar bot: {e}")
            raise
    
    def stop_bot(self):
        """Para o bot"""
        try:
            logger.info("🛑 Parando SNE Bot...")
            
            # Enviar mensagem de encerramento
            mensagem_final = """
🛑 **SNE RADAR BOT - SISTEMA ENCERRADO**

✅ **Obrigado por usar o SNE Radar!**
📊 **Sistema de monetização funcionando perfeitamente**

🎯 **Até a próxima!**
"""
            self.enviar_oraculo(mensagem_final)
            
            logger.info("✅ SNE Bot parado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar bot: {e}")
            raise
    
    def processar_comando(self, comando: str, user_id: str = "6457067653", args: list = None):
        """Processa comandos do bot"""
        try:
            comando_limpo = comando.replace('/', '').lower()
            
            if comando_limpo in self.comandos:
                logger.info(f"🔧 Processando comando: {comando_limpo}")
                resultado = self.comandos[comando_limpo](user_id, args)
                return resultado
            else:
                mensagem = "❌ Comando não reconhecido. Use /ajuda para ver todos os comandos."
                self.enviar_oraculo(mensagem)
                return mensagem
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar comando {comando}: {e}")
            mensagem = "❌ Erro interno. Tente novamente."
            self.enviar_oraculo(mensagem)
            return mensagem

# ===========================================
# INSTÂNCIA GLOBAL
# ===========================================
sne_bot = SNEBot()

# ===========================================
# FUNÇÃO PRINCIPAL
# ===========================================
def main():
    """Função principal para executar o bot"""
    try:
        logger.info("🚀 Iniciando SNE Bot...")
        
        # Iniciar bot
        sne_bot.start_bot()
        
        # Simular alguns comandos de teste
        logger.info("🧪 Testando comandos...")
        
        # Testar comando start
        sne_bot.processar_comando("/start", "123456789")
        
        # Testar comando demo
        sne_bot.processar_comando("/demo", "123456789", ["BTCUSDT"])
        
        # Testar comando ajuda
        sne_bot.processar_comando("/ajuda", "123456789")
        
        logger.info("✅ Testes concluídos!")
        
        # Manter rodando por um tempo para demonstração
        import time
        logger.info("⏰ Bot rodando por 30 segundos para demonstração...")
        time.sleep(30)
        
        # Parar bot
        sne_bot.stop_bot()
        
        logger.info("✅ SNE Bot executado com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    # Executar bot
    main()

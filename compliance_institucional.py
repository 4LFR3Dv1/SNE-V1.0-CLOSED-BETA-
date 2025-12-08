#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLIANCE INSTITUCIONAL - SNE RADAR
Sistema de compliance para relatórios institucionais
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from config_institucional import obter_config_institucional


class ComplianceInstitucional:
    """Sistema de compliance para relatórios institucionais"""
    
    def __init__(self):
        """Inicializa sistema de compliance"""
        self.config = obter_config_institucional()
        
        # Regulamentações suportadas
        self.regulamentacoes = {
            'MiFID_II': self._carregar_mifid_ii(),
            'ESMA': self._carregar_esma(),
            'Basel_III': self._carregar_basel_iii(),
            'IFRS': self._carregar_ifrs()
        }
        
        # Logs de compliance
        self.logs_compliance = []
        self.violacoes_detectadas = []
        
        # Métricas de compliance
        self.metricas_compliance = {
            'total_relatorios': 0,
            'relatorios_compliant': 0,
            'violacoes_detectadas': 0,
            'score_medio_compliance': 0.0
        }
    
    def validar_relatorio(self, relatorio: str, dados_institucionais: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida relatório contra regulamentações
        
        Args:
            relatorio: Conteúdo do relatório
            dados_institucionais: Dados institucionais
            
        Returns:
            Dict com resultado da validação
        """
        try:
            print("🔍 Validando compliance do relatório...")
            
            # Inicializar resultado
            resultado = {
                'valido': True,
                'score_compliance': 100.0,
                'validacoes': [],
                'violacoes': [],
                'avisos': [],
                'timestamp': datetime.now().isoformat(),
                'regulamentacoes': {}
            }
            
            # Validar cada regulamentação
            scores_regulamentacoes = []
            for reg_name, reg_config in self.regulamentacoes.items():
                validacao_reg = self._validar_regulamentacao(reg_name, reg_config, relatorio, dados_institucionais)
                resultado['regulamentacoes'][reg_name] = validacao_reg
                
                # Atualizar resultado geral
                if not validacao_reg['valido']:
                    resultado['valido'] = False
                
                scores_regulamentacoes.append(validacao_reg['score'])
                resultado['validacoes'].extend(validacao_reg['validacoes'])
                resultado['violacoes'].extend(validacao_reg['violacoes'])
                resultado['avisos'].extend(validacao_reg['avisos'])
            
            # Calcular score médio das regulamentações
            if scores_regulamentacoes:
                resultado['score_compliance'] = sum(scores_regulamentacoes) / len(scores_regulamentacoes)
            else:
                resultado['score_compliance'] = 0.0
            
            # Validar estrutura geral
            validacao_estrutura = self._validar_estrutura_geral(relatorio, dados_institucionais)
            resultado.update(validacao_estrutura)
            
            # Atualizar métricas
            self._atualizar_metricas_compliance(resultado)
            
            # Registrar log
            self._registrar_log_compliance(resultado)
            
            print(f"✅ Compliance validado: {resultado['score_compliance']:.1f}%")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Erro na validação de compliance: {e}")
            return self._gerar_resultado_erro(str(e))
    
    def _validar_regulamentacao(self, reg_name: str, reg_config: Dict[str, Any], relatorio: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida contra uma regulamentação específica"""
        validacoes = []
        violacoes = []
        avisos = []
        
        if reg_name == 'MiFID_II':
            return self._validar_mifid_ii(relatorio, dados)
        elif reg_name == 'ESMA':
            return self._validar_esma(relatorio, dados)
        elif reg_name == 'Basel_III':
            return self._validar_basel_iii(relatorio, dados)
        elif reg_name == 'IFRS':
            return self._validar_ifrs(relatorio, dados)
        else:
            return {
                'valido': False,
                'score': 0.0,
                'validacoes': [],
                'violacoes': ['Regulamentação não reconhecida'],
                'avisos': []
            }
    
    def _validar_mifid_ii(self, relatorio: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida MiFID II - Transparência de preços e melhor execução"""
        validacoes = []
        violacoes = []
        avisos = []
        
        # 1. Transparência de preços
        if 'Price transparency' in relatorio or 'price transparency' in relatorio:
            validacoes.append("✅ MiFID II - Price Transparency")
        else:
            violacoes.append("❌ MiFID II - Price transparency não mencionada")
        
        # 2. Melhor execução
        if 'best execution' in relatorio.lower() or 'melhor execução' in relatorio.lower():
            validacoes.append("✅ MiFID II - Best Execution")
        else:
            avisos.append("⚠️ MiFID II - Best execution não mencionada")
        
        # 3. Categorização de cliente
        if dados.get('metadata', {}).get('classification') == 'INTERNAL USE ONLY':
            validacoes.append("✅ MiFID II - Client Categorization")
        else:
            violacoes.append("❌ MiFID II - Classificação de cliente inadequada")
        
        # 4. Divulgação de conflitos
        if 'disclaimer' in relatorio.lower() or 'conflito' in relatorio.lower():
            validacoes.append("✅ MiFID II - Conflict Disclosure")
        else:
            avisos.append("⚠️ MiFID II - Divulgação de conflitos não clara")
        
        # 5. Informações sobre produtos
        if 'risk' in relatorio.lower() and 'trading' in relatorio.lower():
            validacoes.append("✅ MiFID II - Product Information")
        else:
            violacoes.append("❌ MiFID II - Informações sobre produtos insuficientes")
        
        # Calcular score
        total_checks = len(validacoes) + len(violacoes) + len(avisos)
        score = (len(validacoes) / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'valido': len(violacoes) == 0,
            'score': score,
            'validacoes': validacoes,
            'violacoes': violacoes,
            'avisos': avisos
        }
    
    def _validar_esma(self, relatorio: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida ESMA - Gestão de risco e limites de posição"""
        validacoes = []
        violacoes = []
        avisos = []
        
        # 1. Gestão de risco
        if 'risk management' in relatorio.lower() or 'gestão de risco' in relatorio.lower():
            validacoes.append("✅ ESMA - Risk Management")
        else:
            violacoes.append("❌ ESMA - Gestão de risco não mencionada")
        
        # 2. Limites de posição
        risco = dados.get('risk_assessment', {})
        position_size = risco.get('position_size', 0)
        
        if position_size <= 5.0:  # Máximo 5% por posição
            validacoes.append("✅ ESMA - Position Limits")
        else:
            violacoes.append(f"❌ ESMA - Limite de posição excedido: {position_size}%")
        
        # 3. Relatórios de risco
        if 'risk assessment' in relatorio.lower() or 'avaliação de risco' in relatorio.lower():
            validacoes.append("✅ ESMA - Risk Reporting")
        else:
            violacoes.append("❌ ESMA - Relatório de risco ausente")
        
        # 4. Monitoramento de risco
        if 'monitoring' in relatorio.lower() or 'monitoramento' in relatorio.lower():
            validacoes.append("✅ ESMA - Risk Monitoring")
        else:
            avisos.append("⚠️ ESMA - Monitoramento de risco não mencionado")
        
        # 5. Controles de risco
        if 'controls' in relatorio.lower() or 'controles' in relatorio.lower():
            validacoes.append("✅ ESMA - Risk Controls")
        else:
            avisos.append("⚠️ ESMA - Controles de risco não mencionados")
        
        # Calcular score
        total_checks = len(validacoes) + len(violacoes) + len(avisos)
        score = (len(validacoes) / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'valido': len(violacoes) == 0,
            'score': score,
            'validacoes': validacoes,
            'violacoes': violacoes,
            'avisos': avisos
        }
    
    def _validar_basel_iii(self, relatorio: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida Basel III - Adequação de capital e liquidez"""
        validacoes = []
        violacoes = []
        avisos = []
        
        # 1. Adequação de capital
        risco = dados.get('risk_assessment', {})
        risk_score = risco.get('risk_score', 0)
        
        if risk_score <= 7.0:  # Risco controlado
            validacoes.append("✅ Basel III - Capital Adequacy")
        else:
            violacoes.append(f"❌ Basel III - Risco de capital alto: {risk_score}/10")
        
        # 2. Cobertura de liquidez
        contexto = dados.get('market_context', {})
        liquidity_score = contexto.get('liquidity_score', 0)
        
        if liquidity_score >= 6.0:
            validacoes.append("✅ Basel III - Liquidity Coverage")
        else:
            avisos.append(f"⚠️ Basel III - Liquidez baixa: {liquidity_score}/10")
        
        # 3. Razão de alavancagem
        position_size = risco.get('position_size', 0)
        if position_size <= 3.0:  # Máximo 3% para Basel III
            validacoes.append("✅ Basel III - Leverage Ratio")
        else:
            avisos.append(f"⚠️ Basel III - Alavancagem alta: {position_size}%")
        
        # 4. Gestão de liquidez
        if 'liquidity' in relatorio.lower() or 'liquidez' in relatorio.lower():
            validacoes.append("✅ Basel III - Liquidity Management")
        else:
            avisos.append("⚠️ Basel III - Gestão de liquidez não mencionada")
        
        # 5. Controles de risco
        if 'risk controls' in relatorio.lower() or 'controles de risco' in relatorio.lower():
            validacoes.append("✅ Basel III - Risk Controls")
        else:
            avisos.append("⚠️ Basel III - Controles de risco não mencionados")
        
        # Calcular score
        total_checks = len(validacoes) + len(violacoes) + len(avisos)
        score = (len(validacoes) / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'valido': len(violacoes) == 0,
            'score': score,
            'validacoes': validacoes,
            'violacoes': violacoes,
            'avisos': avisos
        }
    
    def _validar_ifrs(self, relatorio: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida IFRS - Padrões contábeis internacionais"""
        validacoes = []
        violacoes = []
        avisos = []
        
        # 1. Valor justo
        if 'fair value' in relatorio.lower() or 'valor justo' in relatorio.lower():
            validacoes.append("✅ IFRS - Fair Value")
        else:
            avisos.append("⚠️ IFRS - Valor justo não mencionado")
        
        # 2. Impairment
        if 'impairment' in relatorio.lower() or 'perda' in relatorio.lower():
            validacoes.append("✅ IFRS - Impairment")
        else:
            avisos.append("⚠️ IFRS - Impairment não mencionado")
        
        # 3. Divulgação
        if 'disclosure' in relatorio.lower() or 'divulgação' in relatorio.lower():
            validacoes.append("✅ IFRS - Disclosure")
        else:
            avisos.append("⚠️ IFRS - Divulgação não mencionada")
        
        # 4. Reconhecimento de receita
        if 'revenue' in relatorio.lower() or 'receita' in relatorio.lower():
            validacoes.append("✅ IFRS - Revenue Recognition")
        else:
            avisos.append("⚠️ IFRS - Reconhecimento de receita não mencionado")
        
        # 5. Medição de instrumentos financeiros
        if 'financial instruments' in relatorio.lower() or 'instrumentos financeiros' in relatorio.lower():
            validacoes.append("✅ IFRS - Financial Instruments")
        else:
            avisos.append("⚠️ IFRS - Instrumentos financeiros não mencionados")
        
        # Calcular score
        total_checks = len(validacoes) + len(violacoes) + len(avisos)
        score = (len(validacoes) / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'valido': len(violacoes) == 0,
            'score': score,
            'validacoes': validacoes,
            'violacoes': violacoes,
            'avisos': avisos
        }
    
    def _validar_estrutura_geral(self, relatorio: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estrutura geral do relatório"""
        validacoes = []
        violacoes = []
        avisos = []
        
        # 1. Metadados obrigatórios
        metadata = dados.get('metadata', {})
        campos_obrigatorios = ['report_id', 'classification', 'generated', 'analyst']
        
        for campo in campos_obrigatorios:
            if campo in metadata and metadata[campo]:
                validacoes.append(f"✅ Metadata - {campo}")
            else:
                violacoes.append(f"❌ Metadata - {campo} ausente")
        
        # 2. Seções obrigatórias
        secoes_obrigatorias = [
            'EXECUTIVE SUMMARY',
            'MARKET CONTEXT',
            'TECHNICAL ANALYSIS',
            'RISK ASSESSMENT',
            'COMPLIANCE'
        ]
        
        for secao in secoes_obrigatorias:
            if secao in relatorio:
                validacoes.append(f"✅ Seção - {secao}")
            else:
                violacoes.append(f"❌ Seção - {secao} ausente")
        
        # 3. Tamanho mínimo do relatório
        if len(relatorio) >= 1000:
            validacoes.append("✅ Tamanho - Relatório adequado")
        else:
            violacoes.append("❌ Tamanho - Relatório muito pequeno")
        
        # 4. Data de validade
        if 'valid until' in relatorio.lower() or 'válido até' in relatorio.lower():
            validacoes.append("✅ Validade - Data de expiração")
        else:
            avisos.append("⚠️ Validade - Data de expiração não clara")
        
        # 5. Disclaimer
        if 'disclaimer' in relatorio.lower() or 'aviso' in relatorio.lower():
            validacoes.append("✅ Disclaimer - Aviso legal")
        else:
            avisos.append("⚠️ Disclaimer - Aviso legal não encontrado")
        
        return {
            'validacoes': validacoes,
            'violacoes': violacoes,
            'avisos': avisos
        }
    
    def _carregar_mifid_ii(self) -> Dict[str, Any]:
        """Carrega configuração MiFID II"""
        return {
            'price_transparency': True,
            'best_execution': True,
            'client_categorization': True,
            'conflict_disclosure': True,
            'product_information': True
        }
    
    def _carregar_esma(self) -> Dict[str, Any]:
        """Carrega configuração ESMA"""
        return {
            'risk_management': True,
            'position_limits': True,
            'risk_reporting': True,
            'risk_monitoring': True,
            'risk_controls': True
        }
    
    def _carregar_basel_iii(self) -> Dict[str, Any]:
        """Carrega configuração Basel III"""
        return {
            'capital_adequacy': True,
            'liquidity_coverage': True,
            'leverage_ratio': True,
            'liquidity_management': True,
            'risk_controls': True
        }
    
    def _carregar_ifrs(self) -> Dict[str, Any]:
        """Carrega configuração IFRS"""
        return {
            'fair_value': True,
            'impairment': True,
            'disclosure': True,
            'revenue_recognition': True,
            'financial_instruments': True
        }
    
    def _atualizar_metricas_compliance(self, resultado: Dict[str, Any]):
        """Atualiza métricas de compliance"""
        self.metricas_compliance['total_relatorios'] += 1
        
        if resultado['valido']:
            self.metricas_compliance['relatorios_compliant'] += 1
        
        if resultado['violacoes']:
            self.metricas_compliance['violacoes_detectadas'] += len(resultado['violacoes'])
        
        # Atualizar score médio
        total_score = self.metricas_compliance['score_medio_compliance'] * (self.metricas_compliance['total_relatorios'] - 1)
        total_score += resultado['score_compliance']
        self.metricas_compliance['score_medio_compliance'] = total_score / self.metricas_compliance['total_relatorios']
    
    def _registrar_log_compliance(self, resultado: Dict[str, Any]):
        """Registra log de compliance"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'resultado': resultado,
            'metricas': self.metricas_compliance.copy()
        }
        
        self.logs_compliance.append(log_entry)
        
        # Salvar em arquivo
        self._salvar_log_compliance(log_entry)
    
    def _salvar_log_compliance(self, log_entry: Dict[str, Any]):
        """Salva log de compliance em arquivo"""
        log_path = os.path.join(self.config.diretorio_compliance, f"compliance_{datetime.now().strftime('%Y%m%d')}.json")
        
        try:
            logs_existentes = []
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs_existentes = json.load(f)
            
            logs_existentes.append(log_entry)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(logs_existentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar log de compliance: {e}")
    
    def _gerar_resultado_erro(self, erro: str) -> Dict[str, Any]:
        """Gera resultado de erro"""
        return {
            'valido': False,
            'score_compliance': 0.0,
            'validacoes': [],
            'violacoes': [f"Erro na validação: {erro}"],
            'avisos': [],
            'timestamp': datetime.now().isoformat(),
            'regulamentacoes': {},
            'erro': True
        }
    
    def gerar_relatorio_compliance(self) -> str:
        """Gera relatório de compliance"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Calcular estatísticas
        total_relatorios = self.metricas_compliance['total_relatorios']
        relatorios_compliant = self.metricas_compliance['relatorios_compliant']
        violacoes_total = self.metricas_compliance['violacoes_detectadas']
        score_medio = self.metricas_compliance['score_medio_compliance']
        
        compliance_rate = (relatorios_compliant / total_relatorios * 100) if total_relatorios > 0 else 0
        
        return f"""
{'='*80}
🏛️ RELATÓRIO DE COMPLIANCE INSTITUCIONAL - SNE RADAR
{'='*80}
📅 Data: {timestamp}
📊 Status: {'ATIVO' if self.config.compliance_obrigatorio else 'INATIVO'}

📈 MÉTRICAS DE COMPLIANCE:
├── Total de Relatórios: {total_relatorios}
├── Relatórios Compliant: {relatorios_compliant} ({compliance_rate:.1f}%)
├── Violações Detectadas: {violacoes_total}
└── Score Médio: {score_medio:.1f}%

🔧 REGULAMENTAÇÕES MONITORADAS:
├── MiFID II: {'✅ ATIVO' if 'MiFID_II' in self.regulamentacoes else '❌ INATIVO'}
├── ESMA: {'✅ ATIVO' if 'ESMA' in self.regulamentacoes else '❌ INATIVO'}
├── Basel III: {'✅ ATIVO' if 'Basel_III' in self.regulamentacoes else '❌ INATIVO'}
└── IFRS: {'✅ ATIVO' if 'IFRS' in self.regulamentacoes else '❌ INATIVO'}

📋 CONFIGURAÇÕES:
├── Compliance Obrigatório: {'SIM' if self.config.compliance_obrigatorio else 'NÃO'}
├── Auditoria Ativa: {'SIM' if self.config.auditoria_obrigatoria else 'NÃO'}
├── Métricas de Qualidade: {'SIM' if self.config.metricas_qualidade else 'NÃO'}
└── Notificações: {'SIM' if self.config.notificacoes_compliance else 'NÃO'}

📊 ÚLTIMOS LOGS:
{self._formatar_ultimos_logs()}

🎯 RECOMENDAÇÕES:
{self._gerar_recomendacoes_compliance()}
{'='*80}
"""
    
    def _formatar_ultimos_logs(self) -> str:
        """Formata últimos logs de compliance"""
        if not self.logs_compliance:
            return "• Nenhum log disponível"
        
        logs_recentes = self.logs_compliance[-5:]  # Últimos 5 logs
        formatted = []
        
        for log in logs_recentes:
            timestamp = log['timestamp'][:19]  # Remover microsegundos
            score = log['resultado'].get('score_compliance', 0)
            valido = log['resultado'].get('valido', False)
            status = "✅ COMPLIANT" if valido else "❌ NON-COMPLIANT"
            
            formatted.append(f"• {timestamp}: {status} ({score:.1f}%)")
        
        return "\n".join(formatted)
    
    def _gerar_recomendacoes_compliance(self) -> str:
        """Gera recomendações de compliance"""
        recomendacoes = []
        
        # Verificar score médio
        if self.metricas_compliance['score_medio_compliance'] < 90:
            recomendacoes.append("• Score médio baixo - Revisar processos de compliance")
        
        # Verificar taxa de compliance
        total_relatorios = self.metricas_compliance['total_relatorios']
        relatorios_compliant = self.metricas_compliance['relatorios_compliant']
        
        if total_relatorios > 0:
            compliance_rate = relatorios_compliant / total_relatorios * 100
            if compliance_rate < 95:
                recomendacoes.append("• Taxa de compliance baixa - Implementar controles adicionais")
        
        # Verificar violações
        if self.metricas_compliance['violacoes_detectadas'] > 0:
            recomendacoes.append("• Violações detectadas - Investigar causas raiz")
        
        if not recomendacoes:
            recomendacoes.append("• Sistema de compliance funcionando adequadamente")
        
        return "\n".join(recomendacoes)
    
    def obter_metricas_compliance(self) -> Dict[str, Any]:
        """Retorna métricas de compliance"""
        return self.metricas_compliance.copy()
    
    def limpar_logs_antigos(self, dias_retention: int = 30):
        """Limpa logs antigos"""
        cutoff_date = datetime.now() - timedelta(days=dias_retention)
        
        logs_filtrados = []
        for log in self.logs_compliance:
            log_date = datetime.fromisoformat(log['timestamp'])
            if log_date >= cutoff_date:
                logs_filtrados.append(log)
        
        self.logs_compliance = logs_filtrados
        print(f"✅ Logs antigos removidos. Mantidos: {len(logs_filtrados)} logs")


# Instância global do sistema de compliance
compliance_institucional = ComplianceInstitucional()


def obter_compliance_institucional() -> ComplianceInstitucional:
    """Retorna instância global do sistema de compliance"""
    return compliance_institucional


if __name__ == "__main__":
    # Teste do sistema de compliance
    compliance = obter_compliance_institucional()
    
    # Relatório de teste
    relatorio_teste = """
    EXECUTIVE SUMMARY
    Market Regime: BULL_TREND with STRONG strength
    Risk Level: 4.5/10 (MEDIUM)
    Recommendation: BUY with HIGH confidence
    
    MARKET CONTEXT & REGIME ANALYSIS
    Risk management guidelines followed
    Position limits respected
    
    TECHNICAL ANALYSIS
    Risk assessment completed
    
    RISK ASSESSMENT
    Position size: 2.0% of portfolio
    Stop loss: $41,800
    Risk controls implemented
    
    COMPLIANCE & REGULATORY NOTES
    MiFID II requirements met
    ESMA guidelines followed
    Basel III compliance maintained
    IFRS standards applied
    Disclaimer: Trading involves risk
    """
    
    # Dados institucionais de teste
    dados_teste = {
        'metadata': {
            'report_id': 'SNE-TEST-001',
            'classification': 'INTERNAL USE ONLY',
            'generated': datetime.now().isoformat(),
            'analyst': 'SNE-AI-SYSTEM v2.1'
        },
        'risk_assessment': {
            'position_size': 2.0,
            'risk_score': 4.5
        },
        'market_context': {
            'liquidity_score': 8
        }
    }
    
    # Validar compliance
    resultado = compliance.validar_relatorio(relatorio_teste, dados_teste)
    
    print("✅ Sistema de compliance testado com sucesso!")
    print(f"📊 Score de compliance: {resultado['score_compliance']:.1f}%")
    print(f"✅ Válido: {resultado['valido']}")
    print(f"📋 Validações: {len(resultado['validacoes'])}")
    print(f"❌ Violações: {len(resultado['violacoes'])}")
    print(f"⚠️ Avisos: {len(resultado['avisos'])}")
    
    # Gerar relatório de compliance
    relatorio_compliance = compliance.gerar_relatorio_compliance()
    print("\n" + relatorio_compliance)









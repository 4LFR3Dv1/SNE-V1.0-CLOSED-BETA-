#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURAÇÕES INSTITUCIONAIS - SNE RADAR
Sistema de configurações para modo institucional
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any


class ConfigInstitucional:
    """Configurações para modo institucional"""
    
    def __init__(self):
        """Inicializa configurações institucionais"""
        self.modo_ativo = True
        self.compliance_obrigatorio = True
        self.auditoria_obrigatoria = True
        self.metricas_qualidade = True
        
        # Diretórios
        self.diretorio_relatorios = "reports/institutional/"
        self.diretorio_compliance = "reports/compliance/"
        self.diretorio_auditoria = "reports/audit/"
        self.diretorio_logs = "logs/institutional/"
        
        # Configurações de compliance
        self.regulamentacoes = [
            'MiFID_II',
            'ESMA',
            'Basel_III',
            'IFRS'
        ]
        
        # Limites de qualidade
        self.score_minimo_qualidade = 85.0
        self.confluencia_minima = 7.0
        self.risco_maximo = 5.0
        
        # Configurações de formatação
        self.template_institucional = self._carregar_template_institucional()
        self.cores_institucionais = self._definir_cores_institucionais()
        self.tipografia_institucional = self._definir_tipografia()
        
        # Configurações de auditoria
        self.retencao_logs_dias = 365
        self.backup_automatico = True
        self.criptografia_logs = True
        
        # Configurações de performance
        self.cache_timeout_minutos = 5
        self.max_concurrent_reports = 10
        self.timeout_api_segundos = 30
        
        # Configurações de notificação
        self.notificacoes_compliance = True
        self.notificacoes_auditoria = True
        self.notificacoes_qualidade = True
        
        # Inicializar diretórios
        self._inicializar_diretorios()
    
    def _carregar_template_institucional(self) -> Dict[str, Any]:
        """Carrega template institucional padrão"""
        return {
            'cabecalho': {
                'titulo': 'SNE RADAR INSTITUTIONAL',
                'subtitulo': 'TRADING DESK REPORT',
                'separador': '=' * 80,
                'classificacao': 'INTERNAL USE ONLY'
            },
            'secoes': [
                'EXECUTIVE SUMMARY',
                'MARKET CONTEXT & REGIME ANALYSIS',
                'TECHNICAL ANALYSIS MULTI-TIMEFRAME',
                'RISK ASSESSMENT & POSITION SIZING',
                'TRADE RECOMMENDATIONS & EXECUTION PLAN',
                'COMPLIANCE & REGULATORY NOTES',
                'APPENDIX: DETAILED CALCULATIONS'
            ],
            'metadados': [
                'Report ID',
                'Classification',
                'Generated',
                'Valid Until',
                'Analyst',
                'Compliance'
            ]
        }
    
    def _definir_cores_institucionais(self) -> Dict[str, str]:
        """Define paleta de cores institucionais"""
        return {
            'primary': '#1E3A8A',      # Navy Blue
            'secondary': '#059669',    # Professional Green
            'accent': '#DC2626',       # Alert Red
            'neutral': '#6B7280',       # Gray
            'background': '#F9FAFB',   # Light Gray
            'success': '#10B981',      # Success Green
            'warning': '#F59E0B',      # Warning Orange
            'error': '#EF4444'         # Error Red
        }
    
    def _definir_tipografia(self) -> Dict[str, str]:
        """Define tipografia institucional"""
        return {
            'headers': 'Inter Bold, 16px',
            'body': 'Inter Regular, 14px',
            'data': 'JetBrains Mono, 13px',
            'labels': 'Inter Medium, 12px',
            'captions': 'Inter Light, 11px'
        }
    
    def _inicializar_diretorios(self):
        """Inicializa diretórios necessários"""
        diretorios = [
            self.diretorio_relatorios,
            self.diretorio_compliance,
            self.diretorio_auditoria,
            self.diretorio_logs
        ]
        
        for diretorio in diretorios:
            if not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
                print(f"✅ Diretório criado: {diretorio}")
    
    def obter_configuracao_completa(self) -> Dict[str, Any]:
        """Retorna configuração completa"""
        return {
            'modo_ativo': self.modo_ativo,
            'compliance_obrigatorio': self.compliance_obrigatorio,
            'auditoria_obrigatoria': self.auditoria_obrigatoria,
            'metricas_qualidade': self.metricas_qualidade,
            'diretorios': {
                'relatorios': self.diretorio_relatorios,
                'compliance': self.diretorio_compliance,
                'auditoria': self.diretorio_auditoria,
                'logs': self.diretorio_logs
            },
            'regulamentacoes': self.regulamentacoes,
            'limites_qualidade': {
                'score_minimo': self.score_minimo_qualidade,
                'confluencia_minima': self.confluencia_minima,
                'risco_maximo': self.risco_maximo
            },
            'template': self.template_institucional,
            'cores': self.cores_institucionais,
            'tipografia': self.tipografia_institucional,
            'auditoria': {
                'retencao_logs_dias': self.retencao_logs_dias,
                'backup_automatico': self.backup_automatico,
                'criptografia_logs': self.criptografia_logs
            },
            'performance': {
                'cache_timeout_minutos': self.cache_timeout_minutos,
                'max_concurrent_reports': self.max_concurrent_reports,
                'timeout_api_segundos': self.timeout_api_segundos
            },
            'notificacoes': {
                'compliance': self.notificacoes_compliance,
                'auditoria': self.notificacoes_auditoria,
                'qualidade': self.notificacoes_qualidade
            }
        }
    
    def salvar_configuracao(self, caminho: str = "config_institucional.json"):
        """Salva configuração em arquivo JSON"""
        config = self.obter_configuracao_completa()
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuração salva: {caminho}")
    
    def carregar_configuracao(self, caminho: str = "config_institucional.json"):
        """Carrega configuração de arquivo JSON"""
        if not os.path.exists(caminho):
            print(f"⚠️ Arquivo de configuração não encontrado: {caminho}")
            return False
        
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Aplicar configurações
            self.modo_ativo = config.get('modo_ativo', True)
            self.compliance_obrigatorio = config.get('compliance_obrigatorio', True)
            self.auditoria_obrigatoria = config.get('auditoria_obrigatoria', True)
            self.metricas_qualidade = config.get('metricas_qualidade', True)
            
            # Diretórios
            diretorios = config.get('diretorios', {})
            self.diretorio_relatorios = diretorios.get('relatorios', 'reports/institutional/')
            self.diretorio_compliance = diretorios.get('compliance', 'reports/compliance/')
            self.diretorio_auditoria = diretorios.get('auditoria', 'reports/audit/')
            self.diretorio_logs = diretorios.get('logs', 'logs/institutional/')
            
            # Limites de qualidade
            limites = config.get('limites_qualidade', {})
            self.score_minimo_qualidade = limites.get('score_minimo', 85.0)
            self.confluencia_minima = limites.get('confluencia_minima', 7.0)
            self.risco_maximo = limites.get('risco_maximo', 5.0)
            
            print(f"✅ Configuração carregada: {caminho}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
            return False
    
    def validar_configuracao(self) -> List[str]:
        """Valida configuração atual"""
        validacoes = []
        
        # Validar diretórios
        diretorios = [
            self.diretorio_relatorios,
            self.diretorio_compliance,
            self.diretorio_auditoria,
            self.diretorio_logs
        ]
        
        for diretorio in diretorios:
            if os.path.exists(diretorio):
                validacoes.append(f"✅ Diretório existe: {diretorio}")
            else:
                validacoes.append(f"❌ Diretório não existe: {diretorio}")
        
        # Validar limites
        if self.score_minimo_qualidade >= 80.0:
            validacoes.append(f"✅ Score mínimo adequado: {self.score_minimo_qualidade}%")
        else:
            validacoes.append(f"⚠️ Score mínimo baixo: {self.score_minimo_qualidade}%")
        
        if self.confluencia_minima >= 6.0:
            validacoes.append(f"✅ Confluência mínima adequada: {self.confluencia_minima}")
        else:
            validacoes.append(f"⚠️ Confluência mínima baixa: {self.confluencia_minima}")
        
        if self.risco_maximo <= 10.0:
            validacoes.append(f"✅ Risco máximo adequado: {self.risco_maximo}")
        else:
            validacoes.append(f"⚠️ Risco máximo alto: {self.risco_maximo}")
        
        return validacoes
    
    def gerar_relatorio_configuracao(self) -> str:
        """Gera relatório de configuração atual"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        relatorio = f"""
{'='*80}
🏛️ CONFIGURAÇÃO INSTITUCIONAL - SNE RADAR
{'='*80}
📅 Data: {timestamp}
📊 Status: {'ATIVO' if self.modo_ativo else 'INATIVO'}

📁 DIRETÓRIOS:
├── Relatórios: {self.diretorio_relatorios}
├── Compliance: {self.diretorio_compliance}
├── Auditoria: {self.diretorio_auditoria}
└── Logs: {self.diretorio_logs}

📋 COMPLIANCE:
├── Obrigatório: {'SIM' if self.compliance_obrigatorio else 'NÃO'}
├── Auditoria: {'SIM' if self.auditoria_obrigatoria else 'NÃO'}
└── Métricas: {'SIM' if self.metricas_qualidade else 'NÃO'}

📊 LIMITES DE QUALIDADE:
├── Score Mínimo: {self.score_minimo_qualidade}%
├── Confluência Mínima: {self.confluencia_minima}
└── Risco Máximo: {self.risco_maximo}

🔧 REGULAMENTAÇÕES:
{chr(10).join([f'├── {reg}' for reg in self.regulamentacoes])}

📈 PERFORMANCE:
├── Cache Timeout: {self.cache_timeout_minutos} min
├── Max Concurrent: {self.max_concurrent_reports}
└── API Timeout: {self.timeout_api_segundos} seg

🔔 NOTIFICAÇÕES:
├── Compliance: {'SIM' if self.notificacoes_compliance else 'NÃO'}
├── Auditoria: {'SIM' if self.notificacoes_auditoria else 'NÃO'}
└── Qualidade: {'SIM' if self.notificacoes_qualidade else 'NÃO'}
{'='*80}
"""
        
        return relatorio


# Instância global de configuração
config_institucional = ConfigInstitucional()


def obter_config_institucional() -> ConfigInstitucional:
    """Retorna instância global de configuração institucional"""
    return config_institucional


def inicializar_config_institucional():
    """Inicializa configuração institucional"""
    print("🏛️ Inicializando configuração institucional...")
    
    # Carregar configuração existente ou criar nova
    if not config_institucional.carregar_configuracao():
        print("📝 Criando nova configuração institucional...")
        config_institucional.salvar_configuracao()
    
    # Validar configuração
    validacoes = config_institucional.validar_configuracao()
    for validacao in validacoes:
        print(f"  {validacao}")
    
    print("✅ Configuração institucional inicializada!")
    return config_institucional


if __name__ == "__main__":
    # Teste da configuração
    config = inicializar_config_institucional()
    print(config.gerar_relatorio_configuracao())













#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDITORIA INSTITUCIONAL - SNE RADAR
Sistema de auditoria para relatórios institucionais
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from config_institucional import obter_config_institucional


class AuditoriaInstitucional:
    """Sistema de auditoria para relatórios institucionais"""
    
    def __init__(self):
        """Inicializa sistema de auditoria"""
        self.config = obter_config_institucional()
        
        # Banco de dados de auditoria
        self.db_path = os.path.join(self.config.diretorio_auditoria, "auditoria.db")
        self._inicializar_banco_dados()
        
        # Cache de auditoria
        self.cache_auditoria = {}
        
        # Métricas de auditoria
        self.metricas_auditoria = {
            'total_operacoes': 0,
            'operacoes_auditadas': 0,
            'violacoes_detectadas': 0,
            'tempo_medio_auditoria': 0.0,
            'score_medio_integridade': 0.0
        }
        
        # Configurações de auditoria
        self.configuracoes_auditoria = {
            'audit_trail': True,
            'data_integrity': True,
            'access_logs': True,
            'change_logs': True,
            'compliance_logs': True,
            'retention_period': self.config.retencao_logs_dias,
            'encryption': self.config.criptografia_logs,
            'backup_automatico': self.config.backup_automatico
        }
    
    def _inicializar_banco_dados(self):
        """Inicializa banco de dados de auditoria"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Conectar ao banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabelas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operacoes_auditoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operacao TEXT NOT NULL,
                    usuario TEXT,
                    sistema TEXT,
                    dados_input TEXT,
                    dados_output TEXT,
                    hash_input TEXT,
                    hash_output TEXT,
                    status TEXT,
                    duracao_ms INTEGER,
                    compliance_score REAL,
                    integridade_score REAL,
                    violacoes TEXT,
                    observacoes TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_acesso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    usuario TEXT,
                    sistema TEXT,
                    operacao TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    status TEXT,
                    duracao_ms INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_alteracao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    tabela TEXT,
                    operacao TEXT,
                    registro_id TEXT,
                    dados_anteriores TEXT,
                    dados_novos TEXT,
                    usuario TEXT,
                    sistema TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    report_id TEXT,
                    regulamentacao TEXT,
                    status TEXT,
                    score REAL,
                    violacoes TEXT,
                    validacoes TEXT,
                    observacoes TEXT
                )
            ''')
            
            # Criar índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_operacoes_timestamp ON operacoes_auditoria(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_operacoes_status ON operacoes_auditoria(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_acesso_timestamp ON logs_acesso(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alteracao_timestamp ON logs_alteracao(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_compliance_timestamp ON logs_compliance(timestamp)')
            
            conn.commit()
            conn.close()
            
            print("✅ Banco de dados de auditoria inicializado")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de auditoria: {e}")
    
    def registrar_operacao(self, operacao: str, dados_input: Dict[str, Any], dados_output: Dict[str, Any], 
                          usuario: str = "SNE-AI-SYSTEM", sistema: str = "SNE-RADAR") -> str:
        """
        Registra operação para auditoria
        
        Args:
            operacao: Tipo de operação (ex: "gerar_relatorio")
            dados_input: Dados de entrada
            dados_output: Dados de saída
            usuario: Usuário que executou a operação
            sistema: Sistema que executou a operação
            
        Returns:
            str com ID da operação registrada
        """
        try:
            timestamp = datetime.now().isoformat()
            operacao_id = self._gerar_id_operacao()
            
            # Calcular hashes para integridade
            hash_input = self._calcular_hash_dados(dados_input)
            hash_output = self._calcular_hash_dados(dados_output)
            
            # Calcular scores
            compliance_score = self._calcular_score_compliance(dados_output)
            integridade_score = self._calcular_score_integridade(dados_input, dados_output)
            
            # Detectar violações
            violacoes = self._detectar_violacoes(dados_input, dados_output)
            
            # Registrar no banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO operacoes_auditoria (
                    timestamp, operacao, usuario, sistema, dados_input, dados_output,
                    hash_input, hash_output, status, duracao_ms, compliance_score,
                    integridade_score, violacoes, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, operacao, usuario, sistema,
                json.dumps(self._serializar_dados_json_safe(dados_input), ensure_ascii=False),
                json.dumps(self._serializar_dados_json_safe(dados_output), ensure_ascii=False),
                hash_input, hash_output,
                "SUCCESS" if not violacoes else "WARNING",
                0,  # Duração será calculada posteriormente
                compliance_score, integridade_score,
                json.dumps(violacoes, ensure_ascii=False),
                f"Operação {operacao} registrada"
            ))
            
            conn.commit()
            conn.close()
            
            # Atualizar métricas
            self._atualizar_metricas_auditoria(compliance_score, integridade_score, len(violacoes))
            
            # Salvar em cache
            self.cache_auditoria[operacao_id] = {
                'timestamp': timestamp,
                'operacao': operacao,
                'usuario': usuario,
                'sistema': sistema,
                'compliance_score': compliance_score,
                'integridade_score': integridade_score,
                'violacoes': violacoes
            }
            
            print(f"✅ Operação auditada: {operacao_id}")
            return operacao_id
            
        except Exception as e:
            print(f"❌ Erro ao registrar operação: {e}")
            return f"ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def registrar_acesso(self, usuario: str, operacao: str, ip_address: str = "127.0.0.1", 
                        user_agent: str = "SNE-AI-SYSTEM", status: str = "SUCCESS") -> str:
        """Registra acesso do usuário"""
        try:
            timestamp = datetime.now().isoformat()
            acesso_id = self._gerar_id_operacao()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs_acesso (
                    timestamp, usuario, sistema, operacao, ip_address, user_agent, status, duracao_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, usuario, "SNE-RADAR", operacao, ip_address, user_agent, status, 0
            ))
            
            conn.commit()
            conn.close()
            
            return acesso_id
            
        except Exception as e:
            print(f"❌ Erro ao registrar acesso: {e}")
            return f"ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def registrar_alteracao(self, tabela: str, operacao: str, registro_id: str, 
                           dados_anteriores: Dict[str, Any], dados_novos: Dict[str, Any],
                           usuario: str = "SNE-AI-SYSTEM") -> str:
        """Registra alteração de dados"""
        try:
            timestamp = datetime.now().isoformat()
            alteracao_id = self._gerar_id_operacao()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs_alteracao (
                    timestamp, tabela, operacao, registro_id, dados_anteriores, dados_novos, usuario, sistema
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, tabela, operacao, registro_id,
                json.dumps(dados_anteriores, ensure_ascii=False),
                json.dumps(dados_novos, ensure_ascii=False),
                usuario, "SNE-RADAR"
            ))
            
            conn.commit()
            conn.close()
            
            return alteracao_id
            
        except Exception as e:
            print(f"❌ Erro ao registrar alteração: {e}")
            return f"ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def registrar_compliance(self, report_id: str, regulamentacao: str, status: str, 
                           score: float, violacoes: List[str], validacoes: List[str]) -> str:
        """Registra log de compliance"""
        try:
            timestamp = datetime.now().isoformat()
            compliance_id = self._gerar_id_operacao()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs_compliance (
                    timestamp, report_id, regulamentacao, status, score, violacoes, validacoes, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, report_id, regulamentacao, status, score,
                json.dumps(violacoes, ensure_ascii=False),
                json.dumps(validacoes, ensure_ascii=False),
                f"Compliance {regulamentacao} - Score: {score:.1f}%"
            ))
            
            conn.commit()
            conn.close()
            
            return compliance_id
            
        except Exception as e:
            print(f"❌ Erro ao registrar compliance: {e}")
            return f"ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _serializar_dados_json_safe(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Serializa dados para JSON de forma segura"""
        if dados is None:
            return {}
        
        dados_serializados = {}
        for key, value in dados.items():
            if isinstance(value, bool):
                dados_serializados[key] = str(value)
            elif isinstance(value, (int, float, str, list, dict)):
                dados_serializados[key] = value
            else:
                dados_serializados[key] = str(value)
        
        return dados_serializados
    
    def _calcular_hash_dados(self, dados: Dict[str, Any]) -> str:
        """Calcula hash dos dados para integridade"""
        dados_str = json.dumps(dados, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(dados_str.encode()).hexdigest()
    
    def _calcular_score_compliance(self, dados_output: Dict[str, Any]) -> float:
        """Calcula score de compliance"""
        # Simular cálculo baseado em dados de saída
        score = 100.0
        
        # Verificar se tem compliance
        if 'compliance' in dados_output:
            score -= 0  # Compliance presente
        else:
            score -= 20  # Compliance ausente
        
        # Verificar se tem auditoria
        if 'audit' in dados_output:
            score -= 0  # Auditoria presente
        else:
            score -= 10  # Auditoria ausente
        
        # Verificar metadados
        metadata = dados_output.get('metadata', {})
        if metadata.get('report_id'):
            score -= 0  # ID presente
        else:
            score -= 15  # ID ausente
        
        return max(0.0, score)
    
    def _calcular_score_integridade(self, dados_input: Dict[str, Any], dados_output: Dict[str, Any]) -> float:
        """Calcula score de integridade"""
        score = 100.0
        
        # Verificar consistência de dados
        if len(dados_output) < len(dados_input) * 0.8:
            score -= 20  # Muitos dados perdidos
        
        # Verificar hash de integridade
        hash_input = self._calcular_hash_dados(dados_input)
        hash_output = self._calcular_hash_dados(dados_output)
        
        if hash_input == hash_output:
            score -= 30  # Dados não foram processados
        
        return max(0.0, score)
    
    def _detectar_violacoes(self, dados_input: Dict[str, Any], dados_output: Dict[str, Any]) -> List[str]:
        """Detecta violações de auditoria"""
        violacoes = []
        
        # Verificar dados sensíveis
        if 'password' in str(dados_input).lower() or 'senha' in str(dados_input).lower():
            violacoes.append("Dados sensíveis detectados no input")
        
        if 'password' in str(dados_output).lower() or 'senha' in str(dados_output).lower():
            violacoes.append("Dados sensíveis detectados no output")
        
        # Verificar tamanho dos dados
        if len(str(dados_input)) > 1000000:  # 1MB
            violacoes.append("Dados de input muito grandes")
        
        if len(str(dados_output)) > 1000000:  # 1MB
            violacoes.append("Dados de output muito grandes")
        
        # Verificar campos obrigatórios
        metadata = dados_output.get('metadata', {})
        if not metadata.get('timestamp'):
            violacoes.append("Timestamp ausente nos metadados")
        
        if not metadata.get('report_id'):
            violacoes.append("Report ID ausente nos metadados")
        
        return violacoes
    
    def _gerar_id_operacao(self) -> str:
        """Gera ID único para operação"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(timestamp.encode()).hexdigest()[:6].upper()
        return f"AUDIT-{timestamp}-{random_suffix}"
    
    def _atualizar_metricas_auditoria(self, compliance_score: float, integridade_score: float, violacoes: int):
        """Atualiza métricas de auditoria"""
        self.metricas_auditoria['total_operacoes'] += 1
        self.metricas_auditoria['operacoes_auditadas'] += 1
        
        if violacoes > 0:
            self.metricas_auditoria['violacoes_detectadas'] += violacoes
        
        # Atualizar scores médios
        total_compliance = self.metricas_auditoria['score_medio_integridade'] * (self.metricas_auditoria['total_operacoes'] - 1)
        total_compliance += compliance_score
        self.metricas_auditoria['score_medio_integridade'] = total_compliance / self.metricas_auditoria['total_operacoes']
    
    def gerar_relatorio_auditoria(self, periodo_dias: int = 30) -> str:
        """Gera relatório de auditoria"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Consultar dados do período
        dados_periodo = self._consultar_dados_periodo(periodo_dias)
        
        return f"""
{'='*80}
🏛️ RELATÓRIO DE AUDITORIA INSTITUCIONAL - SNE RADAR
{'='*80}
📅 Data: {timestamp}
📊 Período: Últimos {periodo_dias} dias
📈 Status: {'ATIVO' if self.configuracoes_auditoria['audit_trail'] else 'INATIVO'}

📊 MÉTRICAS DE AUDITORIA:
├── Total de Operações: {self.metricas_auditoria['total_operacoes']}
├── Operações Auditadas: {self.metricas_auditoria['operacoes_auditadas']}
├── Violações Detectadas: {self.metricas_auditoria['violacoes_detectadas']}
├── Tempo Médio de Auditoria: {self.metricas_auditoria['tempo_medio_auditoria']:.2f}ms
└── Score Médio de Integridade: {self.metricas_auditoria['score_medio_integridade']:.1f}%

🔧 CONFIGURAÇÕES DE AUDITORIA:
├── Audit Trail: {'✅ ATIVO' if self.configuracoes_auditoria['audit_trail'] else '❌ INATIVO'}
├── Integridade de Dados: {'✅ ATIVO' if self.configuracoes_auditoria['data_integrity'] else '❌ INATIVO'}
├── Logs de Acesso: {'✅ ATIVO' if self.configuracoes_auditoria['access_logs'] else '❌ INATIVO'}
├── Logs de Alteração: {'✅ ATIVO' if self.configuracoes_auditoria['change_logs'] else '❌ INATIVO'}
├── Logs de Compliance: {'✅ ATIVO' if self.configuracoes_auditoria['compliance_logs'] else '❌ INATIVO'}
├── Período de Retenção: {self.configuracoes_auditoria['retention_period']} dias
├── Criptografia: {'✅ ATIVO' if self.configuracoes_auditoria['encryption'] else '❌ INATIVO'}
└── Backup Automático: {'✅ ATIVO' if self.configuracoes_auditoria['backup_automatico'] else '❌ INATIVO'}

📈 ESTATÍSTICAS DO PERÍODO:
{dados_periodo}

🎯 RECOMENDAÇÕES DE AUDITORIA:
{self._gerar_recomendacoes_auditoria()}

📋 PRÓXIMAS AÇÕES:
{self._gerar_proximas_acoes()}
{'='*80}
"""
    
    def _consultar_dados_periodo(self, periodo_dias: int) -> str:
        """Consulta dados do período"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consultar operações do período
            cursor.execute('''
                SELECT COUNT(*) as total, 
                       AVG(compliance_score) as avg_compliance,
                       AVG(integridade_score) as avg_integridade,
                       COUNT(CASE WHEN violacoes != '[]' THEN 1 END) as com_violacoes
                FROM operacoes_auditoria 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(periodo_dias))
            
            resultado = cursor.fetchone()
            
            # Consultar acessos do período
            cursor.execute('''
                SELECT COUNT(*) as total_acessos
                FROM logs_acesso 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(periodo_dias))
            
            acessos = cursor.fetchone()
            
            conn.close()
            
            if resultado:
                return f"""├── Operações no Período: {resultado[0]}
├── Score Médio Compliance: {resultado[1]:.1f}%
├── Score Médio Integridade: {resultado[2]:.1f}%
├── Operações com Violações: {resultado[3]}
└── Total de Acessos: {acessos[0] if acessos else 0}"""
            else:
                return "├── Nenhum dado disponível para o período"
                
        except Exception as e:
            return f"├── Erro ao consultar dados: {e}"
    
    def _gerar_recomendacoes_auditoria(self) -> str:
        """Gera recomendações de auditoria"""
        recomendacoes = []
        
        # Verificar score de integridade
        if self.metricas_auditoria['score_medio_integridade'] < 90:
            recomendacoes.append("• Score de integridade baixo - Revisar processos de validação")
        
        # Verificar violações
        if self.metricas_auditoria['violacoes_detectadas'] > 0:
            recomendacoes.append("• Violações detectadas - Implementar controles adicionais")
        
        # Verificar configurações
        if not self.configuracoes_auditoria['encryption']:
            recomendacoes.append("• Criptografia desabilitada - Ativar para maior segurança")
        
        if not self.configuracoes_auditoria['backup_automatico']:
            recomendacoes.append("• Backup automático desabilitado - Ativar para proteção de dados")
        
        if not recomendacoes:
            recomendacoes.append("• Sistema de auditoria funcionando adequadamente")
        
        return "\n".join(recomendacoes)
    
    def _gerar_proximas_acoes(self) -> str:
        """Gera próximas ações de auditoria"""
        acoes = []
        
        # Verificar retenção de logs
        if self.configuracoes_auditoria['retention_period'] > 365:
            acoes.append("• Considerar reduzir período de retenção para otimizar espaço")
        
        # Verificar performance
        if self.metricas_auditoria['tempo_medio_auditoria'] > 1000:
            acoes.append("• Otimizar performance de auditoria")
        
        # Verificar backup
        acoes.append("• Verificar integridade dos backups")
        acoes.append("• Testar procedimentos de recuperação")
        acoes.append("• Revisar políticas de retenção")
        
        return "\n".join(acoes)
    
    def obter_metricas_auditoria(self) -> Dict[str, Any]:
        """Retorna métricas de auditoria"""
        return self.metricas_auditoria.copy()
    
    def limpar_dados_antigos(self, dias_retention: int = None):
        """Limpa dados antigos do banco"""
        if dias_retention is None:
            dias_retention = self.configuracoes_auditoria['retention_period']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Limpar operações antigas
            cursor.execute('''
                DELETE FROM operacoes_auditoria 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(dias_retention))
            
            operacoes_removidas = cursor.rowcount
            
            # Limpar logs de acesso antigos
            cursor.execute('''
                DELETE FROM logs_acesso 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(dias_retention))
            
            acessos_removidos = cursor.rowcount
            
            # Limpar logs de alteração antigos
            cursor.execute('''
                DELETE FROM logs_alteracao 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(dias_retention))
            
            alteracoes_removidas = cursor.rowcount
            
            # Limpar logs de compliance antigos
            cursor.execute('''
                DELETE FROM logs_compliance 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(dias_retention))
            
            compliance_removidos = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ Dados antigos removidos:")
            print(f"  • Operações: {operacoes_removidas}")
            print(f"  • Acessos: {acessos_removidos}")
            print(f"  • Alterações: {alteracoes_removidas}")
            print(f"  • Compliance: {compliance_removidos}")
            
        except Exception as e:
            print(f"❌ Erro ao limpar dados antigos: {e}")
    
    def exportar_auditoria(self, periodo_dias: int = 30, formato: str = "json") -> str:
        """Exporta dados de auditoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consultar dados do período
            cursor.execute('''
                SELECT * FROM operacoes_auditoria 
                WHERE timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            '''.format(periodo_dias))
            
            dados = cursor.fetchall()
            
            # Obter nomes das colunas
            cursor.execute("PRAGMA table_info(operacoes_auditoria)")
            colunas = [coluna[1] for coluna in cursor.fetchall()]
            
            conn.close()
            
            # Converter para formato desejado
            if formato == "json":
                resultado = []
                for linha in dados:
                    registro = dict(zip(colunas, linha))
                    resultado.append(registro)
                
                # Salvar arquivo
                arquivo_path = os.path.join(self.config.diretorio_auditoria, f"auditoria_export_{datetime.now().strftime('%Y%m%d')}.json")
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    json.dump(resultado, f, indent=2, ensure_ascii=False)
                
                return arquivo_path
            
            else:
                return "Formato não suportado"
                
        except Exception as e:
            print(f"❌ Erro ao exportar auditoria: {e}")
            return ""


# Instância global do sistema de auditoria
auditoria_institucional = AuditoriaInstitucional()


def obter_auditoria_institucional() -> AuditoriaInstitucional:
    """Retorna instância global do sistema de auditoria"""
    return auditoria_institucional


if __name__ == "__main__":
    # Teste do sistema de auditoria
    auditoria = obter_auditoria_institucional()
    
    # Dados de teste
    dados_input_teste = {
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'timestamp': datetime.now().isoformat()
    }
    
    dados_output_teste = {
        'metadata': {
            'report_id': 'SNE-TEST-AUDIT-001',
            'timestamp': datetime.now().isoformat(),
            'analyst': 'SNE-AI-SYSTEM v2.1'
        },
        'compliance': {
            'mifid_ii': True,
            'esma': True
        },
        'audit': {
            'audit_trail': True,
            'data_integrity': True
        }
    }
    
    # Registrar operação
    operacao_id = auditoria.registrar_operacao(
        "gerar_relatorio_institucional",
        dados_input_teste,
        dados_output_teste
    )
    
    # Registrar acesso
    acesso_id = auditoria.registrar_acesso(
        "teste_usuario",
        "gerar_relatorio",
        "192.168.1.100"
    )
    
    # Registrar compliance
    compliance_id = auditoria.registrar_compliance(
        "SNE-TEST-AUDIT-001",
        "MiFID_II",
        "SUCCESS",
        95.0,
        [],
        ["Price transparency", "Best execution"]
    )
    
    print("✅ Sistema de auditoria testado com sucesso!")
    print(f"📊 Operação registrada: {operacao_id}")
    print(f"🔐 Acesso registrado: {acesso_id}")
    print(f"📋 Compliance registrado: {compliance_id}")
    
    # Gerar relatório de auditoria
    relatorio_auditoria = auditoria.gerar_relatorio_auditoria(30)
    print("\n" + relatorio_auditoria)
    
    # Obter métricas
    metricas = auditoria.obter_metricas_auditoria()
    print(f"\n📈 Métricas de auditoria:")
    print(f"  • Total de operações: {metricas['total_operacoes']}")
    print(f"  • Operações auditadas: {metricas['operacoes_auditadas']}")
    print(f"  • Violações detectadas: {metricas['violacoes_detectadas']}")
    print(f"  • Score médio integridade: {metricas['score_medio_integridade']:.1f}%")









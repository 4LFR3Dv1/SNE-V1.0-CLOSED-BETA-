#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE CACHE INTELIGENTE DO SNE RADAR 3.0
Cache para análises, relatórios e sinais com TTL e invalidação automática
"""

import os
import time
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from threading import Lock, RLock
import pickle
from functools import wraps

# ===========================================
# CONFIGURAÇÃO DE LOGGING
# ===========================================
logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gerenciador de cache inteligente para o SNE Radar 3.0
    Suporta múltiplos tipos de cache com TTL e invalidação automática
    """
    
    def __init__(self):
        """Inicializa o gerenciador de cache"""
        self._caches = {}  # {cache_name: {data: {}, metadata: {}}}
        self._locks = {}  # {cache_name: RLock()}
        self._stats = {}  # Estatísticas de cache
        self._global_lock = Lock()
        
        # Carregar configurações
        try:
            from config_seguro import CACHE_CONFIG
            self.cache_configs = CACHE_CONFIG
        except ImportError:
            # Configurações padrão
            self.cache_configs = {
                'analises': {'maxsize': 100, 'ttl': 300},
                'relatorios': {'maxsize': 50, 'ttl': 600},
                'sinais': {'maxsize': 200, 'ttl': 180}
            }
        
        # Inicializar caches
        self._initialize_caches()
        
        logger.info("💾 CacheManager inicializado")
    
    def _initialize_caches(self):
        """Inicializa os caches configurados"""
        for cache_name, config in self.cache_configs.items():
            self._caches[cache_name] = {
                'data': {},
                'metadata': {
                    'created_at': datetime.now(),
                    'last_cleanup': datetime.now(),
                    'hits': 0,
                    'misses': 0,
                    'evictions': 0
                }
            }
            self._locks[cache_name] = RLock()
            self._stats[cache_name] = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'size': 0
            }
    
    # ===========================================
    # OPERAÇÕES BÁSICAS DE CACHE
    # ===========================================
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache
        
        Args:
            cache_name: Nome do cache
            key: Chave do item
            
        Returns:
            Any: Valor armazenado ou None se não encontrado/expirado
        """
        if cache_name not in self._caches:
            logger.warning(f"⚠️ Cache '{cache_name}' não existe")
            return None
        
        with self._locks[cache_name]:
            cache_data = self._caches[cache_name]['data']
            cache_metadata = self._caches[cache_name]['metadata']
            
            if key not in cache_data:
                self._stats[cache_name]['misses'] += 1
                logger.debug(f"❌ Cache miss: {cache_name}:{key}")
                return None
            
            item = cache_data[key]
            
            # Verificar se expirou
            if self._is_expired(item):
                del cache_data[key]
                self._stats[cache_name]['evictions'] += 1
                self._stats[cache_name]['misses'] += 1
                logger.debug(f"⏰ Cache expired: {cache_name}:{key}")
                return None
            
            # Atualizar estatísticas
            self._stats[cache_name]['hits'] += 1
            cache_metadata['hits'] += 1
            
            logger.debug(f"✅ Cache hit: {cache_name}:{key}")
            return item['value']
    
    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Armazena um valor no cache
        
        Args:
            cache_name: Nome do cache
            key: Chave do item
            value: Valor a ser armazenado
            ttl: TTL em segundos (opcional)
            
        Returns:
            bool: True se armazenado com sucesso
        """
        if cache_name not in self._caches:
            logger.warning(f"⚠️ Cache '{cache_name}' não existe")
            return False
        
        with self._locks[cache_name]:
            cache_data = self._caches[cache_name]['data']
            cache_config = self.cache_configs[cache_name]
            
            # Usar TTL padrão se não especificado
            if ttl is None:
                ttl = cache_config['ttl']
            
            # Verificar limite de tamanho
            if len(cache_data) >= cache_config['maxsize']:
                self._evict_oldest(cache_name)
            
            # Armazenar item
            cache_data[key] = {
                'value': value,
                'created_at': datetime.now(),
                'ttl': ttl,
                'access_count': 0
            }
            
            self._stats[cache_name]['size'] = len(cache_data)
            logger.debug(f"💾 Cache set: {cache_name}:{key} (TTL: {ttl}s)")
            return True
    
    def delete(self, cache_name: str, key: str) -> bool:
        """
        Remove um item do cache
        
        Args:
            cache_name: Nome do cache
            key: Chave do item
            
        Returns:
            bool: True se removido com sucesso
        """
        if cache_name not in self._caches:
            return False
        
        with self._locks[cache_name]:
            cache_data = self._caches[cache_name]['data']
            
            if key in cache_data:
                del cache_data[key]
                self._stats[cache_name]['size'] = len(cache_data)
                logger.debug(f"🗑️ Cache delete: {cache_name}:{key}")
                return True
            
            return False
    
    def clear(self, cache_name: str) -> bool:
        """
        Limpa todo o cache
        
        Args:
            cache_name: Nome do cache
            
        Returns:
            bool: True se limpo com sucesso
        """
        if cache_name not in self._caches:
            return False
        
        with self._locks[cache_name]:
            self._caches[cache_name]['data'].clear()
            self._stats[cache_name]['size'] = 0
            logger.info(f"🧹 Cache cleared: {cache_name}")
            return True
    
    # ===========================================
    # OPERAÇÕES AVANÇADAS
    # ===========================================
    def get_or_set(self, cache_name: str, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """
        Obtém do cache ou executa função para gerar valor
        
        Args:
            cache_name: Nome do cache
            key: Chave do item
            factory_func: Função para gerar valor se não estiver no cache
            ttl: TTL em segundos
            
        Returns:
            Any: Valor do cache ou gerado pela função
        """
        # Tentar obter do cache
        cached_value = self.get(cache_name, key)
        if cached_value is not None:
            return cached_value
        
        # Gerar novo valor
        try:
            new_value = factory_func()
            self.set(cache_name, key, new_value, ttl)
            return new_value
        except Exception as e:
            logger.error(f"❌ Erro ao executar factory_func para {cache_name}:{key}: {e}")
            raise
    
    def invalidate_pattern(self, cache_name: str, pattern: str) -> int:
        """
        Invalida itens que correspondem a um padrão
        
        Args:
            cache_name: Nome do cache
            pattern: Padrão para correspondência
            
        Returns:
            int: Número de itens invalidados
        """
        if cache_name not in self._caches:
            return 0
        
        import re
        
        with self._locks[cache_name]:
            cache_data = self._caches[cache_name]['data']
            keys_to_delete = []
            
            for key in cache_data.keys():
                if re.search(pattern, key):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del cache_data[key]
            
            self._stats[cache_name]['size'] = len(cache_data)
            logger.info(f"🔄 Invalidated {len(keys_to_delete)} items matching pattern '{pattern}' in {cache_name}")
            return len(keys_to_delete)
    
    def cleanup_expired(self, cache_name: str) -> int:
        """
        Remove itens expirados do cache
        
        Args:
            cache_name: Nome do cache
            
        Returns:
            int: Número de itens removidos
        """
        if cache_name not in self._caches:
            return 0
        
        with self._locks[cache_name]:
            cache_data = self._caches[cache_name]['data']
            cache_metadata = self._caches[cache_name]['metadata']
            
            expired_keys = []
            for key, item in cache_data.items():
                if self._is_expired(item):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del cache_data[key]
            
            self._stats[cache_name]['size'] = len(cache_data)
            self._stats[cache_name]['evictions'] += len(expired_keys)
            cache_metadata['evictions'] += len(expired_keys)
            cache_metadata['last_cleanup'] = datetime.now()
            
            if expired_keys:
                logger.info(f"🧹 Cleaned up {len(expired_keys)} expired items from {cache_name}")
            
            return len(expired_keys)
    
    def cleanup_all(self) -> Dict[str, int]:
        """
        Limpa todos os caches de itens expirados
        
        Returns:
            Dict: Número de itens removidos por cache
        """
        results = {}
        for cache_name in self._caches.keys():
            results[cache_name] = self.cleanup_expired(cache_name)
        
        logger.info(f"🧹 Cleanup completed: {results}")
        return results
    
    # ===========================================
    # CACHE POR USUÁRIO
    # ===========================================
    def get_user_cache(self, user_id: str, cache_name: str, key: str) -> Optional[Any]:
        """
        Obtém cache específico do usuário
        
        Args:
            user_id: ID do usuário
            cache_name: Nome do cache
            key: Chave do item
            
        Returns:
            Any: Valor armazenado ou None
        """
        user_key = f"{user_id}_{cache_name}_{key}"
        return self.get(cache_name, user_key)
    
    def set_user_cache(self, user_id: str, cache_name: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Armazena cache específico do usuário
        
        Args:
            user_id: ID do usuário
            cache_name: Nome do cache
            key: Chave do item
            value: Valor a ser armazenado
            ttl: TTL em segundos
            
        Returns:
            bool: True se armazenado com sucesso
        """
        user_key = f"{user_id}_{cache_name}_{key}"
        return self.set(cache_name, user_key, value, ttl)
    
    def delete_user_cache(self, user_id: str, cache_name: str, key: str) -> bool:
        """
        Remove cache específico do usuário
        
        Args:
            user_id: ID do usuário
            cache_name: Nome do cache
            key: Chave do item
            
        Returns:
            bool: True se removido com sucesso
        """
        user_key = f"{user_id}_{cache_name}_{key}"
        return self.delete(cache_name, user_key)
    
    def clear_user_cache(self, user_id: str, cache_name: str) -> int:
        """
        Limpa todo o cache de um usuário específico
        
        Args:
            user_id: ID do usuário
            cache_name: Nome do cache
            
        Returns:
            int: Número de itens removidos
        """
        if cache_name not in self._caches:
            return 0
        
        pattern = f"^{user_id}_{cache_name}_"
        return self.invalidate_pattern(cache_name, pattern)
    
    def get_user_cache_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de cache de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict: Estatísticas do usuário
        """
        stats = {}
        
        for cache_name in self._caches.keys():
            with self._locks[cache_name]:
                cache_data = self._caches[cache_name]['data']
                
                # Contar itens do usuário
                user_items = 0
                total_size = 0
                
                for key, item in cache_data.items():
                    if key.startswith(f"{user_id}_"):
                        user_items += 1
                        total_size += len(str(item['value']))
                
                stats[cache_name] = {
                    'items': user_items,
                    'total_size': total_size
                }
        
        return stats
    
    def cleanup_user_expired_cache(self, user_id: str) -> int:
        """
        Remove itens expirados do cache de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            int: Número de itens removidos
        """
        total_removed = 0
        
        for cache_name in self._caches.keys():
            with self._locks[cache_name]:
                cache_data = self._caches[cache_name]['data']
                
                expired_keys = []
                for key, item in cache_data.items():
                    if key.startswith(f"{user_id}_") and self._is_expired(item):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del cache_data[key]
                
                total_removed += len(expired_keys)
                
                # Atualizar estatísticas
                self._stats[cache_name]['size'] = len(cache_data)
                self._stats[cache_name]['evictions'] += len(expired_keys)
        
        if total_removed > 0:
            logger.info(f"🧹 Limpeza de cache do usuário {user_id}: {total_removed} itens removidos")
        
        return total_removed
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Verifica se um item do cache expirou"""
        created_at = item['created_at']
        ttl = item['ttl']
        return datetime.now() > created_at + timedelta(seconds=ttl)
    
    def _evict_oldest(self, cache_name: str):
        """Remove o item mais antigo do cache"""
        cache_data = self._caches[cache_name]['data']
        
        if not cache_data:
            return
        
        # Encontrar item mais antigo
        oldest_key = min(cache_data.keys(), 
                        key=lambda k: cache_data[k]['created_at'])
        
        del cache_data[oldest_key]
        self._stats[cache_name]['evictions'] += 1
        logger.debug(f"🗑️ Evicted oldest item: {cache_name}:{oldest_key}")
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        Gera uma chave única baseada nos argumentos
        
        Args:
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            str: Chave gerada
        """
        # Converter argumentos em string
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        # Gerar hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_stats(self, cache_name: str = None) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Args:
            cache_name: Nome do cache (opcional)
            
        Returns:
            Dict: Estatísticas do cache
        """
        if cache_name:
            if cache_name not in self._stats:
                return {}
            
            stats = self._stats[cache_name].copy()
            cache_data = self._caches[cache_name]['data']
            cache_metadata = self._caches[cache_name]['metadata']
            
            stats.update({
                'actual_size': len(cache_data),
                'max_size': self.cache_configs[cache_name]['maxsize'],
                'ttl': self.cache_configs[cache_name]['ttl'],
                'hit_rate': stats['hits'] / (stats['hits'] + stats['misses']) if (stats['hits'] + stats['misses']) > 0 else 0,
                'created_at': cache_metadata['created_at'].isoformat(),
                'last_cleanup': cache_metadata['last_cleanup'].isoformat()
            })
            
            return stats
        else:
            # Retornar estatísticas de todos os caches
            all_stats = {}
            for name in self._caches.keys():
                all_stats[name] = self.get_stats(name)
            return all_stats
    
    def save_to_disk(self, cache_name: str, filename: str = None) -> bool:
        """
        Salva cache em disco
        
        Args:
            cache_name: Nome do cache
            filename: Nome do arquivo (opcional)
            
        Returns:
            bool: True se salvo com sucesso
        """
        if cache_name not in self._caches:
            return False
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cache_{cache_name}_{timestamp}.pkl"
        
        try:
            with self._locks[cache_name]:
                cache_data = self._caches[cache_name].copy()
                
                # Converter datetime para string para serialização
                for key, item in cache_data['data'].items():
                    if 'created_at' in item:
                        item['created_at'] = item['created_at'].isoformat()
                
                cache_data['metadata']['created_at'] = cache_data['metadata']['created_at'].isoformat()
                cache_data['metadata']['last_cleanup'] = cache_data['metadata']['last_cleanup'].isoformat()
            
            with open(filename, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"💾 Cache {cache_name} salvo em {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache {cache_name}: {e}")
            return False
    
    def load_from_disk(self, cache_name: str, filename: str) -> bool:
        """
        Carrega cache do disco
        
        Args:
            cache_name: Nome do cache
            filename: Nome do arquivo
            
        Returns:
            bool: True se carregado com sucesso
        """
        try:
            with open(filename, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Converter strings de volta para datetime
            for key, item in cache_data['data'].items():
                if 'created_at' in item and isinstance(item['created_at'], str):
                    item['created_at'] = datetime.fromisoformat(item['created_at'])
            
            if isinstance(cache_data['metadata']['created_at'], str):
                cache_data['metadata']['created_at'] = datetime.fromisoformat(cache_data['metadata']['created_at'])
            if isinstance(cache_data['metadata']['last_cleanup'], str):
                cache_data['metadata']['last_cleanup'] = datetime.fromisoformat(cache_data['metadata']['last_cleanup'])
            
            with self._locks[cache_name]:
                self._caches[cache_name] = cache_data
                self._stats[cache_name]['size'] = len(cache_data['data'])
            
            logger.info(f"📂 Cache {cache_name} carregado de {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar cache {cache_name}: {e}")
            return False

# ===========================================
# DECORATORS DE CACHE
# ===========================================
def cached(cache_name: str, ttl: Optional[int] = None, key_func=None):
    """
    Decorator para cachear resultados de funções
    
    Args:
        cache_name: Nome do cache
        ttl: TTL em segundos
        key_func: Função para gerar chave (opcional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_manager.generate_key(func.__name__, *args, **kwargs)
            
            # Tentar obter do cache
            cached_result = cache_manager.get(cache_name, cache_key)
            if cached_result is not None:
                logger.debug(f"✅ Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # Executar função e cachear resultado
            try:
                result = func(*args, **kwargs)
                cache_manager.set(cache_name, cache_key, result, ttl)
                logger.debug(f"💾 Cached result for {func.__name__}: {cache_key}")
                return result
            except Exception as e:
                logger.error(f"❌ Error in cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

# ===========================================
# INSTÂNCIA GLOBAL DE CACHE
# ===========================================
cache_manager = CacheManager()

# ===========================================
# FUNÇÕES UTILITÁRIAS
# ===========================================
def get_cached_analysis(symbol: str, timeframe: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    """Obtém análise em cache"""
    key = f"{symbol}_{timeframe}"
    if user_id:
        return cache_manager.get_user_cache(user_id, 'analises', key)
    else:
        return cache_manager.get('analises', key)

def set_cached_analysis(symbol: str, timeframe: str, analysis: Dict[str, Any], user_id: str = None) -> bool:
    """Armazena análise em cache"""
    key = f"{symbol}_{timeframe}"
    if user_id:
        return cache_manager.set_user_cache(user_id, 'analises', key, analysis)
    else:
        return cache_manager.set('analises', key, analysis)

def get_cached_report(report_type: str, timestamp: str, user_id: str = None) -> Optional[Dict[str, Any]]:
    """Obtém relatório em cache"""
    key = f"{report_type}_{timestamp}"
    if user_id:
        return cache_manager.get_user_cache(user_id, 'relatorios', key)
    else:
        return cache_manager.get('relatorios', key)

def set_cached_report(report_type: str, timestamp: str, report: Dict[str, Any], user_id: str = None) -> bool:
    """Armazena relatório em cache"""
    key = f"{report_type}_{timestamp}"
    if user_id:
        return cache_manager.set_user_cache(user_id, 'relatorios', key, report)
    else:
        return cache_manager.set('relatorios', key, report)

def invalidate_symbol_cache(symbol: str, user_id: str = None):
    """Invalida cache de um símbolo específico"""
    pattern = f"^{symbol}_"
    if user_id:
        cache_manager.invalidate_pattern('analises', f"^{user_id}_analises_{symbol}_")
        cache_manager.invalidate_pattern('sinais', f"^{user_id}_sinais_{symbol}_")
    else:
        cache_manager.invalidate_pattern('analises', pattern)
        cache_manager.invalidate_pattern('sinais', pattern)

def get_user_cached_analysis(user_id: str, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
    """Obtém análise em cache específica do usuário"""
    return cache_manager.get_user_cache(user_id, 'analises', f"{symbol}_{timeframe}")

def set_user_cached_analysis(user_id: str, symbol: str, timeframe: str, analysis: Dict[str, Any]) -> bool:
    """Armazena análise em cache específica do usuário"""
    return cache_manager.set_user_cache(user_id, 'analises', f"{symbol}_{timeframe}", analysis)

def clear_user_cache(user_id: str, cache_type: str = None) -> int:
    """Limpa cache de um usuário"""
    if cache_type:
        return cache_manager.clear_user_cache(user_id, cache_type)
    else:
        total = 0
        for cache_name in ['analises', 'relatorios', 'sinais']:
            total += cache_manager.clear_user_cache(user_id, cache_name)
        return total

if __name__ == "__main__":
    # Teste do sistema de cache
    print("🧪 Testando sistema de cache do SNE Radar 3.0...")
    
    try:
        # Testar operações básicas
        print("\n💾 Testando operações básicas...")
        
        # Armazenar dados
        cache_manager.set('analises', 'BTCUSDT_1h', {'price': 50000, 'signal': 'BUY'})
        cache_manager.set('relatorios', 'daily_20241201', {'summary': 'Market bullish'})
        
        # Recuperar dados
        analysis = cache_manager.get('analises', 'BTCUSDT_1h')
        report = cache_manager.get('relatorios', 'daily_20241201')
        
        print(f"   Análise BTCUSDT: {analysis}")
        print(f"   Relatório diário: {report}")
        
        # Testar decorator
        print("\n🎯 Testando decorator @cached...")
        
        @cached('analises', ttl=60)
        def expensive_analysis(symbol):
            print(f"   Executando análise cara para {symbol}...")
            time.sleep(0.1)  # Simular processamento
            return {'symbol': symbol, 'result': 'analysis_complete'}
        
        # Primeira chamada (executa função)
        result1 = expensive_analysis('ETHUSDT')
        print(f"   Resultado 1: {result1}")
        
        # Segunda chamada (usa cache)
        result2 = expensive_analysis('ETHUSDT')
        print(f"   Resultado 2: {result2}")
        
        # Testar estatísticas
        print("\n📊 Estatísticas de cache:")
        stats = cache_manager.get_stats()
        for cache_name, cache_stats in stats.items():
            print(f"   {cache_name}: {cache_stats}")
        
        # Testar cleanup
        print("\n🧹 Testando cleanup...")
        cleanup_results = cache_manager.cleanup_all()
        print(f"   Itens removidos: {cleanup_results}")
        
        print("\n✅ Sistema de cache testado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao testar sistema de cache: {e}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner Profissional de Moedas
Identifica as melhores moedas para trading baseado em liquidez e volume
"""

import requests
import time

class ProfessionalCoinScanner:
    """
    Scanner profissional de moedas com filtros de liquidez
    """
    
    def __init__(self):
        self.min_volume_24h = 50_000_000  # $50M mínimo
        self.min_trades_1h = 500  # Mínimo de trades
        self.max_spread = 0.002  # 0.2% máximo
        self.cache = None
        self.cache_timestamp = 0
        self.cache_duration = 300  # 5 minutos
    
    def escanear_mercado(self, force_refresh=False, modo_simplificado=False):
        """
        Escaneia mercado e retorna melhores pares
        Usa cache para evitar requests excessivos
        
        Args:
            force_refresh: Força atualização do cache
            modo_simplificado: Usa apenas pares padrão (mais rápido)
        """
        # Verificar cache
        if not force_refresh and self.cache and (time.time() - self.cache_timestamp) < self.cache_duration:
            return self.cache
        
        print("🔍 Escaneando mercado Binance...")
        
        # Modo simplificado: usa apenas pares padrão
        if modo_simplificado:
            print("📊 Modo simplificado: usando top 20 pares")
            todos_pares = self._get_pares_padrao()[:20]
        else:
            # Buscar todos os pares USDT
            todos_pares = self._buscar_todos_pares_usdt()
            
            if not todos_pares:
                print("⚠️ Erro ao buscar pares, usando modo simplificado")
                todos_pares = self._get_pares_padrao()[:20]
        
        print(f"   Analisando {len(todos_pares)} pares...")
        
        # Filtrar por volume e liquidez
        pares_filtrados = []
        
        for par in todos_pares:
            try:
                metricas = self._analisar_metricas(par)
                
                if metricas and self._validar_liquidez(metricas):
                    pares_filtrados.append({
                        'symbol': par,
                        'volume_24h': metricas['volume_24h'],
                        'price_change_pct': metricas['price_change_pct'],
                        'trades_count': metricas['trades_count'],
                        'spread': metricas['spread'],
                        'volatilidade': metricas['volatilidade'],
                        'score_liquidez': metricas['score_liquidez']
                    })
            except Exception as e:
                # Em modo simplificado, adiciona par mesmo sem métricas completas
                if modo_simplificado:
                    pares_filtrados.append({
                        'symbol': par,
                        'volume_24h': 100_000_000,  # Valor padrão
                        'price_change_pct': 0,
                        'trades_count': 1000,
                        'spread': 0.001,
                        'volatilidade': 1.0,
                        'score_liquidez': 50
                    })
                continue
        
        # Se não conseguiu nenhum par, usa lista padrão com valores estimados
        if not pares_filtrados:
            print("⚠️ Não foi possível obter métricas, usando estimativas")
            for par in self._get_pares_padrao()[:20]:
                pares_filtrados.append({
                    'symbol': par,
                    'volume_24h': 100_000_000,
                    'price_change_pct': 0,
                    'trades_count': 1000,
                    'spread': 0.001,
                    'volatilidade': 1.0,
                    'score_liquidez': 50
                })
        
        # Ordenar por score de liquidez
        pares_filtrados.sort(key=lambda x: x['score_liquidez'], reverse=True)
        
        # Atualizar cache
        self.cache = pares_filtrados[:30]  # Top 30
        self.cache_timestamp = time.time()
        
        print(f"✅ {len(self.cache)} pares prontos para análise")
        
        return self.cache
    
    def _buscar_todos_pares_usdt(self):
        """
        Busca todos os pares USDT da Binance
        """
        try:
            url = "https://api.binance.com/api/v3/exchangeInfo"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️ API retornou status {response.status_code}, usando pares padrão")
                return self._get_pares_padrao()
            
            data = response.json()
            
            pares_usdt = []
            for symbol_info in data['symbols']:
                if (symbol_info['quoteAsset'] == 'USDT' and 
                    symbol_info['status'] == 'TRADING' and
                    symbol_info['permissions'] and 'SPOT' in symbol_info['permissions']):
                    pares_usdt.append(symbol_info['symbol'])
            
            return pares_usdt if pares_usdt else self._get_pares_padrao()
        except Exception as e:
            print(f"⚠️ Erro ao conectar com Binance: {e}")
            print("📊 Usando lista de pares padrão...")
            return self._get_pares_padrao()
    
    def _get_pares_padrao(self):
        """
        Retorna lista de pares padrão quando API falha
        """
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT',
            'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'LTCUSDT', 'NEARUSDT',
            'FTMUSDT', 'APTUSDT', 'ARBUSDT', 'OPUSDT', 'INJUSDT',
            'SUIUSDT', 'SEIUSDT', 'TIAUSDT', 'WLDUSDT', 'PEPEUSDT',
            'RNDRUSDT', 'TAOUSDT', 'FETUSDT', 'RENDERUSDT', 'ARUSDT'
        ]
    
    def _analisar_metricas(self, symbol):
        """
        Analisa métricas de liquidez de um par
        """
        try:
            # Ticker 24h
            ticker = self._buscar_ticker_24h(symbol)
            
            if not ticker:
                return None
            
            # Book de ordens (para calcular spread)
            book = self._buscar_book(symbol)
            
            volume_24h = float(ticker.get('quoteVolume', 0))
            price_change_pct = float(ticker.get('priceChangePercent', 0))
            trades_count = int(ticker.get('count', 0))
            
            # Calcular spread
            spread = self._calcular_spread(book) if book else 0.01
            
            # Volatilidade (aproximada pelo price change)
            volatilidade = abs(price_change_pct)
            
            # Score de liquidez
            score_liquidez = self._calcular_score_liquidez(
                volume_24h, trades_count, spread, volatilidade
            )
            
            return {
                'volume_24h': volume_24h,
                'price_change_pct': price_change_pct,
                'trades_count': trades_count,
                'spread': spread,
                'volatilidade': volatilidade,
                'score_liquidez': score_liquidez
            }
        except:
            return None
    
    def _buscar_ticker_24h(self, symbol):
        """
        Busca ticker 24h
        """
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=5)
            return response.json()
        except:
            return None
    
    def _buscar_book(self, symbol):
        """
        Busca book de ordens (apenas top 5)
        """
        try:
            url = f"https://api.binance.com/api/v3/depth"
            params = {"symbol": symbol, "limit": 5}
            response = requests.get(url, params=params, timeout=5)
            return response.json()
        except:
            return None
    
    def _calcular_spread(self, book):
        """
        Calcula spread bid-ask
        """
        try:
            if not book or 'bids' not in book or 'asks' not in book:
                return 0.01
            
            if not book['bids'] or not book['asks']:
                return 0.01
            
            best_bid = float(book['bids'][0][0])
            best_ask = float(book['asks'][0][0])
            
            if best_bid == 0:
                return 0.01
            
            spread = (best_ask - best_bid) / best_bid
            return spread
        except:
            return 0.01
    
    def _calcular_score_liquidez(self, volume_24h, trades_count, spread, volatilidade):
        """
        Calcula score de liquidez (0-100)
        """
        score = 0
        
        # Volume (40 pontos)
        if volume_24h >= 500_000_000:  # $500M+
            score += 40
        elif volume_24h >= 200_000_000:  # $200M+
            score += 30
        elif volume_24h >= 100_000_000:  # $100M+
            score += 20
        elif volume_24h >= 50_000_000:   # $50M+
            score += 10
        
        # Trades (30 pontos)
        if trades_count >= 10000:
            score += 30
        elif trades_count >= 5000:
            score += 20
        elif trades_count >= 1000:
            score += 10
        elif trades_count >= 500:
            score += 5
        
        # Spread (20 pontos)
        if spread <= 0.0005:  # 0.05%
            score += 20
        elif spread <= 0.001:  # 0.1%
            score += 15
        elif spread <= 0.002:  # 0.2%
            score += 10
        
        # Volatilidade (10 pontos)
        if 1 <= volatilidade <= 5:  # Ideal para day trading
            score += 10
        elif volatilidade > 5:
            score += 5
        
        return score
    
    def _validar_liquidez(self, metricas):
        """
        Valida se par tem liquidez suficiente
        """
        return (
            metricas['volume_24h'] >= self.min_volume_24h and
            metricas['trades_count'] >= self.min_trades_1h and
            metricas['spread'] <= self.max_spread
        )
    
    def obter_top_por_volume(self, n=10):
        """
        Retorna top N pares por volume
        """
        pares = self.escanear_mercado()
        return sorted(pares, key=lambda x: x['volume_24h'], reverse=True)[:n]
    
    def obter_top_por_volatilidade(self, n=10):
        """
        Retorna top N pares por volatilidade
        """
        pares = self.escanear_mercado()
        return sorted(pares, key=lambda x: x['volatilidade'], reverse=True)[:n]


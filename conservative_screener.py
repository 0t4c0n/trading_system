#!/usr/bin/env python3
"""
Conservative Stock Screener with MA50 Stop Loss Bonus - ROBUST VERSION
======================================================================

🔧 MEJORAS DE ROBUSTEZ: Solo añade retry logic y mejores headers
📊 MANTIENE: 100% de la lógica original de trading y scoring
🎯 OBJETIVO: Mismo resultado local vs GitHub Actions
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Any
import math
import glob
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RobustDataFetcher:
    """Clase para obtener datos de forma robusta con retry logic"""
    
    def __init__(self):
        self.session = self._create_robust_session()
        self.request_count = 0
        self.last_request_time = 0
        
    def _create_robust_session(self):
        """Crea sesión HTTP robusta con retry logic"""
        session = requests.Session()
        
        # Configurar retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers realistas para evitar detección como bot
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _smart_delay(self):
        """Delay inteligente para evitar rate limiting"""
        self.request_count += 1
        current_time = time.time()
        
        # Rate limiting: max 1 request por segundo
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0:
            sleep_time = 1.0 - time_since_last + random.uniform(0.1, 0.3)
            time.sleep(sleep_time)
        
        # Delay adicional cada 10 requests
        if self.request_count % 10 == 0:
            time.sleep(random.uniform(1.0, 2.0))
        
        # Delay más largo cada 50 requests para evitar throttling
        if self.request_count % 50 == 0:
            print(f"🛑 Pausa preventiva tras {self.request_count} requests...")
            time.sleep(random.uniform(3.0, 5.0))
        
        self.last_request_time = time.time()
    
    def robust_yfinance_history(self, symbol, period="6mo", max_retries=3):
        """Obtiene datos históricos de forma robusta"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, timeout=30)
                
                if len(hist) > 0:
                    return hist
                
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    print(f"⚠️ {symbol}: Reintentando en {sleep_time:.1f}s (intento {attempt + 1}/{max_retries})")
                    time.sleep(sleep_time)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ {symbol}: Falló tras {max_retries} intentos: {str(e)[:100]}")
                    return pd.DataFrame()
                else:
                    sleep_time = (2 ** attempt) + random.uniform(1.0, 2.0)
                    print(f"⚠️ {symbol}: Error {str(e)[:50]}, reintentando en {sleep_time:.1f}s")
                    time.sleep(sleep_time)
        
        return pd.DataFrame()
    
    def robust_yfinance_info(self, symbol, max_retries=3):
        """Obtiene info fundamental de forma robusta"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and isinstance(info, dict) and len(info) > 5:
                    return info
                
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(sleep_time)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return {}
                else:
                    sleep_time = (2 ** attempt) + random.uniform(1.0, 2.0)
                    time.sleep(sleep_time)
        
        return {}
    
    def robust_api_request(self, url, headers=None, params=None, max_retries=3):
        """Request HTTP robusto con retry logic"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    params=params, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited - esperar más tiempo
                    sleep_time = (3 ** attempt) + random.uniform(2.0, 5.0)
                    print(f"🚫 Rate limited, esperando {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                else:
                    if attempt < max_retries - 1:
                        sleep_time = (2 ** attempt) + random.uniform(1.0, 2.0)
                        time.sleep(sleep_time)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"❌ Request falló tras {max_retries} intentos: {str(e)[:100]}")
                    return None
                else:
                    sleep_time = (2 ** attempt) + random.uniform(1.0, 2.0)
                    time.sleep(sleep_time)
        
        return None

class MomentumResponsiveScreener:
    def __init__(self):
        self.stock_symbols = []
        self.spy_benchmark = None
        self.max_allowed_risk = 10.0  # 🛡️ SAGRADO: Máximo 10% de riesgo
        self.rr_weight = 12.0  # Peso R/R en score final
        
        # PARÁMETROS PARA MOMENTUM AGRESIVO
        self.momentum_20d_weight = 0.7   # 70% peso al momentum 20d
        self.momentum_60d_weight = 0.3   # 30% peso al momentum 60d
        self.momentum_90d_weight = 0.0   # 0% peso al momentum 90d (eliminado)
        
        # FILTROS MÁS AGRESIVOS PARA CAPTURAR MOMENTUM EMERGENTE
        self.min_outperf_20d = 5.0       # Era 2% - más agresivo
        self.min_outperf_60d = 0.0       # Era 5% - solo evitar losers obvios
        
        # 🌟 NUEVO: BONUS ESPECIAL PARA REBOTE MA50
        self.ma50_stop_bonus = 22  # 22 puntos extra por rebote MA50
        
        # 🔧 NUEVO: Data fetcher robusto
        self.data_fetcher = RobustDataFetcher()
        
        print(f"🚀 Screener inicializado - BONUS MA50: +{self.ma50_stop_bonus} pts")
        print(f"🔧 Modo robusto activado - Rate limiting inteligente habilitado")
    
    def get_nyse_nasdaq_symbols(self):
        """Obtiene símbolos de NYSE y NASDAQ combinados - VERSIÓN ROBUSTA"""
        all_symbols = []
        
        try:
            print("🔍 Obteniendo símbolos NYSE/NASDAQ con retry logic...")
            nyse_symbols = self.get_exchange_symbols('NYSE')
            nasdaq_symbols = self.get_exchange_symbols('NASDAQ')
            
            all_symbols = list(set(nyse_symbols + nasdaq_symbols))
            print(f"✓ NYSE: {len(nyse_symbols)} | NASDAQ: {len(nasdaq_symbols)} | Total: {len(all_symbols)} símbolos")
            
            return all_symbols
            
        except Exception as e:
            print(f"⚠️ Error obteniendo símbolos: {e}")
            backup_symbols = self.get_backup_symbols()
            print(f"🔄 Usando lista de respaldo: {len(backup_symbols)} símbolos")
            return backup_symbols
    
    def get_exchange_symbols(self, exchange):
        """Obtiene símbolos de un exchange específico - VERSIÓN ROBUSTA"""
        try:
            url = "https://api.nasdaq.com/api/screener/stocks"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://www.nasdaq.com/market-activity/stocks/screener'
            }
            
            params = {
                'tableonly': 'true',
                'limit': '25000',
                'exchange': exchange
            }
            
            # Usar el fetcher robusto
            response = self.data_fetcher.robust_api_request(url, headers=headers, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                if 'data' in data and 'table' in data['data']:
                    symbols = [row['symbol'] for row in data['data']['table']['rows']]
                    return symbols
            
            return []
            
        except Exception as e:
            print(f"❌ Error obteniendo símbolos de {exchange}: {e}")
            return []
    
    def get_backup_symbols(self):
        """Lista de respaldo con principales acciones"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'DIS',
            'JPM', 'BAC', 'V', 'MA', 'BRK-B', 'XOM', 'CVX',
            'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'LLY',
            'CRM', 'ORCL', 'ADBE', 'IBM', 'INTC', 'CSCO',
            'NOW', 'AMGN', 'COST', 'QCOM', 'TXN', 'HON', 'UPS',
            'LOW', 'SBUX', 'MDT', 'BMY', 'NEE', 'PM', 'RTX',
            'SPGI', 'GS', 'BLK', 'BKNG', 'ISRG', 'CVS', 'DE'
        ]
    
    def calculate_spy_benchmark(self):
        """Calcula rendimientos de SPY para benchmarking - VERSIÓN ROBUSTA"""
        try:
            print("📊 Calculando benchmark SPY con retry logic...")
            spy_data = self.data_fetcher.robust_yfinance_history("SPY", period="6mo")
            
            if len(spy_data) < 100:
                print("⚠️ SPY: Datos insuficientes, usando valores por defecto")
                return {
                    'return_20d': 2.0,
                    'return_60d': 5.0,
                    'return_90d': 8.0
                }
            
            spy_current = spy_data['Close'].iloc[-1]
            spy_20d_ago = spy_data['Close'].iloc[-21] if len(spy_data) >= 21 else spy_current
            spy_60d_ago = spy_data['Close'].iloc[-61] if len(spy_data) >= 61 else spy_current
            spy_90d_ago = spy_data['Close'].iloc[-91] if len(spy_data) >= 91 else spy_current
            
            spy_return_20d = ((spy_current - spy_20d_ago) / spy_20d_ago) * 100
            spy_return_60d = ((spy_current - spy_60d_ago) / spy_60d_ago) * 100
            spy_return_90d = ((spy_current - spy_90d_ago) / spy_90d_ago) * 100
            
            benchmark = {
                'return_20d': spy_return_20d,
                'return_60d': spy_return_60d,
                'return_90d': spy_return_90d
            }
            
            print(f"✅ SPY Benchmark: 20d={spy_return_20d:.1f}% | 60d={spy_return_60d:.1f}% | 90d={spy_return_90d:.1f}%")
            return benchmark
            
        except Exception as e:
            print(f"❌ Error calculando SPY benchmark: {e}")
            # Valores por defecto razonables
            return {
                'return_20d': 2.0,
                'return_60d': 5.0,
                'return_90d': 8.0
            }
    
    def calculate_weekly_atr(self, hist):
        """Calcula Weekly ATR (Average True Range)"""
        try:
            if len(hist) < 14:
                return 0
            
            # Datos semanales (viernes)
            weekly_data = hist.resample('W-FRI').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            if len(weekly_data) < 7:
                return 0
            
            # True Range semanal
            weekly_data['prev_close'] = weekly_data['Close'].shift(1)
            weekly_data['tr1'] = weekly_data['High'] - weekly_data['Low']
            weekly_data['tr2'] = abs(weekly_data['High'] - weekly_data['prev_close'])
            weekly_data['tr3'] = abs(weekly_data['Low'] - weekly_data['prev_close'])
            weekly_data['true_range'] = weekly_data[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # ATR de 7 semanas
            weekly_atr = weekly_data['true_range'].tail(7).mean()
            return weekly_atr
            
        except Exception as e:
            return 0
    
    def is_near_ma50_support(self, hist, current_price):
        """
        🌟 DETECTA REBOTE EN MA50 PARA BONUS
        Solo retorna True/False, no modifica lógica de trading
        """
        try:
            if len(hist) < 50:
                return False
            
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # Rango de ±3% para considerar "cerca" de MA50
            distance_pct = abs((current_price - ma50) / ma50) * 100
            
            # Debe estar dentro del 3% de MA50
            if distance_pct > 3.0:
                return False
            
            # Verificar que esté por encima (rebote, no rotura)
            if current_price < ma50 * 0.99:  # 1% de margen
                return False
            
            # Verificar tendencia alcista reciente (últimos 5 días)
            recent_returns = hist['Close'].pct_change().tail(5).sum()
            if recent_returns < 0:
                return False
            
            return True
            
        except Exception as e:
            return False
    
    def get_fundamental_data(self, symbol):
        """Obtiene datos fundamentales - VERSIÓN ROBUSTA"""
        fundamental_data = {
            'fundamental_score': 0,
            'earnings_growth': None,
            'revenue_growth': None,
            'roe': None
        }
        
        try:
            # Usar fetcher robusto
            ticker_info = self.data_fetcher.robust_yfinance_info(symbol)
            
            if not ticker_info:
                return fundamental_data
            
            # Earnings growth
            earnings_growth = ticker_info.get('earningsQuarterlyGrowth')
            if earnings_growth is not None and earnings_growth > 0:
                fundamental_data['earnings_growth'] = earnings_growth
                if earnings_growth > 0.50:
                    fundamental_data['fundamental_score'] += 25
                elif earnings_growth > 0.25:
                    fundamental_data['fundamental_score'] += 20
                elif earnings_growth > 0.15:
                    fundamental_data['fundamental_score'] += 15
                else:
                    fundamental_data['fundamental_score'] += 10
            
            # Revenue growth
            revenue_growth = ticker_info.get('revenueQuarterlyGrowth')
            if revenue_growth is not None:
                fundamental_data['revenue_growth'] = revenue_growth
                if revenue_growth > 0.25:
                    fundamental_data['fundamental_score'] += 20
                elif revenue_growth > 0.10:
                    fundamental_data['fundamental_score'] += 15
                elif revenue_growth > 0:
                    fundamental_data['fundamental_score'] += 10
            
            # ROE
            roe = ticker_info.get('returnOnEquity')
            if roe is not None:
                fundamental_data['roe'] = roe
                if roe > 0.20:
                    fundamental_data['fundamental_score'] += 15
                elif roe > 0.15:
                    fundamental_data['fundamental_score'] += 10
                elif roe > 0.10:
                    fundamental_data['fundamental_score'] += 5
            
            return fundamental_data
            
        except Exception as e:
            return fundamental_data
    
    def normalize_symbol(self, symbol):
        """Convierte símbolos de formato NASDAQ a formato Yahoo Finance"""
        if not symbol or not isinstance(symbol, str):
            return symbol
        
        symbol = symbol.strip().upper()
        
        # Skip índices que empiezan con ^
        if symbol.startswith('^'):
            return symbol
        
        # Símbolos de bankruptcy/delisted con Q
        if symbol.endswith('Q') and len(symbol) > 1:
            return symbol
        
        # Preferred stocks - múltiples patrones
        if '^' in symbol:
            parts = symbol.split('^')
            if len(parts) == 2:
                base, suffix = parts
                if suffix.isalpha() and len(suffix) <= 2:
                    return f"{base}-P{suffix}"
        
        if 'p' in symbol and len(symbol) > 3:
            p_index = symbol.rfind('p')
            if p_index > 0 and p_index < len(symbol) - 1:
                base = symbol[:p_index]
                suffix = symbol[p_index + 1:]
                if len(suffix) <= 2 and suffix.isalnum():
                    return f"{base}-P{suffix}"
        
        # Class shares con punto
        if '.' in symbol:
            parts = symbol.split('.')
            if len(parts) == 2 and len(parts[1]) <= 2:
                return f"{parts[0]}-{parts[1]}"
        
        return symbol
    
    def evaluate_stock_momentum_responsive(self, symbol):
        """
        🌟 EVALUACIÓN COMPLETA CON BONUS MA50 - VERSIÓN ROBUSTA
        Solo cambio: añade bonus de 22 puntos cuando stop loss es MA50
        + Robustez en obtención de datos
        """
        try:
            normalized_symbol = self.normalize_symbol(symbol)
            if not normalized_symbol:
                return None
            
            # USAR FETCHER ROBUSTO
            hist = self.data_fetcher.robust_yfinance_history(normalized_symbol, period="6mo")
            
            if len(hist) < 100:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Filtros básicos
            if current_price < 5.0 or current_price > 1000.0:
                return None
            
            volume_avg_30d = hist['Volume'].tail(30).mean()
            if volume_avg_30d < 1_000_000:
                return None
            
            # Calcular outperformance vs SPY
            if not self.spy_benchmark:
                return None
            
            # Returns de la acción
            price_20d = hist['Close'].iloc[-21] if len(hist) >= 21 else current_price
            price_60d = hist['Close'].iloc[-61] if len(hist) >= 61 else current_price
            price_90d = hist['Close'].iloc[-91] if len(hist) >= 91 else current_price
            
            return_20d = ((current_price - price_20d) / price_20d) * 100
            return_60d = ((current_price - price_60d) / price_60d) * 100
            return_90d = ((current_price - price_90d) / price_90d) * 100
            
            # Outperformance vs SPY
            outperformance_20d = return_20d - self.spy_benchmark['return_20d']
            outperformance_60d = return_60d - self.spy_benchmark['return_60d']
            outperformance_90d = return_90d - self.spy_benchmark['return_90d']
            
            # Filtros de outperformance más agresivos
            if outperformance_20d < self.min_outperf_20d:
                return None
            if outperformance_60d < self.min_outperf_60d:
                return None
            
            # TENDENCIA - Filtros técnicos
            ma21 = hist['Close'].rolling(window=21).mean().iloc[-1]
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            ma200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else ma50
            
            if not (current_price > ma21 > ma50):
                return None
            
            # ATR para stop loss y take profit
            hist['tr1'] = hist['High'] - hist['Low']
            hist['tr2'] = abs(hist['High'] - hist['Close'].shift(1))
            hist['tr3'] = abs(hist['Low'] - hist['Close'].shift(1))
            hist['true_range'] = hist[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = hist['true_range'].tail(14).mean()
            
            weekly_atr = self.calculate_weekly_atr(hist)
            
            # STOP LOSS inteligente
            support_level = min(ma21, ma50, current_price * 0.92)
            atr_stop = current_price - (atr * 2)
            stop_price = max(support_level, atr_stop)
            risk_pct = ((current_price - stop_price) / current_price) * 100
            
            if risk_pct > self.max_allowed_risk:
                return None
            
            # 🌟 DETECTAR REBOTE MA50 PARA BONUS
            is_ma50_rebote = self.is_near_ma50_support(hist, current_price)
            ma50_bonus = self.ma50_stop_bonus if is_ma50_rebote else 0
            
            # FUNDAMENTAL DATA con fetcher robusto
            fundamental_data = self.get_fundamental_data(normalized_symbol)
            
            # Verificar beneficios positivos OBLIGATORIO
            earnings_growth = fundamental_data.get('earnings_growth')
            if earnings_growth is None or earnings_growth <= 0:
                return None
            
            # MOMENTUM SCORE agresivo
            momentum_score = (
                outperformance_20d * self.momentum_20d_weight +
                outperformance_60d * self.momentum_60d_weight
            )
            
            # VOLUME SURGE
            volume_recent = hist['Volume'].tail(5).mean()
            volume_avg_30d = hist['Volume'].tail(30).mean()
            volume_surge_val = (volume_recent / volume_avg_30d - 1) * 100
            
            volume_score = 0
            if volume_surge_val > 50:
                volume_score = 15
            elif volume_surge_val > 25:
                volume_score = 10
            elif volume_surge_val > 10:
                volume_score = 5
            
            # VOLATILITY ANALYSIS
            returns_20d = hist['Close'].pct_change().tail(20)
            volatility_20d = returns_20d.std() * (252 ** 0.5) * 100
            
            volatility_bonus = 0
            volatility_rank = "MEDIUM"
            if volatility_20d < 20:
                volatility_bonus = 8
                volatility_rank = "LOW"
            elif volatility_20d < 30:
                volatility_bonus = 5
                volatility_rank = "MEDIUM"
            elif volatility_20d > 50:
                volatility_bonus = -5
                volatility_rank = "HIGH"
            
            volatility_metrics = {
                'volatility_20d': volatility_20d,
                'volatility_rank': volatility_rank
            }
            
            # RISK BONUS por bajo riesgo
            risk_bonus = 0
            if risk_pct < 5:
                risk_bonus = 10
            elif risk_pct < 7:
                risk_bonus = 5
            
            # SCORE TÉCNICO FINAL
            technical_score = max(0, 
                momentum_score * 1.2 +                                # Momentum agresivo
                ma50_bonus +                                           # 🌟 BONUS MA50
                fundamental_data.get('fundamental_score', 0) * 0.8 +  # Fundamentales
                volatility_bonus +                                     # Volatilidad
                volume_score +                                         # Volumen
                risk_bonus                                             # Risk bonus
            )
            
            # TAKE PROFIT con Weekly ATR
            take_profit_multiplier = 3.0 if weekly_atr > 0 else 3.5
            atr_for_tp = weekly_atr if weekly_atr > 0 else atr
            take_profit_price = current_price + (atr_for_tp * take_profit_multiplier)
            upside_pct = ((take_profit_price - current_price) / current_price) * 100
            
            # RISK/REWARD RATIO
            risk_reward_ratio = upside_pct / max(risk_pct, 0.1)
            
            # RR BONUS para score final
            rr_bonus = 0
            if risk_reward_ratio > 4.0:
                rr_bonus = 25
            elif risk_reward_ratio > 3.0:
                rr_bonus = 20
            elif risk_reward_ratio > 2.5:
                rr_bonus = 15
            elif risk_reward_ratio > 2.0:
                rr_bonus = 10
            
            # SCORE FINAL
            final_score = technical_score + (rr_bonus * 0.8)
            
            # INFORMACIÓN COMPLETA
            ticker_info = self.data_fetcher.robust_yfinance_info(normalized_symbol)
            company_info = {
                'name': ticker_info.get('longName', 'N/A') if ticker_info else 'N/A',
                'sector': ticker_info.get('sector', 'N/A') if ticker_info else 'N/A',
                'market_cap': ticker_info.get('marketCap', 'N/A') if ticker_info else 'N/A'
            }
            
            result = {
                'symbol': normalized_symbol,
                'score': round(final_score, 1),
                'technical_score': round(technical_score, 1),
                'rr_bonus': round(rr_bonus, 1),
                'ma50_bonus': ma50_bonus,  # 🌟 NUEVO
                'is_ma50_rebote': is_ma50_rebote,  # 🌟 NUEVO
                'current_price': round(current_price, 2),
                'stop_loss': round(stop_price, 2),
                'take_profit': round(take_profit_price, 2),
                'risk_pct': round(risk_pct, 2),
                'upside_pct': round(upside_pct, 2),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'outperformance_20d': round(outperformance_20d, 2),
                'outperformance_60d': round(outperformance_60d, 2),
                'outperformance_90d': round(outperformance_90d, 2),
                'volume_surge': round(volume_surge_val, 1),
                'fundamental_score': fundamental_data.get('fundamental_score', 0),
                'atr': round(atr, 2),
                'weekly_atr': round(weekly_atr, 2),
                'volatility_rank': volatility_metrics.get('volatility_rank', 'MEDIUM'),
                'company_info': company_info
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error evaluando {symbol}: {str(e)[:100]}")
            return None
    
    def screen_all_stocks_momentum_responsive(self):
        """Screening con 3,000+ símbolos reales + MA50 bonus - VERSIÓN ROBUSTA"""
        print(f"=== SCREENING CON ROBUSTEZ MEJORADA ===")
        print(f"🔧 Rate limiting inteligente habilitado")
        print(f"🔄 Retry logic automático configurado")
        print(f"🌟 Bonus MA50: +{self.ma50_stop_bonus} puntos por rebote")
        
        # Obtener símbolos de forma robusta
        self.stock_symbols = self.get_nyse_nasdaq_symbols()
        
        if len(self.stock_symbols) < 100:
            print("⚠️ Pocos símbolos obtenidos, usando lista extendida de respaldo...")
            self.stock_symbols = self.get_backup_symbols()
        
        # Calcular benchmark SPY de forma robusta
        self.spy_benchmark = self.calculate_spy_benchmark()
        
        results = []
        total_symbols = len(self.stock_symbols)
        processed_count = 0
        success_count = 0
        
        print(f"🚀 Iniciando análisis robusto de {total_symbols} símbolos...")
        
        start_time = time.time()
        
        for i, symbol in enumerate(self.stock_symbols):
            try:
                processed_count += 1
                
                # Progress update cada 100 símbolos
                if processed_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed
                    eta = (total_symbols - processed_count) / rate / 60
                    print(f"📊 Progreso: {processed_count}/{total_symbols} ({processed_count/total_symbols*100:.1f}%) | "
                          f"Éxitos: {success_count} | ETA: {eta:.1f}min | "
                          f"Rate: {rate:.1f} symbols/sec")
                
                result = self.evaluate_stock_momentum_responsive(symbol)
                
                if result:
                    results.append(result)
                    success_count += 1
                    
                    # Log de acciones con MA50 bonus
                    if result.get('is_ma50_rebote', False):
                        print(f"🌟 MA50 REBOTE: {symbol} (+{self.ma50_stop_bonus} pts) - Score: {result['score']}")
                
            except Exception as e:
                print(f"❌ Error procesando {symbol}: {str(e)[:100]}")
                continue
        
        elapsed = time.time() - start_time
        
        # Ordenar resultados por score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n🎯 SCREENING ROBUSTO COMPLETADO:")
        print(f"⏱️ Tiempo total: {elapsed/60:.1f} minutos")
        print(f"📊 Símbolos procesados: {processed_count}")
        print(f"✅ Éxitos: {success_count}")
        print(f"📈 Rate final: {processed_count/elapsed:.1f} symbols/sec")
        print(f"🌟 Acciones con bonus MA50: {sum(1 for r in results if r.get('is_ma50_rebote', False))}")
        print(f"🏆 Top candidates: {len([r for r in results if r['score'] >= 50])}")
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"momentum_responsive_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'execution_time_minutes': elapsed / 60,
                'symbols_processed': processed_count,
                'symbols_successful': success_count,
                'ma50_bonus_detections': sum(1 for r in results if r.get('is_ma50_rebote', False)),
                'spy_benchmark': self.spy_benchmark,
                'results': results
            }, f, indent=2)
        
        # También guardar como archivo principal
        with open('weekly_screening_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'execution_time_minutes': elapsed / 60,
                'symbols_processed': processed_count,
                'symbols_successful': success_count,
                'ma50_bonus_detections': sum(1 for r in results if r.get('is_ma50_rebote', False)),
                'spy_benchmark': self.spy_benchmark,
                'results': results
            }, f, indent=2)
        
        print(f"💾 Resultados guardados en: {filename}")
        print(f"💾 Archivo principal: weekly_screening_results.json")
        
        return results

def main():
    """Función principal con manejo robusto de errores"""
    try:
        print("🚀 Iniciando Conservative Screener - Versión Robusta")
        print("🔧 Mejoras de robustez activadas para GitHub Actions")
        
        screener = MomentumResponsiveScreener()
        results = screener.screen_all_stocks_momentum_responsive()
        
        if results:
            print(f"\n🎯 TOP 10 CANDIDATES (con robustez mejorada):")
            for i, stock in enumerate(results[:10], 1):
                ma50_indicator = " 🌟MA50" if stock.get('is_ma50_rebote', False) else ""
                print(f"{i:2d}. {stock['symbol']:6s} | Score: {stock['score']:5.1f} | "
                      f"R/R: {stock['risk_reward_ratio']:4.1f} | "
                      f"Risk: {stock['risk_pct']:4.1f}%{ma50_indicator}")
        else:
            print("⚠️ No se encontraron resultados - verificar conectividad")
        
        print("✅ Screening robusto completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Conservative Stock Screener with MA50 Stop Loss Bonus - OPTIMIZED VERSION
=========================================================================

⚡ OPTIMIZACIONES: Paralelización + Rate limiting inteligente + Filtros rápidos
📊 MANTIENE: 100% de la lógica original de trading y scoring
🎯 OBJETIVO: 3x más rápido, mismo resultado local vs GitHub Actions
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Importación compatible de Retry
try:
    from urllib3.util.retry import Retry
    RETRY_AVAILABLE = True
except ImportError:
    RETRY_AVAILABLE = False

def quick_filter_symbol(symbol):
    """Filtro rápido para descartar símbolos obvios sin requests pesados"""
    if not symbol or len(symbol) > 6:
        return False
    
    # Skip símbolos problemáticos conocidos
    problem_patterns = ['^', '.PK', '.OB', 'WARR', 'TEST']
    for pattern in problem_patterns:
        if pattern in symbol:
            return False
    
    # Skip penny stocks típicos por patrones de nombre
    if len(symbol) >= 4 and symbol.endswith(('Q', 'E', 'F')):
        return False
        
    return True

class RobustDataFetcher:
    """Clase optimizada para obtener datos con balance velocidad/robustez"""
    
    def __init__(self):
        self.session = self._create_robust_session()
        self.request_count = 0
        self.last_request_time = 0
        
    def _create_robust_session(self):
        """Crea sesión HTTP robusta - COMPATIBILIDAD MÁXIMA"""
        session = requests.Session()
        
        # Solo usar retry automático si está disponible
        if RETRY_AVAILABLE:
            try:
                try:
                    # Intentar con parámetros nuevos (urllib3 >= 1.26)
                    retry_strategy = Retry(
                        total=2,  # Reducido para velocidad
                        status_forcelist=[429, 500, 502, 503, 504],
                        allowed_methods=["HEAD", "GET", "OPTIONS"],
                        backoff_factor=0.5  # Más rápido
                    )
                except TypeError:
                    try:
                        # Fallback para urllib3 < 1.26
                        retry_strategy = Retry(
                            total=2,
                            status_forcelist=[429, 500, 502, 503, 504],
                            method_whitelist=["HEAD", "GET", "OPTIONS"],
                            backoff_factor=0.5
                        )
                    except:
                        # Fallback mínimo
                        retry_strategy = Retry(
                            total=2,
                            status_forcelist=[429, 500, 502, 503, 504],
                            backoff_factor=0.5
                        )
                
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
            except Exception:
                pass  # Continuar sin retry automático
        
        # Headers optimizados
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def _smart_delay(self):
        """Delay optimizado - 3x más rápido que versión anterior"""
        self.request_count += 1
        current_time = time.time()
        
        # Rate limiting: 3 requests por segundo (vs 1 anterior)
        time_since_last = current_time - self.last_request_time
        if time_since_last < 0.33:  # 0.33s = ~3 req/sec
            sleep_time = 0.33 - time_since_last + random.uniform(0.02, 0.08)
            time.sleep(sleep_time)
        
        # Solo delay largo cada 100 requests
        if self.request_count % 100 == 0:
            time.sleep(random.uniform(0.5, 1.0))
        
        self.last_request_time = time.time()
    
    def robust_yfinance_history(self, symbol, period="6mo", max_retries=2):
        """Obtiene datos históricos - OPTIMIZADO para velocidad"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, timeout=15)  # Timeout reducido
                
                if len(hist) > 50:
                    return hist
                
                if attempt < max_retries - 1:
                    time.sleep(0.5 + random.uniform(0.1, 0.3))
                
            except Exception:
                if attempt == max_retries - 1:
                    return pd.DataFrame()
                else:
                    time.sleep(0.5 + random.uniform(0.1, 0.5))
        
        return pd.DataFrame()
    
    def robust_yfinance_info(self, symbol, max_retries=2):
        """Obtiene info fundamental - OPTIMIZADO"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and isinstance(info, dict) and len(info) > 3:
                    return info
                
                if attempt < max_retries - 1:
                    time.sleep(0.5 + random.uniform(0.1, 0.3))
                
            except Exception:
                if attempt == max_retries - 1:
                    return {}
                else:
                    time.sleep(0.5 + random.uniform(0.1, 0.5))
        
        return {}
    
    def robust_api_request(self, url, headers=None, params=None, max_retries=2):
        """Request HTTP optimizado"""
        for attempt in range(max_retries):
            try:
                self._smart_delay()
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    params=params, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    time.sleep(1.0 + random.uniform(0.5, 1.5))
                else:
                    if attempt < max_retries - 1:
                        time.sleep(0.5 + random.uniform(0.2, 0.8))
                
            except Exception:
                if attempt == max_retries - 1:
                    return None
                else:
                    time.sleep(0.5 + random.uniform(0.2, 1.0))
        
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
        
        # 🔧 Data fetcher optimizado
        self.data_fetcher = RobustDataFetcher()
        
        print(f"🚀 Screener inicializado - BONUS MA50: +{self.ma50_stop_bonus} pts")
        print(f"⚡ Optimizaciones: Paralelización (5 threads) + Rate limiting (3 req/sec)")
        print(f"🌟 MA50 Bonus: Se aplica cuando MA50 es el stop loss óptimo seleccionado")
    
    def get_nyse_nasdaq_symbols(self):
        """Obtiene símbolos de NYSE y NASDAQ - OPTIMIZADO"""
        all_symbols = []
        
        try:
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
        """Obtiene símbolos de un exchange específico - OPTIMIZADO"""
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
            
            response = self.data_fetcher.robust_api_request(url, headers=headers, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                if 'data' in data and 'table' in data['data']:
                    symbols = [row['symbol'] for row in data['data']['table']['rows']]
                    return symbols
            
            return []
            
        except Exception:
            return []
    
    def get_backup_symbols(self):
        """Lista de respaldo optimizada"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'DIS',
            'JPM', 'BAC', 'V', 'MA', 'BRK-B', 'XOM', 'CVX',
            'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'LLY',
            'CRM', 'ORCL', 'ADBE', 'IBM', 'INTC', 'CSCO',
            'NOW', 'AMGN', 'COST', 'QCOM', 'TXN', 'HON', 'UPS',
            'LOW', 'SBUX', 'MDT', 'BMY', 'NEE', 'PM', 'RTX',
            'SPGI', 'GS', 'BLK', 'BKNG', 'ISRG', 'CVS', 'DE',
            'AMD', 'AVGO', 'GOOG', 'AMAT', 'PYPL', 'CMCSA', 'TMUS',
            'UBER', 'SHOP', 'SQ', 'ROKU', 'ZM', 'DOCU', 'CRWD'
        ]
    
    def calculate_spy_benchmark(self):
        """Calcula rendimientos de SPY - OPTIMIZADO"""
        try:
            spy_data = self.data_fetcher.robust_yfinance_history("SPY", period="6mo")
            
            if len(spy_data) < 100:
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
            
        except Exception:
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
            
            weekly_atr = weekly_data['true_range'].tail(7).mean()
            return weekly_atr
            
        except Exception:
            return 0
    
    def is_ma50_used_as_stop_loss(self, hist, current_price, stop_price):
        """🌟 VERIFICA SI MA50 SE USA COMO STOP LOSS PARA BONUS"""
        try:
            if len(hist) < 50:
                return False
            
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            ma21 = hist['Close'].rolling(window=21).mean().iloc[-1]
            
            # Verificar que MA50 sea válida
            if pd.isna(ma50) or ma50 <= 0:
                return False
            
            # Calcular los componentes del stop loss como en la lógica original
            support_level = min(ma21, ma50, current_price * 0.92)
            
            # Calcular ATR stop
            hist['tr1'] = hist['High'] - hist['Low']
            hist['tr2'] = abs(hist['High'] - hist['Close'].shift(1))
            hist['tr3'] = abs(hist['Low'] - hist['Close'].shift(1))
            hist['true_range'] = hist[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = hist['true_range'].tail(14).mean()
            atr_stop = current_price - (atr * 2)
            
            # El stop loss final es el máximo entre support_level y atr_stop
            calculated_stop = max(support_level, atr_stop)
            
            # Verificar si MA50 es efectivamente el stop loss usado
            # 1. MA50 debe ser el mínimo en support_level (ma21, ma50, current_price * 0.92)
            # 2. Y ese support_level debe ser el stop loss final (mayor que atr_stop)
            
            is_ma50_the_support = (support_level == ma50)
            is_support_the_stop = (calculated_stop == support_level)
            
            # Verificar que el stop calculado coincida con el stop pasado (tolerancia de 1%)
            stop_matches = abs(calculated_stop - stop_price) / stop_price < 0.01
            
            ma50_is_stop_loss = is_ma50_the_support and is_support_the_stop and stop_matches
            
            if ma50_is_stop_loss:
                print(f"🌟 MA50 STOP LOSS DETECTED: MA50=${ma50:.2f} | MA21=${ma21:.2f} | "
                      f"Support=${support_level:.2f} | ATR_Stop=${atr_stop:.2f} | "
                      f"Final_Stop=${calculated_stop:.2f}")
            
            return ma50_is_stop_loss
            
        except Exception as e:
            print(f"⚠️ Error verificando MA50 como stop loss: {e}")
            return False
    
    def get_fundamental_data(self, symbol):
        """Obtiene datos fundamentales - OPTIMIZADO"""
        fundamental_data = {
            'fundamental_score': 0,
            'earnings_growth': None,
            'revenue_growth': None,
            'roe': None
        }
        
        try:
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
            
        except Exception:
            return fundamental_data
    
    def normalize_symbol(self, symbol):
        """Convierte símbolos de formato NASDAQ a formato Yahoo Finance"""
        if not symbol or not isinstance(symbol, str):
            return symbol
        
        symbol = symbol.strip().upper()
        
        if symbol.startswith('^'):
            return symbol
        
        if symbol.endswith('Q') and len(symbol) > 1:
            return symbol
        
        # Preferred stocks
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
        """🌟 EVALUACIÓN COMPLETA CON BONUS MA50 - OPTIMIZADA"""
        try:
            normalized_symbol = self.normalize_symbol(symbol)
            if not normalized_symbol:
                return None
            
            # USAR FETCHER OPTIMIZADO
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
            
            # Filtros de outperformance
            if outperformance_20d < self.min_outperf_20d:
                return None
            if outperformance_60d < self.min_outperf_60d:
                return None
            
            # TENDENCIA
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
            
            # 🌟 VERIFICAR SI MA50 SE USA COMO STOP LOSS PARA BONUS
            is_ma50_stop_loss = self.is_ma50_used_as_stop_loss(hist, current_price, stop_price)
            ma50_bonus = self.ma50_stop_bonus if is_ma50_stop_loss else 0
            
            # Log específico para MA50 bonus
            if is_ma50_stop_loss:
                print(f"🌟 {normalized_symbol}: MA50 COMO STOP LOSS (+{ma50_bonus} pts) | "
                      f"Stop: ${stop_price:.2f} | MA50: ${ma50:.2f}")
            
            # FUNDAMENTAL DATA
            fundamental_data = self.get_fundamental_data(normalized_symbol)
            
            # Verificar beneficios positivos OBLIGATORIO
            earnings_growth = fundamental_data.get('earnings_growth')
            if earnings_growth is None or earnings_growth <= 0:
                return None
            
            # MOMENTUM SCORE
            momentum_score = (
                outperformance_20d * self.momentum_20d_weight +
                outperformance_60d * self.momentum_60d_weight
            )
            
            # VOLUME SURGE
            volume_recent = hist['Volume'].tail(5).mean()
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
            
            # RISK BONUS
            risk_bonus = 0
            if risk_pct < 5:
                risk_bonus = 10
            elif risk_pct < 7:
                risk_bonus = 5
            
            # SCORE TÉCNICO FINAL
            technical_score = max(0, 
                momentum_score * 1.2 +
                ma50_bonus +
                fundamental_data.get('fundamental_score', 0) * 0.8 +
                volatility_bonus +
                volume_score +
                risk_bonus
            )
            
            # TAKE PROFIT
            take_profit_multiplier = 3.0 if weekly_atr > 0 else 3.5
            atr_for_tp = weekly_atr if weekly_atr > 0 else atr
            take_profit_price = current_price + (atr_for_tp * take_profit_multiplier)
            upside_pct = ((take_profit_price - current_price) / current_price) * 100
            
            # RISK/REWARD RATIO
            risk_reward_ratio = upside_pct / max(risk_pct, 0.1)
            
            # RR BONUS
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
                'ma50_bonus': ma50_bonus,
                'is_ma50_stop_loss': is_ma50_stop_loss,  # Cambiado nombre
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
                'volatility_rank': volatility_rank,
                'company_info': company_info
            }
            
            return result
            
        except Exception:
            return None
    
    def process_symbol_batch(self, symbols_batch):
        """Procesa un lote de símbolos"""
        results = []
        for symbol in symbols_batch:
            try:
                result = self.evaluate_stock_momentum_responsive(symbol)
                if result:
                    results.append(result)
            except Exception:
                continue
        return results
    
    def screen_all_stocks_momentum_responsive(self):
        """Screening OPTIMIZADO con paralelización"""
        print(f"=== CONSERVATIVE SCREENER OPTIMIZADO ===")
        print(f"🌟 Bonus MA50: +{self.ma50_stop_bonus} puntos")
        print(f"🚀 Paralelización: 5 threads habilitados")
        print(f"🎯 MA50 Bonus: Solo cuando MA50 es el stop loss seleccionado por el algoritmo")
        
        # Obtener símbolos
        self.stock_symbols = self.get_nyse_nasdaq_symbols()
        
        if len(self.stock_symbols) < 100:
            self.stock_symbols = self.get_backup_symbols()
        
        # FILTRO RÁPIDO: Sin requests HTTP
        print(f"🔍 Aplicando filtro rápido a {len(self.stock_symbols)} símbolos...")
        filtered_symbols = [s for s in self.stock_symbols if quick_filter_symbol(s)]
        print(f"✅ Filtro rápido: {len(filtered_symbols)} símbolos ({len(filtered_symbols)/len(self.stock_symbols)*100:.1f}%)")
        
        # Calcular benchmark SPY
        self.spy_benchmark = self.calculate_spy_benchmark()
        
        # PARALELIZACIÓN
        batch_size = 20
        batches = [filtered_symbols[i:i + batch_size] for i in range(0, len(filtered_symbols), batch_size)]
        
        print(f"🔄 Procesando {len(batches)} lotes de {batch_size} símbolos...")
        print("=" * 60)
        
        all_results = []
        start_time = time.time()
        
        # Procesar con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_batch = {
                executor.submit(self.process_symbol_batch, batch): i 
                for i, batch in enumerate(batches)
            }
            
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                    
                    # Progress cada 10 lotes con información detallada
                    if (batch_idx + 1) % 10 == 0:
                        elapsed = time.time() - start_time
                        processed = (batch_idx + 1) * batch_size
                        total = len(filtered_symbols)
                        remaining_batches = len(batches) - (batch_idx + 1)
                        eta_minutes = (remaining_batches * elapsed / (batch_idx + 1)) / 60 if (batch_idx + 1) > 0 else 0
                        
                        ma50_count = sum(1 for r in all_results if r.get('is_ma50_stop_loss', False))
                        avg_score = sum(r.get('score', 0) for r in all_results) / len(all_results) if all_results else 0
                        
                        print(f"📊 Lote {batch_idx+1}/{len(batches)} | "
                              f"Procesados: {processed}/{total} ({processed/total*100:.1f}%) | "
                              f"Candidatos: {len(all_results)} | "
                              f"🌟 MA50 Stop Loss: {ma50_count} | "
                              f"Score Promedio: {avg_score:.1f} | "
                              f"ETA: {eta_minutes:.1f}min")
                        
                        # Log de ejemplo de último candidato con MA50 como stop loss
                        recent_ma50 = [r for r in all_results if r.get('is_ma50_stop_loss', False)]
                        if recent_ma50:
                            last_ma50 = recent_ma50[-1]
                            print(f"     🌟 Último MA50 Stop: {last_ma50.get('symbol', 'N/A')} (Score: {last_ma50.get('score', 0):.1f})")
                        
                except Exception:
                    continue
        
        elapsed = time.time() - start_time
        
        # Ordenar resultados
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        ma50_bonus_count = sum(1 for r in all_results if r.get('is_ma50_stop_loss', False))
        
        print(f"\n🎯 SCREENING OPTIMIZADO COMPLETADO:")
        print(f"⏱️ Tiempo: {elapsed/60:.1f} minutos")
        print(f"🔍 Símbolos: {len(filtered_symbols)}")
        print(f"✅ Candidatos: {len(all_results)}")
        print(f"🌟 MA50 como Stop Loss: {ma50_bonus_count}")
        print(f"📈 Velocidad: {len(filtered_symbols)/(elapsed/60):.0f} símbolos/min")
        
        # Mostrar específicamente las acciones con MA50 como stop loss
        if ma50_bonus_count > 0:
            ma50_stocks = [r for r in all_results if r.get('is_ma50_stop_loss', False)]
            print(f"\n🌟 ACCIONES CON MA50 COMO STOP LOSS (+{self.ma50_stop_bonus} pts):")
            for i, stock in enumerate(ma50_stocks[:10], 1):  # Top 10 con MA50 stop loss
                price = stock.get('current_price', 0)
                stop = stock.get('stop_loss', 0)
                score = stock.get('score', 0)
                technical_score = stock.get('technical_score', 0)
                print(f"  {i:2d}. {stock.get('symbol', 'N/A'):6s} | "
                      f"Score: {score:5.1f} (Base: {technical_score-self.ma50_stop_bonus:.1f} + MA50: +{self.ma50_stop_bonus}) | "
                      f"Price: ${price:.2f} | Stop: ${stop:.2f}")
        else:
            print(f"\n⚠️ NINGUNA ACCIÓN USA MA50 COMO STOP LOSS")
            print(f"   Esto significa que para todas las acciones analizadas:")
            print(f"   - MA21, precio*0.92, o ATR stop fueron mejores opciones")
            print(f"   - MA50 no fue el nivel de soporte óptimo")
            print(f"   - Es normal en mercados con tendencias fuertes")
        
        # Guardar resultados
        self.save_results_optimized(all_results, elapsed, len(filtered_symbols), ma50_bonus_count)
        
        return all_results
    
    def save_results_optimized(self, results, elapsed_time, symbols_processed, ma50_count):
        """Guarda resultados"""
        top_15 = results[:15]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"momentum_responsive_results_{timestamp}.json"
        
        # Archivo con timestamp
        result_data = {
            'timestamp': datetime.now().isoformat(),
            'execution_time_minutes': elapsed_time / 60,
            'symbols_processed': symbols_processed,
            'symbols_successful': len(results),
            'ma50_bonus_detections': ma50_count,
            'optimization_enabled': True,
            'parallel_processing': True,
            'spy_benchmark': self.spy_benchmark,
            'results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        # Archivo principal
        screening_data = {
            'analysis_date': datetime.now().isoformat(),
            'execution_time_minutes': elapsed_time / 60,
            'symbols_analyzed': symbols_processed,
            'results_count': len(results),
            'ma50_bonus_count': ma50_count,
            'analysis_type': 'momentum_responsive_optimized',
            'optimizations': {
                'parallel_processing': True,
                'quick_filtering': True,
                'ma50_bonus_system': True,
                'ma50_bonus_value': self.ma50_stop_bonus
            },
            'top_symbols': [r['symbol'] for r in top_15],
            'detailed_results': top_15,
            'benchmark_context': {
                'spy_20d': self.spy_benchmark['return_20d'] if self.spy_benchmark else 0,
                'spy_60d': self.spy_benchmark['return_60d'] if self.spy_benchmark else 0,
                'spy_90d': self.spy_benchmark['return_90d'] if self.spy_benchmark else 0
            }
        }
        
        with open('weekly_screening_results.json', 'w') as f:
            json.dump(screening_data, f, indent=2, default=str)
        
        print(f"💾 Archivos guardados: {filename} + weekly_screening_results.json")

def test_ma50_detection():
    """Función de test para verificar MA50 como stop loss"""
    print("🔍 === TEST DE MA50 COMO STOP LOSS ===")
    
    screener = MomentumResponsiveScreener()
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    print(f"Probando si MA50 es elegida como stop loss en {len(test_symbols)} símbolos...")
    
    for symbol in test_symbols:
        try:
            hist = screener.data_fetcher.robust_yfinance_history(symbol, period="6mo")
            if len(hist) < 50:
                print(f"❌ {symbol}: Datos insuficientes ({len(hist)} días)")
                continue
                
            current_price = hist['Close'].iloc[-1]
            ma21 = hist['Close'].rolling(window=21).mean().iloc[-1]
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # Simular cálculo de stop loss
            support_level = min(ma21, ma50, current_price * 0.92)
            hist['tr1'] = hist['High'] - hist['Low']
            hist['tr2'] = abs(hist['High'] - hist['Close'].shift(1))
            hist['tr3'] = abs(hist['Low'] - hist['Close'].shift(1))
            hist['true_range'] = hist[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = hist['true_range'].tail(14).mean()
            atr_stop = current_price - (atr * 2)
            final_stop = max(support_level, atr_stop)
            
            is_ma50_stop = screener.is_ma50_used_as_stop_loss(hist, current_price, final_stop)
            
            if is_ma50_stop:
                print(f"🌟 {symbol}: MA50 ES EL STOP LOSS (+{screener.ma50_stop_bonus} pts)")
                print(f"     MA21: ${ma21:.2f} | MA50: ${ma50:.2f} | 0.92*Price: ${current_price*0.92:.2f}")
                print(f"     Support: ${support_level:.2f} | ATR Stop: ${atr_stop:.2f} | Final: ${final_stop:.2f}")
            else:
                print(f"⚪ {symbol}: MA50 NO es stop loss")
                print(f"     MA21: ${ma21:.2f} | MA50: ${ma50:.2f} | ATR Stop: ${atr_stop:.2f} | Final: ${final_stop:.2f}")
                
        except Exception as e:
            print(f"❌ {symbol}: Error en test - {e}")
    
    print("=== FIN TEST MA50 STOP LOSS ===\n")

def main():
    """Función principal optimizada"""
    try:
        print("🚀 Conservative Screener - Versión Optimizada")
        print("⚡ Paralelización + Rate limiting (3 req/sec)")
        
        # Test opcional del MA50 (comentar para producción)
        # test_ma50_detection()
        
        screener = MomentumResponsiveScreener()
        results = screener.screen_all_stocks_momentum_responsive()
        
        if results:
            print(f"\n🏆 TOP 10 CANDIDATOS:")
            for i, stock in enumerate(results[:10], 1):
                ma50_indicator = " 🌟" if stock.get('is_ma50_stop_loss', False) else ""
                ma50_bonus_val = stock.get('ma50_bonus', 0)
                score_breakdown = f"Score: {stock['score']:5.1f}"
                if ma50_bonus_val > 0:
                    base_score = stock['score'] - ma50_bonus_val
                    score_breakdown = f"Score: {stock['score']:5.1f} (Base: {base_score:.1f} + MA50: +{ma50_bonus_val})"
                
                print(f"{i:2d}. {stock['symbol']:6s} | "
                      f"{score_breakdown} | "
                      f"R/R: {stock['risk_reward_ratio']:4.1f} | "
                      f"Risk: {stock['risk_pct']:4.1f}%{ma50_indicator}")
            
            # Estadísticas adicionales del MA50 bonus
            ma50_count = sum(1 for r in results if r.get('is_ma50_stop_loss', False))
            if ma50_count > 0:
                print(f"\n🌟 RESUMEN MA50 STOP LOSS BONUS:")
                print(f"   - Total usando MA50 como stop: {ma50_count}")
                print(f"   - Valor del bonus: +{results[0].get('ma50_bonus', 22)} pts cada uno")
                print(f"   - Porcentaje: {ma50_count/len(results)*100:.1f}% de candidatos")
                print(f"   - Concepto: Bonus por usar MA50 como nivel de stop loss óptimo")
            else:
                print(f"\n⚠️ Ninguna acción usa MA50 como stop loss en esta ejecución")
                print(f"   (MA21, precio*0.92, o ATR stop fueron mejores opciones)")
        else:
            print("⚠️ Sin resultados - verificar conectividad")
        
        print("✅ Screening optimizado completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
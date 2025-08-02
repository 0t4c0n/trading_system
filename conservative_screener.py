#!/usr/bin/env python3
"""
Conservative Stock Screener with MA50 Stop Loss Bonus
=====================================================

🌟 CAMBIO MÍNIMO: Solo añade bonus de +22 puntos para rebotes en MA50
📊 MANTIENE: Toda la funcionalidad original de obtención de símbolos NYSE/NASDAQ
🎯 FILOSOFÍA: Daily monitoring, monthly trading
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
        
        print(f"🚀 Screener inicializado - BONUS MA50: +{self.ma50_stop_bonus} pts")
    
    def get_nyse_nasdaq_symbols(self):
        """Obtiene símbolos de NYSE y NASDAQ combinados"""
        all_symbols = []
        
        try:
            nyse_symbols = self.get_exchange_symbols('NYSE')
            nasdaq_symbols = self.get_exchange_symbols('NASDAQ')
            
            all_symbols = list(set(nyse_symbols + nasdaq_symbols))
            print(f"✓ NYSE: {len(nyse_symbols)} | NASDAQ: {len(nasdaq_symbols)} | Total: {len(all_symbols)} símbolos")
            
            return all_symbols
            
        except Exception as e:
            print(f"Error obteniendo símbolos: {e}")
            backup_symbols = self.get_backup_symbols()
            print(f"Usando lista de respaldo: {len(backup_symbols)} símbolos")
            return backup_symbols
    
    def get_exchange_symbols(self, exchange):
        """Obtiene símbolos de un exchange específico"""
        try:
            url = "https://api.nasdaq.com/api/screener/stocks"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'tableonly': 'true',
                'limit': '25000',
                'exchange': exchange
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'table' in data['data']:
                    symbols = [row['symbol'] for row in data['data']['table']['rows']]
                    return symbols
            
            return []
            
        except Exception as e:
            print(f"Error obteniendo símbolos de {exchange}: {e}")
            return []
    
    def get_backup_symbols(self):
        """Lista de respaldo con principales acciones"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'DIS',
            'JPM', 'BAC', 'V', 'MA', 'BRK-B', 'XOM', 'CVX',
            'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'LLY',
            'CRM', 'ORCL', 'ADBE', 'IBM', 'INTC', 'CSCO'
        ]
    
    def calculate_spy_benchmark(self):
        """Calcula rendimientos de SPY para benchmarking"""
        try:
            spy_ticker = yf.Ticker("SPY")
            spy_data = spy_ticker.history(period="6mo")
            
            if len(spy_data) < 100:
                print("⚠️ SPY: Datos insuficientes")
                return None
            
            spy_current = spy_data['Close'].iloc[-1]
            spy_20d_ago = spy_data['Close'].iloc[-21] if len(spy_data) >= 21 else spy_current
            spy_60d_ago = spy_data['Close'].iloc[-61] if len(spy_data) >= 61 else spy_current
            spy_90d_ago = spy_data['Close'].iloc[-91] if len(spy_data) >= 91 else spy_current
            
            return {
                'current_price': spy_current,
                'return_20d': ((spy_current / spy_20d_ago) - 1) * 100,
                'return_60d': ((spy_current / spy_60d_ago) - 1) * 100,
                'return_90d': ((spy_current / spy_90d_ago) - 1) * 100
            }
            
        except Exception as e:
            print(f"Error calculando SPY benchmark: {e}")
            return None
    
    def calculate_weekly_atr(self, hist, period=14):
        """Calcula Weekly ATR para take profit optimizado"""
        try:
            if len(hist) < period * 7:
                return 0
            
            # Resample a weekly data
            weekly_data = hist.resample('W').agg({
                'Open': 'first',
                'High': 'max', 
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            if len(weekly_data) < period:
                return 0
            
            # True Range para datos semanales
            weekly_data['PrevClose'] = weekly_data['Close'].shift(1)
            weekly_data['TR'] = np.maximum(
                weekly_data['High'] - weekly_data['Low'],
                np.maximum(
                    abs(weekly_data['High'] - weekly_data['PrevClose']),
                    abs(weekly_data['Low'] - weekly_data['PrevClose'])
                )
            )
            
            # Weekly ATR
            weekly_atr = weekly_data['TR'].rolling(period).mean().iloc[-1]
            return weekly_atr if not pd.isna(weekly_atr) else 0
            
        except Exception as e:
            return 0
    
    def calculate_support_resistance(self, hist):
        """Calcula niveles de soporte y resistencia"""
        try:
            if len(hist) < 20:
                return {'support': None, 'resistance': None}
            
            recent_data = hist.tail(60)
            
            # Soporte: mínimos significativos
            lows = recent_data['Low'].rolling(5, center=True).min()
            support_candidates = recent_data[recent_data['Low'] == lows]['Low'].dropna()
            support = support_candidates.quantile(0.2) if len(support_candidates) > 0 else None
            
            # Resistencia: máximos significativos  
            highs = recent_data['High'].rolling(5, center=True).max()
            resistance_candidates = recent_data[recent_data['High'] == highs]['High'].dropna()
            resistance = resistance_candidates.quantile(0.8) if len(resistance_candidates) > 0 else None
            
            return {
                'support': support,
                'resistance': resistance
            }
            
        except Exception as e:
            return {'support': None, 'resistance': None}
    
    def calculate_volatility_metrics(self, hist):
        """Calcula métricas de volatilidad"""
        try:
            if len(hist) < 30:
                return {'volatility_rank': 'UNKNOWN'}
            
            returns = hist['Close'].pct_change().dropna()
            volatility_30d = returns.tail(30).std() * np.sqrt(252) * 100
            
            # Ranking de volatilidad
            if volatility_30d < 25:
                vol_rank = 'LOW'
            elif volatility_30d < 45:
                vol_rank = 'MEDIUM'
            else:
                vol_rank = 'HIGH'
            
            return {
                'volatility_30d': volatility_30d,
                'volatility_rank': vol_rank
            }
            
        except Exception as e:
            return {'volatility_rank': 'UNKNOWN'}
    
    def calculate_ultra_conservative_stop_loss(self, hist, current_price, atr, support_resistance, volatility_metrics):
        """
        🌟 MODIFICADO: Calcula stop loss con PRIORIDAD PARA MA50 y bonus
        """
        try:
            if len(hist) < 50:
                return {
                    'stop_price': current_price * 0.92,
                    'risk_percentage': 8.0,
                    'methods_used': ['insufficient_data_fallback'],
                    'stop_selection': 'insufficient_data',
                    'ma50_bonus_eligible': False
                }
            
            all_stops = {}
            
            # ATR stop
            atr_stop = current_price - (atr * 2.0)
            if atr_stop > 0:
                atr_risk = ((current_price - atr_stop) / current_price) * 100
                if 5 < atr_risk <= 10.0:
                    all_stops['atr'] = {
                        'price': atr_stop,
                        'risk': atr_risk
                    }
            
            # Support stop
            support = support_resistance.get('support')
            if support and support > 0:
                support_stop = support * 0.98
                if support_stop > 0:
                    support_risk = ((current_price - support_stop) / current_price) * 100
                    if 5 < support_risk <= 10.0:
                        all_stops['support'] = {
                            'price': support_stop,
                            'risk': support_risk
                        }
            
            # Moving averages stops
            ma21_stop_data = None
            ma50_stop_data = None
            
            if len(hist) >= 50:
                ma21 = hist['Close'].rolling(21).mean().iloc[-1]
                ma50 = hist['Close'].rolling(50).mean().iloc[-1]
                
                # MA21 stop
                if ma21 > 0 and current_price > ma21:
                    ma21_stop = ma21 * 0.985
                    ma21_risk = ((current_price - ma21_stop) / current_price) * 100
                    
                    if 5 < ma21_risk <= 10.0:
                        ma21_stop_data = {
                            'price': ma21_stop,
                            'risk': ma21_risk
                        }
                        all_stops['ma21'] = ma21_stop_data
                
                # 🌟 MA50 stop - ¡LA ESTRELLA PARA BONUS!
                if ma50 > 0 and current_price > ma50:
                    ma50_stop = ma50 * 0.985
                    ma50_risk = ((current_price - ma50_stop) / current_price) * 100
                    
                    if 5 < ma50_risk <= 10.0:
                        ma50_stop_data = {
                            'price': ma50_stop,
                            'risk': ma50_risk
                        }
                        all_stops['ma50'] = ma50_stop_data
            
            # 🌟 LÓGICA DE PRIORIZACIÓN - MA50 FIRST PARA BONUS!
            final_stop = None
            selection_method = None
            ma50_bonus_eligible = False
            
            # PRIORIDAD 1: MA50 válido - ¡REBOTE ALCISTA!
            if ma50_stop_data:
                final_stop = ma50_stop_data['price']
                risk_percentage = ma50_stop_data['risk']
                selection_method = 'ma50_priority'
                methods_used = ['ma50']
                ma50_bonus_eligible = True  # 🌟 ELEGIBLE PARA BONUS
                
            # PRIORIDAD 2: MA21 válido (si no hay MA50 válido)
            elif ma21_stop_data:
                final_stop = ma21_stop_data['price']
                risk_percentage = ma21_stop_data['risk']
                selection_method = 'ma21_priority'
                methods_used = ['ma21']
                
            # PRIORIDAD 3: Si MA50/MA21 son "muy pequeños" (<5%), usar mínimo de otros
            elif (ma50_stop_data and ma50_stop_data['risk'] < 5.0) or (ma21_stop_data and ma21_stop_data['risk'] < 5.0):
                # Usar mínimo de ATR y support (más restrictivo)
                other_stops = {k: v for k, v in all_stops.items() if k not in ['ma21', 'ma50']}
                
                if other_stops:
                    min_stop_key = min(other_stops.keys(), key=lambda k: other_stops[k]['price'])
                    final_stop = other_stops[min_stop_key]['price']
                    risk_percentage = other_stops[min_stop_key]['risk']
                    selection_method = f'ma_too_small_using_{min_stop_key}'
                    methods_used = [min_stop_key]
                    
                    # Verificar que el "mínimo de otros" no sea demasiado tight
                    min_acceptable_stop = current_price * 0.97  # Mínimo 3%
                    if final_stop > min_acceptable_stop:
                        final_stop = min_acceptable_stop
                        risk_percentage = 3.0
                        selection_method += '_adjusted_to_min_3pct'
                else:
                    # Si no hay otros stops válidos, usar fallback 8%
                    final_stop = current_price * 0.92
                    risk_percentage = 8.0
                    selection_method = 'ma_too_small_fallback_8pct'
                    methods_used = ['fallback_8pct']
            
            # PRIORIDAD 4: Otros métodos si MA están disponibles pero fuera de rango 5-10%
            elif all_stops:
                other_stops = {k: v for k, v in all_stops.items() if k not in ['ma21', 'ma50']}
                
                if other_stops:
                    min_stop_key = min(other_stops.keys(), key=lambda k: other_stops[k]['price'])
                    final_stop = other_stops[min_stop_key]['price']
                    risk_percentage = other_stops[min_stop_key]['risk']
                    selection_method = f'other_method_{min_stop_key}'
                    methods_used = [min_stop_key]
                else:
                    # ❌ SIN STOP LOSS VÁLIDO - DESCARTAR ACCIÓN
                    return {
                        'stop_price': None,
                        'risk_percentage': 100.0,  # Forzar descarte
                        'methods_used': ['no_valid_stop'],
                        'stop_selection': 'no_valid_stop_discard',
                        'ma50_bonus_eligible': False,
                        'discard_reason': 'No se pudo calcular stop loss válido ≤10%'
                    }
            
            # ❌ NO HAY NINGÚN STOP LOSS VÁLIDO - DESCARTAR
            else:
                return {
                    'stop_price': None,
                    'risk_percentage': 100.0,  # Forzar descarte
                    'methods_used': ['no_stops_calculated'],
                    'stop_selection': 'no_stops_discard',
                    'ma50_bonus_eligible': False,
                    'discard_reason': 'No se pudieron calcular stops ≤10%'
                }
            
            return {
                'stop_price': final_stop,
                'risk_percentage': risk_percentage,
                'methods_used': methods_used,
                'all_stops_calculated': {k: f"{v['price']:.2f} ({v['risk']:.1f}%)" for k, v in all_stops.items()},
                'stop_selection': selection_method,
                'ma21_data': f"{ma21_stop_data['price']:.2f} ({ma21_stop_data['risk']:.1f}%)" if ma21_stop_data else 'N/A',
                'ma50_data': f"{ma50_stop_data['price']:.2f} ({ma50_stop_data['risk']:.1f}%)" if ma50_stop_data else 'N/A',
                'priority_logic_applied': True,
                'ma50_bonus_eligible': ma50_bonus_eligible  # 🌟 FLAG PARA BONUS
            }
            
        except Exception as e:
            return {
                'stop_price': current_price * 0.92,
                'risk_percentage': 8.0,
                'methods_used': ['error_fallback'],
                'error': str(e),
                'stop_selection': 'error_fallback',
                'ma50_bonus_eligible': False
            }
    
    def calculate_momentum_score_responsive(self, outperf_20d, outperf_60d, outperf_90d):
        """Calcula score de momentum responsivo"""
        # Scores individuales por momentum
        momentum_20d_score = outperf_20d * self.momentum_20d_weight * 1.5
        momentum_60d_score = outperf_60d * self.momentum_60d_weight * 1.0
        momentum_90d_score = outperf_90d * self.momentum_90d_weight * 0.0  # Eliminado
        
        # Score base
        base_momentum_score = momentum_20d_score + momentum_60d_score + momentum_90d_score
        
        # Bonus por acceleration
        acceleration_bonus = self.calculate_momentum_acceleration_bonus(outperf_20d, outperf_60d, outperf_90d)
        
        # Bonus por momentum excepcional en 20d
        exceptional_bonus = 0
        if outperf_20d > 15:
            exceptional_bonus = min((outperf_20d - 15) * 0.5, 20)
        
        total_momentum_score = base_momentum_score + acceleration_bonus + exceptional_bonus
        
        return {
            'total_score': total_momentum_score,
            'momentum_20d_score': momentum_20d_score,
            'momentum_60d_score': momentum_60d_score,
            'momentum_90d_score': momentum_90d_score,
            'acceleration_bonus': acceleration_bonus,
            'exceptional_bonus': exceptional_bonus,
            'weights_used': {
                '20d': self.momentum_20d_weight,
                '60d': self.momentum_60d_weight,
                '90d': self.momentum_90d_weight
            }
        }
    
    def calculate_momentum_acceleration_bonus(self, outperf_20d, outperf_60d, outperf_90d):
        """Calcula bonus por aceleración de momentum"""
        acceleration_bonus = 0
        
        if outperf_20d > outperf_60d + 5:
            acceleration_bonus += min((outperf_20d - outperf_60d) * 0.3, 15)
        
        if outperf_60d > 0 and outperf_20d > outperf_60d:
            acceleration_bonus += 5
        
        return acceleration_bonus
    
    def get_fundamental_data(self, ticker_info):
        """Extrae datos fundamentales con filtros estrictos"""
        fundamental_data = {
            'quarterly_earnings_positive': None,
            'quarterly_earnings_growth': None,
            'revenue_growth': None,
            'roe': None,
            'fundamental_score': 0,
            'has_required_data': False
        }
        
        try:
            # Filtro crítico: Beneficios último trimestre
            quarterly_growth = ticker_info.get('earningsQuarterlyGrowth')
            quarterly_positive = ticker_info.get('trailingEps')
            
            if quarterly_growth is not None and quarterly_positive is not None:
                fundamental_data['quarterly_earnings_positive'] = quarterly_positive > 0
                fundamental_data['quarterly_earnings_growth'] = quarterly_growth
                fundamental_data['has_required_data'] = True
                
                # Solo dar puntos si hay beneficios POSITIVOS
                if quarterly_positive > 0:
                    if quarterly_growth > 0.30:
                        fundamental_data['fundamental_score'] += 40
                    elif quarterly_growth > 0.15:
                        fundamental_data['fundamental_score'] += 25
                    elif quarterly_growth > 0:
                        fundamental_data['fundamental_score'] += 15
                    else:
                        fundamental_data['fundamental_score'] += 5
            
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
        🌟 MODIFICADO: Evaluación completa con BONUS MA50
        Solo cambio: añade bonus de 22 puntos cuando stop loss es MA50
        """
        try:
            normalized_symbol = self.normalize_symbol(symbol)
            if not normalized_symbol:
                return None
            
            ticker = yf.Ticker(normalized_symbol)
            hist = ticker.history(period="6mo")
            
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
            
            # Filtros de momentum agresivos
            if outperformance_20d < self.min_outperf_20d:
                return None
            if outperformance_60d < self.min_outperf_60d:
                return None
            
            # Tendencia alcista
            if len(hist) >= 200:
                ma21 = hist['Close'].rolling(21).mean().iloc[-1]
                ma50 = hist['Close'].rolling(50).mean().iloc[-1]
                ma200 = hist['Close'].rolling(200).mean().iloc[-1]
                
                above_ma21 = current_price > ma21
                trend_bullish = ma21 > ma50 > ma200
                
                if not (above_ma21 or (current_price > ma50 * 0.98)):
                    return None
            else:
                ma21 = ma50 = ma200 = 0
                above_ma21 = trend_bullish = True
            
            # Métricas técnicas
            atr = hist['Close'].rolling(14).apply(
                lambda x: pd.Series(x).pct_change().abs().mean() * x.iloc[-1]
            ).iloc[-1]
            
            weekly_atr = self.calculate_weekly_atr(hist, 14)
            support_resistance = self.calculate_support_resistance(hist)
            volatility_metrics = self.calculate_volatility_metrics(hist)
            
            # 🌟 STOP LOSS CON DETECCIÓN MA50 PARA BONUS
            stop_analysis = self.calculate_ultra_conservative_stop_loss(
                hist, current_price, atr, support_resistance, volatility_metrics
            )
            
            # Filtro sagrado: Si riesgo > 10%, descartar
            if stop_analysis['risk_percentage'] > self.max_allowed_risk:
                return None
            
            # Fundamentales con filtros estrictos
            try:
                ticker_info = ticker.info
                fundamental_data = self.get_fundamental_data(ticker_info)
                
                if fundamental_data.get('quarterly_earnings_positive') == False:
                    return None
                
                if not fundamental_data.get('has_required_data', False):
                    return None
                    
            except Exception as e:
                return None
            
            # Score de momentum responsivo
            momentum_analysis = self.calculate_momentum_score_responsive(
                outperformance_20d, outperformance_60d, outperformance_90d
            )
            
            # Factor de volatilidad
            volatility_bonus = 0
            vol_rank = volatility_metrics.get('volatility_rank', 'MEDIUM')
            if vol_rank == 'LOW':
                volatility_bonus = 15
            elif vol_rank == 'MEDIUM':
                volatility_bonus = 5
            
            # Factor de volumen
            volume_surge_val = ((hist['Volume'].tail(5).mean() / volume_avg_30d) - 1) * 100
            volume_score = min(max(volume_surge_val * 0.3, -10), 20)
            
            # Bonus por riesgo
            risk_bonus = (self.max_allowed_risk - stop_analysis['risk_percentage']) * 1.5
            
            # 🌟 BONUS ESPECIAL MA50 - ¡SOLO ESTO ES NUEVO!
            ma50_bonus = 0
            if stop_analysis.get('ma50_bonus_eligible', False):
                ma50_bonus = self.ma50_stop_bonus
                print(f"🌟 {symbol} - BONUS MA50 APLICADO: +{ma50_bonus} pts (rebote alcista)")
            
            # Score técnico CON BONUS MA50
            technical_score = (
                momentum_analysis['total_score'] +
                volatility_bonus +
                volume_score +
                risk_bonus +
                ma50_bonus  # 🌟 ÚNICO CAMBIO REAL
            )
            
            # Score de fundamentales
            fundamental_score = fundamental_data.get('fundamental_score', 0)
            
            # SCORE FINAL
            final_score = technical_score + fundamental_score
            
            # Take profit con Weekly ATR
            take_profit_analysis = self.calculate_take_profit_weekly_atr(
                current_price, weekly_atr, atr, final_score
            )
            
            # Company info
            company_info = {
                'longName': ticker_info.get('longName', symbol),
                'sector': ticker_info.get('sector', 'Unknown'),
                'industry': ticker_info.get('industry', 'Unknown')
            }
            
            # Score breakdown detallado
            score_breakdown = {
                'momentum_score': momentum_analysis['total_score'],
                'fundamental_score': fundamental_score,
                'volatility_bonus': volatility_bonus,
                'volume_score': volume_score,
                'risk_bonus': risk_bonus,
                'ma50_bonus': ma50_bonus,  # 🌟 NUEVO EN BREAKDOWN
                'total_technical': technical_score,
                'final_score': final_score
            }
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'score': final_score,
                'technical_score': technical_score,
                'risk_pct': stop_analysis['risk_percentage'],
                'stop_loss': stop_analysis['stop_price'],
                'take_profit': take_profit_analysis['take_profit'],
                'upside_pct': take_profit_analysis['upside_pct'],
                'risk_reward_ratio': take_profit_analysis['risk_reward_ratio'],
                'outperformance_20d': outperformance_20d,
                'outperformance_60d': outperformance_60d,
                'outperformance_90d': outperformance_90d,
                'volume_avg_30d': volume_avg_30d,
                'atr': atr,
                'weekly_atr': weekly_atr,
                'optimizations': {
                    'weekly_atr': weekly_atr,
                    'ma50_bonus_applied': ma50_bonus > 0,  # 🌟 FLAG
                    'ma50_bonus_value': ma50_bonus  # 🌟 VALOR
                },
                'support_resistance': support_resistance,
                'stop_analysis': stop_analysis,
                'take_profit_analysis': take_profit_analysis,
                'momentum_analysis': momentum_analysis,
                'score_breakdown': score_breakdown,
                'company_info': company_info,
                'ma_levels': {
                    'ma_21': round(ma21, 2),
                    'ma_50': round(ma50, 2),
                    'ma_200': round(ma200, 2),
                    'entry_type': 'above_ma21' if above_ma21 else 'rebote_ma50',
                    'trend_bullish': trend_bullish
                },
                'fundamental_data': fundamental_data,
                'momentum_responsive': True,
                'max_risk_applied': self.max_allowed_risk,
                'aggressive_targets': True,
                'weekly_atr_optimized': True,
                'target_hold': '~1 mes con monitorización diaria',  # 🔄 ACTUALIZADO
                'analysis_date': datetime.now().isoformat(),
                'momentum_filters_applied': {
                    'min_20d': self.min_outperf_20d,
                    'min_60d': self.min_outperf_60d,
                    '90d_eliminated': True
                },
                'filters_passed': True,
                'improvements_applied': 'weekly_atr_take_profit_ma50_bonus'  # 🌟 NUEVO
            }
            
            return self.apply_ultra_conservative_risk_filter(result)
            
        except Exception as e:
            return None
    
    def calculate_take_profit_weekly_atr(self, current_price, weekly_atr, daily_atr, score):
        """Calcula take profit basado en Weekly ATR"""
        try:
            # Usar Weekly ATR si disponible, sino Daily ATR
            atr_to_use = weekly_atr if weekly_atr > 0 else daily_atr
            atr_type = 'weekly' if weekly_atr > 0 else 'daily'
            
            # Multiplicadores basados en score
            if score >= 80:
                multiplier = 3.0 if atr_type == 'weekly' else 3.5
            elif score >= 60:
                multiplier = 2.5 if atr_type == 'weekly' else 3.0
            else:
                multiplier = 2.0 if atr_type == 'weekly' else 2.5
            
            take_profit = current_price + (atr_to_use * multiplier)
            upside_pct = ((take_profit - current_price) / current_price) * 100
            
            return {
                'take_profit': take_profit,
                'upside_pct': upside_pct,
                'atr_multiplier_used': multiplier,
                'atr_type_used': atr_type,
                'atr_value': atr_to_use,
                'risk_reward_ratio': upside_pct / 10.0
            }
            
        except Exception as e:
            return {
                'take_profit': current_price * 1.20,
                'upside_pct': 20.0,
                'risk_reward_ratio': 2.0,
                'error': str(e)
            }
    
    def apply_ultra_conservative_risk_filter(self, stock_result):
        """Aplica filtro final ultra conservador"""
        try:
            risk_pct = stock_result.get('risk_pct', 0)
            
            # SAGRADO: Máximo 10% de riesgo
            if risk_pct > self.max_allowed_risk:
                return None
            
            # Verificación adicional de consistencia
            score = stock_result.get('score', 0)
            if score < 20:
                return None
            
            return stock_result
            
        except Exception as e:
            return None
    
    def screen_all_stocks_momentum_responsive(self):
        """Screening con 3,000+ símbolos reales + MA50 bonus"""
        print(f"=== SCREENING CON BONUS MA50 (+{self.ma50_stop_bonus} pts) ===")
        print(f"🎯 Take Profit: Weekly ATR-based para holds de 1 mes")
        print(f"🛡️ Stop Loss: MA50 PRIORITY con bonus de rebote")
        print(f"📈 Momentum: 20d {self.momentum_20d_weight*100:.0f}% + 60d {self.momentum_60d_weight*100:.0f}%")
        print(f"🌟 BONUS MA50: +{self.ma50_stop_bonus} puntos para rebotes alcistas")
        
        # Calcular benchmark SPY
        self.spy_benchmark = self.calculate_spy_benchmark()
        if self.spy_benchmark is None:
            print("❌ No se pudo calcular benchmark SPY")
            return []
        
        # Obtener símbolos REALES (3,000+)
        all_symbols = self.get_nyse_nasdaq_symbols()
        if not all_symbols:
            print("❌ No se pudieron obtener símbolos")
            return []
        
        # Procesamiento en lotes
        batch_size = 25
        total_batches = (len(all_symbols) + batch_size - 1) // batch_size
        
        all_results = []
        ma50_bonus_count = 0
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(all_symbols))
            batch_symbols = all_symbols[start_idx:end_idx]
            
            print(f"\n=== LOTE {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx}) ===")
            
            for symbol in batch_symbols:
                try:
                    result = self.evaluate_stock_momentum_responsive(symbol)
                    if result:
                        all_results.append(result)
                        
                        # Contar aplicaciones de bonus MA50
                        if result.get('optimizations', {}).get('ma50_bonus_applied', False):
                            ma50_bonus_count += 1
                        
                except Exception as e:
                    continue
            
            # Progress report cada 5 lotes
            if (batch_num + 1) % 5 == 0:
                processed = (batch_num + 1) * batch_size
                print(f"📊 Progreso: {processed}/{len(all_symbols)} - Válidos: {len(all_results)} - MA50 Bonus: {ma50_bonus_count}")
        
        # Ordenar por score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n✅ SCREENING COMPLETADO:")
        print(f"   📊 Procesados: {len(all_symbols)}")
        print(f"   ✅ Aprobados: {len(all_results)}")
        print(f"   🌟 Con bonus MA50: {ma50_bonus_count}")
        print(f"   📈 Tasa éxito: {len(all_results)/len(all_symbols)*100:.1f}%")
        
        return all_results

def cleanup_old_files():
    """Limpia archivos antiguos manteniendo los últimos 10"""
    patterns = [
        'momentum_responsive_results_*.json',
        'weekly_screening_results_*.json'
    ]
    
    for pattern in patterns:
        try:
            import glob
            files = glob.glob(pattern)
            if len(files) > 10:
                files.sort()
                for old_file in files[:-10]:
                    os.remove(old_file)
                    print(f"🗑️ Eliminado archivo antiguo: {old_file}")
        except Exception as e:
            print(f"⚠️ Error limpiando archivos {pattern}: {e}")

def archive_previous_results():
    """Archiva archivo anterior de screening"""
    try:
        if not os.path.exists("weekly_screening_results.json"):
            return
        
        with open("weekly_screening_results.json", 'r') as f:
            prev_data = json.load(f)
            prev_date = prev_data.get('analysis_date', '')
        
        if prev_date:
            date_part = prev_date[:10].replace('-', '')
        else:
            date_part = "unknown"
        
        archive_filename = f"weekly_screening_results_{date_part}.json"
        os.rename("weekly_screening_results.json", archive_filename)
        print(f"📁 Archivo anterior archivado: {archive_filename}")
        
    except Exception as e:
        print(f"⚠️ Error archivando archivo anterior: {e}")
        try:
            backup_name = f"weekly_screening_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename("weekly_screening_results.json", backup_name)
            print(f"📁 Backup creado: {backup_name}")
        except Exception as e2:
            print(f"❌ Error creando backup: {e2}")

def main():
    """Función principal con MA50 bonus system"""
    screener = MomentumResponsiveScreener()
    
    # Archivar archivo anterior
    archive_previous_results()
    
    # Ejecutar screening con MA50 bonus
    results = screener.screen_all_stocks_momentum_responsive()
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Archivo completo con timestamp
    full_results_file = f"momentum_responsive_results_{timestamp}.json"
    with open(full_results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'momentum_responsive_with_ma50_bonus_daily_execution',
            'improvements_applied': {
                'ma50_bonus_system': True,  # 🌟 NUEVO
                'ma50_bonus_value': screener.ma50_stop_bonus,
                'daily_execution_ready': True
            },
            'max_allowed_risk': screener.max_allowed_risk,
            'ma50_bonus_stats': {
                'bonus_value': screener.ma50_stop_bonus,
                'eligible_count': len([r for r in results if r.get('optimizations', {}).get('ma50_bonus_applied', False)]),
                'total_results': len(results)
            },
            'total_screened': len(screener.get_nyse_nasdaq_symbols()) if screener.get_nyse_nasdaq_symbols() else 0,
            'total_passed': len(results),
            'spy_benchmark': screener.spy_benchmark,
            'results': results,
            'methodology': {
                'philosophy': 'Daily monitoring, monthly trading con MA50 bonus',
                'ma50_bonus_system': f'+{screener.ma50_stop_bonus} puntos por rebote en MA50',
                'execution_frequency': 'Diaria con criterios de rotación estrictos'
            }
        }, f, indent=2, default=str)
    
    # Archivo compatible con sistema existente
    top_15 = results[:15]
    screening_data = {
        'analysis_date': datetime.now().isoformat(),
        'analysis_type': 'momentum_responsive_with_ma50_bonus_daily',
        'philosophy': 'daily_monitoring_monthly_trading_with_ma50_bonus',
        'momentum_optimization': {
            'ma50_bonus_system': True,  # 🌟 NUEVO FLAG
            'ma50_bonus_value': screener.ma50_stop_bonus
        },
        'ma50_bonus_stats': {
            'bonus_value': screener.ma50_stop_bonus,
            'eligible_count': len([r for r in top_15 if r.get('optimizations', {}).get('ma50_bonus_applied', False)]),
            'total_results': len(top_15)
        },
        'top_symbols': [r['symbol'] for r in top_15],
        'detailed_results': top_15,
        'benchmark_context': {
            'spy_20d': screener.spy_benchmark['return_20d'] if screener.spy_benchmark else 0,
            'spy_60d': screener.spy_benchmark['return_60d'] if screener.spy_benchmark else 0,
            'spy_90d': screener.spy_benchmark['return_90d'] if screener.spy_benchmark else 0
        },
        'momentum_responsive_stats': {
            'avg_risk': sum(r.get('risk_pct', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_risk_reward': sum(r.get('risk_reward_ratio', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_upside': sum(r.get('upside_pct', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_momentum_20d': sum(r.get('outperformance_20d', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'ma50_bonus_count': len([r for r in top_15 if r.get('optimizations', {}).get('ma50_bonus_applied', False)]) if top_15 else 0  # 🌟
        }
    }
    
    with open("weekly_screening_results.json", 'w') as f:
        json.dump(screening_data, f, indent=2, default=str)
    
    # Limpieza automática
    cleanup_old_files()
    
    print(f"\n✅ Archivos guardados con MA50 BONUS SYSTEM:")
    print(f"   - {full_results_file} (resultados con bonus MA50)")
    print(f"   - weekly_screening_results.json (actual)")
    
    if len(top_15) > 0:
        print(f"\n🏆 TOP 5 CON MA50 BONUS SYSTEM:")
        for i, stock in enumerate(top_15[:5]):
            ma50_bonus = stock.get('optimizations', {}).get('ma50_bonus_applied', False)
            ma50_bonus_val = stock.get('optimizations', {}).get('ma50_bonus_value', 0)
            ma50_indicator = f" 🌟+{ma50_bonus_val}" if ma50_bonus else ""
            
            print(f"   {i+1}. {stock['symbol']}{ma50_indicator} | Score: {stock.get('score', 0):.1f} | Risk: {stock.get('risk_pct', 0):.1f}%")

if __name__ == "__main__":
    main()
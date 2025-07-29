#!/usr/bin/env python3
"""
Ultra Conservative Stock Screener - Con score final mejorado que incluye Risk/Reward
Score final = technical_score + (risk_reward_ratio * peso) para mejor ranking
🆕 INCLUYE GESTIÓN AUTOMÁTICA DE HISTORIAL
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

class UltraConservativeScreener:
    def __init__(self):
        self.stock_symbols = []
        self.spy_benchmark = None
        self.max_allowed_risk = 10.0  # 🆕 FILTRO: Máximo 10% de riesgo
        self.rr_weight = 12.0  # 🆕 PESO R/R rebalanceado (era 20.0)
        
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
        """Lista de respaldo con principales acciones de baja volatilidad"""
        return [
            # Ultra stable large caps
            'AAPL', 'MSFT', 'GOOGL', 'JNJ', 'PG', 'KO', 'PEP',
            # Dividend aristocrats y utilities 
            'VZ', 'T', 'XOM', 'CVX', 'WMT', 'HD', 'MCD',
            # Financial giants (estables)
            'JPM', 'BAC', 'V', 'MA', 'BRK-B',
            # Healthcare estables
            'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT',
            # Tech estables
            'IBM', 'INTC', 'ORCL', 'CSCO', 'CRM'
        ]
    
    def calculate_spy_benchmark(self):
        """Calcula rendimientos de SPY para benchmarking"""
        print("📊 Descargando benchmark SPY...")
        
        try:
            spy_ticker = yf.Ticker("SPY")
            spy_data = spy_ticker.history(period="1y")
            
            if spy_data.empty or len(spy_data) < 200:
                print("⚠️ SPY: Datos insuficientes")
                return None
            
            current_price = spy_data['Close'].iloc[-1]
            price_20d = spy_data['Close'].iloc[-21] if len(spy_data) >= 21 else spy_data['Close'].iloc[0]
            price_60d = spy_data['Close'].iloc[-61] if len(spy_data) >= 61 else spy_data['Close'].iloc[0]
            price_90d = spy_data['Close'].iloc[-91] if len(spy_data) >= 91 else spy_data['Close'].iloc[0]
            
            benchmark = {
                'return_20d': ((current_price / price_20d) - 1) * 100,
                'return_60d': ((current_price / price_60d) - 1) * 100,
                'return_90d': ((current_price / price_90d) - 1) * 100,
                'data': spy_data
            }
            
            print(f"✅ SPY - 20d: {benchmark['return_20d']:+.2f}%, 60d: {benchmark['return_60d']:+.2f}%, 90d: {benchmark['return_90d']:+.2f}%")
            return benchmark
            
        except Exception as e:
            print(f"❌ Error calculando SPY benchmark: {e}")
            return None
    
    def calculate_atr(self, df, period=20):
        """Calcula Average True Range"""
        try:
            high = df['High']
            low = df['Low']
            close = df['Close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            true_range = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr.iloc[-1] if not atr.empty else 0
        except Exception:
            return 0
    
    def calculate_support_resistance(self, df, window=20):
        """Calcula niveles de soporte y resistencia dinámicos"""
        try:
            if len(df) < window * 2:
                return None
            
            recent_data = df.tail(window * 2)
            
            # Máximos y mínimos locales
            highs = recent_data['High'].rolling(window=window//2, center=True).max()
            lows = recent_data['Low'].rolling(window=window//2, center=True).min()
            
            # Resistencia: promedio de máximos recientes
            resistance_candidates = recent_data['High'][recent_data['High'] == highs].dropna()
            resistance = resistance_candidates.tail(3).mean() if len(resistance_candidates) > 0 else recent_data['High'].max()
            
            # Soporte: promedio de mínimos recientes
            support_candidates = recent_data['Low'][recent_data['Low'] == lows].dropna()
            support = support_candidates.tail(3).mean() if len(support_candidates) > 0 else recent_data['Low'].min()
            
            current_price = df['Close'].iloc[-1]
            
            return {
                'resistance': resistance,
                'support': support,
                'current': current_price,
                'distance_to_resistance': ((resistance / current_price) - 1) * 100,
                'distance_to_support': ((current_price / support) - 1) * 100
            }
            
        except Exception as e:
            return None
    
    def calculate_volatility_metrics(self, df, period=20):
        """Calcula métricas de volatilidad avanzadas"""
        try:
            if len(df) < period:
                return {'volatility_rank': 'MEDIUM'}
            
            # Volatilidad histórica
            returns = df['Close'].pct_change().dropna()
            historical_vol = returns.rolling(window=period).std().iloc[-1] * math.sqrt(252) * 100
            
            # ATR como % del precio
            atr = self.calculate_atr(df, period)
            current_price = df['Close'].iloc[-1]
            atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
            
            return {
                'historical_volatility': historical_vol,
                'atr_percentage': atr_pct,
                'atr_absolute': atr,
                'volatility_rank': 'LOW' if historical_vol < 20 else 'MEDIUM' if historical_vol < 35 else 'HIGH'
            }
            
        except Exception as e:
            return {'volatility_rank': 'MEDIUM'}
    
    def calculate_ultra_conservative_stop_loss(self, hist, current_price, atr, support_resistance, volatility_metrics):
        """
        🆕 STOP LOSS ULTRA CONSERVADOR - Diseñado para estar siempre ≤ 10%
        """
        try:
            stops = []
            
            # 1. ATR-based stop (más conservador)
            if atr > 0:
                vol_rank = volatility_metrics.get('volatility_rank', 'MEDIUM')
                
                # Multiplicadores MÁS CONSERVADORES
                if vol_rank == 'LOW':
                    atr_multiplier = 1.2  # Reducido de 1.5
                elif vol_rank == 'MEDIUM':
                    atr_multiplier = 1.5  # Reducido de 2.0
                else:  # HIGH volatility
                    atr_multiplier = 1.8  # Reducido de 2.5
                
                atr_stop = current_price - (atr * atr_multiplier)
                stops.append(('atr', atr_stop))
            
            # 2. Support-based stop (más conservador)
            if support_resistance and support_resistance['support'] < current_price:
                # Buffer más grande para evitar whipsaws
                support_stop = support_resistance['support'] * 0.985  # 3% buffer vs 2%
                stops.append(('support', support_stop))
            
            # 3. Moving averages stops (🆕 corregidos para manejar rebotes MA50)
            if len(hist) >= 50:
                ma21 = hist['Close'].rolling(21).mean().iloc[-1]
                ma50 = hist['Close'].rolling(50).mean().iloc[-1]
                
                # 🆕 CORREGIDO: Solo usar MA21 si precio ESTÁ POR ENCIMA y cerca
                if (ma21 > 0 and current_price > ma21 and 
                    ((current_price - ma21) / current_price) < 0.06):
                    stops.append(('ma21', ma21 * 0.985))  # 3% buffer
                
                # 🆕 MEJORADO: MA50 como stop para rebotes (más relevante ahora)
                if (ma50 > 0 and current_price > ma50 and 
                    ((current_price - ma50) / current_price) < 0.09):  # Hasta 9% por encima de MA50
                    stops.append(('ma50', ma50 * 0.985))
            
            # SELECCIÓN FINAL: El MÁS ALTO (menos riesgo) PERO con límite del 10%
            if stops:
                stop_values = [s[1] for s in stops if s[1] > 0]
                final_stop = min(stop_values) if stop_values else current_price * 0.80
                                
                # También asegurar que no sea demasiado tight (mínimo 3%)
                min_stop = current_price * 0.97
                final_stop = min(final_stop, min_stop)
                
                risk_percentage = ((current_price - final_stop) / current_price) * 100
                
                return {
                    'stop_price': final_stop,
                    'risk_percentage': risk_percentage,
                    'methods_used': [s[0] for s in stops],
                    'all_stops': {s[0]: s[1] for s in stops},
                    'enforcement_used': False,
                    'stop_selection': 'ultra_conservative'
                }
            
            # Fallback ultra conservador
            return {
                'stop_price': current_price * 0.80,
                'risk_percentage': 20.0,
                'methods_used': ['fallback_ultra_conservative'],
                'enforcement_used': True
            }
            
        except Exception as e:
            return {
                'stop_price': current_price * 0.80,
                'risk_percentage': 20.0,
                'methods_used': ['error_fallback'],
                'error': str(e)
            }
    
    def apply_ultra_conservative_risk_filter(self, stock_result):
        """
        🆕 FILTRO PRINCIPAL: Descarta acciones con riesgo > 10%
        """
        if not stock_result:
            return None
        
        risk_pct = stock_result.get('risk_pct', 100)
        
        if risk_pct > self.max_allowed_risk:
            # Logging para estadísticas
            symbol = stock_result.get('symbol', 'UNKNOWN')
            print(f"🚫 {symbol} DESCARTADO - Riesgo {risk_pct:.1f}% > {self.max_allowed_risk}%")
            return None  # ❌ DESCARTAR
        
        return stock_result  # ✅ MANTENER
    
    def calculate_relative_performance(self, stock_data, spy_data, days):
        """Calcula performance relativa vs SPY"""
        try:
            if len(stock_data) < days or len(spy_data) < days:
                return 0
            
            stock_current = stock_data['Close'].iloc[-1]
            stock_past = stock_data['Close'].iloc[-days]
            stock_return = ((stock_current / stock_past) - 1) * 100
            
            spy_current = spy_data['Close'].iloc[-1]
            spy_past = spy_data['Close'].iloc[-days]
            spy_return = ((spy_current / spy_past) - 1) * 100
            
            return stock_return - spy_return
            
        except Exception:
            return 0
    
    def get_fundamental_data(self, ticker_info):
        """Extrae datos fundamentales (mismo que antes)"""
        fundamental_data = {
            'quarterly_earnings_positive': None,
            'quarterly_earnings_growth': None,
            'revenue_growth': None,
            'roe': None,
            'fundamental_score': 0
        }
        
        try:
            # Beneficios último trimestre
            quarterly_growth = ticker_info.get('quarterlyEarningsGrowthYOY')
            quarterly_positive = ticker_info.get('trailingEps')
            if quarterly_growth is not None:
                fundamental_data['quarterly_earnings_positive'] = quarterly_positive > 0
                fundamental_data['quarterly_earnings_growth'] = quarterly_growth
                
                if quarterly_growth > 0.30:
                    fundamental_data['fundamental_score'] += 40
                elif quarterly_growth > 0.15:
                    fundamental_data['fundamental_score'] += 25
                elif quarterly_growth > 0:
                    fundamental_data['fundamental_score'] += 10
            
            # Crecimiento de ingresos
            revenue_growth = ticker_info.get('revenueGrowth')
            if revenue_growth is not None:
                fundamental_data['revenue_growth'] = revenue_growth
                if revenue_growth > 0.10:
                    fundamental_data['fundamental_score'] += 20
                elif revenue_growth > 0.05:
                    fundamental_data['fundamental_score'] += 10
            
            # ROE
            roe = ticker_info.get('returnOnEquity')
            if roe is not None:
                fundamental_data['roe'] = roe
                if roe > 0.20:
                    fundamental_data['fundamental_score'] += 25
                elif roe > 0.15:
                    fundamental_data['fundamental_score'] += 15
                elif roe > 0.10:
                    fundamental_data['fundamental_score'] += 10
                    
        except Exception as e:
            print(f"⚠️ Error fundamentales: {e}")
        
        return fundamental_data
    
    def calculate_advanced_take_profit(self, hist, current_price, atr, support_resistance, outperformance_60d, score):
        try:
            if score > 180:
                momentum_strength = "FUERTE"
                atr_multiplier = 3.0
                min_reasonable = current_price * 1.10
                max_reasonable = current_price * 1.60
                projection_factor = 0.5
            elif score >= 120:
                momentum_strength = "MODERADO"
                atr_multiplier = 2.5
                min_reasonable = current_price * 1.07
                max_reasonable = current_price * 1.40
                projection_factor = 0.4
            else:
                momentum_strength = "DÉBIL"
                atr_multiplier = 2.0
                min_reasonable = current_price * 1.05
                max_reasonable = current_price * 1.30
                projection_factor = 0.3

            targets = []

            target_atr = current_price + atr * atr_multiplier
            targets.append(('atr_adaptive', target_atr))

            if support_resistance and support_resistance['resistance'] > current_price:
                target_resistance = current_price + (support_resistance['resistance'] - current_price) * 0.95
                targets.append(('resistance', target_resistance))

            if outperformance_60d > 0:
                target_outperf = current_price * (1 + (outperformance_60d / 100) * projection_factor)
                targets.append(('outperformance', target_outperf))

            candidate_targets = [t[1] for t in targets if t[1] > current_price]
            if not candidate_targets:
                fallback_target = current_price + atr * 2.0
                return {
                    'target_price': fallback_target,
                    'upside_percentage': ((fallback_target / current_price) - 1) * 100,
                    'momentum_strength': momentum_strength,
                    'atr_multiplier_used': 2.0,
                    'confidence_level': 'Fallback',
                    'primary_method': 'fallback_atr',
                    'methods_used': ['fallback'],
                    'calculation_method': 'fallback_simple'
                }

            raw_final_target = max(candidate_targets)
            final_target = max(min_reasonable, min(raw_final_target, max_reasonable))
            upside_percentage = ((final_target / current_price) - 1) * 100

            return {
                'target_price': final_target,
                'upside_percentage': upside_percentage,
                'momentum_strength': momentum_strength,
                'atr_multiplier_used': atr_multiplier,
                'confidence_level': 'Alta' if score > 180 else 'Media' if score >= 120 else 'Baja',
                'primary_method': 'best_of_three',
                'methods_used': [t[0] for t in targets],
                'all_targets': {t[0]: t[1] for t in targets},
                'calculation_method': 'best_target_selection',
                'score_range': f"{score:.1f} ({momentum_strength})"
            }

        except Exception as e:
            fallback_target = current_price + atr * 2.0
            return {
                'target_price': fallback_target,
                'upside_percentage': ((fallback_target / current_price) - 1) * 100,
                'momentum_strength': 'UNKNOWN',
                'atr_multiplier_used': 2.0,
                'confidence_level': 'Fallback',
                'primary_method': 'error_fallback',
                'methods_used': ['error'],
                'error': str(e),
                'calculation_method': 'error_fallback'
            }
    
    def calculate_final_score(self, technical_score, risk_reward_ratio):
        """
        🆕 CALCULA SCORE FINAL mejorado y rebalanceado
        """
        # Score base técnico + bonus por R/R ratio (peso reducido)
        rr_bonus = min(risk_reward_ratio * self.rr_weight, 60)  # 🆕 Max 60 pts (era 100)
        
        final_score = technical_score + rr_bonus
        
        return {
            'final_score': final_score,
            'technical_score': technical_score,
            'rr_bonus': rr_bonus,
            'rr_weight_used': self.rr_weight,
            'scoring_method': 'enhanced_balanced'  # 🆕 Identificador del método
        }
    
    def evaluate_stock_ultra_conservative(self, symbol):
        """
        🆕 EVALUACIÓN ULTRA CONSERVADORA con score final mejorado
        """
        def normalize_symbol(symbol):
            # Convierte símbolos con ^ (como OAK^B) a formato Yahoo: OAK-PB
            if '^' in symbol:
                parts = symbol.split('^')
                if len(parts) == 2 and len(parts[1]) == 1:
                    return f"{parts[0]}-P{parts[1]}"
            elif '.' in symbol:
                return symbol.replace(".","-")
            else:
                return symbol
        try:
            symbol = normalize_symbol(symbol)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if len(hist) < 200:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # 🆕 FILTROS TÉCNICOS MEJORADOS - Más flexibles para captar rebotes en soportes
            ma21 = hist['Close'].rolling(21).mean().iloc[-1]
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            ma200 = hist['Close'].rolling(200).mean().iloc[-1]
            
            # Condición principal: Tendencia alcista general (MAs en orden correcto)
            trend_bullish = ma21 > ma50 > ma200
            
            # 🆕 Condiciones de entrada mejoradas (más flexibles):
            # Opción 1: Precio por encima de MA21 (momentum fuerte)
            above_ma21 = current_price > ma21
            
            # Opción 2: Rebote en MA50 con tendencia alcista (excelente entrada)
            # - Precio por encima de MA50 (soporte confirmado)
            # - Precio no muy alejado por encima de MA21 (dentro de rango razonable)
            rebote_ma50 = (current_price > ma50 and 
                          current_price >= ma50 * 1.02 and  # Al menos 2% por encima de MA50
                          current_price <= ma21 * 1.07)     # 🆕 CORREGIDO: Máximo 7% por encima de MA21
            
            # 🆕 FILTRO MEJORADO: Acepta ambos casos
            if not (trend_bullish and (above_ma21 or rebote_ma50)):
                return None
            
            volume_avg_30d = hist['Volume'].tail(30).mean()
            if volume_avg_30d < 1_000_000:
                return None
            
            # BENCHMARKING vs SPY
            if self.spy_benchmark is None:
                return None
            
            spy_data = self.spy_benchmark['data']
            outperformance_20d = self.calculate_relative_performance(hist, spy_data, 20)
            outperformance_60d = self.calculate_relative_performance(hist, spy_data, 60)
            outperformance_90d = self.calculate_relative_performance(hist, spy_data, 90)
            
            if not (outperformance_20d > 2 and outperformance_60d > 5 and outperformance_90d > 8):
                return None
            
            # ANÁLISIS TÉCNICO
            atr = self.calculate_atr(hist, 20)
            support_resistance = self.calculate_support_resistance(hist)
            volatility_metrics = self.calculate_volatility_metrics(hist)
            
            # STOP LOSS ULTRA CONSERVADOR
            stop_analysis = self.calculate_ultra_conservative_stop_loss(
                hist, current_price, atr, support_resistance, volatility_metrics
            )
            
            # FILTRO CRÍTICO: Si riesgo > 10%, descartar inmediatamente
            if stop_analysis['risk_percentage'] > self.max_allowed_risk:
                return None  # ❌ DESCARTADO por riesgo excesivo
            
            # FUNDAMENTALES
            try:
                ticker_info = ticker.info
                fundamental_data = self.get_fundamental_data(ticker_info)
                
                if fundamental_data.get('quarterly_earnings_positive') is False:
                    return None
                    
            except Exception:
                fundamental_data = {'fundamental_score': 0}
            
            # 🆕 SCORE TÉCNICO MEJORADO - Con peso decreciente por outperformance excesiva
            
            # Función de peso decreciente AJUSTADA POR TIMEFRAME para evitar premiar momentum agotado
            def calculate_sustainable_momentum_score(outperf, base_weight, timeframe="60d"):
                """Calcula score de momentum con peso decreciente ajustado por período temporal"""
                if outperf <= 0:
                    return 0
                
                # 🆕 RANGOS AJUSTADOS POR TIMEFRAME
                if timeframe == "20d":
                    # Períodos cortos: momentum más volátil, rangos más conservadores
                    if outperf <= 15:      # Momentum saludable corto plazo
                        return outperf * base_weight
                    elif outperf <= 30:    # Fuerte pero sostenible
                        return 15 * base_weight + (outperf - 15) * (base_weight * 0.8)
                    elif outperf <= 50:    # Muy fuerte - precaución
                        return 15 * base_weight + 15 * (base_weight * 0.8) + (outperf - 30) * (base_weight * 0.5)
                    else:                  # Extremo - posible agotamiento
                        cap_50 = 15 * base_weight + 15 * (base_weight * 0.8) + 20 * (base_weight * 0.5)
                        excess = outperf - 50
                        return cap_50 + min(excess * (base_weight * 0.2), base_weight * 8)
                        
                elif timeframe == "60d":
                    # Período medio: rangos equilibrados (como antes pero ajustados)
                    if outperf <= 25:      # Momentum saludable medio plazo
                        return outperf * base_weight
                    elif outperf <= 45:    # Fuerte pero sostenible
                        return 25 * base_weight + (outperf - 25) * (base_weight * 0.8)
                    elif outperf <= 70:    # Muy fuerte - precaución
                        return 25 * base_weight + 20 * (base_weight * 0.8) + (outperf - 45) * (base_weight * 0.5)
                    else:                  # Extremo - posible agotamiento
                        cap_70 = 25 * base_weight + 20 * (base_weight * 0.8) + 25 * (base_weight * 0.5)
                        excess = outperf - 70
                        return cap_70 + min(excess * (base_weight * 0.2), base_weight * 10)
                        
                elif timeframe == "90d":
                    # Período largo: momentum más sostenible, rangos más amplios
                    if outperf <= 35:      # Momentum saludable largo plazo
                        return outperf * base_weight
                    elif outperf <= 60:    # Fuerte pero sostenible
                        return 35 * base_weight + (outperf - 35) * (base_weight * 0.8)
                    elif outperf <= 90:    # Muy fuerte - precaución
                        return 35 * base_weight + 25 * (base_weight * 0.8) + (outperf - 60) * (base_weight * 0.5)
                    else:                  # Extremo - posible agotamiento
                        cap_90 = 35 * base_weight + 25 * (base_weight * 0.8) + 30 * (base_weight * 0.5)
                        excess = outperf - 90
                        return cap_90 + min(excess * (base_weight * 0.2), base_weight * 12)
                
                # Fallback (no debería llegar aquí)
                return outperf * base_weight * 0.5
            
            # Aplicar peso decreciente a cada timeframe
            momentum_60d_score = calculate_sustainable_momentum_score(outperformance_60d, 1.5, "60d")
            momentum_20d_score = calculate_sustainable_momentum_score(outperformance_20d, 1.0, "20d") 
            momentum_90d_score = calculate_sustainable_momentum_score(outperformance_90d, 0.8, "90d")
            
            momentum_score = momentum_60d_score + momentum_20d_score + momentum_90d_score
            
            # 🆕 Factor de volatilidad (bonus por baja volatilidad)
            volatility_bonus = 0
            vol_rank = volatility_metrics.get('volatility_rank', 'MEDIUM')
            if vol_rank == 'LOW':
                volatility_bonus = 15      # Bonus por baja volatilidad
            elif vol_rank == 'MEDIUM':
                volatility_bonus = 5       # Bonus menor
            # HIGH volatility = 0 bonus
            
            # 🆕 Factor de volumen (momentum de volumen)
            volume_surge_val = ((hist['Volume'].tail(5).mean() / volume_avg_30d) - 1) * 100
            volume_score = min(max(volume_surge_val * 0.3, -10), 20)  # Entre -10 y +20 pts
            
            # 🆕 Bonus por riesgo REBALANCEADO (menos peso)
            risk_bonus = (self.max_allowed_risk - stop_analysis['risk_percentage']) * 1.5  # Peso reducido de 3 → 1.5
            
            # Score técnico rebalanceado
            technical_score = (
                momentum_score +                                    # 🆕 Momentum completo (20d+60d+90d)
                risk_bonus +                                        # 🆕 Bonus riesgo rebalanceado  
                fundamental_data.get('fundamental_score', 0) * 0.8 + # 🆕 Peso fundamental ligeramente aumentado
                volatility_bonus +                                  # 🆕 Bonus volatilidad
                volume_score                                        # 🆕 Factor volumen
            )

            # TAKE PROFIT (con score técnico corregido)
            take_profit_analysis = self.calculate_advanced_take_profit(
                hist, current_price, atr, support_resistance, outperformance_60d, technical_score
            )
            
            # 🆕 CALCULAR RISK/REWARD RATIO
            risk_reward_ratio = take_profit_analysis['upside_percentage'] / max(stop_analysis['risk_percentage'], 0.1)
            
            # 🆕 CALCULAR SCORE FINAL (incluye R/R)
            score_breakdown = self.calculate_final_score(technical_score, risk_reward_ratio)
            
            # INFORMACIÓN COMPLETA
            company_info = {
                'name': ticker_info.get('longName', 'N/A') if 'ticker_info' in locals() else 'N/A',
                'sector': ticker_info.get('sector', 'N/A') if 'ticker_info' in locals() else 'N/A',
                'market_cap': ticker_info.get('marketCap', 'N/A') if 'ticker_info' in locals() else 'N/A'
            }
            
            result = {
                'symbol': symbol,
                'score': round(score_breakdown['final_score'], 1),  # 🆕 Score final con R/R
                'technical_score': round(technical_score, 1),       # Score técnico base
                'rr_bonus': round(score_breakdown['rr_bonus'], 1),  # Bonus por R/R
                'current_price': round(current_price, 2),
                'stop_loss': round(stop_analysis['stop_price'], 2),
                'take_profit': round(take_profit_analysis['target_price'], 2),
                'risk_pct': round(stop_analysis['risk_percentage'], 2),
                'upside_pct': round(take_profit_analysis['upside_percentage'], 2),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'outperformance_20d': round(outperformance_20d, 2),
                'outperformance_60d': round(outperformance_60d, 2),
                'outperformance_90d': round(outperformance_90d, 2),
                'volume_surge': round(volume_surge_val, 1),
                'fundamental_score': fundamental_data.get('fundamental_score', 0),
                'atr': round(atr, 2),
                'volatility_rank': volatility_metrics.get('volatility_rank', 'MEDIUM'),
                'support_resistance': support_resistance,
                'stop_analysis': stop_analysis,
                'take_profit_analysis': take_profit_analysis,
                'score_breakdown': {
                    **score_breakdown,  # Info del score final
                    'momentum_60d_score': round(momentum_60d_score, 1),
                    'momentum_20d_score': round(momentum_20d_score, 1), 
                    'momentum_90d_score': round(momentum_90d_score, 1),
                    'total_momentum_score': round(momentum_score, 1),
                    'volatility_bonus': volatility_bonus,
                    'volume_score': volume_score,
                    'risk_bonus': risk_bonus,
                    'sustainable_momentum_applied': 'timeframe_adjusted_ranges'
                },  # 🆕 Desglose completo del scoring con momentum sostenible
                'company_info': company_info,
                'ma_levels': {
                    'ma_21': round(ma21, 2),
                    'ma_50': round(ma50, 2),
                    'ma_200': round(ma200, 2),
                    'entry_type': 'above_ma21' if above_ma21 else 'rebote_ma50',  # 🆕 Tipo de entrada detectada
                    'trend_bullish': trend_bullish
                },
                'ultra_conservative': True,
                'max_risk_applied': self.max_allowed_risk,
                'rr_weight_applied': self.rr_weight,  # 🆕 Info de peso usado
                'target_hold': '2-3 meses',
                'analysis_date': datetime.now().isoformat()
            }
            
            # APLICAR FILTRO FINAL
            return self.apply_ultra_conservative_risk_filter(result)
            
        except Exception as e:
            print(f"❌ Error procesando {symbol}: {e}")
            return None
    
    def screen_all_stocks_ultra_conservative(self):
        """Screening ultra conservador con score final mejorado"""
        print(f"=== ULTRA CONSERVATIVE SCREENING CON FILTROS MEJORADOS (MAX RISK: {self.max_allowed_risk}%) ===")
        print(f"🎯 Score final con MOMENTUM SOSTENIBLE AJUSTADO POR TIMEFRAME")
        print(f"📈 Filtros de entrada MEJORADOS: Permite rebotes en MA50 con tendencia alcista")
        
        # Calcular benchmark SPY
        self.spy_benchmark = self.calculate_spy_benchmark()
        if self.spy_benchmark is None:
            print("❌ No se pudo calcular benchmark SPY")
            return []
        
        # Obtener símbolos
        all_symbols = self.get_nyse_nasdaq_symbols()
        if not all_symbols:
            print("❌ No se pudieron obtener símbolos")
            return []
        
        # Procesamiento
        batch_size = 25
        total_batches = (len(all_symbols) + batch_size - 1) // batch_size
        
        all_results = []
        failed_count = 0
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(all_symbols))
            batch_symbols = all_symbols[start_idx:end_idx]
            
            print(f"\n=== LOTE {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx}) ===")
            
            for i, symbol in enumerate(batch_symbols):
                try:
                    result = self.evaluate_stock_ultra_conservative(symbol)
                    
                    if result:
                        all_results.append(result)
                        final_score = result.get('score', 0)
                        technical_score = result.get('technical_score', 0)
                        rr_ratio = result.get('risk_reward_ratio', 0)
                        risk = result.get('risk_pct', 0)
                        print(f"✅ {symbol} - Score: {final_score:.1f} (técnico: {technical_score:.1f}) - R/R: {rr_ratio:.1f} - Risk: {risk:.1f}%")
                    else:
                        pass
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ {symbol} - Error: {e}")
                
                time.sleep(0.1)
            
            if batch_num < total_batches - 1:
                print("⏸️ Pausa entre lotes...")
                time.sleep(2)
        
        # 🆕 ORDENAR POR SCORE FINAL (que incluye R/R)
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n=== RESUMEN ULTRA CONSERVADOR CON SCORE MEJORADO ===")
        print(f"Procesadas: {len(all_symbols)} | Pasaron TODOS los filtros: {len(all_results)}")
        print(f"Filtro de riesgo máximo: {self.max_allowed_risk}%")
        print(f"Peso R/R en score final: {self.rr_weight}")
        print(f"Errores: {failed_count}")
        
        if all_results:
            avg_risk = sum(r['risk_pct'] for r in all_results) / len(all_results)
            avg_rr = sum(r['risk_reward_ratio'] for r in all_results) / len(all_results)
            avg_final_score = sum(r['score'] for r in all_results) / len(all_results)
            avg_technical_score = sum(r['technical_score'] for r in all_results) / len(all_results)
            
            print(f"📊 Riesgo promedio: {avg_risk:.1f}% (máx {self.max_allowed_risk}%)")
            print(f"📊 R/R promedio: {avg_rr:.1f}:1")
            print(f"📊 Score final promedio: {avg_final_score:.1f}")
            print(f"📊 Score técnico promedio: {avg_technical_score:.1f}")
            
        return all_results

def cleanup_old_files():
    """🆕 Limpia archivos antiguos manteniendo solo las últimas 6 semanas"""
    print("🧹 Iniciando limpieza automática de archivos...")
    
    def cleanup_file_type(pattern, keep_count, file_type_name):
        """Limpia un tipo específico de archivos"""
        files = glob.glob(pattern)
        if not files:
            print(f"   📂 {file_type_name}: No hay archivos para limpiar")
            return
        
        # Ordenar por fecha de creación (más reciente primero)
        files.sort(key=os.path.getctime, reverse=True)
        
        files_to_delete = files[keep_count:]
        if files_to_delete:
            for old_file in files_to_delete:
                try:
                    os.remove(old_file)
                    print(f"   🗑️ Eliminado: {old_file}")
                except Exception as e:
                    print(f"   ⚠️ Error eliminando {old_file}: {e}")
        
        remaining_count = len(files) - len(files_to_delete)
        print(f"   ✅ {file_type_name}: {remaining_count}/{len(files)} archivos mantenidos")
    
    # Limpiar diferentes tipos de archivos
    cleanup_file_type("weekly_screening_results_*.json", 6, "Screening históricos")
    cleanup_file_type("ultra_conservative_results_*.json", 6, "Resultados ultra conservadores")
    cleanup_file_type("ENHANCED_WEEKLY_REPORT_*.md", 4, "Reportes semanales")
    cleanup_file_type("consistency_analysis_*.json", 4, "Análisis de consistencia") 
    cleanup_file_type("rotation_recommendations_*.json", 4, "Recomendaciones de rotación")
    
    print("✅ Limpieza automática completada")

def archive_previous_results():
    """🆕 Archiva el archivo anterior para mantener historial"""
    if not os.path.exists("weekly_screening_results.json"):
        print("📁 No hay archivo anterior para archivar")
        return
    
    try:
        # Leer fecha del archivo anterior
        with open("weekly_screening_results.json", 'r') as f:
            prev_data = json.load(f)
            prev_date = prev_data.get('analysis_date', '')
            
        # Extraer solo la fecha (YYYYMMDD)
        if prev_date:
            date_part = prev_date[:10].replace('-', '')  # 2025-07-28 → 20250728
        else:
            date_part = "unknown"
        
        # Crear nombre del archivo histórico
        archive_filename = f"weekly_screening_results_{date_part}.json"
        
        # Renombrar archivo (mover a historial)
        os.rename("weekly_screening_results.json", archive_filename)
        print(f"📁 Archivo anterior archivado: {archive_filename}")
        
    except Exception as e:
        print(f"⚠️ Error archivando archivo anterior: {e}")
        # Si hay error, intentar backup con timestamp
        try:
            backup_name = f"weekly_screening_results_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename("weekly_screening_results.json", backup_name)
            print(f"📁 Backup creado: {backup_name}")
        except Exception as e2:
            print(f"❌ Error creando backup: {e2}")

def main():
    """Función principal ultra conservadora con gestión de historial mejorada"""
    screener = UltraConservativeScreener()
    
    # 🆕 PASO 1: Archivar archivo anterior (si existe)
    archive_previous_results()
    
    # PASO 2: Ejecutar screening ultra conservador
    results = screener.screen_all_stocks_ultra_conservative()
    
    # PASO 3: Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Archivo completo con timestamp
    full_results_file = f"ultra_conservative_results_{timestamp}.json"
    with open(full_results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'ultra_conservative_sustainable_momentum_scoring',
            'max_allowed_risk': screener.max_allowed_risk,
            'rr_weight_in_final_score': screener.rr_weight,
            'total_screened': len(screener.get_nyse_nasdaq_symbols()) if screener.get_nyse_nasdaq_symbols() else 0,
            'total_passed': len(results),
            'spy_benchmark': screener.spy_benchmark,
            'results': results,
            'methodology': {
                'entry_filters': 'Enhanced: MA21>MA50>MA200 + (price>MA21 OR rebote_ma50)',
                'max_risk_filter': f'{screener.max_allowed_risk}% maximum',
                'stop_loss': 'Ultra conservative: ATR + support + MA with 10% enforcement',
                'take_profit': 'Multi-method with mean calculation, realistic score ranges (60-200+ pts), and timeframe-adjusted sustainable momentum',
                'scoring': f'Sustainable momentum with timeframe-adjusted ranges (20d/60d/90d) + fundamentals + volatility + volume + risk_bonus + (R/R × {screener.rr_weight})'
            }
        }, f, indent=2, default=str)
    
    # Archivo compatible con sistema existente (NUEVO)
    top_15 = results[:15]
    screening_data = {
        'analysis_date': datetime.now().isoformat(),
        'analysis_type': 'ultra_conservative_sustainable_momentum_scoring',
        'max_risk_filter': screener.max_allowed_risk,
        'rr_weight_in_final_score': screener.rr_weight,
        'top_symbols': [r['symbol'] for r in top_15],
        'detailed_results': top_15,
        'benchmark_context': {
            'spy_20d': screener.spy_benchmark['return_20d'] if screener.spy_benchmark else 0,
            'spy_60d': screener.spy_benchmark['return_60d'] if screener.spy_benchmark else 0,
            'spy_90d': screener.spy_benchmark['return_90d'] if screener.spy_benchmark else 0
        },
        'ultra_conservative_stats': {
            'avg_risk': sum(r.get('risk_pct', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_risk_reward': sum(r.get('risk_reward_ratio', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_final_score': sum(r.get('score', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_technical_score': sum(r.get('technical_score', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'max_risk_found': max(r.get('risk_pct', 0) for r in top_15) if top_15 else 0,
            'min_risk_found': min(r.get('risk_pct', 0) for r in top_15) if top_15 else 0
        }
    }
    
    with open("weekly_screening_results.json", 'w') as f:
        json.dump(screening_data, f, indent=2, default=str)
    
    # 🆕 PASO 4: Limpieza automática
    cleanup_old_files()
    
    print(f"\n✅ Archivos guardados con gestión de historial:")
    print(f"   - {full_results_file} (resultados ultra conservadores)")
    print(f"   - weekly_screening_results.json (actual)")
    print(f"   - Archivos históricos mantenidos automáticamente")
    
    if len(top_15) > 0:
        print(f"\n🏆 TOP 5 ULTRA CONSERVADORAS (Score Final con R/R):")
        for i, stock in enumerate(top_15[:5]):
            final_score = stock.get('score', 0)
            technical_score = stock.get('technical_score', 0)
            rr_bonus = stock.get('rr_bonus', 0)
            risk = stock.get('risk_pct', 0)
            rr = stock.get('risk_reward_ratio', 0)
            target = stock.get('take_profit', 0)
            stop = stock.get('stop_loss', 0)
            
            print(f"   {i+1}. {stock['symbol']} - Score Final: {final_score:.1f} (Técnico: {technical_score:.1f} + R/R Bonus: {rr_bonus:.1f})")
            print(f"      💰 ${stock['current_price']:.2f} → Target: ${target:.2f} (Stop: ${stop:.2f})")
            print(f"      📊 Risk: {risk:.1f}% | R/R: {rr:.1f}:1")
            print()
            
        print(f"🎯 MOMENTUM SOSTENIBLE CON RANGOS AJUSTADOS POR TIMEFRAME:")
        print(f"   📅 20 días: 0-15% peso completo, 15-30% peso 80%, 30-50% peso 50%, >50% peso 20%")
        print(f"   📅 60 días: 0-25% peso completo, 25-45% peso 80%, 45-70% peso 50%, >70% peso 20%")  
        print(f"   📅 90 días: 0-35% peso completo, 35-60% peso 80%, 60-90% peso 50%, >90% peso 20%")
        print(f"   - Factor volatilidad: Bonus por baja volatilidad")
        print(f"   - Factor volumen: Momentum de volumen incluido")
        print(f"   - Riesgo rebalanceado: Peso reducido de 3.0 → 1.5")
        print(f"   - R/R rebalanceado: Peso reducido de 20 → {screener.rr_weight}")
    else:
        print(f"\n⚠️ Ninguna acción pasa el filtro ultra conservador de {screener.max_allowed_risk}% esta semana")
        print("💡 Considera aumentar el límite a 12% o revisar condiciones de mercado")

if __name__ == "__main__":
    main()
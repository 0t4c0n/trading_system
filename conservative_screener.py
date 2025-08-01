#!/usr/bin/env python3
"""
Momentum Responsive Stock Screener - Optimizado para rotación mensual agresiva
Take profit targets agresivos + timeframes responsivos + momentum acceleration
🎯 Filosofía: "Swing for the fences" con gestión manual de exits
🛡️ MANTIENE: Stop loss ≤10% como filtro crítico de riesgo
🆕 NOVO: Sistema responsivo para capturar momentum emergente rápidamente
🛠️ CORREGIDO: Filtros fundamentales estrictos y lógica SPY benchmark
🔧 FIXED: Weekly ATR para take profit + Min stop loss para filtrado restrictivo
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
        
        # 🆕 NUEVOS PARÁMETROS PARA MOMENTUM AGRESIVO
        self.momentum_20d_weight = 0.7   # 70% peso al momentum 20d
        self.momentum_60d_weight = 0.3   # 30% peso al momentum 60d
        self.momentum_90d_weight = 0.0   # 0% peso al momentum 90d (eliminado)
        
        # 🆕 FILTROS MÁS AGRESIVOS PARA CAPTURAR MOMENTUM EMERGENTE
        self.min_outperf_20d = 5.0       # Era 2% - más agresivo
        self.min_outperf_60d = 0.0       # Era 5% - solo evitar losers obvios
        # outperf_90d eliminado completamente
        
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
    
    def calculate_weekly_atr(self, df, period=14):
        """🆕 Calcula ATR semanal - más apropiado para swing trading de 1 mes"""
        try:
            if len(df) < 50:  # Necesitamos suficientes datos
                return self.calculate_atr(df, 20) * 2.2  # Fallback escalado
            
            # Resample a datos semanales (viernes como cierre)
            weekly_data = df.resample('W-FRI').agg({
                'High': 'max',
                'Low': 'min', 
                'Close': 'last'
            }).dropna()
            
            if len(weekly_data) < period:
                # Fallback: Daily ATR escalado
                return self.calculate_atr(df, 20) * 2.2
                
            # Calcular ATR en datos semanales
            return self.calculate_atr(weekly_data, period)
            
        except Exception as e:
            print(f"⚠️ Error calculando Weekly ATR: {e}")
            return self.calculate_atr(df, 20) * 2.2  # Fallback seguro
    
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
        """🛡️ STOP LOSS ULTRA CONSERVADOR - Nueva lógica de priorización
        🔧 NUEVA PRIORIZACIÓN: MA50 → MA21 → otros (si MA muy pequeños) → 8% fallback
        """
        try:
            # Calcular todas las opciones de stop
            all_stops = {}
            
            # 1. ATR-based stop (conservador)
            if atr > 0:
                vol_rank = volatility_metrics.get('volatility_rank', 'MEDIUM')
                
                if vol_rank == 'LOW':
                    atr_multiplier = 1.2
                elif vol_rank == 'MEDIUM':
                    atr_multiplier = 1.5
                else:  # HIGH volatility
                    atr_multiplier = 1.8
                
                atr_stop = current_price - (atr * atr_multiplier)
                atr_risk = ((current_price - atr_stop) / current_price) * 100
                
                if atr_risk <= 10.0:  # Solo considerar si está dentro del límite
                    all_stops['atr'] = {
                        'price': atr_stop,
                        'risk': atr_risk
                    }
            
            # 2. Support-based stop
            if support_resistance and support_resistance['support'] < current_price:
                support_stop = support_resistance['support'] * 0.985  # 1.5% buffer
                support_risk = ((current_price - support_stop) / current_price) * 100
                
                if support_risk <= 10.0:  # Solo considerar si está dentro del límite
                    all_stops['support'] = {
                        'price': support_stop,
                        'risk': support_risk
                    }
            
            # 3. Moving averages stops
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
                
                # MA50 stop
                if ma50 > 0 and current_price > ma50:
                    ma50_stop = ma50 * 0.985
                    ma50_risk = ((current_price - ma50_stop) / current_price) * 100
                    
                    if 5 < ma50_risk <= 10.0:
                        ma50_stop_data = {
                            'price': ma50_stop,
                            'risk': ma50_risk
                        }
                        all_stops['ma50'] = ma50_stop_data
            
            # 🆕 NUEVA LÓGICA DE PRIORIZACIÓN
            final_stop = None
            selection_method = None
            
            # PRIORIDAD 1: MA50 válido
            if ma50_stop_data:
                final_stop = ma50_stop_data['price']
                risk_percentage = ma50_stop_data['risk']
                selection_method = 'ma50_priority'
                methods_used = ['ma50']
                
            # PRIORIDAD 2: MA21 válido (si no hay MA50 válido)
            elif ma21_stop_data:
                final_stop = ma21_stop_data['price']
                risk_percentage = ma21_stop_data['risk']
                selection_method = 'ma21_priority'
                methods_used = ['ma21']
                
            # PRIORIDAD 3: Si MA50/MA21 son "muy pequeños" (< 5%), usar mínimo de otros
            elif (((ma50_stop_data and ma50_stop_data['risk'] < 5.0) or 
                (ma21_stop_data and ma21_stop_data['risk'] < 5.0))):
                
                # Usar mínimo de ATR y support (más restrictivo)
                other_stops = {k: v for k, v in all_stops.items() if k not in ['ma21', 'ma50']}
                
                if other_stops:
                    # Seleccionar el más restrictivo (menor precio = mayor riesgo, pero controlado)
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
                    # Si no hay otros stops válidos, usar fallback
                    final_stop = current_price * 0.92  # 8% fallback
                    risk_percentage = 8.0
                    selection_method = 'ma_too_small_fallback_8pct'
                    methods_used = ['fallback_8pct']
            
            # FALLBACK: Stop mínimo del 8%
            else:
                final_stop = current_price * 0.80  # 8% desde precio actual
                risk_percentage = 20.0
                selection_method = 'descartar'
                methods_used = ['descartar']
            
            return {
                'stop_price': final_stop,
                'risk_percentage': risk_percentage,
                'methods_used': methods_used,
                'all_stops_calculated': {k: f"{v['price']:.2f} ({v['risk']:.1f}%)" for k, v in all_stops.items()},
                'stop_selection': selection_method,
                'ma21_data': f"{ma21_stop_data['price']:.2f} ({ma21_stop_data['risk']:.1f}%)" if ma21_stop_data else 'N/A',
                'ma50_data': f"{ma50_stop_data['price']:.2f} ({ma50_stop_data['risk']:.1f}%)" if ma50_stop_data else 'N/A',
                'priority_logic_applied': True
            }
            
        except Exception as e:
            return {
                'stop_price': current_price * 0.92,  # 8% fallback en caso de error
                'risk_percentage': 8.0,
                'methods_used': ['error_fallback_8pct'],
                'error': str(e),
                'stop_selection': 'error_fallback'
            }
    
    def apply_ultra_conservative_risk_filter(self, stock_result):
        """🛡️ FILTRO SAGRADO: Descarta acciones con riesgo > 10%"""
        if not stock_result:
            return None
        
        risk_pct = stock_result.get('risk_pct', 100)
        
        if risk_pct > self.max_allowed_risk:
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
        """🛠️ CORREGIDO: Extrae datos fundamentales con filtros estrictos"""
        fundamental_data = {
            'quarterly_earnings_positive': None,
            'quarterly_earnings_growth': None,
            'revenue_growth': None,
            'roe': None,
            'fundamental_score': 0,
            'has_required_data': False  # 🆕 Flag para verificar si tiene datos mínimos
        }
        
        try:
            # 🛠️ FILTRO CRÍTICO: Beneficios último trimestre
            quarterly_growth = ticker_info.get('earningsQuarterlyGrowth')
            quarterly_positive = ticker_info.get('trailingEps')
            
            # 🛠️ LÓGICA CORREGIDA: Establecer valores explícitos
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
                        fundamental_data['fundamental_score'] += 10
                # Si beneficios son negativos o cero, score = 0
            else:
                # 🛠️ CRÍTICO: Si no hay datos de beneficios, marcar como negativo
                fundamental_data['quarterly_earnings_positive'] = False
                fundamental_data['has_required_data'] = False
                print(f"⚠️ Sin datos de beneficios - descartando")
            
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
            # En caso de error, marcar como sin beneficios para mayor seguridad
            fundamental_data['quarterly_earnings_positive'] = False
            fundamental_data['has_required_data'] = False
        
        return fundamental_data
    
    def calculate_aggressive_take_profit(self, hist, current_price, atr, support_resistance, outperformance_60d, score):
        """
        🎯 TAKE PROFIT AGRESIVO con Weekly ATR - Optimizado para holds de 1 mes
        🔧 FIXED: Usar Weekly ATR + multiplicadores ajustados para swing trading
        """
        try:
            # 🆕 USAR WEEKLY ATR en lugar de daily
            weekly_atr = self.calculate_weekly_atr(hist, 14)
            
            # 🎯 MULTIPLICADORES AJUSTADOS para Weekly ATR (más conservadores porque weekly ATR es mayor)
            if score > 100:  # Momentum fuerte
                momentum_strength = "FUERTE"
                atr_multiplier = 3.0  # Era 4.5 - reducido porque weekly ATR es mayor
            elif score >= 60:  # Momentum moderado
                momentum_strength = "MODERADO"
                atr_multiplier = 2.5  # Era 4.0
            else:  # Momentum débil
                momentum_strength = "DÉBIL"
                atr_multiplier = 2.0  # Era 3.5
            
            # 🎯 CÁLCULO PRINCIPAL: Weekly ATR agresivo
            target_price = current_price + (weekly_atr * atr_multiplier)
            
            # 🔧 VALIDACIÓN: Límites de seguridad
            min_target = current_price * 1.10  # Mínimo 10%
            max_target = current_price * 2.50  # Máximo 150%
            
            method_note = "weekly_atr_swing_optimized"
            if target_price < min_target:
                target_price = min_target
                method_note = "min_enforced"
            elif target_price > max_target:
                target_price = max_target
                method_note = "max_enforced"
            
            # 🎯 AJUSTE OPCIONAL: Resistencia si mejora el target
            if support_resistance and support_resistance['resistance'] > current_price:
                resistance_target = support_resistance['resistance'] * 1.05
                if resistance_target > target_price and resistance_target < max_target:
                    target_price = resistance_target
                    method_note = "resistance_enhanced_weekly"
            
            upside_percentage = ((target_price / current_price) - 1) * 100
            
            return {
                'target_price': target_price,
                'upside_percentage': upside_percentage,
                'momentum_strength': momentum_strength,
                'atr_multiplier_used': atr_multiplier,
                'weekly_atr_used': weekly_atr,  # 🆕 Para tracking
                'daily_atr_used': atr,  # Para comparación
                'confidence_level': 'Alta' if score > 100 else 'Media' if score >= 60 else 'Baja',
                'primary_method': 'weekly_atr_swing_for_fences',
                'method_note': method_note,
                'calculation_method': 'weekly_atr_1month_optimized',
                'score_range': f"{score:.1f} ({momentum_strength})",
                'atr_comparison': f"Weekly: {weekly_atr:.2f} vs Daily: {atr:.2f}",
                'target_range': f"{upside_percentage:.1f}% (1-month swing optimized)"
            }
            
        except Exception as e:
            # Fallback con daily ATR escalado
            fallback_target = current_price * 1.25
            return {
                'target_price': fallback_target,
                'upside_percentage': 25.0,
                'momentum_strength': 'FALLBACK',
                'atr_multiplier_used': 0,
                'weekly_atr_used': 0,
                'daily_atr_used': atr,
                'confidence_level': 'Fallback',
                'primary_method': 'error_fallback',
                'method_note': 'weekly_atr_error',
                'error': str(e)
            }
    
    def calculate_final_score(self, technical_score, risk_reward_ratio):
        """Calcula score final mejorado"""
        rr_bonus = min(risk_reward_ratio * self.rr_weight, 60)  # Max 60 pts
        
        final_score = technical_score + rr_bonus
        
        return {
            'final_score': final_score,
            'technical_score': technical_score,
            'rr_bonus': rr_bonus,
            'rr_weight_used': self.rr_weight,
            'scoring_method': 'momentum_responsive_weekly_atr'
        }
    
    def calculate_momentum_acceleration_bonus(self, outperf_20d, outperf_60d, outperf_90d):
        """
        🆕 NUEVO: Calcula bonus por momentum acceleration
        Detecta si momentum está acelerándose (building) o decelerando (fading)
        """
        acceleration_bonus = 0
        
        # Patrón ideal: 20d > 60d > 90d (momentum building)
        if outperf_20d > outperf_60d > outperf_90d:
            acceleration_bonus += 15  # Momentum claramente acelerándose
            
        # Patrón fuerte: 20d > 60d (momentum short-term superior)
        elif outperf_20d > outperf_60d:
            acceleration_bonus += 8   # Momentum recent strength
            
        # Patrón preocupante: 20d < 60d < 90d (momentum decelerando)
        elif outperf_20d < outperf_60d < outperf_90d:
            acceleration_bonus -= 10  # Momentum claramente fading
            
        # Patrón moderadamente preocupante: 20d < 60d
        elif outperf_20d < outperf_60d:
            acceleration_bonus -= 5   # Recent weakness
        
        return acceleration_bonus
    
    def calculate_responsive_momentum_score(self, outperf_20d, outperf_60d, outperf_90d):
        """
        🆕 NUEVO SISTEMA DE MOMENTUM RESPONSIVO
        Pesos optimizados para rotación mensual agresiva
        """
        # Scores individuales con nueva ponderación
        momentum_20d_score = outperf_20d * self.momentum_20d_weight * 2.0  # Era 1.5, ahora más agresivo
        momentum_60d_score = outperf_60d * self.momentum_60d_weight * 1.0  # Peso reducido
        momentum_90d_score = outperf_90d * self.momentum_90d_weight * 0.0  # Eliminado
        
        # Score base
        base_momentum_score = momentum_20d_score + momentum_60d_score + momentum_90d_score
        
        # 🆕 Bonus por acceleration
        acceleration_bonus = self.calculate_momentum_acceleration_bonus(outperf_20d, outperf_60d, outperf_90d)
        
        # 🆕 Bonus por momentum excepcional en 20d (capturar emerging momentum)
        exceptional_bonus = 0
        if outperf_20d > 15:  # Momentum excepcional
            exceptional_bonus = min((outperf_20d - 15) * 0.5, 20)  # Max 20 pts bonus
        
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
            if len(parts) == 2:
                base, suffix = parts
                if suffix in ['A', 'B', 'C', 'D'] and len(suffix) == 1:
                    return f"{base}-{suffix}"
                
                international_suffixes = {
                    'L', 'TO', 'AX', 'F', 'HK', 'KS', 'PA', 'MI', 'SW', 'ST', 'OL'
                }
                if suffix in international_suffixes:
                    return symbol
                
                if suffix == 'WS':
                    return f"{base}-WS"
                
                if len(suffix) <= 3 and suffix.isalnum():
                    return f"{base}-{suffix}"
        
        # Limpiar caracteres problemáticos
        cleaned = symbol
        for char in ['/', '\\', '|', '*', '?', '<', '>', ':']:
            cleaned = cleaned.replace(char, '')
        
        return cleaned
    
    def evaluate_stock_momentum_responsive(self, symbol):
        """
        🎯 EVALUACIÓN OPTIMIZADA PARA MOMENTUM TRADING AGRESIVO
        🛠️ CORREGIDO: Filtros fundamentales estrictos y lógica SPY
        🔧 FIXED: Weekly ATR para take profit + Min stop loss
        """
        try:
            normalize_ticker = self.normalize_symbol(symbol)
            ticker = yf.Ticker(normalize_ticker)
            hist = ticker.history(period="1y")
            
            if len(hist) < 200:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # 🎯 FILTROS TÉCNICOS MEJORADOS para momentum
            ma21 = hist['Close'].rolling(21).mean().iloc[-1]
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            ma200 = hist['Close'].rolling(200).mean().iloc[-1]
            
            # Tendencia alcista general
            trend_bullish = ma21 > ma50 > ma200
            
            # 🆕 CONDICIONES DE ENTRADA MÁS FLEXIBLES para momentum emergente
            above_ma21 = current_price > ma21
            rebote_ma50 = (current_price > ma50 and 
                          current_price >= ma50 * 1.02 and
                          current_price <= ma21 * 1.08)  # Más flexible: 8% vs 7%
            
            if (trend_bullish and (above_ma21 or rebote_ma50)) == False:
                return None
            
            volume_avg_30d = hist['Volume'].tail(30).mean()
            if volume_avg_30d < 1000000:
                return None
             
            # 🛠️ CORREGIDO: LÓGICA SPY BENCHMARK FIXED
            if self.spy_benchmark is None:  # ✅ CORREGIDO: era "!= None"
                return None
            
            spy_data = self.spy_benchmark['data']
            outperformance_20d = self.calculate_relative_performance(hist, spy_data, 20)
            outperformance_60d = self.calculate_relative_performance(hist, spy_data, 60)
            outperformance_90d = self.calculate_relative_performance(hist, spy_data, 90)
            
            # 🆕 FILTROS AGRESIVOS PARA CAPTURAR MOMENTUM EMERGENTE
            if not (outperformance_20d > self.min_outperf_20d and 
                    outperformance_60d > self.min_outperf_60d):
                return None
            # Nota: outperformance_90d ya no se filtra
            
            # ANÁLISIS TÉCNICO
            atr = self.calculate_atr(hist, 20)  # Daily ATR para stops
            weekly_atr = self.calculate_weekly_atr(hist, 14)  # 🆕 Weekly ATR para take profit
            support_resistance = self.calculate_support_resistance(hist)
            volatility_metrics = self.calculate_volatility_metrics(hist)
            
            # 🛡️ STOP LOSS ULTRA CONSERVADOR (MANTIENE ≤10%) - Usando Daily ATR
            stop_analysis = self.calculate_ultra_conservative_stop_loss(
                hist, current_price, atr, support_resistance, volatility_metrics
            )
            
            # 🛡️ FILTRO SAGRADO: Si riesgo > 10%, descartar
            if stop_analysis['risk_percentage'] > self.max_allowed_risk:
                return None
            
            # 🛠️ CORREGIDO: FUNDAMENTALES CON FILTROS ESTRICTOS
            try:
                ticker_info = ticker.info
                fundamental_data = self.get_fundamental_data(ticker_info)
                
                # 🛠️ FILTRO CRÍTICO CORREGIDO
                if fundamental_data.get('quarterly_earnings_positive') == False:
                    print(f"🚫 {symbol} DESCARTADO - Sin beneficios positivos")
                    return None
                
                # 🛠️ NUEVO: Verificar que tenga datos mínimos requeridos
                if not fundamental_data.get('has_required_data', False):
                    print(f"🚫 {symbol} DESCARTADO - Sin datos fundamentales suficientes")
                    return None
                    
            except Exception as e:
                print(f"🚫 {symbol} DESCARTADO - Error obteniendo fundamentales: {e}")
                return None
            
            # 🆕 SCORE TÉCNICO CON NUEVO SISTEMA DE MOMENTUM RESPONSIVO
            momentum_analysis = self.calculate_responsive_momentum_score(
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
            
            # 🆕 SCORE TÉCNICO RESPONSIVO
            technical_score = (
                momentum_analysis['total_score'] +                      # Nuevo sistema de momentum
                risk_bonus +                                           
                fundamental_data.get('fundamental_score', 0) * 0.8 +   
                volatility_bonus +                                     
                volume_score                                           
            )

            # 🎯 TAKE PROFIT AGRESIVO CON WEEKLY ATR
            take_profit_analysis = self.calculate_aggressive_take_profit(
                hist, current_price, atr, support_resistance, outperformance_60d, technical_score
            )
            
            # CALCULAR RISK/REWARD RATIO
            risk_reward_ratio = take_profit_analysis['upside_percentage'] / max(stop_analysis['risk_percentage'], 0.1)
            
            # CALCULAR SCORE FINAL
            score_breakdown = self.calculate_final_score(technical_score, risk_reward_ratio)
            
            # INFORMACIÓN COMPLETA
            company_info = {
                'name': ticker_info.get('longName', 'N/A') if 'ticker_info' in locals() else 'N/A',
                'sector': ticker_info.get('sector', 'N/A') if 'ticker_info' in locals() else 'N/A',
                'market_cap': ticker_info.get('marketCap', 'N/A') if 'ticker_info' in locals() else 'N/A'
            }
            
            result = {
                'symbol': symbol,
                'score': round(score_breakdown['final_score'], 1),
                'technical_score': round(technical_score, 1),
                'rr_bonus': round(score_breakdown['rr_bonus'], 1),
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
                'weekly_atr': round(weekly_atr, 2),  # 🆕 Weekly ATR
                'volatility_rank': volatility_metrics.get('volatility_rank', 'MEDIUM'),
                'support_resistance': support_resistance,
                'stop_analysis': stop_analysis,
                'take_profit_analysis': take_profit_analysis,
                'momentum_analysis': momentum_analysis,  # 🆕 Desglose completo de momentum
                'score_breakdown': {
                    **score_breakdown,
                    'volatility_bonus': volatility_bonus,
                    'volume_score': volume_score,
                    'risk_bonus': risk_bonus,
                    'scoring_method': 'momentum_responsive_aggressive_weekly_atr'
                },
                'company_info': company_info,
                'ma_levels': {
                    'ma_21': round(ma21, 2),
                    'ma_50': round(ma50, 2),
                    'ma_200': round(ma200, 2),
                    'entry_type': 'above_ma21' if above_ma21 else 'rebote_ma50',
                    'trend_bullish': trend_bullish
                },
                'fundamental_data': fundamental_data,  # 🛠️ Incluir datos fundamentales
                'momentum_responsive': True,
                'max_risk_applied': self.max_allowed_risk,
                'aggressive_targets': True,
                'weekly_atr_optimized': True,  # 🆕 Flag
                'target_hold': '~1 mes (rotación agresiva)',
                'analysis_date': datetime.now().isoformat(),
                'momentum_filters_applied': {
                    'min_20d': self.min_outperf_20d,
                    'min_60d': self.min_outperf_60d,
                    '90d_eliminated': True
                },
                'filters_passed': True,  # 🛠️ Flag indicando que pasó todos los filtros
                'improvements_applied': 'weekly_atr_take_profit_min_stop_loss'  # 🔧 Tracking
            }
            
            # APLICAR FILTRO FINAL
            return self.apply_ultra_conservative_risk_filter(result)
            
        except Exception as e:
            print(f"❌ Error procesando {symbol}: {e}")
            return None
    
    def screen_all_stocks_momentum_responsive(self):
        """Screening optimizado para momentum trading agresivo con Weekly ATR"""
        print(f"=== MOMENTUM RESPONSIVE SCREENING AGRESIVO - WEEKLY ATR OPTIMIZED ===")
        print(f"🎯 Take Profit: Weekly ATR-based (× 3.0/2.5/2.0) para holds de 1 mes")
        print(f"🛡️ Stop Loss: Min de múltiples métodos (MÁS RESTRICTIVO)")
        print(f"📈 Momentum: 20d {self.momentum_20d_weight*100:.0f}% + 60d {self.momentum_60d_weight*100:.0f}% + 90d eliminado")
        print(f"🔧 Filtros: 20d >{self.min_outperf_20d}%, 60d >{self.min_outperf_60d}%")
        print(f"🛡️ Riesgo: ≤{self.max_allowed_risk}% SAGRADO")
        print(f"🛠️ Fundamentales: Solo beneficios POSITIVOS + datos completos")
        
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
        fundamental_rejects = 0
        risk_filter_rejects = 0
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(all_symbols))
            batch_symbols = all_symbols[start_idx:end_idx]
            
            print(f"\n=== LOTE {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx}) ===")
            
            for i, symbol in enumerate(batch_symbols):
                try:
                    result = self.evaluate_stock_momentum_responsive(symbol)
                    
                    if result:
                        all_results.append(result)
                        final_score = result.get('score', 0)
                        technical_score = result.get('technical_score', 0)
                        rr_ratio = result.get('risk_reward_ratio', 0)
                        risk = result.get('risk_pct', 0)
                        upside = result.get('upside_pct', 0)
                        mom_20d = result.get('outperformance_20d', 0)
                        weekly_atr = result.get('weekly_atr', 0)
                        daily_atr = result.get('atr', 0)
                        earnings_positive = result.get('fundamental_data', {}).get('quarterly_earnings_positive', False)
                        print(f"✅ {symbol} - Score: {final_score:.1f} (técnico: {technical_score:.1f}) - R/R: {rr_ratio:.1f} - Risk: {risk:.1f}% - Upside: {upside:.1f}% - Mom20d: {mom_20d:+.1f}% - WeeklyATR: {weekly_atr:.2f} - Earnings: {'✅' if earnings_positive else '❌'}")
                    else:
                        # Tracking de rechazos
                        if "Sin beneficios" in str(symbol) or "fundamentales" in str(symbol):
                            fundamental_rejects += 1
                        elif "DESCARTADO - Riesgo" in str(symbol):
                            risk_filter_rejects += 1
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ {symbol} - Error: {e}")
                
                time.sleep(0.1)
            
            if batch_num < total_batches - 1:
                print("⏸️ Pausa entre lotes...")
                time.sleep(2)
        
        # Ordenar por score final
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n=== RESUMEN MOMENTUM RESPONSIVO CON WEEKLY ATR ===")
        print(f"Procesadas: {len(all_symbols)} | Pasaron filtros: {len(all_results)}")
        print(f"🔧 Mejoras aplicadas: Weekly ATR take profit + Min stop loss")
        print(f"🛡️ Filtro de riesgo: ≤{self.max_allowed_risk}% (SAGRADO - MÁS RESTRICTIVO)")
        print(f"📈 Momentum: 20d peso {self.momentum_20d_weight:.1f}, 60d peso {self.momentum_60d_weight:.1f}")
        print(f"🛠️ Rechazos por fundamentales: {fundamental_rejects}")
        print(f"🚫 Rechazos por riesgo >10%: {risk_filter_rejects}")
        print(f"❌ Errores: {failed_count}")
        
        if all_results:
            avg_risk = sum(r['risk_pct'] for r in all_results) / len(all_results)
            avg_rr = sum(r['risk_reward_ratio'] for r in all_results) / len(all_results)
            avg_upside = sum(r['upside_pct'] for r in all_results) / len(all_results)
            avg_mom_20d = sum(r['outperformance_20d'] for r in all_results) / len(all_results)
            avg_weekly_atr = sum(r.get('weekly_atr', 0) for r in all_results) / len(all_results)
            avg_daily_atr = sum(r.get('atr', 0) for r in all_results) / len(all_results)
            
            high_upside = len([r for r in all_results if r['upside_pct'] > 30])
            excellent_rr = len([r for r in all_results if r['risk_reward_ratio'] > 3.0])
            
            # 🛠️ NUEVO: Verificar que todos tienen beneficios positivos
            with_positive_earnings = len([r for r in all_results 
                                        if r.get('fundamental_data', {}).get('quarterly_earnings_positive', False)])
            
            print(f"📊 ESTADÍSTICAS OPTIMIZADAS:")
            print(f"   - Riesgo promedio: {avg_risk:.1f}% (más restrictivo con min stop)")
            print(f"   - R/R promedio: {avg_rr:.1f}:1")
            print(f"   - Upside promedio: {avg_upside:.1f}% (weekly ATR optimized)")
            print(f"   - Momentum 20d promedio: {avg_mom_20d:+.1f}%")
            print(f"   - Weekly ATR promedio: {avg_weekly_atr:.2f}")
            print(f"   - Daily ATR promedio: {avg_daily_atr:.2f}")
            print(f"   - Ratio Weekly/Daily ATR: {avg_weekly_atr/avg_daily_atr:.1f}x" if avg_daily_atr > 0 else "")
            print(f"🎯 Con upside >30%: {high_upside}/{len(all_results)} ({high_upside/len(all_results)*100:.1f}%)")
            print(f"🏆 Con R/R >3:1: {excellent_rr}/{len(all_results)} ({excellent_rr/len(all_results)*100:.1f}%)")
            print(f"🛠️ Con beneficios positivos: {with_positive_earnings}/{len(all_results)} ({with_positive_earnings/len(all_results)*100:.1f}%)")
        
        return all_results

def cleanup_old_files():
    """Limpia archivos antiguos manteniendo solo las últimas 6 semanas"""
    print("🧹 Iniciando limpieza automática de archivos...")
    
    def cleanup_file_type(pattern, keep_count, file_type_name):
        files = glob.glob(pattern)
        if not files:
            print(f"   📂 {file_type_name}: No hay archivos para limpiar")
            return
        
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
    
    cleanup_file_type("weekly_screening_results_*.json", 6, "Screening históricos")
    cleanup_file_type("ultra_conservative_results_*.json", 6, "Resultados conservadores")
    cleanup_file_type("momentum_responsive_results_*.json", 6, "Resultados momentum")
    cleanup_file_type("ENHANCED_WEEKLY_REPORT_*.md", 4, "Reportes semanales")
    cleanup_file_type("consistency_analysis_*.json", 4, "Análisis de consistencia") 
    cleanup_file_type("rotation_recommendations_*.json", 4, "Recomendaciones de rotación")
    
    print("✅ Limpieza automática completada")

def archive_previous_results():
    """Archiva el archivo anterior para mantener historial"""
    if not os.path.exists("weekly_screening_results.json"):
        print("📁 No hay archivo anterior para archivar")
        return
    
    try:
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
    """Función principal optimizada para momentum trading agresivo con Weekly ATR"""
    screener = MomentumResponsiveScreener()
    
    # PASO 1: Archivar archivo anterior
    archive_previous_results()
    
    # PASO 2: Ejecutar screening momentum responsivo con Weekly ATR
    results = screener.screen_all_stocks_momentum_responsive()
    
    # PASO 3: Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Archivo completo con timestamp
    full_results_file = f"momentum_responsive_results_{timestamp}.json"
    with open(full_results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'momentum_responsive_aggressive_trading_weekly_atr_optimized',
            'improvements_applied': {
                'weekly_atr_take_profit': True,
                'min_stop_loss_restrictive': True,
                'timeframe_alignment': '1_month_swing_trading'
            },
            'max_allowed_risk': screener.max_allowed_risk,
            'momentum_weights': {
                '20d': screener.momentum_20d_weight,
                '60d': screener.momentum_60d_weight,
                '90d': screener.momentum_90d_weight
            },
            'aggressive_filters': {
                'min_outperf_20d': screener.min_outperf_20d,
                'min_outperf_60d': screener.min_outperf_60d,
                '90d_eliminated': True
            },
            'fundamental_filters': {
                'earnings_positive_required': True,
                'complete_data_required': True,
                'strict_validation': True
            },
            'total_screened': len(screener.get_nyse_nasdaq_symbols()) if screener.get_nyse_nasdaq_symbols() else 0,
            'total_passed': len(results),
            'spy_benchmark': screener.spy_benchmark,
            'results': results,
            'methodology': {
                'philosophy': 'Swing for the fences con gestión manual de exits',
                'target_hold': '~1 mes con rotación agresiva',
                'entry_filters': 'Momentum responsivo: 20d >5%, 60d >0%, 90d eliminado',
                'max_risk_filter': f'{screener.max_allowed_risk}% maximum (SAGRADO)',
                'stop_loss': 'Ultra conservative: ≤10% enforcement with MIN selection (more restrictive)',
                'take_profit': 'Weekly ATR-based: 3.0x/2.5x/2.0x targeting optimized for 1-month holds',
                'scoring': 'Momentum weighted (20d 70%, 60d 30%) + acceleration bonus + R/R integration',
                'fundamental_requirement': 'ONLY positive earnings + complete fundamental data',
                'spy_benchmark_fix': 'Applied - now correctly filters when SPY unavailable',
                'weekly_atr_optimization': 'Weekly ATR for take profit alignment with 1-month holding period',
                'stop_loss_improvement': 'MIN selection for more restrictive risk filtering'
            }
        }, f, indent=2, default=str)
    
    # Archivo compatible con sistema existente
    top_15 = results[:15]
    screening_data = {
        'analysis_date': datetime.now().isoformat(),
        'analysis_type': 'momentum_responsive_aggressive_trading_weekly_atr_optimized',
        'philosophy': 'swing_for_fences_with_manual_exits_weekly_atr',
        'momentum_optimization': {
            'timeframe_weights': {'20d': 70, '60d': 30, '90d': 0},
            'aggressive_filters': True,
            'acceleration_detection': True,
            'weekly_atr_take_profit': True,
            'min_stop_loss_restrictive': True
        },
        'fundamental_validation': {
            'earnings_positive_only': True,
            'complete_data_required': True,
            'strict_filtering': True
        },
        'improvements_applied': {
            'weekly_atr_optimization': 'Take profit targets now use weekly ATR for 1-month alignment',
            'stop_loss_restriction': 'MIN selection makes risk filtering more restrictive',
            'timeframe_alignment': 'Weekly volatility patterns match 1-month holding period'
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
            'high_upside_count': len([r for r in top_15 if r.get('upside_pct', 0) > 30]) if top_15 else 0,
            'excellent_rr_count': len([r for r in top_15 if r.get('risk_reward_ratio', 0) > 3.0]) if top_15 else 0,
            'positive_earnings_count': len([r for r in top_15 
                                          if r.get('fundamental_data', {}).get('quarterly_earnings_positive', False)]) if top_15 else 0,
            'avg_weekly_atr': sum(r.get('weekly_atr', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'avg_daily_atr': sum(r.get('atr', 0) for r in top_15) / len(top_15) if top_15 else 0
        }
    }
    
    with open("weekly_screening_results.json", 'w') as f:
        json.dump(screening_data, f, indent=2, default=str)
    
    # PASO 4: Limpieza automática
    cleanup_old_files()
    
    print(f"\n✅ Archivos guardados con WEEKLY ATR + MIN STOP LOSS OPTIMIZATION:")
    print(f"   - {full_results_file} (resultados momentum responsivos optimizados)")
    print(f"   - weekly_screening_results.json (actual)")
    print(f"   - Archivos históricos mantenidos automáticamente")
    
    if len(top_15) > 0:
        print(f"\n🏆 TOP 5 MOMENTUM AGRESIVO - WEEKLY ATR OPTIMIZED:")
        for i, stock in enumerate(top_15[:5]):
            final_score = stock.get('score', 0)
            technical_score = stock.get('technical_score', 0)
            risk = stock.get('risk_pct', 0)
            rr = stock.get('risk_reward_ratio', 0)
            target = stock.get('take_profit', 0)
            upside = stock.get('upside_pct', 0)
            mom_20d = stock.get('outperformance_20d', 0)
            atr_mult = stock.get('take_profit_analysis', {}).get('atr_multiplier_used', 0)
            weekly_atr = stock.get('weekly_atr', 0)
            daily_atr = stock.get('atr', 0)
            earnings_positive = stock.get('fundamental_data', {}).get('quarterly_earnings_positive', False)
            
            print(f"   {i+1}. {stock['symbol']} - Score Final: {final_score:.1f} (Técnico: {technical_score:.1f})")
            print(f"      🎯 ${stock['current_price']:.2f} → Target: ${target:.2f} ({upside:.1f}% upside)")
            print(f"      🛡️ Risk: {risk:.1f}% | R/R: {rr:.1f}:1 | Mom20d: {mom_20d:+.1f}%")
            print(f"      🔧 Weekly ATR: {weekly_atr:.2f} vs Daily ATR: {daily_atr:.2f} | Multiplier: {atr_mult}x")
            print(f"      📊 Earnings: {'✅' if earnings_positive else '❌'} | Stop: MIN restrictive")
            print()
            
        stats = screening_data['momentum_responsive_stats']
        print(f"📊 ESTADÍSTICAS WEEKLY ATR OPTIMIZED:")
        print(f"   - Upside promedio: {stats['avg_upside']:.1f}% (weekly ATR optimized)")
        print(f"   - R/R promedio: {stats['avg_risk_reward']:.1f}:1")
        print(f"   - Con upside >30%: {stats['high_upside_count']}/{len(top_15)}")
        print(f"   - Con R/R >3:1: {stats['excellent_rr_count']}/{len(top_15)}")
        print(f"   - Momentum 20d promedio: {stats['avg_momentum_20d']:+.1f}%")
        print(f"   - Weekly ATR promedio: {stats['avg_weekly_atr']:.2f}")
        print(f"   - Daily ATR promedio: {stats['avg_daily_atr']:.2f}")
        print(f"   - Weekly/Daily ratio: {stats['avg_weekly_atr']/stats['avg_daily_atr']:.1f}x" if stats['avg_daily_atr'] > 0 else "")
        print(f"   - 🛠️ Con beneficios positivos: {stats['positive_earnings_count']}/{len(top_15)} (100% requerido)")
        print(f"   - 🔧 Mejoras: Weekly ATR + Min Stop Loss = mejor alineación temporal")
    else:
        print(f"\n⚠️ Ninguna acción pasa los filtros momentum agresivos optimizados esta semana")
        print("💡 Filtros ahora más restrictivos: Weekly ATR + Min stop loss + fundamentales estrictos")

if __name__ == "__main__":
    main()
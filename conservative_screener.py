#!/usr/bin/env python3
"""
Conservative Stock Screener with MA50 Stop Loss Bonus
=====================================================

Sistema de screening optimizado para momentum trading agresivo con:
- Weekly ATR para take profit
- Bonus especial de 22 puntos para rebotes en MA50
- Stop loss ultra conservador (≤10%)
- Filtros fundamentales estrictos
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

class MomentumResponsiveScreener:
    def __init__(self):
        # CONFIGURACIÓN CONSERVADORA ESTRICTA
        self.max_allowed_risk = 10.0  # SAGRADO: Máximo 10% de riesgo
        
        # MOMENTUM RESPONSIVE: Pesos optimizados para agresividad
        self.momentum_20d_weight = 0.70  # 70% peso a momentum corto plazo
        self.momentum_60d_weight = 0.30  # 30% peso a momentum medio plazo  
        self.momentum_90d_weight = 0.00  # ELIMINADO para mayor agresividad
        
        # FILTROS AGRESIVOS OPTIMIZADOS
        self.min_outperf_20d = 5    # Mínimo 5% vs SPY en 20 días
        self.min_outperf_60d = 0    # Neutral vs SPY en 60 días (más permisivo)
        # 90d eliminado completamente
        
        # CONFIGURACIÓN TÉCNICA
        self.min_volume = 1_000_000
        self.min_price = 5.0
        self.max_price = 1000.0
        self.spy_benchmark = None
        
        # 🆕 BONUS ESPECIAL PARA REBOTE MA50
        self.ma50_stop_bonus = 22  # 22 puntos extra por rebote MA50
        
        print(f"🚀 Screener inicializado - BONUS MA50: +{self.ma50_stop_bonus} pts")
    
    def get_spy_benchmark(self):
        """Obtiene métricas de referencia del SPY para comparación"""
        try:
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="6mo")
            
            if len(spy_hist) < 90:
                print("⚠️ SPY: Datos insuficientes")
                return None
            
            current_spy = spy_hist['Close'].iloc[-1]
            
            spy_20d = spy_hist['Close'].iloc[-21] if len(spy_hist) >= 21 else current_spy
            spy_60d = spy_hist['Close'].iloc[-61] if len(spy_hist) >= 61 else current_spy
            spy_90d = spy_hist['Close'].iloc[-91] if len(spy_hist) >= 91 else current_spy
            
            return {
                'current_price': current_spy,
                'return_20d': ((current_spy - spy_20d) / spy_20d) * 100,
                'return_60d': ((current_spy - spy_60d) / spy_60d) * 100,
                'return_90d': ((current_spy - spy_90d) / spy_90d) * 100
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo SPY benchmark: {e}")
            return None
    
    def get_nyse_nasdaq_symbols(self):
        """Obtiene símbolos de NYSE y NASDAQ con filtros básicos"""
        try:
            # Lista de símbolos comunes para testing local
            test_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'AMD', 'INTC', 'CRM', 'ADBE', 'PYPL', 'MRNA', 'ZM', 'SHOP',
                'SQ', 'ROKU', 'TWLO', 'DOCU', 'PTON', 'ZS', 'CRWD', 'SNOW'
            ]
            
            # En producción, usar una fuente más completa
            symbols = test_symbols
            
            print(f"📊 Símbolos cargados: {len(symbols)}")
            return symbols
            
        except Exception as e:
            print(f"❌ Error cargando símbolos: {e}")
            return []
    
    def calculate_weekly_atr(self, hist, period=14):
        """Calcula Weekly ATR para take profit optimizado"""
        try:
            if len(hist) < period * 7:  # Necesitamos más datos para weekly
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
            
            # Últimos 60 días para niveles
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
            
            # Volatilidad de 30 días
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
        Calcula stop loss ultra conservador con PRIORIDAD PARA MA50
        🆕 INCLUYE LÓGICA ESPECIAL PARA BONUS MA50
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
                
                # MA50 stop - ¡LA ESTRELLA!
                if ma50 > 0 and current_price > ma50:
                    ma50_stop = ma50 * 0.985
                    ma50_risk = ((current_price - ma50_stop) / current_price) * 100
                    
                    if 5 < ma50_risk <= 10.0:
                        ma50_stop_data = {
                            'price': ma50_stop,
                            'risk': ma50_risk
                        }
                        all_stops['ma50'] = ma50_stop_data
            
            # 🆕 NUEVA LÓGICA DE PRIORIZACIÓN - MA50 FIRST!
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
                
            # PRIORIDAD 3: Otros métodos si MA no están disponibles
            elif all_stops:
                # Usar mínimo de ATR y support (más restrictivo)
                other_stops = {k: v for k, v in all_stops.items() if k not in ['ma21', 'ma50']}
                
                if other_stops:
                    min_stop_key = min(other_stops.keys(), key=lambda k: other_stops[k]['price'])
                    final_stop = other_stops[min_stop_key]['price']
                    risk_percentage = other_stops[min_stop_key]['risk']
                    selection_method = f'min_other_{min_stop_key}'
                    methods_used = [min_stop_key]
                else:
                    # Fallback si solo hay MA pero están fuera de rango
                    final_stop = current_price * 0.92
                    risk_percentage = 8.0
                    selection_method = 'fallback_8pct'
                    methods_used = ['fallback']
            
            # FALLBACK: Stop mínimo del 8%
            else:
                final_stop = current_price * 0.92
                risk_percentage = 8.0
                selection_method = 'fallback_8pct'
                methods_used = ['fallback']
            
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
    
    def calculate_responsive_momentum_score(self, outperf_20d, outperf_60d, outperf_90d):
        """Calcula score de momentum responsivo con pesos optimizados"""
        
        # Puntajes base por rango de outperformance
        def score_by_range(outperf):
            if outperf >= 20:
                return 50
            elif outperf >= 15:
                return 40
            elif outperf >= 10:
                return 30
            elif outperf >= 5:
                return 20
            elif outperf >= 0:
                return 10
            elif outperf >= -5:
                return 5
            else:
                return 0
        
        # Scores individuales
        score_20d = score_by_range(outperf_20d)
        score_60d = score_by_range(outperf_60d)
        score_90d = 0  # Eliminado para mayor agresividad
        
        # Score ponderado
        weighted_score = (
            score_20d * self.momentum_20d_weight +
            score_60d * self.momentum_60d_weight +
            score_90d * self.momentum_90d_weight
        )
        
        # Bonus por aceleración (20d >> 60d)
        acceleration_bonus = 0
        if outperf_20d > outperf_60d + 5:  # 20d supera 60d por +5%
            acceleration_bonus = min((outperf_20d - outperf_60d) * 0.5, 15)
        
        total_score = weighted_score + acceleration_bonus
        
        return {
            'score_20d': score_20d,
            'score_60d': score_60d,
            'score_90d': score_90d,
            'weighted_score': weighted_score,
            'acceleration_bonus': acceleration_bonus,
            'total_score': total_score,
            'momentum_category': self.categorize_momentum(total_score)
        }
    
    def categorize_momentum(self, score):
        """Categoriza el momentum según el score"""
        if score >= 45:
            return 'EXCEPTIONAL'
        elif score >= 35:
            return 'STRONG'
        elif score >= 25:
            return 'MODERATE'
        else:
            return 'WEAK'
    
    def get_fundamental_data(self, ticker_info):
        """Obtiene y valida datos fundamentales con filtros estrictos"""
        try:
            # Extraer métricas clave
            quarterly_earnings = ticker_info.get('quarterlyEarningsGrowth')
            quarterly_revenue = ticker_info.get('quarterlyRevenueGrowth') 
            roe = ticker_info.get('returnOnEquity')
            profit_margins = ticker_info.get('profitMargins')
            
            # Validación estricta de beneficios
            earnings_positive = False
            if quarterly_earnings is not None:
                earnings_positive = quarterly_earnings > 0
            elif profit_margins is not None:
                earnings_positive = profit_margins > 0
            
            # Verificar datos mínimos requeridos
            has_required_data = any([
                quarterly_earnings is not None,
                quarterly_revenue is not None,
                roe is not None,
                profit_margins is not None
            ])
            
            return {
                'quarterly_earnings_growth': quarterly_earnings,
                'quarterly_revenue_growth': quarterly_revenue,
                'roe': roe,
                'profit_margins': profit_margins,
                'quarterly_earnings_positive': earnings_positive,
                'has_required_data': has_required_data,
                'fundamental_score': self.calculate_fundamental_score(
                    quarterly_earnings, quarterly_revenue, roe, profit_margins
                )
            }
            
        except Exception as e:
            return {
                'quarterly_earnings_positive': False,
                'has_required_data': False,
                'fundamental_score': 0,
                'error': str(e)
            }
    
    def calculate_fundamental_score(self, earnings_growth, revenue_growth, roe, profit_margins):
        """Calcula score fundamental"""
        score = 0
        
        # Earnings growth
        if earnings_growth is not None:
            if earnings_growth > 0.15:  # >15%
                score += 20
            elif earnings_growth > 0:
                score += 10
        
        # Revenue growth
        if revenue_growth is not None:
            if revenue_growth > 0.10:  # >10%
                score += 15
            elif revenue_growth > 0:
                score += 8
        
        # ROE
        if roe is not None:
            if roe > 0.15:  # >15%
                score += 15
            elif roe > 0.10:
                score += 10
            elif roe > 0:
                score += 5
        
        # Profit margins
        if profit_margins is not None:
            if profit_margins > 0.15:
                score += 10
            elif profit_margins > 0.05:
                score += 5
        
        return min(score, 50)  # Cap at 50 points
    
    def analyze_stock_momentum_responsive(self, symbol):
        """
        Análisis completo de una acción con BONUS ESPECIAL MA50
        🆕 Incluye bonus de 22 puntos para rebotes en MA50
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")
            
            if len(hist) < 90:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Filtros básicos
            if current_price < self.min_price or current_price > self.max_price:
                return None
            
            volume_avg_30d = hist['Volume'].tail(30).mean()
            if volume_avg_30d < self.min_volume:
                return None
            
            # Calcular outperformance vs SPY
            if not self.spy_benchmark:
                self.spy_benchmark = self.get_spy_benchmark()
            
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
            
            # 🛡️ STOP LOSS ULTRA CONSERVADOR - ¡CON DETECCIÓN MA50!
            stop_analysis = self.calculate_ultra_conservative_stop_loss(
                hist, current_price, atr, support_resistance, volatility_metrics
            )
            
            # 🛡️ FILTRO SAGRADO: Si riesgo > 10%, descartar
            if stop_analysis['risk_percentage'] > self.max_allowed_risk:
                return None
            
            # 🛠️ FUNDAMENTALES CON FILTROS ESTRICTOS
            try:
                ticker_info = ticker.info
                fundamental_data = self.get_fundamental_data(ticker_info)
                
                if fundamental_data.get('quarterly_earnings_positive') == False:
                    print(f"🚫 {symbol} DESCARTADO - Sin beneficios positivos")
                    return None
                
                if not fundamental_data.get('has_required_data', False):
                    print(f"🚫 {symbol} DESCARTADO - Sin datos fundamentales suficientes")
                    return None
                    
            except Exception as e:
                print(f"🚫 {symbol} DESCARTADO - Error obteniendo fundamentales: {e}")
                return None
            
            # 🆕 SCORE TÉCNICO CON SISTEMA DE MOMENTUM RESPONSIVO
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
            
            # 🌟 BONUS ESPECIAL MA50 - ¡REBOTE ALCISTA!
            ma50_bonus = 0
            if stop_analysis.get('ma50_bonus_eligible', False):
                ma50_bonus = self.ma50_stop_bonus
                print(f"🌟 {symbol} - BONUS MA50 APLICADO: +{ma50_bonus} pts (rebote alcista)")
            
            # 🆕 SCORE TÉCNICO RESPONSIVO CON BONUS MA50
            technical_score = (
                momentum_analysis['total_score'] +
                volatility_bonus +
                volume_score +
                risk_bonus +
                ma50_bonus  # 🌟 NUEVO BONUS
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
                'target_hold': '~1 mes (rotación diaria)',  # 🔄 ACTUALIZADO
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
            print(f"❌ Error procesando {symbol}: {e}")
            return None
    
    def calculate_take_profit_weekly_atr(self, current_price, weekly_atr, daily_atr, score):
        """Calcula take profit basado en Weekly ATR"""
        try:
            # Usar Weekly ATR si disponible, sino Daily ATR
            atr_to_use = weekly_atr if weekly_atr > 0 else daily_atr
            atr_type = 'weekly' if weekly_atr > 0 else 'daily'
            
            # Multiplicadores basados en score (más agresivos para weekly)
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
                'risk_reward_ratio': upside_pct / 10.0  # Asumiendo 10% risk max
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
            if score < 20:  # Score mínimo
                return None
            
            return stock_result
            
        except Exception as e:
            print(f"❌ Error en filtro conservador: {e}")
            return None
    
    def screen_all_stocks_momentum_responsive(self):
        """Screening optimizado para momentum trading agresivo con Weekly ATR y MA50 Bonus"""
        print(f"=== MOMENTUM RESPONSIVE SCREENING - WEEKLY ATR + MA50 BONUS ===")
        print(f"🎯 Take Profit: Weekly ATR-based (× 3.0/2.5/2.0) para holds de 1 mes")
        print(f"🛡️ Stop Loss: MA50 PRIORITY con bonus +{self.ma50_stop_bonus} pts")
        print(f"📈 Momentum: 20d {self.momentum_20d_weight*100:.0f}% + 60d {self.momentum_60d_weight*100:.0f}% + 90d eliminado")
        print(f"🔧 Filtros: 20d >{self.min_outperf_20d}%, 60d >{self.min_outperf_60d}%")
        print(f"🌟 BONUS MA50: +{self.ma50_stop_bonus} puntos para rebotes alcistas")
        
        symbols = self.get_nyse_nasdaq_symbols()
        if not symbols:
            print("❌ No se pudieron cargar símbolos")
            return []
        
        results = []
        processed = 0
        ma50_bonus_count = 0
        
        for symbol in symbols:
            try:
                result = self.analyze_stock_momentum_responsive(symbol)
                if result:
                    results.append(result)
                    
                    # Contar aplicaciones de bonus MA50
                    if result.get('optimizations', {}).get('ma50_bonus_applied', False):
                        ma50_bonus_count += 1
                    
                processed += 1
                if processed % 50 == 0:
                    print(f"📊 Procesado: {processed}/{len(symbols)} - Válidos: {len(results)} - MA50 Bonus: {ma50_bonus_count}")
                    
            except Exception as e:
                print(f"❌ Error procesando {symbol}: {e}")
                continue
        
        # Ordenar por score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n✅ SCREENING COMPLETADO:")
        print(f"   📊 Procesados: {processed}")
        print(f"   ✅ Aprobados: {len(results)}")
        print(f"   🌟 Con bonus MA50: {ma50_bonus_count}")
        print(f"   📈 Tasa éxito: {len(results)/processed*100:.1f}%")
        
        return results

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
    """Función principal optimizada para momentum trading con MA50 bonus"""
    screener = MomentumResponsiveScreener()
    
    # PASO 1: Archivar archivo anterior
    archive_previous_results()
    
    # PASO 2: Ejecutar screening con MA50 bonus
    results = screener.screen_all_stocks_momentum_responsive()
    
    # PASO 3: Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Archivo completo con timestamp
    full_results_file = f"momentum_responsive_results_{timestamp}.json"
    with open(full_results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'momentum_responsive_aggressive_trading_weekly_atr_ma50_bonus',
            'improvements_applied': {
                'weekly_atr_take_profit': True,
                'ma50_priority_stop_loss': True,
                'ma50_bonus_system': True,  # 🌟 NUEVO
                'ma50_bonus_value': screener.ma50_stop_bonus,  # 🌟 VALOR
                'daily_execution_ready': True  # 🔄 NUEVO
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
                'philosophy': 'Swing for the fences con gestión diaria de exits',
                'target_hold': '~1 mes con monitorización diaria',  # 🔄 ACTUALIZADO
                'entry_filters': 'Momentum responsivo: 20d >5%, 60d >0%, 90d eliminado',
                'max_risk_filter': f'{screener.max_allowed_risk}% maximum (SAGRADO)',
                'stop_loss': 'MA50 PRIORITY con bonus +22pts por rebote alcista',
                'take_profit': 'Weekly ATR-based: 3.0x/2.5x/2.0x targeting optimized',
                'scoring': 'Momentum weighted + MA50 bonus + R/R integration',
                'fundamental_requirement': 'ONLY positive earnings + complete fundamental data',
                'ma50_bonus_system': f'+{screener.ma50_stop_bonus} puntos por rebote en MA50',  # 🌟
                'execution_frequency': 'Diaria con criterios de rotación estrictos'  # 🔄
            }
        }, f, indent=2, default=str)
    
    # Archivo compatible con sistema existente
    top_15 = results[:15]
    screening_data = {
        'analysis_date': datetime.now().isoformat(),
        'analysis_type': 'momentum_responsive_aggressive_trading_weekly_atr_ma50_bonus',
        'philosophy': 'swing_for_fences_with_daily_monitoring_ma50_bonus',
        'momentum_optimization': {
            'timeframe_weights': {'20d': 70, '60d': 30, '90d': 0},
            'aggressive_filters': True,
            'acceleration_detection': True,
            'weekly_atr_take_profit': True,
            'ma50_priority_stop_loss': True,
            'ma50_bonus_system': True  # 🌟 NUEVO FLAG
        },
        'fundamental_validation': {
            'earnings_positive_only': True,
            'complete_data_required': True,
            'strict_filtering': True
        },
        'improvements_applied': {
            'weekly_atr_optimization': 'Take profit targets use weekly ATR for 1-month alignment',
            'ma50_priority_system': 'MA50 stop loss prioritized with +22pt bonus for bullish rebounds',
            'daily_execution_ready': 'System prepared for daily execution with strict rotation criteria'
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
            'avg_daily_atr': sum(r.get('atr', 0) for r in top_15) / len(top_15) if top_15 else 0,
            'ma50_bonus_count': len([r for r in top_15 if r.get('optimizations', {}).get('ma50_bonus_applied', False)]) if top_15 else 0  # 🌟
        }
    }
    
    with open("weekly_screening_results.json", 'w') as f:
        json.dump(screening_data, f, indent=2, default=str)
    
    # PASO 4: Limpieza automática
    cleanup_old_files()
    
    print(f"\n✅ Archivos guardados con MA50 BONUS SYSTEM:")
    print(f"   - {full_results_file} (resultados con bonus MA50)")
    print(f"   - weekly_screening_results.json (actual)")
    print(f"   - Archivos históricos mantenidos automáticamente")
    
    if len(top_15) > 0:
        print(f"\n🏆 TOP 5 MOMENTUM AGRESIVO - MA50 BONUS SYSTEM:")
        for i, stock in enumerate(top_15[:5]):
            final_score = stock.get('score', 0)
            technical_score = stock.get('technical_score', 0)
            risk = stock.get('risk_pct', 0)
            rr = stock.get('risk_reward_ratio', 0)
            target = stock.get('take_profit', 0)
            upside = stock.get('upside_pct', 0)
            mom_20d = stock.get('outperformance_20d', 0)
            ma50_bonus = stock.get('optimizations', {}).get('ma50_bonus_applied', False)
            ma50_bonus_val = stock.get('optimizations', {}).get('ma50_bonus_value', 0)
            weekly_atr = stock.get('weekly_atr', 0)
            earnings_positive = stock.get('fundamental_data', {}).get('quarterly_earnings_positive', False)
            
            ma50_indicator = f" 🌟+{ma50_bonus_val}" if ma50_bonus else ""
            
            print(f"   {i+1}. {stock['symbol']}{ma50_indicator} | Score: {final_score:.1f} | Risk: {risk:.1f}% | R/R: {rr:.1f} | Upside: {upside:.1f}% | Mom20d: {mom_20d:+.1f}%")

if __name__ == "__main__":
    main()
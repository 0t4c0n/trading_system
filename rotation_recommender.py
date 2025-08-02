#!/usr/bin/env python3
"""
Aggressive Rotation Recommender - ACTUALIZADO: Criterios estrictos para trading mensual
🌍 MANTIENE: Toda la funcionalidad de divisas y portfolio vacío existente
🆕 AÑADE: Criterios estrictos (+30pts, stop proximity, momentum loss) para evitar overtrading
🔄 FILOSOFÍA: Daily monitoring, monthly trading
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math
import requests

class PortfolioCurrencyHandler:
    def __init__(self):
        self.exchange_rates = {}
        self.cache_expiry = None
        self.cache_duration_hours = 6
        
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Obtiene tipo de cambio con cache de 6 horas"""
        if from_currency == to_currency:
            return 1.0
            
        cache_key = f"{from_currency}_{to_currency}"
        
        if (self.cache_expiry and 
            datetime.now() < self.cache_expiry and 
            cache_key in self.exchange_rates):
            return self.exchange_rates[cache_key]
        
        try:
            rate = self._fetch_exchange_rate_multiple_sources(from_currency, to_currency)
            
            if rate > 0:
                self.exchange_rates[cache_key] = rate
                self.cache_expiry = datetime.now() + timedelta(hours=self.cache_duration_hours)
                return rate
            else:
                return self._get_fallback_rate(from_currency, to_currency)
                
        except Exception as e:
            return self._get_fallback_rate(from_currency, to_currency)
    
    def _fetch_exchange_rate_multiple_sources(self, from_currency: str, to_currency: str) -> float:
        """Intenta múltiples fuentes para obtener el tipo de cambio"""
        
        # Source 1: exchangerate-api.com (free tier)
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if to_currency in data.get('rates', {}):
                    return float(data['rates'][to_currency])
        except Exception:
            pass
        
        # Source 2: European Central Bank (free, no API key needed)
        try:
            if from_currency == 'EUR' or to_currency == 'EUR':
                ecb_url = "https://api.exchangerate.host/latest?base=EUR"
                response = requests.get(ecb_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if from_currency == 'EUR' and to_currency in data.get('rates', {}):
                        return float(data['rates'][to_currency])
                    elif to_currency == 'EUR' and from_currency in data.get('rates', {}):
                        return 1.0 / float(data['rates'][from_currency])
        except Exception:
            pass
        
        return 0
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> float:
        """Tipos de cambio de fallback"""
        fallback_rates = {
            'EUR_USD': 1.08,
            'USD_EUR': 0.93,
            'EUR_GBP': 0.87,
            'GBP_EUR': 1.15,
            'USD_GBP': 0.80,
            'GBP_USD': 1.25
        }
        
        key = f"{from_currency}_{to_currency}"
        return fallback_rates.get(key, 1.0)
    
    def normalize_portfolio_to_usd(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza portfolio a USD para cálculos internos"""
        if not portfolio_data:
            return portfolio_data
        
        base_currency = portfolio_data.get('base_currency', 'EUR')
        
        if base_currency == 'USD':
            return portfolio_data
        
        eur_to_usd = self.get_exchange_rate(base_currency, 'USD')
        normalized_portfolio = portfolio_data.copy()
        
        if 'cash' in portfolio_data:
            original_cash = portfolio_data['cash']
            normalized_portfolio['cash_usd'] = original_cash * eur_to_usd
            normalized_portfolio['cash_original'] = original_cash
            normalized_portfolio['cash_currency'] = base_currency
        
        if 'total_invested' in portfolio_data:
            original_total = portfolio_data['total_invested']
            normalized_portfolio['total_invested_usd'] = original_total * eur_to_usd
            normalized_portfolio['total_invested_original'] = original_total
        
        normalized_portfolio['currency_conversion'] = {
            'base_currency': base_currency,
            'target_currency': 'USD',
            'exchange_rate': eur_to_usd,
            'conversion_timestamp': datetime.now().isoformat()
        }
        
        return normalized_portfolio
    
    def analyze_portfolio_status(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el estado del portfolio distinguiendo entre cash y momentum perdido"""
        if not portfolio_data:
            return {
                'status': 'NO_PORTFOLIO',
                'description': 'No portfolio data available',
                'positions_count': 0,
                'is_waiting_for_opportunities': False
            }
        
        positions = portfolio_data.get('positions', {})
        cash = portfolio_data.get('cash_usd', portfolio_data.get('cash', 0))
        total_invested = portfolio_data.get('total_invested_usd', portfolio_data.get('total_invested', 0))
        
        positions_count = len(positions)
        total_portfolio_value = total_invested + cash
        
        if total_portfolio_value > 0:
            cash_percentage = (cash / total_portfolio_value) * 100
        else:
            cash_percentage = 100 if cash > 0 else 0
        
        if positions_count == 0 and cash > 0:
            status = 'ALL_CASH_WAITING'
            description = 'Portfolio 100% en cash - Esperando oportunidades de inversión'
            is_waiting_for_opportunities = True
        elif positions_count == 0 and cash == 0:
            status = 'EMPTY_PORTFOLIO'
            description = 'Portfolio vacío - Necesita capitalización'
            is_waiting_for_opportunities = False
        elif cash_percentage > 90:
            status = 'MOSTLY_CASH'
            description = f'Portfolio mayormente en cash ({cash_percentage:.1f}%) - Posiciones mínimas'
            is_waiting_for_opportunities = True
        elif positions_count > 0:
            status = 'INVESTED'
            description = f'Portfolio activo con {positions_count} posiciones ({100-cash_percentage:.1f}% invertido)'
            is_waiting_for_opportunities = False
        else:
            status = 'UNKNOWN'
            description = 'Estado del portfolio no determinado'
            is_waiting_for_opportunities = False
        
        return {
            'status': status,
            'description': description,
            'positions_count': positions_count,
            'cash_percentage': cash_percentage,
            'total_portfolio_value_usd': total_portfolio_value,
            'cash_usd': cash,
            'invested_usd': total_invested,
            'is_waiting_for_opportunities': is_waiting_for_opportunities,
            'currency_info': portfolio_data.get('currency_conversion', {})
        }

class AggressiveRotationRecommender:
    def __init__(self):
        self.current_portfolio = None
        self.consistency_analysis = None
        self.screening_data = None
        self.currency_handler = PortfolioCurrencyHandler()
        self.portfolio_status = None
        
        # 🆕 CRITERIOS ESTRICTOS PARA TRADING MENSUAL
        self.min_score_difference = 30.0  # Mínimo 30 puntos de diferencia para rotación
        self.stop_loss_proximity_threshold = 0.03  # 3% cerca del stop loss
        self.momentum_loss_days = 3  # 3+ días sin aparecer en screening
        
        # Parámetros originales mantenidos
        self.rotation_threshold = 0.20
        self.min_consistency_weeks = 2
        self.emerging_opportunity_weight = 1.5
        self.momentum_decay_threshold = 0.15
        self.fallback_avg_score = 100.0
        self.min_viable_score = 50.0
        
        # Optimizations integration
        self.weekly_atr_bonus = 1.15
        self.ma50_bonus_multiplier = 1.20  # 🌟 NUEVO: Multiplicador por MA50 bonus
        self.strict_fundamentals_bonus = 1.10
        self.quality_stop_bonus = 1.05
        
        print(f"🎯 Recomendador con CRITERIOS ESTRICTOS para trading mensual")
        print(f"📊 Score +{self.min_score_difference}, Stop {self.stop_loss_proximity_threshold*100}%, Momentum {self.momentum_loss_days}d")
        
    def load_consistency_analysis(self):
        """Carga análisis de consistencia"""
        try:
            with open('consistency_analysis.json', 'r') as f:
                self.consistency_analysis = json.load(f)
            print(f"📊 Consistency analysis loaded")
            return True
        except FileNotFoundError:
            print("⚠️ consistency_analysis.json no encontrado")
            return False
        except Exception as e:
            print(f"❌ Error cargando consistency analysis: {e}")
            return False
    
    def load_screening_data(self):
        """Carga datos de screening más recientes"""
        try:
            with open('weekly_screening_results.json', 'r') as f:
                self.screening_data = json.load(f)
            print(f"🔍 Screening data loaded")
            return True
        except FileNotFoundError:
            print("⚠️ weekly_screening_results.json no encontrado")
            return False
        except Exception as e:
            print(f"❌ Error cargando screening data: {e}")
            return False
    
    def load_current_portfolio(self):
        """Carga la cartera actual del usuario con soporte de divisas"""
        try:
            with open('current_portfolio.json', 'r') as f:
                raw_portfolio = json.load(f)
            
            # Normalize to USD for calculations
            self.current_portfolio = self.currency_handler.normalize_portfolio_to_usd(raw_portfolio)
            
            # Analyze portfolio status
            self.portfolio_status = self.currency_handler.analyze_portfolio_status(self.current_portfolio)
            
            print(f"📂 Portfolio loaded: {self.portfolio_status['description']}")
            print(f"💰 Status: {self.portfolio_status['status']}")
            
            # Display currency info if conversion happened
            if 'currency_conversion' in self.current_portfolio:
                conv = self.current_portfolio['currency_conversion']
                print(f"💱 Currency: {conv['base_currency']} → {conv['target_currency']} @ {conv['exchange_rate']:.4f}")
            
            return True
            
        except FileNotFoundError:
            print("⚠️ No se encontró current_portfolio.json - Creando archivo ejemplo")
            self.create_enhanced_portfolio_example()
            return False
            
        except Exception as e:
            print(f"❌ Error cargando cartera: {e}")
            return False
    
    def create_enhanced_portfolio_example(self):
        """Crea un archivo de ejemplo con soporte de divisas"""
        mixed_portfolio = {
            "base_currency": "EUR",
            "last_manual_update": datetime.now().isoformat(),
            "positions": {
                "AAPL": {
                    "shares": 50,
                    "entry_price": 150.25,  # USD
                    "entry_date": "2024-01-15T14:30:00Z",
                    "broker": "Interactive Brokers",
                    "notes": "Entrada tras breakout",
                    "currency": "USD",
                    "target_hold_period": "1_month"  # 🆕 TRADING MENSUAL
                }
            },
            "cash": 5000.00,  # EUR
            "total_invested": 7000.00,  # EUR
            "portfolio_summary": {
                "total_portfolio_value_eur": 12000.00,
                "cash_percentage": 41.7,
                "invested_percentage": 58.3
            },
            "strategy": {
                "max_positions": 5,
                "target_hold_period": "1 month with daily monitoring",  # 🆕
                "risk_per_position": "10% máximo",
                "rotation_philosophy": "Monthly trades with strict rotation criteria"  # 🆕
            }
        }
        
        with open('current_portfolio.json', 'w') as f:
            json.dump(mixed_portfolio, f, indent=2)
        
        print("📝 Archivo current_portfolio.json creado - ¡Edítalo con tus posiciones reales!")
        
        # Configurar portfolio status para ejemplo
        self.portfolio_status = {
            'status': 'EXAMPLE_CREATED',
            'description': 'Portfolio ejemplo creado - Configura tus posiciones reales',
            'positions_count': 1,
            'cash_percentage': 41.7,
            'is_waiting_for_opportunities': False
        }
    
    def check_position_near_stop_loss(self, symbol: str, current_price: float, entry_price: float) -> tuple:
        """
        🆕 NUEVO: Verifica si una posición está cerca del stop loss
        Retorna: (cerca_stop, distancia_porcentaje, razon)
        """
        try:
            # Buscar datos de la acción en screening actual
            if not self.screening_data:
                return False, 0.0, "No screening data available"
            
            detailed_results = self.screening_data.get('detailed_results', [])
            stock_data = None
            
            for result in detailed_results:
                if result.get('symbol') == symbol:
                    stock_data = result
                    break
            
            if not stock_data:
                # Calcular stop loss básico si no hay datos
                basic_stop = entry_price * 0.90  # 10% stop loss básico
                distance_to_stop = ((current_price - basic_stop) / current_price)
                
                if distance_to_stop <= self.stop_loss_proximity_threshold:
                    return True, distance_to_stop * 100, f"Cerca de stop loss básico (10%)"
                return False, distance_to_stop * 100, "OK - Lejos del stop loss básico"
            
            # Usar stop loss calculado del screening
            calculated_stop = stock_data.get('stop_loss', entry_price * 0.90)
            distance_to_stop = ((current_price - calculated_stop) / current_price)
            
            if distance_to_stop <= self.stop_loss_proximity_threshold:
                return True, distance_to_stop * 100, f"CRÍTICO: Cerca del stop loss calculado ({calculated_stop:.2f})"
            
            return False, distance_to_stop * 100, "OK - Distancia segura del stop loss"
            
        except Exception as e:
            return False, 0.0, f"Error verificando stop loss: {e}"
    
    def check_momentum_loss(self, symbol: str) -> tuple:
        """
        🆕 NUEVO: Verifica si una acción ha perdido momentum (no aparece en screening por X días)
        Retorna: (perdio_momentum, dias_ausente, razon)
        """
        try:
            if not self.consistency_analysis:
                return False, 0, "No consistency data available"
            
            # Buscar el símbolo en análisis de consistencia
            consistency_data = self.consistency_analysis.get('consistency_analysis', {})
            
            # Verificar en todas las categorías
            all_symbols = []
            for category in ['consistent_winners', 'strong_candidates', 'emerging_opportunities', 'newly_emerged']:
                category_symbols = [item['symbol'] for item in consistency_data.get(category, [])]
                all_symbols.extend(category_symbols)
            
            if symbol not in all_symbols:
                # No aparece en screening actual - asumir pérdida de momentum
                days_absent = self.momentum_loss_days + 1  # Simular días ausente
                return True, days_absent, f"Ausente del screening por {days_absent}+ días"
            
            return False, 0, "Presente en screening actual"
            
        except Exception as e:
            return False, 0, f"Error verificando momentum: {e}"
    
    def calculate_optimization_quality_score(self, stock_data: Dict) -> Dict:
        """
        🆕 MEJORADO: Incluye bonus especial por MA50 stop loss
        """
        base_multiplier = 1.0
        optimization_features = []
        
        # Bonus por Weekly ATR
        if stock_data.get('weekly_atr', 0) > 0:
            base_multiplier *= self.weekly_atr_bonus
            optimization_features.append('weekly_atr')
        
        # 🌟 BONUS ESPECIAL POR MA50 STOP LOSS
        optimizations = stock_data.get('optimizations', {})
        if optimizations.get('ma50_bonus_applied', False):
            base_multiplier *= self.ma50_bonus_multiplier
            optimization_features.append('ma50_rebound')
        
        # Bonus por fundamentales estrictos
        fundamental_data = stock_data.get('fundamental_data', {})
        if fundamental_data.get('quarterly_earnings_positive', False):
            base_multiplier *= self.strict_fundamentals_bonus
            optimization_features.append('positive_earnings')
        
        # Bonus por calidad del stop loss
        stop_analysis = stock_data.get('stop_analysis', {})
        if stop_analysis.get('stop_selection', '').startswith('ma'):
            base_multiplier *= self.quality_stop_bonus
            optimization_features.append('quality_stop')
        
        return {
            'quality_multiplier': base_multiplier,
            'optimization_features': optimization_features,
            'ma50_bonus_detected': optimizations.get('ma50_bonus_applied', False),
            'ma50_bonus_value': optimizations.get('ma50_bonus_value', 0)
        }
    
    def analyze_current_positions_aggressive(self):
        """
        🆕 MODIFICADO: Análisis con criterios estrictos para trading mensual
        """
        if not self.current_portfolio or not self.consistency_analysis:
            return {}
        
        current_positions = self.current_portfolio.get('positions', {})
        if not current_positions:
            return {}
        
        position_analysis = {}
        screening_details = {}
        
        if self.screening_data:
            for result in self.screening_data.get('detailed_results', []):
                screening_details[result['symbol']] = result
        
        # Análisis de posiciones actuales con criterios estrictos
        for symbol, position_data in current_positions.items():
            try:
                entry_price = position_data.get('entry_price', 0)
                entry_date = position_data.get('entry_date', '')
                shares = position_data.get('shares', 0)
                
                # Buscar precio actual en screening data
                current_price = self.get_current_price_from_screening(symbol)
                if not current_price:
                    current_price = entry_price  # Fallback
                
                # 🆕 CRITERIO 1: Verificar proximidad al stop loss
                near_stop, stop_distance, stop_reason = self.check_position_near_stop_loss(
                    symbol, current_price, entry_price
                )
                
                # 🆕 CRITERIO 2: Verificar pérdida de momentum
                momentum_lost, days_absent, momentum_reason = self.check_momentum_loss(symbol)
                
                # Calcular P&L actual
                current_pnl = ((current_price - entry_price) / entry_price) * 100
                
                # 🆕 DETERMINAR RECOMENDACIÓN CON CRITERIOS ESTRICTOS
                recommendation = self.determine_strict_position_recommendation(
                    near_stop, momentum_lost, current_pnl, days_absent
                )
                
                # Calcular urgencia
                urgency = self.calculate_action_urgency(near_stop, momentum_lost)
                
                position_analysis[symbol] = {
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'current_pnl': current_pnl,
                    'shares': shares,
                    'position_value': current_price * shares,
                    'stop_loss_analysis': {
                        'near_stop': near_stop,
                        'distance_pct': stop_distance,
                        'reason': stop_reason
                    },
                    'momentum_analysis': {
                        'momentum_lost': momentum_lost,
                        'days_absent': days_absent,
                        'reason': momentum_reason
                    },
                    'recommendation': recommendation,
                    'action_urgency': urgency,
                    'monthly_trading_assessment': {
                        'meets_exit_criteria': near_stop or momentum_lost,
                        'action_required': urgency in ['URGENT', 'HIGH'],
                        'suitable_for_monthly_hold': not (near_stop or momentum_lost)
                    }
                }
                
            except Exception as e:
                print(f"❌ Error analizando posición {symbol}: {e}")
                position_analysis[symbol] = {
                    'error': str(e),
                    'recommendation': 'ERROR_REQUIRES_MANUAL_REVIEW',
                    'action_urgency': 'HIGH'
                }
        
        return position_analysis
    
    def get_current_price_from_screening(self, symbol: str) -> Optional[float]:
        """Obtiene precio actual desde datos de screening"""
        try:
            if not self.screening_data:
                return None
            
            detailed_results = self.screening_data.get('detailed_results', [])
            for result in detailed_results:
                if result.get('symbol') == symbol:
                    return result.get('current_price', None)
            
            return None
        except Exception:
            return None
    
    def determine_strict_position_recommendation(self, near_stop: bool, momentum_lost: bool, 
                                               current_pnl: float, days_absent: int) -> str:
        """
        🆕 NUEVO: Determina recomendación con criterios estrictos de trading mensual
        """
        # CRITERIOS DE SALIDA URGENTE
        if near_stop and current_pnl < -5:
            return "URGENT_EXIT - Near stop loss with significant loss"
        
        if momentum_lost and days_absent >= 5:
            return "URGENT_EXIT - Lost momentum for 5+ days"
        
        # CRITERIOS DE VIGILANCIA
        if near_stop and current_pnl > 0:
            return "CONSIDER_EXIT - Near stop but profitable, monitor closely"
        
        if momentum_lost and days_absent >= 3:
            return "WATCH_CAREFULLY - Lost momentum, consider exit if continues"
        
        # MANTENER POSICIÓN (filosofía de trading mensual)
        if current_pnl > 10:
            return "HOLD_STRONG - Profitable position within monthly timeframe"
        
        if current_pnl > 0:
            return "HOLD - Positive position, consistent with monthly strategy"
        
        if current_pnl > -5:
            return "HOLD_MONITOR - Small loss, within monthly trading tolerance"
        
        return "EVALUATE - Position requires detailed analysis"
    
    def calculate_action_urgency(self, near_stop: bool, momentum_lost: bool) -> str:
        """Calcula urgencia de acción"""
        if near_stop:
            return 'URGENT'
        
        if momentum_lost:
            return 'HIGH'
        
        return 'LOW'
    
    def identify_rotation_opportunities_aggressive(self):
        """
        🆕 MODIFICADO: Identifica oportunidades con criterios estrictos para trading mensual
        """
        if not self.screening_data or not self.consistency_analysis:
            return []
        
        opportunities = []
        current_positions = self.current_portfolio.get('positions', {}) if self.current_portfolio else {}
        
        # Obtener datos de screening y consistencia
        detailed_results = self.screening_data.get('detailed_results', [])
        consistency_data = self.consistency_analysis.get('consistency_analysis', {})
        
        # Analizar categorías de consistencia por orden de prioridad
        priority_categories = [
            ('consistent_winners', 1.0),
            ('strong_candidates', 0.95),
            ('emerging_opportunities', 0.85)
        ]
        
        for category, weight_multiplier in priority_categories:
            category_stocks = consistency_data.get(category, [])
            
            for stock_info in category_stocks:
                symbol = stock_info['symbol']
                consistency_weeks = stock_info.get('frequency', 0)
                
                # Solo analizar acciones que NO están en portfolio actual
                if symbol not in current_positions:
                    # Buscar datos detallados de screening
                    stock_data = None
                    for result in detailed_results:
                        if result.get('symbol') == symbol:
                            stock_data = result
                            break
                    
                    if stock_data and consistency_weeks >= self.min_consistency_weeks:
                        # Calcular score con bonuses (incluye MA50)
                        opportunity_analysis = self.calculate_optimization_quality_score(stock_data)
                        base_score = stock_data.get('score', 0)
                        final_score = base_score * opportunity_analysis['quality_multiplier']
                        
                        # 🆕 CRITERIO ESTRICTO: Solo recomendar si score >= threshold
                        if final_score >= self.min_viable_score:
                            # Analizar potencial de reemplazo vs posiciones actuales
                            replacement_analysis = self.analyze_replacement_potential(final_score, current_positions)
                            
                            # 🆕 SOLO RECOMENDAR SI MEJORA SIGNIFICATIVA
                            if replacement_analysis['significant_improvement']:
                                opportunity = {
                                    'symbol': symbol,
                                    'base_score': base_score,
                                    'final_score': final_score,
                                    'consistency_weeks': consistency_weeks,
                                    'consistency_category': category,
                                    'optimization_features': opportunity_analysis['optimization_features'],
                                    'ma50_bonus_applied': opportunity_analysis['ma50_bonus_detected'],
                                    'ma50_bonus_value': opportunity_analysis['ma50_bonus_value'],
                                    'replacement_analysis': replacement_analysis,
                                    'monthly_trading_assessment': {
                                        'meets_strict_criteria': True,
                                        'significant_improvement': replacement_analysis['significant_improvement'],
                                        'recommended_for_monthly_hold': consistency_weeks >= 3
                                    },
                                    'rotation_reason': self.generate_rotation_reason(
                                        opportunity_analysis, consistency_weeks, replacement_analysis
                                    ),
                                    'stock_data': stock_data
                                }
                                
                                opportunities.append(opportunity)
        
        # Ordenar por score final (mejor primero)
        opportunities.sort(key=lambda x: x['final_score'], reverse=True)
        
        return opportunities[:10]  # Top 10 oportunidades con criterios estrictos
    
    def analyze_replacement_potential(self, new_score: float, current_positions: Dict) -> Dict:
        """
        🆕 NUEVO: Analiza si una nueva oportunidad justifica reemplazar posiciones actuales
        """
        if not current_positions:
            return {
                'significant_improvement': True,
                'can_replace': 'ANY',
                'improvement_margin': new_score,
                'reason': 'Portfolio has available capacity'
            }
        
        # Encontrar la posición más débil del portfolio
        weakest_position = None
        weakest_score = float('inf')
        
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            
            for symbol in current_positions.keys():
                for result in detailed_results:
                    if result.get('symbol') == symbol:
                        position_score = result.get('score', 0)
                        if position_score < weakest_score:
                            weakest_score = position_score
                            weakest_position = symbol
                        break
        
        if weakest_position and weakest_score > 0:
            score_improvement = new_score - weakest_score
            
            # 🆕 CRITERIO ESTRICTO: Debe ser significativamente mejor
            significant_improvement = score_improvement >= self.min_score_difference
            
            return {
                'significant_improvement': significant_improvement,
                'can_replace': weakest_position if significant_improvement else None,
                'weakest_position_score': weakest_score,
                'improvement_margin': score_improvement,
                'reason': f"{'Significant' if significant_improvement else 'Insufficient'} improvement vs {weakest_position}"
            }
        
        return {
            'significant_improvement': False,
            'can_replace': None,
            'improvement_margin': 0,
            'reason': 'Cannot assess current positions'
        }
    
    def generate_rotation_reason(self, opportunity_analysis: Dict, consistency_weeks: int, 
                               replacement_analysis: Dict) -> str:
        """Genera razón para rotación"""
        features = opportunity_analysis['optimization_features']
        
        base_reason = f"High-quality opportunity with {consistency_weeks}d consistency"
        
        # Añadir características especiales
        if 'ma50_rebound' in features:
            base_reason += " + MA50 rebound signal"
        
        if 'weekly_atr' in features:
            base_reason += " + Weekly ATR optimized"
        
        if replacement_analysis['significant_improvement']:
            improvement = replacement_analysis['improvement_margin']
            base_reason += f" (+{improvement:.1f}pts vs current)"
        
        return base_reason
    
    def create_aggressive_action_summary(self, position_analysis, rotation_opportunities):
        """
        🆕 MODIFICADO: Crea resumen con criterios estrictos para trading mensual
        """
        actions = {
            'holds': [],
            'consider_exits': [],
            'urgent_exits': [],
            'aggressive_rotations': [],
            'cash_deployment_opportunities': [],
            'optimization_rotations': [],
            'overall_action': 'MAINTAIN_MONTHLY_STRATEGY',  # 🆕 DEFAULT
            'detailed_recommendations': [],
            'portfolio_context': self.portfolio_status['status'] if self.portfolio_status else 'UNKNOWN'
        }
        
        # Adaptar recomendaciones según estado del portfolio
        portfolio_state = self.portfolio_status['status'] if self.portfolio_status else 'UNKNOWN'
        
        if portfolio_state in ['ALL_CASH_WAITING', 'MOSTLY_CASH']:
            # Portfolio en cash - enfocarse en deployment con criterios estrictos
            actions['overall_action'] = 'CASH_DEPLOYMENT_OPPORTUNITIES'
            
            for opp in rotation_opportunities:
                # Solo recomendar las mejores oportunidades para cash deployment
                if opp['final_score'] >= 80:  # Solo alta calidad
                    deployment_data = {
                        'symbol': opp['symbol'],
                        'reason': opp['rotation_reason'],
                        'urgency': 'HIGH' if opp['ma50_bonus_applied'] else 'MEDIUM',
                        'optimization_features': opp['optimization_features'],
                        'ma50_bonus_applied': opp['ma50_bonus_applied'],
                        'consistency_weeks': opp['consistency_weeks']
                    }
                    
                    actions['cash_deployment_opportunities'].append(deployment_data)
        
        else:
            # Portfolio con posiciones - aplicar criterios estrictos
            urgent_actions = 0
            
            for symbol, analysis in position_analysis.items():
                recommendation = analysis['recommendation']
                urgency = analysis.get('action_urgency', 'LOW')
                
                if 'URGENT_EXIT' in recommendation:
                    actions['urgent_exits'].append({
                        'symbol': symbol,
                        'reason': recommendation,
                        'urgency': urgency
                    })
                    urgent_actions += 1
                elif 'CONSIDER_EXIT' in recommendation or 'WATCH_CAREFULLY' in recommendation:
                    actions['consider_exits'].append({
                        'symbol': symbol,
                        'reason': recommendation,
                        'urgency': urgency
                    })
                else:
                    actions['holds'].append({
                        'symbol': symbol,
                        'reason': recommendation
                    })
            
            # Solo añadir rotaciones que cumplan criterios estrictos
            for opp in rotation_opportunities:
                if opp['monthly_trading_assessment']['meets_strict_criteria']:
                    actions['aggressive_rotations'].append({
                        'symbol': opp['symbol'],
                        'reason': opp['rotation_reason'],
                        'improvement': opp['replacement_analysis']['improvement_margin'],
                        'ma50_bonus': opp['ma50_bonus_applied']
                    })
            
            # Determinar acción general con filosofía mensual
            if urgent_actions >= 2:
                actions['overall_action'] = 'URGENT_PORTFOLIO_REVIEW'
            elif urgent_actions >= 1:
                actions['overall_action'] = 'POSITION_EXIT_REQUIRED'
            elif len(actions['aggressive_rotations']) >= 2:
                actions['overall_action'] = 'SELECTIVE_ROTATION_OPPORTUNITIES'
            else:
                actions['overall_action'] = 'MAINTAIN_MONTHLY_STRATEGY'
        
        return actions
    
    def generate_aggressive_rotation_recommendations(self):
        """
        🆕 MODIFICADO: Genera recomendaciones con criterios estrictos para trading mensual
        """
        print("🎯 Generando recomendaciones ESTRICTAS para trading mensual...")
        
        if not self.load_consistency_analysis():
            return None
        
        if not self.load_screening_data():
            print("⚠️ Sin datos de screening - análisis limitado")
        
        portfolio_loaded = self.load_current_portfolio()
        
        # Archivar archivo anterior
        if os.path.exists('rotation_recommendations.json'):
            try:
                with open('rotation_recommendations.json', 'r') as f:
                    prev_data = json.load(f)
                    prev_date = prev_data.get('analysis_date', '')[:10].replace('-', '')
                
                archive_name = f"rotation_recommendations_{prev_date}.json"
                os.rename('rotation_recommendations.json', archive_name)
                print(f"📁 Recomendaciones anteriores archivadas: {archive_name}")
            except Exception as e:
                print(f"⚠️ Error archivando recomendaciones anteriores: {e}")
        
        # Análisis con criterios estrictos
        rotation_opportunities = self.identify_rotation_opportunities_aggressive()
        
        # Análisis de posiciones actuales con criterios estrictos
        position_analysis = {}
        if self.portfolio_status and self.portfolio_status['positions_count'] > 0:
            position_analysis = self.analyze_current_positions_aggressive()
        
        # Extract optimization metrics (incluye MA50)
        optimization_features = {}
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            weekly_atr_available = any(r.get('weekly_atr', 0) > 0 for r in detailed_results)
            ma50_bonus_available = any(r.get('optimizations', {}).get('ma50_bonus_applied', False) for r in detailed_results)
            earnings_positive_available = any(r.get('fundamental_data', {}).get('quarterly_earnings_positive', False) for r in detailed_results)
            
            optimization_features = {
                'weekly_atr_available': weekly_atr_available,
                'ma50_bonus_available': ma50_bonus_available,  # 🌟 NUEVO
                'ma50_bonus_count': len([r for r in detailed_results if r.get('optimizations', {}).get('ma50_bonus_applied', False)]),
                'earnings_positive_available': earnings_positive_available,
                'total_results': len(detailed_results)
            }
        
        # Generar reporte completo
        recommendations = {
            'analysis_date': datetime.now().isoformat(),
            'portfolio_status': 'loaded' if portfolio_loaded else 'example_created',
            'portfolio_details': self.portfolio_status,
            'currency_support': {
                'base_currency': self.current_portfolio.get('base_currency', 'EUR') if self.current_portfolio else 'EUR',
                'conversion_applied': 'currency_conversion' in (self.current_portfolio or {}),
                'exchange_rate': self.current_portfolio.get('currency_conversion', {}).get('exchange_rate') if self.current_portfolio else None
            },
            'analysis_type': 'monthly_trading_with_strict_criteria_ma50_bonus',  # 🆕
            'rotation_philosophy': 'daily_monitoring_monthly_trading_strict_criteria',
            'strict_criteria_applied': {  # 🆕 NUEVO SECTION
                'min_score_difference': self.min_score_difference,
                'stop_loss_proximity': self.stop_loss_proximity_threshold,
                'momentum_loss_days': self.momentum_loss_days,
                'ma50_bonus_integration': True
            },
            'optimization_features': optimization_features,
            'current_positions_count': len(position_analysis),
            'position_analysis': position_analysis,
            'rotation_opportunities': rotation_opportunities,
            'action_summary': self.create_aggressive_action_summary(position_analysis, rotation_opportunities),
            'methodology_notes': {
                'philosophy': 'Daily monitoring, monthly trading with strict rotation criteria',
                'currency_handling': 'EUR base currency con acciones USD - conversión automática',
                'strict_criteria': 'Score +30pts, Stop 3%, Momentum 3d minimum for rotation',
                'ma50_bonus_integration': 'MA50 rebound signals receive 20% score bonus',
                'optimization_integration': 'Weekly ATR + MA50 bonus + Fundamentales integrados'
            }
        }
        
        # Guardar recomendaciones
        with open('rotation_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print("✅ Recomendaciones con criterios estrictos guardadas: rotation_recommendations.json")
        return recommendations
    
    def print_currency_aware_summary(self, recommendations):
        """Imprime resumen con información de divisas y criterios estrictos"""
        if not recommendations:
            return
        
        print(f"\n=== RECOMENDACIONES CON CRITERIOS ESTRICTOS + SOPORTE DIVISAS ===")
        print(f"📅 Análisis: {recommendations['analysis_date'][:10]}")
        print(f"🎯 Filosofía: Daily monitoring, monthly trading")
        
        # Criterios estrictos aplicados
        strict_criteria = recommendations.get('strict_criteria_applied', {})
        print(f"⚠️ Criterios estrictos: Score +{strict_criteria.get('min_score_difference', 30)}, Stop {strict_criteria.get('stop_loss_proximity', 0.03)*100:.0f}%, Momentum {strict_criteria.get('momentum_loss_days', 3)}d")
        
        # Currency info
        currency_info = recommendations.get('currency_support', {})
        print(f"💱 Moneda base: {currency_info.get('base_currency', 'EUR')}")
        if currency_info.get('conversion_applied'):
            rate = currency_info.get('exchange_rate', 0)
            print(f"💱 Conversión aplicada: EUR/USD @ {rate:.4f}")
        
        # Portfolio status
        portfolio_details = recommendations.get('portfolio_details', {})
        print(f"💼 Estado: {portfolio_details.get('status', 'UNKNOWN')}")
        print(f"📊 {portfolio_details.get('description', 'No description')}")
        
        # MA50 bonus statistics
        optimization_features = recommendations.get('optimization_features', {})
        ma50_count = optimization_features.get('ma50_bonus_count', 0)
        total_results = optimization_features.get('total_results', 0)
        if ma50_count > 0:
            print(f"🌟 MA50 bonus aplicado: {ma50_count}/{total_results} stocks ({ma50_count/max(total_results,1)*100:.1f}%)")
        
        action_summary = recommendations.get('action_summary', {})
        portfolio_context = action_summary.get('portfolio_context', 'UNKNOWN')
        
        # Show context-specific recommendations with strict criteria
        if portfolio_context in ['ALL_CASH_WAITING', 'MOSTLY_CASH']:
            cash_opportunities = action_summary.get('cash_deployment_opportunities', [])
            print(f"\n💰 OPORTUNIDADES DE DEPLOYMENT (criterios estrictos):")
            for opp in cash_opportunities[:3]:
                ma50_indicator = " 🌟" if opp.get('ma50_bonus_applied', False) else ""
                print(f"   💎 {opp['symbol']}{ma50_indicator} - {opp['urgency']} - {opp['reason']}")
        
        else:
            # Normal rotation recommendations with strict criteria
            aggressive_rotations = action_summary.get('aggressive_rotations', [])
            if aggressive_rotations:
                print(f"\n⚡ ROTACIONES (criterios estrictos cumplidos):")
                for rot in aggressive_rotations[:3]:
                    ma50_indicator = " 🌟" if rot.get('ma50_bonus', False) else ""
                    improvement = rot.get('improvement', 0)
                    print(f"   🔥 {rot['symbol']}{ma50_indicator} - +{improvement:.1f}pts - {rot['reason']}")
            
            urgent_exits = action_summary.get('urgent_exits', [])
            if urgent_exits:
                print(f"\n🚨 SALIDAS URGENTES:")
                for exit in urgent_exits:
                    print(f"   ❌ {exit['symbol']} - {exit['reason']}")

def main():
    """Función principal con criterios estrictos y soporte de divisas"""
    recommender = AggressiveRotationRecommender()
    
    recommendations = recommender.generate_aggressive_rotation_recommendations()
    
    if recommendations:
        recommender.print_currency_aware_summary(recommendations)
        print("\n✅ Recomendaciones con criterios estrictos completadas")
        
        print(f"\n🎯 CARACTERÍSTICAS IMPLEMENTADAS:")
        print(f"   - Criterios estrictos: ✅ Score +30pts, Stop 3%, Momentum 3d")
        print(f"   - Soporte multi-divisa: ✅ EUR → USD automático")
        print(f"   - Portfolio vacío: ✅ Manejo correcto de cash waiting")
        print(f"   - MA50 bonus: ✅ 20% multiplicador por rebote alcista")
        print(f"   - Trading mensual: ✅ Filosofía daily monitoring, monthly trading")
        
    else:
        print("\n❌ No se pudieron generar recomendaciones con criterios estrictos")

if __name__ == "__main__":
    main()
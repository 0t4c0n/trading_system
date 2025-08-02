#!/usr/bin/env python3
"""
Monthly Trading Rotation Recommender
===================================

Sistema de recomendaciones optimizado para trades de ~1 mes con ejecución diaria.
Solo recomienda rotaciones cuando se cumplen criterios estrictos:

1. Posición cerca del stop loss (2-3% del stop)
2. Pérdida de momentum (3+ días sin aparecer en screening)  
3. Oportunidad 30+ puntos superior a posición actual
4. Deterioro fundamental de posiciones actuales

Filosofía: "Daily monitoring, monthly rotation"
"""

import json
import os
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class MonthlyTradingRecommender:
    def __init__(self):
        """Inicializar recomendador para trades mensuales con criterios estrictos"""
        
        # CRITERIOS ESTRICTOS PARA ROTACIÓN MENSUAL
        self.min_score_difference = 30.0  # Mínimo 30 puntos de diferencia para recomendar rotación
        self.stop_loss_proximity_threshold = 0.03  # 3% cerca del stop loss
        self.momentum_loss_days = 3  # 3+ días sin aparecer en screening
        self.min_consistency_weeks = 2  # Mínimo 2 semanas de consistencia
        
        # UMBRALES DE CALIDAD
        self.min_viable_score = 50.0  # Score mínimo para ser considerado viable
        self.excellent_score_threshold = 80.0  # Score excelente
        self.rotation_threshold = 0.15  # 15% mejor para considerar rotación
        
        # BONUS Y MULTIPLICADORES
        self.weekly_atr_bonus = 1.15  # 15% bonus por Weekly ATR
        self.ma50_bonus_multiplier = 1.20  # 20% bonus extra por MA50 stop loss
        self.strict_fundamentals_bonus = 1.10  # 10% bonus por fundamentales estrictos
        self.quality_stop_bonus = 1.05  # 5% bonus por stop loss de calidad
        
        # ESTADO INTERNO
        self.current_portfolio = None
        self.portfolio_status = None
        self.consistency_analysis = None
        self.screening_data = None
        
        print(f"🎯 Recomendador inicializado para TRADES MENSUALES")
        print(f"📊 Criterios estrictos: Score +{self.min_score_difference}, Stop {self.stop_loss_proximity_threshold*100}%, Momentum {self.momentum_loss_days}d")
    
    def load_current_portfolio(self):
        """Carga la cartera actual del usuario"""
        try:
            with open('current_portfolio.json', 'r') as f:
                self.current_portfolio = json.load(f)
            
            # Analizar estado del portfolio
            positions = self.current_portfolio.get('positions', {})
            cash = self.current_portfolio.get('cash', 0)
            
            if len(positions) == 0:
                portfolio_context = "ALL_CASH_WAITING"
                description = "Portfolio 100% cash - Esperando oportunidades de deployment"
            elif len(positions) <= 2:
                portfolio_context = "LIGHT_POSITIONS"
                description = f"Portfolio con {len(positions)} posiciones - Espacio para nuevas oportunidades"
            else:
                portfolio_context = "FULL_POSITIONS"
                description = f"Portfolio con {len(positions)} posiciones - Evaluar rotaciones"
            
            self.portfolio_status = {
                'positions_count': len(positions),
                'cash_available': cash,
                'context': portfolio_context,
                'description': description,
                'status': 'loaded'
            }
            
            print(f"📂 Portfolio loaded: {description}")
            return True
            
        except FileNotFoundError:
            print("⚠️ No se encontró current_portfolio.json - Creando archivo ejemplo")
            self.create_portfolio_example()
            return False
            
        except Exception as e:
            print(f"❌ Error cargando cartera: {e}")
            return False
    
    def create_portfolio_example(self):
        """Crea un archivo de ejemplo para portfolio"""
        example_portfolio = {
            "last_manual_update": datetime.now().isoformat(),
            "positions": {
                "AAPL": {
                    "shares": 50,
                    "entry_price": 150.25,
                    "entry_date": "2024-01-15T14:30:00Z",
                    "broker": "Interactive Brokers",
                    "notes": "Entrada tras breakout",
                    "target_hold_period": "1_month"
                }
            },
            "cash": 10000.00,
            "total_invested": 7500.00,
            "portfolio_summary": {
                "total_portfolio_value": 17500.00,
                "cash_percentage": 57.1,
                "invested_percentage": 42.9
            },
            "strategy": {
                "max_positions": 5,
                "target_hold_period": "1 month with daily monitoring",
                "risk_per_position": "10% máximo",
                "rotation_philosophy": "Monthly trades with strict rotation criteria"
            }
        }
        
        with open('current_portfolio.json', 'w') as f:
            json.dump(example_portfolio, f, indent=2)
        
        print("📝 Archivo current_portfolio.json creado - ¡Edítalo con tus posiciones reales!")
        
        # Configurar portfolio status para ejemplo
        self.portfolio_status = {
            'positions_count': 1,
            'cash_available': 10000.00,
            'context': 'EXAMPLE_CREATED',
            'description': 'Portfolio ejemplo creado - Configura tus posiciones reales',
            'status': 'example'
        }
    
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
    
    def check_position_near_stop_loss(self, symbol: str, current_price: float, entry_price: float) -> Tuple[bool, float, str]:
        """
        Verifica si una posición está cerca del stop loss
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
    
    def check_momentum_loss(self, symbol: str) -> Tuple[bool, int, str]:
        """
        Verifica si una acción ha perdido momentum (no aparece en screening por X días)
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
                # No aparece en screening actual - verificar historial
                historical_presence = self.check_historical_presence(symbol)
                
                if historical_presence >= self.momentum_loss_days:
                    return True, historical_presence, f"Ausente del screening por {historical_presence}+ días"
                else:
                    return False, historical_presence, f"Ausente solo {historical_presence} días"
            
            return False, 0, "Presente en screening actual"
            
        except Exception as e:
            return False, 0, f"Error verificando momentum: {e}"
    
    def check_historical_presence(self, symbol: str) -> int:
        """Verifica cuántos días consecutivos una acción ha estado ausente del screening"""
        # Esta es una función simplificada - en producción se podría 
        # verificar archivos históricos de screening
        try:
            # Simular verificación de archivos históricos
            import glob
            historical_files = glob.glob('weekly_screening_results_*.json')
            historical_files.sort(reverse=True)  # Más recientes primero
            
            days_absent = 0
            for i, file in enumerate(historical_files[:7]):  # Últimos 7 días
                try:
                    with open(file, 'r') as f:
                        historical_data = json.load(f)
                    
                    # Buscar símbolo en resultados históricos
                    top_symbols = historical_data.get('top_symbols', [])
                    if symbol not in top_symbols:
                        days_absent += 1
                    else:
                        break  # Encontrado, detener búsqueda
                        
                except Exception:
                    continue
            
            return days_absent
            
        except Exception:
            # Fallback: asumir ausente por 1 día si no hay datos históricos
            return 1
    
    def calculate_opportunity_score_with_bonuses(self, stock_data: Dict) -> float:
        """
        Calcula score de oportunidad con todos los bonuses aplicados
        Incluye bonus especial por MA50 stop loss
        """
        try:
            base_score = stock_data.get('score', 0)
            
            # Multiplicadores por optimizaciones
            multiplier = 1.0
            bonus_reasons = []
            
            # Bonus por Weekly ATR
            if stock_data.get('weekly_atr', 0) > 0:
                multiplier *= self.weekly_atr_bonus
                bonus_reasons.append(f"Weekly ATR (+{(self.weekly_atr_bonus-1)*100:.0f}%)")
            
            # Bonus especial por MA50 stop loss
            optimizations = stock_data.get('optimizations', {})
            if optimizations.get('ma50_bonus_applied', False):
                multiplier *= self.ma50_bonus_multiplier
                ma50_bonus_value = optimizations.get('ma50_bonus_value', 0)
                bonus_reasons.append(f"MA50 Rebound (+{ma50_bonus_value}pts + {(self.ma50_bonus_multiplier-1)*100:.0f}%)")
            
            # Bonus por fundamentales estrictos
            fundamental_data = stock_data.get('fundamental_data', {})
            if fundamental_data.get('quarterly_earnings_positive', False):
                multiplier *= self.strict_fundamentals_bonus
                bonus_reasons.append(f"Fundamentales (+{(self.strict_fundamentals_bonus-1)*100:.0f}%)")
            
            # Bonus por calidad del stop loss
            stop_analysis = stock_data.get('stop_analysis', {})
            if stop_analysis.get('stop_selection', '').startswith('ma'):
                multiplier *= self.quality_stop_bonus
                bonus_reasons.append(f"Quality Stop (+{(self.quality_stop_bonus-1)*100:.0f}%)")
            
            final_score = base_score * multiplier
            
            return {
                'base_score': base_score,
                'final_score': final_score,
                'multiplier_applied': multiplier,
                'bonus_reasons': bonus_reasons,
                'quality_tier': self.classify_opportunity_quality(final_score)
            }
            
        except Exception as e:
            return {
                'base_score': stock_data.get('score', 0),
                'final_score': stock_data.get('score', 0),
                'multiplier_applied': 1.0,
                'bonus_reasons': [],
                'quality_tier': 'UNKNOWN',
                'error': str(e)
            }
    
    def classify_opportunity_quality(self, score: float) -> str:
        """Clasifica la calidad de una oportunidad"""
        if score >= 90:
            return 'EXCEPTIONAL'
        elif score >= 75:
            return 'EXCELLENT'
        elif score >= 60:
            return 'GOOD'
        elif score >= 45:
            return 'AVERAGE'
        else:
            return 'POOR'
    
    def analyze_current_positions_for_monthly_trading(self):
        """
        Analiza posiciones actuales con criterios estrictos para trading mensual
        Solo recomienda cambios en casos críticos
        """
        if not self.current_portfolio or not self.screening_data:
            return {}
        
        current_positions = self.current_portfolio.get('positions', {})
        if not current_positions:
            return {}
        
        position_analysis = {}
        
        for symbol, position_data in current_positions.items():
            try:
                entry_price = position_data.get('entry_price', 0)
                entry_date = position_data.get('entry_date', '')
                shares = position_data.get('shares', 0)
                
                # Buscar precio actual en screening data
                current_price = self.get_current_price_from_screening(symbol)
                if not current_price:
                    current_price = entry_price  # Fallback
                
                # CRITERIO 1: Verificar proximidad al stop loss
                near_stop, stop_distance, stop_reason = self.check_position_near_stop_loss(
                    symbol, current_price, entry_price
                )
                
                # CRITERIO 2: Verificar pérdida de momentum
                momentum_lost, days_absent, momentum_reason = self.check_momentum_loss(symbol)
                
                # CRITERIO 3: Verificar deterioro fundamental (simplificado)
                fundamental_deterioration = self.check_fundamental_deterioration(symbol)
                
                # Calcular P&L actual
                current_pnl = ((current_price - entry_price) / entry_price) * 100
                
                # DETERMINAR RECOMENDACIÓN CON CRITERIOS ESTRICTOS
                recommendation = self.determine_position_recommendation(
                    near_stop, momentum_lost, fundamental_deterioration, current_pnl, days_absent
                )
                
                # Calcular urgencia
                urgency = self.calculate_action_urgency(near_stop, momentum_lost, fundamental_deterioration)
                
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
                    'fundamental_analysis': fundamental_deterioration,
                    'recommendation': recommendation,
                    'action_urgency': urgency,
                    'monthly_trading_assessment': {
                        'meets_exit_criteria': near_stop or momentum_lost or fundamental_deterioration['deteriorated'],
                        'action_required': urgency in ['URGENT', 'HIGH'],
                        'can_hold_monthly': not (near_stop or momentum_lost)
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
    
    def check_fundamental_deterioration(self, symbol: str) -> Dict:
        """Verifica deterioro fundamental (simplificado)"""
        try:
            # En una implementación completa, esto verificaría cambios fundamentales
            # Por ahora, retorna estado neutral
            return {
                'deteriorated': False,
                'reason': 'No deterioration detected',
                'severity': 'NONE'
            }
        except Exception as e:
            return {
                'deteriorated': False,
                'reason': f'Error checking fundamentals: {e}',
                'severity': 'UNKNOWN'
            }
    
    def determine_position_recommendation(self, near_stop: bool, momentum_lost: bool, 
                                        fundamental_deterioration: Dict, current_pnl: float, 
                                        days_absent: int) -> str:
        """
        Determina recomendación para posición con criterios estrictos de trading mensual
        """
        # CRITERIOS DE SALIDA URGENTE
        if near_stop and current_pnl < -5:
            return "URGENT_EXIT - Near stop loss with significant loss"
        
        if momentum_lost and days_absent >= 5:
            return "URGENT_EXIT - Lost momentum for 5+ days"
        
        if fundamental_deterioration.get('deteriorated', False) and fundamental_deterioration.get('severity') == 'HIGH':
            return "URGENT_EXIT - Fundamental deterioration"
        
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
    
    def calculate_action_urgency(self, near_stop: bool, momentum_lost: bool, 
                               fundamental_deterioration: Dict) -> str:
        """Calcula urgencia de acción"""
        if near_stop or fundamental_deterioration.get('severity') == 'HIGH':
            return 'URGENT'
        
        if momentum_lost:
            return 'HIGH'
        
        if fundamental_deterioration.get('deteriorated', False):
            return 'MEDIUM'
        
        return 'LOW'
    
    def identify_monthly_rotation_opportunities(self):
        """
        Identifica oportunidades de rotación con criterios estrictos para trading mensual
        Solo recomienda oportunidades superiores con alta convicción
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
            ('consistent_winners', 1.0),    # Máxima prioridad
            ('strong_candidates', 0.95),    # Alta prioridad  
            ('emerging_opportunities', 0.85) # Prioridad moderada (solo para casos excepcionales)
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
                        # Calcular score con bonuses
                        opportunity_analysis = self.calculate_opportunity_score_with_bonuses(stock_data)
                        final_score = opportunity_analysis['final_score']
                        
                        # CRITERIO ESTRICTO: Solo recomendar si score >= threshold
                        if final_score >= self.min_viable_score:
                            # Determinar urgencia basada en calidad y consistencia
                            urgency = self.determine_opportunity_urgency(
                                final_score, consistency_weeks, opportunity_analysis['quality_tier']
                            )
                            
                            # Calcular score de reemplazo vs posiciones actuales
                            replacement_analysis = self.analyze_replacement_potential(final_score, current_positions)
                            
                            opportunity = {
                                'symbol': symbol,
                                'base_score': opportunity_analysis['base_score'],
                                'final_score': final_score,
                                'quality_tier': opportunity_analysis['quality_tier'],
                                'consistency_weeks': consistency_weeks,
                                'consistency_category': category,
                                'urgency': urgency,
                                'bonus_reasons': opportunity_analysis['bonus_reasons'],
                                'multiplier_applied': opportunity_analysis['multiplier_applied'],
                                'replacement_analysis': replacement_analysis,
                                'monthly_trading_assessment': {
                                    'high_conviction': final_score >= self.excellent_score_threshold,
                                    'meets_rotation_criteria': replacement_analysis['significant_improvement'],
                                    'recommended_for_monthly_hold': consistency_weeks >= 3
                                },
                                'rotation_reason': self.generate_rotation_reason(
                                    opportunity_analysis, consistency_weeks, replacement_analysis
                                ),
                                'stock_data': stock_data  # Incluir datos completos para referencia
                            }
                            
                            opportunities.append(opportunity)
        
        # Ordenar por score final (mejor primero)
        opportunities.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Filtrar solo oportunidades que realmente justifican rotación
        filtered_opportunities = []
        for opp in opportunities:
            if (opp['monthly_trading_assessment']['meets_rotation_criteria'] or
                opp['quality_tier'] in ['EXCEPTIONAL', 'EXCELLENT']):
                filtered_opportunities.append(opp)
        
        return filtered_opportunities[:15]  # Top 15 oportunidades
    
    def determine_opportunity_urgency(self, score: float, consistency_weeks: int, quality_tier: str) -> str:
        """Determina urgencia de oportunidad"""
        if quality_tier == 'EXCEPTIONAL' and consistency_weeks >= 4:
            return 'URGENT'
        
        if quality_tier == 'EXCELLENT' and consistency_weeks >= 3:
            return 'HIGH'
        
        if score >= 70 and consistency_weeks >= 3:
            return 'MEDIUM'
        
        return 'LOW'
    
    def analyze_replacement_potential(self, new_score: float, current_positions: Dict) -> Dict:
        """
        Analiza si una nueva oportunidad justifica reemplazar posiciones actuales
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
            percentage_improvement = (score_improvement / weakest_score) * 100 if weakest_score > 0 else 0
            
            # CRITERIO ESTRICTO: Debe ser significativamente mejor
            significant_improvement = score_improvement >= self.min_score_difference
            
            return {
                'significant_improvement': significant_improvement,
                'can_replace': weakest_position if significant_improvement else None,
                'weakest_position_score': weakest_score,
                'improvement_margin': score_improvement,
                'improvement_percentage': percentage_improvement,
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
        quality = opportunity_analysis['quality_tier']
        bonus_count = len(opportunity_analysis['bonus_reasons'])
        
        base_reason = f"{quality} opportunity with {consistency_weeks}w consistency"
        
        if bonus_count > 0:
            base_reason += f" + {bonus_count} optimizations"
        
        if replacement_analysis['significant_improvement']:
            improvement = replacement_analysis['improvement_margin']
            base_reason += f" (+{improvement:.1f}pts vs current)"
        
        return base_reason
    
    def create_monthly_action_summary(self, position_analysis: Dict, rotation_opportunities: List):
        """
        Crea resumen de acciones con filosofía de trading mensual
        Solo recomienda acciones críticas o de alta convicción
        """
        actions = {
            'overall_action': 'MAINTAIN_MONTHLY_STRATEGY',
            'urgent_exits': [],
            'consider_exits': [],
            'holds': [],
            'rotation_opportunities': [],
            'high_conviction_adds': [],
            'detailed_recommendations': [],
            'monthly_trading_summary': {
                'positions_requiring_action': 0,
                'high_conviction_opportunities': 0,
                'rotation_recommendations': 0,
                'philosophy_status': 'ALIGNED'
            }
        }
        
        # Analizar posiciones actuales
        urgent_actions = 0
        
        for symbol, analysis in position_analysis.items():
            recommendation = analysis['recommendation']
            urgency = analysis.get('action_urgency', 'LOW')
            
            if 'URGENT_EXIT' in recommendation:
                actions['urgent_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation,
                    'urgency': urgency,
                    'pnl': analysis.get('current_pnl', 0)
                })
                urgent_actions += 1
                
            elif 'CONSIDER_EXIT' in recommendation:
                actions['consider_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation,
                    'urgency': urgency,
                    'pnl': analysis.get('current_pnl', 0)
                })
                
            elif 'WATCH_CAREFULLY' in recommendation:
                actions['consider_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation,
                    'urgency': urgency,
                    'pnl': analysis.get('current_pnl', 0)
                })
                
            else:
                actions['holds'].append({
                    'symbol': symbol,
                    'reason': recommendation,
                    'pnl': analysis.get('current_pnl', 0)
                })
        
        # Analizar oportunidades de rotación
        high_conviction_count = 0
        
        for opp in rotation_opportunities:
            urgency = opp.get('urgency', 'LOW')
            quality_tier = opp.get('quality_tier', 'UNKNOWN')
            
            if quality_tier in ['EXCEPTIONAL', 'EXCELLENT']:
                actions['high_conviction_adds'].append({
                    'symbol': opp['symbol'],
                    'score': opp['final_score'],
                    'quality': quality_tier,
                    'consistency': opp['consistency_weeks'],
                    'urgency': urgency,
                    'reason': opp['rotation_reason']
                })
                high_conviction_count += 1
            
            if opp['monthly_trading_assessment']['meets_rotation_criteria']:
                actions['rotation_opportunities'].append({
                    'symbol': opp['symbol'],
                    'score': opp['final_score'],
                    'improvement': opp['replacement_analysis']['improvement_margin'],
                    'reason': opp['rotation_reason'],
                    'urgency': urgency
                })
        
        # Determinar acción general con filosofía mensual
        if urgent_actions >= 2:
            actions['overall_action'] = 'URGENT_PORTFOLIO_REVIEW'
        elif urgent_actions >= 1:
            actions['overall_action'] = 'POSITION_EXIT_REQUIRED'
        elif high_conviction_count >= 2:
            actions['overall_action'] = 'HIGH_CONVICTION_OPPORTUNITIES_AVAILABLE'
        elif len(actions['rotation_opportunities']) > 0:
            actions['overall_action'] = 'CONSIDER_SELECTIVE_ROTATION'
        else:
            actions['overall_action'] = 'MAINTAIN_MONTHLY_STRATEGY'
        
        # Actualizar resumen mensual
        actions['monthly_trading_summary'] = {
            'positions_requiring_action': urgent_actions + len(actions['consider_exits']),
            'high_conviction_opportunities': high_conviction_count,
            'rotation_recommendations': len(actions['rotation_opportunities']),
            'philosophy_status': 'ALIGNED' if urgent_actions == 0 else 'REQUIRES_ATTENTION'
        }
        
        return actions
    
    def generate_monthly_trading_recommendations(self):
        """Genera recomendaciones completas para trading mensual"""
        print("🎯 Generando recomendaciones para TRADING MENSUAL...")
        
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
        
        # Análisis de posiciones actuales
        position_analysis = {}
        if self.portfolio_status and self.portfolio_status['positions_count'] > 0:
            position_analysis = self.analyze_current_positions_for_monthly_trading()
        
        # Identificar oportunidades de rotación
        rotation_opportunities = self.identify_monthly_rotation_opportunities()
        
        # Crear resumen de acciones
        action_summary = self.create_monthly_action_summary(position_analysis, rotation_opportunities)
        
        # Generar reporte completo
        recommendations = {
            'analysis_date': datetime.now().isoformat(),
            'portfolio_status': 'loaded' if portfolio_loaded else 'example_created',
            'portfolio_details': self.portfolio_status,
            'analysis_type': 'monthly_trading_conservative_with_strict_criteria',
            'rotation_philosophy': 'monthly_trades_daily_monitoring_strict_rotation',
            'strict_criteria_applied': {
                'min_score_difference': self.min_score_difference,
                'stop_loss_proximity': self.stop_loss_proximity_threshold,
                'momentum_loss_days': self.momentum_loss_days,
                'min_consistency_weeks': self.min_consistency_weeks
            },
            'current_positions_count': len(position_analysis),
            'position_analysis': position_analysis,
            'rotation_opportunities': rotation_opportunities[:10],  # Top 10
            'action_summary': action_summary,
            'monthly_trading_insights': {
                'total_opportunities_analyzed': len(rotation_opportunities),
                'high_conviction_opportunities': len(action_summary['high_conviction_adds']),
                'positions_requiring_immediate_action': len(action_summary['urgent_exits']),
                'alignment_with_monthly_strategy': action_summary['monthly_trading_summary']['philosophy_status']
            },
            'methodology_notes': {
                'philosophy': 'Monthly trading with daily monitoring - strict rotation criteria',
                'execution_frequency': 'Daily screening, monthly rotation mindset',
                'rotation_criteria': 'Only for significant opportunities or risk management',
                'score_threshold': f'Minimum {self.min_score_difference}pt improvement for rotation',
                'ma50_bonus_integration': 'Prioritizes MA50 stop loss with 20% bonus multiplier'
            }
        }
        
        # Guardar recomendaciones
        with open('rotation_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print("✅ Recomendaciones para trading mensual guardadas: rotation_recommendations.json")
        return recommendations
    
    def print_monthly_trading_summary(self, recommendations):
        """Imprime resumen para trading mensual"""
        if not recommendations:
            return
        
        action_summary = recommendations.get('action_summary', {})
        monthly_insights = recommendations.get('monthly_trading_insights', {})
        
        print(f"\n🎯 === RESUMEN TRADING MENSUAL ===")
        print(f"📅 Filosofía: Trades de ~1 mes con monitorización diaria")
        print(f"⚠️ Criterios estrictos: Score +{self.min_score_difference}, Stop {self.stop_loss_proximity_threshold*100}%, Momentum {self.momentum_loss_days}d")
        
        portfolio_details = recommendations.get('portfolio_details', {})
        print(f"\n💼 PORTFOLIO: {portfolio_details.get('description', 'Unknown')}")
        
        # Acciones urgentes
        urgent_exits = action_summary.get('urgent_exits', [])
        if urgent_exits:
            print(f"\n🚨 SALIDAS URGENTES ({len(urgent_exits)}):")
            for exit in urgent_exits:
                pnl = exit.get('pnl', 0)
                pnl_str = f"({pnl:+.1f}%)" if pnl != 0 else ""
                print(f"   ❌ {exit['symbol']} {pnl_str} - {exit['reason']}")
        
        # Consideraciones de salida
        consider_exits = action_summary.get('consider_exits', [])
        if consider_exits:
            print(f"\n⚠️ EVALUAR SALIDAS ({len(consider_exits)}):")
            for exit in consider_exits:
                pnl = exit.get('pnl', 0)
                pnl_str = f"({pnl:+.1f}%)" if pnl != 0 else ""
                print(f"   🔍 {exit['symbol']} {pnl_str} - {exit['reason']}")
        
        # Oportunidades de alta convicción
        high_conviction = action_summary.get('high_conviction_adds', [])
        if high_conviction:
            print(f"\n🌟 ALTA CONVICCIÓN ({len(high_conviction)}):")
            for opp in high_conviction[:3]:
                print(f"   💎 {opp['symbol']} - {opp['quality']} - {opp['consistency']}w - {opp['reason']}")
        
        # Mantener posiciones
        holds = action_summary.get('holds', [])
        if holds:
            print(f"\n✅ MANTENER ({len(holds)}):")
            for hold in holds[:3]:
                pnl = hold.get('pnl', 0)
                pnl_str = f"({pnl:+.1f}%)" if pnl != 0 else ""
                print(f"   🔒 {hold['symbol']} {pnl_str} - {hold['reason'][:50]}...")
        
        print(f"\n📊 ALINEACIÓN ESTRATÉGICA: {monthly_insights.get('alignment_with_monthly_strategy', 'Unknown')}")
        print(f"🎯 ACCIÓN GENERAL: {action_summary.get('overall_action', 'Unknown')}")

def main():
    """Función principal para recomendaciones de trading mensual"""
    recommender = MonthlyTradingRecommender()
    
    recommendations = recommender.generate_monthly_trading_recommendations()
    
    if recommendations:
        recommender.print_monthly_trading_summary(recommendations)
        print("\n✅ Recomendaciones para trading mensual completadas")
        
        print(f"\n🎯 CARACTERÍSTICAS IMPLEMENTADAS:")
        print(f"   - Criterios estrictos: ✅ Score +30pts, Stop 3%, Momentum 3d")
        print(f"   - Trading mensual: ✅ Filosofía de holds de ~1 mes")
        print(f"   - Monitorización diaria: ✅ Sin rotación excesiva")
        print(f"   - Bonus MA50: ✅ 20% multiplicador por rebote alcista")
        print(f"   - Gestión de riesgo: ✅ Criterios conservadores")
        
    else:
        print("\n❌ No se pudieron generar recomendaciones para trading mensual")

if __name__ == "__main__":
    main()
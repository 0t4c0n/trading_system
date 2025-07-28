#!/usr/bin/env python3
"""
Rotation Recommender Mejorado - Criterios avanzados más allá de la frecuencia
Incluye análisis de momentum, risk-adjusted returns, y scoring multifactorial
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math

class AdvancedRotationRecommender:
    def __init__(self):
        self.current_portfolio = None
        self.consistency_analysis = None
        self.screening_data = None
        
    def load_current_portfolio(self):
        """Carga la cartera actual del usuario"""
        try:
            with open('current_portfolio.json', 'r') as f:
                self.current_portfolio = json.load(f)
                
            current_positions = list(self.current_portfolio.get('positions', {}).keys())
            print(f"📂 Cartera actual: {len(current_positions)} posiciones - {current_positions}")
            return True
            
        except FileNotFoundError:
            print("⚠️ No se encontró current_portfolio.json - Creando archivo ejemplo")
            self.create_example_portfolio()
            return False
            
        except Exception as e:
            print(f"❌ Error cargando cartera: {e}")
            return False
    
    def create_example_portfolio(self):
        """Crea un archivo de ejemplo de cartera"""
        example_portfolio = {
            "positions": {
                "AAPL": {
                    "shares": 100,
                    "entry_price": 150.25,
                    "entry_date": "2024-01-15T14:30:00Z",
                    "broker": "Interactive Brokers",
                    "notes": "Entrada tras breakout"
                }
            },
            "cash": 10000.00,
            "last_manual_update": "2024-01-29T10:00:00Z",
            "notes": "Archivo de ejemplo - actualizar con posiciones reales"
        }
        
        with open('current_portfolio.json', 'w') as f:
            json.dump(example_portfolio, f, indent=2)
        
        print("✅ Creado current_portfolio.json de ejemplo")
    
    def load_consistency_analysis(self):
        """Carga el análisis de consistencia"""
        try:
            with open('consistency_analysis.json', 'r') as f:
                self.consistency_analysis = json.load(f)
                print("📊 Análisis de consistencia cargado")
                return True
                
        except FileNotFoundError:
            print("❌ No se encontró consistency_analysis.json")
            return False
            
        except Exception as e:
            print(f"❌ Error cargando análisis de consistencia: {e}")
            return False
    
    def load_screening_data(self):
        """Carga los datos detallados del screening"""
        try:
            with open('weekly_screening_results.json', 'r') as f:
                self.screening_data = json.load(f)
                print("📊 Datos de screening cargados")
                return True
                
        except FileNotFoundError:
            print("❌ No se encontró weekly_screening_results.json")
            return False
            
        except Exception as e:
            print(f"❌ Error cargando datos de screening: {e}")
            return False
    
    def calculate_advanced_score(self, symbol_info, screening_detail=None):
        """
        Calcula un score avanzado que va más allá de la frecuencia de aparición
        Incluye: momentum, risk-adjusted returns, technical strength, fundamentals
        """
        score = 0
        factors = {}
        
        # 1. FACTOR DE CONSISTENCIA (base - max 100 pts)
        frequency = symbol_info.get('frequency', 0)
        consistency_score = (frequency / 5) * 100
        score += consistency_score
        factors['consistency'] = consistency_score
        
        # 2. FACTOR DE MOMENTUM Y TRENDING (max 100 pts)
        weeks_appeared = symbol_info.get('weeks_appeared', [])
        if len(weeks_appeared) >= 2:
            # Bonus por apariciones consecutivas recientes
            recent_consecutive = 0
            for i in range(len(weeks_appeared) - 1, 0, -1):
                if weeks_appeared[i] == weeks_appeared[i-1] + 1:
                    recent_consecutive += 1
                else:
                    break
            
            momentum_score = min(recent_consecutive * 25, 100)  # 25 pts por semana consecutiva
            
            # Bonus si aparece en la semana más reciente
            if 5 in weeks_appeared:
                momentum_score += 20
            
            score += momentum_score
            factors['momentum'] = momentum_score
        
        # 3. FACTOR DE SCREENING QUALITY (max 150 pts)
        if screening_detail:
            # Score del screener (normalizado)
            raw_score = screening_detail.get('score', 0)
            normalized_score = min((raw_score / 400) * 100, 100)  # Normalizar a 100
            
            # Risk-adjusted return
            risk_pct = screening_detail.get('risk_pct', 15)
            outperformance_60d = screening_detail.get('outperformance_60d', 0)
            
            if risk_pct > 0:
                risk_adjusted_return = (outperformance_60d / risk_pct) * 10
                risk_adjusted_return = min(risk_adjusted_return, 50)  # Max 50 pts
            else:
                risk_adjusted_return = 0
            
            screening_quality = normalized_score + risk_adjusted_return
            score += screening_quality
            factors['screening_quality'] = screening_quality
        
        # 4. FACTOR FUNDAMENTAL (max 50 pts)
        fundamental_score = screening_detail.get('fundamental_score', 0) if screening_detail else 0
        # Normalizar fundamental score (0-100 -> 0-50)
        normalized_fundamental = min(fundamental_score * 0.5, 50)
        score += normalized_fundamental
        factors['fundamentals'] = normalized_fundamental
        
        # 5. FACTOR DE MARKET STRENGTH (max 50 pts)
        if screening_detail:
            outperformance_20d = screening_detail.get('outperformance_20d', 0)
            outperformance_90d = screening_detail.get('outperformance_90d', 0)
            
            # Media ponderada de outperformances (más peso a 60d)
            weighted_outperf = (outperformance_20d * 0.3 + 
                               screening_detail.get('outperformance_60d', 0) * 0.5 +
                               outperformance_90d * 0.2)
            
            market_strength = min(weighted_outperf / 2, 50)  # Normalizar a 50 pts max
            score += market_strength
            factors['market_strength'] = market_strength
        
        return {
            'total_score': score,
            'factors': factors,
            'max_possible': 450  # Máximo teórico
        }
    
    def calculate_position_health(self, symbol, position_data, consistency_info, screening_detail):
        """
        Calcula la 'salud' de una posición existente
        Considera: consistencia reciente, performance vs entrada, deterioro técnico
        """
        health_score = 100  # Empezar con salud perfecta
        warnings = []
        
        # 1. Deterioro de consistencia
        weeks_appeared = consistency_info.get('weeks_appeared', [])
        appeared_this_week = consistency_info.get('appeared_this_week', False)
        
        if not appeared_this_week:
            weeks_absent = 5 - max(weeks_appeared) if weeks_appeared else 5
            if weeks_absent >= 3:
                health_score -= 50
                warnings.append(f"Ausente {weeks_absent} semanas consecutivas")
            elif weeks_absent >= 2:
                health_score -= 30
                warnings.append(f"Ausente {weeks_absent} semanas - vigilar")
            else:
                health_score -= 15
                warnings.append("No aparece esta semana")
        
        # 2. Performance vs precio de entrada
        if screening_detail and position_data:
            current_price = screening_detail.get('current_price', 0)
            entry_price = position_data.get('entry_price', 0)
            
            if current_price > 0 and entry_price > 0:
                performance = ((current_price / entry_price) - 1) * 100
                
                if performance < -15:  # Pérdida > 15%
                    health_score -= 40
                    warnings.append(f"Pérdida del {performance:.1f}% vs entrada")
                elif performance < -8:  # Pérdida > 8%
                    health_score -= 20
                    warnings.append(f"Pérdida del {performance:.1f}% vs entrada")
                elif performance > 25:  # Ganancia > 25%
                    warnings.append(f"Ganancia del {performance:.1f}% - considerar take profit parcial")
        
        # 3. Deterioro técnico
        if screening_detail:
            risk_pct = screening_detail.get('risk_pct', 0)
            if risk_pct > 12:  # Riesgo alto
                health_score -= 25
                warnings.append(f"Riesgo elevado ({risk_pct:.1f}%)")
            
            outperformance_20d = screening_detail.get('outperformance_20d', 0)
            if outperformance_20d < 0:  # Underperformance reciente
                health_score -= 15
                warnings.append(f"Underperformance reciente ({outperformance_20d:.1f}%)")
        
        return {
            'health_score': max(health_score, 0),
            'warnings': warnings,
            'status': 'HEALTHY' if health_score > 70 else 'WARNING' if health_score > 40 else 'CRITICAL'
        }
    
    def calculate_take_profit_target(self, screening_detail):
        """
        Calcula target de take profit más sofisticado
        Basado en: volatilidad, momentum, resistencias técnicas, risk/reward
        """
        if not screening_detail:
            return None
        
        current_price = screening_detail.get('current_price', 0)
        if current_price <= 0:
            return None
        
        # Método 1: Basado en outperformance histórica proyectada
        outperf_60d = screening_detail.get('outperformance_60d', 0)
        
        if outperf_60d > 80:  # Performance excepcional
            base_target = current_price * 1.35  # 35% target
        elif outperf_60d > 50:  # Performance muy buena
            base_target = current_price * 1.25  # 25% target
        elif outperf_60d > 25:  # Performance buena
            base_target = current_price * 1.18  # 18% target
        else:  # Performance moderada
            base_target = current_price * 1.12  # 12% target conservador
        
        # Método 2: Basado en volatilidad (ATR implícito)
        risk_pct = screening_detail.get('risk_pct', 8)
        implied_atr = current_price * (risk_pct / 100) / 2  # Aproximar ATR
        volatility_target = current_price + (implied_atr * 4)  # 4x ATR
        
        # Método 3: Basado en scoring del sistema
        score = screening_detail.get('score', 0)
        if score > 350:
            score_multiplier = 1.08  # 8% extra para scores altos
        elif score > 250:
            score_multiplier = 1.05  # 5% extra
        else:
            score_multiplier = 1.02  # 2% extra básico
        
        # Combinar métodos (más conservador gana)
        combined_target = min(base_target, volatility_target) * score_multiplier
        
        # Asegurar risk/reward mínimo de 2:1
        stop_loss = screening_detail.get('stop_loss', current_price * 0.85)
        min_target_for_2to1 = current_price + (2 * (current_price - stop_loss))
        
        final_target = max(combined_target, min_target_for_2to1)
        
        return {
            'target_price': final_target,
            'upside_pct': ((final_target / current_price) - 1) * 100,
            'risk_reward_ratio': (final_target - current_price) / (current_price - stop_loss),
            'method_breakdown': {
                'base_target': base_target,
                'volatility_target': volatility_target,
                'score_adjusted': combined_target,
                'min_2to1': min_target_for_2to1
            }
        }
    
    def analyze_current_positions_advanced(self):
        """Análisis avanzado de posiciones actuales"""
        if not self.current_portfolio or not self.consistency_analysis:
            return {}
        
        current_positions = self.current_portfolio.get('positions', {})
        position_analysis = {}
        
        # Obtener datos detallados del screening
        screening_details = {}
        if self.screening_data:
            for result in self.screening_data.get('detailed_results', []):
                screening_details[result['symbol']] = result
        
        # Obtener análisis de consistencia
        all_analyzed_symbols = {}
        consistency_data = self.consistency_analysis['consistency_analysis']
        
        for category, symbols in consistency_data.items():
            for symbol_info in symbols:
                symbol = symbol_info['symbol']
                all_analyzed_symbols[symbol] = {
                    'category': category,
                    'info': symbol_info
                }
        
        # Analizar cada posición
        for symbol, position_data in current_positions.items():
            screening_detail = screening_details.get(symbol)
            consistency_info = all_analyzed_symbols.get(symbol, {}).get('info', {})
            
            if symbol in all_analyzed_symbols:
                # Calcular score avanzado
                advanced_score = self.calculate_advanced_score(consistency_info, screening_detail)
                
                # Calcular salud de la posición
                position_health = self.calculate_position_health(
                    symbol, position_data, consistency_info, screening_detail
                )
                
                # Calcular take profit target
                take_profit = self.calculate_take_profit_target(screening_detail)
                
                position_analysis[symbol] = {
                    'status': 'analyzed',
                    'category': all_analyzed_symbols[symbol]['category'],
                    'advanced_score': advanced_score,
                    'position_health': position_health,
                    'take_profit_analysis': take_profit,
                    'screening_detail': screening_detail,
                    'recommendation': self.get_advanced_position_recommendation(
                        advanced_score, position_health, consistency_info
                    )
                }
            else:
                # Posición no aparece en screening reciente
                position_analysis[symbol] = {
                    'status': 'not_in_screening',
                    'category': 'disappeared',
                    'advanced_score': {'total_score': 0, 'factors': {}},
                    'position_health': {
                        'health_score': 20,
                        'warnings': ['No aparece en screening reciente'],
                        'status': 'CRITICAL'
                    },
                    'recommendation': 'URGENT_EXIT - No aparece en análisis reciente'
                }
        
        return position_analysis
    
    def get_advanced_position_recommendation(self, advanced_score, position_health, consistency_info):
        """Recomendación basada en análisis avanzado"""
        total_score = advanced_score['total_score']
        health_score = position_health['health_score']
        appeared_this_week = consistency_info.get('appeared_this_week', False)
        
        # Crear recomendación detallada
        if health_score < 40:
            action = "URGENT_EXIT"
            reason = f"Salud crítica ({health_score:.0f}/100). " + "; ".join(position_health['warnings'])
        elif health_score < 70:
            if total_score > 200:
                action = "WATCH_CAREFULLY"
                reason = f"Salud en alerta ({health_score:.0f}/100) pero score alto ({total_score:.0f}). Vigilar evolución semanal."
            else:
                action = "CONSIDER_EXIT"
                reason = f"Salud deteriorada ({health_score:.0f}/100) y score bajo ({total_score:.0f})."
        else:
            if total_score > 300:
                action = "STRONG_HOLD"
                reason = f"Excelente salud ({health_score:.0f}/100) y score superior ({total_score:.0f}). Mantener con confianza."
            elif total_score > 200:
                action = "HOLD"
                reason = f"Buena salud ({health_score:.0f}/100) y score sólido ({total_score:.0f}). Mantener posición."
            else:
                action = "WATCH_CAREFULLY"
                reason = f"Salud aceptable ({health_score:.0f}/100) pero score moderado ({total_score:.0f}). Monitorear."
        
        # Añadir factores específicos
        factors = advanced_score.get('factors', {})
        if factors.get('momentum', 0) > 80:
            reason += " Momentum fuerte."
        elif factors.get('momentum', 0) < 30:
            reason += " Momentum débil."
        
        if not appeared_this_week and action in ['HOLD', 'STRONG_HOLD']:
            reason += " ATENCIÓN: No aparece esta semana."
        
        return f"{action} - {reason}"
    
    def identify_new_opportunities_advanced(self):
        """Identifica oportunidades con scoring avanzado"""
        if not self.consistency_analysis or not self.screening_data:
            return []
        
        current_positions = set(self.current_portfolio.get('positions', {}).keys()) if self.current_portfolio else set()
        new_opportunities = []
        
        # Crear mapping de screening details
        screening_details = {}
        for result in self.screening_data.get('detailed_results', []):
            screening_details[result['symbol']] = result
        
        # Analizar todas las categorías, no solo winners/candidates
        consistency_data = self.consistency_analysis['consistency_analysis']
        all_categories = ['consistent_winners', 'strong_candidates', 'emerging_opportunities']
        
        for category in all_categories:
            for symbol_info in consistency_data.get(category, []):
                symbol = symbol_info['symbol']
                
                # Solo recomendar si no la tenemos ya
                if symbol not in current_positions:
                    screening_detail = screening_details.get(symbol)
                    
                    # Calcular score avanzado
                    advanced_score = self.calculate_advanced_score(symbol_info, screening_detail)
                    
                    # Calcular take profit
                    take_profit = self.calculate_take_profit_target(screening_detail)
                    
                    # Determinar nivel de confianza basado en score total
                    total_score = advanced_score['total_score']
                    if total_score > 350:
                        confidence = 'VERY_HIGH'
                    elif total_score > 250:
                        confidence = 'HIGH'
                    elif total_score > 150:
                        confidence = 'MEDIUM'
                    else:
                        confidence = 'LOW'
                    
                    # Solo recomendar compras de MEDIUM o superior
                    if confidence in ['VERY_HIGH', 'HIGH', 'MEDIUM']:
                        opportunity = {
                            'symbol': symbol,
                            'category': category,
                            'confidence': confidence,
                            'advanced_score': advanced_score,
                            'take_profit_analysis': take_profit,
                            'screening_detail': screening_detail,
                            'reason': self.generate_opportunity_reason(symbol_info, advanced_score, screening_detail),
                            'appeared_this_week': symbol_info.get('appeared_this_week', False),
                            'target_hold': '2-3 meses'
                        }
                        
                        new_opportunities.append(opportunity)
        
        # Ordenar por score avanzado
        new_opportunities.sort(key=lambda x: x['advanced_score']['total_score'], reverse=True)
        
        return new_opportunities
    
    def generate_opportunity_reason(self, symbol_info, advanced_score, screening_detail):
        """Genera razón detallada para una oportunidad"""
        reasons = []
        
        # Consistencia
        frequency = symbol_info.get('frequency', 0)
        if frequency >= 4:
            reasons.append(f"Consistencia excepcional ({frequency}/5 semanas)")
        elif frequency >= 3:
            reasons.append(f"Consistencia sólida ({frequency}/5 semanas)")
        
        # Factors del scoring
        factors = advanced_score.get('factors', {})
        
        if factors.get('momentum', 0) > 80:
            reasons.append("momentum fuerte (apariciones consecutivas recientes)")
        
        if factors.get('screening_quality', 0) > 100:
            reasons.append("calidad técnica superior")
        
        if screening_detail:
            outperf = screening_detail.get('outperformance_60d', 0)
            if outperf > 50:
                reasons.append(f"outperformance excepcional vs SPY ({outperf:.1f}%)")
            elif outperf > 25:
                reasons.append(f"sólida outperformance vs SPY ({outperf:.1f}%)")
            
            risk = screening_detail.get('risk_pct', 0)
            if risk < 8:
                reasons.append(f"riesgo bajo ({risk:.1f}%)")
            
            fund_score = screening_detail.get('fundamental_score', 0)
            if fund_score > 40:
                reasons.append("fundamentales sólidos")
        
        if not reasons:
            reasons.append(f"Score avanzado: {advanced_score['total_score']:.0f}/450")
        
        return ". ".join(reasons).capitalize()
    
    def generate_rotation_recommendations(self):
        """Genera recomendaciones completas con análisis avanzado"""
        print("🎯 Generando recomendaciones avanzadas de rotación...")
        
        # Cargar todos los datos necesarios
        if not self.load_consistency_analysis():
            return None
        
        if not self.load_screening_data():
            print("⚠️ Sin datos de screening - análisis limitado")
        
        portfolio_loaded = self.load_current_portfolio()
        
        # Análisis avanzado
        position_analysis = self.analyze_current_positions_advanced()
        new_opportunities = self.identify_new_opportunities_advanced()
        watchlist = self.generate_advanced_watchlist()
        
        # Generar reporte completo
        recommendations = {
            'analysis_date': datetime.now().isoformat(),
            'portfolio_status': 'loaded' if portfolio_loaded else 'example_created',
            'analysis_type': 'advanced_multifactor',
            'current_positions_count': len(position_analysis),
            'position_analysis': position_analysis,
            'new_opportunities': new_opportunities[:10],
            'watchlist': watchlist[:15],
            'action_summary': self.create_advanced_action_summary(position_analysis, new_opportunities),
            'weekly_context': {
                'analysis_weeks': self.consistency_analysis.get('weeks_analyzed', 0),
                'total_symbols_analyzed': self.consistency_analysis['summary_stats']['total_unique_symbols'],
                'consistent_winners': self.consistency_analysis['summary_stats']['consistent_winners_count'],
                'strong_candidates': self.consistency_analysis['summary_stats']['strong_candidates_count']
            },
            'methodology_notes': {
                'scoring_factors': 'Consistencia (100pts) + Momentum (100pts) + Calidad técnica (150pts) + Fundamentales (50pts) + Fuerza mercado (50pts)',
                'position_health': 'Basado en consistencia reciente, performance vs entrada, deterioro técnico',
                'take_profit': 'Calculado via outperformance proyectada, volatilidad (ATR), y risk/reward mínimo 2:1'
            }
        }
        
        # Guardar recomendaciones
        with open('rotation_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print("✅ Recomendaciones avanzadas guardadas: rotation_recommendations.json")
        return recommendations
    
    def create_advanced_action_summary(self, position_analysis, new_opportunities):
        """Crea resumen avanzado de acciones"""
        actions = {
            'holds': [],
            'consider_exits': [],
            'urgent_exits': [],
            'strong_buys': [],
            'watch_buys': [],
            'overall_action': 'NO_ACTION',
            'detailed_recommendations': []  # Nuevo: recomendaciones detalladas
        }
        
        # Analizar posiciones actuales
        for symbol, analysis in position_analysis.items():
            recommendation = analysis['recommendation']
            health = analysis.get('position_health', {})
            take_profit = analysis.get('take_profit_analysis')
            screening = analysis.get('screening_detail')
            
            if 'STRONG_HOLD' in recommendation:
                actions['holds'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
                
                # Añadir recomendación detallada
                detailed = {
                    'symbol': symbol,
                    'action': 'STRONG_HOLD',
                    'reason': recommendation.split(' - ')[1] if ' - ' in recommendation else recommendation
                }
                if take_profit:
                    detailed.update({
                        'current_price': screening.get('current_price') if screening else None,
                        'take_profit': take_profit['target_price'],
                        'stop_loss': screening.get('stop_loss') if screening else None
                    })
                actions['detailed_recommendations'].append(detailed)
                
            elif 'HOLD' in recommendation and 'STRONG_HOLD' not in recommendation:
                actions['holds'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
                
            elif 'CONSIDER_EXIT' in recommendation or 'WATCH_CAREFULLY' in recommendation:
                actions['consider_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
                
                actions['detailed_recommendations'].append({
                    'symbol': symbol,
                    'action': 'CONSIDER_EXIT',
                    'reason': recommendation.split(' - ')[1] if ' - ' in recommendation else recommendation
                })
                
            elif 'URGENT_EXIT' in recommendation:
                actions['urgent_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
                
                actions['detailed_recommendations'].append({
                    'symbol': symbol,
                    'action': 'URGENT_EXIT',
                    'reason': recommendation.split(' - ')[1] if ' - ' in recommendation else recommendation
                })
        
        # Analizar nuevas oportunidades
        for opp in new_opportunities:
            take_profit = opp.get('take_profit_analysis')
            screening = opp.get('screening_detail')
            
            if opp['confidence'] == 'VERY_HIGH':
                actions['strong_buys'].append({
                    'symbol': opp['symbol'],
                    'reason': opp['reason'],
                    'price': screening.get('current_price') if screening else None,
                    'risk': screening.get('risk_pct') if screening else None
                })
                
                detailed = {
                    'symbol': opp['symbol'],
                    'action': 'STRONG_BUY',
                    'reason': opp['reason']
                }
                if take_profit and screening:
                    detailed.update({
                        'price': screening.get('current_price'),
                        'stop_loss': screening.get('stop_loss'),
                        'take_profit': take_profit['target_price'],
                        'risk_reward': f"{take_profit['risk_reward_ratio']:.1f}:1"
                    })
                actions['detailed_recommendations'].append(detailed)
                
            elif opp['confidence'] in ['HIGH', 'MEDIUM']:
                actions['watch_buys'].append({
                    'symbol': opp['symbol'],
                    'reason': opp['reason'],
                    'price': screening.get('current_price') if screening else None,
                    'risk': screening.get('risk_pct') if screening else None
                })
        
        # Determinar acción general
        if actions['urgent_exits'] or len(actions['strong_buys']) > 0:
            actions['overall_action'] = 'ACTION_REQUIRED'
        elif actions['consider_exits'] or len(actions['watch_buys']) > 0:
            actions['overall_action'] = 'EVALUATE_CHANGES'
        else:
            actions['overall_action'] = 'MAINTAIN_CURRENT'
        
        return actions
    
    def generate_advanced_watchlist(self):
        """Lista de vigilancia con criterios avanzados"""
        if not self.consistency_analysis:
            return []
        
        current_positions = set(self.current_portfolio.get('positions', {}).keys()) if self.current_portfolio else set()
        watchlist = []
        
        # Screening details
        screening_details = {}
        if self.screening_data:
            for result in self.screening_data.get('detailed_results', []):
                screening_details[result['symbol']] = result
        
        consistency_data = self.consistency_analysis['consistency_analysis']
        
        # Emerging opportunities con potencial
        for symbol_info in consistency_data.get('emerging_opportunities', []):
            symbol = symbol_info['symbol']
            
            if symbol not in current_positions:
                screening_detail = screening_details.get(symbol)
                advanced_score = self.calculate_advanced_score(symbol_info, screening_detail)
                
                # Solo incluir si tiene score decente
                if advanced_score['total_score'] > 100:
                    watchlist.append({
                        'symbol': symbol,
                        'reason': f"Emergiendo con score {advanced_score['total_score']:.0f}/450",
                        'frequency': f"{symbol_info['frequency']}/5 semanas",
                        'appeared_this_week': symbol_info.get('appeared_this_week', False),
                        'action': 'Si aparece próxima semana con score >200 → Considerar compra',
                        'advanced_score': advanced_score['total_score'],
                        'current_price': screening_detail.get('current_price') if screening_detail else None
                    })
        
        # Nuevos símbolos prometedores
        trend_changes = self.consistency_analysis.get('trend_changes', {})
        for symbol in trend_changes.get('newly_emerged', []):
            if symbol not in current_positions:
                screening_detail = screening_details.get(symbol)
                if screening_detail:
                    # Score rápido para nuevos
                    quick_score = screening_detail.get('score', 0) + screening_detail.get('outperformance_60d', 0)
                    
                    if quick_score > 150:  # Solo prometedores
                        watchlist.append({
                            'symbol': symbol,
                            'reason': f"Nueva aparición prometedora (score {quick_score:.0f})",
                            'frequency': '1/5 semanas (nuevo)',
                            'appeared_this_week': True,
                            'action': 'Vigilar 2-3 semanas para confirmar consistencia',
                            'advanced_score': quick_score,
                            'current_price': screening_detail.get('current_price')
                        })
        
        # Ordenar por score avanzado
        watchlist.sort(key=lambda x: x['advanced_score'], reverse=True)
        
        return watchlist
    
    def print_advanced_summary(self, recommendations):
        """Imprime resumen avanzado"""
        if not recommendations:
            return
        
        print(f"\n=== RECOMENDACIONES AVANZADAS DE ROTACIÓN ===")
        print(f"Análisis: {recommendations['analysis_date'][:10]}")
        print(f"Tipo: {recommendations['analysis_type']}")
        print(f"Posiciones actuales: {recommendations['current_positions_count']}")
        
        action_summary = recommendations['action_summary']
        print(f"Acción general: {action_summary['overall_action']}")
        
        # Mostrar recomendaciones detalladas
        detailed_recs = action_summary.get('detailed_recommendations', [])
        if detailed_recs:
            print(f"\n📋 RECOMENDACIONES DETALLADAS:")
            for rec in detailed_recs[:5]:
                print(f"\n🔹 {rec['symbol']} - {rec['action']}")
                print(f"   Razón: {rec['reason']}")
                if rec.get('price'):
                    print(f"   Precio: ${rec['price']:.2f}", end="")
                    if rec.get('stop_loss'):
                        print(f" | Stop: ${rec['stop_loss']:.2f}", end="")
                    if rec.get('take_profit'):
                        print(f" | Target: ${rec['take_profit']:.2f}", end="")
                    if rec.get('risk_reward'):
                        print(f" | R/R: {rec['risk_reward']}")
                    else:
                        print()
        
        # Nuevas oportunidades por scoring
        new_opps = recommendations.get('new_opportunities', [])
        if new_opps:
            print(f"\n🎯 TOP OPORTUNIDADES (por score avanzado):")
            for opp in new_opps[:3]:
                score = opp['advanced_score']['total_score']
                print(f"   {opp['symbol']} - Score: {score:.0f}/450 - {opp['confidence']} - {opp['reason']}")

def main():
    """Función principal"""
    recommender = AdvancedRotationRecommender()
    
    # Generar análisis avanzado completo
    recommendations = recommender.generate_rotation_recommendations()
    
    if recommendations:
        recommender.print_advanced_summary(recommendations)
        print("\n✅ Recomendaciones avanzadas completadas")
        
        # Mostrar metodología
        methodology = recommendations.get('methodology_notes', {})
        print(f"\n📊 METODOLOGÍA:")
        for key, value in methodology.items():
            print(f"   {key}: {value}")
    else:
        print("\n❌ No se pudieron generar recomendaciones avanzadas")

if __name__ == "__main__":
    main()
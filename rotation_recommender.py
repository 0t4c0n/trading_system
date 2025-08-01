#!/usr/bin/env python3
"""
Aggressive Rotation Recommender - UPDATED: Currency Support + Empty Portfolio Handling
🌍 Soporta portfolio en EUR con acciones en USD + conversión automática
💰 Manejo correcto de portfolio 100% cash vs portfolio que perdió momentum
🔧 Integra Weekly ATR + Stop Loss Restrictivo + Fundamentales Estrictos
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
        
        # Parámetros para rotación agresiva
        self.rotation_threshold = 0.20
        self.min_consistency_weeks = 2
        self.emerging_opportunity_weight = 1.5
        self.momentum_decay_threshold = 0.15
        self.fallback_avg_score = 100.0
        self.min_viable_score = 50.0
        
        # Optimizations integration
        self.weekly_atr_bonus = 1.15
        self.strict_fundamentals_bonus = 1.10
        self.quality_stop_bonus = 1.05
        
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
        # Crear dos ejemplos: uno con posiciones y otro 100% cash
        
        # Portfolio con posiciones (mixed)
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
                    "currency": "USD"
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
                "target_hold_period": "2-3 meses",
                "risk_per_position": "10% máximo",
                "objective": "Superar SPY con riesgo controlado"
            },
            "notes": "Portfolio multi-divisa: EUR base con acciones USD - EJEMPLO"
        }
        
        # Portfolio 100% cash
        all_cash_portfolio = {
            "base_currency": "EUR",
            "last_manual_update": datetime.now().isoformat(),
            "positions": {},  # ⚠️ SIN POSICIONES - 100% CASH
            "cash": 25000.00,  # EUR disponible
            "total_invested": 0.00,  # EUR - nada invertido
            "portfolio_summary": {
                "total_portfolio_value_eur": 25000.00,
                "cash_percentage": 100.0,
                "invested_percentage": 0.0
            },
            "strategy": {
                "max_positions": 5,
                "target_hold_period": "2-3 meses",
                "risk_per_position": "10% máximo",
                "objective": "Esperando oportunidades de momentum",
                "cash_deployment_plan": "Invertir progresivamente en top opportunities"
            },
            "notes": "Portfolio 100% cash - Esperando oportunidades - CAMBIAR POR TUS DATOS REALES"
        }
        
        # Save the all-cash example as default
        with open('current_portfolio.json', 'w') as f:
            json.dump(all_cash_portfolio, f, indent=2)
        
        # Also save mixed example for reference
        with open('current_portfolio_mixed_example.json', 'w') as f:
            json.dump(mixed_portfolio, f, indent=2)
        
        print("✅ Creados ejemplos de portfolio:")
        print("   - current_portfolio.json (100% cash)")
        print("   - current_portfolio_mixed_example.json (con posiciones)")
        print("💡 Edita current_portfolio.json con tus datos reales")
    
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
    
    def calculate_optimization_quality_score(self, screening_detail):
        """Calcula score de calidad basado en optimizaciones implementadas"""
        if not screening_detail:
            return {'quality_multiplier': 1.0, 'optimization_factors': []}
        
        quality_multiplier = 1.0
        optimization_factors = []
        
        # Weekly ATR Optimization Bonus
        weekly_atr = screening_detail.get('weekly_atr', 0)
        daily_atr = screening_detail.get('atr', 0)
        weekly_atr_optimized = screening_detail.get('weekly_atr_optimized', False)
        
        if weekly_atr_optimized and weekly_atr > 0:
            quality_multiplier *= self.weekly_atr_bonus
            optimization_factors.append('Weekly ATR')
            
            if daily_atr > 0:
                atr_ratio = weekly_atr / daily_atr
                if atr_ratio > 2.0:
                    quality_multiplier *= 1.05
                    optimization_factors.append(f'ATR ratio {atr_ratio:.1f}x')
        
        # Strict Fundamentals Bonus
        fundamental_data = screening_detail.get('fundamental_data', {})
        earnings_positive = fundamental_data.get('quarterly_earnings_positive', False)
        has_required_data = fundamental_data.get('has_required_data', False)
        
        if earnings_positive and has_required_data:
            quality_multiplier *= self.strict_fundamentals_bonus
            optimization_factors.append('Earnings+')
        
        # Quality Stop Loss Bonus
        stop_analysis = screening_detail.get('stop_analysis', {})
        stop_selection = stop_analysis.get('stop_selection', '')
        
        if 'ma50_priority' in stop_selection or 'ma21_priority' in stop_selection:
            quality_multiplier *= self.quality_stop_bonus
            optimization_factors.append(f'Quality Stop')
        elif 'descartar' in stop_selection:
            quality_multiplier *= 0.3  # Severe penalty
            optimization_factors.append('Poor Stop (marked for discard)')
        
        # Risk Management Quality
        risk_pct = screening_detail.get('risk_pct', 100)
        if risk_pct <= 6:
            quality_multiplier *= 1.08
            optimization_factors.append(f'Low Risk {risk_pct:.1f}%')
        elif risk_pct >= 15:
            quality_multiplier *= 0.5
            optimization_factors.append(f'High Risk {risk_pct:.1f}%')
        
        return {
            'quality_multiplier': quality_multiplier,
            'optimization_factors': optimization_factors,
            'weekly_atr_optimized': weekly_atr_optimized,
            'earnings_positive': earnings_positive,
            'stop_quality': stop_selection,
            'risk_level': 'LOW' if risk_pct <= 6 else 'HIGH' if risk_pct >= 10 else 'MEDIUM'
        }
    
    def identify_rotation_opportunities_aggressive(self):
        """
        🆕 IDENTIFICA OPORTUNIDADES con manejo correcto de portfolio vacío/cash
        """
        if not self.consistency_analysis or not self.screening_data:
            return []
        
        rotation_opportunities = []
        
        # 🌍 NUEVO: Manejo inteligente según estado del portfolio
        if not self.portfolio_status:
            print("⚠️ Portfolio status no determinado")
            return []
        
        portfolio_state = self.portfolio_status['status']
        current_positions = set(self.current_portfolio.get('positions', {}).keys()) if self.current_portfolio else set()
        
        print(f"💼 Portfolio State: {portfolio_state}")
        print(f"📊 Description: {self.portfolio_status['description']}")
        
        # Obtener scores y configurar lógica según estado del portfolio
        screening_details = {}
        current_position_scores = {}
        
        for result in self.screening_data.get('detailed_results', []):
            screening_details[result['symbol']] = result
            if result['symbol'] in current_positions:
                current_score = result.get('score', 0)
                optimization_quality = self.calculate_optimization_quality_score(result)
                adjusted_current_score = current_score * optimization_quality['quality_multiplier']
                current_position_scores[result['symbol']] = adjusted_current_score
        
        # 🌍 LÓGICA ADAPTADA según estado del portfolio
        if portfolio_state in ['ALL_CASH_WAITING', 'MOSTLY_CASH', 'EMPTY_PORTFOLIO']:
            # Portfolio esperando oportunidades - criterios más flexibles
            avg_current_score = self.min_viable_score  # Usar mínimo viable
            min_score_for_rotation = self.min_viable_score
            portfolio_context = "CASH_DEPLOYMENT"
            
            print(f"💰 Portfolio en cash - Buscando oportunidades de deployment")
            print(f"🎯 Score mínimo para inversión: {min_score_for_rotation:.1f}")
            
        elif portfolio_state == 'INVESTED':
            # Portfolio con posiciones - lógica normal de rotación
            if current_position_scores:
                avg_current_score = sum(current_position_scores.values()) / len(current_position_scores)
                min_score_for_rotation = avg_current_score * (1 + self.rotation_threshold)
                portfolio_context = "ROTATION_OPTIMIZATION"
                
                print(f"📊 Portfolio invertido - Score promedio: {avg_current_score:.1f}")
                print(f"🎯 Score mínimo para rotación: {min_score_for_rotation:.1f}")
            else:
                # Posiciones perdieron momentum
                avg_current_score = self.fallback_avg_score
                min_score_for_rotation = self.min_viable_score
                portfolio_context = "MOMENTUM_RECOVERY"
                
                print(f"🚨 Posiciones perdieron momentum - Modo recovery")
        else:
            # Estado desconocido - usar valores por defecto
            avg_current_score = self.fallback_avg_score
            min_score_for_rotation = self.min_viable_score
            portfolio_context = "DEFAULT_ANALYSIS"
        
        # Analizar oportunidades
        consistency_data = self.consistency_analysis['consistency_analysis']
        priority_categories = [
            ('consistent_winners', 1.0),
            ('strong_candidates', 0.9),
            ('emerging_opportunities', 1.2)
        ]
        
        for category, weight_multiplier in priority_categories:
            for symbol_info in consistency_data.get(category, []):
                symbol = symbol_info['symbol']
                
                # Solo analizar nuevas oportunidades (no posiciones actuales)
                if symbol not in current_positions:
                    screening_detail = screening_details.get(symbol)
                    
                    if screening_detail:
                        current_score = screening_detail.get('score', 0)
                        optimization_quality = self.calculate_optimization_quality_score(screening_detail)
                        optimization_multiplier = optimization_quality['quality_multiplier']
                        total_multiplier = weight_multiplier * optimization_multiplier
                        adjusted_score = current_score * total_multiplier
                        
                        should_recommend = False
                        recommendation_reason = ""
                        
                        # 🌍 CRITERIOS ADAPTADOS según contexto del portfolio
                        if portfolio_context == "CASH_DEPLOYMENT":
                            # Portfolio en cash - criterios para deployment inicial
                            if (adjusted_score >= min_score_for_rotation and 
                                symbol_info.get('frequency', 0) >= self.min_consistency_weeks):
                                should_recommend = True
                                opt_text = f" + optimizations ({', '.join(optimization_quality['optimization_factors'])})" if optimization_quality['optimization_factors'] else ""
                                recommendation_reason = f"Cash deployment opportunity - Score {adjusted_score:.1f}{opt_text}"
                            
                        elif portfolio_context == "ROTATION_OPTIMIZATION":
                            # Portfolio normal - lógica de rotación estándar
                            if adjusted_score >= min_score_for_rotation:
                                should_recommend = True
                                percentage_superior = ((adjusted_score/avg_current_score-1)*100)
                                recommendation_reason = f"Score {adjusted_score:.1f} es {percentage_superior:+.1f}% superior"
                            
                        elif portfolio_context == "MOMENTUM_RECOVERY":
                            # Portfolio perdió momentum - criterios de recovery
                            if (adjusted_score >= self.min_viable_score and 
                                symbol_info.get('frequency', 0) >= self.min_consistency_weeks):
                                should_recommend = True
                                recommendation_reason = f"Momentum recovery opportunity - Score {adjusted_score:.1f}"
                        
                        # Criterios adicionales independientes del contexto
                        momentum_strength_score = self.calculate_momentum_strength_score(symbol_info, screening_detail)
                        
                        if not should_recommend and momentum_strength_score['momentum_category'] == 'EXCEPTIONAL':
                            should_recommend = True
                            recommendation_reason = f"Momentum excepcional emergente"
                        
                        if should_recommend:
                            urgency = 'HIGH'
                            if momentum_strength_score['momentum_category'] == 'EXCEPTIONAL':
                                urgency = 'URGENT'
                            elif optimization_quality['quality_multiplier'] > 1.2:
                                urgency = 'URGENT'
                            
                            # Para portfolio en cash, determinar qué % del cash usar
                            recommended_allocation = None
                            if portfolio_context == "CASH_DEPLOYMENT":
                                cash_available = self.portfolio_status.get('cash_usd', 0)
                                if cash_available > 0:
                                    # Sugerir 20% del cash para primera posición, menos para siguientes
                                    recommended_allocation = min(cash_available * 0.2, 5000)  # Max $5k per position initially
                            
                            opportunity = {
                                'symbol': symbol,
                                'category': category,
                                'current_score': current_score,
                                'adjusted_score': adjusted_score,
                                'optimization_quality': optimization_quality,
                                'momentum_strength': momentum_strength_score,
                                'rotation_reason': recommendation_reason,
                                'urgency': urgency,
                                'consistency_weeks': symbol_info.get('frequency', 0),
                                'appeared_this_week': symbol_info.get('appeared_this_week', False),
                                'screening_detail': screening_detail,
                                'portfolio_context': portfolio_context,
                                'recommended_allocation_usd': recommended_allocation,
                                'optimization_features': optimization_quality['optimization_factors']
                            }
                            
                            rotation_opportunities.append(opportunity)
        
        # Ordenar por score ajustado y urgencia
        rotation_opportunities.sort(key=lambda x: (
            x['urgency'] == 'URGENT',
            x['urgency'] == 'HIGH',
            x['adjusted_score']
        ), reverse=True)
        
        print(f"🎯 Oportunidades identificadas: {len(rotation_opportunities)} ({portfolio_context})")
        return rotation_opportunities
    
    def calculate_momentum_strength_score(self, symbol_info, screening_detail=None):
        """Score de fuerza de momentum para rotación agresiva"""
        score = 0
        factors = {}
        
        frequency = symbol_info.get('frequency', 0)
        weeks_appeared = symbol_info.get('weeks_appeared', [])
        appeared_this_week = symbol_info.get('appeared_this_week', False)
        
        if appeared_this_week:
            recent_momentum_score = frequency * 25
            if frequency >= 3:
                recent_momentum_score += 20
            elif frequency >= 2:
                recent_momentum_score += 15
        else:
            recent_momentum_score = max(frequency * 15 - 20, 0)
        
        score += recent_momentum_score
        factors['recent_momentum'] = recent_momentum_score
        
        if screening_detail:
            raw_score = screening_detail.get('score', 0)
            technical_quality = min(raw_score / 200 * 100, 100)
            
            optimization_quality = self.calculate_optimization_quality_score(screening_detail)
            technical_quality *= optimization_quality['quality_multiplier']
            factors['optimization_quality'] = optimization_quality
            
            rr_ratio = screening_detail.get('risk_reward_ratio', 0)
            if rr_ratio > 4.0:
                technical_quality += 20
            elif rr_ratio > 3.0:
                technical_quality += 10
            
            momentum_20d = screening_detail.get('outperformance_20d', 0)
            if momentum_20d > 15:
                technical_quality += 15
            elif momentum_20d > 10:
                technical_quality += 8
            
            score += technical_quality
            factors['technical_quality'] = technical_quality
        
        momentum_category = 'EXCEPTIONAL' if score > 200 else 'STRONG' if score > 150 else 'MODERATE' if score > 100 else 'WEAK' if score > 50 else 'POOR'
        
        return {
            'total_score': score,
            'factors': factors,
            'momentum_category': momentum_category,
            'optimization_applied': screening_detail.get('weekly_atr_optimized', False) if screening_detail else False
        }
    
    def create_aggressive_action_summary(self, position_analysis, rotation_opportunities):
        """Crea resumen de acciones adaptado al estado del portfolio"""
        actions = {
            'holds': [],
            'consider_exits': [],
            'urgent_exits': [],
            'aggressive_rotations': [],
            'cash_deployment_opportunities': [],  # 🌍 NUEVO
            'optimization_rotations': [],
            'overall_action': 'NO_ACTION',
            'detailed_recommendations': [],
            'portfolio_context': self.portfolio_status['status'] if self.portfolio_status else 'UNKNOWN'
        }
        
        # Adaptar recomendaciones según estado del portfolio
        portfolio_state = self.portfolio_status['status'] if self.portfolio_status else 'UNKNOWN'
        
        if portfolio_state in ['ALL_CASH_WAITING', 'MOSTLY_CASH']:
            # Portfolio en cash - enfocarse en deployment
            actions['overall_action'] = 'CASH_DEPLOYMENT_OPPORTUNITIES'
            
            for opp in rotation_opportunities:
                deployment_data = {
                    'symbol': opp['symbol'],
                    'reason': opp['rotation_reason'],
                    'urgency': opp['urgency'],
                    'momentum_category': opp['momentum_strength']['momentum_category'],
                    'optimization_features': opp.get('optimization_features', []),
                    'recommended_allocation_usd': opp.get('recommended_allocation_usd'),
                    'consistency_weeks': opp['consistency_weeks']
                }
                
                actions['cash_deployment_opportunities'].append(deployment_data)
                
                # También añadir a detailed recommendations
                actions['detailed_recommendations'].append({
                    'symbol': opp['symbol'],
                    'action': f"CASH_DEPLOYMENT_{opp['urgency']}",
                    'reason': opp['rotation_reason'],
                    'urgency': opp['urgency'],
                    'allocation_usd': opp.get('recommended_allocation_usd'),
                    'optimization_features': opp.get('optimization_features', [])
                })
        
        else:
            # Portfolio con posiciones - lógica normal de rotación/exits
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
            
            # Añadir oportunidades de rotación
            for opp in rotation_opportunities:
                urgency = opp.get('urgency', 'MEDIUM')
                
                if urgency in ['URGENT', 'HIGH']:
                    actions['aggressive_rotations'].append({
                        'symbol': opp['symbol'],
                        'reason': opp['rotation_reason'],
                        'urgency': urgency
                    })
            
            # Determinar acción general
            if urgent_actions >= 2:
                actions['overall_action'] = 'URGENT_PORTFOLIO_ROTATION'
            elif urgent_actions >= 1 or len(actions['aggressive_rotations']) > 0:
                actions['overall_action'] = 'AGGRESSIVE_ROTATION_REQUIRED'
            elif len(actions['consider_exits']) > 0:
                actions['overall_action'] = 'EVALUATE_MOMENTUM_OPPORTUNITIES'
            else:
                actions['overall_action'] = 'MAINTAIN_WITH_VIGILANCE'
        
        return actions
    
    def generate_aggressive_rotation_recommendations(self):
        """Genera recomendaciones completas con soporte de divisas y portfolio vacío"""
        print("🎯 Generando recomendaciones AGRESIVAS con soporte de divisas + portfolio vacío...")
        
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
        
        # Análisis adaptado
        rotation_opportunities = self.identify_rotation_opportunities_aggressive()
        
        # Para portfolio con posiciones, analizar posiciones actuales
        position_analysis = {}
        if self.portfolio_status and self.portfolio_status['positions_count'] > 0:
            position_analysis = self.analyze_current_positions_aggressive()
        
        # Extract optimization metrics
        optimization_features = {}
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            weekly_atr_available = any(r.get('weekly_atr', 0) > 0 for r in detailed_results)
            weekly_atr_optimized = any(r.get('weekly_atr_optimized', False) for r in detailed_results)
            earnings_positive_available = any(r.get('fundamental_data', {}).get('quarterly_earnings_positive', False) for r in detailed_results)
            
            optimization_features = {
                'weekly_atr_available': weekly_atr_available,
                'weekly_atr_optimized': weekly_atr_optimized,
                'earnings_positive_available': earnings_positive_available,
                'total_results': len(detailed_results),
                'optimization_count': sum([weekly_atr_optimized, earnings_positive_available])
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
            'analysis_type': 'aggressive_momentum_responsive_with_currency_support',
            'rotation_philosophy': 'swing_for_fences_monthly_rotation_currency_aware',
            'optimization_features': optimization_features,
            'current_positions_count': len(position_analysis),
            'position_analysis': position_analysis,
            'rotation_opportunities': rotation_opportunities[:15],
            'action_summary': self.create_aggressive_action_summary(position_analysis, rotation_opportunities),
            'methodology_notes': {
                'philosophy': 'Momentum trading agresivo con soporte multi-divisa y manejo de portfolio vacío',
                'currency_handling': 'EUR base currency con acciones USD - conversión automática',
                'empty_portfolio_logic': 'Distingue portfolio vacío (cash waiting) vs momentum perdido',
                'cash_deployment': 'Recomendaciones específicas para deployment desde cash',
                'optimization_integration': 'Weekly ATR + Stop Loss + Fundamentales integrados'
            }
        }
        
        # Guardar recomendaciones
        with open('rotation_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print("✅ Recomendaciones con soporte de divisas guardadas: rotation_recommendations.json")
        return recommendations
    
    def analyze_current_positions_aggressive(self):
        """Análisis de posiciones actuales (solo si existen)"""
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
        
        # Simplified position analysis for existing positions
        for symbol, position_data in current_positions.items():
            screening_detail = screening_details.get(symbol)
            
            if screening_detail:
                # Position found in screening - analyze normally
                position_analysis[symbol] = {
                    'status': 'found_in_screening',
                    'screening_detail': screening_detail,
                    'recommendation': 'ANALYZE_MOMENTUM',
                    'optimization_applied': screening_detail.get('weekly_atr_optimized', False)
                }
            else:
                # Position not in screening - lost momentum
                position_analysis[symbol] = {
                    'status': 'not_in_screening',
                    'recommendation': 'URGENT_EXIT - Momentum perdido completamente',
                    'action_urgency': 'URGENT',
                    'optimization_applied': False
                }
        
        return position_analysis
    
    def print_currency_aware_summary(self, recommendations):
        """Imprime resumen con información de divisas"""
        if not recommendations:
            return
        
        print(f"\n=== RECOMENDACIONES AGRESIVAS CON SOPORTE DE DIVISAS ===")
        print(f"Análisis: {recommendations['analysis_date'][:10]}")
        
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
        
        if portfolio_details.get('is_waiting_for_opportunities'):
            cash_eur = portfolio_details.get('cash_usd', 0) / currency_info.get('exchange_rate', 1.08)
            print(f"💰 Cash disponible: €{cash_eur:,.2f}")
        
        action_summary = recommendations.get('action_summary', {})
        portfolio_context = action_summary.get('portfolio_context', 'UNKNOWN')
        
        # Show context-specific recommendations
        if portfolio_context in ['ALL_CASH_WAITING', 'MOSTLY_CASH']:
            cash_opportunities = action_summary.get('cash_deployment_opportunities', [])
            print(f"\n💰 OPORTUNIDADES DE DEPLOYMENT DE CASH:")
            for opp in cash_opportunities[:5]:
                allocation = opp.get('recommended_allocation_usd', 0)
                allocation_eur = allocation / currency_info.get('exchange_rate', 1.08)
                opt_indicator = " 🔧" if opp.get('optimization_features') else ""
                print(f"   💎 {opp['symbol']}{opt_indicator} - {opp['urgency']} - ~€{allocation_eur:,.0f} - {opp['reason']}")
        
        else:
            # Normal rotation recommendations
            aggressive_rotations = action_summary.get('aggressive_rotations', [])
            if aggressive_rotations:
                print(f"\n⚡ ROTACIONES AGRESIVAS:")
                for rot in aggressive_rotations[:3]:
                    print(f"   🔥 {rot['symbol']} - {rot['urgency']} - {rot['reason']}")
            
            urgent_exits = action_summary.get('urgent_exits', [])
            if urgent_exits:
                print(f"\n🚨 SALIDAS URGENTES:")
                for exit in urgent_exits:
                    print(f"   ❌ {exit['symbol']} - {exit['reason']}")

def main():
    """Función principal con soporte de divisas y portfolio vacío"""
    recommender = AggressiveRotationRecommender()
    
    recommendations = recommender.generate_aggressive_rotation_recommendations()
    
    if recommendations:
        recommender.print_currency_aware_summary(recommendations)
        print("\n✅ Recomendaciones con soporte de divisas completadas")
        
        portfolio_details = recommendations.get('portfolio_details', {})
        currency_info = recommendations.get('currency_support', {})
        
        print(f"\n🌍 CARACTERÍSTICAS IMPLEMENTADAS:")
        print(f"   - Soporte multi-divisa: ✅ {currency_info.get('base_currency', 'EUR')} → USD")
        print(f"   - Portfolio vacío: ✅ Manejo correcto de cash waiting")
        print(f"   - Conversión automática: ✅ Tipos de cambio en tiempo real")
        print(f"   - Optimizations integration: ✅ Weekly ATR + Fundamentales")
        
        if portfolio_details.get('is_waiting_for_opportunities'):
            print(f"\n💡 TU PORTFOLIO:")
            print(f"   - Estado: Esperando oportunidades de inversión")
            print(f"   - Acción: Revisar cash deployment opportunities")
            print(f"   - Próximo paso: Seleccionar 1-2 top opportunities para iniciar")
    
    else:
        print("\n❌ No se pudieron generar recomendaciones con soporte de divisas")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Aggressive Rotation Recommender - Optimizado para momentum trading con rotación mensual
Recomendaciones más agresivas + menor tiempo de consistencia + detección de oportunidades emergentes
🎯 Filosofía: Rotar agresivamente hacia mejores oportunidades de momentum
🔄 Target: ~1 mes por posición con rotación activa hacia mejores opciones
🆕 INCLUYE GESTIÓN AUTOMÁTICA DE HISTORIAL
🛠️ CORREGIDO: Manejo de casos donde posiciones actuales no aparecen en screening
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math

class AggressiveRotationRecommender:
    def __init__(self):
        self.current_portfolio = None
        self.consistency_analysis = None
        self.screening_data = None
        
        # 🆕 PARÁMETROS PARA ROTACIÓN AGRESIVA
        self.rotation_threshold = 0.20      # 20% score superior para recomendar rotación
        self.min_consistency_weeks = 2      # Solo 2 semanas vs 5 (más agresivo)
        self.emerging_opportunity_weight = 1.5  # Peso extra a momentum emergente
        self.momentum_decay_threshold = 0.15    # 15% caída en score para considerar salida
        
        # 🛠️ NUEVO: Fallback cuando no hay posiciones en screening
        self.fallback_avg_score = 100.0    # Score promedio asumido
        self.min_viable_score = 50.0       # Score mínimo para considerar oportunidad
        
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
    
    def calculate_momentum_strength_score(self, symbol_info, screening_detail=None):
        """
        🆕 SCORE DE FUERZA DE MOMENTUM para rotación agresiva
        Enfoque en momentum reciente y acceleration
        """
        score = 0
        factors = {}
        
        # 1. FACTOR DE MOMENTUM RECIENTE (peso principal - 40%)
        frequency = symbol_info.get('frequency', 0)
        weeks_appeared = symbol_info.get('weeks_appeared', [])
        appeared_this_week = symbol_info.get('appeared_this_week', False)
        
        # 🆕 BONUS AGRESIVO por aparición reciente
        if appeared_this_week:
            recent_momentum_score = frequency * 25  # 25 pts por semana aparecida
            if frequency >= 3:  # 3+ semanas = momentum establecido
                recent_momentum_score += 20  # Bonus por consistencia
            elif frequency >= 2:  # 2 semanas = momentum emergente
                recent_momentum_score += 15  # Bonus menor pero significativo
        else:
            # Penalización por no aparecer esta semana
            recent_momentum_score = max(frequency * 15 - 20, 0)
        
        score += recent_momentum_score
        factors['recent_momentum'] = recent_momentum_score
        
        # 2. FACTOR DE ACCELERATION (peso 30%)
        if len(weeks_appeared) >= 2:
            # Detectar momentum building vs fading
            recent_weeks = [w for w in weeks_appeared if w >= 3]  # Últimas 3 semanas
            acceleration_score = 0
            
            if len(recent_weeks) >= 2:
                # Momentum building: apariciones en semanas consecutivas recientes
                consecutive_recent = 1
                for i in range(len(recent_weeks) - 1, 0, -1):
                    if recent_weeks[i] == recent_weeks[i-1] + 1:
                        consecutive_recent += 1
                    else:
                        break
                
                acceleration_score = consecutive_recent * 15  # 15 pts por semana consecutiva
                
                # 🆕 BONUS ESPECIAL para "emerging momentum"
                if 5 in weeks_appeared and 4 in weeks_appeared:
                    acceleration_score += 25  # Fuerte momentum en últimas 2 semanas
                elif appeared_this_week and frequency == 1:
                    acceleration_score += 20  # Nueva aparición prometedora
            
            score += acceleration_score
            factors['acceleration'] = acceleration_score
        
        # 3. FACTOR DE CALIDAD TÉCNICA (peso 30%)
        if screening_detail:
            raw_score = screening_detail.get('score', 0)
            technical_quality = min(raw_score / 200 * 100, 100)  # Normalizar a 100
            
            # 🆕 BONUS por risk/reward excepcional
            rr_ratio = screening_detail.get('risk_reward_ratio', 0)
            if rr_ratio > 4.0:
                technical_quality += 20  # R/R excepcional
            elif rr_ratio > 3.0:
                technical_quality += 10  # R/R muy bueno
            
            # 🆕 BONUS por momentum 20d fuerte
            momentum_20d = screening_detail.get('outperformance_20d', 0)
            if momentum_20d > 15:
                technical_quality += 15  # Momentum 20d excepcional
            elif momentum_20d > 10:
                technical_quality += 8   # Momentum 20d fuerte
            
            score += technical_quality
            factors['technical_quality'] = technical_quality
        
        return {
            'total_score': score,
            'factors': factors,
            'max_possible': 300,  # Máximo teórico
            'momentum_category': self.categorize_momentum_strength(score)
        }
    
    def categorize_momentum_strength(self, score):
        """Categoriza la fuerza del momentum para decisiones"""
        if score > 200:
            return 'EXCEPTIONAL'  # Rotar inmediatamente
        elif score > 150:
            return 'STRONG'       # Considerar rotación agresiva
        elif score > 100:
            return 'MODERATE'     # Vigilar de cerca
        elif score > 50:
            return 'WEAK'         # No rotar aún
        else:
            return 'POOR'         # Considerar salida
    
    def calculate_position_momentum_health(self, symbol, position_data, consistency_info, screening_detail):
        """
        🆕 SALUD DE MOMENTUM para posiciones existentes
        Optimizado para detectar deterioro temprano
        """
        health_score = 100
        warnings = []
        momentum_signals = {}
        
        # 1. DETERIORO DE MOMENTUM RECIENTE (crítico)
        weeks_appeared = consistency_info.get('weeks_appeared', [])
        appeared_this_week = consistency_info.get('appeared_this_week', False)
        
        if not appeared_this_week:
            weeks_absent = 5 - max(weeks_appeared) if weeks_appeared else 5
            if weeks_absent >= 2:  # Más agresivo: 2 semanas vs 3
                health_score -= 60  # Penalización severa
                warnings.append(f"Sin momentum {weeks_absent} semanas - CRÍTICO")
            elif weeks_absent >= 1:
                health_score -= 30
                warnings.append(f"Sin momentum esta semana - VIGILAR")
        
        # 2. MOMENTUM ACCELERATION (nuevo criterio)
        if screening_detail:
            current_score = screening_detail.get('score', 0)
            momentum_20d = screening_detail.get('outperformance_20d', 0)
            
            # 🆕 Detectar debilitamiento del momentum
            if momentum_20d < 3:  # Momentum débil
                health_score -= 25
                warnings.append(f"Momentum 20d débil ({momentum_20d:+.1f}%)")
            
            # 🆕 Detectar problemas técnicos
            rr_ratio = screening_detail.get('risk_reward_ratio', 0)
            if rr_ratio < 2.0:  # R/R deteriorado
                health_score -= 20
                warnings.append(f"R/R deteriorado ({rr_ratio:.1f}:1)")
        
        # 3. PERFORMANCE vs ENTRADA (agresivo)
        if screening_detail and position_data:
            current_price = screening_detail.get('current_price', 0)
            entry_price = position_data.get('entry_price', 0)
            
            if current_price > 0 and entry_price > 0:
                performance = ((current_price / entry_price) - 1) * 100
                
                if performance < -8:  # Más agresivo: -8% vs -15%
                    health_score -= 40
                    warnings.append(f"Pérdida {performance:.1f}% vs entrada - STOP LOSS cerca")
                elif performance < -5:
                    health_score -= 20
                    warnings.append(f"Pérdida {performance:.1f}% vs entrada")
                elif performance > 30:  # Take profit zone
                    warnings.append(f"Ganancia {performance:.1f}% - considerar take profit parcial")
        
        # 4. MOMENTUM RANKING DETERIORATION (nuevo)
        if consistency_info.get('frequency', 0) < 2:  # Menos de 2 apariciones
            health_score -= 30
            warnings.append("Consistencia insuficiente (<2 semanas)")
        
        return {
            'health_score': max(health_score, 0),
            'warnings': warnings,
            'status': 'HEALTHY' if health_score > 70 else 'WARNING' if health_score > 40 else 'CRITICAL',
            'momentum_signals': momentum_signals,
            'action_urgency': 'HIGH' if health_score < 40 else 'MEDIUM' if health_score < 70 else 'LOW'
        }
    
    def identify_rotation_opportunities_aggressive(self):
        """
        🆕 IDENTIFICA OPORTUNIDADES DE ROTACIÓN AGRESIVA
        🛠️ CORREGIDO: Manejo robusto cuando posiciones actuales no están en screening
        """
        if not self.consistency_analysis or not self.screening_data:
            return []
        
        current_positions = set(self.current_portfolio.get('positions', {}).keys()) if self.current_portfolio else set()
        rotation_opportunities = []
        
        # Obtener scores de posiciones actuales
        current_position_scores = {}
        screening_details = {}
        for result in self.screening_data.get('detailed_results', []):
            screening_details[result['symbol']] = result
            if result['symbol'] in current_positions:
                current_position_scores[result['symbol']] = result.get('score', 0)
        
        # 🛠️ CORREGIDO: Manejo cuando no hay posiciones actuales en screening
        if current_position_scores:
            avg_current_score = sum(current_position_scores.values()) / len(current_position_scores)
            portfolio_status = "SCREENING_MATCHED"
            print(f"📊 Score promedio posiciones actuales: {avg_current_score:.1f}")
        else:
            # TODAS las posiciones perdieron momentum - usar fallback
            avg_current_score = self.fallback_avg_score
            portfolio_status = "MOMENTUM_LOST_ALL_POSITIONS"
            print(f"🚨 CRÍTICO: Ninguna posición actual aparece en screening")
            print(f"📊 Usando score fallback: {avg_current_score:.1f}")
            print(f"🎯 Esto indica que TODAS las posiciones han perdido momentum")
        
        # Calcular threshold de rotación
        min_score_for_rotation = avg_current_score * (1 + self.rotation_threshold)  # 20% superior
        print(f"🎯 Score mínimo para rotación: {min_score_for_rotation:.1f} (+{self.rotation_threshold*100:.0f}%)")
        
        # 🛠️ NUEVO: Ajustar criterios según estado del portfolio
        if portfolio_status == "MOMENTUM_LOST_ALL_POSITIONS":
            # Criterios más flexibles cuando todas las posiciones perdieron momentum
            min_score_for_rotation = max(min_score_for_rotation, self.min_viable_score)
            print(f"🔧 Ajuste por pérdida de momentum: score mínimo = {min_score_for_rotation:.1f}")
        
        # Analizar oportunidades por categoría
        consistency_data = self.consistency_analysis['consistency_analysis']
        
        # 🆕 PRIORIZAR CATEGORÍAS más agresivamente
        priority_categories = [
            ('consistent_winners', 1.0),    # Prioridad máxima
            ('strong_candidates', 0.9),     # Alta prioridad  
            ('emerging_opportunities', 1.2)  # 🆕 BONUS para emergentes
        ]
        
        for category, weight_multiplier in priority_categories:
            for symbol_info in consistency_data.get(category, []):
                symbol = symbol_info['symbol']
                
                if symbol not in current_positions:  # Solo nuevas oportunidades
                    screening_detail = screening_details.get(symbol)
                    
                    if screening_detail:
                        current_score = screening_detail.get('score', 0)
                        adjusted_score = current_score * weight_multiplier
                        
                        # 🆕 CRITERIOS AGRESIVOS DE ROTACIÓN
                        momentum_strength = self.calculate_momentum_strength_score(symbol_info, screening_detail)
                        
                        should_rotate = False
                        rotation_reason = ""
                        
                        # 🛠️ CORREGIDO: Prevenir división por cero
                        try:
                            # Criterio 1: Score superior
                            if adjusted_score >= min_score_for_rotation:
                                should_rotate = True
                                if avg_current_score > 0:
                                    percentage_superior = ((adjusted_score/avg_current_score-1)*100)
                                    rotation_reason = f"Score {adjusted_score:.1f} es {percentage_superior:+.1f}% superior"
                                else:
                                    rotation_reason = f"Score {adjusted_score:.1f} vs portfolio sin momentum"
                        except ZeroDivisionError:
                            # Fallback si hay algún problema
                            if adjusted_score >= self.min_viable_score:
                                should_rotate = True
                                rotation_reason = f"Score viable {adjusted_score:.1f} (portfolio sin momentum)"
                        
                        # 🆕 Criterio 2: Momentum excepcional emergente (aunque score sea menor)
                        if not should_rotate and (momentum_strength['momentum_category'] == 'EXCEPTIONAL' and 
                              symbol_info.get('frequency', 0) >= self.min_consistency_weeks):
                            should_rotate = True
                            rotation_reason = f"Momentum excepcional emergente (score momentum: {momentum_strength['total_score']:.0f})"
                        
                        # 🆕 Criterio 3: Momentum muy fuerte + consistencia mínima
                        if not should_rotate and (momentum_strength['momentum_category'] == 'STRONG' and 
                              symbol_info.get('frequency', 0) >= self.min_consistency_weeks and
                              adjusted_score >= avg_current_score * 0.9):  # Al menos 90% del score actual
                            should_rotate = True
                            rotation_reason = f"Momentum fuerte + score competitivo ({adjusted_score:.1f})"
                        
                        # 🛠️ NUEVO: Criterio especial cuando portfolio perdió momentum
                        if not should_rotate and portfolio_status == "MOMENTUM_LOST_ALL_POSITIONS":
                            if (adjusted_score >= self.min_viable_score and 
                                symbol_info.get('frequency', 0) >= self.min_consistency_weeks):
                                should_rotate = True
                                rotation_reason = f"Portfolio reset - Score viable {adjusted_score:.1f}"
                        
                        if should_rotate:
                            # Determinar urgencia de rotación
                            urgency = 'HIGH'
                            if momentum_strength['momentum_category'] == 'EXCEPTIONAL':
                                urgency = 'URGENT'
                            elif momentum_strength['momentum_category'] in ['STRONG', 'MODERATE']:
                                urgency = 'HIGH'
                            else:
                                urgency = 'MEDIUM'
                            
                            # 🛠️ MEJORADO: Identificar qué posición reemplazar
                            worst_position = None
                            if current_position_scores:
                                worst_symbol = min(current_position_scores, key=current_position_scores.get)
                                worst_score = current_position_scores[worst_symbol]
                                if adjusted_score > worst_score * 1.1:  # 10% mejor que la peor
                                    worst_position = worst_symbol
                            elif portfolio_status == "MOMENTUM_LOST_ALL_POSITIONS" and current_positions:
                                # Si todas perdieron momentum, recomendar reemplazar cualquiera
                                worst_position = list(current_positions)[0]  # Primera posición como ejemplo
                            
                            opportunity = {
                                'symbol': symbol,
                                'category': category,
                                'current_score': current_score,
                                'adjusted_score': adjusted_score,
                                'weight_multiplier': weight_multiplier,
                                'momentum_strength': momentum_strength,
                                'rotation_reason': rotation_reason,
                                'urgency': urgency,
                                'replace_position': worst_position,
                                'consistency_weeks': symbol_info.get('frequency', 0),
                                'appeared_this_week': symbol_info.get('appeared_this_week', False),
                                'screening_detail': screening_detail,
                                'target_hold': '~1 mes (rotación agresiva)',
                                'min_consistency_met': symbol_info.get('frequency', 0) >= self.min_consistency_weeks,
                                'portfolio_status': portfolio_status
                            }
                            
                            rotation_opportunities.append(opportunity)
        
        # Ordenar por score ajustado y urgencia
        rotation_opportunities.sort(key=lambda x: (
            x['urgency'] == 'URGENT',
            x['urgency'] == 'HIGH', 
            x['adjusted_score']
        ), reverse=True)
        
        # 🛠️ NUEVO: Logging mejorado del estado
        print(f"📈 Estado del portfolio: {portfolio_status}")
        print(f"🎯 Oportunidades identificadas: {len(rotation_opportunities)}")
        if portfolio_status == "MOMENTUM_LOST_ALL_POSITIONS":
            print(f"🚨 RECOMENDACIÓN: Considerar rotación completa del portfolio")
        
        return rotation_opportunities
    
    def analyze_current_positions_aggressive(self):
        """Análisis agresivo de posiciones actuales"""
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
        
        # Analizar cada posición con criterios agresivos
        for symbol, position_data in current_positions.items():
            screening_detail = screening_details.get(symbol)
            consistency_info = all_analyzed_symbols.get(symbol, {}).get('info', {})
            
            if symbol in all_analyzed_symbols:
                # Calcular momentum strength
                momentum_strength = self.calculate_momentum_strength_score(consistency_info, screening_detail)
                
                # Calcular salud del momentum
                momentum_health = self.calculate_position_momentum_health(
                    symbol, position_data, consistency_info, screening_detail
                )
                
                # 🆕 RECOMENDACIÓN AGRESIVA basada en momentum health
                recommendation = self.get_aggressive_position_recommendation(
                    momentum_strength, momentum_health, consistency_info
                )
                
                position_analysis[symbol] = {
                    'status': 'analyzed',
                    'category': all_analyzed_symbols[symbol]['category'],
                    'momentum_strength': momentum_strength,
                    'momentum_health': momentum_health,
                    'screening_detail': screening_detail,
                    'recommendation': recommendation,
                    'action_urgency': momentum_health.get('action_urgency', 'LOW')
                }
            else:
                # Posición crítica: no aparece en screening
                position_analysis[symbol] = {
                    'status': 'critical_not_in_screening',
                    'category': 'disappeared',
                    'momentum_strength': {'total_score': 0, 'momentum_category': 'POOR'},
                    'momentum_health': {
                        'health_score': 0,
                        'warnings': ['No aparece en screening reciente - MOMENTUM PERDIDO'],
                        'status': 'CRITICAL'
                    },
                    'recommendation': 'URGENT_EXIT - Momentum perdido completamente',
                    'action_urgency': 'URGENT'
                }
        
        return position_analysis
    
    def get_aggressive_position_recommendation(self, momentum_strength, momentum_health, consistency_info):
        """Recomendación agresiva basada en momentum health"""
        momentum_score = momentum_strength['total_score']
        health_score = momentum_health['health_score']
        momentum_category = momentum_strength['momentum_category']
        appeared_this_week = consistency_info.get('appeared_this_week', False)
        
        # Lógica agresiva de recomendaciones
        if health_score < 30 or momentum_category == 'POOR':
            action = "URGENT_EXIT"
            reason = f"Momentum crítico (health: {health_score:.0f}, categoria: {momentum_category})"
            
        elif health_score < 50 or not appeared_this_week:
            action = "CONSIDER_EXIT"
            reason = f"Momentum debilitándose (health: {health_score:.0f}, esta semana: {appeared_this_week})"
            
        elif health_score < 70 or momentum_category == 'WEAK':
            action = "WATCH_CAREFULLY"
            reason = f"Momentum en alerta (health: {health_score:.0f}, categoria: {momentum_category})"
            
        elif momentum_category in ['STRONG', 'EXCEPTIONAL']:
            action = "STRONG_HOLD"
            reason = f"Momentum excelente (health: {health_score:.0f}, categoria: {momentum_category})"
            
        else:
            action = "HOLD"
            reason = f"Momentum aceptable (health: {health_score:.0f}, categoria: {momentum_category})"
        
        # Añadir warnings específicos
        warnings = momentum_health.get('warnings', [])
        if warnings:
            reason += " | " + "; ".join(warnings[:2])  # Solo primeros 2 warnings
        
        return f"{action} - {reason}"
    
    def generate_aggressive_rotation_recommendations(self):
        """Genera recomendaciones completas con rotación agresiva"""
        print("🎯 Generando recomendaciones AGRESIVAS de rotación para momentum trading...")
        
        # Cargar todos los datos necesarios
        if not self.load_consistency_analysis():
            return None
        
        if not self.load_screening_data():
            print("⚠️ Sin datos de screening - análisis limitado")
        
        portfolio_loaded = self.load_current_portfolio()
        
        # 🆕 Archivar archivo anterior si existe
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
        
        # Análisis agresivo
        position_analysis = self.analyze_current_positions_aggressive()
        rotation_opportunities = self.identify_rotation_opportunities_aggressive()
        
        # Generar reporte completo
        recommendations = {
            'analysis_date': datetime.now().isoformat(),
            'portfolio_status': 'loaded' if portfolio_loaded else 'example_created',
            'analysis_type': 'aggressive_momentum_responsive',
            'rotation_philosophy': 'swing_for_fences_monthly_rotation',
            'aggressive_parameters': {
                'rotation_threshold': f"{self.rotation_threshold*100:.0f}% score superior",
                'min_consistency_weeks': self.min_consistency_weeks,
                'emerging_opportunity_weight': self.emerging_opportunity_weight,
                'momentum_decay_threshold': f"{self.momentum_decay_threshold*100:.0f}%",
                'fallback_avg_score': self.fallback_avg_score,
                'min_viable_score': self.min_viable_score
            },
            'current_positions_count': len(position_analysis),
            'position_analysis': position_analysis,
            'rotation_opportunities': rotation_opportunities[:15],  # Top 15 oportunidades
            'action_summary': self.create_aggressive_action_summary(position_analysis, rotation_opportunities),
            'weekly_context': {
                'analysis_weeks': self.consistency_analysis.get('weeks_analyzed', 0),
                'total_symbols_analyzed': self.consistency_analysis['summary_stats']['total_unique_symbols'],
                'consistent_winners': self.consistency_analysis['summary_stats']['consistent_winners_count'],
                'strong_candidates': self.consistency_analysis['summary_stats']['strong_candidates_count']
            },
            'methodology_notes': {
                'philosophy': 'Momentum trading agresivo con rotación mensual hacia mejores oportunidades',
                'rotation_criteria': 'Score 20% superior OR momentum excepcional emergente OR portfolio reset',
                'consistency_required': f'Mínimo {self.min_consistency_weeks} semanas (vs 5 conservador)',
                'exit_criteria': 'Momentum health <70 OR ausencia 1+ semanas OR deterioro técnico',
                'zero_division_protection': 'Implementado manejo robusto cuando posiciones pierden momentum'
            }
        }
        
        # Guardar recomendaciones
        with open('rotation_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print("✅ Recomendaciones agresivas guardadas: rotation_recommendations.json")
        print("📁 Historial de recomendaciones gestionado automáticamente")
        return recommendations
    
    def create_aggressive_action_summary(self, position_analysis, rotation_opportunities):
        """Crea resumen de acciones para rotación agresiva"""
        actions = {
            'holds': [],
            'consider_exits': [],
            'urgent_exits': [],
            'aggressive_rotations': [],  # 🆕 Nueva categoría
            'emerging_opportunities': [],  # 🆕 Nueva categoría
            'overall_action': 'NO_ACTION',
            'detailed_recommendations': []
        }
        
        # Analizar posiciones actuales con criterios agresivos
        urgent_actions = 0
        for symbol, analysis in position_analysis.items():
            recommendation = analysis['recommendation']
            health = analysis.get('momentum_health', {})
            urgency = analysis.get('action_urgency', 'LOW')
            
            if 'URGENT_EXIT' in recommendation:
                actions['urgent_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation,
                    'urgency': urgency
                })
                urgent_actions += 1
                
                # Añadir recomendación detallada
                actions['detailed_recommendations'].append({
                    'symbol': symbol,
                    'action': 'URGENT_EXIT',
                    'reason': recommendation.split(' - ')[1] if ' - ' in recommendation else recommendation,
                    'urgency': urgency,
                    'momentum_category': analysis.get('momentum_strength', {}).get('momentum_category', 'UNKNOWN')
                })
                
            elif 'CONSIDER_EXIT' in recommendation or 'WATCH_CAREFULLY' in recommendation:
                actions['consider_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation,
                    'urgency': urgency
                })
                
            elif 'STRONG_HOLD' in recommendation or 'HOLD' in recommendation:
                actions['holds'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
        
        # 🆕 Analizar oportunidades de rotación por urgencia
        for opp in rotation_opportunities:
            urgency = opp.get('urgency', 'MEDIUM')
            
            if urgency in ['URGENT', 'HIGH']:
                actions['aggressive_rotations'].append({
                    'symbol': opp['symbol'],
                    'reason': opp['rotation_reason'],
                    'urgency': urgency,
                    'replace_position': opp.get('replace_position'),
                    'momentum_category': opp['momentum_strength']['momentum_category'],
                    'consistency_weeks': opp['consistency_weeks']
                })
                urgent_actions += 1
                
                # Añadir recomendación detallada
                actions['detailed_recommendations'].append({
                    'symbol': opp['symbol'],
                    'action': f"AGGRESSIVE_ROTATION_{urgency}",
                    'reason': opp['rotation_reason'],
                    'urgency': urgency,
                    'replace': opp.get('replace_position'),
                    'momentum_category': opp['momentum_strength']['momentum_category'],
                    'score': opp['current_score'],
                    'target_upside': opp['screening_detail'].get('upside_pct', 0) if opp.get('screening_detail') else 0
                })
            
            elif opp['category'] == 'emerging_opportunities':
                actions['emerging_opportunities'].append({
                    'symbol': opp['symbol'],
                    'reason': opp['rotation_reason'],
                    'momentum_category': opp['momentum_strength']['momentum_category'],
                    'consistency_weeks': opp['consistency_weeks']
                })
        
        # 🛠️ MEJORADO: Determinar acción general agresiva considerando pérdida de momentum
        positions_lost_momentum = len([p for p in position_analysis.values() 
                                     if p.get('status') == 'critical_not_in_screening'])
        total_positions = len(position_analysis)
        
        if positions_lost_momentum >= total_positions and total_positions > 0:
            actions['overall_action'] = 'URGENT_PORTFOLIO_ROTATION'
        elif urgent_actions >= 3:
            actions['overall_action'] = 'URGENT_PORTFOLIO_ROTATION'
        elif urgent_actions >= 1 or len(actions['aggressive_rotations']) > 0:
            actions['overall_action'] = 'AGGRESSIVE_ROTATION_REQUIRED'
        elif len(actions['consider_exits']) > 0 or len(actions['emerging_opportunities']) > 0:
            actions['overall_action'] = 'EVALUATE_MOMENTUM_OPPORTUNITIES'
        else:
            actions['overall_action'] = 'MAINTAIN_WITH_VIGILANCE'
        
        return actions
    
    def print_aggressive_summary(self, recommendations):
        """Imprime resumen de recomendaciones agresivas"""
        if not recommendations:
            return
        
        print(f"\n=== RECOMENDACIONES AGRESIVAS DE MOMENTUM TRADING ===")
        print(f"Análisis: {recommendations['analysis_date'][:10]}")
        print(f"Filosofía: {recommendations['rotation_philosophy']}")
        print(f"Posiciones actuales: {recommendations['current_positions_count']}")
        
        action_summary = recommendations['action_summary']
        overall_action = action_summary['overall_action']
        
        # Mostrar acción general con emoji
        action_emojis = {
            'URGENT_PORTFOLIO_ROTATION': '🚨',
            'AGGRESSIVE_ROTATION_REQUIRED': '⚡',
            'EVALUATE_MOMENTUM_OPPORTUNITIES': '🔍',
            'MAINTAIN_WITH_VIGILANCE': '👀'
        }
        
        print(f"Acción general: {action_emojis.get(overall_action, '📊')} {overall_action}")
        
        # Mostrar rotaciones agresivas
        aggressive_rotations = action_summary.get('aggressive_rotations', [])
        if aggressive_rotations:
            print(f"\n⚡ ROTACIONES AGRESIVAS RECOMENDADAS:")
            for rot in aggressive_rotations[:3]:
                replace_text = f" (reemplazar {rot['replace_position']})" if rot.get('replace_position') else ""
                print(f"   🔥 {rot['symbol']} - {rot['urgency']} - {rot['reason']}{replace_text}")
        
        # Mostrar salidas urgentes
        urgent_exits = action_summary.get('urgent_exits', [])
        if urgent_exits:
            print(f"\n🚨 SALIDAS URGENTES:")
            for exit in urgent_exits:
                print(f"   ❌ {exit['symbol']} - {exit['reason']}")
        
        # Mostrar oportunidades emergentes
        emerging = action_summary.get('emerging_opportunities', [])
        if emerging:
            print(f"\n🌱 OPORTUNIDADES EMERGENTES (vigilar):")
            for opp in emerging[:3]:
                print(f"   👁️ {opp['symbol']} - {opp['momentum_category']} - {opp['consistency_weeks']} semanas")
        
        # Mostrar parámetros agresivos
        params = recommendations['aggressive_parameters']
        print(f"\n📊 PARÁMETROS AGRESIVOS:")
        print(f"   - Rotación si score {params['rotation_threshold']} superior")
        print(f"   - Consistencia mínima: {params['min_consistency_weeks']} semanas")
        print(f"   - Peso emergentes: {params['emerging_opportunity_weight']}x")
        print(f"   - Protección división por cero: Activada")

def main():
    """Función principal para rotación agresiva"""
    recommender = AggressiveRotationRecommender()
    
    # Generar análisis agresivo completo
    recommendations = recommender.generate_aggressive_rotation_recommendations()
    
    if recommendations:
        recommender.print_aggressive_summary(recommendations)
        print("\n✅ Recomendaciones agresivas de momentum completadas")
        
        # Mostrar metodología agresiva
        methodology = recommendations.get('methodology_notes', {})
        print(f"\n🎯 METODOLOGÍA AGRESIVA:")
        for key, value in methodology.items():
            print(f"   {key}: {value}")
            
        # Estadísticas de agresividad
        action_summary = recommendations.get('action_summary', {})
        total_rotations = len(action_summary.get('aggressive_rotations', []))
        total_exits = len(action_summary.get('urgent_exits', []))
        total_emerging = len(action_summary.get('emerging_opportunities', []))
        
        print(f"\n📈 ESTADÍSTICAS DE AGRESIVIDAD:")
        print(f"   - Rotaciones agresivas: {total_rotations}")
        print(f"   - Salidas urgentes: {total_exits}")
        print(f"   - Oportunidades emergentes: {total_emerging}")
        print(f"   - Acciones totales sugeridas: {total_rotations + total_exits}")
        
    else:
        print("\n❌ No se pudieron generar recomendaciones agresivas")

if __name__ == "__main__":
    main()
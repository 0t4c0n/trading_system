#!/usr/bin/env python3
"""
Rotation Recommender - Genera recomendaciones conservadoras de rotación
Basado en análisis de consistencia y cartera actual del usuario
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class RotationRecommender:
    def __init__(self):
        self.current_portfolio = None
        self.consistency_analysis = None
        self.rotation_recommendations = None
        
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
    
    def analyze_current_positions(self):
        """Analiza las posiciones actuales contra el análisis de consistencia"""
        if not self.current_portfolio or not self.consistency_analysis:
            return {}
            
        current_positions = list(self.current_portfolio.get('positions', {}).keys())
        position_analysis = {}
        
        # Obtener todos los símbolos del análisis de consistencia
        all_analyzed_symbols = {}
        consistency_data = self.consistency_analysis['consistency_analysis']
        
        for category, symbols in consistency_data.items():
            for symbol_info in symbols:
                symbol = symbol_info['symbol']
                all_analyzed_symbols[symbol] = {
                    'category': category,
                    'info': symbol_info
                }
        
        # Analizar cada posición actual
        for symbol in current_positions:
            if symbol in all_analyzed_symbols:
                symbol_data = all_analyzed_symbols[symbol]
                position_analysis[symbol] = {
                    'status': 'analyzed',
                    'category': symbol_data['category'],
                    'consistency_info': symbol_data['info'],
                    'recommendation': self.get_position_recommendation(symbol_data)
                }
            else:
                position_analysis[symbol] = {
                    'status': 'not_in_screening',
                    'category': 'disappeared',
                    'consistency_info': None,
                    'recommendation': 'CONSIDER_EXIT - No aparece en screening reciente'
                }
        
        return position_analysis
    
    def get_position_recommendation(self, symbol_data):
        """Determina recomendación para una posición basada en su consistencia"""
        category = symbol_data['category']
        info = symbol_data['info']
        appeared_this_week = info.get('appeared_this_week', False)
        frequency = info.get('frequency', 0)
        
        if category == 'consistent_winners':
            return 'STRONG_HOLD - Consistencia excepcional'
        elif category == 'strong_candidates':
            if appeared_this_week:
                return 'HOLD - Mantiene fortaleza'
            else:
                return 'WATCH_CAREFULLY - Monitorear próxima semana'
        elif category == 'emerging_opportunities':
            if appeared_this_week:
                return 'HOLD - Momentum emergente'
            else:
                return 'CONSIDER_EXIT - Perdiendo momentum'
        elif category == 'volatile_signals':
            return 'CONSIDER_EXIT - Señal volátil, poco confiable'
        elif category == 'disappeared_stocks':
            weeks_absent = 5 - max(info.get('weeks_appeared', [0])) if info.get('weeks_appeared') else 5
            if weeks_absent >= 2:
                return f'URGENT_EXIT - Ausente {weeks_absent} semanas'
            else:
                return 'CONSIDER_EXIT - Momentum perdido'
        else:
            return 'EVALUATE - Categoría desconocida'
    
    def identify_new_opportunities(self):
        """Identifica nuevas oportunidades de compra"""
        if not self.consistency_analysis:
            return []
        
        current_positions = set(self.current_portfolio.get('positions', {}).keys()) if self.current_portfolio else set()
        new_opportunities = []
        
        consistency_data = self.consistency_analysis['consistency_analysis']
        
        # Solo recomendar COMPRAS de consistent winners y strong candidates
        high_confidence_categories = ['consistent_winners', 'strong_candidates']
        
        for category in high_confidence_categories:
            for symbol_info in consistency_data[category]:
                symbol = symbol_info['symbol']
                
                # Solo recomendar si no la tenemos ya
                if symbol not in current_positions:
                    confidence_level = 'VERY_HIGH' if category == 'consistent_winners' else 'HIGH'
                    
                    opportunity = {
                        'symbol': symbol,
                        'category': category,
                        'confidence': confidence_level,
                        'reason': f"Consistencia {symbol_info['frequency']}/5 semanas",
                        'consistency_score': symbol_info.get('consistency_score', 0),
                        'appeared_this_week': symbol_info.get('appeared_this_week', False),
                        'current_price': symbol_info.get('current_price'),
                        'risk_pct': symbol_info.get('risk_pct'),
                        'score': symbol_info.get('score'),
                        'target_hold': '2-3 meses'
                    }
                    
                    new_opportunities.append(opportunity)
        
        # Ordenar por consistency score
        new_opportunities.sort(key=lambda x: x['consistency_score'], reverse=True)
        
        return new_opportunities
    
    def generate_watchlist(self):
        """Genera lista de vigilancia para próximas semanas"""
        if not self.consistency_analysis:
            return []
        
        current_positions = set(self.current_portfolio.get('positions', {}).keys()) if self.current_portfolio else set()
        watchlist = []
        
        consistency_data = self.consistency_analysis['consistency_analysis']
        
        # Emerging opportunities que podrían convertirse en compras
        for symbol_info in consistency_data.get('emerging_opportunities', []):
            symbol = symbol_info['symbol']
            
            if symbol not in current_positions:
                watchlist.append({
                    'symbol': symbol,
                    'reason': 'Emergiendo - Necesita confirmación',
                    'frequency': f"{symbol_info['frequency']}/5 semanas",
                    'appeared_this_week': symbol_info.get('appeared_this_week', False),
                    'action': 'Si aparece próxima semana → Considerar compra',
                    'current_price': symbol_info.get('current_price'),
                    'consistency_score': symbol_info.get('consistency_score', 0)
                })
        
        # Nuevos símbolos de esta semana
        trend_changes = self.consistency_analysis.get('trend_changes', {})
        for symbol in trend_changes.get('newly_emerged', []):
            if symbol not in current_positions:
                watchlist.append({
                    'symbol': symbol,
                    'reason': 'Aparición nueva esta semana',
                    'frequency': '1/5 semanas (nuevo)',
                    'appeared_this_week': True,
                    'action': 'Vigilar consistencia próximas 2 semanas',
                    'current_price': None,
                    'consistency_score': 10  # Score base para nuevos
                })
        
        # Ordenar por consistency score
        watchlist.sort(key=lambda x: x['consistency_score'], reverse=True)
        
        return watchlist
    
    def generate_rotation_recommendations(self):
        """Genera recomendaciones completas de rotación"""
        print("🎯 Generando recomendaciones de rotación...")
        
        # Cargar datos necesarios
        if not self.load_consistency_analysis():
            return None
        
        portfolio_loaded = self.load_current_portfolio()
        
        # Analizar posiciones actuales
        position_analysis = self.analyze_current_positions()
        
        # Identificar oportunidades
        new_opportunities = self.identify_new_opportunities()
        watchlist = self.generate_watchlist()
        
        # Generar reporte
        recommendations = {
            'analysis_date': datetime.now().isoformat(),
            'portfolio_status': 'loaded' if portfolio_loaded else 'example_created',
            'current_positions_count': len(position_analysis),
            'position_analysis': position_analysis,
            'new_opportunities': new_opportunities[:10],  # Top 10
            'watchlist': watchlist[:15],  # Top 15
            'action_summary': self.create_action_summary(position_analysis, new_opportunities),
            'weekly_context': {
                'analysis_weeks': self.consistency_analysis.get('weeks_analyzed', 0),
                'total_symbols_analyzed': self.consistency_analysis['summary_stats']['total_unique_symbols'],
                'consistent_winners': self.consistency_analysis['summary_stats']['consistent_winners_count'],
                'strong_candidates': self.consistency_analysis['summary_stats']['strong_candidates_count']
            }
        }
        
        # Guardar recomendaciones
        with open('rotation_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2, default=str)
        
        print("✅ Recomendaciones guardadas: rotation_recommendations.json")
        return recommendations
    
    def create_action_summary(self, position_analysis, new_opportunities):
        """Crea resumen de acciones recomendadas"""
        actions = {
            'holds': [],
            'consider_exits': [],
            'urgent_exits': [],
            'strong_buys': [],
            'watch_buys': [],
            'overall_action': 'NO_ACTION'
        }
        
        # Analizar posiciones actuales
        for symbol, analysis in position_analysis.items():
            recommendation = analysis['recommendation']
            
            if 'STRONG_HOLD' in recommendation or 'HOLD' in recommendation:
                actions['holds'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
            elif 'CONSIDER_EXIT' in recommendation:
                actions['consider_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
            elif 'URGENT_EXIT' in recommendation:
                actions['urgent_exits'].append({
                    'symbol': symbol,
                    'reason': recommendation
                })
        
        # Analizar nuevas oportunidades
        for opp in new_opportunities:
            if opp['confidence'] == 'VERY_HIGH':
                actions['strong_buys'].append({
                    'symbol': opp['symbol'],
                    'reason': opp['reason'],
                    'price': opp.get('current_price'),
                    'risk': opp.get('risk_pct')
                })
            elif opp['confidence'] == 'HIGH':
                actions['watch_buys'].append({
                    'symbol': opp['symbol'],
                    'reason': opp['reason'],
                    'price': opp.get('current_price'),
                    'risk': opp.get('risk_pct')
                })
        
        # Determinar acción general
        if actions['urgent_exits'] or len(actions['strong_buys']) > 0:
            actions['overall_action'] = 'ACTION_REQUIRED'
        elif actions['consider_exits'] or len(actions['watch_buys']) > 0:
            actions['overall_action'] = 'EVALUATE_CHANGES'
        else:
            actions['overall_action'] = 'MAINTAIN_CURRENT'
        
        return actions
    
    def print_recommendations_summary(self, recommendations):
        """Imprime resumen de recomendaciones"""
        if not recommendations:
            return
        
        print(f"\n=== RECOMENDACIONES DE ROTACIÓN ===")
        print(f"Análisis: {recommendations['analysis_date'][:10]}")
        print(f"Posiciones actuales: {recommendations['current_positions_count']}")
        
        action_summary = recommendations['action_summary']
        print(f"Acción general: {action_summary['overall_action']}")
        
        # Posiciones actuales
        if action_summary['holds']:
            print(f"\n✅ MANTENER ({len(action_summary['holds'])}):")
            for hold in action_summary['holds'][:5]:
                print(f"   {hold['symbol']} - {hold['reason']}")
        
        if action_summary['urgent_exits']:
            print(f"\n🚨 SALIDA URGENTE ({len(action_summary['urgent_exits'])}):")
            for exit in action_summary['urgent_exits']:
                print(f"   {exit['symbol']} - {exit['reason']}")
        
        if action_summary['consider_exits']:
            print(f"\n⚠️ CONSIDERAR SALIDA ({len(action_summary['consider_exits'])}):")
            for exit in action_summary['consider_exits']:
                print(f"   {exit['symbol']} - {exit['reason']}")
        
        # Nuevas oportunidades
        if action_summary['strong_buys']:
            print(f"\n🔥 COMPRA FUERTE ({len(action_summary['strong_buys'])}):")
            for buy in action_summary['strong_buys'][:3]:
                price_info = f" - ${buy['price']:.2f}" if buy['price'] else ""
                risk_info = f" (Risk: {buy['risk']:.1f}%)" if buy['risk'] else ""
                print(f"   {buy['symbol']}{price_info}{risk_info} - {buy['reason']}")
        
        if action_summary['watch_buys']:
            print(f"\n👀 VIGILAR COMPRA ({len(action_summary['watch_buys'])}):")
            for buy in action_summary['watch_buys'][:3]:
                price_info = f" - ${buy['price']:.2f}" if buy['price'] else ""
                print(f"   {buy['symbol']}{price_info} - {buy['reason']}")
        
        # Lista de vigilancia
        watchlist = recommendations.get('watchlist', [])
        if watchlist:
            print(f"\n📋 LISTA DE VIGILANCIA ({len(watchlist)}):")
            for item in watchlist[:5]:
                print(f"   {item['symbol']} - {item['reason']} - {item['action']}")

def main():
    """Función principal para GitHub Actions"""
    recommender = RotationRecommender()
    
    # Generar recomendaciones completas
    recommendations = recommender.generate_rotation_recommendations()
    
    if recommendations:
        recommender.print_recommendations_summary(recommendations)
        print("\n✅ Recomendaciones de rotación completadas")
    else:
        print("\n❌ No se pudieron generar recomendaciones")

if __name__ == "__main__":
    main()

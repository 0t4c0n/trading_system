#!/usr/bin/env python3
"""
Consistency Analyzer - Analiza la consistencia de recomendaciones semanales
Identifica patrones de aparición para decisiones conservadoras de largo plazo
"""

import json
import os
import glob
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Optional

class ConsistencyAnalyzer:
    def __init__(self):
        self.historical_data = []
        self.current_week_data = None
        
    def load_historical_screenings(self, weeks_back=4):
        """Carga los últimos N resultados de screening semanal"""
        print(f"📚 Cargando historial de {weeks_back} semanas...")
        
        # Buscar archivos de screening semanal
        screening_files = glob.glob("weekly_screening_results*.json")
        screening_files.sort(key=os.path.getctime, reverse=True)  # Más reciente primero
        
        historical_data = []
        
        # Cargar archivos existentes
        for i, file_path in enumerate(screening_files[:weeks_back]):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                historical_data.append({
                    'week': weeks_back - i,  # Semana 4, 3, 2, 1
                    'date': data.get('analysis_date', ''),
                    'symbols': data.get('top_symbols', []),
                    'detailed_results': data.get('detailed_results', []),
                    'file_path': file_path
                })
                
                print(f"✓ Semana {weeks_back - i}: {len(data.get('top_symbols', []))} símbolos - {file_path}")
                
            except Exception as e:
                print(f"⚠️ Error cargando {file_path}: {e}")
        
        # Si no hay suficiente historial, rellenar con datos vacíos
        while len(historical_data) < weeks_back:
            missing_week = weeks_back - len(historical_data)
            historical_data.insert(0, {
                'week': missing_week,
                'date': (datetime.now() - timedelta(weeks=missing_week)).isoformat(),
                'symbols': [],
                'detailed_results': [],
                'file_path': 'N/A - Sin datos'
            })
            print(f"⚠️ Semana {missing_week}: Sin datos históricos")
        
        self.historical_data = sorted(historical_data, key=lambda x: x['week'])
        return self.historical_data
    
    def load_current_week_screening(self):
        """Carga el screening de la semana actual"""
        try:
            with open('weekly_screening_results.json', 'r') as f:
                self.current_week_data = json.load(f)
                print(f"📊 Screening actual: {len(self.current_week_data.get('top_symbols', []))} símbolos")
                return True
        except FileNotFoundError:
            print("❌ No se encontró weekly_screening_results.json")
            return False
        except Exception as e:
            print(f"❌ Error cargando screening actual: {e}")
            return False
    
    def analyze_symbol_consistency(self):
        """Analiza la consistencia de aparición de cada símbolo"""
        print("🔍 Analizando consistencia de símbolos...")
        
        # Contar apariciones por símbolo
        symbol_appearances = defaultdict(list)
        symbol_frequency = Counter()
        
        # Incluir semana actual
        current_symbols = self.current_week_data.get('top_symbols', []) if self.current_week_data else []
        
        # Procesar historial + semana actual
        all_weeks_data = self.historical_data + [{
            'week': 5,  # Semana actual
            'date': datetime.now().isoformat(),
            'symbols': current_symbols,
            'detailed_results': self.current_week_data.get('detailed_results', []) if self.current_week_data else []
        }]
        
        for week_data in all_weeks_data:
            week_num = week_data['week']
            symbols = week_data['symbols']
            
            for symbol in symbols:
                symbol_appearances[symbol].append(week_num)
                symbol_frequency[symbol] += 1
        
        # Categorizar símbolos por consistencia
        consistency_analysis = {
            'consistent_winners': [],      # 4+ de 5 semanas
            'strong_candidates': [],       # 3 de 5 semanas  
            'emerging_opportunities': [],   # 2 de 5 semanas
            'volatile_signals': [],        # 1 de 5 semanas
            'disappeared_stocks': []       # Estaban pero ya no están
        }
        
        for symbol, frequency in symbol_frequency.items():
            weeks_appeared = symbol_appearances[symbol]
            
            # Verificar si apareció en semana actual
            appeared_this_week = 5 in weeks_appeared
            
            symbol_info = {
                'symbol': symbol,
                'frequency': frequency,
                'weeks_appeared': weeks_appeared,
                'appeared_this_week': appeared_this_week,
                'consistency_score': self.calculate_consistency_score(weeks_appeared)
            }
            
            # Obtener detalles de la semana actual si está disponible
            if appeared_this_week and self.current_week_data:
                for detail in self.current_week_data.get('detailed_results', []):
                    if detail.get('symbol') == symbol:
                        symbol_info.update({
                            'current_price': detail.get('current_price'),
                            'score': detail.get('score'),
                            'risk_pct': detail.get('risk_pct'),
                            'outperformance_60d': detail.get('outperformance_60d')
                        })
                        break
            
            # Categorizar según frecuencia y patrón
            if frequency >= 4:
                consistency_analysis['consistent_winners'].append(symbol_info)
            elif frequency == 3:
                consistency_analysis['strong_candidates'].append(symbol_info)
            elif frequency == 2:
                consistency_analysis['emerging_opportunities'].append(symbol_info)
            elif frequency == 1:
                if appeared_this_week:
                    consistency_analysis['volatile_signals'].append(symbol_info)
                else:
                    consistency_analysis['disappeared_stocks'].append(symbol_info)
        
        # Ordenar cada categoría por consistency_score
        for category in consistency_analysis:
            consistency_analysis[category].sort(
                key=lambda x: x.get('consistency_score', 0), 
                reverse=True
            )
        
        return consistency_analysis
    
    def calculate_consistency_score(self, weeks_appeared):
        """Calcula un score de consistencia basado en el patrón de aparición"""
        if not weeks_appeared:
            return 0
        
        total_weeks = 5
        frequency = len(weeks_appeared)
        
        # Score base por frecuencia
        frequency_score = (frequency / total_weeks) * 100
        
        # Bonus por apariciones consecutivas
        consecutive_bonus = 0
        if len(weeks_appeared) > 1:
            consecutive_weeks = 1
            for i in range(1, len(weeks_appeared)):
                if weeks_appeared[i] == weeks_appeared[i-1] + 1:
                    consecutive_weeks += 1
                else:
                    break
            consecutive_bonus = (consecutive_weeks / len(weeks_appeared)) * 20
        
        # Bonus por aparecer en semana actual
        current_week_bonus = 10 if 5 in weeks_appeared else 0
        
        return frequency_score + consecutive_bonus + current_week_bonus
    
    def detect_trend_changes(self, consistency_analysis):
        """Detecta cambios de tendencia importantes"""
        trend_changes = {
            'newly_emerged': [],        # Nuevos símbolos esta semana
            'gaining_momentum': [],     # Aumentando frecuencia
            'losing_momentum': [],      # Disminuyendo frecuencia
            'disappeared_this_week': [] # Desaparecieron esta semana
        }
        
        # Símbolos de semana actual
        current_symbols = set(self.current_week_data.get('top_symbols', []) if self.current_week_data else [])
        
        # Símbolos de semana anterior (si existe)
        previous_symbols = set()
        if len(self.historical_data) > 0:
            last_week_data = self.historical_data[-1]
            previous_symbols = set(last_week_data['symbols'])
        
        # Nuevos símbolos (aparecen por primera vez)
        trend_changes['newly_emerged'] = list(current_symbols - previous_symbols)
        
        # Símbolos que desaparecieron
        trend_changes['disappeared_this_week'] = list(previous_symbols - current_symbols)
        
        # Analizar momentum basado en consistency analysis
        for symbol_info in consistency_analysis['emerging_opportunities']:
            symbol = symbol_info['symbol']
            weeks = symbol_info['weeks_appeared']
            
            # Si aparece en las últimas 2 semanas consecutivas = gaining momentum
            if len(weeks) >= 2 and max(weeks) == 5 and (max(weeks) - 1) in weeks:
                trend_changes['gaining_momentum'].append(symbol_info)
        
        # Símbolos perdiendo momentum (estaban consistentes pero ya no aparecen)
        for symbol_info in consistency_analysis['disappeared_stocks']:
            if symbol_info['frequency'] >= 2:  # Tenían cierta consistencia
                trend_changes['losing_momentum'].append(symbol_info)
        
        return trend_changes
    
    def generate_consistency_report(self):
        """Genera reporte completo de consistencia"""
        print("📋 Generando reporte de consistencia...")
        
        # Cargar datos
        if not self.load_current_week_screening():
            return None
        
        self.load_historical_screenings(4)
        
        # Análisis
        consistency_analysis = self.analyze_symbol_consistency()
        trend_changes = self.detect_trend_changes(consistency_analysis)
        
        # Crear reporte completo
        report = {
            'analysis_date': datetime.now().isoformat(),
            'weeks_analyzed': len(self.historical_data) + 1,  # +1 por semana actual
            'data_sources': {
                'historical_files': [h['file_path'] for h in self.historical_data],
                'current_week_file': 'weekly_screening_results.json'
            },
            'consistency_analysis': consistency_analysis,
            'trend_changes': trend_changes,
            'summary_stats': {
                'total_unique_symbols': len(consistency_analysis['consistent_winners'] + 
                                          consistency_analysis['strong_candidates'] + 
                                          consistency_analysis['emerging_opportunities'] + 
                                          consistency_analysis['volatile_signals'] + 
                                          consistency_analysis['disappeared_stocks']),
                'consistent_winners_count': len(consistency_analysis['consistent_winners']),
                'strong_candidates_count': len(consistency_analysis['strong_candidates']),
                'emerging_count': len(consistency_analysis['emerging_opportunities']),
                'newly_emerged_count': len(trend_changes['newly_emerged']),
                'disappeared_count': len(trend_changes['disappeared_this_week'])
            }
        }
        
        # Guardar reporte
        with open('consistency_analysis.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print("✅ Reporte de consistencia guardado: consistency_analysis.json")
        return report
    
    def print_summary(self, report):
        """Imprime resumen del análisis"""
        if not report:
            return
        
        print(f"\n=== ANÁLISIS DE CONSISTENCIA ===")
        print(f"Período: {report['weeks_analyzed']} semanas")
        print(f"Símbolos únicos analizados: {report['summary_stats']['total_unique_symbols']}")
        
        print(f"\n🏆 CONSISTENT WINNERS ({report['summary_stats']['consistent_winners_count']}):")
        for symbol_info in report['consistency_analysis']['consistent_winners'][:5]:
            print(f"   {symbol_info['symbol']} - {symbol_info['frequency']}/5 semanas - Score: {symbol_info['consistency_score']:.1f}")
        
        print(f"\n💎 STRONG CANDIDATES ({report['summary_stats']['strong_candidates_count']}):")
        for symbol_info in report['consistency_analysis']['strong_candidates'][:5]:
            print(f"   {symbol_info['symbol']} - {symbol_info['frequency']}/5 semanas - Score: {symbol_info['consistency_score']:.1f}")
        
        print(f"\n📈 EMERGING OPPORTUNITIES ({report['summary_stats']['emerging_count']}):")
        for symbol_info in report['consistency_analysis']['emerging_opportunities'][:5]:
            print(f"   {symbol_info['symbol']} - {symbol_info['frequency']}/5 semanas - Score: {symbol_info['consistency_score']:.1f}")
        
        if report['trend_changes']['newly_emerged']:
            print(f"\n🆕 NEWLY EMERGED ({len(report['trend_changes']['newly_emerged'])}):")
            for symbol in report['trend_changes']['newly_emerged'][:5]:
                print(f"   {symbol}")
        
        if report['trend_changes']['disappeared_this_week']:
            print(f"\n📉 DISAPPEARED THIS WEEK ({len(report['trend_changes']['disappeared_this_week'])}):")
            for symbol in report['trend_changes']['disappeared_this_week'][:5]:
                print(f"   {symbol}")

def main():
    """Función principal para GitHub Actions"""
    analyzer = ConsistencyAnalyzer()
    
    # Generar análisis completo
    report = analyzer.generate_consistency_report()
    
    if report:
        analyzer.print_summary(report)
        print("\n✅ Análisis de consistencia completado")
    else:
        print("\n❌ No se pudo completar el análisis de consistencia")

if __name__ == "__main__":
    main()

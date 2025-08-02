#!/usr/bin/env python3
"""
Daily Consistency Analyzer - Adaptado para ejecución diaria
Analiza la consistencia de recomendaciones en los últimos 7 días
Para trading mensual con monitorización diaria

🔄 ADAPTADO: De análisis semanal a análisis de últimos 7 días
🎯 FILOSOFÍA: Daily monitoring, monthly trading
"""

import json
import os
import glob
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Optional

class DailyConsistencyAnalyzer:
    def __init__(self):
        self.historical_data = []
        self.current_day_data = None
        
    def load_historical_screenings(self, days_back=6):
        """
        🆕 Carga los últimos N días de screening (6 días históricos + hoy = 7 días)
        Adaptado para ejecución diaria vs semanal
        """
        print(f"📚 Cargando historial de {days_back + 1} días para análisis diario...")
        
        # Buscar archivos de screening históricos diarios
        all_screening_files = []
        
        # 1. Archivos históricos con fecha (patrón diario)
        historical_files = glob.glob("weekly_screening_results_*.json")
        all_screening_files.extend(historical_files)
        
        # 2. Archivo actual (si existe)
        if os.path.exists("weekly_screening_results.json"):
            all_screening_files.append("weekly_screening_results.json")
        
        # Ordenar archivos por fecha de modificación (más recientes primero)
        all_screening_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Tomar solo los últimos days_back archivos históricos
        historical_files_selected = all_screening_files[1:days_back+1] if len(all_screening_files) > 1 else []
        
        # Cargar archivos históricos
        for i, file_path in enumerate(historical_files_selected):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extraer date del archivo o usar fecha de modificación
                if 'analysis_date' in data:
                    file_date = data['analysis_date'][:10]
                else:
                    mod_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                
                historical_entry = {
                    'day': i + 1,  # Día 1 = más reciente histórico
                    'date': file_date,
                    'file_path': file_path,
                    'symbols': data.get('top_symbols', []),
                    'detailed_results': data.get('detailed_results', [])
                }
                
                self.historical_data.append(historical_entry)
                print(f"   ✓ Día -{i+1}: {file_path} ({len(historical_entry['symbols'])} símbolos)")
                
            except Exception as e:
                print(f"   ❌ Error cargando {file_path}: {e}")
                # Crear entrada placeholder para mantener cronología
                self.historical_data.append({
                    'day': i + 1,
                    'date': 'N/A',
                    'file_path': file_path,
                    'symbols': [],
                    'detailed_results': [],
                    'error': str(e)
                })
        
        # Rellenar días faltantes si no hay suficientes archivos históricos
        while len(self.historical_data) < days_back:
            missing_day = len(self.historical_data) + 1
            self.historical_data.append({
                'day': missing_day,
                'date': 'N/A - Sin datos',
                'file_path': 'N/A - Sin datos',
                'symbols': [],
                'detailed_results': []
            })
        
        print(f"✅ Historial diario cargado: {len(self.historical_data)} días")
        return len(self.historical_data) > 0
    
    def load_current_day_screening(self):
        """Carga el screening del día actual"""
        try:
            with open('weekly_screening_results.json', 'r') as f:
                self.current_day_data = json.load(f)
                
            print(f"✓ Screening del día actual cargado: {len(self.current_day_data.get('top_symbols', []))} símbolos")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando screening actual: {e}")
            return False
    
    def analyze_symbol_consistency_daily(self):
        """
        Analiza consistencia de símbolos en los últimos 7 días
        🆕 ADAPTADO: De semanas a días para ejecución diaria
        """
        print("📊 Analizando consistencia diaria (últimos 7 días)...")
        
        # Diccionarios para tracking por símbolo
        symbol_appearances = defaultdict(list)
        symbol_frequency = Counter()
        
        # Incluir día actual (día 7)
        current_symbols = self.current_day_data.get('top_symbols', []) if self.current_day_data else []
        
        # Procesar historial (días 1-6) + día actual (día 7)
        all_days_data = self.historical_data + [{
            'day': 7,  # Día actual
            'date': datetime.now().isoformat()[:10],
            'symbols': current_symbols,
            'detailed_results': self.current_day_data.get('detailed_results', []) if self.current_day_data else []
        }]
        
        for day_data in all_days_data:
            day_num = day_data['day']
            symbols = day_data['symbols']
            
            for symbol in symbols:
                symbol_appearances[symbol].append(day_num)
                symbol_frequency[symbol] += 1
        
        # Categorizar símbolos por consistencia diaria
        consistency_analysis = {
            'consistent_winners': [],      # 5+ de 7 días
            'strong_candidates': [],       # 3-4 de 7 días  
            'emerging_opportunities': [],   # 2 de 7 días
            'newly_emerged': [],           # 1 día (solo hoy)
            'disappeared_stocks': []       # Estaban pero ya no están hoy
        }
        
        for symbol, frequency in symbol_frequency.items():
            days_appeared = symbol_appearances[symbol]
            
            # Verificar si apareció hoy (día 7)
            appeared_today = 7 in days_appeared
            
            symbol_info = {
                'symbol': symbol,
                'frequency': frequency,
                'days_appeared': days_appeared,
                'appeared_today': appeared_today,
                'consistency_score': self.calculate_daily_consistency_score(days_appeared),
                'trend': self.analyze_daily_trend(days_appeared)
            }
            
            # Obtener detalles del día actual si está disponible
            if appeared_today and self.current_day_data:
                for detail in self.current_day_data.get('detailed_results', []):
                    if detail.get('symbol') == symbol:
                        symbol_info.update({
                            'current_price': detail.get('current_price'),
                            'score': detail.get('score'),
                            'risk_pct': detail.get('risk_pct'),
                            'outperformance_20d': detail.get('outperformance_20d'),
                            'ma50_bonus_applied': detail.get('optimizations', {}).get('ma50_bonus_applied', False)
                        })
                        break
            
            # Categorizar según frecuencia diaria
            if frequency >= 5:  # 5+ de 7 días
                consistency_analysis['consistent_winners'].append(symbol_info)
            elif frequency >= 3:  # 3-4 de 7 días
                consistency_analysis['strong_candidates'].append(symbol_info)
            elif frequency == 2:  # 2 de 7 días
                consistency_analysis['emerging_opportunities'].append(symbol_info)
            elif frequency == 1:
                if appeared_today:
                    consistency_analysis['newly_emerged'].append(symbol_info)
                else:
                    consistency_analysis['disappeared_stocks'].append(symbol_info)
        
        # Ordenar cada categoría por consistency_score
        for category in consistency_analysis:
            consistency_analysis[category].sort(
                key=lambda x: x.get('consistency_score', 0), 
                reverse=True
            )
        
        return consistency_analysis
    
    def calculate_daily_consistency_score(self, days_appeared):
        """Calcula un score de consistencia basado en apariciones diarias"""
        if not days_appeared:
            return 0
        
        total_days = 7
        frequency = len(days_appeared)
        
        # Score base por frecuencia
        frequency_score = (frequency / total_days) * 100
        
        # Bonus por apariciones consecutivas
        consecutive_bonus = 0
        if len(days_appeared) > 1:
            sorted_days = sorted(days_appeared)
            consecutive_count = 1
            max_consecutive = 1
            
            for i in range(1, len(sorted_days)):
                if sorted_days[i] == sorted_days[i-1] + 1:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1
            
            consecutive_bonus = (max_consecutive / len(days_appeared)) * 30
        
        # Bonus por aparecer hoy (día actual)
        today_bonus = 15 if 7 in days_appeared else 0
        
        # Bonus por tendencia reciente (últimos 3 días)
        recent_bonus = 0
        recent_days = [d for d in days_appeared if d >= 5]  # Días 5, 6, 7
        if len(recent_days) >= 2:
            recent_bonus = 10
        
        return frequency_score + consecutive_bonus + today_bonus + recent_bonus
    
    def analyze_daily_trend(self, days_appeared):
        """Analiza tendencia de aparición en días recientes"""
        if not days_appeared:
            return 'UNKNOWN'
        
        recent_days = [d for d in days_appeared if d >= 5]  # Últimos 3 días (5, 6, 7)
        
        if len(recent_days) >= 3:
            return 'ACCELERATING'
        elif len(recent_days) == 2:
            return 'STRENGTHENING'
        elif 7 in days_appeared and len(recent_days) == 1:
            return 'EMERGING'
        elif 7 not in days_appeared and max(days_appeared) < 5:
            return 'FADING'
        else:
            return 'STABLE'
    
    def detect_daily_trend_changes(self, consistency_analysis):
        """Detecta cambios de tendencia importantes en base diaria"""
        trend_changes = {
            'newly_emerged_today': [],      # Nuevos símbolos hoy
            'gaining_momentum': [],         # Aumentando frecuencia últimos días
            'losing_momentum': [],          # Disminuyendo frecuencia
            'disappeared_today': [],        # Desaparecieron hoy
            'consecutive_winners': []       # 3+ días consecutivos
        }
        
        # Símbolos de hoy
        current_symbols = set(self.current_day_data.get('top_symbols', []) if self.current_day_data else [])
        
        # Símbolos de ayer (si existe)
        yesterday_symbols = set()
        if len(self.historical_data) > 0:
            last_day_data = self.historical_data[0]  # Más reciente histórico
            yesterday_symbols = set(last_day_data['symbols'])
        
        # Nuevos símbolos (aparecen hoy por primera vez)
        trend_changes['newly_emerged_today'] = list(current_symbols - yesterday_symbols)
        
        # Símbolos que desaparecieron hoy
        trend_changes['disappeared_today'] = list(yesterday_symbols - current_symbols)
        
        # Analizar momentum basado en consistency analysis
        for symbol_info in consistency_analysis['strong_candidates']:
            trend = symbol_info['trend']
            if trend in ['ACCELERATING', 'STRENGTHENING']:
                trend_changes['gaining_momentum'].append(symbol_info)
        
        for symbol_info in consistency_analysis['emerging_opportunities']:
            trend = symbol_info['trend']
            if trend == 'ACCELERATING':
                trend_changes['gaining_momentum'].append(symbol_info)
        
        # Símbolos perdiendo momentum
        for symbol_info in consistency_analysis['disappeared_stocks']:
            if symbol_info['frequency'] >= 3:  # Tenían consistencia
                trend_changes['losing_momentum'].append(symbol_info)
        
        # Winners consecutivos (señal muy fuerte para trading mensual)
        for symbol_info in consistency_analysis['consistent_winners']:
            days = symbol_info['days_appeared']
            if len(days) >= 3:
                sorted_days = sorted(days)
                # Verificar si hay al menos 3 días consecutivos
                consecutive_count = 1
                max_consecutive = 1
                for i in range(1, len(sorted_days)):
                    if sorted_days[i] == sorted_days[i-1] + 1:
                        consecutive_count += 1
                        max_consecutive = max(max_consecutive, consecutive_count)
                    else:
                        consecutive_count = 1
                
                if max_consecutive >= 3:
                    trend_changes['consecutive_winners'].append(symbol_info)
        
        return trend_changes
    
    def generate_daily_consistency_report(self):
        """Genera reporte completo de consistencia diaria"""
        print("📋 Generando reporte de consistencia DIARIA...")
        
        # Cargar datos
        if not self.load_current_day_screening():
            return None
        
        self.load_historical_screenings(6)  # 6 días históricos + hoy = 7 días
        
        # Archivar archivo anterior si existe
        if os.path.exists('consistency_analysis.json'):
            try:
                with open('consistency_analysis.json', 'r') as f:
                    prev_data = json.load(f)
                    prev_date = prev_data.get('analysis_date', '')[:10].replace('-', '')
                
                archive_name = f"consistency_analysis_{prev_date}.json"
                os.rename('consistency_analysis.json', archive_name)
                print(f"📁 Análisis anterior archivado: {archive_name}")
            except Exception as e:
                print(f"⚠️ Error archivando análisis anterior: {e}")
        
        # Análisis diario
        consistency_analysis = self.analyze_symbol_consistency_daily()
        trend_changes = self.detect_daily_trend_changes(consistency_analysis)
        
        # Crear reporte completo
        report = {
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': 'daily_consistency_for_monthly_trading',
            'days_analyzed': 7,  # Últimos 7 días
            'execution_frequency': 'daily',
            'trading_philosophy': 'monthly_trades_daily_monitoring',
            'data_sources': {
                'historical_files': [h['file_path'] for h in self.historical_data],
                'current_day_file': 'weekly_screening_results.json'
            },
            'consistency_analysis': consistency_analysis,
            'trend_changes': trend_changes,
            'summary_stats': {
                'total_unique_symbols': len(consistency_analysis['consistent_winners'] + 
                                          consistency_analysis['strong_candidates'] + 
                                          consistency_analysis['emerging_opportunities'] + 
                                          consistency_analysis['newly_emerged'] + 
                                          consistency_analysis['disappeared_stocks']),
                'consistent_winners_count': len(consistency_analysis['consistent_winners']),
                'strong_candidates_count': len(consistency_analysis['strong_candidates']),
                'emerging_count': len(consistency_analysis['emerging_opportunities']),
                'newly_emerged_today_count': len(trend_changes['newly_emerged_today']),
                'disappeared_today_count': len(trend_changes['disappeared_today']),
                'consecutive_winners_count': len(trend_changes['consecutive_winners'])
            },
            'daily_insights': {
                'high_conviction_signals': len(trend_changes['consecutive_winners']),
                'momentum_building': len(trend_changes['gaining_momentum']),
                'momentum_fading': len(trend_changes['losing_momentum']),
                'new_opportunities': len(trend_changes['newly_emerged_today'])
            }
        }
        
        # Guardar reporte
        with open('consistency_analysis.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print("✅ Reporte de consistencia DIARIA guardado: consistency_analysis.json")
        print("📁 Historial de consistencia gestionado automáticamente")
        return report
    
    def print_daily_summary(self, report):
        """Imprime resumen del análisis diario"""
        if not report:
            return
        
        print(f"\n=== ANÁLISIS DE CONSISTENCIA DIARIA ===")
        print(f"📅 Período: Últimos {report['days_analyzed']} días")
        print(f"🔄 Filosofía: {report['trading_philosophy']}")
        print(f"📊 Símbolos únicos analizados: {report['summary_stats']['total_unique_symbols']}")
        
        print(f"\n🏆 CONSISTENT WINNERS - 5+ días ({report['summary_stats']['consistent_winners_count']}):")
        for symbol_info in report['consistency_analysis']['consistent_winners'][:5]:
            ma50_indicator = " 🌟" if symbol_info.get('ma50_bonus_applied', False) else ""
            trend = symbol_info.get('trend', 'UNKNOWN')
            print(f"   {symbol_info['symbol']}{ma50_indicator} - {symbol_info['frequency']}/7 días - Score: {symbol_info['consistency_score']:.1f} - {trend}")
        
        print(f"\n💎 STRONG CANDIDATES - 3-4 días ({report['summary_stats']['strong_candidates_count']}):")
        for symbol_info in report['consistency_analysis']['strong_candidates'][:5]:
            ma50_indicator = " 🌟" if symbol_info.get('ma50_bonus_applied', False) else ""
            trend = symbol_info.get('trend', 'UNKNOWN')
            print(f"   {symbol_info['symbol']}{ma50_indicator} - {symbol_info['frequency']}/7 días - Score: {symbol_info['consistency_score']:.1f} - {trend}")
        
        print(f"\n📈 EMERGING OPPORTUNITIES - 2 días ({report['summary_stats']['emerging_count']}):")
        for symbol_info in report['consistency_analysis']['emerging_opportunities'][:5]:
            ma50_indicator = " 🌟" if symbol_info.get('ma50_bonus_applied', False) else ""
            trend = symbol_info.get('trend', 'UNKNOWN')
            print(f"   {symbol_info['symbol']}{ma50_indicator} - {symbol_info['frequency']}/7 días - Score: {symbol_info['consistency_score']:.1f} - {trend}")
        
        if report['trend_changes']['consecutive_winners']:
            print(f"\n🔥 CONSECUTIVE WINNERS - Alta convicción ({len(report['trend_changes']['consecutive_winners'])}):")
            for symbol_info in report['trend_changes']['consecutive_winners'][:5]:
                days = len(symbol_info['days_appeared'])
                print(f"   {symbol_info['symbol']} - {days} días con señal consecutiva")
        
        if report['trend_changes']['newly_emerged_today']:
            print(f"\n🆕 NUEVOS HOY ({len(report['trend_changes']['newly_emerged_today'])}):")
            for symbol in report['trend_changes']['newly_emerged_today'][:5]:
                print(f"   {symbol}")
        
        if report['trend_changes']['disappeared_today']:
            print(f"\n📉 DESAPARECIDOS HOY ({len(report['trend_changes']['disappeared_today'])}):")
            for symbol in report['trend_changes']['disappeared_today'][:5]:
                print(f"   {symbol}")
        
        print(f"\n🎯 INSIGHTS PARA TRADING MENSUAL:")
        insights = report['daily_insights']
        print(f"   - Señales alta convicción: {insights['high_conviction_signals']}")
        print(f"   - Momentum creciente: {insights['momentum_building']}")
        print(f"   - Momentum declinante: {insights['momentum_fading']}")
        print(f"   - Nuevas oportunidades: {insights['new_opportunities']}")

def main():
    """Función principal para análisis diario de consistencia"""
    analyzer = DailyConsistencyAnalyzer()
    
    # Generar análisis completo diario
    report = analyzer.generate_daily_consistency_report()
    
    if report:
        analyzer.print_daily_summary(report)
        print("\n✅ Análisis de consistencia DIARIA completado")
        print("🎯 Sistema optimizado para trades mensuales con monitorización diaria")
    else:
        print("\n❌ No se pudo completar el análisis de consistencia diaria")

if __name__ == "__main__":
    main()
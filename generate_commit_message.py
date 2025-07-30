#!/usr/bin/env python3
"""
Script para generar mensaje de commit automático basado en resultados del análisis
"""
import json
import os
import sys
from datetime import datetime

def generate_commit_message():
    try:
        # Cargar archivos de resultados
        with open('weekly_screening_results.json', 'r') as f:
            screening = json.load(f)
        with open('consistency_analysis.json', 'r') as f:
            consistency = json.load(f)
        with open('rotation_recommendations.json', 'r') as f:
            rotation = json.load(f)
        
        # Extraer información
        results = screening.get('detailed_results', [])
        top_symbols = [r['symbol'] for r in results[:5]]
        winners_count = consistency.get('summary_stats', {}).get('consistent_winners_count', 0)
        action = rotation.get('action_summary', {}).get('overall_action', 'NO_ACTION')
        weeks_analyzed = consistency.get('weeks_analyzed', 0)
        
        # Métricas de trading
        trading_metrics = ''
        if results:
            if 'technical_score' in results[0]:
                avg_tech = sum(r.get('technical_score', 0) for r in results) / len(results)
                avg_final = sum(r.get('score', 0) for r in results) / len(results)
                trading_metrics = f' | Tech: {avg_tech:.0f} Final: {avg_final:.0f}'
            
            avg_rr = sum(r.get('risk_reward_ratio', 0) for r in results) / len(results)
            high_quality = len([r for r in results if r.get('risk_reward_ratio', 0) > 2.5])
            trading_metrics += f' | R/R: {avg_rr:.1f}:1 | HQ: {high_quality}'
        
        # Detectar tipo de análisis
        analysis_type = screening.get('analysis_type', 'standard')
        if 'sustainable_momentum' in analysis_type:
            analysis_label = 'Sustainable Momentum + Historial'
        elif 'enhanced' in analysis_type:
            analysis_label = 'Enhanced + Historial'
        else:
            analysis_label = 'Standard + Historial'
        
        # Obtener fecha del entorno
        report_date = os.environ.get('REPORT_DATE', datetime.now().strftime('%Y-%m-%d'))
        
        # Crear mensaje
        with open('commit_message.txt', 'w') as f:
            f.write(f'{analysis_label} Analysis {report_date}\n\n')
            f.write(f'Top 5: {", ".join(top_symbols) if top_symbols else "None"}\n')
            f.write(f'Consistent Winners: {winners_count}\n')
            f.write(f'Action: {action}\n')
            f.write(f'Filtered: {len(results)}{trading_metrics}\n')
            f.write(f'History: {weeks_analyzed} weeks analyzed\n\n')
            f.write(f'Enhanced Bot v2.1 + Auto History - {datetime.now().strftime("%H:%M UTC")}\n')
        
        print('SUCCESS: Commit message con historial generado')
        return True
        
    except Exception as e:
        print(f'ERROR: Error generando commit message: {e}')
        # Fallback message
        with open('commit_message.txt', 'w') as f:
            report_date = os.environ.get('REPORT_DATE', datetime.now().strftime('%Y-%m-%d'))
            f.write(f'Weekly Analysis + Auto History {report_date}\n\n')
            f.write(f'Enhanced Bot v2.1 - {datetime.now().strftime("%H:%M UTC")}\n')
        return False

if __name__ == "__main__":
    success = generate_commit_message()
    sys.exit(0 if success else 1)
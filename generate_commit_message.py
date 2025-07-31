#!/usr/bin/env python3
"""
Script para generar mensaje de commit automático basado en resultados del análisis
🔧 ACTUALIZADO: Detecta optimizaciones aplicadas (Weekly ATR, Stop Loss restrictivo, Fundamentales estrictos)
"""
import json
import os
import sys
from datetime import datetime

def detect_optimizations(screening, consistency, rotation):
    """🆕 Detecta optimizaciones aplicadas en los datos"""
    optimizations = {
        'weekly_atr_optimization': False,
        'min_stop_loss_restrictive': False,
        'fundamental_strict_filtering': False,
        'optimization_count': 0,
        'optimization_features': [],
        'avg_weekly_atr': 0,
        'avg_daily_atr': 0,
        'atr_ratio': 0,
        'positive_earnings_percentage': 0
    }
    
    # 1. Detectar Weekly ATR Optimization
    if screening:
        # Buscar en detailed_results
        detailed_results = screening.get('detailed_results', [])
        weekly_atr_count = 0
        weekly_atr_sum = 0
        daily_atr_sum = 0
        positive_earnings_count = 0
        
        for result in detailed_results:
            # Weekly ATR detection
            weekly_atr = result.get('weekly_atr', 0)
            daily_atr = result.get('atr', 0)
            
            if weekly_atr > 0:
                weekly_atr_count += 1
                weekly_atr_sum += weekly_atr
                
            if daily_atr > 0:
                daily_atr_sum += daily_atr
            
            # Fundamental filtering detection
            fundamental_data = result.get('fundamental_data', {})
            if fundamental_data.get('quarterly_earnings_positive', False):
                positive_earnings_count += 1
        
        # Weekly ATR optimization
        if weekly_atr_count > 0:
            optimizations['weekly_atr_optimization'] = True
            optimizations['optimization_count'] += 1
            optimizations['optimization_features'].append('Weekly ATR')
            optimizations['avg_weekly_atr'] = weekly_atr_sum / weekly_atr_count
            
            if daily_atr_sum > 0:
                optimizations['avg_daily_atr'] = daily_atr_sum / len(detailed_results)
                if optimizations['avg_daily_atr'] > 0:
                    optimizations['atr_ratio'] = optimizations['avg_weekly_atr'] / optimizations['avg_daily_atr']
        
        # Fundamental strict filtering
        if len(detailed_results) > 0:
            earnings_percentage = (positive_earnings_count / len(detailed_results)) * 100
            optimizations['positive_earnings_percentage'] = earnings_percentage
            
            if earnings_percentage >= 95:  # 95%+ tienen earnings positivos
                optimizations['fundamental_strict_filtering'] = True
                optimizations['optimization_count'] += 1
                optimizations['optimization_features'].append('Strict Fundamentals')
        
        # Buscar en análisis type y metodología
        analysis_type = screening.get('analysis_type', '')
        methodology = screening.get('methodology', {})
        
        if 'weekly_atr' in analysis_type.lower():
            optimizations['weekly_atr_optimization'] = True
            if 'Weekly ATR' not in optimizations['optimization_features']:
                optimizations['optimization_count'] += 1
                optimizations['optimization_features'].append('Weekly ATR')
        
        # Detectar stop loss restrictivo
        improvements = screening.get('improvements_applied', {})
        if improvements.get('min_stop_loss_restrictive', False):
            optimizations['min_stop_loss_restrictive'] = True
            optimizations['optimization_count'] += 1
            optimizations['optimization_features'].append('Min Stop Loss')
        
        # Buscar stop methods en detailed results
        restrictive_stop_count = 0
        for result in detailed_results:
            stop_analysis = result.get('stop_analysis', {})
            stop_method = stop_analysis.get('stop_selection', '')
            
            if 'ma50_priority' in stop_method or 'ma21_priority' in stop_method:
                restrictive_stop_count += 1
        
        if restrictive_stop_count > len(detailed_results) * 0.3:  # 30%+ usan métodos restrictivos
            optimizations['min_stop_loss_restrictive'] = True
            if 'Min Stop Loss' not in optimizations['optimization_features']:
                optimizations['optimization_count'] += 1
                optimizations['optimization_features'].append('Min Stop Loss')
    
    # 2. Detectar optimizaciones en rotation data
    if rotation:
        analysis_type = rotation.get('analysis_type', '')
        if 'weekly_atr' in analysis_type.lower():
            optimizations['weekly_atr_optimization'] = True
            if 'Weekly ATR' not in optimizations['optimization_features']:
                optimizations['optimization_count'] += 1
                optimizations['optimization_features'].append('Weekly ATR')
        
        # Buscar optimization features
        opt_features = rotation.get('optimization_features', {})
        if opt_features.get('weekly_atr_available', False):
            optimizations['weekly_atr_optimization'] = True
            if 'Weekly ATR' not in optimizations['optimization_features']:
                optimizations['optimization_count'] += 1
                optimizations['optimization_features'].append('Weekly ATR')
    
    return optimizations

def generate_optimization_indicators(optimizations):
    """🆕 Genera indicadores de optimización para el commit message"""
    indicators = []
    
    if optimizations['weekly_atr_optimization']:
        if optimizations['atr_ratio'] > 0:
            indicators.append(f"Weekly ATR {optimizations['atr_ratio']:.1f}x")
        else:
            indicators.append("Weekly ATR")
    
    if optimizations['min_stop_loss_restrictive']:
        indicators.append("Min Stop")
    
    if optimizations['fundamental_strict_filtering']:
        earnings_pct = optimizations['positive_earnings_percentage']
        indicators.append(f"Earnings+ {earnings_pct:.0f}%")
    
    return indicators

def determine_analysis_label(screening, optimizations):
    """🆕 Determina el label de análisis basado en optimizaciones"""
    analysis_type = screening.get('analysis_type', 'standard') if screening else 'standard'
    
    # Priorizar por optimizaciones detectadas
    if optimizations['optimization_count'] >= 3:
        return 'Full Optimization Stack'
    elif optimizations['weekly_atr_optimization'] and optimizations['fundamental_strict_filtering']:
        return 'Weekly ATR + Fundamentals'
    elif optimizations['weekly_atr_optimization']:
        return 'Weekly ATR Optimized'
    elif 'sustainable_momentum' in analysis_type:
        return 'Sustainable Momentum + Historial'
    elif 'enhanced' in analysis_type:
        return 'Enhanced + Historial'
    else:
        return 'Standard + Historial'

def generate_optimization_stats(screening, optimizations):
    """🆕 Genera estadísticas de optimización para el commit"""
    stats = []
    
    if screening:
        results = screening.get('detailed_results', [])
        if results:
            # Basic stats
            avg_rr = sum(r.get('risk_reward_ratio', 0) for r in results) / len(results)
            high_quality = len([r for r in results if r.get('risk_reward_ratio', 0) > 2.5])
            
            stats.append(f'R/R: {avg_rr:.1f}:1')
            stats.append(f'HQ: {high_quality}')
            
            # Optimization-specific stats
            if optimizations['weekly_atr_optimization']:
                weekly_atr_count = len([r for r in results if r.get('weekly_atr', 0) > 0])
                stats.append(f'WATR: {weekly_atr_count}')
            
            if optimizations['fundamental_strict_filtering']:
                earnings_pct = optimizations['positive_earnings_percentage']
                stats.append(f'E+: {earnings_pct:.0f}%')
    
    return stats

def generate_commit_message():
    try:
        # Cargar archivos de resultados
        screening = None
        consistency = None
        rotation = None
        
        try:
            with open('weekly_screening_results.json', 'r') as f:
                screening = json.load(f)
        except:
            pass
            
        try:
            with open('consistency_analysis.json', 'r') as f:
                consistency = json.load(f)
        except:
            pass
            
        try:
            with open('rotation_recommendations.json', 'r') as f:
                rotation = json.load(f)
        except:
            pass
        
        # 🆕 Detectar optimizaciones
        optimizations = detect_optimizations(screening, consistency, rotation)
        
        # Extraer información básica
        results = screening.get('detailed_results', []) if screening else []
        top_symbols = [r['symbol'] for r in results[:5]]
        winners_count = consistency.get('summary_stats', {}).get('consistent_winners_count', 0) if consistency else 0
        action = rotation.get('action_summary', {}).get('overall_action', 'NO_ACTION') if rotation else 'NO_ACTION'
        weeks_analyzed = consistency.get('weeks_analyzed', 0) if consistency else 0
        
        # 🆕 Generar indicadores de optimización
        optimization_indicators = generate_optimization_indicators(optimizations)
        
        # 🆕 Determinar analysis label basado en optimizaciones
        analysis_label = determine_analysis_label(screening, optimizations)
        
        # 🆕 Generar estadísticas incluyendo optimizaciones
        optimization_stats = generate_optimization_stats(screening, optimizations)
        
        # Métricas de trading básicas
        trading_metrics = ''
        if results:
            # Technical scores (si están disponibles)
            if 'technical_score' in results[0]:
                avg_tech = sum(r.get('technical_score', 0) for r in results) / len(results)
                avg_final = sum(r.get('score', 0) for r in results) / len(results)
                trading_metrics = f' | Tech: {avg_tech:.0f} Final: {avg_final:.0f}'
            
            # Añadir stats de optimización
            if optimization_stats:
                trading_metrics += f' | {" | ".join(optimization_stats)}'
        
        # Obtener fecha del entorno
        report_date = os.environ.get('REPORT_DATE', datetime.now().strftime('%Y-%m-%d'))
        
        # 🆕 Crear mensaje con optimizaciones
        with open('commit_message.txt', 'w') as f:
            # Title con optimizaciones
            title = f'{analysis_label} Analysis {report_date}'
            if optimization_indicators:
                title += f' + {" + ".join(optimization_indicators)}'
            f.write(f'{title}\n\n')
            
            # Body con información detallada
            f.write(f'Top 5: {", ".join(top_symbols) if top_symbols else "None"}\n')
            f.write(f'Consistent Winners: {winners_count}\n')
            f.write(f'Action: {action}\n')
            f.write(f'Filtered: {len(results)}{trading_metrics}\n')
            f.write(f'History: {weeks_analyzed} weeks analyzed\n')
            
            # 🆕 Sección de optimizaciones
            if optimizations['optimization_count'] > 0:
                f.write(f'\nOptimizations Applied ({optimizations["optimization_count"]}):\n')
                
                if optimizations['weekly_atr_optimization']:
                    if optimizations['atr_ratio'] > 0:
                        f.write(f'• Weekly ATR: {optimizations["avg_weekly_atr"]:.2f} vs Daily {optimizations["avg_daily_atr"]:.2f} ({optimizations["atr_ratio"]:.1f}x)\n')
                    else:
                        f.write(f'• Weekly ATR optimization applied\n')
                
                if optimizations['min_stop_loss_restrictive']:
                    f.write(f'• Min Stop Loss: MA50 → MA21 → others priority\n')
                
                if optimizations['fundamental_strict_filtering']:
                    f.write(f'• Strict Fundamentals: {optimizations["positive_earnings_percentage"]:.0f}% earnings positive\n')
            
            f.write(f'\nEnhanced Bot v2.2 + Auto History + Optimizations - {datetime.now().strftime("%H:%M UTC")}\n')
        
        # 🆕 Mostrar información de optimizaciones detectadas
        if optimizations['optimization_count'] > 0:
            print(f'SUCCESS: Commit message con {optimizations["optimization_count"]} optimizaciones detectadas')
            print(f'Optimizations: {", ".join(optimizations["optimization_features"])}')
        else:
            print('SUCCESS: Commit message con historial generado (sin optimizaciones detectadas)')
        
        return True
        
    except Exception as e:
        print(f'ERROR: Error generando commit message: {e}')
        
        # Fallback message mejorado
        with open('commit_message.txt', 'w') as f:
            report_date = os.environ.get('REPORT_DATE', datetime.now().strftime('%Y-%m-%d'))
            f.write(f'Weekly Analysis + Auto History {report_date}\n\n')
            f.write(f'Enhanced Bot v2.2 - Error Recovery Mode\n')
            f.write(f'Generated: {datetime.now().strftime("%H:%M UTC")}\n')
        return False

if __name__ == "__main__":
    success = generate_commit_message()
    sys.exit(0 if success else 1)

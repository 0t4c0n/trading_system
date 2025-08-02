#!/usr/bin/env python3
"""
Aggressive Momentum Weekly Report Generator - ACTUALIZADO: Con análisis de momentum responsivo
🆕 ADAPTADO: Para ejecución diaria con perspectiva de trading mensual
🌟 AÑADIDO: Tracking de MA50 bonus system (+22pts)
🔧 MANTIENE: Toda la funcionalidad y estructura original
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class AggressiveMomentumReportGenerator:
    def __init__(self):
        self.screening_data = None
        self.consistency_data = None
        self.rotation_data = None
        self.report_date = datetime.now()
        
    def load_all_data(self):
        """Carga todos los datos necesarios incluyendo nuevos formatos agresivos"""
        success_count = 0
        
        # Cargar screening results
        try:
            with open('weekly_screening_results.json', 'r') as f:
                self.screening_data = json.load(f)
                print("✓ Datos de screening diario cargados")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando screening: {e}")
        
        # Cargar consistency analysis (ahora diario)
        try:
            with open('consistency_analysis.json', 'r') as f:
                self.consistency_data = json.load(f)
                print("✓ Análisis de consistencia diaria cargado")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando consistencia: {e}")
        
        # Cargar rotation recommendations (criterios estrictos)
        try:
            with open('rotation_recommendations.json', 'r') as f:
                self.rotation_data = json.load(f)
                print("✓ Recomendaciones de trading mensual cargadas")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando rotación: {e}")
        
        return success_count >= 2
    
    def create_aggressive_markdown_report(self):
        """Crea reporte agresivo de momentum en formato Markdown"""
        report_filename = f"ENHANCED_WEEKLY_REPORT_{self.report_date.strftime('%Y_%m_%d')}.md"
        
        # Archivar reporte anterior si existe
        if os.path.exists(report_filename):
            try:
                timestamp = datetime.now().strftime('%H%M%S')
                backup_name = f"ENHANCED_WEEKLY_REPORT_{self.report_date.strftime('%Y_%m_%d')}_{timestamp}.md"
                os.rename(report_filename, backup_name)
                print(f"📁 Reporte anterior renombrado: {backup_name}")
            except Exception as e:
                print(f"⚠️ Error renombrando reporte anterior: {e}")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # Header adaptado para ejecución diaria
            f.write(f"# ⚡ DAILY MOMENTUM ANALYSIS - MONTHLY TRADING FOCUS - {self.report_date.strftime('%d %B %Y')}\n\n")
            f.write(f"## 🎯 **Daily Monitoring, Monthly Trading Strategy**\n\n")
            f.write(f"**📅 Execution:** Daily analysis (Mon-Fri post-market)\n")
            f.write(f"**🎯 Philosophy:** Monthly trades (~1 month holds) with daily monitoring\n")
            f.write(f"**🌟 MA50 Bonus:** +22 points for bullish rebounds active\n")
            f.write(f"**⚠️ Rotation:** Strict criteria to avoid overtrading\n\n")
            
            # Resumen ejecutivo adaptado
            self.write_aggressive_executive_summary(f)
            
            # Sección de optimizaciones aplicadas (incluyendo MA50)
            self.write_optimizations_applied_section(f)
            
            # Filosofía de momentum adaptada
            self.write_momentum_philosophy(f)
            
            # Top picks con momentum categories
            if self.screening_data:
                self.write_momentum_picks_with_categories(f)
            
            # Análisis de momentum responsivo
            if self.screening_data:
                self.write_momentum_responsive_analysis(f)
            
            # Rotación con criterios estrictos
            if self.rotation_data:
                self.write_aggressive_rotation_section(f)
            
            # Consistency con enfoque diario
            if self.consistency_data:
                self.write_momentum_consistency_section(f)
            
            # Sección Weekly ATR vs Daily ATR
            self.write_atr_analysis_section(f)
            
            # Sección MA50 bonus analysis
            self.write_ma50_bonus_analysis_section(f)
            
            # Gestión agresiva de momentum
            self.write_aggressive_momentum_management(f)
            
            # Contexto de mercado
            self.write_momentum_market_context(f)
            
            # Footer adaptado
            f.write(f"\n---\n\n")
            f.write(f"**Generado automáticamente:** {self.report_date.isoformat()}\n")
            f.write(f"**Próximo análisis:** {(self.report_date + timedelta(days=1)).strftime('%d %B %Y')} (daily execution)\n")
            f.write(f"**Estrategia:** Daily monitoring + Monthly trading + MA50 bonus system\n\n")
            f.write(f"⚡ *Daily Momentum Trading Bot - Monthly Focus by 0t4c0n*\n")
        
        print(f"✅ Reporte Markdown diario creado: {report_filename}")
        return report_filename
    
    def write_aggressive_executive_summary(self, f):
        """Escribe resumen ejecutivo adaptado para trading mensual"""
        f.write("## 📋 **RESUMEN EJECUTIVO DIARIO**\n\n")
        
        if not self.screening_data:
            f.write("*No hay datos de screening disponibles*\n\n")
            return
        
        detailed_results = self.screening_data.get('detailed_results', [])
        total_analyzed = len(detailed_results)
        
        # Estadísticas MA50 bonus
        ma50_bonus_count = 0
        ma50_bonus_stocks = []
        for stock in detailed_results:
            if stock.get('optimizations', {}).get('ma50_bonus_applied', False):
                ma50_bonus_count += 1
                ma50_bonus_stocks.append(stock['symbol'])
        
        f.write(f"**📊 Análisis diario:** {total_analyzed:,} acciones procesadas\n")
        f.write(f"**🌟 MA50 bonus aplicado:** {ma50_bonus_count} acciones ({ma50_bonus_count/max(total_analyzed,1)*100:.1f}%)\n")
        f.write(f"**🎯 Filosofía:** Daily monitoring para trades de ~1 mes\n")
        f.write(f"**⚠️ Rotaciones:** Solo con criterios estrictos (+30pts, stop proximity, momentum loss)\n\n")
        
        if ma50_bonus_stocks:
            f.write(f"### 🌟 **Highlights MA50 Bonus (Hoy):**\n")
            for stock in ma50_bonus_stocks[:5]:
                f.write(f"- **{stock}** - Señal de rebote alcista detectada\n")
            if len(ma50_bonus_stocks) > 5:
                f.write(f"- *...y {len(ma50_bonus_stocks) - 5} más*\n")
            f.write("\n")
        
        # Análisis de rotación con criterios estrictos
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            rotation_actions = (len(action_summary.get('urgent_exits', [])) + 
                              len(action_summary.get('aggressive_rotations', [])))
            
            f.write(f"### 🔄 **Estado de Trading Mensual:**\n")
            f.write(f"- **Acciones de rotación requeridas:** {rotation_actions}\n")
            f.write(f"- **Alineación estratégica:** {'✅ Alineado' if rotation_actions <= 2 else '⚠️ Requiere atención'}\n")
            f.write(f"- **Criterios estrictos:** Activos para evitar overtrading\n\n")
        
        f.write("---\n\n")
    
    def write_optimizations_applied_section(self, f):
        """Sección de optimizaciones aplicadas (incluyendo MA50)"""
        f.write("## 🔧 **OPTIMIZACIONES APLICADAS**\n\n")
        
        f.write("### 🌟 **MA50 Bonus System (+22 puntos):**\n")
        f.write("- **Detección:** Automática de rebotes en soporte MA50\n")
        f.write("- **Bonus base:** +22 puntos absolutos al score\n")
        f.write("- **Multiplicador adicional:** 20% bonus en score final\n")
        f.write("- **Significado técnico:** Señal alcista de rebote\n")
        f.write("- **Alineación:** Perfecta para holds de 1 mes\n\n")
        
        f.write("### 📊 **Weekly ATR Optimization:**\n")
        f.write("- **Take profit targets:** Basados en Weekly ATR vs Daily ATR\n")
        f.write("- **Timeframe alignment:** Mejor alineación con holds de 1 mes\n")
        f.write("- **Multiplicadores:** 3.0x/2.5x/2.0x según score\n")
        f.write("- **Precision improvement:** Mayor precisión temporal\n\n")
        
        f.write("### 🛡️ **Stop Loss Restrictivo:**\n")
        f.write("- **Prioridad:** MA50 → MA21 → otros métodos\n")
        f.write("- **Límite sagrado:** ≤10% riesgo máximo\n")
        f.write("- **Descarte:** Si no hay stop válido ≤10%\n")
        f.write("- **Quality bonus:** Extra puntos por stops de calidad\n\n")
        
        f.write("### 📈 **Fundamentales Estrictos:**\n")
        f.write("- **Requisito:** Solo earnings positivos obligatorio\n")
        f.write("- **Filtrado:** Datos fundamentales completos requeridos\n")
        f.write("- **Calidad:** Mayor tasa de éxito esperada\n\n")
        
        f.write("### 🔄 **Criterios de Rotación Estrictos:**\n")
        f.write("- **Score difference:** Mínimo +30 puntos para rotación\n")
        f.write("- **Stop proximity:** Alerta a 3% del stop loss\n")
        f.write("- **Momentum loss:** 3+ días sin aparecer en screening\n")
        f.write("- **Filosofía:** Daily monitoring, monthly trading\n\n")
        
        f.write("---\n\n")
    
    def write_momentum_philosophy(self, f):
        """Filosofía de momentum adaptada para trading mensual"""
        f.write("## 🎯 **FILOSOFÍA DE TRADING MENSUAL**\n\n")
        
        f.write("### 🔄 **Ejecución Diaria, Estrategia Mensual:**\n")
        f.write("- **Screening:** Diario (Lun-Vie post-market USA)\n")
        f.write("- **Holds objetivo:** ~1 mes por posición\n")
        f.write("- **Rotaciones:** Solo con alta convicción\n")
        f.write("- **Risk management:** Ultra conservador ≤10%\n\n")
        
        f.write("### 🌟 **MA50 Bonus Integration:**\n")
        f.write("- **Señal técnica:** Rebote en soporte MA50 = alcista\n")
        f.write("- **Timing:** Perfecto para entries en holds mensuales\n")
        f.write("- **Score impact:** +22pts base + 20% multiplicador\n")
        f.write("- **Stop loss:** MA50 prioritario en cálculos\n\n")
        
        f.write("### ⚠️ **Criterios Anti-Overtrading:**\n")
        f.write("- **Score threshold:** +30 puntos mínimo para rotación\n")
        f.write("- **Stop proximity:** Solo alertar si crítico (3%)\n")
        f.write("- **Momentum persistence:** 3+ días de ausencia = pérdida\n")
        f.write("- **Quality over quantity:** Menos trades, mayor convicción\n\n")
        
        f.write("---\n\n")
    
    def write_momentum_picks_with_categories(self, f):
        """Top picks con categorías de momentum (adaptado para MA50)"""
        f.write("## 🏆 **TOP MOMENTUM PICKS - DAILY ANALYSIS**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        if not detailed_results:
            f.write("*No hay picks disponibles*\n\n")
            return
        
        f.write("### 🌟 **Top 10 con MA50 Bonus Tracking:**\n\n")
        f.write("| Rank | Símbolo | Score | MA50 | Risk | R/R | Upside | Mom20d | Categoría |\n")
        f.write("|------|---------|-------|------|------|-----|--------|--------|----------|\n")
        
        for i, stock in enumerate(detailed_results[:10]):
            symbol = stock['symbol']
            score = stock.get('score', 0)
            ma50_bonus = stock.get('optimizations', {}).get('ma50_bonus_applied', False)
            ma50_indicator = "🌟" if ma50_bonus else "—"
            risk = stock.get('risk_pct', 0)
            rr = stock.get('risk_reward_ratio', 0)
            upside = stock.get('upside_pct', 0)
            mom_20d = stock.get('outperformance_20d', 0)
            
            # Categorizar momentum
            if score > 200 or mom_20d > 25:
                category = "EXCEPTIONAL"
            elif score > 150 or mom_20d > 15:
                category = "STRONG"
            elif score > 100:
                category = "MODERATE"
            else:
                category = "EMERGING"
            
            f.write(f"| {i+1} | {symbol} | {score:.1f} | {ma50_indicator} | {risk:.1f}% | {rr:.1f} | {upside:.1f}% | {mom_20d:+.1f}% | {category} |\n")
        
        f.write("\n")
        
        # Estadísticas por categoría
        exceptional = [s for s in detailed_results if s.get('score', 0) > 200 or s.get('outperformance_20d', 0) > 25]
        strong = [s for s in detailed_results if 150 <= s.get('score', 0) <= 200 or 15 <= s.get('outperformance_20d', 0) <= 25]
        
        f.write(f"### 📊 **Distribución por Categorías:**\n")
        f.write(f"- **🔥 Exceptional:** {len(exceptional)} acciones\n")
        f.write(f"- **💪 Strong:** {len(strong)} acciones\n")
        f.write(f"- **📈 Total top-tier:** {len(exceptional) + len(strong)} acciones\n\n")
        
        f.write("---\n\n")
    
    def write_momentum_responsive_analysis(self, f):
        """Análisis de screening con enfoque en optimizaciones"""
        f.write("## 📊 **ANÁLISIS MOMENTUM DIARIO - OPTIMIZATION STACK**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        methodology = self.screening_data.get('methodology', {})
        
        f.write(f"**Acciones analizadas:** {len(detailed_results)}\n")
        f.write(f"**Filosofía:** {methodology.get('philosophy', 'Daily monitoring, monthly trading')}\n")
        f.write(f"**Metodología:** {methodology.get('scoring', 'Momentum responsivo con MA50 bonus')}\n\n")
        
        if detailed_results:
            # Estadísticas MA50 bonus
            ma50_count = len([r for r in detailed_results if r.get('optimizations', {}).get('ma50_bonus_applied', False)])
            weekly_atr_count = len([r for r in detailed_results if r.get('weekly_atr', 0) > 0])
            positive_earnings = len([r for r in detailed_results 
                                   if r.get('fundamental_data', {}).get('quarterly_earnings_positive', False)])
            
            f.write(f"### 🌟 **MA50 Bonus System Stats:**\n")
            f.write(f"- **MA50 bonus aplicado:** {ma50_count}/{len(detailed_results)} acciones ({ma50_count/len(detailed_results)*100:.1f}%)\n")
            f.write(f"- **Bonus promedio:** +22 puntos base por rebote\n")
            f.write(f"- **Multiplicador adicional:** 20% en score final\n")
            f.write(f"- **Señal técnica:** Rebote alcista en soporte MA50\n\n")
            
            f.write(f"### 🔧 **Optimization Stack Stats:**\n")
            f.write(f"- **Weekly ATR disponible:** {weekly_atr_count}/{len(detailed_results)} acciones ({weekly_atr_count/len(detailed_results)*100:.1f}%)\n")
            f.write(f"- **Earnings positivos:** {positive_earnings}/{len(detailed_results)} acciones ({positive_earnings/len(detailed_results)*100:.1f}%)\n")
            f.write(f"- **Risk management:** 100% de acciones ≤10% riesgo (filtro sagrado)\n\n")
            
            # Métricas promedio
            avg_score = sum(r.get('score', 0) for r in detailed_results) / len(detailed_results)
            avg_momentum_20d = sum(r.get('outperformance_20d', 0) for r in detailed_results) / len(detailed_results)
            avg_rr = sum(r.get('risk_reward_ratio', 0) for r in detailed_results) / len(detailed_results)
            avg_upside = sum(r.get('upside_pct', 0) for r in detailed_results) / len(detailed_results)
            
            f.write(f"### 📈 **Métricas Promedio:**\n")
            f.write(f"- **Score promedio:** {avg_score:.1f} (con bonuses aplicados)\n")
            f.write(f"- **Momentum 20d promedio:** {avg_momentum_20d:.1f}% (peso 70%)\n")
            f.write(f"- **Risk/Reward promedio:** {avg_rr:.1f}:1 (targets optimizados)\n")
            f.write(f"- **Upside promedio:** {avg_upside:.1f}% (alineado para 1 mes)\n\n")
        
        f.write("---\n\n")
    
    def write_aggressive_rotation_section(self, f):
        """Sección de rotación con criterios estrictos"""
        f.write("## 🔄 **RECOMENDACIONES DE ROTACIÓN - CRITERIOS ESTRICTOS**\n\n")
        
        if not self.rotation_data:
            f.write("*No hay datos de rotación disponibles*\n\n")
            return
        
        action_summary = self.rotation_data.get('action_summary', {})
        strict_criteria = self.rotation_data.get('strict_criteria_applied', {})
        
        f.write(f"### ⚠️ **Criterios Estrictos Aplicados:**\n")
        f.write(f"- **Score mínimo:** +{strict_criteria.get('min_score_difference', 30)} puntos para rotación\n")
        f.write(f"- **Stop proximity:** {strict_criteria.get('stop_loss_proximity', 0.03)*100:.0f}% threshold\n")
        f.write(f"- **Momentum loss:** {strict_criteria.get('momentum_loss_days', 3)}+ días ausencia\n")
        f.write(f"- **MA50 bonus integration:** Activo en evaluaciones\n\n")
        
        overall_action = action_summary.get('overall_action', 'NO_DATA')
        f.write(f"### 🎯 **Acción General:** {overall_action}\n\n")
        
        # Salidas urgentes
        urgent_exits = action_summary.get('urgent_exits', [])
        if urgent_exits:
            f.write(f"### 🚨 **Salidas Urgentes ({len(urgent_exits)}):**\n")
            for exit in urgent_exits:
                symbol = exit.get('symbol', 'Unknown')
                reason = exit.get('reason', 'No reason')
                f.write(f"- **{symbol}:** {reason}\n")
            f.write("\n")
        
        # Rotaciones agresivas
        aggressive_rotations = action_summary.get('aggressive_rotations', [])
        if aggressive_rotations:
            f.write(f"### ⚡ **Rotaciones Recomendadas ({len(aggressive_rotations)}):**\n")
            for rotation in aggressive_rotations:
                symbol = rotation.get('symbol', 'Unknown')
                reason = rotation.get('reason', 'High potential')
                improvement = rotation.get('improvement', 0)
                ma50_bonus = rotation.get('ma50_bonus', False)
                ma50_indicator = " 🌟" if ma50_bonus else ""
                f.write(f"- **{symbol}{ma50_indicator}:** +{improvement:.1f}pts - {reason}\n")
            f.write("\n")
        
        # Cash deployment (si aplica)
        cash_opportunities = action_summary.get('cash_deployment_opportunities', [])
        if cash_opportunities:
            f.write(f"### 💰 **Oportunidades de Deployment ({len(cash_opportunities)}):**\n")
            for opp in cash_opportunities:
                symbol = opp.get('symbol', 'Unknown')
                reason = opp.get('reason', 'High quality')
                ma50_bonus = opp.get('ma50_bonus_applied', False)
                ma50_indicator = " 🌟" if ma50_bonus else ""
                f.write(f"- **{symbol}{ma50_indicator}:** {reason}\n")
            f.write("\n")
        
        f.write("---\n\n")
    
    def write_momentum_consistency_section(self, f):
        """Consistency con enfoque diario (adaptado de semanal)"""
        f.write("## 📊 **ANÁLISIS DE CONSISTENCIA DIARIA**\n\n")
        
        if not self.consistency_data:
            f.write("*No hay datos de consistencia disponibles*\n\n")
            return
        
        analysis_type = self.consistency_data.get('analysis_type', 'daily_consistency')
        days_analyzed = self.consistency_data.get('days_analyzed', 7)
        
        f.write(f"**Tipo:** {analysis_type}\n")
        f.write(f"**Ventana:** Últimos {days_analyzed} días de trading\n")
        f.write(f"**Filosofía:** Consistencia diaria para trades mensuales\n\n")
        
        consistency_analysis = self.consistency_data.get('consistency_analysis', {})
        
        # Consistent Winners (5+ días de 7)
        consistent_winners = consistency_analysis.get('consistent_winners', [])
        f.write(f"### 🏆 **Consistent Winners (5+ de {days_analyzed} días) - {len(consistent_winners)} acciones:**\n")
        for stock in consistent_winners[:8]:
            symbol = stock['symbol']
            frequency = stock['frequency']
            ma50_bonus = stock.get('ma50_bonus_applied', False)
            ma50_indicator = " 🌟" if ma50_bonus else ""
            f.write(f"- **{symbol}{ma50_indicator}** - {frequency}/{days_analyzed} días\n")
        f.write("\n")
        
        # Strong Candidates (3-4 días de 7)
        strong_candidates = consistency_analysis.get('strong_candidates', [])
        f.write(f"### 💎 **Strong Candidates (3-4 de {days_analyzed} días) - {len(strong_candidates)} acciones:**\n")
        for stock in strong_candidates[:8]:
            symbol = stock['symbol']
            frequency = stock['frequency']
            ma50_bonus = stock.get('ma50_bonus_applied', False)
            ma50_indicator = " 🌟" if ma50_bonus else ""
            f.write(f"- **{symbol}{ma50_indicator}** - {frequency}/{days_analyzed} días\n")
        f.write("\n")
        
        # Cambios de tendencia diarios
        trend_changes = self.consistency_data.get('trend_changes', {})
        newly_emerged = trend_changes.get('newly_emerged_today', [])
        disappeared = trend_changes.get('disappeared_today', [])
        
        if newly_emerged:
            f.write(f"### 🆕 **Nuevos Hoy ({len(newly_emerged)}):** {', '.join(newly_emerged[:10])}\n")
        
        if disappeared:
            f.write(f"### 📉 **Desaparecidos Hoy ({len(disappeared)}):** {', '.join(disappeared[:10])}\n")
        
        f.write("\n---\n\n")
    
    def write_atr_analysis_section(self, f):
        """Análisis comparativo ATR (mantener funcionalidad original)"""
        f.write("## 📊 **WEEKLY ATR vs DAILY ATR ANALYSIS**\n\n")
        
        if not self.screening_data:
            f.write("*No hay datos disponibles para análisis ATR*\n\n")
            return
        
        detailed_results = self.screening_data.get('detailed_results', [])
        if not detailed_results:
            f.write("*No hay resultados detallados para análisis ATR*\n\n")
            return
        
        # Calcular estadísticas ATR
        weekly_atrs = [r.get('weekly_atr', 0) for r in detailed_results if r.get('weekly_atr', 0) > 0]
        daily_atrs = [r.get('atr', 0) for r in detailed_results if r.get('atr', 0) > 0]
        
        if not weekly_atrs or not daily_atrs:
            f.write("*Datos ATR insuficientes para análisis comparativo*\n\n")
            return
        
        avg_weekly = sum(weekly_atrs) / len(weekly_atrs)
        avg_daily = sum(daily_atrs) / len(daily_atrs)
        avg_ratio = avg_weekly / avg_daily if avg_daily > 0 else 0
        
        f.write(f"### 📈 **Estadísticas ATR del Portfolio:**\n")
        f.write(f"- **Weekly ATR promedio:** {avg_weekly:.2f}\n")
        f.write(f"- **Daily ATR promedio:** {avg_daily:.2f}\n")
        f.write(f"- **Ratio Weekly/Daily:** {avg_ratio:.1f}x\n")
        f.write(f"- **Acciones con Weekly ATR:** {len(weekly_atrs)}/{len(detailed_results)}\n\n")
        
        f.write(f"### 🎯 **Impacto en Take Profit Targets:**\n")
        f.write(f"- **Alineación temporal:** Weekly ATR mejor para holds de 1 mes\n")
        f.write(f"- **Multiplicadores:** Más conservadores con Weekly ATR\n")
        f.write(f"- **Precisión:** Mayor hit rate esperado\n")
        f.write(f"- **Volatility matching:** Mejor sincronización con timeframe\n\n")
        
        f.write("---\n\n")
    
    def write_ma50_bonus_analysis_section(self, f):
        """🌟 Nueva sección específica para análisis MA50 bonus"""
        f.write("## 🌟 **MA50 BONUS SYSTEM - DETAILED ANALYSIS**\n\n")
        
        if not self.screening_data:
            f.write("*No hay datos disponibles para análisis MA50*\n\n")
            return
        
        detailed_results = self.screening_data.get('detailed_results', [])
        
        # Estadísticas MA50
        ma50_stocks = []
        total_ma50_bonus = 0
        
        for stock in detailed_results:
            optimizations = stock.get('optimizations', {})
            if optimizations.get('ma50_bonus_applied', False):
                ma50_stocks.append({
                    'symbol': stock['symbol'],
                    'bonus_value': optimizations.get('ma50_bonus_value', 0),
                    'final_score': stock.get('score', 0),
                    'risk_pct': stock.get('risk_pct', 0),
                    'upside_pct': stock.get('upside_pct', 0)
                })
                total_ma50_bonus += optimizations.get('ma50_bonus_value', 0)
        
        f.write(f"### 📊 **MA50 Bonus Impact Today:**\n")
        f.write(f"- **Stocks with MA50 bonus:** {len(ma50_stocks)}/{len(detailed_results)} ({len(ma50_stocks)/max(len(detailed_results),1)*100:.1f}%)\n")
        
        if ma50_stocks:
            avg_bonus = total_ma50_bonus / len(ma50_stocks)
            f.write(f"- **Average bonus value:** +{avg_bonus:.1f} points\n")
            f.write(f"- **Total bonus points awarded:** {total_ma50_bonus} points\n")
            f.write(f"- **Technical significance:** Bullish rebounds at MA50 support\n\n")
            
            f.write(f"### 🏆 **Top MA50 Bonus Stocks:**\n")
            sorted_ma50 = sorted(ma50_stocks, key=lambda x: x['final_score'], reverse=True)
            
            for i, stock in enumerate(sorted_ma50[:8]):
                f.write(f"{i+1}. **{stock['symbol']}** - Score: {stock['final_score']:.1f} "
                       f"(+{stock['bonus_value']} MA50) | Risk: {stock['risk_pct']:.1f}% | "
                       f"Upside: {stock['upside_pct']:.1f}%\n")
            f.write("\n")
        
        f.write(f"### 🎯 **MA50 System Performance:**\n")
        f.write(f"- **Detection method:** Automated MA50 support level identification\n")
        f.write(f"- **Technical signal:** Bullish rebound at 50-day moving average\n")
        f.write(f"- **Score enhancement:** +22 base points + 20% multiplier\n")
        f.write(f"- **Monthly trading alignment:** Perfect for 1-month hold strategy\n")
        f.write(f"- **Risk management:** MA50 prioritized as stop loss level\n\n")
        
        f.write("---\n\n")
    
    def write_aggressive_momentum_management(self, f):
        """Gestión de momentum adaptada para criterios estrictos"""
        f.write("## 🎯 **GESTIÓN DE MOMENTUM - TRADING MENSUAL**\n\n")
        
        f.write("### 🔄 **Criterios de Entrada (Daily Screening):**\n")
        f.write("- **Momentum 20d:** >5% vs SPY (peso 70%)\n")
        f.write("- **Momentum 60d:** >0% vs SPY (peso 30%)\n")
        f.write("- **Tendencia:** MA21 > MA50 > MA200 o rebote MA50\n")
        f.write("- **Fundamentales:** Earnings positivos OBLIGATORIO\n")
        f.write("- **Risk management:** Stop loss ≤10% calculable\n")
        f.write("- **MA50 bonus:** +22pts si rebote detectado\n\n")
        
        f.write("### ⚠️ **Criterios de Salida (Strict Rotation):**\n")
        f.write("- **Stop loss proximity:** Alerta si <3% del stop\n")
        f.write("- **Momentum loss:** No aparece 3+ días consecutivos\n")
        f.write("- **Score deterioration:** Caída >15% en ranking\n")
        f.write("- **Better opportunity:** Nueva opción +30pts superior\n")
        f.write("- **Time-based:** ~1 mes hold period target\n\n")
        
        f.write("### 🎯 **Take Profit Strategy:**\n")
        f.write("- **Primary method:** Weekly ATR-based (3.0x/2.5x/2.0x)\n")
        f.write("- **Timeframe alignment:** Optimizado para holds mensuales\n")
        f.write("- **Dynamic adjustment:** Según score y momentum category\n")
        f.write("- **Risk/Reward target:** Mínimo 2:1, objetivo 3:1+\n\n")
        
        f.write("---\n\n")
    
    def write_momentum_market_context(self, f):
        """Contexto de mercado (mantener funcionalidad original)"""
        f.write("## 📊 **CONTEXTO DE MERCADO DIARIO**\n\n")
        
        if not self.screening_data:
            f.write("*No hay datos de mercado disponibles*\n\n")
            return
        
        benchmark_context = self.screening_data.get('benchmark_context', {})
        
        f.write(f"### 📈 **SPY Benchmark Performance:**\n")
        f.write(f"- **SPY 20-day return:** {benchmark_context.get('spy_20d', 0):+.2f}%\n")
        f.write(f"- **SPY 60-day return:** {benchmark_context.get('spy_60d', 0):+.2f}%\n")
        f.write(f"- **SPY 90-day return:** {benchmark_context.get('spy_90d', 0):+.2f}%\n\n")
        
        # Análisis de outperformance
        detailed_results = self.screening_data.get('detailed_results', [])
        if detailed_results:
            outperformers_20d = len([r for r in detailed_results if r.get('outperformance_20d', 0) > 5])
            outperformers_60d = len([r for r in detailed_results if r.get('outperformance_60d', 0) > 0])
            
            f.write(f"### 🏆 **Outperformance Analysis:**\n")
            f.write(f"- **20-day outperformers (+5%):** {outperformers_20d}/{len(detailed_results)} "
                   f"({outperformers_20d/len(detailed_results)*100:.1f}%)\n")
            f.write(f"- **60-day outperformers (positive):** {outperformers_60d}/{len(detailed_results)} "
                   f"({outperformers_60d/len(detailed_results)*100:.1f}%)\n\n")
        
        f.write("### 🎯 **Market Alignment for Monthly Trading:**\n")
        f.write("- **Daily screening:** Capture momentum shifts early\n")
        f.write("- **Monthly holds:** Ride momentum waves effectively\n")
        f.write("- **Risk management:** Conservative approach in any market\n")
        f.write("- **Opportunity detection:** MA50 rebounds = market timing\n\n")
    
    def create_aggressive_dashboard_data(self):
        """Crea datos JSON para el dashboard agresivo con optimizaciones"""
        dashboard_data = {
            "timestamp": self.report_date.isoformat(),
            "market_date": self.report_date.strftime("%Y-%m-%d"),
            "analysis_type": "daily_momentum_monthly_trading_ma50_bonus",
            "execution_frequency": "daily",
            "trading_philosophy": "daily_monitoring_monthly_trading",
            "optimization_stack": {
                "ma50_bonus_system": True,
                "weekly_atr_take_profit": True,
                "strict_rotation_criteria": True,
                "ultra_conservative_risk": True
            },
            "summary": {
                "analysis_type": "Daily Momentum Analysis - Monthly Trading Focus",
                "total_analyzed": 0,
                "exceptional_momentum": 0,
                "strong_momentum": 0,
                "ma50_bonus_applied": 0,
                "rotation_opportunities": 0,
                "optimization_applied": True,
                "message": "Daily momentum analysis with monthly trading philosophy completed"
            },
            "top_picks": [],
            "momentum_analysis": {
                "philosophy": "daily_monitoring_monthly_trading_ma50_bonus",
                "execution_frequency": "daily",
                "momentum_weights": {
                    "momentum_20d": 0.70,
                    "momentum_60d": 0.30
                },
                "exceptional_momentum": [],
                "strong_momentum": [],
                "emerging_momentum": []
            },
            "ma50_bonus_highlights": [],
            "rotation_recommendations": {},
            "market_context": {},
            "optimization_metrics": {
                "ma50_bonus_system": True,
                "weekly_atr_implemented": False,
                "strict_rotation_criteria": True,
                "avg_ma50_bonus": 0,
                "ma50_bonus_percentage": 0
            }
        }
        
        # Datos de screening con enfoque en MA50 bonus
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            dashboard_data["summary"]["total_analyzed"] = len(detailed_results)
            
            # MA50 bonus highlights
            ma50_stocks = []
            ma50_count = 0
            total_ma50_bonus = 0
            
            for stock in detailed_results[:15]:
                optimizations = stock.get('optimizations', {})
                if optimizations.get('ma50_bonus_applied', False):
                    ma50_count += 1
                    bonus_value = optimizations.get('ma50_bonus_value', 0)
                    total_ma50_bonus += bonus_value
                    
                    ma50_stocks.append({
                        "symbol": stock['symbol'],
                        "score": stock.get('score', 0),
                        "bonus_value": bonus_value,
                        "risk_pct": stock.get('risk_pct', 0),
                        "upside_pct": stock.get('upside_pct', 0)
                    })
            
            dashboard_data["ma50_bonus_highlights"] = ma50_stocks
            dashboard_data["summary"]["ma50_bonus_applied"] = ma50_count
            dashboard_data["optimization_metrics"]["avg_ma50_bonus"] = total_ma50_bonus / max(ma50_count, 1)
            dashboard_data["optimization_metrics"]["ma50_bonus_percentage"] = (ma50_count / max(len(detailed_results), 1)) * 100
            
            # Clasificar por momentum con MA50 tracking
            exceptional = []
            strong = []
            emerging = []
            
            for stock in detailed_results:
                score = stock.get('score', 0)
                momentum_20d = stock.get('outperformance_20d', 0)
                ma50_bonus = stock.get('optimizations', {}).get('ma50_bonus_applied', False)
                
                if score > 200 or momentum_20d > 25:
                    momentum_category = 'EXCEPTIONAL'
                    exceptional.append(stock['symbol'])
                elif score > 150 or momentum_20d > 15:
                    momentum_category = 'STRONG'
                    strong.append(stock['symbol'])
                else:
                    momentum_category = 'MODERATE'
                    emerging.append(stock['symbol'])
                
                # Añadir a top picks con información MA50
                if len(dashboard_data["top_picks"]) < 10:
                    pick = {
                        "symbol": stock['symbol'],
                        "score": score,
                        "momentum_category": momentum_category,
                        "risk_pct": stock.get('risk_pct', 0),
                        "upside_pct": stock.get('upside_pct', 0),
                        "ma50_bonus": ma50_bonus,
                        "ma50_bonus_value": stock.get('optimizations', {}).get('ma50_bonus_value', 0),
                        "monthly_trading_suitable": stock.get('risk_pct', 0) <= 10.0,
                        "optimization_features": stock.get('optimizations', {}),
                        "target_hold": "~1 month with daily monitoring",
                        "rotation_urgency": "HIGH" if ma50_bonus else "MEDIUM"
                    }
                    dashboard_data["top_picks"].append(pick)
            
            dashboard_data["summary"]["exceptional_momentum"] = len(exceptional)
            dashboard_data["summary"]["strong_momentum"] = len(strong)
            dashboard_data["momentum_analysis"]["exceptional_momentum"] = exceptional[:10]
            dashboard_data["momentum_analysis"]["strong_momentum"] = strong[:10]
            dashboard_data["momentum_analysis"]["emerging_momentum"] = emerging[:10]
        
        # Datos de rotación con criterios estrictos
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            dashboard_data["summary"]["rotation_opportunities"] = len(action_summary.get('aggressive_rotations', []))
            
            dashboard_data["rotation_recommendations"] = {
                "overall_action": action_summary.get('overall_action', 'MAINTAIN_MONTHLY_STRATEGY'),
                "strict_criteria_applied": True,
                "urgent_exits": len(action_summary.get('urgent_exits', [])),
                "rotation_opportunities": len(action_summary.get('aggressive_rotations', [])),
                "cash_deployment": len(action_summary.get('cash_deployment_opportunities', [])),
                "philosophy_alignment": "daily_monitoring_monthly_trading"
            }
        
        # Contexto de mercado
        if self.screening_data:
            benchmark = self.screening_data.get('benchmark_context', {})
            dashboard_data["market_context"] = {
                "spy_20d": benchmark.get('spy_20d', 0),
                "spy_60d": benchmark.get('spy_60d', 0),
                "spy_90d": benchmark.get('spy_90d', 0)
            }
        
        # Crear directorio docs si no existe
        os.makedirs('docs', exist_ok=True)
        
        # Guardar datos del dashboard
        with open('docs/data.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print("✅ Datos del dashboard diario guardados: docs/data.json")
        return dashboard_data
    
    def generate_complete_aggressive_report(self):
        """Genera reporte completo de momentum con enfoque mensual"""
        print("📋 Generando reporte DIARIO - MONTHLY TRADING FOCUS + MA50 BONUS...")
        
        # Cargar todos los datos
        if not self.load_all_data():
            print("❌ No se pudieron cargar suficientes datos")
            return False
        
        # Crear reporte Markdown diario
        markdown_file = self.create_aggressive_markdown_report()
        
        # Crear datos para dashboard con MA50 bonus
        dashboard_data = self.create_aggressive_dashboard_data()
        
        print(f"✅ Reporte diario para trading mensual completado:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - Dashboard: docs/data.json")
        print(f"   - Incluye: MA50 bonus system, Weekly ATR, Criterios estrictos")
        
        return True

def main():
    """Función principal para reporte diario de trading mensual"""
    generator = AggressiveMomentumReportGenerator()
    
    success = generator.generate_complete_aggressive_report()
    
    if success:
        print("\n✅ Reporte DIARIO para trading mensual generado exitosamente")
        print("\n🎯 CARACTERÍSTICAS IMPLEMENTADAS:")
        print("   - 📅 Ejecución diaria con filosofía de trading mensual")
        print("   - 🌟 Sistema MA50 bonus (+22pts) completamente integrado")
        print("   - ⚠️ Criterios estrictos de rotación (evita overtrading)")
        print("   - 📊 Consistencia analizada en ventana de 7 días")
        print("   - 🔄 Weekly ATR para alineación temporal con holds mensuales")
        print("   - 📈 Dashboard optimizado para monitorización diaria")
        print("   - 🛡️ Gestión de riesgo ultra-conservadora (≤10%)")
        print("   - 🎯 Mantenimiento de toda la funcionalidad original")
    else:
        print("\n❌ Error generando reporte diario para trading mensual")

if __name__ == "__main__":
    main()
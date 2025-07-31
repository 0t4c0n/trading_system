#!/usr/bin/env python3
"""
Aggressive Momentum Weekly Report Generator - Con análisis de momentum responsivo
Integra rotación mensual, momentum categories, y gestión agresiva
🆕 INCLUYE GESTIÓN AUTOMÁTICA DE HISTORIAL
🔧 ACTUALIZADO: Soporte para Weekly ATR, Stop Loss restrictivo, Fundamentales estrictos
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
                print("✓ Datos de screening agresivo cargados")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando screening: {e}")
        
        # Cargar consistency analysis
        try:
            with open('consistency_analysis.json', 'r') as f:
                self.consistency_data = json.load(f)
                print("✓ Análisis de consistencia cargado")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando consistencia: {e}")
        
        # Cargar rotation recommendations (ahora agresivas)
        try:
            with open('rotation_recommendations.json', 'r') as f:
                self.rotation_data = json.load(f)
                print("✓ Recomendaciones de rotación agresiva cargadas")
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
            # Header agresivo
            f.write(f"# ⚡ MOMENTUM AGRESIVO - WEEKLY ATR OPTIMIZED - {self.report_date.strftime('%d %B %Y')}\n\n")
            
            # Resumen ejecutivo agresivo
            self.write_aggressive_executive_summary(f)
            
            # 🆕 Sección de optimizaciones aplicadas
            self.write_optimizations_applied_section(f)
            
            # Filosofía de momentum agresivo
            self.write_momentum_philosophy(f)
            
            # Top picks con momentum categories
            if self.screening_data:
                self.write_momentum_picks_with_categories(f)
            
            # Análisis de momentum responsivo
            if self.screening_data:
                self.write_momentum_responsive_analysis(f)
            
            # Rotación agresiva
            if self.rotation_data:
                self.write_aggressive_rotation_section(f)
            
            # Consistency con momentum focus
            if self.consistency_data:
                self.write_momentum_consistency_section(f)
            
            # 🆕 Sección Weekly ATR vs Daily ATR
            self.write_atr_analysis_section(f)
            
            # Gestión agresiva de momentum
            self.write_aggressive_momentum_management(f)
            
            # Contexto de mercado
            self.write_momentum_market_context(f)
            
            # Footer
            f.write(f"\n---\n\n")
            f.write(f"**Generado automáticamente:** {self.report_date.isoformat()}\n")
            f.write(f"**Próximo análisis:** {(self.report_date + timedelta(days=7)).strftime('%d %B %Y')}\n")
            f.write(f"**Estrategia:** Momentum agresivo con rotación mensual + Weekly ATR optimization\n\n")
            f.write(f"⚡ *Aggressive Momentum Trading Bot - Weekly ATR Optimized by 0t4c0n*\n")
        
        print(f"✅ Reporte Markdown agresivo creado: {report_filename}")
        return report_filename
    
    def write_optimizations_applied_section(self, f):
        """🆕 Nueva sección: Optimizaciones aplicadas"""
        f.write("## 🔧 **OPTIMIZACIONES APLICADAS**\n\n")
        
        improvements = {}
        stats = {}
        
        if self.screening_data:
            improvements = self.screening_data.get('momentum_optimization', {})
            stats = self.screening_data.get('momentum_responsive_stats', {})
        
        f.write("### **📊 Weekly ATR Optimization**\n\n")
        if improvements.get('weekly_atr_take_profit', False):
            f.write("✅ **IMPLEMENTADO:** Take profit targets ahora usan Weekly ATR\n")
            f.write("- **Beneficio:** Mejor alineación con holding period de ~1 mes\n")
            f.write("- **Multiplicadores ajustados:** 3.0x/2.5x/2.0x (vs 4.5x/4.0x/3.5x daily)\n")
            
            avg_weekly = stats.get('avg_weekly_atr', 0)
            avg_daily = stats.get('avg_daily_atr', 0)
            if avg_weekly > 0 and avg_daily > 0:
                ratio = avg_weekly / avg_daily
                f.write(f"- **ATR promedio:** Weekly {avg_weekly:.2f} vs Daily {avg_daily:.2f} (ratio {ratio:.1f}x)\n")
        else:
            f.write("⚠️ **NO DETECTADO:** Sistema usando Daily ATR tradicional\n")
        
        f.write("\n### **🛡️ Stop Loss Restrictivo**\n\n")
        if improvements.get('min_stop_loss_restrictive', False):
            f.write("✅ **IMPLEMENTADO:** Lógica de priorización más restrictiva\n")
            f.write("- **Nueva priorización:** MA50 → MA21 → otros → 8% fallback\n")
            f.write("- **Beneficio:** Filtrado de riesgo más estricto (menos acciones de alto riesgo)\n")
            
            avg_risk = stats.get('avg_risk', 0)
            f.write(f"- **Riesgo promedio resultante:** {avg_risk:.1f}%\n")
        else:
            f.write("⚠️ **NO DETECTADO:** Stop loss usando lógica estándar\n")
        
        f.write("\n### **📈 Filtros Fundamentales Estrictos**\n\n")
        positive_earnings_count = stats.get('positive_earnings_count', 0)
        total_results = len(self.screening_data.get('detailed_results', [])) if self.screening_data else 0
        
        if positive_earnings_count == total_results and total_results > 0:
            f.write("✅ **IMPLEMENTADO:** Solo acciones con beneficios positivos\n")
            f.write(f"- **Verificado:** {positive_earnings_count}/{total_results} acciones con earnings positivos\n")
            f.write("- **Beneficio:** Mayor calidad fundamental de las selecciones\n")
        else:
            f.write("⚠️ **PARCIAL O NO IMPLEMENTADO:** Algunos resultados sin beneficios positivos\n")
            f.write(f"- **Estado:** {positive_earnings_count}/{total_results} con earnings positivos\n")
        
        f.write("\n### **⚡ Impacto General**\n\n")
        f.write("- **Precisión:** Mejor alineación temporal entre análisis técnico y fundamental\n")
        f.write("- **Calidad:** Filtrado más estricto = menor cantidad pero mayor calidad\n")
        f.write("- **Consistencia:** Weekly ATR + fundamentales sólidos + stops restrictivos\n")
        f.write("- **Target:** Optimizado para holds de 1 mes con rotación activa\n\n")
    
    def write_atr_analysis_section(self, f):
        """🆕 Nueva sección: Análisis comparativo ATR"""
        f.write("## 📊 **ANÁLISIS ATR: WEEKLY vs DAILY**\n\n")
        
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
        
        f.write(f"### **📈 Estadísticas ATR del Portfolio**\n\n")
        f.write(f"- **Weekly ATR promedio:** {avg_weekly:.2f}\n")
        f.write(f"- **Daily ATR promedio:** {avg_daily:.2f}\n")
        f.write(f"- **Ratio Weekly/Daily:** {avg_ratio:.1f}x\n")
        f.write(f"- **Acciones con Weekly ATR:** {len(weekly_atrs)}/{len(detailed_results)}\n\n")
        
        f.write(f"### **🎯 Impacto en Take Profit Targets**\n\n")
        
        # Análisis de take profit improvements
        high_upside_weekly = len([r for r in detailed_results 
                                if r.get('weekly_atr', 0) > 0 and r.get('upside_pct', 0) > 30])
        total_with_weekly = len([r for r in detailed_results if r.get('weekly_atr', 0) > 0])
        
        if total_with_weekly > 0:
            f.write(f"- **Acciones con upside >30%:** {high_upside_weekly}/{total_with_weekly} ({high_upside_weekly/total_with_weekly*100:.1f}%)\n")
        
        # Mostrar ejemplos específicos
        f.write(f"\n### **📋 Ejemplos ATR Top 5**\n\n")
        f.write("| Símbolo | Weekly ATR | Daily ATR | Ratio | Take Profit Method | Upside % |\n")
        f.write("|---------|------------|-----------|-------|-------------------|----------|\n")
        
        for i, stock in enumerate(detailed_results[:5]):
            symbol = stock.get('symbol', 'N/A')
            weekly_atr = stock.get('weekly_atr', 0)
            daily_atr = stock.get('atr', 0)
            ratio = weekly_atr / daily_atr if daily_atr > 0 else 0
            tp_method = stock.get('take_profit_analysis', {}).get('primary_method', 'N/A')
            upside = stock.get('upside_pct', 0)
            
            # Truncar método si es muy largo
            if len(tp_method) > 20:
                tp_method = tp_method[:17] + "..."
            
            f.write(f"| **{symbol}** | {weekly_atr:.2f} | {daily_atr:.2f} | {ratio:.1f}x | {tp_method} | {upside:.1f}% |\n")
        
        f.write(f"\n### **💡 Conclusiones del Análisis ATR**\n\n")
        
        if avg_ratio > 2.0:
            f.write("- **Weekly ATR significativamente mayor:** Justifica multiplicadores más conservadores\n")
        elif avg_ratio > 1.5:
            f.write("- **Weekly ATR moderadamente mayor:** Alineación apropiada con timeframe mensual\n")
        else:
            f.write("- **Weekly ATR similar a Daily:** Podría indicar volatilidad consistente\n")
        
        f.write("- **Beneficio principal:** Targets alineados con patrones de volatilidad semanal\n")
        f.write("- **Resultado esperado:** Mejor hit rate en take profits para holds de 1 mes\n\n")
    
    def write_aggressive_executive_summary(self, f):
        """Escribe resumen ejecutivo de momentum agresivo con optimizaciones"""
        f.write("## ⚡ **RESUMEN EJECUTIVO - MOMENTUM AGRESIVO OPTIMIZADO**\n\n")
        
        # Detectar nivel de agresividad
        exceptional_count = 0
        strong_count = 0
        avg_momentum_20d = 0
        avg_rr_ratio = 0
        urgent_rotations = 0
        
        # 🆕 Métricas de optimización
        avg_weekly_atr = 0
        avg_daily_atr = 0
        positive_earnings_count = 0
        
        if self.screening_data and self.screening_data.get('detailed_results'):
            results = self.screening_data['detailed_results']
            if results:
                # Clasificar por momentum
                for stock in results:
                    momentum_20d = stock.get('outperformance_20d', 0)
                    score = stock.get('score', 0)
                    
                    if score > 200 or momentum_20d > 25:
                        exceptional_count += 1
                    elif score > 150 or momentum_20d > 15:
                        strong_count += 1
                
                avg_momentum_20d = sum(r.get('outperformance_20d', 0) for r in results) / len(results)
                avg_rr_ratio = sum(r.get('risk_reward_ratio', 0) for r in results) / len(results)
                
                # 🆕 Métricas de optimización
                weekly_atrs = [r.get('weekly_atr', 0) for r in results if r.get('weekly_atr', 0) > 0]
                daily_atrs = [r.get('atr', 0) for r in results if r.get('atr', 0) > 0]
                
                if weekly_atrs:
                    avg_weekly_atr = sum(weekly_atrs) / len(weekly_atrs)
                if daily_atrs:
                    avg_daily_atr = sum(daily_atrs) / len(daily_atrs)
                
                # Contar earnings positivos
                positive_earnings_count = len([r for r in results 
                                             if r.get('fundamental_data', {}).get('quarterly_earnings_positive', False)])
        
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            overall_action = action_summary.get('overall_action', 'NO_DATA')
            urgent_rotations = len(action_summary.get('aggressive_rotations', []))
            
            if overall_action == 'URGENT_PORTFOLIO_ROTATION':
                f.write("### 🚨 **ROTACIÓN URGENTE DE CARTERA - MOMENTUM EXCEPCIONAL DETECTADO**\n\n")
            elif overall_action == 'AGGRESSIVE_ROTATION_REQUIRED':
                f.write("### ⚡ **ROTACIÓN AGRESIVA REQUERIDA - OPORTUNIDADES DE MOMENTUM**\n\n")
            elif overall_action == 'EVALUATE_MOMENTUM_OPPORTUNITIES':
                f.write("### 🔍 **EVALUAR OPORTUNIDADES - MOMENTUM EMERGENTE**\n\n")
            else:
                f.write("### 👀 **MANTENER CON VIGILANCIA - MOMENTUM ESTABLE**\n\n")
        
        # Métricas clave de momentum
        f.write(f"**🎯 FILOSOFÍA:** Swing for the Fences - Rotación mensual con Weekly ATR optimization\n\n")
        f.write(f"- **Momentum excepcional detectado:** {exceptional_count} acciones (rotación urgente)\n")
        f.write(f"- **Momentum fuerte identificado:** {strong_count} acciones (rotación agresiva)\n")
        f.write(f"- **Rotaciones urgentes recomendadas:** {urgent_rotations}\n")
        f.write(f"- **Momentum 20d promedio:** {avg_momentum_20d:.1f}% (peso 70% en scoring)\n")
        f.write(f"- **R/R promedio:** {avg_rr_ratio:.1f}:1 (targets optimizados con Weekly ATR)\n")
        f.write(f"- **Target hold period:** ~1 mes (vs 2-3 meses conservador)\n\n")
        
        # 🆕 Métricas de optimización
        f.write(f"**🔧 OPTIMIZACIONES APLICADAS:**\n")
        if avg_weekly_atr > 0 and avg_daily_atr > 0:
            atr_ratio = avg_weekly_atr / avg_daily_atr
            f.write(f"- **Weekly ATR optimization:** {avg_weekly_atr:.2f} vs Daily {avg_daily_atr:.2f} (ratio {atr_ratio:.1f}x)\n")
        else:
            f.write(f"- **Weekly ATR optimization:** Detectando implementación...\n")
        
        total_results = len(self.screening_data.get('detailed_results', [])) if self.screening_data else 0
        if total_results > 0:
            earnings_pct = (positive_earnings_count / total_results) * 100
            f.write(f"- **Filtros fundamentales estrictos:** {positive_earnings_count}/{total_results} ({earnings_pct:.0f}%) con beneficios positivos\n")
        
        f.write(f"- **Stop loss restrictivo:** Priorización MA50 → MA21 → otros para menor riesgo promedio\n\n")
        
        f.write(f"**⚖️ BALANCE RIESGO/MOMENTUM OPTIMIZADO:**\n")
        f.write(f"- Rotación agresiva hacia momentum superior con Weekly ATR alignment\n")
        f.write(f"- Salida rápida si momentum se debilita (1+ semanas ausencia)\n")
        f.write(f"- Targets adaptativos según volatilidad semanal vs diaria\n")
        f.write(f"- Solo acciones con fundamentales sólidos (earnings positivos)\n\n")
    
    def write_momentum_philosophy(self, f):
        """Escribe la filosofía de momentum agresivo actualizada"""
        f.write("## 🎯 **FILOSOFÍA: SWING FOR THE FENCES - WEEKLY ATR OPTIMIZED**\n\n")
        
        f.write("### **🚀 Evolución: Optimization Stack Implementado**\n\n")
        f.write("El sistema ha implementado un **stack de optimizaciones** para momentum trading agresivo ")
        f.write("con rotación mensual. El objetivo es capturar las mejores oportunidades con **alineación temporal mejorada** ")
        f.write("entre análisis técnico y fundamental.\n\n")
        
        f.write("### **📊 Pesos de Momentum Actualizados:**\n\n")
        f.write("| Timeframe | Peso | Optimización | Razón |\n")
        f.write("|-----------|------|--------------|-------|\n")
        f.write("| **Momentum 20d** | **70%** | Aceleración detection | Momentum reciente más predictivo |\n")
        f.write("| **Momentum 60d** | **30%** | Contexto de tendencia | Validación de medio plazo |\n")
        f.write("| **Momentum 90d** | **0%** | Eliminado | Demasiado lento para rotación mensual |\n\n")
        
        f.write("### **🔧 Stack de Optimizaciones Técnicas:**\n\n")
        f.write("#### **📊 1. Weekly ATR for Take Profit**\n")
        f.write("- **Problema resuelto:** Daily ATR no se alinea con holds de 1 mes\n")  
        f.write("- **Solución:** Weekly ATR con multiplicadores ajustados (3.0x/2.5x/2.0x)\n")
        f.write("- **Beneficio:** Targets alineados con patrones de volatilidad semanal\n\n")
        
        f.write("#### **🛡️ 2. Min Stop Loss Restrictivo**\n")
        f.write("- **Problema resuelto:** Stops demasiado amplios pasaban filtro de 10%\n")
        f.write("- **Solución:** Priorización MA50 → MA21 → otros → 8% fallback\n")
        f.write("- **Beneficio:** Filtrado más estricto = menor cantidad pero mayor calidad\n\n")
        
        f.write("#### **📈 3. Fundamentales Solo Positivos**\n")
        f.write("- **Problema resuelto:** Acciones con earnings negativos diluían calidad\n")
        f.write("- **Solución:** Filtro estricto: solo quarterly_earnings_positive = true\n")
        f.write("- **Beneficio:** Mayor probabilidad de sostenibilidad del momentum\n\n")
        
        f.write("### **🎪 Categorías de Momentum Mejoradas:**\n\n")
        f.write("- **🔥 EXCEPCIONAL** (Score >200 OR Momentum 20d >25%): Rotación urgente + Weekly ATR 3.0x\n")
        f.write("- **⚡ FUERTE** (Score >150 OR Momentum 20d >15%): Rotación agresiva + Weekly ATR 2.5x\n")
        f.write("- **📈 MODERADO** (Score >100 OR Momentum 20d >8%): Vigilar evolución + Weekly ATR 2.0x\n")
        f.write("- **⚠️ DÉBIL** (Score <100): No rotar, considerar salida\n\n")
        
        if self.rotation_data:
            params = self.rotation_data.get('aggressive_parameters', {})
            f.write("### **🔧 Parámetros Agresivos Optimizados:**\n\n")
            f.write(f"- **Threshold de rotación:** {params.get('rotation_threshold', '20% score superior')}\n")
            f.write(f"- **Consistencia mínima:** {params.get('min_consistency_weeks', 2)} semanas (vs 5 conservador)\n")
            f.write(f"- **Peso oportunidades emergentes:** {params.get('emerging_opportunity_weight', 1.5)}x\n")
            f.write(f"- **Threshold deterioro momentum:** {params.get('momentum_decay_threshold', '15%')}\n")
            f.write(f"- **Weekly ATR multipliers:** 3.0x/2.5x/2.0x (ajustados para volatilidad semanal)\n")
            f.write(f"- **Stop loss priority:** MA50 → MA21 → ATR/Support → 8% fallback\n\n")
    
    def write_momentum_picks_with_categories(self, f):
        """Escribe top picks con categorías de momentum y optimizaciones"""
        f.write("## 🔥 **TOP MOMENTUM PICKS - WEEKLY ATR OPTIMIZED**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        
        if detailed_results:
            # Clasificar por categorías de momentum
            exceptional = []
            strong = []
            moderate = []
            
            for stock in detailed_results[:10]:
                score = stock.get('score', 0)
                momentum_20d = stock.get('outperformance_20d', 0)
                
                if score > 200 or momentum_20d > 25:
                    exceptional.append(stock)
                elif score > 150 or momentum_20d > 15:
                    strong.append(stock)
                else:
                    moderate.append(stock)
            
            # Momentum EXCEPCIONAL
            if exceptional:
                f.write("### 🔥 **MOMENTUM EXCEPCIONAL - ROTACIÓN URGENTE + WEEKLY ATR 3.0x**\n\n")
                f.write("*Estas acciones muestran momentum excepcional con optimizaciones aplicadas.*\n\n")
                
                for i, stock in enumerate(exceptional):
                    self.write_optimized_stock_detail(f, stock, i+1, "EXCEPCIONAL")
                f.write("\n")
            
            # Momentum FUERTE
            if strong:
                f.write("### ⚡ **MOMENTUM FUERTE - ROTACIÓN AGRESIVA + WEEKLY ATR 2.5x**\n\n")
                f.write("*Candidatos sólidos para rotación agresiva con optimizaciones técnicas.*\n\n")
                
                for i, stock in enumerate(strong):
                    self.write_optimized_stock_detail(f, stock, i+1, "FUERTE")
                f.write("\n")
            
            # Momentum MODERADO
            if moderate:
                f.write("### 📈 **MOMENTUM MODERADO - VIGILAR + WEEKLY ATR 2.0x**\n\n")
                f.write("*Momentum aceptable con optimizaciones conservadoras aplicadas.*\n\n")
                
                for i, stock in enumerate(moderate[:3]):  # Solo top 3
                    self.write_optimized_stock_detail(f, stock, i+1, "MODERADO")
                f.write("\n")
    
    def write_optimized_stock_detail(self, f, stock, rank, category):
        """🆕 Escribe detalle de stock con información de optimizaciones"""
        symbol = stock.get('symbol', 'N/A')
        current_price = stock.get('current_price', 0)
        take_profit = stock.get('take_profit', 0)
        stop_loss = stock.get('stop_loss', 0)
        
        # Scores
        final_score = stock.get('score', 0)
        technical_score = stock.get('technical_score', 0)
        rr_bonus = stock.get('rr_bonus', 0)
        
        # Momentum metrics
        momentum_20d = stock.get('outperformance_20d', 0)
        momentum_60d = stock.get('outperformance_60d', 0)
        risk_reward = stock.get('risk_reward_ratio', 0)
        upside_pct = stock.get('upside_pct', 0)
        
        # 🆕 Optimizaciones metrics
        weekly_atr = stock.get('weekly_atr', 0)
        daily_atr = stock.get('atr', 0)
        atr_ratio = weekly_atr / daily_atr if daily_atr > 0 else 0
        
        # Fundamental data
        fundamental_data = stock.get('fundamental_data', {})
        earnings_positive = fundamental_data.get('quarterly_earnings_positive', False)
        
        # Stop analysis
        stop_analysis = stock.get('stop_analysis', {})
        stop_method = stop_analysis.get('stop_selection', 'unknown')
        
        # Take profit analysis
        tp_analysis = stock.get('take_profit_analysis', {})
        atr_multiplier = tp_analysis.get('atr_multiplier_used', 0)
        tp_method = tp_analysis.get('primary_method', 'unknown')
        
        f.write(f"#### **{rank}. {symbol}** - Momentum {category} 🔧 OPTIMIZED\n\n")
        
        # Info básica
        company_name = stock.get('company_info', {}).get('name', 'N/A')[:40]
        sector = stock.get('company_info', {}).get('sector', 'N/A')
        f.write(f"**Empresa:** {company_name}\n")
        f.write(f"**Sector:** {sector}\n\n")
        
        # Scoring breakdown
        f.write(f"**📊 SCORING AGRESIVO:**\n")
        f.write(f"- **Score Final:** {final_score:.1f} (Técnico: {technical_score:.1f} + R/R Bonus: {rr_bonus:.1f})\n")
        f.write(f"- **Categoría Momentum:** {category}\n")
        f.write(f"- **Risk/Reward:** {risk_reward:.1f}:1\n\n")
        
        # 🆕 Optimizaciones aplicadas
        f.write(f"**🔧 OPTIMIZACIONES APLICADAS:**\n")
        f.write(f"- **Weekly ATR:** {weekly_atr:.2f} vs Daily ATR: {daily_atr:.2f} (ratio {atr_ratio:.1f}x)\n")
        f.write(f"- **Take Profit Method:** {tp_method} (multiplier {atr_multiplier}x)\n")
        f.write(f"- **Stop Loss Method:** {stop_method}\n")
        f.write(f"- **Fundamentales:** Earnings {'✅ POSITIVOS' if earnings_positive else '❌ NEGATIVOS'}\n\n")
        
        # Momentum analysis (peso 70% + 30%)
        f.write(f"**⚡ ANÁLISIS DE MOMENTUM:**\n")
        f.write(f"- **Momentum 20d:** +{momentum_20d:.1f}% vs SPY *(peso 70%)*\n")
        f.write(f"- **Momentum 60d:** +{momentum_60d:.1f}% vs SPY *(peso 30%)*\n")
        
        # Calcular momentum score total
        momentum_score = (momentum_20d * 0.7) + (momentum_60d * 0.3)
        f.write(f"- **Momentum Score Ponderado:** {momentum_score:.1f}%\n")
        
        # Trading levels agresivos
        f.write(f"- **Precio actual:** ${current_price:.2f}\n")
        f.write(f"- **Target optimizado:** ${take_profit:.2f} ({upside_pct:.1f}% upside)\n")
        f.write(f"- **Stop loss restrictivo:** ${stop_loss:.2f}\n\n")
        
        # Recomendación de rotación
        if category == "EXCEPCIONAL":
            f.write(f"**🚨 ACCIÓN:** Rotación urgente recomendada - Momentum excepcional con Weekly ATR 3.0x\n")
        elif category == "FUERTE":
            f.write(f"**⚡ ACCIÓN:** Rotación agresiva recomendada - Momentum sólido con Weekly ATR 2.5x\n")
        else:
            f.write(f"**👁️ ACCIÓN:** Vigilar evolución - Weekly ATR 2.0x aplicado\n")
        
        # Target hold
        f.write(f"**🎯 Target Hold:** ~1 mes (rotación mensual con optimizaciones)\n\n")
        
        f.write("---\n\n")
    
    def write_momentum_responsive_analysis(self, f):
        """Escribe análisis de screening con enfoque en optimizaciones"""
        f.write("## 📊 **ANÁLISIS MOMENTUM RESPONSIVO - OPTIMIZED STACK**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        methodology = self.screening_data.get('methodology', {})
        
        f.write(f"**Acciones analizadas:** {len(detailed_results)}\n")
        f.write(f"**Metodología:** {methodology.get('scoring', 'Momentum responsivo con Weekly ATR optimization')}\n\n")
        
        # 🆕 Estadísticas de optimización
        if detailed_results:
            # Clasificación por momentum
            exceptional_count = len([s for s in detailed_results if s.get('score', 0) > 200 or s.get('outperformance_20d', 0) > 25])
            strong_count = len([s for s in detailed_results if 150 <= s.get('score', 0) <= 200 or 15 <= s.get('outperformance_20d', 0) <= 25])
            moderate_count = len(detailed_results) - exceptional_count - strong_count
            
            f.write(f"### 🔥 **DISTRIBUCIÓN DE MOMENTUM:**\n\n")
            f.write(f"- **Excepcional:** {exceptional_count} acciones ({(exceptional_count/len(detailed_results)*100):.1f}%)\n")
            f.write(f"- **Fuerte:** {strong_count} acciones ({(strong_count/len(detailed_results)*100):.1f}%)\n")
            f.write(f"- **Moderado:** {moderate_count} acciones ({(moderate_count/len(detailed_results)*100):.1f}%)\n\n")
            
            # 🆕 Métricas de optimización
            weekly_atrs = [r.get('weekly_atr', 0) for r in detailed_results if r.get('weekly_atr', 0) > 0]
            daily_atrs = [r.get('atr', 0) for r in detailed_results if r.get('atr', 0) > 0]
            positive_earnings = len([r for r in detailed_results 
                                   if r.get('fundamental_data', {}).get('quarterly_earnings_positive', False)])
            
            f.write(f"### 🔧 **ESTADÍSTICAS DE OPTIMIZACIÓN:**\n\n")
            
            if weekly_atrs and daily_atrs:
                avg_weekly = sum(weekly_atrs) / len(weekly_atrs)
                avg_daily = sum(daily_atrs) / len(daily_atrs)
                avg_ratio = avg_weekly / avg_daily
                
                f.write(f"- **Weekly ATR implementado:** {len(weekly_atrs)}/{len(detailed_results)} acciones\n")
                f.write(f"- **Weekly ATR promedio:** {avg_weekly:.2f}\n")
                f.write(f"- **Daily ATR promedio:** {avg_daily:.2f}\n")
                f.write(f"- **Ratio Weekly/Daily:** {avg_ratio:.1f}x\n")
            else:
                f.write(f"- **Weekly ATR:** No implementado en esta ejecución\n")
            
            f.write(f"- **Earnings positivos:** {positive_earnings}/{len(detailed_results)} ({(positive_earnings/len(detailed_results)*100):.1f}%)\n")
            
            # Stop loss methods
            stop_methods = {}
            for r in detailed_results:
                method = r.get('stop_analysis', {}).get('stop_selection', 'unknown')
                stop_methods[method] = stop_methods.get(method, 0) + 1
            
            if stop_methods:
                f.write(f"- **Stop Loss Methods:** {', '.join([f'{k}: {v}' for k, v in stop_methods.items()])}\n")
            
            f.write(f"\n")
            
            # Métricas promedio tradicionales
            avg_momentum_20d = sum(r.get('outperformance_20d', 0) for r in detailed_results) / len(detailed_results)
            avg_momentum_60d = sum(r.get('outperformance_60d', 0) for r in detailed_results) / len(detailed_results)
            avg_rr = sum(r.get('risk_reward_ratio', 0) for r in detailed_results) / len(detailed_results)
            avg_upside = sum(r.get('upside_pct', 0) for r in detailed_results) / len(detailed_results)
            
            f.write(f"### 📈 **MÉTRICAS MOMENTUM PROMEDIO:**\n\n")
            f.write(f"- **Momentum 20d promedio:** {avg_momentum_20d:.1f}% (peso 70%)\n")
            f.write(f"- **Momentum 60d promedio:** {avg_momentum_60d:.1f}% (peso 30%)\n")
            f.write(f"- **Risk/Reward promedio:** {avg_rr:.1f}:1 (targets optimizados)\n")
            f.write(f"- **Upside promedio:** {avg_upside:.1f}% (~1 mes objetivo optimizado)\n\n")
        
        # Top 10 con métricas de optimización
        if detailed_results:
            f.write("### ⚡ **TOP 10 MOMENTUM RANKING - OPTIMIZED**\n\n")
            f.write("| Rank | Símbolo | Score Final | Mom 20d | Mom 60d | R/R | Weekly ATR | Earnings | Categoría |\n")
            f.write("|------|---------|-------------|---------|---------|-----|------------|----------|----------|\n")
            
            for i, stock in enumerate(detailed_results[:10]):
                symbol = stock.get('symbol', 'N/A')
                score = stock.get('score', 0)
                mom_20d = stock.get('outperformance_20d', 0)
                mom_60d = stock.get('outperformance_60d', 0)
                rr = stock.get('risk_reward_ratio', 0)
                weekly_atr = stock.get('weekly_atr', 0)
                earnings = '✅' if stock.get('fundamental_data', {}).get('quarterly_earnings_positive', False) else '❌'
                
                # Determinar categoría
                if score > 200 or mom_20d > 25:
                    category = "🔥 EXCEPCIONAL"
                elif score > 150 or mom_20d > 15:
                    category = "⚡ FUERTE"
                else:
                    category = "📈 MODERADO"
                
                f.write(f"| {i+1} | **{symbol}** | {score:.1f} | +{mom_20d:.1f}% | +{mom_60d:.1f}% | {rr:.1f}:1 | {weekly_atr:.2f} | {earnings} | {category} |\n")
            
            f.write("\n")
    
    def write_aggressive_rotation_section(self, f):
        """Escribe sección de rotación agresiva"""
        f.write("## 🎯 **ROTACIÓN AGRESIVA DE MOMENTUM**\n\n")
        
        if not self.rotation_data:
            f.write("*No hay datos de rotación disponibles*\n\n")
            return
        
        action_summary = self.rotation_data.get('action_summary', {})
        overall_action = action_summary.get('overall_action', 'NO_ACTION')
        
        # Mostrar acción general
        action_descriptions = {
            'URGENT_PORTFOLIO_ROTATION': '🚨 **ROTACIÓN URGENTE DE CARTERA**',
            'AGGRESSIVE_ROTATION_REQUIRED': '⚡ **ROTACIÓN AGRESIVA REQUERIDA**',
            'EVALUATE_MOMENTUM_OPPORTUNITIES': '🔍 **EVALUAR OPORTUNIDADES DE MOMENTUM**',
            'MAINTAIN_WITH_VIGILANCE': '👀 **MANTENER CON VIGILANCIA**'
        }
        
        f.write(f"### {action_descriptions.get(overall_action, overall_action)}\n\n")
        
        # Filosofía de rotación
        rotation_philosophy = self.rotation_data.get('rotation_philosophy', 'momentum_responsive')
        if rotation_philosophy == 'swing_for_fences_monthly_rotation':
            f.write("**Filosofía:** Swing for the Fences - Rotación mensual hacia mejores oportunidades de momentum\n\n")
        
        # Rotaciones agresivas
        aggressive_rotations = action_summary.get('aggressive_rotations', [])
        if aggressive_rotations:
            f.write("### ⚡ **ROTACIONES AGRESIVAS INMEDIATAS**\n\n")
            f.write("*Oportunidades de momentum superior - Ejecutar rotación inmediatamente*\n\n")
            
            for rotation in aggressive_rotations:
                if isinstance(rotation, dict):
                    symbol = rotation.get('symbol', 'N/A')
                    reason = rotation.get('reason', 'Momentum superior detectado')
                    urgency = rotation.get('urgency', 'HIGH')
                    momentum_cat = rotation.get('momentum_category', 'UNKNOWN')
                    replace = rotation.get('replace_position', '')
                    
                    f.write(f"#### **🔥 {symbol}** - {urgency}\n")
                    f.write(f"**Razón:** {reason}\n")
                    f.write(f"**Categoría Momentum:** {momentum_cat}\n")
                    if replace:
                        f.write(f"**Reemplazar:** {replace}\n")
                    f.write(f"**Target Hold:** ~1 mes\n\n")
                else:
                    f.write(f"- **{rotation}** - Momentum superior detectado\n")
            f.write("\n")
        
        # Salidas urgentes
        urgent_exits = action_summary.get('urgent_exits', [])
        if urgent_exits:
            f.write("### 🚨 **SALIDAS URGENTES**\n\n")
            f.write("*Momentum perdido - Salir inmediatamente*\n\n")
            
            for exit in urgent_exits:
                if isinstance(exit, dict):
                    symbol = exit.get('symbol', 'N/A')
                    reason = exit.get('reason', 'Momentum perdido')
                    urgency = exit.get('urgency', 'URGENT')
                    
                    f.write(f"- **❌ {symbol}** ({urgency}): {reason}\n")
                else:
                    f.write(f"- **❌ {exit}** - Momentum perdido\n")
            f.write("\n")
        
        # Oportunidades emergentes
        emerging_opportunities = action_summary.get('emerging_opportunities', [])
        if emerging_opportunities:
            f.write("### 🌱 **OPORTUNIDADES EMERGENTES**\n\n")
            f.write("*Momentum emergente - Vigilar para próxima rotación*\n\n")
            
            for opp in emerging_opportunities:
                if isinstance(opp, dict):
                    symbol = opp.get('symbol', 'N/A')
                    reason = opp.get('reason', 'Momentum emergente')
                    momentum_cat = opp.get('momentum_category', 'EMERGING')
                    weeks = opp.get('consistency_weeks', 0)
                    
                    f.write(f"- **🌱 {symbol}** ({momentum_cat}): {reason} - {weeks} semanas consistencia\n")
                else:
                    f.write(f"- **🌱 {opp}** - Momentum emergente prometedor\n")
            f.write("\n")
        
        # Recomendaciones detalladas
        detailed_recommendations = action_summary.get('detailed_recommendations', [])
        if detailed_recommendations:
            f.write("### 📋 **RECOMENDACIONES DETALLADAS**\n\n")
            
            for rec in detailed_recommendations[:5]:  # Top 5
                symbol = rec.get('symbol', 'N/A')
                action = rec.get('action', 'UNKNOWN')
                reason = rec.get('reason', '')
                urgency = rec.get('urgency', 'MEDIUM')
                momentum_cat = rec.get('momentum_category', 'UNKNOWN')
                
                action_emoji = {
                    'URGENT_ROTATION': '🚨',
                    'AGGRESSIVE_ROTATION_HIGH': '⚡',
                    'AGGRESSIVE_ROTATION_URGENT': '🔥',
                    'URGENT_EXIT': '❌',
                    'CONSIDER_EXIT': '⚠️'
                }.get(action, '📊')
                
                f.write(f"**{action_emoji} {symbol}** - {action} ({urgency})\n")
                f.write(f"- **Momentum:** {momentum_cat}\n")
                f.write(f"- **Razón:** {reason}\n")
                
                if rec.get('score'):
                    f.write(f"- **Score:** {rec['score']:.1f}\n")
                if rec.get('target_upside'):
                    f.write(f"- **Target Upside:** {rec['target_upside']:.1f}%\n")
                
                f.write("\n")
    
    def write_momentum_consistency_section(self, f):
        """Escribe análisis de consistencia con enfoque en momentum"""
        f.write("## 🔥 **ANÁLISIS DE CONSISTENCIA MOMENTUM**\n\n")
        
        consistency_analysis = self.consistency_data.get('consistency_analysis', {})
        weeks_analyzed = self.consistency_data.get('weeks_analyzed', 0)
        
        f.write(f"**Período analizado:** {weeks_analyzed} semanas\n")
        f.write(f"**Enfoque:** Consistencia de momentum para rotación agresiva\n\n")
        
        # Consistent Winners con momentum
        consistent_winners = consistency_analysis.get('consistent_winners', [])
        if consistent_winners:
            f.write("### 🏆 **MOMENTUM CONSISTENTE** (4-5 semanas)\n\n")
            f.write("*Momentum establecido - Candidatos prioritarios para rotación agresiva*\n\n")
            
            for winner in consistent_winners[:5]:
                symbol = winner['symbol']
                frequency = winner['frequency']
                score = winner.get('consistency_score', 0)
                appeared = winner.get('appeared_this_week', False)
                
                status_emoji = "✅" if appeared else "⚠️"
                f.write(f"- **{symbol}** - {frequency}/{weeks_analyzed} semanas - Score: {score:.1f} - Esta semana: {status_emoji}\n")
            f.write("\n")
        
        # Strong Candidates
        strong_candidates = consistency_analysis.get('strong_candidates', [])
        if strong_candidates:
            f.write("### ⚡ **MOMENTUM FUERTE** (3 semanas)\n\n")
            f.write("*Momentum sólido - Rotación agresiva recomendada si aparece próxima semana*\n\n")
            
            for candidate in strong_candidates[:5]:
                symbol = candidate['symbol']
                frequency = candidate['frequency']
                score = candidate.get('consistency_score', 0)
                appeared = candidate.get('appeared_this_week', False)
                
                status_emoji = "✅" if appeared else "⚠️"
                f.write(f"- **{symbol}** - {frequency}/{weeks_analyzed} semanas - Score: {score:.1f} - Esta semana: {status_emoji}\n")
            f.write("\n")
        
        # Emerging Opportunities con criterios agresivos
        emerging = consistency_analysis.get('emerging_opportunities', [])
        if emerging:
            f.write("### 🌱 **MOMENTUM EMERGENTE** (2 semanas)\n\n")
            f.write("*Momentum building - Vigilar para próxima rotación si confirma*\n\n")
            
            for opp in emerging[:5]:
                symbol = opp['symbol']
                frequency = opp['frequency']
                appeared = opp.get('appeared_this_week', False)
                
                status_emoji = "🔥" if appeared else "👁️"
                f.write(f"- **{symbol}** - {frequency}/{weeks_analyzed} semanas - Esta semana: {status_emoji} {'(CONFIRMA!)' if appeared else '(vigilar)'}\n")
            f.write("\n")
        
        # Cambios de momentum
        trend_changes = self.consistency_data.get('trend_changes', {})
        newly_emerged = trend_changes.get('newly_emerged', [])
        disappeared = trend_changes.get('disappeared_this_week', [])
        
        if newly_emerged:
            f.write(f"### 🆕 **MOMENTUM NUEVO:** {', '.join(newly_emerged[:8])}\n")
            f.write("*Primera aparición - Vigilar próximas 2 semanas para confirmar momentum*\n\n")
        
        if disappeared:
            f.write(f"### 📉 **MOMENTUM PERDIDO:** {', '.join(disappeared[:8])}\n")
            f.write("*Si tienes posiciones en estas, **considerar salida inmediata** - momentum deteriorado*\n\n")
    
    def write_aggressive_momentum_management(self, f):
        """Escribe guía de gestión agresiva de momentum actualizada"""
        f.write("## ⚡ **GESTIÓN AGRESIVA DE MOMENTUM - OPTIMIZED STACK**\n\n")
        
        f.write("### 🎯 **Filosofía: Swing for the Fences + Optimizations**\n\n")
        f.write("El momentum trading agresivo optimizado requiere **rotación activa** hacia las mejores oportunidades ")
        f.write("con **alineación temporal mejorada**. Las optimizaciones implementadas mejoran la precisión ")
        f.write("de entrada y salida para holds de ~1 mes.\n\n")
        
        f.write("### 🔄 **Criterios de Rotación Mensual Optimizados:**\n\n")
        f.write("#### **🔥 ROTAR INMEDIATAMENTE (hacia momentum superior optimizado):**\n")
        f.write("- ✅ Nueva oportunidad con score 20%+ superior\n")
        f.write("- ✅ Momentum excepcional detectado (categoría EXCEPCIONAL) + Weekly ATR 3.0x\n")
        f.write("- ✅ Acceleration signals confirmados (aparece esta semana + 2+ semanas historial)\n")
        f.write("- ✅ R/R ratio >3.5:1 con momentum sólido + earnings positivos\n")
        f.write("- ✅ Weekly ATR alignment favorable (ratio >2.0x vs daily)\n\n")
        
        f.write("#### **⚡ ROTAR AGRESIVAMENTE (en 1-2 días con optimizaciones):**\n")
        f.write("- ⚠️ Momentum fuerte identificado con 3+ semanas consistencia + Weekly ATR 2.5x\n")
        f.write("- ⚠️ Posición actual perdiendo momentum (no aparece esta semana)\n")
        f.write("- ⚠️ Deterioro técnico visible (RSI divergencia, volume decay)\n")
        f.write("- ⚠️ Stop loss method cambió a menos restrictivo (ej: MA50 → ATR)\n")
        f.write("- ⚠️ Earnings se volvieron negativos en nueva data\n\n")
        
        f.write("#### **❌ SALIR INMEDIATAMENTE (triggers optimizados):**\n")
        f.write("- ❌ Ausencia 2+ semanas consecutivas (momentum perdido)\n")
        f.write("- ❌ Categoría momentum cambió a DÉBIL o inferior\n")
        f.write("- ❌ Score deterioró >15% semana a semana\n")
        f.write("- ❌ Underperformance vs SPY por 2+ semanas\n")
        f.write("- ❌ Stop loss técnico alcanzado (MA50/MA21 priority)\n")
        f.write("- ❌ Earnings se volvieron negativos\n")
        f.write("- ❌ Weekly ATR suggests higher volatility than manageable\n\n")
        
        f.write("### 📅 **Workflow Semanal Agresivo Optimizado:**\n\n")
        f.write("1. **Lunes AM:** Revisar reporte y identificar rotaciones urgentes con Weekly ATR data\n")
        f.write("2. **Lunes PM:** Ejecutar salidas urgentes y rotaciones excepcionales\n")
        f.write("3. **Martes:** Ejecutar rotaciones agresivas restantes\n")
        f.write("4. **Miércoles:** Evaluar oportunidades emergentes con fundamentales sólidos\n")
        f.write("5. **Jueves:** Ajustar stops según MA priority y preparar próxima semana\n")
        f.write("6. **Viernes:** Review Weekly ATR patterns y volatility changes\n")
        f.write("7. **Sábado:** Actualizar portfolio con cambios reales\n\n")
        
        f.write("### ⚖️ **Balance Agresivo Riesgo-Momentum Optimizado:**\n\n")
        f.write("- **Objetivo:** Capturar 15-25% por posición en ~1 mes con Weekly ATR alignment\n")
        f.write("- **Win rate target:** 55-65% (mayor volatilidad aceptable pero controlada)\n")
        f.write("- **Max drawdown:** <12% por posición (momentum stops + MA priority)\n")
        f.write("- **Portfolio turnover:** 8-12 rotaciones por año (alta actividad optimizada)\n")
        f.write("- **Risk per trade:** 8-10% (más agresivo que conservador 5% pero con stops restrictivos)\n")
        f.write("- **Weekly ATR consideration:** Monitor ratio changes for exit timing\n")
        f.write("- **Fundamental floor:** Solo earnings positivos para todas las posiciones\n\n")
    
    def write_momentum_market_context(self, f):
        """Escribe contexto de mercado con enfoque en momentum y optimizaciones"""
        f.write("## 📊 **CONTEXTO DE MERCADO - MOMENTUM GLOBAL OPTIMIZADO**\n\n")
        
        if self.screening_data:
            benchmark = self.screening_data.get('benchmark_context', {})
            f.write(f"### 📈 **SPY Momentum Benchmark:**\n")
            f.write(f"- **20 días:** {benchmark.get('spy_20d', 0):+.1f}% *(peso 70% en scoring)*\n")
            f.write(f"- **60 días:** {benchmark.get('spy_60d', 0):+.1f}% *(peso 30% en scoring)*\n")
            f.write(f"- **90 días:** {benchmark.get('spy_90d', 0):+.1f}% *(eliminado del scoring)*\n\n")
        
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            f.write(f"### 🎯 **Análisis de Momentum Semanal:**\n")
            f.write(f"- **Símbolos únicos analizados:** {stats.get('total_unique_symbols', 0)}\n")
            f.write(f"- **Momentum consistente:** {stats.get('consistent_winners_count', 0)}\n")
            f.write(f"- **Momentum fuerte:** {stats.get('strong_candidates_count', 0)}\n")
            f.write(f"- **Momentum emergente:** {stats.get('emerging_count', 0)}\n\n")
        
        # 🆕 Estadísticas de optimización
        if self.screening_data:
            optimization_stats = self.screening_data.get('momentum_responsive_stats', {})
            
            f.write(f"### 🔧 **Estadísticas de Optimización:**\n")
            
            # Weekly ATR stats
            avg_weekly_atr = optimization_stats.get('avg_weekly_atr', 0)
            avg_daily_atr = optimization_stats.get('avg_daily_atr', 0)
            
            if avg_weekly_atr > 0 and avg_daily_atr > 0:
                atr_ratio = avg_weekly_atr / avg_daily_atr
                f.write(f"- **Weekly ATR promedio:** {avg_weekly_atr:.2f}\n")
                f.write(f"- **Daily ATR promedio:** {avg_daily_atr:.2f}\n")
                f.write(f"- **Ratio Weekly/Daily:** {atr_ratio:.1f}x\n")
                
                if atr_ratio > 2.5:
                    f.write(f"- **Interpretación:** High weekly volatility - targets conservadores justificados\n")
                elif atr_ratio > 2.0:
                    f.write(f"- **Interpretación:** Moderate weekly volatility - balance óptimo\n")
                else:
                    f.write(f"- **Interpretación:** Low weekly volatility - could consider más agresivo\n")
            else:
                f.write(f"- **Weekly ATR:** No implementado en esta ejecución\n")
            
            # Fundamental quality stats
            positive_earnings = optimization_stats.get('positive_earnings_count', 0)
            total_results = len(self.screening_data.get('detailed_results', [])) if self.screening_data else 0
            
            if total_results > 0:
                earnings_pct = (positive_earnings / total_results) * 100
                f.write(f"- **Calidad fundamental:** {positive_earnings}/{total_results} ({earnings_pct:.0f}%) earnings positivos\n")
                
                if earnings_pct == 100:
                    f.write(f"- **Status fundamental:** ✅ OPTIMAL - Solo earnings positivos\n")
                elif earnings_pct >= 80:
                    f.write(f"- **Status fundamental:** 🔶 GOOD - Mayoría earnings positivos\n")
                else:
                    f.write(f"- **Status fundamental:** ⚠️ MIXED - Verificar filtros fundamentales\n")
            
            f.write(f"\n")
        
        # Metodología optimizada
        f.write(f"### 🔬 **Metodología Momentum Agresivo Optimizada:**\n")
        f.write(f"- **Scoring:** Score técnico + (R/R ratio × 12) para ranking final\n")
        f.write(f"- **Momentum weighting:** 70% peso a momentum 20d, 30% a momentum 60d\n")
        f.write(f"- **Take profit calculation:** Weekly ATR × (2.0 to 3.0) basado en momentum strength\n")
        f.write(f"- **Stop loss priority:** MA50 → MA21 → ATR/Support → 8% fallback\n")
        f.write(f"- **Exit criteria:** Ausencia 1+ semanas OR deterioro score >15%\n")
        f.write(f"- **Rotation threshold:** Score 20% superior OR momentum excepcional\n")
        f.write(f"- **Fundamental requirement:** Solo quarterly_earnings_positive = true\n\n")
        
        f.write("### 🎯 **Filosofía de Momentum Actualizada:**\n")
        f.write("- **Objetivo:** Capturar momentum superior con rotación mensual optimizada\n")
        f.write("- **Holding period:** ~1 mes con salidas agresivas si momentum se debilita\n")
        f.write("- **Decisiones:** Momentum strength + acceleration signals + technical quality + fundamentales sólidos\n")
        f.write("- **Risk management:** Momentum stops + volatility scaling + quick exits + Weekly ATR awareness\n")
        f.write("- **Success metric:** Outperformance vs SPY con mayor win rate que buy&hold + improved timing precision\n")
        f.write("- **Optimization stack:** Weekly ATR + Min stop loss + Strict fundamentals = higher quality selections\n\n")
    
    def create_aggressive_dashboard_data(self):
        """Crea datos JSON para el dashboard agresivo con optimizaciones"""
        dashboard_data = {
            "timestamp": self.report_date.isoformat(),
            "market_date": self.report_date.strftime("%Y-%m-%d"),
            "analysis_type": "aggressive_momentum_responsive_weekly_atr_optimized",
            "optimization_stack": {
                "weekly_atr_take_profit": True,
                "min_stop_loss_restrictive": True,
                "fundamental_strict_filtering": True,
                "timeframe_alignment": "1_month_swing_trading"
            },
            "summary": {
                "analysis_type": "Aggressive Momentum Responsive - Weekly ATR Optimized",
                "total_analyzed": 0,
                "exceptional_momentum": 0,
                "strong_momentum": 0,
                "rotation_opportunities": 0,
                "optimization_applied": True,
                "message": "Análisis momentum agresivo con stack de optimizaciones completado"
            },
            "top_picks": [],
            "momentum_analysis": {
                "philosophy": "swing_for_fences_monthly_rotation_optimized",
                "momentum_weights": {
                    "momentum_20d": 0.70,
                    "momentum_60d": 0.30
                },
                "exceptional_momentum": [],
                "strong_momentum": [],
                "emerging_momentum": []
            },
            "rotation_recommendations": {},
            "market_context": {},
            "optimization_metrics": {
                "weekly_atr_implemented": False,
                "avg_weekly_atr": 0,
                "avg_daily_atr": 0,
                "atr_ratio": 0,
                "positive_earnings_count": 0,
                "positive_earnings_percentage": 0
            }
        }
        
        # Datos de screening agresivo con optimizaciones
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            dashboard_data["summary"]["total_analyzed"] = len(detailed_results)
            
            # 🆕 Métricas de optimización
            stats = self.screening_data.get('momentum_responsive_stats', {})
            
            opt_metrics = dashboard_data["optimization_metrics"]
            opt_metrics["avg_weekly_atr"] = stats.get('avg_weekly_atr', 0)
            opt_metrics["avg_daily_atr"] = stats.get('avg_daily_atr', 0)
            
            if opt_metrics["avg_daily_atr"] > 0:
                opt_metrics["atr_ratio"] = opt_metrics["avg_weekly_atr"] / opt_metrics["avg_daily_atr"]
                opt_metrics["weekly_atr_implemented"] = opt_metrics["avg_weekly_atr"] > 0
            
            opt_metrics["positive_earnings_count"] = stats.get('positive_earnings_count', 0)
            if len(detailed_results) > 0:
                opt_metrics["positive_earnings_percentage"] = (opt_metrics["positive_earnings_count"] / len(detailed_results)) * 100
            
            # Clasificar por momentum
            exceptional = []
            strong = []
            emerging = []
            
            for stock in detailed_results:
                score = stock.get('score', 0)
                momentum_20d = stock.get('outperformance_20d', 0)
                
                # Añadir categoría de momentum
                if score > 200 or momentum_20d > 25:
                    momentum_category = 'EXCEPTIONAL'
                    exceptional.append(stock['symbol'])
                elif score > 150 or momentum_20d > 15:
                    momentum_category = 'STRONG'
                    strong.append(stock['symbol'])
                else:
                    momentum_category = 'MODERATE'
                    emerging.append(stock['symbol'])
                
                # Añadir a top picks con categoría y optimizaciones
                if len(dashboard_data["top_picks"]) < 10:
                    # 🆕 Incluir métricas de optimización
                    weekly_atr = stock.get('weekly_atr', 0)
                    daily_atr = stock.get('atr', 0)
                    fundamental_data = stock.get('fundamental_data', {})
                    earnings_positive = fundamental_data.get('quarterly_earnings_positive', False)
                    stop_analysis = stock.get('stop_analysis', {})
                    
                    pick = {
                        "rank": len(dashboard_data["top_picks"]) + 1,
                        "symbol": stock.get('symbol', ''),
                        "company": stock.get('company_info', {}).get('name', 'N/A')[:30],
                        "sector": stock.get('company_info', {}).get('sector', 'N/A'),
                        "price": stock.get('current_price', 0),
                        "score": stock.get('score', 0),
                        "technical_score": stock.get('technical_score', 0),
                        "rr_bonus": stock.get('rr_bonus', 0),
                        "stop_loss": stock.get('stop_loss', 0),
                        "take_profit": stock.get('take_profit', 0),
                        "momentum_category": momentum_category,
                        "metrics": {
                            "risk_pct": stock.get('risk_pct', 0),
                            "upside_pct": stock.get('upside_pct', 0),
                            "risk_reward_ratio": stock.get('risk_reward_ratio', 0),
                            "outperformance_20d": stock.get('outperformance_20d', 0),
                            "outperformance_60d": stock.get('outperformance_60d', 0),
                            "volume_surge": stock.get('volume_surge', 0),
                            "momentum_strength": score  # Usar score como proxy
                        },
                        # 🆕 Optimizations data
                        "optimizations": {
                            "weekly_atr": weekly_atr,
                            "daily_atr": daily_atr,
                            "atr_ratio": weekly_atr / daily_atr if daily_atr > 0 else 0,
                            "earnings_positive": earnings_positive,
                            "stop_method": stop_analysis.get('stop_selection', 'unknown'),
                            "take_profit_method": stock.get('take_profit_analysis', {}).get('primary_method', 'unknown'),
                            "weekly_atr_optimized": weekly_atr > 0
                        },
                        "target_hold": "~1 mes (rotación agresiva optimizada)",
                        "rotation_urgency": "URGENT" if momentum_category == 'EXCEPTIONAL' else "HIGH" if momentum_category == 'STRONG' else "MEDIUM"
                    }
                    dashboard_data["top_picks"].append(pick)
            
            dashboard_data["summary"]["exceptional_momentum"] = len(exceptional)
            dashboard_data["summary"]["strong_momentum"] = len(strong)
            dashboard_data["momentum_analysis"]["exceptional_momentum"] = exceptional[:10]
            dashboard_data["momentum_analysis"]["strong_momentum"] = strong[:10]
            dashboard_data["momentum_analysis"]["emerging_momentum"] = emerging[:10]
        
        # Datos de rotación agresiva
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            dashboard_data["summary"]["rotation_opportunities"] = len(action_summary.get('aggressive_rotations', []))
            
            dashboard_data["rotation_recommendations"] = {
                "overall_action": action_summary.get('overall_action', 'NO_DATA'),
                "aggressive_rotations": [r.get('symbol', r) if isinstance(r, dict) else r for r in action_summary.get('aggressive_rotations', [])],
                "urgent_exits": [e.get('symbol', e) if isinstance(e, dict) else e for e in action_summary.get('urgent_exits', [])],
                "emerging_opportunities": [o.get('symbol', o) if isinstance(o, dict) else o for o in action_summary.get('emerging_opportunities', [])],
                "detailed_recommendations": action_summary.get('detailed_recommendations', [])[:5]
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
        
        # Guardar datos del dashboard agresivo optimizado
        with open('docs/data.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print("✅ Datos del dashboard agresivo optimizado guardados: docs/data.json")
        return dashboard_data
    
    def generate_complete_aggressive_report(self):
        """Genera reporte completo de momentum agresivo con optimizaciones"""
        print("📋 Generando reporte semanal de MOMENTUM AGRESIVO - WEEKLY ATR OPTIMIZED...")
        
        # Cargar todos los datos
        if not self.load_all_data():
            print("❌ No se pudieron cargar suficientes datos")
            return False
        
        # Crear reporte Markdown agresivo
        markdown_file = self.create_aggressive_markdown_report()
        
        # Crear datos para dashboard agresivo optimizado
        dashboard_data = self.create_aggressive_dashboard_data()
        
        print(f"✅ Reporte momentum agresivo optimizado completado:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - Dashboard: docs/data.json")
        print(f"   - Incluye: Weekly ATR optimization, Stop loss restrictivo, Fundamentales estrictos")
        
        return True

def main():
    """Función principal para momentum agresivo optimizado"""
    generator = AggressiveMomentumReportGenerator()
    
    success = generator.generate_complete_aggressive_report()
    
    if success:
        print("\n✅ Reporte momentum agresivo OPTIMIZADO generado exitosamente")
        print("\n⚡ OPTIMIZACIONES APLICADAS:")
        print("   - 📊 Weekly ATR para take profit (alineación temporal mejorada)")
        print("   - 🛡️ Stop loss más restrictivo (MA50 → MA21 → otros → 8% fallback)")
        print("   - 📈 Filtros fundamentales estrictos (solo earnings positivos)")
        print("   - 🎯 Categorías momentum con Weekly ATR multipliers (3.0x/2.5x/2.0x)")
        print("   - 🔧 Tracking completo de optimizaciones en reportes y dashboard")
        print("   - 📊 Análisis comparativo ATR (Weekly vs Daily)")
        print("   - 🏆 Estadísticas de calidad fundamental")
        print("   - 🚀 Dashboard responsivo con métricas de optimización")
        print("   - 📁 Gestión automática de historial de reportes optimizados")
    else:
        print("\n❌ Error generando reporte momentum agresivo optimizado")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced Weekly Report Generator - Con niveles de trading y gestión activa
Integra análisis avanzado, niveles de stop/target, y recomendaciones detalladas
🆕 INCLUYE GESTIÓN AUTOMÁTICA DE HISTORIAL
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class EnhancedReportGenerator:
    def __init__(self):
        self.screening_data = None
        self.consistency_data = None
        self.rotation_data = None
        self.report_date = datetime.now()
        
    def load_all_data(self):
        """Carga todos los datos necesarios incluyendo nuevos formatos"""
        success_count = 0
        
        # Cargar screening results (priorizar enhanced si existe)
        screening_files = ['weekly_screening_results.json', 'enhanced_screening_results_*.json']
        for pattern in screening_files:
            try:
                if '*' in pattern:
                    # Buscar el más reciente
                    import glob
                    files = glob.glob(pattern)
                    if files:
                        latest_file = max(files, key=os.path.getctime)
                        with open(latest_file, 'r') as f:
                            self.screening_data = json.load(f)
                            print(f"✓ Datos de screening mejorado cargados: {latest_file}")
                            success_count += 1
                            break
                else:
                    with open(pattern, 'r') as f:
                        self.screening_data = json.load(f)
                        print("✓ Datos de screening cargados")
                        success_count += 1
                        break
            except Exception as e:
                continue
        
        # Cargar consistency analysis
        try:
            with open('consistency_analysis.json', 'r') as f:
                self.consistency_data = json.load(f)
                print("✓ Análisis de consistencia cargado")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando consistencia: {e}")
        
        # Cargar rotation recommendations
        try:
            with open('rotation_recommendations.json', 'r') as f:
                self.rotation_data = json.load(f)
                print("✓ Recomendaciones de rotación cargadas")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando rotación: {e}")
        
        return success_count >= 2
    
    def create_enhanced_markdown_report(self):
        """Crea reporte mejorado en formato Markdown con niveles de trading y gestión de historial"""
        report_filename = f"ENHANCED_WEEKLY_REPORT_{self.report_date.strftime('%Y_%m_%d')}.md"
        
        # 🆕 Archivar reporte anterior si es del mismo día
        if os.path.exists(report_filename):
            try:
                timestamp = datetime.now().strftime('%H%M%S')
                backup_name = f"ENHANCED_WEEKLY_REPORT_{self.report_date.strftime('%Y_%m_%d')}_{timestamp}.md"
                os.rename(report_filename, backup_name)
                print(f"📁 Reporte anterior renombrado: {backup_name}")
            except Exception as e:
                print(f"⚠️ Error renombrando reporte anterior: {e}")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # Header mejorado
            f.write(f"# 📈 ANÁLISIS CONSERVADOR CON NIVELES DE TRADING - {self.report_date.strftime('%d %B %Y')}\n\n")
            
            # Resumen ejecutivo mejorado
            self.write_enhanced_executive_summary(f)
            
            # Sección de Top Picks con niveles de trading
            if self.screening_data:
                self.write_top_picks_with_levels(f)
            
            # Screening results mejorado
            if self.screening_data:
                self.write_enhanced_screening_section(f)
            
            # Consistency analysis
            if self.consistency_data:
                self.write_consistency_section(f)
            
            # Rotation recommendations mejoradas
            if self.rotation_data:
                self.write_enhanced_rotation_section(f)
            
            # Gestión activa y take profit
            self.write_active_management_guide(f)
            
            # Market context
            self.write_enhanced_market_context(f)
            
            # Footer
            f.write(f"\n---\n\n")
            f.write(f"**Generado automáticamente:** {self.report_date.isoformat()}\n")
            f.write(f"**Próximo análisis:** {(self.report_date + timedelta(days=7)).strftime('%d %B %Y')}\n")
            f.write(f"**Estrategia:** Inversión conservadora con gestión activa de niveles\n\n")
            f.write(f"🤖 *Enhanced Trading Bot with Trading Levels by 0t4c0n*\n")
        
        print(f"✅ Reporte Markdown mejorado creado: {report_filename}")
        print("📁 Historial de reportes gestionado automáticamente por cleanup")
        return report_filename
    
    def write_enhanced_executive_summary(self, f):
        """Escribe resumen ejecutivo mejorado"""
        f.write("## 🎯 **RESUMEN EJECUTIVO MEJORADO**\n\n")
        
        # Calcular métricas de trading
        avg_risk_reward = 0
        avg_upside = 0
        avg_risk = 0
        strong_opportunities = 0
        
        if self.screening_data and self.screening_data.get('detailed_results'):
            results = self.screening_data['detailed_results']
            if results:
                avg_risk_reward = sum(r.get('risk_reward_ratio', 0) for r in results) / len(results)
                avg_upside = sum(r.get('upside_pct', 0) for r in results) / len(results)
                avg_risk = sum(r.get('risk_pct', 0) for r in results) / len(results)
                strong_opportunities = len([r for r in results if r.get('risk_reward_ratio', 0) > 2.5])
        
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            overall_action = action_summary.get('overall_action', 'NO_DATA')
            
            if overall_action == 'ACTION_REQUIRED':
                f.write("### 🚨 **ACCIÓN REQUERIDA - NIVELES DEFINIDOS**\n\n")
            elif overall_action == 'EVALUATE_CHANGES':
                f.write("### ⚠️ **EVALUAR CAMBIOS CON GESTIÓN ACTIVA**\n\n")
            else:
                f.write("### ✅ **MANTENER POSICIONES - VIGILAR NIVELES**\n\n")
            
            # Estadísticas clave mejoradas
            holds = len(action_summary.get('holds', []))
            exits = len(action_summary.get('consider_exits', [])) + len(action_summary.get('urgent_exits', []))
            buys = len(action_summary.get('strong_buys', [])) + len(action_summary.get('watch_buys', []))
            
            f.write(f"- **Cartera actual:** {holds} mantener, {exits} evaluar salida\n")
            f.write(f"- **Nuevas oportunidades:** {buys} identificadas con niveles de trading\n")
            f.write(f"- **Calidad de oportunidades:** {strong_opportunities} con R/R > 2.5:1\n")
        
        f.write(f"- **Métricas de trading promedio:**\n")
        f.write(f"  - Risk/Reward ratio: {avg_risk_reward:.1f}:1\n")
        f.write(f"  - Upside potencial: {avg_upside:.1f}%\n")
        f.write(f"  - Riesgo promedio: {avg_risk:.1f}%\n")
        
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            f.write(f"- **Consistencia:** {stats.get('consistent_winners_count', 0)} winners, {stats.get('strong_candidates_count', 0)} candidates\n")
        
        f.write("\n")
    
    def write_top_picks_with_levels(self, f):
        """Nueva sección: Top Picks con niveles de trading detallados"""
        f.write("## 🎯 **TOP PICKS CON NIVELES DE TRADING**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        
        if detailed_results:
            # Tomar top 5 mejores
            top_picks = detailed_results[:5]
            
            for i, stock in enumerate(top_picks):
                symbol = stock.get('symbol', 'N/A')
                current_price = stock.get('current_price', 0)
                take_profit = stock.get('take_profit', 0)
                stop_loss = stock.get('stop_loss', 0)
                risk_pct = stock.get('risk_pct', 0)
                upside_pct = stock.get('upside_pct', 0)
                risk_reward = stock.get('risk_reward_ratio', 0)
                score = stock.get('score', 0)
                
                f.write(f"### {i+1}. **{symbol}** - Score: {score:.1f}\n\n")
                
                # Información básica
                company_info = stock.get('company_info', {})
                f.write(f"**Empresa:** {company_info.get('name', 'N/A')}\n")
                f.write(f"**Sector:** {company_info.get('sector', 'N/A')}\n\n")
                
                # Niveles de trading
                f.write(f"**📊 NIVELES DE TRADING:**\n")
                f.write(f"- **Precio actual:** ${current_price:.2f}\n")
                f.write(f"- **🛑 Stop Loss:** ${stop_loss:.2f} ({risk_pct:.1f}% riesgo)\n")
                f.write(f"- **🎯 Take Profit:** ${take_profit:.2f} ({upside_pct:.1f}% upside)\n")
                f.write(f"- **⚖️ Risk/Reward:** {risk_reward:.1f}:1\n\n")
                
                # Análisis técnico
                outperf_60d = stock.get('outperformance_60d', 0)
                volume_surge = stock.get('volume_surge', 0)
                volatility_rank = stock.get('volatility_rank', 'N/A')
                
                f.write(f"**📈 ANÁLISIS TÉCNICO:**\n")
                f.write(f"- Outperformance vs SPY (60d): +{outperf_60d:.1f}%\n")
                f.write(f"- Volume surge: {volume_surge:+.1f}%\n")
                f.write(f"- Volatilidad: {volatility_rank}\n")
                
                # Soportes y resistencias si están disponibles
                sr_data = stock.get('support_resistance')
                if sr_data:
                    resistance = sr_data.get('resistance', 0)
                    support = sr_data.get('support', 0)
                    f.write(f"- Resistencia técnica: ${resistance:.2f}\n")
                    f.write(f"- Soporte técnico: ${support:.2f}\n")
                
                f.write("\n")
                
                # Fundamentales
                fund_score = stock.get('fundamental_score', 0)
                fund_details = stock.get('fundamental_details', {})
                f.write(f"**💼 FUNDAMENTALES:** Score {fund_score}/100\n")
                
                if fund_details.get('quarterly_earnings_growth'):
                    f.write(f"- Crecimiento beneficios: {fund_details['quarterly_earnings_growth']*100:+.1f}%\n")
                if fund_details.get('revenue_growth'):
                    f.write(f"- Crecimiento ingresos: {fund_details['revenue_growth']*100:+.1f}%\n")
                if fund_details.get('roe'):
                    f.write(f"- ROE: {fund_details['roe']*100:.1f}%\n")
                
                f.write("\n")
                
                # Recomendación de trading
                trading_rec = stock.get('trading_recommendation', '')
                f.write(f"**🎯 RECOMENDACIÓN:** {trading_rec}\n\n")
                
                # Gestión activa
                f.write(f"**🔄 GESTIÓN ACTIVA:**\n")
                f.write(f"- Si pierde consistencia (no aparece 2+ semanas): Considerar salida gradual\n")
                f.write(f"- Si alcanza 80% del take profit: Considerar take profit parcial\n")
                f.write(f"- Si rompe stop loss: Salida inmediata\n")
                f.write(f"- Revisar niveles semanalmente según evolución\n\n")
                
                f.write("---\n\n")
        
    def write_enhanced_screening_section(self, f):
        """Escribe sección de screening mejorada"""
        f.write("## 🔍 **SCREENING SEMANAL MEJORADO**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        benchmark_context = self.screening_data.get('benchmark_context', {})
        trading_summary = self.screening_data.get('trading_summary', {})
        
        f.write(f"**Acciones analizadas:** {len(detailed_results)}\n")
        f.write(f"**Metodología:** Análisis técnico avanzado + niveles de trading dinámicos\n")
        f.write(f"**Benchmark SPY (60d):** {benchmark_context.get('spy_60d', 0):+.1f}%\n\n")
        
        # Estadísticas de trading
        if trading_summary:
            f.write(f"**📊 ESTADÍSTICAS DE TRADING:**\n")
            f.write(f"- Risk/Reward promedio: {trading_summary.get('avg_risk_reward', 0):.1f}:1\n")
            f.write(f"- Upside promedio: {trading_summary.get('avg_upside', 0):.1f}%\n")
            f.write(f"- Riesgo promedio: {trading_summary.get('avg_risk', 0):.1f}%\n\n")
        
        if detailed_results:
            f.write("### 📈 **TOP 10 CON MÉTRICAS DE TRADING**\n\n")
            f.write("| Rank | Símbolo | Precio | Stop Loss | Take Profit | Risk % | R/R | Score | Outperf 60d |\n")
            f.write("|------|---------|--------|-----------|-------------|--------|-----|-------|-------------|\n")
            
            for i, stock in enumerate(detailed_results[:10]):
                symbol = stock.get('symbol', 'N/A')
                price = stock.get('current_price', 0)
                stop = stock.get('stop_loss', 0)
                target = stock.get('take_profit', 0)
                risk = stock.get('risk_pct', 0)
                rr = stock.get('risk_reward_ratio', 0)
                score = stock.get('score', 0)
                outperf = stock.get('outperformance_60d', 0)
                
                f.write(f"| {i+1} | **{symbol}** | ${price:.2f} | ${stop:.2f} | ${target:.2f} | {risk:.1f}% | {rr:.1f}:1 | {score:.0f} | +{outperf:.1f}% |\n")
            
            f.write("\n")
            
            # Análisis de calidad
            high_quality = [s for s in detailed_results if s.get('risk_reward_ratio', 0) > 2.5]
            medium_quality = [s for s in detailed_results if 2.0 <= s.get('risk_reward_ratio', 0) <= 2.5]
            
            f.write(f"**🏆 ANÁLISIS DE CALIDAD:**\n")
            f.write(f"- Alta calidad (R/R > 2.5:1): {len(high_quality)} acciones\n")
            f.write(f"- Calidad media (R/R 2.0-2.5:1): {len(medium_quality)} acciones\n")
            f.write(f"- Enfoque recomendado: Priorizar alta calidad para nuevas entradas\n\n")
    
    def write_consistency_section(self, f):
        """Escribe sección de análisis de consistencia (similar a antes pero mejorada)"""
        f.write("## 📈 **ANÁLISIS DE CONSISTENCIA (5 SEMANAS)**\n\n")
        
        consistency_analysis = self.consistency_data.get('consistency_analysis', {})
        
        # Consistent Winners
        consistent_winners = consistency_analysis.get('consistent_winners', [])
        if consistent_winners:
            f.write("### 🏆 **CONSISTENT WINNERS** (Alta confianza - 4+ semanas)\n\n")
            f.write("*Ideales para holds de 1-3 meses con gestión activa de niveles*\n\n")
            for winner in consistent_winners[:5]:
                symbol = winner['symbol']
                frequency = winner['frequency']
                score = winner.get('consistency_score', 0)
                appeared = "✅" if winner.get('appeared_this_week', False) else "❌"
                
                f.write(f"- **{symbol}** - {frequency}/5 semanas - Score: {score:.1f} - Esta semana: {appeared}\n")
            f.write("\n")
        
        # Strong Candidates
        strong_candidates = consistency_analysis.get('strong_candidates', [])
        if strong_candidates:
            f.write("### 💎 **STRONG CANDIDATES** (Buena confianza - 3 semanas)\n\n")
            f.write("*Candidatos sólidos para entrada si aparecen próxima semana*\n\n")
            for candidate in strong_candidates[:5]:
                symbol = candidate['symbol']
                frequency = candidate['frequency']
                score = candidate.get('consistency_score', 0)
                appeared = "✅" if candidate.get('appeared_this_week', False) else "❌"
                
                f.write(f"- **{symbol}** - {frequency}/5 semanas - Score: {score:.1f} - Esta semana: {appeared}\n")
            f.write("\n")
        
        # Emerging Opportunities
        emerging = consistency_analysis.get('emerging_opportunities', [])
        if emerging:
            f.write("### 🌱 **EMERGING OPPORTUNITIES** (Vigilar evolución - 2 semanas)\n\n")
            f.write("*Vigilar para confirmar tendencia antes de entrada*\n\n")
            for opp in emerging[:5]:
                symbol = opp['symbol']
                frequency = opp['frequency']
                appeared = "✅" if opp.get('appeared_this_week', False) else "❌"
                
                f.write(f"- **{symbol}** - {frequency}/5 semanas - Esta semana: {appeared}\n")
            f.write("\n")
        
        # Cambios de tendencia
        trend_changes = self.consistency_data.get('trend_changes', {})
        newly_emerged = trend_changes.get('newly_emerged', [])
        disappeared = trend_changes.get('disappeared_this_week', [])
        
        if newly_emerged:
            f.write(f"### 🆕 **NUEVAS APARICIONES:** {', '.join(newly_emerged[:10])}\n")
            f.write("*Esperar 2-3 semanas de consistencia antes de considerar entrada*\n\n")
        
        if disappeared:
            f.write(f"### 📉 **DESAPARECIERON:** {', '.join(disappeared[:10])}\n")
            f.write("*Si tienes posiciones en estas, considerar gestión activa de salida*\n\n")
    
    def write_enhanced_rotation_section(self, f):
        """Escribe sección de recomendaciones de rotación mejorada"""
        f.write("## 🔄 **RECOMENDACIONES DE ROTACIÓN CON NIVELES**\n\n")
        
        if not self.rotation_data:
            f.write("*No hay datos de rotación disponibles*\n\n")
            return
        
        action_summary = self.rotation_data.get('action_summary', {})
        detailed_recs = action_summary.get('detailed_recommendations', [])
        
        # Usar recomendaciones detalladas si están disponibles
        if detailed_recs:
            # Agrupar por tipo de acción
            strong_buys = [r for r in detailed_recs if r['action'] == 'STRONG_BUY']
            holds = [r for r in detailed_recs if 'HOLD' in r['action']]
            exits = [r for r in detailed_recs if 'EXIT' in r['action']]
            
            # Strong Buys con niveles
            if strong_buys:
                f.write("### 🔥 **COMPRAS DE ALTA CONFIANZA CON NIVELES**\n\n")
                for rec in strong_buys:
                    f.write(f"#### **{rec['symbol']}**\n")
                    f.write(f"**Razón:** {rec['reason']}\n\n")
                    
                    if rec.get('price'):
                        f.write(f"**📊 Niveles de trading:**\n")
                        f.write(f"- Precio entrada: ${rec['price']:.2f}\n")
                        if rec.get('stop_loss'):
                            f.write(f"- Stop Loss: ${rec['stop_loss']:.2f}\n")
                        if rec.get('take_profit'):
                            f.write(f"- Take Profit: ${rec['take_profit']:.2f}\n")
                        if rec.get('risk_reward'):
                            f.write(f"- Risk/Reward: {rec['risk_reward']}\n")
                    
                    f.write(f"**🎯 Estrategia:** Entrada gradual, gestión activa según evolución semanal\n\n")
            
            # Posiciones actuales
            if holds:
                f.write("### ✅ **MANTENER CON GESTIÓN ACTIVA**\n\n")
                for rec in holds:
                    f.write(f"- **{rec['symbol']}**: {rec['reason']}\n")
                f.write("\n")
            
            # Salidas
            if exits:
                f.write("### ⚠️ **EVALUAR SALIDAS**\n\n")
                for rec in exits:
                    urgency = "🚨 URGENTE" if "URGENT" in rec['action'] else "⏳ GRADUAL"
                    f.write(f"- **{rec['symbol']}** ({urgency}): {rec['reason']}\n")
                f.write("\n")
        
        # Lista de vigilancia
        watchlist = self.rotation_data.get('watchlist', [])
        if watchlist:
            f.write("### 📋 **LISTA DE VIGILANCIA AVANZADA**\n\n")
            f.write("*Símbolos para monitorear con criterios específicos de entrada:*\n\n")
            for item in watchlist[:10]:
                score = item.get('advanced_score', 0)
                f.write(f"- **{item['symbol']}** (Score: {score:.0f}) - {item['reason']} - *{item['action']}*\n")
            f.write("\n")
    
    def write_active_management_guide(self, f):
        """Nueva sección: Guía de gestión activa"""
        f.write("## 🎛️ **GUÍA DE GESTIÓN ACTIVA DE TAKE PROFIT**\n\n")
        
        f.write("### 🎯 **¿Por qué gestión activa vs targets fijos?**\n\n")
        f.write("Los take profit calculados son **orientativos** basados en análisis técnico y estadístico, pero el mercado es dinámico. ")
        f.write("La gestión activa permite optimizar las salidas según la evolución real de cada posición.\n\n")
        
        f.write("### 📊 **Criterios de gestión semanal:**\n\n")
        f.write("#### **🟢 MANTENER POSICIÓN (seguir hacia target):**\n")
        f.write("- ✅ Aparece en screening 2+ semanas consecutivas\n")
        f.write("- ✅ Mantiene outperformance vs SPY\n")
        f.write("- ✅ Price action por encima de MA21\n")
        f.write("- ✅ Volume surge positivo\n\n")
        
        f.write("#### **🟡 TAKE PROFIT PARCIAL (25-50% posición):**\n")
        f.write("- ⚠️ Alcanza 75-80% del target calculado\n")
        f.write("- ⚠️ Señales de debilitamiento técnico (volumen decreciente)\n")
        f.write("- ⚠️ Pierde momentum pero mantiene tendencia\n")
        f.write("- ⚠️ Ganancias >20% en posiciones de alta convicción\n\n")
        
        f.write("#### **🔴 TAKE PROFIT TOTAL:**\n")
        f.write("- ❌ Desaparece del screening 2+ semanas consecutivas\n")
        f.write("- ❌ Rompe soporte técnico importante\n")
        f.write("- ❌ Underperformance vs SPY por 3+ semanas\n")
        f.write("- ❌ Deterioro fundamental evidente\n")
        f.write("- ❌ Cambio de tendencia en sector/mercado\n\n")
        
        f.write("### 🔄 **Workflow semanal recomendado:**\n\n")
        f.write("1. **Lunes:** Revisar este reporte y nuevas recomendaciones\n")
        f.write("2. **Martes:** Evaluar posiciones actuales según criterios arriba\n")
        f.write("3. **Miércoles:** Ejecutar rotaciones necesarias\n")
        f.write("4. **Jueves-Viernes:** Actualizar stops si es necesario\n")
        f.write("5. **Sábado:** Actualizar current_portfolio.json con cambios reales\n\n")
        
        f.write("### ⚖️ **Balance riesgo-beneficio:**\n\n")
        f.write("- **Objetivo principal:** Superar SPY con drawdown <20%\n")
        f.write("- **Holding period ideal:** 1-3 meses por posición\n")
        f.write("- **Take profit promedio esperado:** 15-25% por posición exitosa\n")
        f.write("- **Win rate objetivo:** 65-70% de posiciones positivas\n\n")
    
    def write_enhanced_market_context(self, f):
        """Escribe contexto de mercado mejorado"""
        f.write("## 📊 **CONTEXTO DE MERCADO Y METODOLOGÍA**\n\n")
        
        if self.screening_data:
            benchmark = self.screening_data.get('benchmark_context', {})
            f.write(f"### 📈 **SPY Performance (Benchmark):**\n")
            f.write(f"- 20 días: {benchmark.get('spy_20d', 0):+.1f}%\n")
            f.write(f"- 60 días: {benchmark.get('spy_60d', 0):+.1f}%\n")
            f.write(f"- 90 días: {benchmark.get('spy_90d', 0):+.1f}%\n\n")
        
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            f.write(f"### 🏆 **Análisis de Consistencia:**\n")
            f.write(f"- Símbolos únicos analizados: {stats.get('total_unique_symbols', 0)}\n")
            f.write(f"- Consistent Winners: {stats.get('consistent_winners_count', 0)}\n")
            f.write(f"- Strong Candidates: {stats.get('strong_candidates_count', 0)}\n")
            f.write(f"- Emerging Opportunities: {stats.get('emerging_count', 0)}\n\n")
        
        # Metodología mejorada
        if self.screening_data.get('methodology'):
            methodology = self.screening_data['methodology']
            f.write(f"### 🔬 **Metodología Mejorada:**\n")
            f.write(f"- **Stop Loss:** {methodology.get('stop_loss', 'N/A')}\n")
            f.write(f"- **Take Profit:** {methodology.get('take_profit', 'N/A')}\n")
            f.write(f"- **Scoring:** {methodology.get('scoring', 'N/A')}\n")
            f.write(f"- **Risk Management:** {methodology.get('risk_management', 'N/A')}\n\n")
        
        f.write("### 🎯 **Filosofía de Inversión Actualizada:**\n")
        f.write("- **Objetivo:** Superar al SPY con riesgo controlado y gestión activa\n")
        f.write("- **Holding period:** 1-3 meses con gestión semanal de niveles\n")
        f.write("- **Decisiones:** Basadas en consistencia + niveles técnicos + momentum\n")
        f.write("- **Take profit:** Gestión activa según evolución, no targets rígidos\n")
        f.write("- **Risk management:** Stop loss dinámico + sizing por volatilidad\n\n")
    
    def create_enhanced_dashboard_data(self):
        """Crea datos JSON mejorados para el dashboard"""
        dashboard_data = {
            "timestamp": self.report_date.isoformat(),
            "market_date": self.report_date.strftime("%Y-%m-%d"),
            "analysis_type": "enhanced_conservative_with_trading_levels",
            "summary": {
                "analysis_type": "Enhanced Conservative with Trading Levels",
                "total_analyzed": 0,
                "passed_filters": 0,
                "consistent_winners": 0,
                "strong_candidates": 0,
                "high_quality_opportunities": 0,
                "message": "Análisis mejorado con niveles de trading completado"
            },
            "top_picks": [],
            "consistency_analysis": {},
            "rotation_recommendations": {},
            "market_context": {},
            "trading_metrics": {
                "avg_risk_reward": 0,
                "avg_upside": 0,
                "avg_risk": 0,
                "high_quality_count": 0
            }
        }
        
        # Datos de screening mejorados
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            dashboard_data["summary"]["passed_filters"] = len(detailed_results)
            
            # Métricas de trading
            if detailed_results:
                avg_rr = sum(r.get('risk_reward_ratio', 0) for r in detailed_results) / len(detailed_results)
                avg_up = sum(r.get('upside_pct', 0) for r in detailed_results) / len(detailed_results)
                avg_risk = sum(r.get('risk_pct', 0) for r in detailed_results) / len(detailed_results)
                high_quality = len([r for r in detailed_results if r.get('risk_reward_ratio', 0) > 2.5])
                
                dashboard_data["trading_metrics"] = {
                    "avg_risk_reward": avg_rr,
                    "avg_upside": avg_up,
                    "avg_risk": avg_risk,
                    "high_quality_count": high_quality
                }
                dashboard_data["summary"]["high_quality_opportunities"] = high_quality
            
            # Top picks mejorados para dashboard
            for i, stock in enumerate(detailed_results[:10]):
                pick = {
                    "rank": i + 1,
                    "symbol": stock.get('symbol', ''),
                    "company": stock.get('company_info', {}).get('name', 'N/A')[:30],
                    "sector": stock.get('company_info', {}).get('sector', 'N/A'),
                    "price": stock.get('current_price', 0),
                    "score": stock.get('score', 0),
                    "stop_loss": stock.get('stop_loss', 0),
                    "take_profit": stock.get('take_profit', 0),
                    "metrics": {
                        "risk_pct": stock.get('risk_pct', 0),
                        "upside_pct": stock.get('upside_pct', 0),
                        "risk_reward_ratio": stock.get('risk_reward_ratio', 0),
                        "outperformance_60d": stock.get('outperformance_60d', 0),
                        "volume_surge": stock.get('volume_surge', 0),
                        "fundamental_score": stock.get('fundamental_score', 0),
                        "volatility_rank": stock.get('volatility_rank', 'MEDIUM')
                    },
                    "ma_levels": stock.get('ma_levels', {}),
                    "target_hold": stock.get('target_hold', '1-3 meses'),
                    "trading_recommendation": stock.get('trading_recommendation', ''),
                    "atr": stock.get('atr', 0)
                }
                dashboard_data["top_picks"].append(pick)
        
        # Resto de datos (consistencia, rotación, mercado) - similar a antes
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            dashboard_data["summary"]["consistent_winners"] = stats.get('consistent_winners_count', 0)
            dashboard_data["summary"]["strong_candidates"] = stats.get('strong_candidates_count', 0)
            dashboard_data["summary"]["total_analyzed"] = stats.get('total_unique_symbols', 0)
            
            dashboard_data["consistency_analysis"] = {
                "weeks_analyzed": self.consistency_data.get('weeks_analyzed', 5),
                "consistent_winners": [s['symbol'] for s in self.consistency_data.get('consistency_analysis', {}).get('consistent_winners', [])[:10]],
                "strong_candidates": [s['symbol'] for s in self.consistency_data.get('consistency_analysis', {}).get('strong_candidates', [])[:10]],
                "newly_emerged": self.consistency_data.get('trend_changes', {}).get('newly_emerged', [])[:10]
            }
        
        if self.rotation_data:
            dashboard_data["rotation_recommendations"] = {
                "overall_action": self.rotation_data.get('action_summary', {}).get('overall_action', 'NO_DATA'),
                "strong_buys": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('strong_buys', [])],
                "consider_exits": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('consider_exits', [])],
                "urgent_exits": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('urgent_exits', [])],
                "holds": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('holds', [])],
                "detailed_recommendations": self.rotation_data.get('action_summary', {}).get('detailed_recommendations', [])[:5]
            }
        
        if self.screening_data:
            benchmark = self.screening_data.get('benchmark_context', {})
            dashboard_data["market_context"] = {
                "spy_20d": benchmark.get('spy_20d', 0),
                "spy_60d": benchmark.get('spy_60d', 0),
                "spy_90d": benchmark.get('spy_90d', 0)
            }
        
        # Crear directorio docs si no existe
        os.makedirs('docs', exist_ok=True)
        
        # Guardar datos del dashboard mejorado
        with open('docs/data.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print("✅ Datos del dashboard mejorado guardados: docs/data.json")
        return dashboard_data
    
    def generate_complete_enhanced_report(self):
        """Genera reporte completo mejorado"""
        print("📋 Generando reporte semanal mejorado con niveles de trading...")
        
        # Cargar todos los datos
        if not self.load_all_data():
            print("❌ No se pudieron cargar suficientes datos")
            return False
        
        # Crear reporte Markdown mejorado
        markdown_file = self.create_enhanced_markdown_report()
        
        # Crear datos para dashboard mejorado
        dashboard_data = self.create_enhanced_dashboard_data()
        
        print(f"✅ Reporte semanal mejorado completado:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - Dashboard: docs/data.json")
        print(f"   - Incluye: Niveles de trading, gestión activa, análisis avanzado")
        
        return True

def main():
    """Función principal mejorada"""
    generator = EnhancedReportGenerator()
    
    success = generator.generate_complete_enhanced_report()
    
    if success:
        print("\n✅ Reporte semanal mejorado generado exitosamente")
        print("\n🎯 NUEVAS CARACTERÍSTICAS:")
        print("   - Niveles de stop loss y take profit dinámicos")
        print("   - Guía de gestión activa de posiciones")
        print("   - Risk/reward ratios para cada oportunidad")
        print("   - Criterios de salida basados en consistencia")
        print("   - Dashboard mejorado con niveles de trading")
        print("   - Gestión automática de historial de reportes")
    else:
        print("\n❌ Error generando reporte semanal mejorado")

if __name__ == "__main__":
    main()
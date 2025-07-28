#!/usr/bin/env python3
"""
Weekly Report Generator - Crea reportes semanales en Markdown y datos para dashboard
Combina screening, análisis de consistencia y recomendaciones de rotación
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class WeeklyReportGenerator:
    def __init__(self):
        self.screening_data = None
        self.consistency_data = None
        self.rotation_data = None
        self.report_date = datetime.now()
        
    def load_all_data(self):
        """Carga todos los datos necesarios para el reporte"""
        success_count = 0
        
        # Cargar screening results
        try:
            with open('weekly_screening_results.json', 'r') as f:
                self.screening_data = json.load(f)
                print("✓ Datos de screening cargados")
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
        
        # Cargar rotation recommendations
        try:
            with open('rotation_recommendations.json', 'r') as f:
                self.rotation_data = json.load(f)
                print("✓ Recomendaciones de rotación cargadas")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando rotación: {e}")
        
        return success_count >= 2  # Al menos 2 de 3 archivos necesarios
    
    def create_markdown_report(self):
        """Crea reporte semanal en formato Markdown"""
        report_filename = f"WEEKLY_REPORT_{self.report_date.strftime('%Y_%m_%d')}.md"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# 📊 ANÁLISIS SEMANAL CONSERVADOR - {self.report_date.strftime('%d %B %Y')}\n\n")
            
            # Resumen ejecutivo
            self.write_executive_summary(f)
            
            # Screening results
            if self.screening_data:
                self.write_screening_section(f)
            
            # Consistency analysis
            if self.consistency_data:
                self.write_consistency_section(f)
            
            # Rotation recommendations
            if self.rotation_data:
                self.write_rotation_section(f)
            
            # Market context
            self.write_market_context(f)
            
            # Footer
            f.write(f"\n---\n\n")
            f.write(f"**Generado automáticamente:** {self.report_date.isoformat()}\n")
            f.write(f"**Próximo análisis:** {(self.report_date + timedelta(days=7)).strftime('%d %B %Y')}\n")
            f.write(f"**Estrategia:** Inversión conservadora a largo plazo (2-3 meses por posición)\n\n")
            f.write(f"🤖 *Trading Bot Automatizado by 0t4c0n*\n")
        
        print(f"✅ Reporte Markdown creado: {report_filename}")
        return report_filename
    
    def write_executive_summary(self, f):
        """Escribe resumen ejecutivo"""
        f.write("## 🎯 **RESUMEN EJECUTIVO**\n\n")
        
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            overall_action = action_summary.get('overall_action', 'NO_DATA')
            
            if overall_action == 'ACTION_REQUIRED':
                f.write("### 🚨 **ACCIÓN REQUERIDA ESTA SEMANA**\n\n")
            elif overall_action == 'EVALUATE_CHANGES':
                f.write("### ⚠️ **EVALUAR CAMBIOS ESTA SEMANA**\n\n")
            else:
                f.write("### ✅ **MANTENER POSICIONES ACTUALES**\n\n")
            
            # Estadísticas clave
            holds = len(action_summary.get('holds', []))
            exits = len(action_summary.get('consider_exits', [])) + len(action_summary.get('urgent_exits', []))
            buys = len(action_summary.get('strong_buys', [])) + len(action_summary.get('watch_buys', []))
            
            f.write(f"- **Posiciones actuales:** {holds} mantener, {exits} evaluar salida\n")
            f.write(f"- **Nuevas oportunidades:** {buys} identificadas\n")
        
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            f.write(f"- **Consistencia:** {stats.get('consistent_winners_count', 0)} winners, {stats.get('strong_candidates_count', 0)} candidates\n")
        
        if self.screening_data:
            total_passed = len(self.screening_data.get('detailed_results', []))
            f.write(f"- **Screening:** {total_passed} acciones pasaron filtros conservadores\n")
        
        f.write("\n")
    
    def write_screening_section(self, f):
        """Escribe sección de screening"""
        f.write("## 🔍 **SCREENING SEMANAL**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        benchmark_context = self.screening_data.get('benchmark_context', {})
        
        f.write(f"**Acciones analizadas:** {len(detailed_results)}\n")
        f.write(f"**Filtros aplicados:** Técnicos + Fundamentales estrictos\n")
        f.write(f"**Benchmark SPY (60d):** {benchmark_context.get('spy_60d', 0):+.1f}%\n\n")
        
        if detailed_results:
            f.write("### 🏆 **TOP 10 ESTA SEMANA**\n\n")
            f.write("| Símbolo | Score | Precio | Risk % | Outperform 60d | Fundamentales |\n")
            f.write("|---------|-------|--------|--------|----------------|---------------|\n")
            
            for i, stock in enumerate(detailed_results[:10]):
                symbol = stock.get('symbol', 'N/A')
                score = stock.get('score', 0)
                price = stock.get('current_price', 0)
                risk = stock.get('risk_pct', 0)
                outperf = stock.get('outperformance_60d', 0)
                fundamentals = stock.get('fundamental_score', 0)
                
                f.write(f"| {symbol} | {score:.1f} | ${price:.2f} | {risk:.1f}% | +{outperf:.1f}% | {fundamentals:.0f}pts |\n")
            
            f.write("\n")
    
    def write_consistency_section(self, f):
        """Escribe sección de análisis de consistencia"""
        f.write("## 📈 **ANÁLISIS DE CONSISTENCIA (5 SEMANAS)**\n\n")
        
        consistency_analysis = self.consistency_data.get('consistency_analysis', {})
        
        # Consistent Winners
        consistent_winners = consistency_analysis.get('consistent_winners', [])
        if consistent_winners:
            f.write("### 🏆 **CONSISTENT WINNERS** (Alta confianza - 4+ semanas)\n\n")
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
            f.write("### 🌱 **EMERGING OPPORTUNITIES** (Vigilar - 2 semanas)\n\n")
            for opp in emerging[:5]:
                symbol = opp['symbol']
                frequency = opp['frequency']
                appeared = "✅" if opp.get('appeared_this_week', False) else "❌"
                
                f.write(f"- **{symbol}** - {frequency}/5 semanas - Esta semana: {appeared}\n")
            f.write("\n")
        
        # Trend changes
        trend_changes = self.consistency_data.get('trend_changes', {})
        newly_emerged = trend_changes.get('newly_emerged', [])
        disappeared = trend_changes.get('disappeared_this_week', [])
        
        if newly_emerged:
            f.write(f"### 🆕 **NUEVAS APARICIONES:** {', '.join(newly_emerged[:10])}\n\n")
        
        if disappeared:
            f.write(f"### 📉 **DESAPARECIERON:** {', '.join(disappeared[:10])}\n\n")
    
    def write_rotation_section(self, f):
        """Escribe sección de recomendaciones de rotación"""
        f.write("## 🔄 **RECOMENDACIONES DE ROTACIÓN**\n\n")
        
        if not self.rotation_data:
            f.write("*No hay datos de rotación disponibles*\n\n")
            return
        
        action_summary = self.rotation_data.get('action_summary', {})
        
        # Posiciones actuales
        f.write("### 📂 **TU CARTERA ACTUAL**\n\n")
        
        holds = action_summary.get('holds', [])
        if holds:
            f.write("#### ✅ **MANTENER:**\n")
            for hold in holds:
                f.write(f"- **{hold['symbol']}** - {hold['reason']}\n")
            f.write("\n")
        
        urgent_exits = action_summary.get('urgent_exits', [])
        if urgent_exits:
            f.write("#### 🚨 **SALIDA URGENTE:**\n")
            for exit in urgent_exits:
                f.write(f"- **{exit['symbol']}** - {exit['reason']}\n")
            f.write("\n")
        
        consider_exits = action_summary.get('consider_exits', [])
        if consider_exits:
            f.write("#### ⚠️ **CONSIDERAR SALIDA:**\n")
            for exit in consider_exits:
                f.write(f"- **{exit['symbol']}** - {exit['reason']}\n")
            f.write("\n")
        
        # Nuevas oportunidades
        strong_buys = action_summary.get('strong_buys', [])
        if strong_buys:
            f.write("### 🔥 **COMPRAS DE ALTA CONFIANZA**\n\n")
            for buy in strong_buys:
                price_info = f" - ${buy['price']:.2f}" if buy.get('price') else ""
                risk_info = f" (Risk: {buy['risk']:.1f}%)" if buy.get('risk') else ""
                f.write(f"- **{buy['symbol']}**{price_info}{risk_info} - {buy['reason']}\n")
            f.write("\n")
        
        watch_buys = action_summary.get('watch_buys', [])
        if watch_buys:
            f.write("### 👀 **VIGILAR PARA COMPRA**\n\n")
            for buy in watch_buys:
                price_info = f" - ${buy['price']:.2f}" if buy.get('price') else ""
                f.write(f"- **{buy['symbol']}**{price_info} - {buy['reason']}\n")
            f.write("\n")
        
        # Lista de vigilancia
        watchlist = self.rotation_data.get('watchlist', [])
        if watchlist:
            f.write("### 📋 **LISTA DE VIGILANCIA**\n\n")
            f.write("*Símbolos para monitorear próximas semanas:*\n\n")
            for item in watchlist[:10]:
                f.write(f"- **{item['symbol']}** - {item['reason']} - *{item['action']}*\n")
            f.write("\n")
    
    def write_market_context(self, f):
        """Escribe contexto de mercado"""
        f.write("## 📊 **CONTEXTO DE MERCADO**\n\n")
        
        if self.screening_data:
            benchmark = self.screening_data.get('benchmark_context', {})
            f.write(f"**SPY Performance:**\n")
            f.write(f"- 20 días: {benchmark.get('spy_20d', 0):+.1f}%\n")
            f.write(f"- 60 días: {benchmark.get('spy_60d', 0):+.1f}%\n")
            f.write(f"- 90 días: {benchmark.get('spy_90d', 0):+.1f}%\n\n")
        
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            f.write(f"**Análisis de Consistencia:**\n")
            f.write(f"- Símbolos únicos analizados: {stats.get('total_unique_symbols', 0)}\n")
            f.write(f"- Consistent Winners: {stats.get('consistent_winners_count', 0)}\n")
            f.write(f"- Strong Candidates: {stats.get('strong_candidates_count', 0)}\n")
            f.write(f"- Emerging Opportunities: {stats.get('emerging_count', 0)}\n\n")
        
        f.write("**Filosofía de Inversión:**\n")
        f.write("- Objetivo: Superar al SPY con riesgo controlado\n")
        f.write("- Holding period: 2-3 meses por posición\n")
        f.write("- Decisiones basadas en consistencia, no ruido semanal\n")
        f.write("- Filtros técnicos + fundamentales estrictos\n\n")
    
    def create_dashboard_data(self):
        """Crea datos JSON para el dashboard web"""
        dashboard_data = {
            "timestamp": self.report_date.isoformat(),
            "market_date": self.report_date.strftime("%Y-%m-%d"),
            "summary": {
                "analysis_type": "Conservative Long-term",
                "total_analyzed": 0,
                "passed_filters": 0,
                "consistent_winners": 0,
                "strong_candidates": 0,
                "message": "Análisis semanal conservador completado"
            },
            "top_picks": [],
            "consistency_analysis": {},
            "rotation_recommendations": {},
            "market_context": {}
        }
        
        # Datos de screening
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            dashboard_data["summary"]["passed_filters"] = len(detailed_results)
            
            # Top picks para dashboard
            for i, stock in enumerate(detailed_results[:10]):
                pick = {
                    "rank": i + 1,
                    "symbol": stock.get('symbol', ''),
                    "company": stock.get('company_info', {}).get('name', 'N/A')[:30],
                    "sector": stock.get('company_info', {}).get('sector', 'N/A'),
                    "price": stock.get('current_price', 0),
                    "score": stock.get('score', 0),
                    "metrics": {
                        "risk_pct": stock.get('risk_pct', 0),
                        "outperformance_60d": stock.get('outperformance_60d', 0),
                        "volume_surge": stock.get('volume_surge', 0),
                        "fundamental_score": stock.get('fundamental_score', 0)
                    },
                    "ma_levels": stock.get('ma_levels', {}),
                    "target_hold": stock.get('target_hold', '2-3 meses')
                }
                dashboard_data["top_picks"].append(pick)
        
        # Datos de consistencia
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
        
        # Datos de rotación
        if self.rotation_data:
            dashboard_data["rotation_recommendations"] = {
                "overall_action": self.rotation_data.get('action_summary', {}).get('overall_action', 'NO_DATA'),
                "strong_buys": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('strong_buys', [])],
                "consider_exits": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('consider_exits', [])],
                "urgent_exits": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('urgent_exits', [])],
                "holds": [s['symbol'] for s in self.rotation_data.get('action_summary', {}).get('holds', [])]
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
        
        print("✅ Datos del dashboard guardados: docs/data.json")
        return dashboard_data
    
    def generate_complete_report(self):
        """Genera reporte completo (Markdown + Dashboard)"""
        print("📋 Generando reporte semanal completo...")
        
        # Cargar todos los datos
        if not self.load_all_data():
            print("❌ No se pudieron cargar suficientes datos")
            return False
        
        # Crear reporte Markdown
        markdown_file = self.create_markdown_report()
        
        # Crear datos para dashboard
        dashboard_data = self.create_dashboard_data()
        
        print(f"✅ Reporte semanal completado:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - Dashboard: docs/data.json")
        
        return True

def main():
    """Función principal para GitHub Actions"""
    generator = WeeklyReportGenerator()
    
    success = generator.generate_complete_report()
    
    if success:
        print("\n✅ Reporte semanal generado exitosamente")
    else:
        print("\n❌ Error generando reporte semanal")

if __name__ == "__main__":
    main()

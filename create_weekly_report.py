#!/usr/bin/env python3
"""
Aggressive Momentum Weekly Report Generator - Con análisis de momentum responsivo
Integra rotación mensual, momentum categories, y gestión agresiva
🆕 INCLUYE GESTIÓN AUTOMÁTICA DE HISTORIAL
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
            f.write(f"# ⚡ MOMENTUM AGRESIVO - SWING FOR THE FENCES - {self.report_date.strftime('%d %B %Y')}\n\n")
            
            # Resumen ejecutivo agresivo
            self.write_aggressive_executive_summary(f)
            
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
            
            # Gestión agresiva de momentum
            self.write_aggressive_momentum_management(f)
            
            # Contexto de mercado
            self.write_momentum_market_context(f)
            
            # Footer
            f.write(f"\n---\n\n")
            f.write(f"**Generado automáticamente:** {self.report_date.isoformat()}\n")
            f.write(f"**Próximo análisis:** {(self.report_date + timedelta(days=7)).strftime('%d %B %Y')}\n")
            f.write(f"**Estrategia:** Momentum agresivo con rotación mensual\n\n")
            f.write(f"⚡ *Aggressive Momentum Trading Bot - Swing for the Fences by 0t4c0n*\n")
        
        print(f"✅ Reporte Markdown agresivo creado: {report_filename}")
        return report_filename
    
    def write_aggressive_executive_summary(self, f):
        """Escribe resumen ejecutivo de momentum agresivo"""
        f.write("## ⚡ **RESUMEN EJECUTIVO - MOMENTUM AGRESIVO**\n\n")
        
        # Detectar nivel de agresividad
        exceptional_count = 0
        strong_count = 0
        avg_momentum_20d = 0
        avg_rr_ratio = 0
        urgent_rotations = 0
        
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
        f.write(f"**🎯 FILOSOFÍA:** Swing for the Fences - Rotación mensual hacia mejores oportunidades\n\n")
        f.write(f"- **Momentum excepcional detectado:** {exceptional_count} acciones (rotación urgente)\n")
        f.write(f"- **Momentum fuerte identificado:** {strong_count} acciones (rotación agresiva)\n")
        f.write(f"- **Rotaciones urgentes recomendadas:** {urgent_rotations}\n")
        f.write(f"- **Momentum 20d promedio:** {avg_momentum_20d:.1f}% (peso 70% en scoring)\n")
        f.write(f"- **R/R promedio:** {avg_rr_ratio:.1f}:1 (targets agresivos)\n")
        f.write(f"- **Target hold period:** ~1 mes (vs 2-3 meses conservador)\n\n")
        
        f.write(f"**⚖️ BALANCE RIESGO/MOMENTUM:**\n")
        f.write(f"- Rotación agresiva hacia momentum superior\n")
        f.write(f"- Salida rápida si momentum se debilita (1+ semanas ausencia)\n")
        f.write(f"- Targets adaptativos según categoría de momentum\n\n")
    
    def write_momentum_philosophy(self, f):
        """Escribe la filosofía de momentum agresivo"""
        f.write("## 🎯 **FILOSOFÍA: SWING FOR THE FENCES**\n\n")
        
        f.write("### **🚀 Cambio de Paradigma: De Conservador a Agresivo**\n\n")
        f.write("El sistema ha evolucionado de una estrategia conservadora a **momentum trading agresivo** ")
        f.write("con rotación mensual. El objetivo es capturar las mejores oportunidades de momentum ")
        f.write("y rotar agresivamente hacia posiciones superiores.\n\n")
        
        f.write("### **📊 Nuevos Pesos de Momentum:**\n\n")
        f.write("| Timeframe | Peso | Razón |\n")
        f.write("|-----------|------|-------|\n")
        f.write("| **Momentum 20d** | **70%** | Momentum reciente más predictivo para rotación mensual |\n")
        f.write("| **Momentum 60d** | **30%** | Contexto de tendencia de mediano plazo |\n\n")
        
        f.write("### **🎪 Categorías de Momentum:**\n\n")
        f.write("- **🔥 EXCEPCIONAL** (Score >200 OR Momentum 20d >25%): Rotación urgente\n")
        f.write("- **⚡ FUERTE** (Score >150 OR Momentum 20d >15%): Rotación agresiva\n")
        f.write("- **📈 MODERADO** (Score >100 OR Momentum 20d >8%): Vigilar evolución\n")
        f.write("- **⚠️ DÉBIL** (Score <100): No rotar, considerar salida\n\n")
        
        if self.rotation_data:
            params = self.rotation_data.get('aggressive_parameters', {})
            f.write("### **🔧 Parámetros Agresivos:**\n\n")
            f.write(f"- **Threshold de rotación:** {params.get('rotation_threshold', '20% score superior')}\n")
            f.write(f"- **Consistencia mínima:** {params.get('min_consistency_weeks', 2)} semanas (vs 5 conservador)\n")
            f.write(f"- **Peso oportunidades emergentes:** {params.get('emerging_opportunity_weight', 1.5)}x\n")
            f.write(f"- **Threshold deterioro momentum:** {params.get('momentum_decay_threshold', '15%')}\n\n")
    
    def write_momentum_picks_with_categories(self, f):
        """Escribe top picks con categorías de momentum"""
        f.write("## 🔥 **TOP MOMENTUM PICKS - CATEGORÍAS AGRESIVAS**\n\n")
        
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
                f.write("### 🔥 **MOMENTUM EXCEPCIONAL - ROTACIÓN URGENTE**\n\n")
                f.write("*Estas acciones muestran momentum excepcional. Rotación urgente recomendada.*\n\n")
                
                for i, stock in enumerate(exceptional):
                    self.write_momentum_stock_detail(f, stock, i+1, "EXCEPCIONAL")
                f.write("\n")
            
            # Momentum FUERTE
            if strong:
                f.write("### ⚡ **MOMENTUM FUERTE - ROTACIÓN AGRESIVA**\n\n")
                f.write("*Candidatos sólidos para rotación agresiva con momentum sostenible.*\n\n")
                
                for i, stock in enumerate(strong):
                    self.write_momentum_stock_detail(f, stock, i+1, "FUERTE")
                f.write("\n")
            
            # Momentum MODERADO
            if moderate:
                f.write("### 📈 **MOMENTUM MODERADO - VIGILAR EVOLUCIÓN**\n\n")
                f.write("*Momentum aceptable. Vigilar para confirmar strength antes de rotación.*\n\n")
                
                for i, stock in enumerate(moderate[:3]):  # Solo top 3
                    self.write_momentum_stock_detail(f, stock, i+1, "MODERADO")
                f.write("\n")
    
    def write_momentum_stock_detail(self, f, stock, rank, category):
        """Escribe detalle de una acción con enfoque en momentum"""
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
        
        f.write(f"#### **{rank}. {symbol}** - Momentum {category}\n\n")
        
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
        
        # Momentum analysis (peso 70% + 30%)
        f.write(f"**⚡ ANÁLISIS DE MOMENTUM:**\n")
        f.write(f"- **Momentum 20d:** +{momentum_20d:.1f}% vs SPY *(peso 70%)*\n")
        f.write(f"- **Momentum 60d:** +{momentum_60d:.1f}% vs SPY *(peso 30%)*\n")
        
        # Calcular momentum score total
        momentum_score = (momentum_20d * 0.7) + (momentum_60d * 0.3)
        f.write(f"- **Momentum Score Ponderado:** {momentum_score:.1f}%\n")
        
        # Trading levels agresivos
        f.write(f"- **Precio actual:** ${current_price:.2f}\n")
        f.write(f"- **Target agresivo:** ${take_profit:.2f} ({upside_pct:.1f}% upside)\n")
        f.write(f"- **Stop loss:** ${stop_loss:.2f}\n\n")
        
        # Recomendación de rotación
        if category == "EXCEPCIONAL":
            f.write(f"**🚨 ACCIÓN:** Rotación urgente recomendada - Momentum excepcional\n")
        elif category == "FUERTE":
            f.write(f"**⚡ ACCIÓN:** Rotación agresiva recomendada - Momentum sólido\n")
        else:
            f.write(f"**👁️ ACCIÓN:** Vigilar evolución - Confirmar strength\n")
        
        # Target hold
        f.write(f"**🎯 Target Hold:** ~1 mes (rotación mensual agresiva)\n\n")
        
        f.write("---\n\n")
    
    def write_momentum_responsive_analysis(self, f):
        """Escribe análisis de screening con enfoque en momentum responsivo"""
        f.write("## 📊 **ANÁLISIS MOMENTUM RESPONSIVO**\n\n")
        
        detailed_results = self.screening_data.get('detailed_results', [])
        methodology = self.screening_data.get('methodology', {})
        
        f.write(f"**Acciones analizadas:** {len(detailed_results)}\n")
        f.write(f"**Metodología:** {methodology.get('scoring', 'Momentum responsivo con rotación agresiva')}\n\n")
        
        # Estadísticas de momentum
        if detailed_results:
            # Clasificación por momentum
            exceptional_count = len([s for s in detailed_results if s.get('score', 0) > 200 or s.get('outperformance_20d', 0) > 25])
            strong_count = len([s for s in detailed_results if 150 <= s.get('score', 0) <= 200 or 15 <= s.get('outperformance_20d', 0) <= 25])
            moderate_count = len(detailed_results) - exceptional_count - strong_count
            
            f.write(f"### 🔥 **DISTRIBUCIÓN DE MOMENTUM:**\n\n")
            f.write(f"- **Excepcional:** {exceptional_count} acciones ({(exceptional_count/len(detailed_results)*100):.1f}%)\n")
            f.write(f"- **Fuerte:** {strong_count} acciones ({(strong_count/len(detailed_results)*100):.1f}%)\n")
            f.write(f"- **Moderado:** {moderate_count} acciones ({(moderate_count/len(detailed_results)*100):.1f}%)\n\n")
            
            # Métricas promedio
            avg_momentum_20d = sum(r.get('outperformance_20d', 0) for r in detailed_results) / len(detailed_results)
            avg_momentum_60d = sum(r.get('outperformance_60d', 0) for r in detailed_results) / len(detailed_results)
            avg_rr = sum(r.get('risk_reward_ratio', 0) for r in detailed_results) / len(detailed_results)
            avg_upside = sum(r.get('upside_pct', 0) for r in detailed_results) / len(detailed_results)
            
            f.write(f"### 📈 **MÉTRICAS MOMENTUM PROMEDIO:**\n\n")
            f.write(f"- **Momentum 20d promedio:** {avg_momentum_20d:.1f}% (peso 70%)\n")
            f.write(f"- **Momentum 60d promedio:** {avg_momentum_60d:.1f}% (peso 30%)\n")
            f.write(f"- **Risk/Reward promedio:** {avg_rr:.1f}:1 (targets agresivos)\n")
            f.write(f"- **Upside promedio:** {avg_upside:.1f}% (~1 mes objetivo)\n\n")
        
        # Top 10 con métricas de momentum
        if detailed_results:
            f.write("### ⚡ **TOP 10 MOMENTUM RANKING**\n\n")
            f.write("| Rank | Símbolo | Score Final | Momentum 20d | Momentum 60d | R/R | Categoría |\n")
            f.write("|------|---------|-------------|--------------|--------------|-----|----------|\n")
            
            for i, stock in enumerate(detailed_results[:10]):
                symbol = stock.get('symbol', 'N/A')
                score = stock.get('score', 0)
                mom_20d = stock.get('outperformance_20d', 0)
                mom_60d = stock.get('outperformance_60d', 0)
                rr = stock.get('risk_reward_ratio', 0)
                
                # Determinar categoría
                if score > 200 or mom_20d > 25:
                    category = "🔥 EXCEPCIONAL"
                elif score > 150 or mom_20d > 15:
                    category = "⚡ FUERTE"
                else:
                    category = "📈 MODERADO"
                
                f.write(f"| {i+1} | **{symbol}** | {score:.1f} | +{mom_20d:.1f}% | +{mom_60d:.1f}% | {rr:.1f}:1 | {category} |\n")
            
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
        """Escribe guía de gestión agresiva de momentum"""
        f.write("## ⚡ **GESTIÓN AGRESIVA DE MOMENTUM**\n\n")
        
        f.write("### 🎯 **Filosofía: Swing for the Fences**\n\n")
        f.write("El momentum trading agresivo requiere **rotación activa** hacia las mejores oportunidades. ")
        f.write("A diferencia del enfoque conservador, priorizamos **velocidad de ejecución** y ")
        f.write("**salidas tempranas** cuando el momentum se debilita.\n\n")
        
        f.write("### 🔄 **Criterios de Rotación Mensual:**\n\n")
        f.write("#### **🔥 ROTAR INMEDIATAMENTE (hacia momentum superior):**\n")
        f.write("- ✅ Nueva oportunidad con score 20%+ superior\n")
        f.write("- ✅ Momentum excepcional detectado (categoría EXCEPCIONAL)\n")
        f.write("- ✅ Acceleration signals confirmados (aparece esta semana + 2+ semanas historial)\n")
        f.write("- ✅ R/R ratio >3.5:1 con momentum sólido\n\n")
        
        f.write("#### **⚡ ROTAR AGRESIVAMENTE (en 1-2 días):**\n")
        f.write("- ⚠️ Momentum fuerte identificado con 3+ semanas consistencia\n")
        f.write("- ⚠️ Posición actual perdiendo momentum (no aparece esta semana)\n")
        f.write("- ⚠️ Deterioro técnico visible (RSI divergencia, volume decay)\n")
        f.write("- ⚠️ Sector rotation hacia áreas de mayor momentum\n\n")
        
        f.write("#### **❌ SALIR INMEDIATAMENTE:**\n")
        f.write("- ❌ Ausencia 2+ semanas consecutivas (momentum perdido)\n")
        f.write("- ❌ Categoría momentum cambió a DÉBIL o inferior\n")
        f.write("- ❌ Score deterioró >15% semana a semana\n")
        f.write("- ❌ Underperformance vs SPY por 2+ semanas\n")
        f.write("- ❌ Stop loss técnico alcanzado\n\n")
        
        f.write("### 📅 **Workflow Semanal Agresivo:**\n\n")
        f.write("1. **Lunes AM:** Revisar reporte y identificar rotaciones urgentes\n")
        f.write("2. **Lunes PM:** Ejecutar salidas urgentes y rotaciones excepcionales\n")
        f.write("3. **Martes:** Ejecutar rotaciones agresivas restantes\n")
        f.write("4. **Miércoles:** Evaluar oportunidades emergentes\n")
        f.write("5. **Jueves-Viernes:** Ajustar stops y preparar próxima semana\n")
        f.write("6. **Sábado:** Actualizar portfolio con cambios reales\n\n")
        
        f.write("### ⚖️ **Balance Agresivo Riesgo-Momentum:**\n\n")
        f.write("- **Objetivo:** Capturar 15-25% por posición en ~1 mes\n")
        f.write("- **Win rate target:** 55-65% (mayor volatilidad aceptable)\n")
        f.write("- **Max drawdown:** <12% por posición (momentum stops)\n")
        f.write("- **Portfolio turnover:** 8-12 rotaciones por año (alta actividad)\n")
        f.write("- **Risk per trade:** 8-10% (más agresivo que conservador 5%)\n\n")
    
    def write_momentum_market_context(self, f):
        """Escribe contexto de mercado con enfoque en momentum"""
        f.write("## 📊 **CONTEXTO DE MERCADO - MOMENTUM GLOBAL**\n\n")
        
        if self.screening_data:
            benchmark = self.screening_data.get('benchmark_context', {})
            f.write(f"### 📈 **SPY Momentum Benchmark:**\n")
            f.write(f"- **20 días:** {benchmark.get('spy_20d', 0):+.1f}% *(peso 70% en scoring)*\n")
            f.write(f"- **60 días:** {benchmark.get('spy_60d', 0):+.1f}% *(peso 30% en scoring)*\n")
            f.write(f"- **90 días:** {benchmark.get('spy_90d', 0):+.1f}% *(contexto tendencial)*\n\n")
        
        if self.consistency_data:
            stats = self.consistency_data.get('summary_stats', {})
            f.write(f"### 🎯 **Análisis de Momentum Semanal:**\n")
            f.write(f"- **Símbolos únicos analizados:** {stats.get('total_unique_symbols', 0)}\n")
            f.write(f"- **Momentum consistente:** {stats.get('consistent_winners_count', 0)}\n")
            f.write(f"- **Momentum fuerte:** {stats.get('strong_candidates_count', 0)}\n")
            f.write(f"- **Momentum emergente:** {stats.get('emerging_count', 0)}\n\n")
        
        # Metodología agresiva
        f.write(f"### 🔬 **Metodología Momentum Agresivo:**\n")
        f.write(f"- **Scoring:** Score técnico + (R/R ratio × 12) para ranking final\n")
        f.write(f"- **Momentum weighting:** 70% peso a momentum 20d, 30% a momentum 60d\n")
        f.write(f"- **Exit criteria:** Ausencia 1+ semanas OR deterioro score >15%\n")
        f.write(f"- **Rotation threshold:** Score 20% superior OR momentum excepcional\n")
        f.write(f"- **Target calculation:** ATR × (2.3 to 3.5) basado en momentum strength\n\n")
        
        f.write("### 🎯 **Filosofía de Momentum Actualizada:**\n")
        f.write("- **Objetivo:** Capturar momentum superior con rotación mensual\n")
        f.write("- **Holding period:** ~1 mes con salidas agresivas si momentum se debilita\n")
        f.write("- **Decisiones:** Momentum strength + acceleration signals + technical quality\n")
        f.write("- **Risk management:** Momentum stops + volatility scaling + quick exits\n")
        f.write("- **Success metric:** Outperformance vs SPY con mayor win rate que buy&hold\n\n")
    
    def create_aggressive_dashboard_data(self, f):
        """Crea datos JSON para el dashboard agresivo"""
        dashboard_data = {
            "timestamp": self.report_date.isoformat(),
            "market_date": self.report_date.strftime("%Y-%m-%d"),
            "analysis_type": "aggressive_momentum_responsive",
            "summary": {
                "analysis_type": "Aggressive Momentum Responsive",
                "total_analyzed": 0,
                "exceptional_momentum": 0,
                "strong_momentum": 0,
                "rotation_opportunities": 0,
                "message": "Análisis momentum agresivo con rotación mensual completado"
            },
            "top_picks": [],
            "momentum_analysis": {
                "philosophy": "swing_for_fences_monthly_rotation",
                "momentum_weights": {
                    "momentum_20d": 0.70,
                    "momentum_60d": 0.30
                },
                "exceptional_momentum": [],
                "strong_momentum": [],
                "emerging_momentum": []
            },
            "rotation_recommendations": {},
            "market_context": {}
        }
        
        # Datos de screening agresivo
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            dashboard_data["summary"]["total_analyzed"] = len(detailed_results)
            
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
                
                # Añadir a top picks con categoría
                if len(dashboard_data["top_picks"]) < 10:
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
                        "target_hold": "~1 mes (rotación agresiva)",
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
        
        # Guardar datos del dashboard agresivo
        with open('docs/data.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        print("✅ Datos del dashboard agresivo guardados: docs/data.json")
        return dashboard_data
    
    def generate_complete_aggressive_report(self):
        """Genera reporte completo de momentum agresivo"""
        print("📋 Generando reporte semanal de MOMENTUM AGRESIVO...")
        
        # Cargar todos los datos
        if not self.load_all_data():
            print("❌ No se pudieron cargar suficientes datos")
            return False
        
        # Crear reporte Markdown agresivo
        markdown_file = self.create_aggressive_markdown_report()
        
        # Crear datos para dashboard agresivo
        dashboard_data = self.create_aggressive_dashboard_data()
        
        print(f"✅ Reporte momentum agresivo completado:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - Dashboard: docs/data.json")
        print(f"   - Incluye: Momentum categories, rotación mensual, targets agresivos")
        
        return True

def main():
    """Función principal para momentum agresivo"""
    generator = AggressiveMomentumReportGenerator()
    
    success = generator.generate_complete_aggressive_report()
    
    if success:
        print("\n✅ Reporte momentum agresivo generado exitosamente")
        print("\n⚡ NUEVAS CARACTERÍSTICAS AGRESIVAS:")
        print("   - Momentum categories (EXCEPCIONAL, FUERTE, MODERADO)")
        print("   - Rotación mensual hacia mejores oportunidades")
        print("   - Pesos momentum: 70% (20d) + 30% (60d)")
        print("   - Targets agresivos con sistema ATR adaptativo")
        print("   - Salidas rápidas cuando momentum se debilita")
        print("   - Dashboard responsivo con urgencia de rotación")
        print("   - Gestión automática de historial de reportes agresivos")
    else:
        print("\n❌ Error generando reporte momentum agresivo")

if __name__ == "__main__":
    main()
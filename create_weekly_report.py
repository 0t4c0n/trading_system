#!/usr/bin/env python3
"""
Daily Trading Report Generator - Adaptado para ejecución diaria
Genera reportes diarios para trading mensual con MA50 bonus y criterios estrictos
🔄 ADAPTADO: De reportes semanales a reportes diarios
🎯 FILOSOFÍA: Daily monitoring, monthly trading
🌟 INCLUYE: MA50 bonus system tracking
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class DailyTradingReportGenerator:
    def __init__(self):
        self.screening_data = None
        self.consistency_data = None
        self.rotation_data = None
        self.report_date = datetime.now()
        
    def load_all_data(self):
        """Carga todos los datos necesarios para reporte diario"""
        success_count = 0
        
        # Cargar screening results (diario)
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
        
        # Cargar rotation recommendations (trading mensual)
        try:
            with open('rotation_recommendations.json', 'r') as f:
                self.rotation_data = json.load(f)
                print("✓ Recomendaciones de trading mensual cargadas")
                success_count += 1
        except Exception as e:
            print(f"⚠️ Error cargando rotación: {e}")
        
        return success_count >= 2
    
    def create_daily_markdown_report(self):
        """Crea reporte diario de trading mensual en formato Markdown"""
        report_filename = f"ENHANCED_DAILY_REPORT_{self.report_date.strftime('%Y_%m_%d')}.md"
        
        # Archivar reporte anterior si existe
        if os.path.exists(report_filename):
            try:
                timestamp = datetime.now().strftime('%H%M%S')
                backup_name = f"ENHANCED_DAILY_REPORT_{self.report_date.strftime('%Y_%m_%d')}_{timestamp}.md"
                os.rename(report_filename, backup_name)
                print(f"📁 Reporte anterior respaldado: {backup_name}")
            except Exception as e:
                print(f"⚠️ Error respaldando reporte anterior: {e}")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            self.write_daily_header(f)
            self.write_executive_daily_summary(f)
            self.write_ma50_bonus_analysis(f)
            self.write_daily_consistency_analysis(f)
            self.write_monthly_trading_recommendations(f)
            self.write_daily_market_context(f)
            self.write_optimization_metrics(f)
            self.write_daily_methodology(f)
        
        print(f"✅ Reporte diario creado: {report_filename}")
        return report_filename
    
    def write_daily_header(self, f):
        """Escribe cabecera del reporte diario"""
        f.write(f"# 📈 DAILY TRADING REPORT - {self.report_date.strftime('%B %d, %Y')}\n\n")
        f.write(f"## 🎯 **Monthly Trading with Daily Monitoring**\n\n")
        f.write(f"**📅 Report Date:** {self.report_date.strftime('%A, %B %d, %Y')}\n")
        f.write(f"**🔄 Execution Frequency:** Daily (Mon-Fri post-market)\n")
        f.write(f"**🎯 Trading Philosophy:** Monthly trades (~1 month holds) with daily monitoring\n")
        f.write(f"**🌟 MA50 Bonus System:** Active (+22 points for bullish rebounds)\n")
        f.write(f"**⚠️ Rotation Criteria:** Strict (+30pt threshold, stop proximity, momentum loss)\n\n")
        f.write("---\n\n")
    
    def write_executive_daily_summary(self, f):
        """Escribe resumen ejecutivo diario"""
        f.write("## 📋 **DAILY EXECUTIVE SUMMARY**\n\n")
        
        if not self.screening_data:
            f.write("*No screening data available for daily summary*\n\n")
            return
        
        detailed_results = self.screening_data.get('detailed_results', [])
        total_analyzed = len(detailed_results)
        
        # Métricas de MA50 bonus
        ma50_bonus_count = 0
        ma50_bonus_stocks = []
        for stock in detailed_results:
            if stock.get('optimizations', {}).get('ma50_bonus_applied', False):
                ma50_bonus_count += 1
                ma50_bonus_stocks.append(stock['symbol'])
        
        # Estadísticas de consistencia diaria
        consistent_count = 0
        strong_candidate_count = 0
        if self.consistency_data:
            consistency_analysis = self.consistency_data.get('consistency_analysis', {})
            consistent_count = len(consistency_analysis.get('consistent_winners', []))
            strong_candidate_count = len(consistency_analysis.get('strong_candidates', []))
        
        # Recomendaciones de rotación
        rotation_actions = 0
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            rotation_actions = (len(action_summary.get('urgent_exits', [])) + 
                              len(action_summary.get('rotation_opportunities', [])))
        
        f.write(f"### **🔍 Daily Screening Results**\n")
        f.write(f"- **Total analyzed:** {total_analyzed:,} stocks\n")
        f.write(f"- **🌟 MA50 bonus applied:** {ma50_bonus_count} stocks ({ma50_bonus_count/max(total_analyzed,1)*100:.1f}%)\n")
        f.write(f"- **Consistent winners:** {consistent_count} (5+ days)\n")
        f.write(f"- **Strong candidates:** {strong_candidate_count} (3-4 days)\n\n")
        
        f.write(f"### **🎯 Monthly Trading Assessment**\n")
        f.write(f"- **Rotation actions required:** {rotation_actions}\n")
        f.write(f"- **Daily monitoring status:** {'🟢 Normal' if rotation_actions <= 2 else '🟡 Attention' if rotation_actions <= 5 else '🔴 High Activity'}\n")
        f.write(f"- **Trading philosophy alignment:** {'✅ Aligned' if rotation_actions <= 3 else '⚠️ Review Required'}\n\n")
        
        if ma50_bonus_stocks:
            f.write(f"### **🌟 MA50 Bonus Highlights (Today)**\n")
            for stock in ma50_bonus_stocks[:5]:
                f.write(f"- **{stock}** - Bullish rebound signal detected\n")
            if len(ma50_bonus_stocks) > 5:
                f.write(f"- *...and {len(ma50_bonus_stocks) - 5} more*\n")
            f.write("\n")
        
        f.write("---\n\n")
    
    def write_ma50_bonus_analysis(self, f):
        """🌟 Nueva sección: Análisis detallado del sistema MA50 bonus"""
        f.write("## 🌟 **MA50 BONUS SYSTEM ANALYSIS**\n\n")
        
        if not self.screening_data:
            f.write("*No data available for MA50 bonus analysis*\n\n")
            return
        
        detailed_results = self.screening_data.get('detailed_results', [])
        
        # Estadísticas MA50
        ma50_stocks = []
        total_ma50_bonus = 0
        avg_score_with_ma50 = 0
        avg_score_without_ma50 = 0
        
        with_ma50 = []
        without_ma50 = []
        
        for stock in detailed_results:
            optimizations = stock.get('optimizations', {})
            if optimizations.get('ma50_bonus_applied', False):
                ma50_stocks.append({
                    'symbol': stock['symbol'],
                    'bonus_value': optimizations.get('ma50_bonus_value', 0),
                    'final_score': stock.get('score', 0),
                    'risk_pct': stock.get('risk_pct', 0),
                    'current_price': stock.get('current_price', 0)
                })
                total_ma50_bonus += optimizations.get('ma50_bonus_value', 0)
                with_ma50.append(stock.get('score', 0))
            else:
                without_ma50.append(stock.get('score', 0))
        
        if with_ma50:
            avg_score_with_ma50 = sum(with_ma50) / len(with_ma50)
        if without_ma50:
            avg_score_without_ma50 = sum(without_ma50) / len(without_ma50)
        
        f.write(f"### **📊 MA50 Bonus Impact Today**\n\n")
        f.write(f"- **Stocks with MA50 bonus:** {len(ma50_stocks)}/{len(detailed_results)} ({len(ma50_stocks)/max(len(detailed_results),1)*100:.1f}%)\n")
        if ma50_stocks:
            avg_bonus = total_ma50_bonus / len(ma50_stocks)
            f.write(f"- **Average bonus value:** +{avg_bonus:.1f} points\n")
            f.write(f"- **Score impact:** {avg_score_with_ma50:.1f} (with) vs {avg_score_without_ma50:.1f} (without)\n")
            f.write(f"- **Performance lift:** +{avg_score_with_ma50 - avg_score_without_ma50:.1f} points average\n\n")
        
        if ma50_stocks:
            f.write(f"### **🏆 Top MA50 Bonus Stocks (Today)**\n\n")
            sorted_ma50 = sorted(ma50_stocks, key=lambda x: x['final_score'], reverse=True)
            
            for i, stock in enumerate(sorted_ma50[:10]):
                f.write(f"{i+1}. **{stock['symbol']}** - Score: {stock['final_score']:.1f} "
                       f"(+{stock['bonus_value']} MA50 bonus) | Risk: {stock['risk_pct']:.1f}%\n")
            f.write("\n")
        
        f.write(f"### **🎯 MA50 System Performance**\n\n")
        f.write(f"- **Detection accuracy:** Identifies bullish rebounds at MA50 support\n")
        f.write(f"- **Risk management:** Prioritizes MA50 as stop loss level\n")
        f.write(f"- **Score enhancement:** +22 base points + 20% multiplier\n")
        f.write(f"- **Monthly alignment:** Perfect for 1-month hold strategy\n\n")
        
        f.write("---\n\n")
    
    def write_daily_consistency_analysis(self, f):
        """Escribe análisis de consistencia diaria"""
        f.write("## 📊 **DAILY CONSISTENCY ANALYSIS (Last 7 Days)**\n\n")
        
        if not self.consistency_data:
            f.write("*No consistency data available*\n\n")
            return
        
        consistency_analysis = self.consistency_data.get('consistency_analysis', {})
        trend_changes = self.consistency_data.get('trend_changes', {})
        
        # Consistent Winners (5+ días)
        consistent_winners = consistency_analysis.get('consistent_winners', [])
        f.write(f"### **🏆 Consistent Winners (5+ of 7 days) - {len(consistent_winners)} stocks**\n\n")
        
        if consistent_winners:
            for stock in consistent_winners[:8]:
                ma50_indicator = " 🌟" if stock.get('ma50_bonus_applied', False) else ""
                trend = stock.get('trend', 'UNKNOWN')
                f.write(f"- **{stock['symbol']}{ma50_indicator}** | "
                       f"{stock['frequency']}/7 days | "
                       f"Score: {stock.get('consistency_score', 0):.1f} | "
                       f"Trend: {trend}\n")
            f.write("\n")
        else:
            f.write("*No consistent winners found in last 7 days*\n\n")
        
        # Strong Candidates (3-4 días)
        strong_candidates = consistency_analysis.get('strong_candidates', [])
        f.write(f"### **💎 Strong Candidates (3-4 of 7 days) - {len(strong_candidates)} stocks**\n\n")
        
        if strong_candidates:
            for stock in strong_candidates[:8]:
                ma50_indicator = " 🌟" if stock.get('ma50_bonus_applied', False) else ""
                trend = stock.get('trend', 'UNKNOWN')
                f.write(f"- **{stock['symbol']}{ma50_indicator}** | "
                       f"{stock['frequency']}/7 days | "
                       f"Score: {stock.get('consistency_score', 0):.1f} | "
                       f"Trend: {trend}\n")
            f.write("\n")
        else:
            f.write("*No strong candidates found*\n\n")
        
        # Consecutive Winners (señal muy fuerte)
        consecutive_winners = trend_changes.get('consecutive_winners', [])
        if consecutive_winners:
            f.write(f"### **🔥 Consecutive Winners - High Conviction Signals**\n\n")
            for stock in consecutive_winners[:5]:
                days_consecutive = len([d for d in stock['days_appeared'] if d >= 5])  # Últimos 3 días
                f.write(f"- **{stock['symbol']}** | {stock['frequency']}/7 days | "
                       f"Consecutive signal strength\n")
            f.write("\n")
        
        # Cambios de tendencia diarios
        f.write(f"### **📈 Daily Trend Changes**\n\n")
        
        newly_emerged = trend_changes.get('newly_emerged_today', [])
        if newly_emerged:
            f.write(f"**🆕 Newly Emerged Today ({len(newly_emerged)}):** {', '.join(newly_emerged[:10])}\n")
            if len(newly_emerged) > 10:
                f.write(f" *(+{len(newly_emerged) - 10} more)*\n")
        
        disappeared = trend_changes.get('disappeared_today', [])
        if disappeared:
            f.write(f"**📉 Disappeared Today ({len(disappeared)}):** {', '.join(disappeared[:10])}\n")
            if len(disappeared) > 10:
                f.write(f" *(+{len(disappeared) - 10} more)*\n")
        
        gaining_momentum = trend_changes.get('gaining_momentum', [])
        if gaining_momentum:
            gaining_symbols = [s['symbol'] for s in gaining_momentum]
            f.write(f"**⬆️ Gaining Momentum ({len(gaining_symbols)}):** {', '.join(gaining_symbols[:8])}\n")
            if len(gaining_symbols) > 8:
                f.write(f" *(+{len(gaining_symbols) - 8} more)*\n")
        
        f.write("\n---\n\n")
    
    def write_monthly_trading_recommendations(self, f):
        """Escribe recomendaciones para trading mensual"""
        f.write("## 💡 **MONTHLY TRADING RECOMMENDATIONS**\n\n")
        
        if not self.rotation_data:
            f.write("*No rotation recommendations available*\n\n")
            return
        
        action_summary = self.rotation_data.get('action_summary', {})
        overall_action = action_summary.get('overall_action', 'NO_DATA')
        
        f.write(f"### **🎯 Overall Recommendation: {overall_action}**\n\n")
        
        # Salidas urgentes
        urgent_exits = action_summary.get('urgent_exits', [])
        if urgent_exits:
            f.write(f"### **🚨 URGENT EXITS REQUIRED**\n\n")
            for exit in urgent_exits:
                symbol = exit.get('symbol', exit) if isinstance(exit, dict) else exit
                reason = exit.get('reason', 'Review required') if isinstance(exit, dict) else 'Review required'
                pnl = exit.get('pnl', 0) if isinstance(exit, dict) else 0
                pnl_str = f" ({pnl:+.1f}%)" if pnl != 0 else ""
                f.write(f"- **{symbol}**{pnl_str} - {reason}\n")
            f.write("\n")
        
        # Oportunidades de rotación
        rotation_opportunities = action_summary.get('rotation_opportunities', [])
        if rotation_opportunities:
            f.write(f"### **🔄 ROTATION OPPORTUNITIES**\n\n")
            for opp in rotation_opportunities[:5]:
                symbol = opp.get('symbol', opp) if isinstance(opp, dict) else opp
                score = opp.get('score', 0) if isinstance(opp, dict) else 0
                improvement = opp.get('improvement', 0) if isinstance(opp, dict) else 0
                reason = opp.get('reason', 'High potential') if isinstance(opp, dict) else 'High potential'
                
                f.write(f"- **{symbol}** | Score: {score:.1f} (+{improvement:.1f} vs current) | {reason}\n")
            f.write("\n")
        
        # Alta convicción
        high_conviction = action_summary.get('high_conviction_adds', [])
        if high_conviction:
            f.write(f"### **🌟 HIGH CONVICTION OPPORTUNITIES**\n\n")
            for conv in high_conviction[:5]:
                symbol = conv.get('symbol', conv) if isinstance(conv, dict) else conv
                quality = conv.get('quality', 'EXCELLENT') if isinstance(conv, dict) else 'EXCELLENT'
                consistency = conv.get('consistency', 0) if isinstance(conv, dict) else 0
                reason = conv.get('reason', 'Strong signal') if isinstance(conv, dict) else 'Strong signal'
                
                f.write(f"- **{symbol}** | Quality: {quality} | {consistency} days consistent | {reason}\n")
            f.write("\n")
        
        # Mantener posiciones
        holds = action_summary.get('holds', [])
        if holds:
            f.write(f"### **✅ MAINTAIN POSITIONS ({len(holds)})**\n\n")
            for hold in holds[:5]:
                symbol = hold.get('symbol', hold) if isinstance(hold, dict) else hold
                pnl = hold.get('pnl', 0) if isinstance(hold, dict) else 0
                pnl_str = f" ({pnl:+.1f}%)" if pnl != 0 else ""
                reason = hold.get('reason', 'Position healthy') if isinstance(hold, dict) else 'Position healthy'
                
                f.write(f"- **{symbol}**{pnl_str} - {reason[:60]}{'...' if len(reason) > 60 else ''}\n")
            f.write("\n")
        
        # Criterios de rotación estrictos
        f.write(f"### **⚠️ Strict Rotation Criteria Applied**\n\n")
        strict_criteria = self.rotation_data.get('strict_criteria_applied', {})
        f.write(f"- **Minimum score difference:** +{strict_criteria.get('min_score_difference', 30)} points\n")
        f.write(f"- **Stop loss proximity:** {strict_criteria.get('stop_loss_proximity', 0.03)*100:.0f}% threshold\n")
        f.write(f"- **Momentum loss:** {strict_criteria.get('momentum_loss_days', 3)}+ days absence\n")
        f.write(f"- **Consistency requirement:** {strict_criteria.get('min_consistency_weeks', 2)}+ days minimum\n\n")
        
        f.write("---\n\n")
    
    def write_daily_market_context(self, f):
        """Escribe contexto de mercado diario"""
        f.write("## 📊 **DAILY MARKET CONTEXT**\n\n")
        
        if not self.screening_data:
            f.write("*No market data available*\n\n")
            return
        
        benchmark_context = self.screening_data.get('benchmark_context', {})
        
        f.write(f"### **📈 SPY Benchmark Performance**\n\n")
        f.write(f"- **SPY 20-day return:** {benchmark_context.get('spy_20d', 0):+.2f}%\n")
        f.write(f"- **SPY 60-day return:** {benchmark_context.get('spy_60d', 0):+.2f}%\n")
        f.write(f"- **SPY 90-day return:** {benchmark_context.get('spy_90d', 0):+.2f}%\n\n")
        
        # Análisis de outperformance
        detailed_results = self.screening_data.get('detailed_results', [])
        if detailed_results:
            outperformers_20d = len([r for r in detailed_results if r.get('outperformance_20d', 0) > 5])
            outperformers_60d = len([r for r in detailed_results if r.get('outperformance_60d', 0) > 0])
            
            f.write(f"### **🏆 Outperformance vs SPY**\n\n")
            f.write(f"- **20-day outperformers (+5%):** {outperformers_20d}/{len(detailed_results)} "
                   f"({outperformers_20d/len(detailed_results)*100:.1f}%)\n")
            f.write(f"- **60-day outperformers (positive):** {outperformers_60d}/{len(detailed_results)} "
                   f"({outperformers_60d/len(detailed_results)*100:.1f}%)\n\n")
        
        f.write("---\n\n")
    
    def write_optimization_metrics(self, f):
        """Escribe métricas de optimización del sistema"""
        f.write("## 🔧 **SYSTEM OPTIMIZATION METRICS**\n\n")
        
        if not self.screening_data:
            f.write("*No optimization data available*\n\n")
            return
        
        stats = self.screening_data.get('momentum_responsive_stats', {})
        
        f.write(f"### **📊 Daily Performance Metrics**\n\n")
        f.write(f"- **Average risk per position:** {stats.get('avg_risk', 0):.1f}%\n")
        f.write(f"- **Average risk/reward ratio:** {stats.get('avg_risk_reward', 0):.1f}x\n")
        f.write(f"- **Average upside potential:** {stats.get('avg_upside', 0):.1f}%\n")
        f.write(f"- **Average 20d momentum:** {stats.get('avg_momentum_20d', 0):+.1f}%\n\n")
        
        f.write(f"### **🌟 MA50 Bonus System Metrics**\n\n")
        ma50_count = stats.get('ma50_bonus_count', 0)
        total_results = len(self.screening_data.get('detailed_results', []))
        f.write(f"- **MA50 bonus applied:** {ma50_count}/{total_results} stocks "
               f"({ma50_count/max(total_results,1)*100:.1f}%)\n")
        f.write(f"- **Bonus value:** +22 points per application\n")
        f.write(f"- **System effectiveness:** {'🟢 High' if ma50_count/max(total_results,1) > 0.15 else '🟡 Moderate' if ma50_count/max(total_results,1) > 0.05 else '🔴 Low'}\n\n")
        
        f.write(f"### **📈 Quality Metrics**\n\n")
        f.write(f"- **High upside (>30%):** {stats.get('high_upside_count', 0)} stocks\n")
        f.write(f"- **Excellent R/R (>3.0x):** {stats.get('excellent_rr_count', 0)} stocks\n")
        f.write(f"- **Positive earnings:** {stats.get('positive_earnings_count', 0)} stocks\n")
        f.write(f"- **Weekly ATR availability:** {stats.get('avg_weekly_atr', 0):.2f} average\n\n")
        
        f.write("---\n\n")
    
    def write_daily_methodology(self, f):
        """Escribe metodología adaptada para ejecución diaria"""
        f.write("## 🎯 **DAILY METHODOLOGY FOR MONTHLY TRADING**\n\n")
        
        f.write(f"### **🔄 Execution Framework**\n\n")
        f.write(f"- **Frequency:** Daily execution (Mon-Fri post-market)\n")
        f.write(f"- **Philosophy:** Monthly trades with daily monitoring\n")
        f.write(f"- **Rotation approach:** Strict criteria to avoid overtrading\n")
        f.write(f"- **Risk management:** Ultra-conservative (≤10% per position)\n\n")
        
        f.write(f"### **🌟 MA50 Bonus System**\n\n")
        f.write(f"- **Detection:** Automated identification of MA50 rebounds\n")
        f.write(f"- **Scoring:** +22 base points + 20% multiplier\n")
        f.write(f"- **Stop loss priority:** MA50 level prioritized over other methods\n")
        f.write(f"- **Technical significance:** Bullish rebound signal\n\n")
        
        f.write(f"### **⚠️ Strict Rotation Criteria**\n\n")
        f.write(f"- **Score difference:** Minimum +30 points improvement required\n")
        f.write(f"- **Stop loss proximity:** Alert when within 3% of stop\n")
        f.write(f"- **Momentum loss:** 3+ consecutive days without appearance\n")
        f.write(f"- **Fundamental deterioration:** Automatic detection\n\n")
        
        f.write(f"### **📊 Daily Consistency Analysis**\n\n")
        f.write(f"- **Window:** Last 7 trading days\n")
        f.write(f"- **Consistent winners:** 5+ days appearance\n")
        f.write(f"- **Strong candidates:** 3-4 days appearance\n")
        f.write(f"- **Trend detection:** Momentum building/fading analysis\n\n")
        
        f.write(f"### **🎯 Success Metrics**\n\n")
        f.write(f"- **Target:** Outperform SPY over 3-6 month periods\n")
        f.write(f"- **Hold period:** ~1 month average per position\n")
        f.write(f"- **Drawdown:** <15% maximum (vs SPY ~25%)\n")
        f.write(f"- **Rotation frequency:** 2-4 per month (controlled)\n")
        f.write(f"- **MA50 bonus impact:** Enhanced technical signal quality\n\n")
    
    def create_daily_dashboard_data(self):
        """Crea datos JSON para el dashboard diario"""
        dashboard_data = {
            "timestamp": self.report_date.isoformat(),
            "market_date": self.report_date.strftime("%Y-%m-%d"),
            "analysis_type": "daily_trading_monthly_philosophy_ma50_bonus",
            "execution_frequency": "daily",
            "trading_philosophy": "monthly_trades_daily_monitoring",
            "ma50_bonus_system": {
                "active": True,
                "bonus_value": 22,
                "multiplier": 1.20
            },
            "summary": {
                "analysis_type": "Daily Trading with Monthly Philosophy + MA50 Bonus",
                "total_analyzed": 0,
                "consistent_winners": 0,
                "strong_candidates": 0,
                "ma50_bonus_applied": 0,
                "rotation_actions_required": 0,
                "message": "Daily analysis for monthly trading completed"
            },
            "top_picks": [],
            "consistency_analysis": {
                "window": "last_7_days",
                "consistent_winners": [],
                "strong_candidates": [],
                "emerging_opportunities": [],
                "consecutive_winners": []
            },
            "monthly_trading_recommendations": {},
            "ma50_bonus_highlights": [],
            "market_context": {},
            "optimization_metrics": {
                "ma50_bonus_system": True,
                "daily_execution": True,
                "strict_rotation_criteria": True,
                "monthly_trading_alignment": True
            }
        }
        
        # Datos de screening diario
        if self.screening_data:
            detailed_results = self.screening_data.get('detailed_results', [])
            dashboard_data["summary"]["total_analyzed"] = len(detailed_results)
            
            # MA50 bonus highlights
            ma50_stocks = []
            for stock in detailed_results[:15]:
                if stock.get('optimizations', {}).get('ma50_bonus_applied', False):
                    ma50_stocks.append({
                        "symbol": stock['symbol'],
                        "score": stock.get('score', 0),
                        "bonus_value": stock.get('optimizations', {}).get('ma50_bonus_value', 0),
                        "risk_pct": stock.get('risk_pct', 0),
                        "upside_pct": stock.get('upside_pct', 0)
                    })
            
            dashboard_data["ma50_bonus_highlights"] = ma50_stocks
            dashboard_data["summary"]["ma50_bonus_applied"] = len(ma50_stocks)
            
            # Top picks con enfoque mensual
            for stock in detailed_results[:10]:
                pick = {
                    "symbol": stock['symbol'],
                    "score": stock.get('score', 0),
                    "risk_pct": stock.get('risk_pct', 0),
                    "upside_pct": stock.get('upside_pct', 0),
                    "monthly_trading_suitable": stock.get('risk_pct', 0) <= 10.0,
                    "ma50_bonus": stock.get('optimizations', {}).get('ma50_bonus_applied', False),
                    "fundamental_quality": stock.get('fundamental_data', {}).get('quarterly_earnings_positive', False)
                }
                dashboard_data["top_picks"].append(pick)
        
        # Datos de consistencia diaria
        if self.consistency_data:
            consistency_analysis = self.consistency_data.get('consistency_analysis', {})
            
            dashboard_data["summary"]["consistent_winners"] = len(consistency_analysis.get('consistent_winners', []))
            dashboard_data["summary"]["strong_candidates"] = len(consistency_analysis.get('strong_candidates', []))
            
            # Actualizar analysis section
            dashboard_data["consistency_analysis"]["consistent_winners"] = [
                {"symbol": s['symbol'], "frequency": s['frequency'], "trend": s.get('trend', 'UNKNOWN')}
                for s in consistency_analysis.get('consistent_winners', [])[:10]
            ]
            
            dashboard_data["consistency_analysis"]["strong_candidates"] = [
                {"symbol": s['symbol'], "frequency": s['frequency'], "trend": s.get('trend', 'UNKNOWN')}
                for s in consistency_analysis.get('strong_candidates', [])[:10]
            ]
        
        # Datos de rotación mensual
        if self.rotation_data:
            action_summary = self.rotation_data.get('action_summary', {})
            
            rotation_count = (len(action_summary.get('urgent_exits', [])) + 
                            len(action_summary.get('rotation_opportunities', [])))
            dashboard_data["summary"]["rotation_actions_required"] = rotation_count
            
            dashboard_data["monthly_trading_recommendations"] = {
                "overall_action": action_summary.get('overall_action', 'MAINTAIN_MONTHLY_STRATEGY'),
                "urgent_exits": len(action_summary.get('urgent_exits', [])),
                "rotation_opportunities": len(action_summary.get('rotation_opportunities', [])),
                "high_conviction_adds": len(action_summary.get('high_conviction_adds', [])),
                "philosophy_alignment": "aligned" if rotation_count <= 3 else "review_required"
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
    
    def generate_complete_daily_report(self):
        """Genera reporte completo diario para trading mensual"""
        print("📋 Generando reporte DIARIO para trading mensual con MA50 bonus...")
        
        # Cargar todos los datos
        if not self.load_all_data():
            print("❌ No se pudieron cargar suficientes datos")
            return False
        
        # Crear reporte Markdown diario
        markdown_file = self.create_daily_markdown_report()
        
        # Crear datos para dashboard diario
        dashboard_data = self.create_daily_dashboard_data()
        
        print(f"✅ Reporte diario para trading mensual completado:")
        print(f"   - Markdown: {markdown_file}")
        print(f"   - Dashboard: docs/data.json")
        print(f"   - Incluye: MA50 bonus system, Daily consistency, Monthly rotation criteria")
        
        return True

def main():
    """Función principal para reporte diario de trading mensual"""
    generator = DailyTradingReportGenerator()
    
    success = generator.generate_complete_daily_report()
    
    if success:
        print("\n✅ Reporte DIARIO para trading mensual generado exitosamente")
        print("\n🎯 CARACTERÍSTICAS IMPLEMENTADAS:")
        print("   - 📅 Análisis diario con filosofía de trading mensual")
        print("   - 🌟 Sistema MA50 bonus (+22pts) completamente integrado")
        print("   - ⚠️ Criterios estrictos de rotación (evita overtrading)")
        print("   - 📊 Consistencia analizada en ventana de 7 días")
        print("   - 🔄 Recomendaciones alineadas con holds de ~1 mes")
        print("   - 📈 Dashboard optimizado para monitorización diaria")
        print("   - 🛡️ Gestión de riesgo ultra-conservadora (≤10%)")
    else:
        print("\n❌ Error generando reporte diario para trading mensual")

if __name__ == "__main__":
    main()
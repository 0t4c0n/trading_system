#!/usr/bin/env python3
"""
Conservative Stock Screener - Análisis semanal para inversiones a largo plazo
Orientado a holds de 1-3 meses con filtros técnicos y fundamentales estrictos
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Any

class ConservativeStockScreener:
    def __init__(self):
        self.stock_symbols = []
        self.spy_benchmark = None
        
    def get_nyse_nasdaq_symbols(self):
        """Obtiene símbolos de NYSE y NASDAQ combinados"""
        all_symbols = []
        
        try:
            nyse_symbols = self.get_exchange_symbols('NYSE')
            nasdaq_symbols = self.get_exchange_symbols('NASDAQ')
            
            all_symbols = list(set(nyse_symbols + nasdaq_symbols))
            print(f"✓ NYSE: {len(nyse_symbols)} | NASDAQ: {len(nasdaq_symbols)} | Total: {len(all_symbols)} símbolos")
            
            return all_symbols
            
        except Exception as e:
            print(f"Error obteniendo símbolos: {e}")
            backup_symbols = self.get_backup_symbols()
            print(f"Usando lista de respaldo: {len(backup_symbols)} símbolos")
            return backup_symbols
    
    def get_exchange_symbols(self, exchange):
        """Obtiene símbolos de un exchange específico"""
        try:
            url = "https://api.nasdaq.com/api/screener/stocks"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'tableonly': 'true',
                'limit': '25000',
                'exchange': exchange
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'table' in data['data']:
                    symbols = [row['symbol'] for row in data['data']['table']['rows']]
                    return symbols
            
            return []
            
        except Exception as e:
            print(f"Error obteniendo símbolos de {exchange}: {e}")
            return []
    
    def get_backup_symbols(self):
        """Lista de respaldo con principales acciones"""
        return [
            # Tech giants
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA',
            # Other major tech
            'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'V', 'MA', 'PYPL',
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'LLY',
            # Consumer
            'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'UPS', 'HON', 'LMT', 'RTX',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC'
        ]
    
    def calculate_spy_benchmark(self):
        """Calcula rendimientos de SPY para benchmarking"""
        print("📊 Descargando benchmark SPY...")
        
        try:
            spy_ticker = yf.Ticker("SPY")
            spy_data = spy_ticker.history(period="1y")
            
            if spy_data.empty or len(spy_data) < 200:
                print("⚠️ SPY: Datos insuficientes")
                return None
            
            # Calcular rendimientos a múltiples plazos
            current_price = spy_data['Close'].iloc[-1]
            price_20d = spy_data['Close'].iloc[-21] if len(spy_data) >= 21 else spy_data['Close'].iloc[0]
            price_60d = spy_data['Close'].iloc[-61] if len(spy_data) >= 61 else spy_data['Close'].iloc[0]
            price_90d = spy_data['Close'].iloc[-91] if len(spy_data) >= 91 else spy_data['Close'].iloc[0]
            
            benchmark = {
                'return_20d': ((current_price / price_20d) - 1) * 100,
                'return_60d': ((current_price / price_60d) - 1) * 100,
                'return_90d': ((current_price / price_90d) - 1) * 100,
                'data': spy_data
            }
            
            print(f"✅ SPY - 20d: {benchmark['return_20d']:+.2f}%, 60d: {benchmark['return_60d']:+.2f}%, 90d: {benchmark['return_90d']:+.2f}%")
            return benchmark
            
        except Exception as e:
            print(f"❌ Error calculando SPY benchmark: {e}")
            return None
    
    def calculate_atr(self, df, period=20):
        """Calcula Average True Range"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr.iloc[-1] if not atr.empty else 0
    
    def calculate_relative_performance(self, stock_data, spy_data, days):
        """Calcula performance relativa vs SPY"""
        try:
            if len(stock_data) < days or len(spy_data) < days:
                return 0
            
            stock_current = stock_data['Close'].iloc[-1]
            stock_past = stock_data['Close'].iloc[-days]
            stock_return = ((stock_current / stock_past) - 1) * 100
            
            spy_current = spy_data['Close'].iloc[-1]
            spy_past = spy_data['Close'].iloc[-days]
            spy_return = ((spy_current / spy_past) - 1) * 100
            
            return stock_return - spy_return
            
        except Exception:
            return 0
    
    def get_fundamental_data(self, ticker_info):
        """Extrae datos fundamentales clave"""
        fundamental_data = {
            'quarterly_earnings_positive': None,
            'quarterly_earnings_growth': None,
            'revenue_growth': None,
            'roe': None,
            'fundamental_score': 0
        }
        
        try:
            # Beneficios último trimestre
            quarterly_growth = ticker_info.get('quarterlyEarningsGrowthYOY')
            if quarterly_growth is not None:
                fundamental_data['quarterly_earnings_positive'] = quarterly_growth > 0
                fundamental_data['quarterly_earnings_growth'] = quarterly_growth
                
                # Scoring beneficios
                if quarterly_growth > 0.30:  # >30%
                    fundamental_data['fundamental_score'] += 40
                elif quarterly_growth > 0.15:  # >15%
                    fundamental_data['fundamental_score'] += 25
                elif quarterly_growth > 0:
                    fundamental_data['fundamental_score'] += 10
            else:
                # Fallback con trailing EPS
                trailing_eps = ticker_info.get('trailingEps')
                if trailing_eps is not None and trailing_eps > 0:
                    fundamental_data['quarterly_earnings_positive'] = True
                    fundamental_data['fundamental_score'] += 15
            
            # Crecimiento de ingresos
            revenue_growth = ticker_info.get('revenueGrowth')
            if revenue_growth is not None:
                fundamental_data['revenue_growth'] = revenue_growth
                if revenue_growth > 0.10:  # >10%
                    fundamental_data['fundamental_score'] += 20
                elif revenue_growth > 0.05:  # >5%
                    fundamental_data['fundamental_score'] += 10
            
            # ROE
            roe = ticker_info.get('returnOnEquity')
            if roe is not None:
                fundamental_data['roe'] = roe
                if roe > 0.20:  # >20%
                    fundamental_data['fundamental_score'] += 25
                elif roe > 0.15:  # >15%
                    fundamental_data['fundamental_score'] += 15
                elif roe > 0.10:  # >10%
                    fundamental_data['fundamental_score'] += 10
                    
        except Exception as e:
            print(f"⚠️ Error fundamentales: {e}")
        
        return fundamental_data
    
    def evaluate_stock_conservative(self, symbol):
        """Evaluación conservadora para largo plazo"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Datos históricos - 1 año para análisis robusto
            hist = ticker.history(period="1y")
            if len(hist) < 200:
                return None  # ❌ Early exit - datos insuficientes
            
            current_price = hist['Close'].iloc[-1]
            
            # FILTROS TÉCNICOS BÁSICOS
            ma21 = hist['Close'].rolling(21).mean().iloc[-1]
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            ma200 = hist['Close'].rolling(200).mean().iloc[-1]
            
            # Tendencia sólida a largo plazo (MUY ESTRICTO)
            if not (ma21 > ma50 > ma200 and current_price > ma21):
                return None  # ❌ Early exit - tendencia incorrecta
            
            # Volumen mínimo para liquidez
            volume_avg_30d = hist['Volume'].tail(30).mean()
            if volume_avg_30d < 1_000_000:
                return None  # ❌ Early exit - volumen insuficiente
            
            # BENCHMARKING vs SPY (MÚLTIPLES PLAZOS)
            if self.spy_benchmark is None:
                return None  # Sin benchmark no podemos evaluar
            
            spy_data = self.spy_benchmark['data']
            
            outperformance_20d = self.calculate_relative_performance(hist, spy_data, 20)
            outperformance_60d = self.calculate_relative_performance(hist, spy_data, 60)
            outperformance_90d = self.calculate_relative_performance(hist, spy_data, 90)
            
            # FILTRO CRÍTICO: Debe superar SPY en TODOS los plazos
            if not (outperformance_20d > 2 and outperformance_60d > 5 and outperformance_90d > 8):
                return None  # ❌ Early exit - no supera consistentemente al mercado
            
            # STOP-LOSS CONSERVADOR (más generoso para largo plazo)
            atr_30d = self.calculate_atr(hist, 30)
            ma50_stop = ma50 if (current_price - ma50) / current_price < 0.12 else None  # 12%
            
            valid_stops = [
                ma21,
                ma50_stop,
                current_price - (atr_30d * 2.0)  # ATR más generoso
            ]
            valid_stops = [s for s in valid_stops if s is not None]
            
            stop_base = min(valid_stops) if valid_stops else ma21
            stop_final = stop_base * 0.98  # 2% margen
            
            risk_pct = ((current_price - stop_final) / current_price) * 100
            if risk_pct > 15:  # 15% máximo riesgo
                return None  # ❌ Early exit - riesgo excesivo
            
            # FUNDAMENTALES
            try:
                ticker_info = ticker.info
                fundamental_data = self.get_fundamental_data(ticker_info)
                
                # FILTRO FUNDAMENTAL OBLIGATORIO: Beneficios positivos
                if fundamental_data['quarterly_earnings_positive'] is False:
                    return None  # ❌ Early exit - beneficios negativos
                    
            except Exception:
                # Si no hay datos fundamentales, penalizar pero no eliminar
                fundamental_data = {'fundamental_score': 0}
            
            # CÁLCULO DE VOLUMEN SURGE
            volume_recent_5d = hist['Volume'].tail(5).mean()
            volume_surge = ((volume_recent_5d / volume_avg_30d) - 1) * 100
            
            # SCORE FINAL CONSERVADOR
            technical_score = (
                outperformance_60d * 1.5 +     # Mayor peso a performance 3M
                outperformance_20d * 1.0 +
                (15 - risk_pct) * 2 +          # Menor riesgo = mucho mejor
                volume_surge * 0.3 +           # Interés del mercado
                fundamental_data.get('fundamental_score', 0) * 0.5
            )
            
            # Información de empresa
            company_info = {
                'name': ticker_info.get('longName', 'N/A') if 'ticker_info' in locals() else 'N/A',
                'sector': ticker_info.get('sector', 'N/A') if 'ticker_info' in locals() else 'N/A',
                'market_cap': ticker_info.get('marketCap', 'N/A') if 'ticker_info' in locals() else 'N/A'
            }
            
            return {
                'symbol': symbol,
                'score': technical_score,
                'current_price': round(current_price, 2),
                'stop_loss': round(stop_final, 2),
                'risk_pct': round(risk_pct, 2),
                'outperformance_20d': round(outperformance_20d, 2),
                'outperformance_60d': round(outperformance_60d, 2),
                'outperformance_90d': round(outperformance_90d, 2),
                'volume_surge': round(volume_surge, 1),
                'fundamental_score': fundamental_data.get('fundamental_score', 0),
                'quarterly_earnings_growth': fundamental_data.get('quarterly_earnings_growth'),
                'revenue_growth': fundamental_data.get('revenue_growth'),
                'company_info': company_info,
                'ma_levels': {
                    'ma_21': round(ma21, 2),
                    'ma_50': round(ma50, 2),
                    'ma_200': round(ma200, 2)
                },
                'target_hold': '2-3 meses',
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error procesando {symbol}: {e}")
            return None
    
    def screen_all_stocks(self):
        """Screening completo con optimización para GitHub Actions"""
        print("=== CONSERVATIVE SCREENING - LARGO PLAZO ===")
        
        # Calcular benchmark SPY
        self.spy_benchmark = self.calculate_spy_benchmark()
        if self.spy_benchmark is None:
            print("❌ No se pudo calcular benchmark SPY")
            return []
        
        # Obtener todos los símbolos
        all_symbols = self.get_nyse_nasdaq_symbols()
        if not all_symbols:
            print("❌ No se pudieron obtener símbolos")
            return []
        
        # Procesamiento en lotes para optimizar tiempo
        batch_size = 50
        total_batches = (len(all_symbols) + batch_size - 1) // batch_size
        
        all_results = []
        failed_count = 0
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(all_symbols))
            batch_symbols = all_symbols[start_idx:end_idx]
            
            print(f"\n=== LOTE {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx}) ===")
            
            for i, symbol in enumerate(batch_symbols):
                try:
                    result = self.evaluate_stock_conservative(symbol)
                    
                    if result:
                        all_results.append(result)
                        print(f"✅ {symbol} - Score: {result['score']:.1f} - Risk: {result['risk_pct']:.1f}% - {i+1}/{len(batch_symbols)}")
                    else:
                        print(f"❌ {symbol} - Filtrado - {i+1}/{len(batch_symbols)}")
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ {symbol} - Error: {e}")
                
                # Rate limiting
                time.sleep(0.2)
            
            # Pausa entre lotes
            if batch_num < total_batches - 1:
                print("⏸️ Pausa entre lotes...")
                time.sleep(5)
        
        # Ordenar por score y tomar mejores
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n=== RESUMEN FINAL ===")
        print(f"Procesadas: {len(all_symbols)} | Pasaron filtros: {len(all_results)} | Errores: {failed_count}")
        print(f"Tasa de éxito: {len(all_results)/len(all_symbols)*100:.1f}%")
        
        return all_results

def main():
    """Función principal para GitHub Actions"""
    screener = ConservativeStockScreener()
    
    # Ejecutar screening
    results = screener.screen_all_stocks()
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Archivo completo con todos los resultados
    full_results_file = f"screening_results_full_{timestamp}.json"
    with open(full_results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_screened': len(screener.get_nyse_nasdaq_symbols()) if screener.get_nyse_nasdaq_symbols() else 0,
            'total_passed': len(results),
            'spy_benchmark': screener.spy_benchmark,
            'results': results
        }, f, indent=2, default=str)
    
    # Top 15 para análisis de consistencia
    top_15 = results[:15]
    top_15_file = "weekly_screening_results.json"
    with open(top_15_file, 'w') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'top_symbols': [r['symbol'] for r in top_15],
            'detailed_results': top_15,
            'benchmark_context': {
                'spy_20d': screener.spy_benchmark['return_20d'] if screener.spy_benchmark else 0,
                'spy_60d': screener.spy_benchmark['return_60d'] if screener.spy_benchmark else 0,
                'spy_90d': screener.spy_benchmark['return_90d'] if screener.spy_benchmark else 0
            }
        }, f, indent=2, default=str)
    
    print(f"✅ Archivos guardados:")
    print(f"   - {full_results_file} (resultados completos)")
    print(f"   - {top_15_file} (top 15 para análisis)")
    
    if len(top_15) > 0:
        print(f"\n🏆 TOP 5 ESTA SEMANA:")
        for i, stock in enumerate(top_15[:5]):
            print(f"   {i+1}. {stock['symbol']} - Score: {stock['score']:.1f} - ${stock['current_price']} - Risk: {stock['risk_pct']:.1f}%")
    else:
        print("\n⚠️ No se encontraron acciones que pasen todos los filtros esta semana")

if __name__ == "__main__":
    main()

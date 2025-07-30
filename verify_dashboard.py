#!/usr/bin/env python3
"""
Script para verificar que el dashboard data.json se generó correctamente
"""
import json
import sys

def verify_dashboard():
    try:
        with open("docs/data.json", "r") as f:
            data = json.load(f)
        
        analysis_type = data.get("analysis_type", "standard")
        top_picks = len(data.get("top_picks", []))
        
        print(f"Tipo de análisis: {analysis_type}")
        print(f"Top picks generados: {top_picks}")

        # Verificar características avanzadas
        features = []
        if "trading_metrics" in data:
            metrics = data["trading_metrics"]
            print(f"Avg R/R: {metrics.get('avg_risk_reward', 0):.1f}:1")
            print(f"Oportunidades alta calidad: {metrics.get('high_quality_count', 0)}")
            features.append("Trading Metrics")

        if any("take_profit" in str(pick) for pick in data.get("top_picks", [])):
            features.append("Stop/Target Dinámicos")

        if any("technical_score" in str(pick) for pick in data.get("top_picks", [])):
            features.append("Scoring Avanzado")

        if features:
            print(f"Características detectadas: {' | '.join(features)}")
            
        return True
        
    except Exception as e:
        print(f"ERROR verificando dashboard: {e}")
        return False

if __name__ == "__main__":
    success = verify_dashboard()
    sys.exit(0 if success else 1)
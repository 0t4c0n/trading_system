#!/usr/bin/env python3
"""
Script para verificar que el análisis de consistencia se completó correctamente
"""
import json
import sys

def verify_consistency():
    try:
        with open("consistency_analysis.json", "r") as f:
            data = json.load(f)
            
        stats = data.get("summary_stats", {})
        sources = data.get("data_sources", {})
        
        print(f"Consistent Winners: {stats.get('consistent_winners_count', 0)}")
        print(f"Strong Candidates: {stats.get('strong_candidates_count', 0)}")
        print(f"Emerging Opportunities: {stats.get('emerging_count', 0)}")
        print(f"Total símbolos únicos analizados: {stats.get('total_unique_symbols', 0)}")
        print(f"Semanas analizadas: {data.get('weeks_analyzed', 0)}")

        # Mostrar fuentes de datos
        hist_files = sources.get("historical_files", [])
        valid_files = [f for f in hist_files if "N/A" not in f]
        print(f"Archivos históricos válidos: {len(valid_files)}")
        
        return True
        
    except Exception as e:
        print(f"ERROR verificando análisis de consistencia: {e}")
        return False

if __name__ == "__main__":
    success = verify_consistency()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Script para verificar que las recomendaciones de rotación se generaron correctamente
"""
import json
import sys

def verify_rotation():
    try:
        with open("rotation_recommendations.json", "r") as f:
            data = json.load(f)
            
        action = data.get("action_summary", {}).get("overall_action", "NO_ACTION")
        strong_buys = len(data.get("action_summary", {}).get("strong_buys", []))
        exits = len(data.get("action_summary", {}).get("consider_exits", [])) + len(data.get("action_summary", {}).get("urgent_exits", []))
        holds = len(data.get("action_summary", {}).get("holds", []))
        
        print(f"Acción general: {action}")
        print(f"Compras fuertes recomendadas: {strong_buys}")
        print(f"Salidas a considerar: {exits}")
        print(f"Mantener posiciones: {holds}")

        # Verificar si es análisis avanzado
        analysis_type = data.get("analysis_type", "standard")
        if "advanced" in analysis_type or "multifactor" in analysis_type:
            print("SUCCESS: ANÁLISIS MULTIFACTORIAL AVANZADO CON HISTORIAL DETECTADO")
        else:
            print("Análisis estándar completado")
            
        return True
        
    except Exception as e:
        print(f"ERROR verificando recomendaciones de rotación: {e}")
        return False

if __name__ == "__main__":
    success = verify_rotation()
    sys.exit(0 if success else 1)
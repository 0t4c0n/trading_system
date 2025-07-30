#!/usr/bin/env python3
"""
Script para verificar que todos los archivos necesarios se generaron correctamente
"""
import os
import json
import sys

def verify_generated_files():
    """Verifica archivos generados y calidad con historial"""
    print("=== VERIFICACIÓN FINAL DE ARCHIVOS Y GESTIÓN DE HISTORIAL ===")
    
    # Archivos principales a verificar
    required_files = [
        "weekly_screening_results.json",
        "consistency_analysis.json", 
        "rotation_recommendations.json",
        "docs/data.json"
    ]
    
    all_files_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            try:
                size = os.path.getsize(file)
                print(f"✅ {file}: {size} bytes")
                
                # Verificar que es JSON válido
                with open(file, 'r') as f:
                    json.load(f)
                    
            except Exception as e:
                print(f"❌ {file}: Error leyendo archivo - {e}")
                all_files_ok = False
        else:
            print(f"❌ {file}: FALTA")
            all_files_ok = False
    
    # Verificar reportes opcionales
    print("\n=== VERIFICACIÓN DE REPORTES OPCIONALES ===")
    
    enhanced_reports = [f for f in os.listdir('.') if f.startswith('ENHANCED_WEEKLY_REPORT_') and f.endswith('.md')]
    regular_reports = [f for f in os.listdir('.') if f.startswith('WEEKLY_REPORT_') and f.endswith('.md')]
    
    if enhanced_reports:
        print(f"📈 Reportes mejorados: {', '.join(enhanced_reports)}")
    elif regular_reports:
        print(f"📊 Reportes regulares: {', '.join(regular_reports)}")
    else:
        print("ℹ️  Sin reportes Markdown (puede ser normal)")
    
    # Verificar calidad de datos
    print("\n=== VERIFICACIÓN DE CALIDAD DE DATOS ===")
    
    try:
        with open("weekly_screening_results.json", 'r') as f:
            screening = json.load(f)
        
        results_count = len(screening.get('detailed_results', []))
        analysis_type = screening.get('analysis_type', 'standard')
        
        print(f"Resultados filtrados: {results_count}")
        print(f"Tipo de análisis: {analysis_type}")
        
        if results_count == 0:
            print("⚠️  WARNING: Sin resultados en screening")
        elif results_count < 5:
            print("⚠️  WARNING: Pocos resultados en screening")
        else:
            print("✅ Screening con datos suficientes")
            
    except Exception as e:
        print(f"❌ Error verificando calidad: {e}")
        all_files_ok = False
    
    # Verificar historial
    print("\n=== VERIFICACIÓN DE GESTIÓN DE HISTORIAL ===")
    
    history_dir = "historical_data"
    if os.path.exists(history_dir):
        hist_files = os.listdir(history_dir)
        print(f"📚 Archivos en historial: {len(hist_files)}")
        if len(hist_files) > 0:
            recent_files = sorted(hist_files)[-3:]  # Últimos 3
            print(f"Archivos recientes: {', '.join(recent_files)}")
    else:
        print("ℹ️  Directorio de historial no existe (primera ejecución)")
    
    return all_files_ok

if __name__ == "__main__":
    success = verify_generated_files()
    print(f"\n=== RESULTADO FINAL: {'✅ SUCCESS' if success else '❌ FAILURE'} ===")
    sys.exit(0 if success else 1)
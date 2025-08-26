#!/usr/bin/env python3
"""🚀 Script Principal de Validación
Script principal para ejecutar todas las validaciones y pruebas
del sistema de trading avanzado.

Desarrollado por: Experto en Trading & Programación
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_validator import SystemValidator

def run_system_validation() -> Dict[str, Any]:
    """🔧 Ejecuta validación del sistema"""
    print("🔧 Ejecutando validación del sistema...")
    validator = SystemValidator()
    return validator.run_comprehensive_validation()

def run_unit_tests() -> bool:
    """🧪 Ejecuta pruebas unitarias"""
    print("\n🧪 Ejecutando pruebas unitarias...")
    
    try:
        # Importar y ejecutar las pruebas
        from tests.test_enhanced_system import run_all_tests
        result = run_all_tests()
        
        # Determinar si las pruebas pasaron
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        return success_rate >= 75  # 75% de éxito mínimo
        
    except ImportError as e:
        print(f"❌ Error importando pruebas: {e}")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return False

def run_integration_tests() -> bool:
    """🔗 Ejecuta pruebas de integración básicas"""
    print("\n🔗 Ejecutando pruebas de integración...")
    
    try:
        # Test 1: Importar todos los módulos principales
        print("  📦 Probando importaciones...")
        from advanced_indicators import AdvancedIndicators
        from trading_engine.enhanced_strategies import ProfessionalRSIStrategy
        from trading_engine.signal_filters import AdvancedSignalFilter
        from backtesting.enhanced_backtester import EnhancedBacktester
        from sentiment_analyzer import SentimentAnalyzer
        print("    ✅ Importaciones exitosas")
        
        # Test 2: Crear instancias básicas
        print("  🏗️  Probando instanciación...")
        indicators = AdvancedIndicators()
        strategy = ProfessionalRSIStrategy()
        signal_filter = AdvancedSignalFilter()
        backtester = EnhancedBacktester()
        sentiment = SentimentAnalyzer()
        print("    ✅ Instanciación exitosa")
        
        # Test 3: Crear datos de prueba y ejecutar análisis básico
        print("  📊 Probando análisis básico...")
        import pandas as pd
        import numpy as np
        
        # Crear datos de muestra
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')
        np.random.seed(42)
        prices = np.random.normal(50000, 1000, 50)
        
        test_data = pd.DataFrame({
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 50)
        }, index=dates)
        
        # Probar algunos indicadores
        bb_result = indicators.bollinger_bands(test_data)
        vwap_result = indicators.vwap(test_data)
        atr_result = indicators.average_true_range(test_data)
        
        if not all([bb_result, vwap_result, atr_result]):
            print("    ❌ Error en cálculo de indicadores")
            return False
        
        print("    ✅ Análisis básico exitoso")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error en pruebas de integración: {e}")
        return False

def run_performance_benchmark() -> Dict[str, float]:
    """⚡ Ejecuta benchmark de rendimiento"""
    print("\n⚡ Ejecutando benchmark de rendimiento...")
    
    import time
    import pandas as pd
    import numpy as np
    
    results = {}
    
    try:
        from advanced_indicators import AdvancedIndicators
        indicators = AdvancedIndicators()
        
        # Crear dataset de prueba
        print("  📊 Creando dataset de prueba...")
        dates = pd.date_range(start='2024-01-01', periods=1000, freq='1h')
        np.random.seed(42)
        prices = np.random.normal(50000, 1000, 1000)
        
        test_data = pd.DataFrame({
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 1000).astype('float64')
        }, index=dates)
        
        # Benchmark indicadores individuales
        indicators_to_test = [
            ('Bollinger Bands', lambda: indicators.bollinger_bands(test_data)),
            ('VWAP', lambda: indicators.vwap(test_data)),
            ('OBV', lambda: indicators.on_balance_volume(test_data)),
            ('MFI', lambda: indicators.money_flow_index(test_data)),
            ('ATR', lambda: indicators.average_true_range(test_data)),
            ('Volume Profile', lambda: indicators.volume_profile(test_data)),
            ('Support/Resistance', lambda: indicators.support_resistance_levels(test_data))
        ]
        
        for name, func in indicators_to_test:
            start_time = time.time()
            try:
                func()
                execution_time = time.time() - start_time
                results[name] = execution_time
                print(f"    ✅ {name}: {execution_time:.3f}s")
            except Exception as e:
                print(f"    ❌ {name}: ERROR - {e}")
                results[name] = float('inf')
        
        # Calcular tiempo total
        total_time = sum(t for t in results.values() if t != float('inf'))
        results['Total'] = total_time
        
        print(f"  📊 Tiempo total: {total_time:.3f}s")
        
        # Evaluar rendimiento
        if total_time < 2.0:
            print(f"  🎉 Rendimiento: EXCELENTE")
        elif total_time < 5.0:
            print(f"  ✅ Rendimiento: BUENO")
        elif total_time < 10.0:
            print(f"  ⚠️  Rendimiento: ACEPTABLE")
        else:
            print(f"  ❌ Rendimiento: LENTO")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Error en benchmark: {e}")
        return {'error': str(e)}

def generate_comprehensive_report(validation_results: Dict, tests_passed: bool, 
                                integration_passed: bool, performance_results: Dict):
    """📄 Genera reporte comprehensivo"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comprehensive_validation_report_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 📊 Reporte Comprehensivo de Validación\n\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Resumen ejecutivo
        f.write(f"## 🎯 Resumen Ejecutivo\n\n")
        
        overall_status = validation_results.get('overall_status', 'UNKNOWN')
        f.write(f"**Estado General:** {overall_status}\n\n")
        
        status_summary = []
        if validation_results.get('overall_status') in ['EXCELLENT', 'GOOD']:
            status_summary.append("✅ Sistema validado")
        else:
            status_summary.append("⚠️ Sistema requiere atención")
            
        if tests_passed:
            status_summary.append("✅ Pruebas unitarias pasadas")
        else:
            status_summary.append("❌ Pruebas unitarias fallidas")
            
        if integration_passed:
            status_summary.append("✅ Integración funcional")
        else:
            status_summary.append("❌ Problemas de integración")
        
        f.write(f"**Resumen:** {' | '.join(status_summary)}\n\n")
        
        # Detalles de validación del sistema
        f.write(f"## 🔧 Validación del Sistema\n\n")
        
        f.write(f"### 📦 Dependencias\n\n")
        for pkg, status in validation_results.get('dependencies', {}).items():
            icon = "✅" if status else "❌"
            f.write(f"- {icon} {pkg}\n")
        
        f.write(f"\n### 🧩 Módulos\n\n")
        for mod, status in validation_results.get('modules', {}).items():
            icon = "✅" if status else "❌"
            f.write(f"- {icon} {mod}\n")
        
        f.write(f"\n### 📊 Fuentes de Datos\n\n")
        for src, status in validation_results.get('data_sources', {}).items():
            icon = "✅" if status else "❌"
            f.write(f"- {icon} {src}\n")
        
        # Resultados de pruebas
        f.write(f"\n## 🧪 Resultados de Pruebas\n\n")
        f.write(f"- **Pruebas Unitarias:** {'✅ PASADAS' if tests_passed else '❌ FALLIDAS'}\n")
        f.write(f"- **Pruebas de Integración:** {'✅ PASADAS' if integration_passed else '❌ FALLIDAS'}\n")
        
        # Benchmark de rendimiento
        f.write(f"\n## ⚡ Benchmark de Rendimiento\n\n")
        if 'error' not in performance_results:
            f.write(f"| Indicador | Tiempo (s) |\n")
            f.write(f"|-----------|------------|\n")
            for name, time_val in performance_results.items():
                if time_val != float('inf'):
                    f.write(f"| {name} | {time_val:.3f} |\n")
        else:
            f.write(f"❌ Error en benchmark: {performance_results['error']}\n")
        
        # Recomendaciones
        f.write(f"\n## 💡 Recomendaciones\n\n")
        
        recommendations = []
        
        # Basado en validación del sistema
        if validation_results.get('overall_status') not in ['EXCELLENT', 'GOOD']:
            recommendations.append("🔧 Revisar y corregir problemas de configuración del sistema")
        
        # Basado en pruebas
        if not tests_passed:
            recommendations.append("🧪 Investigar y corregir fallos en pruebas unitarias")
        
        if not integration_passed:
            recommendations.append("🔗 Resolver problemas de integración entre módulos")
        
        # Basado en rendimiento
        total_time = performance_results.get('Total', 0)
        if total_time > 10.0:
            recommendations.append("⚡ Optimizar rendimiento de indicadores")
        
        if not recommendations:
            f.write(f"🎉 ¡No se requieren acciones adicionales! El sistema está funcionando óptimamente.\n")
        else:
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
        
        # Próximos pasos
        f.write(f"\n## 🚀 Próximos Pasos\n\n")
        f.write(f"1. 📈 Ejecutar backtesting con datos reales\n")
        f.write(f"2. 🔄 Configurar monitoreo continuo\n")
        f.write(f"3. 📊 Implementar dashboard de métricas\n")
        f.write(f"4. 🛡️ Configurar alertas de sistema\n")
        f.write(f"5. 📝 Documentar procedimientos operativos\n")
    
    print(f"\n📄 Reporte comprehensivo guardado en: {filename}")
    return filename

def main():
    """🚀 Función principal"""
    parser = argparse.ArgumentParser(description='🔧 Validador Comprehensivo del Sistema de Trading')
    parser.add_argument('--skip-tests', action='store_true', help='Omitir pruebas unitarias')
    parser.add_argument('--skip-integration', action='store_true', help='Omitir pruebas de integración')
    parser.add_argument('--skip-performance', action='store_true', help='Omitir benchmark de rendimiento')
    parser.add_argument('--report-only', action='store_true', help='Solo generar reporte')
    
    args = parser.parse_args()
    
    print(f"{'='*80}")
    print(f"🚀 VALIDADOR COMPREHENSIVO DEL SISTEMA DE TRADING")
    print(f"{'='*80}")
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Validación del sistema
    validation_results = run_system_validation()
    
    # 2. Pruebas unitarias
    tests_passed = True
    if not args.skip_tests and not args.report_only:
        tests_passed = run_unit_tests()
    elif args.skip_tests:
        print("\n🧪 Pruebas unitarias omitidas")
    
    # 3. Pruebas de integración
    integration_passed = True
    if not args.skip_integration and not args.report_only:
        integration_passed = run_integration_tests()
    elif args.skip_integration:
        print("\n🔗 Pruebas de integración omitidas")
    
    # 4. Benchmark de rendimiento
    performance_results = {}
    if not args.skip_performance and not args.report_only:
        performance_results = run_performance_benchmark()
    elif args.skip_performance:
        print("\n⚡ Benchmark de rendimiento omitido")
    
    # 5. Generar reporte comprehensivo
    report_file = generate_comprehensive_report(
        validation_results, tests_passed, integration_passed, performance_results
    )
    
    # Resumen final
    print(f"\n{'='*80}")
    print(f"📊 RESUMEN FINAL")
    print(f"{'='*80}")
    
    overall_success = (
        validation_results.get('overall_status') in ['EXCELLENT', 'GOOD'] and
        tests_passed and
        integration_passed
    )
    
    if overall_success:
        print(f"🎉 ¡VALIDACIÓN EXITOSA! El sistema está listo para producción.")
        exit_code = 0
    else:
        print(f"⚠️  VALIDACIÓN PARCIAL. Revisar reporte para detalles.")
        exit_code = 1
    
    print(f"📄 Reporte detallado: {report_file}")
    print(f"⏰ Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
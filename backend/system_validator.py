"""🔧 System Validator
Validador del sistema para verificar que todas las dependencias
y componentes estén correctamente configurados.

Desarrollado por: Experto en Trading & Programación
"""

import sys
import os
import importlib
import subprocess
from typing import Dict, List, Tuple
from datetime import datetime

class SystemValidator:
    """🔍 Validador comprehensivo del sistema"""
    
    def __init__(self):
        self.results = {
            'dependencies': {},
            'modules': {},
            'data_sources': {},
            'performance': {},
            'overall_status': 'UNKNOWN'
        }
        
        self.required_packages = [
            'pandas', 'numpy', 'requests', 'ta', 'scipy',
            'matplotlib', 'seaborn', 'yfinance', 'ccxt'
        ]
        
        self.required_modules = [
            'advanced_indicators',
            'trading_engine.enhanced_strategies',
            'trading_engine.signal_filters',
            'backtesting.enhanced_backtester',
            'sentiment_analyzer'
        ]
    
    def validate_dependencies(self) -> Dict[str, bool]:
        """✅ Valida dependencias de Python"""
        print("🔍 Validando dependencias de Python...")
        
        for package in self.required_packages:
            try:
                importlib.import_module(package)
                self.results['dependencies'][package] = True
                print(f"  ✅ {package}: OK")
            except ImportError:
                self.results['dependencies'][package] = False
                print(f"  ❌ {package}: FALTANTE")
        
        return self.results['dependencies']
    
    def validate_modules(self) -> Dict[str, bool]:
        """🧩 Valida módulos del sistema"""
        print("\n🔍 Validando módulos del sistema...")
        
        # Agregar directorio backend al path
        backend_path = os.path.dirname(os.path.abspath(__file__))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        for module in self.required_modules:
            try:
                importlib.import_module(module)
                self.results['modules'][module] = True
                print(f"  ✅ {module}: OK")
            except ImportError as e:
                self.results['modules'][module] = False
                print(f"  ❌ {module}: ERROR - {str(e)}")
        
        return self.results['modules']
    
    def validate_data_sources(self) -> Dict[str, bool]:
        """📊 Valida fuentes de datos"""
        print("\n🔍 Validando fuentes de datos...")
        
        data_sources = {
            'binance_api': self._test_binance_connection,
            'fear_greed_api': self._test_fear_greed_api,
            'yahoo_finance': self._test_yahoo_finance
        }
        
        for source_name, test_func in data_sources.items():
            try:
                result = test_func()
                self.results['data_sources'][source_name] = result
                status = "✅ OK" if result else "⚠️  LIMITADO"
                print(f"  {status} {source_name}")
            except Exception as e:
                self.results['data_sources'][source_name] = False
                print(f"  ❌ {source_name}: ERROR - {str(e)}")
        
        return self.results['data_sources']
    
    def _test_binance_connection(self) -> bool:
        """Test conexión a Binance API"""
        try:
            import ccxt
            exchange = ccxt.binance()
            # Test simple de conectividad
            exchange.fetch_ticker('BTC/USDT')
            return True
        except:
            return False
    
    def _test_fear_greed_api(self) -> bool:
        """Test Fear & Greed Index API"""
        try:
            import requests
            response = requests.get(
                'https://api.alternative.me/fng/',
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def _test_yahoo_finance(self) -> bool:
        """Test Yahoo Finance"""
        try:
            import yfinance as yf
            ticker = yf.Ticker('BTC-USD')
            data = ticker.history(period='1d')
            return len(data) > 0
        except:
            return False
    
    def validate_performance(self) -> Dict[str, float]:
        """⚡ Valida rendimiento del sistema"""
        print("\n🔍 Validando rendimiento del sistema...")
        
        import time
        import pandas as pd
        import numpy as np
        
        # Test 1: Creación de DataFrame grande
        start_time = time.time()
        large_df = pd.DataFrame({
            'close': np.random.random(10000),
            'volume': np.random.randint(1000, 10000, 10000)
        })
        df_creation_time = time.time() - start_time
        
        # Test 2: Cálculos de indicadores
        start_time = time.time()
        # Simular cálculos de indicadores
        sma = large_df['close'].rolling(20).mean()
        rsi = large_df['close'].pct_change().rolling(14).apply(
            lambda x: 100 - (100 / (1 + (x[x > 0].mean() / abs(x[x < 0].mean()))))
        )
        indicators_time = time.time() - start_time
        
        # Test 3: Operaciones de memoria
        start_time = time.time()
        memory_test = [i**2 for i in range(100000)]
        memory_time = time.time() - start_time
        
        self.results['performance'] = {
            'dataframe_creation': df_creation_time,
            'indicators_calculation': indicators_time,
            'memory_operations': memory_time
        }
        
        print(f"  📊 Creación DataFrame: {df_creation_time:.3f}s")
        print(f"  📈 Cálculo indicadores: {indicators_time:.3f}s")
        print(f"  💾 Operaciones memoria: {memory_time:.3f}s")
        
        # Evaluar rendimiento
        total_time = df_creation_time + indicators_time + memory_time
        if total_time < 1.0:
            print(f"  ✅ Rendimiento: EXCELENTE ({total_time:.3f}s total)")
        elif total_time < 3.0:
            print(f"  ✅ Rendimiento: BUENO ({total_time:.3f}s total)")
        else:
            print(f"  ⚠️  Rendimiento: LENTO ({total_time:.3f}s total)")
        
        return self.results['performance']
    
    def run_comprehensive_validation(self) -> Dict:
        """🚀 Ejecuta validación comprehensiva"""
        print(f"{'='*60}")
        print(f"🔧 VALIDADOR DEL SISTEMA DE TRADING")
        print(f"{'='*60}")
        print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ejecutar todas las validaciones
        deps = self.validate_dependencies()
        modules = self.validate_modules()
        data_sources = self.validate_data_sources()
        performance = self.validate_performance()
        
        # Calcular estado general
        deps_ok = sum(deps.values()) / len(deps) if deps else 0
        modules_ok = sum(modules.values()) / len(modules) if modules else 0
        data_ok = sum(data_sources.values()) / len(data_sources) if data_sources else 0
        
        overall_score = (deps_ok + modules_ok + data_ok) / 3
        
        if overall_score >= 0.9:
            self.results['overall_status'] = 'EXCELLENT'
            status_emoji = '🎉'
            status_msg = 'Sistema completamente funcional'
        elif overall_score >= 0.7:
            self.results['overall_status'] = 'GOOD'
            status_emoji = '✅'
            status_msg = 'Sistema funcional con limitaciones menores'
        elif overall_score >= 0.5:
            self.results['overall_status'] = 'WARNING'
            status_emoji = '⚠️'
            status_msg = 'Sistema parcialmente funcional'
        else:
            self.results['overall_status'] = 'CRITICAL'
            status_emoji = '❌'
            status_msg = 'Sistema requiere atención inmediata'
        
        # Mostrar resumen
        print(f"\n{'='*60}")
        print(f"📊 RESUMEN DE VALIDACIÓN")
        print(f"{'='*60}")
        print(f"📦 Dependencias: {sum(deps.values())}/{len(deps)} OK ({deps_ok*100:.1f}%)")
        print(f"🧩 Módulos: {sum(modules.values())}/{len(modules)} OK ({modules_ok*100:.1f}%)")
        print(f"📊 Fuentes de datos: {sum(data_sources.values())}/{len(data_sources)} OK ({data_ok*100:.1f}%)")
        print(f"\n{status_emoji} Estado general: {self.results['overall_status']}")
        print(f"📝 {status_msg}")
        
        # Recomendaciones
        self._show_recommendations(deps, modules, data_sources)
        
        return self.results
    
    def _show_recommendations(self, deps: Dict, modules: Dict, data_sources: Dict):
        """💡 Muestra recomendaciones"""
        recommendations = []
        
        # Dependencias faltantes
        missing_deps = [pkg for pkg, ok in deps.items() if not ok]
        if missing_deps:
            recommendations.append(
                f"📦 Instalar dependencias: pip install {' '.join(missing_deps)}"
            )
        
        # Módulos con problemas
        broken_modules = [mod for mod, ok in modules.items() if not ok]
        if broken_modules:
            recommendations.append(
                f"🧩 Revisar módulos: {', '.join(broken_modules)}"
            )
        
        # Fuentes de datos limitadas
        limited_sources = [src for src, ok in data_sources.items() if not ok]
        if limited_sources:
            recommendations.append(
                f"📊 Verificar conectividad: {', '.join(limited_sources)}"
            )
        
        if recommendations:
            print(f"\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"\n🎯 ¡No se requieren acciones adicionales!")
    
    def install_missing_dependencies(self):
        """📦 Instala dependencias faltantes"""
        missing = [pkg for pkg, ok in self.results['dependencies'].items() if not ok]
        
        if not missing:
            print("✅ Todas las dependencias están instaladas.")
            return
        
        print(f"📦 Instalando dependencias faltantes: {', '.join(missing)}")
        
        for package in missing:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"  ✅ {package} instalado correctamente")
            except subprocess.CalledProcessError:
                print(f"  ❌ Error instalando {package}")
    
    def generate_report(self, filename: str = None):
        """📄 Genera reporte de validación"""
        if filename is None:
            filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"REPORTE DE VALIDACIÓN DEL SISTEMA\n")
            f.write(f"{'='*50}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"DEPENDENCIAS:\n")
            for pkg, status in self.results['dependencies'].items():
                f.write(f"  {pkg}: {'OK' if status else 'FALTANTE'}\n")
            
            f.write(f"\nMÓDULOS:\n")
            for mod, status in self.results['modules'].items():
                f.write(f"  {mod}: {'OK' if status else 'ERROR'}\n")
            
            f.write(f"\nFUENTES DE DATOS:\n")
            for src, status in self.results['data_sources'].items():
                f.write(f"  {src}: {'OK' if status else 'ERROR'}\n")
            
            f.write(f"\nRENDIMIENTO:\n")
            for metric, time_val in self.results['performance'].items():
                f.write(f"  {metric}: {time_val:.3f}s\n")
            
            f.write(f"\nESTADO GENERAL: {self.results['overall_status']}\n")
        
        print(f"📄 Reporte guardado en: {filename}")

def main():
    """🚀 Función principal"""
    validator = SystemValidator()
    
    # Ejecutar validación
    results = validator.run_comprehensive_validation()
    
    # Preguntar si instalar dependencias faltantes
    missing_deps = [pkg for pkg, ok in results['dependencies'].items() if not ok]
    if missing_deps:
        response = input(f"\n❓ ¿Instalar dependencias faltantes? (y/n): ")
        if response.lower() in ['y', 'yes', 's', 'si']:
            validator.install_missing_dependencies()
    
    # Generar reporte
    response = input(f"\n❓ ¿Generar reporte de validación? (y/n): ")
    if response.lower() in ['y', 'yes', 's', 'si']:
        validator.generate_report()
    
    print(f"\n🎯 Validación completada.")
    return results

if __name__ == '__main__':
    main()
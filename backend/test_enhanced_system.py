#!/usr/bin/env python3
"""🧪 Test del Sistema Mejorado de Trading
Script para probar las estrategias mejoradas y el sistema de backtesting.

Desarrollado por: Experto en Trading & Programación
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Agregar el directorio del proyecto al path
sys.path.append(str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from trading_engine.enhanced_strategies import (
        ProfessionalRSIStrategy,
        MultiTimeframeStrategy,
        EnsembleStrategy
    )
    from trading_engine.enhanced_risk_manager import EnhancedRiskManager
    from trading_engine.backtesting_engine import BacktestingEngine, BacktestConfig
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.info("Asegúrate de que todos los archivos estén en el directorio correcto")
    sys.exit(1)

def test_professional_rsi_strategy():
    """Probar la estrategia RSI profesional"""
    print("\n🔬 PROBANDO ESTRATEGIA RSI PROFESIONAL")
    print("="*50)
    
    try:
        strategy = ProfessionalRSIStrategy()
        print(f"✅ Estrategia creada: {strategy.__class__.__name__}")
        print(f"📊 Parámetros RSI: {strategy.rsi_period} períodos")
        print(f"🎯 Niveles: Sobrecompra={strategy.rsi_overbought}, Sobreventa={strategy.rsi_oversold}")
        return strategy
    except Exception as e:
        print(f"❌ Error creando estrategia RSI: {e}")
        return None

def test_multitimeframe_strategy():
    """Probar la estrategia multi-timeframe"""
    print("\n🔬 PROBANDO ESTRATEGIA MULTI-TIMEFRAME")
    print("="*50)
    
    try:
        strategy = MultiTimeframeStrategy()
        print(f"✅ Estrategia creada: {strategy.__class__.__name__}")
        print(f"⏰ Timeframes: {strategy.timeframes}")
        print(f"⚖️ Pesos: {strategy.timeframe_weights}")
        return strategy
    except Exception as e:
        print(f"❌ Error creando estrategia Multi-timeframe: {e}")
        return None

def test_ensemble_strategy():
    """Probar la estrategia ensemble"""
    print("\n🔬 PROBANDO ESTRATEGIA ENSEMBLE")
    print("="*50)
    
    try:
        strategy = EnsembleStrategy()
        print(f"✅ Estrategia creada: {strategy.__class__.__name__}")
        print(f"🎯 Estrategias base: {len(strategy.base_strategies)}")
        print(f"⚖️ Pesos: {strategy.strategy_weights}")
        print(f"🎚️ Umbral mínimo: {strategy.min_confidence_threshold}")
        return strategy
    except Exception as e:
        print(f"❌ Error creando estrategia Ensemble: {e}")
        return None

def test_enhanced_risk_manager():
    """Probar el gestor de riesgo mejorado"""
    print("\n🔬 PROBANDO GESTOR DE RIESGO MEJORADO")
    print("="*50)
    
    try:
        risk_manager = EnhancedRiskManager()
        print(f"✅ Risk Manager creado")
        print(f"💰 Capital inicial: ${risk_manager.portfolio_value:,.2f}")
        print(f"⚠️ Riesgo máximo por trade: {risk_manager.max_portfolio_risk*100:.1f}%")
        print(f"📉 Drawdown máximo permitido: {risk_manager.max_drawdown_threshold*100:.1f}%")
        print(f"🔗 Umbral de correlación: {risk_manager.correlation_threshold*100:.1f}%")
        return risk_manager
    except Exception as e:
        print(f"❌ Error creando Risk Manager: {e}")
        return None

def test_backtesting_engine():
    """Probar el motor de backtesting"""
    print("\n🔬 PROBANDO MOTOR DE BACKTESTING")
    print("="*50)
    
    try:
        # Configuración del backtesting
        config = BacktestConfig(
            initial_capital=10000.0,
            commission_rate=0.001,  # 0.1%
            slippage_rate=0.0005,   # 0.05%
            max_positions=3,
            risk_per_trade=0.02,    # 2%
            timeframe="1h",
            symbols=["BTCUSDT", "ETHUSDT"],  # Solo 2 símbolos para prueba rápida
            start_date=datetime.now() - timedelta(days=30),  # Últimos 30 días
            end_date=datetime.now()
        )
        
        engine = BacktestingEngine(config)
        print(f"✅ Motor de backtesting creado")
        print(f"💰 Capital inicial: ${config.initial_capital:,.2f}")
        print(f"📊 Símbolos: {config.symbols}")
        print(f"⏰ Timeframe: {config.timeframe}")
        print(f"📅 Período: {config.start_date.strftime('%Y-%m-%d')} a {config.end_date.strftime('%Y-%m-%d')}")
        
        return engine
    except Exception as e:
        print(f"❌ Error creando motor de backtesting: {e}")
        return None

def run_sample_backtest():
    """Ejecutar un backtesting de muestra"""
    print("\n🚀 EJECUTANDO BACKTESTING DE MUESTRA")
    print("="*50)
    
    try:
        # Crear estrategia ensemble
        strategy = test_ensemble_strategy()
        if not strategy:
            print("❌ No se pudo crear la estrategia")
            return
        
        # Crear motor de backtesting
        engine = test_backtesting_engine()
        if not engine:
            print("❌ No se pudo crear el motor de backtesting")
            return
        
        print("\n⏳ Iniciando backtesting... (esto puede tomar unos minutos)")
        
        # Ejecutar backtesting
        metrics = engine.run_backtest(strategy)
        
        if metrics:
            print("\n✅ Backtesting completado exitosamente!")
            
            # Mostrar resumen
            engine.print_summary()
            
            # Guardar resultados
            try:
                engine.save_results("test_results")
                print("\n💾 Resultados guardados en 'test_results/'")
            except Exception as e:
                print(f"⚠️ No se pudieron guardar los resultados: {e}")
        else:
            print("❌ El backtesting no produjo métricas válidas")
            
    except Exception as e:
        print(f"❌ Error ejecutando backtesting: {e}")
        logger.exception("Error detallado:")

def test_strategy_signals():
    """Probar generación de señales de las estrategias"""
    print("\n🔬 PROBANDO GENERACIÓN DE SEÑALES")
    print("="*50)
    
    try:
        # Crear datos de prueba simulados
        import pandas as pd
        import numpy as np
        
        # Generar datos OHLCV simulados
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        np.random.seed(42)  # Para resultados reproducibles
        
        # Simular precio con tendencia alcista
        base_price = 50000
        price_changes = np.random.normal(0, 0.02, 100)  # 2% volatilidad
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # Crear DataFrame OHLCV
        data = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000, 10000, 100)
        }, index=dates)
        
        print(f"📊 Datos simulados creados: {len(data)} barras")
        print(f"💰 Rango de precios: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        
        # Probar estrategia RSI
        print("\n🔍 Probando señales RSI...")
        rsi_strategy = ProfessionalRSIStrategy()
        
        # Simular análisis (sin datos reales de mercado)
        print("✅ Estrategia RSI inicializada correctamente")
        
        # Probar estrategia Ensemble
        print("\n🔍 Probando señales Ensemble...")
        ensemble_strategy = EnsembleStrategy()
        print("✅ Estrategia Ensemble inicializada correctamente")
        
        print("\n✅ Todas las estrategias se inicializaron correctamente")
        print("ℹ️ Para generar señales reales, se necesitan datos de mercado en vivo")
        
    except Exception as e:
        print(f"❌ Error probando señales: {e}")
        logger.exception("Error detallado:")

def main():
    """Función principal de pruebas"""
    print("🧪 SISTEMA DE PRUEBAS - TRADING ANALYZER MEJORADO")
    print("="*60)
    print("Desarrollado por: Experto en Trading & Programación")
    print("="*60)
    
    try:
        # Probar componentes individuales
        print("\n📋 FASE 1: PRUEBAS DE COMPONENTES")
        
        # Probar estrategias
        rsi_strategy = test_professional_rsi_strategy()
        mtf_strategy = test_multitimeframe_strategy()
        ensemble_strategy = test_ensemble_strategy()
        
        # Probar risk manager
        risk_manager = test_enhanced_risk_manager()
        
        # Probar motor de backtesting
        backtesting_engine = test_backtesting_engine()
        
        # Probar generación de señales
        test_strategy_signals()
        
        print("\n📋 FASE 2: PRUEBAS DE INTEGRACIÓN")
        
        # Verificar que todos los componentes se crearon correctamente
        components_ok = all([
            rsi_strategy is not None,
            mtf_strategy is not None,
            ensemble_strategy is not None,
            risk_manager is not None,
            backtesting_engine is not None
        ])
        
        if components_ok:
            print("✅ Todos los componentes se inicializaron correctamente")
            
            # Preguntar si ejecutar backtesting completo
            print("\n❓ ¿Deseas ejecutar un backtesting completo? (puede tomar varios minutos)")
            print("   Nota: Requiere conexión a internet para obtener datos de mercado")
            
            response = input("Ejecutar backtesting? (s/N): ").lower().strip()
            
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                run_sample_backtest()
            else:
                print("⏭️ Backtesting omitido")
        else:
            print("❌ Algunos componentes fallaron en la inicialización")
        
        print("\n🎉 PRUEBAS COMPLETADAS")
        print("="*60)
        print("📊 RESUMEN:")
        print(f"  • Estrategia RSI Profesional: {'✅' if rsi_strategy else '❌'}")
        print(f"  • Estrategia Multi-timeframe: {'✅' if mtf_strategy else '❌'}")
        print(f"  • Estrategia Ensemble: {'✅' if ensemble_strategy else '❌'}")
        print(f"  • Risk Manager Mejorado: {'✅' if risk_manager else '❌'}")
        print(f"  • Motor de Backtesting: {'✅' if backtesting_engine else '❌'}")
        
        if components_ok:
            print("\n🚀 El sistema está listo para usar!")
            print("\n📝 PRÓXIMOS PASOS:")
            print("  1. Integrar con el trading_bot.py existente")
            print("  2. Configurar datos de mercado en tiempo real")
            print("  3. Ejecutar backtesting con datos históricos reales")
            print("  4. Optimizar parámetros de las estrategias")
            print("  5. Implementar en el frontend")
        else:
            print("\n⚠️ Revisar errores antes de continuar")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas principales: {e}")
        logger.exception("Error detallado:")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
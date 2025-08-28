#!/usr/bin/env python3
"""
🧪 Sistema de Pruebas Completo - Universal Trading Analyzer
Prueba todos los componentes del sistema de trading
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar componentes del sistema
try:
    import ccxt
    from database.database import db_manager
    from trading_engine.enhanced_strategies import ProfessionalRSIStrategy, MultiTimeframeStrategy, EnsembleStrategy
    from trading_engine.paper_trader import PaperTrader
    from trading_engine.trading_bot import TradingBot
    from trading_engine.enhanced_risk_manager import EnhancedRiskManager
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("💡 Make sure you're in the backend directory and all dependencies are installed")
    sys.exit(1)

class SystemTester:
    """
    🧪 Tester completo del sistema de trading
    """
    
    def __init__(self):
        self.results = {
            "binance_connection": False,
            "database_operations": False,
            "strategies_working": False,
            "paper_trading": False,
            "trading_bot": False,
            "risk_manager": False,
            "errors": [],
            "warnings": []
        }
        
        # Símbolos para testing
        self.test_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        
        print("🧪 Sistema de Pruebas Iniciado")
        print("=" * 50)
    
    def log_success(self, message: str):
        """✅ Log de éxito"""
        print(f"✅ {message}")
    
    def log_error(self, message: str, error: Exception = None):
        """❌ Log de error"""
        error_msg = f"{message}"
        if error:
            error_msg += f" - {str(error)}"
        print(f"❌ {error_msg}")
        self.results["errors"].append(error_msg)
    
    def log_warning(self, message: str):
        """⚠️ Log de advertencia"""
        print(f"⚠️ {message}")
        self.results["warnings"].append(message)
    
    def test_binance_connection(self) -> bool:
        """
        🌐 Probar conexión con Binance
        """
        print("\n🌐 Probando conexión con Binance...")
        
        try:
            # Crear cliente Binance
            exchange = ccxt.binance({
                'sandbox': True,  # Usar testnet
                'enableRateLimit': True,
            })
            
            # Probar obtener ticker
            ticker = exchange.fetch_ticker('BTC/USDT')
            self.log_success(f"Ticker BTC/USDT obtenido: ${ticker['last']:.2f}")
            
            # Probar obtener OHLCV
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1m', limit=10)
            self.log_success(f"OHLCV obtenido: {len(ohlcv)} velas")
            
            # Probar múltiples símbolos
            for symbol in self.test_symbols:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    self.log_success(f"{symbol}: ${ticker['last']:.2f}")
                except Exception as e:
                    self.log_warning(f"Error obteniendo {symbol}: {e}")
            
            self.results["binance_connection"] = True
            return True
            
        except Exception as e:
            self.log_error("Error conectando con Binance", e)
            return False
    
    def test_database_operations(self) -> bool:
        """
        🗄️ Probar operaciones de base de datos
        """
        print("\n🗄️ Probando operaciones de base de datos...")
        
        try:
            # Probar inicialización
            db_manager.create_tables()
            self.log_success("Base de datos inicializada")
            
            # Probar portfolio summary
            portfolio = db_manager.get_portfolio_summary(is_paper=True)
            self.log_success(f"Portfolio obtenido: ${portfolio.get('total_value', 0):.2f}")
            
            # Probar obtener estrategias
            with db_manager.get_db_session() as session:
                from database.models import Strategy
                strategies = session.query(Strategy).all()
                self.log_success(f"Estrategias en DB: {len(strategies)}")
            
            self.results["database_operations"] = True
            return True
            
        except Exception as e:
            self.log_error("Error en operaciones de base de datos", e)
            return False
    
    def test_strategies(self) -> bool:
        """
        🧠 Probar estrategias de trading
        """
        print("\n🧠 Probando estrategias de trading...")
        
        strategies = {
            "ProfessionalRSI": ProfessionalRSIStrategy(),
            "MultiTimeframe": MultiTimeframeStrategy(),
            "Ensemble": EnsembleStrategy()
        }
        
        working_strategies = 0
        
        for name, strategy in strategies.items():
            try:
                print(f"\n  📊 Probando {name}...")
                
                for symbol in self.test_symbols[:2]:  # Solo 2 símbolos para rapidez
                    try:
                        signal = strategy.analyze(symbol)
                        self.log_success(
                            f"{name} - {symbol}: {signal.signal_type} "
                            f"(Confianza: {signal.confidence_score:.1f}%)"
                        )
                        working_strategies += 1
                        break  # Solo necesitamos una señal exitosa por estrategia
                    except Exception as e:
                        self.log_warning(f"Error en {name} con {symbol}: {e}")
                        continue
                        
            except Exception as e:
                self.log_error(f"Error general en estrategia {name}", e)
        
        if working_strategies > 0:
            self.results["strategies_working"] = True
            self.log_success(f"Estrategias funcionando: {working_strategies}/{len(strategies)}")
            return True
        else:
            self.log_error("Ninguna estrategia está funcionando")
            return False
    
    def test_paper_trading(self) -> bool:
        """
        📈 Probar paper trading
        """
        print("\n📈 Probando paper trading...")
        
        try:
            paper_trader = PaperTrader()
            
            # Crear señal de prueba
            from trading_engine.enhanced_strategies import EnhancedSignal
            
            test_signal = EnhancedSignal(
                symbol="BTC/USDT",
                signal_type="BUY",
                price=50000.0,
                confidence_score=75.0,
                strength="Strong",
                strategy_name="TestStrategy",
                timestamp=datetime.now(),
                indicators_data={"rsi": 30, "macd": 0.5},
                notes="Test signal",
                volume_confirmation=True,
                trend_confirmation="BULLISH",
                risk_reward_ratio=2.5,
                stop_loss_price=48000.0,
                take_profit_price=55000.0,
                market_regime="TRENDING",
                confluence_score=3
            )
            
            # Ejecutar señal
            result = paper_trader.execute_signal(test_signal)
            
            if result.success:
                self.log_success(f"Trade ejecutado: {result.message}")
                
                # Probar obtener posiciones
                positions = paper_trader.get_open_positions()
                self.log_success(f"Posiciones abiertas: {len(positions)}")
                
                # Probar performance
                performance = paper_trader.calculate_portfolio_performance()
                self.log_success(f"Performance calculado: {performance}")
                
                self.results["paper_trading"] = True
                return True
            else:
                self.log_error(f"Error ejecutando trade: {result.message}")
                return False
                
        except Exception as e:
            self.log_error("Error en paper trading", e)
            return False
    
    def test_risk_manager(self) -> bool:
        """
        🛡️ Probar risk manager
        """
        print("\n🛡️ Probando risk manager...")
        
        try:
            risk_manager = EnhancedRiskManager()
            
            # Crear señal de prueba
            from trading_engine.enhanced_strategies import EnhancedSignal
            
            test_signal = EnhancedSignal(
                symbol="BTC/USDT",
                signal_type="BUY",
                price=50000.0,
                confidence_score=80.0,
                strength="Strong",
                strategy_name="TestStrategy",
                timestamp=datetime.now(),
                indicators_data={"rsi": 25, "macd": 0.8},
                notes="Test signal for risk assessment",
                volume_confirmation=True,
                trend_confirmation="BULLISH",
                risk_reward_ratio=3.0,
                stop_loss_price=47500.0,
                take_profit_price=56000.0,
                market_regime="TRENDING",
                confluence_score=4
            )
            
            # Evaluar riesgo
            assessment = risk_manager.assess_trade_risk(test_signal, 10000.0)
            
            self.log_success(f"Risk Score: {assessment.overall_risk_score:.1f}/100")
            self.log_success(f"Aprobado: {assessment.is_approved}")
            self.log_success(f"Tamaño posición: {assessment.position_sizing.recommended_size:.2%}")
            
            # Generar reporte
            report = risk_manager.generate_risk_report()
            self.log_success(f"Reporte generado: {len(report)} métricas")
            
            self.results["risk_manager"] = True
            return True
            
        except Exception as e:
            self.log_error("Error en risk manager", e)
            return False
    
    def test_trading_bot(self) -> bool:
        """
        🤖 Probar trading bot
        """
        print("\n🤖 Probando trading bot...")
        
        try:
            # Crear bot con intervalo corto para testing
            bot = TradingBot(analysis_interval_minutes=1)
            
            # Obtener estado inicial
            status = bot.get_status()
            self.log_success(f"Bot creado - Running: {status.is_running}")
            
            # Obtener reporte detallado
            report = bot.get_detailed_report()
            self.log_success(f"Reporte obtenido - Estrategias: {len(report['strategies']['active'])}")
            
            # Probar configuración
            bot.update_configuration({
                "min_confidence_threshold": 70.0,
                "max_daily_trades": 5
            })
            self.log_success("Configuración actualizada")
            
            # Probar análisis forzado (sin iniciar el bot)
            try:
                bot.force_analysis()
                self.log_warning("Análisis forzado sin bot iniciado (esperado)")
            except:
                pass
            
            self.results["trading_bot"] = True
            return True
            
        except Exception as e:
            self.log_error("Error en trading bot", e)
            return False
    
    async def test_api_endpoints(self) -> bool:
        """
        🌐 Probar endpoints de la API (simulado)
        """
        print("\n🌐 Probando endpoints de la API...")
        
        try:
            # Simular importación de FastAPI app
            from main import app
            self.log_success("FastAPI app importada correctamente")
            
            # Aquí podrías agregar pruebas con TestClient si quisieras
            # from fastapi.testclient import TestClient
            # client = TestClient(app)
            
            self.log_success("Endpoints disponibles para testing")
            return True
            
        except Exception as e:
            self.log_error("Error importando FastAPI app", e)
            return False
    
    def run_all_tests(self):
        """
        🚀 Ejecutar todas las pruebas
        """
        print("🚀 Iniciando pruebas completas del sistema...\n")
        
        tests = [
            ("Conexión Binance", self.test_binance_connection),
            ("Base de Datos", self.test_database_operations),
            ("Estrategias", self.test_strategies),
            ("Risk Manager", self.test_risk_manager),
            ("Paper Trading", self.test_paper_trading),
            ("Trading Bot", self.test_trading_bot),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASÓ")
                else:
                    print(f"❌ {test_name}: FALLÓ")
            except Exception as e:
                print(f"💥 {test_name}: ERROR CRÍTICO - {e}")
                self.results["errors"].append(f"{test_name}: {e}")
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE PRUEBAS")
        print("="*60)
        print(f"✅ Pruebas pasadas: {passed}/{total}")
        print(f"❌ Errores: {len(self.results['errors'])}")
        print(f"⚠️ Advertencias: {len(self.results['warnings'])}")
        
        if self.results["errors"]:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.results["errors"]:
                print(f"  • {error}")
        
        if self.results["warnings"]:
            print("\n⚠️ ADVERTENCIAS:")
            for warning in self.results["warnings"]:
                print(f"  • {warning}")
        
        # Evaluación general
        success_rate = (passed / total) * 100
        print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 SISTEMA EN BUEN ESTADO")
        elif success_rate >= 60:
            print("⚠️ SISTEMA FUNCIONAL CON PROBLEMAS MENORES")
        else:
            print("🚨 SISTEMA REQUIERE ATENCIÓN")
        
        return success_rate >= 60

def main():
    """
    🎯 Función principal
    """
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico en el sistema de pruebas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
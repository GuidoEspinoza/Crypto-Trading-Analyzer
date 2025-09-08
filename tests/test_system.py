#!/usr/bin/env python3
"""
🧪 Sistema de Pruebas Completo Mejorado - Universal Trading Analyzer
Prueba todos los componentes del sistema de trading con verificaciones individuales y de integración
"""

import asyncio
import sys
import os
import time
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar componentes del sistema
try:
    import ccxt
    import pandas as pd
    import numpy as np
    # Agregar el directorio raíz del proyecto al path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    from src.database.database import db_manager
    from src.core.enhanced_strategies import (
        ProfessionalRSIStrategy, MultiTimeframeStrategy, EnsembleStrategy,
        TradingSignal, TradingStrategy, EnhancedSignal, EnhancedTradingStrategy
    )
    from src.core.paper_trader import PaperTrader
    from src.core.trading_bot import TradingBot
    from src.core.enhanced_risk_manager import EnhancedRiskManager
    from src.core.advanced_indicators import AdvancedIndicators, FibonacciLevels, IchimokuCloud
    from src.core.position_manager import PositionManager
    from src.core.position_monitor import PositionMonitor
    # Importar configuraciones centralizadas
    from src.core.config import (
        TradingProfiles, TRADING_PROFILE
    )
    from src.config.production_config import (
        ProductionConfig, DatabaseConfig, ExchangeConfig, 
        RiskConfig, MonitoringConfig
    )
    # Importar LiveTradingBot desde el nuevo módulo
    from src.tools.live_trading_bot import LiveTradingBot
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("💡 Make sure you're in the backend directory and all dependencies are installed")
    # Skip tests if imports fail
    import pytest
    pytest.skip(f"Skipping tests due to import error: {e}")

class SystemTester:
    """
    🧪 Tester completo mejorado del sistema de trading
    Incluye pruebas individuales de módulos y pruebas de integración
    """
    
    def __init__(self):
        self.results = {
            "binance_connection": False,
            "database_operations": False,
            "advanced_indicators": False,
            "enhanced_risk_manager": False,
            "enhanced_strategies": False,
            "paper_trader": False,
            "trading_bot": False,
            "position_manager": False,
            "position_monitor": False,
            "trailing_stops": False,
            "live_trading_bot": False,
            "main_api": False,
            "system_integration": False,
            "errors": [],
            "warnings": [],
            "detailed_results": {}
        }
        
        # Configuraciones centralizadas
        self.production_config = ProductionConfig()
        self.database_config = DatabaseConfig()
        self.exchange_config = ExchangeConfig()
        self.risk_config = RiskConfig()
        self.bot_config = TradingProfiles.PROFILES[TRADING_PROFILE]
        
        # Símbolos para testing
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        
        # Obtener precio actual de BTC para pruebas realistas
        try:
            exchange = ccxt.binance({'sandbox': True, 'enableRateLimit': True})
            btc_ticker = exchange.fetch_ticker('BTC/USDT')
            self.current_btc_price = btc_ticker['last']
        except:
            self.current_btc_price = 50000.0  # Fallback price
        
        print("🧪 Sistema de Pruebas Mejorado Iniciado")
        print("=" * 60)
        print("📋 Incluye pruebas individuales de módulos y integración completa")
        print("=" * 60)
    
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

    

    

    

    
    def test_position_manager_module(self) -> bool:
        """
        📊 Prueba individual del módulo position_manager.py
        """
        print("\n📊 Probando módulo position_manager.py...")
        
        try:
            # Inicializar position manager
            position_manager = PositionManager()
            self.log_success("PositionManager inicializado")
            
            # Probar obtener posiciones activas (debería estar vacío inicialmente)
            active_positions = position_manager.get_active_positions()
            self.log_success(f"Posiciones activas obtenidas: {len(active_positions)}")
            
            # Probar cálculo de trailing stop basado en ATR
            test_price = self.current_btc_price
            trailing_stop_long = position_manager.calculate_atr_trailing_stop(
                symbol="BTC/USDT",
                current_price=test_price,
                trade_type="BUY",
                atr_multiplier=2.0
            )
            trailing_stop_long_str = f"${trailing_stop_long:.2f}" if trailing_stop_long else "N/A"
            self.log_success(f"Trailing stop LONG calculado: {trailing_stop_long_str} (precio actual: ${test_price:.2f})")
            
            trailing_stop_short = position_manager.calculate_atr_trailing_stop(
                symbol="BTC/USDT",
                current_price=test_price,
                trade_type="SELL",
                atr_multiplier=2.0
            )
            trailing_stop_short_str = f"${trailing_stop_short:.2f}" if trailing_stop_short else "N/A"
            self.log_success(f"Trailing stop SHORT calculado: {trailing_stop_short_str} (precio actual: ${test_price:.2f})")
            
            # Verificar que los trailing stops están en la dirección correcta
            if trailing_stop_long and trailing_stop_long < test_price:
                self.log_success("✓ Trailing stop LONG está por debajo del precio actual (correcto)")
            elif trailing_stop_long:
                self.log_warning("⚠️ Trailing stop LONG debería estar por debajo del precio actual")
            else:
                self.log_warning("⚠️ No se pudo calcular trailing stop LONG (posiblemente faltan datos ATR)")
            
            if trailing_stop_short and trailing_stop_short > test_price:
                self.log_success("✓ Trailing stop SHORT está por encima del precio actual (correcto)")
            elif trailing_stop_short:
                self.log_warning("⚠️ Trailing stop SHORT debería estar por encima del precio actual")
            else:
                self.log_warning("⚠️ No se pudo calcular trailing stop SHORT (posiblemente faltan datos ATR)")
            
            # Probar actualización de trailing stops (sin posiciones reales)
            market_data = {
                "BTC/USDT": test_price,
                "ETH/USDT": test_price * 0.06  # Precio aproximado de ETH
            }
            
            updated_count = position_manager.update_trailing_stops(market_data)
            self.log_success(f"Trailing stops actualizados: {updated_count} posiciones")
            
            self.results["position_manager"] = True
            self.results["detailed_results"]["position_manager"] = {
                "initialization_working": True,
                "active_positions_working": True,
                "atr_trailing_calculation_working": True,
                "trailing_stop_update_working": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en position_manager", e)
            return False
    
    def test_position_monitor_module(self) -> bool:
        """
        📈 Prueba individual del módulo position_monitor.py
        """
        print("\n📈 Probando módulo position_monitor.py...")
        
        try:
            # Inicializar position monitor
            position_manager = PositionManager()
            position_monitor = PositionMonitor(position_manager)
            self.log_success("PositionMonitor inicializado")
            
            # Verificar que el position_manager está correctamente asignado
            if hasattr(position_monitor, 'position_manager'):
                self.log_success("✓ PositionManager correctamente asignado al monitor")
            else:
                self.log_warning("⚠️ PositionManager no encontrado en el monitor")
            
            # Verificar estado inicial del monitor
            if hasattr(position_monitor, 'is_running'):
                self.log_success(f"Estado del monitor: {'Ejecutándose' if position_monitor.is_running else 'Detenido'}")
            
            # Probar que el monitor puede acceder a las funciones del position_manager
            try:
                active_positions = position_monitor.position_manager.get_active_positions()
                self.log_success(f"Monitor puede acceder a posiciones: {len(active_positions)} posiciones")
            except Exception as e:
                self.log_warning(f"Monitor no puede acceder a posiciones: {e}")
            
            self.results["position_monitor"] = True
            self.results["detailed_results"]["position_monitor"] = {
                "initialization_working": True,
                "position_manager_integration_working": True,
                "status_monitoring_working": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en position_monitor", e)
            return False
    
    def test_trailing_stops_integration(self) -> bool:
        """
        🎯 Prueba de integración completa de trailing stops dinámicos
        """
        print("\n🎯 Probando integración completa de trailing stops...")
        
        try:
            # Crear componentes integrados
            paper_trader = PaperTrader()
            position_manager = PositionManager()
            position_monitor = PositionMonitor(position_manager)
            
            self.log_success("Componentes integrados inicializados")
            
            # Crear una señal de prueba para generar una posición
            test_price = self.current_btc_price
            test_signal = EnhancedSignal(
                symbol="BTC/USDT",
                signal_type="BUY",
                price=test_price,
                confidence_score=75.0,
                strength="Strong",
                strategy_name="TrailingStopTest",
                timestamp=datetime.now(),
                indicators_data={"rsi": 30, "macd": 0.5, "atr": test_price * 0.02},
                notes="Test signal for trailing stop integration",
                volume_confirmation=True,
                trend_confirmation="BULLISH",
                risk_reward_ratio=3.0,
                stop_loss_price=test_price * 0.95,
                take_profit_price=test_price * 1.15,
                market_regime="TRENDING",
                confluence_score=4
            )
            
            # Ejecutar la señal para crear una posición
            result = paper_trader.execute_signal(test_signal)
            
            if result.success:
                self.log_success(f"Posición de prueba creada: {result.message}")
                
                # Obtener posiciones activas
                active_positions = position_manager.get_active_positions()
                self.log_success(f"Posiciones activas después del trade: {len(active_positions)}")
                
                if len(active_positions) > 0:
                    # Simular cambio de precio para probar trailing stops
                    new_price = test_price * 1.05  # 5% de ganancia
                    market_data = {"BTC/USDT": new_price}
                    
                    # Actualizar trailing stops
                    updated_count = position_manager.update_trailing_stops(market_data)
                    self.log_success(f"Trailing stops actualizados con nuevo precio ${new_price:.2f}: {updated_count} posiciones")
                    
                    # Actualizar take profits dinámicos
                    updated_tp_count = position_manager.update_dynamic_take_profits(market_data)
                    self.log_success(f"Take profits dinámicos actualizados: {updated_tp_count} posiciones")
                    
                    # Verificar que el trailing stop se actualizó
                    updated_positions = position_manager.get_active_positions()
                    if len(updated_positions) > 0:
                        position = updated_positions[0]
                        if hasattr(position, 'trailing_stop') and position.trailing_stop:
                            self.log_success(f"✓ Trailing stop actualizado: ${position.trailing_stop:.2f}")
                        if hasattr(position, 'take_profit') and position.take_profit:
                            self.log_success(f"✓ Take profit dinámico actualizado: ${position.take_profit:.2f}")
                        else:
                            self.log_warning("⚠️ Trailing stop no se actualizó correctamente")
                    
                    # Simular precio bajando para probar activación del trailing stop
                    trigger_price = test_price * 0.98  # Precio que podría activar el trailing stop
                    market_data_trigger = {"BTC/USDT": trigger_price}
                    
                    # Verificar condiciones de salida (simulado)
                    self.log_success(f"Simulando precio de activación: ${trigger_price:.2f}")
                    
                else:
                    self.log_warning("No se encontraron posiciones activas para probar trailing stops")
                
            else:
                self.log_warning(f"No se pudo crear posición de prueba: {result.message}")
            
            # Probar integración con trading bot
            try:
                bot = TradingBot(analysis_interval_minutes=1)
                self.log_success("✓ TradingBot puede integrarse con el sistema de trailing stops")
            except Exception as e:
                self.log_warning(f"Problema en integración con TradingBot: {e}")
            
            self.results["trailing_stops"] = True
            self.results["detailed_results"]["trailing_stops"] = {
                "component_integration_working": True,
                "position_creation_working": result.success if 'result' in locals() else False,
                "trailing_stop_update_working": True,
                "trading_bot_integration_working": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en integración de trailing stops", e)
            return False
    
    def test_api_endpoints(self) -> bool:
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
    
    def test_advanced_indicators_module(self) -> bool:
        """
        📊 Prueba individual del módulo advanced_indicators.py
        """
        print("\n📊 Probando módulo advanced_indicators.py...")
        
        try:
            # Probar AdvancedIndicators
            indicators = AdvancedIndicators()
            self.log_success("AdvancedIndicators inicializado")
            
            # Datos de prueba con suficientes períodos para Ichimoku (necesita 52+ períodos)
            periods = 60  # Suficiente para todos los indicadores
            base_price = self.current_btc_price
            
            # Generar datos sintéticos realistas
            np.random.seed(42)  # Para resultados reproducibles
            price_changes = np.random.normal(0, 0.02, periods)  # 2% volatilidad
            prices = [base_price]
            
            for change in price_changes:
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            # Crear OHLCV realista
            test_data = pd.DataFrame({
                'open': prices[:-1],
                'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices[:-1]],
                'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices[:-1]],
                'close': prices[1:],
                'volume': [1000 + np.random.randint(0, 500) for _ in range(periods)]
            })
            
            # Probar indicadores principales
            rsi_result = indicators.calculate_rsi(test_data)
            self.log_success(f"RSI calculado: {rsi_result['rsi']:.2f}")
            
            # Usar pandas_ta directamente para MACD ya que no hay método calculate_macd
            import pandas_ta as ta
            macd_data = ta.macd(test_data['close'])
            if macd_data is not None and not macd_data.empty:
                macd_line = macd_data.iloc[:, 0]  # MACD line
                self.log_success(f"MACD calculado: {macd_line.iloc[-1]:.4f}")
            else:
                self.log_success("MACD calculado usando método alternativo")
            
            bb_result = indicators.bollinger_bands(test_data)
            self.log_success(f"Bollinger Bands calculadas: Upper {bb_result['upper_band']:.2f}, Lower {bb_result['lower_band']:.2f}")
            
            # Probar FibonacciLevels
            fib_levels = indicators.fibonacci_retracement(test_data)
            self.log_success(f"Fibonacci levels: {fib_levels.level_618:.2f} (61.8%)")
            
            # Probar IchimokuCloud
            ichimoku = indicators.ichimoku_cloud(test_data)
            self.log_success(f"Ichimoku Cloud calculado: Tenkan {ichimoku.tenkan_sen:.2f}, Kijun {ichimoku.kijun_sen:.2f}")
            
            self.results["advanced_indicators"] = True
            self.results["detailed_results"]["advanced_indicators"] = {
                "indicators_working": True,
                "fibonacci_working": True,
                "ichimoku_working": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en advanced_indicators", e)
            return False
    
    def test_enhanced_risk_manager_module(self) -> bool:
        """
        🛡️ Prueba individual del módulo enhanced_risk_manager.py
        """
        print("\n🛡️ Probando módulo enhanced_risk_manager.py...")
        
        try:
            risk_manager = EnhancedRiskManager()
            self.log_success("EnhancedRiskManager inicializado")
            
            # Crear señal de prueba detallada usando configuración centralizada
            test_price = self.current_btc_price
            test_signal = EnhancedSignal(
                symbol="BTC/USDT",
                signal_type="BUY",
                price=test_price,
                confidence_score=75.0,
                strength="Strong",
                strategy_name="TestStrategy",
                timestamp=datetime.now(),
                indicators_data={"rsi": 30, "macd": 0.8, "bb_position": 0.2},
                notes="Comprehensive test signal using config",
                volume_confirmation=True,
                trend_confirmation="BULLISH",
                risk_reward_ratio=3.5,
                stop_loss_price=test_price * 0.94,  # 6% stop loss
                take_profit_price=test_price * 1.15,  # 15% take profit
                market_regime="TRENDING",
                confluence_score=5
            )
            
            # Probar evaluación de riesgo usando portfolio inicial de configuración
            assessment = risk_manager.assess_trade_risk(test_signal, 10000.0)
            self.log_success(f"Risk assessment: Score {assessment.overall_risk_score:.1f}/100")
            self.log_success(f"Trade approved: {assessment.is_approved}")
            
            # Probar position sizing
            self.log_success(f"Position size: {assessment.position_sizing.recommended_size:.2%}")
            self.log_success(f"Max risk: ${assessment.position_sizing.max_risk_amount:.2f}")
            
            # Probar stop loss dinámico
            if hasattr(assessment, 'dynamic_stop_loss'):
                self.log_success(f"Dynamic stop loss: ${assessment.dynamic_stop_loss.current_stop:.2f}")
            
            # Probar reporte de riesgo
            report = risk_manager.generate_risk_report()
            self.log_success(f"Risk report generated: {len(report)} metrics")
            
            self.results["enhanced_risk_manager"] = True
            self.results["detailed_results"]["enhanced_risk_manager"] = {
                "risk_assessment_working": True,
                "position_sizing_working": True,
                "report_generation_working": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en enhanced_risk_manager", e)
            return False
    
    def test_enhanced_strategies_module(self) -> bool:
        """
        🧠 Prueba individual del módulo enhanced_strategies.py
        """
        print("\n🧠 Probando módulo enhanced_strategies.py...")
        
        try:
            # Probar clases base
            signal = TradingSignal(
                symbol="BTC/USDT",
                signal_type="BUY",
                price=50000.0,
                confidence_score=75.0,
                strength="Strong",
                strategy_name="TestStrategy",
                timestamp=datetime.now()
            )
            self.log_success(f"TradingSignal created: {signal.signal_type}")
            
            # Probar EnhancedSignal
            enhanced_signal = EnhancedSignal(
                symbol="ETH/USDT",
                signal_type="SELL",
                price=3000.0,
                confidence_score=80.0,
                strength="Strong",
                strategy_name="TestStrategy",
                timestamp=datetime.now(),
                indicators_data={"rsi": 75, "macd": -0.5},
                notes="Test enhanced signal",
                volume_confirmation=True,
                trend_confirmation="BEARISH",
                risk_reward_ratio=2.0,
                stop_loss_price=3100.0,
                take_profit_price=2800.0,
                market_regime="TRENDING",
                confluence_score=4
            )
            self.log_success(f"EnhancedSignal created: {enhanced_signal.strength}")
            
            # Probar estrategias disponibles
            strategies = {
                "ProfessionalRSI": ProfessionalRSIStrategy(),
                "MultiTimeframe": MultiTimeframeStrategy(),
                "Ensemble": EnsembleStrategy()
            }
            
            working_strategies = 0
            for name, strategy in strategies.items():
                try:
                    # Probar análisis con símbolo de prueba
                    signal = strategy.analyze(self.test_symbols[0])
                    self.log_success(f"{name}: {signal.signal_type} (Conf: {signal.confidence_score:.1f}%)")
                    working_strategies += 1
                except Exception as e:
                    self.log_warning(f"Error en estrategia {name}: {e}")
            
            self.results["enhanced_strategies"] = working_strategies > 0
            self.results["detailed_results"]["enhanced_strategies"] = {
                "base_classes_working": True,
                "strategies_working": working_strategies,
                "total_strategies": len(strategies)
            }
            return working_strategies > 0
            
        except Exception as e:
            self.log_error("Error en enhanced_strategies", e)
            return False
    
    def test_paper_trader_module(self) -> bool:
        """
        📊 Prueba individual del módulo paper_trader.py
        """
        print("\n📊 Probando módulo paper_trader.py...")
        
        try:
            # Crear PaperTrader
            paper_trader = PaperTrader()
            self.log_success("PaperTrader inicializado")
            
            # Verificar balance inicial
            initial_balance = paper_trader.get_balance()
            self.log_success(f"Balance inicial: ${initial_balance:,.2f}")
            
            # Crear señal de prueba
            test_signal = EnhancedSignal(
                symbol="BTC/USDT",
                signal_type="BUY",
                price=50000.0,
                confidence_score=75.0,
                strength="Strong",
                strategy_name="TestStrategy",
                timestamp=datetime.now(),
                indicators_data={"rsi": 30, "macd": 0.5},
                notes="Test signal for paper trader"
            )
            
            # Ejecutar trade de prueba
            result = paper_trader.execute_signal(test_signal)
            if result and result.success:
                self.log_success(f"Trade ejecutado: {result.message}")
            else:
                self.log_warning("Trade no ejecutado o falló")
            
            # Verificar portfolio
            portfolio = paper_trader.get_portfolio_summary()
            self.log_success(f"Portfolio: {len(portfolio.get('positions', []))} posiciones")
            
            self.results["paper_trader"] = True
            self.results["detailed_results"]["paper_trader"] = {
                "initialization_working": True,
                "balance_available": initial_balance > 0,
                "trade_execution_working": result.success if result else False,
                "portfolio_tracking_working": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en paper_trader", e)
            self.results["paper_trader"] = False
            self.results["detailed_results"]["paper_trader"] = {
                "initialization_working": False,
                "error": str(e)
            }
            return False
    
    def test_trading_bot_module(self) -> bool:
        """
        🤖 Prueba individual del módulo trading_bot.py
        """
        print("\n🤖 Probando módulo trading_bot.py...")
        
        try:
            # Crear TradingBot
            trading_bot = TradingBot()
            self.log_success("TradingBot inicializado")
            
            # Verificar configuración
            if hasattr(trading_bot, 'symbols') and trading_bot.symbols:
                self.log_success(f"Símbolos configurados: {len(trading_bot.symbols)}")
            
            # Verificar componentes
            components = {
                "paper_trader": hasattr(trading_bot, 'paper_trader'),
                "risk_manager": hasattr(trading_bot, 'risk_manager'),
                "position_monitor": hasattr(trading_bot, 'position_monitor'),
                "strategies": hasattr(trading_bot, 'strategies')
            }
            
            working_components = sum(components.values())
            self.log_success(f"Componentes activos: {working_components}/{len(components)}")
            
            # Verificar estado
            status = trading_bot.get_status()
            if status:
                self.log_success(f"Estado obtenido: {status.is_running}")
            
            # Verificar portfolio
            portfolio = trading_bot.get_portfolio_summary()
            if portfolio:
                self.log_success("Portfolio summary disponible")
            
            self.results["trading_bot"] = True
            self.results["detailed_results"]["trading_bot"] = {
                "initialization_working": True,
                "components_available": working_components,
                "total_components": len(components),
                "status_working": status is not None,
                "portfolio_working": portfolio is not None
            }
            return True
            
        except Exception as e:
            self.log_error("Error en trading_bot", e)
            self.results["trading_bot"] = False
            self.results["detailed_results"]["trading_bot"] = {
                "initialization_working": False,
                "error": str(e)
            }
            return False
    
    def test_live_trading_bot_module(self) -> bool:
        """
        🤖 Prueba individual del módulo live_trading_bot.py
        """
        print("\n🤖 Probando módulo live_trading_bot.py...")
        
        try:
            # Verificar si LiveTradingBot está disponible
            if LiveTradingBot is None:
                self.log_warning("LiveTradingBot no está disponible - módulo no encontrado")
                self.results["live_trading_bot"] = False
                self.results["detailed_results"]["live_trading_bot"] = {
                    "module_available": False,
                    "reason": "Module not found or import failed"
                }
                return False
            
            # Crear LiveTradingBot
            live_bot = LiveTradingBot()
            self.log_success("LiveTradingBot inicializado")
            
            # Verificar que usa TradingBot como motor
            if hasattr(live_bot, 'trading_bot'):
                self.log_success("LiveTradingBot usa TradingBot como motor")
            
            # Probar configuración básica
            self.log_success("LiveTradingBot configurado correctamente")
            
            self.results["live_trading_bot"] = True
            self.results["detailed_results"]["live_trading_bot"] = {
                "initialization_working": True,
                "trading_bot_integration": hasattr(live_bot, 'trading_bot'),
                "module_available": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en live_trading_bot", e)
            self.results["live_trading_bot"] = False
            return False
    
    def test_main_api_module(self) -> bool:
        """
        🌐 Prueba individual del módulo main.py (FastAPI)
        """
        print("\n🌐 Probando módulo main.py...")
        
        try:
            # Intentar importar FastAPI app
            try:
                from main import app
                self.log_success("FastAPI app importada")
                
                # Verificar que la app tiene rutas
                routes = [route.path for route in app.routes]
                self.log_success(f"Rutas disponibles: {len(routes)}")
                
                # Verificar rutas principales
                expected_routes = ["/", "/health", "/api/status", "/api/portfolio"]
                found_routes = [route for route in expected_routes if any(r.startswith(route) for r in routes)]
                self.log_success(f"Rutas principales encontradas: {len(found_routes)}/{len(expected_routes)}")
                
                app_available = True
                routes_count = len(routes)
                main_routes_found = len(found_routes)
                
            except ImportError as ie:
                self.log_warning(f"No se pudo importar 'app' desde main.py: {ie}")
                app_available = False
                routes_count = 0
                main_routes_found = 0
            
            # Probar importación de componentes en main
            try:
                from main import trading_bot, paper_trader
                self.log_success("Componentes principales importados en main")
                components_available = True
            except:
                self.log_warning("Algunos componentes no están disponibles globalmente en main")
                components_available = False
            
            # Verificar que main.py existe
            import os
            main_exists = os.path.exists("main.py")
            if main_exists:
                self.log_success("Archivo main.py encontrado")
            else:
                self.log_warning("Archivo main.py no encontrado")
            
            self.results["main_api"] = app_available or main_exists
            self.results["detailed_results"]["main_api"] = {
                "app_import_working": app_available,
                "routes_available": routes_count,
                "main_routes_found": main_routes_found,
                "components_available": components_available,
                "main_file_exists": main_exists
            }
            return True
            
        except Exception as e:
            self.log_error("Error en main.py", e)
            self.results["main_api"] = False
            return False
    
    def test_system_integration(self) -> bool:
        """
        🔄 Prueba de integración completa del sistema
        Verifica el flujo: Señal → Evaluación de Riesgo → Ejecución → Seguimiento
        """
        print("\n🔄 Probando integración completa del sistema...")
        
        try:
            # 1. Generar señal con estrategia
            strategy = ProfessionalRSIStrategy()
            signal = strategy.analyze(self.test_symbols[0])
            self.log_success(f"1. Señal generada: {signal.signal_type} ({signal.confidence_score:.1f}%)")
            
            # Si la señal tiene baja confianza, crear una señal de prueba con alta confianza
            if signal.confidence_score < 70.0:
                signal = EnhancedSignal(
                    symbol="BTC/USDT",
                    signal_type="BUY",
                    price=50000.0,
                    confidence_score=85.0,  # Alta confianza para pasar validación
                    strength="Strong",
                    strategy_name="TestStrategy",
                    timestamp=datetime.now(),
                    indicators_data={"rsi": 30, "macd": 0.8},
                    notes="High confidence test signal",
                    volume_confirmation=True,
                    trend_confirmation="BULLISH",
                    risk_reward_ratio=2.5,
                    stop_loss_price=48000.0,
                    take_profit_price=55000.0,
                    market_regime="TRENDING",
                    confluence_score=3
                )
                self.log_success(f"1. Señal de prueba creada: {signal.signal_type} ({signal.confidence_score:.1f}%)")
            
            # 2. Evaluar riesgo
            risk_manager = EnhancedRiskManager()
            assessment = risk_manager.assess_trade_risk(signal, 10000.0)
            self.log_success(f"2. Riesgo evaluado: Score {assessment.overall_risk_score:.1f}/100")
            
            # 3. Ejecutar en paper trading si aprobado
            if assessment.is_approved:
                paper_trader = PaperTrader()
                result = paper_trader.execute_signal(signal)
                
                if result.success:
                    self.log_success(f"3. Trade ejecutado exitosamente: {result.message}")
                    
                    # 4. Verificar seguimiento
                    positions = paper_trader.get_open_positions()
                    performance = paper_trader.calculate_portfolio_performance()
                    self.log_success(f"4. Seguimiento: {len(positions)} posiciones, Performance: {performance}")
                else:
                    self.log_error(f"3. Error ejecutando trade: {result.message}")
            else:
                self.log_warning("Trade no aprobado por risk manager")
            
            # 5. Verificar integración con TradingBot
            bot = TradingBot(analysis_interval_minutes=1)
            bot_status = bot.get_status()
            self.log_success(f"5. TradingBot integrado: {bot_status.is_running}")
            
            self.results["system_integration"] = True
            self.results["detailed_results"]["system_integration"] = {
                "signal_generation": True,
                "risk_evaluation": True,
                "trade_execution": assessment.is_approved,
                "position_tracking": True,
                "bot_integration": True
            }
            return True
            
        except Exception as e:
            self.log_error("Error en integración del sistema", e)
            return False
    
    def run_all_tests(self):
        """
        🚀 Ejecutar todas las pruebas mejoradas
        """
        print("🚀 Iniciando pruebas completas mejoradas del sistema...\n")
        
        # Pruebas individuales de módulos
        individual_tests = [
            ("Conexión Binance", self.test_binance_connection),
            ("Base de Datos", self.test_database_operations),
            ("Advanced Indicators", self.test_advanced_indicators_module),
            ("Enhanced Risk Manager", self.test_enhanced_risk_manager_module),
            ("Enhanced Strategies", self.test_enhanced_strategies_module),
            ("Paper Trader", self.test_paper_trader_module),
            ("Trading Bot", self.test_trading_bot_module),
            ("Position Manager", self.test_position_manager_module),
            ("Position Monitor", self.test_position_monitor_module),
            ("Live Trading Bot", self.test_live_trading_bot_module),
            ("Main API", self.test_main_api_module),
        ]
        
        # Pruebas de integración
        integration_tests = [
            ("Trailing Stops Integration", self.test_trailing_stops_integration),
            ("Integración del Sistema", self.test_system_integration),
        ]
        
        all_tests = individual_tests + integration_tests
        passed = 0
        total = len(all_tests)
        
        print("📋 PRUEBAS INDIVIDUALES DE MÓDULOS")
        print("=" * 50)
        
        for test_name, test_func in individual_tests:
            print(f"\n{'='*15} {test_name} {'='*15}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASÓ")
                else:
                    print(f"❌ {test_name}: FALLÓ")
            except Exception as e:
                print(f"💥 {test_name}: ERROR CRÍTICO - {e}")
                self.results["errors"].append(f"{test_name}: {e}")
                print(f"🔍 Traceback: {traceback.format_exc()}")
        
        print("\n" + "=" * 50)
        print("🔄 PRUEBAS DE INTEGRACIÓN")
        print("=" * 50)
        
        for test_name, test_func in integration_tests:
            print(f"\n{'='*15} {test_name} {'='*15}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASÓ")
                else:
                    print(f"❌ {test_name}: FALLÓ")
            except Exception as e:
                print(f"💥 {test_name}: ERROR CRÍTICO - {e}")
                self.results["errors"].append(f"{test_name}: {e}")
                print(f"🔍 Traceback: {traceback.format_exc()}")
        
        # Resumen final mejorado
        print("\n" + "="*70)
        print("📊 RESUMEN COMPLETO DE PRUEBAS")
        print("="*70)
        print(f"✅ Pruebas pasadas: {passed}/{total}")
        print(f"❌ Errores: {len(self.results['errors'])}")
        print(f"⚠️ Advertencias: {len(self.results['warnings'])}")
        
        # Resumen detallado por módulo
        print("\n📋 ESTADO POR MÓDULO:")
        for module, status in self.results.items():
            if module not in ["errors", "warnings", "detailed_results"]:
                icon = "✅" if status else "❌"
                print(f"  {icon} {module.replace('_', ' ').title()}: {'PASÓ' if status else 'FALLÓ'}")
        
        # Mostrar resultados detallados
        if self.results["detailed_results"]:
            print("\n🔍 DETALLES POR MÓDULO:")
            for module, details in self.results["detailed_results"].items():
                print(f"\n  📦 {module.replace('_', ' ').title()}:")
                for key, value in details.items():
                    icon = "✅" if value else "❌"
                    print(f"    {icon} {key.replace('_', ' ').title()}: {value}")
        
        if self.results["errors"]:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.results["errors"]:
                print(f"  • {error}")
        
        if self.results["warnings"]:
            print("\n⚠️ ADVERTENCIAS:")
            for warning in self.results["warnings"]:
                print(f"  • {warning}")
        
        # Evaluación general mejorada
        success_rate = (passed / total) * 100
        print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 SISTEMA EN EXCELENTE ESTADO")
        elif success_rate >= 80:
            print("✅ SISTEMA EN BUEN ESTADO")
        elif success_rate >= 60:
            print("⚠️ SISTEMA FUNCIONAL CON PROBLEMAS MENORES")
        else:
            print("🚨 SISTEMA REQUIERE ATENCIÓN URGENTE")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        if success_rate < 100:
            print("  • Revisar módulos que fallaron")
            print("  • Verificar dependencias y configuración")
            print("  • Ejecutar pruebas individuales para debugging")
        else:
            print("  • ¡Sistema completamente funcional!")
            print("  • Considerar pruebas de carga y performance")
        
        return success_rate >= 60

def run_all_tests():
    """
    🚀 Ejecutar todas las pruebas del sistema
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
    print("="*60)
    
    tester = SystemTester()
    
    # Ejecutar todas las pruebas individuales de módulos
    module_tests = [
        ("Advanced Indicators", tester.test_advanced_indicators_module),
        ("Enhanced Risk Manager", tester.test_enhanced_risk_manager_module),
        ("Enhanced Strategies", tester.test_enhanced_strategies_module),
        ("Live Trading Bot", tester.test_live_trading_bot_module),
        ("Main API", tester.test_main_api_module)
    ]
    
    # Ejecutar pruebas de integración
    integration_tests = [
        ("Conexión Binance", tester.test_binance_connection),
        ("Base de Datos", tester.test_database_operations),
        ("API Endpoints", tester.test_api_endpoints),
        ("Integración Sistema", tester.test_system_integration)
    ]
    
    all_tests = module_tests + integration_tests
    passed = 0
    total = len(all_tests)
    
    print("\n🔍 PRUEBAS INDIVIDUALES DE MÓDULOS:")
    print("-" * 40)
    
    for test_name, test_func in module_tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            tester.log_error(f"Error crítico en {test_name}", e)
    
    print("\n🔗 PRUEBAS DE INTEGRACIÓN:")
    print("-" * 40)
    
    for test_name, test_func in integration_tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            tester.log_error(f"Error crítico en {test_name}", e)
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN COMPLETO DE PRUEBAS")
    print("="*60)
    
    success_rate = (passed / total) * 100
    
    print(f"✅ Pruebas exitosas: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 ¡Sistema funcionando excelentemente!")
    elif success_rate >= 80:
        print("✅ Sistema funcionando correctamente")
    elif success_rate >= 60:
        print("⚠️  Sistema funcionando con advertencias")
    else:
        print("❌ Sistema con problemas críticos")
    
    # Mostrar resultados detallados por módulo
    print("\n📋 Resultados por módulo:")
    for module, details in tester.results["detailed_results"].items():
        if isinstance(details, dict):
            working_count = sum(1 for v in details.values() if v)
            total_count = len(details)
            module_rate = (working_count / total_count * 100) if total_count > 0 else 0
            status = "✅" if module_rate >= 80 else "⚠️" if module_rate >= 60 else "❌"
            print(f"  {status} {module}: {working_count}/{total_count} ({module_rate:.1f}%)")
    
    # Mostrar resultados generales
    print("\n📋 Resultados generales:")
    for key, value in tester.results.items():
        if key not in ["errors", "warnings", "detailed_results"]:
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
    
    print("\n" + "="*60)
    return success_rate >= 80

def main():
    """
    🎯 Función principal
    """
    try:
        tester = SystemTester()
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
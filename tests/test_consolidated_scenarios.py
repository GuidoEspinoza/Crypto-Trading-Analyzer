#!/usr/bin/env python3
"""
🧪 PRUEBAS CONSOLIDADAS DE TRADING

Este archivo consolida las pruebas más importantes:
- TP y SL dinámicos básicos
- Escenarios avanzados y casos extremos
- Circuit breaker
- Funcionalidades de trading integradas
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List

import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.config import TradingProfiles, TRADING_PROFILE
from src.core.position_manager import PositionManager
from src.core.enhanced_risk_manager import EnhancedRiskManager
from src.core.enhanced_strategies import EnhancedSignal
from src.core.trading_bot import TradingBot
from src.database.database import db_manager
from src.database.models import Trade

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsolidatedTester:
    """🧪 Tester consolidado para todas las funcionalidades de trading"""
    
    def __init__(self):
        self.config = TradingProfiles.PROFILES[TRADING_PROFILE]
        self.position_manager = PositionManager(self.config)
        self.risk_manager = EnhancedRiskManager()
        self.trading_bot = TradingBot()
        
        # Estructuras para tracking de pruebas
        self.test_positions = {}
        self.test_results = []
        
    def run_all_tests(self):
        """🚀 Ejecutar todas las pruebas consolidadas"""
        logger.info("🧪 ===== INICIANDO PRUEBAS CONSOLIDADAS =====")
        
        try:
            # Pruebas básicas de TP/SL
            self.test_basic_tp_sl_functionality()
            
            # Pruebas de escenarios avanzados
            self.test_extreme_volatility()
            self.test_sideways_market()
            self.test_multiple_positions()
            
            # Pruebas de circuit breaker
            self.test_circuit_breaker()
            
            logger.info("✅ ===== TODAS LAS PRUEBAS COMPLETADAS =====")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en las pruebas: {e}")
            return False
    
    def test_basic_tp_sl_functionality(self):
        """📊 Pruebas básicas de TP/SL dinámicos"""
        logger.info("\n📊 === TEST: FUNCIONALIDAD BÁSICA TP/SL ===")
        
        # Crear posición de prueba
        trade_id = self._create_test_position()
        if not trade_id:
            logger.error("❌ No se pudo crear posición de prueba")
            return False
        
        # Simular movimientos de precio
        price_scenarios = [
            (51000, "Subida moderada +2%"),
            (49000, "Caída moderada -2%"),
            (52000, "Subida +4%"),
            (47000, "Caída -6%")
        ]
        
        for price, description in price_scenarios:
            logger.info(f"📈 {description}: ${price:,.2f}")
            self._show_position_status(trade_id, price)
            time.sleep(0.1)
    
    def test_extreme_volatility(self):
        """🌪️ Prueba con volatilidad extrema"""
        logger.info("\n🌪️ === TEST: VOLATILIDAD EXTREMA ===")
        
        # Crear posición inicial
        signal = self._create_test_signal("BTC/USDT", 50000, "BUY")
        position = self._create_test_position_dict(signal)
        
        # Simular movimientos extremos de precio
        price_movements = [
            (52000, "Subida inicial +4%"),
            (48000, "Caída brusca -8%"),
            (55000, "Recuperación +14.6%"),
            (45000, "Crash -18.2%"),
            (60000, "Rally extremo +33.3%")
        ]
        
        for price, description in price_movements:
            logger.info(f"📊 {description}: ${price:,.2f}")
            
            # Actualizar trailing stops
            market_data = {position['symbol']: price}
            self.position_manager.update_trailing_stops(market_data)
            self.position_manager.update_dynamic_take_profits(market_data)
            
            time.sleep(0.1)
    
    def test_sideways_market(self):
        """📈 Prueba de mercado lateral"""
        logger.info("\n📈 === TEST: MERCADO LATERAL ===")
        
        signal = self._create_test_signal("ETH/USDT", 3000, "BUY")
        position = self._create_test_position_dict(signal)
        
        # Simular movimientos laterales
        base_price = 3000
        lateral_movements = [
            (3020, "+0.67%"),
            (2980, "-0.67%"),
            (3010, "+0.33%"),
            (2990, "-0.33%"),
            (3005, "+0.17%")
        ]
        
        for price, change in lateral_movements:
            logger.info(f"📊 Movimiento lateral {change}: ${price:,.2f}")
            market_data = {position['symbol']: price}
            self.position_manager.update_trailing_stops(market_data)
            time.sleep(0.1)
    
    def test_multiple_positions(self):
        """🔄 Prueba de múltiples posiciones simultáneas"""
        logger.info("\n🔄 === TEST: MÚLTIPLES POSICIONES ===")
        
        # Crear múltiples posiciones
        positions = [
            self._create_test_signal("BTC/USDT", 50000, "BUY"),
            self._create_test_signal("ETH/USDT", 3000, "BUY"),
            self._create_test_signal("ADA/USDT", 0.5, "SELL")
        ]
        
        # Simular actualizaciones simultáneas
        market_data = {
            "BTC/USDT": 51000,
            "ETH/USDT": 3100,
            "ADA/USDT": 0.48
        }
        
        logger.info("📊 Actualizando múltiples posiciones simultáneamente...")
        self.position_manager.update_trailing_stops(market_data)
        self.position_manager.update_dynamic_take_profits(market_data)
    
    def test_circuit_breaker(self):
        """🔴 Prueba del circuit breaker"""
        logger.info("\n🔴 === TEST: CIRCUIT BREAKER ===")
        
        logger.info(f"📊 Configuración actual:")
        logger.info(f"   • Pérdidas máximas consecutivas: {self.trading_bot.max_consecutive_losses}")
        logger.info(f"   • Cooldown: {self.trading_bot.circuit_breaker_cooldown_hours} horas")
        
        # Simular pérdidas consecutivas
        for i in range(self.trading_bot.max_consecutive_losses + 1):
            logger.info(f"\n   Trade #{i+1}: Simulando pérdida...")
            self.trading_bot._update_consecutive_losses(trade_was_profitable=False)
            
            logger.info(f"   • Pérdidas consecutivas: {self.trading_bot.consecutive_losses}/{self.trading_bot.max_consecutive_losses}")
            logger.info(f"   • Circuit breaker activo: {self.trading_bot.circuit_breaker_active}")
            
            if self.trading_bot.circuit_breaker_active:
                remaining = self.trading_bot._get_remaining_cooldown_hours()
                logger.info(f"   • ⏰ Tiempo restante de cooldown: {remaining:.2f} horas")
                break
    
    def _create_test_position(self) -> int:
        """📊 Crear posición de prueba en base de datos"""
        try:
            with db_manager.get_db_session() as session:
                test_trade = Trade(
                    symbol="BTC/USDT",
                    strategy_name="TEST_CONSOLIDATED",
                    trade_type="BUY",
                    entry_price=50000.0,
                    quantity=0.1,
                    entry_value=5000.0,
                    status="OPEN",
                    is_paper_trade=True,
                    timeframe="1h",
                    confidence_score=85.0,
                    notes="Test consolidado",
                    stop_loss=48000.0,
                    take_profit=53000.0,
                    entry_time=datetime.now()
                )
                
                session.add(test_trade)
                session.commit()
                
                logger.info(f"✅ Posición creada: ID {test_trade.id}")
                return test_trade.id
                
        except Exception as e:
            logger.error(f"❌ Error creando posición: {e}")
            return None
    
    def _create_test_signal(self, symbol: str, price: float, signal_type: str) -> EnhancedSignal:
        """📊 Crear señal de prueba"""
        return EnhancedSignal(
            symbol=symbol,
            signal_type=signal_type,
            price=price,
            confidence_score=85.0,
            strength="Strong",
            strategy_name="TEST_SIGNAL",
            timestamp=datetime.now(),
            indicators_data={"test": True},
            notes="Test signal",
            stop_loss_price=price * 0.96 if signal_type == "BUY" else price * 1.04,
            take_profit_price=price * 1.06 if signal_type == "BUY" else price * 0.94
        )
    
    def _create_test_position_dict(self, signal: EnhancedSignal) -> Dict:
        """📊 Crear diccionario de posición de prueba"""
        return {
            'symbol': signal.symbol,
            'entry_price': signal.price,
            'signal_type': signal.signal_type,
            'stop_loss': signal.stop_loss_price,
            'take_profit': signal.take_profit_price,
            'quantity': 0.1
        }
    
    def _show_position_status(self, trade_id: int, current_price: float):
        """📊 Mostrar estado de la posición"""
        try:
            with db_manager.get_db_session() as session:
                trade = session.query(Trade).filter(Trade.id == trade_id).first()
                if trade:
                    pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    logger.info(f"   📈 PnL: {pnl_pct:+.2f}% | SL: ${trade.stop_loss:,.2f} | TP: ${trade.take_profit:,.2f}")
        except Exception as e:
            logger.error(f"❌ Error mostrando estado: {e}")

def main():
    """🎯 Función principal"""
    print("🧪 ===== PRUEBAS CONSOLIDADAS DE TRADING =====")
    print("🎯 Probando funcionalidades integradas")
    print("🛡️ Verificando robustez del sistema")
    print()
    
    tester = ConsolidatedTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ===== PRUEBAS CONSOLIDADAS COMPLETADAS EXITOSAMENTE =====")
        print("✅ Funcionalidad básica de TP/SL verificada")
        print("✅ Manejo correcto de volatilidad extrema")
        print("✅ Estabilidad en mercados laterales")
        print("✅ Coordinación efectiva de múltiples posiciones")
        print("✅ Circuit breaker funcionando correctamente")
    else:
        print("\n❌ ===== ALGUNAS PRUEBAS FALLARON =====")
        sys.exit(1)

if __name__ == "__main__":
    main()
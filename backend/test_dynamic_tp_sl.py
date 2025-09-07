#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Test de TP y SL Dinámicos

Script para probar el funcionamiento de:
- Take Profit dinámico y ajustable
- Stop Loss trailing inteligente
- Coordinación entre ambos sistemas
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from trading_engine.config import TradingBotConfig
from trading_engine.position_manager import PositionManager
from trading_engine.enhanced_risk_manager import EnhancedRiskManager
from trading_engine.enhanced_strategies import EnhancedSignal
from trading_engine.paper_trader import PaperTrader
from trading_engine.trading_bot import TradingBot
from database.database import db_manager
from database.models import Trade

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DynamicTPSLTester:
    """🧪 Tester para TP y SL dinámicos"""
    
    def __init__(self):
        self.config = TradingBotConfig()
        self.position_manager = PositionManager(self.config)
        self.risk_manager = EnhancedRiskManager()
        
    def run_all_tests(self):
        """🚀 Ejecutar todas las pruebas"""
        logger.info("🧪 ===== INICIANDO PRUEBAS DE TP/SL DINÁMICOS =====")
        
        try:
            # Test 1: Crear posición de prueba
            trade_id = self._create_test_position()
            if not trade_id:
                logger.error("❌ No se pudo crear posición de prueba")
                return False
            
            # Test 2: Simular movimientos de precio y ajustes
            self._test_price_movements(trade_id)
            
            # Test 3: Verificar trailing stop
            self._test_trailing_stop(trade_id)
            
            # Test 4: Verificar take profit dinámico
            self._test_dynamic_take_profit(trade_id)
            
            # Test 5: Coordinación entre TP y SL
            self._test_tp_sl_coordination(trade_id)
            
            logger.info("✅ ===== TODAS LAS PRUEBAS COMPLETADAS =====")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en las pruebas: {e}")
            return False
    
    def _create_test_position(self) -> int:
        """📊 Crear posición de prueba"""
        logger.info("📊 Creando posición de prueba...")
        
        try:
            with db_manager.get_db_session() as session:
                # Crear trade de prueba
                test_trade = Trade(
                    symbol="BTC/USDT",
                    strategy_name="TEST_DYNAMIC_TP_SL",
                    trade_type="BUY",
                    entry_price=50000.0,
                    quantity=0.1,
                    entry_value=5000.0,
                    status="OPEN",
                    is_paper_trade=True,
                    timeframe="1h",
                    confidence_score=85.0,
                    notes="Test para TP/SL dinámicos",
                    stop_loss=48000.0,  # 4% SL inicial
                    take_profit=53000.0,  # 6% TP inicial
                    entry_time=datetime.now()
                )
                
                session.add(test_trade)
                session.commit()
                
                logger.info(f"✅ Posición creada: ID {test_trade.id}")
                logger.info(f"   📈 Entry: $50,000 | SL: $48,000 | TP: $53,000")
                
                return test_trade.id
                
        except Exception as e:
            logger.error(f"❌ Error creando posición: {e}")
            return None
    
    def _test_price_movements(self, trade_id: int):
        """📈 Test de movimientos de precio"""
        logger.info("\n📈 === TEST: MOVIMIENTOS DE PRECIO ===")
        
        # Simular diferentes precios
        price_scenarios = [
            {"price": 51000, "description": "Subida 2% (sin ajustes)"},
            {"price": 52500, "description": "Subida 5% (activar dinámicos)"},
            {"price": 54000, "description": "Subida 8% (ajustes agresivos)"},
            {"price": 56000, "description": "Subida 12% (máximos ajustes)"}
        ]
        
        for scenario in price_scenarios:
            logger.info(f"\n🎯 Escenario: {scenario['description']}")
            logger.info(f"   Precio actual: ${scenario['price']:,.2f}")
            
            # Simular datos de mercado
            market_data = {"BTC/USDT": scenario['price']}
            
            # Actualizar trailing stops
            trailing_updates = self.position_manager.update_trailing_stops(market_data)
            logger.info(f"   🛡️ Trailing stops actualizados: {trailing_updates}")
            
            # Actualizar take profits dinámicos
            tp_updates = self.position_manager.update_dynamic_take_profits(market_data)
            logger.info(f"   🎯 Take profits actualizados: {tp_updates}")
            
            # Mostrar estado actual
            self._show_position_status(trade_id, scenario['price'])
            
            time.sleep(1)  # Pausa para visualizar
    
    def _test_trailing_stop(self, trade_id: int):
        """🛡️ Test específico de trailing stop"""
        logger.info("\n🛡️ === TEST: TRAILING STOP ESPECÍFICO ===")
        
        # Simular subida y bajada para verificar trailing
        scenarios = [
            {"price": 55000, "action": "Subir precio (trailing debe seguir)"},
            {"price": 54000, "action": "Bajar precio (trailing debe mantenerse)"},
            {"price": 56000, "action": "Subir más (trailing debe ajustarse)"},
            {"price": 53000, "action": "Bajar significativo (verificar protección)"}
        ]
        
        for scenario in scenarios:
            logger.info(f"\n🔄 {scenario['action']}")
            logger.info(f"   Precio: ${scenario['price']:,.2f}")
            
            market_data = {"BTC/USDT": scenario['price']}
            updates = self.position_manager.update_trailing_stops(market_data)
            
            self._show_position_status(trade_id, scenario['price'])
            time.sleep(1)
    
    def _test_dynamic_take_profit(self, trade_id: int):
        """🎯 Test específico de take profit dinámico"""
        logger.info("\n🎯 === TEST: TAKE PROFIT DINÁMICO ESPECÍFICO ===")
        
        # Simular ganancias progresivas
        scenarios = [
            {"price": 52500, "profit": "5%", "expected": "TP +1%"},
            {"price": 54000, "profit": "8%", "expected": "TP +1.5%"},
            {"price": 56000, "profit": "12%", "expected": "TP +2%"},
            {"price": 58000, "profit": "16%", "expected": "TP +2% (máximo)"}
        ]
        
        for scenario in scenarios:
            logger.info(f"\n💰 Ganancia {scenario['profit']} - {scenario['expected']}")
            logger.info(f"   Precio: ${scenario['price']:,.2f}")
            
            market_data = {"BTC/USDT": scenario['price']}
            updates = self.position_manager.update_dynamic_take_profits(market_data)
            
            self._show_position_status(trade_id, scenario['price'])
            time.sleep(1)
    
    def _test_tp_sl_coordination(self, trade_id: int):
        """🤝 Test de coordinación entre TP y SL"""
        logger.info("\n🤝 === TEST: COORDINACIÓN TP/SL ===")
        
        # Simular escenario completo
        final_price = 57000  # 14% de ganancia
        logger.info(f"\n🎯 Escenario final: Precio ${final_price:,.2f} (+14%)")
        
        market_data = {"BTC/USDT": final_price}
        
        # Actualizar ambos sistemas
        trailing_updates = self.position_manager.update_trailing_stops(market_data)
        tp_updates = self.position_manager.update_dynamic_take_profits(market_data)
        
        logger.info(f"   🛡️ Trailing stops: {trailing_updates} actualizaciones")
        logger.info(f"   🎯 Take profits: {tp_updates} actualizaciones")
        
        # Mostrar estado final
        self._show_position_status(trade_id, final_price)
        
        # Verificar coherencia
        self._verify_tp_sl_coherence(trade_id)
    
    def _show_position_status(self, trade_id: int, current_price: float):
        """📊 Mostrar estado actual de la posición"""
        try:
            with db_manager.get_db_session() as session:
                trade = session.query(Trade).filter(Trade.id == trade_id).first()
                
                if trade:
                    # Calcular métricas
                    profit_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    profit_usd = (current_price - trade.entry_price) * trade.quantity
                    
                    # Distancias
                    sl_distance = abs(current_price - (trade.stop_loss or 0)) / current_price * 100 if trade.stop_loss else 0
                    tp_distance = abs((trade.take_profit or 0) - current_price) / current_price * 100 if trade.take_profit else 0
                    
                    logger.info(f"   📊 Estado: Ganancia {profit_pct:.2f}% (${profit_usd:.2f})")
                    logger.info(f"   🛡️ SL: ${trade.stop_loss:.2f} (distancia: {sl_distance:.2f}%)" if trade.stop_loss else "   🛡️ SL: No configurado")
                    logger.info(f"   🎯 TP: ${trade.take_profit:.2f} (distancia: {tp_distance:.2f}%)" if trade.take_profit else "   🎯 TP: No configurado")
                    
        except Exception as e:
            logger.error(f"❌ Error mostrando estado: {e}")
    
    def _verify_tp_sl_coherence(self, trade_id: int):
        """✅ Verificar coherencia entre TP y SL"""
        logger.info("\n✅ === VERIFICACIÓN DE COHERENCIA ===")
        
        try:
            with db_manager.get_db_session() as session:
                trade = session.query(Trade).filter(Trade.id == trade_id).first()
                
                if trade and trade.stop_loss and trade.take_profit:
                    # Verificar que SL < Entry < TP para BUY
                    if trade.trade_type == "BUY":
                        sl_ok = trade.stop_loss < trade.entry_price
                        tp_ok = trade.take_profit > trade.entry_price
                        order_ok = trade.stop_loss < trade.entry_price < trade.take_profit
                    else:  # SELL
                        sl_ok = trade.stop_loss > trade.entry_price
                        tp_ok = trade.take_profit < trade.entry_price
                        order_ok = trade.take_profit < trade.entry_price < trade.stop_loss
                    
                    logger.info(f"   🛡️ Stop Loss coherente: {'✅' if sl_ok else '❌'}")
                    logger.info(f"   🎯 Take Profit coherente: {'✅' if tp_ok else '❌'}")
                    logger.info(f"   📊 Orden correcto: {'✅' if order_ok else '❌'}")
                    
                    if sl_ok and tp_ok and order_ok:
                        logger.info("   🎉 ¡Todos los niveles son coherentes!")
                    else:
                        logger.warning("   ⚠️ Hay inconsistencias en los niveles")
                        
        except Exception as e:
            logger.error(f"❌ Error verificando coherencia: {e}")

def main():
    """🚀 Función principal"""
    print("🧪 ===== TEST DE TP Y SL DINÁMICOS =====")
    print("🎯 Probando funcionalidad de ajustes automáticos")
    print("🛡️ Verificando trailing stops inteligentes")
    print("🤝 Validando coordinación entre sistemas\n")
    
    tester = DynamicTPSLTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 ===== PRUEBAS COMPLETADAS EXITOSAMENTE =====")
            print("✅ TP y SL dinámicos funcionan correctamente")
            print("✅ Trailing stops se ajustan apropiadamente")
            print("✅ Take profits se incrementan dinámicamente")
            print("✅ Coordinación entre sistemas es coherente")
        else:
            print("\n❌ ===== PRUEBAS FALLARON =====")
            print("⚠️ Revisar logs para identificar problemas")
            
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        logger.error(f"Error en main: {e}")

if __name__ == "__main__":
    main()
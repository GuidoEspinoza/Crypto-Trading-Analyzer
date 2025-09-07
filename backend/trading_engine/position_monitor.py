"""📊 Position Monitor - Monitoreo de Posiciones en Tiempo Real

Este módulo implementa:
- Monitoreo continuo de precios para posiciones activas
- Coordinación con PositionManager para gestión centralizada
- Ejecución automática de Take Profit y Stop Loss
- Trailing stops dinámicos
- Gestión de riesgo en tiempo real
- Notificaciones de cambios importantes
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from sqlalchemy.orm import Session

# Importaciones locales
from .config import TradingBotConfig, RiskManagerConfig
from database.database import db_manager
from database.models import Trade
from .enhanced_strategies import TradingSignal
from .paper_trader import PaperTrader, TradeResult
from .position_manager import PositionManager, PositionInfo

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class PositionStatus:
    """📊 Estado actual de una posición"""
    trade_id: int
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    stop_loss: Optional[float]  # Puede ser None
    take_profit: Optional[float]  # Puede ser None
    trailing_stop: Optional[float]
    unrealized_pnl: float
    unrealized_pnl_percentage: float
    should_close: bool
    close_reason: str
    trade_type: str  # BUY o SELL

class PositionMonitor:
    """📊 Monitor de Posiciones en Tiempo Real
    
    Características:
    - Monitoreo continuo de precios
    - Coordinación con PositionManager
    - Ejecución automática de TP/SL
    - Trailing stops dinámicos
    - Gestión de riesgo en tiempo real
    """
    
    def __init__(self, price_fetcher: Callable[[str], float], paper_trader=None):
        """
        Inicializar el monitor de posiciones
        
        Args:
            price_fetcher: Función para obtener precios actuales
            paper_trader: Instancia del paper trader para ejecutar órdenes
        """
        self.price_fetcher = price_fetcher
        self.paper_trader = paper_trader
        self.config = TradingBotConfig()
        self.risk_config = RiskManagerConfig()
        
        # Inicializar PositionManager
        self.position_manager = PositionManager(paper_trader)
        
        # Control de threading
        self.monitoring_active = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        # Cache de precios para optimización
        self.price_cache = {}
        self.last_price_update = {}
        
        # Configuración de monitoreo desde TradingBotConfig
        self.monitor_interval = self.config.get_live_update_interval()  # segundos entre checks
        self.price_cache_duration = 30  # segundos de validez del cache
        
        # Inicializar estadísticas del monitor
        self.stats = {
            "tp_executed": 0,
            "sl_executed": 0,
            "positions_monitored": 0,
            "monitoring_cycles": 0
        }
        
        logger.info("📊 Position Monitor initialized with PositionManager")
    
    def start_monitoring(self):
        """🚀 Iniciar monitoreo de posiciones"""
        if self.monitoring_active:
            logger.warning("⚠️ Position monitoring already active")
            return
        
        self.monitoring_active = True
        self.stop_event.clear()
        
        # Iniciar thread de monitoreo
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="PositionMonitor"
        )
        self.monitor_thread.start()
        
        logger.info("🚀 Position monitoring started")
    
    def stop_monitoring(self):
        """🛑 Detener monitoreo de posiciones"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("🛑 Position monitoring stopped")
    
    def _monitoring_loop(self):
        """🔄 Loop principal de monitoreo"""
        logger.info("📊 Starting position monitoring loop")
        
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                # Obtener posiciones activas del PositionManager
                active_positions = self.position_manager.get_active_positions()
                
                if not active_positions:
                    # No hay posiciones, esperar más tiempo
                    time.sleep(self.monitor_interval * 2)
                    continue
                
                logger.debug(f"📊 Monitoring {len(active_positions)} active positions")
                
                # Recopilar precios actuales para todas las posiciones
                market_data = {}
                for position in active_positions:
                    current_price = self._get_current_price(position.symbol)
                    if current_price is not None:
                        market_data[position.symbol] = current_price
                
                # Actualizar trailing stops dinámicos
                if market_data:
                    try:
                        updated_count = self.position_manager.update_trailing_stops(market_data)
                        if updated_count > 0:
                            logger.debug(f"🎯 Updated {updated_count} trailing stops")
                    except Exception as e:
                        logger.error(f"❌ Error updating trailing stops: {e}")
                    
                    # Actualizar take profits dinámicos
                    try:
                        updated_tp_count = self.position_manager.update_dynamic_take_profits(market_data)
                        if updated_tp_count > 0:
                            logger.debug(f"🎯 Updated {updated_tp_count} dynamic take profits")
                    except Exception as e:
                        logger.error(f"❌ Error updating dynamic take profits: {e}")
                
                # Procesar cada posición
                for position in active_positions:
                    if self.stop_event.is_set():
                        break
                    
                    try:
                        self._monitor_position(position)
                    except Exception as e:
                        logger.error(f"❌ Error monitoring position {position.trade_id}: {e}")
                
                # Esperar antes del siguiente ciclo
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
        
        logger.info("📊 Position monitoring loop ended")
    
    def _get_open_positions(self) -> List[Dict]:
        """📊 Obtener posiciones abiertas de la base de datos"""
        try:
            with db_manager.get_db_session() as session:
                # Obtener todas las posiciones abiertas, incluso sin SL/TP
                open_trades = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                return [
                    {
                        "id": trade.id,
                        "symbol": trade.symbol,
                        "trade_type": trade.trade_type,
                        "entry_price": trade.entry_price,
                        "quantity": trade.quantity,
                        "stop_loss": trade.stop_loss,
                        "take_profit": trade.take_profit,
                        "entry_time": trade.entry_time,
                        "strategy_name": trade.strategy_name
                    }
                    for trade in open_trades
                ]
        except Exception as e:
            logger.error(f"❌ Error getting open positions: {e}")
            return []
    
    def _monitor_position(self, position: PositionInfo):
        """🔄 Monitorear una posición individual"""
        symbol = position.symbol
        trade_id = position.trade_id
        
        # Obtener precio actual
        current_price = self._get_current_price(symbol)
        if current_price is None:
            logger.warning(f"⚠️ Could not get price for {symbol}")
            return
        
        # Actualizar precio en PositionManager
        self.position_manager.update_position_price(trade_id, current_price)
        
        # Verificar condiciones de cierre
        close_reason = self.position_manager.check_exit_conditions(position)
        
        if close_reason:
            logger.info(
                f"🎯 Position {trade_id} ({symbol}) should close: {close_reason} "
                f"| Current: ${current_price:.4f} | Entry: ${position.entry_price:.4f}"
            )
            
            # Ejecutar cierre usando PositionManager
            success = self.position_manager.close_position(trade_id, current_price, close_reason)
            
            if success:
                logger.info(f"✅ Position {trade_id} closed successfully")
                # Actualizar estadísticas del monitor
                if close_reason == "TAKE_PROFIT":
                    self.stats["tp_executed"] += 1
                elif close_reason in ["STOP_LOSS", "TRAILING_STOP"]:
                    self.stats["sl_executed"] += 1
            else:
                logger.error(f"❌ Failed to close position {trade_id}")
        else:
            # Log de estado (solo cada minuto para evitar spam)
            if trade_id not in getattr(self, '_last_log_time', {}) or \
               time.time() - getattr(self, '_last_log_time', {}).get(trade_id, 0) > 60:
                
                if not hasattr(self, '_last_log_time'):
                    self._last_log_time = {}
                self._last_log_time[trade_id] = time.time()
                
                pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                if position.trade_type == "SELL":
                    pnl_pct = -pnl_pct
                
                # Formatear SL y TP manejando valores None
                sl_str = f"${position.stop_loss:.4f}" if position.stop_loss is not None else "N/A"
                tp_str = f"${position.take_profit:.4f}" if position.take_profit is not None else "N/A"
                
                logger.debug(
                    f"📊 Position {trade_id} ({symbol}): ${current_price:.4f} "
                    f"| PnL: {pnl_pct:.2f}% "
                    f"| SL: {sl_str} | TP: {tp_str}"
                )
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """💰 Obtener precio actual con cache"""
        now = time.time()
        
        # Verificar cache
        if symbol in self.price_cache and symbol in self.last_price_update:
            if now - self.last_price_update[symbol] < self.price_cache_duration:
                return self.price_cache[symbol]
        
        # Obtener precio fresco
        try:
            price = self.price_fetcher(symbol)
            if price and price > 0:
                self.price_cache[symbol] = price
                self.last_price_update[symbol] = now
                return price
        except Exception as e:
            logger.error(f"❌ Error fetching price for {symbol}: {e}")
        
        return None
    
    def _create_position_status(self, position: Dict, current_price: float) -> PositionStatus:
        """📊 Crear estado actual de la posición"""
        entry_price = position["entry_price"]
        quantity = position["quantity"]
        stop_loss = position.get("stop_loss")  # Puede ser None
        take_profit = position.get("take_profit")  # Puede ser None
        trade_type = position["trade_type"]
        
        # Calcular PnL
        if trade_type == "BUY":
            unrealized_pnl = (current_price - entry_price) * quantity
            unrealized_pnl_percentage = ((current_price - entry_price) / entry_price) * 100
            
            # Verificar condiciones de cierre para BUY
            should_close = False
            close_reason = ""
            
            if stop_loss is not None and current_price <= stop_loss:
                should_close = True
                close_reason = "STOP_LOSS"
            elif take_profit is not None and current_price >= take_profit:
                should_close = True
                close_reason = "TAKE_PROFIT"
                
        else:  # SELL
            unrealized_pnl = (entry_price - current_price) * quantity
            unrealized_pnl_percentage = ((entry_price - current_price) / entry_price) * 100
            
            # Verificar condiciones de cierre para SELL
            should_close = False
            close_reason = ""
            
            if stop_loss is not None and current_price >= stop_loss:
                should_close = True
                close_reason = "STOP_LOSS"
            elif take_profit is not None and current_price <= take_profit:
                should_close = True
                close_reason = "TAKE_PROFIT"
        
        return PositionStatus(
            trade_id=position["id"],
            symbol=position["symbol"],
            entry_price=entry_price,
            current_price=current_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_stop=None,  # TODO: Implementar trailing stop
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_percentage=unrealized_pnl_percentage,
            should_close=should_close,
            close_reason=close_reason,
            trade_type=trade_type
        )
    
    def _execute_position_close(self, status: PositionStatus):
        """🎯 Ejecutar cierre de posición"""
        if not self.paper_trader:
            logger.error("❌ No paper trader available for position close")
            return
        
        try:
            # Crear señal de cierre
            close_signal = TradingSignal(
                symbol=status.symbol,
                signal_type="SELL" if status.trade_type == "BUY" else "BUY",
                price=status.current_price,
                confidence=100.0,  # Cierre automático = 100% confianza
                timeframe="1h",
                strategy_name="AUTO_CLOSE",
                indicators={"reason": status.close_reason},
                stop_loss=0,  # No necesario para cierre
                take_profit=0,  # No necesario para cierre
                notes=f"Auto close: {status.close_reason} | PnL: {status.unrealized_pnl_percentage:.2f}%"
            )
            
            # Ejecutar cierre
            result = self.paper_trader.execute_signal(close_signal)
            
            if result.success:
                logger.info(
                    f"✅ Position {status.trade_id} closed successfully: {status.close_reason} "
                    f"| PnL: {status.unrealized_pnl_percentage:.2f}% | Price: ${status.current_price:.4f}"
                )
                
                # Actualizar trade en base de datos
                self._update_closed_trade(status)
            else:
                logger.error(f"❌ Failed to close position {status.trade_id}: {result.message}")
                
        except Exception as e:
            logger.error(f"❌ Error executing position close for {status.trade_id}: {e}")
    
    def _update_closed_trade(self, status: PositionStatus):
        """📝 Actualizar trade cerrado en base de datos"""
        try:
            with db_manager.get_db_session() as session:
                trade = session.query(Trade).filter(Trade.id == status.trade_id).first()
                if trade:
                    trade.exit_price = status.current_price
                    trade.exit_value = status.current_price * status.quantity
                    trade.pnl = status.unrealized_pnl
                    trade.pnl_percentage = status.unrealized_pnl_percentage
                    trade.status = "CLOSED"
                    trade.exit_time = datetime.now()
                    trade.notes = f"{trade.notes or ''} | Auto closed: {status.close_reason}"
                    
                    session.commit()
                    logger.debug(f"📝 Trade {status.trade_id} updated in database")
                    
        except Exception as e:
            logger.error(f"❌ Error updating closed trade {status.trade_id}: {e}")
    
    def _update_trailing_stop(self, status: PositionStatus):
        """📈 Actualizar trailing stop (implementación futura)"""
        # TODO: Implementar trailing stops dinámicos
        pass
    
    def get_monitoring_status(self) -> Dict:
        """📊 Obtener estado del monitoreo"""
        # Obtener estadísticas del PositionManager
        position_stats = self.position_manager.get_statistics()
        
        return {
            "monitoring_active": self.monitoring_active,
            "monitor_interval": self.monitor_interval,
            "price_cache_size": len(self.price_cache),
            "last_update": max(self.last_price_update.values()) if self.last_price_update else None,
            
            # Estadísticas del PositionManager
            "active_positions": position_stats["active_positions"],
            "positions_managed": position_stats["positions_managed"],
            "take_profits_executed": position_stats["take_profits_executed"],
            "stop_losses_executed": position_stats["stop_losses_executed"],
            "trailing_stops_activated": position_stats["trailing_stops_activated"],
            "total_realized_pnl": position_stats["total_realized_pnl"]
        }
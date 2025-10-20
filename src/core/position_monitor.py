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
from src.config.main_config import TradingBotConfig, RiskManagerConfig, TradingProfiles, CacheConfig
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
        
        # Control de trades ya procesados para evitar intentos repetitivos
        self.processed_trades = set()  # Set de trade_ids ya procesados para cierre
        self.failed_close_attempts = {}  # Dict para contar intentos fallidos por trade_id
        profile = TradingProfiles.get_current_profile()
        self.max_close_attempts = profile.get('max_close_attempts', 3)  # Máximo número de intentos antes de marcar como procesado
        
        # Configuración de monitoreo desde TradingBotConfig
        self.monitor_interval = TradingBotConfig.get_monitoring_interval()  # segundos entre checks
        self.price_cache_duration = CacheConfig.get_ttl_for_operation("price_data")  # segundos de validez del cache
        
        # Inicializar estadísticas del monitor
        self.stats = {
            "tp_executed": 0,
            "sl_executed": 0,
            "positions_monitored": 0,
            "monitoring_cycles": 0
        }
        
        logger.info("📊 Position Monitor initialized with PositionManager")
    
    def _cleanup_processed_trades(self):
        """🧹 Limpiar trades procesados que ya no están en posiciones activas"""
        try:
            # Obtener IDs de posiciones activas actuales
            active_positions = self.position_manager.get_active_positions(refresh_cache=True)
            active_trade_ids = {pos.trade_id for pos in active_positions}
            
            # Remover trades procesados que ya no están activos
            processed_to_remove = self.processed_trades - active_trade_ids
            self.processed_trades -= processed_to_remove
            
            # Limpiar intentos fallidos de trades que ya no están activos
            failed_to_remove = set(self.failed_close_attempts.keys()) - active_trade_ids
            for trade_id in failed_to_remove:
                del self.failed_close_attempts[trade_id]
            
            if processed_to_remove or failed_to_remove:
                logger.debug(
                    f"🧹 Cleaned {len(processed_to_remove)} processed trades and "
                    f"{len(failed_to_remove)} failed attempts"
                )
                
        except Exception as e:
            logger.error(f"❌ Error cleaning processed trades: {e}")
    
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
            profile = TradingProfiles.get_current_profile()
            from src.config.main_config import TradingBotConfig
            timeout = TradingBotConfig.get_thread_join_timeout()
            self.monitor_thread.join(timeout=timeout)
        
        logger.info("🛑 Position monitoring stopped")
    
    def _monitoring_loop(self):
        """🔄 Loop principal de monitoreo"""
        logger.info("📊 Starting position monitoring loop")
        
        cleanup_counter = 0
        profile = TradingProfiles.get_current_profile()
        from src.config.main_config import TradingBotConfig
        cleanup_interval = TradingBotConfig.get_cleanup_interval()  # Limpiar cada N ciclos
        
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                # Incrementar contador de ciclos
                self.stats["monitoring_cycles"] += 1
                cleanup_counter += 1
                
                # Limpiar trades procesados periódicamente
                if cleanup_counter >= cleanup_interval:
                    self._cleanup_processed_trades()
                    cleanup_counter = 0
                
                # Obtener posiciones activas del PositionManager (refrescar cache)
                active_positions = self.position_manager.get_active_positions(refresh_cache=True)
                
                if not active_positions:
                    # No hay posiciones, esperar más tiempo
                    time.sleep(self.monitor_interval * 2)
                    continue
                
                logger.debug(f"📊 Monitoring {len(active_positions)} active positions")
                
                # Recopilar precios actuales para todas las posiciones
                market_data = {}
                for position in active_positions:
                    try:
                        current_price = self._get_current_price(position.symbol)
                        market_data[position.symbol] = current_price
                    except ValueError as e:
                        logger.warning(f"⚠️ No se pudo obtener precio para {position.symbol}: {e}")
                        # Continuar con otras posiciones
                        continue
                    except Exception as e:
                        logger.error(f"🚨 Error inesperado obteniendo precio para {position.symbol}: {e}")
                        continue
                
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
        """📊 Obtener posiciones abiertas directamente de Capital.com"""
        try:
            # Usar PositionManager que ya maneja Capital.com
            active_positions = self.position_manager.get_active_positions(refresh_cache=True)
            
            return [
                {
                    "id": pos.trade_id,
                    "symbol": pos.symbol,
                    "trade_type": pos.trade_type,
                    "entry_price": pos.entry_price,
                    "quantity": pos.quantity,
                    "stop_loss": pos.stop_loss,
                    "take_profit": pos.take_profit,
                    "entry_time": pos.entry_time,
                    "strategy_name": getattr(pos, 'strategy_name', 'Unknown')
                }
                for pos in active_positions
            ]
        except Exception as e:
            logger.error(f"❌ Error getting open positions from Capital.com: {e}")
            return []
    
    def _monitor_position(self, position: PositionInfo):
        """🔄 Monitorear una posición individual"""
        symbol = position.symbol
        trade_id = position.trade_id
        
        # Verificar si este trade ya fue procesado para cierre
        if trade_id in self.processed_trades:
            return
        
        # Obtener precio actual
        try:
            current_price = self._get_current_price(symbol)
        except ValueError as e:
            logger.warning(f"⚠️ No se pudo obtener precio para {symbol}: {e}")
            return
        except Exception as e:
            logger.error(f"🚨 Error inesperado obteniendo precio para {symbol}: {e}")
            return
        
        # Actualizar precio en PositionManager
        self.position_manager.update_position_price(trade_id, current_price)
        
        # Verificar condiciones de cierre
        close_reason = self.position_manager.check_exit_conditions(position)
        
        if close_reason:
            # Verificar si ya hemos intentado cerrar este trade demasiadas veces
            if trade_id in self.failed_close_attempts:
                if self.failed_close_attempts[trade_id] >= self.max_close_attempts:
                    logger.warning(
                        f"⚠️ Trade {trade_id} marked as processed after {self.max_close_attempts} failed attempts"
                    )
                    self.processed_trades.add(trade_id)
                    return
            
            logger.info(
                f"🎯 Position {trade_id} ({symbol}) should close: {close_reason} "
                f"| Current: ${current_price:.4f} | Entry: ${position.entry_price:.4f}"
            )
            
            # Ejecutar cierre usando PositionManager
            success = self.position_manager.close_position(trade_id, current_price, close_reason)
            
            if success:
                logger.info(f"✅ Position {trade_id} closed successfully")
                # Marcar como procesado exitosamente
                self.processed_trades.add(trade_id)
                # Limpiar contador de intentos fallidos si existía
                if trade_id in self.failed_close_attempts:
                    del self.failed_close_attempts[trade_id]
                
                # Actualizar estadísticas del monitor
                if close_reason == "TAKE_PROFIT":
                    self.stats["tp_executed"] += 1
                elif close_reason in ["STOP_LOSS", "TRAILING_STOP"]:
                    self.stats["sl_executed"] += 1
            else:
                # Incrementar contador de intentos fallidos
                if trade_id not in self.failed_close_attempts:
                    self.failed_close_attempts[trade_id] = 0
                self.failed_close_attempts[trade_id] += 1
                
                logger.error(
                    f"❌ Failed to close position {trade_id} "
                    f"(attempt {self.failed_close_attempts[trade_id]}/{self.max_close_attempts})"
                )
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
            trailing_stop=self._calculate_trailing_stop(position, current_price),
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
        """📝 Registrar cierre de trade (información disponible en Capital.com)"""
        try:
            # El historial de trades se puede consultar directamente en Capital.com
            # No necesitamos mantener una base de datos local
            logger.info(f"📝 Trade {status.trade_id} closed: {status.close_reason}")
            logger.info(f"💰 Final PnL: {status.unrealized_pnl:.2f} ({status.unrealized_pnl_percentage:.2f}%)")
                    
        except Exception as e:
            logger.error(f"❌ Error updating closed trade {status.trade_id}: {e}")
    
    def get_monitor_stats(self) -> Dict:
        """📊 Obtener estadísticas del monitor
        
        Returns:
            Diccionario con estadísticas del monitor
        """
        return {
            "monitoring_active": self.monitoring_active,
            "monitoring_cycles": self.stats["monitoring_cycles"],
            "tp_executed": self.stats["tp_executed"],
            "sl_executed": self.stats["sl_executed"],
            "positions_monitored": self.stats["positions_monitored"],
            "processed_trades_count": len(self.processed_trades),
            "failed_attempts_count": len(self.failed_close_attempts),
            "processed_trades": list(self.processed_trades),
            "failed_attempts": dict(self.failed_close_attempts),
            "max_close_attempts": self.max_close_attempts
        }
    
    def reset_processed_trades(self):
        """🔄 Resetear lista de trades procesados (para debugging)"""
        logger.info(f"🔄 Resetting {len(self.processed_trades)} processed trades")
        self.processed_trades.clear()
        self.failed_close_attempts.clear()
        logger.info("✅ Processed trades reset completed")
    
    def _calculate_trailing_stop(self, position: Dict, current_price: float) -> Optional[float]:
        """📈 Calcular trailing stop dinámico"""
        try:
            entry_price = position["entry_price"]
            trade_type = position["trade_type"]
            
            # Configuración de trailing stop desde perfil (decimal)
            trailing_distance = TradingProfiles.get_current_profile()["default_trailing_distance"]
            
            if trade_type == "BUY":
                # Para posiciones largas, trailing stop se mueve hacia arriba
                trailing_stop = current_price * (1 - trailing_distance)
                # Solo actualizar si es mayor que el stop loss actual
                current_sl = position.get("stop_loss")
                if current_sl is None or trailing_stop > current_sl:
                    return trailing_stop
            else:  # SELL
                # Para posiciones cortas, trailing stop se mueve hacia abajo
                trailing_stop = current_price * (1 + trailing_distance)
                # Solo actualizar si es menor que el stop loss actual
                current_sl = position.get("stop_loss")
                if current_sl is None or trailing_stop < current_sl:
                    return trailing_stop
            
            return None
        except Exception as e:
            logger.error(f"❌ Error calculando trailing stop: {e}")
            return None
    
    def _update_trailing_stop(self, status: PositionStatus):
        """📈 Actualizar trailing stop dinámico"""
        try:
            position_dict = {
                "entry_price": status.entry_price,
                "trade_type": status.trade_type,
                "stop_loss": status.stop_loss
            }
            
            trailing_stop = self._calculate_trailing_stop(position_dict, status.current_price)
            if trailing_stop:
                # Actualizar el trailing stop usando PositionManager
                success = self.position_manager.update_position_stop_loss(status.trade_id, trailing_stop)
                if success:
                    logger.info(f"📈 Trailing stop actualizado para {status.symbol}: ${trailing_stop:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando trailing stop: {e}")
    
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
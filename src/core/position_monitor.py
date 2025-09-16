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
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from collections import defaultdict
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importaciones locales
from src.config.config_manager import ConfigManager

# Inicializar configuración centralizada
try:
    config_manager = ConfigManager()
    config = config_manager.get_consolidated_config()
    if config is None:
        config = {}
except Exception as e:
    # Configuración de fallback en caso de error
    config = {}
from ..database.database import db_manager
from ..database.models import Trade
from .enhanced_strategies import TradingSignal
from .paper_trader import PaperTrader, TradeResult
from .position_manager import PositionManager, PositionInfo

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """📦 Entrada de cache con TTL"""
    value: float
    timestamp: datetime
    ttl_seconds: int = 30
    
    def is_expired(self) -> bool:
        """Verificar si la entrada ha expirado"""
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl_seconds

@dataclass
class PositionStatus:
    """📊 Estado de una posición"""
    trade_id: int
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
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
        
        # Inicializar PositionManager
        self.position_manager = PositionManager(paper_trader)
        
        # Control de threading mejorado
        self.monitoring_active = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self._monitor_lock = threading.Lock()  # Lock para operaciones de monitoreo
        
        # Cache inteligente de precios con TTL
        self.price_cache: Dict[str, CacheEntry] = {}
        self._cache_lock = threading.RLock()  # Lock para acceso seguro al cache
        
        # Pool de threads para procesamiento paralelo
        self._thread_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="PositionMonitor")
        
        # Control de trades procesados con optimización de memoria
        self.processed_trades = set()  # Set de trade_ids ya procesados para cierre
        self.failed_close_attempts = defaultdict(int)  # Dict para contar intentos fallidos por trade_id
        # Obtener configuración desde el perfil de trading
        from ..config.config import PaperTraderConfig
        self.max_close_attempts = PaperTraderConfig.get_max_close_attempts()  # Máximo número de intentos antes de marcar como procesado
        
        # Configuración de monitoreo optimizada
        self.monitor_interval = config.get("trading_bot", {}).get("live_update_interval", 30)  # segundos entre checks (default 30)
        self.price_cache_duration = PaperTraderConfig.get_price_cache_duration()  # segundos de validez del cache
        self.cache_cleanup_interval = 300  # 5 minutos
        self._last_cache_cleanup = datetime.now()
        self.log_interval = PaperTraderConfig.get_position_log_interval()  # segundos entre logs de estado
        self.idle_sleep_multiplier = PaperTraderConfig.get_idle_sleep_multiplier()  # multiplicador para sleep cuando no hay posiciones
        
        # Estadísticas thread-safe del monitor
        self.stats = {
            "tp_executed": 0,
            "sl_executed": 0,
            "positions_monitored": 0,
            "monitoring_cycles": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        self._stats_lock = threading.Lock()
        
        # Registro de callbacks para cleanup
        self._cleanup_callbacks: List[Callable] = []
        
        logger.info("📊 Position Monitor initialized with enhanced threading and caching")
    
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
        """🛑 Detener monitoreo de posiciones con cleanup completo"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            timeout = config.get("trading_bot", {}).get("thread_join_timeout", 30)
            self.monitor_thread.join(timeout=timeout)
        
        # Cleanup del thread pool
        try:
            self._thread_pool.shutdown(wait=True, timeout=10)
        except Exception as e:
            logger.warning(f"⚠️ Error shutting down thread pool: {e}")
        
        # Ejecutar callbacks de cleanup
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.warning(f"⚠️ Error in cleanup callback: {e}")
        
        # Limpiar cache
        with self._cache_lock:
            self.price_cache.clear()
        
        logger.info("🛑 Position monitoring stopped with complete cleanup")
    
    def _monitoring_loop(self):
        """🔄 Loop principal de monitoreo"""
        logger.info("📊 Starting position monitoring loop")
        
        cleanup_counter = 0
        cleanup_interval = config.get("trading_bot", {}).get("cleanup_interval", 100)  # Limpiar cada N ciclos
        
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                # Incrementar contador de ciclos thread-safe
                with self._stats_lock:
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
                    time.sleep(self.monitor_interval * self.idle_sleep_multiplier)
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
    
    def _cleanup_expired_cache(self):
        """🧹 Limpiar entradas expiradas del cache"""
        now = datetime.now()
        
        # Solo hacer cleanup cada cierto intervalo
        if (now - self._last_cache_cleanup).total_seconds() < self.cache_cleanup_interval:
            return
        
        with self._cache_lock:
            expired_keys = [
                symbol for symbol, entry in self.price_cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.price_cache[key]
            
            if expired_keys:
                logger.debug(f"🧹 Cleaned {len(expired_keys)} expired cache entries")
        
        self._last_cache_cleanup = now
    
    def add_cleanup_callback(self, callback: Callable):
        """➕ Agregar callback para cleanup"""
        self._cleanup_callbacks.append(callback)
    
    def get_cache_info(self) -> Dict:
        """📊 Obtener información del cache"""
        with self._cache_lock:
            cache_info = {
                "size": len(self.price_cache),
                "entries": {
                    symbol: {
                        "value": entry.value,
                        "timestamp": entry.timestamp.isoformat(),
                        "ttl_seconds": entry.ttl_seconds,
                        "expired": entry.is_expired()
                    }
                    for symbol, entry in self.price_cache.items()
                }
            }
        
        return cache_info
    
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
        
        # Verificar si este trade ya fue procesado para cierre
        if trade_id in self.processed_trades:
            return
        
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
                
                # Actualizar estadísticas del monitor thread-safe
                with self._stats_lock:
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
            # Log de estado (configurable para evitar spam)
            if trade_id not in getattr(self, '_last_log_time', {}) or \
               time.time() - getattr(self, '_last_log_time', {}).get(trade_id, 0) > self.log_interval:
                
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
        """💰 Obtener precio actual con cache inteligente y TTL"""
        now = datetime.now()
        
        # Verificar cache con lock thread-safe
        with self._cache_lock:
            if symbol in self.price_cache:
                cache_entry = self.price_cache[symbol]
                if not cache_entry.is_expired():
                    with self._stats_lock:
                        self.stats["cache_hits"] += 1
                    return cache_entry.value
                else:
                    # Remover entrada expirada
                    del self.price_cache[symbol]
        
        # Cache miss - obtener precio fresco
        with self._stats_lock:
            self.stats["cache_misses"] += 1
        
        try:
            price = self.price_fetcher(symbol)
            if price and price > 0:
                # Almacenar en cache con TTL
                with self._cache_lock:
                    self.price_cache[symbol] = CacheEntry(
                        value=price,
                        timestamp=now,
                        ttl_seconds=self.price_cache_duration
                    )
                
                # Cleanup periódico del cache
                self._cleanup_expired_cache()
                
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
                timeframe=config.get("trading_bot", {}).get("primary_timeframe", "1h"),
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
    
    def get_monitor_stats(self) -> Dict:
        """📊 Obtener estadísticas del monitor thread-safe
        
        Returns:
            Diccionario con estadísticas del monitor
        """
        with self._stats_lock:
            stats_copy = self.stats.copy()
        
        with self._cache_lock:
            cache_size = len(self.price_cache)
            cache_efficiency = (
                stats_copy["cache_hits"] / (stats_copy["cache_hits"] + stats_copy["cache_misses"])
                if (stats_copy["cache_hits"] + stats_copy["cache_misses"]) > 0 else 0
            )
        
        return {
            "monitoring_active": self.monitoring_active,
            "monitoring_cycles": stats_copy["monitoring_cycles"],
            "tp_executed": stats_copy["tp_executed"],
            "sl_executed": stats_copy["sl_executed"],
            "positions_monitored": stats_copy["positions_monitored"],
            "cache_hits": stats_copy["cache_hits"],
            "cache_misses": stats_copy["cache_misses"],
            "cache_efficiency": f"{cache_efficiency:.2%}",
            "cache_size": cache_size,
            "processed_trades_count": len(self.processed_trades),
            "failed_attempts_count": len(self.failed_close_attempts),
            "processed_trades": list(self.processed_trades),
            "failed_attempts": dict(self.failed_close_attempts),
            "max_close_attempts": self.max_close_attempts,
            "thread_pool_active": not self._thread_pool._shutdown
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
            
            # Configuración de trailing stop desde config
            trailing_percentage = self.risk_config["trailing_stop_percentage"]
            
            if trade_type == "BUY":
                # Para posiciones largas, trailing stop se mueve hacia arriba
                trailing_stop = current_price * (1 - trailing_percentage / 100)
                # Solo actualizar si es mayor que el stop loss actual
                current_sl = position.get("stop_loss")
                if current_sl is None or trailing_stop > current_sl:
                    return trailing_stop
            else:  # SELL
                # Para posiciones cortas, trailing stop se mueve hacia abajo
                trailing_stop = current_price * (1 + trailing_percentage / 100)
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
        """📊 Obtener estado del monitoreo con métricas avanzadas"""
        # Obtener estadísticas del PositionManager
        position_stats = self.position_manager.get_statistics()
        
        # Obtener información del cache thread-safe
        with self._cache_lock:
            cache_size = len(self.price_cache)
            cache_entries = list(self.price_cache.keys())
            expired_entries = sum(1 for entry in self.price_cache.values() if entry.is_expired())
        
        # Obtener estadísticas thread-safe
        with self._stats_lock:
            cache_hits = self.stats["cache_hits"]
            cache_misses = self.stats["cache_misses"]
            cache_efficiency = (
                cache_hits / (cache_hits + cache_misses)
                if (cache_hits + cache_misses) > 0 else 0
            )
        
        return {
            "monitoring_active": self.monitoring_active,
            "monitor_interval": self.monitor_interval,
            
            # Métricas de cache mejoradas
            "cache": {
                "size": cache_size,
                "entries": cache_entries,
                "expired_entries": expired_entries,
                "hits": cache_hits,
                "misses": cache_misses,
                "efficiency": f"{cache_efficiency:.2%}",
                "ttl_seconds": self.price_cache_duration
            },
            
            # Métricas de threading
            "threading": {
                "thread_pool_active": not self._thread_pool._shutdown,
                "monitor_thread_alive": self.monitor_thread.is_alive() if self.monitor_thread else False,
                "stop_event_set": self.stop_event.is_set()
            },
            
            # Estadísticas del PositionManager
            "positions": {
                "active_positions": position_stats["active_positions"],
                "positions_managed": position_stats["positions_managed"],
                "take_profits_executed": position_stats["take_profits_executed"],
                "stop_losses_executed": position_stats["stop_losses_executed"],
                "trailing_stops_activated": position_stats["trailing_stops_activated"],
                "total_realized_pnl": position_stats["total_realized_pnl"]
            }
        }
"""📊 Position Manager - Gestor de Posiciones Activas

Este módulo implementa:
- Gestión centralizada de posiciones activas
- Coordinación entre position_monitor y paper_trader
- Tracking de Take Profit y Stop Loss
- Gestión de trailing stops
- Análisis de performance de posiciones
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

# Importaciones locales
from src.config.main_config import TradingBotConfig, RiskManagerConfig, TradingProfiles
from database.database import db_manager
from database.models import Trade
from .enhanced_strategies import TradingSignal
from .paper_trader import PaperTrader, TradeResult
from .advanced_indicators import AdvancedIndicators

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class PositionInfo:
    """📊 Información completa de una posición"""
    trade_id: int
    symbol: str
    trade_type: str  # BUY o SELL
    entry_price: float
    current_price: float
    quantity: float
    entry_value: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_percentage: float
    stop_loss: Optional[float]  # Puede ser None
    take_profit: Optional[float]  # Puede ser None
    trailing_stop: Optional[float]
    entry_time: datetime
    strategy_name: str
    confidence_score: float
    timeframe: str
    notes: str
    
    # Métricas adicionales
    days_held: float
    max_profit: float
    max_loss: float
    risk_reward_ratio: float

@dataclass
class PositionUpdate:
    """🔄 Actualización de posición"""
    trade_id: int
    action: str  # UPDATE_PRICE, UPDATE_TRAILING, CLOSE_POSITION
    new_price: Optional[float] = None
    new_trailing_stop: Optional[float] = None
    close_reason: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PositionManager:
    """📊 Gestor de Posiciones Activas
    
    Características:
    - Gestión centralizada de todas las posiciones
    - Coordinación con position_monitor
    - Ejecución automática de TP/SL
    - Trailing stops dinámicos
    - Análisis de performance
    """
    
    def __init__(self, paper_trader: PaperTrader = None):
        """
        Inicializar el gestor de posiciones
        
        Args:
            paper_trader: Instancia del paper trader para ejecutar órdenes
        """
        self.paper_trader = paper_trader or PaperTrader()
        self.config = TradingBotConfig()
        self.risk_config = RiskManagerConfig()
        
        # Cache de posiciones para optimización
        self.positions_cache = {}
        self.last_cache_update = 0
        profile = TradingProfiles.get_current_profile()
        self.cache_duration = profile['position_check_interval']  # segundos
        
        # Configuración de trailing stops desde RiskManagerConfig
        self.trailing_stop_activation = self.risk_config.TRAILING_STOP_ACTIVATION  # Ya en decimal
        self.trailing_stop_distance = profile['default_trailing_distance']  # Ya en decimal
        
        # Estadísticas
        self.stats = {
            "positions_managed": 0,
            "tp_executed": 0,
            "sl_executed": 0,
            "trailing_stops_activated": 0,
            "total_pnl": 0.0
        }
        
        logger.info("📊 Position Manager initialized")
    
    def get_active_positions(self, refresh_cache: bool = False) -> List[PositionInfo]:
        """📊 Obtener todas las posiciones activas
        
        Args:
            refresh_cache: Forzar actualización del cache
            
        Returns:
            Lista de posiciones activas
        """
        now = time.time()
        
        # Verificar cache
        if not refresh_cache and (now - self.last_cache_update) < self.cache_duration:
            return list(self.positions_cache.values())
        
        # Obtener posiciones frescas de la base de datos
        positions = []
        
        try:
            with db_manager.get_db_session() as session:
                open_trades = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                for trade in open_trades:
                    position_info = self._create_position_info(trade)
                    if position_info:
                        positions.append(position_info)
                        self.positions_cache[trade.id] = position_info
                
                self.last_cache_update = now
                logger.debug(f"📊 Loaded {len(positions)} active positions")
                
        except Exception as e:
            logger.error(f"❌ Error loading active positions: {e}")
        
        return positions
    
    def _create_position_info(self, trade: Trade) -> Optional[PositionInfo]:
        """📊 Crear información de posición desde un trade
        
        Args:
            trade: Trade de la base de datos
            
        Returns:
            PositionInfo o None si hay error
        """
        try:
            # Calcular días mantenida
            days_held = (datetime.now() - trade.entry_time).total_seconds() / 86400
            
            # Calcular métricas de riesgo/recompensa
            potential_profit = 0
            potential_loss = 0
            
            if trade.take_profit is not None and trade.stop_loss is not None:
                if trade.trade_type == "BUY":
                    potential_profit = trade.take_profit - trade.entry_price
                    potential_loss = trade.entry_price - trade.stop_loss
                else:  # SELL
                    potential_profit = trade.entry_price - trade.take_profit
                    potential_loss = trade.stop_loss - trade.entry_price
            
            risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
            
            # Obtener precio actual (placeholder - se actualizará desde position_monitor)
            current_price = trade.entry_price  # Se actualizará externamente
            
            # Calcular PnL actual
            if trade.trade_type == "BUY":
                unrealized_pnl = (current_price - trade.entry_price) * trade.quantity
                current_value = current_price * trade.quantity
            else:  # SELL
                unrealized_pnl = (trade.entry_price - current_price) * trade.quantity
                current_value = current_price * trade.quantity
            
            unrealized_pnl_percentage = (unrealized_pnl / trade.entry_value) * 100 if trade.entry_value > 0 else 0
            
            return PositionInfo(
                trade_id=trade.id,
                symbol=trade.symbol,
                trade_type=trade.trade_type,
                entry_price=trade.entry_price,
                current_price=current_price,
                quantity=trade.quantity,
                entry_value=trade.entry_value,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_percentage=unrealized_pnl_percentage,
                stop_loss=trade.stop_loss,
                take_profit=trade.take_profit,
                trailing_stop=getattr(trade, 'trailing_stop', None),
                entry_time=trade.entry_time,
                strategy_name=trade.strategy_name,
                confidence_score=trade.confidence_score,
                timeframe=trade.timeframe,
                notes=trade.notes or "",
                days_held=days_held,
                max_profit=self._calculate_max_profit(trade),
                max_loss=self._calculate_max_loss(trade),
                risk_reward_ratio=risk_reward_ratio
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating position info for trade {trade.id}: {e}")
            return None
    
    def update_position_price(self, trade_id: int, new_price: float) -> bool:
        """💰 Actualizar precio de una posición
        
        Args:
            trade_id: ID del trade
            new_price: Nuevo precio actual
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            if trade_id in self.positions_cache:
                position = self.positions_cache[trade_id]
                
                # Actualizar precio
                old_price = position.current_price
                position.current_price = new_price
                
                # Recalcular métricas
                if position.trade_type == "BUY":
                    position.unrealized_pnl = (new_price - position.entry_price) * position.quantity
                    position.current_value = new_price * position.quantity
                else:  # SELL
                    position.unrealized_pnl = (position.entry_price - new_price) * position.quantity
                    position.current_value = new_price * position.quantity
                
                position.unrealized_pnl_percentage = (position.unrealized_pnl / position.entry_value) * 100 if position.entry_value > 0 else 0
                
                # Actualizar trailing stop si aplica
                self._update_trailing_stop(position)
                
                logger.debug(f"💰 Updated position {trade_id}: {old_price:.4f} -> {new_price:.4f}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating position price for {trade_id}: {e}")
        
        return False
    
    def _update_trailing_stop(self, position: PositionInfo):
        """📈 Actualizar trailing stop de una posición
        
        Args:
            position: Información de la posición
        """
        try:
            # Solo para posiciones BUY por ahora
            if position.trade_type != "BUY":
                return
            
            # Verificar si la posición está en ganancia suficiente para activar trailing
            profit_percentage = position.unrealized_pnl_percentage / 100.0  # Convertir porcentaje a decimal para comparación
            
            if profit_percentage >= self.trailing_stop_activation:
                # Calcular nuevo trailing stop
                new_trailing = position.current_price * (1 - self.trailing_stop_distance)
                
                # Solo actualizar si es mejor que el trailing actual
                if position.trailing_stop is None or new_trailing > position.trailing_stop:
                    old_trailing = position.trailing_stop
                    position.trailing_stop = new_trailing
                    
                    if old_trailing is None:
                        self.stats["trailing_stops_activated"] += 1
                        logger.info(f"📈 Trailing stop activated for {position.symbol}: ${new_trailing:.4f}")
                    else:
                        logger.debug(f"📈 Trailing stop updated for {position.symbol}: ${old_trailing:.4f} -> ${new_trailing:.4f}")
                        
        except Exception as e:
            logger.error(f"❌ Error updating trailing stop for position {position.trade_id}: {e}")
    
    def check_exit_conditions(self, position: PositionInfo) -> Optional[str]:
        """🎯 Verificar si una posición debe cerrarse
        
        Args:
            position: Información de la posición
            
        Returns:
            Razón de cierre o None si no debe cerrarse
        """
        try:
            current_price = position.current_price
            
            if position.trade_type == "BUY":
                # Verificar Take Profit (solo si está configurado)
                if position.take_profit is not None and current_price >= position.take_profit:
                    return "TAKE_PROFIT"
                
                # Verificar Stop Loss (solo si está configurado)
                if position.stop_loss is not None and current_price <= position.stop_loss:
                    return "STOP_LOSS"
                
                # Verificar Trailing Stop
                if position.trailing_stop is not None and current_price <= position.trailing_stop:
                    return "TRAILING_STOP"
                    
            else:  # SELL
                # Verificar Take Profit (solo si está configurado)
                if position.take_profit is not None and current_price <= position.take_profit:
                    return "TAKE_PROFIT"
                
                # Verificar Stop Loss (solo si está configurado)
                if position.stop_loss is not None and current_price >= position.stop_loss:
                    return "STOP_LOSS"
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking exit conditions for position {position.trade_id}: {e}")
            return None
    
    def close_position(self, trade_id: int, current_price: float, reason: str) -> bool:
        """🎯 Cerrar posición específica
        
        Args:
            trade_id: ID del trade a cerrar
            current_price: Precio actual para el cierre
            reason: Razón del cierre
            
        Returns:
            True si se cerró correctamente
        """
        try:
            with db_manager.get_db_session() as session:
                # Buscar el trade
                trade = session.query(Trade).filter(
                    Trade.id == trade_id,
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).first()
                
                if not trade:
                    logger.error(f"❌ Trade {trade_id} not found or already closed")
                    return False
                
                # Calcular PnL
                if trade.trade_type == "BUY":
                    pnl = (current_price - trade.entry_price) * trade.quantity
                else:  # SELL
                    pnl = (trade.entry_price - current_price) * trade.quantity
                
                pnl_percentage = (pnl / trade.entry_value) * 100 if trade.entry_value > 0 else 0
                
                # Actualizar trade
                trade.exit_price = current_price
                trade.exit_value = current_price * trade.quantity
                trade.pnl = pnl
                trade.pnl_percentage = pnl_percentage
                trade.status = "CLOSED"
                trade.exit_time = datetime.now()
                trade.notes = f"{trade.notes or ''} | Auto closed: {reason}"
                
                # Actualizar portfolio
                asset_symbol = trade.symbol.split('/')[0]
                
                if trade.trade_type == "BUY":
                    # Vender el asset, obtener USDT
                    sale_value = current_price * trade.quantity
                    self.paper_trader._update_usdt_balance(sale_value, session)
                    self.paper_trader._update_asset_balance(asset_symbol, -trade.quantity, current_price, session)
                else:
                    # Comprar el asset, gastar USDT
                    purchase_value = current_price * trade.quantity
                    self.paper_trader._update_usdt_balance(-purchase_value, session)
                    self.paper_trader._update_asset_balance(asset_symbol, trade.quantity, current_price, session)
                
                session.commit()
                
                # Actualizar estadísticas
                if reason == "TAKE_PROFIT":
                    self.stats["tp_executed"] += 1
                elif reason in ["STOP_LOSS", "TRAILING_STOP"]:
                    self.stats["sl_executed"] += 1
                
                self.stats["total_pnl"] += pnl
                
                # Remover del cache
                if trade_id in self.positions_cache:
                    del self.positions_cache[trade_id]
                
                # Obtener balances actuales para el log detallado
                usdt_balance = self.paper_trader._get_usdt_balance()
                portfolio_summary = self.paper_trader.get_portfolio_summary()
                total_portfolio_value = portfolio_summary.get('total_value', 0.0)
                
                # Determinar tipo de activación para el log
                activation_type = "📈 TAKE PROFIT" if reason == "TAKE_PROFIT" else "📉 STOP LOSS"
                if reason == "TRAILING_STOP":
                    activation_type = "🎯 TRAILING STOP"
                
                # Determinar si es ganancia o pérdida
                result_type = "💰 GANANCIA" if pnl > 0 else "💸 PÉRDIDA"
                if pnl == 0:
                    result_type = "⚖️ NEUTRO"
                
                # Log detallado del cierre automático
                logger.info("")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info("🤖 CIERRE AUTOMÁTICO DE POSICIÓN")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info(f"⚡ ACTIVACIÓN: {activation_type}")
                logger.info(f"📊 SÍMBOLO: {trade.symbol}")
                logger.info(f"💱 PRECIO ENTRADA: ${trade.entry_price:.4f}")
                logger.info(f"💱 PRECIO SALIDA: ${current_price:.4f}")
                logger.info(f"📦 CANTIDAD: {trade.quantity:.6f} {asset_symbol}")
                logger.info(f"")
                logger.info(f"📊 RESULTADO DE LA OPERACIÓN:")
                logger.info(f"{result_type}: ${pnl:.2f} ({pnl_percentage:+.2f}%)")
                logger.info(f"")
                logger.info(f"💼 ESTADO DEL PORTAFOLIO:")
                logger.info(f"💰 Balance USDT: ${usdt_balance:.2f}")
                logger.info(f"📈 Valor Total Portafolio: ${total_portfolio_value:.2f}")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info("")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error closing position {trade_id}: {e}")
            return False
    

    
    def get_position_by_id(self, trade_id: int) -> Optional[PositionInfo]:
        """📊 Obtener posición por ID
        
        Args:
            trade_id: ID del trade
            
        Returns:
            PositionInfo o None si no existe
        """
        if trade_id in self.positions_cache:
            return self.positions_cache[trade_id]
        
        # Buscar en base de datos
        positions = self.get_active_positions(refresh_cache=True)
        for position in positions:
            if position.trade_id == trade_id:
                return position
        
        return None
    
    def get_positions_by_symbol(self, symbol: str) -> List[PositionInfo]:
        """📊 Obtener posiciones por símbolo
        
        Args:
            symbol: Símbolo a buscar
            
        Returns:
            Lista de posiciones del símbolo
        """
        positions = self.get_active_positions()
        return [pos for pos in positions if pos.symbol == symbol]
    
    def get_portfolio_exposure(self) -> Dict:
        """📊 Obtener exposición actual del portfolio
        
        Returns:
            Diccionario con métricas de exposición
        """
        positions = self.get_active_positions()
        
        total_exposure = 0.0
        symbol_exposure = {}
        total_unrealized_pnl = 0.0
        
        for position in positions:
            total_exposure += position.current_value
            total_unrealized_pnl += position.unrealized_pnl
            
            if position.symbol not in symbol_exposure:
                symbol_exposure[position.symbol] = {
                    "value": 0.0,
                    "positions": 0,
                    "pnl": 0.0
                }
            
            symbol_exposure[position.symbol]["value"] += position.current_value
            symbol_exposure[position.symbol]["positions"] += 1
            symbol_exposure[position.symbol]["pnl"] += position.unrealized_pnl
        
        return {
            "total_positions": len(positions),
            "total_exposure": total_exposure,
            "total_unrealized_pnl": total_unrealized_pnl,
            "symbol_breakdown": symbol_exposure,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict:
        """📊 Obtener estadísticas del gestor
        
        Returns:
            Diccionario con estadísticas
        """
        positions = self.get_active_positions()
        
        return {
            "active_positions": len(positions),
            "positions_managed": self.stats["positions_managed"],
            "take_profits_executed": self.stats["tp_executed"],
            "stop_losses_executed": self.stats["sl_executed"],
            "trailing_stops_activated": self.stats["trailing_stops_activated"],
            "total_realized_pnl": self.stats["total_pnl"],
            "cache_size": len(self.positions_cache),
            "last_cache_update": datetime.fromtimestamp(self.last_cache_update).isoformat() if self.last_cache_update > 0 else None
        }
    
    def calculate_atr_trailing_stop(self, symbol: str, current_price: float, trade_type: str, atr_multiplier: float = 2.0) -> Optional[float]:
        """📊 Calcular trailing stop dinámico basado en ATR
        
        Args:
            symbol: Símbolo del activo
            current_price: Precio actual
            trade_type: Tipo de trade (BUY/SELL)
            atr_multiplier: Multiplicador del ATR para el trailing stop
            
        Returns:
            Precio del trailing stop o None si hay error
        """
        try:
            # Obtener datos históricos para calcular ATR
            # Por ahora usamos un ATR estimado basado en el precio
            # En una implementación completa, se obtendría data histórica real
            estimated_atr = current_price * 0.02  # 2% como estimación conservadora
            
            if trade_type == "BUY":
                # Para posiciones largas, trailing stop debajo del precio
                trailing_stop = current_price - (estimated_atr * atr_multiplier)
            else:  # SELL
                # Para posiciones cortas, trailing stop arriba del precio
                trailing_stop = current_price + (estimated_atr * atr_multiplier)
            
            return trailing_stop
            
        except Exception as e:
            logger.error(f"❌ Error calculating ATR trailing stop for {symbol}: {e}")
            return None
    
    def update_trailing_stops(self, market_data: Dict[str, float]) -> int:
        """🎯 Actualizar trailing stops para todas las posiciones activas
        
        Args:
            market_data: Diccionario con precios actuales {symbol: price}
            
        Returns:
            Número de trailing stops actualizados
        """
        updated_count = 0
        
        try:
            positions = self.get_active_positions()
            
            if not positions:
                return 0
            
            with db_manager.get_db_session() as session:
                for position in positions:
                    if position.symbol not in market_data:
                        continue
                    
                    current_price = market_data[position.symbol]
                    
                    # Calcular nuevo trailing stop
                    new_trailing_stop = self.calculate_atr_trailing_stop(
                        position.symbol, 
                        current_price, 
                        position.trade_type
                    )
                    
                    if new_trailing_stop is None:
                        continue
                    
                    # Obtener trade de la base de datos
                    trade = session.query(Trade).filter(
                        Trade.id == position.trade_id,
                        Trade.status == "OPEN"
                    ).first()
                    
                    if not trade:
                        continue
                    
                    # Verificar si la posición tiene suficiente ganancia para activar trailing stop
                    profit_pct = 0
                    if position.trade_type == "BUY":
                        profit_pct = (current_price - position.entry_price) / position.entry_price
                    else:  # SELL
                        profit_pct = (position.entry_price - current_price) / position.entry_price
                    
                    # Solo activar trailing stop si hay ganancia suficiente
                    if profit_pct < self.trailing_stop_activation:
                        logger.debug(f"Trailing stop not activated for {position.symbol}: profit {profit_pct:.2%} < activation threshold {self.trailing_stop_activation:.2%}")
                        continue
                    
                    # Verificar si necesita actualizar trailing stop
                    should_update = False
                    
                    if position.trade_type == "BUY":
                        # Para posiciones largas, solo subir el trailing stop
                        if (not hasattr(trade, 'trailing_stop') or 
                            trade.trailing_stop is None or 
                            new_trailing_stop > trade.trailing_stop):
                            should_update = True
                    else:  # SELL
                        # Para posiciones cortas, solo bajar el trailing stop
                        if (not hasattr(trade, 'trailing_stop') or 
                            trade.trailing_stop is None or 
                            new_trailing_stop < trade.trailing_stop):
                            should_update = True
                    
                    if should_update:
                        # Actualizar trailing stop en la base de datos
                        if not hasattr(trade, 'trailing_stop'):
                            # Añadir columna si no existe (para compatibilidad)
                            pass
                        
                        trade.trailing_stop = new_trailing_stop
                        
                        # Actualizar cache
                        if position.trade_id in self.positions_cache:
                            self.positions_cache[position.trade_id].trailing_stop = new_trailing_stop
                        
                        updated_count += 1
                        
                        logger.debug(
                            f"📊 Updated trailing stop for {position.symbol}: "
                            f"${new_trailing_stop:.4f} (Price: ${current_price:.4f})"
                        )
                
                session.commit()
                
                if updated_count > 0:
                    self.stats["trailing_stops_activated"] += updated_count
                    logger.info(f"🎯 Updated {updated_count} trailing stops")
                    # Invalidar caché para reflejar los nuevos trailing stops
                    self.positions_cache.clear()
                
        except Exception as e:
            logger.error(f"❌ Error updating trailing stops: {e}")
        
        return updated_count
    
    def update_dynamic_take_profits(self, market_data: Dict[str, float], risk_manager=None) -> int:
        """🎯 Actualizar take profits dinámicos para todas las posiciones activas
        
        Args:
            market_data: Diccionario con precios actuales {symbol: price}
            risk_manager: Instancia del risk manager para lógica de TP dinámico
            
        Returns:
            Número de take profits actualizados
        """
        updated_count = 0
        
        try:
            positions = self.get_active_positions()
            
            with db_manager.get_db_session() as session:
                for position in positions:
                    if position.symbol not in market_data:
                        continue
                    
                    current_price = market_data[position.symbol]
                    
                    # Obtener trade de la base de datos
                    trade = session.query(Trade).filter(
                        Trade.id == position.trade_id,
                        Trade.status == "OPEN"
                    ).first()
                    
                    if not trade:
                        continue
                    
                    # Calcular ganancia actual
                    if position.trade_type == "BUY":
                        current_profit_pct = (current_price - position.entry_price) / position.entry_price
                    else:  # SELL
                        current_profit_pct = (position.entry_price - current_price) / position.entry_price
                    
                    # Solo actualizar si hay ganancias significativas (>= tp_min en porcentaje)
                    # current_profit_pct ahora está en DECIMAL y tp_min está en DECIMAL
                    if current_profit_pct < RiskManagerConfig.get_tp_min_percentage():
                        continue
                    
                    # Calcular nuevo take profit dinámico
                    new_take_profit = self._calculate_dynamic_take_profit(
                        position, current_price, current_profit_pct
                    )
                    
                    if new_take_profit is None:
                        continue
                    
                    # Verificar si necesita actualizar take profit
                    should_update = False
                    current_tp = getattr(trade, 'take_profit_price', None)
                    
                    if position.trade_type == "BUY":
                        # Para posiciones largas, solo subir el take profit
                        if current_tp is None or new_take_profit > current_tp:
                            should_update = True
                    else:  # SELL
                        # Para posiciones cortas, solo bajar el take profit
                        if current_tp is None or new_take_profit < current_tp:
                            should_update = True
                    
                    if should_update:
                        # Actualizar take profit en la base de datos
                        trade.take_profit_price = new_take_profit
                        
                        # Actualizar cache
                        if position.trade_id in self.positions_cache:
                            self.positions_cache[position.trade_id].take_profit = new_take_profit
                        
                        updated_count += 1
                        
                        logger.info(
                            f"🎯 Updated dynamic take profit for {position.symbol}: "
                            f"${new_take_profit:.4f} (Price: ${current_price:.4f}, Profit: {current_profit_pct*100:.2f}%)"
                        )
                
                session.commit()
                
                if updated_count > 0:
                    self.stats["tp_executed"] += updated_count
                    logger.info(f"🎯 Updated {updated_count} dynamic take profits")
                
        except Exception as e:
            logger.error(f"❌ Error updating dynamic take profits: {e}")
        
        return updated_count
    
    def _calculate_dynamic_take_profit(self, position: 'PositionInfo', current_price: float, current_profit_pct: float) -> Optional[float]:
        """📊 Calcular take profit dinámico basado en ganancias actuales
        
        Args:
            position: Información de la posición
            current_price: Precio actual
            current_profit_pct: Porcentaje de ganancia actual
            
        Returns:
            Nuevo precio de take profit o None si hay error
        """
        try:
            # Importar configuración dinámica
            from src.config.main_config import RiskManagerConfig
            
            # Obtener umbrales dinámicos desde config
            tp_min = RiskManagerConfig.get_tp_min_percentage()
            tp_max = RiskManagerConfig.get_tp_max_percentage()
            
            # Incremento base del TP (usar mínimo de config)
            tp_increment_pct = tp_min
            
            # Ajustar incremento según ganancia actual (rangos dinámicos)
            # current_profit_pct ahora está en DECIMAL; tp_min/tp_max están en DECIMAL.
            if current_profit_pct >= tp_max:  # tp_max o más de ganancia
                tp_increment_pct = tp_max * 0.67  # Incrementar TP en 2/3 del máximo
            elif current_profit_pct >= tp_max * 0.67:  # 2/3 del tp_max o más de ganancia
                tp_increment_pct = tp_max * 0.5  # Incrementar TP en 1/2 del máximo
            elif current_profit_pct >= tp_min * 0.67:  # 2/3 del tp_min o más de ganancia
                tp_increment_pct = tp_min  # Incrementar TP en mínimo
            else:
                return None  # No actualizar si ganancia es menor al umbral mínimo
            
            # Calcular nuevo take profit
            if position.trade_type == "BUY":
                # Para BUY: incrementar TP hacia arriba
                new_tp = current_price * (1 + tp_increment_pct)
            else:  # SELL
                # Para SELL: decrementar TP hacia abajo
                new_tp = current_price * (1 - tp_increment_pct)
            
            return round(new_tp, 4)
            
        except Exception as e:
            logger.error(f"❌ Error calculating dynamic take profit for {position.symbol}: {e}")
            return None
    
    def _calculate_max_profit(self, trade) -> float:
        """Calcular el máximo profit alcanzado durante el trade."""
        try:
            if not trade.exit_price or not trade.entry_price:
                return 0.0
            
            if trade.trade_type == "BUY":
                profit_pct = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100
            else:  # SELL
                profit_pct = ((trade.entry_price - trade.exit_price) / trade.entry_price) * 100
            
            return max(0.0, profit_pct)
        except Exception:
            return 0.0
    
    def _calculate_max_loss(self, trade) -> float:
        """Calcular la máxima pérdida alcanzada durante el trade."""
        try:
            if not trade.exit_price or not trade.entry_price:
                return 0.0
            
            if trade.trade_type == "BUY":
                loss_pct = ((trade.entry_price - trade.exit_price) / trade.entry_price) * 100
            else:  # SELL
                loss_pct = ((trade.exit_price - trade.entry_price) / trade.entry_price) * 100
            
            return max(0.0, loss_pct)
        except Exception:
            return 0.0
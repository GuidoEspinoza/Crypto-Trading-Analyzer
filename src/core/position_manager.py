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
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session

# Importaciones locales
from src.config.config_manager import ConfigManager

# Inicializar configuración centralizada con manejo de errores
try:
    config_manager = ConfigManager()
    config = config_manager.get_consolidated_config()
    if config is None:
        config = {}
except Exception as e:
    # Configuración de fallback en caso de error
    config = {
        'trading': {'usdt_base_price': 1.0},
        'paper_trader': {'max_slippage': 0.001, 'simulation_fees': 0.001},
        'advanced_indicators': {'fibonacci_lookback': 50},
        'api': {'latency_simulation_sleep': 0.1}
    }
from ..database.database import db_manager
from ..database.models import Trade
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
    trailing_stop: Optional[float] = None  # Trailing stop dinámico

@dataclass
class PositionUpdate:
    """🔄 Actualización de posición"""
    trade_id: int
    action: str  # UPDATE_PRICE, CLOSE_POSITION
    new_price: Optional[float] = None
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
        
        # Cache de posiciones para optimización
        self.positions_cache = {}
        self.last_cache_update = 0
        
        # Obtener configuración del perfil de trading
        try:
            from src.config.config import TradingProfiles
            profile = TradingProfiles.get_current_profile()
            self.cache_duration = profile.get('position_check_interval', 30)  # segundos
            self.seconds_per_day = profile.get('seconds_per_day', 86400)  # Configurable para tests
        except Exception as e:
            logger.warning(f"⚠️ Error loading trading profile, using defaults: {e}")
            self.cache_duration = 30  # segundos
            self.seconds_per_day = 86400  # Configurable para tests
        
        # Configuraciones adicionales del perfil
        try:
            self.atr_estimation_pct = profile.get('atr_estimation_percentage', 2.0) / 100  # Convertir de % a decimal
            self.trailing_stop_activation = profile.get('trailing_stop_activation', 3.0) / 100  # Convertir de % a decimal
            self.profit_scaling_ratios = {
                'tp_max_ratio': profile.get('tp_max_ratio', 0.67),  # 2/3 del máximo
                'tp_mid_ratio': profile.get('tp_mid_ratio', 0.5),   # 1/2 del máximo
                'tp_min_ratio': profile.get('tp_min_ratio', 0.67)   # 2/3 del mínimo (default value)
            }
        except NameError:
            # Si profile no está definido (error en el try anterior)
            self.atr_estimation_pct = 2.0 / 100  # 2% como estimación conservadora
            self.trailing_stop_activation = 3.0 / 100  # 3% como valor por defecto
            self.profit_scaling_ratios = {
                'tp_max_ratio': 0.67,  # 2/3 del máximo
                'tp_mid_ratio': 0.5,   # 1/2 del máximo
                'tp_min_ratio': 0.67   # 2/3 del mínimo (default value)
            }
        
        # Estadísticas
        self.stats = {
            "positions_managed": 0,
            "tp_executed": 0,
            "sl_executed": 0,
            "total_pnl": 0.0
        }
        
        logger.info("📊 Position Manager initialized")
    
    def invalidate_cache(self, trade_id: Optional[int] = None):
        """🔄 Invalidar cache de posiciones
        
        Args:
            trade_id: ID específico a invalidar, None para invalidar todo
        """
        if trade_id is not None:
            # Invalidar posición específica
            if trade_id in self.positions_cache:
                del self.positions_cache[trade_id]
                logger.debug(f"🔄 Cache invalidated for position {trade_id}")
        else:
            # Invalidar todo el cache
            self.positions_cache.clear()
            self.last_cache_update = 0
            logger.debug("🔄 Full cache invalidated")
    
    def is_cache_valid(self) -> bool:
        """✅ Verificar si el cache es válido
        
        Returns:
            True si el cache es válido
        """
        now = time.time()
        return (now - self.last_cache_update) < self.cache_duration
    
    def update_cache_entry(self, position: PositionInfo):
        """🔄 Actualizar entrada específica del cache
        
        Args:
            position: Información de posición actualizada
        """
        self.positions_cache[position.trade_id] = position
        logger.debug(f"🔄 Cache updated for position {position.trade_id}")
    
    def get_cache_stats(self) -> Dict:
        """📊 Obtener estadísticas del cache
        
        Returns:
            Diccionario con estadísticas del cache
        """
        now = time.time()
        cache_age = now - self.last_cache_update if self.last_cache_update > 0 else 0
        
        return {
            "cache_size": len(self.positions_cache),
            "cache_age_seconds": cache_age,
            "cache_valid": self.is_cache_valid(),
            "cache_duration": self.cache_duration,
            "last_update": datetime.fromtimestamp(self.last_cache_update).isoformat() if self.last_cache_update > 0 else None
        }
    
    def get_active_positions(self, refresh_cache: bool = False) -> List[PositionInfo]:
        """📊 Obtener todas las posiciones activas
        
        Args:
            refresh_cache: Forzar actualización del cache
            
        Returns:
            Lista de posiciones activas
        """
        # Verificar cache usando método optimizado
        if not refresh_cache and self.is_cache_valid():
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
                
                self.last_cache_update = time.time()
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
            days_held = (datetime.now() - trade.entry_time).total_seconds() / self.seconds_per_day
            
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
                entry_time=trade.entry_time,
                strategy_name=trade.strategy_name,
                confidence_score=trade.confidence_score,
                timeframe=trade.timeframe,
                notes=trade.notes or "",
                days_held=days_held,
                max_profit=self._calculate_max_profit(trade),
                max_loss=self._calculate_max_loss(trade),
                risk_reward_ratio=risk_reward_ratio,
                trailing_stop=None  # Por defecto None, se puede configurar después
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
                
                # Actualizar cache con la posición modificada
                self.update_cache_entry(position)
                
                logger.debug(f"💰 Updated position {trade_id}: {old_price:.4f} -> {new_price:.4f}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating position price for {trade_id}: {e}")
        
        return False
    

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
                    
            else:  # SELL
                # Verificar Take Profit (solo si está configurado)
                if position.take_profit is not None and current_price <= position.take_profit:
                    return "TAKE_PROFIT"
                
                # Verificar Stop Loss (solo si está configurado)
                if position.stop_loss is not None and current_price >= position.stop_loss:
                    return "STOP_LOSS"
            
            # Verificar salidas basadas en tiempo
            time_exit_reason = self._check_time_based_exit(position)
            if time_exit_reason:
                return time_exit_reason
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking exit conditions for position {position.trade_id}: {e}")
            return None
    
    def _check_time_based_exit(self, position: PositionInfo) -> Optional[str]:
        """⏰ Verificar si una posición debe cerrarse por tiempo
        
        Args:
            position: Información de la posición
            
        Returns:
            Razón de cierre temporal o None
        """
        try:
            # Obtener configuración de salidas temporales
            from src.config.config_manager import ConfigManager
            config = ConfigManager.get_consolidated_config()
            time_config = config.get("advanced_optimizations", {}).get("time_based_exits", {})
            
            # Verificar si las salidas temporales están habilitadas
            if not time_config.get("enabled", False):
                return None
            
            # Obtener información del trade desde la base de datos
            with db_manager.get_db_session() as session:
                trade = session.query(Trade).filter(
                    Trade.id == position.trade_id,
                    Trade.status == "OPEN"
                ).first()
                
                if not trade:
                    return None
                
                # Calcular tiempo transcurrido
                current_time = datetime.now()
                time_elapsed = current_time - trade.entry_time
                time_elapsed_hours = time_elapsed.total_seconds() / 3600
                
                # Obtener parámetros temporales del trade (si están disponibles)
                # Estos deberían estar en el campo notes o en una tabla separada
                expected_duration = getattr(trade, 'expected_duration_hours', None)
                max_hold_time = getattr(trade, 'max_hold_time_hours', None)
                
                # Si no hay parámetros específicos, usar valores por defecto basados en timeframe
                if expected_duration is None or max_hold_time is None:
                    timeframe = getattr(trade, 'timeframe', '1h')
                    expected_duration, max_hold_time = self._get_default_time_parameters(timeframe)
                
                # Calcular P&L actual
                current_pnl_percentage = position.unrealized_pnl_percentage
                
                # Verificar condiciones de salida temporal
                
                # 1. Tiempo máximo alcanzado
                if time_elapsed_hours >= max_hold_time:
                    return "MAX_TIME_REACHED"
                
                # 2. Tiempo esperado alcanzado con ganancia mínima
                profit_threshold = time_config.get("profit_threshold_for_early_exit", 0.03)  # 3%
                if (time_elapsed_hours >= expected_duration and 
                    current_pnl_percentage >= profit_threshold):
                    return "TIME_TARGET_WITH_PROFIT"
                
                # 3. Tiempo esperado alcanzado con pérdida significativa
                loss_threshold = time_config.get("loss_threshold_for_early_exit", -0.015)  # -1.5%
                if (time_elapsed_hours >= expected_duration * 1.2 and  # 20% más del tiempo esperado
                    current_pnl_percentage <= loss_threshold):
                    return "TIME_TARGET_WITH_LOSS"
                
                # 4. Decaimiento temporal - reducir tolerancia con el tiempo
                time_decay_factor = time_config.get("time_decay_factor", 0.1)
                time_progress = min(time_elapsed_hours / max_hold_time, 1.0)
                
                # Ajustar umbrales según el progreso temporal
                adjusted_loss_threshold = loss_threshold * (1 - time_decay_factor * time_progress)
                
                if current_pnl_percentage <= adjusted_loss_threshold:
                    return "TIME_DECAY_LOSS"
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error checking time-based exit for position {position.trade_id}: {e}")
            return None
    
    def _get_default_time_parameters(self, timeframe: str) -> tuple:
        """⏰ Obtener parámetros temporales optimizados para trading activo
        
        Args:
            timeframe: Timeframe del análisis
            
        Returns:
            tuple: (expected_duration_hours, max_hold_time_hours)
        """
        # Configuración base optimizada para trading activo
        base_timeframe_map = {
            "1m": (0.3, 1.5),    # Muy rápido
            "3m": (0.8, 3.0),    # Rápido
            "5m": (1.5, 6.0),    # Optimizado para scalping
            "15m": (3.0, 9.0),   # Trading activo
            "30m": (6.0, 18.0),  # Swing corto
            "1h": (10.0, 36.0),  # Swing medio
            "2h": (18.0, 54.0),  # Swing largo
            "4h": (36.0, 120.0), # Posicional corto
            "6h": (54.0, 180.0), # Posicional medio
            "8h": (72.0, 240.0), # Posicional largo
            "12h": (120.0, 360.0), # Holding corto
            "1d": (180.0, 540.0),  # Holding medio
            "3d": (360.0, 1080.0), # Holding largo
            "1w": (720.0, 1800.0)  # Holding muy largo
        }
        
        # Obtener configuración de salidas temporales
        try:
            time_config = self.config_manager.get_module_config('position_manager', 'AGRESIVO')
            time_exits = time_config.get('time_based_exits', {})
            timeframe_multipliers = time_exits.get('timeframe_multipliers', {})
            
            # Aplicar multiplicador específico del timeframe si existe
            base_expected, base_max = base_timeframe_map.get(timeframe, (18.0, 54.0))
            multiplier = timeframe_multipliers.get(timeframe, 1.0)
            
            return (base_expected * multiplier, base_max * multiplier)
            
        except Exception as e:
            logger.warning(f"⚠️ Error getting timeframe multipliers: {e}")
            return base_timeframe_map.get(timeframe, (18.0, 54.0))  # Valores por defecto optimizados
    
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
                elif reason == "STOP_LOSS":
                    self.stats["sl_executed"] += 1
                
                self.stats["total_pnl"] += pnl
                
                # Remover del cache usando método optimizado
                self.invalidate_cache(trade_id)
                
                # Obtener balances actuales para el log detallado
                usdt_balance = self.paper_trader._get_usdt_balance()
                portfolio_summary = self.paper_trader.get_portfolio_summary()
                total_portfolio_value = portfolio_summary.get('total_value', 0.0)
                
                # Determinar tipo de activación para el log
                activation_type = "📈 TAKE PROFIT" if reason == "TAKE_PROFIT" else "📉 STOP LOSS"
                
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
            "total_realized_pnl": self.stats["total_pnl"],
            "cache_size": len(self.positions_cache),
            "last_cache_update": datetime.fromtimestamp(self.last_cache_update).isoformat() if self.last_cache_update > 0 else None
        }
    

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
                        current_profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                    else:  # SELL
                        current_profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
                    
                    # Solo actualizar si hay ganancias significativas (1.5% o más)
                    if current_profit_pct < 1.5:
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
                            f"${new_take_profit:.4f} (Price: ${current_price:.4f}, Profit: {current_profit_pct:.2f}%)"
                        )
                
                session.commit()
                
                if updated_count > 0:
                    self.stats["tp_executed"] += updated_count
                    logger.info(f"🎯 Updated {updated_count} dynamic take profits")
                
        except Exception as e:
            logger.error(f"❌ Error updating dynamic take profits: {e}")
        
        return updated_count
    
    def update_trailing_stops(self, market_data: Dict[str, float]) -> int:
        """🔄 Actualizar trailing stops para todas las posiciones activas
        
        Args:
            market_data: Diccionario con precios actuales {symbol: price}
            
        Returns:
            Número de trailing stops actualizados
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
                        current_profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                    else:  # SELL
                        current_profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
                    
                    # Solo activar trailing stop si hay ganancia suficiente
                    min_profit_for_trailing = self.trailing_stop_activation * 100  # Convertir a porcentaje
                    if current_profit_pct < min_profit_for_trailing:
                        continue
                    
                    # Calcular nuevo trailing stop
                    new_trailing_stop = self._calculate_trailing_stop(position, current_price, current_profit_pct)
                    
                    if new_trailing_stop is None:
                        continue
                    
                    # Verificar si el nuevo trailing stop es mejor que el actual
                    should_update = False
                    if position.trade_type == "BUY":
                        # Para posiciones LONG, el trailing stop debe subir
                        if position.trailing_stop is None or new_trailing_stop > position.trailing_stop:
                            should_update = True
                    else:  # SELL
                        # Para posiciones SHORT, el trailing stop debe bajar
                        if position.trailing_stop is None or new_trailing_stop < position.trailing_stop:
                            should_update = True
                    
                    if should_update:
                        # Actualizar en la base de datos
                        trade.stop_loss = new_trailing_stop
                        
                        # Actualizar en cache
                        if position.trade_id in self.positions_cache:
                            self.positions_cache[position.trade_id].trailing_stop = new_trailing_stop
                            self.positions_cache[position.trade_id].stop_loss = new_trailing_stop
                        
                        updated_count += 1
                        
                        logger.info(
                            f"🔄 Updated trailing stop for {position.symbol}: "
                            f"${new_trailing_stop:.4f} (Price: ${current_price:.4f}, Profit: {current_profit_pct:.2f}%)"
                        )
                
                session.commit()
                
                if updated_count > 0:
                    self.stats["trailing_stops_updated"] = self.stats.get("trailing_stops_updated", 0) + updated_count
                    logger.info(f"🔄 Updated {updated_count} trailing stops")
                
        except Exception as e:
            logger.error(f"❌ Error updating trailing stops: {e}")
        
        return updated_count
    
    def _calculate_trailing_stop(self, position: 'PositionInfo', current_price: float, current_profit_pct: float) -> Optional[float]:
        """📊 Calcular trailing stop basado en ATR y ganancia actual
        
        Args:
            position: Información de la posición
            current_price: Precio actual
            current_profit_pct: Porcentaje de ganancia actual
            
        Returns:
            Nuevo precio de trailing stop o None si no se puede calcular
        """
        try:
            # Calcular trailing stop basado en ATR
            atr_trailing = self.calculate_atr_trailing_stop(
                symbol=position.symbol,
                current_price=current_price,
                trade_type=position.trade_type,
                atr_multiplier=2.0
            )
            
            if atr_trailing is None:
                # Fallback: usar porcentaje fijo basado en ganancia
                trailing_distance_pct = max(0.5, min(3.0, current_profit_pct * 0.3))  # Entre 0.5% y 3%
                
                if position.trade_type == "BUY":
                    return current_price * (1 - trailing_distance_pct / 100)
                else:  # SELL
                    return current_price * (1 + trailing_distance_pct / 100)
            
            return atr_trailing
            
        except Exception as e:
            logger.error(f"❌ Error calculating trailing stop for {position.symbol}: {e}")
            return None
    
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
            from src.config.config import RiskManagerConfig
            
            # Obtener umbrales dinámicos desde config
            tp_min = config.get("risk_manager", {}).get("tp_min_percentage", 2.0)
            tp_max = config.get("risk_manager", {}).get("tp_max_percentage", 8.0)
            
            # Incremento base del TP (usar mínimo de config)
            tp_increment_pct = tp_min
            
            # Ajustar incremento según ganancia actual (rangos dinámicos)
            if current_profit_pct >= tp_max:  # tp_max% o más de ganancia
                tp_increment_pct = tp_max * 0.67  # Incrementar TP en 2/3 del máximo
            elif current_profit_pct >= tp_max * 0.67:  # 2/3 del tp_max% o más de ganancia
                tp_increment_pct = tp_max * 0.5  # Incrementar TP en 1/2 del máximo
            elif current_profit_pct >= tp_min * 0.67:  # 2/3 del tp_min% o más de ganancia
                tp_increment_pct = tp_min  # Incrementar TP en mínimo
            else:
                return None  # No actualizar si ganancia es menor al umbral mínimo
            
            # Calcular nuevo take profit
            if position.trade_type == "BUY":
                # Para BUY: incrementar TP hacia arriba
                new_tp = current_price * (1 + (tp_increment_pct / 100))
            else:  # SELL
                # Para SELL: decrementar TP hacia abajo
                new_tp = current_price * (1 - (tp_increment_pct / 100))
            
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
    
    def close_profitable_positions_before_reset(self, market_data: Dict[str, float] = None) -> Dict[str, Any]:
        """🔄 Cerrar posiciones rentables antes del reset diario
        
        Esta función se ejecuta automáticamente 15 minutos antes del reset diario
        para cristalizar ganancias y empezar el nuevo día con un balance limpio.
        
        Args:
            market_data: Diccionario con precios actuales {symbol: price}
            
        Returns:
            Diccionario con estadísticas de la operación
        """
        from src.config.global_constants import PRE_RESET_CLOSURE_CONFIG, DAILY_RESET_HOUR, DAILY_RESET_MINUTE
        import pytz
        from datetime import datetime, timedelta
        
        # Verificar si la funcionalidad está habilitada
        if not PRE_RESET_CLOSURE_CONFIG.get("enabled", False):
            logger.info("🔄 Pre-reset closure is disabled")
            return {"status": "disabled", "positions_closed": 0}
        
        try:
            # Configuración
            min_profit_threshold = PRE_RESET_CLOSURE_CONFIG.get("min_profit_threshold", 0.5)
            max_positions_per_batch = PRE_RESET_CLOSURE_CONFIG.get("max_positions_per_batch", 10)
            retry_attempts = PRE_RESET_CLOSURE_CONFIG.get("retry_attempts", 3)
            retry_delay = PRE_RESET_CLOSURE_CONFIG.get("retry_delay_seconds", 30)
            log_detailed = PRE_RESET_CLOSURE_CONFIG.get("log_detailed_operations", True)
            
            # Verificar si estamos en el momento correcto para ejecutar
            chile_tz = pytz.timezone("America/Santiago")
            current_time = datetime.now(chile_tz)
            
            # Calcular tiempo de reset
            reset_time = current_time.replace(
                hour=DAILY_RESET_HOUR, 
                minute=DAILY_RESET_MINUTE, 
                second=0, 
                microsecond=0
            )
            
            # Calcular tiempo de cierre (15 minutos antes del reset)
            minutes_before = PRE_RESET_CLOSURE_CONFIG.get("minutes_before_reset", 15)
            closure_time = reset_time - timedelta(minutes=minutes_before)
            
            # Verificar si estamos en la ventana de cierre (±2 minutos de tolerancia)
            time_diff = abs((current_time - closure_time).total_seconds())
            if time_diff > 120:  # 2 minutos de tolerancia
                if log_detailed:
                    logger.debug(f"🔄 Not in closure window. Current: {current_time.strftime('%H:%M:%S')}, Target: {closure_time.strftime('%H:%M:%S')}")
                return {"status": "not_in_window", "positions_closed": 0}
            
            logger.info(f"🔄 Starting pre-reset closure at {current_time.strftime('%H:%M:%S CLT')}")
            logger.info(f"🎯 Target: Close profitable positions before reset at {reset_time.strftime('%H:%M:%S CLT')}")
            
            # Obtener posiciones activas
            active_positions = self.get_active_positions()
            if not active_positions:
                logger.info("🔄 No active positions to close")
                return {"status": "no_positions", "positions_closed": 0}
            
            # Obtener precios actuales si no se proporcionaron
            if market_data is None:
                market_data = {}
                for position in active_positions:
                    try:
                        # Aquí deberías usar tu método de obtención de precios
                        # Por ahora usamos el precio actual de la posición
                        market_data[position.symbol] = position.current_price
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get current price for {position.symbol}: {e}")
                        continue
            
            # Filtrar posiciones rentables
            profitable_positions = []
            for position in active_positions:
                if position.symbol not in market_data:
                    continue
                
                current_price = market_data[position.symbol]
                
                # Calcular ganancia actual
                if position.trade_type == "BUY":
                    profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                else:  # SELL
                    profit_pct = ((position.entry_price - current_price) / position.entry_price) * 100
                
                # Solo incluir posiciones con ganancia superior al umbral
                if profit_pct >= min_profit_threshold:
                    profitable_positions.append({
                        "position": position,
                        "current_price": current_price,
                        "profit_pct": profit_pct
                    })
            
            if not profitable_positions:
                logger.info(f"🔄 No profitable positions found (min threshold: {min_profit_threshold}%)")
                return {"status": "no_profitable_positions", "positions_closed": 0}
            
            # Ordenar por ganancia (mayor ganancia primero)
            profitable_positions.sort(key=lambda x: x["profit_pct"], reverse=True)
            
            # Limitar el número de posiciones por lote
            positions_to_close = profitable_positions[:max_positions_per_batch]
            
            logger.info(f"🎯 Found {len(profitable_positions)} profitable positions, closing {len(positions_to_close)}")
            
            # Cerrar posiciones
            closed_count = 0
            failed_count = 0
            total_profit = 0.0
            closure_details = []
            
            for pos_data in positions_to_close:
                position = pos_data["position"]
                current_price = pos_data["current_price"]
                profit_pct = pos_data["profit_pct"]
                
                success = False
                for attempt in range(retry_attempts):
                    try:
                        # Intentar cerrar la posición
                        if self.close_position(position.trade_id, current_price, "PRE_RESET_CLOSURE"):
                            success = True
                            closed_count += 1
                            
                            # Calcular profit en USDT
                            profit_usdt = (profit_pct / 100) * position.entry_value
                            total_profit += profit_usdt
                            
                            closure_details.append({
                                "symbol": position.symbol,
                                "trade_id": position.trade_id,
                                "profit_pct": profit_pct,
                                "profit_usdt": profit_usdt,
                                "entry_price": position.entry_price,
                                "exit_price": current_price
                            })
                            
                            if log_detailed:
                                logger.info(
                                    f"✅ Closed {position.symbol} (ID: {position.trade_id}) | "
                                    f"Profit: {profit_pct:.2f}% (${profit_usdt:.2f}) | "
                                    f"Entry: ${position.entry_price:.4f} → Exit: ${current_price:.4f}"
                                )
                            break
                        else:
                            if attempt < retry_attempts - 1:
                                logger.warning(f"⚠️ Failed to close {position.symbol} (attempt {attempt + 1}), retrying in {retry_delay}s...")
                                time.sleep(retry_delay)
                            
                    except Exception as e:
                        logger.error(f"❌ Error closing position {position.trade_id}: {e}")
                        if attempt < retry_attempts - 1:
                            time.sleep(retry_delay)
                
                if not success:
                    failed_count += 1
                    logger.error(f"❌ Failed to close {position.symbol} after {retry_attempts} attempts")
            
            # Logging final
            logger.info("🔄 ═══════════════════════════════════════════════════════════")
            logger.info("🔄 PRE-RESET CLOSURE COMPLETED")
            logger.info("🔄 ═══════════════════════════════════════════════════════════")
            logger.info(f"✅ Positions closed: {closed_count}")
            logger.info(f"❌ Failed closures: {failed_count}")
            logger.info(f"💰 Total profit crystallized: ${total_profit:.2f}")
            logger.info(f"📊 Average profit per position: {(sum(d['profit_pct'] for d in closure_details) / len(closure_details)):.2f}%" if closure_details else "N/A")
            logger.info("🔄 ═══════════════════════════════════════════════════════════")
            
            return {
                "status": "completed",
                "positions_closed": closed_count,
                "positions_failed": failed_count,
                "total_profit_usdt": total_profit,
                "closure_details": closure_details,
                "execution_time": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in pre-reset closure: {e}")
            return {"status": "error", "error": str(e), "positions_closed": 0}
    
    def should_execute_pre_reset_closure(self) -> bool:
        """🕐 Verificar si es momento de ejecutar el cierre pre-reset
        
        Returns:
            True si es momento de ejecutar el cierre
        """
        from src.config.global_constants import PRE_RESET_CLOSURE_CONFIG, DAILY_RESET_HOUR, DAILY_RESET_MINUTE
        import pytz
        from datetime import datetime, timedelta
        
        # Verificar si está habilitado
        if not PRE_RESET_CLOSURE_CONFIG.get("enabled", False):
            return False
        
        try:
            chile_tz = pytz.timezone("America/Santiago")
            current_time = datetime.now(chile_tz)
            
            # Calcular tiempo de reset
            reset_time = current_time.replace(
                hour=DAILY_RESET_HOUR, 
                minute=DAILY_RESET_MINUTE, 
                second=0, 
                microsecond=0
            )
            
            # Calcular tiempo de cierre
            minutes_before = PRE_RESET_CLOSURE_CONFIG.get("minutes_before_reset", 15)
            closure_time = reset_time - timedelta(minutes=minutes_before)
            
            # Verificar si estamos en la ventana de cierre (±1 minuto de tolerancia)
            time_diff = abs((current_time - closure_time).total_seconds())
            return time_diff <= 60  # 1 minuto de tolerancia
            
        except Exception as e:
            logger.error(f"❌ Error checking pre-reset closure timing: {e}")
            return False
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

# Importaciones locales
from src.config.main_config import TradingBotConfig, RiskManagerConfig, TradingProfiles

# Base de datos eliminada - usando Capital.com directamente
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
    - Integración con Capital.com API
    """

    def __init__(self, paper_trader: PaperTrader = None, capital_client=None):
        """
        Inicializar el gestor de posiciones

        Args:
            paper_trader: Instancia del paper trader para ejecutar órdenes
            capital_client: Cliente de Capital.com para operaciones reales
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.paper_trader = paper_trader or PaperTrader()
        self.capital_client = capital_client
        self.config = TradingBotConfig()
        self.risk_config = RiskManagerConfig()

        # Cache de posiciones para optimización
        self.positions_cache = {}
        self.last_cache_update = 0
        profile = TradingProfiles.get_current_profile()
        self.cache_duration = profile["position_check_interval"]  # segundos

        # Configuración de trailing stops desde RiskManagerConfig
        self.trailing_stop_activation = (
            self.risk_config.TRAILING_STOP_ACTIVATION
        )  # Ya en decimal
        self.trailing_stop_distance = profile[
            "default_trailing_distance"
        ]  # Ya en decimal

        # Estadísticas
        self.stats = {
            "positions_managed": 0,
            "tp_executed": 0,
            "sl_executed": 0,
            "trailing_stops_activated": 0,
            "total_pnl": 0.0,
        }

        logger.info("📊 Position Manager initialized")

    def get_active_positions(self, refresh_cache: bool = False) -> List[PositionInfo]:
        """📊 Obtener todas las posiciones activas

        Args:
            refresh_cache: Forzar actualización del cache

        Returns:
            Lista de posiciones activas
        """
        try:
            if not self.capital_client:
                logger.debug("📊 No Capital.com client available")
                return []

            # Obtener posiciones de Capital.com
            positions_result = self.capital_client.get_positions()
            if not positions_result.get("success"):
                logger.warning(
                    f"⚠️ Failed to get positions: {positions_result.get('error')}"
                )
                return []

            capital_positions = positions_result.get("positions", [])
            active_positions = []

            for position in capital_positions:
                try:
                    position_info = self._convert_capital_position_to_info(position)
                    if position_info:
                        active_positions.append(position_info)
                except Exception as e:
                    logger.error(f"❌ Error converting position: {e}")
                    continue

            logger.debug(f"📊 Found {len(active_positions)} active positions")
            return active_positions

        except Exception as e:
            logger.error(f"❌ Error getting active positions: {e}")
            return []

    # Método _create_position_info eliminado - las posiciones se obtienen directamente de Capital.com

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
                    position.unrealized_pnl = (
                        new_price - position.entry_price
                    ) * position.quantity
                    position.current_value = new_price * position.quantity
                else:  # SELL
                    position.unrealized_pnl = (
                        position.entry_price - new_price
                    ) * position.quantity
                    position.current_value = new_price * position.quantity

                position.unrealized_pnl_percentage = (
                    (position.unrealized_pnl / position.entry_value) * 100
                    if position.entry_value > 0
                    else 0
                )

                # Actualizar trailing stop si aplica
                self._update_trailing_stop(position)

                logger.debug(
                    f"💰 Updated position {trade_id}: {old_price:.4f} -> {new_price:.4f}"
                )
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
            profit_percentage = (
                position.unrealized_pnl_percentage / 100.0
            )  # Convertir porcentaje a decimal para comparación

            if profit_percentage >= self.trailing_stop_activation:
                # Calcular nuevo trailing stop
                new_trailing = position.current_price * (
                    1 - self.trailing_stop_distance
                )

                # Solo actualizar si es mejor que el trailing actual
                if (
                    position.trailing_stop is None
                    or new_trailing > position.trailing_stop
                ):
                    old_trailing = position.trailing_stop
                    position.trailing_stop = new_trailing

                    if old_trailing is None:
                        self.stats["trailing_stops_activated"] += 1
                        logger.info(
                            f"📈 Trailing stop activated for {position.symbol}: ${new_trailing:.4f}"
                        )
                    else:
                        logger.debug(
                            f"📈 Trailing stop updated for {position.symbol}: ${old_trailing:.4f} -> ${new_trailing:.4f}"
                        )

        except Exception as e:
            logger.error(
                f"❌ Error updating trailing stop for position {position.trade_id}: {e}"
            )

    def check_exit_conditions(self, position: PositionInfo) -> Optional[str]:
        """🎯 Verificar si una posición debe cerrarse

        Args:
            position: Información de la posición

        Returns:
            Razón de cierre o None si no debe cerrarse
        """
        try:
            current_price = position.current_price

            # 1. Verificar timeout de posición (nuevo parámetro)
            timeout_reason = self._check_position_timeout(position)
            if timeout_reason:
                return timeout_reason

            if position.trade_type == "BUY":
                # Verificar Take Profit (solo si está configurado)
                if (
                    position.take_profit is not None
                    and current_price >= position.take_profit
                ):
                    return "TAKE_PROFIT"

                # Verificar Stop Loss (solo si está configurado)
                if (
                    position.stop_loss is not None
                    and current_price <= position.stop_loss
                ):
                    return "STOP_LOSS"

                # Verificar Trailing Stop
                if (
                    position.trailing_stop is not None
                    and current_price <= position.trailing_stop
                ):
                    return "TRAILING_STOP"

            else:  # SELL
                # Verificar Take Profit (solo si está configurado)
                if (
                    position.take_profit is not None
                    and current_price <= position.take_profit
                ):
                    return "TAKE_PROFIT"

                # Verificar Stop Loss (solo si está configurado)
                if (
                    position.stop_loss is not None
                    and current_price >= position.stop_loss
                ):
                    return "STOP_LOSS"

            return None

        except Exception as e:
            logger.error(
                f"❌ Error checking exit conditions for position {position.trade_id}: {e}"
            )
            return None

    def close_position(self, trade_id: int, current_price: float, reason: str) -> bool:
        """🎯 Cerrar posición específica

        Args:
            trade_id: ID del trade a cerrar (dealId de Capital.com)
            current_price: Precio actual para el cierre
            reason: Razón del cierre

        Returns:
            True si se cerró correctamente
        """
        try:
            if not self.capital_client:
                logger.warning("⚠️ No Capital.com client available for closing position")
                return False

            # Convertir trade_id a string para Capital.com API
            deal_id = str(trade_id)

            # Cerrar posición usando Capital.com API
            result = self.capital_client.close_position(deal_id)

            if result.get("success"):
                # Handle both successful closes and "already closed" cases
                if result.get("error_type") == "already_closed":
                    logger.info(
                        f"🎯 Position {deal_id} was already closed - {result.get('message', 'Position resolved')}"
                    )
                else:
                    logger.info(
                        f"🎯 Position {deal_id} closed successfully by {reason} at ${current_price:.4f}"
                    )
                
                self.stats["positions_managed"] += 1

                # Actualizar estadísticas según la razón
                if "TAKE_PROFIT" in reason:
                    self.stats["tp_executed"] += 1
                elif "STOP_LOSS" in reason:
                    self.stats["sl_executed"] += 1
                elif "TRAILING_STOP" in reason:
                    self.stats["trailing_stops_activated"] += 1

                return True
            else:
                error_msg = result.get("error", "Unknown error")
                error_type = result.get("error_type", "unknown")
                
                # Handle specific error types gracefully
                if error_type == "already_closed":
                    logger.info(f"🎯 Position {deal_id} already closed - treating as success")
                    return True
                elif error_type == "session":
                    logger.warning(f"⚠️ Session error closing position {deal_id} - will retry later")
                    return False
                elif error_type == "network":
                    logger.warning(f"⚠️ Network error closing position {deal_id} - will retry later")
                    return False
                else:
                    logger.error(f"❌ Failed to close position {deal_id}: {error_msg}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error closing position {trade_id}: {e}")
            return False

    def process_position_timeouts(self) -> Dict[str, int]:
        """⏰ Procesar timeouts de posiciones activas

        Verifica todas las posiciones activas y cierra las que hayan excedido
        el tiempo límite configurado en position_timeout_hours.

        Returns:
            Diccionario con estadísticas del procesamiento
        """
        try:
            positions = self.get_active_positions()
            if not positions:
                return {
                    "total_positions": 0,
                    "timeout_positions": 0,
                    "closed_positions": 0,
                }

            timeout_positions = 0
            closed_positions = 0

            for position in positions:
                # Verificar si la posición debe cerrarse por timeout
                exit_reason = self.check_exit_conditions(position)

                if exit_reason == "POSITION_TIMEOUT":
                    timeout_positions += 1

                    # Intentar cerrar la posición
                    success = self.close_position(
                        trade_id=position.trade_id,
                        current_price=position.current_price,
                        reason=exit_reason,
                    )

                    if success:
                        closed_positions += 1
                        logger.info(
                            f"✅ Position {position.trade_id} ({position.symbol}) closed due to timeout"
                        )
                    else:
                        logger.error(
                            f"❌ Failed to close timeout position {position.trade_id} ({position.symbol})"
                        )

            result = {
                "total_positions": len(positions),
                "timeout_positions": timeout_positions,
                "closed_positions": closed_positions,
                "timestamp": datetime.now().isoformat(),
            }

            if timeout_positions > 0:
                logger.info(
                    f"⏰ Timeout processing completed: {closed_positions}/{timeout_positions} "
                    f"positions closed from {len(positions)} total"
                )

            return result

        except Exception as e:
            logger.error(f"❌ Error processing position timeouts: {e}")
            return {
                "total_positions": 0,
                "timeout_positions": 0,
                "closed_positions": 0,
                "error": str(e),
            }

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
                    "pnl": 0.0,
                }

            symbol_exposure[position.symbol]["value"] += position.current_value
            symbol_exposure[position.symbol]["positions"] += 1
            symbol_exposure[position.symbol]["pnl"] += position.unrealized_pnl

        return {
            "total_positions": len(positions),
            "total_exposure": total_exposure,
            "total_unrealized_pnl": total_unrealized_pnl,
            "symbol_breakdown": symbol_exposure,
            "timestamp": datetime.now().isoformat(),
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
            "last_cache_update": (
                datetime.fromtimestamp(self.last_cache_update).isoformat()
                if self.last_cache_update > 0
                else None
            ),
        }

    def calculate_atr_trailing_stop(
        self,
        symbol: str,
        current_price: float,
        trade_type: str,
        atr_multiplier: float = 2.0,
    ) -> Optional[float]:
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
        # Base de datos eliminada - trailing stops se gestionan directamente en Capital.com
        logger.debug(
            "🎯 Trailing stops simplificados - usando Capital.com directamente"
        )
        return 0

    def update_dynamic_take_profits(
        self, market_data: Dict[str, float], risk_manager=None
    ) -> int:
        """🎯 Actualizar take profits dinámicos para todas las posiciones activas

        Args:
            market_data: Diccionario con precios actuales {symbol: price}
            risk_manager: Instancia del risk manager para lógica de TP dinámico

        Returns:
            Número de take profits actualizados
        """
        # Simplificado - los take profits dinámicos se gestionan directamente en Capital.com
        logger.debug(
            "🎯 Take profits dinámicos simplificados - usando Capital.com directamente"
        )
        return 0

    def _calculate_dynamic_take_profit(
        self, position: "PositionInfo", current_price: float, current_profit_pct: float
    ) -> Optional[float]:
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
            elif (
                current_profit_pct >= tp_max * 0.67
            ):  # 2/3 del tp_max o más de ganancia
                tp_increment_pct = tp_max * 0.5  # Incrementar TP en 1/2 del máximo
            elif (
                current_profit_pct >= tp_min * 0.67
            ):  # 2/3 del tp_min o más de ganancia
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
            logger.error(
                f"❌ Error calculating dynamic take profit for {position.symbol}: {e}"
            )
            return None

    def _check_position_timeout(self, position: PositionInfo) -> Optional[str]:
        """⏰ Verificar si una posición ha excedido el tiempo límite

        Args:
            position: Información de la posición

        Returns:
            Razón de cierre por timeout o None si no debe cerrarse
        """
        try:
            # Obtener configuración del perfil actual
            profile = TradingProfiles.get_current_profile()
            position_timeout_hours = profile.get(
                "position_timeout_hours", 6
            )  # Default 6 horas
            min_movement_threshold = profile.get(
                "min_movement_threshold", 0.005
            )  # Default 0.5%

            # Calcular tiempo transcurrido desde la entrada
            current_time = datetime.now()

            # Verificar que entry_time no sea None
            if position.entry_time is None:
                logger.warning(
                    f"⚠️ Position {position.trade_id} has no entry_time, skipping timeout check"
                )
                return None

            time_elapsed = current_time - position.entry_time
            hours_elapsed = time_elapsed.total_seconds() / 3600

            # Solo verificar timeout si han pasado las horas configuradas
            if hours_elapsed >= position_timeout_hours:
                # Calcular movimiento de la posición
                price_movement = (
                    abs(position.current_price - position.entry_price)
                    / position.entry_price
                )

                # Si el movimiento es menor al umbral mínimo, cerrar por timeout
                if price_movement < min_movement_threshold:
                    logger.info(
                        f"⏰ Position {position.trade_id} ({position.symbol}) timeout: "
                        f"{hours_elapsed:.1f}h elapsed, only {price_movement*100:.2f}% movement "
                        f"(threshold: {min_movement_threshold*100:.2f}%)"
                    )
                    return "POSITION_TIMEOUT"
                else:
                    logger.debug(
                        f"⏰ Position {position.trade_id} ({position.symbol}) has sufficient movement: "
                        f"{price_movement*100:.2f}% > {min_movement_threshold*100:.2f}% threshold"
                    )

            return None

        except Exception as e:
            logger.error(
                f"❌ Error checking position timeout for {position.trade_id}: {e}"
            )
            return None

    # Métodos _calculate_max_profit y _calculate_max_loss eliminados -
    # las métricas se calculan directamente desde Capital.com

    def _convert_capital_position_to_info(
        self, capital_position: dict
    ) -> Optional[PositionInfo]:
        """🔄 Convertir posición de Capital.com a PositionInfo

        Args:
            capital_position: Posición desde Capital.com API

        Returns:
            PositionInfo o None si hay error
        """
        try:
            # Extraer datos anidados de position y market
            position_data = capital_position.get("position", {})
            market_data = capital_position.get("market", {})

            # Usar 'epic' del market para el símbolo
            symbol = market_data.get("epic", "")

            # Si no hay epic, intentar con instrumentName como fallback
            if not symbol:
                symbol = market_data.get("instrumentName", "")

            # Extraer datos de la posición usando la estructura correcta
            entry_price = float(
                position_data.get("level", 0)
            )  # level es el precio de entrada
            current_price = float(
                market_data.get("bid", 0)
            )  # usar bid como precio actual
            quantity = float(position_data.get("size", 0))
            pnl = float(position_data.get("upl", 0))  # Unrealized P&L
            direction = position_data.get("direction", "BUY")
            created_date = position_data.get("createdDateUTC")

            # Validar entry_price
            if entry_price <= 0:
                self.logger.warning(
                    f"⚠️ Invalid entry_price={entry_price} for {symbol}, using current_price as fallback"
                )
                entry_price = current_price

            self.logger.debug(
                f"💰 Using entry_price={entry_price:.4f} for {symbol} ({direction})"
            )

            # Convertir dealId (puede ser hexadecimal) a hash numérico
            deal_id_str = position_data.get("dealId", "0")
            trade_id = hash(deal_id_str) % (
                10**10
            )  # Convertir a número positivo de 10 dígitos

            position_info = PositionInfo(
                trade_id=trade_id,
                symbol=symbol,
                trade_type=direction,
                entry_price=entry_price,
                current_price=current_price,
                quantity=quantity,
                entry_value=quantity * entry_price,
                current_value=quantity * current_price,
                unrealized_pnl=pnl,
                unrealized_pnl_percentage=0.0,  # Se calculará después
                stop_loss=(
                    float(position_data.get("stopLevel"))
                    if position_data.get("stopLevel")
                    else None
                ),
                take_profit=(
                    float(position_data.get("profitLevel"))
                    if position_data.get("profitLevel")
                    else None
                ),
                trailing_stop=None,  # Capital.com no expone trailing stops directamente
                entry_time=self._parse_capital_time(
                    position_data.get("createdDateUTC")
                ),
                strategy_name="Capital.com",
                confidence_score=0.0,
                timeframe="Unknown",
                notes=f"Deal ID: {position_data.get('dealId')}",
                days_held=0.0,  # Se calculará después
                max_profit=0.0,
                max_loss=0.0,
                risk_reward_ratio=0.0,  # Se calculará después si hay SL/TP
            )

            # Calcular PnL percentage
            if position_info.entry_value > 0:
                position_info.unrealized_pnl_percentage = (
                    position_info.unrealized_pnl / position_info.entry_value
                ) * 100

            # Calcular días mantenida
            if position_info.entry_time:
                time_diff = datetime.now() - position_info.entry_time
                position_info.days_held = time_diff.total_seconds() / (24 * 3600)

            # Calcular risk_reward_ratio si hay SL y TP
            if position_info.stop_loss and position_info.take_profit:
                if position_info.trade_type == "BUY":
                    risk = abs(position_info.entry_price - position_info.stop_loss)
                    reward = abs(position_info.take_profit - position_info.entry_price)
                else:  # SELL
                    risk = abs(position_info.stop_loss - position_info.entry_price)
                    reward = abs(position_info.entry_price - position_info.take_profit)

                if risk > 0:
                    position_info.risk_reward_ratio = reward / risk

            return position_info

        except Exception as e:
            logger.error(f"❌ Error converting Capital.com position: {e}")
            logger.debug(f"Position data: {capital_position}")
            return None

    def _parse_capital_time(self, time_str: str) -> Optional[datetime]:
        """🕐 Parsear tiempo de Capital.com

        Args:
            time_str: String de tiempo de Capital.com

        Returns:
            datetime o None si hay error
        """
        try:
            if not time_str:
                self.logger.warning(f"⚠️ Empty time string received")
                return None

            # Capital.com usa formato ISO con Z
            if time_str.endswith("Z"):
                time_str = time_str[:-1] + "+00:00"

            parsed_time = datetime.fromisoformat(time_str)
            self.logger.debug(f"✅ Successfully parsed time: {parsed_time}")
            return parsed_time

        except Exception as e:
            self.logger.error(f"❌ Error parsing Capital.com time '{time_str}': {e}")
            return None

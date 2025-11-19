"""
🎭 Universal Trading Analyzer - Paper Trader (Simplificado)
Ejecutor de trades virtuales sin base de datos - usando Capital.com directamente
"""

from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
import random

# Importar configuración
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.main_config import (
    PaperTraderConfig,
    TradingBotConfig,
    USD_BASE_PRICE,
    TRADING_FEES,
    PRODUCTION_MODE,
    PAPER_TRADING_ONLY,
    ENABLE_REAL_TRADING,
    VERBOSE_LOGGING,
)
from src.config.time_trading_config import (
    is_smart_trading_hours_allowed,
    _detect_market_type,
)

# Asegurar conversión a float consistente desde configuración
FEE_RATE: float = float(TRADING_FEES)

# Evitar import en tiempo de ejecución para no arrastrar dependencias pesadas
if TYPE_CHECKING:
    from .enhanced_strategies import TradingSignal

# Configurar logging basado en modo de operación
log_level = logging.DEBUG if VERBOSE_LOGGING else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    """
    📊 Resultado de una operación de trading
    """

    success: bool
    trade_id: Optional[int]
    message: str
    entry_price: float
    quantity: float
    entry_value: float


class PaperTrader:
    """
    🎭 Paper Trader Simplificado - Sin base de datos

    Características:
    - Gestión automática de portfolio en memoria
    - Risk management integrado
    - Tracking básico de trades
    - Cálculo de P&L en tiempo real
    """

    def __init__(
        self,
        initial_balance: float = None,
        initial_positions: Dict = None,
        capital_client=None,
    ):
        """
        Inicializar Paper Trader

        Args:
            initial_balance: Balance inicial en USD (opcional, usa config si no se especifica)
            initial_positions: Posiciones iniciales de Capital.com para sincronizar (opcional)
            capital_client: Cliente de Capital.com para obtener valores reales (opcional)
        """
        # Configuración del paper trader desde archivo centralizado
        self.config = PaperTraderConfig()
        # Balance inicial desde configuración o parámetro
        default_balance = 0.0  # Balance por defecto
        self.initial_balance = (
            initial_balance if initial_balance is not None else default_balance
        )
        self.max_position_size = self.config.get_max_position_size()
        self.max_total_exposure = self.config.get_max_total_exposure()
        self.min_trade_value = self.config.get_min_trade_value()
        self.max_balance_usage = self.config.MAX_BALANCE_USAGE
        self.min_confidence_threshold = self.config.get_min_confidence_threshold()

        # Portfolio en memoria (simplificado)
        self.portfolio = {
            "USD": {
                "quantity": self.initial_balance,
                "avg_price": 1.0,
                "current_price": 1.0,
                "current_value": self.initial_balance,
                "unrealized_pnl": 0.0,
                "unrealized_pnl_percentage": 0.0,
                "last_updated": datetime.now(),
            }
        }

        # Configurar logging basado en modo de operación
        log_level = logging.DEBUG if VERBOSE_LOGGING else logging.INFO
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)

        # Sincronizar posiciones iniciales de Capital.com si se proporcionan
        if initial_positions:
            self._sync_initial_positions(initial_positions, capital_client)

        # Historial de trades en memoria
        self.trades = []
        self.trade_counter = 1

        # Verificaciones de modo de operación
        if PRODUCTION_MODE:
            if not PAPER_TRADING_ONLY:
                self.logger.warning("⚠️  PRODUCTION MODE: Paper trading is disabled!")
            if ENABLE_REAL_TRADING:
                self.logger.warning("⚠️  PRODUCTION MODE: Real trading is enabled!")
            self.logger.info("🏭 Running in PRODUCTION MODE")
        else:
            self.logger.info("🧪 Running in DEVELOPMENT MODE")

        self.logger.info(
            f"🎭 Paper Trader initialized with ${self.initial_balance:,.2f}"
        )

    def _sync_initial_positions(self, capital_positions: Dict, capital_client=None):
        """
        🔄 Sincronizar posiciones iniciales de Capital.com con el paper trader

        Args:
            capital_positions: Diccionario con posiciones de Capital.com
            capital_client: Cliente de Capital.com para obtener valores reales
        """
        try:
            synced_positions = 0
            real_available_balance = None
            real_equity = None
            real_pnl = None

            # Obtener valores reales de Capital.com si el cliente está disponible
            if capital_client and hasattr(capital_client, "get_available_balance"):
                try:
                    balance_info = capital_client.get_available_balance()
                    if balance_info.get("success"):
                        real_available_balance = float(balance_info.get("available", 0))
                        real_equity = float(balance_info.get("balance", 0))
                        real_pnl = float(balance_info.get("profit_loss", 0))

                        self.logger.info(f"💰 Valores reales de Capital.com:")
                        self.logger.info(f"   Available: ${real_available_balance:.2f}")
                        self.logger.info(f"   Equity: ${real_equity:.2f}")
                        self.logger.info(f"   P&L: ${real_pnl:.2f}")
                except Exception as e:
                    self.logger.warning(
                        f"⚠️ No se pudieron obtener valores reales de Capital.com: {e}"
                    )

            for symbol, position_data in capital_positions.items():
                direction = position_data.get("direction", "").upper()
                size = float(position_data.get("size", 0))
                avg_price = float(position_data.get("level", 0))

                if size == 0 or avg_price == 0:
                    continue

                # En CFDs, BUY = posición larga (cantidad positiva), SELL = posición corta (cantidad negativa)
                if direction == "BUY":
                    quantity = size  # Posición larga
                elif direction == "SELL":
                    quantity = -size  # Posición corta (cantidad negativa)
                else:
                    self.logger.warning(
                        f"⚠️ Dirección desconocida para {symbol}: {direction}"
                    )
                    continue

                # Calcular valor de la posición
                position_value = abs(quantity) * avg_price

                # Agregar posición al portfolio del paper trader
                self.portfolio[symbol] = {
                    "quantity": quantity,
                    "avg_price": avg_price,
                    "current_price": avg_price,  # Se actualizará con precios reales
                    "current_value": position_value,
                    "unrealized_pnl": 0.0,
                    "unrealized_pnl_percentage": 0.0,
                    "last_updated": datetime.now(),
                }

                synced_positions += 1
                position_type = "LONG" if quantity > 0 else "SHORT"
                self.logger.info(
                    f"🔄 Sincronizada posición {position_type}: {abs(quantity):.6f} {symbol} @ ${avg_price:.2f}"
                )

            # Usar valores reales de Capital.com si están disponibles
            if real_available_balance is not None and real_equity is not None:
                # Usar el balance disponible real de Capital.com
                self.portfolio["USD"]["quantity"] = real_available_balance
                self.portfolio["USD"]["current_value"] = real_available_balance

                # Guardar valores reales para cálculos de portfolio
                self._real_equity = real_equity
                self._real_pnl = real_pnl

                self.logger.info(
                    f"✅ Sincronizadas {synced_positions} posiciones de Capital.com con paper trader"
                )
                self.logger.info(f"💰 Balance USD real: ${real_available_balance:.2f}")
                self.logger.info(f"📈 Equity real: ${real_equity:.2f}")
                self.logger.info(f"💵 P&L real: ${real_pnl:.2f}")
            else:
                # Fallback: usar cálculo anterior si no hay valores reales
                total_portfolio_value = sum(
                    abs(pos["quantity"]) * pos["avg_price"]
                    for symbol, pos in self.portfolio.items()
                    if symbol != "USD"
                )
                adjusted_usd_balance = max(
                    self.initial_balance, total_portfolio_value * 0.2
                )

                self.portfolio["USD"]["quantity"] = adjusted_usd_balance
                self.portfolio["USD"]["current_value"] = adjusted_usd_balance

                self.logger.info(
                    f"✅ Sincronizadas {synced_positions} posiciones de Capital.com con paper trader"
                )
                self.logger.info(
                    f"💰 Valor total del portfolio calculado: ${total_portfolio_value:.2f}"
                )
                self.logger.info(
                    f"💵 Balance USD ajustado: ${adjusted_usd_balance:.2f}"
                )

            if synced_positions == 0:
                self.logger.info(
                    "ℹ️ No hay posiciones activas en Capital.com para sincronizar"
                )

        except Exception as e:
            self.logger.error(f"❌ Error sincronizando posiciones iniciales: {e}")
            # No fallar la inicialización por este error

    def reset_portfolio(self) -> Dict:
        """
        🔄 Resetear el portfolio a los valores por defecto

        Returns:
            Dict con el resultado del reset
        """
        try:
            # Resetear portfolio a valores iniciales
            self.portfolio = {
                "USD": {
                    "quantity": self.initial_balance,
                    "avg_price": 1.0,
                    "current_price": 1.0,
                    "current_value": self.initial_balance,
                    "unrealized_pnl": 0.0,
                    "unrealized_pnl_percentage": 0.0,
                    "last_updated": datetime.now(),
                }
            }

            # Limpiar historial de trades
            self.trades = []
            self.trade_counter = 1

            self.logger.info(f"🔄 Portfolio reset to ${self.initial_balance:,.2f}")

            return {
                "success": True,
                "message": f"Portfolio reset successfully to ${self.initial_balance:,.2f}",
                "initial_balance": self.initial_balance,
                "current_balance": self.initial_balance,
            }

        except Exception as e:
            self.logger.error(f"❌ Error resetting portfolio: {e}")
            return {
                "success": False,
                "message": f"Error resetting portfolio: {e}",
                "initial_balance": self.initial_balance,
                "current_balance": self.get_balance(),
            }

    def execute_signal(self, signal: "TradingSignal") -> TradeResult:
        """
        🎯 Ejecutar una señal de trading

        Args:
            signal: Señal de trading a ejecutar

        Returns:
            TradeResult con el resultado de la operación
        """
        try:
            # Validar señal
            if not self._validate_signal(signal):
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message="Signal validation failed",
                    entry_price=signal.price,
                    quantity=0.0,
                    entry_value=0.0,
                )

            # 🕐 Validar horarios inteligentes por tipo de mercado
            market_type = _detect_market_type(signal.symbol)
            trading_hours_result = is_smart_trading_hours_allowed(signal.symbol)
            is_allowed = trading_hours_result.get("is_allowed", True)
            reason = trading_hours_result.get("reason", "Unknown reason")

            if not is_allowed:
                self.logger.info(f"⏰ {signal.symbol} ({market_type}): {reason}")
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message=f"Trading not allowed: {reason}",
                    entry_price=signal.price,
                    quantity=0.0,
                    entry_value=0.0,
                )

            # Ejecutar según el tipo de señal
            if signal.signal_type.upper() == "BUY":
                return self._execute_buy(signal)
            elif signal.signal_type.upper() == "SELL":
                return self._execute_sell(signal)
            else:
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message=f"Unknown signal_type: {signal.signal_type}",
                    entry_price=signal.price,
                    quantity=0.0,
                    entry_value=0.0,
                )

        except Exception as e:
            self.logger.error(f"❌ Error executing signal: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Error executing signal: {e}",
                entry_price=signal.price if hasattr(signal, "price") else 0.0,
                quantity=0.0,
                entry_value=0.0,
            )

    def _validate_signal(self, signal: "TradingSignal") -> bool:
        """
        ✅ Validar una señal de trading

        Args:
            signal: Señal a validar

        Returns:
            bool: True si la señal es válida
        """
        try:
            # Validaciones básicas
            if (
                not hasattr(signal, "symbol")
                or not signal.symbol
                or not signal.symbol.strip()
            ):
                self.logger.warning("❌ Signal missing or empty symbol")
                return False

            if not hasattr(signal, "signal_type") or not signal.signal_type:
                self.logger.warning("❌ Signal missing signal_type")
                return False

            # Validar signal_type
            if signal.signal_type.upper() not in ["BUY", "SELL"]:
                self.logger.warning(
                    f"❌ Invalid signal_type: {signal.signal_type}. Must be BUY or SELL"
                )
                return False

            # Validación robusta de precio
            if not hasattr(signal, "price"):
                self.logger.warning("❌ Signal missing price")
                return False

            # Verificar que el precio sea un número válido
            try:
                price = float(signal.price)
                if price <= 0:
                    self.logger.warning(f"❌ Signal price must be positive: {price}")
                    return False
                if not isinstance(price, (int, float)) or price != price:  # NaN check
                    self.logger.warning(f"❌ Signal price is NaN: {signal.price}")
                    return False
                if price == float("inf") or price == float("-inf"):
                    self.logger.warning(f"❌ Signal price is infinite: {price}")
                    return False
            except (ValueError, TypeError):
                self.logger.warning(
                    f"❌ Signal price is not a valid number: {signal.price}"
                )
                return False

            # Validación de confidence_score
            if not hasattr(signal, "confidence_score"):
                self.logger.warning("❌ Signal missing confidence_score")
                return False

            try:
                confidence = float(signal.confidence_score)
                if confidence < 0 or confidence > 100:
                    self.logger.warning(
                        f"❌ Signal confidence_score out of range: {confidence}. Must be between 0-100"
                    )
                    return False
                if confidence < self.min_confidence_threshold:
                    self.logger.warning(
                        f"❌ Signal confidence too low: {confidence} < {self.min_confidence_threshold}"
                    )
                    return False
            except (ValueError, TypeError):
                self.logger.warning(
                    f"❌ Signal confidence_score is not a valid number: {signal.confidence_score}"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Error validating signal: {e}")
            return False

    def _execute_buy(self, signal: "TradingSignal") -> TradeResult:
        """
        📈 Ejecutar una orden de compra (CFD - Posición Larga)

        En CFDs, BUY significa abrir una posición larga (apostar que el precio sube)
        o cerrar una posición corta existente.

        Args:
            signal: Señal de compra

        Returns:
            TradeResult con el resultado de la operación
        """
        try:
            symbol = signal.symbol
            price = signal.price

            # En CFDs, verificar si ya tenemos una posición abierta
            if symbol in self.portfolio:
                position = self.portfolio[symbol]
                current_quantity = position["quantity"]

                # Si ya tenemos posición corta, cerrarla primero y luego abrir larga
                if current_quantity < 0:
                    close_result = self._close_short_position(symbol, price)
                    if not close_result.success:
                        return close_result
                    # Abrir nueva posición larga después de cerrar la corta
                    return self._open_long_position(symbol, price)
                # Si ya tenemos posición larga, aumentarla según la estrategia
                elif current_quantity > 0:
                    return self._increase_long_position(symbol, price)

            # Abrir nueva posición larga (CFD BUY)
            return self._open_long_position(symbol, price)

        except Exception as e:
            self.logger.error(f"❌ Error executing buy: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Error executing buy: {e}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0,
            )

    def _close_short_position(self, symbol: str, price: float) -> TradeResult:
        """🔄 Cerrar posición corta existente"""
        position = self.portfolio[symbol]
        quantity = abs(position["quantity"])  # Convertir a positivo
        entry_price = position["avg_price"]

        # En posición corta, ganamos cuando el precio baja
        # P&L = (precio_entrada - precio_salida) * cantidad
        entry_value = quantity * entry_price
        exit_value = quantity * price
        gross_pnl = entry_value - exit_value  # Invertido para posición corta
        fee = exit_value * FEE_RATE
        net_pnl = gross_pnl - fee

        # Actualizar portfolio (liberar margen y agregar P&L)
        # Liberar margen reservado y sumar PnL neto
        reserved_margin = position.get("reserved_margin", 0.0)
        self._update_usd_balance(reserved_margin + net_pnl)
        # Eliminar posición (cantidad positiva para cancelar negativa)
        self._update_asset_balance(symbol, quantity, price)

        # Crear registro de trade
        trade_id = self.trade_counter
        self.trade_counter += 1

        trade_record = {
            "id": trade_id,
            "symbol": symbol,
            "trade_type": "BUY_CLOSE_SHORT",
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_price": price,
            "exit_value": exit_value,
            "fee": fee,
            "pnl": net_pnl,
            "status": "CLOSED",
            "exit_time": datetime.now(),
            "is_paper_trade": True,
            "notes": f"Paper trade CLOSE SHORT {symbol} | PnL: ${net_pnl:.2f}",
        }

        self.trades.append(trade_record)

        pnl_sign = "+" if net_pnl >= 0 else ""
        self.logger.info(
            f"✅ CLOSE SHORT: {quantity:.6f} {symbol} @ ${price:.2f} | PnL: {pnl_sign}${net_pnl:.2f} (Trade #{trade_id})"
        )

        return TradeResult(
            success=True,
            trade_id=trade_id,
            message=f"SHORT position closed | PnL: {pnl_sign}${net_pnl:.2f}",
            entry_price=price,
            quantity=quantity,
            entry_value=exit_value,
        )

    def _open_long_position(self, symbol: str, price: float) -> TradeResult:
        """📈 Abrir nueva posición larga (CFD BUY)"""
        # Calcular cantidad basada en el tamaño máximo de posición
        usd_balance = self.get_balance("USD")
        max_trade_value = min(
            usd_balance * self.max_balance_usage,
            usd_balance * self.max_position_size,  # Corregido: multiplicar por balance
        )

        # 🔄 SINCRONIZACIÓN: Usar la misma lógica que el real trader
        # Considerar apalancamiento típico de Capital.com (1:5 para crypto, 1:10 para forex)
        # Para simplificar, usamos apalancamiento promedio de 1:5
        leverage = 5.0
        required_margin = max_trade_value / leverage

        # Validar margen requerido en lugar de valor mínimo fijo
        # Esto sincroniza con la validación del real trader
        if required_margin > usd_balance:
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Insufficient balance for margin. Required: ${required_margin:,.2f}, Available: ${usd_balance:,.2f} (Position value: ${max_trade_value:,.2f} with {leverage}x leverage)",
                entry_price=price,
                quantity=0.0,
                entry_value=0.0,
            )

        # Validar tamaño mínimo de posición (0.01 unidades como en Capital.com)
        quantity = max_trade_value / price
        if quantity < 0.01:
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Position size too small: {quantity:.4f} units (minimum: 0.01)",
                entry_price=price,
                quantity=0.0,
                entry_value=0.0,
            )

        # Calcular cantidad y fees (quantity ya calculada arriba)
        fee = max_trade_value * FEE_RATE
        total_margin_required = (
            required_margin + fee
        )  # Usar el margen ya calculado con apalancamiento
        # Nota: La validación principal de margen ya se hizo arriba con apalancamiento

        # Actualizar portfolio (reservar margen)
        self._update_usd_balance(-total_margin_required)
        self._update_asset_balance(symbol, quantity, price)
        # Guardar metadata de margen y exposición para cierres consistentes
        try:
            self.portfolio[symbol]["reserved_margin"] = required_margin
            self.portfolio[symbol]["leverage"] = leverage
            self.portfolio[symbol]["entry_value"] = max_trade_value
        except Exception:
            pass

        # Crear registro de trade
        trade_id = self.trade_counter
        self.trade_counter += 1

        trade_record = {
            "id": trade_id,
            "symbol": symbol,
            "trade_type": "BUY_OPEN_LONG",
            "quantity": quantity,
            "entry_price": price,
            "entry_value": max_trade_value,
            "fee": fee,
            "status": "OPEN",
            "entry_time": datetime.now(),
            "is_paper_trade": True,
            "notes": f"Paper trade OPEN LONG {symbol}",
        }

        self.trades.append(trade_record)

        self.logger.info(
            f"✅ OPEN LONG: {quantity:.6f} {symbol} @ ${price:.2f} (Trade #{trade_id})"
        )

        return TradeResult(
            success=True,
            trade_id=trade_id,
            message=f"LONG position opened successfully",
            entry_price=price,
            quantity=quantity,
            entry_value=max_trade_value,
        )

    def _increase_long_position(self, symbol: str, price: float) -> TradeResult:
        """📈 Aumentar posición larga existente"""
        # Por simplicidad, por ahora cerramos la posición existente y abrimos una nueva
        # En el futuro se puede implementar lógica más sofisticada
        return self._open_long_position(symbol, price)

    def _execute_sell(self, signal: "TradingSignal") -> TradeResult:
        """
        📉 Ejecutar una orden de venta (CFD - Posición Corta)

        En CFDs, SELL significa abrir una posición corta (apostar que el precio baja)
        No necesitas tener el activo para vender.

        Args:
            signal: Señal de venta

        Returns:
            TradeResult con el resultado de la operación
        """
        try:
            symbol = signal.symbol
            price = signal.price

            # En CFDs, verificar si ya tenemos una posición abierta
            if symbol in self.portfolio:
                position = self.portfolio[symbol]
                current_quantity = position["quantity"]

                # Si ya tenemos posición larga, cerrarla primero y luego abrir corta
                if current_quantity > 0:
                    close_result = self._close_long_position(symbol, price)
                    if not close_result.success:
                        return close_result
                    # Abrir nueva posición corta después de cerrar la larga
                    return self._open_short_position(symbol, price)
                # Si ya tenemos posición corta, aumentarla según la estrategia
                elif current_quantity < 0:
                    return self._increase_short_position(symbol, price)

            # Abrir nueva posición corta (CFD SELL)
            return self._open_short_position(symbol, price)

        except Exception as e:
            self.logger.error(f"❌ Error executing sell: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Error executing sell: {e}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0,
            )

    def _close_long_position(self, symbol: str, price: float) -> TradeResult:
        """🔄 Cerrar posición larga existente"""
        position = self.portfolio[symbol]
        quantity = position["quantity"]
        entry_price = position["avg_price"]

        # Calcular P&L
        sale_value = quantity * price
        entry_value = quantity * entry_price
        gross_pnl = sale_value - entry_value
        fee = sale_value * FEE_RATE
        net_pnl = gross_pnl - fee

        # Actualizar portfolio: liberar margen y sumar PnL neto (no sumar valor nominal)
        reserved_margin = position.get("reserved_margin", 0.0)
        self._update_usd_balance(reserved_margin + net_pnl)
        # Eliminar posición
        self._update_asset_balance(symbol, -quantity, price)

        # Crear registro de trade
        trade_id = self.trade_counter
        self.trade_counter += 1

        trade_record = {
            "id": trade_id,
            "symbol": symbol,
            "trade_type": "SELL_CLOSE_LONG",
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_price": price,
            "exit_value": sale_value,
            "fee": fee,
            "pnl": net_pnl,
            "status": "CLOSED",
            "exit_time": datetime.now(),
            "is_paper_trade": True,
            "notes": f"Paper trade CLOSE LONG {symbol} | PnL: ${net_pnl:.2f}",
        }

        self.trades.append(trade_record)

        pnl_sign = "+" if net_pnl >= 0 else ""
        self.logger.info(
            f"✅ CLOSE LONG: {quantity:.6f} {symbol} @ ${price:.2f} | PnL: {pnl_sign}${net_pnl:.2f} (Trade #{trade_id})"
        )

        return TradeResult(
            success=True,
            trade_id=trade_id,
            message=f"LONG position closed | PnL: {pnl_sign}${net_pnl:.2f}",
            entry_price=price,
            quantity=quantity,
            entry_value=sale_value,
        )

    def _open_short_position(self, symbol: str, price: float) -> TradeResult:
        """📉 Abrir nueva posición corta (CFD SELL)"""
        # Calcular cantidad basada en el tamaño máximo de posición
        usd_balance = self.get_balance("USD")
        max_trade_value = min(
            usd_balance * self.max_balance_usage,
            usd_balance * self.max_position_size,  # Corregido: multiplicar por balance
        )

        # 🔄 SINCRONIZACIÓN: Usar la misma lógica que el real trader
        # Considerar apalancamiento típico de Capital.com (1:5 para crypto, 1:10 para forex)
        # Para simplificar, usamos apalancamiento promedio de 1:5
        leverage = 5.0
        required_margin = max_trade_value / leverage

        # Validar margen requerido en lugar de valor mínimo fijo
        # Esto sincroniza con la validación del real trader
        if required_margin > usd_balance:
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Insufficient balance for margin. Required: ${required_margin:,.2f}, Available: ${usd_balance:,.2f} (Position value: ${max_trade_value:,.2f} with {leverage}x leverage)",
                entry_price=price,
                quantity=0.0,
                entry_value=0.0,
            )

        # Validar tamaño mínimo de posición (0.01 unidades como en Capital.com)
        quantity_abs = max_trade_value / price
        if quantity_abs < 0.01:
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Position size too small: {quantity_abs:.4f} units (minimum: 0.01)",
                entry_price=price,
                quantity=0.0,
                entry_value=0.0,
            )

        # En posición corta, la cantidad es negativa
        quantity = -quantity_abs  # Negativo para indicar posición corta
        fee = max_trade_value * FEE_RATE
        # Nota: La validación de margen ya se hizo arriba con apalancamiento

        # Actualizar portfolio (reservar margen)
        total_margin_required = required_margin + fee
        self._update_usd_balance(-total_margin_required)
        self._update_asset_balance(symbol, quantity, price)  # Cantidad negativa
        # Guardar metadata de margen y exposición para cierres consistentes
        try:
            self.portfolio[symbol]["reserved_margin"] = required_margin
            self.portfolio[symbol]["leverage"] = leverage
            self.portfolio[symbol]["entry_value"] = max_trade_value
        except Exception:
            pass

        # Crear registro de trade
        trade_id = self.trade_counter
        self.trade_counter += 1

        trade_record = {
            "id": trade_id,
            "symbol": symbol,
            "trade_type": "SELL_OPEN_SHORT",
            "quantity": abs(quantity),  # Guardar como positivo en el registro
            "entry_price": price,
            "entry_value": max_trade_value,
            "fee": fee,
            "status": "OPEN",
            "entry_time": datetime.now(),
            "is_paper_trade": True,
            "notes": f"Paper trade OPEN SHORT {symbol}",
        }

        self.trades.append(trade_record)

        self.logger.info(
            f"✅ OPEN SHORT: {abs(quantity):.6f} {symbol} @ ${price:.2f} (Trade #{trade_id})"
        )

        return TradeResult(
            success=True,
            trade_id=trade_id,
            message=f"SHORT position opened successfully",
            entry_price=price,
            quantity=abs(quantity),
            entry_value=max_trade_value,
        )

    def _increase_short_position(self, symbol: str, price: float) -> TradeResult:
        """📉 Aumentar posición corta existente"""
        # Por simplicidad, por ahora cerramos la posición existente y abrimos una nueva
        # En el futuro se puede implementar lógica más sofisticada
        return self._open_short_position(symbol, price)

    def get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio

        Returns:
            Dict con el resumen del portfolio
        """
        try:
            # Calcular PnL no realizado sobre posiciones (excluyendo USD)
            total_pnl = sum(
                pos["unrealized_pnl"]
                for symbol, pos in self.portfolio.items()
                if symbol != "USD"
            )
            # Equity simulado: USD disponible + PnL no realizado
            usd_value = self.portfolio.get("USD", {}).get("current_value", 0.0)
            total_value = usd_value + total_pnl
            funds_balance = usd_value  # Fondos (sin P&L), equivalente a saldo disponible en cash

            # Crear lista de assets (posiciones abiertas)
            assets = []
            for symbol, position in self.portfolio.items():
                if symbol != "USD" and position["quantity"] != 0:
                    assets.append(
                        {
                            "symbol": symbol,
                            "quantity": position["quantity"],
                            "avg_price": position["avg_price"],
                            "current_price": position["current_price"],
                            "current_value": position["current_value"],
                            "unrealized_pnl": position["unrealized_pnl"],
                            "unrealized_pnl_percentage": position[
                                "unrealized_pnl_percentage"
                            ],
                        }
                    )

            return {
                "total_value": total_value,
                "funds_balance": funds_balance,
                "initial_balance": self.initial_balance,
                "available_balance": self.portfolio.get("USD", {}).get("quantity", 0.0),
                "total_pnl": total_pnl,
                "total_pnl_percentage": (
                    (total_pnl / self.initial_balance) * 100
                    if self.initial_balance > 0
                    else 0.0
                ),
                "positions": len(
                    [pos for pos in self.portfolio.values() if pos["quantity"] != 0]
                ),
                "assets": assets,
                "last_updated": datetime.now(),
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting portfolio summary: {e}")
            return {
                "total_value": self.initial_balance,
                "initial_balance": self.initial_balance,
                "available_balance": self.initial_balance,
                "total_pnl": 0.0,
                "total_pnl_percentage": 0.0,
                "positions": 0,
                "assets": [],
                "last_updated": datetime.now(),
            }

    def get_balance(self, symbol: str = "USD") -> float:
        """
        💰 Obtener balance de un símbolo específico

        Args:
            symbol: Símbolo del asset (default: USD)

        Returns:
            float: Balance disponible
        """
        try:
            if symbol in self.portfolio:
                return self.portfolio[symbol]["quantity"]
            return 0.0
        except Exception as e:
            self.logger.error(f"❌ Error getting balance for {symbol}: {e}")
            return 0.0

    @property
    def balance(self) -> float:
        """
        💰 Propiedad para obtener el balance USD actual

        Returns:
            float: Balance USD disponible
        """
        return self.get_balance("USD")

    def _update_usd_balance(self, amount: float):
        """
        💵 Actualizar balance de USD

        Args:
            amount: Cantidad a agregar/quitar (puede ser negativa)
        """
        try:
            if "USD" not in self.portfolio:
                self.portfolio["USD"] = {
                    "quantity": self.initial_balance,
                    "avg_price": 1.0,
                    "current_price": 1.0,
                    "current_value": self.initial_balance,
                    "unrealized_pnl": 0.0,
                    "unrealized_pnl_percentage": 0.0,
                    "last_updated": datetime.now(),
                }

            self.portfolio["USD"]["quantity"] += amount
            self.portfolio["USD"]["current_value"] = self.portfolio["USD"]["quantity"]
            self.portfolio["USD"]["last_updated"] = datetime.now()

        except Exception as e:
            self.logger.error(f"❌ Error updating USD balance: {e}")

    def _update_asset_balance(
        self, asset_symbol: str, quantity_change: float, price: float
    ):
        """
        📈 Actualizar balance de un asset

        Args:
            asset_symbol: Símbolo del asset
            quantity_change: Cambio en cantidad (puede ser negativo)
            price: Precio actual
        """
        try:
            if asset_symbol not in self.portfolio:
                self.portfolio[asset_symbol] = {
                    "quantity": 0.0,
                    "avg_price": price,
                    "current_price": price,
                    "current_value": 0.0,
                    "unrealized_pnl": 0.0,
                    "unrealized_pnl_percentage": 0.0,
                    "last_updated": datetime.now(),
                }

            position = self.portfolio[asset_symbol]
            old_quantity = position["quantity"]
            new_quantity = old_quantity + quantity_change

            # Actualizar precio promedio para largos y cortos
            if quantity_change != 0:
                if old_quantity == 0:
                    position["avg_price"] = price
                else:
                    # Usar cantidades absolutas para shorts
                    abs_old = abs(old_quantity)
                    abs_change = abs(quantity_change)
                    abs_new = abs(new_quantity)
                    position["avg_price"] = (
                        (abs_old * position["avg_price"]) + (abs_change * price)
                    ) / max(abs_new, 1e-12)

            position["quantity"] = new_quantity
            position["current_price"] = price
            # Exposición actual (valor absoluto)
            position["current_value"] = abs(new_quantity) * price

            # Calcular PnL no realizado
            if new_quantity > 0:
                # Largo: sube precio, PnL positivo
                position["unrealized_pnl"] = (
                    price - position["avg_price"]
                ) * new_quantity
                position["unrealized_pnl_percentage"] = (
                    (price - position["avg_price"]) / position["avg_price"]
                ) * 100
            elif new_quantity < 0:
                # Corto: baja precio, PnL positivo
                abs_qty = abs(new_quantity)
                position["unrealized_pnl"] = (
                    position["avg_price"] - price
                ) * abs_qty
                position["unrealized_pnl_percentage"] = (
                    (position["avg_price"] - price) / position["avg_price"]
                ) * 100
            else:
                position["unrealized_pnl"] = 0.0
                position["unrealized_pnl_percentage"] = 0.0

            position["last_updated"] = datetime.now()

            # Eliminar posición solo si la cantidad es exactamente 0
            if new_quantity == 0:
                del self.portfolio[asset_symbol]

        except Exception as e:
            self.logger.error(f"❌ Error updating {asset_symbol} balance: {e}")

    def get_open_positions(self) -> List[Dict]:
        """
        📊 Obtener posiciones abiertas

        Returns:
            List[Dict]: Lista de posiciones abiertas
        """
        try:
            positions = []
            for symbol, position in self.portfolio.items():
                if (
                    symbol != "USD" and position["quantity"] != 0
                ):  # Incluir tanto posiciones largas como cortas
                    positions.append(
                        {
                            "symbol": symbol,
                            "quantity": position["quantity"],
                            "avg_price": position["avg_price"],
                            "current_price": position["current_price"],
                            "current_value": position["current_value"],
                            "unrealized_pnl": position["unrealized_pnl"],
                            "unrealized_pnl_percentage": position[
                                "unrealized_pnl_percentage"
                            ],
                            "last_updated": position["last_updated"],
                        }
                    )
            return positions
        except Exception as e:
            self.logger.error(f"❌ Error getting open positions: {e}")
            return []

    def get_trade_history(self) -> List[Dict]:
        """
        📈 Obtener historial de trades

        Returns:
            List[Dict]: Lista de trades realizados
        """
        try:
            return self.trades.copy()
        except Exception as e:
            self.logger.error(f"❌ Error getting trade history: {e}")
            return []

    def calculate_portfolio_performance(self) -> Dict:
        """
        📊 Calcular rendimiento del portfolio usando valores reales de Capital.com

        Returns:
            Dict: Métricas de rendimiento del portfolio
        """
        try:
            # Si tenemos valores reales de Capital.com, usarlos
            if hasattr(self, "_real_equity") and hasattr(self, "_real_pnl"):
                total_value = self._real_equity
                total_pnl = self._real_pnl
                balance_usd = self.portfolio["USD"]["current_value"]

                # Calcular total invertido basado en equity - pnl
                total_invested = total_value - total_pnl

                # Calcular porcentaje de rendimiento
                total_return_percentage = (
                    (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
                )

                return {
                    "total_value": total_value,
                    "total_pnl": total_pnl,
                    "total_return_percentage": total_return_percentage,
                    "initial_balance": self.initial_balance,
                    "usd_balance": balance_usd,
                    "open_positions": len(
                        [
                            pos
                            for symbol, pos in self.portfolio.items()
                            if symbol != "USD" and pos.get("quantity", 0) != 0
                        ]
                    ),
                }

            # Fallback: calcular usando posiciones del paper trader
            total_value = 0.0
            total_pnl = 0.0

            for symbol, position in self.portfolio.items():
                current_value = position.get("current_value", 0.0)
                unrealized_pnl = position.get("unrealized_pnl", 0.0)

                total_value += current_value
                total_pnl += unrealized_pnl

            # Calcular porcentaje de retorno
            total_return_percentage = 0.0
            if self.initial_balance > 0:
                total_return_percentage = (total_pnl / self.initial_balance) * 100

            return {
                "total_value": total_value,
                "total_pnl": total_pnl,
                "total_return_percentage": total_return_percentage,
                "initial_balance": self.initial_balance,
                "usd_balance": self.get_balance("USD"),
                "open_positions": len(
                    [
                        pos
                        for symbol, pos in self.portfolio.items()
                        if symbol != "USD" and pos.get("quantity", 0) != 0
                    ]
                ),
            }

        except Exception as e:
            self.logger.error(f"❌ Error calculating portfolio performance: {e}")
            return {
                "total_value": self.initial_balance,
                "total_pnl": 0.0,
                "total_return_percentage": 0.0,
                "initial_balance": self.initial_balance,
                "usd_balance": self.initial_balance,
                "open_positions": 0,
            }

    def get_statistics(self) -> Dict:
        """
        📊 Obtener estadísticas del trading

        Returns:
            Dict: Estadísticas básicas
        """
        try:
            total_trades = len(self.trades)
            buy_trades = len([t for t in self.trades if t["trade_type"] == "BUY"])
            sell_trades = len([t for t in self.trades if t["trade_type"] == "SELL"])

            portfolio_performance = self.calculate_portfolio_performance()

            return {
                "total_trades": total_trades,
                "buy_trades": buy_trades,
                "sell_trades": sell_trades,
                "current_balance": self.get_balance("USD"),
                "total_portfolio_value": portfolio_performance["total_value"],
                "total_pnl": portfolio_performance["total_pnl"],
                "total_pnl_percentage": portfolio_performance[
                    "total_return_percentage"
                ],
                "open_positions": portfolio_performance["open_positions"],
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting statistics: {e}")
            return {
                "total_trades": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "current_balance": self.initial_balance,
                "total_portfolio_value": self.initial_balance,
                "total_pnl": 0.0,
                "total_pnl_percentage": 0.0,
                "open_positions": 0,
            }

    def validate_trade(self, trade_data: Dict) -> bool:
        """
        ✅ Validar datos de trade

        Args:
            trade_data: Datos del trade a validar

        Returns:
            bool: True si el trade es válido
        """
        try:
            required_fields = ["symbol", "action", "price"]
            for field in required_fields:
                if field not in trade_data:
                    self.logger.warning(f"❌ Missing required field: {field}")
                    return False

            # Validación robusta de precio
            try:
                price = float(trade_data["price"])
                if price <= 0:
                    self.logger.warning(f"❌ Trade price must be positive: {price}")
                    return False
                if not isinstance(price, (int, float)) or price != price:  # NaN check
                    self.logger.warning(f"❌ Trade price is NaN: {trade_data['price']}")
                    return False
                if price == float("inf") or price == float("-inf"):
                    self.logger.warning(f"❌ Trade price is infinite: {price}")
                    return False
            except (ValueError, TypeError):
                self.logger.warning(
                    f"❌ Trade price is not a valid number: {trade_data['price']}"
                )
                return False

            if trade_data["action"].upper() not in ["BUY", "SELL"]:
                self.logger.warning(f"❌ Invalid action: {trade_data['action']}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"❌ Error validating trade: {e}")
            return False

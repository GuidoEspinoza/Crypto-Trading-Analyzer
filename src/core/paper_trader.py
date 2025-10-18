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

from src.config.main_config import PaperTraderConfig, TradingBotConfig, USD_BASE_PRICE, TRADING_FEES, PRODUCTION_MODE, PAPER_TRADING_ONLY, ENABLE_REAL_TRADING, VERBOSE_LOGGING

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
    
    def __init__(self, initial_balance: float = None):
        """
        Inicializar Paper Trader
        
        Args:
            initial_balance: Balance inicial en USD (opcional, usa config si no se especifica)
        """
        # Configuración del paper trader desde archivo centralizado
        self.config = PaperTraderConfig()
        # Balance inicial desde configuración o parámetro
        default_balance = 0.0  # Balance por defecto
        self.initial_balance = initial_balance if initial_balance is not None else default_balance
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
                "last_updated": datetime.now()
            }
        }
        
        # Historial de trades en memoria
        self.trades = []
        self.trade_counter = 1
        
        # Configurar logging basado en modo de operación
        log_level = logging.DEBUG if VERBOSE_LOGGING else logging.INFO
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
        
        # Verificaciones de modo de operación
        if PRODUCTION_MODE:
            if not PAPER_TRADING_ONLY:
                self.logger.warning("⚠️  PRODUCTION MODE: Paper trading is disabled!")
            if ENABLE_REAL_TRADING:
                self.logger.warning("⚠️  PRODUCTION MODE: Real trading is enabled!")
            self.logger.info("🏭 Running in PRODUCTION MODE")
        else:
            self.logger.info("🧪 Running in DEVELOPMENT MODE")
        
        self.logger.info(f"🎭 Paper Trader initialized with ${self.initial_balance:,.2f}")
    
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
                    "last_updated": datetime.now()
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
                "current_balance": self.initial_balance
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error resetting portfolio: {e}")
            return {
                "success": False,
                "message": f"Error resetting portfolio: {e}",
                "initial_balance": self.initial_balance,
                "current_balance": self.get_balance()
            }
    
    def execute_signal(self, signal: 'TradingSignal') -> TradeResult:
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
                    entry_value=0.0
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
                    entry_value=0.0
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error executing signal: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Error executing signal: {e}",
                entry_price=signal.price if hasattr(signal, 'price') else 0.0,
                quantity=0.0,
                entry_value=0.0
            )
    
    def _validate_signal(self, signal: 'TradingSignal') -> bool:
        """
        ✅ Validar una señal de trading
        
        Args:
            signal: Señal a validar
            
        Returns:
            bool: True si la señal es válida
        """
        try:
            # Validaciones básicas
            if not hasattr(signal, 'symbol') or not signal.symbol:
                self.logger.warning("❌ Signal missing symbol")
                return False
                
            if not hasattr(signal, 'signal_type') or not signal.signal_type:
                self.logger.warning("❌ Signal missing signal_type")
                return False
                
            if not hasattr(signal, 'price') or signal.price <= 0:
                self.logger.warning("❌ Signal missing or invalid price")
                return False
                
            if not hasattr(signal, 'confidence_score') or signal.confidence_score < self.min_confidence_threshold:
                self.logger.warning(f"❌ Signal confidence too low: {signal.confidence_score} < {self.min_confidence_threshold}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating signal: {e}")
            return False
    
    def _execute_buy(self, signal: 'TradingSignal') -> TradeResult:
        """
        📈 Ejecutar una orden de compra
        
        Args:
            signal: Señal de compra
            
        Returns:
            TradeResult con el resultado de la operación
        """
        try:
            symbol = signal.symbol
            price = signal.price
            
            # Calcular cantidad basada en el tamaño máximo de posición
            usd_balance = self.get_balance("USD")
            max_trade_value = min(
                usd_balance * self.max_balance_usage,
                self.max_position_size
            )
            
            if max_trade_value < self.min_trade_value:
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message=f"Insufficient balance for minimum trade value ${self.min_trade_value:,.2f}",
                    entry_price=price,
                    quantity=0.0,
                    entry_value=0.0
                )
            
            # Calcular cantidad y fees
            quantity = max_trade_value / price
            fee = max_trade_value * FEE_RATE
            total_cost = max_trade_value + fee
            
            if total_cost > usd_balance:
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message=f"Insufficient balance: ${total_cost:,.2f} required, ${usd_balance:,.2f} available",
                    entry_price=price,
                    quantity=0.0,
                    entry_value=0.0
                )
            
            # Actualizar portfolio
            self._update_usd_balance(-total_cost)
            self._update_asset_balance(symbol, quantity, price)
            
            # Crear registro de trade
            trade_id = self.trade_counter
            self.trade_counter += 1
            
            trade_record = {
                "id": trade_id,
                "symbol": symbol,
                "trade_type": "BUY",
                "quantity": quantity,
                "entry_price": price,
                "entry_value": max_trade_value,
                "fee": fee,
                "status": "OPEN",
                "entry_time": datetime.now(),
                "is_paper_trade": True,
                "notes": f"Paper trade BUY {symbol}"
            }
            
            self.trades.append(trade_record)
            
            self.logger.info(f"✅ BUY executed: {quantity:.6f} {symbol} @ ${price:.2f} (Trade #{trade_id})")
            
            return TradeResult(
                success=True,
                trade_id=trade_id,
                message=f"BUY order executed successfully",
                entry_price=price,
                quantity=quantity,
                entry_value=max_trade_value
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error executing buy: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Error executing buy: {e}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0
            )
    
    def _execute_sell(self, signal: 'TradingSignal') -> TradeResult:
        """
        📉 Ejecutar una orden de venta
        
        Args:
            signal: Señal de venta
            
        Returns:
            TradeResult con el resultado de la operación
        """
        try:
            symbol = signal.symbol
            price = signal.price
            
            # Verificar si tenemos posición en este asset
            if symbol not in self.portfolio:
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message=f"No position in {symbol} to sell",
                    entry_price=price,
                    quantity=0.0,
                    entry_value=0.0
                )
            
            position = self.portfolio[symbol]
            available_quantity = position["quantity"]
            
            if available_quantity <= 0:
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message=f"No {symbol} available to sell",
                    entry_price=price,
                    quantity=0.0,
                    entry_value=0.0
                )
            
            # Vender toda la posición
            quantity = available_quantity
            sale_value = quantity * price
            fee = sale_value * FEE_RATE
            net_proceeds = sale_value - fee
            
            # Actualizar portfolio
            self._update_usd_balance(net_proceeds)
            self._update_asset_balance(symbol, -quantity, price)
            
            # Crear registro de trade
            trade_id = self.trade_counter
            self.trade_counter += 1
            
            trade_record = {
                "id": trade_id,
                "symbol": symbol,
                "trade_type": "SELL",
                "quantity": quantity,
                "exit_price": price,
                "exit_value": sale_value,
                "fee": fee,
                "status": "CLOSED",
                "exit_time": datetime.now(),
                "is_paper_trade": True,
                "notes": f"Paper trade SELL {symbol}"
            }
            
            self.trades.append(trade_record)
            
            self.logger.info(f"✅ SELL executed: {quantity:.6f} {symbol} @ ${price:.2f} (Trade #{trade_id})")
            
            return TradeResult(
                success=True,
                trade_id=trade_id,
                message=f"SELL order executed successfully",
                entry_price=price,
                quantity=quantity,
                entry_value=sale_value
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error executing sell: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"Error executing sell: {e}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0
            )
    
    def get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio
        
        Returns:
            Dict con el resumen del portfolio
        """
        try:
            total_value = sum(pos["current_value"] for pos in self.portfolio.values())
            total_pnl = sum(pos["unrealized_pnl"] for pos in self.portfolio.values())
            
            return {
                "total_value": total_value,
                "initial_balance": self.initial_balance,
                "total_pnl": total_pnl,
                "total_pnl_percentage": (total_pnl / self.initial_balance) * 100 if self.initial_balance > 0 else 0.0,
                "positions": len([pos for pos in self.portfolio.values() if pos["quantity"] > 0]),
                "last_updated": datetime.now()
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting portfolio summary: {e}")
            return {
                "total_value": self.initial_balance,
                "initial_balance": self.initial_balance,
                "total_pnl": 0.0,
                "total_pnl_percentage": 0.0,
                "positions": 0,
                "last_updated": datetime.now()
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
                    "last_updated": datetime.now()
                }
            
            self.portfolio["USD"]["quantity"] += amount
            self.portfolio["USD"]["current_value"] = self.portfolio["USD"]["quantity"]
            self.portfolio["USD"]["last_updated"] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"❌ Error updating USD balance: {e}")
    
    def _update_asset_balance(self, asset_symbol: str, quantity_change: float, price: float):
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
                    "last_updated": datetime.now()
                }
            
            position = self.portfolio[asset_symbol]
            old_quantity = position["quantity"]
            new_quantity = old_quantity + quantity_change
            
            # Actualizar precio promedio si es una compra
            if quantity_change > 0:
                if old_quantity > 0:
                    total_cost = (old_quantity * position["avg_price"]) + (quantity_change * price)
                    position["avg_price"] = total_cost / new_quantity
                else:
                    position["avg_price"] = price
            
            position["quantity"] = new_quantity
            position["current_price"] = price
            position["current_value"] = new_quantity * price
            
            # Calcular PnL no realizado
            if new_quantity > 0:
                position["unrealized_pnl"] = (price - position["avg_price"]) * new_quantity
                position["unrealized_pnl_percentage"] = ((price - position["avg_price"]) / position["avg_price"]) * 100
            else:
                position["unrealized_pnl"] = 0.0
                position["unrealized_pnl_percentage"] = 0.0
            
            position["last_updated"] = datetime.now()
            
            # Eliminar posición si la cantidad es 0
            if new_quantity <= 0:
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
                if symbol != "USD" and position["quantity"] > 0:
                    positions.append({
                        "symbol": symbol,
                        "quantity": position["quantity"],
                        "avg_price": position["avg_price"],
                        "current_price": position["current_price"],
                        "current_value": position["current_value"],
                        "unrealized_pnl": position["unrealized_pnl"],
                        "unrealized_pnl_percentage": position["unrealized_pnl_percentage"],
                        "last_updated": position["last_updated"]
                    })
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
            
            portfolio_summary = self.get_portfolio_summary()
            
            return {
                "total_trades": total_trades,
                "buy_trades": buy_trades,
                "sell_trades": sell_trades,
                "current_balance": self.get_balance("USD"),
                "total_portfolio_value": portfolio_summary["total_value"],
                "total_pnl": portfolio_summary["total_pnl"],
                "total_pnl_percentage": portfolio_summary["total_pnl_percentage"],
                "open_positions": len(self.get_open_positions())
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
                "open_positions": 0
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
            
            if trade_data["price"] <= 0:
                self.logger.warning("❌ Invalid price")
                return False
            
            if trade_data["action"].upper() not in ["BUY", "SELL"]:
                self.logger.warning(f"❌ Invalid action: {trade_data['action']}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating trade: {e}")
            return False
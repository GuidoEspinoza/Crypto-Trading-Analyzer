"""
🎭 Universal Trading Analyzer - Paper Trader
Ejecutor de trades virtuales con gestión automática de portfolio
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from dataclasses import dataclass

# Importar modelos de database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import db_manager
from database.models import Trade, Portfolio, TradingSignal as DBTradingSignal
from .enhanced_strategies import TradingSignal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📊 CONFIGURACIÓN DEL PAPER TRADER PROFESIONAL
# ===============================================
# Parámetros de gestión de riesgo y trading optimizados
DEFAULT_INITIAL_BALANCE = 1000.0     # Balance inicial en USDT (más realista)
MAX_POSITION_SIZE = 0.08              # Máximo 8% del portfolio por trade
MAX_TOTAL_EXPOSURE = 0.75             # Máximo 75% del portfolio invertido (más conservador)
MIN_TRADE_VALUE = 25.0               # Mínimo $25 por trade (más profesional)
MAX_SLIPPAGE = 0.001                 # Máximo 0.1% de slippage permitido
MIN_LIQUIDITY_RATIO = 0.05           # Mínimo 5% del volumen diario para ejecutar

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
    🎭 Paper Trader - Ejecutor de trades virtuales
    
    Características:
    - Gestión automática de portfolio
    - Risk management integrado
    - Tracking completo de trades
    - Cálculo de P&L en tiempo real
    """
    
    def __init__(self, initial_balance: float = DEFAULT_INITIAL_BALANCE):
        """
        Inicializar Paper Trader
        
        Args:
            initial_balance: Balance inicial en USDT
        """
        self.initial_balance = initial_balance
        self.max_position_size = MAX_POSITION_SIZE
        self.max_total_exposure = MAX_TOTAL_EXPOSURE
        self.min_trade_value = MIN_TRADE_VALUE
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🎭 Paper Trader initialized with ${initial_balance:,.2f}")
    
    def reset_portfolio(self) -> Dict:
        """
        🔄 Resetear el portfolio a los valores por defecto
        
        Returns:
            Dict con el resultado del reset
        """
        try:
            with db_manager.get_db_session() as session:
                # Eliminar todos los trades
                session.query(Trade).filter(Trade.is_paper_trade == True).delete()
                
                # Resetear portfolio a valores iniciales
                portfolio_entries = session.query(Portfolio).filter(Portfolio.is_paper == True).all()
                
                for entry in portfolio_entries:
                    if entry.symbol == "USDT":
                        # Restaurar balance inicial de USDT
                        entry.quantity = self.initial_balance
                        entry.avg_price = 1.0
                        entry.current_price = 1.0
                        entry.current_value = self.initial_balance
                        entry.unrealized_pnl = 0.0
                        entry.unrealized_pnl_percentage = 0.0
                        entry.last_updated = datetime.now()
                    else:
                        # Eliminar todas las otras posiciones
                        session.delete(entry)
                
                session.commit()
                
                self.logger.info(f"🔄 Portfolio reset to initial balance: ${self.initial_balance:,.2f}")
                
                return {
                    "success": True,
                    "message": f"Portfolio reset successfully to ${self.initial_balance:,.2f}",
                    "initial_balance": self.initial_balance,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            error_msg = f"Error resetting portfolio: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_signal(self, signal: TradingSignal) -> TradeResult:
        """
        🎯 Ejecutar una señal de trading
        
        Args:
            signal: Señal generada por una estrategia
            
        Returns:
            TradeResult: Resultado de la ejecución
        """
        try:
            self.logger.info(f"🎯 Processing signal: {signal.signal_type} {signal.symbol} @ {signal.price}")
            
            # Validar señal
            if not self._validate_signal(signal):
                return TradeResult(
                    success=False,
                    trade_id=None,
                    message="❌ Signal validation failed",
                    entry_price=signal.price,
                    quantity=0.0,
                    entry_value=0.0
                )
            
            # Ejecutar según tipo de señal
            if signal.signal_type == "BUY":
                return self._execute_buy(signal)
            elif signal.signal_type == "SELL":
                return self._execute_sell(signal)
            else:  # HOLD
                return TradeResult(
                    success=True,
                    trade_id=None,
                    message="⚪ HOLD signal - No action taken",
                    entry_price=signal.price,
                    quantity=0.0,
                    entry_value=0.0
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error executing signal: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"❌ Execution error: {str(e)}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0
            )
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """
        ✅ Validar si una señal es ejecutable
        
        Args:
            signal: Señal a validar
            
        Returns:
            bool: True si es válida
        """
        # Validaciones básicas
        if signal.confidence_score < 60.0:
            self.logger.info(f"❌ Low confidence: {signal.confidence_score}")
            return False
        
        if signal.price <= 0:
            self.logger.error(f"❌ Invalid price: {signal.price}")
            return False
        
        if signal.signal_type not in ["BUY", "SELL", "HOLD"]:
            self.logger.error(f"❌ Invalid signal type: {signal.signal_type}")
            return False
        
        # Validaciones de portfolio
        portfolio_summary = self._get_portfolio_summary()
        
        if signal.signal_type == "BUY":
            # Verificar si tenemos USDT suficiente
            usdt_balance = self._get_usdt_balance()
            max_trade_value = usdt_balance * self.max_position_size
            
            if max_trade_value < self.min_trade_value:
                self.logger.info(f"❌ Insufficient USDT balance: ${usdt_balance:.2f}")
                return False
        
        elif signal.signal_type == "SELL":
            # Verificar si tenemos el asset para vender
            asset_symbol = signal.symbol.split('/')[0]  # BTC de BTC/USDT
            asset_balance = self._get_asset_balance(asset_symbol)
            
            if asset_balance <= 0:
                self.logger.info(f"❌ No {asset_symbol} balance to sell")
                return False
        
        return True
    
    def _execute_buy(self, signal: TradingSignal) -> TradeResult:
        """
        🟢 Ejecutar orden de compra
        
        Args:
            signal: Señal de compra
            
        Returns:
            TradeResult: Resultado de la compra
        """
        try:
            with db_manager.get_db_session() as session:
                # Calcular cantidad a comprar
                usdt_balance = self._get_usdt_balance()
                max_trade_value = usdt_balance * self.max_position_size
                trade_value = min(max_trade_value, usdt_balance * 0.95)  # 95% para fees
                
                if trade_value < self.min_trade_value:
                    return TradeResult(
                        success=False,
                        trade_id=None,
                        message=f"❌ Trade value too small: ${trade_value:.2f}",
                        entry_price=signal.price,
                        quantity=0.0,
                        entry_value=0.0
                    )
                
                quantity = trade_value / signal.price
                
                # Crear trade en base de datos
                new_trade = Trade(
                    symbol=signal.symbol,
                    strategy_name=signal.strategy_name,
                    trade_type="BUY",
                    entry_price=signal.price,
                    quantity=quantity,
                    entry_value=trade_value,
                    status="OPEN",
                    is_paper_trade=True,
                    timeframe="1h",  # Default
                    confidence_score=signal.confidence_score,
                    notes=signal.notes
                )
                
                session.add(new_trade)
                session.flush()  # Para obtener el ID
                
                # Actualizar portfolio - Reducir USDT
                self._update_usdt_balance(-trade_value, session)
                
                # Actualizar portfolio - Aumentar asset
                asset_symbol = signal.symbol.split('/')[0]
                self._update_asset_balance(asset_symbol, quantity, signal.price, session)
                
                # Guardar señal en base de datos
                self._save_signal_to_db(signal, new_trade.id, "EXECUTED", session)
                
                session.commit()
                
                self.logger.info(f"✅ BUY executed: {quantity:.6f} {asset_symbol} @ ${signal.price:.2f}")
                
                return TradeResult(
                    success=True,
                    trade_id=new_trade.id,
                    message=f"✅ Bought {quantity:.6f} {asset_symbol} for ${trade_value:.2f}",
                    entry_price=signal.price,
                    quantity=quantity,
                    entry_value=trade_value
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error executing buy: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"❌ Buy error: {str(e)}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0
            )
    
    def _execute_sell(self, signal: TradingSignal) -> TradeResult:
        """
        🔴 Ejecutar orden de venta
        
        Args:
            signal: Señal de venta
            
        Returns:
            TradeResult: Resultado de la venta
        """
        try:
            with db_manager.get_db_session() as session:
                asset_symbol = signal.symbol.split('/')[0]
                asset_balance = self._get_asset_balance(asset_symbol)
                
                if asset_balance <= 0:
                    return TradeResult(
                        success=False,
                        trade_id=None,
                        message=f"❌ No {asset_symbol} balance to sell",
                        entry_price=signal.price,
                        quantity=0.0,
                        entry_value=0.0
                    )
                
                # Vender todo el balance del asset
                quantity = asset_balance
                sale_value = quantity * signal.price
                
                # Buscar trades abiertos para cerrar
                open_trades = session.query(Trade).filter(
                    Trade.symbol == signal.symbol,
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                total_pnl = 0.0
                
                # Cerrar trades abiertos
                for trade in open_trades:
                    trade.exit_price = signal.price
                    trade.exit_value = trade.quantity * signal.price
                    trade.pnl = trade.exit_value - trade.entry_value
                    trade.pnl_percentage = (trade.pnl / trade.entry_value) * 100
                    trade.status = "CLOSED"
                    trade.exit_time = datetime.now()
                    total_pnl += trade.pnl
                
                # Crear nuevo trade de venta
                new_trade = Trade(
                    symbol=signal.symbol,
                    strategy_name=signal.strategy_name,
                    trade_type="SELL",
                    entry_price=signal.price,
                    exit_price=signal.price,
                    quantity=quantity,
                    entry_value=sale_value,
                    exit_value=sale_value,
                    pnl=0.0,  # Para trades de venta directa
                    status="CLOSED",
                    is_paper_trade=True,
                    timeframe="1h",
                    confidence_score=signal.confidence_score,
                    notes=signal.notes,
                    exit_time=datetime.now()
                )
                
                session.add(new_trade)
                session.flush()
                
                # Actualizar portfolio - Aumentar USDT
                self._update_usdt_balance(sale_value, session)
                
                # Actualizar portfolio - Reducir asset a 0
                self._update_asset_balance(asset_symbol, -asset_balance, signal.price, session)
                
                # Guardar señal en base de datos
                self._save_signal_to_db(signal, new_trade.id, "EXECUTED", session)
                
                session.commit()
                
                self.logger.info(f"✅ SELL executed: {quantity:.6f} {asset_symbol} @ ${signal.price:.2f} (PnL: ${total_pnl:.2f})")
                
                return TradeResult(
                    success=True,
                    trade_id=new_trade.id,
                    message=f"✅ Sold {quantity:.6f} {asset_symbol} for ${sale_value:.2f} (PnL: ${total_pnl:.2f})",
                    entry_price=signal.price,
                    quantity=quantity,
                    entry_value=sale_value
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error executing sell: {e}")
            return TradeResult(
                success=False,
                trade_id=None,
                message=f"❌ Sell error: {str(e)}",
                entry_price=signal.price,
                quantity=0.0,
                entry_value=0.0
            )
    
    def _get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio
        """
        return db_manager.get_portfolio_summary(is_paper=True)
    
    def _get_usdt_balance(self) -> float:
        """
        💰 Obtener balance de USDT
        """
        try:
            with db_manager.get_db_session() as session:
                usdt_portfolio = session.query(Portfolio).filter(
                    Portfolio.symbol == "USDT",
                    Portfolio.is_paper == True
                ).first()
                
                return usdt_portfolio.quantity if usdt_portfolio else 0.0
        except Exception as e:
            self.logger.error(f"❌ Error getting USDT balance: {e}")
            return 0.0
    
    def _get_asset_balance(self, asset_symbol: str) -> float:
        """
        🪙 Obtener balance de un asset específico
        """
        try:
            with db_manager.get_db_session() as session:
                asset_portfolio = session.query(Portfolio).filter(
                    Portfolio.symbol == asset_symbol,
                    Portfolio.is_paper == True
                ).first()
                
                return asset_portfolio.quantity if asset_portfolio else 0.0
        except Exception as e:
            self.logger.error(f"❌ Error getting {asset_symbol} balance: {e}")
            return 0.0
    
    def _update_usdt_balance(self, amount: float, session: Session):
        """
        💰 Actualizar balance de USDT
        """
        usdt_portfolio = session.query(Portfolio).filter(
            Portfolio.symbol == "USDT",
            Portfolio.is_paper == True
        ).first()
        
        if usdt_portfolio:
            usdt_portfolio.quantity += amount
            usdt_portfolio.current_value = usdt_portfolio.quantity * 1.0
            usdt_portfolio.last_updated = datetime.now()
        else:
            # Crear entrada USDT si no existe
            new_usdt = Portfolio(
                symbol="USDT",
                quantity=max(0, amount),
                avg_price=1.0,
                current_price=1.0,
                current_value=max(0, amount),
                is_paper=True
            )
            session.add(new_usdt)
    
    def _update_asset_balance(self, asset_symbol: str, quantity_change: float, price: float, session: Session):
        """
        🪙 Actualizar balance de un asset
        """
        asset_portfolio = session.query(Portfolio).filter(
            Portfolio.symbol == asset_symbol,
            Portfolio.is_paper == True
        ).first()
        
        if asset_portfolio:
            # Actualizar balance existente
            if quantity_change > 0:  # Compra
                total_cost = (asset_portfolio.quantity * asset_portfolio.avg_price) + (quantity_change * price)
                asset_portfolio.quantity += quantity_change
                asset_portfolio.avg_price = total_cost / asset_portfolio.quantity if asset_portfolio.quantity > 0 else price
            else:  # Venta
                asset_portfolio.quantity += quantity_change  # quantity_change es negativo
                
            asset_portfolio.current_price = price
            asset_portfolio.current_value = asset_portfolio.quantity * price
            asset_portfolio.last_updated = datetime.now()
            
            # Calcular PnL no realizado
            if asset_portfolio.quantity > 0:
                cost_basis = asset_portfolio.quantity * asset_portfolio.avg_price
                current_value = asset_portfolio.quantity * price
                asset_portfolio.unrealized_pnl = current_value - cost_basis
                asset_portfolio.unrealized_pnl_percentage = (asset_portfolio.unrealized_pnl / cost_basis) * 100
        
        else:
            # Crear nueva entrada de asset
            if quantity_change > 0:
                new_asset = Portfolio(
                    symbol=asset_symbol,
                    quantity=quantity_change,
                    avg_price=price,
                    current_price=price,
                    current_value=quantity_change * price,
                    unrealized_pnl=0.0,
                    unrealized_pnl_percentage=0.0,
                    is_paper=True
                )
                session.add(new_asset)
    
    def _save_signal_to_db(self, signal: TradingSignal, trade_id: Optional[int], action: str, session: Session):
        """
        💾 Guardar señal en base de datos
        """
        try:
            db_signal = DBTradingSignal(
                symbol=signal.symbol,
                strategy_name=signal.strategy_name,
                signal_type=signal.signal_type,
                timeframe="1h",  # Default
                price=signal.price,
                confidence_score=signal.confidence_score,
                strength=signal.strength,
                indicators_data=str(signal.indicators_data),  # Convertir a string
                action_taken=action,
                trade_id=trade_id,
                generated_at=signal.timestamp
            )
            
            session.add(db_signal)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving signal to DB: {e}")
    
    def get_open_positions(self) -> List[Dict]:
        """
        📊 Obtener posiciones abiertas
        """
        try:
            with db_manager.get_db_session() as session:
                open_trades = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                return [
                    {
                        "id": trade.id,
                        "symbol": trade.symbol,
                        "strategy": trade.strategy_name,
                        "entry_price": trade.entry_price,
                        "quantity": trade.quantity,
                        "entry_value": trade.entry_value,
                        "entry_time": trade.entry_time.isoformat(),
                        "confidence_score": trade.confidence_score
                    }
                    for trade in open_trades
                ]
        except Exception as e:
            self.logger.error(f"❌ Error getting open positions: {e}")
            return []
    
    def calculate_portfolio_performance(self) -> Dict:
        """
        📈 Calcular performance del portfolio
        """
        try:
            portfolio_summary = self._get_portfolio_summary()
            total_value = portfolio_summary.get("total_value", 0)
            total_pnl = portfolio_summary.get("total_pnl", 0)
            
            with db_manager.get_db_session() as session:
                # Contar trades
                total_trades = session.query(Trade).filter(Trade.is_paper_trade == True).count()
                winning_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == True,
                    Trade.pnl > 0
                ).count()
                
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                return {
                    "total_value": total_value,
                    "total_pnl": total_pnl,
                    "total_return_percentage": ((total_value - self.initial_balance) / self.initial_balance) * 100,
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "win_rate": round(win_rate, 2),
                    "initial_balance": self.initial_balance
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error calculating performance: {e}")
            return {}
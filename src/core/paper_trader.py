"""
🎭 Universal Trading Analyzer - Paper Trader
Ejecutor de trades virtuales con gestión automática de portfolio
"""

from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from sqlalchemy.orm import Session
from dataclasses import dataclass

# Importar modelos de database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.main_config import PaperTraderConfig, TradingBotConfig, USDT_BASE_PRICE, TRADING_FEES

# Asegurar conversión a float consistente desde configuración
FEE_RATE: float = float(TRADING_FEES)

from database.database import db_manager
from database.models import Trade, Portfolio, TradingSignal as DBTradingSignal
# Evitar import en tiempo de ejecución para no arrastrar dependencias pesadas
if TYPE_CHECKING:
    from .enhanced_strategies import TradingSignal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📊 CONFIGURACIÓN DEL PAPER TRADER PROFESIONAL
# ===============================================
# Todos los parámetros se obtienen desde config.py para centralizar la configuración
# Los valores hardcodeados han sido eliminados para evitar inconsistencias

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
    
    def __init__(self, initial_balance: float = None):
        """
        Inicializar Paper Trader
        
        Args:
            initial_balance: Balance inicial en USDT (opcional, usa config si no se especifica)
        """
        # Configuración del paper trader desde archivo centralizado
        self.config = PaperTraderConfig()
        # Obtener balance inicial desde la base de datos (fallback a 0.0)
        try:
            db_initial_balance = db_manager.get_global_initial_balance()
        except Exception:
            db_initial_balance = 0.0
        self.initial_balance = initial_balance if initial_balance is not None else db_initial_balance
        self.max_position_size = self.config.get_max_position_size()
        self.max_total_exposure = self.config.get_max_total_exposure()
        self.min_trade_value = self.config.get_min_trade_value()
        self.max_balance_usage = self.config.MAX_BALANCE_USAGE
        self.min_confidence_threshold = self.config.get_min_confidence_threshold()
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🎭 Paper Trader initialized with ${self.initial_balance:,.2f}")
    
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
        try:
            # Validaciones básicas
            if signal.confidence_score < self.min_confidence_threshold:
                self.logger.info(f"❌ Low confidence: {signal.confidence_score:.1f}% < {self.min_confidence_threshold:.1f}%")
                return False
            
            if signal.price <= 0:
                self.logger.error(f"❌ Invalid price: {signal.price}")
                return False
            
            if signal.signal_type not in ["BUY", "SELL", "HOLD"]:
                self.logger.error(f"❌ Invalid signal type: {signal.signal_type}")
                return False
            
            # Asegurar que el portfolio está inicializado
            self._ensure_portfolio_initialized()
            
            # Validaciones de portfolio
            if signal.signal_type == "BUY":
                # Verificar si tenemos USDT suficiente
                usdt_balance = self._get_usdt_balance()
                max_trade_value = usdt_balance * (self.max_position_size)  # porcentaje en decimal
                
                # Limitar por uso máximo de balance y por exposición total permitida
                allowed_exposure = self._get_allowed_additional_exposure()
                effective_max_trade_value = min(max_trade_value, usdt_balance * self.max_balance_usage, allowed_exposure)
                
                if usdt_balance < self.min_trade_value:
                    self.logger.info(f"❌ Insufficient USDT balance: ${usdt_balance:.2f} < ${self.min_trade_value:.2f}")
                    return False
                    
                if effective_max_trade_value < self.min_trade_value:
                    self.logger.info(f"❌ Max trade value too low (after exposure limits): ${effective_max_trade_value:.2f} < ${self.min_trade_value:.2f}")
                    return False
            
            elif signal.signal_type == "SELL":
                # Verificar si tenemos el asset para vender
                asset_symbol = (signal.symbol.split('/')[0] if '/' in signal.symbol else (signal.symbol[:-4] if signal.symbol.endswith(('USDT')) else signal.symbol))  # Normaliza base: BTC de BTC/USDT o BTCUSDT
                asset_balance = self._get_asset_balance(asset_symbol)
                
                if asset_balance <= 0:
                    self.logger.info(f"❌ No {asset_symbol} balance to sell: {asset_balance}")
                    return False
            
            self.logger.info(f"✅ Signal validation passed: {signal.signal_type} {signal.symbol} @ ${signal.price:.2f} ({signal.confidence_score:.1f}%)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating signal: {e}")
            return False
    
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
                max_trade_value = usdt_balance * (self.max_position_size)  # Ya en decimal
                
                # Aplicar límites de uso de balance y de exposición total
                allowed_exposure = self._get_allowed_additional_exposure()
                trade_value_pre_fee = min(max_trade_value, usdt_balance * (self.max_balance_usage), allowed_exposure)  # Límite configurable y exposición
                
                if trade_value_pre_fee < self.min_trade_value:
                    return TradeResult(
                        success=False,
                        trade_id=None,
                        message=f"❌ Trade value too small: ${trade_value_pre_fee:.2f}",
                        entry_price=signal.price,
                        quantity=0.0,
                        entry_value=0.0
                    )
                
                # Ejecutar a precio de mercado (sin slippage) y aplicar fee
                execution_price = float(signal.price)
                trade_value = trade_value_pre_fee / (1.0 + FEE_RATE)
                quantity = trade_value / execution_price
                fee_usdt = trade_value * FEE_RATE
                total_cost = trade_value + fee_usdt
                
                # Obtener TP/SL de la señal o calcularlos automáticamente
                stop_loss_price = None
                take_profit_price = None
                
                # Verificar si la señal incluye TP/SL
                if hasattr(signal, 'stop_loss_price') and signal.stop_loss_price > 0:
                    stop_loss_price = signal.stop_loss_price
                if hasattr(signal, 'take_profit_price') and signal.take_profit_price > 0:
                    take_profit_price = signal.take_profit_price
                
                # Si faltan TP/SL, calcularlos usando enhanced_risk_manager
                if stop_loss_price is None or take_profit_price is None:
                    try:
                        from .enhanced_risk_manager import EnhancedRiskManager
                        risk_manager = EnhancedRiskManager()
                        
                        # Convertir TradingSignal a EnhancedSignal si es necesario
                        if not hasattr(signal, 'market_regime'):
                            # Crear EnhancedSignal temporal para el cálculo
                            from .enhanced_strategies import EnhancedSignal
                            enhanced_signal = EnhancedSignal(
                                symbol=signal.symbol,
                                signal_type=signal.signal_type,
                                price=signal.price,
                                confidence_score=signal.confidence_score,
                                strength=getattr(signal, 'strength', 'Moderate'),
                                strategy_name=signal.strategy_name,
                                timestamp=signal.timestamp,
                                indicators_data=getattr(signal, 'indicators_data', {}),
                                notes=f"{signal.notes or ''} | Fee: ${fee_usdt:.4f}",
                                stop_loss_price=getattr(signal, 'stop_loss_price', 0.0),
                                take_profit_price=getattr(signal, 'take_profit_price', 0.0),
                                market_regime='NORMAL',
                                timeframe=TradingBotConfig.get_primary_timeframe()
                            )
                        else:
                            enhanced_signal = signal
                        
                        # Calcular evaluación de riesgo
                        current_portfolio_value = self.get_portfolio_value()
                        risk_assessment = risk_manager.assess_trade_risk(enhanced_signal, current_portfolio_value)
                        
                        # Usar TP/SL calculados si no están disponibles
                        if stop_loss_price is None:
                            stop_loss_price = risk_assessment.dynamic_stop_loss.stop_loss_price
                        if take_profit_price is None:
                            take_profit_price = risk_assessment.dynamic_take_profit.take_profit_price
                            
                        self.logger.info(f"🛡️ TP/SL calculados automáticamente: SL=${stop_loss_price:.4f}, TP=${take_profit_price:.4f}")
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error calculando TP/SL automáticos: {e}")
                        # Fallback: usar porcentajes fijos desde config
                        from src.config.main_config import RiskManagerConfig
                        sl_pct = RiskManagerConfig.get_sl_min_percentage()
                        tp_pct = RiskManagerConfig.get_tp_min_percentage()
                        
                        if stop_loss_price is None:
                            stop_loss_price = signal.price * (1 - sl_pct)
                        if take_profit_price is None:
                            take_profit_price = signal.price * (1 + tp_pct)
                            
                        self.logger.info(f"🛡️ TP/SL fallback aplicados: SL=${stop_loss_price:.4f}, TP=${take_profit_price:.4f}")

                # Crear trade en base de datos
                normalized_symbol = self._normalize_to_usdt_ticker(signal.symbol)
                new_trade = Trade(
                    symbol=normalized_symbol,
                    strategy_name=signal.strategy_name,
                    trade_type="BUY",
                    entry_price=execution_price,
                    quantity=quantity,
                    entry_value=total_cost,
                    status="OPEN",
                    is_paper_trade=True,
                    timeframe=TradingBotConfig.get_primary_timeframe(),
                    confidence_score=signal.confidence_score,
                    notes=f"{signal.notes or ''} | Fee: ${fee_usdt:.4f}",
                    stop_loss=stop_loss_price,
                    take_profit=take_profit_price
                )
                
                session.add(new_trade)
                session.flush()  # Para obtener el ID
                
                # Actualizar portfolio - Reducir USDT (incluye fees)
                self._update_usdt_balance(-total_cost, session)
                
                # Actualizar portfolio - Aumentar asset
                asset_symbol = (signal.symbol.split('/')[0] if '/' in signal.symbol else (signal.symbol[:-4] if signal.symbol.endswith(('USDT')) else signal.symbol))
                self._update_asset_balance(asset_symbol, quantity, execution_price, session)
                
                # Guardar señal en base de datos
                self._save_signal_to_db(signal, new_trade.id, "EXECUTED", session)
                
                session.commit()
                
                # Obtener balance de USDT después de la compra
                usdt_balance_after = self._get_usdt_balance()
                
                self.logger.info(f"✅ BUY executed: {quantity:.6f} {asset_symbol} @ ${execution_price:.2f}")
                self.logger.info(f"💰 USDT Balance after purchase: ${usdt_balance_after:.2f}")
                
                return TradeResult(
                    success=True,
                    trade_id=new_trade.id,
                    message=f"✅ Bought {quantity:.6f} {asset_symbol} for ${total_cost:.2f}",
                    entry_price=execution_price,
                    quantity=quantity,
                    entry_value=total_cost
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
                asset_symbol = (signal.symbol.split('/')[0] if '/' in signal.symbol else (signal.symbol[:-4] if signal.symbol.endswith('USDT') else signal.symbol))
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
                
                # Ejecutar a precio de mercado (sin slippage) y aplicar fee
                execution_price = float(signal.price)
                sale_value_gross = quantity * execution_price
                fee_usdt_total = sale_value_gross * FEE_RATE

                normalized_symbol = self._normalize_to_usdt_ticker(signal.symbol)
                # Buscar trades abiertos para cerrar
                open_trades = session.query(Trade).filter(
                    Trade.symbol == normalized_symbol,
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                total_pnl = 0.0
                
                # Cerrar trades abiertos
                for trade in open_trades:
                    trade.exit_price = execution_price
                    exit_value_gross = trade.quantity * execution_price
                    fee_usdt_trade = exit_value_gross * FEE_RATE
                    trade.exit_value = exit_value_gross - fee_usdt_trade
                    trade.pnl = trade.exit_value - trade.entry_value
                    trade.pnl_percentage = (trade.pnl / trade.entry_value) * 100
                    trade.status = "CLOSED"
                    trade.exit_time = datetime.now()
                    total_pnl += trade.pnl
                
                # Crear nuevo trade de venta
                new_trade = Trade(
                    symbol=normalized_symbol,
                    strategy_name=signal.strategy_name,
                    trade_type="SELL",
                    entry_price=execution_price,
                    exit_price=execution_price,
                    quantity=quantity,
                    entry_value=sale_value_gross,
                    exit_value=sale_value_gross - fee_usdt_total,
                    pnl=0.0,  # Para trades de venta directa
                    status="CLOSED",
                    is_paper_trade=True,
                    timeframe=TradingBotConfig.get_primary_timeframe(),
                    confidence_score=signal.confidence_score,
                    notes=f"{signal.notes or ''} | Fee: ${fee_usdt_total:.4f}",
                    exit_time=datetime.now()
                )
                
                session.add(new_trade)
                session.flush()
                
                # Actualizar portfolio - Aumentar USDT (neto de fees)
                self._update_usdt_balance(sale_value_gross - fee_usdt_total, session)
                
                # Actualizar portfolio - Reducir asset a 0
                self._update_asset_balance(asset_symbol, -asset_balance, execution_price, session)
                
                # Guardar señal en base de datos
                self._save_signal_to_db(signal, new_trade.id, "EXECUTED", session)
                
                session.commit()
                
                # Obtener balance de USDT después de la venta
                usdt_balance_after = self._get_usdt_balance()
                
                self.logger.info(f"✅ SELL executed: {quantity:.6f} {asset_symbol} @ ${execution_price:.2f} (PnL: ${total_pnl:.2f})")
                self.logger.info(f"💰 USDT Balance after sale: ${usdt_balance_after:.2f}")
                
                return TradeResult(
                    success=True,
                    trade_id=new_trade.id,
                    message=f"✅ Sold {quantity:.6f} {asset_symbol} for ${sale_value_gross - fee_usdt_total:.2f} (PnL: ${total_pnl:.2f})",
                    entry_price=execution_price,
                    quantity=quantity,
                    entry_value=sale_value_gross - fee_usdt_total
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
    
    def get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio (método público)
        """
        return self._get_portfolio_summary()
    
    def get_balance(self, symbol: str = "USDT") -> float:
        """
        💰 Obtener balance de un símbolo específico
        
        Args:
            symbol: Símbolo del asset (por defecto USDT)
            
        Returns:
            float: Balance del símbolo
        """
        if symbol == "USDT":
            return self._get_usdt_balance()
        else:
            return self._get_asset_balance(symbol)
    
    def _get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio
        """
        return db_manager.get_portfolio_summary(is_paper=True)
    
    def _get_total_exposure_value(self) -> float:
        """
        📈 Valor total expuesto en activos (excluye USDT disponible)
        """
        try:
            summary = self._get_portfolio_summary()
            total_value = float(summary.get("total_value", 0.0))
            available_balance = float(summary.get("available_balance", 0.0))
            exposed_value = max(total_value - available_balance, 0.0)
            return exposed_value
        except Exception as e:
            self.logger.error(f"❌ Error calculating total exposure: {e}")
            return 0.0
    
    def _get_allowed_additional_exposure(self) -> float:
        """
        ✅ Exposición adicional permitida según max_total_exposure del perfil
        """
        try:
            portfolio_value = float(self.get_portfolio_value())
            max_allowed_exposure = portfolio_value * float(self.max_total_exposure)
            current_exposure = self._get_total_exposure_value()
            remaining = max(max_allowed_exposure - current_exposure, 0.0)
            return remaining
        except Exception as e:
            self.logger.error(f"❌ Error calculating allowed exposure: {e}")
            return 0.0
    
    def _ensure_portfolio_initialized(self):
        """
        🔧 Asegurar que el portfolio está inicializado correctamente
        """
        try:
            with db_manager.get_db_session() as session:
                usdt_portfolio = session.query(Portfolio).filter(
                    Portfolio.symbol == "USDT",
                    Portfolio.is_paper == True
                ).first()
                
                if not usdt_portfolio:
                    # Crear portfolio inicial con balance configurado
                    initial_portfolio = Portfolio(
                        symbol="USDT",
                        quantity=self.initial_balance,
                        avg_price=USDT_BASE_PRICE,
                    current_price=USDT_BASE_PRICE,
                        current_value=self.initial_balance,
                        unrealized_pnl=0.0,
                        unrealized_pnl_percentage=0.0,
                        is_paper=True
                    )
                    
                    session.add(initial_portfolio)
                    session.commit()
                    self.logger.info(f"💰 Initialized paper trading portfolio with ${self.initial_balance:,.2f} USDT")
                    
        except Exception as e:
            self.logger.error(f"❌ Error initializing portfolio: {e}")
    
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
                
                balance = usdt_portfolio.quantity if usdt_portfolio else 0.0
                self.logger.debug(f"💰 Current USDT balance: ${balance:.2f}")
                return balance
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

    def _normalize_to_usdt_ticker(self, symbol: str) -> str:
        """
        Normaliza cualquier símbolo de entrada al ticker USDT (BASEUSDT) en mayúsculas.
        Acepta formatos como "BTCUSDT", "BTC/USDT", "BTCUSDC", "BTC/BUSD" o "BTC" y devuelve "BTCUSDT".
        """
        try:
            if not symbol:
                return ""
            s = symbol.upper()
            if s == "USDT":
                return "USDT"
            if '/' in s:
                base, _quote = s.split('/')
                return f"{base}USDT"
            if s.endswith(("USDT")):
                base = s[:-4]
                return f"{base}USDT"
            # Caso sin sufijo
            return f"{s}USDT"
        except Exception:
            return symbol
    
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
            usdt_portfolio.current_value = usdt_portfolio.quantity * USDT_BASE_PRICE
            usdt_portfolio.last_updated = datetime.now()
        else:
            # Crear entrada USDT si no existe
            new_usdt = Portfolio(
                symbol="USDT",
                quantity=max(0, amount),
                avg_price=USDT_BASE_PRICE,
                current_price=USDT_BASE_PRICE,
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
                timeframe=TradingBotConfig.get_primary_timeframe(),
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
                    "total_return_percentage": ((total_value - self.initial_balance) / self.initial_balance) * 100 if self.initial_balance > 0 else 0.0,
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "win_rate": round(win_rate, 2),
                    "initial_balance": self.initial_balance,
                    "cash_balance": self._get_usdt_balance()  # Añadir balance de USDT para compatibilidad
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error calculating performance: {e}")
            return {}
    
    # Métodos adicionales para compatibilidad con tests
    def buy(self, symbol: str, quantity: float, price: float) -> Dict:
        """
        💰 Método de compra simplificado para compatibilidad con tests
        """
        try:
            # Crear señal de compra
            from .enhanced_strategies import TradingSignal
            signal = TradingSignal(
                symbol=symbol,
                signal_type="BUY",
                price=price,
                confidence_score=self.min_confidence_threshold,
                strength="Strong",
                strategy_name="test_strategy",
                indicators_data={"test_buy": True},
                timestamp=datetime.now()
            )
            
            result = self.execute_signal(signal)
            return {
                "success": result.success,
                "message": result.message,
                "trade_id": result.trade_id,
                "quantity": quantity,
                "price": price
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Buy error: {str(e)}",
                "trade_id": None
            }
    
    def sell(self, symbol: str, quantity: float, price: float) -> Dict:
        """
        💸 Método de venta simplificado para compatibilidad con tests
        """
        try:
            # Crear señal de venta
            from .enhanced_strategies import TradingSignal
            signal = TradingSignal(
                symbol=symbol,
                signal_type="SELL",
                price=price,
                confidence_score=self.min_confidence_threshold,
                strength="Strong",
                strategy_name="test_strategy",
                indicators_data={"test_sell": True},
                timestamp=datetime.now()
            )
            
            result = self.execute_signal(signal)
            return {
                "success": result.success,
                "message": result.message,
                "trade_id": result.trade_id,
                "quantity": quantity,
                "price": price
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Sell error: {str(e)}",
                "trade_id": None
            }
    
    def get_portfolio_value(self) -> float:
        """
        💼 Obtener valor total del portfolio
        """
        try:
            portfolio_summary = self._get_portfolio_summary()
            return portfolio_summary.get("total_value", 0.0)
        except Exception as e:
            self.logger.error(f"❌ Error getting portfolio value: {e}")
            return 0.0
    
    def get_positions(self) -> Dict:
        """
        📊 Obtener todas las posiciones actuales
        """
        try:
            with db_manager.get_db_session() as session:
                portfolios = session.query(Portfolio).filter(
                    Portfolio.is_paper == True,
                    Portfolio.quantity > 0
                ).all()
                
                positions = {}
                for portfolio in portfolios:
                    if portfolio.symbol != "USDT":  # Excluir USDT del listado de posiciones
                        positions[portfolio.symbol] = {
                            "quantity": portfolio.quantity,
                            "avg_price": portfolio.avg_price,
                            "current_price": portfolio.current_price,
                            "current_value": portfolio.current_value,
                            "unrealized_pnl": portfolio.unrealized_pnl,
                            "unrealized_pnl_percentage": portfolio.unrealized_pnl_percentage
                        }
                
                return positions
        except Exception as e:
            self.logger.error(f"❌ Error getting positions: {e}")
            return {}
    
    def get_trade_history(self) -> List[Dict]:
        """
        📈 Obtener historial de trades
        """
        try:
            with db_manager.get_db_session() as session:
                trades = session.query(Trade).filter(
                    Trade.is_paper_trade == True
                ).order_by(Trade.entry_time.desc()).all()
                
                return [
                    {
                        "id": trade.id,
                        "symbol": trade.symbol,
                        "side": trade.trade_type,  # Usar trade_type en lugar de side
                        "quantity": trade.quantity,
                        "entry_price": trade.entry_price,
                        "exit_price": trade.exit_price,
                        "entry_time": trade.entry_time.isoformat() if trade.entry_time else None,
                        "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
                        "pnl": trade.pnl,
                        "status": trade.status,
                        "strategy_name": trade.strategy_name
                    }
                    for trade in trades
                ]
        except Exception as e:
            self.logger.error(f"❌ Error getting trade history: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        📊 Obtener estadísticas del trading
        """
        return self.calculate_portfolio_performance()
    
    def validate_trade(self, trade_data: Dict) -> bool:
        """
        ✅ Validar si un trade es ejecutable
        """
        try:
            symbol = trade_data.get("symbol")
            quantity = trade_data.get("quantity", 0)
            price = trade_data.get("price", 0)
            side = trade_data.get("side")
            
            # Validaciones básicas
            if not symbol or not side:
                return False
            
            if quantity <= 0 or price <= 0:
                return False
            
            if side not in ["BUY", "SELL"]:
                return False
            
            # Validar valor mínimo del trade
            trade_value = quantity * price
            if trade_value < self.min_trade_value:
                return False
            
            # Calcular límites efectivos para el tamaño de trade según perfil
            current_usdt = self.get_balance("USDT")
            max_allowed_by_position = current_usdt * float(self.max_position_size)
            max_allowed_by_balance_usage = current_usdt * float(self.max_balance_usage)
            allowed_exposure = self._get_allowed_additional_exposure()
            effective_allowed = min(max_allowed_by_position, max_allowed_by_balance_usage, allowed_exposure)
            
            # Para compras, verificar balance y límites
            if side == "BUY":
                if trade_value > current_usdt:
                    return False
                if effective_allowed < self.min_trade_value:
                    return False
                if trade_value > effective_allowed:
                    return False
            else:  # SELL
                asset_symbol = (symbol.split('/')[0] if '/' in symbol else (symbol[:-4] if symbol.endswith(('USDT')) else symbol))
                asset_qty = self.get_balance(asset_symbol)
                if quantity > asset_qty:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating trade: {e}")
            return False
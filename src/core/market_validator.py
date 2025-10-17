"""🔍 Market Validator - Verificación de Ejecución de TP/SL

Este módulo implementa:
- Verificación de precios históricos vs TP/SL configurados
- Detección de ejecuciones perdidas
- Análisis de gaps de precios
- Validación de integridad del sistema de trading
"""

import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

# Importaciones locales
from database.database import db_manager
from database.models import Trade, Portfolio
from .position_manager import PositionManager
from src.config.main_config import APIConfig, MonitoringConfig, CacheConfig

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class MissedExecution:
    """📊 Información sobre una ejecución perdida"""
    trade_id: int
    symbol: str
    target_price: float
    target_type: str  # "TP" o "SL"
    actual_price_reached: float
    timestamp_reached: datetime
    current_price: float
    potential_pnl_missed: float
    reason: str

class MarketValidator:
    """🔍 Validador de Mercado para verificar ejecuciones perdidas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def check_missed_executions(self, hours_back: int = None) -> List[MissedExecution]:
        if hours_back is None:
            hours_back = MonitoringConfig.DEFAULT_HOURS_BACK
        """🔍 Verificar ejecuciones perdidas en las últimas horas
        
        Args:
            hours_back: Horas hacia atrás para verificar
            
        Returns:
            Lista de ejecuciones perdidas detectadas
        """
        missed_executions = []
        
        try:
            with db_manager.get_db_session() as session:
                # Obtener posiciones activas
                active_trades = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                self.logger.info(f"🔍 Verificando {len(active_trades)} posiciones activas")
                
                for trade in active_trades:
                    # Verificar TP y SL si están configurados
                    if trade.take_profit is not None:
                        missed_tp = self._check_price_reached(
                            trade, trade.take_profit, "TP", hours_back
                        )
                        if missed_tp:
                            missed_executions.append(missed_tp)
                    
                    if trade.stop_loss is not None:
                        missed_sl = self._check_price_reached(
                            trade, trade.stop_loss, "SL", hours_back
                        )
                        if missed_sl:
                            missed_executions.append(missed_sl)
                            
        except Exception as e:
            self.logger.error(f"❌ Error checking missed executions: {e}")
            
        return missed_executions
    
    def _check_price_reached(self, trade: Trade, target_price: float, 
                           target_type: str, hours_back: int) -> Optional[MissedExecution]:
        """🎯 Verificar si un precio objetivo fue alcanzado
        
        Args:
            trade: Trade a verificar
            target_price: Precio objetivo (TP o SL)
            target_type: Tipo de objetivo ("TP" o "SL")
            hours_back: Horas hacia atrás para verificar
            
        Returns:
            MissedExecution si se detectó una ejecución perdida
        """
        try:
            # Obtener datos históricos de precios
            price_data = self._get_historical_prices(
                trade.symbol.replace('/', ''), hours_back
            )
            
            if not price_data:
                return None
            
            # Verificar si el precio objetivo fue alcanzado
            for price_point in price_data:
                timestamp = datetime.fromtimestamp(price_point['timestamp'] / 1000)
                high_price = float(price_point['high'])
                low_price = float(price_point['low'])
                
                # Solo verificar después del tiempo de entrada del trade
                if timestamp <= trade.entry_time:
                    continue
                
                price_reached = False
                actual_price = 0.0
                
                if trade.trade_type == "BUY":
                    if target_type == "TP" and high_price >= target_price:
                        price_reached = True
                        actual_price = high_price
                    elif target_type == "SL" and low_price <= target_price:
                        price_reached = True
                        actual_price = low_price
                else:  # SELL
                    if target_type == "TP" and low_price <= target_price:
                        price_reached = True
                        actual_price = low_price
                    elif target_type == "SL" and high_price >= target_price:
                        price_reached = True
                        actual_price = high_price
                
                if price_reached:
                    # Calcular PnL potencial perdido
                    current_price = self._get_current_price(trade.symbol.replace('/', ''))
                    potential_pnl = self._calculate_missed_pnl(
                        trade, target_price, current_price
                    )
                    
                    return MissedExecution(
                        trade_id=trade.id,
                        symbol=trade.symbol,
                        target_price=target_price,
                        target_type=target_type,
                        actual_price_reached=actual_price,
                        timestamp_reached=timestamp,
                        current_price=current_price,
                        potential_pnl_missed=potential_pnl,
                        reason=f"Price reached {actual_price:.4f} but not executed"
                    )
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking price reached for {trade.symbol}: {e}")
            
        return None
    
    def _get_historical_prices(self, symbol: str, hours_back: int) -> List[Dict]:
        """📈 Obtener precios históricos usando Capital.com
        
        Args:
            symbol: Símbolo (ej: Bitcoin/USD)
            hours_back: Horas hacia atrás
            
        Returns:
            Lista de datos de precios
        """
        try:
            # Si tenemos referencia a TradingBot con Capital.com, usar su cliente
            if hasattr(self, 'trading_bot') and self.trading_bot and hasattr(self.trading_bot, 'capital_client'):
                try:
                    return self.trading_bot.capital_client.get_historical_prices(symbol, hours_back)
                except Exception as e:
                    self.logger.warning(f"Error obteniendo datos históricos de Capital.com para {symbol}: {e}")
            
            # Fallback: retornar lista vacía si no hay datos disponibles
            self.logger.warning(f"No se pudieron obtener datos históricos para {symbol}")
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching historical prices for {symbol}: {e}")
            return []
    
    def _get_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual usando Capital.com"""
        try:
            # Si tenemos referencia a TradingBot, usar su método centralizado
            if hasattr(self, 'trading_bot') and self.trading_bot:
                return float(self.trading_bot._get_current_price(symbol))
            
            # Fallback: usar Capital.com directamente si está disponible
            if hasattr(self, 'capital_client') and self.capital_client:
                try:
                    price = self.capital_client.get_current_price(symbol)
                    if price > 0:
                        return price
                except Exception as e:
                    self.logger.warning(f"Error obteniendo precio de Capital.com para {symbol}: {e}")
            
            # Último fallback: usar precio de la base de datos
            from src.database.database import db_manager
            last_trade_price = db_manager.get_last_trade_for_symbol(symbol, is_paper=False)
            if last_trade_price:
                return last_trade_price
            
            self.logger.warning(f"No se pudo obtener precio para {symbol}")
            return 0.0
        except Exception as e:
            self.logger.error(f"❌ Error fetching current price for {symbol}: {e}")
            return 0.0
    
    def _calculate_missed_pnl(self, trade: Trade, target_price: float, 
                            current_price: float) -> float:
        """💰 Calcular PnL potencial perdido
        
        Args:
            trade: Trade original
            target_price: Precio objetivo que se alcanzó
            current_price: Precio actual
            
        Returns:
            PnL potencial perdido
        """
        try:
            if trade.trade_type == "BUY":
                # PnL si se hubiera ejecutado en target_price
                target_pnl = (target_price - trade.entry_price) * trade.quantity
                # PnL actual con precio actual
                current_pnl = (current_price - trade.entry_price) * trade.quantity
            else:  # SELL
                target_pnl = (trade.entry_price - target_price) * trade.quantity
                current_pnl = (trade.entry_price - current_price) * trade.quantity
            
            return target_pnl - current_pnl
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating missed PnL: {e}")
            return 0.0
    
    def generate_missed_executions_report(self, hours_back: int = None) -> str:
        if hours_back is None:
            hours_back = MonitoringConfig.DEFAULT_HOURS_BACK
        """📊 Generar reporte de ejecuciones perdidas
        
        Args:
            hours_back: Horas hacia atrás para verificar
            
        Returns:
            Reporte formateado
        """
        missed_executions = self.check_missed_executions(hours_back)
        
        if not missed_executions:
            return f"✅ No se detectaron ejecuciones perdidas en las últimas {hours_back} horas"
        
        report = f"🔍 REPORTE DE EJECUCIONES PERDIDAS ({hours_back}h)\n"
        report += "=" * 60 + "\n\n"
        
        total_missed_pnl = 0.0
        
        for i, missed in enumerate(missed_executions, 1):
            report += f"{i}. {missed.symbol} (Trade #{missed.trade_id})\n"
            report += f"   Tipo: {missed.target_type}\n"
            report += f"   Precio objetivo: ${missed.target_price:.4f}\n"
            report += f"   Precio alcanzado: ${missed.actual_price_reached:.4f}\n"
            report += f"   Timestamp: {missed.timestamp_reached.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"   Precio actual: ${missed.current_price:.4f}\n"
            report += f"   PnL perdido: ${missed.potential_pnl_missed:.2f}\n"
            report += f"   Razón: {missed.reason}\n\n"
            
            total_missed_pnl += missed.potential_pnl_missed
        
        report += f"💰 TOTAL PnL PERDIDO: ${total_missed_pnl:.2f}\n"
        report += f"📊 EJECUCIONES PERDIDAS: {len(missed_executions)}\n"
        
        return report

# Instancia global
market_validator = MarketValidator()
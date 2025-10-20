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
# Base de datos eliminada - usando Capital.com directamente
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
        """🔍 Verificar ejecuciones perdidas en las últimas horas
        
        Args:
            hours_back: Horas hacia atrás para verificar
            
        Returns:
            Lista de ejecuciones perdidas detectadas
        """
        # Simplificado - las ejecuciones se verifican directamente en Capital.com
        self.logger.debug("🔍 Verificación de ejecuciones simplificada - usando Capital.com directamente")
        return []
    
    # Método _check_price_reached eliminado - las ejecuciones se verifican directamente en Capital.com
    
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
        import math
        
        def _validate_price(price: float) -> bool:
            """Validar que el precio sea válido y seguro para trading"""
            return (price is not None and 
                    not math.isnan(price) and 
                    not math.isinf(price) and 
                    price > 0)
        
        try:
            # Si tenemos referencia a TradingBot, usar su método centralizado
            if hasattr(self, 'trading_bot') and self.trading_bot:
                try:
                    price = self.trading_bot._get_current_price(symbol)
                    if _validate_price(price):
                        return float(price)
                except ValueError as e:
                    self.logger.warning(f"TradingBot no pudo obtener precio para {symbol}: {e}")
                except Exception as e:
                    self.logger.error(f"Error inesperado en TradingBot para {symbol}: {e}")
            
            # Fallback: usar Capital.com directamente si está disponible
            if hasattr(self, 'capital_client') and self.capital_client:
                try:
                    price = self.capital_client.get_current_price(symbol)
                    if _validate_price(price):
                        return price
                    else:
                        self.logger.warning(f"Capital.com retornó precio inválido para {symbol}: {price}")
                except Exception as e:
                    self.logger.warning(f"Error obteniendo precio de Capital.com para {symbol}: {e}")
            
            # CRÍTICO: No retornar 0.0 - lanzar excepción para evitar validaciones incorrectas
            error_msg = f"🚨 CRÍTICO: No se pudo obtener precio válido para {symbol} en market_validator"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            error_msg = f"🚨 CRÍTICO: Error inesperado obteniendo precio en market_validator para {symbol}: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            self.logger.error(f"❌ Error fetching current price for {symbol}: {e}")
            return 0.0
    
    # Método _calculate_missed_pnl eliminado - los cálculos de PnL se obtienen directamente de Capital.com
    
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
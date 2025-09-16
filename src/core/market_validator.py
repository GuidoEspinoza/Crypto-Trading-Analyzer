"""🔍 Market Validator - Verificación de Ejecución de TP/SL

Este módulo implementa:
- Verificación de precios históricos vs TP/SL configurados
- Detección de ejecuciones perdidas
- Análisis de gaps de precios
- Validación de integridad del sistema de trading

Optimizaciones implementadas:
- Parámetros configurables desde config
- Manejo mejorado de errores
- Validación de datos de entrada
- Cacheo de precios para mejor rendimiento
- Timeframes configurables
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from functools import lru_cache
import time

# Importaciones locales
from ..database.database import db_manager
from ..database.models import Trade, Portfolio
from .position_manager import PositionManager
from src.config.config_manager import ConfigManager

# Configuración centralizada
config_manager = ConfigManager()
config = config_manager.get_consolidated_config()

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class MissedExecution:
    """📊 Información sobre una ejecución perdida
    
    Attributes:
        trade_id: ID único del trade
        symbol: Símbolo del par de trading
        target_price: Precio objetivo configurado
        target_type: Tipo de objetivo ("TP" para Take Profit, "SL" para Stop Loss)
        actual_price_reached: Precio real alcanzado en el mercado
        timestamp_reached: Momento cuando se alcanzó el precio
        current_price: Precio actual del mercado
        potential_pnl_missed: PnL potencial perdido por no ejecutar
        reason: Descripción del motivo de la ejecución perdida
        confidence_score: Nivel de confianza en la detección (0.0-1.0)
    """
    trade_id: int
    symbol: str
    target_price: float
    target_type: str  # "TP" o "SL"
    actual_price_reached: float
    timestamp_reached: datetime
    current_price: float
    potential_pnl_missed: float
    reason: str
    confidence_score: float = field(default=1.0)
    
    def __post_init__(self):
        """Validar datos después de la inicialización"""
        if self.target_type not in ["TP", "SL"]:
            raise ValueError(f"target_type debe ser 'TP' o 'SL', recibido: {self.target_type}")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"confidence_score debe estar entre 0.0 y 1.0, recibido: {self.confidence_score}")
        if self.target_price <= 0 or self.actual_price_reached <= 0 or self.current_price <= 0:
            raise ValueError("Los precios deben ser positivos")

class MarketValidator:
    """🔍 Validador de Mercado para verificar ejecuciones perdidas
    
    Características:
    - Verificación configurable de ejecuciones perdidas
    - Cacheo de precios para mejor rendimiento
    - Validación robusta de datos
    - Timeframes configurables
    - Manejo avanzado de errores
    """
    
    def __init__(self, 
                 cache_duration: int = None,
                 default_timeframe: str = None,
                 max_retries: int = None,
                 confidence_threshold: float = None):
        """Inicializar el validador de mercado
        
        Args:
            cache_duration: Duración del cache en segundos (default: desde config)
            default_timeframe: Timeframe por defecto para análisis (default: desde config)
            max_retries: Máximo número de reintentos para requests (default: desde config)
            confidence_threshold: Umbral mínimo de confianza para reportar ejecuciones perdidas
        """
        self.logger = logging.getLogger(__name__)
        self.binance_base_url = config.get("api", {}).get("binance_base_url", "https://api.binance.com")
        
        # Configuraciones con valores por defecto desde config
        self.cache_duration = cache_duration or config.get("monitoring", {}).get("cache_duration", 300)
        self.default_timeframe = default_timeframe or config.get("monitoring", {}).get("default_timeframe", "1h")
        self.max_retries = max_retries or config.get("api", {}).get("max_retries", 3)
        self.confidence_threshold = confidence_threshold or config.get("monitoring", {}).get("confidence_threshold", 0.8)
        
        # Cache para precios históricos
        self._price_cache = {}
        self._cache_timestamps = {}
        
        self.logger.info(f"🔍 MarketValidator inicializado con timeframe: {self.default_timeframe}, cache: {self.cache_duration}s")
        
    def check_missed_executions(self, 
                               hours_back: int = None,
                               symbols_filter: List[str] = None,
                               min_confidence: float = None) -> List[MissedExecution]:
        """🔍 Verificar ejecuciones perdidas en las últimas horas
        
        Args:
            hours_back: Horas hacia atrás para verificar (default: desde config)
            symbols_filter: Lista de símbolos específicos a verificar (opcional)
            min_confidence: Confianza mínima para incluir en resultados
            
        Returns:
            Lista de ejecuciones perdidas detectadas
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        # Validar parámetros
        if hours_back is None:
            hours_back = config.get("monitoring", {}).get("default_hours_back", 24)
        
        if hours_back <= 0:
            raise ValueError(f"hours_back debe ser positivo, recibido: {hours_back}")
        
        if min_confidence is None:
            min_confidence = self.confidence_threshold
        
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(f"min_confidence debe estar entre 0.0 y 1.0, recibido: {min_confidence}")
        
        missed_executions = []
        processed_trades = 0
        
        try:
            with db_manager.get_db_session() as session:
                # Construir query base
                query = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                )
                
                # Aplicar filtro de símbolos si se especifica
                if symbols_filter:
                    # Convertir símbolos al formato de la base de datos
                    db_symbols = [s.replace('', '/') if '/' not in s else s for s in symbols_filter]
                    query = query.filter(Trade.symbol.in_(db_symbols))
                
                active_trades = query.all()
                
                self.logger.info(f"🔍 Verificando {len(active_trades)} posiciones activas (últimas {hours_back}h)")
                
                for trade in active_trades:
                    try:
                        processed_trades += 1
                        
                        # Verificar TP si está configurado
                        if trade.take_profit is not None and trade.take_profit > 0:
                            missed_tp = self._check_price_reached(
                                trade, trade.take_profit, "TP", hours_back
                            )
                            if missed_tp and missed_tp.confidence_score >= min_confidence:
                                missed_executions.append(missed_tp)
                        
                        # Verificar SL si está configurado
                        if trade.stop_loss is not None and trade.stop_loss > 0:
                            missed_sl = self._check_price_reached(
                                trade, trade.stop_loss, "SL", hours_back
                            )
                            if missed_sl and missed_sl.confidence_score >= min_confidence:
                                missed_executions.append(missed_sl)
                                
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error procesando trade {trade.id}: {e}")
                        continue
                        
                self.logger.info(f"✅ Procesados {processed_trades} trades, encontradas {len(missed_executions)} ejecuciones perdidas")
                            
        except Exception as e:
            self.logger.error(f"❌ Error checking missed executions: {e}")
            raise
            
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
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        # Validaciones
        if target_price <= 0:
            raise ValueError(f"target_price debe ser positivo: {target_price}")
        if target_type not in ["TP", "SL"]:
            raise ValueError(f"target_type debe ser 'TP' o 'SL': {target_type}")
        if hours_back <= 0:
            raise ValueError(f"hours_back debe ser positivo: {hours_back}")
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
                    
                    # Calcular confianza basada en la diferencia de precios
                    price_diff_ratio = abs(actual_price - target_price) / target_price
                    confidence_score = max(0.5, 1.0 - (price_diff_ratio * 10))  # Mínimo 50% de confianza
                    
                    # Ajustar confianza según el volumen (si está disponible)
                    volume = price_point.get('volume', 0)
                    if volume > 0:
                        # Normalizar volumen (asumiendo que volumen alto = mayor confianza)
                        volume_factor = min(1.0, volume / 1000000)  # Normalizar a 1M como referencia
                        confidence_score = min(1.0, confidence_score + (volume_factor * 0.2))
                    
                    return MissedExecution(
                        trade_id=trade.id,
                        symbol=trade.symbol,
                        target_price=target_price,
                        target_type=target_type,
                        actual_price_reached=actual_price,
                        timestamp_reached=timestamp,
                        current_price=current_price,
                        potential_pnl_missed=potential_pnl,
                        reason=f"Price reached {actual_price:.4f} but not executed",
                        confidence_score=confidence_score
                    )
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking price reached for {trade.symbol}: {e}")
            
        return None
    
    def _get_historical_prices(self, symbol: str, hours_back: int, 
                                 timeframe: str = None) -> List[Dict]:
        """📈 Obtener precios históricos de Binance con cacheo
        
        Args:
            symbol: Símbolo (ej: BTCUSDT)
            hours_back: Horas hacia atrás
            timeframe: Timeframe para los datos (default: self.default_timeframe)
            
        Returns:
            Lista de datos de precios
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        # Validaciones
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"symbol debe ser un string válido: {symbol}")
        if hours_back <= 0:
            raise ValueError(f"hours_back debe ser positivo: {hours_back}")
        
        if timeframe is None:
            timeframe = self.default_timeframe
        
        # Verificar cache
        cache_key = f"{symbol}_{hours_back}_{timeframe}"
        current_time = time.time()
        
        if (cache_key in self._price_cache and 
            cache_key in self._cache_timestamps and
            current_time - self._cache_timestamps[cache_key] < self.cache_duration):
            self.logger.debug(f"📋 Usando cache para {symbol} ({timeframe})")
            return self._price_cache[cache_key]
        try:
            # Calcular timestamps
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = int((datetime.now() - timedelta(hours=hours_back)).timestamp() * 1000)
            
            # Configurar parámetros de la request
            url = f"{config.get('api', {}).get('binance_base_url', 'https://api.binance.com')}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'startTime': start_time,
                'endTime': end_time,
                'limit': config.get("api", {}).get("default_klines_limit", 1000)
            }
            
            # Realizar request con reintentos
            price_data = []
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(url, params=params, timeout=config.get("api", {}).get("request_timeout", 10))
                    response.raise_for_status()
                    
                    klines = response.json()
                    
                    # Convertir a formato más manejable
                    for kline in klines:
                        price_data.append({
                            'timestamp': int(kline[0]),
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5])
                        })
                    
                    # Guardar en cache
                    self._price_cache[cache_key] = price_data
                    self._cache_timestamps[cache_key] = current_time
                    
                    self.logger.debug(f"📈 Obtenidos {len(price_data)} puntos de precio para {symbol} ({timeframe})")
                    return price_data
                    
                except requests.RequestException as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Backoff exponencial
                        self.logger.warning(f"⚠️ Intento {attempt + 1} falló para {symbol}, reintentando en {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        raise
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching historical prices for {symbol}: {e}")
            return []
    
    @lru_cache(maxsize=100)
    def _get_current_price_cached(self, symbol: str, cache_time: int) -> float:
        """💰 Obtener precio actual con cache (método interno)
        
        Args:
            symbol: Símbolo (ej: BTCUSDT)
            cache_time: Timestamp para invalidar cache
            
        Returns:
            Precio actual
        """
        return self._fetch_current_price(symbol)
    
    def _get_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual con cacheo automático
        
        Args:
            symbol: Símbolo (ej: BTCUSDT)
            
        Returns:
            Precio actual
            
        Raises:
            ValueError: Si el símbolo es inválido
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"symbol debe ser un string válido: {symbol}")
        
        # Usar cache con ventana de 30 segundos
        cache_window = 30
        cache_time = int(time.time() // cache_window)
        
        try:
            return self._get_current_price_cached(symbol, cache_time)
        except Exception as e:
            self.logger.error(f"❌ Error fetching current price for {symbol}: {e}")
            return 0.0
    
    def _fetch_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual desde la API (sin cache)
        
        Args:
            symbol: Símbolo (ej: BTCUSDT)
            
        Returns:
            Precio actual
        """
        for attempt in range(self.max_retries):
            try:
                url = f"{config.get('api', {}).get('binance_base_url', 'https://api.binance.com')}/api/v3/ticker/price"
                params = {'symbol': symbol}
                
                response = requests.get(url, params=params, timeout=config.get("api", {}).get("request_timeout", 10))
                response.raise_for_status()
                
                data = response.json()
                price = float(data['price'])
                
                if price <= 0:
                    raise ValueError(f"Precio inválido recibido: {price}")
                
                return price
                
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"⚠️ Intento {attempt + 1} falló para precio de {symbol}, reintentando en {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    raise
        
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
    
    def generate_missed_executions_report(self, 
                                         hours_back: int = None,
                                         symbols_filter: List[str] = None,
                                         min_confidence: float = None,
                                         include_summary: bool = True,
                                         sort_by: str = "pnl") -> str:
        """📊 Generar reporte detallado de ejecuciones perdidas
        
        Args:
            hours_back: Horas hacia atrás para verificar (default: desde config)
            symbols_filter: Lista de símbolos específicos a incluir
            min_confidence: Confianza mínima para incluir en el reporte
            include_summary: Si incluir resumen estadístico
            sort_by: Criterio de ordenamiento ('pnl', 'time', 'symbol', 'confidence')
            
        Returns:
            Reporte formateado
            
        Raises:
            ValueError: Si sort_by no es válido
        """
        if hours_back is None:
            hours_back = config.get("monitoring", {}).get("default_hours_back", 24)
        
        if sort_by not in ["pnl", "time", "symbol", "confidence"]:
            raise ValueError(f"sort_by debe ser 'pnl', 'time', 'symbol' o 'confidence': {sort_by}")
        
        missed_executions = self.check_missed_executions(
            hours_back=hours_back,
            symbols_filter=symbols_filter,
            min_confidence=min_confidence
        )
        
        if not missed_executions:
            return f"✅ No se detectaron ejecuciones perdidas en las últimas {hours_back} horas"
        
        # Ordenar según criterio especificado
        if sort_by == "pnl":
            missed_executions.sort(key=lambda x: abs(x.potential_pnl_missed), reverse=True)
        elif sort_by == "time":
            missed_executions.sort(key=lambda x: x.timestamp_reached, reverse=True)
        elif sort_by == "symbol":
            missed_executions.sort(key=lambda x: x.symbol)
        elif sort_by == "confidence":
            missed_executions.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Generar reporte
        report = f"🔍 REPORTE DE EJECUCIONES PERDIDAS ({hours_back}h)\n"
        report += "=" * 70 + "\n"
        
        if symbols_filter:
            report += f"📊 Símbolos filtrados: {', '.join(symbols_filter)}\n"
        if min_confidence and min_confidence > 0:
            report += f"🎯 Confianza mínima: {min_confidence:.1%}\n"
        report += f"📈 Ordenado por: {sort_by.upper()}\n\n"
        
        total_missed_pnl = 0.0
        tp_count = 0
        sl_count = 0
        
        for i, missed in enumerate(missed_executions, 1):
            # Emoji según tipo
            type_emoji = "🎯" if missed.target_type == "TP" else "🛡️"
            confidence_bar = "█" * int(missed.confidence_score * 10) + "░" * (10 - int(missed.confidence_score * 10))
            
            report += f"{i}. {type_emoji} {missed.symbol} (Trade #{missed.trade_id})\n"
            report += f"   📊 Tipo: {missed.target_type} | Confianza: {confidence_bar} {missed.confidence_score:.1%}\n"
            report += f"   🎯 Precio objetivo: ${missed.target_price:.4f}\n"
            report += f"   📈 Precio alcanzado: ${missed.actual_price_reached:.4f}\n"
            report += f"   ⏰ Timestamp: {missed.timestamp_reached.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"   💰 Precio actual: ${missed.current_price:.4f}\n"
            report += f"   💸 PnL perdido: ${missed.potential_pnl_missed:+.2f}\n"
            report += f"   📝 Razón: {missed.reason}\n\n"
            
            total_missed_pnl += missed.potential_pnl_missed
            if missed.target_type == "TP":
                tp_count += 1
            else:
                sl_count += 1
        
        if include_summary:
            report += "=" * 70 + "\n"
            report += "📊 RESUMEN ESTADÍSTICO\n"
            report += "=" * 70 + "\n"
            report += f"💰 TOTAL PnL PERDIDO: ${total_missed_pnl:+.2f}\n"
            report += f"📊 EJECUCIONES PERDIDAS: {len(missed_executions)}\n"
            report += f"🎯 Take Profits perdidos: {tp_count}\n"
            report += f"🛡️ Stop Losses perdidos: {sl_count}\n"
            
            if missed_executions:
                avg_confidence = sum(m.confidence_score for m in missed_executions) / len(missed_executions)
                report += f"📈 Confianza promedio: {avg_confidence:.1%}\n"
                
                symbols_affected = len(set(m.symbol for m in missed_executions))
                report += f"🔗 Símbolos afectados: {symbols_affected}\n"
        
        return report
    
    def clear_cache(self) -> None:
        """🧹 Limpiar cache de precios"""
        self._price_cache.clear()
        self._cache_timestamps.clear()
        self._get_current_price_cached.cache_clear()
        self.logger.info("🧹 Cache de precios limpiado")
    
    def get_cache_stats(self) -> Dict[str, Union[int, float]]:
        """📊 Obtener estadísticas del cache
        
        Returns:
            Diccionario con estadísticas del cache
        """
        current_time = time.time()
        valid_entries = 0
        
        for key, timestamp in self._cache_timestamps.items():
            if current_time - timestamp < self.cache_duration:
                valid_entries += 1
        
        cache_info = self._get_current_price_cached.cache_info()
        
        return {
            'price_cache_entries': len(self._price_cache),
            'valid_cache_entries': valid_entries,
            'current_price_cache_hits': cache_info.hits,
            'current_price_cache_misses': cache_info.misses,
            'cache_hit_ratio': cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0.0,
            'cache_duration': self.cache_duration
        }
    
    def validate_configuration(self) -> Dict[str, bool]:
        """✅ Validar configuración del validador
        
        Returns:
            Diccionario con resultados de validación
        """
        validation_results = {
            'cache_duration_valid': self.cache_duration > 0,
            'timeframe_valid': self.default_timeframe in ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'],
            'max_retries_valid': 1 <= self.max_retries <= 10,
            'confidence_threshold_valid': 0.0 <= self.confidence_threshold <= 1.0,
            'api_config_available': 'api' in config and 'binance_base_url' in config.get('api', {}),
            'monitoring_config_available': 'monitoring' in config and 'default_hours_back' in config.get('monitoring', {})
        }
        
        all_valid = all(validation_results.values())
        validation_results['all_valid'] = all_valid
        
        if not all_valid:
            invalid_configs = [k for k, v in validation_results.items() if not v and k != 'all_valid']
            self.logger.warning(f"⚠️ Configuraciones inválidas detectadas: {invalid_configs}")
        
        return validation_results
    
    def __str__(self) -> str:
        """📝 Representación string del validador"""
        return (f"MarketValidator(timeframe={self.default_timeframe}, "
                f"cache_duration={self.cache_duration}s, "
                f"max_retries={self.max_retries}, "
                f"confidence_threshold={self.confidence_threshold:.1%})")
    
    def __repr__(self) -> str:
        """📝 Representación detallada del validador"""
        return self.__str__()

# Instancia global con configuración por defecto
market_validator = MarketValidator()

# Función de conveniencia para acceso rápido
def get_market_validator(**kwargs) -> MarketValidator:
    """🔍 Obtener instancia de MarketValidator con configuración personalizada
    
    Args:
        **kwargs: Parámetros de configuración para MarketValidator
        
    Returns:
        Instancia configurada de MarketValidator
    """
    return MarketValidator(**kwargs)
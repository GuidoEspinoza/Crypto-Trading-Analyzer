"""📊 Data Fetcher - Módulo de Obtención de Datos de Mercado
Módulo para obtener datos históricos y en tiempo real de diferentes fuentes.

Desarrollado por: Experto en Trading & Programación
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)

class DataFetcher:
    """📊 Fetcher de datos de mercado"""
    
    def __init__(self, exchange_name: str = "binance"):
        """Inicializar el data fetcher
        
        Args:
            exchange_name: Nombre del exchange (binance, coinbase, etc.)
        """
        self.exchange_name = exchange_name
        self.exchange = self._initialize_exchange(exchange_name)
        
    def _initialize_exchange(self, exchange_name: str):
        """Inicializar conexión al exchange"""
        try:
            if exchange_name.lower() == "binance":
                return ccxt.binance({
                    'sandbox': False,
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
            elif exchange_name.lower() == "coinbase":
                return ccxt.coinbasepro({
                    'sandbox': False,
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
            else:
                logger.warning(f"Exchange {exchange_name} no soportado, usando Binance")
                return ccxt.binance({
                    'sandbox': False,
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
        except Exception as e:
            logger.error(f"Error inicializando exchange {exchange_name}: {e}")
            raise
    
    def get_historical_data(self, 
                          symbol: str, 
                          timeframe: str = "1h", 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          limit: int = 1000) -> Optional[pd.DataFrame]:
        """Obtener datos históricos
        
        Args:
            symbol: Símbolo del par (ej: 'BTC/USDT')
            timeframe: Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            start_date: Fecha de inicio
            end_date: Fecha de fin
            limit: Límite de velas
            
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        try:
            # Convertir símbolo al formato del exchange
            if '/' not in symbol:
                if symbol.endswith('USDT'):
                    symbol = symbol[:-4] + '/USDT'
                else:
                    symbol = symbol + '/USDT'
            
            # Configurar parámetros de tiempo
            since = None
            if start_date:
                since = int(start_date.timestamp() * 1000)
            
            # Obtener datos
            ohlcv_data = []
            
            if since and end_date:
                # Obtener datos por chunks si hay rango de fechas
                current_time = since
                end_timestamp = int(end_date.timestamp() * 1000)
                
                while current_time < end_timestamp:
                    try:
                        chunk = self.exchange.fetch_ohlcv(
                            symbol=symbol,
                            timeframe=timeframe,
                            since=current_time,
                            limit=min(limit, 1000)
                        )
                        
                        if not chunk:
                            break
                            
                        ohlcv_data.extend(chunk)
                        
                        # Actualizar timestamp para siguiente chunk
                        current_time = chunk[-1][0] + 1
                        
                        # Rate limiting
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error obteniendo chunk de datos: {e}")
                        break
            else:
                # Obtener datos simples
                ohlcv_data = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=limit
                )
            
            if not ohlcv_data:
                logger.warning(f"No se obtuvieron datos para {symbol}")
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convertir timestamp a datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Asegurar tipos numéricos
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            # Filtrar por fecha de fin si se especifica
            if end_date:
                df = df[df.index <= end_date]
            
            # Remover duplicados y ordenar
            df = df.drop_duplicates().sort_index()
            
            logger.info(f"✅ Datos obtenidos para {symbol}: {len(df)} velas desde {df.index[0]} hasta {df.index[-1]}")
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos para {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtener precio actual
        
        Args:
            symbol: Símbolo del par
            
        Returns:
            Precio actual o None si hay error
        """
        try:
            # Convertir símbolo al formato del exchange
            if '/' not in symbol:
                if symbol.endswith('USDT'):
                    symbol = symbol[:-4] + '/USDT'
                else:
                    symbol = symbol + '/USDT'
            
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
            
        except Exception as e:
            logger.error(f"Error obteniendo precio actual para {symbol}: {e}")
            return None
    
    def get_market_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtener datos de mercado recientes
        
        Args:
            symbol: Símbolo del par
            timeframe: Timeframe
            limit: Número de velas
            
        Returns:
            DataFrame con datos recientes
        """
        return self.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
    
    def get_available_symbols(self) -> List[str]:
        """Obtener lista de símbolos disponibles
        
        Returns:
            Lista de símbolos disponibles
        """
        try:
            markets = self.exchange.load_markets()
            # Filtrar solo pares USDT activos
            usdt_pairs = [
                symbol for symbol, market in markets.items() 
                if symbol.endswith('/USDT') and market['active']
            ]
            return sorted(usdt_pairs)
            
        except Exception as e:
            logger.error(f"Error obteniendo símbolos disponibles: {e}")
            return []
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validar si un símbolo existe
        
        Args:
            symbol: Símbolo a validar
            
        Returns:
            True si el símbolo existe
        """
        try:
            # Convertir símbolo al formato del exchange
            if '/' not in symbol:
                if symbol.endswith('USDT'):
                    symbol = symbol[:-4] + '/USDT'
                else:
                    symbol = symbol + '/USDT'
            
            markets = self.exchange.load_markets()
            return symbol in markets and markets[symbol]['active']
            
        except Exception as e:
            logger.error(f"Error validando símbolo {symbol}: {e}")
            return False
    
    def get_exchange_info(self) -> Dict:
        """Obtener información del exchange
        
        Returns:
            Información del exchange
        """
        try:
            return {
                'name': self.exchange.name,
                'id': self.exchange.id,
                'has_ohlcv': self.exchange.has['fetchOHLCV'],
                'has_ticker': self.exchange.has['fetchTicker'],
                'timeframes': list(self.exchange.timeframes.keys()) if hasattr(self.exchange, 'timeframes') else [],
                'rate_limit': getattr(self.exchange, 'rateLimit', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Error obteniendo información del exchange: {e}")
            return {}
"""
Market Hours Checker
Verifica si los mercados están abiertos antes de ejecutar trades
"""

import logging
from datetime import datetime, time, timezone
from typing import Dict, Optional, Tuple
import pytz

logger = logging.getLogger(__name__)

class MarketHoursChecker:
    """
    Verificador de horarios de mercado para diferentes tipos de activos
    """
    
    def __init__(self):
        # Definir zonas horarias
        self.utc = pytz.UTC
        self.ny_tz = pytz.timezone('America/New_York')
        self.london_tz = pytz.timezone('Europe/London')
        
        # Horarios de mercado por tipo de activo
        self.market_hours = {
            'FOREX': {
                'timezone': self.utc,
                'days': [0, 1, 2, 3, 4],  # Lunes a Viernes
                'open_time': time(22, 0),  # Domingo 22:00 UTC
                'close_time': time(22, 0),  # Viernes 22:00 UTC
                'always_open': True  # Forex está abierto 24/5
            },
            'CRYPTO': {
                'timezone': self.utc,
                'days': list(range(7)),  # Todos los días
                'open_time': time(0, 0),
                'close_time': time(23, 59),
                'always_open': True  # Crypto está abierto 24/7
            },
            'INDICES': {
                'timezone': self.ny_tz,
                'days': [0, 1, 2, 3, 4],  # Lunes a Viernes
                'open_time': time(9, 30),  # 9:30 AM EST
                'close_time': time(16, 0),  # 4:00 PM EST
                'always_open': False
            },
            'COMMODITIES': {
                'timezone': self.ny_tz,
                'days': [0, 1, 2, 3, 4],  # Lunes a Viernes
                'open_time': time(9, 0),   # 9:00 AM EST
                'close_time': time(17, 0), # 5:00 PM EST
                'always_open': False
            }
        }
        
        # Mapeo de símbolos a tipos de mercado
        self.symbol_to_market = {
            # Crypto
            'BTCUSD': 'CRYPTO',
            'ETHUSD': 'CRYPTO',
            'SOLUSD': 'CRYPTO',
            'ADAUSD': 'CRYPTO',
            'XRPUSD': 'CRYPTO',
            
            # Indices
            'US100': 'INDICES',
            'US500': 'INDICES',
            'DE40': 'INDICES',
            
            # Commodities
            'GOLD': 'COMMODITIES',
            'SILVER': 'COMMODITIES',
            'OIL_CRUDE': 'COMMODITIES',
            
            # Forex
            'EURUSD': 'FOREX',
            'GBPUSD': 'FOREX',
            'USDJPY': 'FOREX'
        }
    
    def get_market_type(self, symbol: str) -> str:
        """
        Obtener el tipo de mercado para un símbolo
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Tipo de mercado ('FOREX', 'CRYPTO', 'INDICES', 'COMMODITIES')
        """
        return self.symbol_to_market.get(symbol, 'FOREX')  # Default a FOREX
    
    def is_market_open(self, symbol: str, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Verificar si el mercado está abierto para un símbolo específico
        
        Args:
            symbol: Símbolo del activo
            current_time: Tiempo actual (opcional, usa datetime.now() si no se proporciona)
            
        Returns:
            Tuple (is_open: bool, reason: str)
        """
        if current_time is None:
            current_time = datetime.now(self.utc)
        
        market_type = self.get_market_type(symbol)
        market_config = self.market_hours[market_type]
        
        # Si el mercado está siempre abierto (Crypto, Forex)
        if market_config['always_open']:
            if market_type == 'CRYPTO':
                return True, f"Crypto market is always open (24/7)"
            elif market_type == 'FOREX':
                # Forex está cerrado solo los fines de semana
                weekday = current_time.weekday()
                if weekday == 5:  # Sábado
                    return False, f"Forex market is closed on Saturday"
                elif weekday == 6:  # Domingo antes de las 22:00 UTC
                    if current_time.time() < time(22, 0):
                        return False, f"Forex market opens Sunday at 22:00 UTC"
                return True, f"Forex market is open (24/5)"
        
        # Para mercados con horarios específicos (Indices, Commodities)
        market_tz = market_config['timezone']
        local_time = current_time.astimezone(market_tz)
        
        # Verificar día de la semana
        if local_time.weekday() not in market_config['days']:
            return False, f"{market_type} market is closed on weekends"
        
        # Verificar horario
        current_time_only = local_time.time()
        open_time = market_config['open_time']
        close_time = market_config['close_time']
        
        if open_time <= current_time_only <= close_time:
            return True, f"{market_type} market is open ({open_time} - {close_time} {market_tz.zone})"
        else:
            return False, f"{market_type} market is closed (opens at {open_time} {market_tz.zone})"
    
    def get_market_status_summary(self, symbols: list) -> Dict[str, Dict]:
        """
        Obtener resumen del estado de mercado para múltiples símbolos
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Diccionario con el estado de cada símbolo
        """
        current_time = datetime.now(self.utc)
        summary = {}
        
        for symbol in symbols:
            is_open, reason = self.is_market_open(symbol, current_time)
            market_type = self.get_market_type(symbol)
            
            summary[symbol] = {
                'is_open': is_open,
                'reason': reason,
                'market_type': market_type,
                'checked_at': current_time.isoformat()
            }
        
        return summary
    
    def should_trade(self, symbol: str) -> Tuple[bool, str]:
        """
        Determinar si se debe ejecutar un trade para un símbolo
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Tuple (should_trade: bool, reason: str)
        """
        is_open, reason = self.is_market_open(symbol)
        
        if not is_open:
            return False, f"Trading blocked: {reason}"
        
        return True, f"Trading allowed: {reason}"
    
    def get_general_market_status(self) -> Dict[str, list]:
        """
        Obtener un resumen general del estado de los mercados
        
        Returns:
            Diccionario con mercados abiertos y cerrados
        """
        current_time = datetime.now(self.utc)
        open_markets = []
        closed_markets = []
        
        # Verificar cada tipo de mercado
        market_types = ['FOREX', 'CRYPTO', 'INDICES', 'COMMODITIES']
        
        for market_type in market_types:
            if market_type == 'CRYPTO':
                # Crypto siempre está abierto
                open_markets.append(market_type)
            elif market_type == 'FOREX':
                # Verificar horario de Forex (24/5)
                weekday = current_time.weekday()
                if weekday < 5:  # Lunes a Viernes
                    open_markets.append(market_type)
                else:
                    closed_markets.append(market_type)
            else:
                # Para INDICES y COMMODITIES, verificar horario de NY
                ny_time = current_time.astimezone(self.timezones['US/Eastern'])
                current_time_only = ny_time.time()
                
                if (weekday < 5 and 
                    time(9, 30) <= current_time_only <= time(16, 0)):
                    open_markets.append(market_type)
                else:
                    closed_markets.append(market_type)
        
        return {
            'open_markets': open_markets,
            'closed_markets': closed_markets
        }

# Instancia global para uso en el bot
market_hours_checker = MarketHoursChecker()
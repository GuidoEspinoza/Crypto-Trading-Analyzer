"""
Market Hours Checker
Verifica si los mercados están abiertos y si se encuentran en ventanas óptimas de trading
"""

import logging
from datetime import datetime, time, timezone, timedelta
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
        self.ny_tz = pytz.timezone("America/New_York")
        self.london_tz = pytz.timezone("Europe/London")

        # Horarios de mercado por tipo de activo (fallback por tipo)
        self.market_hours = {
            "FOREX": {
                "timezone": self.utc,
                "days": [0, 1, 2, 3, 4],  # Lunes a Viernes
                "open_time": time(22, 0),  # Domingo 22:00 UTC
                "close_time": time(22, 0),  # Viernes 22:00 UTC
                "always_open": True,  # Forex está abierto 24/5
            },
            "CRYPTO": {
                "timezone": self.utc,
                "days": list(range(7)),  # Todos los días
                "open_time": time(0, 0),
                "close_time": time(23, 59),
                "always_open": True,  # Crypto está abierto 24/7
            },
            "INDICES": {
                "timezone": self.ny_tz,
                "days": [0, 1, 2, 3, 4],  # Lunes a Viernes
                "open_time": time(9, 30),  # 9:30 AM New York
                "close_time": time(16, 0),  # 16:00 New York
                "always_open": False,
            },
            "COMMODITIES": {
                "timezone": self.ny_tz,
                "days": [0, 1, 2, 3, 4],  # Lunes a Viernes
                "open_time": time(9, 0),  # 9:00 AM EST
                "close_time": time(17, 0),  # 5:00 PM EST
                "always_open": False,
            },
        }

        # Mapeo de símbolos a tipos de mercado
        self.symbol_to_market = {
            # Crypto
            "BTCUSD": "CRYPTO",
            "ETHUSD": "CRYPTO",
            "SOLUSD": "CRYPTO",
            "ADAUSD": "CRYPTO",
            "XRPUSD": "CRYPTO",
            # Indices
            "US100": "INDICES",
            "US500": "INDICES",
            "US30": "INDICES",
            "RTY": "INDICES",
            "UK100": "INDICES",
            "FR40": "INDICES",
            "HK50": "INDICES",
            "J225": "INDICES",
            "DE40": "INDICES",
            # Commodities
            "GOLD": "COMMODITIES",
            "SILVER": "COMMODITIES",
            # Eliminados del portafolio actual: COPPER, WHEAT, CORN
            "OIL_CRUDE": "COMMODITIES",
            # Forex
            "EURUSD": "FOREX",
            "GBPUSD": "FOREX",
            "USDJPY": "FOREX",
            "NZDUSD": "FOREX",
            "USDNOK": "FOREX",
        }

        # Horarios específicos por símbolo para índices (sesión principal de cada mercado)
        # Estos override se aplican antes del fallback por tipo
        self.symbol_specific_hours = {
            # USA
            "US100": {
                "timezone": self.ny_tz,
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 30),
                "close_time": time(16, 0),
                "always_open": False,
            },
            "US500": {
                "timezone": self.ny_tz,
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 30),
                "close_time": time(16, 0),
                "always_open": False,
            },
            "US30": {
                "timezone": self.ny_tz,
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 30),
                "close_time": time(16, 0),
                "always_open": False,
            },
            "RTY": {
                "timezone": self.ny_tz,
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 30),
                "close_time": time(16, 0),
                "always_open": False,
            },
            # Reino Unido
            "UK100": {
                "timezone": self.london_tz,
                "days": [0, 1, 2, 3, 4],
                "open_time": time(8, 0),   # 08:00 London
                "close_time": time(16, 30),  # 16:30 London
                "always_open": False,
            },
            # Alemania (Xetra)
            "DE40": {
                "timezone": pytz.timezone("Europe/Berlin"),
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 0),   # 09:00 Berlin
                "close_time": time(17, 30),  # 17:30 Berlin
                "always_open": False,
            },
            # Francia (Euronext Paris)
            "FR40": {
                "timezone": pytz.timezone("Europe/Paris"),
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 0),   # 09:00 Paris
                "close_time": time(17, 30),  # 17:30 Paris
                "always_open": False,
            },
            # Hong Kong (HKEX) - simplificado sin pausa de mediodía
            "HK50": {
                "timezone": pytz.timezone("Asia/Hong_Kong"),
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 30),   # 09:30 HKT
                "close_time": time(16, 0),  # 16:00 HKT
                "always_open": False,
            },
            # Japón (TSE) - simplificado sin pausa de mediodía
            "J225": {
                "timezone": pytz.timezone("Asia/Tokyo"),
                "days": [0, 1, 2, 3, 4],
                "open_time": time(9, 0),   # 09:00 JST
                "close_time": time(15, 0),  # 15:00 JST
                "always_open": False,
            },
        }

        # Buffers para evitar apertura/cierre (minutos)
        # Valores por defecto para índices si no hay override específico
        self.default_open_buffer_min = 30
        self.default_close_buffer_min = 30

        # Overrides por símbolo (cuando se requiere mayor cautela)
        self.symbol_buffers = {
            # Small caps suelen ser más volátiles en apertura
            "RTY": {"open_buffer": 45, "close_buffer": 30},
            # Hong Kong puede requerir mayor margen por gaps
            "HK50": {"open_buffer": 30, "close_buffer": 30},
            # Resto usa valores por defecto
        }

        # Pausas de mediodía por símbolo (horas locales)
        # Estas ventanas se excluyen del trading aunque el mercado esté abierto
        self.symbol_lunch_breaks = {
            # Hong Kong: 12:00 - 13:00 HKT
            "HK50": [(time(12, 0), time(13, 0))],
            # Tokio: 11:30 - 12:30 JST
            "J225": [(time(11, 30), time(12, 30))],
            # Australia: sin pausa
        }

    def get_market_type(self, symbol: str) -> str:
        """
        Obtener el tipo de mercado para un símbolo

        Args:
            symbol: Símbolo del activo

        Returns:
            Tipo de mercado ('FOREX', 'CRYPTO', 'INDICES', 'COMMODITIES')
        """
        return self.symbol_to_market.get(symbol, "FOREX")  # Default a FOREX

    def is_market_open(
        self, symbol: str, current_time: Optional[datetime] = None
    ) -> Tuple[bool, str]:
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
        # Config por símbolo si existe, si no, fallback por tipo
        market_config = self.symbol_specific_hours.get(symbol, self.market_hours[market_type])

        # Si el mercado está siempre abierto (Crypto, Forex)
        if market_config["always_open"]:
            if market_type == "CRYPTO":
                return True, f"Crypto market is always open (24/7)"
            elif market_type == "FOREX":
                # Forex está cerrado solo los fines de semana
                weekday = current_time.weekday()
                if weekday == 5:  # Sábado
                    return False, f"Forex market is closed on Saturday"
                elif weekday == 6:  # Domingo antes de las 22:00 UTC
                    if current_time.time() < time(22, 0):
                        return False, f"Forex market opens Sunday at 22:00 UTC"
                return True, f"Forex market is open (24/5)"

        # Para mercados con horarios específicos (Indices, Commodities)
        market_tz = market_config["timezone"]
        local_time = current_time.astimezone(market_tz)

        # Verificar día de la semana
        if local_time.weekday() not in market_config["days"]:
            return False, f"{market_type} market is closed on weekends"

        # Verificar horario
        current_time_only = local_time.time()
        open_time = market_config["open_time"]
        close_time = market_config["close_time"]

        if open_time <= current_time_only <= close_time:
            return (
                True,
                f"{market_type} market is open ({open_time} - {close_time} {market_tz.zone}) | now {local_time.strftime('%H:%M:%S')} {market_tz.zone} / {current_time.strftime('%H:%M:%S')} UTC",
            )
        else:
            return (
                False,
                f"{market_type} market is closed (opens at {open_time} {market_tz.zone}) | now {local_time.strftime('%H:%M:%S')} {market_tz.zone} / {current_time.strftime('%H:%M:%S')} UTC",
            )

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
                "is_open": is_open,
                "reason": reason,
                "market_type": market_type,
                "checked_at": current_time.isoformat(),
            }

        return summary

    def should_trade(self, symbol: str) -> Tuple[bool, str]:
        """
        Determinar si se debe ejecutar un trade para un símbolo.
        Considera horario de mercado y ventanas óptimas (evita apertura/cierre y pausas).

        Args:
            symbol: Símbolo del activo

        Returns:
            Tuple (should_trade: bool, reason: str)
        """
        is_open, reason = self.is_market_open(symbol)

        if not is_open:
            return False, f"Trading blocked: {reason}"

        # Aplicar buffers y pausas de mediodía
        # Obtener configuración del símbolo
        market_type = self.get_market_type(symbol)
        market_config = self.symbol_specific_hours.get(symbol, self.market_hours[market_type])
        market_tz = market_config["timezone"]
        current_utc = datetime.now(self.utc)
        local_time = current_utc.astimezone(market_tz)

        # Determinar buffers por símbolo
        buffers = self.symbol_buffers.get(symbol, {})
        open_buffer_min = buffers.get("open_buffer", self.default_open_buffer_min)
        close_buffer_min = buffers.get("close_buffer", self.default_close_buffer_min)

        # Construir ventanas con buffer
        open_dt = datetime.combine(local_time.date(), market_config["open_time"])  # local
        close_dt = datetime.combine(local_time.date(), market_config["close_time"])  # local
        open_dt_buffered = open_dt + timedelta(minutes=open_buffer_min)
        close_dt_buffered = close_dt - timedelta(minutes=close_buffer_min)

        # Pausas de mediodía
        lunch_breaks = self.symbol_lunch_breaks.get(symbol, [])
        current_local_dt = local_time
        current_local_time = current_local_dt.time()

        for start_time, end_time in lunch_breaks:
            if start_time <= current_local_time <= end_time:
                return False, (
                    f"Trading blocked: lunch break {start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')} "
                    f"{market_tz.zone} | {current_local_dt.strftime('%H:%M')} local"
                )

        # Verificar si estamos dentro de la ventana óptima (evitar apertura/cierre)
        if open_dt_buffered <= current_local_dt <= close_dt_buffered:
            return True, (
                f"Trading allowed: buffered window {open_dt_buffered.strftime('%H:%M')}–{close_dt_buffered.strftime('%H:%M')} "
                f"{market_tz.zone} | now {current_local_dt.strftime('%H:%M')} local"
            )
        else:
            # Determinar motivo específico
            if current_local_dt < open_dt_buffered:
                return False, (
                    f"Trading blocked: within open buffer (first {open_buffer_min}m) | "
                    f"opens {market_config['open_time'].strftime('%H:%M')} {market_tz.zone}, optimal from {open_dt_buffered.strftime('%H:%M')}"
                )
            else:
                return False, (
                    f"Trading blocked: within close buffer (last {close_buffer_min}m) | "
                    f"closes {market_config['close_time'].strftime('%H:%M')} {market_tz.zone}, optimal until {close_dt_buffered.strftime('%H:%M')}"
                )

    def get_general_market_status(self) -> Dict[str, list]:
        """
        Obtener un resumen general del estado de los mercados

        Returns:
            Diccionario con mercados abiertos y cerrados
        """
        current_time = datetime.now(self.utc)
        open_markets = []
        closed_markets = []

        # Verificar cada tipo de mercado (sin FOREX en core)
        market_types = ["CRYPTO", "INDICES", "COMMODITIES"]

        for market_type in market_types:
            if market_type == "CRYPTO":
                # Crypto siempre está abierto
                open_markets.append(market_type)
            else:
                # Para INDICES y COMMODITIES, verificar horario de NY (resumen general)
                ny_time = current_time.astimezone(self.ny_tz)
                weekday = ny_time.weekday()
                current_time_only = ny_time.time()

                if weekday < 5 and time(9, 30) <= current_time_only <= time(16, 0):
                    open_markets.append(market_type)
                else:
                    closed_markets.append(market_type)

        return {"open_markets": open_markets, "closed_markets": closed_markets}


# Instancia global para uso en el bot
market_hours_checker = MarketHoursChecker()

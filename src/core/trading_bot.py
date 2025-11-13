"""
🤖 Universal Trading Analyzer - Trading Bot
Bot principal que ejecuta estrategias automáticamente 24/7
"""

import asyncio
import logging
import os
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import json
import queue
from functools import lru_cache
import hashlib
from concurrent.futures import ThreadPoolExecutor
import weakref

# Importar todos nuestros componentes
from src.config.main_config import (
    TradingBotConfig,
    TradingProfiles,
    APIConfig,
    CacheConfig,
    GLOBAL_SYMBOLS,
)
from src.config.time_trading_config import (
    TIMEZONE,
    DAILY_RESET_HOUR,
    DAILY_RESET_MINUTE,
    UTC_TZ,
    is_trading_day_allowed,
    get_weekend_trading_params,
    is_smart_trading_hours_allowed,
    get_smart_trading_status_summary,
)

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
from .enhanced_strategies import TradingSignal
from .professional_adapter import ProfessionalStrategyAdapter
from .mean_reversion_adapter import MeanReversionAdapter
from .breakout_adapter import BreakoutAdapter
from .consensus_adapter import ConsensusAdapter
from .paper_trader import PaperTrader, TradeResult
from .enhanced_risk_manager import EnhancedRiskManager, EnhancedRiskAssessment
from .position_monitor import PositionMonitor

from .capital_client import CapitalClient, create_capital_client_from_env
from src.utils.market_hours import market_hours_checker

# Configurar logging ANTES de la clase
logging.basicConfig(
    level=logging.WARNING,  # Cambiar a WARNING para reducir verbosidad
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar loggers específicos para reducir ruido
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('pydantic').setLevel(logging.ERROR)

# Mantener INFO para componentes críticos del trading bot
logging.getLogger('src.core.trading_bot').setLevel(logging.INFO)
logging.getLogger('src.core.balance_manager').setLevel(logging.INFO)
logging.getLogger('src.core.capital_client').setLevel(logging.INFO)


@dataclass
class BotStatus:
    """
    📊 Estado del trading bot
    """

    is_running: bool
    uptime: str
    total_signals_generated: int
    total_trades_executed: int
    successful_trades: int
    current_portfolio_value: float
    total_pnl: float
    active_strategies: List[str]
    last_analysis_time: datetime
    next_analysis_time: datetime


class TradingBot:
    """
    🤖 Trading Bot Principal con optimizaciones de rendimiento

    Características:
    - Ejecuta múltiples estrategias automáticamente
    - Análisis cada X minutos (configurable)
    - Risk management integrado
    - Paper trading seguro
    - Logging completo
    - Monitoreo a través de Capital.com
    - Cache inteligente para mejor rendimiento
    - Procesamiento paralelo de estrategias
    """

    # Cache compartido entre instancias
    _cache = {}
    _cache_timestamps = {}

    # Cache TTL se obtiene de la configuración del perfil
    @classmethod
    def _get_cache_ttl(cls):
        return CacheConfig.get_ttl_for_operation("price_data")

    def __init__(self, analysis_interval_minutes: int = None):
        """
        Inicializar Trading Bot Profesional

        Args:
            analysis_interval_minutes: Intervalo entre análisis (usa configuración centralizada si no se especifica)
        """
        # Configuración centralizada del bot
        self.config = TradingBotConfig()

        self.analysis_interval = (
            analysis_interval_minutes or self.config.get_analysis_interval()
        )
        self.is_running = False
        self.start_time = None
        self.last_analysis_time = None
        self.next_analysis_time = None  # Tiempo del próximo análisis programado

        # Configurar logger PRIMERO
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Cliente de Capital.com
        self.capital_client = None
        self._initialize_capital_client()

        # Obtener balance real para sincronizar con paper trader
        real_balance = self._get_real_balance()

        # Obtener posiciones existentes de Capital.com para sincronizar
        initial_positions = self._get_capital_positions_for_sync()

        # Componentes principales
        self.paper_trader = PaperTrader(
            initial_balance=real_balance,
            initial_positions=initial_positions,
            capital_client=self.capital_client,
        )
        self.risk_manager = EnhancedRiskManager(capital_client=self.capital_client)

        # Sistema de monitoreo de posiciones
        self.position_monitor = PositionMonitor(
            price_fetcher=self._get_current_price,
            paper_trader=self.paper_trader,
            capital_client=self.capital_client,
        )

        # Sistema de eventos para comunicación con LiveTradingBot
        profile_config = TradingProfiles.get_current_profile()
        self.event_queue = queue.Queue(
            maxsize=profile_config.get("event_queue_maxsize", 1000)
        )
        self.adjustment_thread = None
        self.trade_event_callback = None  # Callback para eventos de trades

        # ThreadPool para procesamiento paralelo
        self.executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="TradingBot"
        )

        # Estrategias disponibles (Enhanced)
        self.strategies = {}
        self._initialize_strategies()

        # Símbolos a analizar - usar configuración centralizada
        self.symbols = GLOBAL_SYMBOLS.copy()

        # Configuración de trading profesional desde configuración centralizada
        self.min_confidence_threshold = self.config.get_min_confidence_threshold()
        self.max_daily_trades = TradingProfiles.get_max_daily_trades()
        self.max_concurrent_positions = self.config.get_max_concurrent_positions()
        self.enable_trading = True  # Activar/desactivar ejecución de trades

        # Configuración de trading real vs paper trading
        self.enable_real_trading = (
            os.getenv("ENABLE_REAL_TRADING", "false").lower() == "true"
        )

        # Previews de órdenes calculadas (para pruebas sin enviar a Capital.com)
        self.order_previews: List[Dict[str, Any]] = []
        self.real_trading_size_multiplier = float(
            os.getenv("REAL_TRADING_SIZE_MULTIPLIER", "0.1")
        )  # 10% del tamaño de paper trading por defecto

        # Configuración de timeframes profesional desde configuración centralizada
        self.primary_timeframe = self.config.get_primary_timeframe()
        self.confirmation_timeframe = self.config.get_confirmation_timeframe()
        self.trend_timeframe = self.config.get_trend_timeframe()

        # Inicializar zona horaria y referencia de último reset
        try:
            tz = ZoneInfo(TIMEZONE) if ZoneInfo else None
        except Exception:
            tz = None
        now_local = datetime.now(tz) if tz else datetime.now()
        reset_dt = (
            datetime(
                now_local.year,
                now_local.month,
                now_local.day,
                DAILY_RESET_HOUR,
                DAILY_RESET_MINUTE,
                tzinfo=tz,
            )
            if tz
            else datetime(
                now_local.year,
                now_local.month,
                now_local.day,
                DAILY_RESET_HOUR,
                DAILY_RESET_MINUTE,
            )
        )
        initial_last_reset_day = (
            now_local.date()
            if now_local >= reset_dt
            else (now_local.date() - timedelta(days=1))
        )

        # Estadísticas
        self.stats = {
            "signals_generated": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "daily_trades": 0,
            "last_reset_day": initial_last_reset_day,
            # Métricas separadas para días laborables vs fines de semana
            "weekday_signals": 0,
            "weekend_signals": 0,
            "weekday_trades": 0,
            "weekend_trades": 0,
            "weekday_successful_trades": 0,
            "weekend_successful_trades": 0,
            "weekday_pnl": 0.0,
            "weekend_pnl": 0.0,
        }

        # Tracking de pérdidas consecutivas para estadísticas
        self.consecutive_losses = 0

        # Sistema de tracking de trades para cooldown
        self.last_trade_times = {}  # {symbol: datetime} - último trade por símbolo
        self.last_signal_types = (
            {}
        )  # {symbol: signal_type} - último tipo de señal por símbolo

        # Estados adicionales para AntiFlip Policy
        self.last_signal_confidences = {}  # {symbol: float} - última confianza
        self.antiflip_opposite_counts = {}  # {(symbol, signal_type): int} persistencia de señales opuestas
        self.last_exit_times = {}  # {symbol: datetime} - último momento de salida/cierre

        # Thread para ejecución
        self.analysis_thread = None
        self.stop_event = threading.Event()

        self.logger.info(
            "🤖 Trading Bot initialized with Position Monitor and Trade Cooldown System"
        )

    def _initialize_capital_client(self):
        """🔌 Inicializar cliente de Capital.com"""
        try:
            self.capital_client = create_capital_client_from_env()
            # Crear sesión automáticamente
            self.capital_client.create_session()
            self.logger.info("✅ Capital.com client initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Capital.com client: {e}")
            self.capital_client = None

    def _get_real_balance(self) -> float:
        """💰 Obtener balance real de Capital.com"""
        try:
            if self.capital_client and hasattr(self.capital_client, "get_accounts"):
                accounts_response = self.capital_client.get_accounts()
                self.logger.debug(f"🔍 Accounts response: {accounts_response}")

                # Manejar la estructura correcta de la respuesta
                if accounts_response and accounts_response.get("success"):
                    accounts_data = accounts_response.get("accounts", {})
                    accounts_list = accounts_data.get("accounts", [])

                    if accounts_list and len(accounts_list) > 0:
                        # Usar el primer account disponible
                        account = accounts_list[0]
                        self.logger.debug(f"🔍 First account structure: {account}")
                        balance_info = account.get("balance", {})
                        self.logger.debug(f"🔍 Balance info: {balance_info}")
                        available_balance = balance_info.get("available", 0.0)
                        balance = float(available_balance)
                        self.logger.info(
                            f"💰 Balance real obtenido de Capital.com: ${balance:.2f}"
                        )
                        return balance
                    else:
                        self.logger.warning(
                            "⚠️ No se encontraron cuentas en la respuesta de Capital.com"
                        )
                        self.logger.debug(f"🔍 Accounts list was: {accounts_list}")
                else:
                    self.logger.warning("⚠️ Respuesta de cuentas no exitosa o vacía")
                    self.logger.debug(f"🔍 Full response was: {accounts_response}")
            else:
                self.logger.warning(
                    "⚠️ Cliente de Capital.com no disponible para obtener balance"
                )
                self.logger.debug(
                    f"🔍 capital_client: {self.capital_client}, has get_accounts: {hasattr(self.capital_client, 'get_accounts') if self.capital_client else 'N/A'}"
                )
        except Exception as e:
            self.logger.error(
                f"❌ Error obteniendo balance real: {type(e).__name__}: {str(e)}"
            )
            import traceback

            self.logger.debug(f"🔍 Traceback completo: {traceback.format_exc()}")

        # Fallback: usar balance por defecto de configuración
        default_balance = 1000.0  # Balance por defecto
        self.logger.info(f"💰 Usando balance por defecto: ${default_balance:.2f}")
        return default_balance

    def _get_capital_positions_for_sync(self) -> Dict:
        """
        🔄 Obtener posiciones de Capital.com para sincronizar con paper trader

        Returns:
            Diccionario con posiciones en formato compatible con paper trader
        """
        try:
            if not self.capital_client:
                self.logger.info("ℹ️ Capital client not available, no positions to sync")
                return {}

            positions_result = self.capital_client.get_positions()
            if not positions_result.get("success"):
                self.logger.warning(
                    f"⚠️ Failed to get positions: {positions_result.get('error')}"
                )
                return {}

            positions_data = {}
            capital_positions = positions_result.get("positions", [])

            for position in capital_positions:
                # Extraer información de la posición
                market_info = position.get("market", {})
                position_info = position.get("position", {})

                symbol = market_info.get("epic", "").replace(
                    "_", ""
                )  # ETHUSD, BTCUSD, etc.
                direction = position_info.get("direction", "").upper()  # BUY o SELL
                size = float(position_info.get("size", 0))
                level = float(position_info.get("level", 0))  # Precio promedio
                currency = position_info.get("currency", "USD")

                # Solo incluir posiciones activas
                if size > 0 and level > 0 and symbol:
                    positions_data[symbol] = {
                        "direction": direction,
                        "size": size,
                        "level": level,
                        "currency": currency,
                    }

                    self.logger.debug(
                        f"🔄 Posición encontrada: {direction} {size} {symbol} @ ${level:.2f}"
                    )

            if positions_data:
                self.logger.info(
                    f"📊 Encontradas {len(positions_data)} posiciones activas en Capital.com para sincronizar"
                )
            else:
                self.logger.info(
                    "ℹ️ No hay posiciones activas en Capital.com para sincronizar"
                )

            return positions_data

        except Exception as e:
            self.logger.error(f"❌ Error getting Capital.com positions for sync: {e}")
            return {}

    def set_trade_event_callback(self, callback):
        """
        🔗 Configurar callback para eventos de trades

        Args:
            callback: Función que será llamada cuando se ejecute un trade
        """
        self.trade_event_callback = callback
        self.logger.info("✅ Trade event callback configured")

    def _emit_trade_event(self, signal, trade_result, risk_assessment):
        """
        📡 Emitir evento de trade ejecutado

        Args:
            signal: Señal de trading que generó el trade
            trade_result: Resultado de la ejecución del trade
            risk_assessment: Evaluación de riesgo del trade
        """
        try:
            if self.trade_event_callback:
                trade_event = {
                    "type": "TRADE_EXECUTED",
                    "timestamp": datetime.now(UTC_TZ),
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "confidence": signal.confidence_score,
                    "entry_price": trade_result.entry_price,
                    "quantity": trade_result.quantity,
                    "trade_value": trade_result.entry_value,
                    "success": trade_result.success,
                    "message": trade_result.message,
                    "risk_score": risk_assessment.overall_risk_score,
                    "risk_level": risk_assessment.risk_level.value,
                    "position_size": risk_assessment.position_sizing.recommended_size,
                    "stop_loss": getattr(trade_result, "stop_loss_price", None),
                    "take_profit": getattr(trade_result, "take_profit_price", None),
                }

                # Llamar al callback
                self.trade_event_callback(trade_event)

                # También agregar al queue para compatibilidad
                if not self.event_queue.full():
                    self.event_queue.put(trade_event)

        except Exception as e:
            self.logger.error(f"❌ Error emitting trade event: {e}")

    def _initialize_strategies(self):
        """🔧 Inicializar estrategias de trading"""
        try:
            # Estrategia de consenso como estrategia principal
            self.strategies = {
                "ConsensusStrategy": ConsensusAdapter(self.capital_client),
            }

            # Estrategias individuales (mantenidas para análisis directo si es necesario)
            self.individual_strategies = {
                "TrendFollowingProfessional": ProfessionalStrategyAdapter(
                    self.capital_client
                ),
                "MeanReversionProfessional": MeanReversionAdapter(self.capital_client),
                "BreakoutProfessional": BreakoutAdapter(self.capital_client),
            }

            # Inyectar referencia del bot en todas las estrategias
            for s in self.strategies.values():
                if hasattr(s, "set_trading_bot"):
                    s.set_trading_bot(self)

            for s in self.individual_strategies.values():
                if hasattr(s, "set_trading_bot"):
                    s.set_trading_bot(self)

            self.logger.info(f"🧠 Consensus strategy initialized as primary strategy")
            self.logger.info(
                f"✅ {len(self.strategies)} primary strategies + {len(self.individual_strategies)} individual strategies initialized"
            )
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategies: {e}")
            self.strategies = {}
            self.individual_strategies = {}

    @classmethod
    def _get_cache_key(cls, method_name: str, *args, **kwargs) -> str:
        """Generar clave de cache única para método y parámetros"""
        try:
            key_data = f"{method_name}_{str(args)}_{str(sorted(kwargs.items()))}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception:
            return f"{method_name}_{time.time()}"

    @classmethod
    def _get_from_cache(cls, cache_key: str):
        """Obtener valor del cache si es válido"""
        current_time = time.time()
        if (
            cache_key in cls._cache
            and cache_key in cls._cache_timestamps
            and current_time - cls._cache_timestamps[cache_key] < cls._get_cache_ttl()
        ):
            return cls._cache[cache_key]
        return None

    @classmethod
    def _store_in_cache(cls, cache_key: str, value):
        """Almacenar valor en cache con timestamp"""
        cls._cache[cache_key] = value
        cls._cache_timestamps[cache_key] = time.time()

        # Limpiar cache viejo si es necesario
        if len(cls._cache) > 500:  # Límite de entradas
            cls._cleanup_cache()

    @classmethod
    def _cleanup_cache(cls):
        """Limpiar entradas viejas del cache"""
        current_time = time.time()
        expired_keys = [
            key
            for key, timestamp in cls._cache_timestamps.items()
            if current_time - timestamp >= cls._get_cache_ttl()
        ]
        for key in expired_keys:
            cls._cache.pop(key, None)
            cls._cache_timestamps.pop(key, None)

    def start(self):
        """
        🚀 Iniciar el trading bot
        """
        if self.is_running:
            self.logger.warning("⚠️ Bot is already running")
            return

        self.is_running = True
        self.start_time = datetime.now(UTC_TZ)
        self.stop_event.clear()

        # Inicializar próximo análisis
        self.next_analysis_time = datetime.now(UTC_TZ) + timedelta(
            minutes=self.analysis_interval
        )

        # Configurar schedule para análisis periódico
        schedule.clear()
        schedule.every(self.analysis_interval).minutes.do(self._run_analysis_cycle)

        # Programar reset diario exacto a la hora configurada en UTC
        try:
            # Convertir UTC a hora local del sistema para schedule
            try:
                import pytz
                
                # Crear un datetime UTC para hoy a la hora del reset
                utc_time = datetime.now(UTC_TZ).replace(
                    hour=DAILY_RESET_HOUR, 
                    minute=DAILY_RESET_MINUTE, 
                    second=0, 
                    microsecond=0
                )
                
                # Obtener la zona horaria local del sistema (Chile)
                local_tz = pytz.timezone('America/Santiago')
                local_time = utc_time.astimezone(local_tz)
                
                # Formatear las horas para logging y scheduling
                local_time_str = f"{local_time.hour:02d}:{local_time.minute:02d}"
                utc_time_str = f"{DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d}"

                # Programar el reset usando la hora local
                schedule.every().day.at(local_time_str).do(
                    self._reset_daily_stats_if_needed
                ).tag("daily_reset")
                
                self.logger.info(
                    f"⏰ Daily reset scheduled at {utc_time_str} UTC ({local_time_str} local Chile time)"
                )
                
            except ImportError:
                # Fallback si pytz no está disponible
                reset_time_str = f"{DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d}"
                schedule.every().day.at(reset_time_str).do(
                    self._reset_daily_stats_if_needed
                ).tag("daily_reset")
                
                self.logger.warning(
                    f"⚠️ pytz not available, using system timezone. Daily reset scheduled at {reset_time_str}"
                )
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not schedule daily reset: {e}")

        # Programar cierre automático de posiciones rentables 15 minutos antes del reset
        try:
            self.schedule_pre_reset_profit_taking()
        except Exception as e:
            self.logger.warning(f"⚠️ Could not schedule pre-reset profit taking: {e}")

        # Iniciar thread de ejecución (sin análisis inicial inmediato)
        self.analysis_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.analysis_thread.start()

        # Iniciar monitoreo de posiciones solo si está habilitado en configuración
        if self.config.get_position_monitoring_enabled():
            self.position_monitor.start_monitoring()
            self.logger.info("🔍 Position monitoring started")
        else:
            self.logger.info(
                "🔍 Position monitoring disabled - Bot will only open positions with TP/SL"
            )

        # Sistema de ajuste TP/SL desactivado (Opción A): no se inicia monitoreo

        # Ejecutar primer análisis inmediatamente (sin delay)
        self.logger.info("🔄 Running immediate initial analysis...")
        try:
            self._run_analysis_cycle()
            self.logger.info("✅ Initial analysis completed successfully")
        except Exception as e:
            self.logger.error(f"❌ Error in initial analysis: {e}")

        self.logger.info(
            f"🚀 Trading Bot started - Analysis every {self.analysis_interval} minutes"
        )
        self.logger.info(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
        self.logger.info(f"🧠 Active strategies: {', '.join(self.strategies.keys())}")
        if self.config.get_position_monitoring_enabled():
            self.logger.info("🔍 Position monitoring started")
        else:
            self.logger.info(
                "🔍 Position monitoring disabled - Bot will only open positions with TP/SL"
            )
        self.logger.info("🎯 TP/SL adjustment monitoring disabled")

    def stop(self):
        """
        🛑 Detener el trading bot y limpiar recursos
        """
        if not self.is_running:
            self.logger.warning("⚠️ Bot is not running")
            return

        self.is_running = False
        self.stop_event.set()
        schedule.clear()

        # Resetear tiempo del próximo análisis
        self.next_analysis_time = None

        # Detener monitoreo de posiciones solo si está habilitado
        if self.config.get_position_monitoring_enabled():
            self.position_monitor.stop_monitoring()
            self.logger.info("🔍 Position monitoring stopped")
        else:
            self.logger.info("🔍 Position monitoring was disabled")

        # Limpiar ThreadPoolExecutor
        if hasattr(self, "executor") and self.executor:
            profile_config = TradingProfiles.get_current_profile()
            timeout = self.config.get_executor_shutdown_timeout()
            self.executor.shutdown(wait=True, timeout=timeout)
            self.logger.info("🧹 ThreadPoolExecutor cleaned up")

        if self.analysis_thread and self.analysis_thread.is_alive():
            profile_config = TradingProfiles.get_current_profile()
            timeout = self.config.get_thread_join_timeout()
            self.analysis_thread.join(timeout=timeout)

        if self.adjustment_thread and self.adjustment_thread.is_alive():
            profile_config = TradingProfiles.get_current_profile()
            timeout = self.config.get_thread_join_timeout()
            self.adjustment_thread.join(timeout=timeout)

        # Limpiar cache si es necesario
        self._cleanup_cache()

        self.logger.info("🛑 Trading Bot stopped")
        if self.config.get_position_monitoring_enabled():
            self.logger.info("🔍 Position monitoring stopped")
        else:
            self.logger.info("🔍 Position monitoring was disabled")
        self.logger.info("🎯 TP/SL adjustment monitoring disabled")
        self.logger.info("💾 Cache cleaned up")

    def _get_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual del símbolo usando Capital.com con cache"""
        import math

        # Validar que el símbolo no esté vacío
        if not symbol or not symbol.strip():
            self.logger.error(
                f"🚨 CRÍTICO: Símbolo vacío o inválido proporcionado a _get_current_price: '{symbol}'"
            )
            return 0.0

        def _validate_price(price: float, source: str) -> bool:
            """Validar que el precio sea válido y seguro para trading"""
            if price is None:
                self.logger.warning(f"⚠️ Precio None recibido de {source} para {symbol}")
                return False
            if math.isnan(price):
                self.logger.error(
                    f"🚨 Precio NaN recibido de {source} para {symbol} - CRÍTICO"
                )
                return False
            if math.isinf(price):
                self.logger.error(
                    f"🚨 Precio Infinity recibido de {source} para {symbol} - CRÍTICO"
                )
                return False
            if price <= 0:
                self.logger.warning(
                    f"⚠️ Precio inválido ({price}) de {source} para {symbol}"
                )
                return False
            return True

        try:
            # Normalizar símbolo para Capital.com (Gold, Silver, etc.)
            capital_symbol = self._normalize_symbol_for_capital(symbol)

            # Generar clave de cache para precio basada en símbolo normalizado
            cache_key = self._get_cache_key("current_price", capital_symbol)

            # Verificar cache (TTL más corto para precios)
            cached_price = self._get_from_cache(cache_key)
            if cached_price is not None and _validate_price(cached_price, "cache"):
                return cached_price

            # Usar Capital.com client si está disponible
            if self.capital_client:
                try:
                    market_data = self.capital_client.get_market_data([capital_symbol])
                    if market_data and capital_symbol in market_data:
                        # Intentar obtener bid, offer o mid price
                        price_data = market_data[capital_symbol]
                        current_price = None

                        # Prioridad: bid > offer > mid
                        for price_key in ["bid", "offer", "mid"]:
                            if (
                                price_key in price_data
                                and price_data[price_key] is not None
                            ):
                                try:
                                    current_price = float(price_data[price_key])
                                    if _validate_price(
                                        current_price, f"Capital.com-{price_key}"
                                    ):
                                        # Almacenar en cache solo precios válidos
                                        self._store_in_cache(cache_key, current_price)
                                        return current_price
                                except (ValueError, TypeError) as e:
                                    self.logger.warning(
                                        f"⚠️ Error convirtiendo precio {price_key}: {e}"
                                    )
                                    continue

                        self.logger.warning(
                            f"⚠️ Capital.com no retornó precios válidos para {capital_symbol}"
                        )

                except Exception as e:
                    self.logger.error(
                        f"🚨 Capital.com connection failed for {capital_symbol}: {e}"
                    )

            # Fallback: intentar obtener desde estrategias
            try:
                if self.strategies:
                    strategy = next(iter(self.strategies.values()))
                    df = strategy.get_market_data(symbol, "1m", limit=1)
                    if not df.empty:
                        fallback_price = float(df["close"].iloc[-1])
                        if _validate_price(fallback_price, "strategy-fallback"):
                            # Cache del fallback también
                            cache_key = self._get_cache_key("current_price", symbol)
                            self._store_in_cache(cache_key, fallback_price)
                            return fallback_price

                    self.logger.warning(
                        f"⚠️ Strategy fallback no retornó datos válidos para {symbol}"
                    )
            except Exception as e:
                self.logger.error(f"🚨 Strategy fallback failed for {symbol}: {e}")

            # CRÍTICO: No retornar 0.0 - lanzar excepción para evitar trades peligrosos
            error_msg = f"🚨 CRÍTICO: No se pudo obtener precio válido para {symbol} de ninguna fuente"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            error_msg = (
                f"🚨 CRÍTICO: Error inesperado obteniendo precio para {symbol}: {e}"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _normalize_symbol_for_capital(self, symbol: str) -> str:
        """🔄 Normalizar símbolo para Capital.com (ya están en formato correcto)"""
        return symbol

    def _get_capital_symbols(self) -> List[str]:
        """📋 Obtener lista de símbolos disponibles en Capital.com desde configuración centralizada"""
        return GLOBAL_SYMBOLS.copy()

    def _get_tp_max_percent(self, symbol: str) -> Optional[float]:
        """
        🎯 Retorna el máximo porcentaje permitido para Take Profit por grupo de instrumentos.
        - Índices: 0.4%
        - FX mayores: 0.28%
        - Otros: None (sin clamp)
        """
        try:
            s = (symbol or "").upper()
            indices = {"US500", "US30", "US100", "DE40", "UK100", "J225", "HK50"}
            fx_majors = {
                "EURUSD", "GBPUSD", "USDJPY", "EURJPY", "EURCHF",
                "USDCAD", "AUDUSD", "NZDUSD", "GBPJPY"
            }
            if s in indices:
                return 0.004  # 0.4%
            if s in fx_majors:
                return 0.0028  # 0.28%
        except Exception:
            pass
        return None

    def _get_sl_max_percent(self, symbol: str) -> Optional[float]:
        """
        🛡️ Retorna el máximo porcentaje permitido para Stop Loss por grupo de instrumentos.
        - FX mayores: 0.50%
        - Otros: None (sin clamp)
        """
        try:
            s = (symbol or "").upper()
            fx_majors = {
                "EURUSD", "GBPUSD", "USDJPY", "EURJPY", "EURCHF",
                "USDCAD", "AUDUSD", "NZDUSD", "GBPJPY"
            }
            if s in fx_majors:
                return 0.005  # 0.50%
        except Exception:
            pass
        return None

    def _build_order_preview(self, signal: "TradingSignal", risk_assessment: "EnhancedRiskAssessment") -> Dict[str, Any]:
        """
        🧪 Construir un preview de la orden con SL ajustado por spread y reglas del instrumento.

        No envía trades reales. Útil para validar en pruebas que el SL respeta:
        - Precio lado (bid/offer)
        - Spread del instrumento
        - Dealing rules: minStopOrProfitDistance y minStepDistance
        """
        preview: Dict[str, Any] = {
            "symbol": getattr(signal, "symbol", "UNKNOWN"),
            "side": getattr(signal, "signal_type", "UNKNOWN"),
            "entry_price": getattr(signal, "price", None) or getattr(signal, "current_price", None),
            "bid": None,
            "offer": None,
            "spread": None,
            "dealing_rules": {},
            "sl_base": None,
            "sl_after_spread": None,
            "sl_final": None,
            "stop_distance_points_preview": None,
            "tp_base": None,
            "tp_final": None,
        }

        try:
            capital_symbol = self._normalize_symbol_for_capital(signal.symbol)
            current_price = self._get_current_price(signal.symbol)

            # Precios lado y spread
            bid = None
            offer = None
            spread = None
            if self.capital_client:
                md = self.capital_client.get_market_data([capital_symbol])
                if md and capital_symbol in md:
                    bid = md[capital_symbol].get("bid")
                    offer = md[capital_symbol].get("offer")
                    if bid is not None and offer is not None and offer > bid:
                        spread = offer - bid
            preview["bid"] = bid
            preview["offer"] = offer
            preview["spread"] = spread

            # Dealing rules
            dr = self.capital_client.get_dealing_rules(capital_symbol) if self.capital_client else {"success": False}
            if dr.get("success"):
                preview["dealing_rules"] = {
                    "minStopOrProfitDistance": dr.get("min_stop_distance", {}),
                    "minStepDistance": dr.get("min_step_distance", {}),
                    "trailingStopsPreference": dr.get("trailing_stops_preference", None),
                }

            # Base SL: ROI-based si perfil aplica; si no, usar de signal o risk manager
            sl_price = None
            take_profit = None
            risk_reward = None
            try:
                current_profile_config = TradingProfiles.get_current_profile()
                current_profile = current_profile_config.get("name", "")
                # Usar ROI-based para perfiles que lo soportan
                if current_profile in ["Scalping", "Intraday"]:
                    from .trend_following_professional import TrendFollowingProfessional
                    strategy_instance = TrendFollowingProfessional()
                    atr = current_price * 0.02  # estimación de ATR
                    # Usar tamaño recomendado del risk manager como base
                    size_units = getattr(risk_assessment.position_sizing, "recommended_size", 0.0) or 0.0
                    position_size_usd = size_units * current_price
                    sl_price, take_profit, risk_reward = strategy_instance.calculate_roi_based_risk_reward(
                        current_price, signal.signal_type, position_size_usd, atr
                    )
                # Fallbacks
                if sl_price is None and hasattr(signal, "stop_loss_price") and signal.stop_loss_price:
                    sl_price = signal.stop_loss_price
                if sl_price is None and hasattr(risk_assessment, "dynamic_stop_loss"):
                    sl_price = risk_assessment.dynamic_stop_loss.stop_loss_price
            except Exception:
                pass

            preview["sl_base"] = sl_price
            preview["tp_base"] = take_profit

            # Aplicar los mismos ajustes de preferencia TP/SL que en ejecución real
            try:
                adjustments_info = {
                    "tp_multiplier": None,
                    "sl_multiplier": None,
                    "risk_usd_estimate": None,
                    "adjustments_applied": False,
                }

                # Tamaño recomendado en unidades (para estimar riesgoUSD)
                size_units = getattr(risk_assessment.position_sizing, "recommended_size", 0.0) or 0.0

                # Precio de referencia sensible al lado
                ref_price_adj = None
                try:
                    ref_price_adj = (
                        bid if signal.signal_type == "BUY" and bid is not None
                        else offer if signal.signal_type == "SELL" and offer is not None
                        else current_price
                    )
                except Exception:
                    ref_price_adj = current_price

                if sl_price is not None and take_profit is not None and ref_price_adj is not None:
                    # Distancias actuales
                    if signal.signal_type == "BUY":
                        tp_dist = max(take_profit - ref_price_adj, 0.0)
                        sl_dist = max(ref_price_adj - sl_price, 0.0)
                    else:
                        tp_dist = max(ref_price_adj - take_profit, 0.0)
                        sl_dist = max(sl_price - ref_price_adj, 0.0)

                    # Estimar riesgo en USD: asume CFD, riesgo ≈ distancia * size_units
                    risk_usd_estimate = sl_dist * size_units
                    adjustments_info["risk_usd_estimate"] = risk_usd_estimate

                    # Aplicar reducción TP 50%
                    new_tp_dist = tp_dist * 0.5
                    adjustments_info["tp_multiplier"] = 0.5

                    # SL: +50% solo si riesgoUSD en [10, 20] y símbolo != US30
                    symbol_upper = (getattr(signal, "symbol", "") or "").upper()
                    keep_sl_unchanged = symbol_upper == "US30"
                    increase_sl = (not keep_sl_unchanged) and (10.0 <= risk_usd_estimate <= 20.0)
                    new_sl_dist = sl_dist * (1.5 if increase_sl else 1.0)
                    adjustments_info["sl_multiplier"] = 1.5 if increase_sl else 1.0

                    # Reconstruir niveles manteniendo orientación
                    if signal.signal_type == "BUY":
                        take_profit = ref_price_adj + new_tp_dist
                        sl_price = ref_price_adj - new_sl_dist
                    else:
                        take_profit = ref_price_adj - new_tp_dist
                        sl_price = ref_price_adj + new_sl_dist

                    adjustments_info["adjustments_applied"] = True

                # Actualizar bases en preview tras ajustes
                preview["sl_base"] = sl_price
                preview["tp_base"] = take_profit
                preview["adjustments"] = adjustments_info
            except Exception:
                # Si algo falla, continuar sin bloquear el preview
                pass

            # Ajuste por spread según lado
            sl_after_spread = sl_price
            try:
                if spread is not None and sl_price is not None:
                    if signal.signal_type == "BUY":
                        sl_after_spread = sl_price - spread
                    elif signal.signal_type == "SELL":
                        sl_after_spread = sl_price + spread
            except Exception:
                pass
            preview["sl_after_spread"] = sl_after_spread

            # Aplicar mínimos y pasos
            sl_final = sl_after_spread
            try:
                import math
                ref_price = (
                    bid if signal.signal_type == "BUY" and bid is not None
                    else offer if signal.signal_type == "SELL" and offer is not None
                    else current_price
                )
                min_stop = preview["dealing_rules"].get("minStopOrProfitDistance", {}) if preview["dealing_rules"] else {}
                step = preview["dealing_rules"].get("minStepDistance", {}) if preview["dealing_rules"] else {}

                unit = (min_stop.get("unit") or "").upper()
                value = float(min_stop.get("value") or 0.0)
                min_points = 0.0
                if unit == "PERCENTAGE":
                    min_points = ref_price * value
                elif unit == "POINTS":
                    min_points = value

                if sl_final is not None and ref_price is not None and min_points > 0:
                    if signal.signal_type == "BUY":
                        dist = ref_price - sl_final
                        if dist < min_points:
                            sl_final = ref_price - min_points
                    else:
                        dist = sl_final - ref_price
                        if dist < min_points:
                            sl_final = ref_price + min_points

                # Redondeo al paso mínimo
                step_unit = (step.get("unit") or "").upper()
                step_value = float(step.get("value") or 0.0)
                if step_unit == "POINTS" and step_value > 0 and sl_final is not None and ref_price is not None:
                    if signal.signal_type == "BUY":
                        dist = ref_price - sl_final
                        dist = math.ceil(dist / step_value) * step_value
                        sl_final = ref_price - dist
                    else:
                        dist = sl_final - ref_price
                        dist = math.ceil(dist / step_value) * step_value
                        sl_final = ref_price + dist

                # Clamp SL por instrumento (FX mayores)
                try:
                    max_sl_pct = self._get_sl_max_percent(getattr(signal, "symbol", ""))
                    if max_sl_pct is not None and sl_final is not None and ref_price is not None:
                        max_dist_sl = ref_price * max_sl_pct
                        if signal.signal_type == "BUY":
                            dist_sl = ref_price - sl_final
                            if dist_sl > max_dist_sl:
                                sl_final = ref_price - max_dist_sl
                        else:
                            dist_sl = sl_final - ref_price
                            if dist_sl > max_dist_sl:
                                sl_final = ref_price + max_dist_sl
                        # Reaplicar redondeo al paso si corresponde
                        if step_unit == "POINTS" and step_value > 0:
                            if signal.signal_type == "BUY":
                                dist_sl = ref_price - sl_final
                                dist_sl = math.ceil(dist_sl / step_value) * step_value
                                sl_final = ref_price - dist_sl
                            else:
                                dist_sl = sl_final - ref_price
                                dist_sl = math.ceil(dist_sl / step_value) * step_value
                                sl_final = ref_price + dist_sl
                except Exception:
                    pass

                # Distancia de stop en puntos como preview (útil para TSL)
                if sl_final is not None and ref_price is not None:
                    if signal.signal_type == "BUY":
                        preview["stop_distance_points_preview"] = max(0.0, ref_price - sl_final)
                    else:
                        preview["stop_distance_points_preview"] = max(0.0, sl_final - ref_price)

                # TP enforcement y redondeo
                tp_final = None
                if take_profit is not None and ref_price is not None:
                    tp_base = take_profit
                    # Orientación
                    if signal.signal_type == "BUY" and tp_base <= ref_price:
                        tp_base = ref_price + max(min_points, step_value)
                    elif signal.signal_type == "SELL" and tp_base >= ref_price:
                        tp_base = ref_price - max(min_points, step_value)

                    # Enforce mínimo
                    if signal.signal_type == "BUY":
                        dist_tp = tp_base - ref_price
                        if dist_tp < min_points:
                            tp_base = ref_price + min_points
                    else:
                        dist_tp = ref_price - tp_base
                        if dist_tp < min_points:
                            tp_base = ref_price - min_points

                    # Redondeo por pasos
                    if step_unit == "POINTS" and step_value > 0:
                        if signal.signal_type == "BUY":
                            dist_tp = tp_base - ref_price
                            dist_tp = math.ceil(dist_tp / step_value) * step_value
                            tp_final = ref_price + dist_tp
                        else:
                            dist_tp = ref_price - tp_base
                            dist_tp = math.ceil(dist_tp / step_value) * step_value
                            tp_final = ref_price - dist_tp
                    else:
                        tp_final = tp_base

                    # Clamp por instrumento (índices / FX)
                    try:
                        max_pct = self._get_tp_max_percent(getattr(signal, "symbol", ""))
                        if max_pct is not None and tp_final is not None:
                            max_dist = ref_price * max_pct
                            if signal.signal_type == "BUY":
                                dist = tp_final - ref_price
                                if dist > max_dist:
                                    tp_final = ref_price + max_dist
                            else:
                                dist = ref_price - tp_final
                                if dist > max_dist:
                                    tp_final = ref_price - max_dist
                            # Reaplicar redondeo al paso si corresponde
                            if step_unit == "POINTS" and step_value > 0:
                                import math
                                if signal.signal_type == "BUY":
                                    dist = tp_final - ref_price
                                    dist = math.ceil(dist / step_value) * step_value
                                    tp_final = ref_price + dist
                                else:
                                    dist = ref_price - tp_final
                                    dist = math.ceil(dist / step_value) * step_value
                                    tp_final = ref_price - dist
                    except Exception:
                        pass
                preview["tp_final"] = tp_final
            except Exception:
                pass

            preview["sl_final"] = sl_final
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo construir order_preview: {e}")

        return preview

    def _apply_dealing_rules_to_tp_sl(self, signal_type: str, bid: float, offer: float, sl_price: float, tp_price: float, dealing_rules: dict) -> tuple:
        """
        Aplicar reglas del instrumento y orientación por spread a SL/TP.
        Retorna (sl_final, tp_final, stop_distance_points).
        """
        try:
            import math
            ref_price = offer if signal_type == "BUY" else bid
            min_stop = dealing_rules.get("min_stop_distance", {}) if dealing_rules else {}
            step = dealing_rules.get("min_step_distance", {}) if dealing_rules else {}

            unit = (min_stop.get("unit") or "").upper()
            value = float(min_stop.get("value") or 0.0)
            min_points = 0.0
            if unit == "PERCENTAGE" and ref_price:
                min_points = ref_price * value
            elif unit == "POINTS":
                min_points = value

            step_unit = (step.get("unit") or "").upper()
            step_value = float(step.get("value") or 0.0)

            # SL
            sl_base = sl_price
            if sl_base is not None and ref_price is not None:
                if signal_type == "BUY" and sl_base >= ref_price:
                    sl_base = ref_price - max(min_points, step_value)
                elif signal_type == "SELL" and sl_base <= ref_price:
                    sl_base = ref_price + max(min_points, step_value)

                if signal_type == "BUY":
                    dist = ref_price - sl_base
                    if dist < min_points:
                        sl_base = ref_price - min_points
                else:
                    dist = sl_base - ref_price
                    if dist < min_points:
                        sl_base = ref_price + min_points

                if step_unit == "POINTS" and step_value > 0:
                    if signal_type == "BUY":
                        dist = ref_price - sl_base
                        dist = math.ceil(dist / step_value) * step_value
                        sl_final = ref_price - dist
                    else:
                        dist = sl_base - ref_price
                        dist = math.ceil(dist / step_value) * step_value
                        sl_final = ref_price + dist
                else:
                    sl_final = sl_base
            else:
                sl_final = sl_price

            # Clamp SL por instrumento (FX mayores) basado en ref_price
            try:
                symbol = getattr(self, "current_signal_symbol", None)
                max_sl_pct = self._get_sl_max_percent(symbol) if symbol else None
                if max_sl_pct is not None and sl_final is not None and ref_price is not None:
                    max_dist_sl = ref_price * max_sl_pct
                    if signal_type == "BUY":
                        dist_sl = ref_price - sl_final
                        if dist_sl > max_dist_sl:
                            sl_final = ref_price - max_dist_sl
                    else:
                        dist_sl = sl_final - ref_price
                        if dist_sl > max_dist_sl:
                            sl_final = ref_price + max_dist_sl
                    # Reaplicar redondeo al paso si corresponde
                    if step_unit == "POINTS" and step_value > 0:
                        import math
                        if signal_type == "BUY":
                            dist_sl = ref_price - sl_final
                            dist_sl = math.ceil(dist_sl / step_value) * step_value
                            sl_final = ref_price - dist_sl
                        else:
                            dist_sl = sl_final - ref_price
                            dist_sl = math.ceil(dist_sl / step_value) * step_value
                            sl_final = ref_price + dist_sl
            except Exception:
                pass

            # TP
            tp_final = tp_price
            if tp_price is not None and ref_price is not None:
                tp_base = tp_price
                if signal_type == "BUY" and tp_base <= ref_price:
                    tp_base = ref_price + max(min_points, step_value)
                elif signal_type == "SELL" and tp_base >= ref_price:
                    tp_base = ref_price - max(min_points, step_value)

                if signal_type == "BUY":
                    dist_tp = tp_base - ref_price
                    if dist_tp < min_points:
                        tp_base = ref_price + min_points
                else:
                    dist_tp = ref_price - tp_base
                    if dist_tp < min_points:
                        tp_base = ref_price - min_points

                if step_unit == "POINTS" and step_value > 0:
                    if signal_type == "BUY":
                        dist_tp = tp_base - ref_price
                        dist_tp = math.ceil(dist_tp / step_value) * step_value
                        tp_final = ref_price + dist_tp
                    else:
                        dist_tp = ref_price - tp_base
                        dist_tp = math.ceil(dist_tp / step_value) * step_value
                        tp_final = ref_price - dist_tp
                else:
                    tp_final = tp_base

                # Clamp por instrumento (índices / FX) basado en ref_price
                try:
                    # No tenemos símbolo aquí; se aplicará en contexto de ejecución
                    # Usaremos una heurística: si existe atributo 'current_signal_symbol' en self
                    symbol = getattr(self, "current_signal_symbol", None)
                    max_pct = self._get_tp_max_percent(symbol) if symbol else None
                    if max_pct is not None and tp_final is not None:
                        max_dist = ref_price * max_pct
                        if signal_type == "BUY":
                            dist = tp_final - ref_price
                            if dist > max_dist:
                                tp_final = ref_price + max_dist
                        else:
                            dist = ref_price - tp_final
                            if dist > max_dist:
                                tp_final = ref_price - max_dist
                        # Reaplicar redondeo al paso si corresponde
                        if step_unit == "POINTS" and step_value > 0:
                            import math
                            if signal_type == "BUY":
                                dist = tp_final - ref_price
                                dist = math.ceil(dist / step_value) * step_value
                                tp_final = ref_price + dist
                            else:
                                dist = ref_price - tp_final
                                dist = math.ceil(dist / step_value) * step_value
                                tp_final = ref_price - dist
                except Exception:
                    pass

            stop_distance_points = None
            if sl_final is not None and ref_price is not None:
                stop_distance_points = (
                    ref_price - sl_final if signal_type == "BUY" else sl_final - ref_price
                )
                stop_distance_points = max(0.0, stop_distance_points)

            return sl_final, tp_final, stop_distance_points
        except Exception:
            return sl_price, tp_price, None

    def _check_max_positions_limit(self) -> bool:
        """
        🛡️ Verificar si se puede abrir una nueva posición según el límite max_positions

        Returns:
            bool: True si se puede abrir nueva posición, False si se alcanzó el límite
        """
        try:
            # Obtener configuración actual
            current_profile = TradingProfiles.get_current_profile()
            max_positions = current_profile.get(
                "max_positions", 8
            )  # Default 8 si no está configurado

            # Contar posiciones abiertas usando Capital.com
            if self.capital_client and self.enable_real_trading:
                # Usar endpoint /positions de Capital.com para trading real
                positions_result = self.capital_client.get_positions()

                if positions_result.get("success"):
                    open_positions = positions_result.get("positions", [])
                    current_positions_count = len(open_positions)

                    self.logger.info(
                        f"📊 Posiciones abiertas: {current_positions_count}/{max_positions}"
                    )

                    # Log detalle de posiciones si hay alguna
                    if open_positions:
                        self.logger.info("📋 Posiciones actuales:")
                        for pos in open_positions[
                            :5
                        ]:  # Mostrar máximo 5 para no saturar logs
                            # Usar 'epic' como símbolo principal, con fallback a instrumentName
                            symbol = pos.get("market", {}).get(
                                "epic",
                                pos.get("market", {}).get("instrumentName", "Unknown"),
                            )
                            size = pos.get("position", {}).get("size", 0)
                            direction = pos.get("position", {}).get(
                                "direction", "Unknown"
                            )
                            pnl = pos.get("position", {}).get("upl", 0)
                            self.logger.info(
                                f"   • {symbol}: {direction} {size} (PnL: ${pnl:.2f})"
                            )

                        if len(open_positions) > 5:
                            self.logger.info(
                                f"   ... y {len(open_positions) - 5} posiciones más"
                            )

                    return current_positions_count < max_positions
                else:
                    self.logger.warning(
                        f"⚠️ No se pudo obtener posiciones de Capital.com: {positions_result.get('error')}"
                    )
                    # En caso de error, permitir trading (fail-safe)
                    return True
            else:
                # Para paper trading, usar el paper trader
                paper_positions = self.paper_trader.get_open_positions()
                current_positions_count = len(paper_positions)

                self.logger.info(
                    f"📊 Posiciones paper: {current_positions_count}/{max_positions}"
                )

                # Log detalle de posiciones paper si hay alguna
                if paper_positions:
                    self.logger.info("📋 Posiciones paper actuales:")
                    for pos in paper_positions[:5]:  # Mostrar máximo 5
                        symbol = pos.get("symbol", "Unknown")
                        quantity = pos.get("quantity", 0)
                        pnl_pct = pos.get("unrealized_pnl_percentage", 0)
                        self.logger.info(
                            f"   • {symbol}: {quantity:.4f} (PnL: {pnl_pct:+.2f}%)"
                        )

                    if len(paper_positions) > 5:
                        self.logger.info(
                            f"   ... y {len(paper_positions) - 5} posiciones más"
                        )

                return current_positions_count < max_positions

        except Exception as e:
            self.logger.error(f"❌ Error verificando límite de posiciones: {e}")
            # En caso de error, permitir trading (fail-safe)
            return True

    def _check_trade_cooldown(self, signal: "TradingSignal") -> bool:
        """
        🕐 Verificar si una señal debe ser filtrada por cooldown

        Args:
            signal: Señal de trading a verificar

        Returns:
            bool: True si la señal pasa el filtro de cooldown, False si debe ser filtrada
        """
        try:
            # Obtener configuración de cooldown del perfil actual
            current_profile = TradingProfiles.get_current_profile()
            min_time_between_trades = current_profile.get(
                "min_time_between_trades_minutes", 0
            )
            min_time_between_opposite_signals = current_profile.get(
                "min_time_between_opposite_signals_minutes", 0
            )

            symbol = signal.symbol
            signal_type = signal.signal_type
            current_time = datetime.now(UTC_TZ)

            # Verificar si hay un trade previo para este símbolo
            if symbol in self.last_trade_times:
                last_trade_time = self.last_trade_times[symbol]
                last_signal_type = self.last_signal_types.get(symbol)

                # Calcular tiempo transcurrido desde el último trade
                time_diff = current_time - last_trade_time
                time_diff_minutes = time_diff.total_seconds() / 60

                # Verificar cooldown general entre trades del mismo símbolo
                if time_diff_minutes < min_time_between_trades:
                    remaining_time = min_time_between_trades - time_diff_minutes
                    self.logger.info(
                        f"🕐 COOLDOWN: Señal {signal_type} para {symbol} filtrada. "
                        f"Tiempo desde último trade: {time_diff_minutes:.1f}min, "
                        f"mínimo requerido: {min_time_between_trades}min, "
                        f"tiempo restante: {remaining_time:.1f}min"
                    )
                    return False

                # Verificar cooldown específico para señales opuestas
                if last_signal_type and last_signal_type != signal_type:
                    if time_diff_minutes < min_time_between_opposite_signals:
                        remaining_time = (
                            min_time_between_opposite_signals - time_diff_minutes
                        )
                        self.logger.info(
                            f"🚫 COOLDOWN OPUESTO: Señal {signal_type} para {symbol} filtrada. "
                            f"Última señal: {last_signal_type}, tiempo transcurrido: {time_diff_minutes:.1f}min, "
                            f"mínimo requerido para señales opuestas: {min_time_between_opposite_signals}min, "
                            f"tiempo restante: {remaining_time:.1f}min"
                        )
                        return False

            # La señal pasa todos los filtros de cooldown
            return True

        except Exception as e:
            self.logger.error(
                f"❌ Error verificando cooldown para {signal.symbol}: {e}"
            )
            # En caso de error, permitir la señal (fail-safe)
            return True

    def _update_trade_tracking(self, signal: "TradingSignal"):
        """
        📝 Actualizar el tracking de trades después de ejecutar una operación

        Args:
            signal: Señal de trading ejecutada
        """
        try:
            current_time = datetime.now(UTC_TZ)
            symbol = signal.symbol
            signal_type = signal.signal_type

            # Actualizar tracking
            self.last_trade_times[symbol] = current_time
            self.last_signal_types[symbol] = signal_type
            # Guardar confianza de la última señal
            try:
                self.last_signal_confidences[symbol] = float(signal.confidence_score)
            except Exception:
                self.last_signal_confidences[symbol] = None

            # Reiniciar contadores de persistencia opuesta para el símbolo
            self.antiflip_opposite_counts[(symbol, "BUY")] = 0
            self.antiflip_opposite_counts[(symbol, "SELL")] = 0

            self.logger.debug(
                f"📝 Trade tracking actualizado: {symbol} -> {signal_type} a las {current_time.strftime('%H:%M:%S')}"
            )

        except Exception as e:
            self.logger.error(
                f"❌ Error actualizando trade tracking para {signal.symbol}: {e}"
            )

    def _get_open_position_direction(self, symbol: str) -> Optional[str]:
        """🔎 Obtener dirección de posición abierta para un símbolo usando paper trader.

        Returns: "LONG", "SHORT" o None si no hay posición.
        """
        try:
            positions = self.paper_trader.get_open_positions()
            for pos in positions:
                if pos.get("symbol") == symbol:
                    qty = pos.get("quantity", 0)
                    if qty > 0:
                        return "LONG"
                    elif qty < 0:
                        return "SHORT"
                    else:
                        return None
            return None
        except Exception:
            return None

    def _update_antiflip_persistence(self, signal: "TradingSignal"):
        """🔄 Actualizar contador de persistencia de señales opuestas.

        Si la señal es opuesta a la última señal para el símbolo, incrementa contador.
        Si es del mismo lado, reinicia el contador del lado opuesto.
        """
        try:
            symbol = signal.symbol
            signal_type = signal.signal_type
            last_type = self.last_signal_types.get(symbol)

            key_buy = (symbol, "BUY")
            key_sell = (symbol, "SELL")
            # Inicializar si no existen
            self.antiflip_opposite_counts.setdefault(key_buy, 0)
            self.antiflip_opposite_counts.setdefault(key_sell, 0)

            if last_type and last_type != signal_type:
                # Es opuesta: incrementar contador del tipo actual
                key = (symbol, signal_type)
                self.antiflip_opposite_counts[key] = (
                    self.antiflip_opposite_counts.get(key, 0) + 1
                )
            else:
                # Misma dirección: reiniciar contador del opuesto
                if signal_type == "BUY":
                    self.antiflip_opposite_counts[key_sell] = 0
                else:
                    self.antiflip_opposite_counts[key_buy] = 0
        except Exception:
            pass

    def _passes_antiflip_policy(self, signal: "TradingSignal") -> bool:
        """🛡️ Evaluar si una señal pasa la política AntiFlip.

        Reglas:
        - Min hold: no cerrar/revertir antes de X minutos desde la última entrada.
        - Cooldown después de salida: esperar X minutos antes de nueva entrada opuesta.
        - Persistencia: requerir N señales opuestas consecutivas antes de flip.
        - Histeresis: elevar umbral de confianza para flip.
        - Opuesto fuerte: requerir `strength` fuerte o alta confianza.
        """
        try:
            cfg = TradingProfiles.get_current_profile()
            min_hold = int(cfg.get("antiflip_min_hold_minutes", 0))
            exit_cd = int(cfg.get("antiflip_cooldown_after_exit_minutes", 0))
            persist_n = int(cfg.get("antiflip_opposite_persistence_count", 0))
            hyst_mult = float(cfg.get("antiflip_hysteresis_multiplier", 1.0))
            strong_required = bool(cfg.get("antiflip_require_strong_opposite", False))

            symbol = signal.symbol
            signal_type = signal.signal_type
            now = datetime.now(UTC_TZ)

            # Dirección actual de posición, si existe
            pos_dir = self._get_open_position_direction(symbol)

            # Regla: Cooldown posterior a salida
            last_exit = self.last_exit_times.get(symbol)
            if last_exit and exit_cd > 0:
                minutes_since_exit = (now - last_exit).total_seconds() / 60
                if minutes_since_exit < exit_cd:
                    remaining = exit_cd - minutes_since_exit
                    self.logger.info(
                        f"🛑 ANTI-FLIP: {symbol} bloqueado por cooldown post-exit ({minutes_since_exit:.1f}/{exit_cd}min, quedan {remaining:.1f}min)"
                    )
                    return False

            # Regla: Min hold si hay posición abierta y la señal pretende flip
            if pos_dir is not None:
                # Señal contraria al lado de la posición
                is_opposite_to_position = (
                    (pos_dir == "LONG" and signal_type == "SELL")
                    or (pos_dir == "SHORT" and signal_type == "BUY")
                )
                if is_opposite_to_position and min_hold > 0:
                    last_trade_time = self.last_trade_times.get(symbol)
                    if last_trade_time:
                        minutes_since_entry = (now - last_trade_time).total_seconds() / 60
                        if minutes_since_entry < min_hold:
                            remaining = min_hold - minutes_since_entry
                            self.logger.info(
                                f"🛑 ANTI-FLIP: {symbol} mantener posición {pos_dir} mínimo {min_hold}min (actual {minutes_since_entry:.1f}min, quedan {remaining:.1f}min)"
                            )
                            return False

            # Regla: Persistencia de señal opuesta
            last_type = self.last_signal_types.get(symbol)
            if last_type and last_type != signal_type and persist_n > 0:
                count = self.antiflip_opposite_counts.get((symbol, signal_type), 0)
                if count < persist_n:
                    self.logger.info(
                        f"🛑 ANTI-FLIP: {symbol} espera persistencia opuesta {count}/{persist_n} para {signal_type}"
                    )
                    return False

            # Regla: Histeresis de confianza para flip
            if last_type and last_type != signal_type and hyst_mult > 1.0:
                # Umbral de confianza ajustado por fin de semana y histeresis
                wk_params = get_weekend_trading_params()
                base_thr = self._normalize_percentage_threshold(self.min_confidence_threshold) * wk_params["min_confidence_multiplier"]
                required_conf = base_thr * hyst_mult
                if float(signal.confidence_score) < required_conf:
                    self.logger.info(
                        f"🛑 ANTI-FLIP: {symbol} confianza {signal.confidence_score:.1f}% < requerido {required_conf:.1f}% por histeresis"
                    )
                    return False

            # Regla: Opuesto fuerte requerido
            if last_type and last_type != signal_type and strong_required:
                # Usar `strength` si existe, si no, umbral de confianza alto
                strength = getattr(signal, "strength", None)
                is_strong = bool(strength) and str(strength).upper() in ["STRONG", "HIGH", "VERY_STRONG"]
                if not is_strong and float(signal.confidence_score) < 80.0:
                    self.logger.info(
                        f"🛑 ANTI-FLIP: {symbol} opuesto requiere fuerte/alta confianza (conf={signal.confidence_score:.1f}%)"
                    )
                    return False

            return True
        except Exception as e:
            self.logger.error(f"❌ Error evaluando AntiFlip para {signal.symbol}: {e}")
            # Fail-safe: permitir señal si hay error en evaluación
            return True

    def _is_weekend_trading(self) -> bool:
        """🗓️ Determinar si estamos en modo de trading de fin de semana"""
        try:
            current_day = datetime.now(UTC_TZ).weekday()  # 0=Monday, 6=Sunday
            return current_day >= 5  # Saturday (5) or Sunday (6)
        except Exception as e:
            self.logger.error(f"❌ Error determinando si es fin de semana: {e}")
            return False

    def _log_market_status(self):
        """📊 Mostrar estado de los mercados al inicio del análisis"""
        try:
            market_status = market_hours_checker.get_general_market_status()

            if market_status["open_markets"]:
                self.logger.info(
                    f"🟢 Mercados abiertos: {', '.join(market_status['open_markets'])}"
                )

            if market_status["closed_markets"]:
                self.logger.info(
                    f"🔴 Mercados cerrados: {', '.join(market_status['closed_markets'])}"
                )

            # Mostrar estado específico de los símbolos que estamos monitoreando
            tradeable_symbols = []
            non_tradeable_symbols = []

            for symbol in self.symbols:
                if market_hours_checker.should_trade(symbol)[0]:
                    tradeable_symbols.append(symbol)
                else:
                    non_tradeable_symbols.append(symbol)

            if tradeable_symbols:
                self.logger.info(
                    f"✅ Símbolos operables: {', '.join(tradeable_symbols)}"
                )

            if non_tradeable_symbols:
                self.logger.info(
                    f"⏸️ Símbolos no operables: {', '.join(non_tradeable_symbols)}"
                )

        except Exception as e:
            self.logger.warning(f"⚠️ Error al verificar estado de mercados: {e}")

    def _run_scheduler(self):
        """
        ⏰ Ejecutar scheduler en loop
        """
        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(APIConfig.SCHEDULER_SLEEP_INTERVAL)
            except Exception as e:
                self.logger.error(f"❌ Error in scheduler: {e}")
                time.sleep(APIConfig.ERROR_RECOVERY_SLEEP)

    def _run_analysis_cycle(self):
        """
        🔄 Ejecutar un ciclo completo de análisis con cache y procesamiento paralelo
        """
        try:
            self.logger.info("🔄 Starting optimized analysis cycle...")

            # Verificar si el trading está permitido hoy
            if not is_trading_day_allowed():
                current_day = datetime.now(UTC_TZ).strftime("%A")
                self.logger.info(
                    f"📅 Trading not allowed on {current_day} - skipping analysis cycle"
                )
                return

            # Verificar horarios inteligentes de trading (11:00 - 02:30 UTC)
            smart_hours_status = is_smart_trading_hours_allowed()

            # Manejo robusto del resultado de smart_hours_status
            if isinstance(smart_hours_status, bool):
                # Si devuelve un booleano (caso de error o configuración simple)
                if not smart_hours_status:
                    self.logger.info(
                        "🕘 Outside smart trading hours - skipping analysis cycle"
                    )
                    return
                else:
                    self.logger.info("🕘 Within smart trading hours")
            elif isinstance(smart_hours_status, dict):
                # Si devuelve un diccionario (caso normal)
                if not smart_hours_status.get("is_allowed", False):
                    self.logger.info(
                        f"🕘 {smart_hours_status.get('reason', 'Outside trading hours')} - skipping analysis cycle"
                    )
                    return
                else:
                    self.logger.info(
                        f"🕘 {smart_hours_status.get('reason', 'Within trading hours')}"
                    )
            else:
                # Caso inesperado - permitir trading por defecto
                self.logger.warning(
                    f"🕘 Unexpected smart_hours_status type: {type(smart_hours_status)} - allowing trading"
                )
                smart_hours_status = {
                    "is_allowed": True,
                    "reason": "Default allow due to unexpected status",
                }

                # Log detallado sobre configuración de horarios por mercado
                from src.config.time_trading_config import MARKET_SPECIFIC_CONFIG

                current_time = datetime.now(ZoneInfo(TIMEZONE))
                current_hour = current_time.hour

                self.logger.info(
                    f"🌍 Hora actual UTC: {current_time.strftime('%H:%M:%S UTC')}"
                )

                # Mostrar estado de cada tipo de mercado
                for market_type, config in MARKET_SPECIFIC_CONFIG.items():
                    # Obtener horarios de alta volatilidad para mostrar estado
                    volatility_hours = config.get("high_volatility_hours", {})
                    if volatility_hours:
                        # Mostrar la primera sesión como ejemplo
                        first_session = list(volatility_hours.values())[0]
                        start_hour = first_session["start"].hour
                        end_hour = first_session["end"].hour
                        is_active = start_hour <= current_hour < end_hour
                        status_icon = "🟢" if is_active else "🔴"
                        status_text = "ACTIVO" if is_active else "INACTIVO"

                        self.logger.info(
                            f"📊 {market_type.upper()}: {start_hour:02d}:00-{end_hour:02d}:00 CLT {status_icon} {status_text}"
                        )

                # Mostrar resumen de estado de horarios inteligentes
                smart_summary = get_smart_trading_status_summary()
                self.logger.info(f"📈 {smart_summary}")

            # Obtener parámetros de trading para fines de semana (si aplica)
            weekend_params = get_weekend_trading_params()
            is_weekend = datetime.now(UTC_TZ).strftime("%A").lower() in ["saturday", "sunday"]

            if is_weekend:
                self.logger.info(
                    f"🏖️ Weekend trading mode active with adjusted parameters:"
                )
                self.logger.info(
                    f"   - Min confidence multiplier: {weekend_params['min_confidence_multiplier']}"
                )
                self.logger.info(
                    f"   - Max daily trades multiplier: {weekend_params['max_daily_trades_multiplier']}"
                )
                self.logger.info(
                    f"   - Max position size multiplier: {weekend_params['max_position_size_multiplier']}"
                )

            # Mostrar estado de mercados
            self._log_market_status()

            # Resetear contador diario si es necesario
            self._reset_daily_stats_if_needed()

            # Verificar si podemos hacer más trades hoy (aplicando multiplicador de fin de semana y lógica adaptativa)
            base_max_trades = int(
                self.max_daily_trades * weekend_params["max_daily_trades_multiplier"]
            )
            # Usar el umbral de calidad del perfil para calcular el máximo adaptativo
            profile = TradingProfiles.get_current_profile()
            quality_threshold = profile.get("daily_trades_quality_threshold", 80.0)
            adaptive_max_trades = int(
                TradingProfiles.get_adaptive_daily_trades_limit(
                    current_trades_count=self.stats["daily_trades"],
                    signal_confidence=quality_threshold,
                )
                * weekend_params["max_daily_trades_multiplier"]
            )

            if self.stats["daily_trades"] >= base_max_trades:
                if self.stats["daily_trades"] >= adaptive_max_trades:
                    if is_weekend:
                        self.logger.info(
                            f"⏸️ Weekend adaptive daily trade limit reached ({adaptive_max_trades}, base: {base_max_trades})"
                        )
                    else:
                        self.logger.info(
                            f"⏸️ Adaptive daily trade limit reached ({adaptive_max_trades}, base: {base_max_trades})"
                        )
                    return
                else:
                    self.logger.info(
                        f"📈 Base limit reached ({base_max_trades}), but high-confidence trades still allowed (max: {adaptive_max_trades})"
                    )
            elif self.stats["daily_trades"] >= adaptive_max_trades:
                if is_weekend:
                    self.logger.info(
                        f"⏸️ Weekend daily trade limit reached ({adaptive_max_trades})"
                    )
                else:
                    self.logger.info(
                        f"⏸️ Daily trade limit reached ({adaptive_max_trades})"
                    )
                return

            # Generar clave de cache para este ciclo
            cache_key = self._get_cache_key(
                "analysis_cycle", tuple(self.symbols), tuple(self.strategies.keys())
            )

            # Verificar cache
            cached_signals = self._get_from_cache(cache_key)
            if cached_signals is not None:
                self.logger.info("⚡ Using cached analysis results")
                all_signals = cached_signals
                # Procesar señales con trading
                if all_signals:
                    self._process_signals(all_signals)
                else:
                    self.logger.info("⚪ No trading signals generated this cycle")
            else:
                # Usar el nuevo flujo secuencial con ejecución inmediata
                self.logger.info("🔄 Starting sequential analysis with immediate execution")
                self._analyze_symbols_sequential_with_immediate_execution()
                self.logger.info("✅ Sequential analysis with immediate execution completed")

            # Actualizar estadísticas en base de datos
            self._update_strategy_stats()

            # Actualizar tiempo del último análisis
            self.last_analysis_time = datetime.now(UTC_TZ)

            # Actualizar tiempo del próximo análisis
            self.next_analysis_time = self.last_analysis_time + timedelta(
                minutes=self.analysis_interval
            )

            self.logger.info("✅ Optimized analysis cycle completed")

        except Exception as e:
            self.logger.error(f"❌ Error in analysis cycle: {e}")
            # Log the full traceback for debugging
            import traceback
            self.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            
            # Don't stop the bot - continue with next cycle
            self.logger.info("🔄 Bot will continue with next analysis cycle despite error")

    def _analyze_symbols_parallel(self) -> List[TradingSignal]:
        """
        🚀 Analizar símbolos en paralelo para mejor rendimiento
        """
        all_signals = []

        # Crear tareas para el pool de hilos
        tasks = []
        for symbol in self.symbols:
            for strategy_name, strategy in self.strategies.items():
                tasks.append((symbol, strategy_name, strategy))

        # Ejecutar análisis en paralelo
        try:
            futures = []
            for symbol, strategy_name, strategy in tasks:
                future = self.executor.submit(
                    self._analyze_single_symbol, symbol, strategy_name, strategy
                )
                futures.append(future)

            # Recopilar resultados
            profile_config = TradingProfiles.get_current_profile()
            timeout = self.config.get_analysis_future_timeout()
            for future in futures:
                try:
                    signal = future.result(timeout=timeout)  # Timeout configurable
                    weekend_indicator = "🏖️" if self._is_weekend_trading() else "📊"

                    if signal:
                        if signal.signal_type != "HOLD":
                            all_signals.append(signal)
                            self.stats["signals_generated"] += 1
                            # Tracking separado para fines de semana
                            if self._is_weekend_trading():
                                self.stats["weekend_signals"] += 1
                            else:
                                self.stats["weekday_signals"] += 1

                        self.logger.info(
                            f"{weekend_indicator} Signal: {signal.signal_type} {signal.symbol} ({signal.strategy_name}) - Confidence: {signal.confidence_score}%"
                        )
                    else:
                        self.logger.debug(
                            f"{weekend_indicator} No signal generated for symbol"
                        )

                except Exception as e:
                    self.logger.error(f"❌ Error in parallel analysis: {e}")

        except Exception as e:
            self.logger.error(f"❌ Error in parallel execution: {e}")
            # Fallback a análisis secuencial
            all_signals = self._analyze_symbols_sequential()

        return all_signals

    def _analyze_single_symbol(
        self, symbol: str, strategy_name: str, strategy
    ) -> Optional[TradingSignal]:
        """
        📈 Analizar un símbolo con una estrategia específica
        """
        try:
            signal = strategy.analyze(symbol)
            if hasattr(signal, "strategy_name"):
                signal.strategy_name = strategy_name
            return signal
        except Exception as e:
            self.logger.error(f"❌ Error analyzing {symbol} with {strategy_name}: {e}")
            return None

    def _analyze_symbols_sequential(self) -> List[TradingSignal]:
        """
        🐌 Análisis secuencial como fallback
        """
        all_signals = []
        for symbol in self.symbols:
            for strategy_name, strategy in self.strategies.items():
                try:
                    signal = strategy.analyze(symbol)
                    weekend_indicator = "🏖️" if self._is_weekend_trading() else "📊"

                    if signal:
                        if signal.signal_type != "HOLD":
                            all_signals.append(signal)
                            self.stats["signals_generated"] += 1
                            # Tracking separado para fines de semana
                            if self._is_weekend_trading():
                                self.stats["weekend_signals"] += 1
                            else:
                                self.stats["weekday_signals"] += 1

                        self.logger.info(
                            f"{weekend_indicator} Signal: {signal.signal_type} {symbol} ({strategy_name}) - Confidence: {signal.confidence_score}%"
                        )
                    else:
                        self.logger.debug(
                            f"{weekend_indicator} No signal generated for {symbol} with {strategy_name}"
                        )

                except Exception as e:
                    self.logger.error(
                        f"❌ Error analyzing {symbol} with {strategy_name}: {e}"
                    )
        return all_signals

    def _analyze_symbols_sequential_with_immediate_execution(self):
        """
        🎯 Nuevo flujo: Analizar símbolo por símbolo con ejecución inmediata de trades
        
        FLUJO OPTIMIZADO SÍMBOLO POR SÍMBOLO:
        1. Tomar símbolo
        2. Analizar con todas las estrategias
        3. Procesar señales inmediatamente
        4. Ejecutar trades si hay señales válidas
        5. Esperar 1 segundo
        6. Repetir con siguiente símbolo
        """
        weekend_indicator = "🏖️" if self._is_weekend_trading() else "🎯"
        self.logger.info(f"{weekend_indicator} Starting sequential symbol-by-symbol analysis with immediate execution...")
        
        total_symbols = len(self.symbols)
        
        for symbol_index, symbol in enumerate(self.symbols, 1):
            try:
                self.logger.info(f"📊 {symbol} ({symbol_index}/{total_symbols})")
                
                # PASO 1: Analizar símbolo con todas las estrategias
                symbol_signals = []
                
                for strategy_name, strategy in self.strategies.items():
                    try:
                        signal = self._analyze_single_symbol(symbol, strategy_name, strategy)
                        if signal and signal.signal_type != "HOLD":
                            symbol_signals.append(signal)
                            self.stats["signals_generated"] += 1
                            # Tracking separado para fines de semana
                            if self._is_weekend_trading():
                                self.stats["weekend_signals"] += 1
                            else:
                                self.stats["weekday_signals"] += 1
                            
                            self.logger.info(
                                f"   ✅ Signal: {signal.signal_type} {signal.symbol} ({signal.strategy_name}) - Confidence: {signal.confidence_score}%"
                            )
                    except Exception as e:
                        self.logger.error(f"   ❌ Error analyzing {symbol} with {strategy_name}: {e}")
                
                # PASO 2: Procesar señales inmediatamente para este símbolo
                if symbol_signals:
                    self.logger.info(f"   🎯 Processing {len(symbol_signals)} signals for {symbol}...")
                    self._process_signals(symbol_signals)
                
                # PASO 3: Esperar 1 segundo antes del siguiente símbolo (excepto el último)
                if symbol_index < total_symbols:
                    time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error processing symbol {symbol}: {e}")
                # Continuar con el siguiente símbolo incluso si hay error
                continue
        
        self.logger.info(f"✅ Sequential symbol-by-symbol analysis completed for {total_symbols} symbols")

    def _normalize_percentage_threshold(self, value: float) -> float:
        """Normaliza umbrales que pueden venir en escala 0–1 a 0–100.

        Si el valor es <= 1.0 se asume fracción y se convierte a porcentaje.
        De lo contrario se retorna tal cual.
        """
        try:
            v = float(value)
            return v * 100.0 if v <= 1.0 else v
        except Exception:
            # Fallback defensivo
            return 0.0

    def _process_signals(self, signals: List[TradingSignal]):
        """
        🎯 Procesar y ejecutar señales de trading con flujo secuencial

        FLUJO OPTIMIZADO:
        1. Obtener balance disponible
        2. Analizar una señal -> ejecutar trade
        3. Actualizar balance disponible
        4. Repetir para la siguiente señal

        Args:
            signals: Lista de señales generadas
        """

        # Obtener parámetros de fin de semana para ajustar confianza mínima
        weekend_params = get_weekend_trading_params()
        base_threshold = self._normalize_percentage_threshold(self.min_confidence_threshold)
        adjusted_min_confidence = base_threshold * weekend_params["min_confidence_multiplier"]

        # Filtrar señales por confianza mínima (ajustada para fines de semana)
        high_confidence_signals = [
            signal
            for signal in signals
            if signal.confidence_score >= adjusted_min_confidence
        ]

        if not high_confidence_signals:
            is_weekend = datetime.now(UTC_TZ).strftime("%A").lower() in ["saturday", "sunday"]
            if is_weekend and adjusted_min_confidence != self.min_confidence_threshold:
                self.logger.info(
                    f"📉 No signals above weekend confidence threshold ({adjusted_min_confidence:.1f}%, adjusted from {self.min_confidence_threshold}%)"
                )
            else:
                self.logger.info(
                    f"📉 No signals above confidence threshold ({adjusted_min_confidence:.1f}%)"
                )
            return

        # Ordenar por confianza (mayor primero)
        high_confidence_signals.sort(key=lambda x: x.confidence_score, reverse=True)

        weekend_indicator = "🏖️" if self._is_weekend_trading() else "🎯"
        self.logger.info(
            f"{weekend_indicator} Processing {len(high_confidence_signals)} high-confidence signals sequentially..."
        )

        # Inicializar portfolio_summary antes del bucle para evitar errores
        portfolio_summary = self.get_portfolio_summary()

        # Procesar cada señal de forma secuencial con balance actualizado
        for i, signal in enumerate(high_confidence_signals, 1):
            try:
                weekend_indicator = "🏖️" if self._is_weekend_trading() else "📊"
                self.logger.info(
                    f"{weekend_indicator} Processing signal {i}/{len(high_confidence_signals)}: {signal.symbol}"
                )

                # Actualizar persistencia de señales opuestas para AntiFlip
                self._update_antiflip_persistence(signal)

                # Verificar límite diario adaptativo (aplicando multiplicador de fin de semana)
                weekend_params_loop = get_weekend_trading_params()
                base_max_trades_loop = int(
                    self.max_daily_trades
                    * weekend_params_loop["max_daily_trades_multiplier"]
                )
                # Usar la confianza específica de esta señal para determinar el límite
                adaptive_max_trades_loop = int(
                    TradingProfiles.get_adaptive_daily_trades_limit(
                        current_trades_count=self.stats["daily_trades"],
                        signal_confidence=signal.confidence_score,
                    )
                    * weekend_params_loop["max_daily_trades_multiplier"]
                )

                if self.stats["daily_trades"] >= adaptive_max_trades_loop:
                    if (
                        signal.confidence_score
                        >= TradingProfiles.get_current_profile().get(
                            "daily_trades_quality_threshold", 80.0
                        )
                    ):
                        self.logger.info(
                            f"⏸️ Adaptive daily trade limit reached for high-confidence signal ({adaptive_max_trades_loop})"
                        )
                    else:
                        self.logger.info(
                            f"⏸️ Daily trade limit reached ({base_max_trades_loop})"
                        )
                    break

                # CRÍTICO: Verificar límite de posiciones simultáneas
                if not self._check_max_positions_limit():
                    self.logger.info("⏸️ Maximum positions limit reached")
                    break

                # Verificar cooldown entre trades del mismo símbolo
                if not self._check_trade_cooldown(signal):
                    continue  # El método ya registra el mensaje de log

                # Filtro estricto adicional para señales de consenso
                if getattr(signal, "strategy_name", "") == "ConsensusStrategy":
                    # Umbrales conservadores para mejorar precisión
                    min_consensus_pct = 70.0
                    min_coherence_pct = 65.0
                    # Permitir ejecución con una sola estrategia contribuyente si el consenso es fuerte
                    # (el consenso sigue siendo el decisor principal; las individuales alimentan)
                    min_contrib = 1
                    min_rr = 1.30

                    consensus_pct = float(getattr(signal, "consensus_percentage", 0.0))
                    coherence = float(getattr(signal, "coherence_score", 0.0))
                    contrib = int(getattr(signal, "contributing_strategies_count", 0))
                    rr = float(getattr(signal, "risk_reward_ratio", 0.0))

                    if consensus_pct < min_consensus_pct:
                        self.logger.info(
                            f"❌ {signal.symbol}: Consenso insuficiente {consensus_pct:.1f}% < {min_consensus_pct}%"
                        )
                        continue
                    if coherence < min_coherence_pct:
                        self.logger.info(
                            f"❌ {signal.symbol}: Coherencia insuficiente {coherence:.1f}% < {min_coherence_pct}%"
                        )
                        continue
                    if contrib < min_contrib:
                        self.logger.info(
                            f"❌ {signal.symbol}: Estrategias contribuyentes {contrib} < {min_contrib}"
                        )
                        continue
                    if rr < min_rr:
                        self.logger.info(
                            f"❌ {signal.symbol}: R/R insuficiente {rr:.2f} < {min_rr:.2f}"
                        )
                        continue

                # Verificar horarios de mercado
                should_trade, market_reason = market_hours_checker.should_trade(
                    signal.symbol
                )
                if not should_trade:
                    self.logger.info(f"⏰ {signal.symbol}: {market_reason}")
                    continue

                self.logger.info(f"✅ {signal.symbol}: {market_reason}")

                # 🔄 PASO 1: Obtener balance actualizado antes de cada análisis
                portfolio_summary = self.get_portfolio_summary()
                portfolio_value = portfolio_summary.get("total_value", 1000.0)
                available_balance = portfolio_summary.get(
                    "available_balance", portfolio_value
                )

                self.logger.info(
                    f"💰 Updated balance for {signal.symbol}: Total=${portfolio_value:,.2f}, Available=${available_balance:,.2f}"
                )

                # 🔄 PASO 2: Análisis de riesgo con balance actualizado
                risk_assessment = self.risk_manager.assess_trade_risk(
                    signal, portfolio_value
                )

                # Aplicar multiplicador de tamaño de posición para fines de semana
                weekend_params = get_weekend_trading_params()
                original_position_size = (
                    risk_assessment.position_sizing.recommended_size
                )
                adjusted_position_size = (
                    original_position_size
                    * weekend_params["max_position_size_multiplier"]
                )

                # Actualizar el tamaño de posición en el risk assessment
                risk_assessment.position_sizing.recommended_size = (
                    adjusted_position_size
                )

                is_weekend = datetime.now(UTC_TZ).strftime("%A").lower() in [
                    "saturday",
                    "sunday",
                ]
                self.logger.info(f"🛡️ Risk assessment for {signal.symbol}:")
                self.logger.info(
                    f"   - Risk Score: {risk_assessment.overall_risk_score:.1f}/100"
                )
                if is_weekend and weekend_params["max_position_size_multiplier"] != 1.0:
                    self.logger.info(
                        f"   - Position Size: {adjusted_position_size:.2f} (weekend adjusted from {original_position_size:.2f})"
                    )
                else:
                    self.logger.info(
                        f"   - Position Size: {adjusted_position_size:.2f}"
                    )
                self.logger.info(f"   - Approved: {risk_assessment.is_approved}")
                self.logger.info(f"   - Risk Level: {risk_assessment.risk_level.value}")

                # 🔄 PASO 3: Ejecutar trade si está aprobado
                if risk_assessment.is_approved and self.enable_trading:
                    # Verificar política AntiFlip antes de ejecutar
                    pre_position_dir = self._get_open_position_direction(signal.symbol)
                    if not self._passes_antiflip_policy(signal):
                        self.logger.info(
                            f"🛑 {signal.symbol}: señal filtrada por política AntiFlip"
                        )
                        continue

                    # Construir preview de orden (SL/TSL ajustados por reglas) antes de ejecutar
                    try:
                        preview = self._build_order_preview(signal, risk_assessment)
                        if isinstance(preview, dict):
                            self.order_previews.append(preview)
                    except Exception:
                        pass

                    # Ejecutar paper trade siempre
                    trade_result = self.paper_trader.execute_signal(signal)

                    # Ejecutar trade real si está habilitado
                    real_trade_result = None
                    if self.enable_real_trading and self.capital_client:
                        real_trade_result = self._execute_real_trade(
                            signal, risk_assessment
                        )

                    if trade_result.success:
                        # Siempre contar trades ejecutados y métricas por día de semana/fin de semana
                        self.stats["trades_executed"] += 1
                        if self._is_weekend_trading():
                            self.stats["weekend_trades"] += 1
                        else:
                            self.stats["weekday_trades"] += 1

                        # Contar daily_trades SOLO para entradas (aperturas, incrementos y flips de dirección)
                        post_position_dir = self._get_open_position_direction(
                            signal.symbol
                        )
                        # Apertura: antes no había posición y ahora sí
                        opened_new_position = (
                            pre_position_dir is None and post_position_dir is not None
                        )
                        # Incremento: misma dirección antes y después, y existe posición
                        increased_same_direction = (
                            pre_position_dir == post_position_dir
                            and post_position_dir is not None
                        )
                        # Flip: había posición y ahora hay en dirección opuesta
                        flipped_direction_open = (
                            pre_position_dir is not None
                            and post_position_dir is not None
                            and pre_position_dir != post_position_dir
                        )
                        if (
                            opened_new_position
                            or increased_same_direction
                            or flipped_direction_open
                        ):
                            self.stats["daily_trades"] += 1

                        # Determinar si fue exitoso basándose en el tipo de trade y PnL real
                        trade_was_profitable = False
                        if signal.signal_type == "SELL":
                            # Para ventas, verificar si hay PnL positivo en el mensaje
                            if (
                                "PnL:" in trade_result.message
                                and "$" in trade_result.message
                            ):
                                try:
                                    # Extraer PnL del mensaje: "PnL: $X.XX"
                                    pnl_part = trade_result.message.split("PnL: $")[
                                        1
                                    ].split(")")[0]
                                    pnl_value = float(pnl_part)
                                    trade_was_profitable = pnl_value > 0
                                except:
                                    trade_was_profitable = False
                        else:
                            # Para compras, solo contar como exitoso si se ejecutó correctamente
                            # El éxito real se determinará cuando se venda
                            trade_was_profitable = trade_result.success

                        if trade_was_profitable:
                            self.stats["successful_trades"] += 1
                            # Tracking separado para fines de semana
                            if self._is_weekend_trading():
                                self.stats["weekend_successful_trades"] += 1
                            else:
                                self.stats["weekday_successful_trades"] += 1

                        # Actualizar tracking de pérdidas consecutivas para estadísticas
                        if trade_was_profitable:
                            self.consecutive_losses = 0
                        else:
                            self.consecutive_losses += 1

                        # Mensaje de log combinado
                        log_message = f"✅ Paper Trade executed: {trade_result.message}"
                        if real_trade_result:
                            if real_trade_result.get("success"):
                                log_message += f" | 🔴 Real Trade: SUCCESS - Deal ID: {real_trade_result.get('deal_id', 'N/A')}"
                            else:
                                log_message += f" | 🔴 Real Trade: FAILED - {real_trade_result.get('error', 'Unknown error')}"

                        self.logger.info(log_message)

                        # Actualizar tracking de cooldown para el símbolo
                        self._update_trade_tracking(signal)

                        # Iniciar cooldown post-exit si la operación cerró una posición
                        try:
                            symbol = signal.symbol
                            closed_long = pre_position_dir == "LONG" and signal.signal_type == "SELL"
                            closed_short = pre_position_dir == "SHORT" and signal.signal_type == "BUY"
                            if closed_long or closed_short:
                                self.last_exit_times[symbol] = datetime.now(UTC_TZ)
                                self.logger.info(
                                    f"🕒 Exit cooldown iniciado para {symbol} a las {self.last_exit_times[symbol].strftime('%H:%M:%S')}"
                                )
                        except Exception:
                            pass

                        # 🔄 PASO 4: Actualizar balance después del trade (implícito en próxima iteración)

                        # Emitir evento de trade ejecutado
                        self._emit_trade_event(signal, trade_result, risk_assessment)
                    else:
                        # Trade falló en ejecución - no contar como pérdida consecutiva
                        self.logger.warning(f"❌ Trade failed: {trade_result.message}")

                elif not risk_assessment.is_approved:
                    rejection_reason = f"Risk level: {risk_assessment.risk_level.value}"
                    self.logger.info(f"🚫 Trade rejected: {rejection_reason}")

                    # Mostrar recomendaciones
                    for rec in risk_assessment.recommendations:
                        self.logger.info(f"   💡 {rec}")

            except Exception as e:
                self.logger.error(f"❌ Error processing signal {signal.symbol}: {e}")

        # Actualizar P&L total
        current_pnl = portfolio_summary.get("total_pnl", 0)
        previous_pnl = self.stats["total_pnl"]
        pnl_change = current_pnl - previous_pnl

        self.stats["total_pnl"] = current_pnl

        # Tracking separado de PnL para fines de semana
        if self._is_weekend_trading() and pnl_change != 0:
            self.stats["weekend_pnl"] += pnl_change
        elif not self._is_weekend_trading() and pnl_change != 0:
            self.stats["weekday_pnl"] += pnl_change

        # Emitir evento de análisis completado
        self._emit_analysis_event(
            len(high_confidence_signals), self.stats["daily_trades"]
        )

    def _reset_daily_stats_if_needed(self):
        """
        📅 Resetear estadísticas diarias a las 14:00 UTC (11:00 AM Chile convertido)
        """
        try:
            tz = ZoneInfo(TIMEZONE) if ZoneInfo else None
        except Exception:
            tz = None
        now_local = datetime.now(tz) if tz else datetime.now()
        current_day = now_local.date()
        reset_dt = (
            datetime(
                current_day.year,
                current_day.month,
                current_day.day,
                DAILY_RESET_HOUR,
                DAILY_RESET_MINUTE,
                tzinfo=tz,
            )
            if tz
            else datetime(
                current_day.year,
                current_day.month,
                current_day.day,
                DAILY_RESET_HOUR,
                DAILY_RESET_MINUTE,
            )
        )

        # Realizar reset solo una vez por día cuando la hora local haya alcanzado o superado el reset
        if now_local >= reset_dt and self.stats.get("last_reset_day") != current_day:
            self.stats["daily_trades"] = 0
            self.stats["last_reset_day"] = current_day
            # Resetear circuit breaker al inicio del nuevo periodo diario
            self.consecutive_losses = 0
            self.circuit_breaker_active = False
            self.circuit_breaker_activated_at = None
            self.logger.info(
                f"📅 Daily stats reset at {DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d} ({TIMEZONE}) on {current_day} - Circuit breaker reset"
            )
        else:
            # Sin acción antes del horario de reset o si ya se realizó en el día
            pass

    def _update_strategy_stats(self):
        """
        📈 Estadísticas de estrategias disponibles en Capital.com
        """
        # Las estadísticas se pueden ver directamente en Capital.com
        # No necesitamos mantener una base de datos local para esto
        pass

    def get_status(self) -> BotStatus:
        """
        📊 Obtener estado actual del bot
        """
        uptime = "Not running"
        next_analysis = self.next_analysis_time  # Usar variable de instancia
        last_analysis = self.last_analysis_time  # No usar datetime.now() como fallback

        if self.is_running and self.start_time:
            uptime_delta = datetime.now(UTC_TZ) - self.start_time
            hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        portfolio_summary = self.get_portfolio_summary()

        status = BotStatus(
            is_running=self.is_running,
            uptime=uptime,
            total_signals_generated=self.stats["signals_generated"],
            total_trades_executed=self.stats["trades_executed"],
            successful_trades=self.stats["successful_trades"],
            current_portfolio_value=portfolio_summary.get("total_value", 0),
            total_pnl=portfolio_summary.get("total_pnl", 0),
            active_strategies=list(self.strategies.keys()),
            last_analysis_time=last_analysis,
            next_analysis_time=next_analysis,
        )

        return status

    def get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio directamente de Capital.com

        Returns:
            Dict: Resumen del portfolio
        """
        try:
            logger.info(f"🔧 DEBUG: get_portfolio_summary iniciado")
            logger.info(
                f"🔧 DEBUG: capital_client disponible: {self.capital_client is not None}"
            )

            if self.capital_client is None:
                raise Exception("Capital client no está inicializado")

            # Obtener balance disponible de Capital.com
            logger.info(f"🔧 DEBUG: llamando get_available_balance()")
            balance_info = self.capital_client.get_available_balance()

            if isinstance(balance_info, dict):
                available_balance = float(balance_info.get("available", 0.0))
                # El balance total (equity) incluye posiciones abiertas
                total_balance = float(balance_info.get("balance", available_balance))
                total_pnl = float(balance_info.get("profit_loss", 0.0))
            elif isinstance(balance_info, (str, int, float)):
                available_balance = float(balance_info)
                total_balance = available_balance
                total_pnl = 0.0
            else:
                available_balance = 0.0
                total_balance = 0.0
                total_pnl = 0.0

            logger.info(f"🔧 DEBUG: available_balance: ${available_balance:.2f}")
            logger.info(f"🔧 DEBUG: total_balance (equity): ${total_balance:.2f}")
            logger.info(f"🔧 DEBUG: profit_loss: ${total_pnl:.2f}")

            # Obtener posiciones abiertas de Capital.com (solo para contar)
            logger.info(f"🔧 DEBUG: llamando get_positions()")
            positions_response = self.capital_client.get_positions()

            # Extraer la lista de posiciones de la respuesta
            positions = []
            if positions_response.get("success") and positions_response.get(
                "positions"
            ):
                positions = positions_response.get("positions", [])
                logger.info(f"🔧 DEBUG: positions count: {len(positions)}")

            # El valor total del portfolio es el balance total (equity) que ya incluye las posiciones
            total_value = total_balance

            logger.info(f"🔧 DEBUG: final total_value (equity): ${total_value:.2f}")

            result = {
                "total_value": total_value,
                "available_balance": available_balance,
                "total_pnl": total_pnl,
                "open_positions": len(positions) if positions else 0,
                "source": "capital_com",
            }

            logger.info(f"🔧 DEBUG: get_portfolio_summary returning: {result}")
            return result

        except Exception as e:
            import traceback

            logger.error(f"❌ Error obteniendo portfolio de Capital.com: {e}")
            logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
            # Fallback: usar paper trader si hay error
            fallback_result = self.paper_trader.get_portfolio_summary()
            logger.info(f"🔧 DEBUG: using paper trader fallback: {fallback_result}")
            return fallback_result

    def get_detailed_report(self) -> Dict:
        """
        📋 Obtener reporte detallado del bot
        """
        status = self.get_status()
        portfolio_summary = self.get_portfolio_summary()
        risk_report = self.risk_manager.generate_risk_report()
        open_positions = self.paper_trader.get_open_positions()

        return {
            "bot_status": {
                "is_running": status.is_running,
                "uptime": status.uptime,
                "analysis_interval_minutes": self.analysis_interval,
                "next_analysis": (
                    status.next_analysis_time.isoformat()
                    if status.next_analysis_time
                    else None
                ),
                "enable_trading": self.enable_trading,
            },
            "trading_stats": {
                "total_signals_generated": status.total_signals_generated,
                "total_trades_executed": status.total_trades_executed,
                "successful_trades": status.successful_trades,
                "win_rate": (
                    status.successful_trades / max(1, status.total_trades_executed)
                )
                * 100,
                "daily_trades": self.stats["daily_trades"],
                "daily_limit": self.max_daily_trades,
                "weekday_stats": {
                    "signals_generated": self.stats.get("weekday_signals", 0),
                    "trades_executed": self.stats.get("weekday_trades", 0),
                    "successful_trades": self.stats.get("weekday_successful_trades", 0),
                    "win_rate": (
                        self.stats.get("weekday_successful_trades", 0)
                        / max(1, self.stats.get("weekday_trades", 0))
                    )
                    * 100,
                    "total_pnl": self.stats.get("weekday_pnl", 0.0),
                },
                "weekend_stats": {
                    "signals_generated": self.stats.get("weekend_signals", 0),
                    "trades_executed": self.stats.get("weekend_trades", 0),
                    "successful_trades": self.stats.get("weekend_successful_trades", 0),
                    "win_rate": (
                        self.stats.get("weekend_successful_trades", 0)
                        / max(1, self.stats.get("weekend_trades", 0))
                    )
                    * 100,
                    "total_pnl": self.stats.get("weekend_pnl", 0.0),
                },
            },
            "portfolio": {
                "current_value": status.current_portfolio_value,
                "total_pnl": status.total_pnl,
                "total_return_percentage": (
                    (
                        status.current_portfolio_value
                        - self.config.DEFAULT_PORTFOLIO_VALUE
                    )
                    / self.config.DEFAULT_PORTFOLIO_VALUE
                )
                * 100,
                "assets": portfolio_summary.get("assets", []),
            },
            "strategies": {
                "active": status.active_strategies,
                "symbols_monitored": self.symbols,
                "min_confidence_threshold": self.min_confidence_threshold,
            },
            "risk_management": risk_report,
            "open_positions": open_positions,
            "position_monitor": {
                "enabled": self.config.get_position_monitoring_enabled(),
                "status": (
                    self.position_monitor.get_monitoring_status()
                    if self.config.get_position_monitoring_enabled()
                    else "disabled"
                ),
                "active_positions": len(open_positions),
            },
            "configuration": {
                "analysis_interval_minutes": self.analysis_interval,
                "max_daily_trades": self.max_daily_trades,
                "min_confidence_threshold": self.min_confidence_threshold,
                "enable_trading": self.enable_trading,
            },
            "timestamp": datetime.now(UTC_TZ).isoformat(),
        }

    def get_configuration(self) -> Dict:
        """
        📋 Obtener configuración actual del bot
        """
        try:
            active_strategies = [name for name, strategy in self.strategies.items()]

            config = {
                # Configuraciones básicas
                "analysis_interval_minutes": self.analysis_interval,
                "active_strategies": active_strategies,
                "is_running": self.is_running,
                "total_strategies": len(self.strategies),
                "uptime_hours": (
                    (datetime.now(UTC_TZ) - self.start_time).total_seconds() / 3600
                    if self.start_time
                    else 0
                ),
                "max_daily_trades": self.max_daily_trades,
                "min_confidence_threshold": self.min_confidence_threshold,
                "enable_trading": self.enable_trading,
                "symbols": self.symbols,
                # Configuraciones de posiciones
                "max_concurrent_positions": getattr(
                    self, "max_concurrent_positions", None
                ),
                # Configuraciones de timeframes
                "primary_timeframe": getattr(self, "primary_timeframe", None),
                "confirmation_timeframe": getattr(self, "confirmation_timeframe", None),
                "trend_timeframe": getattr(self, "trend_timeframe", None),
                # Configuraciones de trading real
                "enable_real_trading": getattr(self, "enable_real_trading", False),
                "real_trading_size_multiplier": getattr(
                    self, "real_trading_size_multiplier", 0.1
                ),
            }

            # Agregar configuraciones del paper trader si está disponible
            if hasattr(self, "paper_trader") and self.paper_trader:
                if hasattr(self.paper_trader, "get_configuration"):
                    paper_config = self.paper_trader.get_configuration()
                    config.update(
                        {
                            "max_position_size": paper_config.get("max_position_size"),
                            "max_total_exposure": paper_config.get(
                                "max_total_exposure"
                            ),
                            "min_trade_value": paper_config.get("min_trade_value"),
                        }
                    )
                else:
                    # Valores por defecto si no hay método get_configuration
                    config.update(
                        {
                            "max_position_size": getattr(
                                self.paper_trader, "max_position_size", None
                            ),
                            "max_total_exposure": getattr(
                                self.paper_trader, "max_total_exposure", None
                            ),
                            "min_trade_value": getattr(
                                self.paper_trader, "min_trade_value", None
                            ),
                        }
                    )

            # Agregar configuraciones del risk manager si está disponible
            if hasattr(self, "risk_manager") and self.risk_manager:
                if hasattr(self.risk_manager, "get_configuration"):
                    risk_config = self.risk_manager.get_configuration()
                    config.update(
                        {
                            "max_risk_per_trade": risk_config.get("max_risk_per_trade"),
                            "max_daily_risk": risk_config.get("max_daily_risk"),
                            "max_drawdown_threshold": risk_config.get(
                                "max_drawdown_threshold"
                            ),
                            "correlation_threshold": risk_config.get(
                                "correlation_threshold"
                            ),
                        }
                    )
                else:
                    # Valores por defecto si no hay método get_configuration
                    config.update(
                        {
                            "max_risk_per_trade": getattr(
                                self.risk_manager, "max_portfolio_risk", None
                            ),
                            "max_daily_risk": getattr(
                                self.risk_manager, "max_daily_risk", None
                            ),
                            "max_drawdown_threshold": getattr(
                                self.risk_manager, "max_drawdown_threshold", None
                            ),
                            "correlation_threshold": getattr(
                                self.risk_manager, "correlation_threshold", None
                            ),
                        }
                    )

            return config
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo configuración: {e}")
            return {}

    def update_configuration(self, config: Dict):
        """
        ⚙️ Actualizar configuración del bot

        Args:
            config: Diccionario con nueva configuración
        """
        try:
            # Configuraciones básicas del bot
            if "analysis_interval_minutes" in config:
                self.analysis_interval = max(1, config["analysis_interval_minutes"])
                self.logger.info(
                    f"⚙️ Analysis interval updated to {self.analysis_interval} minutes"
                )

            if "max_daily_trades" in config:
                self.max_daily_trades = max(1, config["max_daily_trades"])
                self.logger.info(
                    f"⚙️ Max daily trades updated to {self.max_daily_trades}"
                )

            if "min_confidence_threshold" in config:
                self.min_confidence_threshold = max(
                    0, min(100, config["min_confidence_threshold"])
                )
                self.logger.info(
                    f"⚙️ Min confidence threshold updated to {self.min_confidence_threshold}%"
                )

            if "enable_trading" in config:
                self.enable_trading = bool(config["enable_trading"])
                status = "enabled" if self.enable_trading else "disabled"
                self.logger.info(f"⚙️ Trading execution {status}")

            if "symbols" in config and isinstance(config["symbols"], list):
                self.symbols = config["symbols"]
                self.logger.info(f"⚙️ Symbols updated: {', '.join(self.symbols)}")

            # Configuraciones de posiciones
            if "max_concurrent_positions" in config:
                self.max_concurrent_positions = max(
                    1, config["max_concurrent_positions"]
                )
                self.logger.info(
                    f"⚙️ Max concurrent positions updated to {self.max_concurrent_positions}"
                )

            # Configuraciones de timeframes
            if "primary_timeframe" in config:
                self.primary_timeframe = config["primary_timeframe"]
                self.logger.info(
                    f"⚙️ Primary timeframe updated to {self.primary_timeframe}"
                )

            if "confirmation_timeframe" in config:
                self.confirmation_timeframe = config["confirmation_timeframe"]
                self.logger.info(
                    f"⚙️ Confirmation timeframe updated to {self.confirmation_timeframe}"
                )

            if "trend_timeframe" in config:
                self.trend_timeframe = config["trend_timeframe"]
                self.logger.info(f"⚙️ Trend timeframe updated to {self.trend_timeframe}")

            # Configuraciones de trading real
            if "enable_real_trading" in config:
                self.enable_real_trading = bool(config["enable_real_trading"])
                status = "enabled" if self.enable_real_trading else "disabled"
                self.logger.info(f"⚙️ Real trading {status}")

            if "real_trading_size_multiplier" in config:
                self.real_trading_size_multiplier = max(
                    0.01, min(1.0, config["real_trading_size_multiplier"])
                )
                self.logger.info(
                    f"⚙️ Real trading size multiplier updated to {self.real_trading_size_multiplier}"
                )

            # Configuraciones del paper trader (si están disponibles)
            if hasattr(self, "paper_trader") and self.paper_trader:
                paper_config = {}
                if "max_position_size" in config:
                    paper_config["max_position_size"] = max(
                        0.01, min(1.0, config["max_position_size"])
                    )
                if "max_total_exposure" in config:
                    paper_config["max_total_exposure"] = max(
                        0.01, min(1.0, config["max_total_exposure"])
                    )
                if "min_trade_value" in config:
                    paper_config["min_trade_value"] = max(
                        1.0, config["min_trade_value"]
                    )

                if paper_config:
                    # Actualizar configuración del paper trader si tiene método de actualización
                    if hasattr(self.paper_trader, "update_configuration"):
                        self.paper_trader.update_configuration(paper_config)
                        self.logger.info(
                            f"⚙️ Paper trader configuration updated: {paper_config}"
                        )

            # Configuraciones del risk manager (si están disponibles)
            if hasattr(self, "risk_manager") and self.risk_manager:
                risk_config = {}
                if "max_risk_per_trade" in config:
                    risk_config["max_portfolio_risk"] = max(
                        0.001, min(0.05, config["max_risk_per_trade"])
                    )
                if "max_daily_risk" in config:
                    risk_config["max_daily_risk"] = max(
                        0.005, min(0.1, config["max_daily_risk"])
                    )
                if "max_drawdown_threshold" in config:
                    risk_config["max_drawdown_threshold"] = max(
                        0.05, min(0.5, config["max_drawdown_threshold"])
                    )
                if "correlation_threshold" in config:
                    risk_config["correlation_threshold"] = max(
                        0.1, min(1.0, config["correlation_threshold"])
                    )

                if risk_config:
                    # Actualizar configuración del risk manager si tiene método de actualización
                    if hasattr(self.risk_manager, "update_configuration"):
                        self.risk_manager.update_configuration(risk_config)
                        self.logger.info(
                            f"⚙️ Risk manager configuration updated: {risk_config}"
                        )

        except Exception as e:
            self.logger.error(f"❌ Error updating configuration: {e}")

    def force_analysis(self):
        """
        🔄 Forzar análisis inmediato (útil para testing)
        """
        if self.is_running:
            self.logger.info("🔄 Forcing immediate analysis...")
            self._run_analysis_cycle()
        else:
            self.logger.warning("⚠️ Bot is not running - cannot force analysis")

    def emergency_stop(self):
        """
        🚨 Parada de emergencia (cierra todas las posiciones)
        """
        self.logger.warning("🚨 EMERGENCY STOP INITIATED")

        try:
            # Detener el bot
            self.stop()

            # Obtener posiciones abiertas
            open_positions = self.paper_trader.get_open_positions()

            if open_positions:
                self.logger.warning(
                    f"🚨 Closing {len(open_positions)} open positions..."
                )

                # Aquí podrías implementar lógica para cerrar posiciones automáticamente
                # Por ahora solo loggeamos
                for position in open_positions:
                    self.logger.warning(
                        f"   📊 Open position: {position['symbol']} - ${position['entry_value']:.2f}"
                    )

            self.logger.warning("🚨 Emergency stop completed")

        except Exception as e:
            self.logger.error(f"❌ Error during emergency stop: {e}")

    def test_connection(self) -> bool:
        """🔌 Probar conexión con la API de Capital.com

        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            if not self.capital_client:
                self._initialize_capital_client()

            if not self.capital_client:
                self.logger.error("❌ Capital.com client not available")
                return False

            # Probar conexión con ping
            ping_result = self.capital_client.ping()
            if not ping_result.get("success"):
                self.logger.error("❌ Capital.com ping failed")
                return False

            # Probar obtención de cuentas
            accounts = self.capital_client.get_accounts()
            if not accounts:
                self.logger.error("❌ No accounts found in Capital.com")
                return False

            self.logger.info("✅ Conexión con Capital.com exitosa")
            self.logger.info(f"📊 Cuentas disponibles: {len(accounts)}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error de conexión con Capital.com: {e}")
            return False

    def _emit_trade_event(
        self, signal: TradingSignal, trade_result: TradeResult, risk_assessment
    ):
        """📢 Emitir evento de trade ejecutado"""
        try:
            event = {
                "type": "trade_executed",
                "timestamp": datetime.now(UTC_TZ),
                "symbol": signal.symbol,
                "signal_type": signal.signal_type,
                "confidence": signal.confidence_score,
                "entry_price": trade_result.entry_price,
                "quantity": trade_result.quantity,
                "tp_price": getattr(signal, "take_profit", None),
                "sl_price": getattr(signal, "stop_loss", None),
                "risk_score": risk_assessment.overall_risk_score,
                "position_size": risk_assessment.position_sizing.recommended_size,
                "success": trade_result.success,
                "message": trade_result.message,
            }

            self.event_queue.put(event, block=False)

        except queue.Full:
            self.logger.warning("⚠️ Event queue full, dropping trade event")
        except Exception as e:
            self.logger.error(f"❌ Error emitting trade event: {e}")

    def _emit_analysis_event(self, signals_count: int, daily_trades: int):
        """📢 Emitir evento de análisis completado"""
        try:
            event = {
                "type": "analysis_completed",
                "timestamp": datetime.now(UTC_TZ),
                "signals_generated": signals_count,
                "daily_trades": daily_trades,
                "max_daily_trades": self.max_daily_trades,
                "portfolio_value": self.stats.get("total_pnl", 0),
            }

            self.event_queue.put(event, block=False)

        except queue.Full:
            self.logger.warning("⚠️ Event queue full, dropping analysis event")
        except Exception as e:
            self.logger.error(f"❌ Error emitting analysis event: {e}")

    def _normalize_symbol_for_capital(self, symbol: str) -> str:
        """
        🔄 Normalizar símbolo para Capital.com

        Args:
            symbol: Símbolo original (ej: ETHUSD, US100, GOLD)

        Returns:
            Símbolo tal como está definido en GLOBAL_SYMBOLS (sin modificaciones)
        """
        # Los símbolos en GLOBAL_SYMBOLS ya están en el formato correcto para Capital.com
        # No necesitamos agregar USD automáticamente
        return symbol.upper()

    def _execute_real_trade(
        self, signal: TradingSignal, risk_assessment
    ) -> Dict[str, Any]:
        """
        🔴 Ejecutar trade real en Capital.com

        Args:
            signal: Señal de trading
            risk_assessment: Evaluación de riesgo

        Returns:
            Dict con resultado del trade real
        """
        try:
            # 1. Verificar balance disponible
            balance_result = self.capital_client.get_available_balance()
            if not balance_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to get account balance: {balance_result.get('error')}",
                }

            available_balance = balance_result.get("available", 0)
            currency_symbol = balance_result.get("symbol", "$")

            self.logger.info(
                f"💰 Available balance: {currency_symbol}{available_balance}"
            )

            # 2. Convertir símbolo al formato de Capital.com
            capital_symbol = self._normalize_symbol_for_capital(signal.symbol)

            # 3. Usar el tamaño de posición calculado por el risk manager (que ya considera apalancamiento)
            current_price = (
                signal.price if hasattr(signal, "price") else signal.current_price
            )

            # El risk_assessment ya calculó el tamaño óptimo en UNIDADES del activo
            # recommended_size ya incluye el apalancamiento aplicado
            # Aplicar real_trading_size_multiplier para trading real (por defecto 10% del tamaño de paper trading)
            real_size = (
                risk_assessment.position_sizing.recommended_size
                * self.real_trading_size_multiplier
            )
            leverage_used = risk_assessment.position_sizing.leverage_used
            position_value_usd = (
                risk_assessment.position_sizing.position_value
            )  # Valor total en USD

            # 4. Redondear a 4 decimales para crypto (más precisión)
            real_size = round(real_size, 4)

            # 5. Validar y ajustar tamaño mínimo según Capital.com
            if hasattr(self.capital_client, 'get_minimum_order_size'):
                min_size = self.capital_client.get_minimum_order_size(capital_symbol)
                if real_size < min_size:
                    self.logger.warning(f"⚠️ Tamaño calculado {real_size:.4f} es menor al mínimo {min_size} para {capital_symbol}")
                    self.logger.info(f"🔧 Ajustando tamaño a mínimo requerido: {min_size}")
                    real_size = min_size
                    
                    # Recalcular valores con el nuevo tamaño
                    total_position_value = real_size * current_price
                    required_margin = total_position_value / leverage_used
                    
                    self.logger.info(f"📊 Valores recalculados:")
                    self.logger.info(f"   Nuevo tamaño: {real_size:.4f} unidades")
                    self.logger.info(f"   Nuevo valor posición: {currency_symbol}{total_position_value:.2f}")
                    self.logger.info(f"   Nuevo margen requerido: {currency_symbol}{required_margin:.2f}")

            # Calcular valores para mostrar correctamente (si no se calcularon arriba)
            if 'total_position_value' not in locals():
                total_position_value = real_size * current_price
                required_margin = total_position_value / leverage_used

            # Log detallado del cálculo
            self.logger.info(f"💰 Cálculo de posición real:")
            self.logger.info(
                f"   Balance disponible: {currency_symbol}{available_balance:.2f}"
            )
            self.logger.info(
                f"   Tamaño base recomendado: {risk_assessment.position_sizing.recommended_size:.4f} unidades"
            )
            self.logger.info(
                f"   Real trading multiplier: {self.real_trading_size_multiplier}"
            )
            self.logger.info(f"   Tamaño final real: {real_size:.4f} unidades")
            self.logger.info(f"   Apalancamiento usado: {leverage_used}x")
            self.logger.info(
                f"   Precio actual {capital_symbol}: {currency_symbol}{current_price:.2f}"
            )
            self.logger.info(
                f"   Valor total posición: {currency_symbol}{total_position_value:.2f}"
            )
            self.logger.info(
                f"   Margen requerido: {currency_symbol}{required_margin:.2f}"
            )
            self.logger.info(
                f"   Verificación: {real_size:.4f} * {currency_symbol}{current_price:.2f} = {currency_symbol}{total_position_value:.2f}"
            )

            # 5. Verificar si tenemos suficiente balance para el trade
            # Los valores ya están calculados arriba: total_position_value y required_margin

            if available_balance < required_margin:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Available: {currency_symbol}{available_balance:.2f}, Required margin: {currency_symbol}{required_margin:.2f}, Position value: {currency_symbol}{total_position_value:.2f}",
                }

            # Verificar tamaño mínimo (Capital.com generalmente requiere mínimo 0.01)
            if real_size < 0.01:
                return {
                    "success": False,
                    "error": f"Position size too small: {real_size} (minimum: 0.01)",
                }

            # 6. Obtener valores de TP y SL de la señal
            stop_loss = None
            take_profit = None

            # Verificar si estamos usando perfiles que soportan cálculo basado en ROI
            current_profile_config = TradingProfiles.get_current_profile()
            current_profile = current_profile_config.get("name", "")
            if current_profile in ["Scalping", "Intraday"]:
                # Para perfiles ROI, recalcular TP/SL basado en ROI del balance invertido
                try:
                    from .trend_following_professional import TrendFollowingProfessional

                    strategy_instance = TrendFollowingProfessional()

                    # Obtener ATR para el cálculo
                    current_price = self._get_current_price(signal.symbol)
                    atr = current_price * 0.02  # ATR estimado como 2% del precio

                    # Calcular TP/SL basado en ROI usando el tamaño de posición real
                    position_size_usd = real_size * current_price  # Convertir a USD
                    stop_loss, take_profit, risk_reward = (
                        strategy_instance.calculate_roi_based_risk_reward(
                            current_price, signal.signal_type, position_size_usd, atr
                        )
                    )

                    # Ajuste del stop loss sensible al spread del instrumento
                    try:
                        md = self.capital_client.get_market_data([capital_symbol]) if self.capital_client else {}
                        if md and capital_symbol in md:
                            bid = md[capital_symbol].get("bid")
                            offer = md[capital_symbol].get("offer")
                            if bid is not None and offer is not None and offer > bid:
                                spread = offer - bid
                                if signal.signal_type == "BUY":
                                    stop_loss = stop_loss - spread
                                else:
                                    stop_loss = stop_loss + spread
                        # Aplicar mínimos de distancia del SL y redondeo según dealing rules
                        dr = self.capital_client.get_dealing_rules(capital_symbol) if self.capital_client else {"success": False}
                        if dr.get("success"):
                            import math
                            min_stop = dr.get("min_stop_distance", {})
                            step = dr.get("min_step_distance", {})
                            # Precio de referencia según lado
                            ref_price = (
                                bid if signal.signal_type == "BUY" and bid is not None
                                else offer if signal.signal_type == "SELL" and offer is not None
                                else current_price
                            )
                            unit = (min_stop.get("unit") or "").upper()
                            value = float(min_stop.get("value") or 0.0)
                            min_points = 0.0
                            if unit == "PERCENTAGE":
                                min_points = ref_price * value
                            elif unit == "POINTS":
                                min_points = value
                            # Enforce mínimo
                            if signal.signal_type == "BUY":
                                dist = ref_price - stop_loss
                                if dist < min_points:
                                    stop_loss = ref_price - min_points
                            else:
                                dist = stop_loss - ref_price
                                if dist < min_points:
                                    stop_loss = ref_price + min_points
                            # Redondeo al paso mínimo
                            step_unit = (step.get("unit") or "").upper()
                            step_value = float(step.get("value") or 0.0)
                            if step_unit == "POINTS" and step_value > 0:
                                if signal.signal_type == "BUY":
                                    dist = ref_price - stop_loss
                                    dist = math.ceil(dist / step_value) * step_value
                                    stop_loss = ref_price - dist
                                else:
                                    dist = stop_loss - ref_price
                                    dist = math.ceil(dist / step_value) * step_value
                                    stop_loss = ref_price + dist
                    except Exception as e:
                        self.logger.warning(f"⚠️ No se pudo ajustar SL por spread: {e}")

                    self.logger.info(
                        f"🎯 {current_profile} ROI-based TP/SL calculated:"
                    )
                    self.logger.info(f"🛡️ Stop Loss (ROI-based): ${stop_loss:.4f}")
                    self.logger.info(f"🎯 Take Profit (ROI-based): ${take_profit:.4f}")
                    self.logger.info(f"📊 Risk/Reward Ratio: {risk_reward:.2f}")

                except Exception as e:
                    self.logger.warning(
                        f"⚠️ Error calculating ROI-based TP/SL for SCALPING: {e}"
                    )
                    # Fallback a valores originales
                    stop_loss = None
                    take_profit = None

            # Si no se calculó con ROI o no es SCALPING, usar valores de la señal
            if (
                stop_loss is None
                and hasattr(signal, "stop_loss_price")
                and signal.stop_loss_price > 0
            ):
                stop_loss = signal.stop_loss_price
                self.logger.info(f"🛡️ Stop Loss: ${stop_loss:.4f}")

            if (
                take_profit is None
                and hasattr(signal, "take_profit_price")
                and signal.take_profit_price > 0
            ):
                take_profit = signal.take_profit_price
                self.logger.info(f"🎯 Take Profit: ${take_profit:.4f}")

            # Si no hay TP/SL en la señal, usar valores del risk assessment
            if stop_loss is None and hasattr(risk_assessment, "dynamic_stop_loss"):
                stop_loss = risk_assessment.dynamic_stop_loss.stop_loss_price
                self.logger.info(
                    f"🛡️ Stop Loss (from risk assessment): ${stop_loss:.4f}"
                )

            if take_profit is None and hasattr(risk_assessment, "dynamic_take_profit"):
                take_profit = risk_assessment.dynamic_take_profit.take_profit_price
                self.logger.info(
                    f"🎯 Take Profit (from risk assessment): ${take_profit:.4f}"
                )

            # Ajuste de distancias TP/SL según preferencia del usuario:
            # - Reducir TP en 50% para todos los símbolos
            # - Aumentar SL en 50% solo si el riesgo en USD está entre 10–20 y el símbolo no es US30
            try:
                if stop_loss is not None and take_profit is not None:
                    # Obtener precio actual para calcular distancias
                    ref_price = None
                    try:
                        ref_price = self._get_current_price(signal.symbol)
                    except Exception:
                        ref_price = None

                    # Si no se puede obtener precio actual, usar heurística con TP/SL existentes
                    if ref_price is None:
                        # Para BUY, ref es el punto medio; para SELL, igual
                        ref_price = (take_profit + stop_loss) / 2.0

                    # Calcular distancias actuales
                    if signal.signal_type == "BUY":
                        tp_dist = max(take_profit - ref_price, 0.0)
                        sl_dist = max(ref_price - stop_loss, 0.0)
                    else:
                        tp_dist = max(ref_price - take_profit, 0.0)
                        sl_dist = max(stop_loss - ref_price, 0.0)

                    # Calcular riesgo en USD aproximado para decidir aumento de SL
                    # Asume relación CFD: riesgo ≈ distancia * tamaño real
                    risk_usd = sl_dist * real_size

                    # Determinar si aplicar aumento de SL (50%)
                    symbol_upper = (signal.symbol or "").upper()
                    keep_sl_unchanged = symbol_upper == "US30"
                    increase_sl = (not keep_sl_unchanged) and (10.0 <= risk_usd <= 20.0)

                    # Aplicar reducción de TP (50%)
                    new_tp_dist = tp_dist * 0.5

                    # Aplicar aumento de SL (50%) si corresponde
                    new_sl_dist = sl_dist * (1.5 if increase_sl else 1.0)

                    # Reconstruir niveles TP/SL manteniendo orientación
                    if signal.signal_type == "BUY":
                        take_profit = ref_price + new_tp_dist
                        stop_loss = ref_price - new_sl_dist
                    else:
                        take_profit = ref_price - new_tp_dist
                        stop_loss = ref_price + new_sl_dist

                    self.logger.info(
                        f"⚙️ Ajustes TP/SL aplicados: TP -50% (distancia), SL {'+50%' if increase_sl else 'sin cambio'} (distancia), riesgoUSD≈{risk_usd:.2f}"
                    )
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo aplicar ajustes de TP/SL preferidos: {e}")

            # 7. Aplicar estrictamente reglas del instrumento (min distance, steps, orientación)
            try:
                bid = None
                offer = None
                md = self.capital_client.get_market_data([capital_symbol]) if self.capital_client else {}
                if md and capital_symbol in md:
                    bid = md[capital_symbol].get("bid")
                    offer = md[capital_symbol].get("offer")
                dr = self.capital_client.get_dealing_rules(capital_symbol) if self.capital_client else {"success": False}
                if not dr.get("success"):
                    dr = {}
                # Proveer símbolo actual al helper para clampeo por instrumento
                try:
                    self.current_signal_symbol = signal.symbol
                except Exception:
                    self.current_signal_symbol = None
                sl_adj, tp_adj, stop_points = self._apply_dealing_rules_to_tp_sl(
                    signal.signal_type, bid, offer, stop_loss, take_profit, dr
                )
                # Limpiar símbolo temporal
                try:
                    self.current_signal_symbol = None
                except Exception:
                    pass
                stop_loss = sl_adj
                take_profit = tp_adj
                self.logger.info(
                    f"🔧 Reglas aplicadas: SL={stop_loss}, TP={take_profit}, stopDistance={stop_points}"
                )
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo aplicar reglas de instrumento a TP/SL: {e}")

            self.logger.info(
                f"🔴 Executing REAL trade: {signal.signal_type} {capital_symbol} size={real_size}"
            )
            self.logger.info(f"🔴 Stop Loss: {stop_loss}, Take Profit: {take_profit}")
            self.logger.info(f"🔴 Capital.com API URL: {self.capital_client.base_url}")

            # Determinar si usar trailing stop basado en configuración del perfil
            use_trailing_stop = TradingProfiles.get_current_profile().get(
                "use_trailing_stop", False
            )
            trailing_distance = None
            trailing_stop_available = False

            if use_trailing_stop and stop_loss:
                # Obtener bid/offer para calcular distancia sensible al spread
                bid = None
                offer = None
                try:
                    md = self.capital_client.get_market_data([capital_symbol]) if self.capital_client else {}
                    if md and capital_symbol in md:
                        bid = md[capital_symbol].get("bid")
                        offer = md[capital_symbol].get("offer")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error obteniendo bid/offer para {capital_symbol}: {e}")

                spread = 0.0
                if bid is not None and offer is not None and offer > bid:
                    spread = offer - bid

                if signal.signal_type == "BUY":
                    reference_price = bid if bid is not None else current_price
                    base_distance = reference_price - stop_loss
                else:
                    reference_price = offer if offer is not None else current_price
                    base_distance = stop_loss - reference_price

                # Si ya calculamos stopDistance por reglas, úsalo como base
                if 'stop_points' in locals() and isinstance(stop_points, (int, float)) and stop_points > 0:
                    base_distance = stop_points

                trailing_distance = base_distance + spread

                if trailing_distance > 0:
                    trailing_stop_available = True
                    self.logger.info(
                        f"🎯 Trailing stop enabled for {signal.signal_type}"
                    )
                    self.logger.info(
                        f"🎯 Price ref: {reference_price:.4f}, SL: {stop_loss:.4f}, Spread: {spread:.4f}"
                    )
                    self.logger.info(
                        f"🎯 stopDistance ajustado por spread: {trailing_distance:.4f} puntos"
                    )
                else:
                    trailing_stop_available = False
                    self.logger.warning(
                        f"⚠️ Distancia de trailing inválida: {trailing_distance:.4f} (debe ser positiva)"
                    )
                    self.logger.warning("⚠️ Se usará stop loss tradicional")

            # Ejecutar orden según el tipo de señal
            if signal.signal_type == "BUY":
                # Verificar modo hedging y posición existente para posible flip
                self.logger.info(
                    f"🔴 Verificando modo hedging y posiciones existentes para BUY..."
                )

                preferences_result = self.capital_client.get_account_preferences()
                hedging_mode = False
                if preferences_result.get("success"):
                    hedging_mode = preferences_result.get("hedging_mode", False)
                    self.logger.info(
                        f"🔄 Modo hedging: {'ACTIVADO' if hedging_mode else 'DESACTIVADO'}"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ No se pudo obtener preferencias de cuenta: {preferences_result.get('error')}"
                    )

                positions_result = self.capital_client.get_positions()
                if not positions_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Failed to get positions: {positions_result.get('error')}",
                    }

                open_position = None
                for position in positions_result.get("positions", []):
                    if position.get("market", {}).get("epic") == capital_symbol:
                        open_position = position
                        break

                # Si existe posición SELL y no hay hedging, cerrar completamente y luego abrir BUY
                if (
                    open_position
                    and not hedging_mode
                    and str(open_position.get("position", {}).get("direction", "")).upper() == "SELL"
                ):
                    deal_id = open_position.get("position", {}).get("dealId")
                    position_size = abs(
                        float(open_position.get("position", {}).get("size", 0))
                    )
                    close_size = position_size  # cerrar toda la posición opuesta

                    self.logger.info(
                        f"🔴 Cerrando posición SELL existente antes de abrir BUY - Deal ID: {deal_id}, Size: {close_size}"
                    )
                    close_result = self.capital_client.close_position(
                        deal_id=deal_id, direction="BUY", size=close_size
                    )
                    self.logger.info(f"🔴 Respuesta de Capital.com CLOSE: {close_result}")

                    if not close_result.get("success"):
                        return {
                            "success": False,
                            "error": f"Failed to close opposite position: {close_result.get('error')}",
                        }

                # Abrir BUY (en modo hedging siempre abre; en modo normal abre tras cierre o si no había opuesta)
                self.logger.info(f"🔴 Enviando orden BUY a Capital.com...")
                if trailing_stop_available and trailing_distance:
                    result = self.capital_client.buy_market_order(
                        epic=capital_symbol,
                        size=real_size,
                        take_profit=take_profit,
                        trailing_stop=True,
                        stop_distance=trailing_distance,
                    )
                    self.logger.info(
                        f"🎯 BUY order with trailing stop - Distance: {trailing_distance}"
                    )
                else:
                    result = self.capital_client.buy_market_order(
                        epic=capital_symbol,
                        size=real_size,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                    )
                    if use_trailing_stop and not trailing_stop_available:
                        self.logger.info(
                            f"🔄 BUY order with traditional stop loss (trailing stop not available)"
                        )
                    else:
                        self.logger.info(f"🔴 BUY order with traditional stop loss")
                self.logger.info(f"🔴 Respuesta de Capital.com BUY: {result}")
            elif signal.signal_type == "SELL":
                # Verificar modo hedging antes de decidir si cerrar o abrir nueva posición
                self.logger.info(
                    f"🔴 Verificando modo hedging y posiciones existentes para SELL..."
                )

                # Obtener preferencias de cuenta para verificar modo hedging
                preferences_result = self.capital_client.get_account_preferences()
                hedging_mode = False
                if preferences_result.get("success"):
                    hedging_mode = preferences_result.get("hedging_mode", False)
                    self.logger.info(
                        f"🔄 Modo hedging: {'ACTIVADO' if hedging_mode else 'DESACTIVADO'}"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ No se pudo obtener preferencias de cuenta: {preferences_result.get('error')}"
                    )

                # Obtener posiciones existentes
                positions_result = self.capital_client.get_positions()
                if not positions_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Failed to get positions: {positions_result.get('error')}",
                    }

                # Buscar posición abierta para este símbolo
                open_position = None
                for position in positions_result.get("positions", []):
                    if position.get("market", {}).get("epic") == capital_symbol:
                        open_position = position
                        break

                # Si existe posición BUY y no hay hedging, cerrar completamente y luego abrir SELL
                if (
                    open_position
                    and not hedging_mode
                    and str(open_position.get("position", {}).get("direction", "")).upper() == "BUY"
                ):
                    deal_id = open_position.get("position", {}).get("dealId")
                    position_size = abs(
                        float(open_position.get("position", {}).get("size", 0))
                    )
                    close_size = position_size  # cerrar toda la posición opuesta

                    self.logger.info(
                        f"🔴 Cerrando posición BUY existente antes de abrir SELL - Deal ID: {deal_id}, Size: {close_size}"
                    )
                    close_result = self.capital_client.close_position(
                        deal_id=deal_id, direction="SELL", size=close_size
                    )
                    self.logger.info(f"🔴 Respuesta de Capital.com CLOSE: {close_result}")

                    if not close_result.get("success"):
                        return {
                            "success": False,
                            "error": f"Failed to close opposite position: {close_result.get('error')}",
                        }

                # Abrir nueva posición SELL (en hedging siempre abre; en normal abre tras cierre o si no había opuesta)
                if hedging_mode and open_position:
                    self.logger.info(
                        f"🔄 Abriendo nueva posición SELL en modo hedging (manteniendo posición existente)"
                    )
                else:
                    self.logger.info(f"🔴 Enviando orden SELL a Capital.com...")

                if trailing_stop_available and trailing_distance:
                    result = self.capital_client.sell_market_order(
                        epic=capital_symbol,
                        size=real_size,
                        take_profit=take_profit,
                        trailing_stop=True,
                        stop_distance=trailing_distance,
                    )
                    self.logger.info(
                        f"🎯 SELL order with trailing stop - Distance: {trailing_distance}"
                    )
                else:
                    result = self.capital_client.sell_market_order(
                        epic=capital_symbol,
                        size=real_size,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                    )
                    if use_trailing_stop and not trailing_stop_available:
                        self.logger.info(
                            f"🔄 SELL order with traditional stop loss (trailing stop not available)"
                        )
                    else:
                        self.logger.info(f"🔴 SELL order with traditional stop loss")
                self.logger.info(f"🔴 Respuesta de Capital.com SELL: {result}")
            else:
                return {
                    "success": False,
                    "error": f"Unknown signal type: {signal.signal_type}",
                }

            # Log del resultado
            if result.get("success"):
                self.logger.info(
                    f"🔴 Real trade SUCCESS: {signal.signal_type} {capital_symbol} - Deal ID: {result.get('deal_id')}"
                )
            else:
                self.logger.error(
                    f"🔴 Real trade FAILED: {signal.signal_type} {capital_symbol} - Error: {result.get('error')}"
                )

            return result

        except Exception as e:
            error_msg = f"Exception executing real trade: {str(e)}"
            self.logger.error(f"🔴 {error_msg}")
            return {"success": False, "error": error_msg}

    def get_events(self) -> List[Dict]:
        """📥 Obtener eventos pendientes para LiveTradingBot"""
        events = []
        try:
            while not self.event_queue.empty():
                events.append(self.event_queue.get_nowait())
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f"❌ Error getting events: {e}")

        return events

    def process_position_timeouts(self) -> Dict[str, int]:
        """⏰ Procesar timeouts de posiciones activas

        Verifica todas las posiciones activas y cierra las que hayan excedido
        el tiempo límite configurado en position_timeout_hours.

        Returns:
            Diccionario con estadísticas del procesamiento
        """
        try:
            logger.info("⏰ Starting position timeout processing...")
            result = self.position_monitor.process_position_timeouts()

            if result.get("timeout_positions", 0) > 0:
                logger.info(
                    f"⏰ Timeout processing completed: {result['closed_positions']}/{result['timeout_positions']} "
                    f"positions closed from {result['total_positions']} total"
                )
            else:
                logger.debug(
                    f"⏰ No positions with timeout found from {result['total_positions']} total"
                )

            return result

        except Exception as e:
            logger.error(f"❌ Error processing position timeouts: {e}")
            return {
                "total_positions": 0,
                "timeout_positions": 0,
                "closed_positions": 0,
                "error": str(e),
            }

    def get_profitable_positions(self, min_profit: float = 1.0) -> List[Dict]:
        """
        💰 Obtener posiciones con ganancias no realizadas mayores al mínimo especificado

        Args:
            min_profit: Ganancia mínima en USD para considerar la posición rentable (default: 1.0)

        Returns:
            Lista de posiciones rentables con información relevante
        """
        try:
            if not self.capital_client:
                self.logger.warning(
                    "⚠️ Capital client not available for getting positions"
                )
                return []

            # Obtener posiciones abiertas de Capital.com
            positions_result = self.capital_client.get_positions()
            if not positions_result.get("success"):
                self.logger.warning(
                    f"⚠️ Failed to get positions: {positions_result.get('error')}"
                )
                return []

            profitable_positions = []
            capital_positions = positions_result.get("positions", [])

            for position in capital_positions:
                try:
                    # Extraer información de la posición
                    market_info = position.get("market", {})
                    position_info = position.get("position", {})

                    # Obtener UPL (Unrealized Profit/Loss)
                    upl = float(position_info.get("upl", 0))
                    deal_id = position_info.get("dealId")
                    epic = market_info.get("epic", "")
                    direction = position_info.get("direction", "")
                    size = float(position_info.get("size", 0))
                    level = float(position_info.get("level", 0))

                    # Verificar si la posición es rentable
                    if upl > min_profit and deal_id:
                        profitable_positions.append(
                            {
                                "deal_id": deal_id,
                                "epic": epic,
                                "direction": direction,
                                "size": size,
                                "entry_level": level,
                                "upl": upl,
                                "currency": position_info.get("currency", "USD"),
                            }
                        )

                        self.logger.info(
                            f"💰 Profitable position found: {epic} {direction} - UPL: ${upl:.2f}"
                        )

                except (ValueError, KeyError) as e:
                    self.logger.warning(f"⚠️ Error processing position data: {e}")
                    continue

            self.logger.info(
                f"💰 Found {len(profitable_positions)} profitable positions (UPL > ${min_profit})"
            )
            return profitable_positions

        except Exception as e:
            self.logger.error(f"❌ Error getting profitable positions: {e}")
            return []

    def close_profitable_positions(self, min_profit: float = 1.0) -> Dict[str, Any]:
        """
        🎯 Cerrar todas las posiciones con ganancias no realizadas mayores al mínimo especificado

        Args:
            min_profit: Ganancia mínima en USD para cerrar la posición (default: 1.0)

        Returns:
            Diccionario con el resultado del cierre de posiciones
        """
        try:
            if not self.capital_client:
                return {
                    "success": False,
                    "error": "Capital client not available",
                    "positions_found": 0,
                    "positions_closed": 0,
                    "total_profit_realized": 0.0,
                }

            # Obtener posiciones rentables
            profitable_positions = self.get_profitable_positions(min_profit)

            if not profitable_positions:
                self.logger.info(
                    f"💰 No profitable positions found with UPL > ${min_profit}"
                )
                return {
                    "success": True,
                    "message": f"No profitable positions found with UPL > ${min_profit}",
                    "positions_found": 0,
                    "positions_closed": 0,
                    "total_profit_realized": 0.0,
                }

            # Cerrar cada posición rentable
            closed_positions = 0
            total_profit = 0.0
            failed_closes = []

            for position in profitable_positions:
                deal_id = position["deal_id"]
                epic = position["epic"]
                upl = position["upl"]

                try:
                    # Cerrar la posición usando el dealId
                    close_result = self.capital_client.close_position(deal_id)

                    if close_result.get("success"):
                        closed_positions += 1
                        total_profit += upl
                        self.logger.info(
                            f"🎯 Closed profitable position: {epic} (Deal ID: {deal_id}) - Profit: ${upl:.2f}"
                        )
                    else:
                        failed_closes.append(
                            {
                                "deal_id": deal_id,
                                "epic": epic,
                                "error": close_result.get("error", "Unknown error"),
                            }
                        )
                        self.logger.error(
                            f"❌ Failed to close position {epic} (Deal ID: {deal_id}): {close_result.get('error')}"
                        )

                except Exception as e:
                    failed_closes.append(
                        {"deal_id": deal_id, "epic": epic, "error": str(e)}
                    )
                    self.logger.error(
                        f"❌ Exception closing position {epic} (Deal ID: {deal_id}): {e}"
                    )

            # Preparar resultado
            result = {
                "success": True,
                "message": f"Closed {closed_positions}/{len(profitable_positions)} profitable positions",
                "positions_found": len(profitable_positions),
                "positions_closed": closed_positions,
                "total_profit_realized": total_profit,
                "failed_closes": failed_closes,
            }

            if closed_positions > 0:
                self.logger.info(
                    f"🎯 Successfully closed {closed_positions} profitable positions - Total profit realized: ${total_profit:.2f}"
                )

            if failed_closes:
                self.logger.warning(f"⚠️ Failed to close {len(failed_closes)} positions")
                result["success"] = (
                    closed_positions > 0
                )  # Parcialmente exitoso si cerró algunas

            return result

        except Exception as e:
            self.logger.error(f"❌ Error closing profitable positions: {e}")
            return {
                "success": False,
                "error": str(e),
                "positions_found": 0,
                "positions_closed": 0,
                "total_profit_realized": 0.0,
            }

    def schedule_pre_reset_profit_taking(self):
        """
        ⏰ Programar el cierre automático de posiciones rentables 15 minutos antes del reset diario
        """
        try:
            # Calcular la hora de cierre en UTC (15 minutos antes del reset)
            utc_reset_hour = DAILY_RESET_HOUR
            utc_reset_minute = DAILY_RESET_MINUTE - 15

            # Ajustar si los minutos son negativos
            if utc_reset_minute < 0:
                utc_reset_hour -= 1
                utc_reset_minute += 60

            # Asegurar que la hora esté en rango válido
            if utc_reset_hour < 0:
                utc_reset_hour += 24

            # Convertir UTC a hora local del sistema para schedule
            try:
                import pytz
                
                # Crear un datetime UTC para hoy a la hora del pre-reset
                utc_time = datetime.now(UTC_TZ).replace(
                    hour=utc_reset_hour, 
                    minute=utc_reset_minute, 
                    second=0, 
                    microsecond=0
                )
                
                # Obtener la zona horaria local del sistema (Chile)
                local_tz = pytz.timezone('America/Santiago')
                local_time = utc_time.astimezone(local_tz)
                
                # Formatear las horas para logging y scheduling
                local_time_str = f"{local_time.hour:02d}:{local_time.minute:02d}"
                utc_time_str = f"{utc_reset_hour:02d}:{utc_reset_minute:02d}"

                # Programar el cierre automático usando la hora local
                schedule.every().day.at(local_time_str).do(
                    self._execute_pre_reset_profit_taking
                ).tag("pre_reset_profit_taking")

                self.logger.info(
                    f"⏰ Pre-reset profit taking scheduled at {utc_time_str} UTC ({local_time_str} local Chile time) - 15 minutes before reset"
                )
                
            except ImportError:
                # Fallback si pytz no está disponible
                pre_reset_time_str = f"{utc_reset_hour:02d}:{utc_reset_minute:02d}"
                schedule.every().day.at(pre_reset_time_str).do(
                    self._execute_pre_reset_profit_taking
                ).tag("pre_reset_profit_taking")
                
                self.logger.warning(
                    f"⚠️ pytz not available, using system timezone. Pre-reset scheduled at {pre_reset_time_str}"
                )

        except Exception as e:
            self.logger.error(f"❌ Error scheduling pre-reset profit taking: {e}")

    def _execute_pre_reset_profit_taking(self):
        """
        🎯 Ejecutar el cierre automático de posiciones rentables antes del reset
        """
        try:
            # Mostrar la hora actual en UTC y local para claridad
            try:
                import pytz
                
                utc_now = datetime.now(UTC_TZ)
                local_tz = pytz.timezone('America/Santiago')
                local_now = utc_now.astimezone(local_tz)
                
                self.logger.info(
                    f"🎯 Executing pre-reset profit taking at {utc_now.strftime('%H:%M:%S')} UTC "
                    f"({local_now.strftime('%H:%M:%S')} Chile time)..."
                )
            except ImportError:
                self.logger.info("🎯 Executing pre-reset profit taking...")

            # Cerrar posiciones con UPL > 1 USD
            result = self.close_profitable_positions(min_profit=1.0)

            if result.get("success"):
                positions_closed = result.get("positions_closed", 0)
                total_profit = result.get("total_profit_realized", 0.0)

                if positions_closed > 0:
                    self.logger.info(
                        f"🎯 Pre-reset profit taking completed: {positions_closed} positions closed, ${total_profit:.2f} profit realized"
                    )

                    # Emitir evento de cierre automático
                    try:
                        self.event_queue.put(
                            {
                                "type": "pre_reset_profit_taking",
                                "timestamp": datetime.now(UTC_TZ),
                                "positions_closed": positions_closed,
                                "total_profit": total_profit,
                                "message": f"Closed {positions_closed} profitable positions before reset",
                            }
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"⚠️ Could not emit pre-reset profit taking event: {e}"
                        )
                else:
                    self.logger.info(
                        "🎯 Pre-reset profit taking: No profitable positions to close"
                    )
            else:
                self.logger.error(
                    f"❌ Pre-reset profit taking failed: {result.get('error')}"
                )

        except Exception as e:
            self.logger.error(f"❌ Error executing pre-reset profit taking: {e}")

    def get_consensus_statistics(self) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas del consenso de estrategias

        Returns:
            Diccionario con estadísticas del consenso
        """
        try:
            consensus_adapter = self.strategies.get("ConsensusStrategy")
            if not consensus_adapter:
                return {"error": "Consensus strategy not available"}

            return consensus_adapter.get_consensus_stats()

        except Exception as e:
            self.logger.error(f"❌ Error getting consensus statistics: {e}")
            return {"error": str(e)}

    def update_strategy_weights(self, weights: Dict[str, float]) -> Dict[str, Any]:
        """
        ⚖️ Actualizar los pesos de las estrategias en el consenso

        Args:
            weights: Diccionario con los nuevos pesos {strategy_name: weight}

        Returns:
            Diccionario con el resultado de la actualización
        """
        try:
            consensus_adapter = self.strategies.get("ConsensusStrategy")
            if not consensus_adapter:
                return {"success": False, "error": "Consensus strategy not available"}

            result = consensus_adapter.update_strategy_weights(weights)

            if result.get("success"):
                self.logger.info(f"⚖️ Strategy weights updated: {weights}")
            else:
                self.logger.error(
                    f"❌ Failed to update strategy weights: {result.get('error')}"
                )

            return result

        except Exception as e:
            self.logger.error(f"❌ Error updating strategy weights: {e}")
            return {"success": False, "error": str(e)}

    def get_last_consensus_details(self) -> Dict[str, Any]:
        """
        🔍 Obtener detalles del último análisis de consenso

        Returns:
            Diccionario con detalles del último consenso
        """
        try:
            consensus_adapter = self.strategies.get("ConsensusStrategy")
            if not consensus_adapter:
                return {"error": "Consensus strategy not available"}

            return consensus_adapter.get_last_consensus_analysis()

        except Exception as e:
            self.logger.error(f"❌ Error getting last consensus details: {e}")
            return {"error": str(e)}

    def get_individual_strategy_signals(self, symbol: str) -> Dict[str, Any]:
        """
        🔍 Obtener señales individuales de cada estrategia para un símbolo

        Args:
            symbol: Símbolo a analizar

        Returns:
            Diccionario con las señales de cada estrategia individual
        """
        try:
            if not hasattr(self, "individual_strategies"):
                return {"error": "Individual strategies not available"}

            signals = {}
            for strategy_name, strategy in self.individual_strategies.items():
                try:
                    signal = strategy.analyze(symbol)
                    if signal:
                        signals[strategy_name] = {
                            "signal_type": signal.signal_type,
                            "confidence_score": signal.confidence_score,
                            "price": getattr(
                                signal, "price", getattr(signal, "current_price", None)
                            ),
                            "timestamp": signal.timestamp,
                            "strategy_specific_data": getattr(
                                signal, "strategy_specific_data", {}
                            ),
                        }
                    else:
                        signals[strategy_name] = {
                            "signal_type": "HOLD",
                            "confidence_score": 0,
                        }

                except Exception as e:
                    self.logger.warning(
                        f"⚠️ Error analyzing {symbol} with {strategy_name}: {e}"
                    )
                    signals[strategy_name] = {"error": str(e)}

            return {"symbol": symbol, "individual_signals": signals}

        except Exception as e:
            self.logger.error(f"❌ Error getting individual strategy signals: {e}")
            return {"error": str(e)}


trading_bot = TradingBot()

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
    TradingBotConfig, TradingProfiles, APIConfig, CacheConfig, 
    TIMEZONE, DAILY_RESET_HOUR, DAILY_RESET_MINUTE,
    GLOBAL_SYMBOLS
)
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
from .enhanced_strategies import TradingSignal, ProfessionalRSIStrategy, MultiTimeframeStrategy, EnsembleStrategy
from .paper_trader import PaperTrader, TradeResult
from .enhanced_risk_manager import EnhancedRiskManager, EnhancedRiskAssessment
from .position_monitor import PositionMonitor
from .position_adjuster import PositionAdjuster
from .capital_client import CapitalClient, create_capital_client_from_env

# Configurar logging ANTES de la clase
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        self.analysis_interval = analysis_interval_minutes or self.config.get_analysis_interval()
        self.is_running = False
        self.start_time = None
        
        # Configurar logger PRIMERO
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cliente de Capital.com
        self.capital_client = None
        self._initialize_capital_client()
        
        # Obtener balance real para sincronizar con paper trader
        real_balance = self._get_real_balance()
        
        # Componentes principales
        self.paper_trader = PaperTrader(initial_balance=real_balance)
        self.risk_manager = EnhancedRiskManager(capital_client=self.capital_client)
        
        # Sistema de monitoreo de posiciones
        self.position_monitor = PositionMonitor(
            price_fetcher=self._get_current_price,
            paper_trader=self.paper_trader
        )
        
        # Sistema de ajuste de posiciones TP/SL (desactivado - Opción A)
        self.position_adjuster = None
        
        # Sistema de eventos para comunicación con LiveTradingBot
        profile_config = TradingProfiles.get_current_profile()
        self.event_queue = queue.Queue(maxsize=profile_config.get('event_queue_maxsize', 1000))
        self.adjustment_thread = None
        self.trade_event_callback = None  # Callback para eventos de trades
        
        # ThreadPool para procesamiento paralelo
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="TradingBot")
        
        # Estrategias disponibles (Enhanced)
        self.strategies = {}
        self._initialize_strategies()
        
        # Símbolos a analizar - usar configuración centralizada
        self.symbols = GLOBAL_SYMBOLS.copy()
        
        # Configuración de trading profesional desde configuración centralizada
        self.min_confidence_threshold = self.config.get_min_confidence_threshold()
        self.max_daily_trades = self.config.get_max_daily_trades()
        self.max_concurrent_positions = self.config.get_max_concurrent_positions()
        self.enable_trading = True  # Activar/desactivar ejecución de trades
        
        # Configuración de trading real vs paper trading
        self.enable_real_trading = os.getenv('ENABLE_REAL_TRADING', 'false').lower() == 'true'
        self.real_trading_size_multiplier = float(os.getenv('REAL_TRADING_SIZE_MULTIPLIER', '0.1'))  # 10% del tamaño de paper trading por defecto
        
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
        reset_dt = datetime(
            now_local.year,
            now_local.month,
            now_local.day,
            DAILY_RESET_HOUR,
            DAILY_RESET_MINUTE,
            tzinfo=tz
        ) if tz else datetime(
            now_local.year,
            now_local.month,
            now_local.day,
            DAILY_RESET_HOUR,
            DAILY_RESET_MINUTE
        )
        initial_last_reset_day = now_local.date() if now_local >= reset_dt else (now_local.date() - timedelta(days=1))
        
        # Estadísticas
        self.stats = {
            "signals_generated": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "daily_trades": 0,
            "last_reset_day": initial_last_reset_day
        }
        
        # Tracking de pérdidas consecutivas para estadísticas
        self.consecutive_losses = 0
        
        # Thread para ejecución
        self.analysis_thread = None
        self.stop_event = threading.Event()
        
        self.logger.info("🤖 Trading Bot initialized with Position Monitor")

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
            if self.capital_client and hasattr(self.capital_client, 'get_accounts'):
                accounts = self.capital_client.get_accounts()
                if accounts and len(accounts) > 0:
                    # Usar el primer account disponible
                    balance = float(accounts[0].get('balance', {}).get('available', 0.0))
                    self.logger.info(f"💰 Balance real obtenido de Capital.com: ${balance:.2f}")
                    return balance
                else:
                    self.logger.warning("⚠️ No se encontraron cuentas en Capital.com")
            else:
                self.logger.warning("⚠️ Cliente de Capital.com no disponible para obtener balance")
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo balance real: {e}")
        
        # Fallback: usar balance por defecto de configuración
        default_balance = 1000.0  # Balance por defecto
        self.logger.info(f"💰 Usando balance por defecto: ${default_balance:.2f}")
        return default_balance

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
                    'type': 'TRADE_EXECUTED',
                    'timestamp': datetime.now(),
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type,
                    'confidence': signal.confidence_score,
                    'entry_price': trade_result.entry_price,
                    'quantity': trade_result.quantity,
                    'trade_value': trade_result.entry_value,
                    'success': trade_result.success,
                    'message': trade_result.message,
                    'risk_score': risk_assessment.overall_risk_score,
                    'risk_level': risk_assessment.risk_level.value,
                    'position_size': risk_assessment.position_sizing.recommended_size,
                    'stop_loss': getattr(trade_result, 'stop_loss_price', None),
                    'take_profit': getattr(trade_result, 'take_profit_price', None)
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
            self.strategies = {
                "ProfessionalRSI": ProfessionalRSIStrategy(),
                "MultiTimeframe": MultiTimeframeStrategy(),
                "Ensemble": EnsembleStrategy()
            }
            # Inyectar referencia del bot en las estrategias para delegar operaciones comunes
            for s in self.strategies.values():
                if hasattr(s, 'set_trading_bot'):
                    s.set_trading_bot(self)
            self.logger.info(f"✅ {len(self.strategies)} strategies initialized")
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategies: {e}")
            self.strategies = {}
    
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
        if (cache_key in cls._cache and 
            cache_key in cls._cache_timestamps and
            current_time - cls._cache_timestamps[cache_key] < cls._get_cache_ttl()):
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
            key for key, timestamp in cls._cache_timestamps.items()
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
        self.start_time = datetime.now()
        self.stop_event.clear()
        
        # Configurar schedule para análisis periódico
        schedule.clear()
        schedule.every(self.analysis_interval).minutes.do(self._run_analysis_cycle)
        
        # Programar reset diario exacto a la hora configurada (usa hora local del sistema)
        try:
            reset_time_str = f"{DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d}"
            schedule.every().day.at(reset_time_str).do(self._reset_daily_stats_if_needed).tag('daily_reset')
            self.logger.info(f"⏰ Daily reset scheduled at {reset_time_str} ({TIMEZONE})")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not schedule daily reset: {e}")
        
        # Iniciar thread de ejecución (sin análisis inicial inmediato)
        self.analysis_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.analysis_thread.start()
        
        # Iniciar monitoreo de posiciones
        self.position_monitor.start_monitoring()
        
        # Sistema de ajuste TP/SL desactivado (Opción A): no se inicia monitoreo
        # self._start_position_adjustment_monitoring()
        
        # Programar primer análisis para evitar bloqueo
        schedule.every(self.config.get_first_analysis_delay()).minutes.do(self._run_first_analysis).tag('first_analysis')
        
        self.logger.info(f"🚀 Trading Bot started - Analysis every {self.analysis_interval} minutes")
        self.logger.info(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
        self.logger.info(f"🧠 Active strategies: {', '.join(self.strategies.keys())}")
        self.logger.info("🔍 Position monitoring started")
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
        
        # Detener monitoreo de posiciones
        self.position_monitor.stop_monitoring()
        
        # Sistema de ajuste TP/SL desactivado (Opción A): no hay monitoreo que detener
        # if self.position_adjuster:
        #     self.position_adjuster.stop_monitoring()
        
        # Limpiar ThreadPoolExecutor
        if hasattr(self, 'executor') and self.executor:
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
        self.logger.info("🔍 Position monitoring stopped")
        self.logger.info("🎯 TP/SL adjustment monitoring disabled")
        self.logger.info("💾 Cache cleaned up")
    
    def _get_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual del símbolo usando Capital.com con cache"""
        try:
            # Normalizar símbolo para Capital.com (Gold, Silver, etc.)
            capital_symbol = self._normalize_symbol_for_capital(symbol)
            
            # Generar clave de cache para precio basada en símbolo normalizado
            cache_key = self._get_cache_key("current_price", capital_symbol)
            
            # Verificar cache (TTL más corto para precios)
            cached_price = self._get_from_cache(cache_key)
            if cached_price is not None:
                return cached_price
            
            # Usar Capital.com client si está disponible
            if self.capital_client:
                try:
                    market_data = self.capital_client.get_market_data([capital_symbol])
                    if market_data and capital_symbol in market_data:
                        current_price = float(market_data[capital_symbol].get('bid', 0))
                        
                        # Almacenar en cache
                        if current_price > 0:
                            self._store_in_cache(cache_key, current_price)
                        
                        return current_price
                except Exception as e:
                    self.logger.warning(f"⚠️ Capital.com price fetch failed for {capital_symbol}: {e}")
            
            # Fallback: intentar obtener desde estrategias
            try:
                if self.strategies:
                    strategy = next(iter(self.strategies.values()))
                    df = strategy.get_market_data(symbol, "1m", limit=1)
                    fallback_price = float(df['close'].iloc[-1]) if not df.empty else 0.0
                    
                    # Cache del fallback también
                    if fallback_price > 0:
                        cache_key = self._get_cache_key("current_price", symbol)
                        self._store_in_cache(cache_key, fallback_price)
                    
                    return fallback_price
            except:
                pass
            return 0.0
        except Exception as e:
            self.logger.error(f"❌ Error getting current price for {symbol}: {e}")
            return 0.0

    def _normalize_symbol_for_capital(self, symbol: str) -> str:
        """🔄 Normalizar símbolo para Capital.com (ya están en formato correcto)"""
        return symbol

    def _get_capital_symbols(self) -> List[str]:
        """📋 Obtener lista de símbolos disponibles en Capital.com desde configuración centralizada"""
        return GLOBAL_SYMBOLS.copy()

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
            
            # Resetear contador diario si es necesario
            self._reset_daily_stats_if_needed()
            
            # Verificar si podemos hacer más trades hoy
            if self.stats["daily_trades"] >= self.max_daily_trades:
                self.logger.info(f"⏸️ Daily trade limit reached ({self.max_daily_trades})")
                return
            
            # Generar clave de cache para este ciclo
            cache_key = self._get_cache_key("analysis_cycle", tuple(self.symbols), tuple(self.strategies.keys()))
            
            # Verificar cache
            cached_signals = self._get_from_cache(cache_key)
            if cached_signals is not None:
                self.logger.info("⚡ Using cached analysis results")
                all_signals = cached_signals
            else:
                # Analizar en paralelo usando ThreadPoolExecutor
                all_signals = self._analyze_symbols_parallel()
                
                # Almacenar en cache
                self._store_in_cache(cache_key, all_signals)
            
            # Procesar señales con trading
            if all_signals:
                self._process_signals(all_signals)
            else:
                self.logger.info("⚪ No trading signals generated this cycle")
            
            # Actualizar estadísticas en base de datos
            self._update_strategy_stats()
            
            self.logger.info("✅ Optimized analysis cycle completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in analysis cycle: {e}")
    
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
                future = self.executor.submit(self._analyze_single_symbol, symbol, strategy_name, strategy)
                futures.append(future)
            
            # Recopilar resultados
            profile_config = TradingProfiles.get_current_profile()
            timeout = self.config.get_analysis_future_timeout()
            for future in futures:
                try:
                    signal = future.result(timeout=timeout)  # Timeout configurable
                    if signal and signal.signal_type != "HOLD":
                        all_signals.append(signal)
                        self.stats["signals_generated"] += 1
                        self.logger.info(f"📊 Signal: {signal.signal_type} {signal.symbol} ({signal.strategy_name}) - Confidence: {signal.confidence_score}%")
                except Exception as e:
                    self.logger.error(f"❌ Error in parallel analysis: {e}")
        
        except Exception as e:
            self.logger.error(f"❌ Error in parallel execution: {e}")
            # Fallback a análisis secuencial
            all_signals = self._analyze_symbols_sequential()
        
        return all_signals
    
    def _analyze_single_symbol(self, symbol: str, strategy_name: str, strategy) -> Optional[TradingSignal]:
        """
        📈 Analizar un símbolo con una estrategia específica
        """
        try:
            signal = strategy.analyze(symbol)
            if hasattr(signal, 'strategy_name'):
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
                    if signal.signal_type != "HOLD":
                        all_signals.append(signal)
                        self.stats["signals_generated"] += 1
                        self.logger.info(f"📊 Signal: {signal.signal_type} {symbol} ({strategy_name}) - Confidence: {signal.confidence_score}%")
                except Exception as e:
                    self.logger.error(f"❌ Error analyzing {symbol} with {strategy_name}: {e}")
        return all_signals
    
    def _process_signals(self, signals: List[TradingSignal]):
        """
        🎯 Procesar y ejecutar señales de trading
        
        Args:
            signals: Lista de señales generadas
        """

        
        # Filtrar señales por confianza mínima
        high_confidence_signals = [
            signal for signal in signals 
            if signal.confidence_score >= self.min_confidence_threshold
        ]
        
        if not high_confidence_signals:
            self.logger.info(f"📉 No signals above confidence threshold ({self.min_confidence_threshold}%)")
            return
        
        # Ordenar por confianza (mayor primero)
        high_confidence_signals.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Obtener valor actual del portfolio
        portfolio_summary = self.get_portfolio_summary()
        portfolio_value = portfolio_summary.get("total_value", 1000.0)  # Valor por defecto
        
        self.logger.info(f"💼 Current portfolio value: ${portfolio_value:,.2f}")
        
        # Procesar cada señal
        for signal in high_confidence_signals:
            try:
                # Verificar límite diario
                if self.stats["daily_trades"] >= self.max_daily_trades:
                    self.logger.info("⏸️ Daily trade limit reached")
                    break
                
                # Análisis de riesgo
                risk_assessment = self.risk_manager.assess_trade_risk(signal, portfolio_value)
                
                self.logger.info(f"🛡️ Risk assessment for {signal.symbol}:")
                self.logger.info(f"   - Risk Score: {risk_assessment.overall_risk_score:.1f}/100")
                self.logger.info(f"   - Position Size: {risk_assessment.position_sizing.recommended_size:.2f}")
                self.logger.info(f"   - Approved: {risk_assessment.is_approved}")
                self.logger.info(f"   - Risk Level: {risk_assessment.risk_level.value}")
                
                # Ejecutar si está aprobado
                if risk_assessment.is_approved and self.enable_trading:
                    # Ejecutar paper trade siempre
                    trade_result = self.paper_trader.execute_signal(signal)
                    
                    # Ejecutar trade real si está habilitado
                    real_trade_result = None
                    if self.enable_real_trading and self.capital_client:
                        real_trade_result = self._execute_real_trade(signal, risk_assessment)
                    
                    if trade_result.success:
                        self.stats["trades_executed"] += 1
                        self.stats["daily_trades"] += 1
                        
                        # Determinar si fue exitoso basándose en el tipo de trade y PnL real
                        trade_was_profitable = False
                        if signal.signal_type == "SELL":
                            # Para ventas, verificar si hay PnL positivo en el mensaje
                            if "PnL:" in trade_result.message and "$" in trade_result.message:
                                try:
                                    # Extraer PnL del mensaje: "PnL: $X.XX"
                                    pnl_part = trade_result.message.split("PnL: $")[1].split(")")[0]
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
        self.stats["total_pnl"] = portfolio_summary.get("total_pnl", 0)
        
        # Emitir evento de análisis completado
        self._emit_analysis_event(len(high_confidence_signals), self.stats["daily_trades"])
    
    def _reset_daily_stats_if_needed(self):
        """
        📅 Resetear estadísticas diarias a las 11:00 AM hora Chile (America/Santiago)
        """
        try:
            tz = ZoneInfo(TIMEZONE) if ZoneInfo else None
        except Exception:
            tz = None
        now_local = datetime.now(tz) if tz else datetime.now()
        current_day = now_local.date()
        reset_dt = datetime(
            current_day.year,
            current_day.month,
            current_day.day,
            DAILY_RESET_HOUR,
            DAILY_RESET_MINUTE,
            tzinfo=tz
        ) if tz else datetime(
            current_day.year,
            current_day.month,
            current_day.day,
            DAILY_RESET_HOUR,
            DAILY_RESET_MINUTE
        )

        # Realizar reset solo una vez por día cuando la hora local haya alcanzado o superado el reset
        if now_local >= reset_dt and self.stats.get("last_reset_day") != current_day:
            self.stats["daily_trades"] = 0
            self.stats["last_reset_day"] = current_day
            # Resetear circuit breaker al inicio del nuevo periodo diario
            self.consecutive_losses = 0
            self.circuit_breaker_active = False
            self.circuit_breaker_activated_at = None
            self.logger.info(f"📅 Daily stats reset at {DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d} ({TIMEZONE}) on {current_day} - Circuit breaker reset")
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
        next_analysis = datetime.now()
        
        if self.is_running and self.start_time:
            uptime_delta = datetime.now() - self.start_time
            hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            next_analysis = datetime.now() + timedelta(minutes=self.analysis_interval)
        
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
            last_analysis_time=datetime.now() - timedelta(minutes=self.analysis_interval) if self.is_running else datetime.now(),
            next_analysis_time=next_analysis
        )
        
        return status
    
    def get_portfolio_summary(self) -> Dict:
        """
        📊 Obtener resumen del portfolio directamente de Capital.com
        
        Returns:
            Dict: Resumen del portfolio
        """
        try:
            # Obtener balance disponible de Capital.com
            balance_info = self.capital_client.get_available_balance()
            if isinstance(balance_info, dict):
                available_balance = float(balance_info.get('available', 0.0))
            elif isinstance(balance_info, (str, int, float)):
                available_balance = float(balance_info)
            else:
                available_balance = 0.0
            
            # Obtener posiciones abiertas de Capital.com
            positions = self.capital_client.get_positions()
            
            # Calcular valor total del portfolio
            total_value = available_balance
            total_pnl = 0.0
            
            if positions:
                for position in positions:
                    if position.get('size', 0) != 0:  # Solo posiciones activas
                        current_value = float(position.get('size', 0)) * float(position.get('level', 0))
                        total_value += abs(current_value)
                        total_pnl += float(position.get('pnl', 0))
            
            return {
                'total_value': total_value,
                'available_balance': available_balance,
                'total_pnl': total_pnl,
                'open_positions': len(positions) if positions else 0,
                'source': 'capital_com'
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo portfolio de Capital.com: {e}")
            # Fallback: usar paper trader si hay error
            return self.paper_trader.get_portfolio_summary()
    
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
                "next_analysis": status.next_analysis_time.isoformat(),
                "enable_trading": self.enable_trading
            },
            "trading_stats": {
                "total_signals_generated": status.total_signals_generated,
                "total_trades_executed": status.total_trades_executed,
                "successful_trades": status.successful_trades,
                "win_rate": (status.successful_trades / max(1, status.total_trades_executed)) * 100,
                "daily_trades": self.stats["daily_trades"],
                "daily_limit": self.max_daily_trades
            },
            "portfolio": {
                "current_value": status.current_portfolio_value,
                "total_pnl": status.total_pnl,
                "total_return_percentage": ((status.current_portfolio_value - self.config.DEFAULT_PORTFOLIO_VALUE) / self.config.DEFAULT_PORTFOLIO_VALUE) * 100,
                "assets": portfolio_summary.get("assets", [])
            },
            "strategies": {
                "active": status.active_strategies,
                "symbols_monitored": self.symbols,
                "min_confidence_threshold": self.min_confidence_threshold
            },
            "risk_management": risk_report,
            "open_positions": open_positions,
            "position_monitor": {
                "status": self.position_monitor.get_monitoring_status(),
                "active_positions": len(open_positions)
            },
            "configuration": {
                "analysis_interval_minutes": self.analysis_interval,
                "max_daily_trades": self.max_daily_trades,
                "min_confidence_threshold": self.min_confidence_threshold,
                "enable_trading": self.enable_trading
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_configuration(self) -> Dict:
        """
        📋 Obtener configuración actual del bot
        """
        try:
            active_strategies = [name for name, strategy in self.strategies.items()]
            
            config = {
                # Configuraciones básicas
                'analysis_interval_minutes': self.analysis_interval,
                'active_strategies': active_strategies,
                'is_running': self.is_running,
                'total_strategies': len(self.strategies),
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
                'max_daily_trades': self.max_daily_trades,
                'min_confidence_threshold': self.min_confidence_threshold,
                'enable_trading': self.enable_trading,
                'symbols': self.symbols,
                
                # Configuraciones de posiciones
                'max_concurrent_positions': getattr(self, 'max_concurrent_positions', None),
                
                # Configuraciones de timeframes
                'primary_timeframe': getattr(self, 'primary_timeframe', None),
                'confirmation_timeframe': getattr(self, 'confirmation_timeframe', None),
                'trend_timeframe': getattr(self, 'trend_timeframe', None),
                
                # Configuraciones de trading real
                'enable_real_trading': getattr(self, 'enable_real_trading', False),
                'real_trading_size_multiplier': getattr(self, 'real_trading_size_multiplier', 0.1),
            }
            
            # Agregar configuraciones del paper trader si está disponible
            if hasattr(self, 'paper_trader') and self.paper_trader:
                if hasattr(self.paper_trader, 'get_configuration'):
                    paper_config = self.paper_trader.get_configuration()
                    config.update({
                        'max_position_size': paper_config.get('max_position_size'),
                        'max_total_exposure': paper_config.get('max_total_exposure'),
                        'min_trade_value': paper_config.get('min_trade_value'),
                    })
                else:
                    # Valores por defecto si no hay método get_configuration
                    config.update({
                        'max_position_size': getattr(self.paper_trader, 'max_position_size', None),
                        'max_total_exposure': getattr(self.paper_trader, 'max_total_exposure', None),
                        'min_trade_value': getattr(self.paper_trader, 'min_trade_value', None),
                    })
            
            # Agregar configuraciones del risk manager si está disponible
            if hasattr(self, 'risk_manager') and self.risk_manager:
                if hasattr(self.risk_manager, 'get_configuration'):
                    risk_config = self.risk_manager.get_configuration()
                    config.update({
                        'max_risk_per_trade': risk_config.get('max_risk_per_trade'),
                        'max_daily_risk': risk_config.get('max_daily_risk'),
                        'max_drawdown_threshold': risk_config.get('max_drawdown_threshold'),
                        'correlation_threshold': risk_config.get('correlation_threshold'),
                    })
                else:
                    # Valores por defecto si no hay método get_configuration
                    config.update({
                        'max_risk_per_trade': getattr(self.risk_manager, 'max_risk_per_trade', None),
                        'max_daily_risk': getattr(self.risk_manager, 'max_daily_risk', None),
                        'max_drawdown_threshold': getattr(self.risk_manager, 'max_drawdown_threshold', None),
                        'correlation_threshold': getattr(self.risk_manager, 'correlation_threshold', None),
                    })
            
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
                self.logger.info(f"⚙️ Analysis interval updated to {self.analysis_interval} minutes")
            
            if "max_daily_trades" in config:
                self.max_daily_trades = max(1, config["max_daily_trades"])
                self.logger.info(f"⚙️ Max daily trades updated to {self.max_daily_trades}")
            
            if "min_confidence_threshold" in config:
                self.min_confidence_threshold = max(0, min(100, config["min_confidence_threshold"]))
                self.logger.info(f"⚙️ Min confidence threshold updated to {self.min_confidence_threshold}%")
            
            if "enable_trading" in config:
                self.enable_trading = bool(config["enable_trading"])
                status = "enabled" if self.enable_trading else "disabled"
                self.logger.info(f"⚙️ Trading execution {status}")
            
            if "symbols" in config and isinstance(config["symbols"], list):
                self.symbols = config["symbols"]
                self.logger.info(f"⚙️ Symbols updated: {', '.join(self.symbols)}")
            
            # Configuraciones de posiciones
            if "max_concurrent_positions" in config:
                self.max_concurrent_positions = max(1, config["max_concurrent_positions"])
                self.logger.info(f"⚙️ Max concurrent positions updated to {self.max_concurrent_positions}")
            
            # Configuraciones de timeframes
            if "primary_timeframe" in config:
                self.primary_timeframe = config["primary_timeframe"]
                self.logger.info(f"⚙️ Primary timeframe updated to {self.primary_timeframe}")
            
            if "confirmation_timeframe" in config:
                self.confirmation_timeframe = config["confirmation_timeframe"]
                self.logger.info(f"⚙️ Confirmation timeframe updated to {self.confirmation_timeframe}")
            
            if "trend_timeframe" in config:
                self.trend_timeframe = config["trend_timeframe"]
                self.logger.info(f"⚙️ Trend timeframe updated to {self.trend_timeframe}")
            
            # Configuraciones de trading real
            if "enable_real_trading" in config:
                self.enable_real_trading = bool(config["enable_real_trading"])
                status = "enabled" if self.enable_real_trading else "disabled"
                self.logger.info(f"⚙️ Real trading {status}")
            
            if "real_trading_size_multiplier" in config:
                self.real_trading_size_multiplier = max(0.01, min(1.0, config["real_trading_size_multiplier"]))
                self.logger.info(f"⚙️ Real trading size multiplier updated to {self.real_trading_size_multiplier}")
            
            # Configuraciones del paper trader (si están disponibles)
            if hasattr(self, 'paper_trader') and self.paper_trader:
                paper_config = {}
                if "max_position_size" in config:
                    paper_config["max_position_size"] = max(0.01, min(1.0, config["max_position_size"]))
                if "max_total_exposure" in config:
                    paper_config["max_total_exposure"] = max(0.01, min(1.0, config["max_total_exposure"]))
                if "min_trade_value" in config:
                    paper_config["min_trade_value"] = max(1.0, config["min_trade_value"])
                
                if paper_config:
                    # Actualizar configuración del paper trader si tiene método de actualización
                    if hasattr(self.paper_trader, 'update_configuration'):
                        self.paper_trader.update_configuration(paper_config)
                        self.logger.info(f"⚙️ Paper trader configuration updated: {paper_config}")
            
            # Configuraciones del risk manager (si están disponibles)
            if hasattr(self, 'risk_manager') and self.risk_manager:
                risk_config = {}
                if "max_risk_per_trade" in config:
                    risk_config["max_risk_per_trade"] = max(0.1, min(5.0, config["max_risk_per_trade"]))
                if "max_daily_risk" in config:
                    risk_config["max_daily_risk"] = max(0.5, min(10.0, config["max_daily_risk"]))
                if "max_drawdown_threshold" in config:
                    risk_config["max_drawdown_threshold"] = max(0.05, min(0.5, config["max_drawdown_threshold"]))
                if "correlation_threshold" in config:
                    risk_config["correlation_threshold"] = max(0.1, min(1.0, config["correlation_threshold"]))
                
                if risk_config:
                    # Actualizar configuración del risk manager si tiene método de actualización
                    if hasattr(self.risk_manager, 'update_configuration'):
                        self.risk_manager.update_configuration(risk_config)
                        self.logger.info(f"⚙️ Risk manager configuration updated: {risk_config}")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating configuration: {e}")
    
    def _run_first_analysis(self):
        """
        🔄 Ejecutar primer análisis y eliminar del schedule
        """
        try:
            self.logger.info("🔄 Running first analysis...")
            self._run_analysis_cycle()
            # Eliminar este job del schedule después de ejecutarlo
            schedule.clear('first_analysis')
            self.logger.info("✅ First analysis completed and removed from schedule")
        except Exception as e:
            self.logger.error(f"❌ Error in first analysis: {e}")
            schedule.clear('first_analysis')
    
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
                self.logger.warning(f"🚨 Closing {len(open_positions)} open positions...")
                
                # Aquí podrías implementar lógica para cerrar posiciones automáticamente
                # Por ahora solo loggeamos
                for position in open_positions:
                    self.logger.warning(f"   📊 Open position: {position['symbol']} - ${position['entry_value']:.2f}")
            
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
    
    def _start_position_adjustment_monitoring(self):
        """🎯 Iniciar monitoreo de ajustes de posiciones TP/SL"""
        try:
            # Configurar callback para eventos de ajuste
            self.position_adjuster.set_adjustment_callback(self._on_position_adjusted)
            
            # Iniciar monitoreo en hilo separado con wrapper para async
            self.adjustment_thread = threading.Thread(
                target=self._run_position_monitoring_async,
                daemon=True
            )
            self.adjustment_thread.start()
            
            self.logger.info("🎯 Position adjustment monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting position adjustment monitoring: {e}")
    
    def _run_position_monitoring_async(self):
        """🔄 Wrapper para ejecutar el monitoreo async en un hilo"""
        try:
            # Crear un nuevo loop de eventos para este hilo
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Ejecutar el monitoreo async
            loop.run_until_complete(self.position_adjuster.start_monitoring())
            
        except Exception as e:
            self.logger.error(f"❌ Error in position monitoring thread: {e}")
        finally:
            try:
                loop.close()
            except:
                pass
    
    def _on_position_adjusted(self, adjustment_data: Dict):
        """📢 Callback cuando se ajusta una posición"""
        try:
            # Emitir evento de ajuste
            self._emit_adjustment_event(adjustment_data)
            
            # Log del ajuste
            symbol = adjustment_data.get('symbol', 'Unknown')
            old_tp = adjustment_data.get('old_tp', 0)
            old_sl = adjustment_data.get('old_sl', 0)
            new_tp = adjustment_data.get('new_tp', 0)
            new_sl = adjustment_data.get('new_sl', 0)
            
            self.logger.info(f"🎯 Position adjusted for {symbol}:")
            self.logger.info(f"   TP: {old_tp:.4f} → {new_tp:.4f}")
            self.logger.info(f"   SL: {old_sl:.4f} → {new_sl:.4f}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in position adjustment callback: {e}")
    
    def _emit_trade_event(self, signal: TradingSignal, trade_result: TradeResult, risk_assessment):
        """📢 Emitir evento de trade ejecutado"""
        try:
            event = {
                'type': 'trade_executed',
                'timestamp': datetime.now(),
                'symbol': signal.symbol,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence_score,
                'entry_price': trade_result.entry_price,
                'quantity': trade_result.quantity,
                'tp_price': getattr(signal, 'take_profit', None),
                'sl_price': getattr(signal, 'stop_loss', None),
                'risk_score': risk_assessment.overall_risk_score,
                'position_size': risk_assessment.position_sizing.recommended_size,
                'success': trade_result.success,
                'message': trade_result.message
            }
            
            self.event_queue.put(event, block=False)
            
        except queue.Full:
            self.logger.warning("⚠️ Event queue full, dropping trade event")
        except Exception as e:
            self.logger.error(f"❌ Error emitting trade event: {e}")
    
    def _emit_adjustment_event(self, adjustment_data: Dict):
        """📢 Emitir evento de ajuste de posición"""
        try:
            event = {
                'type': 'position_adjustment',
                'timestamp': datetime.now(),
                **adjustment_data
            }
            
            self.event_queue.put(event, block=False)
            
        except queue.Full:
            self.logger.warning("⚠️ Event queue full, dropping adjustment event")
        except Exception as e:
            self.logger.error(f"❌ Error emitting adjustment event: {e}")
    
    def _emit_analysis_event(self, signals_count: int, daily_trades: int):
        """📢 Emitir evento de análisis completado"""
        try:
            event = {
                'type': 'analysis_completed',
                'timestamp': datetime.now(),
                'signals_generated': signals_count,
                'daily_trades': daily_trades,
                'max_daily_trades': self.max_daily_trades,
                'portfolio_value': self.stats.get('total_pnl', 0)
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
            symbol: Símbolo original (ej: ETHUSD, ETH)
            
        Returns:
            Símbolo normalizado para Capital.com
        """
        # Mapeo de símbolos comunes
        symbol_mapping = {
            "ETHUSD": "ETHUSD",
            "ETH": "ETHUSD",
            "BTCUSD": "BTCUSD", 
            "BTC": "BTCUSD",
            "ADAUSD": "ADAUSD",
            "ADA": "ADAUSD",
            "SOLUSD": "SOLUSD",
            "SOL": "SOLUSD",
            "DOTUSD": "DOTUSD",
            "DOT": "DOTUSD"
        }
        
        # Convertir a mayúsculas y buscar en el mapeo
        normalized = symbol_mapping.get(symbol.upper(), symbol.upper())
        
        # Si no está en el mapeo y no termina en USD, agregar USD
        if normalized not in symbol_mapping.values() and not normalized.endswith("USD"):
            normalized = f"{normalized}USD"
            
        return normalized
    
    def _execute_real_trade(self, signal: TradingSignal, risk_assessment) -> Dict[str, Any]:
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
                    "error": f"Failed to get account balance: {balance_result.get('error')}"
                }
            
            available_balance = balance_result.get("available", 0)
            currency_symbol = balance_result.get("symbol", "$")
            
            self.logger.info(f"💰 Available balance: {currency_symbol}{available_balance}")
            
            # 2. Convertir símbolo al formato de Capital.com
            capital_symbol = self._normalize_symbol_for_capital(signal.symbol)
            
            # 3. Usar el tamaño de posición calculado por el risk manager (que ya considera apalancamiento)
            current_price = signal.price if hasattr(signal, 'price') else signal.current_price
            
            # El risk_assessment ya calculó el tamaño óptimo en UNIDADES del activo
            # recommended_size ya incluye el apalancamiento aplicado
            real_size = risk_assessment.position_sizing.recommended_size
            leverage_used = risk_assessment.position_sizing.leverage_used
            position_value_usd = risk_assessment.position_sizing.position_value  # Valor total en USD
            
            # 4. Redondear a 4 decimales para crypto (más precisión)
            real_size = round(real_size, 4)
            
            # Calcular valores para mostrar correctamente
            total_position_value = real_size * current_price  # Valor total de la posición
            required_margin = total_position_value / leverage_used  # Margen requerido
            
            # Log detallado del cálculo
            self.logger.info(f"💰 Cálculo de posición real:")
            self.logger.info(f"   Balance disponible: {currency_symbol}{available_balance:.2f}")
            self.logger.info(f"   Tamaño recomendado: {real_size:.4f} unidades")
            self.logger.info(f"   Apalancamiento usado: {leverage_used}x")
            self.logger.info(f"   Precio actual {capital_symbol}: {currency_symbol}{current_price:.2f}")
            self.logger.info(f"   Valor total posición: {currency_symbol}{total_position_value:.2f}")
            self.logger.info(f"   Margen requerido: {currency_symbol}{required_margin:.2f}")
            self.logger.info(f"   Verificación: {real_size:.4f} * {currency_symbol}{current_price:.2f} = {currency_symbol}{total_position_value:.2f}")
            
            # 5. Verificar si tenemos suficiente balance para el trade
            # Los valores ya están calculados arriba: total_position_value y required_margin
            
            if available_balance < required_margin:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Available: {currency_symbol}{available_balance:.2f}, Required margin: {currency_symbol}{required_margin:.2f}, Position value: {currency_symbol}{total_position_value:.2f}"
                }
            
            # Verificar tamaño mínimo (Capital.com generalmente requiere mínimo 0.01)
            if real_size < 0.01:
                return {
                    "success": False,
                    "error": f"Position size too small: {real_size} (minimum: 0.01)"
                }
            
            # 6. Obtener valores de TP y SL de la señal
            stop_loss = None
            take_profit = None
            
            if hasattr(signal, 'stop_loss_price') and signal.stop_loss_price > 0:
                stop_loss = signal.stop_loss_price
                self.logger.info(f"🛡️ Stop Loss: ${stop_loss:.4f}")
            
            if hasattr(signal, 'take_profit_price') and signal.take_profit_price > 0:
                take_profit = signal.take_profit_price
                self.logger.info(f"🎯 Take Profit: ${take_profit:.4f}")
            
            # Si no hay TP/SL en la señal, usar valores del risk assessment
            if stop_loss is None and hasattr(risk_assessment, 'dynamic_stop_loss'):
                stop_loss = risk_assessment.dynamic_stop_loss.stop_loss_price
                self.logger.info(f"🛡️ Stop Loss (from risk assessment): ${stop_loss:.4f}")
                
            if take_profit is None and hasattr(risk_assessment, 'dynamic_take_profit'):
                take_profit = risk_assessment.dynamic_take_profit.take_profit_price
                self.logger.info(f"🎯 Take Profit (from risk assessment): ${take_profit:.4f}")
            
            self.logger.info(f"🔴 Executing REAL trade: {signal.signal_type} {capital_symbol} size={real_size}")
            self.logger.info(f"🔴 Stop Loss: {stop_loss}, Take Profit: {take_profit}")
            self.logger.info(f"🔴 Capital.com API URL: {self.capital_client.base_url}")
            
            # Ejecutar orden según el tipo de señal
            if signal.signal_type == "BUY":
                self.logger.info(f"🔴 Enviando orden BUY a Capital.com...")
                result = self.capital_client.buy_market_order(
                    epic=capital_symbol,
                    size=real_size,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                self.logger.info(f"🔴 Respuesta de Capital.com BUY: {result}")
            elif signal.signal_type == "SELL":
                # Para SELL, primero verificar si tenemos posiciones abiertas
                self.logger.info(f"🔴 Verificando posiciones existentes para SELL...")
                positions_result = self.capital_client.get_positions()
                if not positions_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Failed to get positions: {positions_result.get('error')}"
                    }
                
                # Buscar posición abierta para este símbolo
                open_position = None
                for position in positions_result.get("positions", []):
                    if position.get("market", {}).get("epic") == capital_symbol:
                        open_position = position
                        break
                
                if open_position:
                    # Cerrar posición existente
                    deal_id = open_position.get("position", {}).get("dealId")
                    position_size = abs(float(open_position.get("position", {}).get("size", 0)))
                    close_size = min(real_size, position_size)
                    
                    self.logger.info(f"🔴 Cerrando posición existente - Deal ID: {deal_id}, Size: {close_size}")
                    result = self.capital_client.close_position(
                        deal_id=deal_id,
                        direction="SELL",
                        size=close_size
                    )
                    self.logger.info(f"🔴 Respuesta de Capital.com CLOSE: {result}")
                else:
                    # Abrir nueva posición de venta
                    self.logger.info(f"🔴 Enviando orden SELL a Capital.com...")
                    result = self.capital_client.sell_market_order(
                        epic=capital_symbol,
                        size=real_size,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
                    self.logger.info(f"🔴 Respuesta de Capital.com SELL: {result}")
            else:
                return {
                    "success": False,
                    "error": f"Unknown signal type: {signal.signal_type}"
                }
            
            # Log del resultado
            if result.get("success"):
                self.logger.info(f"🔴 Real trade SUCCESS: {signal.signal_type} {capital_symbol} - Deal ID: {result.get('deal_id')}")
            else:
                self.logger.error(f"🔴 Real trade FAILED: {signal.signal_type} {capital_symbol} - Error: {result.get('error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Exception executing real trade: {str(e)}"
            self.logger.error(f"🔴 {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
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
trading_bot = TradingBot()
"""
🤖 Universal Trading Analyzer - Trading Bot
Bot principal que ejecuta estrategias automáticamente 24/7
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading
import json

# Importar todos nuestros componentes
from .config import TradingBotConfig
from .enhanced_strategies import TradingSignal, ProfessionalRSIStrategy, MultiTimeframeStrategy, EnsembleStrategy
from .paper_trader import PaperTrader, TradeResult
from .enhanced_risk_manager import EnhancedRiskManager, EnhancedRiskAssessment
from .position_monitor import PositionMonitor
from database.database import db_manager
from database.models import Strategy as DBStrategy

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
    🤖 Trading Bot Principal
    
    Características:
    - Ejecuta múltiples estrategias automáticamente
    - Análisis cada X minutos (configurable)
    - Risk management integrado
    - Paper trading seguro
    - Logging completo
    - Dashboard en tiempo real
    """
    
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
        
        # Componentes principales
        self.paper_trader = PaperTrader()
        self.risk_manager = EnhancedRiskManager()
        
        # Sistema de monitoreo de posiciones
        self.position_monitor = PositionMonitor(
            price_fetcher=self._get_current_price,
            paper_trader=self.paper_trader
        )
        
        # Estrategias disponibles (Enhanced)
        self.strategies = {}
        self._initialize_strategies()
        
        # Símbolos a analizar desde configuración centralizada
        self.symbols = self.config.SYMBOLS
        
        # Configuración de trading profesional desde configuración centralizada
        self.min_confidence_threshold = self.config.get_min_confidence_threshold()
        self.max_daily_trades = self.config.get_max_daily_trades()
        self.max_concurrent_positions = self.config.get_max_concurrent_positions()
        self.enable_trading = True  # Activar/desactivar ejecución de trades
        
        # Configuración de timeframes profesional desde configuración centralizada
        self.primary_timeframe = self.config.get_primary_timeframe()
        self.confirmation_timeframe = self.config.get_confirmation_timeframe()
        self.trend_timeframe = self.config.get_trend_timeframe()
        
        # Estadísticas
        self.stats = {
            "signals_generated": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "daily_trades": 0,
            "last_reset_date": datetime.now().date()
        }
        
        # Circuit breaker avanzado
        self.consecutive_losses = 0
        self.circuit_breaker_active = False
        self.circuit_breaker_activated_at = None
        self.max_consecutive_losses = self.config.get_max_consecutive_losses()
        self.circuit_breaker_cooldown_hours = self.config.get_circuit_breaker_cooldown_hours()
        
        # Nuevas funcionalidades del circuit breaker
        self.max_drawdown_threshold = 0.15  # 15% drawdown máximo
        self.current_drawdown = 0.0
        self.peak_portfolio_value = 0.0
        self.gradual_reactivation_enabled = True
        self.reactivation_phase = 0  # 0: inactivo, 1-3: fases de reactivación
        self.reactivation_trades_allowed = 0
        self.reactivation_success_count = 0
        self.circuit_breaker_trigger_reason = ""
        
        # Thread para ejecución
        self.analysis_thread = None
        self.stop_event = threading.Event()
        
        self.logger.info("🤖 Trading Bot initialized with Position Monitor")
    
    def _initialize_strategies(self):
        """🔧 Inicializar estrategias de trading"""
        try:
            self.strategies = {
                "ProfessionalRSI": ProfessionalRSIStrategy(),
                "MultiTimeframe": MultiTimeframeStrategy(),
                "Ensemble": EnsembleStrategy()
            }
            self.logger.info(f"✅ {len(self.strategies)} strategies initialized")
        except Exception as e:
            self.logger.error(f"❌ Error initializing strategies: {e}")
            self.strategies = {}
    
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
        
        # Iniciar thread de ejecución (sin análisis inicial inmediato)
        self.analysis_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.analysis_thread.start()
        
        # Iniciar monitoreo de posiciones
        self.position_monitor.start_monitoring()
        
        # Programar primer análisis para evitar bloqueo
        schedule.every(self.config.get_first_analysis_delay()).seconds.do(self._run_first_analysis).tag('first_analysis')
        
        self.logger.info(f"🚀 Trading Bot started - Analysis every {self.analysis_interval} minutes")
        self.logger.info(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
        self.logger.info(f"🧠 Active strategies: {', '.join(self.strategies.keys())}")
        self.logger.info("🔍 Position monitoring started")
    
    def stop(self):
        """
        🛑 Detener el trading bot
        """
        if not self.is_running:
            self.logger.warning("⚠️ Bot is not running")
            return
        
        self.is_running = False
        self.stop_event.set()
        schedule.clear()
        
        # Detener monitoreo de posiciones
        self.position_monitor.stop_monitoring()
        
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=10)
        
        self.logger.info("🛑 Trading Bot stopped")
        self.logger.info("🔍 Position monitoring stopped")
    
    def _get_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual del símbolo para el position monitor"""
        try:
            import ccxt
            exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
            ticker = exchange.fetch_ticker(symbol)
            return float(ticker['last']) if ticker['last'] else 0.0
        except Exception as e:
            self.logger.error(f"❌ Error getting current price for {symbol}: {e}")
            # Fallback: intentar obtener desde estrategias
            try:
                if self.strategies:
                    strategy = next(iter(self.strategies.values()))
                    df = strategy.get_market_data(symbol, "1m", limit=1)
                    return float(df['close'].iloc[-1]) if not df.empty else 0.0
            except:
                pass
            return 0.0
    
    def _run_scheduler(self):
        """
        ⏰ Ejecutar scheduler en loop
        """
        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"❌ Error in scheduler: {e}")
                time.sleep(5)
    
    def _run_analysis_cycle(self):
        """
        🔄 Ejecutar un ciclo completo de análisis
        """
        try:
            self.logger.info("🔄 Starting analysis cycle...")
            
            # Resetear contador diario si es necesario
            self._reset_daily_stats_if_needed()
            
            # Verificar si podemos hacer más trades hoy
            if self.stats["daily_trades"] >= self.max_daily_trades:
                self.logger.info(f"⏸️ Daily trade limit reached ({self.max_daily_trades})")
                return
            
            # Analizar cada símbolo con cada estrategia
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
            
            # Procesar señales con trading
            if all_signals:
                self._process_signals(all_signals)
            else:
                self.logger.info("⚪ No trading signals generated this cycle")
            
            # Actualizar estadísticas en base de datos
            self._update_strategy_stats()
            
            self.logger.info("✅ Analysis cycle completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in analysis cycle: {e}")
    
    def _process_signals(self, signals: List[TradingSignal]):
        """
        🎯 Procesar y ejecutar señales de trading
        
        Args:
            signals: Lista de señales generadas
        """
        # Verificar circuit breaker avanzado
        if not self._check_circuit_breaker():
            self.logger.warning("🚨 Circuit breaker active - skipping signal processing")
            return
        
        # Verificar límites de reactivación gradual
        if not self._can_trade_during_reactivation():
            self.logger.info("🟡 Reactivation limits reached - skipping signal processing")
            return
        
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
        portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
        portfolio_value = portfolio_summary.get("total_value", self.config.DEFAULT_PORTFOLIO_VALUE)
        
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
                    trade_result = self.paper_trader.execute_signal(signal)
                    
                    if trade_result.success:
                        self.stats["trades_executed"] += 1
                        self.stats["daily_trades"] += 1
                        
                        # Determinar si fue exitoso y actualizar circuit breaker
                        trade_was_profitable = "profit" in trade_result.message.lower() or trade_result.entry_value > 0
                        if trade_was_profitable:
                            self.stats["successful_trades"] += 1
                        
                        # Actualizar tracking de pérdidas consecutivas
                        self._update_consecutive_losses(trade_was_profitable)
                        
                        self.logger.info(f"✅ Trade executed: {trade_result.message}")
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
    
    def _reset_daily_stats_if_needed(self):
        """
        📅 Resetear estadísticas diarias si es un nuevo día
        """
        today = datetime.now().date()
        if today != self.stats["last_reset_date"]:
            self.stats["daily_trades"] = 0
            self.stats["last_reset_date"] = today
            # Resetear circuit breaker al inicio de un nuevo día
            self.consecutive_losses = 0
            self.circuit_breaker_active = False
            self.circuit_breaker_activated_at = None
            self.logger.info(f"📅 Daily stats reset for {today} - Circuit breaker reset")
    
    def _check_circuit_breaker(self) -> bool:
        """
        🚨 Verificar estado del circuit breaker avanzado
        
        Returns:
            bool: True si el trading está permitido, False si está bloqueado
        """
        # Verificar drawdown antes que pérdidas consecutivas
        self._check_drawdown_circuit_breaker()
        
        # Si no está activo, permitir trading
        if not self.circuit_breaker_active:
            return True
        
        # Verificar si ha pasado el tiempo de cooldown
        if self.circuit_breaker_activated_at:
            time_since_activation = datetime.now() - self.circuit_breaker_activated_at
            cooldown_duration = timedelta(hours=self.circuit_breaker_cooldown_hours)
            
            if time_since_activation >= cooldown_duration:
                # Reactivación gradual
                if self.gradual_reactivation_enabled:
                    self._initiate_gradual_reactivation()
                else:
                    # Desactivar circuit breaker después del cooldown
                    self.circuit_breaker_active = False
                    self.circuit_breaker_activated_at = None
                    self.consecutive_losses = 0
                    self.logger.info(f"🟢 Circuit breaker deactivated after {self.circuit_breaker_cooldown_hours}h cooldown")
                return True
            else:
                remaining_time = cooldown_duration - time_since_activation
                remaining_hours = remaining_time.total_seconds() / 3600
                self.logger.info(f"🔴 Circuit breaker active - {remaining_hours:.1f}h remaining")
                return False
        
        return False
    
    def _update_consecutive_losses(self, trade_was_profitable: bool):
        """
        📊 Actualizar contador de pérdidas consecutivas y reactivación gradual
        
        Args:
            trade_was_profitable: True si el trade fue rentable, False si fue pérdida
        """
        if trade_was_profitable:
            # Resetear contador si el trade fue rentable
            self.consecutive_losses = 0
            self.logger.info(f"✅ Profitable trade - consecutive losses reset to 0")
            
            # Actualizar progreso de reactivación gradual
            self._update_reactivation_success(True)
            
        else:
            # Incrementar contador de pérdidas
            self.consecutive_losses += 1
            self.logger.warning(f"❌ Loss #{self.consecutive_losses}/{self.max_consecutive_losses}")
            
            # Actualizar progreso de reactivación gradual (pérdida)
            self._update_reactivation_success(False)
            
            # Activar circuit breaker si se alcanza el límite
            if self.consecutive_losses >= self.max_consecutive_losses and not self.circuit_breaker_active:
                self.circuit_breaker_active = True
                self.circuit_breaker_activated_at = datetime.now()
                self.circuit_breaker_trigger_reason = f"CONSECUTIVE_LOSSES_{self.consecutive_losses}"
                self.logger.error(f"🚨 CIRCUIT BREAKER ACTIVATED! {self.consecutive_losses} consecutive losses")
                self.logger.error(f"🛑 Trading suspended for {self.circuit_breaker_cooldown_hours} hours")
    
    def _get_remaining_cooldown_hours(self) -> float:
        """
        ⏰ Calcular horas restantes de cooldown del circuit breaker
        
        Returns:
            float: Horas restantes de cooldown (0 si no está activo)
        """
        if not self.circuit_breaker_active or not self.circuit_breaker_activated_at:
            return 0.0
        
        time_since_activation = datetime.now() - self.circuit_breaker_activated_at
        cooldown_duration = timedelta(hours=self.circuit_breaker_cooldown_hours)
        remaining_time = cooldown_duration - time_since_activation
        
        if remaining_time.total_seconds() <= 0:
            return 0.0
        
        return remaining_time.total_seconds() / 3600
    
    def _check_drawdown_circuit_breaker(self):
        """
        📉 Verificar circuit breaker por drawdown del portafolio
        """
        try:
            portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
            current_value = portfolio_summary.get("total_value", 0)
            
            # Actualizar pico del portafolio
            if current_value > self.peak_portfolio_value:
                self.peak_portfolio_value = current_value
                self.current_drawdown = 0.0
            elif self.peak_portfolio_value > 0:
                # Calcular drawdown actual
                self.current_drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value
                
                # Activar circuit breaker si el drawdown excede el umbral
                if (self.current_drawdown >= self.max_drawdown_threshold and 
                    not self.circuit_breaker_active):
                    
                    self.circuit_breaker_active = True
                    self.circuit_breaker_activated_at = datetime.now()
                    self.circuit_breaker_trigger_reason = f"DRAWDOWN_{self.current_drawdown:.1%}"
                    
                    self.logger.error(f"🚨 CIRCUIT BREAKER ACTIVATED BY DRAWDOWN!")
                    self.logger.error(f"📉 Current drawdown: {self.current_drawdown:.1%} (threshold: {self.max_drawdown_threshold:.1%})")
                    self.logger.error(f"💰 Peak value: ${self.peak_portfolio_value:,.2f}, Current: ${current_value:,.2f}")
                    
        except Exception as e:
            self.logger.error(f"Error checking drawdown circuit breaker: {e}")
    
    def _initiate_gradual_reactivation(self):
        """
        🔄 Iniciar reactivación gradual del trading
        """
        try:
            if self.reactivation_phase == 0:
                # Fase 1: Solo 1 trade de prueba
                self.reactivation_phase = 1
                self.reactivation_trades_allowed = 1
                self.reactivation_success_count = 0
                self.logger.info(f"🟡 Iniciando reactivación gradual - Fase 1: {self.reactivation_trades_allowed} trade permitido")
                
            elif self.reactivation_phase == 1 and self.reactivation_success_count >= 1:
                # Fase 2: Hasta 3 trades
                self.reactivation_phase = 2
                self.reactivation_trades_allowed = 3
                self.reactivation_success_count = 0
                self.logger.info(f"🟡 Reactivación gradual - Fase 2: {self.reactivation_trades_allowed} trades permitidos")
                
            elif self.reactivation_phase == 2 and self.reactivation_success_count >= 2:
                # Fase 3: Trading normal pero con límites reducidos
                self.reactivation_phase = 3
                self.reactivation_trades_allowed = 5
                self.reactivation_success_count = 0
                self.logger.info(f"🟡 Reactivación gradual - Fase 3: {self.reactivation_trades_allowed} trades permitidos")
                
            elif self.reactivation_phase == 3 and self.reactivation_success_count >= 3:
                # Reactivación completa
                self._complete_reactivation()
                
        except Exception as e:
            self.logger.error(f"Error in gradual reactivation: {e}")
    
    def _complete_reactivation(self):
        """
        ✅ Completar reactivación del circuit breaker
        """
        self.circuit_breaker_active = False
        self.circuit_breaker_activated_at = None
        self.consecutive_losses = 0
        self.reactivation_phase = 0
        self.reactivation_trades_allowed = 0
        self.reactivation_success_count = 0
        self.circuit_breaker_trigger_reason = ""
        
        self.logger.info(f"🟢 Circuit breaker completamente reactivado - Trading normal restaurado")
    
    def _can_trade_during_reactivation(self) -> bool:
        """
        🔍 Verificar si se puede hacer trading durante la reactivación gradual
        """
        if self.reactivation_phase == 0:
            return True  # No hay reactivación en curso
            
        # Contar trades ejecutados en la fase actual
        today = datetime.now().date()
        trades_today = self.stats.get("daily_trades", 0)
        
        if trades_today < self.reactivation_trades_allowed:
            return True
        else:
            self.logger.info(f"🟡 Límite de trades de reactivación alcanzado: {trades_today}/{self.reactivation_trades_allowed}")
            return False
    
    def _update_reactivation_success(self, trade_was_profitable: bool):
        """
        📊 Actualizar contador de éxito durante reactivación
        """
        if self.reactivation_phase > 0 and trade_was_profitable:
            self.reactivation_success_count += 1
            self.logger.info(f"✅ Trade exitoso durante reactivación: {self.reactivation_success_count} en fase {self.reactivation_phase}")
            
            # Verificar si se puede avanzar a la siguiente fase
            if ((self.reactivation_phase == 1 and self.reactivation_success_count >= 1) or
                (self.reactivation_phase == 2 and self.reactivation_success_count >= 2) or
                (self.reactivation_phase == 3 and self.reactivation_success_count >= 3)):
                
                self._initiate_gradual_reactivation()
    
    def _update_strategy_stats(self):
        """
        📈 Actualizar estadísticas de estrategias en la base de datos
        """
        try:
            with db_manager.get_db_session() as session:
                for strategy_name in self.strategies.keys():
                    # Buscar o crear estrategia en DB
                    db_strategy = session.query(DBStrategy).filter(
                        DBStrategy.name == f"{strategy_name}_AutoBot"
                    ).first()
                    
                    if not db_strategy:
                        db_strategy = DBStrategy(
                            name=f"{strategy_name}_AutoBot",
                            description=f"Estrategia {strategy_name} ejecutada por Trading Bot automático",
                            is_active=True,
                            is_paper_only=True
                        )
                        session.add(db_strategy)
                    
                    # Actualizar timestamp
                    db_strategy.last_trade_at = datetime.now()
                    db_strategy.updated_at = datetime.now()
                
                session.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Error updating strategy stats: {e}")
    
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
        
        portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
        
        # Información adicional del circuit breaker
        circuit_breaker_info = {
            "circuit_breaker_active": self.circuit_breaker_active,
            "consecutive_losses": self.consecutive_losses,
            "max_consecutive_losses": self.max_consecutive_losses,
            "circuit_breaker_activated_at": self.circuit_breaker_activated_at,
            "circuit_breaker_cooldown_hours": self.circuit_breaker_cooldown_hours
        }
        
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
        
        # Agregar información del circuit breaker como atributo adicional
        status.circuit_breaker_info = circuit_breaker_info
        
        return status
    
    def get_detailed_report(self) -> Dict:
        """
        📋 Obtener reporte detallado del bot
        """
        status = self.get_status()
        portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
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
            "risk_management": {
                **risk_report,
                "circuit_breaker": {
                    "active": self.circuit_breaker_active,
                    "consecutive_losses": self.consecutive_losses,
                    "max_consecutive_losses": self.max_consecutive_losses,
                    "activated_at": self.circuit_breaker_activated_at.isoformat() if self.circuit_breaker_activated_at else None,
                    "cooldown_hours": self.circuit_breaker_cooldown_hours,
                    "remaining_cooldown_hours": self._get_remaining_cooldown_hours() if hasattr(self, '_get_remaining_cooldown_hours') else 0
                }
            },
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
            
            return {
                'analysis_interval_minutes': self.analysis_interval,
                'active_strategies': active_strategies,
                'is_running': self.is_running,
                'total_strategies': len(self.strategies),
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
                'max_daily_trades': self.max_daily_trades,
                'min_confidence_threshold': self.min_confidence_threshold,
                'enable_trading': self.enable_trading,
                'symbols': self.symbols
            }
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

# Instancia global del trading bot
trading_bot = TradingBot()
#!/usr/bin/env python3
"""
🚀 Live Trading Bot - Simulador de Trading en Tiempo Real
Bot de trading que muestra logs simples en consola
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from colorama import Fore, Back, Style, init

# Inicializar colorama para colores en terminal
init(autoreset=True)

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.core.trading_bot import TradingBot
from src.config.config import TradingBotConfig, SYMBOLS
from src.database.database import db_manager
from src.config.live_trading_bot_config import LiveTradingBotConfig, live_trading_bot_config

# Configurar logging con colores
class ColoredFormatter(logging.Formatter):
    """Formatter personalizado para agregar colores a los logs"""
    
    def __init__(self, config: LiveTradingBotConfig):
        super().__init__()
        self.config = config
        self.COLORS = config.get_logging_config().level_colors
    
    def format(self, record):
        # Aplicar color según el nivel
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        # Colorear mensajes específicos usando configuración
        message = record.getMessage()
        display_config = self.config.get_display_config()
        
        if not display_config.emojis_enabled:
            # Si los emojis están deshabilitados, removerlos
            import re
            message = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]+', '', message)
        
        # Colores para diferentes tipos de procesos usando configuración
        emoji_map = display_config.emoji_mapping
        
        if emoji_map['analyzing'] in message and "Analizando" in message:
            message = f"{Fore.CYAN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['cycle_start'] in message and "INICIANDO CICLO" in message:
            message = f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['price_info'] in message and "Precio actual" in message:
            message = f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['indicators'] in message and "RSI" in message:
            message = f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"
        elif emoji_map['decision'] in message and "DECISIÓN FINAL" in message:
            message = f"{Fore.GREEN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['trade_executed'] in message and "TRADE EJECUTADO" in message:
            message = f"{Fore.GREEN + Back.BLACK + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['config_strategies'] in message and "CONFIGURACIÓN DE ESTRATEGIAS" in message:
            message = f"{Fore.CYAN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['config_paper_trader'] in message and "CONFIGURACIÓN DEL PAPER TRADER" in message:
            message = f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['config_bot'] in message and "CONFIGURACIÓN DEL BOT" in message:
            message = f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif message.strip().startswith(emoji_map['decision']) and ":" in message:
            message = f"{Fore.CYAN}{message}{Style.RESET_ALL}"
        elif message.strip().startswith("•"):
            message = f"{Fore.WHITE + Style.DIM}{message}{Style.RESET_ALL}"
        elif emoji_map['warning'] in message:
            message = f"{Fore.YELLOW}{message}{Style.RESET_ALL}"
        elif emoji_map['error'] in message:
            message = f"{Fore.RED}{message}{Style.RESET_ALL}"
        elif emoji_map['rocket'] in message:
            message = f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['trade_executing'] in message and "Ejecutando trade" in message:
            message = f"{Fore.CYAN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['strategy_executing'] in message and "Ejecutando estrategia" in message:
            message = f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"
        elif emoji_map['signal_arrow'] in message:
            message = f"{Fore.BLUE}{message}{Style.RESET_ALL}"
        elif emoji_map['adjustment'] in message and "AJUSTE DINÁMICO EJECUTADO" in message:
            message = f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['stop_loss'] in message and "STOP LOSS" in message:
            message = f"{Fore.RED + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif emoji_map['take_profit'] in message and "TAKE PROFIT" in message:
            message = f"{Fore.GREEN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        
        record.msg = message
        return super().format(record)

# Configurar logger con colores (sin duplicación)
logger = logging.getLogger(__name__)
logger.setLevel(live_trading_bot_config.get_logging_config().level)

# Limpiar handlers existentes para evitar duplicación
logger.handlers.clear()

# Aplicar el formatter con colores
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter(live_trading_bot_config))
logger.addHandler(handler)

# Evitar que los logs se propaguen al logger raíz
logger.propagate = live_trading_bot_config.get_logging_config().propagate

# Silenciar todos los otros loggers para mostrar solo los del live trading bot
def silence_other_loggers():
    """Silenciar todos los loggers excepto el del live trading bot"""
    # Lista de módulos a silenciar
    modules_to_silence = [
        'src.core.trading_bot',
        'src.core.enhanced_strategies', 
        'src.core.paper_trader',
        'src.core.enhanced_risk_manager',
        'src.core.position_manager',
        'src.core.position_monitor',
        'src.core.position_adjuster',
        'src.core.market_validator',
        'src.database.database',
        'src.database.migrations',
        'src.config.config',
        'src.config.config_manager',
        'src.config.database_config',
        'src.utils.error_handler',
        'sqlalchemy.engine'
    ]
    
    for module_name in modules_to_silence:
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(logging.CRITICAL)  # Solo errores críticos
        module_logger.propagate = False

# Aplicar el silenciado de otros loggers
silence_other_loggers()

# Configurar el logger raíz para evitar mensajes no deseados
root_logger = logging.getLogger()
root_logger.setLevel(logging.CRITICAL)  # Solo errores críticos en el logger raíz

class LiveTradingBot:
    """
    🚀 Bot de trading en vivo con logs simples
    """
    
    def __init__(self):
        self.config = TradingBotConfig()
        # Obtener el intervalo de análisis del perfil activo (AGRESIVO: 45 segundos)
        from src.config.config_manager import ConfigManager
        profile_config = ConfigManager.get_module_config('trading_bot')
        analysis_interval = profile_config.get('analysis_interval', 45)  # 45 segundos para AGRESIVO
        self.trading_bot = TradingBot(analysis_interval_minutes=analysis_interval/60)  # Convertir a minutos
        self.live_config = live_trading_bot_config
        
        # Configuración del bot
        self.symbols = SYMBOLS
        self.update_interval = self.config.get_live_update_interval()
        self.running = False
        
        # Inicializar estrategias del trading bot
        logger.info("🔧 Inicializando estrategias de trading...")
        try:
            # Forzar inicialización de estrategias
            self.trading_bot._initialize_strategies()
            logger.info(f"✅ {len(self.trading_bot.strategies)} estrategias inicializadas")
            
            # Mostrar información detallada de cada estrategia
            logger.info("📋 CONFIGURACIÓN DE ESTRATEGIAS:")
            for strategy_name, strategy in self.trading_bot.strategies.items():
                logger.info(f"   🎯 {strategy_name}:")
                # Corregir visualización de porcentajes - si el valor es < 1, está en formato decimal
                confidence_display = strategy.min_confidence * 100 if strategy.min_confidence < 1 else strategy.min_confidence
                logger.info(f"      • Confianza mínima: {confidence_display:.1f}%")
                if hasattr(strategy, 'rsi_oversold'):
                    logger.info(f"      • RSI Sobreventa: {strategy.rsi_oversold}")
                if hasattr(strategy, 'rsi_overbought'):
                    logger.info(f"      • RSI Sobrecompra: {strategy.rsi_overbought}")
                if hasattr(strategy, 'stop_loss_pct'):
                    logger.info(f"      • Stop Loss: {strategy.stop_loss_pct}%")
                if hasattr(strategy, 'take_profit_pct'):
                    logger.info(f"      • Take Profit: {strategy.take_profit_pct}%")
            
            # Mostrar configuración del Paper Trader
            portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            logger.info("💰 CONFIGURACIÓN DEL PAPER TRADER:")
            logger.info(f"   • Balance inicial: ${self.trading_bot.paper_trader.initial_balance:,.2f}")
            logger.info(f"   • Tamaño máximo por posición: {self.trading_bot.paper_trader.max_position_size*100:.1f}%")
            logger.info(f"   • Exposición máxima total: ${self.trading_bot.paper_trader.max_total_exposure:.1f}")
            logger.info(f"   • Valor mínimo por trade: ${self.trading_bot.paper_trader.min_trade_value}")
            logger.info(f"   • Valor actual del portfolio: ${portfolio_performance.get('total_value', 0):,.2f}")
            
            # Mostrar configuración del bot
            from src.config.config_manager import ConfigManager
            active_profile = ConfigManager.get_active_profile()
            logger.info("⚙️ CONFIGURACIÓN DEL BOT:")
            logger.info(f"   • Perfil activo: {active_profile} ⚡")
            logger.info(f"   • Símbolos: {', '.join(self.symbols)}")
            logger.info(f"   • Intervalo de análisis: {self.trading_bot.analysis_interval*60:.0f} segundos")
            logger.info(f"   • Intervalo de actualización en vivo: {self.update_interval} segundos")
            logger.info(f"   • Confianza mínima para trades: {self.config.get_min_confidence_threshold()}%")
            
            # Configurar callback para ajustes de TP/SL dinámicos
            try:
                if hasattr(self.trading_bot, 'position_adjuster') and self.trading_bot.position_adjuster:
                    self.trading_bot.position_adjuster.set_adjustment_callback(self._display_adjustment_event)
                    logger.info("✅ Callback de ajustes de posición configurado")
            except Exception as adj_e:
                logger.error(f"⚠️ Error configurando callback de ajustes: {adj_e}")
            
            # Configurar callback para eventos de trades
            try:
                if hasattr(self.trading_bot, 'set_trade_event_callback'):
                    self.trading_bot.set_trade_event_callback(self._handle_trading_bot_event)
                    logger.info("✅ Callback de eventos del TradingBot configurado")
            except Exception as trade_e:
                logger.error(f"⚠️ Error configurando callback de trades: {trade_e}")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando estrategias: {e}")
        
        self.last_signals = {}
        
        # Buffer para agrupar señales por símbolo y evitar entremezclado
        self.signals_buffer = {}
        self.current_analysis_symbol = None
        
        # Inicializar estadísticas de sesión usando configuración
        session_config = self.live_config.get_session_stats_config()
        self.session_stats = {
            "start_time": datetime.now(),
            "total_trades": session_config.initial_total_trades,
            "successful_trades": session_config.initial_successful_trades,
            "total_pnl": session_config.initial_total_pnl
        }
    
    def get_status(self):
        """Obtener estado del bot delegando al TradingBot interno"""
        try:
            bot_status = self.trading_bot.get_status()
            # Asegurar que siempre retornemos un diccionario
            if not isinstance(bot_status, dict):
                bot_status = {"status": str(bot_status)}
            
            # Agregar información específica del live bot
            live_status = {
                "is_running": self.running,
                "uptime": str(datetime.now() - self.session_stats['start_time']),
                "total_trades": self.session_stats['total_trades'],
                "successful_trades": self.session_stats['successful_trades'],
                "session_pnl": self.session_stats['total_pnl']
            }
            
            return {**bot_status, **live_status}
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado: {e}")
            return {
                "error": str(e),
                "is_running": getattr(self, 'running', False),
                "total_trades": 0
            }
    
    def get_detailed_report(self) -> Dict:
        """Obtener reporte detallado del bot delegando al TradingBot interno"""
        return self.trading_bot.get_detailed_report()
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas del live trading bot"""
        try:
            # Obtener estadísticas del trading bot interno
            bot_stats = self.trading_bot.get_statistics() if hasattr(self.trading_bot, 'get_statistics') else {}
            
            # Calcular estadísticas de la sesión
            session_duration = datetime.now() - self.session_stats['start_time']
            success_rate = (self.session_stats['successful_trades'] / max(1, self.session_stats['total_trades'])) * 100
            
            live_stats = {
                "session_duration_minutes": session_duration.total_seconds() / 60,
                "total_trades": self.session_stats['total_trades'],
                "successful_trades": self.session_stats['successful_trades'],
                "failed_trades": self.session_stats['total_trades'] - self.session_stats['successful_trades'],
                "success_rate_percent": round(success_rate, 2),
                "total_pnl": self.session_stats['total_pnl'],
                "average_pnl_per_trade": self.session_stats['total_pnl'] / max(1, self.session_stats['total_trades']),
                "symbols_traded": list(self.symbols),
                "is_running": self.running,
                "update_interval_seconds": self.update_interval
            }
            
            return {**bot_stats, **live_stats}
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {
                "error": str(e),
                "total_trades": 0,
                "success_rate_percent": 0.0
            }
    
    def get_configuration(self) -> Dict:
        """
        📋 Obtener configuración actual del live trading bot
        """
        try:
            # Obtener configuración del trading bot interno
            bot_config = self.trading_bot.get_configuration()
            
            # Añadir configuración específica del live bot
            live_config = {
                'live_symbols': self.symbols,
                'update_interval_seconds': self.update_interval,
                'is_live_running': self.running,
                'session_start_time': self.session_stats['start_time'].isoformat(),
                'session_total_trades': self.session_stats['total_trades'],
                'session_successful_trades': self.session_stats['successful_trades'],
                'session_total_pnl': self.session_stats['total_pnl']
            }
            
            # Combinar configuraciones
            return {**bot_config, **live_config}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración del live bot: {e}")
            return {}
    
    def _handle_trading_bot_event(self, event: Dict):
        """
        📢 Manejar eventos del TradingBot y mostrarlos en LiveTradingBot
        """
        try:
            event_type = event.get('type', 'unknown')
            timestamp = event.get('timestamp', datetime.now())
            
            if event_type == 'cycle_start':
                cycle_num = event.get('cycle_number', 0)
                symbols = event.get('symbols', [])
                strategies = event.get('strategies', [])
                daily_trades = event.get('daily_trades', 0)
                max_daily_trades = event.get('max_daily_trades', 0)
                
                logger.info(f"🔄 Ciclo #{cycle_num} - Analizando {len(symbols)} símbolos con {len(strategies)} estrategias")
                logger.info(f"📊 Trades diarios: {daily_trades}/{max_daily_trades}")
                
            elif event_type == 'signal_generated':
                symbol = event.get('symbol', '')
                signal_type = event.get('signal_type', '')
                strategy = event.get('strategy', '')
                confidence = event.get('confidence', 0)
                price = event.get('price', 0)
                
                # Solo mostrar señales finales (no intermedias de estrategias individuales)
                # Las señales intermedias se almacenan en buffer para análisis
                if strategy not in ['ProfessionalRSI', 'MultiTimeframe']:  # Solo mostrar Ensemble o señales finales
                    # Usar colores según el tipo de señal
                    if signal_type == 'BUY':
                        color = Fore.GREEN + Style.BRIGHT
                    elif signal_type == 'SELL':
                        color = Fore.RED + Style.BRIGHT
                    else:
                        color = Fore.YELLOW
                    
                    logger.info(f"{color}📊 Señal Final: {signal_type} {symbol} - Confianza: {confidence}% - Precio: ${price:,.2f}{Style.RESET_ALL}")
                
            elif event_type == 'bot_status':
                status_type = event.get('status_type', '')
                message = event.get('message', '')
                data = event.get('data', {})
                
                if status_type == 'start':
                    symbols = data.get('symbols', [])
                    strategies = data.get('strategies', [])
                    interval = data.get('analysis_interval', 0)
                    
                    logger.info(f"🚀 {message}")
                    logger.info(f"📊 Monitoreando símbolos: {', '.join(symbols)}")
                    logger.info(f"🧠 Estrategias activas: {', '.join(strategies)}")
                    logger.info("🔍 Monitoreo de posiciones iniciado")
                    logger.info("🎯 Monitoreo de ajustes TP/SL iniciado")
                    
                elif status_type == 'limit_reached':
                    logger.info(f"⏸️ {message}")
                    
                elif status_type == 'cache_hit':
                    signals_count = data.get('signals_count', 0)
                    logger.info(f"⚡ Usando resultados de análisis en caché ({signals_count} señales)")
                    
                elif status_type == 'no_signals':
                    symbols_analyzed = data.get('symbols_analyzed', 0)
                    strategies_used = data.get('strategies_used', 0)
                    logger.info(f"⚪ No se generaron señales de trading en este ciclo ({symbols_analyzed} símbolos, {strategies_used} estrategias)")
                    
                elif status_type == 'cycle_completed':
                    cycle_num = data.get('cycle_number', 0)
                    signals_generated = data.get('signals_generated', 0)
                    logger.info(f"✅ Ciclo #{cycle_num} completado - {signals_generated} señales generadas")
                    
                    # Mostrar resumen de análisis si hay señales
                    if signals_generated > 0:
                        self._show_cycle_summary()
                    
            elif event_type == 'price_update':
                symbol = event.get('symbol', '')
                price = event.get('price', 0)
                indicators = event.get('indicators', {})
                
                # Solo mostrar actualizaciones de precio importantes
                if indicators:
                    logger.debug(f"💰 {symbol}: ${price:,.2f} - Indicadores: {indicators}")
                    
            elif event_type in ['trade_executed', 'adjustment_executed', 'analysis_completed']:
                # Estos eventos ya se manejan con los callbacks existentes
                self._display_trade_event(event)
                
        except Exception as e:
            logger.error(f"❌ Error manejando evento del TradingBot: {e}")
    
    def _show_cycle_summary(self):
        """📋 Mostrar resumen de análisis del ciclo actual"""
        try:
            logger.info(f"\n{Fore.CYAN}{'='*60}")
            logger.info(f"📋 RESUMEN DEL CICLO - {datetime.now().strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}{Style.RESET_ALL}")
            
            # Mostrar información de balances
            if hasattr(self.trading_bot, 'paper_trader') and self.trading_bot.paper_trader:
                portfolio_summary = self.trading_bot.paper_trader.get_portfolio_summary()
                # Obtener balance USDT directamente del paper trader
                usdt_balance = self.trading_bot.paper_trader.get_balance('USDT')
                total_value = portfolio_summary.get('total_value', 0)
                pnl = portfolio_summary.get('total_pnl', 0)
                pnl_percentage = portfolio_summary.get('total_pnl_percentage', 0)
                
                logger.info(f"💰 BALANCES:")
                logger.info(f"   • Balance USDT disponible: ${usdt_balance:,.2f}")
                logger.info(f"   • Valor total portfolio: ${total_value:,.2f}")
                if pnl >= 0:
                    logger.info(f"   • P&L: {Fore.GREEN}+${pnl:,.2f} (+{pnl_percentage:.2f}%){Style.RESET_ALL}")
                else:
                    logger.info(f"   • P&L: {Fore.RED}${pnl:,.2f} ({pnl_percentage:.2f}%){Style.RESET_ALL}")
                logger.info("")
            
            # Obtener señales del último ciclo desde el TradingBot
            if hasattr(self.trading_bot, 'last_signals') and self.trading_bot.last_signals:
                for symbol, signal_data in self.trading_bot.last_signals.items():
                    signal_type = signal_data.get('signal_type', 'HOLD')
                    confidence = signal_data.get('confidence', 0)
                    price = signal_data.get('price', 0)
                    strategy = signal_data.get('strategy', 'Unknown')
                    
                    # Color según el tipo de señal
                    if signal_type == 'BUY':
                        color = Fore.GREEN + Style.BRIGHT
                        emoji = "📈"
                    elif signal_type == 'SELL':
                        color = Fore.RED + Style.BRIGHT
                        emoji = "📉"
                    else:
                        color = Fore.YELLOW
                        emoji = "⚪"
                    
                    logger.info(f"{color}{emoji} {symbol}: {signal_type} - {confidence}% confianza - ${price:,.2f} ({strategy}){Style.RESET_ALL}")
            
            logger.info(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando resumen del ciclo: {e}")
    
    async def analyze_and_trade(self):
        """🔍 Analizar mercado y ejecutar trades"""
        try:
            logger.info(f"🔄 INICIANDO CICLO DE ANÁLISIS - {datetime.now().strftime('%H:%M:%S')}")
            
            for symbol in self.symbols:
                logger.info(f"📊 Analizando {symbol}...")
                
                # Obtener precio actual
                try:
                    import ccxt
                    exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    logger.info(f"💰 {symbol} - Precio actual: ${current_price:,.2f}")
                except Exception as e:
                    logger.error(f"❌ Error obteniendo precio para {symbol}: {e}")
                    current_price = 0
                
                # Analizar con cada estrategia del trading bot (igual que trading_bot.py)
                all_signals = []
                
                for strategy_name, strategy in self.trading_bot.strategies.items():
                    try:
                        logger.info(f"🔍 Ejecutando estrategia {strategy_name} para {symbol}")
                        
                        # Obtener datos de mercado para mostrar indicadores usando configuración
                        try:
                            ti_config = self.live_config.get_technical_indicators_config()
                            df = strategy.get_market_data(symbol, ti_config.default_timeframe, ti_config.market_data_limit)
                            if not df.empty:
                                last_close = df['close'].iloc[-1]
                                volume_avg = df['volume'].rolling(ti_config.volume_rolling_period).mean().iloc[-1]
                                current_volume = df['volume'].iloc[-1]
                                
                                # Calcular algunos indicadores básicos usando configuración
                                import pandas_ta as ta
                                rsi = ta.rsi(df['close'], length=ti_config.rsi_period).iloc[-1]
                                sma_short = ta.sma(df['close'], length=ti_config.sma_short_period).iloc[-1]
                                sma_long = ta.sma(df['close'], length=ti_config.sma_long_period).iloc[-1]
                                
                                emoji_map = self.live_config.get_display_config().emoji_mapping
                                logger.info(f"{emoji_map['indicators']} {symbol} - RSI: {rsi:.1f}, SMA{ti_config.sma_short_period}: ${sma_short:.2f}, SMA{ti_config.sma_long_period}: ${sma_long:.2f}")
                                logger.info(f"{emoji_map['analyzing']} {symbol} - Volumen: {current_volume:,.0f} (Promedio: {volume_avg:,.0f})")
                                
                        except Exception as e:
                            emoji_map = self.live_config.get_display_config().emoji_mapping
                            logger.error(f"{emoji_map['error']} Error obteniendo indicadores para {symbol}: {e}")
                        
                        # Ejecutar análisis de la estrategia
                        signal = strategy.analyze(symbol)
                        
                        logger.info(f"➡️ {strategy_name} - {symbol}: {signal.signal_type} (Confianza: {signal.confidence_score:.1f}%)")
                        
                        # Agregar señal a la lista si no es HOLD
                        if signal.signal_type != "HOLD":
                            all_signals.append(signal)
                            
                    except Exception as e:
                        logger.error(f"❌ Error en estrategia {strategy_name} para {symbol}: {e}")
                
                # Procesar señales usando la misma lógica que trading_bot.py
                if all_signals:
                    self._process_signals_for_symbol(symbol, all_signals)
                else:
                    logger.info(f"⚪ No se generaron señales de trading para {symbol}")
                    self.last_signals[symbol] = {
                        'signal': None,
                        'timestamp': datetime.now(),
                        'action': 'HOLD'
                    }
                

                
        except Exception as e:
            logger.error(f"❌ Error crítico en análisis: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_binance_config_info(self, signal):
        """
        📋 Mostrar configuración sugerida para Binance (solo informativo)
        """
        try:
            from src.config.config import RiskManagerConfig
            
            symbol = signal.symbol
            signal_type = signal.signal_type
            price = signal.price
            
            # Calcular valores sugeridos para Binance
            binance_config = self.live_config.get_binance_adjustments_config()
            
            if signal_type == "BUY":
                # Precio sugerido ligeramente por debajo
                suggested_price = price * binance_config.buy_adjustment_factor
                
                # Monto sugerido (ejemplo)
                suggested_usdt = 100.0  # Valor ejemplo
                crypto_amount = suggested_usdt / suggested_price
                
                # TP/SL sugeridos
                tp_pct = RiskManagerConfig.get_tp_min_percentage()
                sl_pct = RiskManagerConfig.get_sl_min_percentage()
                
                take_profit_price = price * (1 + tp_pct / 100)
                stop_loss_price = price * (1 - sl_pct / 100)
                
                logger.info(f"\n{Fore.CYAN}📋 CONFIGURACIÓN SUGERIDA PARA BINANCE:{Style.RESET_ALL}")
                logger.info(f"   🎯 Tipo: {signal_type}")
                logger.info(f"   💰 Precio sugerido: ${suggested_price:.4f}")
                logger.info(f"   📊 Cantidad: {crypto_amount:.6f} {symbol.split('/')[0]}")
                logger.info(f"   💵 Total USDT: ${suggested_usdt:.2f}")
                logger.info(f"   🎯 Take Profit: ${take_profit_price:.4f} (+{tp_pct:.1f}%)")
                logger.info(f"   🛡️ Stop Loss: ${stop_loss_price:.4f} (-{sl_pct:.1f}%)")
                
            elif signal_type == "SELL":
                suggested_price = price * binance_config.sell_adjustment_factor
                
                logger.info(f"\n{Fore.CYAN}📋 CONFIGURACIÓN SUGERIDA PARA BINANCE:{Style.RESET_ALL}")
                logger.info(f"   🎯 Tipo: {signal_type}")
                logger.info(f"   💰 Precio sugerido: ${suggested_price:.4f}")
                logger.info(f"   📝 Vender posición completa del activo")
                
        except Exception as e:
            logger.error(f"❌ Error mostrando configuración de Binance: {e}")
    
    def _show_binance_config(self, signal, trade_result):
        """
        📋 Mostrar configuración para replicar en Binance
        """
        try:
            # Importar configuración dinámica
            from src.config.config import RiskManagerConfig
            
            # Extraer datos del trade ejecutado
            symbol = signal.symbol
            signal_type = signal.signal_type
            price = trade_result.entry_price if hasattr(trade_result, 'entry_price') else signal.current_price
            
            # Calcular valores para Binance usando configuración
            binance_config = self.live_config.get_binance_adjustments_config()
            
            if signal_type == "BUY":
                # Precio ligeramente por debajo para mejor ejecución
                binance_price = price * binance_config.buy_adjustment_factor
                
                # Monto en cripto (del trade ejecutado)
                crypto_amount = trade_result.quantity if hasattr(trade_result, 'quantity') else 0
                
                # Total en USDT
                total_usdt = trade_result.entry_value if hasattr(trade_result, 'entry_value') else (crypto_amount * price)
                
                # Usar valores dinámicos de TP y SL desde la señal si están disponibles
                if hasattr(signal, 'take_profit_price') and signal.take_profit_price > 0:
                    take_profit_price = signal.take_profit_price
                    take_profit_pct = ((take_profit_price - price) / price) * 100
                else:
                    # Fallback: usar configuración dinámica
                    tp_max = RiskManagerConfig.get_tp_max_percentage()
                    take_profit_price = price * (1 + tp_max / 100)
                    take_profit_pct = tp_max
                
                if hasattr(signal, 'stop_loss_price') and signal.stop_loss_price > 0:
                    stop_loss_price = signal.stop_loss_price
                    stop_loss_pct = ((price - stop_loss_price) / price) * 100
                else:
                    # Fallback: usar configuración dinámica
                    sl_max = RiskManagerConfig.get_sl_max_percentage()
                    stop_loss_price = price * (1 - sl_max / 100)
                    stop_loss_pct = sl_max
                
                emoji_map = self.live_config.get_display_config().emoji_mapping
                separator = emoji_map['separator']
                
                logger.info("")
                logger.info(f"{emoji_map['decision']} {separator}")
                logger.info(f"{emoji_map['config_strategies']} CONFIGURACIÓN PARA BINANCE SPOT - ORDEN LÍMITE")
                logger.info(f"{emoji_map['decision']} {separator}")
                logger.info(f"{emoji_map['money']} PRECIO:     {binance_price:,.2f} USDT")
                logger.info(f"{emoji_map['coin']} MONTO:      {crypto_amount:.8f} {symbol.replace('USDT', '')}")
                logger.info(f"{emoji_map['money']} TOTAL:      {total_usdt:.2f} USDT")
                logger.info("")
                logger.info(f"{emoji_map['shield']} PROTECCIÓN (TP/SL):")
                logger.info(f"{emoji_map['up_trend']} TAKE PROFIT: {take_profit_price:,.2f} USDT (+{take_profit_pct:.1f}%)")
                logger.info(f"{emoji_map['down_trend']} STOP LOSS:   {stop_loss_price:,.2f} USDT (-{stop_loss_pct:.1f}%)")
                logger.info(f"{emoji_map['decision']} {separator}")
                logger.info("")
                
            elif signal_type == "SELL":
                # Para ventas
                binance_price = price * binance_config.sell_adjustment_factor
                
                # Usar datos del trade ejecutado (no el balance actual que ya es 0)
                asset_name = symbol.replace('USDT', '')
                crypto_balance = trade_result.quantity if hasattr(trade_result, 'quantity') else 0
                total_usdt = trade_result.entry_value if hasattr(trade_result, 'entry_value') else (crypto_balance * price)
                
                # Usar valores dinámicos de TP y SL desde la señal si están disponibles
                if hasattr(signal, 'take_profit_price') and signal.take_profit_price > 0:
                    take_profit_price = signal.take_profit_price
                    take_profit_pct = ((price - take_profit_price) / price) * 100
                else:
                    # Fallback: usar configuración dinámica
                    tp_max = RiskManagerConfig.get_tp_max_percentage()
                    take_profit_price = price * (1 - tp_max / 100)
                    take_profit_pct = tp_max
                
                if hasattr(signal, 'stop_loss_price') and signal.stop_loss_price > 0:
                    stop_loss_price = signal.stop_loss_price
                    stop_loss_pct = ((stop_loss_price - price) / price) * 100
                else:
                    # Fallback: usar configuración dinámica
                    sl_max = RiskManagerConfig.get_sl_max_percentage()
                    stop_loss_price = price * (1 + sl_max / 100)
                    stop_loss_pct = sl_max
                
                emoji_map = self.live_config.get_display_config().emoji_mapping
                separator = emoji_map['separator']
                
                logger.info("")
                logger.info(f"{emoji_map['decision']} {separator}")
                logger.info(f"{emoji_map['config_strategies']} CONFIGURACIÓN PARA BINANCE SPOT - VENTA LÍMITE")
                logger.info(f"{emoji_map['decision']} {separator}")
                logger.info(f"{emoji_map['money']} PRECIO:     {binance_price:,.2f} USDT")
                logger.info(f"{emoji_map['coin']} MONTO:      {crypto_balance:.8f} {asset_name}")
                logger.info(f"{emoji_map['money']} TOTAL:      {total_usdt:.2f} USDT")
                logger.info("")
                logger.info(f"{emoji_map['shield']} PROTECCIÓN (TP/SL):")
                logger.info(f"{emoji_map['up_trend']} TAKE PROFIT: {take_profit_price:,.2f} USDT (-{take_profit_pct:.1f}%)")
                logger.info(f"{emoji_map['down_trend']} STOP LOSS:   {stop_loss_price:,.2f} USDT (+{stop_loss_pct:.1f}%)")
                logger.info(f"{emoji_map['decision']} {separator}")
                logger.info("")
                
        except Exception as e:
            logger.error(f"❌ Error mostrando configuración de Binance: {e}")
    
    def _display_adjustment_event(self, adjustment_result):
        """
        🔧 Mostrar eventos de ajustes dinámicos de TP/SL
        
        Args:
            adjustment_result: Resultado del ajuste de posición
        """
        try:
            if not adjustment_result:
                return
                
            symbol = adjustment_result.get('symbol', 'UNKNOWN')
            adjustment_type = adjustment_result.get('adjustment_type', 'UNKNOWN')
            old_value = adjustment_result.get('old_value', 0)
            new_value = adjustment_result.get('new_value', 0)
            reason = adjustment_result.get('reason', 'UNKNOWN')
            timestamp = adjustment_result.get('timestamp', datetime.now())
            
            # Formatear timestamp
            time_str = timestamp.strftime('%H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
            
            # Determinar emoji y color según el tipo de ajuste
            if 'STOP_LOSS' in adjustment_type.upper():
                emoji = "🛡️"
                action_color = Fore.RED + Style.BRIGHT
                action_name = "STOP LOSS"
            elif 'TAKE_PROFIT' in adjustment_type.upper():
                emoji = "🎯"
                action_color = Fore.GREEN + Style.BRIGHT
                action_name = "TAKE PROFIT"
            else:
                emoji = "🔧"
                action_color = Fore.YELLOW + Style.BRIGHT
                action_name = adjustment_type
            
            # Mostrar el evento de ajuste
            logger.info(f"")
            logger.info(f"{emoji} ═══════════════════════════════════════════════════════════")
            logger.info(f"{action_color}🔧 AJUSTE DINÁMICO EJECUTADO - {time_str}{Style.RESET_ALL}")
            logger.info(f"{emoji} ═══════════════════════════════════════════════════════════")
            logger.info(f"📊 SÍMBOLO:     {symbol}")
            logger.info(f"🔄 TIPO:        {action_name}")
            logger.info(f"📉 VALOR ANTERIOR: ${old_value:,.4f}")
            logger.info(f"📈 VALOR NUEVO:    ${new_value:,.4f}")
            logger.info(f"💡 RAZÓN:       {reason}")
            
            # Calcular y mostrar el cambio
            if old_value and new_value:
                change_pct = ((new_value - old_value) / old_value) * 100
                change_direction = "📈" if change_pct > 0 else "📉"
                logger.info(f"{change_direction} CAMBIO:      {change_pct:+.2f}%")
            
            logger.info(f"{emoji} ═══════════════════════════════════════════════════════════")
            logger.info(f"")
            
        except Exception as e:
             logger.error(f"❌ Error mostrando evento de ajuste: {e}")
    
    def _display_trade_event(self, trade_event):
        """
        💼 Mostrar eventos de trades ejecutados por el TradingBot
        
        Args:
            trade_event: Evento de trade ejecutado
        """
        try:
            if not trade_event:
                return
                
            symbol = trade_event.get('symbol', 'UNKNOWN')
            signal_type = trade_event.get('signal_type', 'UNKNOWN')
            confidence = trade_event.get('confidence', 0)
            entry_price = trade_event.get('entry_price', 0)
            quantity = trade_event.get('quantity', 0)
            trade_value = trade_event.get('trade_value', 0)
            success = trade_event.get('success', False)
            message = trade_event.get('message', '')
            risk_score = trade_event.get('risk_score', 0)
            risk_level = trade_event.get('risk_level', 'UNKNOWN')
            stop_loss = trade_event.get('stop_loss')
            take_profit = trade_event.get('take_profit')
            timestamp = trade_event.get('timestamp', datetime.now())
            
            # Formatear timestamp
            time_str = timestamp.strftime('%H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
            
            # Determinar emoji y color según el tipo de señal
            if signal_type.upper() == 'BUY':
                signal_emoji = "📈"
                signal_color = Fore.GREEN + Style.BRIGHT
            elif signal_type.upper() == 'SELL':
                signal_emoji = "📉"
                signal_color = Fore.RED + Style.BRIGHT
            else:
                signal_emoji = "🔄"
                signal_color = Fore.YELLOW + Style.BRIGHT
            
            # Determinar estado del trade
            status_emoji = "✅" if success else "❌"
            status_color = Fore.GREEN if success else Fore.RED
            
            # Mostrar el evento de trade
            logger.info(f"")
            logger.info(f"💼 ═══════════════════════════════════════════════════════════")
            logger.info(f"{signal_color}{signal_emoji} TRADE EJECUTADO POR TRADING BOT - {time_str}{Style.RESET_ALL}")
            logger.info(f"💼 ═══════════════════════════════════════════════════════════")
            logger.info(f"📊 SÍMBOLO:     {symbol}")
            logger.info(f"🎯 SEÑAL:       {signal_type} (Confianza: {confidence:.1f}%)")
            logger.info(f"💰 PRECIO:      ${entry_price:,.4f}")
            logger.info(f"📦 CANTIDAD:    {quantity:.8f}")
            logger.info(f"💵 VALOR:       ${trade_value:,.2f}")
            logger.info(f"{status_color}📋 ESTADO:      {status_emoji} {message}{Style.RESET_ALL}")
            logger.info(f"🛡️ RIESGO:      {risk_score:.1f}/100 ({risk_level})")
            
            # Mostrar TP/SL si están disponibles
            if stop_loss:
                logger.info(f"🛡️ STOP LOSS:   ${stop_loss:,.4f}")
            if take_profit:
                logger.info(f"🎯 TAKE PROFIT: ${take_profit:,.4f}")
            
            logger.info(f"💼 ═══════════════════════════════════════════════════════════")
            logger.info(f"")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando evento de trade: {e}")
     
    def _process_signals_for_symbol(self, symbol: str, signals):
        """
        🎯 Procesar y ejecutar señales de trading para un símbolo específico
        
        Args:
            symbol: Símbolo del activo
            signals: Lista de señales generadas para este símbolo
        """
        try:
            # Filtrar señales por confianza mínima
            high_confidence_signals = [
                signal for signal in signals 
                if signal.confidence_score >= self.trading_bot.min_confidence_threshold
            ]
            
            if not high_confidence_signals:
                logger.info(f"📉 No hay señales por encima del umbral de confianza ({self.trading_bot.min_confidence_threshold}%) para {symbol}")
                self.last_signals[symbol] = {
                    'signal': None,
                    'timestamp': datetime.now(),
                    'action': 'HOLD'
                }
                return
            
            # Obtener posiciones activas para diversificación
            active_positions = self.trading_bot.position_monitor.position_manager.get_active_positions()
            current_positions = len(active_positions)
            
            # Configuración de diversificación desde el perfil activo
            config = self.trading_bot.config_manager.get_consolidated_config() if hasattr(self.trading_bot, 'config_manager') else {}
            trading_config = config.get("trading_bot", {})
            max_positions = trading_config.get("max_positions", 5)
            diversification_threshold = max_positions * 0.6  # 60% del máximo
            
            # Ordenar señales con prioridad de diversificación
            def signal_priority(signal):
                base_score = signal.confidence_score
                
                # Priorizar compras si tenemos pocas posiciones (diversificación)
                if signal.signal_type == "BUY" and current_positions < diversification_threshold:
                    # Boost de +10 puntos para compras cuando necesitamos diversificar
                    return base_score + 10
                # Priorizar ventas si estamos cerca del límite de posiciones
                elif signal.signal_type == "SELL" and current_positions >= max_positions * 0.8:
                    # Boost de +5 puntos para ventas cuando estamos cerca del límite
                    return base_score + 5
                
                return base_score
            
            # Ordenar por prioridad (mayor primero)
            high_confidence_signals.sort(key=signal_priority, reverse=True)
            
            logger.info(f"📊 POSICIONES DIVERSIFICACION para {symbol}: {current_positions}/{max_positions} positions")
            if current_positions < diversification_threshold:
                logger.info(f"🎯 Prioritizing BUY signals for {symbol} - portfolio diversification")
            
            # Obtener valor actual del portfolio
            from src.database.database import db_manager
            portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
            portfolio_value = portfolio_summary.get("total_value", 10000.0)  # Valor por defecto
            
            logger.info(f"💼 Valor actual del portfolio: ${portfolio_value:,.2f}")
            
            # Procesar la mejor señal para este símbolo
            best_signal = high_confidence_signals[0]
            
            try:
                # Verificar límite diario
                if self.trading_bot.stats["daily_trades"] >= self.trading_bot.max_daily_trades:
                    logger.info("⏸️ Límite diario de trades alcanzado")
                    return
                
                # Análisis de riesgo
                risk_assessment = self.trading_bot.risk_manager.assess_trade_risk(best_signal, portfolio_value)
                
                logger.info(f"🛡️ Evaluación de riesgo para {best_signal.symbol}:")
                logger.info(f"   - Puntuación de Riesgo: {risk_assessment.overall_risk_score:.1f}/100")
                logger.info(f"   - Tamaño de Posición: {risk_assessment.position_sizing.recommended_size:.2f}")
                logger.info(f"   - Aprobado: {risk_assessment.is_approved}")
                logger.info(f"   - Nivel de Riesgo: {risk_assessment.risk_level.value}")
                
                # Ejecutar si está aprobado
                if risk_assessment.is_approved and self.trading_bot.enable_trading:
                    trade_result = self.trading_bot.paper_trader.execute_signal(best_signal)
                    
                    if trade_result.success:
                        self.trading_bot.stats["trades_executed"] += 1
                        self.trading_bot.stats["daily_trades"] += 1
                        self.session_stats["total_trades"] += 1
                        
                        # Determinar si fue exitoso basándose en el tipo de trade y PnL real
                        trade_was_profitable = False
                        if best_signal.signal_type == "SELL":
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
                            self.trading_bot.stats["successful_trades"] += 1
                            self.session_stats["successful_trades"] += 1
                        
                        logger.info(f"✅ Trade ejecutado: {trade_result.message}")
                        
                        # Mostrar configuración para Binance
                        self._show_binance_config(best_signal, trade_result)
                        
                        # Actualizar last_signals con la señal ejecutada
                        self.last_signals[symbol] = {
                            'signal': best_signal,
                            'timestamp': datetime.now(),
                            'action': best_signal.signal_type,
                            'confidence': best_signal.confidence_score,
                            'executed': True
                        }
                    else:
                        logger.warning(f"❌ Trade falló: {trade_result.message}")
                        self.last_signals[symbol] = {
                            'signal': best_signal,
                            'timestamp': datetime.now(),
                            'action': 'FAILED',
                            'confidence': best_signal.confidence_score,
                            'executed': False
                        }
                
                elif not risk_assessment.is_approved:
                    rejection_reason = f"Nivel de riesgo: {risk_assessment.risk_level.value}"
                    logger.info(f"🚫 Trade rechazado: {rejection_reason}")
                    
                    # Mostrar recomendaciones
                    for rec in risk_assessment.recommendations:
                        logger.info(f"   💡 {rec}")
                    
                    # Actualizar last_signals con la señal rechazada
                    self.last_signals[symbol] = {
                        'signal': best_signal,
                        'timestamp': datetime.now(),
                        'action': 'REJECTED',
                        'confidence': best_signal.confidence_score,
                        'executed': False,
                        'rejection_reason': rejection_reason
                    }
                
            except Exception as e:
                logger.error(f"❌ Error procesando señal para {best_signal.symbol}: {e}")
                self.last_signals[symbol] = {
                    'signal': None,
                    'timestamp': datetime.now(),
                    'action': 'ERROR',
                    'error': str(e)
                }
            
            # Actualizar P&L total
            self.trading_bot.stats["total_pnl"] = portfolio_summary.get("total_pnl", 0)
            
        except Exception as e:
            logger.error(f"❌ Error crítico procesando señales para {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    async def start(self):
        """🚀 Iniciar el bot de trading en vivo"""
        self.running = True
        logger.info("🚀 Iniciando Live Trading Bot...")
        logger.info("⚠️ Modo: Paper Trading (Sin dinero real)")
        logger.info("Presiona Ctrl+C para detener")
        
        # Iniciar el TradingBot interno y su position_monitor
        try:
            logger.info("🔧 Iniciando TradingBot interno y position_monitor...")
            self.trading_bot.start()  # Esto inicia el position_monitor automáticamente
            logger.info("✅ TradingBot interno y position_monitor iniciados correctamente")
        except Exception as e:
            logger.error(f"❌ Error iniciando TradingBot interno: {e}")
            return
        
        # Contador de ciclos para debug
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                logger.info(f"🔄 Ciclo #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Analizar mercado y ejecutar trades
                await self.analyze_and_trade()
                
                # Mostrar estadísticas actuales
                self.show_current_stats()
                
                logger.info(f"⏱️ Esperando {self.update_interval} segundos antes del próximo análisis...")
                
                # Esperar antes del siguiente ciclo
                await asyncio.sleep(self.update_interval)
                    
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error crítico: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            
            # Detener el TradingBot interno y su position_monitor
            try:
                logger.info("🛑 Deteniendo TradingBot interno y position_monitor...")
                self.trading_bot.stop()
                logger.info("✅ TradingBot interno detenido correctamente")
            except Exception as e:
                logger.error(f"❌ Error deteniendo TradingBot interno: {e}")
            
            # Mostrar resumen final
            self.show_final_summary()
    
    def show_current_stats(self):
        """📊 Mostrar estadísticas actuales usando datos del TradingBot"""
        try:
            portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            portfolio_summary = self.trading_bot.paper_trader.get_portfolio_summary()
            
            # Obtener balance de USDT correctamente
            current_balance = self.trading_bot.paper_trader.get_balance('USDT')
            total_value = portfolio_performance.get('total_value', 0)
            pnl = portfolio_performance.get('total_pnl', 0)
            pnl_pct = portfolio_performance.get('total_return_percentage', 0)
            
            logger.info("\n" + "="*60)
            logger.info("📊 ESTADÍSTICAS ACTUALES")
            logger.info("="*60)
            logger.info(f"💰 Balance actual: ${current_balance:,.2f}")
            logger.info(f"📈 Valor total del portfolio: ${total_value:,.2f}")
            logger.info(f"💵 PnL total: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
            logger.info(f"🎯 Trades totales: {self.session_stats['total_trades']}")
            if self.session_stats['total_trades'] > 0:
                success_rate = (self.session_stats['successful_trades'] / self.session_stats['total_trades']) * 100
                logger.info(f"✅ Tasa de éxito: {success_rate:.1f}%")
            
            # Mostrar balances de cada activo
            logger.info("\n🪙 BALANCES POR ACTIVO:")
            assets = portfolio_summary.get('assets', [])
            if assets:
                for asset in assets:
                    symbol = asset.get('symbol', '')
                    quantity = asset.get('quantity', 0)
                    current_value = asset.get('current_value', 0)
                    
                    if symbol == 'USDT':
                        # Para USDT solo mostrar el valor
                        logger.info(f"   💵 {symbol}: ${current_value:,.2f}")
                    else:
                        # Para otros activos mostrar cantidad y valor en USDT
                        logger.info(f"   🪙 {symbol}: {quantity:.6f} (${current_value:,.2f})")
            else:
                logger.info("   📭 No hay activos en el portfolio")
            
            logger.info("="*60 + "\n")
        except Exception as e:
            logger.error(f"❌ Error mostrando estadísticas: {e}")
    
    def show_final_summary(self):
        """📋 Mostrar resumen final de la sesión usando datos del TradingBot"""
        try:
            session_duration = datetime.now() - self.session_stats['start_time']
            portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            # Obtener balance final de USDT correctamente
            final_balance = self.trading_bot.paper_trader.get_balance('USDT')
            total_value = portfolio_performance.get('total_value', 0)
            total_pnl = portfolio_performance.get('total_pnl', 0)
            pnl_pct = portfolio_performance.get('total_return_percentage', 0)
            
            logger.info("\n" + "="*80)
            logger.info("🏁 RESUMEN FINAL DE LA SESIÓN")
            logger.info("="*80)
            logger.info(f"⏱️ Duración de la sesión: {session_duration}")
            logger.info(f"💰 Balance inicial: ${self.trading_bot.paper_trader.initial_balance:,.2f}")
            logger.info(f"💰 Balance final: ${final_balance:,.2f}")
            logger.info(f"📈 Valor total final: ${total_value:,.2f}")
            logger.info(f"💵 PnL total: ${total_pnl:,.2f} ({pnl_pct:+.2f}%)")
            logger.info(f"🎯 Total de trades: {self.session_stats['total_trades']}")
            if self.session_stats['total_trades'] > 0:
                success_rate = (self.session_stats['successful_trades'] / self.session_stats['total_trades']) * 100
                logger.info(f"✅ Trades exitosos: {self.session_stats['successful_trades']} ({success_rate:.1f}%)")
                avg_pnl = total_pnl / self.session_stats['total_trades']
                logger.info(f"📊 PnL promedio por trade: ${avg_pnl:.2f}")
            logger.info("="*80)
            logger.info("🙏 ¡Gracias por usar el Live Trading Bot!")
            logger.info("="*80 + "\n")
        except Exception as e:
            logger.error(f"❌ Error mostrando resumen final: {e}")

async def main():
    """🎯 Función principal"""
    try:
        bot = LiveTradingBot()
        await bot.start()
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico en main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Ya manejado en main()
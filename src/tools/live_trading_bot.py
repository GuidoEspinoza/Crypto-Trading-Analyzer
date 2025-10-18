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
from src.config.main_config import TradingBotConfig, PRODUCTION_MODE, PAPER_TRADING_ONLY, ENABLE_REAL_TRADING, VERBOSE_LOGGING
# Base de datos eliminada - usando Capital.com directamente

# Configurar logging con colores
class ColoredFormatter(logging.Formatter):
    """Formatter personalizado para agregar colores a los logs"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        # Aplicar color según el nivel
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        # Colorear mensajes específicos
        message = record.getMessage()
        
        # Colores para diferentes tipos de procesos
        if "📊 Analizando" in message:
            message = f"{Fore.CYAN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "🔄 INICIANDO CICLO" in message:
            message = f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "💰" in message and "Precio actual" in message:
            message = f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "📈" in message and "RSI" in message:
            message = f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"
        elif "🎯 DECISIÓN FINAL" in message:
            message = f"{Fore.GREEN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "✅ TRADE EJECUTADO" in message:
            message = f"{Fore.GREEN + Back.BLACK + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "📋 CONFIGURACIÓN DE ESTRATEGIAS" in message:
            message = f"{Fore.CYAN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "💰 CONFIGURACIÓN DEL PAPER TRADER" in message:
            message = f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "⚙️ CONFIGURACIÓN DEL BOT" in message:
            message = f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif message.strip().startswith("🎯") and ":" in message:
            message = f"{Fore.CYAN}{message}{Style.RESET_ALL}"
        elif message.strip().startswith("•"):
            message = f"{Fore.WHITE + Style.DIM}{message}{Style.RESET_ALL}"
        elif "⚠️" in message:
            message = f"{Fore.YELLOW}{message}{Style.RESET_ALL}"
        elif "❌" in message:
            message = f"{Fore.RED}{message}{Style.RESET_ALL}"
        elif "🚀" in message:
            message = f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "💼 Ejecutando trade" in message:
            message = f"{Fore.CYAN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "🔍 Ejecutando estrategia" in message:
            message = f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"
        elif "➡️" in message:
            message = f"{Fore.BLUE}{message}{Style.RESET_ALL}"
        elif "🔧 AJUSTE DINÁMICO EJECUTADO" in message:
            message = f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "🛡️" in message and "STOP LOSS" in message:
            message = f"{Fore.RED + Style.BRIGHT}{message}{Style.RESET_ALL}"
        elif "🎯" in message and "TAKE PROFIT" in message:
            message = f"{Fore.GREEN + Style.BRIGHT}{message}{Style.RESET_ALL}"
        
        record.msg = message
        return super().format(record)

# Configurar logger con colores (sin duplicación)
logger = logging.getLogger(__name__)
log_level = logging.DEBUG if VERBOSE_LOGGING else logging.INFO
logger.setLevel(log_level)

# Limpiar handlers existentes para evitar duplicación
logger.handlers.clear()

# Aplicar el formatter con colores
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Evitar que los logs se propaguen al logger raíz
logger.propagate = False

class LiveTradingBot:
    """
    🚀 Bot de trading en vivo con logs simples
    """
    
    def __init__(self):
        self.config = TradingBotConfig()
        self.trading_bot = TradingBot()
        
        # Verificaciones de modo de operación
        if PRODUCTION_MODE:
            if not PAPER_TRADING_ONLY:
                logger.warning("⚠️  PRODUCTION MODE: Paper trading is disabled!")
            if ENABLE_REAL_TRADING:
                logger.warning("⚠️  PRODUCTION MODE: Real trading is enabled!")
            logger.info("🏭 Live Trading Bot running in PRODUCTION MODE")
        else:
            logger.info("🧪 Live Trading Bot running in DEVELOPMENT MODE")
        
        # Configuración del bot
        self.symbols = TradingBotConfig.SYMBOLS_LIVE_BOT
        # Intervalo de análisis configurado en minutos; convertir a segundos para asyncio.sleep
        self.update_interval_minutes = self.config.get_live_update_interval()
        self.update_interval = max(60, int(self.update_interval_minutes * 60))
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
                logger.info(f"      • Confianza mínima: {strategy.min_confidence}%")
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
            logger.info(f"   • Exposición máxima total: {self.trading_bot.paper_trader.max_total_exposure*100:.1f}%")
            logger.info(f"   • Valor mínimo por trade: ${self.trading_bot.paper_trader.min_trade_value}")
            logger.info(f"   • Valor actual del portfolio: ${portfolio_performance.get('total_value', 0.0):,.2f}")
            
            # Mostrar configuración del bot
            logger.info("⚙️ CONFIGURACIÓN DEL BOT:")
            logger.info(f"   • Símbolos: {', '.join(self.symbols)}")
            logger.info(f"   • Intervalo de análisis: {self.update_interval_minutes} minutos ({self.update_interval} segundos)")
            logger.info(f"   • Confianza mínima para trades: {self.config.get_min_confidence_threshold()}%")
            
            # Ajustes de TP/SL desactivados (Opción A): no configurar callback
            # try:
            #     if hasattr(self.trading_bot, 'position_adjuster') and self.trading_bot.position_adjuster:
            #         self.trading_bot.position_adjuster.set_adjustment_callback(self._display_adjustment_event)
            #         logger.info("✅ Callback de ajustes de posición configurado")
            # except Exception as adj_e:
            #     logger.error(f"⚠️ Error configurando callback de ajustes: {adj_e}")
            
            # Configurar callback para eventos de trades
            try:
                if hasattr(self.trading_bot, 'set_trade_event_callback'):
                    self.trading_bot.set_trade_event_callback(self._display_trade_event)
                    logger.info("✅ Callback de eventos de trade configurado")
            except Exception as trade_e:
                logger.error(f"⚠️ Error configurando callback de trades: {trade_e}")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando estrategias: {e}")
        
        self.last_signals = {}
        self.session_stats = {
            "start_time": datetime.now(),
            "total_trades": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "last_known_trades": 0,
            "last_known_successful": 0
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
    

    
    async def analyze_and_trade(self):
        """🔍 Analizar mercado y ejecutar trades"""
        try:
            logger.info(f"🔄 INICIANDO CICLO DE ANÁLISIS - {datetime.now().strftime('%H:%M:%S')}")
            
            for symbol in self.symbols:
                logger.info(f"📊 Analizando {symbol}...")
                
                # Obtener precio actual usando fuente centralizada con cache TTL
                try:
                    current_price = float(self.trading_bot._get_current_price(symbol))
                    logger.info(f"💰 {symbol} - Precio actual: ${current_price:,.2f}")
                except Exception as e:
                    logger.error(f"❌ Error obteniendo precio para {symbol}: {e}")
                    current_price = 0.0
                
                # Analizar con cada estrategia del trading bot (igual que trading_bot.py)
                all_signals = []
                
                for strategy_name, strategy in self.trading_bot.strategies.items():
                    try:
                        logger.info(f"🔍 Ejecutando estrategia {strategy_name} para {symbol}")
                        
                        # Obtener datos de mercado para mostrar indicadores
                        try:
                            df = strategy.get_market_data(symbol, "1h", 50)
                            if not df.empty:
                                last_close = df['close'].iloc[-1]
                                volume_avg = df['volume'].rolling(20).mean().iloc[-1]
                                current_volume = df['volume'].iloc[-1]
                                
                                # Calcular algunos indicadores básicos
                                import pandas_ta as ta
                                rsi = ta.rsi(df['close'], length=14).iloc[-1]
                                sma_20 = ta.sma(df['close'], length=20).iloc[-1]
                                sma_50 = ta.sma(df['close'], length=50).iloc[-1]
                                
                                logger.info(f"📈 {symbol} - RSI: {rsi:.1f}, SMA20: ${sma_20:.2f}, SMA50: ${sma_50:.2f}")
                                logger.info(f"📊 {symbol} - Volumen: {current_volume:,.0f} (Promedio: {volume_avg:,.0f})")
                                
                        except Exception as e:
                            logger.error(f"❌ Error obteniendo indicadores para {symbol}: {e}")
                        
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
            
            # Ordenar por confianza (mayor primero)
            high_confidence_signals.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Obtener valor actual del portfolio (simplificado - sin base de datos)
            portfolio_value = self.trading_bot.config.DEFAULT_PORTFOLIO_VALUE
            
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
                
                # Ejecutar si está aprobado - usar el método del trading_bot que maneja real trading
                if risk_assessment.is_approved and self.trading_bot.enable_trading:
                    logger.info(f"🔄 Procesando señal con trading_bot._process_signals para {best_signal.symbol}")
                    logger.info(f"🔧 Real trading habilitado: {self.trading_bot.enable_real_trading}")
                    logger.info(f"🔧 Capital client disponible: {self.trading_bot.capital_client is not None}")
                    
                    # Usar el método del trading_bot que maneja tanto paper como real trading
                    self.trading_bot._process_signals([best_signal])
                    
                    # Actualizar estadísticas locales basándose en las estadísticas del trading_bot
                    current_trades = self.trading_bot.stats["trades_executed"]
                    current_daily_trades = self.trading_bot.stats["daily_trades"]
                    current_successful_trades = self.trading_bot.stats["successful_trades"]
                    
                    # Verificar si se ejecutó un nuevo trade
                    if current_trades > self.session_stats.get("last_known_trades", 0):
                        self.session_stats["total_trades"] += 1
                        self.session_stats["last_known_trades"] = current_trades
                        
                        # Verificar si fue exitoso
                        if current_successful_trades > self.session_stats.get("last_known_successful", 0):
                            self.session_stats["successful_trades"] += 1
                            self.session_stats["last_known_successful"] = current_successful_trades
                        
                        logger.info(f"✅ Señal procesada por trading_bot para {best_signal.symbol}")
                        
                        # Actualizar last_signals con la señal ejecutada
                        self.last_signals[symbol] = {
                            'signal': best_signal,
                            'timestamp': datetime.now(),
                            'action': best_signal.signal_type,
                            'confidence': best_signal.confidence_score,
                            'executed': True
                        }
                    else:
                        logger.warning(f"❌ No se ejecutó trade para {best_signal.symbol}")
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
            try:
                portfolio_summary = self.trading_bot.paper_trader.get_portfolio_summary()
                self.trading_bot.stats["total_pnl"] = portfolio_summary.get("total_pnl", 0)
            except Exception as e:
                logger.debug(f"No se pudo obtener portfolio_summary: {e}")
                self.trading_bot.stats["total_pnl"] = 0
            
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
                
                logger.info(f"⏱️ Esperando {self.update_interval_minutes} minutos ({self.update_interval} segundos) antes del próximo análisis...")
                
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
            # Intentar obtener portfolio_performance, si no existe usar valores por defecto
            try:
                portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            except AttributeError:
                portfolio_performance = {'total_value': 0.0, 'total_pnl': 0.0, 'total_return_percentage': 0.0}
            
            portfolio_summary = self.trading_bot.paper_trader.get_portfolio_summary()
            
            # Obtener balance de USD correctamente
            current_balance = self.trading_bot.paper_trader.get_balance('USD')
            total_value = portfolio_performance.get('total_value', 0.0)
            pnl = portfolio_performance.get('total_pnl', 0.0)
            pnl_pct = portfolio_performance.get('total_return_percentage', 0.0)
            
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
                    
                    if symbol == 'USD':
                        # Para USD solo mostrar el valor
                        logger.info(f"   💵 {symbol}: ${current_value:,.2f}")
                    else:
                        # Para otros activos mostrar cantidad y valor en USD
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
            # Intentar obtener portfolio_performance, si no existe usar valores por defecto
            try:
                portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            except AttributeError:
                portfolio_performance = {'total_value': 0.0, 'total_pnl': 0.0, 'total_return_percentage': 0.0}
            # Obtener balance final de USD correctamente
            final_balance = self.trading_bot.paper_trader.get_balance('USD')
            total_value = portfolio_performance.get('total_value', 0.0)
            total_pnl = portfolio_performance.get('total_pnl', 0.0)
            pnl_pct = portfolio_performance.get('total_return_percentage', 0.0)
            
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
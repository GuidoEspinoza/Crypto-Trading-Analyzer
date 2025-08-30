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

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_engine.trading_bot import TradingBot
from trading_engine.paper_trader import PaperTrader
from trading_engine.enhanced_risk_manager import EnhancedRiskManager
from trading_engine.config import TradingBotConfig
from database.database import db_manager

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
        
        record.msg = message
        return super().format(record)

# Configurar logger con colores (sin duplicación)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        self.paper_trader = PaperTrader()
        self.risk_manager = EnhancedRiskManager()
        
        # Configuración del bot
        self.symbols = TradingBotConfig.SYMBOLS_LIVE_BOT
        self.update_interval = 30  # segundos
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
            logger.info("💰 CONFIGURACIÓN DEL PAPER TRADER:")
            logger.info(f"   • Balance inicial: ${self.paper_trader.initial_balance:,.2f}")
            logger.info(f"   • Tamaño máximo por posición: {self.paper_trader.max_position_size:.1f}%")
            logger.info(f"   • Exposición máxima total: {self.paper_trader.max_total_exposure:.1f}%")
            logger.info(f"   • Valor mínimo por trade: ${self.paper_trader.min_trade_value}")
            
            # Mostrar configuración del bot
            logger.info("⚙️ CONFIGURACIÓN DEL BOT:")
            logger.info(f"   • Símbolos: {', '.join(self.symbols)}")
            logger.info(f"   • Intervalo de análisis: {self.update_interval} segundos")
            logger.info(f"   • Confianza mínima para trades: {self.config.MIN_CONFIDENCE_THRESHOLD}%")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando estrategias: {e}")
        
        self.last_signals = {}
        self.session_stats = {
            "start_time": datetime.now(),
            "total_trades": 0,
            "successful_trades": 0,
            "total_pnl": 0.0
        }
    

    
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
                
                # Analizar con cada estrategia del trading bot
                best_signal = None
                best_confidence = 0
                
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
                        
                        # Seleccionar la señal con mayor confianza
                        if signal.confidence_score > best_confidence:
                            best_signal = signal
                            best_confidence = signal.confidence_score
                            
                    except Exception as e:
                        logger.error(f"❌ Error en estrategia {strategy_name} para {symbol}: {e}")
                
                # Decisión final
                if best_signal:
                    logger.info(f"🎯 DECISIÓN FINAL para {symbol}: {best_signal.signal_type} con {best_confidence:.1f}% de confianza")
                    
                    self.last_signals[symbol] = {
                        'signal': best_signal,
                        'timestamp': datetime.now(),
                        'action': 'PENDING'
                    }
                    
                    # Ejecutar trade si la señal es válida y tiene suficiente confianza
                    if best_signal.signal_type in ['BUY', 'SELL'] and best_signal.confidence_score >= 65.0:
                        logger.info(f"💼 Ejecutando trade {best_signal.signal_type} para {symbol}...")
                        trade_result = self.paper_trader.execute_signal(best_signal)
                        
                        if trade_result.success:
                            self.last_signals[symbol]['action'] = 'EXECUTED'
                            self.session_stats['total_trades'] += 1
                            if trade_result.trade_id:
                                self.session_stats['successful_trades'] += 1
                            logger.info(f"✅ TRADE EJECUTADO: {symbol} - Cantidad: {trade_result.quantity:.6f}, Valor: ${trade_result.entry_value:,.2f}")
                        else:
                            self.last_signals[symbol]['action'] = 'REJECTED'
                            logger.warning(f"⚠️ TRADE RECHAZADO para {symbol}: {trade_result.message}")
                    elif best_signal.signal_type in ['BUY', 'SELL']:
                        logger.warning(f"⚠️ {symbol}: Señal {best_signal.signal_type} con confianza insuficiente ({best_confidence:.1f}% < 65%)")
                        self.last_signals[symbol]['action'] = 'LOW_CONFIDENCE'
                    else:
                        logger.info(f"⏸️ {symbol}: MANTENER POSICIÓN (HOLD)")
                        self.last_signals[symbol]['action'] = 'HOLD'
                else:
                    logger.error(f"❌ No se pudo generar señal para {symbol}")
                

                
        except Exception as e:
            logger.error(f"❌ Error crítico en análisis: {e}")
            import traceback
            traceback.print_exc()
    
    async def start(self):
        """🚀 Iniciar el bot de trading en vivo"""
        self.running = True
        logger.info("🚀 Iniciando Live Trading Bot...")
        logger.info("⚠️ Modo: Paper Trading (Sin dinero real)")
        logger.info("Presiona Ctrl+C para detener")
        
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
            # Mostrar resumen final
            self.show_final_summary()
    
    def show_current_stats(self):
        """📊 Mostrar estadísticas actuales"""
        try:
            portfolio = self.paper_trader._get_portfolio_summary()
            total_value = portfolio.get('total_value', 0)
            total_pnl = portfolio.get('total_unrealized_pnl', 0)
            
            logger.info(f"💰 Balance actual: ${total_value:,.2f}")
            logger.info(f"📈 P&L Total: ${total_pnl:.2f}")
            logger.info(f"🎯 Trades ejecutados: {self.session_stats['total_trades']}")
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
    
    def show_final_summary(self):
        """📋 Mostrar resumen final de la sesión"""
        logger.info("="*60)
        logger.info("📋 RESUMEN FINAL DE LA SESIÓN")
        logger.info("="*60)
        
        try:
            portfolio = self.paper_trader._get_portfolio_summary()
            session_duration = datetime.now() - self.session_stats['start_time']
            
            logger.info(f"⏱️ Duración: {str(session_duration).split('.')[0]}")
            logger.info(f"💰 Balance Final: ${portfolio.get('total_value', 0):,.2f}")
            logger.info(f"📈 P&L Total: ${portfolio.get('total_unrealized_pnl', 0):.2f}")
            logger.info(f"🎯 Trades Ejecutados: {self.session_stats['total_trades']}")
            logger.info(f"✅ Trades Exitosos: {self.session_stats['successful_trades']}")
            
            success_rate = (self.session_stats['successful_trades'] / max(self.session_stats['total_trades'], 1)) * 100
            logger.info(f"📊 Tasa de Éxito: {success_rate:.1f}%")
            
            logger.info("¡Gracias por usar Live Trading Bot! 🚀")
        except Exception as e:
            logger.error(f"Error generando resumen final: {e}")

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
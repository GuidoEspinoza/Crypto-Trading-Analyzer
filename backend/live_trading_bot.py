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
        
        # Configuración del bot
        self.symbols = TradingBotConfig.SYMBOLS_LIVE_BOT
        self.update_interval = self.config.LIVE_UPDATE_INTERVAL
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
            logger.info(f"   • Tamaño máximo por posición: {self.trading_bot.paper_trader.max_position_size:.1f}%")
            logger.info(f"   • Exposición máxima total: {self.trading_bot.paper_trader.max_total_exposure:.1f}%")
            logger.info(f"   • Valor mínimo por trade: ${self.trading_bot.paper_trader.min_trade_value}")
            logger.info(f"   • Valor actual del portfolio: ${portfolio_performance.get('total_value', 0):,.2f}")
            
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
    
    def get_status(self):
        """Obtener estado del bot delegando al TradingBot interno"""
        return self.trading_bot.get_status()
    
    def get_detailed_report(self) -> Dict:
        """Obtener reporte detallado del bot delegando al TradingBot interno"""
        return self.trading_bot.get_detailed_report()
    
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
    
    def _show_binance_config(self, signal, trade_result):
        """
        📋 Mostrar configuración para replicar en Binance
        """
        try:
            # Extraer datos del trade ejecutado
            symbol = signal.symbol
            signal_type = signal.signal_type
            price = trade_result.entry_price if hasattr(trade_result, 'entry_price') else signal.current_price
            
            # Calcular valores para Binance
            if signal_type == "BUY":
                # Precio ligeramente por debajo para mejor ejecución
                binance_price = price * 0.9997  # 0.03% por debajo
                
                # Monto en cripto (del trade ejecutado)
                crypto_amount = trade_result.quantity if hasattr(trade_result, 'quantity') else 0
                
                # Total en USDT
                total_usdt = trade_result.entry_value if hasattr(trade_result, 'entry_value') else (crypto_amount * price)
                
                # Take Profit (3% arriba)
                take_profit_price = price * 1.03
                take_profit_pct = 3.0
                
                # Stop Loss (3% abajo)
                stop_loss_price = price * 0.97
                stop_loss_pct = 3.0
                
                logger.info("")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info("📋 CONFIGURACIÓN PARA BINANCE SPOT - ORDEN LÍMITE")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info(f"💰 PRECIO:     {binance_price:,.2f} USDT")
                logger.info(f"🪙 MONTO:      {crypto_amount:.8f} {symbol.replace('USDT', '')}")
                logger.info(f"💵 TOTAL:      {total_usdt:.2f} USDT")
                logger.info("")
                logger.info("🛡️ PROTECCIÓN (TP/SL):")
                logger.info(f"📈 TAKE PROFIT: {take_profit_price:,.2f} USDT (+{take_profit_pct:.1f}%)")
                logger.info(f"📉 STOP LOSS:   {stop_loss_price:,.2f} USDT (-{stop_loss_pct:.1f}%)")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info("")
                
            elif signal_type == "SELL":
                # Para ventas
                binance_price = price * 1.0003  # 0.03% por arriba
                
                # Obtener balance actual del activo
                from database.database import db_manager
                portfolio = db_manager.get_portfolio_summary(is_paper=True)
                asset_name = symbol.replace('USDT', '')
                crypto_balance = portfolio.get('assets', {}).get(asset_name, 0)
                
                total_usdt = crypto_balance * price
                
                logger.info("")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info("📋 CONFIGURACIÓN PARA BINANCE SPOT - VENTA LÍMITE")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info(f"💰 PRECIO:     {binance_price:,.2f} USDT")
                logger.info(f"🪙 MONTO:      {crypto_balance:.8f} {asset_name}")
                logger.info(f"💵 TOTAL:      {total_usdt:.2f} USDT")
                logger.info("🎯 ═══════════════════════════════════════════════════════════")
                logger.info("")
                
        except Exception as e:
            logger.error(f"❌ Error mostrando configuración de Binance: {e}")
    
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
            
            # Obtener valor actual del portfolio
            from database.database import db_manager
            portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
            portfolio_value = portfolio_summary.get("total_value", self.trading_bot.config.DEFAULT_PORTFOLIO_VALUE)
            
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
                        
                        # Determinar si fue exitoso (simplificado)
                        if "profit" in trade_result.message.lower() or trade_result.entry_value > 0:
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
        """📊 Mostrar estadísticas actuales usando datos del TradingBot"""
        try:
            portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            current_balance = portfolio_performance.get('cash_balance', 0)
            total_value = portfolio_performance.get('total_value', 0)
            pnl = portfolio_performance.get('total_pnl', 0)
            pnl_pct = portfolio_performance.get('total_pnl_percentage', 0)
            
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
            logger.info("="*60 + "\n")
        except Exception as e:
            logger.error(f"❌ Error mostrando estadísticas: {e}")
    
    def show_final_summary(self):
        """📋 Mostrar resumen final de la sesión usando datos del TradingBot"""
        try:
            session_duration = datetime.now() - self.session_stats['start_time']
            portfolio_performance = self.trading_bot.paper_trader.calculate_portfolio_performance()
            final_balance = portfolio_performance.get('cash_balance', 0)
            total_value = portfolio_performance.get('total_value', 0)
            total_pnl = portfolio_performance.get('total_pnl', 0)
            pnl_pct = portfolio_performance.get('total_pnl_percentage', 0)
            
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
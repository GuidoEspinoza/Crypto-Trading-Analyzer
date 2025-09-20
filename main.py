"""🚀 Universal Trading Analyzer - API Principal
FastAPI backend para análisis técnico de criptomonedas
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import ccxt
import pandas as pd
import pandas_ta as ta
from typing import Dict, List, Optional
import uvicorn
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importar configuración centralizada
from src.config.main_config import config
from src.config.config_manager import ConfigManager
from src.config.config import TradingBotConfig

# Importar nuestros indicadores avanzados
from src.core.advanced_indicators import AdvancedIndicators, FibonacciLevels, IchimokuCloud

# Importar database
from src.database import get_db, db_manager
from src.database.models import Trade, Portfolio, Strategy, TradingSignal

# 🤖 Importar Trading Engine
from src.core.trading_bot import TradingBot
# Estrategias originales removidas - usando solo enhanced strategies
from src.core.enhanced_strategies import ProfessionalRSIStrategy, MultiTimeframeStrategy, EnsembleStrategy
from src.core.paper_trader import PaperTrader
from src.core.enhanced_risk_manager import EnhancedRiskManager
# BacktestingEngine removido durante la limpieza del proyecto

# Instancias globales (se inicializan cuando se necesiten)
trading_bot = None
paper_trader = None

def get_trading_bot():
    """Obtener o crear instancia del trading bot"""
    global trading_bot
    if trading_bot is None:
        trading_bot = TradingBot()
    return trading_bot

def get_paper_trader():
    """Obtener o crear instancia del paper trader"""
    global paper_trader
    if paper_trader is None:
        paper_trader = PaperTrader()
    return paper_trader

def ensure_bot_exists():
    """Asegurar que el bot existe antes de usarlo"""
    bot = get_trading_bot()
    if bot is None:
        raise HTTPException(status_code=500, detail="Trading bot not initialized")
    return bot

# Crear instancia de FastAPI con configuración centralizada
app = FastAPI(
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    docs_url=config.api.docs_url,
    redoc_url=config.api.redoc_url
)

# Configurar CORS con configuración centralizada
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)

# Inicializar exchange con configuración centralizada
exchange = getattr(ccxt, config.exchange.exchange_name)({
    'sandbox': config.exchange.sandbox,
    'enableRateLimit': config.exchange.enable_rate_limit,
})

# Modelos Pydantic para requests
class BotConfigUpdate(BaseModel):
    analysis_interval_minutes: Optional[int] = None
    max_daily_trades: Optional[int] = None
    min_confidence_threshold: Optional[float] = None
    enable_trading: Optional[bool] = None
    symbols: Optional[List[str]] = None
    trading_mode: Optional[str] = None  # "paper" or "live"

class TradingModeUpdate(BaseModel):
    trading_mode: str  # "paper" or "live"
    confirm_live_trading: Optional[bool] = False  # Confirmación requerida para trading real

# 🔧 **UTILIDADES**

@app.get("/")
async def root():
    """
    🏠 Endpoint raíz - Información de la API
    """
    return {
        "message": "🤖 Universal Trading Analyzer API v4.0 + Autonomous Trading Bot",
        "status": "active",
        "endpoints": {
            "utilities": {
                "title": "🔧 Utilidades",
                "endpoints": [
                    "GET / - Información de la API",
                    "GET /health - Estado de salud del servidor"
                ]
            },
            "trading_bot": {
                "title": "🤖 Trading Bot",
                "endpoints": [
                    "GET /bot/status - Estado del bot",
                    "POST /bot/start - Iniciar trading bot",
                    "POST /bot/stop - Detener trading bot",
                    "GET /bot/report - Reporte detallado",
                    "GET /bot/config - Configuración actual",
                    "PUT /bot/config - Actualizar configuración",
                    "POST /bot/force-analysis - Análisis forzado",
                    "POST /bot/emergency-stop - Parada de emergencia"
                ]
            },
            "real_time_analysis": {
                "title": "📊 Análisis en tiempo real",
                "endpoints": [
                    "GET /enhanced/analyze/{strategy_name}/{symbol} - Análisis con estrategias avanzadas",
                    "GET /test/strategy/{strategy_name}/{symbol} - Prueba de estrategias",
                    "GET /enhanced/risk-analysis/{symbol} - Análisis de riesgo",
                    "GET /enhanced/strategies/list - Lista de estrategias disponibles"
                ]
            }
        },
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    🏥 Estado de salud del servidor
    """
    try:
        # Verificar conexión a exchange
        ticker = exchange.fetch_ticker(config.exchange.default_symbol)
        exchange_status = "connected" if ticker else "disconnected"
        
        # Verificar base de datos
        db_status = "connected" if db_manager else "disconnected"
        
        # Verificar trading bot
        bot_status = "not_initialized"
        if trading_bot is not None:
            bot_status = "running" if trading_bot.is_running else "stopped"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "exchange": exchange_status,
                "database": db_status,
                "trading_bot": bot_status
            },
            "version": config.api.version
        }
    except Exception as e:
        raise HTTPException(status_code=config.error.service_unavailable_code, detail=f"Service unhealthy: {str(e)}")

# 🤖 **TRADING BOT**

@app.get("/bot/status")
async def get_bot_status():
    """
    📊 Obtener estado actual del trading bot
    """
    try:
        bot = ensure_bot_exists()
        status = bot.get_status()
        
        return {
            "status": "success",
            "bot_status": {
                "is_running": status.is_running,
                "uptime": status.uptime,
                "total_signals_generated": status.total_signals_generated,
                "total_trades_executed": status.total_trades_executed,
                "successful_trades": status.successful_trades,
                "win_rate": (status.successful_trades / max(1, status.total_trades_executed)) * 100,
                "current_portfolio_value": status.current_portfolio_value,
                "total_pnl": status.total_pnl,
                "total_return_percentage": ((status.current_portfolio_value - config.trading_bot.initial_portfolio_value) / config.trading_bot.initial_portfolio_value) * 100,
                "active_strategies": status.active_strategies,
                "last_analysis_time": status.last_analysis_time.isoformat(),
                "next_analysis_time": status.next_analysis_time.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bot status: {str(e)}")

@app.get("/bot/debug")
async def get_bot_debug_info():
    """
    🔍 Obtener información de debug del trading bot incluyendo circuit breaker
    """
    try:
        bot = ensure_bot_exists()
        status = bot.get_status()
        
        # Obtener información del circuit breaker
        circuit_breaker_info = getattr(status, 'circuit_breaker_info', {})
        
        return {
            "status": "success",
            "debug_info": {
                "is_running": status.is_running,
                "enable_trading": getattr(bot, 'enable_trading', True),
                "circuit_breaker": circuit_breaker_info,
                "current_drawdown": getattr(bot, 'current_drawdown', 0),
                "max_drawdown_threshold": getattr(bot, 'max_drawdown_threshold', 0),
                "peak_portfolio_value": getattr(bot, 'peak_portfolio_value', 0),
                "signals_generated": status.total_signals_generated,
                "trades_executed": status.total_trades_executed,
                "can_execute_trade": bot._can_execute_trade() if hasattr(bot, '_can_execute_trade') else None
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting debug info: {str(e)}")

@app.post("/bot/start")
async def start_trading_bot():
    """
    🚀 Iniciar el trading bot
    """
    try:
        bot = get_trading_bot()
        if bot.is_running:
            return {
                "status": "warning",
                "message": "🤖 Trading bot is already running",
                "bot_status": bot.get_status().is_running,
                "timestamp": datetime.now().isoformat()
            }
        
        bot.start()
        
        return {
            "status": "success",
            "message": "🚀 Trading bot started successfully!",
            "bot_status": {
                "is_running": True,
                "analysis_interval": getattr(bot, 'analysis_interval', config.trading_bot.analysis_interval_minutes),
                "strategies": list(getattr(bot, 'strategies', {}).keys()),
                "symbols": getattr(bot, 'symbols', config.trading_bot.default_symbols),
                "min_confidence": getattr(bot, 'min_confidence_threshold', config.trading_bot.min_confidence_threshold)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting bot: {str(e)}")

@app.post("/bot/stop")
async def stop_trading_bot():
    """
    🛑 Detener el trading bot
    """
    try:
        if trading_bot is None or not trading_bot.is_running:
            return {
                "status": "warning",
                "message": "🤖 Trading bot is not running",
                "bot_status": False,
                "timestamp": datetime.now().isoformat()
            }
        
        trading_bot.stop()
        
        return {
            "status": "success",
            "message": "🛑 Trading bot stopped successfully",
            "bot_status": False,
            "final_stats": {
                "total_signals": getattr(trading_bot, 'stats', {}).get("signals_generated", 0),
                "total_trades": getattr(trading_bot, 'stats', {}).get("trades_executed", 0),
                "successful_trades": getattr(trading_bot, 'stats', {}).get("successful_trades", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping bot: {str(e)}")

@app.get("/bot/report")
async def get_bot_detailed_report():
    """
    📋 Obtener reporte detallado del trading bot
    """
    try:
        bot = ensure_bot_exists()
        report = bot.get_detailed_report() if hasattr(bot, 'get_detailed_report') else {"message": "Report not available"}
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")












@app.post("/bot/emergency-stop")
async def emergency_stop_bot():
    """
    🚨 Parada de emergencia del bot
    """
    try:
        bot = ensure_bot_exists()
        if hasattr(bot, 'emergency_stop'):
            bot.emergency_stop()
        elif hasattr(bot, 'stop'):
            bot.stop()
        else:
            raise HTTPException(status_code=501, detail="Emergency stop not implemented")
        
        return {
            "status": "success",
            "message": "🚨 Emergency stop executed successfully",
            "actions_taken": [
                "Bot stopped immediately",
                "All open positions logged",
                "Emergency procedures activated"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during emergency stop: {str(e)}")

#  **ANÁLISIS EN TIEMPO REAL**

@app.get("/enhanced/strategies/list")
async def get_enhanced_strategies():
    """📊 Obtener lista de estrategias mejoradas disponibles"""
    try:
        strategies_list = []
        for key, strategy_info in config.strategy.available_strategies.items():
            strategy_data = {
                "name": strategy_info["name"],
                "description": strategy_info["description"],
                "features": strategy_info["features"]
            }
            
            # Para MultiTimeframe, mostrar los timeframes del perfil actual
            if strategy_info["name"] == "MultiTimeframe":
                trading_config = TradingBotConfig()
                current_timeframes = trading_config.get_professional_timeframes()
                timeframes_str = ", ".join(current_timeframes)
                strategy_data["description"] = f"Análisis multi-timeframe con votación ponderada (Perfil actual: {timeframes_str})"
                strategy_data["features"] = [f"{timeframes_str} analysis", "Weighted voting", "Confluence scoring"]
            
            strategies_list.append(strategy_data)
        
        return {
            "enhanced_strategies": strategies_list,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enhanced/analyze/{strategy_name}/{symbol}")
async def analyze_with_enhanced_strategy(strategy_name: str, symbol: str, timeframe: str = None):
    """🔍 Analizar símbolo con estrategia mejorada"""
    if timeframe is None:
        timeframe = config.analysis.default_timeframe
    """🔍 Analizar símbolo con estrategia mejorada"""
    try:
        # Crear instancia de la estrategia
        if strategy_name.lower() == "professionalrsi":
            strategy = ProfessionalRSIStrategy()
        elif strategy_name.lower() == "multitimeframe":
            strategy = MultiTimeframeStrategy()
        elif strategy_name.lower() == "ensemble":
            strategy = EnsembleStrategy()
        else:
            raise HTTPException(status_code=400, detail=f"Estrategia '{strategy_name}' no encontrada")
        
        # Analizar
        signal = strategy.analyze(symbol, timeframe)
        
        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": {
                "type": signal.signal_type,
                "confidence": signal.confidence_score,
                "strength": signal.strength,
                "price": signal.price,
                "volume_confirmation": signal.volume_confirmation,
                "trend_confirmation": signal.trend_confirmation,
                "risk_reward_ratio": signal.risk_reward_ratio,
                "stop_loss_price": signal.stop_loss_price,
                "take_profit_price": signal.take_profit_price,
                "market_regime": signal.market_regime,
                "confluence_score": signal.confluence_score,
                "notes": signal.notes
            },
            "timestamp": signal.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/test/strategy/{strategy_name}/{symbol}")
async def test_strategy_comprehensive(strategy_name: str, symbol: str, 
                                    timeframe: str = None,
                                    test_mode: str = "signal_only"):
    """🧪 Prueba comprehensiva de estrategias con diferentes modos"""
    if timeframe is None:
        timeframe = config.analysis.default_timeframe
    """🧪 Prueba comprehensiva de estrategias con diferentes modos"""
    try:
        # Crear estrategia
        if strategy_name.lower() == "professionalrsi":
            strategy = ProfessionalRSIStrategy()
        elif strategy_name.lower() == "multitimeframe":
            strategy = MultiTimeframeStrategy()
        elif strategy_name.lower() == "ensemble":
            strategy = EnsembleStrategy()
        else:
            raise HTTPException(status_code=400, detail=f"Estrategia '{strategy_name}' no encontrada")
        
        # Analizar señal
        signal = strategy.analyze(symbol, timeframe)
        
        # Análisis de riesgo si está disponible
        risk_analysis = None
        if test_mode in ["full", "risk_analysis"]:
            try:
                risk_manager = EnhancedRiskManager()
                risk_assessment = risk_manager.assess_trade_risk(signal, 10000)
                risk_analysis = {
                    "overall_risk_score": risk_assessment.overall_risk_score,
                    "risk_level": risk_assessment.risk_level.value,
                    "position_sizing": {
                        "recommended_size": risk_assessment.position_sizing.recommended_size,
                        "max_position_size": risk_assessment.position_sizing.max_position_size,
                        "risk_per_trade": risk_assessment.position_sizing.risk_per_trade
                    },
                    "recommendations": risk_assessment.recommendations
                }
            except Exception as risk_error:
                risk_analysis = {"error": f"Error en análisis de riesgo: {str(risk_error)}"}
        
        # Backtesting rápido si está en modo completo
        quick_backtest = None
        if test_mode == "full":
            try:
                from datetime import timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)  # Último mes
                
                config = BacktestConfig(
                    symbols=[symbol],
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=10000,
                    timeframe=timeframe
                )
                
                engine = BacktestingEngine(config)
                metrics = engine.run_backtest(strategy, start_date, end_date)
                
                quick_backtest = {
                    "period": "last_30_days",
                    "total_return": metrics.total_return,
                    "win_rate": metrics.win_rate,
                    "total_trades": metrics.total_trades,
                    "sharpe_ratio": metrics.sharpe_ratio
                }
            except Exception as bt_error:
                quick_backtest = {"error": f"Error en backtesting rápido: {str(bt_error)}"}
        
        return {
            "strategy_test_results": {
                "strategy_name": strategy_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "test_mode": test_mode,
                "signal_analysis": {
                    "action": signal.signal_type if signal else "NO_SIGNAL",
                    "confidence": signal.confidence_score if signal else 0,
                    "entry_price": signal.price if signal else None,
                    "stop_loss_price": getattr(signal, 'stop_loss_price', None) if signal else None,
                    "take_profit_price": getattr(signal, 'take_profit_price', None) if signal else None,
                    "volume_confirmation": getattr(signal, 'volume_confirmation', None) if signal else None,
                    "market_regime": getattr(signal, 'market_regime', None) if signal else None,
                    "risk_reward_ratio": getattr(signal, 'risk_reward_ratio', None) if signal else None,
                    "notes": signal.notes if signal else "No signal generated"
                },
                "risk_analysis": risk_analysis,
                "quick_backtest": quick_backtest
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en prueba de estrategia: {str(e)}")

@app.get("/enhanced/risk-analysis/{symbol}")
async def get_enhanced_risk_analysis(symbol: str, timeframe: str = None):
    """🛡️ Análisis de riesgo mejorado"""
    if timeframe is None:
        timeframe = config.analysis.default_timeframe
    try:
        # Crear señal de prueba para análisis
        strategy = ProfessionalRSIStrategy()
        signal = strategy.analyze(symbol, timeframe)
        
        # Analizar riesgo
        risk_manager = EnhancedRiskManager()
        risk_assessment = risk_manager.assess_trade_risk(signal, 10000)
        
        return {
            "symbol": symbol,
            "risk_analysis": {
                "overall_risk_score": risk_assessment.overall_risk_score,
                "risk_level": risk_assessment.risk_level.value,
                "position_sizing": {
                    "recommended_size": risk_assessment.position_sizing.recommended_size,
                    "max_position_size": risk_assessment.position_sizing.max_position_size,
                    "risk_per_trade": risk_assessment.position_sizing.risk_per_trade
                },
                "stop_loss": {
                    "price": risk_assessment.dynamic_stop_loss.stop_loss_price,
                    "type": risk_assessment.dynamic_stop_loss.stop_type,
                    "trailing_distance": risk_assessment.dynamic_stop_loss.trailing_distance
                },
                "recommendations": risk_assessment.recommendations,
                "market_risk_factors": risk_assessment.market_risk_factors
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🎭 Paper Trading Endpoints
@app.get("/paper-trading/summary")
async def get_paper_trading_summary(force_refresh: bool = False):
    """
    📊 Obtener resumen del portfolio de paper trading
    
    Args:
        force_refresh: Si es True, fuerza la actualización del caché
    """
    try:
        # Verificar si los datos están en caché ANTES de llamar al método
        cache_key = "portfolio_summary_True"
        was_cached = (not force_refresh and 
                     hasattr(db_manager, '_query_cache') and 
                     cache_key in db_manager._query_cache and
                     db_manager._is_cache_valid(cache_key))
        
        # Si se solicita forzar actualización, invalidar caché específico
        if force_refresh:
            if hasattr(db_manager, '_query_cache') and cache_key in db_manager._query_cache:
                del db_manager._query_cache[cache_key]
            if hasattr(db_manager, '_cache_timestamps') and cache_key in db_manager._cache_timestamps:
                del db_manager._cache_timestamps[cache_key]
        
        summary = db_manager.get_portfolio_summary(is_paper=True)
        return {
            "status": "success",
            "portfolio": summary,
            "timestamp": datetime.now().isoformat(),
            "from_cache": was_cached
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/paper-trading/positions")
async def get_paper_trading_positions():
    """
    📈 Obtener posiciones abiertas del portfolio
    """
    try:
        paper_trader = PaperTrader()
        positions = paper_trader.get_open_positions()
        return {
            "status": "success",
            "positions": positions,
            "total_positions": len(positions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/paper-trading/performance")
async def get_paper_trading_performance():
    """
    📊 Obtener métricas de performance del portfolio
    """
    try:
        paper_trader = PaperTrader()
        performance = paper_trader.calculate_portfolio_performance()
        return {
            "status": "success",
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/paper-trading/reset")
async def reset_paper_trading():
    """
    🔄 Resetear el portfolio de paper trading a los valores por defecto
    """
    try:
        # Usar la instancia del trading bot para acceder al paper_trader correcto
        bot = get_trading_bot()
        result = bot.paper_trader.reset_portfolio()
        
        if result["success"]:
            # Forzar invalidación inmediata del caché específico del portfolio summary
            cache_key = "portfolio_summary_True"
            if hasattr(db_manager, '_query_cache') and cache_key in db_manager._query_cache:
                del db_manager._query_cache[cache_key]
            if hasattr(db_manager, '_cache_timestamps') and cache_key in db_manager._cache_timestamps:
                del db_manager._cache_timestamps[cache_key]
            
            # Limpiar todo el caché para asegurar consistencia
            db_manager.clear_cache()
            
            return {
                "status": "success",
                "message": result["message"],
                "initial_balance": config.paper_trading.initial_balance,
                "timestamp": result["timestamp"],
                "cache_cleared": True
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ejecutar servidor si se ejecuta directamente
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False
    )
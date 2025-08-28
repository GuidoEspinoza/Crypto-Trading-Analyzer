"""
🚀 Universal Trading Analyzer - API Principal
FastAPI backend para análisis técnico de criptomonedas
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import ccxt
import pandas as pd
import pandas_ta as ta
from typing import Dict, List, Optional
import uvicorn
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importar nuestros indicadores avanzados
from advanced_indicators import AdvancedIndicators, FibonacciLevels, IchimokuCloud

# Importar database
from database import get_db, db_manager
from database.models import Trade, Portfolio, Strategy, TradingSignal

# 🤖 Importar Trading Engine
from trading_engine.trading_bot import trading_bot
# Estrategias originales removidas - usando solo enhanced strategies
from trading_engine.enhanced_strategies import ProfessionalRSIStrategy, MultiTimeframeStrategy, EnsembleStrategy
from trading_engine.paper_trader import PaperTrader
from trading_engine.enhanced_risk_manager import EnhancedRiskManager
# BacktestingEngine removido durante la limpieza del proyecto

# Crear instancia de FastAPI
app = FastAPI(
    title="🚀 Universal Trading Analyzer + Trading Bot",
    description="API para análisis técnico de criptomonedas en tiempo real + Trading Bot automático",
    version="4.0.0",  # ¡Actualizada con Trading Bot!
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar exchange (Binance público, sin API keys)
exchange = ccxt.binance({
    'sandbox': False,
    'enableRateLimit': True,
})

# Modelos Pydantic para requests
class BotConfigUpdate(BaseModel):
    analysis_interval_minutes: Optional[int] = None
    max_daily_trades: Optional[int] = None
    min_confidence_threshold: Optional[float] = None
    enable_trading: Optional[bool] = None
    symbols: Optional[List[str]] = None

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
        ticker = exchange.fetch_ticker('BTC/USDT')
        exchange_status = "connected" if ticker else "disconnected"
        
        # Verificar base de datos
        db_status = "connected" if db_manager else "disconnected"
        
        # Verificar trading bot
        bot_status = "running" if trading_bot.is_running else "stopped"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "exchange": exchange_status,
                "database": db_status,
                "trading_bot": bot_status
            },
            "version": "4.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# 🤖 **TRADING BOT**

@app.get("/bot/status")
async def get_bot_status():
    """
    📊 Obtener estado actual del trading bot
    """
    try:
        status = trading_bot.get_status()
        
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
                "total_return_percentage": ((status.current_portfolio_value - 10000) / 10000) * 100,
                "active_strategies": status.active_strategies,
                "last_analysis_time": status.last_analysis_time.isoformat(),
                "next_analysis_time": status.next_analysis_time.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bot status: {str(e)}")

@app.post("/bot/start")
async def start_trading_bot():
    """
    🚀 Iniciar el trading bot
    """
    try:
        if trading_bot.is_running:
            return {
                "status": "warning",
                "message": "🤖 Trading bot is already running",
                "bot_status": trading_bot.get_status().is_running,
                "timestamp": datetime.now().isoformat()
            }
        
        trading_bot.start()
        
        return {
            "status": "success",
            "message": "🚀 Trading bot started successfully!",
            "bot_status": {
                "is_running": True,
                "analysis_interval": trading_bot.analysis_interval,
                "strategies": list(trading_bot.strategies.keys()),
                "symbols": trading_bot.symbols,
                "min_confidence": trading_bot.min_confidence_threshold
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
        if not trading_bot.is_running:
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
                "total_signals": trading_bot.stats["signals_generated"],
                "total_trades": trading_bot.stats["trades_executed"],
                "successful_trades": trading_bot.stats["successful_trades"]
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
        report = trading_bot.get_detailed_report()
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/bot/config")
async def get_bot_configuration():
    """
    ⚙️ Obtener configuración actual del bot
    """
    try:
        return {
            "status": "success",
            "configuration": {
                "analysis_interval_minutes": trading_bot.analysis_interval,
                "max_daily_trades": trading_bot.max_daily_trades,
                "min_confidence_threshold": trading_bot.min_confidence_threshold,
                "enable_trading": trading_bot.enable_trading,
                "symbols": trading_bot.symbols,
                "strategies": list(trading_bot.strategies.keys())
            },
            "current_stats": {
                "daily_trades": trading_bot.stats["daily_trades"],
                "signals_generated": trading_bot.stats["signals_generated"],
                "trades_executed": trading_bot.stats["trades_executed"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting configuration: {str(e)}")

@app.put("/bot/config")
async def update_bot_configuration(config: BotConfigUpdate):
    """
    ⚙️ Actualizar configuración del bot
    """
    try:
        # Convertir a diccionario eliminando valores None
        config_dict = {k: v for k, v in config.dict().items() if v is not None}
        
        if not config_dict:
            raise HTTPException(status_code=400, detail="No configuration parameters provided")
        
        trading_bot.update_configuration(config_dict)
        
        return {
            "status": "success",
            "message": "⚙️ Bot configuration updated successfully",
            "updated_config": config_dict,
            "current_config": {
                "analysis_interval_minutes": trading_bot.analysis_interval,
                "max_daily_trades": trading_bot.max_daily_trades,
                "min_confidence_threshold": trading_bot.min_confidence_threshold,
                "enable_trading": trading_bot.enable_trading,
                "symbols": trading_bot.symbols
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@app.post("/bot/force-analysis")
async def force_immediate_analysis():
    """
    🔄 Forzar análisis inmediato del mercado
    """
    try:
        if not trading_bot.is_running:
            raise HTTPException(status_code=400, detail="Bot must be running to force analysis")
        
        # Ejecutar análisis en background
        trading_bot.force_analysis()
        
        return {
            "status": "success",
            "message": "🔄 Immediate market analysis initiated",
            "timestamp": datetime.now().isoformat(),
            "note": "Check bot logs or status for analysis results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forcing analysis: {str(e)}")

@app.post("/bot/emergency-stop")
async def emergency_stop_bot():
    """
    🚨 Parada de emergencia del bot
    """
    try:
        trading_bot.emergency_stop()
        
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

# 📊 **ANÁLISIS EN TIEMPO REAL**

@app.get("/enhanced/strategies/list")
async def get_enhanced_strategies():
    """📊 Obtener lista de estrategias mejoradas disponibles"""
    try:
        return {
            "enhanced_strategies": [
                {
                    "name": "ProfessionalRSI",
                    "description": "RSI profesional con análisis de volumen y tendencia",
                    "features": ["Volume confirmation", "Trend analysis", "Risk management"]
                },
                {
                    "name": "MultiTimeframe", 
                    "description": "Análisis multi-timeframe con votación ponderada",
                    "features": ["1h, 4h, 1d analysis", "Weighted voting", "Confluence scoring"]
                },
                {
                    "name": "Ensemble",
                    "description": "Estrategia ensemble que combina múltiples señales",
                    "features": ["Multiple strategies", "Intelligent voting", "Advanced risk management"]
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enhanced/analyze/{strategy_name}/{symbol}")
async def analyze_with_enhanced_strategy(strategy_name: str, symbol: str, timeframe: str = "1h"):
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
                                    timeframe: str = "1h",
                                    test_mode: str = "signal_only"):
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
async def get_enhanced_risk_analysis(symbol: str):
    """🛡️ Análisis de riesgo mejorado"""
    try:
        # Crear señal de prueba para análisis
        strategy = ProfessionalRSIStrategy()
        signal = strategy.analyze(symbol, "1h")
        
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
async def get_paper_trading_summary():
    """
    📊 Obtener resumen del portfolio de paper trading
    """
    try:
        summary = db_manager.get_portfolio_summary(is_paper=True)
        return {
            "status": "success",
            "portfolio": summary,
            "timestamp": datetime.now().isoformat()
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
        paper_trader = PaperTrader()
        result = paper_trader.reset_portfolio()
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"],
                "initial_balance": result["initial_balance"],
                "timestamp": result["timestamp"]
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
        reload=True
    )
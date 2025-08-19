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
from trading_engine.strategies import RSIStrategy, MACDStrategy, IchimokuStrategy
from trading_engine.paper_trader import PaperTrader
from trading_engine.risk_manager import RiskManager

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

@app.get("/")
async def root():
    """
    🏠 Endpoint raíz - Bienvenida a la API
    """
    return {
        "message": "🤖 Universal Trading Analyzer API v4.0 + Autonomous Trading Bot",
        "status": "active",
        "features": [
            "💰 Precios en tiempo real",
            "📊 Indicadores técnicos básicos",
            "🔥 Indicadores avanzados",
            "🕯️ Patrones de velas japonesas",
            "☁️ Ichimoku Cloud",
            "🔢 Fibonacci Retracements",
            "🎯 Señales de trading profesionales",
            "🗄️ Base de datos SQLite",
            "🤖 Trading Bot Automático 24/7",
            "🛡️ Risk Management Avanzado",
            "🎭 Paper Trading Inteligente",
            "📈 Portfolio Management",
            "📊 Backtesting Engine"
        ],
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "trading_bot": {
            "status": "available",
            "endpoints": [
                "/bot/status",
                "/bot/start", 
                "/bot/stop",
                "/bot/report",
                "/bot/config"
            ]
        }
    }

# 🤖 **ENDPOINTS DEL TRADING BOT**

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

# 🧪 **ENDPOINTS PARA TESTING MANUAL DE ESTRATEGIAS**

@app.get("/bot/test-strategy/{strategy_name}/{symbol}")
async def test_strategy_manual(strategy_name: str, symbol: str, timeframe: str = "1h"):
    """
    🧪 Probar una estrategia manualmente
    """
    try:
        strategies = {
            "rsi": RSIStrategy(),
            "macd": MACDStrategy(), 
            "ichimoku": IchimokuStrategy()
        }
        
        if strategy_name.lower() not in strategies:
            raise HTTPException(status_code=400, detail=f"Strategy '{strategy_name}' not found. Available: {list(strategies.keys())}")
        
        strategy = strategies[strategy_name.lower()]
        signal = strategy.analyze(symbol, timeframe)
        
        return {
            "status": "success",
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": {
                "type": signal.signal_type,
                "confidence_score": signal.confidence_score,
                "strength": signal.strength,
                "price": signal.price,
                "indicators_data": signal.indicators_data,
                "notes": signal.notes,
                "timestamp": signal.timestamp.isoformat()
            },
            "recommendation": "🟢 EXECUTE" if signal.confidence_score >= 65 else "🔴 SKIP",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing strategy: {str(e)}")

@app.get("/bot/risk-analysis/{symbol}")
async def get_risk_analysis(symbol: str):
    """
    🛡️ Obtener análisis de riesgo para un símbolo
    """
    try:
        # Crear señal simulada para análisis
        risk_manager = RiskManager()
        portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
        portfolio_value = portfolio_summary.get("total_value", 10000)
        
        # Obtener precio actual
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Crear señal dummy para análisis
        from trading_engine.strategies import TradingSignal
        dummy_signal = TradingSignal(
            symbol=symbol,
            strategy_name="Risk_Analysis",
            signal_type="BUY",
            price=current_price,
            confidence_score=70.0,
            strength="Moderate",
            timestamp=datetime.now(),
            indicators_data={},
            notes="Risk analysis simulation"
        )
        
        risk_assessment = risk_manager.assess_trade_risk(dummy_signal, portfolio_value)
        
        return {
            "status": "success",
            "symbol": symbol,
            "current_price": current_price,
            "portfolio_value": portfolio_value,
            "risk_assessment": {
                "is_approved": risk_assessment.is_approved,
                "risk_score": risk_assessment.risk_score,
                "recommended_position_size": f"{risk_assessment.position_size:.1%}",
                "stop_loss": risk_assessment.stop_loss,
                "take_profit": risk_assessment.take_profit,
                "max_loss_amount": risk_assessment.max_loss_amount,
                "risk_reason": risk_assessment.risk_reason,
                "recommendations": risk_assessment.recommendations
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing risk: {str(e)}")

# ... resto de tus endpoints existentes (mantener todos los de database, price, etc.)

@app.get("/health")
async def health_check():
    """
    ❤️ Health check - Verificar estado de la API, base de datos y trading bot
    """
    try:
        # Verificar conexión con Binance
        ticker = exchange.fetch_ticker('BTC/USDT')
        
        # Verificar base de datos
        with db_manager.get_db_session() as session:
            db_status = "connected"
            trade_count = session.query(Trade).count()
        
        # Verificar estado del bot
        bot_status = trading_bot.get_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "exchange_connection": "OK",
            "database_connection": db_status,
            "trading_bot": {
                "is_running": bot_status.is_running,
                "uptime": bot_status.uptime,
                "total_trades": trade_count,
                "portfolio_value": bot_status.current_portfolio_value
            },
            "last_btc_price": ticker['last'],
            "api_version": "4.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Ejecutar servidor si se ejecuta directamente
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
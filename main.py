"""
🚀 Universal Trading Analyzer - API Principal
FastAPI backend para análisis técnico de criptomonedas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
import uvicorn
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 🤖 Importar Trading Engine
from src.core.trading_bot import TradingBot
# Estrategias mejoradas
# Estrategias originales removidas - solo se usan las profesionales avanzadas
from src.core.professional_adapter import ProfessionalStrategyAdapter
from src.core.paper_trader import PaperTrader
from src.core.enhanced_risk_manager import EnhancedRiskManager
# Capital.com API Client
from src.core.capital_client import CapitalClient, create_capital_client_from_env

# Balance Manager
from src.core.balance_manager import start_balance_manager, stop_balance_manager, get_current_balance_sync

# Importar configuración global
from src.config.main_config import GLOBAL_SYMBOLS, TradingProfiles
import re
import os

# Load environment variables
load_dotenv('.env')

# Instancias globales (se inicializan cuando se necesiten)
trading_bot = None
paper_trader = None
capital_client = None

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

def get_capital_client():
    """Obtener o crear instancia del cliente de Capital.com"""
    global capital_client
    if capital_client is None:
        capital_client = create_capital_client_from_env()
        # Crear sesión automáticamente
        try:
            capital_client.create_session()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Capital.com: {str(e)}")
    return capital_client

def ensure_bot_exists():
    """Asegurar que el bot existe antes de usarlo"""
    bot = get_trading_bot()
    if bot is None:
        raise HTTPException(status_code=500, detail="Trading bot not initialized")
    return bot

def change_trading_profile(new_profile: str) -> bool:
    """
    Cambiar el perfil de trading modificando el archivo main_config.py
    
    Args:
        new_profile: Nuevo perfil a establecer ("SCALPING", "INTRADAY")
    
    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    try:
        config_file_path = os.path.join(os.path.dirname(__file__), "src", "config", "main_config.py")
        
        # Leer el archivo actual
        with open(config_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Buscar y reemplazar la línea TRADING_PROFILE
        pattern = r'TRADING_PROFILE\s*=\s*["\'][^"\']*["\']'
        replacement = f'TRADING_PROFILE = "{new_profile}"'
        
        # Verificar que el patrón existe
        if not re.search(pattern, content):
            return False
        
        # Realizar el reemplazo
        new_content = re.sub(pattern, replacement, content)
        
        # Escribir el archivo modificado
        with open(config_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"Error cambiando perfil de trading: {str(e)}")
        return False

# Crear instancia de FastAPI
app = FastAPI(
    title="🚀 Universal Trading Analyzer + Trading Bot",
    description="API para análisis técnico de metales preciosos en tiempo real + Trading Bot automático",
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

# Eventos de startup y shutdown
@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar el servidor"""
    try:
        # Inicializar Balance Manager
        await start_balance_manager()
        print("✅ Balance Manager iniciado correctamente")
    except Exception as e:
        print(f"❌ Error iniciando Balance Manager: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar el servidor"""
    try:
        # Detener Balance Manager
        await stop_balance_manager()
        print("✅ Balance Manager detenido correctamente")
    except Exception as e:
        print(f"❌ Error deteniendo Balance Manager: {e}")

# Capital.com client se inicializa bajo demanda usando get_capital_client()

# Modelos Pydantic para requests
class BotConfigUpdate(BaseModel):
    # Configuraciones básicas del bot
    analysis_interval_minutes: Optional[int] = Field(None, ge=1, description="Intervalo de análisis en minutos")
    max_daily_trades: Optional[int] = Field(None, ge=1, description="Límite máximo de operaciones diarias")
    min_confidence_threshold: Optional[float] = Field(None, ge=0, le=100, description="Umbral mínimo de confianza (%) entre 0 y 100")
    enable_trading: Optional[bool] = Field(None, description="Habilitar/deshabilitar ejecución de trades")
    symbols: Optional[List[str]] = Field(None, description="Lista de símbolos a monitorear")
    trading_mode: Optional[str] = Field(None, description="Modo de trading ('paper' o 'live') - actualmente solo 'paper'")
    
    # Configuraciones de posiciones y riesgo
    max_concurrent_positions: Optional[int] = Field(None, ge=1, description="Máximo número de posiciones concurrentes")
    max_position_size: Optional[float] = Field(None, ge=0.01, le=1.0, description="Tamaño máximo de posición como porcentaje del balance (0.01-1.0)")
    max_total_exposure: Optional[float] = Field(None, ge=0.01, le=1.0, description="Exposición total máxima como porcentaje del balance (0.01-1.0)")
    min_trade_value: Optional[float] = Field(None, ge=1.0, description="Valor mínimo de trade en USD")
    
    # Configuraciones de timeframes
    primary_timeframe: Optional[str] = Field(None, description="Timeframe principal para análisis (ej: '1h', '4h', '1d')")
    confirmation_timeframe: Optional[str] = Field(None, description="Timeframe de confirmación (ej: '15m', '1h', '4h')")
    trend_timeframe: Optional[str] = Field(None, description="Timeframe para análisis de tendencia (ej: '4h', '1d')")
    
    # Configuraciones de gestión de riesgo
    max_risk_per_trade: Optional[float] = Field(None, ge=0.1, le=5.0, description="Riesgo máximo por trade como porcentaje del balance (0.1-5.0)")
    max_daily_risk: Optional[float] = Field(None, ge=0.5, le=10.0, description="Riesgo máximo diario como porcentaje del balance (0.5-10.0)")
    max_drawdown_threshold: Optional[float] = Field(None, ge=0.05, le=0.5, description="Umbral máximo de drawdown como decimal (0.05-0.5)")
    correlation_threshold: Optional[float] = Field(None, ge=0.1, le=1.0, description="Umbral de correlación para evitar posiciones similares (0.1-1.0)")
    
    # Configuraciones de trading real
    enable_real_trading: Optional[bool] = Field(None, description="Habilitar trading real (requiere configuración adicional)")
    real_trading_size_multiplier: Optional[float] = Field(None, ge=0.01, le=1.0, description="Multiplicador de tamaño para trading real vs paper (0.01-1.0)")

    model_config = {
        "json_schema_extra": {
            "example": {
                # Configuraciones básicas
                "analysis_interval_minutes": 15,
                "max_daily_trades": 10,
                "min_confidence_threshold": 65,
                "enable_trading": True,
                "symbols": GLOBAL_SYMBOLS,
                "trading_mode": "paper",
                
                # Configuraciones de posiciones
                "max_concurrent_positions": 5,
                "max_position_size": 0.15,
                "max_total_exposure": 0.6,
                "min_trade_value": 50.0,
                
                # Timeframes
                "primary_timeframe": "1h",
                "confirmation_timeframe": "15m",
                "trend_timeframe": "4h",
                
                # Gestión de riesgo
                "max_risk_per_trade": 1.0,
                "max_daily_risk": 3.0,
                "max_drawdown_threshold": 0.15,
                "correlation_threshold": 0.7,
                
                # Trading real
                "enable_real_trading": False,
                "real_trading_size_multiplier": 0.1
            }
        }
    }

class TradingModeUpdate(BaseModel):
    trading_mode: str  # "paper" or "live"
    confirm_live_trading: Optional[bool] = Field(False, description="Confirmación requerida para trading real")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Activar paper trading",
                    "value": {"trading_mode": "paper"}
                },
                {
                    "summary": "Solicitar trading en vivo (no implementado)",
                    "value": {"trading_mode": "live", "confirm_live_trading": True}
                }
            ]
        }
    }

class ProfileUpdate(BaseModel):
    profile: str
    restart_bot: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "profile": "INTRADAY",
                "restart_bot": True
            }
        }

class SymbolsUpdate(BaseModel):
    symbols: List[str]
    restart_bot: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "symbols": ["GOLD", "SILVER", "BTCUSD", "ETHUSD"],
                "restart_bot": True
            }
        }

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
                    "GET /bot/dashboard - Dashboard unificado del bot (con parámetro detailed opcional)",
                    "POST /bot/start - Iniciar trading bot",
                    "POST /bot/stop - Detener trading bot",
                    "GET /bot/config - Configuración completa actual",
                    "PUT /bot/config - Actualizar configuración completa",
                    "GET /bot/trading-mode - Modo de trading actual",
                    "PUT /bot/trading-mode - Cambiar modo de trading",
                    "GET /bot/trading-capabilities - Capacidades disponibles",
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
        # Verificar conexión a Capital.com
        try:
            client = get_capital_client()
            ping_result = client.ping()
            capital_status = "connected" if ping_result.get("success") else "disconnected"
        except Exception:
            capital_status = "disconnected"
        
        # Verificar trading bot
        bot_status = "not_initialized"
        if trading_bot is not None:
            bot_status = "running" if trading_bot.is_running else "stopped"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "capital_com": capital_status,
                "trading_bot": bot_status
            },
            "version": "4.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# 🤖 **TRADING BOT**

@app.get("/bot/dashboard")
async def get_bot_dashboard(detailed: bool = False):
    """
    📊 Dashboard del trading bot - Estado y reporte unificado
    
    Args:
        detailed: Si es True, incluye información detallada del bot y análisis completo
    """
    try:
        bot = ensure_bot_exists()
        status = bot.get_status()
        
        # Obtener balance inicial real del paper trader
        initial_balance = bot.paper_trader.initial_balance if bot.paper_trader else 1000.0
        
        # Información básica (siempre incluida)
        dashboard_data = {
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
                "total_return_percentage": ((status.current_portfolio_value - initial_balance) / max(1e-9, initial_balance)) * 100,
                "initial_balance": initial_balance,
                "active_strategies": status.active_strategies,
                "last_analysis_time": status.last_analysis_time.isoformat() if status.last_analysis_time else None,
                "next_analysis_time": status.next_analysis_time.isoformat() if status.next_analysis_time else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Si se solicita información detallada, agregar reporte completo
        if detailed:
            detailed_report = bot.get_detailed_report() if hasattr(bot, 'get_detailed_report') else {}
            dashboard_data["detailed_report"] = detailed_report
            dashboard_data["note"] = "Información detallada incluida - reporte completo del bot"
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bot dashboard: {str(e)}")



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
                "analysis_interval_minutes": getattr(bot, 'analysis_interval', 60),
                "strategies": list(getattr(bot, 'strategies', {}).keys()),
                "symbols": getattr(bot, 'symbols', []),
                "min_confidence_threshold": getattr(bot, 'min_confidence_threshold', 50)
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



@app.get("/bot/config")
async def get_bot_configuration():
    """
    ⚙️ Obtener configuración completa actual del bot
    
    Devuelve todas las configuraciones del trading bot incluyendo:
    - Configuraciones básicas (intervalo, límites, símbolos)
    - Gestión de posiciones y exposición
    - Timeframes de análisis
    - Configuraciones de gestión de riesgo
    - Estado del trading real
    - Estadísticas actuales del bot
    """
    try:
        bot = get_trading_bot()
        current_config = bot.get_configuration() if hasattr(bot, 'get_configuration') else {
            "analysis_interval_minutes": getattr(bot, 'analysis_interval', 60),
            "max_daily_trades": getattr(bot, 'max_daily_trades', 10),
            "min_confidence_threshold": getattr(bot, 'min_confidence_threshold', 50),
            "enable_trading": getattr(bot, 'enable_trading', False),
            "symbols": getattr(bot, 'symbols', []),
        }
        return {
            "status": "success",
            "configuration": current_config,
            "current_stats": {
                "daily_trades": getattr(bot, 'stats', {}).get("daily_trades", 0),
                "signals_generated": getattr(bot, 'stats', {}).get("signals_generated", 0),
                "trades_executed": getattr(bot, 'stats', {}).get("trades_executed", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting configuration: {str(e)}")

@app.put("/bot/config")
async def update_bot_configuration(config: BotConfigUpdate):
    """
    ⚙️ Actualizar configuración completa del bot
    
    Permite modificar todas las configuraciones del trading bot:
    
    **Configuraciones Básicas:**
    - analysis_interval_minutes: Intervalo de análisis (minutos)
    - max_daily_trades: Límite de operaciones diarias
    - min_confidence_threshold: Umbral mínimo de confianza (0-100%)
    - enable_trading: Habilitar/deshabilitar trading
    - symbols: Lista de símbolos a monitorear
    - trading_mode: Modo de trading ('paper' o 'live')
    
    **Gestión de Posiciones:**
    - max_concurrent_positions: Máximo posiciones simultáneas
    - max_position_size: Tamaño máximo por posición (% del balance)
    - max_total_exposure: Exposición total máxima (% del balance)
    - min_trade_value: Valor mínimo de trade (USD)
    
    **Timeframes de Análisis:**
    - primary_timeframe: Timeframe principal ('1h', '4h', '1d')
    - confirmation_timeframe: Timeframe de confirmación ('15m', '1h', '4h')
    - trend_timeframe: Timeframe de tendencia ('4h', '1d')
    
    **Gestión de Riesgo:**
    - max_risk_per_trade: Riesgo máximo por trade (% del balance)
    - max_daily_risk: Riesgo máximo diario (% del balance)
    - max_drawdown_threshold: Umbral máximo de drawdown (decimal)
    - correlation_threshold: Umbral de correlación entre posiciones
    
    **Trading Real (Experimental):**
    - enable_real_trading: Habilitar trading real
    - real_trading_size_multiplier: Multiplicador de tamaño para trading real
    """
    try:
        # Convertir a diccionario eliminando valores None
        config_dict = config.model_dump(exclude_none=True)
        
        if not config_dict:
            raise HTTPException(status_code=400, detail="No configuration parameters provided")
        
        bot = ensure_bot_exists()
        if hasattr(bot, 'update_configuration'):
            bot.update_configuration(config_dict)
        else:
            # Actualizar atributos manualmente si no existe el método
            for key, value in config_dict.items():
                if hasattr(bot, key):
                    setattr(bot, key, value)
        
        current_config = bot.get_configuration() if hasattr(bot, 'get_configuration') else {
            "analysis_interval_minutes": getattr(bot, 'analysis_interval', 60),
            "max_daily_trades": getattr(bot, 'max_daily_trades', 10),
            "min_confidence_threshold": getattr(bot, 'min_confidence_threshold', 50),
            "enable_trading": getattr(bot, 'enable_trading', False),
            "symbols": getattr(bot, 'symbols', [])
        }
        return {
            "status": "success",
            "message": "⚙️ Bot configuration updated successfully",
            "updated_config": config_dict,
            "current_config": current_config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@app.get("/bot/trading-mode")
async def get_trading_mode():
    """
    🎭 Obtener el modo de trading actual (paper/live)
    """
    try:
        # Por ahora, el sistema está configurado para paper trading únicamente
        # En el futuro, esto se leerá de la configuración del bot
        return {
            "status": "success",
            "trading_mode": "paper",
            "description": "Paper trading mode - Virtual trading with simulated funds",
            "live_trading_available": False,
            "warning": "Live trading is not yet implemented. All trades are simulated.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trading mode: {str(e)}")

@app.put("/bot/trading-mode")
async def update_trading_mode(mode_config: TradingModeUpdate):
    """
    🔄 Cambiar modo de trading (paper/live)
    """
    try:
        if mode_config.trading_mode not in ["paper", "live"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid trading mode. Must be 'paper' or 'live'"
            )
        
        if mode_config.trading_mode == "live":
            if not mode_config.confirm_live_trading:
                raise HTTPException(
                    status_code=400,
                    detail="Live trading requires explicit confirmation. Set 'confirm_live_trading' to true."
                )
            
            # Por ahora, rechazamos el trading en vivo ya que no está implementado
            raise HTTPException(
                status_code=501,
                detail="Live trading is not yet implemented. Currently only paper trading is supported."
            )
        
        # Para paper trading, simplemente confirmamos
        return {
            "status": "success",
            "message": "Trading mode confirmed",
            "trading_mode": "paper",
            "description": "Paper trading mode active - All trades are simulated",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error updating trading mode: {str(e)}")

@app.get("/bot/trading-capabilities")
async def get_trading_capabilities():
    """
    🔍 Obtener información sobre las capacidades de trading disponibles
    """
    try:
        return {
            "status": "success",
            "capabilities": {
                "paper_trading": {
                    "available": True,
                    "description": "Virtual trading with simulated funds",
                    "features": [
                        "Risk-free testing",
                        "Real market data",
                        "Portfolio tracking",
                        "Performance analytics",
                        "Strategy backtesting"
                    ]
                },
                "live_trading": {
                    "available": False,
                    "description": "Real trading with actual funds (Not yet implemented)",
                    "requirements": [
                        "Capital.com API integration",
                        "Enhanced security measures",
                        "Real-time order management",
                        "Advanced risk controls",
                        "Regulatory compliance"
                    ],
                    "status": "In development - Capital.com integration in progress"
                }
            },
            "current_mode": "paper",
            "recommended_mode": "paper",
            "safety_note": "Always test strategies thoroughly in paper trading before considering live trading",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trading capabilities: {str(e)}")

@app.post("/bot/force-analysis")
async def force_immediate_analysis():
    """
    🔄 Forzar análisis inmediato del mercado
    """
    try:
        bot = ensure_bot_exists()
        if not getattr(bot, 'is_running', False):
            raise HTTPException(status_code=400, detail="Bot must be running to force analysis")
        
        # Ejecutar análisis en background
        if hasattr(bot, 'force_analysis'):
            bot.force_analysis()
        else:
            raise HTTPException(status_code=501, detail="Force analysis not implemented")
        
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
        raise HTTPException(status_code=500, detail=f"Error in emergency stop: {str(e)}")

@app.get("/bot/profile")
async def get_current_profile():
    """
    📋 Obtener el perfil de trading activo actual
    """
    try:
        current_profile = TradingProfiles.get_current_profile()
        available_profiles = list(TradingProfiles.PROFILES.keys())
        
        return {
            "status": "success",
            "current_profile": {
                "name": current_profile["name"],
                "key": [k for k, v in TradingProfiles.PROFILES.items() if v == current_profile][0],
                "description": current_profile["description"],
                "analysis_interval": current_profile["analysis_interval"],
                "min_confidence": current_profile["min_confidence"],
                "max_daily_trades": current_profile["max_daily_trades"],
                "timeframes": current_profile["timeframes"]
            },
            "available_profiles": [
                {
                    "key": key,
                    "name": profile["name"],
                    "description": profile["description"],
                    "analysis_interval": profile["analysis_interval"]
                }
                for key, profile in TradingProfiles.PROFILES.items()
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting profile: {str(e)}")


@app.put("/bot/profile")
async def update_trading_profile(profile_config: ProfileUpdate):
    """
    🔄 Cambiar el perfil de trading activo
    
    **Perfiles disponibles:**
    - **SCALPING**: Timeframes 1m-5m, análisis cada 5 min, ganancias ultra-rápidas CFD
        - **INTRADAY**: Timeframes 15m-1h, análisis cada 15 min, operaciones diarias balanceadas CFD
    
    **Funcionalidad:** Cambia automáticamente el perfil modificando el archivo de configuración.
    El bot se reiniciará automáticamente si `restart_bot=True`.
    """
    try:
        # Validar que el perfil existe
        if profile_config.profile not in TradingProfiles.PROFILES:
            available = list(TradingProfiles.PROFILES.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Perfil '{profile_config.profile}' no válido. Opciones: {available}"
            )
        
        # Obtener información del perfil actual y nuevo
        current_profile_key = [k for k, v in TradingProfiles.PROFILES.items() 
                              if v == TradingProfiles.get_current_profile()][0]
        new_profile = TradingProfiles.PROFILES[profile_config.profile]
        
        if current_profile_key == profile_config.profile:
            return {
                "status": "info",
                "message": f"El perfil '{profile_config.profile}' ya está activo",
                "current_profile": current_profile_key,
                "timestamp": datetime.now().isoformat()
            }
        
        # Cambiar el perfil automáticamente
        profile_changed = change_trading_profile(profile_config.profile)
        
        if not profile_changed:
            raise HTTPException(
                status_code=500, 
                detail="Error modificando el archivo de configuración"
            )
        
        # Reiniciar el bot si se solicita
        restart_performed = False
        bot_restart_error = None
        
        if profile_config.restart_bot:
            try:
                global trading_bot
                bot = get_trading_bot()
                if getattr(bot, 'is_running', False):
                    bot.stop()
                    # Recargar el módulo de configuración para que tome el nuevo perfil
                    import importlib
                    import src.config.main_config
                    importlib.reload(src.config.main_config)
                    
                    # Crear nuevo bot con la nueva configuración
                    trading_bot = None
                    bot = get_trading_bot()
                    bot.start()
                    restart_performed = True
                else:
                    # Si el bot no está corriendo, solo recargar la configuración
                    import importlib
                    import src.config.main_config
                    importlib.reload(src.config.main_config)
                    trading_bot = None  # Forzar recreación del bot
                    restart_performed = True
                    
            except Exception as e:
                bot_restart_error = str(e)
        
        return {
            "status": "success",
            "message": f"Perfil cambiado exitosamente a '{profile_config.profile}'",
            "previous_profile": current_profile_key,
            "new_profile": profile_config.profile,
            "new_profile_info": {
                "name": new_profile["name"],
                "description": new_profile["description"],
                "analysis_interval": new_profile["analysis_interval"],
                "min_confidence": new_profile["min_confidence"],
                "timeframes": new_profile["timeframes"]
            },
            "restart_performed": restart_performed,
            "restart_error": bot_restart_error,
            "note": "El cambio se aplicó al archivo de configuración. Reinicia la aplicación para garantizar que todos los módulos usen la nueva configuración.",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@app.get("/bot/symbols")
async def get_current_symbols():
    """
    📊 Obtener la lista actual de símbolos a analizar
    """
    try:
        bot = get_trading_bot()
        current_symbols = getattr(bot, 'symbols', GLOBAL_SYMBOLS)
        
        return {
            "status": "success",
            "current_symbols": current_symbols,
            "total_symbols": len(current_symbols),
            "default_symbols": GLOBAL_SYMBOLS,
            "symbol_categories": {
                "metals": [s for s in current_symbols if s in ["GOLD", "SILVER"]],
                "crypto": [s for s in current_symbols if "USD" in s and s not in ["GOLD", "SILVER"]],
                "forex": [s for s in current_symbols if "/" in s],
                "other": [s for s in current_symbols if s not in ["GOLD", "SILVER"] and "USD" not in s and "/" not in s]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting symbols: {str(e)}")

@app.put("/bot/symbols")
async def update_symbols_list(symbols_config: SymbolsUpdate):
    """
    🔄 Actualizar la lista de símbolos a analizar
    
    **Símbolos disponibles comunes:**
    - **Metales:** GOLD, SILVER
    - **Crypto:** BTCUSD, ETHUSD, ADAUSD, SOLUSD, DOTUSD
    - **Forex:** EUR/USD, GBP/USD, USD/JPY
    
    **Nota:** Los cambios se aplicarán al bot actual. Si `restart_bot=True`,
    el bot se reiniciará para aplicar completamente los cambios.
    """
    try:
        # Validar que la lista no esté vacía
        if not symbols_config.symbols:
            raise HTTPException(status_code=400, detail="La lista de símbolos no puede estar vacía")
        
        # Validar símbolos únicos
        unique_symbols = list(set(symbols_config.symbols))
        if len(unique_symbols) != len(symbols_config.symbols):
            symbols_config.symbols = unique_symbols
        
        bot = get_trading_bot()
        old_symbols = getattr(bot, 'symbols', GLOBAL_SYMBOLS).copy()
        
        # Actualizar símbolos en el bot
        if hasattr(bot, 'symbols'):
            bot.symbols = symbols_config.symbols
        
        # Si el bot está corriendo y se solicita reinicio
        restart_performed = False
        if symbols_config.restart_bot and getattr(bot, 'is_running', False):
            try:
                bot.stop()
                bot.start()
                restart_performed = True
            except Exception as e:
                # Si falla el reinicio, restaurar símbolos anteriores
                bot.symbols = old_symbols
                raise HTTPException(status_code=500, detail=f"Error reiniciando bot: {str(e)}")
        
        return {
            "status": "success",
            "message": f"Símbolos actualizados exitosamente. {'Bot reiniciado.' if restart_performed else 'Reinicio pendiente.'}",
            "old_symbols": old_symbols,
            "new_symbols": symbols_config.symbols,
            "changes": {
                "added": [s for s in symbols_config.symbols if s not in old_symbols],
                "removed": [s for s in old_symbols if s not in symbols_config.symbols],
                "total_count": len(symbols_config.symbols)
            },
            "restart_performed": restart_performed,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating symbols: {str(e)}")

# 📊 **ANÁLISIS EN TIEMPO REAL**

@app.get("/enhanced/strategies/list")
async def get_enhanced_strategies():
    """📊 Obtener lista de estrategias mejoradas disponibles"""
    try:
        return {
            "enhanced_strategies": [
                {
                    "name": "TrendFollowingProfessional",
                    "description": "🎯 Estrategia profesional de seguimiento de tendencia con filtros institucionales",
                    "features": ["Institutional filters", "Trend confirmation", "Professional risk management"]
                },
                {
                    "name": "MeanReversionProfessional",
                    "description": "🔄 Estrategia profesional de reversión a la media con análisis de divergencias",
                    "features": ["RSI & Stochastic analysis", "Bollinger & Keltner Channels", "Divergence detection", "Support/Resistance levels"]
                },
                {
                    "name": "BreakoutProfessional", 
                    "description": "💥 Estrategia profesional de breakout con detección de patrones de consolidación",
                    "features": ["Consolidation pattern detection", "Volume breakout analysis", "False breakout filtering", "Momentum confirmation"]
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        # Re-lanzar HTTPException para que mantenga su código de estado
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enhanced/analyze/{strategy_name}/{symbol}")
async def analyze_with_enhanced_strategy(strategy_name: str, symbol: str, timeframe: str = "1h"):
    """🔍 Analizar símbolo con estrategia mejorada"""
    try:
        # Obtener el TradingBot existente
        bot = get_trading_bot()
        
        # Usar las estrategias del TradingBot que ya tienen la referencia asignada
        strategy_key = None
        if strategy_name.lower() == "trendfollowingprofessional":
            strategy_key = "TrendFollowingProfessional"
        elif strategy_name.lower() == "meanreversionprofessional":
            strategy_key = "MeanReversionProfessional"
        elif strategy_name.lower() == "breakoutprofessional":
            strategy_key = "BreakoutProfessional"
        else:
            raise HTTPException(status_code=400, detail=f"Estrategia '{strategy_name}' no encontrada")
        
        # Verificar que la estrategia existe en el bot
        if strategy_key not in bot.strategies:
            raise HTTPException(status_code=400, detail=f"Estrategia '{strategy_key}' no está disponible. Estrategias disponibles: {list(bot.strategies.keys())}")
        
        strategy = bot.strategies[strategy_key]
        
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



# Endpoint de test strategy eliminado - se usa análisis directo de estrategias

@app.get("/enhanced/risk-analysis/{symbol}")
async def get_enhanced_risk_analysis(symbol: str):
    """🛡️ Análisis de riesgo mejorado"""
    try:
        # Crear señal de prueba para análisis
        from src.core.trend_following_professional import TrendFollowingProfessional
        strategy = TrendFollowingProfessional()
        signal = strategy.analyze(symbol, "1h")
        
        # Verificar si se generó una señal válida
        if signal is None:
            return {
                "symbol": symbol,
                "error": "No se pudo generar una señal válida para este símbolo",
                "message": "El mercado puede estar en condiciones laterales o sin tendencia clara",
                "timestamp": datetime.now().isoformat()
            }
        
        # Obtener balance real del paper trader
        bot = get_trading_bot()
        current_portfolio_value = bot.paper_trader.get_balance() if bot.paper_trader else 1000.0
        
        # Analizar riesgo
        risk_manager = EnhancedRiskManager()
        risk_assessment = risk_manager.assess_trade_risk(signal, current_portfolio_value)
        
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

# Endpoints de paper trading eliminados - se usa Capital.com directamente

@app.get("/balance/current")
async def get_current_balance():
    """Obtener el balance actual de Capital.com"""
    try:
        balance_data = get_current_balance_sync()
        if balance_data and balance_data.get('available', 0) > 0:
            return {
                "status": "success",
                "message": "Balance obtenido correctamente",
                "data": balance_data
            }
        else:
            return {
                "status": "warning",
                "message": "No se pudo obtener el balance actual o balance es 0",
                "data": balance_data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo balance: {str(e)}")

# Historial de balance eliminado - se usa Capital.com directamente

# Ejecutar servidor si se ejecuta directamente
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
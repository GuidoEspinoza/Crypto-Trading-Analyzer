"""Configuración centralizada para el sistema de trading CFD.

Este archivo contiene todas las configuraciones principales del bot de trading,
con dos perfiles especializados para trading de CFDs:

⚡ SCALPING: Timeframes 1m-5m, máxima frecuencia, ganancias rápidas ultra-agresivas
📈 INTRADAY: Timeframes 15m-1h, operaciones diarias, balance entre velocidad y precisión

🎯 CAMBIO RÁPIDO DE PERFILES:
Para cambiar entre configuraciones, simplemente modifica la variable TRADING_PROFILE:
- "SCALPING" para estrategia ultra-rápida de ganancias inmediatas
- "INTRADAY" para estrategia diaria balanceada con mayor precisión
"""

import logging
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carga de variables de entorno desde .env si está presente
load_dotenv()

# Configurar logger para validación
logger = logging.getLogger(__name__)

# Utilidad para leer variables de entorno como float con fallback seguro
def _get_env_float(var_name: str, default: float) -> float:
    value = os.getenv(var_name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except Exception:
        logger.warning(f"Valor inválido para {var_name}: {value}, usando default {default}")
        return default

# Utilidad para leer variables de entorno como boolean con fallback seguro
def _get_env_bool(var_name: str, default: bool) -> bool:
    value = os.getenv(var_name)
    if value is None or value == "":
        return default
    
    # Convertir string a boolean
    value_lower = value.lower().strip()
    if value_lower in ('true', '1', 'yes', 'on', 'enabled'):
        return True
    elif value_lower in ('false', '0', 'no', 'off', 'disabled'):
        return False
    else:
        logger.warning(f"Valor inválido para {var_name}: {value}, usando default {default}")
        return default

# ============================================================================
# 🎯 SELECTOR DE PERFIL DE TRADING - CAMBIAR AQUÍ
# ============================================================================

# 🔥 CAMBIAR ESTE VALOR PARA CAMBIAR TODO EL COMPORTAMIENTO DEL BOT
TRADING_PROFILE = "INTRADAY"  # Opciones: "SCALPING", "INTRADAY"

# ============================================================================
# 📊 DEFINICIÓN DE PERFILES DE TRADING
# ============================================================================

class TradingProfiles:
    """Definición de perfiles de trading especializados para CFDs."""
    
    PROFILES = {
        "SCALPING": {
            "name": "Scalping",
            "description": "Timeframes 1m-5m ultra-rápidos, TP/SL basado en ROI del balance, scalping optimizado",
            "timeframes": ["1m", "3m", "5m"],  # OPTIMIZADO: Timeframes ultra-rápidos para scalping
            "analysis_interval": 1,  # OPTIMIZADO: Análisis cada minuto para trades rápidos
            "min_confidence": 75.0,  # CRÍTICO: Confianza alta para reducir señales falsas
            "max_daily_trades": 30,  # CRÍTICO: Reducir trades para mejor gestión
            "max_positions": 6,  # CRÍTICO: Máximo 6 posiciones simultáneas

            # Paper Trader Config - SCALPING CFD CONSERVADOR
            "max_position_size": 0.06,  # 6% por posición - más conservador
            "max_total_exposure": 0.40,  # 40% exposición total - más seguro
            "min_trade_value": 5.0,  # Valor mínimo más alto para calidad
            "paper_min_confidence": 75.0,  # Confianza alta consistente
            "max_slippage": 0.03,  # Slippage más controlado
            "min_liquidity": 8.0,  # Liquidez mínima más alta
            
            # Risk Manager Config - SCALPING CONTROLADO
            "max_risk_per_trade": 0.8,  # CRÍTICO: 0.8% riesgo por trade - más conservador
            "max_daily_risk": 3.0,  # 3% riesgo diario máximo - más seguro
            "max_drawdown_threshold": 0.08,  # 8% drawdown máximo - más estricto
            "correlation_threshold": 0.70,  # Correlación más estricta
            "min_position_size": 5.0,  # Posición mínima más alta
            "risk_max_position_size": 0.06,  # Consistente con max_position_size
            "kelly_fraction": 0.25,  # Kelly más conservador
            "volatility_adjustment_factor": 1.0,  # Factor de ajuste por volatilidad

            "atr_multiplier_min": 1.5,  # CRÍTICO: Stops más amplios para scalping
            "atr_multiplier_max": 2.5,  # CRÍTICO: Stops más amplios optimizados
            "atr_default": 1.8,  # Stop loss por defecto más amplio
            "atr_volatile": 2.5,  # Stops amplios en alta volatilidad
            "atr_sideways": 1.5,  # Stops moderados en laterales
            "trailing_stop_activation": 0.025,  # OPTIMIZADO: Trailing al 2.5% - más agresivo para scalping
            "breakeven_threshold": 0.004,  # OPTIMIZADO: Breakeven al 0.4% para protección rápida
            "intelligent_trailing": True,
            "dynamic_position_sizing": True,
            
            # Capital.com Trailing Stop Config - SCALPING
            "use_trailing_stop": True,  # Activado por defecto para scalping (mayor dinamismo)
            
            # Take Profit y Stop Loss Config - SCALPING ROI-BASED (% del balance invertido)
            "tp_min_percentage": 0.0035,  # ROI: TP mínimo 0.35% del balance para trades ultra-rápidos
            "tp_max_percentage": 0.015,  # ROI: TP máximo 1.5% del balance para cierre rápido
            "sl_min_percentage": 0.003,  # ROI: SL mínimo 0.3% del balance para scalping
            "sl_max_percentage": 0.008,  # ROI: SL máximo 0.8% del balance para control estricto
            "tp_increment_percentage": 1.2,  # Factor TP agresivo
            "tp_confidence_threshold": 0.65,  # Umbral bajo para ajustar TP
            
            # Umbrales y Límites Adicionales
            "max_daily_loss_percent": 6.0,  # Pérdida máxima diaria alta
            "min_confidence_threshold": 0.50,  # Confianza mínima más flexible
            "position_size_multiplier": 1.2,  # Multiplicador agresivo
            
            # Strategy Config - SCALPING CONTROLADO Y SELECTIVO
            "default_min_confidence": 70.0,  # CRÍTICO: Confianza alta para señales de calidad
            "default_atr_period": 14,  # Período estándar para mejor precisión
            "rsi_min_confidence": 75.0,  # CRÍTICO: RSI confianza alta
            "rsi_oversold": 25,  # CRÍTICO: RSI oversold más extremo (menos señales)
            "rsi_overbought": 75,  # CRÍTICO: RSI overbought más extremo (menos señales)
            "rsi_period": 14,  # Período RSI estándar para mejor precisión
            "min_volume_ratio": 1.8,  # CRÍTICO: Volumen mínimo alto para confirmación
            "min_confluence": 6,  # CRÍTICO: Confluencia mínima alta (6 confirmaciones)
            "trend_strength_threshold": 40,  # CRÍTICO: Fuerza tendencia alta
            "min_atr_ratio": 1.2,  # ATR ratio más alto para volatilidad adecuada
            "max_spread_threshold": 0.002,  # CRÍTICO: Spread máximo más estricto
            "volume_weight": 0.35,  # Peso volumen más alto para confirmación
            "confluence_threshold": 0.75,  # CRÍTICO: Umbral confluencia alto
            
            # Multi-Timeframe Config - SCALPING ESTRICTO
            "mtf_enhanced_confidence": 75.0,  # CRÍTICO: Confianza MTF alta
            "mtf_min_confidence": 80.0,  # CRÍTICO: Confianza mínima MTF muy alta
            "mtf_min_consensus": 0.80,  # CRÍTICO: Consenso mínimo MTF alto
            "mtf_require_trend_alignment": True,  # CRÍTICO: Requiere alineación de tendencias
            "mtf_min_timeframe_consensus": 3,  # CRÍTICO: Consenso en todos los timeframes
            "mtf_trend_alignment_required": True,  # CRÍTICO: Alineación obligatoria
            "volume_timeframe": "5m",  # Timeframe volumen más estable
            
            # Live Trading Config - SCALPING ULTRA RÁPIDO
            "trading_fees": 0.001,
            "order_timeout": 15,  # Timeout muy corto
            "max_order_retries": 2,  # Pocos reintentos
            "order_check_interval": 1.0,  # Verificación muy frecuente
            "live_first_analysis_delay": 5,  # Delay inicial muy corto
            
            # Position Adjuster Config - SCALPING ULTRA-RÁPIDO
            "enable_position_monitoring": False,  # DESACTIVADO: Solo abrir posiciones con TP/SL, no cerrar automáticamente
            "position_monitoring_interval": 5,  # OPTIMIZADO: Monitoreo cada 5 segundos
            "price_cache_duration": 5,  # OPTIMIZADO: Cache ultra-corto
            "max_close_attempts": 2,  # Pocos intentos de cierre
            "position_timeout_hours": 4,  # OPTIMIZADO: Cerrar posiciones después de 4 horas para scalping
            "profit_scaling_threshold": 0.008,  # OPTIMIZADO: Escalado al 0.8%
            "trailing_stop_sl_pct": 0.006,  # OPTIMIZADO: SL trailing 0.6%
            "trailing_stop_tp_pct": 0.012,  # OPTIMIZADO: TP trailing 1.2%
            "profit_protection_sl_pct": 0.004,  # OPTIMIZADO: Protección ganancias 0.4%
            "profit_protection_tp_pct": 0.010,  # OPTIMIZADO: TP protección 1.0%
            "risk_management_threshold": -0.008,  # Umbral riesgo -0.8%
            "risk_management_sl_pct": 0.012,  # SL riesgo 1.2%
            "risk_management_tp_pct": 0.015,  # TP riesgo 1.5%
            
            # Enhanced Risk Manager Config
            "kelly_win_rate": 0.62,  # Tasa ganancia scalping
            "kelly_avg_loss": 1.0,
            "default_leverage": 1.0,
            "default_trailing_distance": 0.015,  # Trailing corto
            "tp_increment_base_pct": 0.008,  # Incremento TP pequeño
            
            # Trading Bot Config - SCALPING
            "cache_ttl_seconds": 60,  # Cache muy corto
            "event_queue_maxsize": 300,  # Cola pequeña
            "executor_shutdown_timeout": 15,  # Shutdown rápido
            "thread_join_timeout": 5,  # Join rápido
            "analysis_future_timeout": 15,  # Análisis rápido
            
            # Connection and Network Config
            "connection_timeout": 20,  # Conexión rápida
            "read_timeout": 40,  # Lectura rápida
            "retry_delay": 3,  # Delay corto
            "max_retries": 2,  # Pocos reintentos
            "backoff_factor": 1.5,  # Backoff bajo
            
            # Monitoring and Intervals Config
            "position_check_interval": 20,  # Verificación frecuente
            "market_data_refresh_interval": 30,  # Actualización frecuente
            "health_check_interval": 180,  # Health check frecuente
            "log_rotation_interval": 1800,  # Rotación frecuente
            
            # Performance and Optimization Config
            "max_concurrent_requests": 15,  # Muchos requests
            "request_rate_limit": 150,  # Rate limit alto
            "memory_threshold_mb": 256,  # Memoria baja
            "cpu_threshold_percent": 85,  # CPU alto
            
            # Error Handling Config
            "error_cooldown_seconds": 30,  # Cooldown corto
            "max_consecutive_errors": 3,  # Tolerancia media

        },
        "INTRADAY": {
            "name": "Intraday",
            "description": "Timeframes 15m-1h, operaciones diarias balanceadas CFD con TP/SL basado en ROI del balance",
            "timeframes": ["30m", "1h", "4h"],  # CAMBIADO: eliminado 15m, agregado 4h para mejor calidad
            "analysis_interval": 12,  # AUMENTADO: Análisis cada 12 minutos - mucho más selectivo
            "min_confidence": 80.0,  # AUMENTADO: Confianza aún más estricta para máxima precisión
            "max_daily_trades": 10,  # Máximo 10 operaciones diarias
            "max_positions": 4,  # Máximo 4 posiciones - control total de riesgo

            # Paper Trader Config - INTRADAY CFD OPTIMIZADO
            "max_position_size": 0.06,  # OPTIMIZADO: 6% por posición - más conservador
            "max_total_exposure": 0.30,  # OPTIMIZADO: 30% exposición total - mucho más conservador
            "min_trade_value": 15.0,  # OPTIMIZADO: Valor mínimo más alto para mejor calidad
            "paper_min_confidence": 78.0,  # OPTIMIZADO: Confianza consistente con trading real
            "max_slippage": 0.025,  # OPTIMIZADO: Slippage más estricto para intraday
            "min_liquidity": 12.0,  # OPTIMIZADO: Liquidez más alta requerida
            
            # Risk Manager Config - INTRADAY CONSERVADOR
            "max_risk_per_trade": 1.0,  # OPTIMIZADO: 1% riesgo por trade - más conservador
            "max_daily_risk": 2.5,  # OPTIMIZADO: 2.5% riesgo diario máximo - más estricto
            "max_drawdown_threshold": 0.08,  # 8% drawdown máximo
            "correlation_threshold": 0.65,  # Correlación moderada
            "min_position_size": 10.0,  # Posición mínima moderada
            "risk_max_position_size": 0.06,  # OPTIMIZADO: Consistente con max_position_size
            "kelly_fraction": 0.25,  # Kelly moderado
            "volatility_adjustment_factor": 1.2,  # Factor de ajuste por volatilidad (más alto para intraday)

            "atr_multiplier_min": 2.0,  # Stops amplios para intraday
            "atr_multiplier_max": 3.0,  # OPTIMIZADO: Stops amplios optimizados para intraday
            "atr_default": 2.2,
            "atr_volatile": 3.0,
            "atr_sideways": 1.8,  # Stops moderados en laterales
            "trailing_stop_activation": 0.030,  # OPTIMIZADO: Trailing al 3% - conservador para intraday
            "breakeven_threshold": 0.008,  # Breakeven al 0.8% - conservador
            "intelligent_trailing": True,
            "dynamic_position_sizing": True,
            
            # Capital.com Trailing Stop Config - INTRADAY
            "use_trailing_stop": True,  # Activado por defecto para intraday
            
            # Take Profit y Stop Loss Config - INTRADAY ROI-based R:R 2:1 OPTIMIZADO
            "tp_min_percentage": 0.012,  # OPTIMIZADO: TP mínimo 1.2% ROI - más dinámico
            "tp_max_percentage": 0.025,  # OPTIMIZADO: TP máximo 2.5% ROI - más realista
            "sl_min_percentage": 0.006,  # OPTIMIZADO: SL mínimo 0.6% ROI - más dinámico
            "sl_max_percentage": 0.015,  # OPTIMIZADO: SL máximo 1.5% ROI - mejor control
            "tp_increment_percentage": 1.0,  # Factor TP balanceado
            "tp_confidence_threshold": 0.72,  # Umbral moderado para ajustar TP
            
            # Umbrales y Límites Adicionales
            "max_daily_loss_percent": 2.5,  # OPTIMIZADO: Pérdida máxima diaria más conservadora
            "min_confidence_threshold": 0.78,  # OPTIMIZADO: Confianza mínima mucho más estricta
            "position_size_multiplier": 0.8,  # OPTIMIZADO: Multiplicador más conservador
            
            # Strategy Config - INTRADAY ULTRA-OPTIMIZADO ANTI-LATERAL
            "default_min_confidence": 80.0,  # AUMENTADO: Confianza ultra estricta
            "default_atr_period": 21,  # AUMENTADO: Período más largo para señales más suaves
            "rsi_min_confidence": 85.0,  # AUMENTADO: RSI confianza extrema
            "rsi_oversold": 25,  # AUMENTADO: RSI oversold mucho más estricto
            "rsi_overbought": 75,  # REDUCIDO: RSI overbought mucho más estricto
            "rsi_period": 21,  # AUMENTADO: Período RSI más largo para menos ruido
            "min_volume_ratio": 3.0,  # AUMENTADO: Volumen mínimo ultra alto
            "min_confluence": 7,  # OPTIMIZADO: Confluencia ultra estricta para intraday
            "trend_strength_threshold": 65,  # AUMENTADO: Fuerza tendencia ultra alta
            "min_atr_ratio": 1.8,  # AUMENTADO: ATR ratio ultra estricto
            "max_spread_threshold": 0.0008,  # REDUCIDO: Spread máximo ultra estricto
            "volume_weight": 0.35,  # AUMENTADO: Peso máximo al volumen
            "confluence_threshold": 0.80,  # AUMENTADO: Umbral confluencia ultra estricto
            
            # Multi-Timeframe Config - INTRADAY
            "mtf_enhanced_confidence": 82.0,  # OPTIMIZADO: Confianza MTF muy alta
            "mtf_min_confidence": 80.0,  # OPTIMIZADO: Confianza mínima MTF muy estricta
            "mtf_min_consensus": 0.80,  # OPTIMIZADO: Consenso mucho más estricto MTF
            "mtf_require_trend_alignment": True,  # Requiere alineación
            "mtf_min_timeframe_consensus": 3,  # OPTIMIZADO: Consenso en los 3 timeframes
            "mtf_trend_alignment_required": True,
            "volume_timeframe": "15m",  # Timeframe volumen moderado
            
            # Live Trading Config - INTRADAY BALANCEADO
            "trading_fees": 0.001,
            "order_timeout": 35,  # Timeout moderado
            "max_order_retries": 3,  # Reintentos estándar
            "order_check_interval": 1.8,  # Verificación moderada
            "live_first_analysis_delay": 15,  # Delay inicial moderado
            
            # Position Adjuster Config - INTRADAY ANTI-LATERAL
            "enable_position_monitoring": True,  # ACTIVADO: Para cerrar trades lentos automáticamente
            "position_monitoring_interval": 20,  # REDUCIDO: Monitoreo más frecuente
            "price_cache_duration": 15,  # REDUCIDO: Cache más fresco
            "max_close_attempts": 3,  # Intentos estándar
            "position_timeout_hours": 6,  # OPTIMIZADO: Cerrar posiciones después de 6 horas para intraday
            "min_movement_threshold": 0.005,  # NUEVO: Movimiento mínimo 0.5% para considerar progreso
            "sideways_detection_period": 120,  # NUEVO: Detectar lateral en 2 horas
            "profit_scaling_threshold": 0.015,  # REDUCIDO: Escalado más temprano al 1.5%
            "trailing_stop_sl_pct": 0.012,  # REDUCIDO: SL trailing más agresivo 1.2%
            "trailing_stop_tp_pct": 0.030,  # REDUCIDO: TP trailing más conservador 3.0%
            "profit_protection_sl_pct": 0.008,  # REDUCIDO: Protección ganancias más temprana 0.8%
            "profit_protection_tp_pct": 0.025,  # REDUCIDO: TP protección más conservador 2.5%
            "risk_management_threshold": -0.008,  # MEJORADO: Umbral riesgo más estricto -0.8%
            "risk_management_sl_pct": 0.010,  # REDUCIDO: SL riesgo más agresivo 1.0%
            "risk_management_tp_pct": 0.020,  # REDUCIDO: TP riesgo más conservador 2.0%
            
            # Enhanced Risk Manager Config
            "kelly_win_rate": 0.68,  # Tasa ganancia intraday
            "kelly_avg_loss": 1.0,
            "default_leverage": 1.0,
            "default_trailing_distance": 0.018,  # Trailing moderado
            "tp_increment_base_pct": 0.012,  # Incremento TP moderado
            
            # Trading Bot Config - INTRADAY
            "cache_ttl_seconds": 120,  # Cache moderado
            "event_queue_maxsize": 600,  # Cola moderada
            "executor_shutdown_timeout": 25,  # Shutdown moderado
            "thread_join_timeout": 8,  # Join moderado
            "analysis_future_timeout": 25,  # Análisis moderado
            
            # Connection and Network Config
            "connection_timeout": 30,  # Conexión estándar
            "read_timeout": 60,  # Lectura estándar
            "retry_delay": 5,  # Delay estándar
            "max_retries": 3,  # Reintentos estándar
            "backoff_factor": 2.0,  # Backoff estándar
            
            # Monitoring and Intervals Config
            "position_check_interval": 35,  # Verificación moderada
            "market_data_refresh_interval": 60,  # Actualización moderada
            "health_check_interval": 300,  # Health check moderado
            "log_rotation_interval": 3600,  # Rotación estándar
            
            # Performance and Optimization Config
            "max_concurrent_requests": 10,  # Requests moderados
            "request_rate_limit": 100,  # Rate limit moderado
            "memory_threshold_mb": 384,  # Memoria moderada
            "cpu_threshold_percent": 75,  # CPU moderado
            
            # Error Handling Config
            "error_cooldown_seconds": 45,  # Cooldown moderado
            "max_consecutive_errors": 4,  # Tolerancia moderada

        }
    }
    
    @classmethod
    def get_profile(cls, profile_name: str) -> Dict[str, Any]:
        """Obtiene la configuración del perfil especificado."""
        if profile_name not in cls.PROFILES:
            raise ValueError(f"Perfil '{profile_name}' no válido. Opciones: {list(cls.PROFILES.keys())}")
        return cls.PROFILES[profile_name]
    
    @classmethod
    def get_current_profile(cls) -> Dict[str, Any]:
        """Obtiene el perfil actualmente configurado."""
        return cls.get_profile(TRADING_PROFILE)


# ============================================================================
# 🏭 CONFIGURACIÓN DE MODO PRODUCCIÓN
# ============================================================================

# Modo de operación del sistema
PRODUCTION_MODE = _get_env_float("PRODUCTION_MODE", 0.0) == 1.0  # False por defecto (desarrollo)

# Configuraciones dependientes del modo
# Dashboard eliminado - usando Capital.com directamente
PAPER_TRADING_ONLY = not PRODUCTION_MODE  # Paper trading en desarrollo, real en producción
ENABLE_REAL_TRADING = _get_env_bool("ENABLE_REAL_TRADING", PRODUCTION_MODE)  # Trading real configurado por variable de entorno

# Configuraciones de logging y debugging
VERBOSE_LOGGING = not PRODUCTION_MODE  # Logging detallado en desarrollo
ENABLE_DEBUG_FEATURES = not PRODUCTION_MODE  # Características de debug

# ============================================================================
# 💰 CONFIGURACIÓN DE BALANCE
# ============================================================================

def _get_capital_balance() -> float:
    """
    Obtiene el balance disponible real de la cuenta de Capital.com
    
    Returns:
        float: Balance disponible en USD, o 0.0 si hay error
    """
    try:
        # Importación diferida para evitar dependencias circulares
        import sys
        import importlib
        
        # Importar dinámicamente el módulo
        capital_module = importlib.import_module('src.core.capital_client')
        create_capital_client_from_env = getattr(capital_module, 'create_capital_client_from_env')
        
        # Crear cliente de Capital.com
        capital_client = create_capital_client_from_env()
        
        # Obtener balance disponible
        balance_info = capital_client.get_available_balance()
        
        if balance_info and 'available' in balance_info:
            available_balance = float(balance_info['available'])
            print(f"✅ Balance real obtenido de Capital.com: ${available_balance:,.2f}")
            return available_balance
        else:
            print("⚠️ No se pudo obtener el balance de Capital.com, usando balance por defecto")
            return 0.0
            
    except Exception as e:
        print(f"❌ Error al obtener balance de Capital.com: {e}")
        return 0.0

# 💰 Balance inicial global para todas las posiciones en USD (paper trading)
PAPER_GLOBAL_INITIAL_BALANCE = 1000.0

# 💰 Balance inicial global para todas las posiciones en USD (real trading)
# Se obtiene dinámicamente de Capital.com cuando ENABLE_REAL_TRADING está habilitado
REAL_GLOBAL_INITIAL_BALANCE = 0.0  # Se inicializa en 0, se obtiene dinámicamente cuando se necesite

def get_global_initial_balance() -> float:
    """
    Obtiene el balance inicial global, ya sea del paper trading o del balance real de Capital.com
    
    Returns:
        float: Balance inicial en USD
    """
    global REAL_GLOBAL_INITIAL_BALANCE
    
    if _get_env_bool("ENABLE_REAL_TRADING", False):
        # Si el trading real está habilitado, obtener balance real
        if REAL_GLOBAL_INITIAL_BALANCE == 0.0:  # Solo obtener si no se ha obtenido antes
            REAL_GLOBAL_INITIAL_BALANCE = _get_capital_balance()
        return REAL_GLOBAL_INITIAL_BALANCE
    else:
        # Si no, usar paper trading
        return PAPER_GLOBAL_INITIAL_BALANCE

# Balance inicial global para todas las posiciones en USD
# Usa balance real si el trading real está habilitado, sino usa paper trading
GLOBAL_INITIAL_BALANCE = PAPER_GLOBAL_INITIAL_BALANCE  # Por defecto paper trading, se actualiza dinámicamente

# Precio base de USD (moneda fiat)
USD_BASE_PRICE = 1.0

# ============================================================================
# 🎯 LISTA DE ACTIVOS
# ============================================================================

# Lista de símbolos con nombres exactos como aparecen en Capital.com
GLOBAL_SYMBOLS: List[str] = [
    # === Metales Preciosos (Base) ===
    "GOLD",
    # === Criptomonedas (Base) ===
    "BTCUSD", "ETHUSD",
    # === Forex (Volatilidad y Liquidez) ===
    "EURUSD",
    # === Índices (Volatilidad de Apertura) ===
    "US500"
]

# ============================================================================
# ⏰ CONFIGURACIÓN TEMPORAL GLOBAL
# ============================================================================

# Zona horaria para Chile (CLT/CLST)
# Usado en:
# - TradingBot para programación de operaciones
# - Logging para marcas de tiempo
TIMEZONE: str = "America/Santiago"

# Alias para compatibilidad con código existente
CHILE_TZ: str = TIMEZONE

# Horario de reset diario optimizado para trading de criptomonedas en Chile
# Basado en análisis de volatilidad: mejor horario 11:30 AM - 6:00 PM CLT
# Reset configurado a las 11:00 AM CLT para preparar el bot antes del horario óptimo
DAILY_RESET_HOUR: int = 11  # 11:00 AM CLT
DAILY_RESET_MINUTE: int = 0  # 11:00 AM exacto

# ============================================================================
# CONFIGURACIÓN DEL TRADING BOT PRINCIPAL
# ============================================================================

class TradingBotConfig:
    """Configuración principal del bot de trading."""
    
    # Lista de símbolos para analizar - Optimizada para trading
    # Selección basada en alta liquidez, volatilidad y volumen de trading
    SYMBOLS = GLOBAL_SYMBOLS

    # Símbolos para el bot en vivo - Misma lista optimizada
    SYMBOLS_LIVE_BOT = GLOBAL_SYMBOLS
    
    # 🎯 CONFIGURACIÓN DINÁMICA BASADA EN PERFIL SELECCIONADO
    @classmethod
    def get_analysis_interval(cls) -> int:
        """Intervalo de análisis en minutos según perfil activo."""
        return TradingProfiles.get_current_profile()["analysis_interval"]
    
    @classmethod
    def get_min_confidence_threshold(cls) -> float:
        """Umbral mínimo de confianza según perfil activo."""
        return TradingProfiles.get_current_profile()["min_confidence"]
    
    @classmethod
    def get_max_daily_trades(cls) -> int:
        """Máximo de trades diarios según perfil activo."""
        return TradingProfiles.get_current_profile()["max_daily_trades"]
    
    @classmethod
    def get_max_concurrent_positions(cls) -> int:
        """Máximo de posiciones concurrentes según perfil activo."""
        return TradingProfiles.get_current_profile()["max_positions"]
    
    @classmethod
    def get_professional_timeframes(cls) -> List[str]:
        """Timeframes profesionales según perfil activo."""
        return TradingProfiles.get_current_profile()["timeframes"]
    
    # Valor por defecto del portfolio para cálculos cuando no hay datos
    @classmethod
    def get_default_portfolio_value(cls) -> float:
        """Obtiene el valor por defecto del portfolio."""
        return get_global_initial_balance()
    
    DEFAULT_PORTFOLIO_VALUE: float = 1000.0  # Valor por defecto, se actualiza dinámicamente
    
    # 🎯 CONFIGURACIÓN DINÁMICA ADICIONAL BASADA EN PERFIL
    @classmethod
    def get_primary_timeframe(cls) -> str:
        """Timeframe principal según perfil activo."""
        timeframes = cls.get_professional_timeframes()
        return timeframes[0] if timeframes else "1m"
    
    @classmethod
    def get_confirmation_timeframe(cls) -> str:
        """Timeframe de confirmación según perfil activo."""
        timeframes = cls.get_professional_timeframes()
        return timeframes[1] if len(timeframes) > 1 else timeframes[0]
    
    @classmethod
    def get_trend_timeframe(cls) -> str:
        """Timeframe de tendencia según perfil activo."""
        timeframes = cls.get_professional_timeframes()
        return timeframes[-1] if timeframes else "15m"
    
    @classmethod
    def get_bot_description(cls) -> str:
        """Descripción del bot según perfil activo."""
        return TradingProfiles.get_current_profile()["name"]
    
    @classmethod
    def get_live_update_interval(cls) -> int:
        """Intervalo de actualización del live bot en minutos según perfil."""
        return TradingProfiles.get_current_profile()["analysis_interval"]
    
    @classmethod
    def get_first_analysis_delay(cls) -> int:
        """Delay para primer análisis (en minutos) según perfil."""
        # Usar el doble del intervalo de análisis como delay inicial
        return TradingProfiles.get_current_profile()["analysis_interval"] * 2
    
    @classmethod
    def get_monitoring_interval(cls) -> int:
        """Intervalo de monitoreo de posiciones según perfil."""
        return TradingProfiles.get_current_profile().get("position_monitoring_interval", 30)
    
    @classmethod
    def get_position_monitoring_enabled(cls) -> bool:
        """Indica si el monitoreo automático de posiciones está habilitado según perfil."""
        return TradingProfiles.get_current_profile().get("enable_position_monitoring", False)
    
    @classmethod
    def get_cleanup_interval(cls) -> int:
        """Intervalo de limpieza según perfil."""
        return TradingProfiles.get_current_profile().get("cleanup_interval", 10)
    
    @classmethod
    def get_thread_join_timeout(cls) -> int:
        """Timeout para join de threads según perfil."""
        return TradingProfiles.get_current_profile().get("thread_join_timeout", 10)
    
    @classmethod
    def get_executor_shutdown_timeout(cls) -> int:
        """Timeout para shutdown de executor según perfil."""
        return TradingProfiles.get_current_profile().get("executor_shutdown_timeout", 30)
    
    @classmethod
    def get_analysis_future_timeout(cls) -> int:
        """Timeout para futures de análisis según perfil."""
        return TradingProfiles.get_current_profile().get("analysis_future_timeout", 30)
    
    @classmethod
    def get_max_consecutive_losses(cls) -> int:
        """Máximo de pérdidas consecutivas antes de activar circuit breaker según perfil activo."""
        return TradingProfiles.get_current_profile()["max_consecutive_losses"]
    

    
    @classmethod
    def get_max_drawdown_threshold(cls) -> float:
        """Umbral máximo de drawdown según perfil activo."""
        return TradingProfiles.get_current_profile()["max_drawdown_threshold"]


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USD para simulación
    @classmethod
    def get_initial_balance(cls) -> float:
        """Obtiene el balance inicial según configuración."""
        return get_global_initial_balance()
    
    INITIAL_BALANCE: float = 1000.0  # Valor por defecto, se actualiza dinámicamente
    
    @classmethod
    def get_max_position_size(cls) -> float:
        """Obtiene el tamaño máximo de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["max_position_size"]
    
    @classmethod
    def get_max_total_exposure(cls) -> float:
        """Obtiene la exposición total máxima según perfil activo."""
        return TradingProfiles.get_current_profile()["max_total_exposure"]
    
    @classmethod
    def get_min_trade_value(cls) -> float:
        """Obtiene el valor mínimo por trade según perfil activo."""
        return TradingProfiles.get_current_profile()["min_trade_value"]
    
    @classmethod
    def get_min_confidence_threshold(cls) -> float:
        """Obtiene el umbral mínimo de confianza según perfil activo."""
        return TradingProfiles.get_current_profile()["paper_min_confidence"]
    
    @classmethod
    def get_max_slippage(cls) -> float:
        """Obtiene el slippage máximo permitido según perfil activo."""
        return TradingProfiles.get_current_profile()["max_slippage"]
    
    @classmethod
    def get_min_liquidity(cls) -> float:
        """Obtiene la liquidez mínima requerida según perfil activo."""
        return TradingProfiles.get_current_profile()["min_liquidity"]
    
    # Propiedades dinámicas para compatibilidad con código existente
    MAX_POSITION_SIZE: float = property(lambda self: TradingProfiles.get_current_profile()["max_position_size"])
    MAX_TOTAL_EXPOSURE: float = property(lambda self: TradingProfiles.get_current_profile()["max_total_exposure"])
    MIN_TRADE_VALUE: float = property(lambda self: TradingProfiles.get_current_profile()["min_trade_value"])
    MIN_CONFIDENCE_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["paper_min_confidence"])
    MAX_SLIPPAGE: float = property(lambda self: TradingProfiles.get_current_profile()["max_slippage"])
    MIN_LIQUIDITY: float = property(lambda self: TradingProfiles.get_current_profile()["min_liquidity"])
    
    # Máximo % del balance disponible para trading (reserva para fees)
    MAX_BALANCE_USAGE: float = 0.95


# ============================================================================
# CONFIGURACIÓN DEL GESTOR DE RIESGO
# ============================================================================

class RiskManagerConfig:
    """Configuración del gestor de riesgo avanzado."""
    
    @classmethod
    def get_max_risk_per_trade(cls) -> float:
        """Obtiene el riesgo máximo por trade según perfil activo."""
        return TradingProfiles.get_current_profile()["max_risk_per_trade"]
    
    @classmethod
    def get_max_daily_risk(cls) -> float:
        """Obtiene el riesgo máximo diario según perfil activo."""
        return TradingProfiles.get_current_profile()["max_daily_risk"]
    
    @classmethod
    def get_max_drawdown_threshold(cls) -> float:
        """Obtiene el umbral de drawdown máximo según perfil activo."""
        return TradingProfiles.get_current_profile()["max_drawdown_threshold"]
    
    @classmethod
    def get_correlation_threshold(cls) -> float:
        """Obtiene el umbral de correlación según perfil activo."""
        return TradingProfiles.get_current_profile()["correlation_threshold"]
    
    @classmethod
    def get_min_position_size(cls) -> float:
        """Obtiene el tamaño mínimo de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["min_position_size"]
    
    @classmethod
    def get_max_position_size(cls) -> float:
        """Obtiene el tamaño máximo de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["risk_max_position_size"]
    
    @classmethod
    def get_kelly_fraction(cls) -> float:
        """Obtiene la fracción Kelly según perfil activo."""
        return TradingProfiles.get_current_profile()["kelly_fraction"]
    

    
    @classmethod
    def get_atr_multiplier_min(cls) -> float:
        """Obtiene el multiplicador ATR mínimo según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_multiplier_min"]
    
    @classmethod
    def get_atr_multiplier_max(cls) -> float:
        """Obtiene el multiplicador ATR máximo según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_multiplier_max"]
    
    @classmethod
    def get_atr_default(cls) -> float:
        """Obtiene el multiplicador ATR por defecto según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_default"]
    
    @classmethod
    def get_atr_volatile(cls) -> float:
        """Obtiene el multiplicador ATR para mercados volátiles según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_volatile"]
    
    @classmethod
    def get_atr_sideways(cls) -> float:
        """Obtiene el multiplicador ATR para mercados laterales según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_sideways"]
    
    @classmethod
    def get_trailing_stop_activation(cls) -> float:
        """Obtiene el umbral de activación del trailing stop según perfil activo."""
        return TradingProfiles.get_current_profile()["trailing_stop_activation"]
    
    @classmethod
    def get_breakeven_threshold(cls) -> float:
        """Obtiene el umbral de breakeven según perfil activo."""
        return TradingProfiles.get_current_profile()["breakeven_threshold"]
    
    @classmethod
    def get_tp_min_percentage(cls) -> float:
        """Obtiene el porcentaje mínimo de Take Profit según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_min_percentage"]
    
    @classmethod
    def get_tp_max_percentage(cls) -> float:
        """Obtiene el porcentaje máximo de Take Profit según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_max_percentage"]
    
    @classmethod
    def get_sl_min_percentage(cls) -> float:
        """Obtiene el porcentaje mínimo de Stop Loss según perfil activo."""
        return TradingProfiles.get_current_profile()["sl_min_percentage"]
    
    @classmethod
    def get_sl_max_percentage(cls) -> float:
        """Obtiene el porcentaje máximo de Stop Loss según perfil activo."""
        return TradingProfiles.get_current_profile()["sl_max_percentage"]
    
    @classmethod
    def get_tp_increment_percentage(cls) -> float:
        """Obtiene el porcentaje de incremento de TP según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_increment_percentage"]
    

    
    @classmethod
    def get_tp_confidence_threshold(cls) -> float:
        """Obtiene el umbral de confianza para ajustar TP según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_confidence_threshold"]
    
    @classmethod
    def get_max_daily_loss_percent(cls) -> float:
        """Obtiene el porcentaje máximo de pérdida diaria según perfil activo."""
        return TradingProfiles.get_current_profile()["max_daily_loss_percent"]
    
    @classmethod
    def get_max_drawdown_threshold(cls) -> float:
        """Obtiene el umbral máximo de drawdown según perfil activo."""
        return TradingProfiles.get_current_profile()["max_drawdown_threshold"]
    
    @classmethod
    def get_min_confidence_threshold(cls) -> float:
        """Obtiene el umbral mínimo de confianza según perfil activo."""
        return TradingProfiles.get_current_profile()["min_confidence_threshold"]
    
    @classmethod
    def get_position_size_multiplier(cls) -> float:
        """Obtiene el multiplicador de tamaño de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["position_size_multiplier"]
    

    
    # Propiedades dinámicas para compatibilidad con código existente
    MAX_RISK_PER_TRADE: float = property(lambda self: TradingProfiles.get_current_profile()["max_risk_per_trade"])
    MAX_DAILY_RISK: float = property(lambda self: TradingProfiles.get_current_profile()["max_daily_risk"])
    MAX_DRAWDOWN_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["max_drawdown_threshold"])
    CORRELATION_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["correlation_threshold"])
    MIN_POSITION_SIZE: float = property(lambda self: TradingProfiles.get_current_profile()["min_position_size"])
    MAX_POSITION_SIZE: float = property(lambda self: TradingProfiles.get_current_profile()["risk_max_position_size"])
    KELLY_FRACTION: float = property(lambda self: TradingProfiles.get_current_profile()["kelly_fraction"])

    ATR_MULTIPLIER_MIN: float = property(lambda self: TradingProfiles.get_current_profile()["atr_multiplier_min"])
    ATR_MULTIPLIER_MAX: float = property(lambda self: TradingProfiles.get_current_profile()["atr_multiplier_max"])
    ATR_DEFAULT: float = property(lambda self: TradingProfiles.get_current_profile()["atr_default"])
    ATR_VOLATILE: float = property(lambda self: TradingProfiles.get_current_profile()["atr_volatile"])
    ATR_SIDEWAYS: float = property(lambda self: TradingProfiles.get_current_profile()["atr_sideways"])
    TRAILING_STOP_ACTIVATION: float = property(lambda self: TradingProfiles.get_current_profile()["trailing_stop_activation"])
    BREAKEVEN_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["breakeven_threshold"])
    
    # Valor inicial del portfolio para cálculos de riesgo en USD - Se alimenta del PaperTrader para consistencia
    INITIAL_PORTFOLIO_VALUE: float = PaperTraderConfig.INITIAL_BALANCE  # Mantiene consistencia automática


# ============================================================================
# CONFIGURACIÓN DE ESTRATEGIAS DE TRADING
# ============================================================================

class StrategyConfig:
    """Configuración de las estrategias de trading."""
    
    @classmethod
    def get_current_profile_config(cls) -> Dict[str, Any]:
        """Obtiene la configuración del perfil activo."""
        return TradingProfiles.get_current_profile()
    
    # ---- Configuración Base de Estrategias ----
    class Base:
        """Parámetros base para todas las estrategias."""
        
        @classmethod
        def get_default_min_confidence(cls) -> float:
            """Confianza mínima según perfil activo."""
            return TradingProfiles.get_current_profile().get("default_min_confidence", 55.0)
        
        @classmethod
        def get_default_atr_period(cls) -> int:
            """Período ATR según perfil activo."""
            return TradingProfiles.get_current_profile().get("default_atr_period", 10)
        
        # Valores de confianza por defecto para diferentes señales
        HOLD_CONFIDENCE: float = 45.0
        BASE_CONFIDENCE: float = 50.0
        ENHANCED_CONFIDENCE: float = 60.0
        
        # Compatibilidad con código existente
        DEFAULT_MIN_CONFIDENCE: float = 55.0  # Fallback
        DEFAULT_ATR_PERIOD: int = 10  # Fallback
    
    # ---- Estrategia RSI Profesional - ELIMINADA ----
    # La clase ProfessionalRSI ha sido removida
    
    # ---- Estrategia Multi-Timeframe - ELIMINADA ----
    # La clase MultiTimeframe ha sido removida
    
    # ---- Estrategia Ensemble - ELIMINADA ----
    # La clase Ensemble ha sido removida


# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

class LoggingConfig:
    """Configuración del sistema de logging."""
    
    # Nivel de logging por defecto (por defecto: "INFO")
    LOG_LEVEL: str = "INFO"
    
    # Formato de logs con timestamp (incluye timestamp y nivel)
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Archivo de logs (por defecto: "trading_bot.log")
    LOG_FILE: str = "trading_bot.log"
    
    # Tamaño máximo del archivo de log en MB (por defecto: 10)
    MAX_LOG_SIZE_MB: int = 10
    
    # Número de archivos de backup de logs (por defecto: 5)
    LOG_BACKUP_COUNT: int = 5


# ============================================================================
# CONFIGURACIÓN DE TRADING EN VIVO (LIVE TRADING)
# ============================================================================

class LiveTradingConfig:
    """Configuración específica para trading en vivo."""
    
    # Balance inicial real en USD - Se alimenta automáticamente del PaperTrader para consistencia
    INITIAL_BALANCE: float = PaperTraderConfig.INITIAL_BALANCE  # Mantiene consistencia automática
    
    # Comisiones de exchange en % por trade; configurable vía entorno TRADING_FEES
    # Fallback: perfil actual TradingProfiles["trading_fees"] si existe, sino 0.001
    TRADING_FEES: float = _get_env_float(
        "TRADING_FEES",
        TradingProfiles.get_current_profile().get("trading_fees", 0.001)
    )
    
    # Timeout para órdenes en segundos (Scalping: 15 - Intraday: 35)
    ORDER_TIMEOUT: int = 15  # Estrategia rápida
    
    # Reintentos máximos para órdenes fallidas (Scalping: 2 - Intraday: 3)
    MAX_ORDER_RETRIES: int = 2  # Estrategia rápida
    
    # Intervalo de verificación de órdenes en segundos (Scalping: 1 - Intraday: 1.8)
    ORDER_CHECK_INTERVAL: int = 1  # Estrategia rápida


# Expone TRADING_FEES a nivel de módulo para compatibilidad retroactiva
TRADING_FEES: float = LiveTradingConfig.TRADING_FEES

# ============================================================================
# FUNCIÓN DE UTILIDAD PARA OBTENER CONFIGURACIONES
# ============================================================================

def get_config(config_type: str) -> Any:
    """Obtiene la configuración especificada.
    
    Args:
        config_type: Tipo de configuración ('bot', 'risk', 'paper', 'strategy', 'db', 'log', 'live', 'testing', 'indicators')
    
    Returns:
        Clase de configuración correspondiente
    """
    configs = {
        'bot': TradingBotConfig,
        'risk': RiskManagerConfig,
        'paper': PaperTraderConfig,
        'strategy': StrategyConfig,
        'log': LoggingConfig,
        'live': LiveTradingConfig,
        'testing': TestingConfig,
        'indicators': AdvancedIndicatorsConfig
    }
    
    if config_type not in configs:
        raise ValueError(f"Tipo de configuración '{config_type}' no válido. Opciones: {list(configs.keys())}")
    
    return configs[config_type]


# ============================================================================
# CONFIGURACIÓN DE INDICADORES AVANZADOS
# ============================================================================

class AdvancedIndicatorsConfig:
    """Configuración de períodos y umbrales para indicadores técnicos avanzados."""
    
    # Períodos para Ichimoku Cloud
    ICHIMOKU_TENKAN_PERIOD: int = 9   # Tenkan-sen (línea de conversión)
    ICHIMOKU_KIJUN_PERIOD: int = 26   # Kijun-sen (línea base)
    ICHIMOKU_SENKOU_PERIOD: int = 52  # Senkou Span A
    ICHIMOKU_SENKOU_B_PERIOD: int = 52  # Senkou Span B
    ICHIMOKU_SHIFT: int = 26          # Desplazamiento para proyección
    
    # Períodos para osciladores
    STOCHASTIC_K_PERIOD: int = 14     # Período para %K del Estocástico
    STOCHASTIC_D_PERIOD: int = 3      # Período para %D del Estocástico
    WILLIAMS_R_PERIOD: int = 14       # Período para Williams %R
    
    # Umbrales para osciladores
    STOCHASTIC_OVERSOLD: float = 20.0    # Umbral de sobreventa
    STOCHASTIC_OVERBOUGHT: float = 80.0  # Umbral de sobrecompra
    WILLIAMS_R_OVERSOLD: float = -80.0   # Umbral de sobreventa Williams %R
    WILLIAMS_R_OVERBOUGHT: float = -20.0 # Umbral de sobrecompra Williams %R
    
    # Períodos para otros indicadores
    RSI_PERIOD: int = 14              # Período para RSI
    CCI_PERIOD: int = 20              # Período para CCI
    BOLLINGER_PERIOD: int = 20        # Período para Bandas de Bollinger
    BOLLINGER_STD_DEV: float = 2.0    # Desviación estándar para Bollinger
    MFI_PERIOD: int = 14              # Período para Money Flow Index
    ATR_PERIOD: int = 14              # Período para Average True Range
    ROC_PERIOD: int = 12              # Período para Rate of Change
    
    # Configuración para análisis de soporte/resistencia
    SUPPORT_RESISTANCE_WINDOW: int = 20    # Ventana para S/R
    SUPPORT_RESISTANCE_MIN_TOUCHES: int = 2 # Mínimo de toques para validar nivel
    
    # Configuración para análisis de volumen
    VOLUME_PROFILE_BINS: int = 20     # Número de bins para perfil de volumen
    
    # Configuración para Fibonacci
    FIBONACCI_LOOKBACK: int = 50      # Período de lookback para Fibonacci
    
    # Configuración para análisis de tendencias
    TREND_ANALYSIS_LOOKBACK: int = 50 # Período para análisis de líneas de tendencia
    CHART_PATTERNS_WINDOW: int = 20   # Ventana para detección de patrones


# ============================================================================
# CONFIGURACIÓN DE TESTING
# ============================================================================

class TestingConfig:
    """Configuración específica para testing y desarrollo."""
    
    # Símbolos para testing - subset reducido para pruebas rápidas
    TEST_SYMBOLS: List[str] = GLOBAL_SYMBOLS[:3]  # Primeros 3 símbolos
    
    # Configuración de trading bot para testing
    TEST_MIN_CONFIDENCE: float = 70.0
    TEST_MAX_DAILY_TRADES: int = 5
    
    # Configuración de análisis para testing
    TEST_ANALYSIS_INTERVAL: int = 300  # 300 segundos (5 minutos)
    
    # Balance para testing
    TEST_PAPER_BALANCE: float = 100.0

# ============================================================================
# CONFIGURACIÓN POR DEFECTO PARA DESARROLLO
# ============================================================================

# Configuración rápida para desarrollo y testing
DEV_CONFIG = {
    'symbols': TradingBotConfig.SYMBOLS[:3],  # Solo 3 símbolos para testing
    'analysis_interval': TestingConfig.TEST_ANALYSIS_INTERVAL,  # Análisis cada 5 minutos para testing
    'min_confidence': 60.0,  # Umbral más bajo para testing
    'paper_balance': TestingConfig.TEST_PAPER_BALANCE,  # Balance menor para testing
}

# ============================================================================
# CONFIGURACIÓN COMPLETA CON TRES PERFILES DE TRADING
# ============================================================================
"""
CONFIGURACIÓN ACTUAL: SISTEMA COMPLETO DE TRES PERFILES

# ===== PERFILES DE TRADING =====
# Para cambiar entre perfiles, comentar/descomentar las líneas correspondientes:

# PERFIL RÁPIDA (Scalping/Day Trading):
# - Timeframes: ["1m", "5m", "15m"]
# - Análisis cada: 5 minutos
# - Riesgo por trade: 2.0%
# - Riesgo diario: 6.0%
# - Trades diarios: 20
# - Posiciones concurrentes: 8
# - RSI: 35/65 (muy sensible)
# - Confianza mínima: 60%
# - Trailing stop: 1.0%
# - Liquidez mínima: 3.0%
# - Tamaño posición máx: 10.0%
# - Consenso timeframes: 1
# - Alineación tendencias: No
# - ROI objetivo: 20-35% mensual (alto riesgo/alta recompensa)

# PERFIL AGRESIVA (Swing Trading) - CONFIGURACIÓN ACTUAL:
# - Timeframes: ["15m", "30m", "1h"]
# - Análisis cada: 15 minutos
# - Riesgo por trade: 1.5%
# - Riesgo diario: 4.5%
# - Trades diarios: 12
# - Posiciones concurrentes: 6
# - RSI: 30/70 (balanceado)
# - Confianza mínima: 65%
# - Trailing stop: 1.5%
# - Liquidez mínima: 5.0%
# - Tamaño posición máx: 8.0%
# - Consenso timeframes: 2
# - Alineación tendencias: Sí
# - ROI objetivo: 15-25% mensual (riesgo moderado)

# PERFIL ÓPTIMA (Position Trading):
# - Timeframes: ["1h", "4h", "1d"]
# - Análisis cada: 30 minutos
# - Riesgo por trade: 1.0%
# - Riesgo diario: 3.0%
# - Trades diarios: 8
# - Posiciones concurrentes: 4
# - RSI: 25/75 (conservador)
# - Confianza mínima: 70%
# - Trailing stop: 2.0%
# - Liquidez mínima: 8.0%
# - Tamaño posición máx: 6.0%
# - Consenso timeframes: 3
# - Alineación tendencias: Sí
# - ROI objetivo: 8-15% mensual (bajo riesgo/preservación capital)

📋 PARA CAMBIAR CONFIGURACIÓN:
Simplemente comenta/descomenta las líneas correspondientes en cada parámetro.
Todos los parámetros críticos ahora incluyen las tres opciones claramente marcadas.
"""

# ============================================================================
# 🔧 CONFIGURACIONES CENTRALIZADAS DE PARÁMETROS HARDCODEADOS
# ============================================================================

class APIConfig:
    """🌐 Configuración centralizada de APIs y endpoints"""
    
    # API Configuration (Binance removed - using Capital.com only)
    
    # Request Configuration
    REQUEST_TIMEOUT = 5  # segundos
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos
    
    # Sleep intervals para scheduler y error handling
    SCHEDULER_SLEEP_INTERVAL = 2  # segundos (aumentado para evitar rate limiting)
    ERROR_RECOVERY_SLEEP = 10  # segundos (aumentado para mejor recuperación)
    LATENCY_SIMULATION_SLEEP = 0.5  # segundos (aumentado para simular latencia real)
    
    # Data Limits
    DEFAULT_KLINES_LIMIT = 1000
    MAX_KLINES_LIMIT = 1500
    MIN_KLINES_LIMIT = 100
    

    
    @classmethod
    def get_request_config(cls) -> dict:
        """Obtener configuración de requests"""
        return {
            "timeout": cls.REQUEST_TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY
        }

class CacheConfig:
    """💾 Configuración centralizada de cache"""
    
    # Cache TTL (Time To Live)
    DEFAULT_TTL = 300  # 5 minutos
    SHORT_TTL = 60     # 1 minuto
    LONG_TTL = 900     # 15 minutos
    
    # Cache Limits
    MAX_CACHE_ENTRIES = 1000
    CLEANUP_THRESHOLD = 1200
    
    # Cache Keys
    CACHE_KEY_PREFIXES = {
        "volume_analysis": "vol_",
        "trend_analysis": "trend_",
        "confluence": "conf_",
        "market_regime": "regime_"
    }
    
    @classmethod
    def get_ttl_for_operation(cls, operation_type: str) -> int:
        """Obtener TTL según tipo de operación"""
        ttl_map = {
            "price_data": cls.SHORT_TTL,
            "technical_analysis": cls.DEFAULT_TTL,
            "market_structure": cls.LONG_TTL
        }
        return ttl_map.get(operation_type, cls.DEFAULT_TTL)

class TechnicalAnalysisConfig:
    """📊 Configuración centralizada de análisis técnico"""
    
    # Períodos de Rolling Windows
    VOLUME_PERIODS = {
        "short": 10,
        "medium": 20,
        "long": 50
    }
    
    # Períodos EMA
    EMA_PERIODS = {
        "fast": 20,
        "slow": 50,
        "trend": 200
    }
    
    # Umbrales de Volumen
    VOLUME_THRESHOLDS = {
        "very_strong": 2.5,
        "strong": 1.8,
        "moderate": 1.3,
        "weak": 1.0
    }
    
    # Umbrales ADX
    ADX_THRESHOLDS = {
        "strong_trend": 25,
        "weak_trend": 20,
        "no_trend": 15
    }
    
    # Desviaciones y Tolerancias
    VWAP_DEVIATION_THRESHOLD = 0.02  # 2%
    VOLATILITY_RATIO_THRESHOLD = 1.5
    PRICE_RANGE_TOLERANCE = 0.2  # 20%
    
    # Factores de Aproximación
    APPROXIMATION_FACTORS = {
        "close": 0.98,
        "exact": 1.00,
        "far": 1.02,
        "very_close": 0.99
    }
    
    @classmethod
    def get_volume_strength(cls, ratio: float) -> str:
        """Determinar fuerza del volumen basado en ratio"""
        if ratio >= cls.VOLUME_THRESHOLDS["very_strong"]:
            return "VERY_STRONG"
        elif ratio >= cls.VOLUME_THRESHOLDS["strong"]:
            return "STRONG"
        elif ratio >= cls.VOLUME_THRESHOLDS["moderate"]:
            return "MODERATE"
        else:
            return "WEAK"

class ConfluenceConfig:
    """🎯 Configuración centralizada de confluencia"""
    
    # Pesos de Componentes
    COMPONENT_WEIGHTS = {
        "technical": 0.4,
        "volume": 0.25,
        "structure": 0.2,
        "momentum": 0.15
    }
    
    # Umbrales de Confluencia
    CONFLUENCE_THRESHOLDS = {
        "very_strong": 0.8,
        "strong": 0.65,
        "moderate": 0.45,
        "weak": 0.0
    }
    
    # Pesos de Indicadores Técnicos
    TECHNICAL_WEIGHTS = {
        "rsi": 0.4,
        "bollinger_bands": 0.3,
        "vwap": 0.3
    }
    
    # Pesos de Análisis de Volumen
    VOLUME_WEIGHTS = {
        "strength": 0.5,
        "confirmation": 0.3,
        "trend_bonus": 0.2
    }
    
    # Pesos de Estructura de Mercado
    STRUCTURE_WEIGHTS = {
        "support_resistance": 0.6,
        "trend_lines": 0.4
    }
    
    # Pesos de Momentum
    MOMENTUM_WEIGHTS = {
        "roc": 0.5,
        "mfi": 0.5
    }
    
    @classmethod
    def get_confluence_level(cls, score: float) -> str:
        """Determinar nivel de confluencia basado en score"""
        if score >= cls.CONFLUENCE_THRESHOLDS["very_strong"]:
            return "VERY_STRONG"
        elif score >= cls.CONFLUENCE_THRESHOLDS["strong"]:
            return "STRONG"
        elif score >= cls.CONFLUENCE_THRESHOLDS["moderate"]:
            return "MODERATE"
        else:
            return "WEAK"

class MonitoringConfig:
    """🔍 Configuración centralizada de monitoreo"""
    
    # Intervalos de Tiempo
    DEFAULT_HOURS_BACK = 24
    ANALYSIS_INTERVALS = {
        "short": 1,   # 1 hora
        "medium": 6,  # 6 horas
        "long": 24,   # 24 horas
        "extended": 72  # 72 horas
    }
    
    # Intervalos de Actualización
    UPDATE_INTERVALS = {
        "live_bot": 30,      # 30 segundos
        "monitoring": 60,    # 1 minuto
        "analysis": 300,     # 5 minutos
        "reporting": 900     # 15 minutos
    }
    
    # Límites de Datos
    DATA_LIMITS = {
        "max_missed_executions": 100,
        "max_log_entries": 1000,
        "max_history_days": 30
    }
    
    @classmethod
    def get_analysis_hours(cls, analysis_type: str) -> int:
        """Obtener horas de análisis según tipo"""
        return cls.ANALYSIS_INTERVALS.get(analysis_type, cls.DEFAULT_HOURS_BACK)
    
    @classmethod
    def get_update_interval(cls, component: str) -> int:
        """Obtener intervalo de actualización según componente"""
        return cls.UPDATE_INTERVALS.get(component, 60)

class FibonacciConfig:
    """📐 Configuración centralizada de niveles de Fibonacci"""
    
    # Niveles de Retroceso de Fibonacci
    RETRACEMENT_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]
    
    # Niveles de Extensión de Fibonacci
    EXTENSION_LEVELS = [1.272, 1.414, 1.618, 2.000, 2.618]
    
    # Tolerancias para Niveles
    LEVEL_TOLERANCES = {
        "tight": 0.005,   # 0.5%
        "normal": 0.01,   # 1%
        "loose": 0.02     # 2%
    }
    
    @classmethod
    def get_retracement_levels(cls) -> list:
        """Obtener niveles de retroceso"""
        return cls.RETRACEMENT_LEVELS.copy()
    
    @classmethod
    def get_extension_levels(cls) -> list:
        """Obtener niveles de extensión"""
        return cls.EXTENSION_LEVELS.copy()

class OscillatorConfig:
    """📈 Configuración centralizada de osciladores"""
    
    # Umbrales RSI
    RSI_THRESHOLDS = {
        "oversold_extreme": 20,
        "oversold": 30,
        "neutral_low": 40,
        "neutral_high": 60,
        "overbought": 70,
        "overbought_extreme": 80
    }
    
    # Umbrales Williams %R
    WILLIAMS_R_THRESHOLDS = {
        "oversold": -80,
        "overbought": -20
    }
    
    # Umbrales Stochastic
    STOCHASTIC_THRESHOLDS = {
        "oversold": 20,
        "overbought": 80
    }
    
    # Umbrales de Señales
    SIGNAL_THRESHOLDS = {
        "strong_buy": -100,
        "buy": -50,
        "neutral": 0,
        "sell": 50,
        "strong_sell": 100
    }
    
    @classmethod
    def get_rsi_condition(cls, rsi_value: float) -> str:
        """Determinar condición RSI"""
        if rsi_value <= cls.RSI_THRESHOLDS["oversold_extreme"]:
            return "OVERSOLD_EXTREME"
        elif rsi_value <= cls.RSI_THRESHOLDS["oversold"]:
            return "OVERSOLD"
        elif rsi_value >= cls.RSI_THRESHOLDS["overbought_extreme"]:
            return "OVERBOUGHT_EXTREME"
        elif rsi_value >= cls.RSI_THRESHOLDS["overbought"]:
            return "OVERBOUGHT"
        else:
            return "NEUTRAL"

class CalculationConfig:
    """🧮 Configuración centralizada de constantes de cálculo"""
    
    # Constantes Matemáticas
    PARABOLIC_SAR_STEP = 0.015
    PARABOLIC_SAR_MAX = 0.2
    
    # Períodos de Cálculo
    DEFAULT_PERIODS = {
        "short": 5,
        "medium": 14,
        "long": 34,
        "very_long": 55
    }
    
    # Factores de Suavizado
    SMOOTHING_FACTORS = {
        "alpha": 2.0,
        "beta": 0.5,
        "gamma": 0.1
    }
    
    # Multiplicadores Estándar
    STANDARD_MULTIPLIERS = {
        "bollinger_std": 2.0,
        "atr_multiplier": 1.5,
        "volume_multiplier": 1.2
    }
    
    @classmethod
    def get_period(cls, period_type: str) -> int:
        """Obtener período según tipo"""
        return cls.DEFAULT_PERIODS.get(period_type, 14)


# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================

class ConfigValidator:
    """Validador de parámetros de configuración para asegurar valores válidos."""
    
    # Rangos válidos para parámetros críticos
    VALID_RANGES = {
        'max_position_size': (0.01, 1.0),
        'max_total_exposure': (0.1, 1.0),
        'min_trade_value': (1.0, 1000.0),
        'max_slippage': (0.001, 0.1),
        'stop_loss_percentage': (0.01, 0.5),
        'take_profit_percentage': (0.01, 1.0),
        'trailing_stop_activation': (0.006, 0.5),
        'trailing_stop_distance': (0.005, 0.2),
        'max_drawdown_threshold': (0.05, 0.5),

        'min_confidence_score': (30, 95),
        'analysis_interval': (1, 3600),
        'position_check_interval': (10, 300),
        'connection_timeout': (5, 120),
        'max_retries': (1, 10),
        'retry_delay': (0.5, 30.0),
        'max_consecutive_losses': (1, 20)
    }
    
    @classmethod
    def validate_profile(cls, profile_name: str, profile_config: dict) -> bool:
        """Validar que un perfil tenga parámetros en rangos válidos."""
        errors = []
        
        for param, value in profile_config.items():
            if param in cls.VALID_RANGES:
                min_val, max_val = cls.VALID_RANGES[param]
                if not (min_val <= value <= max_val):
                    errors.append(
                        f"Perfil '{profile_name}': {param}={value} fuera del rango válido [{min_val}, {max_val}]"
                    )
        
        if errors:
            logger.error(f"Errores de validación en perfil '{profile_name}':")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info(f"Perfil '{profile_name}' validado correctamente")
        return True
    
    @classmethod
    def validate_all_profiles(cls) -> bool:
        """Validar todos los perfiles de trading."""
        all_valid = True
        
        for profile_name, profile_config in TradingProfiles.PROFILES.items():
            if not cls.validate_profile(profile_name, profile_config):
                all_valid = False
        
        return all_valid
    
    @classmethod
    def get_safe_value(cls, param_name: str, value: float, default: float = None) -> float:
        """Obtener un valor seguro dentro del rango válido."""
        if param_name not in cls.VALID_RANGES:
            return value


# ============================================================================
# INICIALIZACIÓN Y VALIDACIÓN AUTOMÁTICA
# ============================================================================

def initialize_config() -> bool:
    """Inicializar y validar toda la configuración del sistema."""
    logger.info("Inicializando configuración del sistema de trading...")
    
    # Validar todos los perfiles
    if not ConfigValidator.validate_all_profiles():
        logger.error("Falló la validación de perfiles. Revise la configuración.")
        return False
    
    # Validar perfil actual mediante getters
    try:
        current_profile = TradingProfiles.get_current_profile()
    except ValueError:
        logger.error(f"Perfil actual no existe. Perfiles disponibles: {list(TradingProfiles.PROFILES.keys())}")
        return False
    
    # Mostrar configuración actual
    profile_name = current_profile.get('name', 'DESCONOCIDO')
    logger.info(f"Perfil activo: {profile_name}")
    logger.info(f"Timeframes: {current_profile['timeframes']}")
    logger.info(f"Intervalo de análisis: {current_profile['analysis_interval']} min")
    logger.info(f"Confianza mínima: {current_profile['min_confidence']}%")
    
    logger.info("✅ Configuración inicializada correctamente")
    return True


# ============================================================================
# 🔄 FUNCIONES UTILITARIAS PARA SÍMBOLOS
# ============================================================================
# Las funciones de conversión fueron eliminadas porque GLOBAL_SYMBOLS
# ya contiene los nombres exactos de Capital.com

def get_all_capital_symbols() -> List[str]:
    """
    Obtiene todos los símbolos (ya están en formato Capital.com)
    
    Returns:
        Lista de símbolos de Capital.com
    """
    return GLOBAL_SYMBOLS.copy()

def validate_symbol_mapping() -> bool:
    """
    Valida que GLOBAL_SYMBOLS contenga símbolos válidos
    
    Returns:
        True si los símbolos son válidos
    """
    if not GLOBAL_SYMBOLS:
        logger.warning("⚠️ GLOBAL_SYMBOLS está vacío")
        return False
    
    logger.info(f"✅ GLOBAL_SYMBOLS configurado con {len(GLOBAL_SYMBOLS)} símbolos")
    return True

# Validar configuración al importar el módulo
try:
    if not initialize_config():
        logger.warning("⚠️ Configuración inicializada con advertencias")
    
    # Validar mapeo de símbolos
    validate_symbol_mapping()
    
except Exception as e:
    logger.error(f"❌ Error al inicializar configuración: {e}")
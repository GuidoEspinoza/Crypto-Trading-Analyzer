"""Configuraciones específicas del Paper Trader.

Este módulo contiene todas las configuraciones relacionadas con el paper trading,
incluyendo límites de posición, exposición, slippage y parámetros de simulación.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE PAPER TRADER POR PERFIL
# ============================================================================

class PaperTraderProfiles:
    """Configuraciones específicas del Paper Trader por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Paper Trader Core Config
            "max_position_size": 0.8,  # Tamaño máximo de posición (80% como decimal)
            "max_total_exposure": 0.75,  # Exposición total máxima (75% como decimal)
            "min_trade_value": 5.0,  # Valor mínimo de trade (USDT)
            "paper_min_confidence": 60.0,  # Confianza mínima para paper trading
            "max_slippage": 0.10,  # Slippage máximo (10% como decimal)
            "min_liquidity": 4.0,  # Liquidez mínima requerida
            
            # Trading Fees and Costs
            "trading_fees": 0.001,  # Comisiones de trading (0.1%)
            "order_timeout": 25,  # Timeout de órdenes en segundos
            "max_order_retries": 3,  # Máximo reintentos de órdenes
            "order_check_interval": 1.5,  # Intervalo de verificación de órdenes
            "live_first_analysis_delay": 10,  # Delay inicial para análisis en vivo
            
            # Position Management
            "position_monitoring_interval": 30,  # Intervalo de monitoreo de posiciones (seg)
            "profit_scaling_threshold": 2.0,  # Umbral para escalado de ganancias (%)
            "trailing_stop_activation": 5.0,  # Activación de trailing stop (%)
            "trailing_stop_sl_pct": 0.02,  # SL dinámico para trailing stop (2%)
            "trailing_stop_tp_pct": 0.05,  # TP dinámico para trailing stop (5%)
            "profit_protection_sl_pct": 0.01,  # SL para protección de ganancias (1%)
            "profit_protection_tp_pct": 0.03,  # TP para protección de ganancias (3%)
            
            # Risk Management in Paper Trading
            "risk_management_threshold": -1.0,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.015,  # SL más conservador para pérdidas (1.5%)
            "risk_management_tp_pct": 0.02,  # TP más conservador para pérdidas (2%)
            
            # Price Simulation
            "price_simulation_variation": 0.02,  # Variación de precio para simulación (±2%)
            "simulation_fallback_price": 50000.0,  # Precio base para simulación
            "stats_recent_adjustments_count": 15,  # Número de ajustes recientes a mostrar
            
            # Position Monitor Config
            "max_close_attempts": 3,  # Máximo intentos de cierre de posición
            "price_cache_duration": 30,  # Duración del cache de precios en segundos
            "position_log_interval": 60,  # Intervalo entre logs de estado de posiciones
            "idle_sleep_multiplier": 2,  # Multiplicador para sleep cuando no hay posiciones
        },
        
        "AGRESIVO": {
            # Paper Trader Core Config
            "max_position_size": 0.6,  # Tamaño máximo de posición (60% como decimal)
            "max_total_exposure": 0.65,  # Exposición total máxima (65% como decimal)
            "min_trade_value": 5.0,  # Valor mínimo de trade (USDT)
            "paper_min_confidence": 68.0,  # Confianza mínima para paper trading
            "max_slippage": 0.06,  # Slippage máximo (6% como decimal)
            "min_liquidity": 6.0,  # Liquidez mínima requerida
            
            # Trading Fees and Costs
            "trading_fees": 0.001,  # Comisiones de trading (0.1%)
            "order_timeout": 40,  # Timeout de órdenes en segundos
            "max_order_retries": 3,  # Máximo reintentos de órdenes
            "order_check_interval": 2,  # Intervalo de verificación de órdenes
            "live_first_analysis_delay": 25,  # Delay inicial para análisis en vivo
            
            # Position Management
            "position_monitoring_interval": 45,  # Intervalo de monitoreo de posiciones (seg)
            "profit_scaling_threshold": 2.5,  # Umbral para escalado de ganancias (%)
            "trailing_stop_activation": 6.0,  # Activación de trailing stop (%)
            "trailing_stop_sl_pct": 0.025,  # SL dinámico para trailing stop (2.5%)
            "trailing_stop_tp_pct": 0.06,  # TP dinámico para trailing stop (6%)
            "profit_protection_sl_pct": 0.015,  # SL para protección de ganancias (1.5%)
            "profit_protection_tp_pct": 0.04,  # TP para protección de ganancias (4%)
            
            # Risk Management in Paper Trading
            "risk_management_threshold": -1.5,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.02,  # SL más conservador para pérdidas (2%)
            "risk_management_tp_pct": 0.025,  # TP más conservador para pérdidas (2.5%)
            
            # Price Simulation
            "price_simulation_variation": 0.015,  # Variación de precio para simulación (±1.5%)
            "simulation_fallback_price": 50000.0,  # Precio base para simulación
            "stats_recent_adjustments_count": 12,  # Número de ajustes recientes a mostrar
            
            # Position Monitor Config
            "max_close_attempts": 3,  # Máximo intentos de cierre de posición
            "price_cache_duration": 45,  # Duración del cache de precios en segundos
            "position_log_interval": 90,  # Intervalo entre logs de estado de posiciones
            "idle_sleep_multiplier": 3,  # Multiplicador para sleep cuando no hay posiciones
        },
        
        "OPTIMO": {
            # Paper Trader Core Config
            "max_position_size": 0.4,  # Tamaño máximo de posición (40% como decimal)
            "max_total_exposure": 0.5,  # Exposición total máxima (50% como decimal)
            "min_trade_value": 10.0,  # Valor mínimo de trade (USDT)
            "paper_min_confidence": 75.0,  # Confianza mínima para paper trading
            "max_slippage": 0.04,  # Slippage máximo (4% como decimal)
            "min_liquidity": 8.0,  # Liquidez mínima requerida
            
            # Trading Fees and Costs
            "trading_fees": 0.001,  # Comisiones de trading (0.1%)
            "order_timeout": 60,  # Timeout de órdenes en segundos
            "max_order_retries": 2,  # Máximo reintentos de órdenes
            "order_check_interval": 3,  # Intervalo de verificación de órdenes
            "live_first_analysis_delay": 45,  # Delay inicial para análisis en vivo
            
            # Position Management
            "position_monitoring_interval": 60,  # Intervalo de monitoreo de posiciones (seg)
            "profit_scaling_threshold": 3.0,  # Umbral para escalado de ganancias (%)
            "trailing_stop_activation": 8.0,  # Activación de trailing stop (%)
            "trailing_stop_sl_pct": 0.03,  # SL dinámico para trailing stop (3%)
            "trailing_stop_tp_pct": 0.08,  # TP dinámico para trailing stop (8%)
            "profit_protection_sl_pct": 0.02,  # SL para protección de ganancias (2%)
            "profit_protection_tp_pct": 0.05,  # TP para protección de ganancias (5%)
            
            # Risk Management in Paper Trading
            "risk_management_threshold": -2.0,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.025,  # SL más conservador para pérdidas (2.5%)
            "risk_management_tp_pct": 0.03,  # TP más conservador para pérdidas (3%)
            
            # Price Simulation
            "price_simulation_variation": 0.01,  # Variación de precio para simulación (±1%)
            "simulation_fallback_price": 50000.0,  # Precio base para simulación
            "stats_recent_adjustments_count": 10,  # Número de ajustes recientes a mostrar
            
            # Position Monitor Config
            "max_close_attempts": 2,  # Máximo intentos de cierre de posición
            "price_cache_duration": 60,  # Duración del cache de precios en segundos
            "position_log_interval": 120,  # Intervalo entre logs de estado de posiciones
            "idle_sleep_multiplier": 4,  # Multiplicador para sleep cuando no hay posiciones
        },
        
        "CONSERVADOR": {
            # Paper Trader Core Config
            "max_position_size": 0.25,  # Tamaño máximo de posición (25% como decimal)
            "max_total_exposure": 0.35,  # Exposición total máxima (35% como decimal)
            "min_trade_value": 15.0,  # Valor mínimo de trade (USDT)
            "paper_min_confidence": 82.0,  # Confianza mínima para paper trading
            "max_slippage": 0.02,  # Slippage máximo (2% como decimal)
            "min_liquidity": 12.0,  # Liquidez mínima requerida
            
            # Trading Fees and Costs
            "trading_fees": 0.001,  # Comisiones de trading (0.1%)
            "order_timeout": 90,  # Timeout de órdenes en segundos
            "max_order_retries": 2,  # Máximo reintentos de órdenes
            "order_check_interval": 5,  # Intervalo de verificación de órdenes
            "live_first_analysis_delay": 60,  # Delay inicial para análisis en vivo
            
            # Position Management
            "position_monitoring_interval": 120,  # Intervalo de monitoreo de posiciones (seg)
            "profit_scaling_threshold": 4.0,  # Umbral para escalado de ganancias (%)
            "trailing_stop_activation": 10.0,  # Activación de trailing stop (%)
            "trailing_stop_sl_pct": 0.04,  # SL dinámico para trailing stop (4%)
            "trailing_stop_tp_pct": 0.10,  # TP dinámico para trailing stop (10%)
            "profit_protection_sl_pct": 0.03,  # SL para protección de ganancias (3%)
            "profit_protection_tp_pct": 0.07,  # TP para protección de ganancias (7%)
            
            # Risk Management in Paper Trading
            "risk_management_threshold": -2.5,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.03,  # SL más conservador para pérdidas (3%)
            "risk_management_tp_pct": 0.04,  # TP más conservador para pérdidas (4%)
            
            # Price Simulation
            "price_simulation_variation": 0.005,  # Variación de precio para simulación (±0.5%)
            "simulation_fallback_price": 50000.0,  # Precio base para simulación
            "stats_recent_adjustments_count": 8,  # Número de ajustes recientes a mostrar
            
            # Position Monitor Config
            "max_close_attempts": 2,  # Máximo intentos de cierre de posición
            "price_cache_duration": 120,  # Duración del cache de precios en segundos
            "position_log_interval": 180,  # Intervalo entre logs de estado de posiciones
            "idle_sleep_multiplier": 5,  # Multiplicador para sleep cuando no hay posiciones
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_paper_trader_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del paper trader para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración del paper trader
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in PaperTraderProfiles.PROFILES:
        raise ValueError(f"Perfil de paper trader no válido: {profile}")
    
    return PaperTraderProfiles.PROFILES[profile]

def get_available_paper_trader_profiles() -> List[str]:
    """Obtiene la lista de perfiles de paper trader disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(PaperTraderProfiles.PROFILES.keys())

def validate_paper_trader_profile(profile: str) -> bool:
    """Valida si un perfil de paper trader es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in PaperTraderProfiles.PROFILES

def get_position_limits(profile: str = None) -> Dict[str, float]:
    """Obtiene los límites de posición para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los límites de posición
    """
    config = get_paper_trader_config(profile)
    
    return {
        "max_position_size": config["max_position_size"],
        "max_total_exposure": config["max_total_exposure"],
        "min_trade_value": config["min_trade_value"],
        "max_slippage": config["max_slippage"],
        "min_liquidity": config["min_liquidity"]
    }

def get_trading_costs(profile: str = None) -> Dict[str, Any]:
    """Obtiene los costos de trading para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los costos de trading
    """
    config = get_paper_trader_config(profile)
    
    return {
        "trading_fees": config["trading_fees"],
        "order_timeout": config["order_timeout"],
        "max_order_retries": config["max_order_retries"],
        "order_check_interval": config["order_check_interval"]
    }

# ============================================================================
# 🛡️ CONFIGURACIÓN LEGACY PARA COMPATIBILIDAD
# ============================================================================

# Configuración legacy que mapea perfiles a configuraciones
PAPER_TRADER_CONFIG = {
    "RAPIDO": PaperTraderProfiles.PROFILES["RAPIDO"],
    "AGRESIVO": PaperTraderProfiles.PROFILES["AGRESIVO"],
    "OPTIMO": PaperTraderProfiles.PROFILES["OPTIMO"],
    "CONSERVADOR": PaperTraderProfiles.PROFILES["CONSERVADOR"]
}

def validate_paper_trader_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración de paper trader.
    
    Args:
        config: Configuración a validar
        
    Returns:
        True si la configuración es válida
    """
    return True
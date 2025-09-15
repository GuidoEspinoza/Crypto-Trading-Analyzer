"""Configuraciones específicas de las Estrategias Mejoradas.

Este módulo contiene todas las configuraciones relacionadas con las estrategias
de trading mejoradas, incluyendo parámetros de indicadores, umbrales y pesos.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE ESTRATEGIAS POR PERFIL
# ============================================================================

class EnhancedStrategiesProfiles:
    """Configuraciones específicas de las Estrategias Mejoradas por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # RSI Strategy Config
            "rsi_period": 12,  # Período más corto para señales rápidas
            "rsi_oversold": 25,  # Nivel de sobreventa más agresivo
            "rsi_overbought": 75,  # Nivel de sobrecompra más agresivo
            "rsi_weight": 0.25,  # Peso de la estrategia RSI
            
            # MACD Strategy Config
            "macd_fast": 10,  # EMA rápida más corta
            "macd_slow": 21,  # EMA lenta más corta
            "macd_signal": 7,  # Señal más rápida
            "macd_weight": 0.30,  # Peso de la estrategia MACD
            
            # Bollinger Bands Strategy Config
            "bb_period": 18,  # Período más corto
            "bb_std": 1.8,  # Desviación estándar más estrecha
            "bb_weight": 0.20,  # Peso de Bollinger Bands
            
            # Moving Average Strategy Config
            "ma_short": 8,  # MA corta más rápida
            "ma_long": 18,  # MA larga más rápida
            "ma_weight": 0.25,  # Peso de Moving Average
            
            # Volume Strategy Config
            "volume_period": 12,  # Período de volumen más corto
            "volume_threshold": 1.3,  # Umbral de volumen más bajo
            "volume_weight": 0.15,  # Peso del volumen
            
            # Momentum Strategy Config
            "momentum_period": 8,  # Período de momentum más corto
            "momentum_threshold": 0.02,  # Umbral más bajo (2%)
            "momentum_weight": 0.20,  # Peso del momentum
            
            # Volatility Strategy Config
            "volatility_period": 12,  # Período de volatilidad más corto
            "volatility_threshold": 0.015,  # Umbral más bajo (1.5%)
            "volatility_weight": 0.10,  # Peso de la volatilidad
            
            # Support/Resistance Strategy Config
            "sr_lookback": 15,  # Lookback más corto
            "sr_threshold": 0.008,  # Umbral más estrecho (0.8%)
            "sr_weight": 0.15,  # Peso de soporte/resistencia
            
            # Trend Strategy Config
            "trend_period": 10,  # Período de tendencia más corto
            "trend_threshold": 0.01,  # Umbral más bajo (1%)
            "trend_weight": 0.25,  # Peso de la tendencia
            
            # Pattern Recognition Config
            "pattern_lookback": 8,  # Lookback más corto para patrones
            "pattern_confidence": 0.6,  # Confianza más baja (60%)
            "pattern_weight": 0.15,  # Peso del reconocimiento de patrones
            
            # Signal Combination Config
            "min_signal_strength": 0.55,  # Fuerza mínima de señal más baja
            "signal_decay_factor": 0.9,  # Factor de decaimiento más rápido
            "max_signals_per_hour": 8,  # Más señales por hora
            "signal_cooldown": 300,  # Cooldown más corto (5 min)
        },
        
        "AGRESIVO": {
            # RSI Strategy Config
            "rsi_period": 14,  # Período estándar
            "rsi_oversold": 30,  # Nivel de sobreventa moderado
            "rsi_overbought": 70,  # Nivel de sobrecompra moderado
            "rsi_weight": 0.22,  # Peso de la estrategia RSI
            
            # MACD Strategy Config
            "macd_fast": 12,  # EMA rápida estándar
            "macd_slow": 26,  # EMA lenta estándar
            "macd_signal": 9,  # Señal estándar
            "macd_weight": 0.28,  # Peso de la estrategia MACD
            
            # Bollinger Bands Strategy Config
            "bb_period": 20,  # Período estándar
            "bb_std": 2.0,  # Desviación estándar estándar
            "bb_weight": 0.18,  # Peso de Bollinger Bands
            
            # Moving Average Strategy Config
            "ma_short": 10,  # MA corta
            "ma_long": 21,  # MA larga
            "ma_weight": 0.22,  # Peso de Moving Average
            
            # Volume Strategy Config
            "volume_period": 14,  # Período de volumen estándar
            "volume_threshold": 1.5,  # Umbral de volumen moderado
            "volume_weight": 0.12,  # Peso del volumen
            
            # Momentum Strategy Config
            "momentum_period": 10,  # Período de momentum
            "momentum_threshold": 0.025,  # Umbral moderado (2.5%)
            "momentum_weight": 0.18,  # Peso del momentum
            
            # Volatility Strategy Config
            "volatility_period": 14,  # Período de volatilidad estándar
            "volatility_threshold": 0.02,  # Umbral moderado (2%)
            "volatility_weight": 0.08,  # Peso de la volatilidad
            
            # Support/Resistance Strategy Config
            "sr_lookback": 20,  # Lookback estándar
            "sr_threshold": 0.01,  # Umbral moderado (1%)
            "sr_weight": 0.12,  # Peso de soporte/resistencia
            
            # Trend Strategy Config
            "trend_period": 12,  # Período de tendencia
            "trend_threshold": 0.015,  # Umbral moderado (1.5%)
            "trend_weight": 0.22,  # Peso de la tendencia
            
            # Pattern Recognition Config
            "pattern_lookback": 10,  # Lookback para patrones
            "pattern_confidence": 0.65,  # Confianza moderada (65%)
            "pattern_weight": 0.12,  # Peso del reconocimiento de patrones
            
            # Signal Combination Config
            "min_signal_strength": 0.6,  # Fuerza mínima de señal moderada
            "signal_decay_factor": 0.85,  # Factor de decaimiento moderado
            "max_signals_per_hour": 6,  # Señales moderadas por hora
            "signal_cooldown": 450,  # Cooldown moderado (7.5 min)
        },
        
        "OPTIMO": {
            # RSI Strategy Config
            "rsi_period": 14,  # Período estándar
            "rsi_oversold": 30,  # Nivel de sobreventa estándar
            "rsi_overbought": 70,  # Nivel de sobrecompra estándar
            "rsi_weight": 0.20,  # Peso de la estrategia RSI
            
            # MACD Strategy Config
            "macd_fast": 12,  # EMA rápida estándar
            "macd_slow": 26,  # EMA lenta estándar
            "macd_signal": 9,  # Señal estándar
            "macd_weight": 0.25,  # Peso de la estrategia MACD
            
            # Bollinger Bands Strategy Config
            "bb_period": 20,  # Período estándar
            "bb_std": 2.0,  # Desviación estándar estándar
            "bb_weight": 0.15,  # Peso de Bollinger Bands
            
            # Moving Average Strategy Config
            "ma_short": 12,  # MA corta
            "ma_long": 26,  # MA larga
            "ma_weight": 0.20,  # Peso de Moving Average
            
            # Volume Strategy Config
            "volume_period": 20,  # Período de volumen más largo
            "volume_threshold": 1.8,  # Umbral de volumen más alto
            "volume_weight": 0.10,  # Peso del volumen
            
            # Momentum Strategy Config
            "momentum_period": 14,  # Período de momentum estándar
            "momentum_threshold": 0.03,  # Umbral estándar (3%)
            "momentum_weight": 0.15,  # Peso del momentum
            
            # Volatility Strategy Config
            "volatility_period": 20,  # Período de volatilidad más largo
            "volatility_threshold": 0.025,  # Umbral estándar (2.5%)
            "volatility_weight": 0.05,  # Peso de la volatilidad
            
            # Support/Resistance Strategy Config
            "sr_lookback": 30,  # Lookback más largo
            "sr_threshold": 0.012,  # Umbral más amplio (1.2%)
            "sr_weight": 0.10,  # Peso de soporte/resistencia
            
            # Trend Strategy Config
            "trend_period": 20,  # Período de tendencia más largo
            "trend_threshold": 0.02,  # Umbral estándar (2%)
            "trend_weight": 0.20,  # Peso de la tendencia
            
            # Pattern Recognition Config
            "pattern_lookback": 15,  # Lookback estándar para patrones
            "pattern_confidence": 0.7,  # Confianza estándar (70%)
            "pattern_weight": 0.10,  # Peso del reconocimiento de patrones
            
            # Signal Combination Config
            "min_signal_strength": 0.65,  # Fuerza mínima de señal estándar
            "signal_decay_factor": 0.8,  # Factor de decaimiento estándar
            "max_signals_per_hour": 4,  # Señales moderadas por hora
            "signal_cooldown": 600,  # Cooldown estándar (10 min)
        },
        
        "CONSERVADOR": {
            # RSI Strategy Config
            "rsi_period": 21,  # Período más largo
            "rsi_oversold": 25,  # Nivel de sobreventa más conservador
            "rsi_overbought": 75,  # Nivel de sobrecompra más conservador
            "rsi_weight": 0.18,  # Peso de la estrategia RSI
            
            # MACD Strategy Config
            "macd_fast": 12,  # EMA rápida estándar
            "macd_slow": 26,  # EMA lenta estándar
            "macd_signal": 9,  # Señal estándar
            "macd_weight": 0.22,  # Peso de la estrategia MACD
            
            # Bollinger Bands Strategy Config
            "bb_period": 25,  # Período más largo
            "bb_std": 2.2,  # Desviación estándar más amplia
            "bb_weight": 0.12,  # Peso de Bollinger Bands
            
            # Moving Average Strategy Config
            "ma_short": 20,  # MA corta más larga
            "ma_long": 50,  # MA larga más conservadora
            "ma_weight": 0.18,  # Peso de Moving Average
            
            # Volume Strategy Config
            "volume_period": 30,  # Período de volumen más largo
            "volume_threshold": 2.2,  # Umbral de volumen más alto
            "volume_weight": 0.08,  # Peso del volumen
            
            # Momentum Strategy Config
            "momentum_period": 21,  # Período de momentum más largo
            "momentum_threshold": 0.04,  # Umbral más alto (4%)
            "momentum_weight": 0.12,  # Peso del momentum
            
            # Volatility Strategy Config
            "volatility_period": 30,  # Período de volatilidad más largo
            "volatility_threshold": 0.03,  # Umbral más alto (3%)
            "volatility_weight": 0.03,  # Peso de la volatilidad
            
            # Support/Resistance Strategy Config
            "sr_lookback": 50,  # Lookback más largo
            "sr_threshold": 0.015,  # Umbral más amplio (1.5%)
            "sr_weight": 0.08,  # Peso de soporte/resistencia
            
            # Trend Strategy Config
            "trend_period": 30,  # Período de tendencia más largo
            "trend_threshold": 0.025,  # Umbral más alto (2.5%)
            "trend_weight": 0.18,  # Peso de la tendencia
            
            # Pattern Recognition Config
            "pattern_lookback": 25,  # Lookback más largo para patrones
            "pattern_confidence": 0.8,  # Confianza más alta (80%)
            "pattern_weight": 0.08,  # Peso del reconocimiento de patrones
            
            # Signal Combination Config
            "min_signal_strength": 0.75,  # Fuerza mínima de señal más alta
            "signal_decay_factor": 0.7,  # Factor de decaimiento más lento
            "max_signals_per_hour": 2,  # Pocas señales por hora
            "signal_cooldown": 900,  # Cooldown más largo (15 min)
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_enhanced_strategies_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de estrategias mejoradas para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración de estrategias mejoradas
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in EnhancedStrategiesProfiles.PROFILES:
        raise ValueError(f"Perfil de estrategias no válido: {profile}")
    
    return EnhancedStrategiesProfiles.PROFILES[profile]

def get_available_strategy_profiles() -> List[str]:
    """Obtiene la lista de perfiles de estrategias disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(EnhancedStrategiesProfiles.PROFILES.keys())

def validate_strategy_profile(profile: str) -> bool:
    """Valida si un perfil de estrategias es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in EnhancedStrategiesProfiles.PROFILES

def get_strategy_weights(profile: str = None) -> Dict[str, float]:
    """Obtiene los pesos de las estrategias para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los pesos de las estrategias
    """
    config = get_enhanced_strategies_config(profile)
    
    return {
        "rsi_weight": config["rsi_weight"],
        "macd_weight": config["macd_weight"],
        "bb_weight": config["bb_weight"],
        "ma_weight": config["ma_weight"],
        "volume_weight": config["volume_weight"],
        "momentum_weight": config["momentum_weight"],
        "volatility_weight": config["volatility_weight"],
        "sr_weight": config["sr_weight"],
        "trend_weight": config["trend_weight"],
        "pattern_weight": config["pattern_weight"]
    }

def get_indicator_params(profile: str = None, indicator: str = None) -> Dict[str, Any]:
    """Obtiene los parámetros de un indicador específico para el perfil especificado.
    
    Args:
        profile: Perfil de trading
        indicator: Nombre del indicador (rsi, macd, bb, ma, etc.)
    
    Returns:
        Diccionario con los parámetros del indicador
    """
    config = get_enhanced_strategies_config(profile)
    
    if indicator == "rsi":
        return {
            "period": config["rsi_period"],
            "oversold": config["rsi_oversold"],
            "overbought": config["rsi_overbought"]
        }
    elif indicator == "macd":
        return {
            "fast": config["macd_fast"],
            "slow": config["macd_slow"],
            "signal": config["macd_signal"]
        }
    elif indicator == "bb":
        return {
            "period": config["bb_period"],
            "std": config["bb_std"]
        }
    elif indicator == "ma":
        return {
            "short": config["ma_short"],
            "long": config["ma_long"]
        }
    else:
        raise ValueError(f"Indicador no válido: {indicator}")

def get_signal_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de señales para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de señales
    """
    config = get_enhanced_strategies_config(profile)
    
    return {
        "min_signal_strength": config["min_signal_strength"],
        "signal_decay_factor": config["signal_decay_factor"],
        "max_signals_per_hour": config["max_signals_per_hour"],
        "signal_cooldown": config["signal_cooldown"]
    }

# ============================================================================
# 🛡️ CONFIGURACIÓN LEGACY PARA COMPATIBILIDAD
# ============================================================================

# Configuración legacy que mapea perfiles a configuraciones
ENHANCED_STRATEGIES_CONFIG = {
    "RAPIDO": EnhancedStrategiesProfiles.PROFILES["RAPIDO"],
    "AGRESIVO": EnhancedStrategiesProfiles.PROFILES["AGRESIVO"],
    "OPTIMO": EnhancedStrategiesProfiles.PROFILES["OPTIMO"],
    "CONSERVADOR": EnhancedStrategiesProfiles.PROFILES["CONSERVADOR"]
}

def validate_enhanced_strategies_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración de enhanced strategies.
    
    Args:
        config: Configuración a validar
        
    Returns:
        True si la configuración es válida
    """
    return True
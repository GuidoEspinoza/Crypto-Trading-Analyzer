"""Configuración centralizada para el sistema de trading.

Este archivo contiene todas las configuraciones principales del bot de trading,
con tres niveles de configuración disponibles:

🚀 RÁPIDA (Ultra-corta): Timeframes de 1m-15m, máxima frecuencia de trades, mayor riesgo
⚡ AGRESIVA: Timeframes de 15m-1h, balance entre velocidad y control de riesgo  
🛡️ ÓPTIMA (Conservadora): Timeframes de 1h-1d, enfoque en calidad y preservación de capital

🎯 CAMBIO RÁPIDO DE PERFILES:
Para cambiar entre configuraciones, simplemente modifica la variable TRADING_PROFILE:
- "RAPIDO" para estrategia ultra-rápida
- "AGRESIVO" para estrategia balanceada
- "OPTIMO" para estrategia conservadora
"""

from typing import List, Dict, Any

# ============================================================================
# 🎯 SELECTOR DE PERFIL DE TRADING - CAMBIAR AQUÍ
# ============================================================================

# 🔥 CAMBIAR ESTE VALOR PARA CAMBIAR TODO EL COMPORTAMIENTO DEL BOT
TRADING_PROFILE = "RAPIDO"  # Opciones: "RAPIDO", "AGRESIVO", "OPTIMO", "CONSERVADOR"

# Balance inicial global para todas las posiciones en USDT
GLOBAL_INITIAL_BALANCE = 1000.0

# ============================================================================
# 📊 DEFINICIÓN DE PERFILES DE TRADING
# ============================================================================

class TradingProfiles:
    """Definición de todos los perfiles de trading disponibles."""
    
    PROFILES = {
        "RAPIDO": {
            "name": "🚀 Ultra-Rápido",
            "description": "Timeframes 1m-15m, máxima frecuencia optimizada",
            "timeframes": ["1m", "5m", "15m"],
            "analysis_interval": 5,
            "min_confidence": 65.0,  # Aumentado para mejor calidad de señales
            "max_daily_trades": 20,  # Reducido para mejor selección
            "max_positions": 8,  # Reducido para mejor control
            # Circuit Breaker Config - Optimizado
            "max_consecutive_losses": 7,  # Aumentado para tolerancia
            "circuit_breaker_cooldown_hours": 1.5,  # Reducido para eficiencia
            "max_drawdown_threshold": 12.0,  # Reducido para protección
            "gradual_reactivation": True,  # Nueva funcionalidad
            # Paper Trader Config - Optimizado
            "max_position_size": 8.0,  # Reducido para control
            "max_total_exposure": 75.0,  # Reducido para seguridad
            "min_trade_value": 15.0,  # Aumentado para calidad
            "paper_min_confidence": 60.0,  # Aumentado
            "max_slippage": 0.10,  # Reducido para mejor ejecución
            "min_liquidity": 4.0,  # Aumentado para liquidez
            # Risk Manager Config - Optimizado
            "max_risk_per_trade": 1.5,  # Optimizado para mejor control
            "max_daily_risk": 6.0,  # Reducido para mayor protección
            "max_drawdown_threshold": 10.0,  # Reducido para mejor control
            "correlation_threshold": 0.75,  # Optimizado
            "min_position_size": 12.0,  # Reducido para flexibilidad
            "risk_max_position_size": 8.0,  # Consistente
            "kelly_fraction": 0.28,  # Optimizado
            "volatility_adjustment": 1.25,  # Optimizado
            "atr_multiplier_min": 1.8,  # Optimizado más ajustado
            "atr_multiplier_max": 2.8,  # Optimizado
            "atr_default": 1.8,
            "atr_volatile": 2.8,  # Optimizado
            "atr_sideways": 1.4,  # Optimizado
            "trailing_stop_activation": 1.5,  # Optimizado más agresivo
            "breakeven_threshold": 0.6,  # Optimizado
            "intelligent_trailing": True,  # Nueva funcionalidad
            "dynamic_position_sizing": True,  # Nueva funcionalidad
            # Take Profit y Stop Loss Config - Rangos optimizados
            "tp_min_percentage": 2.5,  # TP mínimo optimizado
            "tp_max_percentage": 5.5,  # TP máximo optimizado
            "sl_min_percentage": 0.8,  # SL mínimo más ajustado
            "sl_max_percentage": 2.5,  # SL máximo optimizado
            "tp_increment_percentage": 1.0,  # Incremento base de TP
            "max_tp_adjustments": 5,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.7,  # Umbral confianza para ajustar TP
            # Umbrales y Límites Adicionales
            "max_daily_loss_percent": 5.0,  # Pérdida máxima diaria
            "max_drawdown_threshold": 10.0,  # Umbral máximo de drawdown
            "min_confidence_threshold": 0.6,  # Confianza mínima para trades
            "position_size_multiplier": 1.0,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 1.2,  # Factor de ajuste por volatilidad
            # Strategy Config - Optimizado
            "default_min_confidence": 52.0,  # Reducido para más oportunidades
            "default_atr_period": 10,
            "rsi_min_confidence": 68.0,  # Aumentado para mejor calidad
            "rsi_oversold": 35,  # Optimizado para señales de calidad
            "rsi_overbought": 65,  # Optimizado para mejor balance
            "rsi_period": 10,
            "min_volume_ratio": 1.6,  # Aumentado para mejor calidad
            "min_confluence": 4,  # Aumentado para mejores señales
            "trend_strength_threshold": 32,  # Optimizado para mejor filtrado
            "min_atr_ratio": 0.9,  # Optimizado
            "max_spread_threshold": 0.002,  # Optimizado más estricto
            "volume_weight": 0.22,  # Nuevo peso para volumen
            "confluence_threshold": 0.65,  # Nuevo umbral
            # Multi-Timeframe Config - Optimizado
            "mtf_enhanced_confidence": 62.0,  # Optimizado
            "mtf_min_confidence": 65.0,  # Aumentado para calidad
            "mtf_min_consensus": 0.65,  # Optimizado
            "mtf_require_trend_alignment": False,
            "mtf_min_timeframe_consensus": 2,
            "mtf_trend_alignment_required": False,
            "volume_timeframe": "5m",  # Nuevo timeframe para volumen
            # Ensemble Config - Optimizado
            "ensemble_min_consensus_threshold": 0.58,  # Optimizado
            "ensemble_confidence_boost_factor": 1.3,  # Optimizado
            # Live Trading Config - Optimizado
            "trading_fees": 0.001,
            "order_timeout": 25,  # Optimizado más rápido
            "max_order_retries": 3,  # Aumentado para robustez
            "order_check_interval": 1.5,  # Optimizado más frecuente
            "live_first_analysis_delay": 10  # Optimizado más rápido
        },
        "AGRESIVO": {
            "name": "⚡ Agresivo",
            "description": "Timeframes 15m-1h, balance velocidad/control optimizado",
            "timeframes": ["15m", "30m", "1h"],
            "analysis_interval": 15,
            "min_confidence": 72.0,  # Optimizado para mejor calidad
            "max_daily_trades": 15,  # Aumentado para más oportunidades
            "max_positions": 7,  # Aumentado para diversificación
            # Circuit Breaker Config - Optimizado
            "max_consecutive_losses": 4,  # Mantenido para tolerancia
            "circuit_breaker_cooldown_hours": 3,  # Optimizado para recuperación
            "max_drawdown_threshold": 10.0,  # Reducido para mejor control
            "gradual_reactivation": True,  # Nueva funcionalidad
            # Paper Trader Config - Optimizado
            "max_position_size": 6.0,  # Reducido para mejor control
            "max_total_exposure": 65.0,  # Reducido para menor riesgo
            "min_trade_value": 15.0,
            "paper_min_confidence": 68.0,  # Aumentado para calidad
            "max_slippage": 0.06,  # Reducido para mejor ejecución
            "min_liquidity": 6.0,  # Aumentado para mejor liquidez
            # Risk Manager Config - Optimizado
            "max_risk_per_trade": 1.0,  # Optimizado para control
            "max_daily_risk": 4.5,  # Reducido para mayor protección
            "max_drawdown_threshold": 8.0,  # Reducido para mejor control
            "correlation_threshold": 0.65,  # Optimizado
            "min_position_size": 8.0,  # Reducido
            "risk_max_position_size": 6.0,  # Reducido para consistencia
            "kelly_fraction": 0.20,  # Optimizado conservador
            "volatility_adjustment": 1.10,  # Reducido para estabilidad
            "atr_multiplier_min": 2.2,  # Optimizado
            "atr_multiplier_max": 3.8,  # Optimizado
            "atr_default": 2.5,
            "atr_volatile": 3.8,  # Optimizado
            "atr_sideways": 2.2,  # Optimizado
            "trailing_stop_activation": 1.5,  # Optimizado
            "breakeven_threshold": 0.8,  # Optimizado
            "intelligent_trailing": True,  # Nueva funcionalidad
            "dynamic_position_sizing": True,  # Nueva funcionalidad
            # Take Profit y Stop Loss Config - Rangos optimizados
            "tp_min_percentage": 3.0,  # TP mínimo 3%
            "tp_max_percentage": 6.0,  # TP máximo 6%
            "sl_min_percentage": 1.0,  # SL mínimo 1%
            "sl_max_percentage": 3.0,  # SL máximo 3%
            "tp_increment_percentage": 1.0,  # Incremento base de TP
            "max_tp_adjustments": 5,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.7,  # Umbral confianza para ajustar TP
            # Umbrales y Límites Adicionales
            "max_daily_loss_percent": 4.0,  # Pérdida máxima diaria (más agresivo)
            "max_drawdown_threshold": 8.0,  # Umbral máximo de drawdown
            "min_confidence_threshold": 0.65,  # Confianza mínima para trades
            "position_size_multiplier": 1.2,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 1.3,  # Factor de ajuste por volatilidad
            # Strategy Config - Optimizado
            "default_min_confidence": 65.0,  # Aumentado
            "default_atr_period": 14,
            "rsi_min_confidence": 72.0,  # Aumentado para calidad
            "rsi_oversold": 28,  # Optimizado
            "rsi_overbought": 72,  # Optimizado
            "rsi_period": 14,
            "min_volume_ratio": 1.8,  # Aumentado para calidad
            "min_confluence": 3,
            "trend_strength_threshold": 32,  # Optimizado
            "min_atr_ratio": 1.1,  # Optimizado
            "max_spread_threshold": 0.0012,  # Optimizado
            "volume_weight": 0.15,  # Nuevo peso para volumen
            "confluence_threshold": 0.68,  # Nuevo umbral de confluencia
            # Multi-Timeframe Config - Optimizado
            "mtf_enhanced_confidence": 68.0,  # Optimizado
            "mtf_min_confidence": 72.0,  # Aumentado
            "mtf_min_consensus": 0.68,  # Optimizado
            "mtf_require_trend_alignment": True,
            "mtf_min_timeframe_consensus": 2,
            "mtf_trend_alignment_required": True,
            "volume_timeframe": "1h",  # Nuevo timeframe para volumen
            # Ensemble Config - Optimizado
            "ensemble_min_consensus_threshold": 0.65,  # Optimizado
            "ensemble_confidence_boost_factor": 1.18,  # Optimizado
            # Live Trading Config - Optimizado
            "trading_fees": 0.001,
            "order_timeout": 40,  # Optimizado
            "max_order_retries": 3,
            "order_check_interval": 2,  # Optimizado
            "live_first_analysis_delay": 25  # Optimizado
        },
        "OPTIMO": {
            "name": "🎯 Óptimo",
            "description": "Timeframes 1h-4h, máxima precisión optimizada",
            "timeframes": ["1h", "2h", "4h"],
            "analysis_interval": 30,
            "min_confidence": 80.0,  # Aumentado para máxima calidad
            "max_daily_trades": 10,  # Aumentado para más oportunidades
            "max_positions": 5,  # Aumentado para diversificación
            # Circuit Breaker Config - Optimizado
            "max_consecutive_losses": 3,  # Aumentado para tolerancia
            "circuit_breaker_cooldown_hours": 4,  # Reducido para eficiencia
            "max_drawdown_threshold": 8.0,  # Mantenido estricto
            "gradual_reactivation": True,  # Nueva funcionalidad
            # Paper Trader Config - Optimizado
            "max_position_size": 10.0,  # Reducido para control
            "max_total_exposure": 55.0,  # Reducido para seguridad
            "min_trade_value": 30.0,  # Aumentado para calidad
            "paper_min_confidence": 75.0,  # Aumentado
            "max_slippage": 0.04,  # Reducido para mejor ejecución
            "min_liquidity": 10.0,  # Aumentado para liquidez
            # Risk Manager Config - Optimizado
            "max_risk_per_trade": 0.7,  # Optimizado para máximo control
            "max_daily_risk": 3.0,  # Reducido para máxima protección
            "max_drawdown_threshold": 6.0,  # Reducido para control estricto
            "correlation_threshold": 0.55,  # Optimizado
            "min_position_size": 20.0,  # Aumentado para calidad
            "risk_max_position_size": 10.0,  # Consistente
            "kelly_fraction": 0.15,  # Muy conservador para precisión
            "volatility_adjustment": 0.90,  # Reducido para estabilidad
            "atr_multiplier_min": 2.2,  # Optimizado
            "atr_multiplier_max": 3.2,  # Optimizado
            "atr_default": 2.2,
            "atr_volatile": 3.2,  # Optimizado
            "atr_sideways": 2.0,  # Optimizado
            "trailing_stop_activation": 1.5,  # Optimizado
            "breakeven_threshold": 0.6,  # Optimizado
            "intelligent_trailing": True,  # Nueva funcionalidad
            "dynamic_position_sizing": True,  # Nueva funcionalidad
            # Take Profit y Stop Loss Config - Rangos optimizados
            "tp_min_percentage": 3.0,  # TP mínimo 3%
            "tp_max_percentage": 6.0,  # TP máximo 6%
            "sl_min_percentage": 1.0,  # SL mínimo 1%
            "sl_max_percentage": 3.0,  # SL máximo 3%
            "tp_increment_percentage": 1.0,  # Incremento base de TP
            "max_tp_adjustments": 5,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.7,  # Umbral confianza para ajustar TP
            # Umbrales y Límites Adicionales
            "max_daily_loss_percent": 3.0,  # Pérdida máxima diaria (óptimo)
            "max_drawdown_threshold": 6.0,  # Umbral máximo de drawdown
            "min_confidence_threshold": 0.7,  # Confianza mínima para trades
            "position_size_multiplier": 1.0,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 1.1,  # Factor de ajuste por volatilidad
            # Strategy Config - Optimizado
            "default_min_confidence": 72.0,  # Aumentado
            "default_atr_period": 14,
            "rsi_min_confidence": 82.0,  # Aumentado para máxima calidad
            "rsi_oversold": 25,  # Optimizado para mejor balance
            "rsi_overbought": 75,  # Optimizado para mejor balance
            "rsi_period": 14,
            "min_volume_ratio": 2.2,  # Aumentado para calidad
            "min_confluence": 4,
            "trend_strength_threshold": 42,  # Optimizado
            "min_atr_ratio": 1.3,  # Optimizado
            "max_spread_threshold": 0.0008,  # Optimizado más estricto
            "volume_weight": 0.18,  # Nuevo peso para volumen
            "confluence_threshold": 0.72,  # Nuevo umbral alto
            # Multi-Timeframe Config - Optimizado
            "mtf_enhanced_confidence": 78.0,  # Optimizado
            "mtf_min_confidence": 82.0,  # Aumentado para calidad
            "mtf_min_consensus": 0.78,  # Optimizado
            "mtf_require_trend_alignment": True,
            "mtf_min_timeframe_consensus": 3,
            "mtf_trend_alignment_required": True,
            "volume_timeframe": "2h",  # Nuevo timeframe para volumen
            # Ensemble Config - Optimizado
            "ensemble_min_consensus_threshold": 0.72,  # Optimizado
            "ensemble_confidence_boost_factor": 1.25,  # Optimizado
            # Live Trading Config - Optimizado
            "trading_fees": 0.001,
            "order_timeout": 50,  # Optimizado
            "max_order_retries": 3,
            "order_check_interval": 4,  # Optimizado
            "live_first_analysis_delay": 45  # Optimizado
        },
        "CONSERVADOR": {
            "name": "🛡️ Conservador",
            "description": "Timeframes 4h-1d, máxima preservación de capital",
            "timeframes": ["4h", "8h", "1d"],  # Timeframes más largos
            "analysis_interval": 45,  # Análisis menos frecuente
            "min_confidence": 85.0,  # Aumentado para máxima seguridad
            "max_daily_trades": 6,  # Aumentado ligeramente para oportunidades
            "max_positions": 3,  # Aumentado para diversificación mínima
            # Circuit Breaker Config - Ultra conservador
            "max_consecutive_losses": 2,  # Muy estricto
            "circuit_breaker_cooldown_hours": 8,  # Cooldown largo
            "max_drawdown_threshold": 5.0,  # Muy estricto
            "gradual_reactivation": True,  # Nueva funcionalidad
            # Paper Trader Config - Conservador
            "max_position_size": 4.0,  # Muy reducido
            "max_total_exposure": 35.0,  # Muy limitado
            "min_trade_value": 50.0,  # Alto para calidad
            "paper_min_confidence": 80.0,  # Muy alto
            "max_slippage": 0.03,  # Muy estricto
            "min_liquidity": 15.0,  # Muy alto
            # Risk Manager Config - Ultra conservador
            "max_risk_per_trade": 0.4,  # Extremadamente bajo
            "max_daily_risk": 1.5,  # Muy limitado para máxima protección
            "max_drawdown_threshold": 4.0,  # Muy estricto
            "correlation_threshold": 0.4,  # Muy estricto
            "min_position_size": 30.0,  # Alto para calidad
            "risk_max_position_size": 4.0,  # Consistente
            "kelly_fraction": 0.08,  # Extremadamente conservador
            "volatility_adjustment": 0.75,  # Muy reducido para estabilidad
            "atr_multiplier_min": 3.5,  # Stops más amplios
            "atr_multiplier_max": 5.5,  # Stops muy amplios
            "atr_default": 3.5,
            "atr_volatile": 5.5,  # Muy amplio
            "atr_sideways": 3.0,  # Amplio
            "trailing_stop_activation": 2.0,  # Más conservador
            "breakeven_threshold": 1.0,  # Más conservador
            "intelligent_trailing": True,  # Nueva funcionalidad
            "dynamic_position_sizing": True,  # Nueva funcionalidad
            # Take Profit y Stop Loss Config - Rangos optimizados
            "tp_min_percentage": 3.0,  # TP mínimo 3%
            "tp_max_percentage": 6.0,  # TP máximo 6%
            "sl_min_percentage": 1.0,  # SL mínimo 1%
            "sl_max_percentage": 3.0,  # SL máximo 3%
            "tp_increment_percentage": 0.8,  # Incremento conservador de TP
            "max_tp_adjustments": 3,  # Menos ajustes para conservador
            "tp_confidence_threshold": 0.8,  # Umbral más alto para conservador
            # Umbrales y Límites Adicionales
            "max_daily_loss_percent": 2.0,  # Pérdida máxima diaria (conservador)
            "max_drawdown_threshold": 4.0,  # Umbral máximo de drawdown
            "min_confidence_threshold": 0.75,  # Confianza mínima para trades
            "position_size_multiplier": 0.8,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 1.0,  # Factor de ajuste por volatilidad
            # Strategy Config - Ultra conservador
            "default_min_confidence": 78.0,  # Muy alto
            "default_atr_period": 21,  # Período más largo
            "rsi_min_confidence": 88.0,  # Extremadamente alto
            "rsi_oversold": 22,  # Optimizado para mejor calidad
            "rsi_overbought": 78,  # Optimizado para mejor calidad
            "rsi_period": 21,  # Período más largo
            "min_volume_ratio": 2.5,  # Alto para calidad
            "min_confluence": 5,  # Muy alto
            "trend_strength_threshold": 50,  # Alto
            "min_atr_ratio": 1.5,  # Alto
            "max_spread_threshold": 0.0005,  # Muy estricto
            "volume_weight": 0.25,  # Peso alto para volumen
            "confluence_threshold": 0.8,  # Muy alto
            # Multi-Timeframe Config - Ultra conservador
            "mtf_enhanced_confidence": 82.0,  # Muy alto
            "mtf_min_confidence": 88.0,  # Extremadamente alto
            "mtf_min_consensus": 0.85,  # Muy alto
            "mtf_require_trend_alignment": True,
            "mtf_min_timeframe_consensus": 3,
            "mtf_trend_alignment_required": True,
            "volume_timeframe": "4h",  # Timeframe más largo
            # Ensemble Config - Ultra conservador
            "ensemble_min_consensus_threshold": 0.8,  # Muy alto
            "ensemble_confidence_boost_factor": 1.1,  # Conservador
            # Live Trading Config - Conservador
            "trading_fees": 0.001,
            "order_timeout": 90,  # Más tiempo
            "max_order_retries": 5,  # Más intentos
            "order_check_interval": 3,  # Más frecuente
            "live_first_analysis_delay": 90  # Más tiempo inicial
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
# CONFIGURACIÓN DEL TRADING BOT PRINCIPAL
# ============================================================================

class TradingBotConfig:
    """Configuración principal del bot de trading."""
    
    # Lista de símbolos para analizar - Optimizada para trading
    # Selección basada en alta liquidez, volatilidad y volumen de trading
    SYMBOLS: List[str] = [
        # Pares principales (máxima liquidez)
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT",
        # Altcoins de alta capitalización y volumen
        "ADAUSDT", "XRPUSDT", "LINKUSDT", "DOGEUSDT", "TRXUSDT",
        # Tokens con alta volatilidad y buen volumen
        "DOTUSDT", "MATICUSDT", "ATOMUSDT", "NEARUSDT", "SUIUSDT"
    ]

    # Símbolos para el bot en vivo - Misma lista optimizada
    SYMBOLS_LIVE_BOT = SYMBOLS
    
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
    DEFAULT_PORTFOLIO_VALUE: float = GLOBAL_INITIAL_BALANCE
    
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
        """Intervalo de actualización para live bot según perfil."""
        return TradingProfiles.get_current_profile()["analysis_interval"]
    
    @classmethod
    def get_first_analysis_delay(cls) -> int:
        """Delay para primer análisis según perfil."""
        # Usar el doble del intervalo de análisis como delay inicial
        return TradingProfiles.get_current_profile()["analysis_interval"] * 2
    
    @classmethod
    def get_max_consecutive_losses(cls) -> int:
        """Máximo de pérdidas consecutivas antes de activar circuit breaker según perfil activo."""
        return TradingProfiles.get_current_profile()["max_consecutive_losses"]
    
    @classmethod
    def get_circuit_breaker_cooldown_hours(cls) -> int:
        """Horas de cooldown después de activar circuit breaker según perfil activo."""
        return TradingProfiles.get_current_profile()["circuit_breaker_cooldown_hours"]


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USDT para simulación
    INITIAL_BALANCE: float = GLOBAL_INITIAL_BALANCE
    
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
    MAX_BALANCE_USAGE: float = 95.0


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
    def get_volatility_adjustment(cls) -> float:
        """Obtiene el factor de ajuste por volatilidad según perfil activo."""
        return TradingProfiles.get_current_profile()["volatility_adjustment"]
    
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
    def get_max_tp_adjustments(cls) -> int:
        """Obtiene el máximo número de ajustes de TP según perfil activo."""
        return TradingProfiles.get_current_profile()["max_tp_adjustments"]
    
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
    
    @classmethod
    def get_volatility_adjustment_factor(cls) -> float:
        """Obtiene el factor de ajuste por volatilidad según perfil activo."""
        return TradingProfiles.get_current_profile()["volatility_adjustment_factor"]
    
    # Propiedades dinámicas para compatibilidad con código existente
    MAX_RISK_PER_TRADE: float = property(lambda self: TradingProfiles.get_current_profile()["max_risk_per_trade"])
    MAX_DAILY_RISK: float = property(lambda self: TradingProfiles.get_current_profile()["max_daily_risk"])
    MAX_DRAWDOWN_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["max_drawdown_threshold"])
    CORRELATION_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["correlation_threshold"])
    MIN_POSITION_SIZE: float = property(lambda self: TradingProfiles.get_current_profile()["min_position_size"])
    MAX_POSITION_SIZE: float = property(lambda self: TradingProfiles.get_current_profile()["risk_max_position_size"])
    KELLY_FRACTION: float = property(lambda self: TradingProfiles.get_current_profile()["kelly_fraction"])
    VOLATILITY_ADJUSTMENT: float = property(lambda self: TradingProfiles.get_current_profile()["volatility_adjustment"])
    ATR_MULTIPLIER_MIN: float = property(lambda self: TradingProfiles.get_current_profile()["atr_multiplier_min"])
    ATR_MULTIPLIER_MAX: float = property(lambda self: TradingProfiles.get_current_profile()["atr_multiplier_max"])
    ATR_DEFAULT: float = property(lambda self: TradingProfiles.get_current_profile()["atr_default"])
    ATR_VOLATILE: float = property(lambda self: TradingProfiles.get_current_profile()["atr_volatile"])
    ATR_SIDEWAYS: float = property(lambda self: TradingProfiles.get_current_profile()["atr_sideways"])
    TRAILING_STOP_ACTIVATION: float = property(lambda self: TradingProfiles.get_current_profile()["trailing_stop_activation"])
    BREAKEVEN_THRESHOLD: float = property(lambda self: TradingProfiles.get_current_profile()["breakeven_threshold"])
    
    # Valor inicial del portfolio para cálculos de riesgo en USDT - Se alimenta del PaperTrader para consistencia
    INITIAL_PORTFOLIO_VALUE: float = PaperTraderConfig.INITIAL_BALANCE  # Mantiene consistencia automática


# ============================================================================
# CONFIGURACIÓN DE ESTRATEGIAS DE TRADING
# ============================================================================

class StrategyConfig:
    """Configuración de las estrategias de trading."""
    
    # ---- Configuración Base de Estrategias ----
    class Base:
        """Parámetros base para todas las estrategias."""
        
        # Confianza mínima por defecto para estrategias base (rápido: 55.0 - agresivo: 60.0 - óptimo: 65.0)
        DEFAULT_MIN_CONFIDENCE: float = 55.0  # Estrategia rápida
        
        # Valores de confianza por defecto para diferentes señales
        HOLD_CONFIDENCE: float = 45.0
        BASE_CONFIDENCE: float = 50.0
        ENHANCED_CONFIDENCE: float = 60.0
        
        # Período ATR por defecto para cálculos de stop-loss (rápido: 10 - agresivo: 14 - óptimo: 20)
        DEFAULT_ATR_PERIOD: int = 10  # Estrategia rápida
    
    # ---- Estrategia RSI Profesional ----
    class ProfessionalRSI:
        """Parámetros para la estrategia RSI profesional."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Confianza mínima requerida en % (rápido: 65.0 - agresivo: 68.0 - óptimo: 72.0)
        MIN_CONFIDENCE: float = 65.0  # Estrategia rápida
        
        # Nivel de sobreventa del RSI - señal de compra (rápido: 35 - agresivo: 30 - óptimo: 25)
        RSI_OVERSOLD: int = 35  # Estrategia rápida
        
        # Nivel de sobrecompra del RSI - señal de venta (rápido: 65 - agresivo: 70 - óptimo: 75)
        RSI_OVERBOUGHT: int = 65  # Estrategia rápida
        
        # Período del RSI - ventana de cálculo (rápido: 10 - agresivo: 14 - óptimo: 21)
        RSI_PERIOD: int = 10  # Estrategia rápida
        
        # Ratio mínimo de volumen vs promedio (rápido: 1.2 - agresivo: 1.5 - óptimo: 1.8)
        MIN_VOLUME_RATIO: float = 1.2  # Estrategia rápida
        
        # Confluencia mínima de indicadores requerida (rápido: 2 - agresivo: 3 - óptimo: 4)
        MIN_CONFLUENCE: int = 2  # Estrategia rápida
        
        # Umbral de fuerza de tendencia ADX (rápido: 25 - agresivo: 30 - óptimo: 35)
        TREND_STRENGTH_THRESHOLD: float = 25  # Estrategia rápida
        
        # Ratio ATR mínimo para volatilidad (rápido: 0.8 - agresivo: 1.0 - óptimo: 1.2)
        MIN_ATR_RATIO: float = 0.8  # Estrategia rápida
        
        # Spread máximo permitido en % (rápido: 0.0025 - agresivo: 0.0015 - óptimo: 0.0010)
        MAX_SPREAD_THRESHOLD: float = 0.0025  # Estrategia rápida
    
    # ---- Estrategia Multi-Timeframe ----
    class MultiTimeframe:
        """Parámetros para la estrategia multi-timeframe."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Confianza mejorada para señales (rápido: 60.0 - agresivo: 65.0 - óptimo: 70.0)
        ENHANCED_CONFIDENCE: float = 60.0  # Estrategia rápida
        
        # Confianza mínima requerida en % (rápido: 62.0 - agresivo: 65.0 - óptimo: 70.0)
        MIN_CONFIDENCE: float = 62.0  # Estrategia rápida
        
        # Timeframes utilizados para análisis (rápido: ["1m", "5m", "15m"] - agresivo: ["15m", "30m", "1h"] - óptimo: ["1h", "4h", "1d"])
        TIMEFRAMES: List[str] = ["1m", "5m", "15m"]  # Estrategia rápida
        
        # Configuración RSI por timeframe - niveles de sobreventa/sobrecompra (rápido)
        RSI_CONFIG: Dict[str, Dict[str, int]] = {
            "1m": {"oversold": 35, "overbought": 65},    # Timeframe corto - rápido
            "5m": {"oversold": 35, "overbought": 65},    # Timeframe medio - rápido
            "15m": {"oversold": 35, "overbought": 65}    # Timeframe largo - rápido
        }
        

        
        # Pesos por timeframe - balance entre corto y medio plazo (rápido: suma = 1.0)
        TIMEFRAME_WEIGHTS: Dict[str, float] = {
            "1m": 0.5,    # Peso principal para oportunidades ultra-cortas
            "5m": 0.3,    # Peso medio para confirmación
            "15m": 0.2    # Peso menor para tendencia general
        }
        

        
        # Consenso mínimo de timeframes requerido (rápido: 1 - agresivo: 2 - óptimo: 3)
        MIN_CONSENSUS: int = 1  # Estrategia rápida
        
        # Requiere alineación de tendencias entre timeframes (rápido: False - agresivo: True - óptimo: True)
        REQUIRE_TREND_ALIGNMENT: bool = False  # Estrategia rápida
        
        # Consenso mínimo de timeframes para señal válida (rápido: 1 - agresivo: 2 - óptimo: 3)
        MIN_TIMEFRAME_CONSENSUS: int = 1  # Estrategia rápida
        
        # Requiere alineación de tendencias entre timeframes (rápido: False - agresivo: True - óptimo: True)
        TREND_ALIGNMENT_REQUIRED: bool = False  # Estrategia rápida
    
    # ---- Estrategia Ensemble ----
    class Ensemble:
        """Parámetros para la estrategia ensemble (combinación de estrategias)."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Pesos de cada estrategia en el ensemble (óptimo: RSI=0.4, MultiTF=0.6)
        STRATEGY_WEIGHTS: Dict[str, float] = {
            "Professional_RSI": 0.4,
            "Multi_Timeframe": 0.6
        }
        
        # Umbral mínimo de consenso entre estrategias (rápido: 0.55 - agresivo: 0.6 - óptimo: 0.7)
        MIN_CONSENSUS_THRESHOLD: float = 0.55  # Estrategia rápida
        
        # Factor de boost de confianza cuando hay consenso (rápido: 1.25 - agresivo: 1.2 - óptimo: 1.15)
        CONFIDENCE_BOOST_FACTOR: float = 1.25  # Estrategia rápida


# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

class DatabaseConfig:
    """Configuración de la base de datos."""
    
    # Nombre del archivo de base de datos SQLite (óptimo: "trading_data.db")
    DATABASE_NAME: str = "trading_data.db"
    
    # Días de retención de datos históricos (óptimo: 90)
    DATA_RETENTION_DAYS: int = 90
    
    # Intervalo de limpieza automática en horas (óptimo: 24)
    CLEANUP_INTERVAL_HOURS: int = 24


# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

class LoggingConfig:
    """Configuración del sistema de logging."""
    
    # Nivel de logging por defecto (óptimo: "INFO")
    LOG_LEVEL: str = "INFO"
    
    # Formato de logs con timestamp (óptimo: incluir timestamp y nivel)
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Archivo de logs (óptimo: "trading_bot.log")
    LOG_FILE: str = "trading_bot.log"
    
    # Tamaño máximo del archivo de log en MB (óptimo: 10)
    MAX_LOG_SIZE_MB: int = 10
    
    # Número de archivos de backup de logs (óptimo: 5)
    LOG_BACKUP_COUNT: int = 5


# ============================================================================
# CONFIGURACIÓN DE TRADING EN VIVO (LIVE TRADING)
# ============================================================================

class LiveTradingConfig:
    """Configuración específica para trading en vivo."""
    
    # Balance inicial real en USDT - Se alimenta automáticamente del PaperTrader para consistencia
    INITIAL_BALANCE: float = PaperTraderConfig.INITIAL_BALANCE  # Mantiene consistencia automática
    
    # Comisiones de Binance en % por trade (rápido: 0.1 - agresivo: 0.1 - óptimo: 0.075)
    TRADING_FEES: float = 0.1  # Estrategia rápida
    
    # Timeout para órdenes en segundos (rápido: 15 - agresivo: 30 - óptimo: 60)
    ORDER_TIMEOUT: int = 15  # Estrategia rápida
    
    # Reintentos máximos para órdenes fallidas (rápido: 2 - agresivo: 3 - óptimo: 5)
    MAX_ORDER_RETRIES: int = 2  # Estrategia rápida
    
    # Intervalo de verificación de órdenes en segundos (rápido: 2 - agresivo: 5 - óptimo: 10)
    ORDER_CHECK_INTERVAL: int = 2  # Estrategia rápida


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
        'db': DatabaseConfig,
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
    TEST_SYMBOLS: List[str] = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    
    # Configuración de trading bot para testing
    TEST_MIN_CONFIDENCE: float = 70.0
    TEST_MAX_DAILY_TRADES: int = 5
    
    # Configuración de análisis para testing
    TEST_ANALYSIS_INTERVAL: int = 5  # minutos
    
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
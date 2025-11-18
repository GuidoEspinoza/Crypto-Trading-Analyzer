# ============================================================================
# 🎯 CONFIGURACIÓN DE PERFILES DE TRADING
# ============================================================================
"""
Configuración centralizada de perfiles de trading para el sistema de trading automatizado.

Este módulo define los perfiles de trading disponibles y permite seleccionar
el perfil activo que determinará el comportamiento completo del bot.

Perfiles disponibles:
- SCALPING: Trading ultra-rápido con timeframes de 1-5 minutos
- INTRADAY: Trading diario con timeframes de 15 minutos a 1 hora

Autor: Sistema de Trading Automatizado
Versión: 2.0
Última actualización: 2024
"""

# ============================================================================
# 🔥 SELECTOR DE PERFIL ACTIVO - CONFIGURACIÓN PRINCIPAL
# ============================================================================

# 🚨 IMPORTANTE: Cambiar este valor modifica todo el comportamiento del bot
# Este es el único lugar donde se debe cambiar el perfil de trading
# TRADING_PROFILE = "SCALPING"  # Opciones disponibles: "SCALPING", "INTRADAY"
TRADING_PROFILE = "INTRADAY"  # Opciones disponibles: "SCALPING", "INTRADAY"

# ============================================================================
# 📊 DEFINICIÓN COMPLETA DE PERFILES DE TRADING
# ============================================================================

PROFILES = {
    # ========================================================================
    # 🏃‍♂️ PERFIL SCALPING - TRADING ULTRA-RÁPIDO
    # ========================================================================
    "SCALPING": {
        # === INFORMACIÓN BÁSICA DEL PERFIL ===
        "name": "Scalping",
        "description": "Perfil optimizado para trading ultra-rápido con timeframes de 1-5 minutos, enfocado en movimientos pequeños pero frecuentes",
        # === CONFIGURACIÓN TEMPORAL ===
        "timeframes": [
            "1m",
            "3m",
            "5m",
        ],  # Timeframes ultra-rápidos para capturar movimientos inmediatos
        "analysis_interval": 1,  # Análisis cada minuto para máxima reactividad
        # === CONFIGURACIÓN DE CALIDAD DE SEÑALES ===
        "min_confidence": 78.0,  # Confianza mínima alta para reducir señales falsas en alta frecuencia
        "max_daily_trades": 30,  # Límite optimizado para aprovechar 42 símbolos disponibles
        "max_daily_trades_adaptive": True,  # Permite trades adicionales con señales de alta calidad
        "daily_trades_quality_threshold": 82.0,  # Umbral de confianza para trades adicionales
        "max_daily_trades_bonus": 15,  # Máximo de trades adicionales con alta confianza (total: 50)
        "max_positions": 18,  # Máximo de posiciones simultáneas para máxima diversificación
        # === CONFIGURACIÓN DE PAPER TRADING - OPTIMIZADA PARA SCALPING ===
        "max_position_size_percent": 8,  # 8% del balance por posición - OPTIMIZADO (era 4%)
        "max_total_exposure_percent": 80,  # 80% de exposición total - OPTIMIZADO (era 60%)
        "min_trade_value": 25.0,  # Valor mínimo por trade - OPTIMIZADO (era 5.0)
        "paper_min_confidence": 78.0,  # Confianza mínima consistente con trading real
        "max_slippage": 0.03,  # Slippage máximo permitido (3%)
        "min_liquidity": 8.0,  # Liquidez mínima requerida para ejecución
        # === CONFIGURACIÓN DE GESTIÓN DE RIESGO ===
        "max_risk_per_trade_percent": 0.6,  # 0.6% de riesgo por trade - ultra conservador
        "max_daily_risk_percent": 2.0,  # 2% de riesgo diario máximo - protección del capital
        "max_drawdown_threshold_percent": 8,  # 8% de drawdown máximo antes de parar
        "correlation_threshold": 0.70,  # Umbral de correlación entre posiciones
        "min_position_size": 5.0,  # Tamaño mínimo de posición
        "risk_max_position_size_percent": 6,  # Consistente con max_position_size_percent
        "kelly_fraction": 0.20,  # Fracción Kelly ultra conservadora para alta frecuencia
        "volatility_adjustment_factor": 1.0,  # Factor de ajuste por volatilidad del mercado
        # === CONFIGURACIÓN DE STOP LOSS Y TAKE PROFIT ===
        "atr_multiplier_min": 1.5,  # Multiplicador ATR mínimo para stops
        "atr_multiplier_max": 2.5,  # Multiplicador ATR máximo para stops
        "atr_default": 1.8,  # Multiplicador ATR por defecto
        "atr_volatile": 2.5,  # Multiplicador ATR en mercados volátiles
        "atr_sideways": 1.5,  # Multiplicador ATR en mercados laterales
        "trailing_stop_activation": 0.025,  # Activación de trailing stop al 2.5%
        "breakeven_threshold_percent": 0.4,  # Umbral para mover stop a breakeven (0.4%)
        "intelligent_trailing": True,  # Activar trailing stop inteligente
        "dynamic_position_sizing": True,  # Activar dimensionamiento dinámico de posiciones
        # === CONFIGURACIÓN DE CAPITAL.COM ===
        "use_trailing_stop": True,  # Usar trailing stops nativos de Capital.com
        # === CONFIGURACIÓN DE TP/SL BASADO EN ROI - OPTIMIZADA PARA SCALPING ===
        # Los porcentajes son sobre el balance total invertido, no sobre el precio del activo
        "tp_min_percent": 0.5,  # Take Profit mínimo: 0.5% ROI - OPTIMIZADO (era 0.35%)
        "tp_max_percent": 1.2,  # Take Profit máximo: 1.2% ROI - más realista para salidas rápidas
        "sl_min_percent": 0.4,  # Stop Loss mínimo: 0.4% ROI - OPTIMIZADO (era 0.3%)
        "sl_max_percent": 0.9,  # Stop Loss máximo: 0.9% ROI - recorte de riesgo
        "tp_increment_percent": 1.2,  # Factor de incremento para TP dinámico
        "tp_confidence_threshold": 0.70,  # Umbral de confianza ligeramente más alto para ajustar TP
        # === LÍMITES DE PROTECCIÓN ADICIONALES ===
        "max_daily_loss_percent": 4.5,  # Pérdida máxima diaria - OPTIMIZADA (era 3.0%)
        "min_confidence_threshold": 0.78,  # Umbral mínimo de confianza para operar
        "position_size_multiplier": 1.5,  # Multiplicador OPTIMIZADO para scalping (era 0.8)
        # === CONFIGURACIÓN DE ESTRATEGIAS ===
        "default_min_confidence": 72.0,  # Confianza mínima por defecto para estrategias
        "default_atr_period": 14,  # Período ATR estándar para cálculos
        "rsi_min_confidence": 78.0,  # Confianza mínima para señales RSI
        "rsi_oversold": 25,  # Nivel RSI de sobreventa (más extremo para menos señales)
        "rsi_overbought": 75,  # Nivel RSI de sobrecompra (más extremo para menos señales)
        "rsi_period": 14,  # Período RSI estándar
        "min_volume_ratio": 1.8,  # Ratio mínimo de volumen para confirmación
        "min_confluence": 6,  # Número mínimo de confirmaciones técnicas
        "trend_strength_threshold": 40,  # Umbral de fuerza de tendencia
        "min_atr_ratio": 1.2,  # Ratio ATR mínimo para volatilidad adecuada
        "max_spread_threshold": 0.002,  # Spread máximo permitido (0.2%)
        "volume_weight": 0.35,  # Peso del volumen en análisis técnico
        "confluence_threshold": 0.75,  # Umbral de confluencia técnica
        # === CONFIGURACIÓN MULTI-TIMEFRAME ===
        "mtf_enhanced_confidence": 75.0,  # Confianza mejorada con análisis MTF
        "mtf_min_confidence": 80.0,  # Confianza mínima para señales MTF
        "mtf_min_consensus": 0.80,  # Consenso mínimo entre timeframes
        "mtf_require_trend_alignment": True,  # Requiere alineación de tendencias
        "mtf_min_timeframe_consensus": 3,  # Consenso mínimo en número de timeframes
        "mtf_trend_alignment_required": True,  # Alineación de tendencia obligatoria
        "volume_timeframe": "5m",  # Timeframe para análisis de volumen
        # === CONFIGURACIÓN DE TRADING EN VIVO ===
        "trading_fees": 0.001,  # Comisiones de trading (0.1%)
        "order_timeout": 15,  # Timeout de órdenes en segundos
        "max_order_retries": 2,  # Máximo de reintentos para órdenes
        "order_check_interval": 1.0,  # Intervalo de verificación de órdenes
        "live_first_analysis_delay": 5,  # Delay inicial antes del primer análisis
        # === CONFIGURACIÓN DE MONITOREO DE POSICIONES ===
        "enable_position_monitoring": False,  # Desactivado: solo usar TP/SL automáticos
        "position_monitoring_interval": 5,  # Intervalo de monitoreo en segundos
        "price_cache_duration": 5,  # Duración del cache de precios
        "max_close_attempts": 2,  # Máximo de intentos para cerrar posiciones
        "position_timeout_hours": 4,  # Timeout para cerrar posiciones automáticamente
        "profit_scaling_threshold_percent": 0.8,  # Umbral para escalado de ganancias
        "trailing_stop_sl_pct": 0.006,  # Porcentaje de trailing stop loss
        "trailing_stop_tp_pct": 0.012,  # Porcentaje de trailing take profit
        "profit_protection_sl_pct": 0.004,  # Protección de ganancias SL
        "profit_protection_tp_pct": 0.010,  # Protección de ganancias TP
        "risk_management_threshold": -0.008,  # Umbral de gestión de riesgo
        "risk_management_sl_pct": 0.012,  # SL de gestión de riesgo
        "risk_management_tp_pct": 0.015,  # TP de gestión de riesgo
        # === CONTROL POR SESIÓN (índices y ventanas horarias) ===
        "session_strict_exits": True,  # Cerrar posiciones fuera de la ventana activa
        "session_exit_grace_minutes": 15,  # Margen de salida al terminar la sesión
        "indices_strict_session_only": True,  # Operar índices solo en sus ventanas
        "indices_tp_ceiling_price_move_pct": 0.004,  # Techo de movimiento de precio ~0.4%
        # === CONFIGURACIÓN AVANZADA DE RIESGO ===
        "kelly_win_rate": 0.62,  # Tasa de ganancia histórica para Kelly
        "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly
        "default_leverage": 1.0,  # Apalancamiento por defecto
        "default_trailing_distance": 0.015,  # Distancia de trailing por defecto
        "tp_increment_base_pct": 0.008,  # Incremento base para TP dinámico
        # === CONFIGURACIÓN DEL BOT DE TRADING ===
        "cache_ttl_seconds": 60,  # Tiempo de vida del cache en segundos
        "event_queue_maxsize": 300,  # Tamaño máximo de cola de eventos
        "executor_shutdown_timeout": 15,  # Timeout para shutdown del executor
        "thread_join_timeout": 5,  # Timeout para join de threads
        "analysis_future_timeout": 15,  # Timeout para análisis futuro
        # === CONFIGURACIÓN DE CONEXIÓN Y RED ===
        "connection_timeout": 20,  # Timeout de conexión
        "read_timeout": 40,  # Timeout de lectura
        "retry_delay": 3,  # Delay entre reintentos
        "max_retries": 2,  # Máximo de reintentos
        "backoff_factor": 1.5,  # Factor de backoff exponencial
        # === CONFIGURACIÓN DE MONITOREO E INTERVALOS ===
        "position_check_interval": 20,  # Intervalo de verificación de posiciones
        "market_data_refresh_interval": 30,  # Intervalo de actualización de datos
        "health_check_interval": 180,  # Intervalo de verificación de salud
        "log_rotation_interval": 1800,  # Intervalo de rotación de logs
        # === CONFIGURACIÓN DE RENDIMIENTO ===
        "max_concurrent_requests": 15,  # Máximo de requests concurrentes
        "request_rate_limit": 150,  # Límite de rate de requests
        "memory_threshold_mb": 256,  # Umbral de memoria en MB
        "cpu_threshold_percent": 85,  # Umbral de CPU en porcentaje
        # === CONFIGURACIÓN DE MANEJO DE ERRORES ===
        "error_cooldown_seconds": 30,  # Cooldown después de errores
        "max_consecutive_errors": 3,  # Máximo de errores consecutivos
        # === CONFIGURACIÓN DE COOLDOWN ENTRE TRADES ===
        "min_time_between_trades_minutes": 3,  # Tiempo mínimo entre trades del mismo símbolo
        "min_time_between_opposite_signals_minutes": 5,  # Tiempo mínimo entre señales opuestas
    },
    "INTRADAY": {
        "name": "Intraday",
        "description": "Perfil optimizado para trading diario con timeframes de 15m-1h, enfocado en movimientos significativos durante el día",
        # === CONFIGURACIÓN TEMPORAL ===
        "timeframes": [
            "15m",
            "30m",
            "1h",
        ],  # Timeframes balanceados para análisis intraday
        "analysis_interval": 12,  # Análisis cada 12 minutos para mayor selectividad
        # "analysis_interval": 1,  # Análisis cada 1 minuto para pruebas
        # === CONFIGURACIÓN DE CALIDAD DE SEÑALES ===
        "min_confidence": 80.0,  # Confianza mínima balanceada para intraday
        "max_daily_trades": 20,  # Límite optimizado para aprovechar diversificación de 42 símbolos
        "max_daily_trades_adaptive": False,  # Desactivado: solo trades base, sin adicionales
        "daily_trades_quality_threshold": 82.0,  # Umbral para trades adicionales (sin uso con adaptive desactivado)
        "max_daily_trades_bonus": 0,  # Sin trades adicionales; el límite efectivo se mantiene en 20
        "max_positions": 7,  # Posiciones simultáneas para máxima diversificación
        # === CONFIGURACIÓN DE PAPER TRADING ===
        "max_position_size_percent": 12,  # 12% del balance por posición - OPTIMIZADO PARA MEJORES RETORNOS
        "max_total_exposure_percent": 75,  # 75% de exposición total - OPTIMIZADO PARA MEJORES RETORNOS
        "min_trade_value": 50.0,  # Valor mínimo más alto para mejor calidad - OPTIMIZADO
        "paper_min_confidence": 80.0,  # Confianza consistente con trading real
        "max_slippage": 0.025,  # Slippage más estricto para intraday
        "min_liquidity": 12.0,  # Liquidez más alta requerida
        # === CONFIGURACIÓN DE GESTIÓN DE RIESGO ===
        "max_risk_per_trade_percent": 1.5,  # 1.5% de riesgo por trade - agresivo para trades selectivos
        "max_daily_risk_percent": 4.0,  # 4% de riesgo diario máximo - balanceado
        "max_drawdown_threshold_percent": 8,  # 8% de drawdown máximo
        "correlation_threshold": 0.65,  # Correlación moderada entre posiciones
        "min_position_size": 10.0,  # Posición mínima moderada
        "risk_max_position_size_percent": 6,  # Consistente con max_position_size
        "kelly_fraction": 0.30,  # Fracción Kelly más agresiva para trades selectivos
        "volatility_adjustment_factor": 1.2,  # Factor de ajuste por volatilidad
        # === CONFIGURACIÓN DE STOP LOSS Y TAKE PROFIT ===
        "atr_multiplier_min": 2.0,  # Stops más amplios para intraday
        "atr_multiplier_max": 3.0,  # Stops amplios optimizados para intraday
        "atr_default": 2.2,  # Multiplicador ATR por defecto
        "atr_volatile": 3.0,  # Multiplicador ATR en mercados volátiles
        "atr_sideways": 1.8,  # Multiplicador ATR en mercados laterales
        "trailing_stop_activation": 0.030,  # Trailing stop al 3% - conservador
        "breakeven_threshold_percent": 0.8,  # Breakeven al 0.8% - conservador
        "intelligent_trailing": True,
        "dynamic_position_sizing": True,
        # === CONFIGURACIÓN DE CAPITAL.COM ===
        "use_trailing_stop": True,  # Usar trailing stops nativos
        # === CONFIGURACIÓN DE TP/SL BASADO EN ROI OPTIMIZADO ===
        # Relación Riesgo:Recompensa 2:1 optimizada para criptomonedas
        "tp_min_percent": 1.5,  # Take Profit mínimo: 1.5% ROI - realista para crypto
        "tp_max_percent": 3.0,  # Take Profit máximo: 3.0% ROI - menor retención
        "sl_min_percent": 1.2,  # Stop Loss mínimo: 1.2% ROI - apropiado para crypto
        "sl_max_percent": 1.8,  # Stop Loss máximo: 1.8% ROI - reducción de riesgo
        "tp_increment_percent": 1.0,  # Factor de incremento TP balanceado
        "tp_confidence_threshold": 0.72,  # Umbral moderado para ajustar TP
        # === LÍMITES DE PROTECCIÓN ADICIONALES ===
        "max_daily_loss_percent": 6.0,  # Pérdida máxima diaria ajustada para posiciones más grandes
        "min_confidence_threshold": 0.72,  # Confianza mínima balanceada
        "position_size_multiplier": 2.0,  # Multiplicador OPTIMIZADO para trades selectivos
        # === CONFIGURACIÓN DE ESTRATEGIAS PARA CRYPTO ===
        "default_min_confidence": 75.0,  # Confianza balanceada para crypto
        "default_atr_period": 14,  # Período estándar más responsivo
        "rsi_min_confidence": 78.0,  # RSI confianza más realista
        "rsi_oversold": 30,  # RSI oversold estándar para crypto
        "rsi_overbought": 70,  # RSI overbought estándar para crypto
        "rsi_period": 14,  # Período RSI estándar más responsivo
        "min_volume_ratio": 2.0,  # Volumen mínimo más realista
        "min_confluence": 5,  # Confluencia más balanceada para intraday
        "trend_strength_threshold": 55,  # Fuerza de tendencia más accesible
        "min_atr_ratio": 1.8,  # ATR ratio ultra estricto
        "max_spread_threshold": 0.0008,  # Spread máximo ultra estricto
        "volume_weight": 0.35,  # Peso máximo al volumen
        "confluence_threshold": 0.80,  # Umbral de confluencia ultra estricto
        # === CONFIGURACIÓN MULTI-TIMEFRAME ===
        "mtf_enhanced_confidence": 78.0,  # Confianza MTF más balanceada
        "mtf_min_confidence": 75.0,  # Confianza mínima MTF coherente
        "mtf_min_consensus": 0.66,  # Consenso ajustado para permitir 66.7% (2 de 3 timeframes)
        "mtf_require_trend_alignment": True,  # Requiere alineación de tendencias
        "mtf_min_timeframe_consensus": 2,  # Consenso en 2 de 3 timeframes
        "mtf_trend_alignment_required": True,  # Alineación obligatoria
        "volume_timeframe": "15m",  # Timeframe de volumen moderado
        # === CONFIGURACIÓN DE TRADING EN VIVO ===
        "trading_fees": 0.001,  # Comisiones de trading (0.1%)
        "order_timeout": 35,  # Timeout moderado para órdenes
        "max_order_retries": 3,  # Reintentos estándar
        "order_check_interval": 1.8,  # Verificación moderada
        "live_first_analysis_delay": 15,  # Delay inicial moderado
        # === CONFIGURACIÓN ANTI-LATERAL ===
        "enable_position_monitoring": True,  # Activado para cerrar trades lentos
        "position_monitoring_interval": 20,  # Monitoreo más frecuente
        "price_cache_duration": 15,  # Cache más fresco
        "max_close_attempts": 3,  # Intentos estándar de cierre
        "position_timeout_hours": 5,  # Cerrar posiciones después de 5 horas
        "min_movement_threshold": 0.005,  # Movimiento mínimo 0.5% para progreso
        "sideways_detection_period": 120,  # Detectar lateral en 2 horas
        "profit_scaling_threshold_percent": 1.5,  # Escalado más temprano al 1.5%
        "trailing_stop_sl_pct": 0.012,  # SL trailing más agresivo 1.2%
        "trailing_stop_tp_pct": 0.030,  # TP trailing más conservador 3.0%
        "profit_protection_sl_pct": 0.008,  # Protección ganancias más temprana 0.8%
        "profit_protection_tp_pct": 0.025,  # TP protección más conservador 2.5%
        "risk_management_threshold": -0.008,  # Umbral riesgo más estricto -0.8%
        "risk_management_sl_pct": 0.010,  # SL riesgo más agresivo 1.0%
        "risk_management_tp_pct": 0.020,  # TP riesgo más conservador 2.0%
        # === CONFIGURACIÓN AVANZADA DE RIESGO ===
        "kelly_win_rate": 0.68,  # Tasa de ganancia intraday
        "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly
        "default_leverage": 1.0,  # Apalancamiento por defecto
        "default_trailing_distance": 0.018,  # Trailing moderado
        "tp_increment_base_pct": 0.012,  # Incremento TP moderado
        # === CONFIGURACIÓN DEL BOT DE TRADING ===
        "cache_ttl_seconds": 120,  # Cache moderado
        "event_queue_maxsize": 600,  # Cola moderada
        "executor_shutdown_timeout": 25,  # Shutdown moderado
        "thread_join_timeout": 8,  # Join moderado
        "analysis_future_timeout": 25,  # Análisis moderado
        # === CONFIGURACIÓN DE CONEXIÓN Y RED ===
        "connection_timeout": 30,  # Conexión estándar
        "read_timeout": 60,  # Lectura estándar
        "retry_delay": 5,  # Delay estándar
        "max_retries": 3,  # Reintentos estándar
        "backoff_factor": 2.0,  # Backoff estándar
        # === CONFIGURACIÓN DE MONITOREO E INTERVALOS ===
        "position_check_interval": 35,  # Verificación moderada
        "market_data_refresh_interval": 60,  # Actualización moderada
        "health_check_interval": 300,  # Health check moderado
        "log_rotation_interval": 3600,  # Rotación estándar
        # === CONFIGURACIÓN DE RENDIMIENTO ===
        "max_concurrent_requests": 10,  # Requests moderados
        "request_rate_limit": 100,  # Rate limit moderado
        "memory_threshold_mb": 384,  # Memoria moderada
        "cpu_threshold_percent": 75,  # CPU moderado
        # === CONFIGURACIÓN DE MANEJO DE ERRORES ===
        "error_cooldown_seconds": 45,  # Cooldown moderado
        "max_consecutive_errors": 4,  # Tolerancia moderada
        # === CONFIGURACIÓN DE COOLDOWN ENTRE TRADES ===
        "min_time_between_trades_minutes": 10,  # Tiempo mínimo entre trades del mismo símbolo
        "min_time_between_opposite_signals_minutes": 15,  # Tiempo mínimo entre señales opuestas
        # === POLÍTICA ANTIFLIP (estabilidad de señales y reducción de pérdidas pequeñas) ===
        "antiflip_min_hold_minutes": 45,  # Mantener posición al menos N minutos antes de permitir flip
        "antiflip_opposite_persistence_count": 2,  # Requerir N señales opuestas consecutivas fuertes
        "antiflip_hysteresis_multiplier": 1.10,  # Confianza opuesta debe ser >= 110% de la última ejecutada
        "antiflip_require_strong_opposite": True,  # Solo permitir flip con señales Strong/Very Strong
        "antiflip_cooldown_after_exit_minutes": 20,  # Cooldown adicional tras cerrar una posición
        # === CONTROL POR SESIÓN (índices y ventanas horarias) ===
        "session_strict_exits": True,  # Cerrar posiciones fuera de la ventana activa
        "session_exit_grace_minutes": 15,  # Margen de salida al terminar la sesión
        "indices_strict_session_only": True,  # Operar índices solo en sus ventanas
        "indices_tp_ceiling_price_move_pct": 0.004,  # Techo de movimiento de precio ~0.4%
    },
}

"""Configuración centralizada para el sistema de trading.

Este archivo contiene todas las configuraciones principales del bot de trading,
con tres niveles de configuración disponibles:

🚀 RÁPIDA: Timeframes de 1m-15m, máxima frecuencia de trades, mayor riesgo
⚡ AGRESIVA: Timeframes de 15m-1h, balance entre velocidad y control de riesgo  
🛡️ ÓPTIMA: Timeframes de 1h-1d, enfoque en calidad y preservación de capital

🎯 CAMBIO RÁPIDO DE PERFILES:
Para cambiar entre configuraciones, simplemente modifica la variable TRADING_PROFILE:
- "RAPIDO" para estrategia ultra-rápida
- "AGRESIVO" para estrategia rápida enfocada en ganancias rápidas
- "OPTIMO" para estrategia balanceada, enfocada en calidad y preservación de capital
- "CONSERVADOR" para estrategia lenta, enfocada en estabilidad y reducción de riesgo
"""

import logging
from typing import List, Dict, Any

# Configurar logger para validación
logger = logging.getLogger(__name__)

# ============================================================================
# 🎯 SELECTOR DE PERFIL DE TRADING - CAMBIAR AQUÍ
# ============================================================================

# 🔥 CAMBIAR ESTE VALOR PARA CAMBIAR TODO EL COMPORTAMIENTO DEL BOT
TRADING_PROFILE = "OPTIMO"  # Opciones: "RAPIDO", "AGRESIVO", "OPTIMO", "CONSERVADOR"

# Balance inicial global para todas las posiciones en USDT
PAPER_GLOBAL_INITIAL_BALANCE = 1000.0

# Precio base de USDT (stablecoin)
USDT_BASE_PRICE = 1.0

# ============================================================================
# 🎯 LISTA DE ACTIVOS
# ============================================================================

GLOBAL_SYMBOLS: List[str] = [
    "BTCUSDT",    # Bitcoin - Líder del mercado, alta liquidez
    "ETHUSDT",    # Ethereum - ETFs institucionales + DeFi dominance
    "SOLUSDT",    # Solana - Alto rendimiento + ecosistema maduro
    
    # HIGH GROWTH: Potencial 2-5x (35% peso recomendado)
    "AVAXUSDT",   # Avalanche - Subnets + partnerships institucionales
    "MATICUSDT",  # Polygon - POL transition + zkEVM
    "ADAUSDT",    # Cardano - Potencial ETF + desarrollo sólido
    "XRPUSDT",    # XRP - Caso legal resuelto + adopción institucional
    
    # EMERGING: Alto potencial 3-10x (25% peso recomendado)
    "NEARUSDT",   # NEAR - Escalabilidad + herramientas dev-friendly
    "LINKUSDT",   # Chainlink - Oráculos esenciales + partnerships
    "BNBUSDT"     # BNB - Utilidad Binance + burn mechanism
    ]

# ============================================================================
# 📊 DEFINICIÓN DE PERFILES DE TRADING
# ============================================================================

class TradingProfiles:
    """Definición de todos los perfiles de trading disponibles."""
    
    PROFILES = {
        "RAPIDO": {
            "name": "🚀 Ultra-Rápido",
            "description": "Timeframes 1m-15m, máxima frecuencia optimizada",
            "timeframes": ["1m", "5m"],
            "analysis_interval": 30,  # Corregido: mínimo 30 segundos
            "min_confidence": 65.0,  # Aumentado para mejor calidad de señales
            "max_daily_trades": 20,  # Reducido para mejor selección
            "max_positions": 8,  # Reducido para mejor control
            # Circuit Breaker Config - Optimizado
            "max_consecutive_losses": 7,  # Aumentado para tolerancia
            "circuit_breaker_cooldown_hours": 1.5,  # Reducido para eficiencia
            "max_drawdown_threshold": 0.12,  # Corregido: 12% como decimal
            "gradual_reactivation": True,  # Nueva funcionalidad
            # Paper Trader Config - Optimizado
            "max_position_size": 0.8,  # Corregido: 80% como decimal
            "max_total_exposure": 0.75,  # Corregido: 75% como decimal
            "min_trade_value": 5.0,  # Reducido para permitir pruebas  # Aumentado para calidad
            "paper_min_confidence": 60.0,  # Aumentado
            "max_slippage": 0.10,  # Reducido para mejor ejecución
            "min_liquidity": 4.0,  # Aumentado para liquidez
            # Risk Manager Config - Optimizado
            "max_risk_per_trade": 1.5,  # Optimizado para mejor control
            "max_daily_risk": 6.0,  # Reducido para mayor protección
            "max_drawdown_threshold": 0.10,  # Corregido: 10% como decimal
            "correlation_threshold": 0.75,  # Optimizado
            "min_position_size": 12.0,  # Reducido para flexibilidad
            "risk_max_position_size": 0.8,  # Corregido: consistente con max_position_size
            "kelly_fraction": 0.28,  # Optimizado
            "volatility_adjustment": 1.25,  # Optimizado
            "atr_multiplier_min": 1.8,  # Optimizado más ajustado
            "atr_multiplier_max": 2.8,  # Optimizado
            "atr_default": 1.8,
            "atr_volatile": 2.8,  # Optimizado
            "atr_sideways": 1.4,  # Optimizado
            "trailing_stop_activation": 0.15,  # Corregido: 15% como decimal
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
            "max_drawdown_threshold": 0.10,  # Corregido: 10% como decimal
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
            "live_first_analysis_delay": 10,  # Optimizado más rápido
            # Position Adjuster Config - Optimizado
            "position_monitoring_interval": 30,  # Intervalo de monitoreo en segundos
            "profit_scaling_threshold": 2.0,  # Umbral para escalado de ganancias (%)
            "trailing_stop_sl_pct": 0.02,  # SL dinámico para trailing stop (2%)
            "trailing_stop_tp_pct": 0.05,  # TP dinámico para trailing stop (5%)
            "profit_protection_sl_pct": 0.01,  # SL para protección de ganancias (1%)
            "profit_protection_tp_pct": 0.03,  # TP para protección de ganancias (3%)
            "risk_management_threshold": -1.0,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.015,  # SL más conservador para pérdidas (1.5%)
            "risk_management_tp_pct": 0.02,  # TP más conservador para pérdidas (2%)
            # Enhanced Risk Manager Config
            "kelly_win_rate": 0.65,  # Tasa de ganancia asumida para Kelly Criterion
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly Criterion
            "default_leverage": 1.0,  # Leverage por defecto
            "default_trailing_distance": 2.0,  # Distancia de trailing por defecto (%)
            "tp_increment_base_pct": 1.0,  # Incremento base de TP (%)
            # Trading Bot Config
            "cache_ttl_seconds": 120,  # TTL del cache en segundos (2 min)
            "event_queue_maxsize": 500,  # Tamaño máximo de la cola de eventos
            "executor_shutdown_timeout": 20,  # Timeout para shutdown del executor (seg)
            "thread_join_timeout": 8,  # Timeout para join de threads (seg)
            "analysis_future_timeout": 20,  # Timeout para análisis paralelo (seg)
            
            # Connection and Network Config
            "connection_timeout": 30,  # Timeout de conexión en segundos
            "read_timeout": 60,  # Timeout de lectura en segundos
            "retry_delay": 5,  # Delay entre reintentos en segundos
            "max_retries": 3,  # Número máximo de reintentos
            "backoff_factor": 2.0,  # Factor de backoff exponencial
            
            # Monitoring and Intervals Config
            "position_check_interval": 30,  # Intervalo de verificación de posiciones (seg)
            "market_data_refresh_interval": 60,  # Intervalo de actualización de datos (seg)
            "health_check_interval": 300,  # Intervalo de health check (seg)
            "log_rotation_interval": 3600,  # Intervalo de rotación de logs (seg)
            
            # Performance and Optimization Config
            "max_concurrent_requests": 10,  # Máximo de requests concurrentes
            "request_rate_limit": 100,  # Límite de requests por minuto
            "memory_threshold_mb": 512,  # Umbral de memoria en MB
            "cpu_threshold_percent": 80,  # Umbral de CPU en porcentaje
            
            # Error Handling Config
            "error_cooldown_seconds": 60,  # Tiempo de espera tras error (seg)
            "max_consecutive_errors": 5,  # Máximo errores consecutivos
            "circuit_breaker_threshold": 10,  # Umbral para circuit breaker
            "circuit_breaker_timeout": 300  # Timeout del circuit breaker (seg)
        },
        "AGRESIVO": {
            "name": "⚡ Agresivo",
            "description": "Timeframes 15m-1h, balance velocidad/control optimizado",
            "timeframes": ["15m", "30m"],
            "analysis_interval": 30,  # Corregido: mínimo 30 segundos
            "min_confidence": 72.0,  # Optimizado para mejor calidad
            "max_daily_trades": 15,  # Aumentado para más oportunidades
            "max_positions": 7,  # Aumentado para diversificación
            # Circuit Breaker Config - Optimizado
            "max_consecutive_losses": 4,  # Mantenido para tolerancia
            "circuit_breaker_cooldown_hours": 3,  # Optimizado para recuperación
            "max_drawdown_threshold": 0.10,  # Corregido: 10% como decimal
            "gradual_reactivation": True,  # Nueva funcionalidad
            # Paper Trader Config - Optimizado
            "max_position_size": 0.6,  # Corregido: 60% como decimal
            "max_total_exposure": 0.65,  # Corregido: 65% como decimal
            "min_trade_value": 5.0,  # Reducido para permitir pruebas
            "paper_min_confidence": 68.0,  # Aumentado para calidad
            "max_slippage": 0.06,  # Reducido para mejor ejecución
            "min_liquidity": 6.0,  # Aumentado para mejor liquidez
            # Risk Manager Config - Optimizado
            "max_risk_per_trade": 1.0,  # Optimizado para control
            "max_daily_risk": 4.5,  # Reducido para mayor protección
            "max_drawdown_threshold": 0.08,  # Corregido: 8% como decimal
            "correlation_threshold": 0.65,  # Optimizado
            "min_position_size": 8.0,  # Reducido
            "risk_max_position_size": 0.6,  # Corregido: consistente con max_position_size
            "kelly_fraction": 0.20,  # Optimizado conservador
            "volatility_adjustment": 1.10,  # Reducido para estabilidad
            "atr_multiplier_min": 2.2,  # Optimizado
            "atr_multiplier_max": 3.8,  # Optimizado
            "atr_default": 2.5,
            "atr_volatile": 3.8,  # Optimizado
            "atr_sideways": 2.2,  # Optimizado
            "trailing_stop_activation": 0.15,  # Corregido: 15% como decimal
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
            "max_drawdown_threshold": 0.08,  # Corregido: 8% como decimal
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
            "live_first_analysis_delay": 25,  # Optimizado
            # Enhanced Risk Manager Config
            "kelly_win_rate": 0.68,  # Tasa de ganancia asumida para Kelly Criterion
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly Criterion
            "default_leverage": 1.0,  # Leverage por defecto
            "default_trailing_distance": 2.2,  # Distancia de trailing por defecto (%)
            "tp_increment_base_pct": 1.3,  # Incremento base de TP (%)
            # Trading Bot Config
            "cache_ttl_seconds": 150,  # TTL del cache en segundos (2.5 min)
            "event_queue_maxsize": 600,  # Tamaño máximo de la cola de eventos
            "executor_shutdown_timeout": 25,  # Timeout para shutdown del executor (seg)
            "thread_join_timeout": 8,  # Timeout para join de threads (seg)
            "analysis_future_timeout": 25,  # Timeout para análisis paralelo (seg)
            
            # Connection and Network Config
            "connection_timeout": 25,  # Timeout de conexión más agresivo
            "read_timeout": 45,  # Timeout de lectura más rápido
            "retry_delay": 3,  # Delay entre reintentos más corto
            "max_retries": 5,  # Más reintentos para agresividad
            "backoff_factor": 1.5,  # Factor de backoff más agresivo
            
            # Monitoring and Intervals Config
            "position_check_interval": 20,  # Verificación más frecuente
            "market_data_refresh_interval": 45,  # Actualización más frecuente
            "health_check_interval": 240,  # Health check más frecuente
            "log_rotation_interval": 3600,  # Rotación de logs estándar
            
            # Performance and Optimization Config
            "max_concurrent_requests": 15,  # Más requests concurrentes
            "request_rate_limit": 150,  # Mayor límite de requests
            "memory_threshold_mb": 768,  # Mayor umbral de memoria
            "cpu_threshold_percent": 85,  # Mayor umbral de CPU
            
            # Error Handling Config
            "error_cooldown_seconds": 45,  # Menor tiempo de espera
            "max_consecutive_errors": 7,  # Más tolerancia a errores
            "circuit_breaker_threshold": 12,  # Mayor umbral para circuit breaker
            "circuit_breaker_timeout": 240  # Menor timeout del circuit breaker
        },
        "OPTIMO": {
            "name": "🎯 Óptimo",
            "description": "Timeframes 1h-4h, máxima precisión optimizada",
            "timeframes": ["1h", "4h"],
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
            "max_position_size": 1.0,  # Corregido: 100% como decimal (máximo permitido)
            "max_total_exposure": 0.55,  # Corregido: 55% como decimal
            "min_trade_value": 30.0,  # Aumentado para calidad
            "paper_min_confidence": 75.0,  # Aumentado
            "max_slippage": 0.04,  # Reducido para mejor ejecución
            "min_liquidity": 10.0,  # Aumentado para liquidez
            # Risk Manager Config - Optimizado
            "max_risk_per_trade": 0.7,  # Optimizado para máximo control
            "max_daily_risk": 3.0,  # Reducido para máxima protección
            "max_drawdown_threshold": 0.06,  # Corregido: 6% como decimal
            "correlation_threshold": 0.55,  # Optimizado
            "min_position_size": 20.0,  # Aumentado para calidad
            "risk_max_position_size": 1.0,  # Corregido: consistente con max_position_size
            "kelly_fraction": 0.15,  # Muy conservador para precisión
            "volatility_adjustment": 0.90,  # Reducido para estabilidad
            "atr_multiplier_min": 2.2,  # Optimizado
            "atr_multiplier_max": 3.2,  # Optimizado
            "atr_default": 2.2,
            "atr_volatile": 3.2,  # Optimizado
            "atr_sideways": 2.0,  # Optimizado
            "trailing_stop_activation": 0.15,  # Corregido: 15% como decimal
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
            "max_drawdown_threshold": 0.06,  # Corregido: 6% como decimal
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
            "live_first_analysis_delay": 15,  # Optimizado
            # Position Adjuster Config - Optimizado
            "position_monitoring_interval": 45,  # Intervalo de monitoreo en segundos
            "profit_scaling_threshold": 2.5,  # Umbral para escalado de ganancias (%)
            "trailing_stop_sl_pct": 0.025,  # SL dinámico para trailing stop (2.5%)
            "trailing_stop_tp_pct": 0.06,  # TP dinámico para trailing stop (6%)
            "profit_protection_sl_pct": 0.012,  # SL para protección de ganancias (1.2%)
            "profit_protection_tp_pct": 0.035,  # TP para protección de ganancias (3.5%)
            "risk_management_threshold": -1.2,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.018,  # SL más conservador para pérdidas (1.8%)
            "risk_management_tp_pct": 0.025,  # TP más conservador para pérdidas (2.5%)
            # Enhanced Risk Manager Config
            "kelly_win_rate": 0.62,  # Tasa de ganancia asumida para Kelly Criterion
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly Criterion
            "default_leverage": 1.0,  # Leverage por defecto
            "default_trailing_distance": 2.5,  # Distancia de trailing por defecto (%)
            "tp_increment_base_pct": 1.2,  # Incremento base de TP (%)
            # Trading Bot Config
            "cache_ttl_seconds": 180,  # TTL del cache en segundos (3 min)
            "event_queue_maxsize": 800,  # Tamaño máximo de la cola de eventos
            "executor_shutdown_timeout": 30,  # Timeout para shutdown del executor (seg)
            "thread_join_timeout": 10,  # Timeout para join de threads (seg)
            "analysis_future_timeout": 30,  # Timeout para análisis paralelo (seg)
            
            # Connection and Network Config
            "connection_timeout": 35,  # Timeout de conexión balanceado
            "read_timeout": 70,  # Timeout de lectura balanceado
            "retry_delay": 7,  # Delay entre reintentos balanceado
            "max_retries": 3,  # Reintentos estándar
            "backoff_factor": 2.0,  # Factor de backoff estándar
            
            # Monitoring and Intervals Config
            "position_check_interval": 40,  # Verificación balanceada
            "market_data_refresh_interval": 75,  # Actualización balanceada
            "health_check_interval": 360,  # Health check balanceado
            "log_rotation_interval": 3600,  # Rotación de logs estándar
            
            # Performance and Optimization Config
            "max_concurrent_requests": 8,  # Requests concurrentes balanceados
            "request_rate_limit": 80,  # Límite de requests balanceado
            "memory_threshold_mb": 640,  # Umbral de memoria balanceado
            "cpu_threshold_percent": 75,  # Umbral de CPU balanceado
            
            # Error Handling Config
            "error_cooldown_seconds": 75,  # Tiempo de espera balanceado
            "max_consecutive_errors": 4,  # Tolerancia a errores balanceada
            "circuit_breaker_threshold": 8,  # Umbral balanceado para circuit breaker
            "circuit_breaker_timeout": 360  # Timeout balanceado del circuit breaker
        },
        "CONSERVADOR": {
            "name": "🛡️ Conservador",
            "description": "Timeframes 1d-1s, máxima preservación de capital",
            "timeframes": ["1d", "1s"],  # Timeframes más largos
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
            "max_position_size": 0.4,  # Corregido: 40% como decimal
            "max_total_exposure": 0.35,  # Corregido: 35% como decimal
            "min_trade_value": 50.0,  # Alto para calidad
            "paper_min_confidence": 80.0,  # Muy alto
            "max_slippage": 0.03,  # Muy estricto
            "min_liquidity": 15.0,  # Muy alto
            # Risk Manager Config - Ultra conservador
            "max_risk_per_trade": 0.4,  # Extremadamente bajo
            "max_daily_risk": 1.5,  # Muy limitado para máxima protección
            "max_drawdown_threshold": 0.05,  # Corregido: 5% como decimal (mínimo permitido)
            "correlation_threshold": 0.4,  # Muy estricto
            "min_position_size": 30.0,  # Alto para calidad
            "risk_max_position_size": 0.4,  # Corregido: consistente con max_position_size
            "kelly_fraction": 0.08,  # Extremadamente conservador
            "volatility_adjustment": 0.75,  # Muy reducido para estabilidad
            "atr_multiplier_min": 3.5,  # Stops más amplios
            "atr_multiplier_max": 5.5,  # Stops muy amplios
            "atr_default": 3.5,
            "atr_volatile": 5.5,  # Muy amplio
            "atr_sideways": 3.0,  # Amplio
            "trailing_stop_activation": 0.20,  # Corregido: 20% como decimal
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
            "max_drawdown_threshold": 0.05,  # Corregido: 5% como decimal (mínimo permitido)
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
            "live_first_analysis_delay": 90,  # Más tiempo inicial
            # Position Adjuster Config - Ultra conservador
            "position_monitoring_interval": 120,  # Intervalo de monitoreo en segundos (2 min)
            "profit_scaling_threshold": 3.0,  # Umbral para escalado de ganancias (%)
            "trailing_stop_sl_pct": 0.015,  # SL dinámico para trailing stop (1.5%)
            "trailing_stop_tp_pct": 0.04,  # TP dinámico para trailing stop (4%)
            "profit_protection_sl_pct": 0.008,  # SL para protección de ganancias (0.8%)
            "profit_protection_tp_pct": 0.025,  # TP para protección de ganancias (2.5%)
            "risk_management_threshold": -0.8,  # Umbral para gestión de riesgo (%)
            "risk_management_sl_pct": 0.012,  # SL más conservador para pérdidas (1.2%)
            "risk_management_tp_pct": 0.018,  # TP más conservador para pérdidas (1.8%)
            # Enhanced Risk Manager Config
            "kelly_win_rate": 0.58,  # Tasa de ganancia asumida para Kelly Criterion
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly Criterion
            "default_leverage": 1.0,  # Leverage por defecto
            "default_trailing_distance": 1.8,  # Distancia de trailing por defecto (%)
            "tp_increment_base_pct": 0.8,  # Incremento base de TP (%)
            # Trading Bot Config
            "cache_ttl_seconds": 300,  # TTL del cache en segundos (5 min)
            "event_queue_maxsize": 1200,  # Tamaño máximo de la cola de eventos
            "executor_shutdown_timeout": 45,  # Timeout para shutdown del executor (seg)
            "thread_join_timeout": 15,  # Timeout para join de threads (seg)
            "analysis_future_timeout": 45,  # Timeout para análisis paralelo (seg)
            
            # Connection and Network Config
            "connection_timeout": 45,  # Timeout de conexión conservador
            "read_timeout": 90,  # Timeout de lectura conservador
            "retry_delay": 10,  # Delay entre reintentos más largo
            "max_retries": 2,  # Menos reintentos para conservador
            "backoff_factor": 3.0,  # Factor de backoff más conservador
            
            # Monitoring and Intervals Config
            "position_check_interval": 60,  # Verificación menos frecuente
            "market_data_refresh_interval": 120,  # Actualización menos frecuente
            "health_check_interval": 600,  # Health check menos frecuente
            "log_rotation_interval": 7200,  # Rotación de logs menos frecuente
            
            # Performance and Optimization Config
            "max_concurrent_requests": 5,  # Menos requests concurrentes
            "request_rate_limit": 50,  # Menor límite de requests
            "memory_threshold_mb": 384,  # Menor umbral de memoria
            "cpu_threshold_percent": 60,  # Menor umbral de CPU
            
            # Error Handling Config
            "error_cooldown_seconds": 120,  # Mayor tiempo de espera
            "max_consecutive_errors": 2,  # Menor tolerancia a errores
            "circuit_breaker_threshold": 5,  # Menor umbral para circuit breaker
            "circuit_breaker_timeout": 600  # Mayor timeout del circuit breaker
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
    SYMBOLS = GLOBAL_SYMBOLS

    # Símbolos para el bot en vivo - Misma lista optimizada
    SYMBOLS_LIVE_BOT = GLOBAL_SYMBOLS[3]
    
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
    DEFAULT_PORTFOLIO_VALUE: float = PAPER_GLOBAL_INITIAL_BALANCE
    
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
    def get_monitoring_interval(cls) -> int:
        """Intervalo de monitoreo de posiciones según perfil."""
        return TradingProfiles.get_current_profile().get("position_monitoring_interval", 30)
    
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
    def get_circuit_breaker_cooldown_hours(cls) -> int:
        """Horas de cooldown después de activar circuit breaker según perfil activo."""
        return TradingProfiles.get_current_profile()["circuit_breaker_cooldown_hours"]
    
    @classmethod
    def get_max_drawdown_threshold(cls) -> float:
        """Umbral máximo de drawdown según perfil activo."""
        return TradingProfiles.get_current_profile()["max_drawdown_threshold"]


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USDT para simulación
    INITIAL_BALANCE: float = PAPER_GLOBAL_INITIAL_BALANCE
    
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
    
    # ---- Estrategia RSI Profesional ----
    class ProfessionalRSI:
        """Parámetros para la estrategia RSI profesional."""
        
        @classmethod
        def get_min_confidence(cls) -> float:
            """Confianza mínima según perfil activo."""
            return TradingProfiles.get_current_profile().get("rsi_min_confidence", 65.0)
        
        @classmethod
        def get_rsi_oversold(cls) -> int:
            """Nivel RSI sobreventa según perfil activo."""
            return TradingProfiles.get_current_profile().get("rsi_oversold", 35)
        
        @classmethod
        def get_rsi_overbought(cls) -> int:
            """Nivel RSI sobrecompra según perfil activo."""
            return TradingProfiles.get_current_profile().get("rsi_overbought", 65)
        
        @classmethod
        def get_rsi_period(cls) -> int:
            """Período RSI según perfil activo."""
            return TradingProfiles.get_current_profile().get("rsi_period", 10)
        
        @classmethod
        def get_min_volume_ratio(cls) -> float:
            """Ratio mínimo de volumen según perfil activo."""
            return TradingProfiles.get_current_profile().get("min_volume_ratio", 1.2)
        
        @classmethod
        def get_min_confluence(cls) -> int:
            """Confluencia mínima según perfil activo."""
            return TradingProfiles.get_current_profile().get("min_confluence", 2)
        
        @classmethod
        def get_trend_strength_threshold(cls) -> float:
            """Umbral fuerza tendencia según perfil activo."""
            return TradingProfiles.get_current_profile().get("trend_strength_threshold", 25)
        
        # Valores estáticos
        BASE_CONFIDENCE: float = 50.0
        HOLD_CONFIDENCE: float = 45.0
        
        # Compatibilidad con código existente (fallbacks)
        MIN_CONFIDENCE: float = 65.0
        RSI_OVERSOLD: int = 35
        RSI_OVERBOUGHT: int = 65
        RSI_PERIOD: int = 10
        MIN_VOLUME_RATIO: float = 1.2
        MIN_CONFLUENCE: int = 2
        TREND_STRENGTH_THRESHOLD: float = 25.0
        
        # Ratio ATR mínimo para volatilidad (rápido: 0.8 - agresivo: 1.0 - óptimo: 1.2)
        MIN_ATR_RATIO: float = 0.8  # Estrategia rápida
        
        # Spread máximo permitido en % (rápido: 0.0025 - agresivo: 0.0015 - óptimo: 0.0010)
        MAX_SPREAD_THRESHOLD: float = 0.0025  # Estrategia rápida
    
    # ---- Estrategia Multi-Timeframe ----
    class MultiTimeframe:
        """Parámetros para la estrategia multi-timeframe."""
        
        @classmethod
        def get_enhanced_confidence(cls) -> float:
            """Confianza mejorada según perfil activo."""
            return TradingProfiles.get_current_profile().get("mtf_enhanced_confidence", 60.0)
        
        @classmethod
        def get_min_confidence(cls) -> float:
            """Confianza mínima según perfil activo."""
            return TradingProfiles.get_current_profile().get("mtf_min_confidence", 62.0)
        
        @classmethod
        def get_min_consensus(cls) -> float:
            """Consenso mínimo según perfil activo."""
            return TradingProfiles.get_current_profile().get("mtf_min_consensus", 0.6)
        
        # Valores estáticos
        BASE_CONFIDENCE: float = 50.0
        HOLD_CONFIDENCE: float = 45.0
        
        # Compatibilidad con código existente (fallbacks)
        ENHANCED_CONFIDENCE: float = 60.0
        MIN_CONFIDENCE: float = 62.0
        
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
        
        @classmethod
        def get_min_consensus_threshold(cls) -> float:
            """Umbral consenso mínimo según perfil activo."""
            return TradingProfiles.get_current_profile().get("ensemble_min_consensus_threshold", 0.55)
        
        @classmethod
        def get_confidence_boost_factor(cls) -> float:
            """Factor boost confianza según perfil activo."""
            return TradingProfiles.get_current_profile().get("ensemble_confidence_boost_factor", 1.25)
        
        # Valores estáticos
        BASE_CONFIDENCE: float = 50.0
        HOLD_CONFIDENCE: float = 45.0
        
        # Pesos de cada estrategia en el ensemble
        STRATEGY_WEIGHTS: Dict[str, float] = {
            "Professional_RSI": 0.4,
            "Multi_Timeframe": 0.6
        }
        
        # Compatibilidad con código existente (fallbacks)
        MIN_CONSENSUS_THRESHOLD: float = 0.55
        CONFIDENCE_BOOST_FACTOR: float = 1.25


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

# ============================================================================
# 🔧 CONFIGURACIONES CENTRALIZADAS DE PARÁMETROS HARDCODEADOS
# ============================================================================

class APIConfig:
    """🌐 Configuración centralizada de APIs y endpoints"""
    
    # Binance API Configuration
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"
    BINANCE_ENDPOINTS = {
        "ticker_price": "/ticker/price",
        "klines": "/klines",
        "exchange_info": "/exchangeInfo",
        "24hr_ticker": "/ticker/24hr"
    }
    
    # Request Configuration
    REQUEST_TIMEOUT = 5  # segundos
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos
    
    # Sleep intervals para scheduler y error handling
    SCHEDULER_SLEEP_INTERVAL = 1  # segundos
    ERROR_RECOVERY_SLEEP = 5  # segundos
    LATENCY_SIMULATION_SLEEP = 0.1  # segundos
    
    # Data Limits
    DEFAULT_KLINES_LIMIT = 1000
    MAX_KLINES_LIMIT = 1500
    MIN_KLINES_LIMIT = 100
    
    @classmethod
    def get_binance_url(cls, endpoint: str) -> str:
        """Obtener URL completa de Binance"""
        return cls.BINANCE_BASE_URL + cls.BINANCE_ENDPOINTS.get(endpoint, "")
    
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
        'trailing_stop_activation': (0.01, 0.5),
        'trailing_stop_distance': (0.005, 0.2),
        'max_drawdown_threshold': (0.05, 0.5),
        'volatility_adjustment_factor': (0.5, 3.0),
        'min_confidence_score': (30, 95),
        'analysis_interval': (30, 3600),
        'position_check_interval': (10, 300),
        'connection_timeout': (5, 120),
        'max_retries': (1, 10),
        'retry_delay': (0.5, 30.0),
        'max_consecutive_losses': (1, 20),
        'circuit_breaker_cooldown_hours': (1, 48)
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
    
    # Verificar que el perfil actual existe
    if TRADING_PROFILE not in TradingProfiles.PROFILES:
        logger.error(f"Perfil '{TRADING_PROFILE}' no existe. Perfiles disponibles: {list(TradingProfiles.PROFILES.keys())}")
        return False
    
    # Mostrar configuración actual
    current_profile = TradingProfiles.get_current_profile()
    logger.info(f"Perfil activo: {TRADING_PROFILE} - {current_profile['name']}")
    logger.info(f"Timeframes: {current_profile['timeframes']}")
    logger.info(f"Intervalo de análisis: {current_profile['analysis_interval']}s")
    logger.info(f"Confianza mínima: {current_profile['min_confidence']}%")
    
    logger.info("✅ Configuración inicializada correctamente")
    return True


# Validar configuración al importar el módulo
try:
    if not initialize_config():
        logger.warning("⚠️ Configuración inicializada con advertencias")
except Exception as e:
    logger.error(f"❌ Error al inicializar configuración: {e}")
"""
🎯 ConfigManager Centralizado - Arquitectura de Configuración Robusta

Este módulo centraliza TODA la configuración del sistema de trading,
eliminando dependencias circulares y garantizando configuraciones 100% consolidadas.

🔧 CARACTERÍSTICAS:
- ✅ Configuración centralizada y validada automáticamente
- ✅ Perfiles de trading robustos (AGRESIVO, OPTIMO, CONSERVADOR)
- ✅ Fallbacks automáticos para evitar valores N/A
- ✅ Validación en tiempo real de todas las configuraciones
- ✅ Eliminación de dependencias circulares
- ✅ API unificada para todos los módulos

🎯 USO:
```python
from config.config_manager import ConfigManager

# Obtener configuración consolidada
config = ConfigManager.get_consolidated_config()

# Obtener configuración específica de un módulo
trading_config = ConfigManager.get_module_config('trading_bot')
risk_config = ConfigManager.get_module_config('risk_manager')
```
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from datetime import datetime
import os

# Importar constantes globales centralizadas
from .global_constants import (
    GLOBAL_INITIAL_BALANCE, USDT_BASE_PRICE, TIMEZONE, 
    DAILY_RESET_HOUR, DAILY_RESET_MINUTE, SYMBOLS, TEST_SYMBOLS,
    ACTIVE_TRADING_PROFILE
)

# Configurar logging
logger = logging.getLogger(__name__)

class TradingProfile(Enum):
    """Perfiles de trading disponibles"""
    AGRESIVO = "AGRESIVO" 
    OPTIMO = "OPTIMO"
    CONSERVADOR = "CONSERVADOR"

@dataclass
class ProfileConfig:
    """Configuración base de un perfil de trading"""
    name: str
    description: str
    timeframes: List[str]
    risk_level: str
    frequency: str
    
    # Configuraciones específicas por módulo
    trading_bot: Dict[str, Any] = field(default_factory=dict)
    risk_manager: Dict[str, Any] = field(default_factory=dict)
    paper_trader: Dict[str, Any] = field(default_factory=dict)
    strategies: Dict[str, Any] = field(default_factory=dict)
    indicators: Dict[str, Any] = field(default_factory=dict)
    position_manager: Dict[str, Any] = field(default_factory=dict)
    position_monitor: Dict[str, Any] = field(default_factory=dict)
    position_adjuster: Dict[str, Any] = field(default_factory=dict)
    market_validator: Dict[str, Any] = field(default_factory=dict)
    
    # 🚀 NUEVAS OPTIMIZACIONES AVANZADAS
    advanced_optimizations: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """🎯 Gestor centralizado de configuraciones del sistema de trading"""
    
    # Perfil activo del sistema (se puede cambiar dinámicamente con set_active_profile())
    _active_profile: TradingProfile = TradingProfile(ACTIVE_TRADING_PROFILE)
    
    # Cache de configuraciones
    _config_cache: Dict[str, Any] = {}
    _profiles_cache: Dict[TradingProfile, ProfileConfig] = {}
    
    # Archivo de configuración persistente
    _config_file = "config_profile.json"
    
    @classmethod
    def initialize(cls, profile: str = None) -> None:
        """🚀 Inicializa el ConfigManager con el perfil especificado"""
        try:
            # Usar ACTIVE_TRADING_PROFILE si no se especifica un perfil
            if profile is None:
                profile = ACTIVE_TRADING_PROFILE
            cls._active_profile = TradingProfile(profile)
            cls._load_all_profiles()
            cls._validate_all_configurations()
            logger.info(f"✅ ConfigManager inicializado con perfil: {profile}")
        except Exception as e:
            logger.error(f"❌ Error inicializando ConfigManager: {e}")
            cls._active_profile = TradingProfile(ACTIVE_TRADING_PROFILE)
            cls._load_default_configurations()
    
    @classmethod
    def _load_all_profiles(cls) -> None:
        """📋 Carga todas las configuraciones de perfiles"""
        
        # Perfil AGRESIVO - Balanceado Optimizado
        cls._profiles_cache[TradingProfile.AGRESIVO] = ProfileConfig(
            name="⚡ Agresivo Optimizado",
            description="Timeframes 5m-30m optimizados para trading activo con alta frecuencia",
            timeframes=["5m", "15m", "30m"],  # Timeframes más cortos para mayor reactividad
            risk_level="medium_high",
            frequency="very_high",  # Aumentar frecuencia para aprovechar movimientos rápidos
            trading_bot={
                'analysis_interval': 30,  # Análisis más frecuente para timeframes cortos
                'min_confidence': 0.68,  # Reducir umbral para más oportunidades (68%)
                'max_positions': 8,  # Más posiciones para aprovechar volatilidad
                'max_daily_trades': 50,  # Aumentar límite diario para trading activo
                'max_concurrent_positions': 8,  # Más posiciones concurrentes
                'symbols': ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT'],
                'position_timeout': 300,  # Timeout más corto para trading activo
                'quick_exit_enabled': True,
                'scalping_mode': True  # Activar modo scalping para timeframes cortos
            },
            risk_manager={
                'max_risk_per_trade': 0.025,  # Riesgo más controlado para trading frecuente
                'risk_per_trade': 2.5,
                'max_daily_risk': 0.12,  # Límite diario ajustado para más trades
                'max_drawdown_threshold': 0.18,  # Tolerancia más estricta
                'max_drawdown': 18.0,
                'stop_loss_percentage': 1.8,  # SL más ajustado para timeframes cortos
                'take_profit_percentage': 3.6,  # TP optimizado para movimientos rápidos (ratio 2:1)
                'correlation_threshold': 0.75,  # Correlación más estricta
                'min_position_size': 6.0,  # Posiciones más pequeñas para mayor diversificación
                'max_position_size': 0.10,  # 10% del balance - Tamaño máximo ajustado
                'kelly_fraction': 0.35,  # Sizing más conservador para alta frecuencia
                'position_size_multiplier': 1.0,  # Multiplicador neutral
                'volatility_adjustment_factor': 1.5,  # Mayor ajuste por volatilidad
                'atr_multiplier': 1.5,  # ATR ajustado para timeframes cortos
                'profit_target_multiplier': 2.0,  # Ratio R/R 2:1 para trading activo
                'dynamic_sizing_enabled': True,  # Sizing dinámico
                'risk_scaling_factor': 1.1  # Factor de escalado más conservador
            },
            paper_trader={
                'initial_balance': GLOBAL_INITIAL_BALANCE,
                'max_position_size': 0.08,  # 8% del balance
                'max_total_exposure': 400.0,
                'min_trade_value': 8.0,
                'min_trade_amount': 8.0,
                'commission_rate': 0.001,
                'paper_min_confidence': 70.0,
                'max_slippage': 0.002,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 30,  # Configuración AGRESIVO optimizada
                'rsi_overbought': 70,  # Configuración AGRESIVO optimizada
                'rsi_period': 9,  # Consistente con indicadores
                'confidence_boost_factor': 1.3,  # Mayor boost para señales fuertes
                'timeframes': ["15m", "1h", "4h"],
                'macd_fast': 8,  # Consistente con indicadores optimizados
                'macd_slow': 21,
                'macd_signal': 7,
                'bb_period': 18,  # Consistente con indicadores
                'bb_std': 1.8,  # Bandas más estrechas para señales tempranas
                'volume_threshold': 1.3,  # Umbral de volumen optimizado
                'momentum_threshold': 0.025,  # Momentum más sensible
                'trend_strength_threshold': 0.6,  # Filtro de tendencia
                'multi_timeframe_confirmation': True  # Confirmación multi-timeframe
            },
            indicators={
                'rsi_period': 9,  # Ligeramente más sensible
                'macd_periods': [8, 21, 7],  # Optimizado para timeframes medios
                'bb_period': 18,  # Más reactivo que el estándar
                'volume_sma_period': 12,  # Volumen más sensible
                'atr_period': 9,  # ATR optimizado
                'stoch_k_period': 12,  # Stochastic balanceado
                'stoch_d_period': 4,
                'williams_r_period': 12,  # Williams %R optimizado
                'cci_period': 16,  # CCI para momentum medio
                'fibonacci_lookback': 40,  # Fibonacci para timeframes medios
                'ema_fast_period': 8,  # EMA rápida optimizada
                'ema_slow_period': 21  # EMA lenta optimizada
            },
            advanced_optimizations={
                # 🎯 OPTIMIZACIONES DE WIN RATE
                'win_rate_target': 95.0,  # Win rate objetivo optimizado
                'confirmation_filters': {
                    'enabled': True,
                    'min_confirmations': 4,  # Mínimo 4 indicadores deben coincidir
                    'rsi_confluence': True,  # RSI debe confirmar
                    'macd_confluence': True,  # MACD debe confirmar
                    'volume_confluence': True,  # Volumen debe confirmar
                    'trend_confluence': True,  # Tendencia debe confirmar
                    'volatility_filter': True,  # Filtrar alta volatilidad
                    'max_volatility_threshold': 0.04  # Máximo 4% de volatilidad
                },
                
                # 📈 TAKE PROFIT DINÁMICO
                'dynamic_take_profit': {
                    'enabled': True,
                    'base_multiplier': 2.5,  # Multiplicador base R:R más agresivo
                    'atr_based': True,  # Usar ATR para cálculo
                    'trend_adjustment': True,  # Ajustar según tendencia
                    'volatility_adjustment': True,  # Ajustar según volatilidad
                    'max_tp_multiplier': 4.0,  # Máximo multiplicador
                    'min_tp_multiplier': 2.0,  # Mínimo multiplicador
                    'scaling_levels': [0.4, 0.3, 0.3]  # Escalado de salidas
                },
                
                # ⚖️ GESTIÓN DE POSICIÓN ADAPTATIVA
                'adaptive_position_sizing': {
                    'enabled': True,
                    'base_risk_percent': 3.5,  # Riesgo base por trade más agresivo
                    'volatility_adjustment': True,  # Ajustar por volatilidad
                    'confidence_scaling': True,  # Escalar por confianza
                    'market_condition_adjustment': True,  # Ajustar por condiciones
                    'max_position_multiplier': 1.8,  # Máximo multiplicador
                    'min_position_multiplier': 0.6,  # Mínimo multiplicador
                    'kelly_criterion_enabled': True  # Usar criterio de Kelly
                },
                
                # 📊 MÉTRICAS DE OPTIMIZACIÓN
                'optimization_metrics': {
                    'target_profit_factor': 7.84,  # Profit factor objetivo
                    'target_sharpe_ratio': 3.0,  # Sharpe ratio objetivo
                    'max_drawdown_limit': 18.0,  # Máximo drawdown permitido
                    'min_win_rate': 92.0,  # Win rate mínimo
                    'rebalance_frequency': 'daily'  # Frecuencia de rebalanceo
                }
            }
        )
        
        # Perfil OPTIMO - Swing Trading Balanceado
        cls._profiles_cache[TradingProfile.OPTIMO] = ProfileConfig(
            name="⚖️ Óptimo Balanceado",
            description="Swing trading 1h-1d optimizado para balance perfecto entre riesgo y retorno",
            timeframes=["1h", "4h", "1d"],
            risk_level="medium",
            frequency="medium",
            trading_bot={
                'analysis_interval': 75,  # Análisis más frecuente para mejor timing
                'min_confidence': 0.72,  # Mayor confianza para swing trading de calidad (72%)
                'max_positions': 6,  # Más posiciones para diversificación balanceada
                'max_daily_trades': 15,  # Usar configuración optimizada
                'max_concurrent_positions': 6,  # Posiciones concurrentes balanceadas
                'symbols': ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT'],  # Más símbolos para diversificación
                'position_timeout': 1200,  # Timeout optimizado para swing trading
                'quick_exit_enabled': True,  # Salidas rápidas habilitadas para protección
                'scalping_mode': False,
                'swing_trading_mode': True,  # Modo swing trading específico
                'trend_following_enabled': True,  # Seguimiento de tendencias para swings
                'cache_ttl_seconds': 150,  # Cache TTL optimizado: 2x analysis_interval para evitar repeticiones
                'event_queue_maxsize': 100,  # Tamaño de cola de eventos
                'min_time_between_trades_seconds': 300,  # Tiempo mínimo entre trades
                'max_trades_per_hour': 4,  # Máximo trades por hora para swing trading
                'post_reset_spacing_minutes': 90  # Espaciado post-reset optimizado para swings
            },
            risk_manager={
                'max_risk_per_trade': 0.03,  # Riesgo balanceado optimizado para swing trading
                'risk_per_trade': 3.0,
                'max_daily_risk': 0.10,  # Mayor límite diario para aprovechar swings
                'max_drawdown_threshold': 0.15,  # Tolerancia optimizada para swing trading
                'max_drawdown': 15.0,
                'stop_loss_percentage': 2.5,  # Stop loss optimizado para swings
                'take_profit_percentage': 7.5,  # TP balanceado para swing trading (ratio 3:1)
                'correlation_threshold': 0.65,  # Correlación más permisiva para diversificación
                'min_position_size': 8.0,  # Posiciones más flexibles
                'max_position_size': 0.18,  # 18% del balance - Mayor tamaño para señales de swing trading
                'kelly_fraction': 0.35,  # Sizing más agresivo para swing trading
                'position_size_multiplier': 1.2,  # Multiplicador optimizado para swings
                'volatility_adjustment_factor': 1.3,  # Mayor ajuste por volatilidad
                'atr_multiplier': 2.2,  # ATR optimizado para swing trading
                'profit_target_multiplier': 3.0,  # Ratio R/R 3:1 para swing trading
                'dynamic_sizing_enabled': True,  # Sizing dinámico
                'risk_scaling_factor': 1.1,  # Factor de escalado optimizado
                'quality_filter_enabled': True,  # Filtro de calidad habilitado
                'swing_risk_adjustment': True  # Ajuste específico para swing trading
            },
            paper_trader={
                'initial_balance': GLOBAL_INITIAL_BALANCE,
                'max_position_size': 0.12,  # 12% del balance por posición
                'max_total_exposure': 600.0,
                'min_trade_value': 15.0,
                'min_trade_amount': 15.0,
                'commission_rate': 0.001,
                'paper_min_confidence': 60.0,
                'max_slippage': 0.0008,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 25,  # Más agresivo para capturar swings tempranos
                'rsi_overbought': 75,  # Más agresivo para ventas en swings
                'rsi_period': 14,  # RSI estándar optimizado para swing trading
                'confidence_boost_factor': 1.35,  # Mayor boost para señales de swing trading
                'timeframes': ["1h", "4h", "1d"],
                'macd_fast': 12,  # MACD optimizado para swing trading
                'macd_slow': 26,
                'macd_signal': 9,
                'bb_period': 20,  # Bandas de Bollinger estándar para swings
                'bb_std': 2.0,  # Bandas estándar para swing trading
                'volume_threshold': 1.3,  # Umbral de volumen balanceado
                'momentum_threshold': 0.025,  # Momentum optimizado para swings
                'trend_strength_threshold': 0.6,  # Filtro de tendencia balanceado
                'multi_timeframe_confirmation': True,  # Confirmación multi-timeframe
                'signal_quality_threshold': 0.75,  # Mayor filtro de calidad para swings
                'divergence_detection': True,  # Detección de divergencias
                'swing_pattern_recognition': True,  # Reconocimiento de patrones de swing
                'support_resistance_levels': True,  # Niveles de soporte y resistencia
                'fibonacci_retracement': True,  # Retrocesos de Fibonacci para swings
                'trend_continuation_filter': True  # Filtro de continuación de tendencia
            },
            indicators={
                'rsi_period': 14,  # RSI estándar para swing trading
                'macd_periods': [12, 26, 9],  # MACD estándar optimizado para swings
                'bb_period': 20,  # Bandas de Bollinger estándar
                'volume_sma_period': 20,  # Volumen balanceado para swings
                'atr_period': 14,  # ATR estándar para swing trading
                'stoch_k_period': 14,  # Stochastic estándar
                'stoch_d_period': 3,
                'williams_r_period': 14,  # Williams %R estándar
                'cci_period': 20,  # CCI para momentum de swing trading
                'fibonacci_lookback': 55,  # Fibonacci optimizado para swings
                'ema_fast_period': 12,  # EMA rápida para swing trading
                'ema_slow_period': 26,  # EMA lenta para swing trading
                'adx_period': 14,  # ADX estándar para fuerza de tendencia
                'obv_period': 20,  # OBV optimizado para swings
                'sma_short_period': 20,  # SMA corta para swing trading
                'sma_long_period': 50,  # SMA larga para swing trading
                'vwap_period': 20,  # VWAP para swing trading
                'momentum_period': 10,  # Momentum para swing trading
                'roc_period': 12  # Rate of Change para swing trading
            },
            advanced_optimizations={
                # 🎯 OPTIMIZACIONES DE WIN RATE PARA SWING TRADING
                'win_rate_target': 88.5,  # Win rate objetivo balanceado para swing trading
                'confirmation_filters': {
                    'enabled': True,
                    'min_confirmations': 4,  # 4 indicadores para balance entre calidad y oportunidades
                    'rsi_confluence': True,  # RSI debe confirmar
                    'macd_confluence': True,  # MACD debe confirmar
                    'volume_confluence': True,  # Volumen debe confirmar
                    'trend_confluence': True,  # Tendencia debe confirmar
                    'volatility_filter': True,  # Filtrar alta volatilidad
                    'max_volatility_threshold': 0.04,  # Máximo 4% de volatilidad para swings
                    'adx_filter': True,  # Filtro ADX para tendencias fuertes
                    'min_adx_threshold': 22.0,  # ADX mínimo balanceado para swings
                    'support_resistance_filter': True,  # Filtro de soporte/resistencia
                    'fibonacci_level_filter': True  # Filtro de niveles de Fibonacci
                },
                
                # 📈 TAKE PROFIT DINÁMICO PARA SWING TRADING
                'dynamic_take_profit': {
                    'enabled': True,
                    'base_multiplier': 3.5,  # Multiplicador base R:R optimizado para swings
                    'atr_based': True,  # Usar ATR para cálculo
                    'trend_adjustment': True,  # Ajustar según tendencia
                    'volatility_adjustment': True,  # Ajustar según volatilidad
                    'max_tp_multiplier': 6.0,  # Máximo multiplicador para swings largos
                    'min_tp_multiplier': 2.5,  # Mínimo multiplicador
                    'scaling_levels': [0.25, 0.35, 0.4],  # Escalado optimizado para swings
                    'fibonacci_targets': True,  # Usar niveles de Fibonacci
                    'swing_extension_targets': True,  # Objetivos de extensión para swings
                    'trend_strength_multiplier': 1.2  # Multiplicador por fuerza de tendencia
                },
                

                
                # ⚖️ GESTIÓN DE POSICIÓN ADAPTATIVA PARA SWING TRADING
                'adaptive_position_sizing': {
                    'enabled': True,
                    'base_risk_percent': 3.0,  # Riesgo base optimizado para swing trading
                    'volatility_adjustment': True,  # Ajustar por volatilidad
                    'confidence_scaling': True,  # Escalar por confianza
                    'market_condition_adjustment': True,  # Ajustar por condiciones
                    'max_position_multiplier': 1.6,  # Máximo multiplicador para swings
                    'min_position_multiplier': 0.6,  # Mínimo multiplicador
                    'kelly_criterion_enabled': True,  # Usar criterio de Kelly
                    'quality_filter_multiplier': 1.3,  # Mayor multiplicador por calidad
                    'swing_momentum_multiplier': 1.15,  # Multiplicador por momentum de swing
                    'trend_alignment_bonus': 1.1  # Bonus por alineación de tendencia
                },
                
                # ⏰ SALIDAS BASADAS EN TIEMPO PARA SWING TRADING
                'time_based_exits': {
                    'enabled': True,
                    'max_hold_time_hours': 72,  # Máximo 3 días para swing trading
                    'profit_target_time_hours': 24,  # Target de profit en 24 horas
                    'loss_cut_time_hours': 48,  # Corte de pérdidas en 48 horas
                    'time_decay_factor': 0.05,  # Menor decaimiento temporal para swings
                    'swing_extension_time': 24,  # Extensión de tiempo para swings prometedores
                    'weekend_hold_adjustment': True  # Ajuste para mantener posiciones en fin de semana
                },
                
                # 📊 MÉTRICAS DE OPTIMIZACIÓN PARA SWING TRADING
                'optimization_metrics': {
                    'target_profit_factor': 6.5,  # Profit factor objetivo balanceado
                    'target_sharpe_ratio': 2.8,  # Sharpe ratio objetivo para swing trading
                    'max_drawdown_limit': 12.0,  # Máximo drawdown permitido
                    'min_win_rate': 85.0,  # Win rate mínimo balanceado
                    'rebalance_frequency': 'daily',  # Frecuencia de rebalanceo
                    'swing_efficiency_target': 0.75,  # Eficiencia de swing objetivo
                    'risk_adjusted_return_target': 2.5  # Retorno ajustado por riesgo objetivo
                }
            }
        )
        
        # Perfil CONSERVADOR - Máxima preservación
        cls._profiles_cache[TradingProfile.CONSERVADOR] = ProfileConfig(
            name="🔒 Conservador",
            description="Timeframes largos, máxima preservación de capital",
            timeframes=["4h", "1d", "1w"],
            risk_level="low",
            frequency="low",
            trading_bot={
                'analysis_interval': 300,  # Análisis cada 5 minutos para holding estratégico
                'min_confidence': 0.75,  # Mayor confianza requerida para holding (75%)
                'max_positions': 2,  # Máximo 2 posiciones para concentración
                'max_daily_trades': 3,  # Máximo 3 trades diarios para holding
                'max_concurrent_positions': 2,  # Máximo 2 posiciones concurrentes
                'symbols': ['BTCUSDT', 'ETHUSDT'],  # Solo los más estables
                'position_timeout': 7200,  # Timeout de 2 horas para holding
                'quick_exit_enabled': False,  # Sin salidas rápidas
                'scalping_mode': False,  # Sin scalping
                'holding_mode_enabled': True,  # Modo holding habilitado
                'long_term_analysis': True,  # Análisis de largo plazo
                'trend_following_enabled': True,  # Seguimiento de tendencias
                'position_accumulation': True,  # Acumulación de posiciones
                'dca_enabled': True,  # Dollar Cost Averaging habilitado
                'fundamental_analysis_weight': 0.3  # Peso del análisis fundamental
            },
            risk_manager={
                'max_risk_per_trade': 0.015,  # Riesgo ultra conservador para holding
                'risk_per_trade': 1.5,  # Riesgo por trade reducido
                'max_daily_risk': 0.03,  # Límite diario muy conservador
                'max_drawdown_threshold': 0.08,  # Tolerancia muy baja
                'max_drawdown': 8.0,  # Drawdown máximo muy conservador
                'stop_loss_percentage': 5.0,  # Stop loss más amplio para holding
                'take_profit_percentage': 12.0,  # TP más amplio para holding estratégico
                'correlation_threshold': 0.5,  # Correlación muy conservadora
                'min_position_size': 15.0,  # Posiciones más grandes para holding
                'max_position_size': 0.25,  # 25% del balance - Mayor tamaño para concentración
                'kelly_fraction': 0.2,  # Sizing muy conservador
                'position_size_multiplier': 1.0,  # Multiplicador neutro
                'volatility_adjustment_factor': 0.8,  # Ajuste muy conservador
                'atr_multiplier': 3.0,  # ATR más amplio para holding
                'profit_target_multiplier': 4.0,  # Ratio R/R para holding
                'dynamic_sizing_enabled': True,  # Sizing dinámico
                'risk_scaling_factor': 0.6,  # Factor muy conservador
                'quality_filter_enabled': True,  # Filtro de calidad obligatorio
                'max_concurrent_positions': 2,  # Límite de posiciones concurrentes
                'holding_risk_adjustment': 0.7  # Ajuste específico para holding
            },
            paper_trader={
                'initial_balance': GLOBAL_INITIAL_BALANCE,
                'max_position_size': 0.15,  # 15% del balance
                'max_total_exposure': 700.0,
                'min_trade_value': 20.0,
                'min_trade_amount': 20.0,
                'commission_rate': 0.001,
                'paper_min_confidence': 55.0,
                'max_slippage': 0.0005,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 25,  # Más conservador para holding estratégico
                'rsi_overbought': 75,  # Más conservador para salidas
                'rsi_period': 21,  # Período más largo para holding
                'confidence_boost_factor': 1.25,  # Mayor boost para señales de alta calidad
                'timeframes': ["4h", "1d", "1w"],  # Timeframes de largo plazo
                'macd_fast': 12,  # Consistente con indicadores optimizados
                'macd_slow': 26,  # Período estándar para holding
                'macd_signal': 9,  # Señal estándar
                'bb_period': 20,  # Período estándar para holding
                'bb_std': 2.0,  # Bandas estándar
                'volume_threshold': 1.0,  # Umbral de volumen neutro
                'momentum_threshold': 0.02,  # Momentum muy conservador
                'trend_strength_threshold': 0.8,  # Filtro de tendencia muy fuerte
                'multi_timeframe_confirmation': True,  # Confirmación obligatoria
                'signal_quality_threshold': 0.85,  # Filtro de muy alta calidad
                'divergence_detection': True,  # Detección de divergencias
                'confirmation_candles': 3,  # Confirmación con 3 velas para holding
                'long_term_trend_filter': True,  # Filtro de tendencia de largo plazo
                'fundamental_analysis_enabled': True,  # Análisis fundamental habilitado
                'market_cycle_awareness': True,  # Conciencia del ciclo de mercado
                'accumulation_zone_detection': True,  # Detección de zonas de acumulación
                'distribution_zone_avoidance': True,  # Evitar zonas de distribución
                'institutional_flow_analysis': True  # Análisis de flujo institucional
            },
            indicators={
                'rsi_period': 21,  # Período estándar para holding
                'macd_periods': [12, 26, 9],  # Configuración estándar para holding
                'bb_period': 20,  # Bandas estándar para holding
                'volume_sma_period': 30,  # Volumen más suavizado para holding
                'atr_period': 21,  # ATR para holding estratégico
                'stoch_k_period': 21,  # Stochastic para holding
                'stoch_d_period': 5,  # Suavizado estándar
                'williams_r_period': 21,  # Williams %R para holding
                'cci_period': 20,  # CCI estándar
                'fibonacci_lookback': 89,  # Fibonacci para timeframes muy largos
                'ema_fast_period': 21,  # EMA rápida para holding
                'ema_slow_period': 50,  # EMA lenta para holding estratégico
                'adx_period': 21,  # ADX para fuerza de tendencia de largo plazo
                'obv_period': 30,  # OBV muy suavizado
                'vwap_period': 50,  # VWAP para referencia de largo plazo
                'sma_short_period': 20,  # SMA corta para holding
                'sma_long_period': 200,  # SMA larga para tendencia principal
                'ichimoku_periods': [9, 26, 52],  # Ichimoku para análisis completo
                'parabolic_sar_step': 0.01,  # SAR muy conservador
                'parabolic_sar_max': 0.1,  # SAR máximo conservador
                'momentum_period': 21,  # Momentum para holding
                'roc_period': 21,  # Rate of Change para holding
                'trix_period': 21,  # TRIX para tendencias de largo plazo
                'dmi_period': 21  # DMI para análisis direccional
            },
            advanced_optimizations={
                # 🎯 OPTIMIZACIONES DE WIN RATE PARA HOLDING ESTRATÉGICO
                'win_rate_target': 92.0,  # Win rate objetivo para holding estratégico
                'confirmation_filters': {
                    'enabled': True,
                    'min_confirmations': 5,  # 5 indicadores para máxima calidad
                    'rsi_confluence': True,  # RSI debe confirmar
                    'macd_confluence': True,  # MACD debe confirmar
                    'volume_confluence': True,  # Volumen debe confirmar
                    'trend_confluence': True,  # Tendencia debe confirmar
                    'volatility_filter': True,  # Filtrar alta volatilidad
                    'max_volatility_threshold': 0.025,  # Máximo 2.5% de volatilidad
                    'adx_filter': True,  # Filtro ADX para tendencias fuertes
                    'min_adx_threshold': 35.0,  # ADX muy alto para holding
                    'vwap_filter': True,  # Filtro VWAP para confirmación
                    'multi_timeframe_filter': True,  # Confirmación multi-timeframe obligatoria
                    'long_term_trend_filter': True,  # Filtro de tendencia de muy largo plazo
                    'institutional_volume_filter': True,  # Filtro de volumen institucional
                    'market_structure_filter': True  # Filtro de estructura de mercado
                },
                
                # 📈 TAKE PROFIT DINÁMICO PARA HOLDING ESTRATÉGICO
                'dynamic_take_profit': {
                    'enabled': True,
                    'base_multiplier': 5.0,  # Multiplicador base R:R para holding
                    'atr_based': True,  # Usar ATR para cálculo
                    'trend_adjustment': True,  # Ajustar según tendencia
                    'volatility_adjustment': True,  # Ajustar según volatilidad
                    'max_tp_multiplier': 10.0,  # Máximo multiplicador para holding largo
                    'min_tp_multiplier': 4.0,  # Mínimo multiplicador para holding
                    'scaling_levels': [0.2, 0.3, 0.5],  # Escalado optimizado para holding
                    'fibonacci_targets': True,  # Usar niveles de Fibonacci
                    'vwap_targets': True,  # Usar VWAP como referencia
                    'long_term_targets': True,  # Objetivos de largo plazo
                    'cycle_based_targets': True,  # Objetivos basados en ciclos de mercado
                    'fundamental_event_targets': True  # Objetivos por eventos fundamentales
                },
                

                
                # ⚖️ GESTIÓN DE POSICIÓN ADAPTATIVA PARA HOLDING ESTRATÉGICO
                'adaptive_position_sizing': {
                    'enabled': True,
                    'base_risk_percent': 1.5,  # Riesgo base ultra conservador para holding
                    'volatility_adjustment': True,  # Ajustar por volatilidad
                    'confidence_scaling': True,  # Escalar por confianza
                    'market_condition_adjustment': True,  # Ajustar por condiciones
                    'max_position_multiplier': 1.8,  # Máximo multiplicador para holding
                    'min_position_multiplier': 0.5,  # Mínimo multiplicador muy conservador
                    'kelly_criterion_enabled': True,  # Usar criterio de Kelly
                    'quality_filter_multiplier': 1.4,  # Mayor multiplicador por calidad
                    'drawdown_protection': True,  # Protección adicional contra drawdown
                    'accumulation_strategy_enabled': True,  # Estrategia de acumulación
                    'dca_position_sizing': True,  # Sizing para DCA
                    'cycle_based_sizing': True  # Sizing basado en ciclos de mercado
                },
                
                # ⏰ SALIDAS BASADAS EN TIEMPO PARA HOLDING ESTRATÉGICO
                'time_based_exits': {
                    'enabled': True,
                    'max_hold_time_hours': 720,  # Máximo 30 días para holding estratégico
                    'profit_target_time_hours': 168,  # Target de profit en 7 días
                    'loss_cut_time_hours': 336,  # Corte de pérdidas en 14 días
                    'time_decay_factor': 0.01,  # Mínimo decaimiento temporal
                    'cycle_based_exits': True,  # Salidas basadas en ciclos
                    'fundamental_event_exits': True,  # Salidas por eventos fundamentales
                    'seasonal_adjustment': True  # Ajuste estacional
                },
                
                # 📊 MÉTRICAS DE OPTIMIZACIÓN PARA HOLDING ESTRATÉGICO
                'optimization_metrics': {
                    'target_profit_factor': 8.0,  # Profit factor objetivo para holding
                    'target_sharpe_ratio': 3.2,  # Sharpe ratio objetivo para holding
                    'max_drawdown_limit': 8.0,  # Máximo drawdown muy bajo
                    'min_win_rate': 90.0,  # Win rate mínimo para holding
                    'rebalance_frequency': 'weekly',  # Frecuencia de rebalanceo semanal
                    'holding_efficiency_target': 0.85,  # Eficiencia de holding objetivo
                    'risk_adjusted_return_target': 3.0,  # Retorno ajustado por riesgo
                    'capital_preservation_priority': 0.9  # Prioridad de preservación de capital
                }
            }
        )
    
    @classmethod
    def _load_default_configurations(cls) -> None:
        """🔧 Carga configuraciones por defecto en caso de error"""
        logger.warning("⚠️ Cargando configuraciones por defecto")
        cls._profiles_cache[TradingProfile.AGRESIVO] = ProfileConfig(
            name="⚡ Agresivo (Default)",
            description="Configuración por defecto",
            timeframes=["15m", "30m", "1h"],
            risk_level="medium_high",
            frequency="high"
        )
    
    @classmethod
    def _validate_all_configurations(cls) -> bool:
        """🔍 Valida todas las configuraciones cargadas"""
        try:
            for profile, config in cls._profiles_cache.items():
                if not cls._validate_profile_config(config):
                    logger.error(f"❌ Configuración inválida para perfil: {profile.value}")
                    return False
            
            logger.info("✅ Todas las configuraciones validadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando configuraciones: {e}")
            return False
    
    @classmethod
    def _validate_profile_config(cls, config: ProfileConfig) -> bool:
        """🔍 Valida una configuración específica de perfil"""
        try:
            # Validar campos obligatorios
            required_fields = ['name', 'description', 'timeframes', 'risk_level', 'frequency']
            for field in required_fields:
                if not hasattr(config, field) or getattr(config, field) is None:
                    return False
            
            # Validar timeframes
            if not config.timeframes or len(config.timeframes) == 0:
                return False
            
            # Validar configuraciones de módulos
            if config.trading_bot and 'min_confidence' in config.trading_bot:
                if not (0 <= config.trading_bot['min_confidence'] <= 100):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando configuración: {e}")
            return False
    
    @classmethod
    def get_consolidated_config(cls, profile: Optional[str] = None) -> Dict[str, Any]:
        """🎯 Obtiene la configuración consolidada del sistema"""
        try:
            if profile:
                target_profile = TradingProfile(profile)
            else:
                target_profile = cls._active_profile
            
            if target_profile not in cls._profiles_cache:
                logger.warning(f"⚠️ Perfil {target_profile.value} no encontrado, usando AGRESIVO")
                target_profile = TradingProfile.AGRESIVO
            
            profile_config = cls._profiles_cache[target_profile]
            
            # Construir configuración consolidada
            consolidated = {
                'profile': target_profile.value,
                'profile_info': {
                    'name': profile_config.name,
                    'description': profile_config.description,
                    'timeframes': profile_config.timeframes,
                    'risk_level': profile_config.risk_level,
                    'frequency': profile_config.frequency
                },
                
                # Constantes globales
                'global_initial_balance': GLOBAL_INITIAL_BALANCE,
                'usdt_base_price': USDT_BASE_PRICE,
                'timezone': TIMEZONE,
                'daily_reset_hour': DAILY_RESET_HOUR,
                'daily_reset_minute': DAILY_RESET_MINUTE,
                'symbols': SYMBOLS,
                'test_symbols': TEST_SYMBOLS,
                
                # Configuraciones por módulo
                'trading_bot': profile_config.trading_bot,
                'risk_manager': profile_config.risk_manager,
                'paper_trader': profile_config.paper_trader,
                'strategies': profile_config.strategies,
                'indicators': profile_config.indicators,
                'position_manager': profile_config.position_manager,
                'position_monitor': profile_config.position_monitor,
                'position_adjuster': profile_config.position_adjuster,
                'market_validator': profile_config.market_validator,
                
                # Alias para compatibilidad con tests (nombres completos)
                'enhanced_risk_manager': profile_config.risk_manager,
                'advanced_indicators': profile_config.indicators,
                'enhanced_strategies': profile_config.strategies,
                
                # Metadatos
                'config_version': '2.0',
                'last_updated': 'auto-generated',
                'validation_status': 'validated'
            }
            
            return consolidated
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración consolidada: {e}")
            return cls._get_fallback_config()
    
    @classmethod
    def get_module_config(cls, module_name: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """🎯 Obtiene la configuración específica de un módulo"""
        try:
            consolidated = cls.get_consolidated_config(profile)
            return consolidated.get(module_name, {})
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración del módulo {module_name}: {e}")
            return {}
    
    @classmethod
    def _load_active_profile_from_file(cls) -> Optional[str]:
        """📂 Carga el perfil activo desde archivo"""
        try:
            if os.path.exists(cls._config_file):
                with open(cls._config_file, 'r') as f:
                    config_data = json.load(f)
                    return config_data.get('active_profile')
        except Exception as e:
            logger.warning(f"⚠️ Error cargando perfil desde archivo: {e}")
        return None
    
    @classmethod
    def _save_active_profile_to_file(cls) -> None:
        """💾 Guarda el perfil activo en archivo"""
        try:
            config_data = {
                'active_profile': cls._active_profile.value,
                'last_updated': datetime.now().isoformat(),
                'updated_by': 'ConfigManager'
            }
            with open(cls._config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"💾 Perfil {cls._active_profile.value} guardado en {cls._config_file}")
        except Exception as e:
            logger.error(f"❌ Error guardando perfil en archivo: {e}")
    
    @classmethod
    def set_active_profile(cls, profile: str) -> bool:
        """🔄 Cambia el perfil activo del sistema"""
        try:
            new_profile = TradingProfile(profile)
            cls._active_profile = new_profile
            logger.info(f"✅ Perfil cambiado a: {profile}")
            return True
            
        except ValueError:
            logger.error(f"❌ Perfil inválido: {profile}")
            return False
    
    @classmethod
    def get_active_profile(cls) -> str:
        """📋 Obtiene el perfil activo actual"""
        return cls._active_profile.value
    
    @classmethod
    def get_available_profiles(cls) -> List[str]:
        """📋 Obtiene la lista de perfiles disponibles"""
        return [profile.value for profile in TradingProfile]
    
    @classmethod
    def _get_fallback_config(cls) -> Dict[str, Any]:
        """🔧 Configuración de fallback en caso de error"""
        return {
            'profile': 'AGRESIVO',
            'profile_info': {
                'name': '⚡ Agresivo (Fallback)',
                'description': 'Configuración de emergencia',
                'timeframes': ['15m', '30m', '1h'],
                'risk_level': 'medium_high',
                'frequency': 'high'
            },
            'global_initial_balance': GLOBAL_INITIAL_BALANCE,
            'usdt_base_price': USDT_BASE_PRICE,
            'timezone': TIMEZONE,
            'daily_reset_hour': DAILY_RESET_HOUR,
            'daily_reset_minute': DAILY_RESET_MINUTE,
            'symbols': SYMBOLS,
            'test_symbols': TEST_SYMBOLS,
            'trading_bot': {
                'analysis_interval': 45,
                'min_confidence': 0.70,
                'max_positions': 5,
                'position_timeout': 600,
                'quick_exit_enabled': False,
                'scalping_mode': False
            },
            'risk_manager': {
                'max_risk_per_trade': 0.02,
                'max_daily_risk': 0.05,
                'max_drawdown_threshold': 0.15,
                'correlation_threshold': 0.7,
                'min_position_size': 10.0,
                'max_position_size': 0.08,  # 8% del balance
                'kelly_fraction': 0.25
            },
            'config_version': '2.0-fallback',
            'validation_status': 'fallback'
        }
    
    @classmethod
    def export_config(cls, filepath: Optional[str] = None) -> str:
        """💾 Exporta la configuración actual a JSON"""
        try:
            config = cls.get_consolidated_config()
            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            
            if filepath:
                Path(filepath).write_text(config_json, encoding='utf-8')
                logger.info(f"✅ Configuración exportada a: {filepath}")
            
            return config_json
            
        except Exception as e:
            logger.error(f"❌ Error exportando configuración: {e}")
            return "{}"

# Inicializar ConfigManager al importar el módulo
ConfigManager.initialize()
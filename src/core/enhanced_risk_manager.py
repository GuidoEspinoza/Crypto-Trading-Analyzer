"""🛡️ Enhanced Risk Manager - Sistema Avanzado de Gestión de Riesgo
Sistema profesional de gestión de riesgo con stop-loss dinámico,
position sizing inteligente y gestión de drawdown.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum

# Importar componentes existentes
from .enhanced_strategies import EnhancedSignal
from src.config.config_manager import ConfigManager

# Inicializar configuración centralizada
try:
    config_manager = ConfigManager()
    config = config_manager.get_consolidated_config()
    if config is None:
        config = {}
except Exception as e:
    # Configuración de fallback en caso de error
    config = {
        'risk_manager': {'max_risk_per_trade': 0.02, 'max_daily_risk': 0.05},
        'trading': {'usdt_base_price': 1.0}
    }

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Niveles de riesgo"""
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    EXTREME = "EXTREME"

@dataclass
class PositionSizing:
    """Información de position sizing"""
    recommended_size: float
    max_position_size: float
    risk_per_trade: float
    position_value: float
    leverage_used: float
    risk_level: RiskLevel
    reasoning: str
    max_risk_amount: float = 0.0  # Cantidad máxima de riesgo

@dataclass
class DynamicStopLoss:
    """Stop loss dinámico"""
    initial_stop: float
    current_stop: float
    trailing_stop: float
    atr_multiplier: float
    stop_type: str  # FIXED, TRAILING, ATR_BASED
    last_update: datetime
    stop_loss_price: float = 0.0  # Precio actual del stop loss
    trailing_distance: float = 0.0  # Distancia del trailing stop

@dataclass
class DynamicTakeProfit:
    """Take profit dinámico y ajustable"""
    initial_tp: float
    current_tp: float
    trailing_tp: float
    tp_increment_pct: float  # Porcentaje de incremento del TP
    tp_type: str  # FIXED, TRAILING, DYNAMIC
    last_update: datetime
    take_profit_price: float = 0.0  # Precio actual del take profit
    confidence_threshold: float = 0.0  # Umbral de confianza para ajustar TP
    max_tp_adjustments: int = 5  # Máximo número de ajustes permitidos (se inicializa desde config)
    adjustments_made: int = 0  # Número de ajustes realizados

@dataclass
class EnhancedRiskAssessment:
    """Evaluación de riesgo mejorada"""
    overall_risk_score: float
    risk_level: RiskLevel
    position_sizing: PositionSizing
    dynamic_stop_loss: DynamicStopLoss
    dynamic_take_profit: DynamicTakeProfit
    market_risk_factors: Dict
    portfolio_risk_metrics: Dict
    recommendations: List[str]
    max_drawdown_alert: bool
    correlation_risk: float
    volatility_risk: float
    liquidity_risk: float
    is_approved: bool = True  # Si el trade está aprobado para ejecutar

class EnhancedRiskManager:
    """🛡️ Gestor de Riesgo Avanzado"""
    
    def __init__(self):
        # Configuración de riesgo desde configuración centralizada
        self.max_portfolio_risk = config.get("risk_manager", {}).get("max_risk_per_trade", 2.0) / 100  # Convertir de % a decimal
        self.max_daily_risk = config.get("risk_manager", {}).get("max_daily_risk", 5.0) / 100  # Convertir de % a decimal
        self.max_drawdown_threshold = config.get("risk_manager", {}).get("max_drawdown_threshold", 10.0) / 100  # Convertir de % a decimal
        self.correlation_threshold = config.get("risk_manager", {}).get("correlation_threshold", 0.7)
        
        # Position sizing profesional desde configuración centralizada
        self.min_position_size = config.get("risk_manager", {}).get("min_position_size", 10.0)
        self.max_position_size = config.get("risk_manager", {}).get("max_position_size", 20.0) / 100  # Convertir de % a decimal
        self.kelly_fraction = config.get("risk_manager", {}).get("kelly_fraction", 0.25)
        self.volatility_adjustment = True  # Ajustar tamaño según volatilidad
        
        # Stop loss dinámico profesional con valores por defecto
        self.atr_multiplier_range = (1.5, 3.0)  # Rango de multiplicadores ATR
        self.trailing_stop_activation = 0.02  # 2% de ganancia para activar trailing stop
        self.breakeven_stop_threshold = 0.01  # 1% para mover stop a breakeven
        
        # Configuración adicional con valores por defecto
        self.min_trailing_distance = 0.005
        self.max_trailing_distance = 0.05
        
        # Métricas de portfolio con valor por defecto
        self.portfolio_value = 1000.0  # Valor inicial del portfolio
        self.current_drawdown = 0.0
        self.max_historical_drawdown = 0.0
        self.daily_pnl = 0.0
        self.open_positions = {}
        self.trade_history = []
        
    def assess_trade_risk(self, signal: EnhancedSignal, current_portfolio_value: float) -> EnhancedRiskAssessment:
        """Evaluar riesgo de un trade específico"""
        try:
            self.portfolio_value = current_portfolio_value
            
            # Análisis de factores de riesgo del mercado
            market_risk = self._analyze_market_risk_factors(signal)
            
            # Calcular position sizing
            position_sizing = self._calculate_position_sizing(signal, market_risk)
            
            # Configurar stop loss dinámico
            dynamic_stop = self._configure_dynamic_stop_loss(signal)
            
            # Configurar take profit dinámico
            dynamic_tp = self._configure_dynamic_take_profit(signal)
            
            # Métricas de riesgo del portfolio
            portfolio_metrics = self._calculate_portfolio_risk_metrics()
            
            # Calcular score de riesgo general
            overall_risk_score = self._calculate_overall_risk_score(
                signal, market_risk, portfolio_metrics
            )
            
            # Determinar nivel de riesgo
            risk_level = self._determine_risk_level(overall_risk_score)
            
            # Generar recomendaciones
            recommendations = self._generate_risk_recommendations(
                signal, market_risk, portfolio_metrics, risk_level
            )
            
            # Alertas de drawdown
            max_dd_alert = self.current_drawdown >= self.max_drawdown_threshold
            
            # Determinar si el trade está aprobado
            min_confidence = 65.0  # Umbral mínimo de confianza por defecto
            is_approved = (
                risk_level not in [RiskLevel.EXTREME, RiskLevel.VERY_HIGH] and
                not max_dd_alert and
                signal.confidence_score >= min_confidence
            )
            
            return EnhancedRiskAssessment(
                overall_risk_score=round(overall_risk_score, 2),
                risk_level=risk_level,
                position_sizing=position_sizing,
                dynamic_stop_loss=dynamic_stop,
                dynamic_take_profit=dynamic_tp,
                market_risk_factors=market_risk,
                portfolio_risk_metrics=portfolio_metrics,
                recommendations=recommendations,
                max_drawdown_alert=max_dd_alert,
                correlation_risk=market_risk.get("correlation_risk", 0.0),
                volatility_risk=market_risk.get("volatility_risk", 0.0),
                liquidity_risk=market_risk.get("liquidity_risk", 0.0),
                is_approved=is_approved
            )
            
        except Exception as e:
            logger.error(f"Error assessing trade risk: {e}")
            return self._create_default_risk_assessment(signal)
    
    def _analyze_market_risk_factors(self, signal: EnhancedSignal) -> Dict:
        """Analizar factores de riesgo del mercado"""
        try:
            risk_factors = {
                "volatility_risk": 0.0,
                "liquidity_risk": 0.0,
                "correlation_risk": 0.0,
                "market_regime_risk": 0.0,
                "confidence_risk": 0.0
            }
            
            # Riesgo de volatilidad con factor por defecto
            volatility_factor = 1.2  # Factor de ajuste de volatilidad por defecto
            
            if signal.market_regime == "VOLATILE":
                risk_factors["volatility_risk"] = min(0.8 * volatility_factor, 1.0)
            elif signal.market_regime == "RANGING":
                risk_factors["volatility_risk"] = min(0.3 * volatility_factor, 1.0)
            else:
                risk_factors["volatility_risk"] = min(0.5 * volatility_factor, 1.0)
            
            # Riesgo de liquidez (basado en volumen)
            # Verificar que indicators_data no sea None
            indicators_data = signal.indicators_data if signal.indicators_data is not None else {}
            volume_data = indicators_data.get("volume_analysis", {})
            if volume_data.get("volume_confirmation", False):
                risk_factors["liquidity_risk"] = 0.2
            else:
                risk_factors["liquidity_risk"] = 0.6
            
            # Riesgo de correlación (simplificado)
            # En un sistema real, calcularíamos correlación con otras posiciones
            risk_factors["correlation_risk"] = 0.3
            
            # Riesgo por régimen de mercado
            if signal.market_regime == "TRENDING":
                risk_factors["market_regime_risk"] = 0.2
            elif signal.market_regime == "RANGING":
                risk_factors["market_regime_risk"] = 0.4
            else:  # VOLATILE
                risk_factors["market_regime_risk"] = 0.8
            
            # Riesgo por confianza de la señal
            confidence_risk = max(0, (100 - signal.confidence_score) / 100)
            risk_factors["confidence_risk"] = confidence_risk
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error analyzing market risk factors: {e}")
            return {"volatility_risk": 0.5, "liquidity_risk": 0.5, "correlation_risk": 0.5,
                   "market_regime_risk": 0.5, "confidence_risk": 0.5}
    
    def _calculate_position_sizing(self, signal: EnhancedSignal, market_risk: Dict) -> PositionSizing:
        """Calcular tamaño de posición usando múltiples métodos"""
        try:
            # Método 1: Riesgo fijo por trade
            risk_per_trade = self.portfolio_value * self.max_portfolio_risk
            
            # Calcular distancia al stop loss
            if signal.stop_loss_price > 0:
                stop_distance = abs(signal.price - signal.stop_loss_price)
                if stop_distance > 0:
                    fixed_risk_size = risk_per_trade / stop_distance
                else:
                    fixed_risk_size = self.min_position_size
            else:
                fixed_risk_size = self.min_position_size
            
            # Método 2: Kelly Criterion (simplificado)
            win_rate = 0.6  # Tasa de ganancia por defecto
            avg_win = signal.risk_reward_ratio if signal.risk_reward_ratio > 0 else 1.5
            avg_loss = 1.0  # Pérdida promedio por defecto
            
            kelly_f = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_size = max(0, kelly_f * self.kelly_fraction * self.portfolio_value)
            
            # Método 3: Ajuste por volatilidad
            volatility_multiplier = 1.0 - market_risk.get("volatility_risk", 0.5)
            volatility_adjusted_size = fixed_risk_size * volatility_multiplier
            
            # Tomar el menor de los tamaños calculados
            recommended_size = min(fixed_risk_size, kelly_size, volatility_adjusted_size)
            
            # Aplicar límites
            max_position_value = self.portfolio_value * self.max_position_size
            recommended_size = max(self.min_position_size, 
                                 min(recommended_size, max_position_value))
            
            # Determinar nivel de riesgo
            position_risk_ratio = recommended_size / self.portfolio_value
            if position_risk_ratio <= 0.01:
                risk_level = RiskLevel.VERY_LOW
            elif position_risk_ratio <= 0.02:
                risk_level = RiskLevel.LOW
            elif position_risk_ratio <= 0.05:
                risk_level = RiskLevel.MODERATE
            elif position_risk_ratio <= 0.08:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.VERY_HIGH
            
            # Reasoning
            reasoning = f"Fixed risk: ${fixed_risk_size:.2f}, Kelly: ${kelly_size:.2f}, " \
                       f"Vol adjusted: ${volatility_adjusted_size:.2f}"
            
            return PositionSizing(
                recommended_size=round(recommended_size, 2),
                max_position_size=round(max_position_value, 2),
                risk_per_trade=round(risk_per_trade, 2),
                position_value=round(recommended_size, 2),
                leverage_used=1.0,  # Default leverage (replaced profile reference)
                risk_level=risk_level,
                reasoning=reasoning,
                max_risk_amount=round(risk_per_trade, 2)
            )
            
        except Exception as e:
            logger.error(f"Error calculating position sizing: {e}")
            return PositionSizing(
                recommended_size=self.min_position_size,
                max_position_size=self.portfolio_value * 0.01,
                risk_per_trade=self.portfolio_value * 0.01,
                position_value=self.min_position_size,
                leverage_used=1.0,  # Default leverage (replaced profile reference)
                risk_level=RiskLevel.LOW,
                reasoning="Error in calculation - using minimum size",
                max_risk_amount=round(self.portfolio_value * 0.01, 2)
            )
    
    def _configure_dynamic_stop_loss(self, signal: EnhancedSignal) -> DynamicStopLoss:
        """Configurar stop loss dinámico"""
        try:
            # Stop loss inicial (del signal)
            initial_stop = signal.stop_loss_price
            
            # Si no hay stop loss en el signal, calcularlo
            if initial_stop == 0:
                # Verificar que indicators_data no sea None
                indicators_data = signal.indicators_data if signal.indicators_data is not None else {}
                atr_data = indicators_data.get("atr", signal.price * 0.02)
                if signal.signal_type == "BUY":
                    initial_stop = signal.price - (2 * atr_data)
                else:
                    initial_stop = signal.price + (2 * atr_data)
            
            # Configurar trailing stop
            atr_multiplier = 2.0  # Multiplicador ATR por defecto
            
            # Ajustar multiplicador según volatilidad
            if signal.market_regime == "VOLATILE":
                atr_multiplier = 2.5  # Más espacio en mercados volátiles
            elif signal.market_regime == "RANGING":
                atr_multiplier = 1.5  # Menos espacio en mercados laterales
            
            # Evitar división por cero
            if signal.price > 0:
                trailing_distance = abs(signal.price - initial_stop) / signal.price * 100
            else:
                trailing_distance = 2.0  # Distancia de trailing por defecto
            return DynamicStopLoss(
                initial_stop=round(initial_stop, 2),
                current_stop=round(initial_stop, 2),
                trailing_stop=round(initial_stop, 2),
                atr_multiplier=atr_multiplier,
                stop_type="ATR_BASED",
                last_update=datetime.now(),
                stop_loss_price=round(initial_stop, 2),
                trailing_distance=round(trailing_distance, 2)
            )
            
        except Exception as e:
            logger.error(f"Error configuring dynamic stop loss: {e}")
            stop_price = signal.price * 0.95 if signal.signal_type == "BUY" else signal.price * 1.05
            trailing_distance = abs(signal.price - stop_price) / signal.price * 100
            return DynamicStopLoss(
                initial_stop=stop_price,
                current_stop=stop_price,
                trailing_stop=stop_price,
                atr_multiplier=2.0,  # Multiplicador ATR por defecto
                stop_type="FIXED",
                last_update=datetime.now(),
                stop_loss_price=stop_price,
                trailing_distance=round(trailing_distance, 2)
            )
    
    def _configure_dynamic_take_profit(self, signal: EnhancedSignal) -> DynamicTakeProfit:
        """🎯 Configurar take profit dinámico y ajustable con optimizaciones avanzadas"""
        try:
            # Obtener configuración de optimizaciones avanzadas
            from src.config.config_manager import ConfigManager
            config = ConfigManager().get_consolidated_config()
            advanced_opts = config.get("advanced_optimizations", {})
            
            # Configuración de take profit dinámico
            tp_config = advanced_opts.get("dynamic_take_profit", {
                "enabled": True,
                "base_multiplier": 2.5,
                "volatility_adjustment": True,
                "momentum_extension": True,
                "partial_profit_levels": [
                    {"percentage": 30, "at_ratio": 1.5},
                    {"percentage": 40, "at_ratio": 2.5},
                    {"percentage": 30, "trailing": True}
                ]
            })
            
            # Take profit inicial (del signal)
            initial_tp = signal.take_profit_price
            
            # Si no hay take profit en el signal, calcularlo con optimizaciones
            if initial_tp == 0:
                indicators_data = signal.indicators_data if signal.indicators_data is not None else {}
                atr_data = indicators_data.get("atr", signal.price * 0.02)
                
                # Usar multiplicador base desde configuración
                base_multiplier = tp_config.get("base_multiplier", 2.5)
                
                # Ajustar multiplicador según win rate
                win_rate_config = advanced_opts.get("win_rate_optimization", {})
                target_win_rate = win_rate_config.get("target_win_rate", 65.0)
                
                # Ajuste dinámico basado en win rate objetivo
                if target_win_rate >= 70:
                    base_multiplier *= 0.9  # TP más conservador para mayor win rate
                elif target_win_rate <= 55:
                    base_multiplier *= 1.2  # TP más agresivo para menor win rate
                
                if signal.signal_type == "BUY":
                    initial_tp = signal.price + (base_multiplier * atr_data)
                else:
                    initial_tp = signal.price - (base_multiplier * atr_data)
            
            # Configurar parámetros del trailing TP con optimizaciones avanzadas
            tp_increment_pct = tp_config.get("base_multiplier", 2.5) * 0.4  # 40% del multiplicador base
            confidence_threshold = 75.0
            
            # Ajustar según régimen de mercado y volatilidad
            if tp_config.get("volatility_adjustment", True):
                if signal.market_regime == "TRENDING":
                    tp_increment_pct *= 1.3  # Más agresivo en tendencias
                    confidence_threshold = max(65.0, confidence_threshold - 10)
                elif signal.market_regime == "VOLATILE":
                    tp_increment_pct *= 0.7  # Más conservador en volatilidad
                    confidence_threshold = min(85.0, confidence_threshold + 10)
                elif signal.market_regime == "RANGING":
                    tp_increment_pct *= 0.8  # Conservador en rangos
                    confidence_threshold = min(80.0, confidence_threshold + 5)
            
            # Ajustar según momentum si está habilitado
            if tp_config.get("momentum_extension", True):
                momentum_strength = getattr(signal, 'momentum_strength', 0.5)
                if momentum_strength > 0.7:
                    tp_increment_pct *= 1.2  # Extender TP con momentum fuerte
                elif momentum_strength < 0.3:
                    tp_increment_pct *= 0.9  # Reducir TP con momentum débil
            
            # Configurar máximo de ajustes basado en gestión adaptativa
            adaptive_config = advanced_opts.get("adaptive_position_management", {})
            max_adjustments = adaptive_config.get("max_tp_adjustments", 5)
            
            # Determinar tipo de TP basado en configuración
            tp_type = "DYNAMIC"
            if tp_config.get("partial_profit_levels"):
                tp_type = "PARTIAL_DYNAMIC"
            
            return DynamicTakeProfit(
                initial_tp=round(initial_tp, 2),
                current_tp=round(initial_tp, 2),
                trailing_tp=round(initial_tp, 2),
                tp_increment_pct=round(tp_increment_pct, 3),
                tp_type=tp_type,
                last_update=datetime.now(),
                take_profit_price=round(initial_tp, 2),
                confidence_threshold=confidence_threshold / 100.0,  # Convertir a decimal
                max_tp_adjustments=max_adjustments,
                adjustments_made=0
            )
            
        except Exception as e:
            logger.error(f"Error configuring dynamic take profit: {e}")
            # Fallback seguro con valores por defecto
            tp_price = signal.price * 1.06 if signal.signal_type == "BUY" else signal.price * 0.94
            return DynamicTakeProfit(
                initial_tp=tp_price,
                current_tp=tp_price,
                trailing_tp=tp_price,
                tp_increment_pct=1.0,
                tp_type="FIXED",
                last_update=datetime.now(),
                take_profit_price=tp_price,
                confidence_threshold=0.7,
                max_tp_adjustments=3,
                adjustments_made=0
            )
    
    def calculate_partial_profit_levels(self, entry_price: float, signal_type: str, 
                                      position_size: float, atr: float) -> List[Dict[str, Any]]:
        """💰 Calcular niveles de toma de ganancias parciales optimizados
        
        Args:
            entry_price: Precio de entrada de la posición
            signal_type: Tipo de señal (BUY/SELL)
            position_size: Tamaño de la posición
            atr: Average True Range para cálculos dinámicos
            
        Returns:
            Lista de niveles de toma de ganancias parciales
        """
        try:
            # Obtener configuración de optimizaciones avanzadas
            from src.config.config_manager import ConfigManager
            config = ConfigManager().get_consolidated_config()
            advanced_opts = config.get("advanced_optimizations", {})
            
            # Configuración de take profit dinámico
            tp_config = advanced_opts.get("dynamic_take_profit", {})
            partial_levels = tp_config.get("partial_profit_levels", [
                {"percentage": 30, "at_ratio": 1.5},
                {"percentage": 40, "at_ratio": 2.5},
                {"percentage": 30, "trailing": True}
            ])
            
            profit_levels = []
            remaining_size = position_size
            
            for i, level in enumerate(partial_levels):
                # Calcular tamaño de esta toma parcial
                if level.get("trailing", False):
                    # El último nivel usa el tamaño restante
                    level_size = remaining_size
                else:
                    level_size = position_size * (level["percentage"] / 100.0)
                    remaining_size -= level_size
                
                # Calcular precio objetivo
                if level.get("trailing", False):
                    # Para trailing, usar precio inicial más conservador
                    ratio = 2.0  # Ratio base para trailing
                    price_target = None  # Se calculará dinámicamente
                    level_type = "TRAILING"
                else:
                    ratio = level["at_ratio"]
                    # Calcular precio objetivo basado en ATR y ratio
                    atr_distance = atr * ratio
                    
                    if signal_type == "BUY":
                        price_target = entry_price + atr_distance
                    else:  # SELL
                        price_target = entry_price - atr_distance
                    
                    level_type = "FIXED"
                
                # Calcular ganancia esperada
                if price_target:
                    if signal_type == "BUY":
                        expected_profit = (price_target - entry_price) * level_size
                        profit_percentage = ((price_target - entry_price) / entry_price) * 100
                    else:  # SELL
                        expected_profit = (entry_price - price_target) * level_size
                        profit_percentage = ((entry_price - price_target) / entry_price) * 100
                else:
                    expected_profit = 0.0
                    profit_percentage = 0.0
                
                profit_level = {
                    "level": i + 1,
                    "type": level_type,
                    "percentage_of_position": level["percentage"] if not level.get("trailing") else 
                                           round((level_size / position_size) * 100, 1),
                    "position_size": round(level_size, 6),
                    "target_price": round(price_target, 4) if price_target else None,
                    "risk_reward_ratio": ratio,
                    "expected_profit": round(expected_profit, 2),
                    "profit_percentage": round(profit_percentage, 2),
                    "is_trailing": level.get("trailing", False),
                    "status": "PENDING",
                    "executed_at": None,
                    "actual_price": None
                }
                
                profit_levels.append(profit_level)
            
            return profit_levels
            
        except Exception as e:
            logger.error(f"Error calculating partial profit levels: {e}")
            # Fallback: niveles básicos
            basic_size = position_size / 3
            basic_atr_distance = atr * 2.0
            
            if signal_type == "BUY":
                basic_target = entry_price + basic_atr_distance
            else:
                basic_target = entry_price - basic_atr_distance
            
            return [
                {
                    "level": 1,
                    "type": "FIXED",
                    "percentage_of_position": 33.3,
                    "position_size": basic_size,
                    "target_price": basic_target,
                    "risk_reward_ratio": 2.0,
                    "expected_profit": 0.0,
                    "profit_percentage": 0.0,
                    "is_trailing": False,
                    "status": "PENDING",
                    "executed_at": None,
                    "actual_price": None
                }
            ]
    
    def _calculate_portfolio_risk_metrics(self) -> Dict:
        """Calcular métricas de riesgo del portfolio"""
        try:
            return {
                "current_drawdown": round(self.current_drawdown, 4),
                "max_historical_drawdown": round(self.max_historical_drawdown, 4),
                "daily_pnl": round(self.daily_pnl, 2),
                "portfolio_value": round(self.portfolio_value, 2),
                "open_positions_count": len(self.open_positions),
                "portfolio_utilization": round(sum(pos.get("size", 0) for pos in self.open_positions.values()) / self.portfolio_value, 4),
                "risk_budget_used": round(len(self.open_positions) * self.max_portfolio_risk, 4)
            }
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {
                "current_drawdown": 0.0,
                "max_historical_drawdown": 0.0,
                "daily_pnl": 0.0,
                "portfolio_value": self.portfolio_value,
                "open_positions_count": 0,
                "portfolio_utilization": 0.0,
                "risk_budget_used": 0.0
            }
    
    def _calculate_overall_risk_score(self, signal: EnhancedSignal, market_risk: Dict, portfolio_metrics: Dict) -> float:
        """Calcular score general de riesgo (0-100)"""
        try:
            # Pesos para cada factor
            weights = {
                "confidence": 0.25,
                "market_volatility": 0.20,
                "portfolio_drawdown": 0.20,
                "liquidity": 0.15,
                "correlation": 0.10,
                "market_regime": 0.10
            }
            
            # Scores individuales (0-100, donde 100 = máximo riesgo)
            confidence_risk = max(0, 100 - signal.confidence_score)
            volatility_risk = market_risk.get("volatility_risk", 0.5) * 100
            drawdown_risk = min(100, portfolio_metrics.get("current_drawdown", 0) * 500)  # Escalar drawdown
            liquidity_risk = market_risk.get("liquidity_risk", 0.5) * 100
            correlation_risk = market_risk.get("correlation_risk", 0.5) * 100
            regime_risk = market_risk.get("market_regime_risk", 0.5) * 100
            
            # Score ponderado
            overall_score = (
                confidence_risk * weights["confidence"] +
                volatility_risk * weights["market_volatility"] +
                drawdown_risk * weights["portfolio_drawdown"] +
                liquidity_risk * weights["liquidity"] +
                correlation_risk * weights["correlation"] +
                regime_risk * weights["market_regime"]
            )
            
            return min(100, max(0, overall_score))
            
        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            return 50.0  # Riesgo medio por defecto
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determinar nivel de riesgo basado en el score"""
        if risk_score <= 20:
            return RiskLevel.VERY_LOW
        elif risk_score <= 40:
            return RiskLevel.LOW
        elif risk_score <= 60:
            return RiskLevel.MODERATE
        elif risk_score <= 80:
            return RiskLevel.HIGH
        elif risk_score <= 95:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.EXTREME
    
    def _generate_risk_recommendations(self, signal: EnhancedSignal, market_risk: Dict, 
                                     portfolio_metrics: Dict, risk_level: RiskLevel) -> List[str]:
        """Generar recomendaciones de gestión de riesgo"""
        recommendations = []
        
        try:
            # Recomendaciones por nivel de riesgo
            if risk_level == RiskLevel.EXTREME:
                recommendations.append("🚨 RIESGO EXTREMO - NO OPERAR")
                recommendations.append("Esperar mejores condiciones de mercado")
            elif risk_level == RiskLevel.VERY_HIGH:
                recommendations.append("⚠️ Riesgo muy alto - Reducir tamaño de posición 50%")
                recommendations.append("Usar stop loss más ajustado")
            elif risk_level == RiskLevel.HIGH:
                recommendations.append("⚠️ Riesgo alto - Monitorear de cerca")
                recommendations.append("Considerar reducir exposición")
            
            # Recomendaciones específicas
            if signal.confidence_score < 60:
                recommendations.append("Baja confianza en señal - Reducir tamaño")
            
            if market_risk.get("volatility_risk", 0) > 0.7:
                recommendations.append("Alta volatilidad - Usar stops más amplios")
            
            if not signal.volume_confirmation:
                recommendations.append("Sin confirmación de volumen - Precaución")
            
            if portfolio_metrics.get("current_drawdown", 0) > 0.1:
                recommendations.append("Drawdown alto - Considerar pausa en trading")
            
            if signal.risk_reward_ratio < 2.0:
                recommendations.append("Ratio riesgo/beneficio bajo - Buscar mejor entrada")
            
            # Si no hay recomendaciones específicas
            if not recommendations and risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW]:
                recommendations.append("✅ Condiciones favorables para operar")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generando recomendaciones - Revisar manualmente"]
    
    def _create_default_risk_assessment(self, signal: EnhancedSignal) -> EnhancedRiskAssessment:
        """Crear evaluación de riesgo por defecto en caso de error"""
        default_stop_price = signal.price * 0.95 if signal.signal_type == "BUY" else signal.price * 1.05
        default_tp_price = signal.price * 1.06 if signal.signal_type == "BUY" else signal.price * 0.94
        default_trailing_distance = abs(signal.price - default_stop_price) / signal.price * 100
        return EnhancedRiskAssessment(
            overall_risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            position_sizing=PositionSizing(
                recommended_size=self.min_position_size,
                max_position_size=self.portfolio_value * 0.01,
                risk_per_trade=self.portfolio_value * 0.01,
                position_value=self.min_position_size,
                leverage_used=1.0,  # Apalancamiento por defecto
                risk_level=RiskLevel.HIGH,
                reasoning="Error in calculation - using conservative defaults",
                max_risk_amount=round(self.portfolio_value * 0.01, 2)
            ),
            dynamic_stop_loss=DynamicStopLoss(
                initial_stop=default_stop_price,
                current_stop=default_stop_price,
                trailing_stop=default_stop_price,
                atr_multiplier=2.0,
                stop_type="FIXED",
                last_update=datetime.now(),
                stop_loss_price=default_stop_price,
                trailing_distance=round(default_trailing_distance, 2)
            ),
            dynamic_take_profit=DynamicTakeProfit(
                initial_tp=default_tp_price,
                current_tp=default_tp_price,
                trailing_tp=default_tp_price,
                tp_increment_pct=1.0,  # Default TP increment (replaced profile reference)
                tp_type="FIXED",
                last_update=datetime.now(),
                take_profit_price=default_tp_price,
                confidence_threshold=0.7,  # Default confidence threshold
                max_tp_adjustments=3,  # Default max TP adjustments
                adjustments_made=0
            ),
            market_risk_factors={"error": "Could not calculate risk factors"},
            portfolio_risk_metrics={"error": "Could not calculate portfolio metrics"},
            recommendations=["Error en análisis de riesgo - Revisar manualmente"],
            max_drawdown_alert=True,
            correlation_risk=0.5,
            volatility_risk=0.8,
            liquidity_risk=0.6,
            is_approved=False  # No aprobar trades en caso de error
        )
    
    def update_position(self, symbol: str, current_price: float, position_data: Dict):
        """Actualizar posición existente y ajustar stop loss dinámico inteligente"""
        try:
            if symbol in self.open_positions:
                position = self.open_positions[symbol]
                
                # Obtener datos de mercado actuales para análisis avanzado
                market_data = self._get_current_market_data(symbol, current_price)
                
                # Actualizar stop loss trailing inteligente
                updated_stop = self._update_intelligent_trailing_stop(
                    position, current_price, market_data
                )
                
                if updated_stop:
                    position["current_stop"] = updated_stop["new_stop"]
                    position["stop_type"] = updated_stop["stop_type"]
                    position["trailing_reason"] = updated_stop["reason"]
                    logger.info(f"Updated intelligent trailing stop for {symbol}: {updated_stop['new_stop']} - {updated_stop['reason']}")
                
                # Actualizar métricas de la posición
                position["current_price"] = current_price
                position["unrealized_pnl"] = self._calculate_unrealized_pnl(position, current_price)
                position["last_update"] = datetime.now()
                
                # Evaluar si necesita ajuste de position sizing dinámico
                self._evaluate_dynamic_position_sizing(position, market_data)
                
        except Exception as e:
            logger.error(f"Error updating position for {symbol}: {e}")
    
    def _get_current_market_data(self, symbol: str, current_price: float) -> Dict:
        """Obtener datos de mercado actuales para análisis avanzado"""
        try:
            # Simular datos de mercado (en implementación real, obtener de exchange)
            # Usar valores por defecto para simulación
            default_volatility = 0.02
            default_volume_ratio = 1.5
            default_trend_strength = 0.7
            support_resistance_pct = 2.0 / 100
            default_momentum = 0.6
            
            return {
                "volatility": default_volatility,
                "volume_ratio": default_volume_ratio,
                "trend_strength": default_trend_strength,
                "support_distance": abs(current_price - (current_price * (1 - support_resistance_pct))) / current_price,
                "resistance_distance": abs((current_price * (1 + support_resistance_pct)) - current_price) / current_price,
                "momentum": default_momentum
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {"volatility": 0.02, "volume_ratio": 1.0, "trend_strength": 0.5, 
                   "support_distance": 0.02, "resistance_distance": 0.02, "momentum": 0.5}
    
    def _update_intelligent_trailing_stop(self, position: Dict, current_price: float, market_data: Dict) -> Dict:
        """Actualizar trailing stop usando lógica inteligente optimizada
        
        Implementa trailing stop adaptativo basado en:
        - Configuraciones dinámicas del ConfigManager
        - Análisis de volatilidad y momentum
        - Win rate histórico y condiciones de mercado
        - Gestión de riesgo adaptativa
        """
        try:
            # Obtener configuraciones optimizadas
            config = ConfigManager.get_module_config('risk_manager')
            trailing_config = config.get('trailing_stop', {})
            
            signal_type = position.get("signal_type")
            entry_price = position.get("entry_price", 0)
            current_stop = position.get("current_stop", 0)
            symbol = position.get("symbol", "")
            
            # Configuración base optimizada
            base_activation = trailing_config.get('activation_threshold', 0.015)  # 1.5%
            base_distance = trailing_config.get('base_distance', 0.008)  # 0.8%
            atr_multiplier = trailing_config.get('atr_multiplier', 1.8)
            
            # Calcular ganancia actual
            if signal_type == "BUY":
                profit_pct = (current_price - entry_price) / entry_price
                
                # Activación dinámica basada en condiciones de mercado
                activation_threshold = self._calculate_dynamic_activation_threshold(
                    base_activation, market_data, trailing_config
                )
                
                if profit_pct >= activation_threshold:
                    # Calcular distancia optimizada
                    trailing_distance = self._calculate_optimized_trailing_distance(
                        base_distance, atr_multiplier, market_data, profit_pct, trailing_config
                    )
                    
                    # Calcular nuevo stop con protección de ganancias
                    new_stop = current_price * (1 - trailing_distance)
                    
                    # Aplicar protección mínima de ganancias
                    min_profit_protection = trailing_config.get('min_profit_protection', 0.005)  # 0.5%
                    min_protected_stop = entry_price * (1 + min_profit_protection)
                    new_stop = max(new_stop, min_protected_stop)
                    
                    # Solo actualizar si es mejor que el stop actual
                    if new_stop > current_stop:
                        return {
                            "new_stop": round(new_stop, 6),
                            "stop_type": "INTELLIGENT_TRAILING_OPTIMIZED",
                            "reason": f"Profit:{profit_pct:.3f}, Dist:{trailing_distance:.4f}, Protected:{min_protected_stop:.6f}",
                            "activation_threshold": activation_threshold,
                            "trailing_distance": trailing_distance
                        }
            
            elif signal_type == "SELL":
                profit_pct = (entry_price - current_price) / entry_price
                
                activation_threshold = self._calculate_dynamic_activation_threshold(
                    base_activation, market_data, trailing_config
                )
                
                if profit_pct >= activation_threshold:
                    trailing_distance = self._calculate_optimized_trailing_distance(
                        base_distance, atr_multiplier, market_data, profit_pct, trailing_config
                    )
                    
                    new_stop = current_price * (1 + trailing_distance)
                    
                    # Protección mínima para shorts
                    min_profit_protection = trailing_config.get('min_profit_protection', 0.005)
                    max_protected_stop = entry_price * (1 - min_profit_protection)
                    new_stop = min(new_stop, max_protected_stop)
                    
                    if new_stop < current_stop:
                        return {
                            "new_stop": round(new_stop, 6),
                            "stop_type": "INTELLIGENT_TRAILING_OPTIMIZED",
                            "reason": f"Profit:{profit_pct:.3f}, Dist:{trailing_distance:.4f}, Protected:{max_protected_stop:.6f}",
                            "activation_threshold": activation_threshold,
                            "trailing_distance": trailing_distance
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating intelligent trailing stop: {e}")
            return None
    
    def _calculate_dynamic_activation_threshold(self, base_threshold: float, market_data: Dict, config: Dict) -> float:
        """Calcular umbral de activación dinámico basado en condiciones de mercado"""
        try:
            # Ajustes basados en volatilidad
            volatility = market_data.get("volatility", 0.02)
            volatility_adjustment = config.get('volatility_adjustment', 0.3)
            
            # Ajustes basados en momentum
            momentum = market_data.get("momentum", 0.5)
            momentum_adjustment = config.get('momentum_adjustment', 0.2)
            
            # Ajustes basados en volumen
            volume_ratio = market_data.get("volume_ratio", 1.0)
            volume_adjustment = config.get('volume_adjustment', 0.1)
            
            # Calcular threshold dinámico
            volatility_factor = 1 + (volatility - 0.02) * volatility_adjustment
            momentum_factor = 1 - abs(momentum - 0.5) * momentum_adjustment
            volume_factor = 1 + (volume_ratio - 1.0) * volume_adjustment
            
            dynamic_threshold = base_threshold * volatility_factor * momentum_factor * volume_factor
            
            # Límites de seguridad
            min_threshold = config.get('min_activation_threshold', 0.008)  # 0.8%
            max_threshold = config.get('max_activation_threshold', 0.025)  # 2.5%
            
            return max(min_threshold, min(max_threshold, dynamic_threshold))
            
        except Exception as e:
            logger.error(f"Error calculating dynamic activation threshold: {e}")
            return base_threshold
    
    def _calculate_optimized_trailing_distance(self, base_distance: float, atr_multiplier: float, 
                                             market_data: Dict, profit_pct: float, config: Dict) -> float:
        """Calcular distancia de trailing optimizada"""
        try:
            # Obtener métricas de mercado
            volatility = market_data.get("volatility", 0.02)
            momentum = market_data.get("momentum", 0.5)
            trend_strength = market_data.get("trend_strength", 0.5)
            volume_ratio = market_data.get("volume_ratio", 1.0)
            
            # Ajuste base por volatilidad (más espacio en alta volatilidad)
            volatility_multiplier = config.get('volatility_multiplier', 1.5)
            volatility_factor = 1 + (volatility - 0.02) * volatility_multiplier
            
            # Ajuste por momentum (menos espacio con momentum fuerte)
            momentum_multiplier = config.get('momentum_multiplier', 0.8)
            momentum_factor = 1 - abs(momentum - 0.5) * momentum_multiplier
            
            # Ajuste por fuerza de tendencia (menos espacio en tendencias fuertes)
            trend_multiplier = config.get('trend_multiplier', 0.6)
            trend_factor = 1 - (trend_strength - 0.5) * trend_multiplier
            
            # Ajuste por volumen (menos espacio con alto volumen)
            volume_multiplier = config.get('volume_multiplier', 0.4)
            volume_factor = 1 - (volume_ratio - 1.0) * volume_multiplier
            
            # Ajuste por nivel de ganancia (más conservador con más ganancia)
            profit_adjustment = config.get('profit_adjustment', 0.5)
            profit_factor = 1 - min(profit_pct, 0.1) * profit_adjustment
            
            # Calcular distancia final
            optimized_distance = (base_distance * atr_multiplier * 
                                volatility_factor * momentum_factor * 
                                trend_factor * volume_factor * profit_factor)
            
            # Límites de seguridad
            min_distance = config.get('min_trailing_distance', 0.003)  # 0.3%
            max_distance = config.get('max_trailing_distance', 0.02)   # 2.0%
            
            return max(min_distance, min(max_distance, optimized_distance))
            
        except Exception as e:
            logger.error(f"Error calculating optimized trailing distance: {e}")
            return base_distance
    
    def _evaluate_dynamic_position_sizing(self, position: Dict, market_data: Dict):
        """Evaluar si se necesita ajuste dinámico del tamaño de posición"""
        try:
            # Calcular performance actual de la posición
            entry_price = position.get("entry_price", 0)
            current_price = position.get("current_price", 0)
            position_size = position.get("size", 0)
            
            if entry_price > 0 and current_price > 0:
                profit_pct = abs(current_price - entry_price) / entry_price
                
                # Si la posición está muy en ganancia y el momentum es fuerte
                pyramid_profit_threshold = 5.0 / 100
                pyramid_momentum_threshold = 0.7
                pyramid_trend_threshold = 0.6
                pyramid_max_additional_pct = 2.0 / 100
                
                if (profit_pct > pyramid_profit_threshold and
                    market_data["momentum"] > pyramid_momentum_threshold and
                    market_data["trend_strength"] > pyramid_trend_threshold):
                    
                    # Considerar incrementar posición (pyramiding)
                    max_additional = self.portfolio_value * pyramid_max_additional_pct
                    if position_size < max_additional:
                        position["pyramid_opportunity"] = True
                        position["pyramid_reason"] = f"Strong momentum ({market_data['momentum']:.2f}) and trend ({market_data['trend_strength']:.2f})"
                        logger.info(f"Pyramid opportunity identified for {position.get('symbol', 'Unknown')}")
                
                # Si hay alta volatilidad, considerar reducir exposición
                high_volatility_threshold = 4.0 / 100
                if market_data["volatility"] > high_volatility_threshold:
                    position["reduce_exposure_warning"] = True
                    position["reduce_reason"] = f"High volatility ({market_data['volatility']:.3f})"
                    logger.warning(f"High volatility warning for {position.get('symbol', 'Unknown')}")
                    
        except Exception as e:
            logger.error(f"Error evaluating dynamic position sizing: {e}")
    
    def _calculate_unrealized_pnl(self, position: Dict, current_price: float) -> float:
        """Calcular PnL no realizado de una posición"""
        try:
            entry_price = position["entry_price"]
            size = position["size"]
            
            if position["signal_type"] == "BUY":
                return (current_price - entry_price) * size
            else:
                return (entry_price - current_price) * size
        except Exception as e:
            logger.error(f"Error calculating unrealized PnL: {e}")
            return 0.0
    
    def _update_intelligent_trailing_take_profit(self, dynamic_tp: DynamicTakeProfit, 
                                                current_price: float, signal_type: str,
                                                entry_price: float, current_profit_pct: float) -> DynamicTakeProfit:
        """Actualizar take profit dinámico basado en ganancias y confianza del mercado"""
        try:
            # Crear copia para actualizar
            updated_tp = DynamicTakeProfit(
                initial_tp=dynamic_tp.initial_tp,
                current_tp=dynamic_tp.current_tp,
                trailing_tp=dynamic_tp.trailing_tp,
                tp_increment_pct=dynamic_tp.tp_increment_pct,
                tp_type=dynamic_tp.tp_type,
                last_update=datetime.now(),
                take_profit_price=dynamic_tp.take_profit_price,
                confidence_threshold=dynamic_tp.confidence_threshold,
                max_tp_adjustments=dynamic_tp.max_tp_adjustments,
                adjustments_made=dynamic_tp.adjustments_made
            )
            
            # Solo actualizar si hay ganancias significativas
            min_profit_for_tp_update = 1.5
            if current_profit_pct < min_profit_for_tp_update:
                return updated_tp
            
            # Verificar si ya se alcanzó el máximo de ajustes
            if updated_tp.adjustments_made >= updated_tp.max_tp_adjustments:
                return updated_tp
            
            # Calcular nuevo take profit basado en ganancias
            profit_multiplier = 1.0
            
            if signal_type == "BUY":
                # Para BUY: incrementar TP hacia arriba
                tp_update_profit_threshold = 5.0
                if current_profit_pct >= tp_update_profit_threshold:
                    profit_multiplier = 1 + (updated_tp.tp_increment_pct / 100)
                    new_tp = updated_tp.current_tp * profit_multiplier
                    
                    # Asegurar que el nuevo TP sea mayor al actual
                    if new_tp > updated_tp.current_tp:
                        updated_tp.current_tp = round(new_tp, 2)
                        updated_tp.trailing_tp = round(new_tp, 2)
                        updated_tp.take_profit_price = round(new_tp, 2)
                        updated_tp.adjustments_made += 1
                        
                        logger.info(f"TP dinámico actualizado (BUY): {updated_tp.current_tp} "
                                  f"(ganancia: {current_profit_pct:.2f}%)")
            
            else:  # SELL
                # Para SELL: decrementar TP hacia abajo
                tp_update_profit_threshold = 5.0
                if current_profit_pct >= tp_update_profit_threshold:
                    profit_multiplier = 1 - (updated_tp.tp_increment_pct / 100)
                    new_tp = updated_tp.current_tp * profit_multiplier
                    
                    # Asegurar que el nuevo TP sea menor al actual
                    if new_tp < updated_tp.current_tp:
                        updated_tp.current_tp = round(new_tp, 2)
                        updated_tp.trailing_tp = round(new_tp, 2)
                        updated_tp.take_profit_price = round(new_tp, 2)
                        updated_tp.adjustments_made += 1
                        
                        logger.info(f"TP dinámico actualizado (SELL): {updated_tp.current_tp} "
                                  f"(ganancia: {current_profit_pct:.2f}%)")
            
            return updated_tp
        
        except Exception as e:
            logger.error(f"Error updating intelligent trailing take profit: {e}")
            return dynamic_tp
    
    def generate_risk_report(self) -> Dict:
        """Generar reporte completo de riesgo del portfolio"""
        try:
            # Calcular métricas actuales del portfolio
            portfolio_metrics = self._calculate_portfolio_risk_metrics()
            
            # Calcular PnL total no realizado
            total_unrealized_pnl = sum(
                pos.get("unrealized_pnl", 0) for pos in self.open_positions.values()
            )
            
            # Calcular exposición total
            total_exposure = sum(
                pos.get("size", 0) for pos in self.open_positions.values()
            )
            
            # Calcular riesgo por posición
            position_risks = []
            for symbol, position in self.open_positions.items():
                position_risk = {
                    "symbol": symbol,
                    "size": position.get("size", 0),
                    "entry_price": position.get("entry_price", 0),
                    "current_price": position.get("current_price", 0),
                    "unrealized_pnl": position.get("unrealized_pnl", 0),
                    "stop_loss": position.get("current_stop", 0),
                    "risk_amount": abs(position.get("entry_price", 0) - position.get("current_stop", 0)) * position.get("size", 0),
                    "position_risk_pct": (position.get("size", 0) / self.portfolio_value) * 100 if self.portfolio_value > 0 else 0
                }
                position_risks.append(position_risk)
            
            # Determinar nivel de riesgo general con valores por defecto
            very_high_risk_threshold = 10.0 / 100
            high_risk_threshold = 5.0 / 100
            moderate_risk_exposure_threshold = 50.0 / 100
            
            overall_risk_level = "LOW"
            if self.current_drawdown > very_high_risk_threshold:
                overall_risk_level = "VERY_HIGH"
            elif self.current_drawdown > high_risk_threshold:
                overall_risk_level = "HIGH"
            elif total_exposure / self.portfolio_value > moderate_risk_exposure_threshold:
                overall_risk_level = "MODERATE"
            
            # Generar alertas con valores por defecto
            max_positions_alert = 5
            high_exposure_alert_threshold = 80.0 / 100
            
            alerts = []
            if self.current_drawdown >= self.max_drawdown_threshold:
                alerts.append("🚨 Drawdown máximo alcanzado")
            if len(self.open_positions) > max_positions_alert:
                alerts.append("⚠️ Demasiadas posiciones abiertas")
            if total_exposure / self.portfolio_value > high_exposure_alert_threshold:
                alerts.append("⚠️ Exposición muy alta del portfolio")
            
            # Recomendaciones con valores por defecto
            reduce_exposure_threshold = 5.0 / 100
            review_stops_loss_threshold = 2.0 / 100
            
            recommendations = []
            if self.current_drawdown > reduce_exposure_threshold:
                recommendations.append("Considerar reducir exposición")
            if len(self.open_positions) == 0:
                recommendations.append("Portfolio sin exposición - Buscar oportunidades")
            if total_unrealized_pnl < -self.portfolio_value * review_stops_loss_threshold:
                recommendations.append("Revisar stops loss de posiciones perdedoras")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "portfolio_value": round(self.portfolio_value, 2),
                "total_unrealized_pnl": round(total_unrealized_pnl, 2),
                "total_exposure": round(total_exposure, 2),
                "exposure_percentage": round((total_exposure / self.portfolio_value) * 100, 2) if self.portfolio_value > 0 else 0,
                "current_drawdown": round(self.current_drawdown * 100, 2),
                "max_drawdown": round(self.max_historical_drawdown * 100, 2),
                "daily_pnl": round(self.daily_pnl, 2),
                "open_positions_count": len(self.open_positions),
                "overall_risk_level": overall_risk_level,
                "position_risks": position_risks,
                "alerts": alerts,
                "recommendations": recommendations,
                "risk_metrics": {
                    "max_portfolio_risk": self.max_portfolio_risk * 100,
                    "max_daily_risk": self.max_daily_risk * 100,
                    "max_drawdown_threshold": self.max_drawdown_threshold * 100,
                    "risk_budget_used": round(len(self.open_positions) * self.max_portfolio_risk * 100, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Error generating risk report: {str(e)}",
                "portfolio_value": self.portfolio_value,
                "current_drawdown": self.current_drawdown * 100,
                "open_positions_count": len(self.open_positions),
                "overall_risk_level": "UNKNOWN"
            }
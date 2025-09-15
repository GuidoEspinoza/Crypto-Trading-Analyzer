"""🛡️ Enhanced Risk Manager - Sistema Avanzado de Gestión de Riesgo
Sistema profesional de gestión de riesgo con stop-loss dinámico,
position sizing inteligente y gestión de drawdown.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum

# Importar componentes existentes
from .enhanced_strategies import EnhancedSignal
from src.config.config import (
    CONSOLIDATED_CONFIG,
    get_module_config,
    RiskManagerConfig, 
    TradingProfiles
)

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
        # Configuración de riesgo desde archivo centralizado
        self.config = RiskManagerConfig()
        self.global_config = TradingProfiles.get_current_profile()
        
        self.max_portfolio_risk = self.config.get_max_risk_per_trade() / 100  # Convertir de % a decimal
        self.max_daily_risk = self.config.get_max_daily_risk() / 100  # Convertir de % a decimal
        self.max_drawdown_threshold = self.config.get_max_drawdown_threshold() / 100  # Convertir de % a decimal
        self.correlation_threshold = self.config.get_correlation_threshold()
        
        # Position sizing profesional desde configuración centralizada
        self.min_position_size = self.config.get_min_position_size()
        self.max_position_size = self.config.get_max_position_size() / 100  # Convertir de % a decimal
        self.kelly_fraction = self.config.get_kelly_fraction()
        self.volatility_adjustment = True  # Ajustar tamaño según volatilidad
        
        # Stop loss dinámico profesional desde configuración centralizada
        self.atr_multiplier_range = (self.config.get_atr_multiplier_min(), self.config.get_atr_multiplier_max())
        self.trailing_stop_activation = self.config.get_trailing_stop_activation() / 100  # Convertir de % a decimal
        self.breakeven_stop_threshold = self.config.get_breakeven_threshold() / 100  # Convertir de % a decimal
        
        # Configuración adicional desde configuración global
        self.min_trailing_distance = self.global_config.get('min_trailing_distance', 0.005)
        self.max_trailing_distance = self.global_config.get('max_trailing_distance', 0.05)
        
        # Métricas de portfolio desde configuración centralizada
        self.portfolio_value = self.config.INITIAL_PORTFOLIO_VALUE
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
            profile = TradingProfiles.get_current_profile()
            min_confidence = profile.get('min_confidence_threshold', 65.0)  # Ya está en porcentaje
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
            
            # Riesgo de volatilidad - Obtener desde configuración
            profile = TradingProfiles.get_current_profile()
            volatility_factor = profile.get('volatility_adjustment_factor', 1.2)
            
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
            profile = TradingProfiles.get_current_profile()
            win_rate = profile.get('kelly_win_rate', 0.6)  # Tasa de ganancia desde perfil
            avg_win = signal.risk_reward_ratio if signal.risk_reward_ratio > 0 else 1.5
            avg_loss = profile.get('kelly_avg_loss', 1.0)  # Pérdida promedio desde perfil
            
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
                leverage_used=profile.get('default_leverage', 1.0),  # Leverage desde perfil
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
                leverage_used=profile.get('default_leverage', 1.0),
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
            atr_multiplier = self.config.get_atr_default()  # Multiplicador ATR por defecto
            
            # Ajustar multiplicador según volatilidad
            if signal.market_regime == "VOLATILE":
                atr_multiplier = self.config.get_atr_volatile()  # Más espacio en mercados volátiles
            elif signal.market_regime == "RANGING":
                atr_multiplier = self.config.get_atr_sideways()  # Menos espacio en mercados laterales
            
            # Evitar división por cero
            if signal.price > 0:
                trailing_distance = abs(signal.price - initial_stop) / signal.price * 100
            else:
                profile = TradingProfiles.get_current_profile()
                trailing_distance = profile.get('default_trailing_distance', 2.0)  # Valor desde perfil
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
                atr_multiplier=self.config.get_atr_default(),
                stop_type="FIXED",
                last_update=datetime.now(),
                stop_loss_price=stop_price,
                trailing_distance=round(trailing_distance, 2)
            )
    
    def _configure_dynamic_take_profit(self, signal: EnhancedSignal) -> DynamicTakeProfit:
        """Configurar take profit dinámico y ajustable"""
        try:
            # Take profit inicial (del signal)
            initial_tp = signal.take_profit_price
            
            # Si no hay take profit en el signal, calcularlo
            if initial_tp == 0:
                # Verificar que indicators_data no sea None
                indicators_data = signal.indicators_data if signal.indicators_data is not None else {}
                atr_data = indicators_data.get("atr", signal.price * 0.02)
                if signal.signal_type == "BUY":
                    initial_tp = signal.price + (3 * atr_data)  # 3 ATR por encima para BUY
                else:
                    initial_tp = signal.price - (3 * atr_data)  # 3 ATR por debajo para SELL
            
            # Obtener configuración desde perfil activo
            from src.config.config import RiskManagerConfig
            risk_config = RiskManagerConfig()
            
            # Configurar parámetros del trailing TP desde configuración
            profile = TradingProfiles.get_current_profile()
            tp_increment_pct = profile.get('tp_increment_base_pct', 1.0)  # Valor base desde perfil
            confidence_threshold = risk_config.get_tp_confidence_threshold()  # Desde perfil activo
            
            # Ajustar según régimen de mercado
            if signal.market_regime == "TRENDING":
                tp_increment_pct = 1.5  # Más agresivo en tendencias
                confidence_threshold = max(0.5, confidence_threshold - 0.1)  # Reducir umbral
            elif signal.market_regime == "VOLATILE":
                tp_increment_pct = 0.8  # Más conservador en volatilidad
                confidence_threshold = min(0.9, confidence_threshold + 0.1)  # Aumentar umbral
            
            return DynamicTakeProfit(
                initial_tp=round(initial_tp, 2),
                current_tp=round(initial_tp, 2),
                trailing_tp=round(initial_tp, 2),
                tp_increment_pct=tp_increment_pct,
                tp_type="DYNAMIC",
                last_update=datetime.now(),
                take_profit_price=round(initial_tp, 2),
                confidence_threshold=confidence_threshold,
                max_tp_adjustments=risk_config.get_max_tp_adjustments(),
                adjustments_made=0
            )
            
        except Exception as e:
            logger.error(f"Error configuring dynamic take profit: {e}")
            tp_price = signal.price * 1.06 if signal.signal_type == "BUY" else signal.price * 0.94
            return DynamicTakeProfit(
                initial_tp=tp_price,
                current_tp=tp_price,
                trailing_tp=tp_price,
                tp_increment_pct=profile.get('tp_increment_base_pct', 1.0),
                tp_type="FIXED",
                last_update=datetime.now(),
                take_profit_price=tp_price,
                confidence_threshold=risk_config.get_tp_confidence_threshold(),
                max_tp_adjustments=risk_config.get_max_tp_adjustments(),
                adjustments_made=0
            )
    
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
        profile = TradingProfiles.get_current_profile()
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
                leverage_used=profile.get('default_leverage', 1.0),
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
                tp_increment_pct=profile.get('tp_increment_base_pct', 1.0),
                tp_type="FIXED",
                last_update=datetime.now(),
                take_profit_price=default_tp_price,
                confidence_threshold=RiskManagerConfig().get_tp_confidence_threshold(),
                max_tp_adjustments=RiskManagerConfig().get_max_tp_adjustments(),
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
            # Usar valores configurables para simulación
            default_volatility = self.global_config.get('default_market_volatility', 0.02)
            default_volume_ratio = self.global_config.get('default_volume_ratio', 1.5)
            default_trend_strength = self.global_config.get('default_trend_strength', 0.7)
            support_resistance_pct = self.global_config.get('support_resistance_distance_pct', 2.0) / 100
            default_momentum = self.global_config.get('default_momentum', 0.6)
            
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
        """Actualizar trailing stop usando lógica inteligente"""
        try:
            signal_type = position.get("signal_type")
            entry_price = position.get("entry_price", 0)
            current_stop = position.get("current_stop", 0)
            atr_multiplier = position.get("atr_multiplier", 2.0)
            
            if signal_type == "BUY":
                # Calcular ganancia actual
                profit_pct = (current_price - entry_price) / entry_price
                
                # Activar trailing solo si hay ganancia suficiente
                if profit_pct >= self.trailing_stop_activation:
                    
                    # Calcular distancia de trailing basada en volatilidad y momentum
                    base_distance = atr_multiplier * self.global_config.get('trailing_base_distance_pct', 1.0) / 100
                    
                    # Ajustar distancia según condiciones de mercado
                    volatility_base = self.global_config.get('volatility_base_threshold', 0.02)
                    volatility_multiplier = self.global_config.get('volatility_adjustment_multiplier', 10)
                    momentum_adjustment = self.global_config.get('momentum_adjustment_factor', 0.2)
                    
                    volatility_adj = 1 + (market_data["volatility"] - volatility_base) * volatility_multiplier
                    momentum_adj = 1 - (market_data["momentum"] - 0.5) * momentum_adjustment
                    
                    adjusted_distance = base_distance * volatility_adj * momentum_adj
                    adjusted_distance = max(self.min_trailing_distance, min(self.max_trailing_distance, adjusted_distance))
                    
                    # Calcular nuevo stop
                    new_stop = current_price * (1 - adjusted_distance)
                    
                    # Solo actualizar si es mejor que el stop actual
                    if new_stop > current_stop:
                        return {
                            "new_stop": round(new_stop, 4),
                            "stop_type": "INTELLIGENT_TRAILING",
                            "reason": f"Vol:{volatility_adj:.2f}, Mom:{momentum_adj:.2f}, Dist:{adjusted_distance:.3f}"
                        }
            
            elif signal_type == "SELL":
                # Lógica similar para posiciones short
                profit_pct = (entry_price - current_price) / entry_price
                
                if profit_pct >= self.trailing_stop_activation:
                    base_distance = atr_multiplier * self.global_config.get('trailing_base_distance_pct', 1.0) / 100
                    volatility_base = self.global_config.get('volatility_base_threshold', 0.02)
                    volatility_multiplier = self.global_config.get('volatility_adjustment_multiplier', 10)
                    momentum_adjustment = self.global_config.get('momentum_adjustment_factor', 0.2)
                    
                    volatility_adj = 1 + (market_data["volatility"] - volatility_base) * volatility_multiplier
                    momentum_adj = 1 - (market_data["momentum"] - 0.5) * momentum_adjustment
                    
                    adjusted_distance = base_distance * volatility_adj * momentum_adj
                    adjusted_distance = max(self.min_trailing_distance, min(self.max_trailing_distance, adjusted_distance))
                    
                    new_stop = current_price * (1 + adjusted_distance)
                    
                    if new_stop < current_stop:
                        return {
                            "new_stop": round(new_stop, 4),
                            "stop_type": "INTELLIGENT_TRAILING",
                            "reason": f"Vol:{volatility_adj:.2f}, Mom:{momentum_adj:.2f}, Dist:{adjusted_distance:.3f}"
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating intelligent trailing stop: {e}")
            return None
    
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
                pyramid_profit_threshold = self.global_config.get('pyramid_profit_threshold', 5.0) / 100
                pyramid_momentum_threshold = self.global_config.get('pyramid_momentum_threshold', 0.7)
                pyramid_trend_threshold = self.global_config.get('pyramid_trend_threshold', 0.6)
                pyramid_max_additional_pct = self.global_config.get('pyramid_max_additional_pct', 2.0) / 100
                
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
                high_volatility_threshold = self.global_config.get('high_volatility_threshold', 4.0) / 100
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
            min_profit_for_tp_update = self.global_config.get('min_profit_for_tp_update', 1.5)
            if current_profit_pct < min_profit_for_tp_update:
                return updated_tp
            
            # Verificar si ya se alcanzó el máximo de ajustes
            if updated_tp.adjustments_made >= updated_tp.max_tp_adjustments:
                return updated_tp
            
            # Calcular nuevo take profit basado en ganancias
            profit_multiplier = 1.0
            
            if signal_type == "BUY":
                # Para BUY: incrementar TP hacia arriba
                tp_update_profit_threshold = self.global_config.get('tp_update_profit_threshold', 5.0)
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
                tp_update_profit_threshold = self.global_config.get('tp_update_profit_threshold', 5.0)
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
            
            # Determinar nivel de riesgo general usando configuración
            very_high_risk_threshold = self.global_config.get('very_high_risk_drawdown_threshold', 10.0) / 100
            high_risk_threshold = self.global_config.get('high_risk_drawdown_threshold', 5.0) / 100
            moderate_risk_exposure_threshold = self.global_config.get('moderate_risk_exposure_threshold', 50.0) / 100
            
            overall_risk_level = "LOW"
            if self.current_drawdown > very_high_risk_threshold:
                overall_risk_level = "VERY_HIGH"
            elif self.current_drawdown > high_risk_threshold:
                overall_risk_level = "HIGH"
            elif total_exposure / self.portfolio_value > moderate_risk_exposure_threshold:
                overall_risk_level = "MODERATE"
            
            # Generar alertas usando configuración
            max_positions_alert = self.global_config.get('max_positions_alert_threshold', 5)
            high_exposure_alert_threshold = self.global_config.get('high_exposure_alert_threshold', 80.0) / 100
            
            alerts = []
            if self.current_drawdown >= self.max_drawdown_threshold:
                alerts.append("🚨 Drawdown máximo alcanzado")
            if len(self.open_positions) > max_positions_alert:
                alerts.append("⚠️ Demasiadas posiciones abiertas")
            if total_exposure / self.portfolio_value > high_exposure_alert_threshold:
                alerts.append("⚠️ Exposición muy alta del portfolio")
            
            # Recomendaciones usando configuración
            reduce_exposure_threshold = self.global_config.get('reduce_exposure_drawdown_threshold', 5.0) / 100
            review_stops_loss_threshold = self.global_config.get('review_stops_loss_threshold', 2.0) / 100
            
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
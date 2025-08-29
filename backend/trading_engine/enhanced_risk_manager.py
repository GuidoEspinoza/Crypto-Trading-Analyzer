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
class EnhancedRiskAssessment:
    """Evaluación de riesgo mejorada"""
    overall_risk_score: float
    risk_level: RiskLevel
    position_sizing: PositionSizing
    dynamic_stop_loss: DynamicStopLoss
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
        # Configuración de riesgo profesional
        self.max_portfolio_risk = 0.015  # 1.5% del portfolio por trade (más conservador)
        self.max_daily_risk = 0.04  # 4% del portfolio por día (reducido)
        self.max_drawdown_threshold = 0.12  # 12% drawdown máximo (más estricto)
        self.correlation_threshold = 0.6  # Correlación máxima entre posiciones (más estricto)
        
        # Position sizing profesional
        self.min_position_size = 0.005  # Tamaño mínimo de posición (0.5%)
        self.max_position_size = 0.08  # 8% del portfolio máximo por posición (reducido)
        self.kelly_fraction = 0.20  # Fracción Kelly más conservadora
        self.volatility_adjustment = True  # Ajustar tamaño según volatilidad
        
        # Stop loss dinámico profesional
        self.atr_multiplier_range = (2.0, 3.5)  # Rango de multiplicadores ATR más amplio
        self.trailing_stop_activation = 0.025  # 2.5% de ganancia para activar trailing
        self.breakeven_stop_threshold = 0.015  # 1.5% para mover stop a breakeven
        
        # Métricas de portfolio
        self.portfolio_value = 10000.0  # Valor inicial del portfolio
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
            is_approved = (
                risk_level not in [RiskLevel.EXTREME, RiskLevel.VERY_HIGH] and
                not max_dd_alert and
                signal.confidence_score >= 50
            )
            
            return EnhancedRiskAssessment(
                overall_risk_score=round(overall_risk_score, 2),
                risk_level=risk_level,
                position_sizing=position_sizing,
                dynamic_stop_loss=dynamic_stop,
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
            
            # Riesgo de volatilidad
            if signal.market_regime == "VOLATILE":
                risk_factors["volatility_risk"] = 0.8
            elif signal.market_regime == "RANGING":
                risk_factors["volatility_risk"] = 0.3
            else:
                risk_factors["volatility_risk"] = 0.5
            
            # Riesgo de liquidez (basado en volumen)
            volume_data = signal.indicators_data.get("volume_analysis", {})
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
            win_rate = 0.6  # Asumimos 60% win rate
            avg_win = signal.risk_reward_ratio if signal.risk_reward_ratio > 0 else 1.5
            avg_loss = 1.0
            
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
                leverage_used=1.0,  # Sin leverage por defecto
                risk_level=risk_level,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error calculating position sizing: {e}")
            return PositionSizing(
                recommended_size=self.min_position_size,
                max_position_size=self.portfolio_value * 0.01,
                risk_per_trade=self.portfolio_value * 0.01,
                position_value=self.min_position_size,
                leverage_used=1.0,
                risk_level=RiskLevel.LOW,
                reasoning="Error in calculation - using minimum size"
            )
    
    def _configure_dynamic_stop_loss(self, signal: EnhancedSignal) -> DynamicStopLoss:
        """Configurar stop loss dinámico"""
        try:
            # Stop loss inicial (del signal)
            initial_stop = signal.stop_loss_price
            
            # Si no hay stop loss en el signal, calcularlo
            if initial_stop == 0:
                atr_data = signal.indicators_data.get("atr", signal.price * 0.02)
                if signal.signal_type == "BUY":
                    initial_stop = signal.price - (2 * atr_data)
                else:
                    initial_stop = signal.price + (2 * atr_data)
            
            # Configurar trailing stop
            atr_multiplier = 2.0  # Multiplicador ATR por defecto
            
            # Ajustar multiplicador según volatilidad
            if signal.market_regime == "VOLATILE":
                atr_multiplier = 3.0  # Más espacio en mercados volátiles
            elif signal.market_regime == "RANGING":
                atr_multiplier = 1.5  # Menos espacio en mercados laterales
            
            trailing_distance = abs(signal.price - initial_stop) / signal.price * 100
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
                atr_multiplier=2.0,
                stop_type="FIXED",
                last_update=datetime.now(),
                stop_loss_price=stop_price,
                trailing_distance=round(trailing_distance, 2)
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
        default_stop_price = signal.price * 0.95 if signal.signal_type == "BUY" else signal.price * 1.05
        default_trailing_distance = abs(signal.price - default_stop_price) / signal.price * 100
        return EnhancedRiskAssessment(
            overall_risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            position_sizing=PositionSizing(
                recommended_size=self.min_position_size,
                max_position_size=self.portfolio_value * 0.01,
                risk_per_trade=self.portfolio_value * 0.01,
                position_value=self.min_position_size,
                leverage_used=1.0,
                risk_level=RiskLevel.HIGH,
                reasoning="Error in calculation - using conservative defaults"
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
        """Actualizar posición existente y ajustar stop loss dinámico"""
        try:
            if symbol in self.open_positions:
                position = self.open_positions[symbol]
                
                # Actualizar stop loss trailing
                if position.get("signal_type") == "BUY":
                    # Para posiciones long
                    if current_price > position["entry_price"] * (1 + self.trailing_stop_activation):
                        # Activar trailing stop
                        new_stop = current_price * (1 - position["atr_multiplier"] * 0.01)
                        if new_stop > position["current_stop"]:
                            position["current_stop"] = new_stop
                            position["stop_type"] = "TRAILING"
                            logger.info(f"Updated trailing stop for {symbol}: {new_stop}")
                
                elif position.get("signal_type") == "SELL":
                    # Para posiciones short
                    if current_price < position["entry_price"] * (1 - self.trailing_stop_activation):
                        # Activar trailing stop
                        new_stop = current_price * (1 + position["atr_multiplier"] * 0.01)
                        if new_stop < position["current_stop"]:
                            position["current_stop"] = new_stop
                            position["stop_type"] = "TRAILING"
                            logger.info(f"Updated trailing stop for {symbol}: {new_stop}")
                
                # Actualizar métricas de la posición
                position["current_price"] = current_price
                position["unrealized_pnl"] = self._calculate_unrealized_pnl(position, current_price)
                position["last_update"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error updating position for {symbol}: {e}")
    
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
            
            # Determinar nivel de riesgo general
            overall_risk_level = "LOW"
            if self.current_drawdown > 0.1:
                overall_risk_level = "VERY_HIGH"
            elif self.current_drawdown > 0.05:
                overall_risk_level = "HIGH"
            elif total_exposure / self.portfolio_value > 0.5:
                overall_risk_level = "MODERATE"
            
            # Generar alertas
            alerts = []
            if self.current_drawdown >= self.max_drawdown_threshold:
                alerts.append("🚨 Drawdown máximo alcanzado")
            if len(self.open_positions) > 5:
                alerts.append("⚠️ Demasiadas posiciones abiertas")
            if total_exposure / self.portfolio_value > 0.8:
                alerts.append("⚠️ Exposición muy alta del portfolio")
            
            # Recomendaciones
            recommendations = []
            if self.current_drawdown > 0.05:
                recommendations.append("Considerar reducir exposición")
            if len(self.open_positions) == 0:
                recommendations.append("Portfolio sin exposición - Buscar oportunidades")
            if total_unrealized_pnl < -self.portfolio_value * 0.02:
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
"""
🛡️ Universal Trading Analyzer - Risk Manager
Sistema avanzado de gestión de riesgo para trading automático
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
import math

# Importar modelos de database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import db_manager
from database.models import Trade, Portfolio
from .strategies import TradingSignal

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RiskAssessment:
    """
    📊 Evaluación de riesgo para una operación
    """
    is_approved: bool
    risk_score: float  # 0-100 (mayor = más riesgoso)
    position_size: float  # Tamaño recomendado de posición
    stop_loss: Optional[float]
    take_profit: Optional[float]
    max_loss_amount: float
    risk_reason: str
    recommendations: List[str]

@dataclass
class PortfolioRisk:
    """
    📈 Análisis de riesgo del portfolio completo
    """
    total_exposure: float  # Porcentaje del portfolio invertido
    concentration_risk: float  # Riesgo de concentración en un asset
    var_1d: float  # Value at Risk 1 día
    max_drawdown: float  # Máximo drawdown actual
    risk_level: str  # Low, Medium, High, Critical
    open_positions_count: int
    recommendations: List[str]

class RiskManager:
    """
    🛡️ Risk Manager - Gestor avanzado de riesgo
    
    Características:
    - Position sizing dinámico
    - Stop loss automático
    - Take profit inteligente  
    - Límites de exposición
    - Gestión de drawdown
    - Análisis de volatilidad
    """
    
    def __init__(self):
        """
        Inicializar Risk Manager con parámetros de riesgo
        """
        # Límites de riesgo generales
        self.max_risk_per_trade = 0.02  # 2% máximo por trade
        self.max_portfolio_risk = 0.20  # 20% máximo del portfolio
        self.max_daily_loss = 0.05  # 5% pérdida máxima diaria
        self.max_drawdown = 0.15  # 15% drawdown máximo
        
        # Límites de posición
        self.max_position_size = 0.10  # 10% máximo por posición
        self.max_concentration = 0.30  # 30% máximo en un asset
        self.max_open_positions = 5  # Máximo 5 posiciones abiertas
        
        # Parámetros de stop loss y take profit
        self.default_stop_loss_pct = 0.05  # 5% stop loss por defecto
        self.default_take_profit_pct = 0.15  # 15% take profit por defecto
        self.trailing_stop_pct = 0.03  # 3% trailing stop
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("🛡️ Risk Manager initialized")
    
    def assess_trade_risk(self, signal: TradingSignal, portfolio_value: float) -> RiskAssessment:
        """
        🔍 Evaluar el riesgo de una señal de trading
        
        Args:
            signal: Señal de trading a evaluar
            portfolio_value: Valor total del portfolio
            
        Returns:
            RiskAssessment: Evaluación completa del riesgo
        """
        try:
            self.logger.info(f"🔍 Assessing risk for {signal.signal_type} {signal.symbol}")
            
            # Análisis básico de la señal
            signal_risk_score = self._calculate_signal_risk(signal)
            
            # Análisis del portfolio actual
            portfolio_risk = self._analyze_portfolio_risk()
            
            # Calcular tamaño de posición recomendado
            recommended_position_size = self._calculate_position_size(
                signal, portfolio_value, signal_risk_score
            )
            
            # Calcular stop loss y take profit
            stop_loss, take_profit = self._calculate_stop_loss_take_profit(signal)
            
            # Evaluar si se aprueba el trade
            is_approved, risk_reason = self._evaluate_trade_approval(
                signal, signal_risk_score, portfolio_risk, recommended_position_size
            )
            
            # Calcular pérdida máxima potencial
            max_loss = recommended_position_size * portfolio_value * self.default_stop_loss_pct
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(
                signal, signal_risk_score, portfolio_risk
            )
            
            return RiskAssessment(
                is_approved=is_approved,
                risk_score=signal_risk_score,
                position_size=recommended_position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                max_loss_amount=max_loss,
                risk_reason=risk_reason,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error assessing trade risk: {e}")
            return RiskAssessment(
                is_approved=False,
                risk_score=100.0,
                position_size=0.0,
                stop_loss=None,
                take_profit=None,
                max_loss_amount=0.0,
                risk_reason=f"Error in risk assessment: {str(e)}",
                recommendations=["❌ Technical error - avoid trading"]
            )
    
    def _calculate_signal_risk(self, signal: TradingSignal) -> float:
        """
        📊 Calcular score de riesgo basado en la señal
        
        Returns:
            float: Risk score 0-100 (mayor = más riesgoso)
        """
        risk_score = 50.0  # Base risk
        
        # Riesgo basado en confianza (menor confianza = mayor riesgo)
        confidence_risk = 100 - signal.confidence_score
        risk_score += confidence_risk * 0.3
        
        # Riesgo basado en fortaleza de la señal
        strength_multipliers = {
            "Very Strong": -15,
            "Strong": -10,
            "Moderate": 0,
            "Weak": +20,
            "None": +40
        }
        risk_score += strength_multipliers.get(signal.strength, 20)
        
        # Riesgo basado en el símbolo (volatilidad histórica)
        symbol_risk = self._get_symbol_risk(signal.symbol)
        risk_score += symbol_risk
        
        # Riesgo basado en tipo de señal
        if signal.signal_type == "SELL":
            risk_score -= 5  # Vender es menos riesgoso que comprar
        
        return max(0, min(100, risk_score))
    
    def _get_symbol_risk(self, symbol: str) -> float:
        """
        🪙 Obtener riesgo específico del símbolo
        """
        # Riesgos relativos por símbolo (basado en volatilidad histórica)
        symbol_risks = {
            "BTC/USDT": 10,    # Bitcoin - relativamente estable
            "ETH/USDT": 15,    # Ethereum - un poco más volátil
            "ADA/USDT": 25,    # Altcoins - más volátiles
            "SOL/USDT": 30,
            "DOGE/USDT": 40,   # Memecoins - muy volátiles
            "SHIB/USDT": 50
        }
        
        return symbol_risks.get(symbol, 35)  # Default para símbolos desconocidos
    
    def _analyze_portfolio_risk(self) -> PortfolioRisk:
        """
        📈 Analizar riesgo del portfolio completo
        """
        try:
            with db_manager.get_db_session() as session:
                # Obtener posiciones abiertas
                open_trades = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True
                ).all()
                
                # Obtener portfolio summary
                portfolio_summary = db_manager.get_portfolio_summary(is_paper=True)
                total_value = portfolio_summary.get("total_value", 10000)
                
                # Calcular exposición total
                total_exposure = sum(trade.entry_value for trade in open_trades)
                exposure_percentage = (total_exposure / total_value) * 100 if total_value > 0 else 0
                
                # Calcular concentración de riesgo
                concentration_risk = self._calculate_concentration_risk(open_trades, total_value)
                
                # Calcular drawdown actual
                initial_balance = 10000.0  # Balance inicial
                current_pnl = portfolio_summary.get("total_pnl", 0)
                max_drawdown = max(0, (-current_pnl / initial_balance) * 100) if current_pnl < 0 else 0
                
                # Determinar nivel de riesgo
                risk_level = self._determine_risk_level(
                    exposure_percentage, concentration_risk, max_drawdown, len(open_trades)
                )
                
                # Generar recomendaciones de portfolio
                portfolio_recommendations = self._generate_portfolio_recommendations(
                    exposure_percentage, concentration_risk, max_drawdown, len(open_trades)
                )
                
                return PortfolioRisk(
                    total_exposure=exposure_percentage,
                    concentration_risk=concentration_risk,
                    var_1d=exposure_percentage * 0.05,  # Estimación simple de VaR
                    max_drawdown=max_drawdown,
                    risk_level=risk_level,
                    open_positions_count=len(open_trades),
                    recommendations=portfolio_recommendations
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error analyzing portfolio risk: {e}")
            return PortfolioRisk(
                total_exposure=0, concentration_risk=0, var_1d=0,
                max_drawdown=0, risk_level="Unknown", open_positions_count=0,
                recommendations=["❌ Error analyzing portfolio risk"]
            )
    
    def _calculate_concentration_risk(self, open_trades: List[Trade], total_value: float) -> float:
        """
        🎯 Calcular riesgo de concentración en assets
        """
        if not open_trades or total_value <= 0:
            return 0.0
        
        # Agrupar trades por símbolo
        symbol_exposure = {}
        for trade in open_trades:
            symbol = trade.symbol
            if symbol not in symbol_exposure:
                symbol_exposure[symbol] = 0
            symbol_exposure[symbol] += trade.entry_value
        
        # Encontrar la mayor concentración
        max_concentration = max(symbol_exposure.values()) if symbol_exposure else 0
        concentration_percentage = (max_concentration / total_value) * 100
        
        return concentration_percentage
    
    def _determine_risk_level(self, exposure: float, concentration: float, 
                            drawdown: float, positions_count: int) -> str:
        """
        🎯 Determinar nivel de riesgo del portfolio
        """
        # Calcular score de riesgo compuesto
        risk_score = 0
        
        # Riesgo por exposición
        if exposure > 80: risk_score += 40
        elif exposure > 60: risk_score += 25
        elif exposure > 40: risk_score += 10
        
        # Riesgo por concentración
        if concentration > 50: risk_score += 30
        elif concentration > 30: risk_score += 15
        elif concentration > 20: risk_score += 5
        
        # Riesgo por drawdown
        if drawdown > 15: risk_score += 40
        elif drawdown > 10: risk_score += 25
        elif drawdown > 5: risk_score += 10
        
        # Riesgo por número de posiciones
        if positions_count > 8: risk_score += 15
        elif positions_count > 5: risk_score += 5
        
        # Determinar nivel
        if risk_score >= 70:
            return "Critical"
        elif risk_score >= 50:
            return "High"
        elif risk_score >= 25:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_position_size(self, signal: TradingSignal, portfolio_value: float, 
                               risk_score: float) -> float:
        """
        📏 Calcular tamaño óptimo de posición
        """
        # Tamaño base según el riesgo
        base_size = self.max_position_size
        
        # Ajustar según score de riesgo
        risk_multiplier = max(0.2, 1 - (risk_score / 100))
        adjusted_size = base_size * risk_multiplier
        
        # Ajustar según confianza de la señal
        confidence_multiplier = signal.confidence_score / 100
        final_size = adjusted_size * confidence_multiplier
        
        # Aplicar límites mínimos y máximos
        final_size = max(0.01, min(self.max_position_size, final_size))
        
        return final_size
    
    def _calculate_stop_loss_take_profit(self, signal: TradingSignal) -> Tuple[Optional[float], Optional[float]]:
        """
        🎯 Calcular stop loss y take profit
        """
        if signal.price <= 0:
            return None, None
        
        # Ajustar percentajes según volatilidad del símbolo
        symbol_volatility = self._get_symbol_volatility(signal.symbol)
        
        # Stop loss más amplio para símbolos más volátiles
        stop_loss_pct = self.default_stop_loss_pct * (1 + symbol_volatility)
        take_profit_pct = self.default_take_profit_pct * (1 + symbol_volatility * 0.5)
        
        if signal.signal_type == "BUY":
            stop_loss = signal.price * (1 - stop_loss_pct)
            take_profit = signal.price * (1 + take_profit_pct)
        elif signal.signal_type == "SELL":
            stop_loss = signal.price * (1 + stop_loss_pct)
            take_profit = signal.price * (1 - take_profit_pct)
        else:
            return None, None
        
        return stop_loss, take_profit
    
    def _get_symbol_volatility(self, symbol: str) -> float:
        """
        📊 Obtener volatilidad relativa del símbolo
        """
        volatilities = {
            "BTC/USDT": 0.0,    # Baseline
            "ETH/USDT": 0.2,    # 20% más volátil
            "ADA/USDT": 0.5,    # 50% más volátil
            "SOL/USDT": 0.7,
            "DOGE/USDT": 1.0,   # 100% más volátil
            "SHIB/USDT": 1.5
        }
        
        return volatilities.get(symbol, 0.8)  # Default para símbolos desconocidos
    
    def _evaluate_trade_approval(self, signal: TradingSignal, risk_score: float, 
                               portfolio_risk: PortfolioRisk, position_size: float) -> Tuple[bool, str]:
        """
        ✅ Evaluar si se aprueba el trade
        """
        # Lista de razones de rechazo
        rejections = []
        
        # Verificar score de riesgo
        if risk_score > 80:
            rejections.append("Risk score too high")
        
        # Verificar exposición del portfolio
        if portfolio_risk.total_exposure > 80:
            rejections.append("Portfolio overexposed")
        
        # Verificar drawdown
        if portfolio_risk.max_drawdown > 15:
            rejections.append("Maximum drawdown exceeded")
        
        # Verificar número de posiciones
        if portfolio_risk.open_positions_count >= self.max_open_positions:
            rejections.append("Too many open positions")
        
        # Verificar concentración
        if portfolio_risk.concentration_risk > 50:
            rejections.append("High concentration risk")
        
        # Verificar tamaño mínimo de posición
        if position_size < 0.01:
            rejections.append("Position size too small")
        
        # Verificar nivel crítico de riesgo
        if portfolio_risk.risk_level == "Critical":
            rejections.append("Portfolio risk level critical")
        
        if rejections:
            return False, "; ".join(rejections)
        else:
            return True, "✅ Trade approved"
    
    def _generate_recommendations(self, signal: TradingSignal, risk_score: float, 
                                portfolio_risk: PortfolioRisk) -> List[str]:
        """
        💡 Generar recomendaciones basadas en el análisis
        """
        recommendations = []
        
        # Recomendaciones basadas en risk score
        if risk_score > 70:
            recommendations.append("🚨 High risk - consider reducing position size")
        elif risk_score > 50:
            recommendations.append("⚠️ Moderate risk - use tight stop loss")
        
        # Recomendaciones basadas en confianza
        if signal.confidence_score < 70:
            recommendations.append("🔍 Low confidence - wait for stronger signal")
        
        # Recomendaciones de portfolio
        if portfolio_risk.total_exposure > 70:
            recommendations.append("📊 High exposure - consider taking profits")
        
        if portfolio_risk.concentration_risk > 30:
            recommendations.append("🎯 High concentration - diversify portfolio")
        
        if portfolio_risk.open_positions_count > 3:
            recommendations.append("📈 Many positions - monitor closely")
        
        # Recomendaciones por defecto
        if not recommendations:
            recommendations.append("✅ Good risk profile - execute with standard parameters")
        
        return recommendations
    
    def _generate_portfolio_recommendations(self, exposure: float, concentration: float, 
                                          drawdown: float, positions: int) -> List[str]:
        """
        💡 Generar recomendaciones específicas del portfolio
        """
        recommendations = []
        
        if exposure > 80:
            recommendations.append("🚨 Reduce exposure - take some profits")
        elif exposure < 20:
            recommendations.append("🎯 Low exposure - consider more positions")
        
        if concentration > 40:
            recommendations.append("📊 Diversify - too concentrated in one asset")
        
        if drawdown > 10:
            recommendations.append("🛡️ High drawdown - implement stricter stops")
        
        if positions > 5:
            recommendations.append("📈 Too many positions - close weakest ones")
        elif positions == 0:
            recommendations.append("🎯 No positions - look for opportunities")
        
        return recommendations
    
    def check_stop_loss_triggers(self) -> List[Dict]:
        """
        🚨 Verificar si alguna posición ha activado stop loss
        """
        triggered_stops = []
        
        try:
            with db_manager.get_db_session() as session:
                open_trades = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True,
                    Trade.stop_loss.isnot(None)
                ).all()
                
                for trade in open_trades:
                    # Obtener precio actual (simulado - en producción sería de la API)
                    current_price = self._get_current_price(trade.symbol)
                    
                    if current_price and trade.stop_loss:
                        should_trigger = False
                        
                        if trade.trade_type == "BUY" and current_price <= trade.stop_loss:
                            should_trigger = True
                        elif trade.trade_type == "SELL" and current_price >= trade.stop_loss:
                            should_trigger = True
                        
                        if should_trigger:
                            triggered_stops.append({
                                "trade_id": trade.id,
                                "symbol": trade.symbol,
                                "entry_price": trade.entry_price,
                                "current_price": current_price,
                                "stop_loss": trade.stop_loss,
                                "loss_amount": abs(current_price - trade.entry_price) * trade.quantity,
                                "action": "SELL" if trade.trade_type == "BUY" else "BUY"
                            })
        
        except Exception as e:
            self.logger.error(f"❌ Error checking stop loss triggers: {e}")
        
        return triggered_stops
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """
        💰 Obtener precio actual (placeholder - en producción usaría la API)
        """
        # En producción, esto haría una llamada a tu API de precios
        # Por ahora retornamos None para evitar errores
        return None
    
    def generate_risk_report(self) -> Dict:
        """
        📋 Generar reporte completo de riesgo
        """
        try:
            portfolio_risk = self._analyze_portfolio_risk()
            triggered_stops = self.check_stop_loss_triggers()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "portfolio_risk": {
                    "total_exposure": portfolio_risk.total_exposure,
                    "concentration_risk": portfolio_risk.concentration_risk,
                    "max_drawdown": portfolio_risk.max_drawdown,
                    "risk_level": portfolio_risk.risk_level,
                    "open_positions": portfolio_risk.open_positions_count,
                    "var_1d": portfolio_risk.var_1d
                },
                "triggered_stops": triggered_stops,
                "recommendations": portfolio_risk.recommendations,
                "risk_limits": {
                    "max_risk_per_trade": self.max_risk_per_trade * 100,
                    "max_portfolio_risk": self.max_portfolio_risk * 100,
                    "max_position_size": self.max_position_size * 100,
                    "max_open_positions": self.max_open_positions
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generating risk report: {e}")
            return {"error": str(e)}
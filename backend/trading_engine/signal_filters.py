"""🔍 Advanced Signal Filtering System
Sistema avanzado de filtrado de señales para reducir falsos positivos
y mejorar la precisión del trading.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Importaciones con manejo de errores
try:
    from .enhanced_strategies import EnhancedSignal
except ImportError:
    # Fallback para importación directa
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from trading_engine.enhanced_strategies import EnhancedSignal

# Importar AdvancedIndicators con path absoluto
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from advanced_indicators import AdvancedIndicators

logger = logging.getLogger(__name__)

@dataclass
class FilteredSignal:
    """Señal filtrada con métricas de calidad"""
    original_signal: EnhancedSignal
    filtered_signal: str  # BUY, SELL, HOLD
    filter_score: float  # 0-100
    filters_passed: List[str]
    filters_failed: List[str]
    risk_assessment: str  # LOW, MEDIUM, HIGH
    quality_grade: str   # A+, A, B+, B, C+, C, D
    
class AdvancedSignalFilter:
    """🎯 Filtro avanzado de señales de trading"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.signal_history = []
        
    def _default_config(self) -> Dict:
        """Configuración por defecto del filtro"""
        return {
            "min_confluence_score": 4,
            "min_confidence": 65,
            "max_volatility_threshold": 0.08,  # 8%
            "volume_confirmation_required": True,
            "trend_confirmation_required": True,
            "min_risk_reward_ratio": 1.5,
            "max_drawdown_tolerance": 0.15,  # 15%
            "signal_cooldown_minutes": 30,
            "market_hours_only": False,
            "blacklist_patterns": ["DOJI"],  # Patrones a evitar
            "whitelist_regimes": ["TRENDING", "RANGING"],  # Regímenes permitidos
            "enable_sentiment_filter": False,
            "enable_correlation_filter": True
        }
    
    def filter_signal(self, signal: EnhancedSignal, market_data: pd.DataFrame) -> FilteredSignal:
        """🔍 Aplica todos los filtros a una señal"""
        try:
            filters_passed = []
            filters_failed = []
            filter_score = 0
            max_possible_score = 0
            
            # === FILTRO 1: CONFLUENCIA MÍNIMA ===
            max_possible_score += 15
            if signal.confluence_score >= self.config["min_confluence_score"]:
                filters_passed.append("confluence_check")
                filter_score += 15
            else:
                filters_failed.append(f"confluence_low_{signal.confluence_score}")
            
            # === FILTRO 2: CONFIANZA MÍNIMA ===
            max_possible_score += 20
            if signal.confidence_score >= self.config["min_confidence"]:
                filters_passed.append("confidence_check")
                filter_score += 20
            else:
                filters_failed.append(f"confidence_low_{signal.confidence_score:.1f}")
            
            # === FILTRO 3: VOLATILIDAD CONTROLADA ===
            max_possible_score += 10
            volatility_check = self._check_volatility(signal, market_data)
            if volatility_check["passed"]:
                filters_passed.append("volatility_check")
                filter_score += 10
            else:
                filters_failed.append(f"volatility_high_{volatility_check['level']}")
            
            # === FILTRO 4: CONFIRMACIÓN DE VOLUMEN ===
            max_possible_score += 15
            if not self.config["volume_confirmation_required"] or signal.volume_confirmation:
                filters_passed.append("volume_check")
                filter_score += 15
            else:
                filters_failed.append("volume_not_confirmed")
            
            # === FILTRO 5: CONFIRMACIÓN DE TENDENCIA ===
            max_possible_score += 15
            if not self.config["trend_confirmation_required"] or signal.trend_confirmed:
                filters_passed.append("trend_check")
                filter_score += 15
            else:
                filters_failed.append("trend_not_confirmed")
            
            # === FILTRO 6: RATIO RIESGO/BENEFICIO ===
            max_possible_score += 10
            if signal.risk_reward_ratio >= self.config["min_risk_reward_ratio"]:
                filters_passed.append("risk_reward_check")
                filter_score += 10
            else:
                filters_failed.append(f"risk_reward_low_{signal.risk_reward_ratio:.2f}")
            
            # === FILTRO 7: RÉGIMEN DE MERCADO ===
            max_possible_score += 10
            if signal.market_regime in self.config["whitelist_regimes"]:
                filters_passed.append("market_regime_check")
                filter_score += 10
            else:
                filters_failed.append(f"market_regime_{signal.market_regime}")
            
            # === FILTRO 8: COOLDOWN DE SEÑALES ===
            max_possible_score += 5
            cooldown_check = self._check_signal_cooldown(signal)
            if cooldown_check:
                filters_passed.append("cooldown_check")
                filter_score += 5
            else:
                filters_failed.append("signal_too_recent")
            
            # === FILTRO 9: PATRONES BLACKLIST ===
            max_possible_score += 5
            pattern_check = self._check_pattern_blacklist(signal)
            if pattern_check:
                filters_passed.append("pattern_check")
                filter_score += 5
            else:
                filters_failed.append("blacklisted_pattern")
            
            # === FILTRO 10: CORRELACIÓN CON MERCADO ===
            if self.config["enable_correlation_filter"]:
                max_possible_score += 5
                correlation_check = self._check_market_correlation(signal, market_data)
                if correlation_check["passed"]:
                    filters_passed.append("correlation_check")
                    filter_score += 5
                else:
                    filters_failed.append(f"correlation_{correlation_check['reason']}")
            
            # Calcular score final
            final_score = (filter_score / max_possible_score) * 100 if max_possible_score > 0 else 0
            
            # Determinar señal filtrada
            filtered_signal = self._determine_filtered_signal(signal, final_score, filters_failed)
            
            # Evaluar riesgo
            risk_assessment = self._assess_risk(signal, final_score, filters_failed)
            
            # Asignar grado de calidad
            quality_grade = self._assign_quality_grade(final_score, len(filters_passed), len(filters_failed))
            
            # Guardar en historial
            self.signal_history.append({
                "timestamp": signal.timestamp,
                "symbol": signal.symbol,
                "original_signal": signal.signal_type,
                "filtered_signal": filtered_signal,
                "score": final_score
            })
            
            return FilteredSignal(
                original_signal=signal,
                filtered_signal=filtered_signal,
                filter_score=final_score,
                filters_passed=filters_passed,
                filters_failed=filters_failed,
                risk_assessment=risk_assessment,
                quality_grade=quality_grade
            )
            
        except Exception as e:
            logger.error(f"Error filtering signal: {str(e)}")
            # Agregar al historial incluso en caso de error
            self.signal_history.append({
                "timestamp": signal.timestamp,
                "symbol": signal.symbol,
                "original_signal": signal.signal_type,
                "filtered_signal": "HOLD",
                "score": 0
            })
            return FilteredSignal(
                original_signal=signal,
                filtered_signal="HOLD",
                filter_score=0,
                filters_passed=[],
                filters_failed=["filter_error"],
                risk_assessment="HIGH",
                quality_grade="D"
            )
    
    def _check_volatility(self, signal: EnhancedSignal, market_data: pd.DataFrame) -> Dict:
        """Verifica si la volatilidad está en niveles aceptables"""
        try:
            # Calcular volatilidad reciente
            returns = market_data['close'].pct_change().dropna()
            recent_volatility = returns.tail(20).std() * np.sqrt(24 * 365)  # Anualizada
            
            volatility_level = "BAJA" if recent_volatility < 0.3 else \
                              "MEDIA" if recent_volatility < 0.6 else \
                              "ALTA" if recent_volatility < 1.0 else "MUY_ALTA"
            
            passed = recent_volatility <= self.config["max_volatility_threshold"]
            
            return {
                "passed": passed,
                "volatility": recent_volatility,
                "level": volatility_level
            }
            
        except Exception:
            return {"passed": True, "volatility": 0, "level": "UNKNOWN"}
    
    def _check_signal_cooldown(self, signal: EnhancedSignal) -> bool:
        """Verifica si ha pasado suficiente tiempo desde la última señal"""
        try:
            if not self.signal_history:
                return True
            
            last_signal_time = max(h["timestamp"] for h in self.signal_history 
                                 if h["symbol"] == signal.symbol)
            
            time_diff = signal.timestamp - last_signal_time
            cooldown_period = timedelta(minutes=self.config["signal_cooldown_minutes"])
            
            return time_diff >= cooldown_period
            
        except Exception:
            return True
    
    def _check_pattern_blacklist(self, signal: EnhancedSignal) -> bool:
        """Verifica si hay patrones en la blacklist"""
        try:
            # Revisar patrones de velas en las notas técnicas
            technical_notes = " ".join(signal.technical_notes).upper()
            
            for blacklisted_pattern in self.config["blacklist_patterns"]:
                if blacklisted_pattern.upper() in technical_notes:
                    return False
            
            return True
            
        except Exception:
            return True
    
    def _check_market_correlation(self, signal: EnhancedSignal, market_data: pd.DataFrame) -> Dict:
        """Verifica correlación con el mercado general"""
        try:
            # Simplificado: verificar si el precio está siguiendo la tendencia general
            recent_trend = market_data['close'].tail(10).pct_change().mean()
            
            if signal.signal == "BUY" and recent_trend < -0.02:  # Mercado bajando fuerte
                return {"passed": False, "reason": "market_downtrend"}
            elif signal.signal == "SELL" and recent_trend > 0.02:  # Mercado subiendo fuerte
                return {"passed": False, "reason": "market_uptrend"}
            
            return {"passed": True, "reason": "correlation_ok"}
            
        except Exception:
            return {"passed": True, "reason": "correlation_unknown"}
    
    def _determine_filtered_signal(self, signal: EnhancedSignal, score: float, failed_filters: List[str]) -> str:
        """Determina la señal final después del filtrado"""
        # Si el score es muy bajo, convertir a HOLD
        if score < 50:
            return "HOLD"
        
        # Si fallan filtros críticos, convertir a HOLD
        critical_failures = [f for f in failed_filters if any(critical in f for critical in 
                           ["confluence_low", "confidence_low", "volatility_high"])]
        
        if critical_failures:
            return "HOLD"
        
        # Si pasa los filtros básicos, mantener la señal original
        return signal.signal_type
    
    def _assess_risk(self, signal: EnhancedSignal, score: float, failed_filters: List[str]) -> str:
        """Evalúa el nivel de riesgo de la señal"""
        risk_factors = 0
        
        # Factores de riesgo
        if score < 70:
            risk_factors += 1
        if signal.market_regime == "VOLATILE":
            risk_factors += 1
        if signal.risk_reward_ratio < 2.0:
            risk_factors += 1
        if len(failed_filters) > 3:
            risk_factors += 1
        if not signal.trend_confirmed:
            risk_factors += 1
        
        if risk_factors >= 4:
            return "HIGH"
        elif risk_factors >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assign_quality_grade(self, score: float, passed_count: int, failed_count: int) -> str:
        """Asigna un grado de calidad a la señal"""
        if score >= 90 and failed_count == 0:
            return "A+"
        elif score >= 85 and failed_count <= 1:
            return "A"
        elif score >= 80 and failed_count <= 2:
            return "B+"
        elif score >= 70 and failed_count <= 3:
            return "B"
        elif score >= 60 and failed_count <= 4:
            return "C+"
        elif score >= 50:
            return "C"
        else:
            return "D"
    
    def get_filter_statistics(self) -> Dict:
        """Obtiene estadísticas del filtrado"""
        if not self.signal_history:
            return {"total_signals": 0}
        
        total_signals = len(self.signal_history)
        filtered_out = sum(1 for h in self.signal_history if h["filtered_signal"] == "HOLD")
        avg_score = np.mean([h["score"] for h in self.signal_history])
        
        return {
            "total_signals": total_signals,
            "signals_filtered_out": filtered_out,
            "filter_rate": (filtered_out / total_signals) * 100,
            "average_score": avg_score,
            "last_24h_signals": len([h for h in self.signal_history 
                                    if (datetime.now() - h["timestamp"]).days < 1])
        }
    
    def update_config(self, new_config: Dict):
        """Actualiza la configuración del filtro"""
        self.config.update(new_config)
        logger.info(f"Filter configuration updated: {new_config}")
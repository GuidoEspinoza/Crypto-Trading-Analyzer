"""🎯 Adaptive Configuration System - Sistema de Configuración Adaptativa
Sistema inteligente que adapta automáticamente los parámetros de trading
basado en condiciones de mercado, rendimiento histórico y perfiles de usuario.

Desarrollado por: Experto en Trading & Programación
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import os

from .technical_config import TechnicalConfig, TradingProfile
from .config_factory import ConfigFactory

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    """Condiciones de mercado para adaptación automática"""
    BULL_MARKET = "BULL_MARKET"
    BEAR_MARKET = "BEAR_MARKET"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    TRENDING = "TRENDING"
    RANGING = "RANGING"

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento para adaptación"""
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: float
    total_trades: int
    last_updated: datetime

@dataclass
class AdaptationRule:
    """Regla de adaptación automática"""
    condition: MarketCondition
    min_performance_threshold: float
    target_profile: TradingProfile
    confidence_adjustment: float
    risk_adjustment: float
    enabled: bool = True

class AdaptiveConfigManager:
    """🎯 Gestor de Configuración Adaptativa
    
    Características principales:
    - Adaptación automática basada en condiciones de mercado
    - Optimización continua de parámetros
    - Perfiles dinámicos según rendimiento
    - Sistema de reglas configurables
    - Historial de adaptaciones
    """
    
    def __init__(self, config_factory: ConfigFactory):
        self.config_factory = config_factory
        self.current_profile = TradingProfile.OPTIMO
        self.adaptation_rules: List[AdaptationRule] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.adaptation_history: List[Dict] = []
        
        # Configuración de adaptación
        self.adaptation_enabled = True
        self.min_trades_for_adaptation = 10
        self.adaptation_cooldown_hours = 4
        self.last_adaptation_time = None
        
        # Cargar configuración persistente
        self._load_adaptive_config()
        self._initialize_default_rules()
        
        logger.info("🎯 AdaptiveConfigManager inicializado")
    
    def _initialize_default_rules(self):
        """Inicializar reglas de adaptación por defecto"""
        default_rules = [
            AdaptationRule(
                condition=MarketCondition.HIGH_VOLATILITY,
                min_performance_threshold=0.6,
                target_profile=TradingProfile.CONSERVADOR,
                confidence_adjustment=-10.0,
                risk_adjustment=-0.5
            ),
            AdaptationRule(
                condition=MarketCondition.BULL_MARKET,
                min_performance_threshold=0.7,
                target_profile=TradingProfile.AGRESIVO,
                confidence_adjustment=5.0,
                risk_adjustment=0.3
            ),
            AdaptationRule(
                condition=MarketCondition.BEAR_MARKET,
                min_performance_threshold=0.5,
                target_profile=TradingProfile.CONSERVADOR,
                confidence_adjustment=-5.0,
                risk_adjustment=-0.3
            ),
            AdaptationRule(
                condition=MarketCondition.TRENDING,
                min_performance_threshold=0.65,
                target_profile=TradingProfile.OPTIMO,
                confidence_adjustment=0.0,
                risk_adjustment=0.1
            ),
            AdaptationRule(
                condition=MarketCondition.RANGING,
                min_performance_threshold=0.6,
                target_profile=TradingProfile.CONSERVADOR,
                confidence_adjustment=-5.0,
                risk_adjustment=-0.2
            )
        ]
        
        if not self.adaptation_rules:
            self.adaptation_rules = default_rules
            logger.info(f"📋 Inicializadas {len(default_rules)} reglas de adaptación por defecto")
    
    def analyze_market_conditions(self, market_data: Dict) -> List[MarketCondition]:
        """Analizar condiciones actuales del mercado"""
        conditions = []
        
        try:
            # Análisis de volatilidad
            volatility = market_data.get('volatility', 0.02)
            if volatility > 0.04:
                conditions.append(MarketCondition.HIGH_VOLATILITY)
            elif volatility < 0.015:
                conditions.append(MarketCondition.LOW_VOLATILITY)
            
            # Análisis de tendencia
            trend_strength = market_data.get('trend_strength', 0.5)
            if trend_strength > 0.7:
                conditions.append(MarketCondition.TRENDING)
            elif trend_strength < 0.3:
                conditions.append(MarketCondition.RANGING)
            
            # Análisis de momentum (bull/bear)
            momentum = market_data.get('momentum', 0.5)
            price_change_24h = market_data.get('price_change_24h', 0.0)
            
            if momentum > 0.7 and price_change_24h > 0.05:
                conditions.append(MarketCondition.BULL_MARKET)
            elif momentum < 0.3 and price_change_24h < -0.05:
                conditions.append(MarketCondition.BEAR_MARKET)
            else:
                conditions.append(MarketCondition.SIDEWAYS)
            
            logger.debug(f"🔍 Condiciones de mercado detectadas: {[c.value for c in conditions]}")
            
        except Exception as e:
            logger.error(f"❌ Error analizando condiciones de mercado: {e}")
            conditions = [MarketCondition.SIDEWAYS]  # Fallback seguro
        
        return conditions
    
    def update_performance_metrics(self, metrics: PerformanceMetrics):
        """Actualizar métricas de rendimiento"""
        self.performance_history.append(metrics)
        
        # Mantener solo las últimas 100 métricas
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        logger.info(f"📊 Métricas actualizadas: WR={metrics.win_rate:.1%}, "
                   f"PF={metrics.profit_factor:.2f}, SR={metrics.sharpe_ratio:.2f}")
    
    def should_adapt(self, current_conditions: List[MarketCondition]) -> bool:
        """Determinar si se debe realizar adaptación"""
        if not self.adaptation_enabled:
            return False
        
        # Verificar cooldown
        if (self.last_adaptation_time and 
            datetime.now() - self.last_adaptation_time < timedelta(hours=self.adaptation_cooldown_hours)):
            return False
        
        # Verificar mínimo de trades
        if not self.performance_history:
            return False
        
        latest_metrics = self.performance_history[-1]
        if latest_metrics.total_trades < self.min_trades_for_adaptation:
            return False
        
        # Verificar si hay reglas aplicables
        applicable_rules = [
            rule for rule in self.adaptation_rules
            if rule.enabled and rule.condition in current_conditions
        ]
        
        return len(applicable_rules) > 0
    
    def adapt_configuration(self, market_conditions: List[MarketCondition]) -> Optional[TradingProfile]:
        """Adaptar configuración basada en condiciones de mercado"""
        if not self.should_adapt(market_conditions):
            return None
        
        try:
            latest_metrics = self.performance_history[-1]
            
            # Encontrar la mejor regla aplicable
            best_rule = None
            best_score = -1
            
            for rule in self.adaptation_rules:
                if not rule.enabled or rule.condition not in market_conditions:
                    continue
                
                # Calcular score basado en rendimiento y condiciones
                performance_score = min(latest_metrics.win_rate, latest_metrics.profit_factor / 2.0)
                
                if performance_score >= rule.min_performance_threshold:
                    score = performance_score + (0.1 if rule.target_profile != self.current_profile else 0)
                    
                    if score > best_score:
                        best_score = score
                        best_rule = rule
            
            if best_rule and best_rule.target_profile != self.current_profile:
                old_profile = self.current_profile
                self.current_profile = best_rule.target_profile
                
                # Aplicar ajustes dinámicos
                self._apply_dynamic_adjustments(best_rule)
                
                # Registrar adaptación
                adaptation_record = {
                    'timestamp': datetime.now().isoformat(),
                    'from_profile': old_profile.value,
                    'to_profile': self.current_profile.value,
                    'trigger_condition': best_rule.condition.value,
                    'performance_metrics': asdict(latest_metrics),
                    'confidence_adjustment': best_rule.confidence_adjustment,
                    'risk_adjustment': best_rule.risk_adjustment
                }
                
                self.adaptation_history.append(adaptation_record)
                self.last_adaptation_time = datetime.now()
                
                logger.info(f"🎯 Adaptación realizada: {old_profile.value} → {self.current_profile.value} "
                           f"(Condición: {best_rule.condition.value})")
                
                # Guardar configuración
                self._save_adaptive_config()
                
                return self.current_profile
            
        except Exception as e:
            logger.error(f"❌ Error durante adaptación: {e}")
        
        return None
    
    def _apply_dynamic_adjustments(self, rule: AdaptationRule):
        """Aplicar ajustes dinámicos a la configuración actual"""
        try:
            current_config = self.config_factory.get_config(self.current_profile)
            
            # Ajustar confianza mínima
            if hasattr(current_config, 'strategies'):
                current_config.strategies.min_confidence += rule.confidence_adjustment
                current_config.strategies.min_confidence = max(30.0, min(90.0, current_config.strategies.min_confidence))
            
            # Ajustar parámetros de riesgo
            if hasattr(current_config, 'risk_management'):
                current_config.risk_management.max_risk_per_trade *= (1 + rule.risk_adjustment)
                current_config.risk_management.max_risk_per_trade = max(0.005, min(0.05, current_config.risk_management.max_risk_per_trade))
            
            # Actualizar configuración en factory
            self.config_factory._configs[self.current_profile] = current_config
            
            logger.debug(f"🔧 Ajustes dinámicos aplicados: confianza={rule.confidence_adjustment:+.1f}, "
                        f"riesgo={rule.risk_adjustment:+.1%}")
            
        except Exception as e:
            logger.error(f"❌ Error aplicando ajustes dinámicos: {e}")
    
    def get_adaptation_summary(self) -> Dict:
        """Obtener resumen de adaptaciones realizadas"""
        return {
            'current_profile': self.current_profile.value,
            'adaptation_enabled': self.adaptation_enabled,
            'total_adaptations': len(self.adaptation_history),
            'last_adaptation': self.adaptation_history[-1] if self.adaptation_history else None,
            'performance_history_count': len(self.performance_history),
            'active_rules': len([r for r in self.adaptation_rules if r.enabled])
        }
    
    def _load_adaptive_config(self):
        """Cargar configuración adaptativa desde archivo"""
        config_file = "adaptive_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                
                # Cargar perfil actual
                if 'current_profile' in data:
                    self.current_profile = TradingProfile(data['current_profile'])
                
                # Cargar historial de adaptaciones
                if 'adaptation_history' in data:
                    self.adaptation_history = data['adaptation_history'][-50:]  # Últimas 50
                
                logger.info(f"📁 Configuración adaptativa cargada desde {config_file}")
                
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar configuración adaptativa: {e}")
    
    def _save_adaptive_config(self):
        """Guardar configuración adaptativa a archivo"""
        config_file = "adaptive_config.json"
        try:
            data = {
                'current_profile': self.current_profile.value,
                'adaptation_history': self.adaptation_history[-50:],  # Últimas 50
                'last_updated': datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"💾 Configuración adaptativa guardada en {config_file}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando configuración adaptativa: {e}")

# Función de conveniencia para obtener el gestor adaptativo
_adaptive_manager = None

def get_adaptive_manager(config_factory: Optional[ConfigFactory] = None) -> AdaptiveConfigManager:
    """Obtener instancia singleton del gestor adaptativo"""
    global _adaptive_manager
    
    if _adaptive_manager is None:
        if config_factory is None:
            from .config_factory import get_config_factory
            config_factory = get_config_factory()
        
        _adaptive_manager = AdaptiveConfigManager(config_factory)
    
    return _adaptive_manager
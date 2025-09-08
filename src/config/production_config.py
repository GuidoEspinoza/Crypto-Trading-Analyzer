#!/usr/bin/env python3
"""
🏭 Configuración de Producción - Crypto Trading Analyzer

Configuración centralizada y optimizada para ambiente de producción.
Combina perfiles de trading dinámicos con configuraciones de sistema robustas.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path

# ============================================================================
# 🎯 CONFIGURACIÓN PRINCIPAL DE PRODUCCIÓN
# ============================================================================

# Perfil de trading activo (cambiar aquí para modificar comportamiento)
TRADING_PROFILE = os.getenv("TRADING_PROFILE", "OPTIMO")

# Balance inicial global
GLOBAL_INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "1000.0"))

# ============================================================================
# 📊 PERFILES DE TRADING OPTIMIZADOS
# ============================================================================

class ProductionTradingProfiles:
    """Perfiles de trading optimizados para producción."""
    
    PROFILES = {
        "CONSERVADOR": {
            "name": "🛡️ Conservador",
            "description": "Máxima seguridad, timeframes largos",
            "timeframes": ["4h", "1d"],
            "analysis_interval": 60,  # 1 hora
            "min_confidence": 75.0,
            "max_daily_trades": 3,
            "max_positions": 3,
            "position_size_percent": 0.015,  # 1.5%
            "max_consecutive_losses": 3,
            "circuit_breaker_cooldown_hours": 6,
            "max_drawdown_threshold": 8.0,
            "initial_tp_percent": 0.025,  # 2.5%
            "initial_sl_percent": 0.008,  # 0.8%
            "ATR_MULTIPLIER_MIN": 1.8,
            "ATR_MULTIPLIER_MAX": 3.2,
            "VOLATILITY_THRESHOLD": 0.015,
        },
        
        "OPTIMO": {
            "name": "⚖️ Óptimo",
            "description": "Balance perfecto riesgo-rendimiento",
            "timeframes": ["1h", "4h"],
            "analysis_interval": 30,  # 30 minutos
            "min_confidence": 70.0,
            "max_daily_trades": 8,
            "max_positions": 5,
            "position_size_percent": 0.02,  # 2%
            "max_consecutive_losses": 5,
            "circuit_breaker_cooldown_hours": 3,
            "max_drawdown_threshold": 10.0,
            "initial_tp_percent": 0.02,  # 2%
            "initial_sl_percent": 0.01,  # 1%
            "ATR_MULTIPLIER_MIN": 1.5,
            "ATR_MULTIPLIER_MAX": 2.8,
            "VOLATILITY_THRESHOLD": 0.02,
        },
        
        "AGRESIVO": {
            "name": "⚡ Agresivo",
            "description": "Mayor frecuencia, riesgo controlado",
            "timeframes": ["15m", "1h"],
            "analysis_interval": 15,  # 15 minutos
            "min_confidence": 65.0,
            "max_daily_trades": 15,
            "max_positions": 8,
            "position_size_percent": 0.025,  # 2.5%
            "max_consecutive_losses": 6,
            "circuit_breaker_cooldown_hours": 2,
            "max_drawdown_threshold": 12.0,
            "initial_tp_percent": 0.018,  # 1.8%
            "initial_sl_percent": 0.012,  # 1.2%
            "ATR_MULTIPLIER_MIN": 1.2,
            "ATR_MULTIPLIER_MAX": 2.5,
            "VOLATILITY_THRESHOLD": 0.025,
        }
    }

# ============================================================================
# 🏗️ CONFIGURACIONES DE SISTEMA
# ============================================================================

@dataclass
class ExchangeConfig:
    """Configuración del exchange."""
    exchange: str = "binance"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    testnet: bool = True
    rate_limit: int = 1200  # requests per minute
    timeout: int = 30  # seconds
    
    def __post_init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.testnet = os.getenv("USE_TESTNET", "true").lower() == "true"

@dataclass
class DatabaseConfig:
    """Configuración de base de datos."""
    db_type: str = "sqlite"
    db_path: str = "src/database/trading_bot.db"
    connection_pool_size: int = 5
    connection_timeout: int = 30
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    
    def __post_init__(self):
        self.db_path = os.getenv("DATABASE_PATH", self.db_path)
        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

@dataclass
class SecurityConfig:
    """Configuración de seguridad."""
    max_api_calls_per_minute: int = 1000
    enable_ip_whitelist: bool = False
    allowed_ips: List[str] = None
    enable_2fa: bool = False
    session_timeout_minutes: int = 60
    
    def __post_init__(self):
        if self.allowed_ips is None:
            self.allowed_ips = []

@dataclass
class MonitoringConfig:
    """Configuración de monitoreo."""
    log_level: str = "INFO"
    log_file_path: str = "logs/production.log"
    max_log_file_size_mb: int = 100
    log_backup_count: int = 10
    enable_metrics: bool = True
    metrics_interval_seconds: int = 60
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    
    def __post_init__(self):
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        # Crear directorio de logs
        Path(self.log_file_path).parent.mkdir(parents=True, exist_ok=True)

@dataclass
class RiskConfig:
    """Configuración de gestión de riesgo."""
    max_daily_loss_percent: float = 5.0
    max_total_drawdown_percent: float = 15.0
    position_size_limit_percent: float = 10.0  # % del portfolio por posición
    max_correlation_threshold: float = 0.7
    enable_emergency_stop: bool = True
    emergency_stop_loss_percent: float = 20.0
    
    def __post_init__(self):
        # Ajustar según variables de entorno
        self.max_daily_loss_percent = float(os.getenv("MAX_DAILY_LOSS", str(self.max_daily_loss_percent)))
        self.max_total_drawdown_percent = float(os.getenv("MAX_DRAWDOWN", str(self.max_total_drawdown_percent)))

# ============================================================================
# 🎛️ CONFIGURACIÓN PRINCIPAL
# ============================================================================

class ProductionConfig:
    """Configuración principal de producción."""
    
    def __init__(self):
        # Cargar perfil de trading
        self.trading_profile = TRADING_PROFILE
        self.profile_config = ProductionTradingProfiles.PROFILES.get(
            self.trading_profile, 
            ProductionTradingProfiles.PROFILES["OPTIMO"]
        )
        
        # Configuraciones de sistema
        self.exchange = ExchangeConfig()
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.risk = RiskConfig()
        
        # Símbolos de trading
        self.symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT",
            "ADAUSDT", "XRPUSDT", "LINKUSDT", "DOGEUSDT", "TRXUSDT",
            "DOTUSDT", "MATICUSDT", "ATOMUSDT", "NEARUSDT", "SUIUSDT"
        ]
        
        # Balance inicial
        self.initial_balance = GLOBAL_INITIAL_BALANCE
        
    def get_profile_setting(self, key: str, default=None):
        """Obtener configuración del perfil activo."""
        return self.profile_config.get(key, default)
    
    def is_production(self) -> bool:
        """Verificar si estamos en ambiente de producción."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    def validate_config(self) -> bool:
        """Validar configuración antes del inicio."""
        try:
            # Validar perfil de trading
            if self.trading_profile not in ProductionTradingProfiles.PROFILES:
                raise ValueError(f"Perfil de trading inválido: {self.trading_profile}")
            
            # Validar balance inicial
            if self.initial_balance <= 0:
                raise ValueError("Balance inicial debe ser mayor a 0")
            
            # Validar configuración de exchange en producción
            if self.is_production() and not self.exchange.api_key:
                raise ValueError("API Key requerida en producción")
            
            return True
            
        except Exception as e:
            print(f"❌ Error de configuración: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario."""
        return {
            "trading_profile": self.trading_profile,
            "profile_config": self.profile_config,
            "symbols": self.symbols,
            "initial_balance": self.initial_balance,
            "is_production": self.is_production(),
            "exchange": self.exchange.__dict__,
            "database": self.database.__dict__,
            "security": self.security.__dict__,
            "monitoring": self.monitoring.__dict__,
            "risk": self.risk.__dict__
        }

# ============================================================================
# 🚀 INSTANCIA GLOBAL
# ============================================================================

# Instancia global de configuración
production_config = ProductionConfig()

# Alias para compatibilidad
TradingProfiles = ProductionTradingProfiles
TRADING_PROFILE = production_config.trading_profile

# Función de utilidad para obtener configuración
def get_config() -> ProductionConfig:
    """Obtener instancia de configuración."""
    return production_config

# Función para cambiar perfil dinámicamente
def set_trading_profile(profile: str) -> bool:
    """Cambiar perfil de trading dinámicamente."""
    global production_config
    if profile in ProductionTradingProfiles.PROFILES:
        production_config.trading_profile = profile
        production_config.profile_config = ProductionTradingProfiles.PROFILES[profile]
        return True
    return False
#!/usr/bin/env python3
"""
🛠️ Database CLI Configuration - Crypto Trading Analyzer

Configuración parametrizada para el CLI de gestión de base de datos.
Permite personalizar comportamientos sin modificar código fuente.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path
import os

# Importar configuraciones globales
from .trading_bot_config import GLOBAL_INITIAL_BALANCE

@dataclass
class CLICleanupConfig:
    """Configuración para operaciones de limpieza."""
    default_cleanup_days: int = 30
    max_cleanup_days: int = 365
    min_cleanup_days: int = 1
    old_trades_retention_days: int = 90
    signals_retention_days: int = 30
    
    def validate(self) -> bool:
        """Validar configuración de limpieza."""
        return (
            self.min_cleanup_days <= self.default_cleanup_days <= self.max_cleanup_days
            and self.old_trades_retention_days > 0
            and self.signals_retention_days > 0
        )

@dataclass
class CLIBackupConfig:
    """Configuración para operaciones de backup."""
    default_backup_dir: str = "backups"
    pre_reset_backup_dir: str = "backups/pre_reset"
    backup_filename_format: str = "trading_bot_backup_{timestamp}.db"
    current_backup_format: str = "{db_path}.backup_{timestamp}"
    auto_backup_before_operations: bool = True
    max_backup_files: int = 10
    
    def get_backup_path(self, base_dir: Optional[str] = None) -> Path:
        """Obtener ruta de directorio de backup."""
        return Path(base_dir or self.default_backup_dir)

@dataclass
class CLIDisplayConfig:
    """Configuración para visualización y formato."""
    stats_separator: str = "=" * 40
    use_emojis: bool = True
    show_file_sizes_in_kb: bool = True
    decimal_places: int = 1
    date_format: str = "%Y%m%d_%H%M%S"
    
    # Emojis para diferentes operaciones
    emoji_migrate: str = "🔄"
    emoji_success: str = "✅"
    emoji_error: str = "❌"
    emoji_warning: str = "⚠️"
    emoji_stats: str = "📊"
    emoji_backup: str = "📁"
    emoji_cleanup: str = "🧹"
    emoji_optimize: str = "🔧"
    emoji_reset: str = "💥"
    emoji_trades: str = "💰"
    emoji_portfolio: str = "📈"
    emoji_strategies: str = "🧠"
    emoji_signals: str = "📡"
    emoji_backtests: str = "🔬"
    emoji_database: str = "💾"
    emoji_stop: str = "⏹️"

@dataclass
class CLIOperationConfig:
    """Configuración para operaciones específicas."""
    vacuum_show_size_comparison: bool = True
    reset_confirmation_text: str = "CONFIRMAR"
    stats_recent_signals_days: int = 7
    enable_pre_operation_backup: bool = True
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"

@dataclass
class CLIPerformanceConfig:
    """Configuración para optimización de rendimiento."""
    batch_size_cleanup: int = 1000
    enable_progress_indicators: bool = True
    vacuum_analyze_after: bool = True
    optimize_queries: bool = True

@dataclass
class DatabaseCLIConfig:
    """Configuración principal para Database CLI."""
    cleanup: CLICleanupConfig
    backup: CLIBackupConfig
    display: CLIDisplayConfig
    operations: CLIOperationConfig
    performance: CLIPerformanceConfig
    
    # Configuración de base de datos
    default_db_path: Optional[str] = None
    enable_foreign_keys: bool = True
    
    def __init__(
        self,
        cleanup: Optional[CLICleanupConfig] = None,
        backup: Optional[CLIBackupConfig] = None,
        display: Optional[CLIDisplayConfig] = None,
        operations: Optional[CLIOperationConfig] = None,
        performance: Optional[CLIPerformanceConfig] = None,
        **kwargs
    ):
        self.cleanup = cleanup or CLICleanupConfig()
        self.backup = backup or CLIBackupConfig()
        self.display = display or CLIDisplayConfig()
        self.operations = operations or CLIOperationConfig()
        self.performance = performance or CLIPerformanceConfig()
        
        # Aplicar kwargs adicionales
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def validate(self) -> bool:
        """Validar toda la configuración."""
        return (
            self.cleanup.validate()
            and isinstance(self.backup.max_backup_files, int)
            and self.backup.max_backup_files > 0
            and self.performance.batch_size_cleanup > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario."""
        return {
            'cleanup': asdict(self.cleanup),
            'backup': asdict(self.backup),
            'display': asdict(self.display),
            'operations': asdict(self.operations),
            'performance': asdict(self.performance),
            'default_db_path': self.default_db_path,
            'enable_foreign_keys': self.enable_foreign_keys
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DatabaseCLIConfig':
        """Crear configuración desde diccionario."""
        return cls(
            cleanup=CLICleanupConfig(**config_dict.get('cleanup', {})),
            backup=CLIBackupConfig(**config_dict.get('backup', {})),
            display=CLIDisplayConfig(**config_dict.get('display', {})),
            operations=CLIOperationConfig(**config_dict.get('operations', {})),
            performance=CLIPerformanceConfig(**config_dict.get('performance', {})),
            default_db_path=config_dict.get('default_db_path'),
            enable_foreign_keys=config_dict.get('enable_foreign_keys', True)
        )

# Perfiles predefinidos
CLI_PROFILES = {
    'development': DatabaseCLIConfig(
        cleanup=CLICleanupConfig(
            default_cleanup_days=7,
            old_trades_retention_days=30,
            signals_retention_days=7
        ),
        backup=CLIBackupConfig(
            auto_backup_before_operations=True,
            max_backup_files=5
        ),
        operations=CLIOperationConfig(
            enable_pre_operation_backup=True,
            stats_recent_signals_days=3
        ),
        performance=CLIPerformanceConfig(
            batch_size_cleanup=500,
            enable_progress_indicators=True
        )
    ),
    
    'production': DatabaseCLIConfig(
        cleanup=CLICleanupConfig(
            default_cleanup_days=30,
            old_trades_retention_days=180,
            signals_retention_days=30
        ),
        backup=CLIBackupConfig(
            auto_backup_before_operations=True,
            max_backup_files=20
        ),
        operations=CLIOperationConfig(
            enable_pre_operation_backup=True,
            stats_recent_signals_days=7
        ),
        performance=CLIPerformanceConfig(
            batch_size_cleanup=2000,
            enable_progress_indicators=False
        )
    ),
    
    'testing': DatabaseCLIConfig(
        cleanup=CLICleanupConfig(
            default_cleanup_days=1,
            old_trades_retention_days=7,
            signals_retention_days=1
        ),
        backup=CLIBackupConfig(
            auto_backup_before_operations=False,
            max_backup_files=3
        ),
        display=CLIDisplayConfig(
            use_emojis=False
        ),
        operations=CLIOperationConfig(
            enable_pre_operation_backup=False,
            stats_recent_signals_days=1
        ),
        performance=CLIPerformanceConfig(
            batch_size_cleanup=100,
            enable_progress_indicators=False
        )
    )
}

# Configuración por defecto
DEFAULT_CLI_CONFIG = CLI_PROFILES['development']

def get_cli_config(profile: str = 'development') -> DatabaseCLIConfig:
    """Obtener configuración CLI por perfil."""
    if profile not in CLI_PROFILES:
        raise ValueError(f"Perfil desconocido: {profile}. Disponibles: {list(CLI_PROFILES.keys())}")
    
    config = CLI_PROFILES[profile]
    
    # Validar configuración
    if not config.validate():
        raise ValueError(f"Configuración inválida para perfil: {profile}")
    
    return config

def get_cli_config_from_env() -> DatabaseCLIConfig:
    """Obtener configuración CLI desde variables de entorno."""
    profile = os.getenv('CLI_PROFILE', 'development')
    return get_cli_config(profile)
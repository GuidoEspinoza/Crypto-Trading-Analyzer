#!/usr/bin/env python3
"""📊 Configuración del Trading Monitor

Este módulo contiene todas las configuraciones parametrizadas para el Trading Monitor,
eliminando parámetros hardcodeados y permitiendo personalización completa.

Clases principales:
- DisplayFormatsConfig: Configuración de formatos de display
- PrecisionConfig: Configuración de precisión numérica
- AlertsConfig: Configuración de alertas y notificaciones
- APIConfig: Configuración de APIs y timeouts
- MessagesConfig: Configuración de mensajes y textos
- TradingMonitorConfig: Configuración principal del monitor

Características:
- Configuración completamente parametrizada
- Soporte para múltiples perfiles
- Actualización dinámica de configuración
- Serialización/deserialización JSON
- Validación de parámetros
- Configuración de emojis personalizable
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class DisplayFormatsConfig:
    """🎨 Configuración de formatos de display"""
    
    # Formatos de fecha y hora
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    date_format: str = "%Y-%m-%d %H:%M"
    detailed_timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Separadores y líneas
    main_separator: str = "=" * 55
    section_separator: str = "-" * 40
    subsection_separator: str = "-" * 30
    detailed_separator: str = "-" * 50
    monitoring_separator: str = "-" * 45
    
    # Anchos de separadores personalizables
    main_separator_width: int = 55
    section_separator_width: int = 40
    subsection_separator_width: int = 30
    detailed_separator_width: int = 50
    monitoring_separator_width: int = 45
    
    def __post_init__(self):
        """Generar separadores dinámicamente basados en anchos"""
        self.main_separator = "=" * self.main_separator_width
        self.section_separator = "-" * self.section_separator_width
        self.subsection_separator = "-" * self.subsection_separator_width
        self.detailed_separator = "-" * self.detailed_separator_width
        self.monitoring_separator = "-" * self.monitoring_separator_width

@dataclass
class PrecisionConfig:
    """🔢 Configuración de precisión numérica"""
    
    # Decimales para precios
    price_decimals: int = 4
    usdt_decimals: int = 2
    percentage_decimals: int = 2
    quantity_decimals: int = 4
    distance_decimals: int = 2
    pnl_decimals: int = 2
    value_decimals: int = 2  # Para valores monetarios generales
    
    # Formatos de números
    price_format: str = "${:.4f}"
    usdt_format: str = "${:.2f}"
    percentage_format: str = "{:.2f}%"
    signed_percentage_format: str = "{:+.2f}%"
    signed_usdt_format: str = "{:+.2f}"
    quantity_format: str = "{:.4f}"
    
    def __post_init__(self):
        """Generar formatos dinámicamente basados en decimales"""
        self.price_format = f"${{:.{self.price_decimals}f}}"
        self.usdt_format = f"${{:.{self.usdt_decimals}f}}"
        self.percentage_format = f"{{:.{self.percentage_decimals}f}}%"
        self.signed_percentage_format = f"{{:+.{self.percentage_decimals}f}}%"
        self.signed_usdt_format = f"{{:+.{self.usdt_decimals}f}}"
        self.quantity_format = f"{{:.{self.quantity_decimals}f}}"

@dataclass
class EmojiConfig:
    """😀 Configuración de emojis"""
    
    enabled: bool = True
    
    # Emojis principales
    monitor: str = "🔍"
    chart: str = "📊"
    clock: str = "🕐"
    clipboard: str = "📋"
    calendar: str = "📅"
    search: str = "🔍"
    target: str = "🎯"
    money: str = "💰"
    refresh: str = "🔄"
    
    # Estados
    success: str = "✅"
    error: str = "❌"
    warning: str = "⚠️"
    critical: str = "🔴"
    info: str = "🟡"
    alert: str = "🚨"
    
    # Trading
    profit_green: str = "💚"
    loss_red: str = "❤️"
    neutral_yellow: str = "💛"
    trending_up: str = "📈"
    trending_down: str = "📉"
    shield: str = "🛡️"
    portfolio: str = "💼"
    
    # Acciones
    rocket: str = "🚀"
    lightbulb: str = "💡"
    memory: str = "💾"
    
    def __post_init__(self):
        """Desactivar emojis si está deshabilitado"""
        if not self.enabled:
            for attr_name in dir(self):
                if not attr_name.startswith('_') and attr_name != 'enabled':
                    setattr(self, attr_name, "")

@dataclass
class AlertsConfig:
    """🚨 Configuración de alertas y notificaciones"""
    
    # Umbrales de alertas
    critical_pending_executions: int = 5
    warning_positions_without_tp: int = 3
    warning_positions_without_sl: int = 3
    critical_positions_without_both: int = 1
    
    # Configuración de alertas
    show_tp_alerts: bool = True
    show_sl_alerts: bool = True
    show_pending_execution_alerts: bool = True
    show_missing_protection_alerts: bool = True
    show_recommendations: bool = True
    
    # Timeouts y reintentos
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

@dataclass
class APIConfig:
    """🌐 Configuración de APIs"""
    
    # Timeouts
    request_timeout: float = 10.0
    price_request_timeout: float = 5.0
    
    # Reintentos
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Cache
    price_cache_ttl: int = 30  # segundos
    enable_price_cache: bool = True
    
    # Display de errores
    show_api_errors: bool = True

@dataclass
class MessagesConfig:
    """💬 Configuración de mensajes y textos"""
    
    # Títulos principales
    main_title: str = "MONITOR INTEGRAL DEL SISTEMA DE TRADING"
    status_title: str = "VERIFICACIÓN DE ESTADO GENERAL"
    missed_executions_title: str = "VERIFICACIÓN DE EJECUCIONES PERDIDAS"
    detailed_analysis_title: str = "ANÁLISIS DETALLADO COMPLETO"
    
    # Secciones
    active_positions_title: str = "POSICIONES ACTIVAS"
    tp_sl_config_title: str = "VERIFICACIÓN DE CONFIGURACIÓN TP/SL"
    current_prices_title: str = "VERIFICACIÓN DE PRECIOS ACTUALES"
    monitoring_system_title: str = "VERIFICACIÓN DEL SISTEMA DE MONITOREO"
    configuration_summary_title: str = "RESUMEN DE CONFIGURACIÓN"
    
    # Mensajes de estado
    no_active_positions: str = "No hay posiciones activas"
    no_missed_executions: str = "No se detectaron ejecuciones perdidas en las últimas {hours} horas"
    all_positions_monitored: str = "Todas las posiciones están siendo monitoreadas correctamente"
    verification_completed: str = "Verificación completada"
    
    # Mensajes de error
    error_during_verification: str = "Error durante la verificación"
    error_showing_positions: str = "Error mostrando posiciones activas"
    error_checking_positions: str = "Error verificando posiciones"
    error_checking_config: str = "Error verificando configuración"
    error_checking_prices: str = "Error verificando precios"
    error_checking_monitoring: str = "Error verificando sistema de monitoreo"
    
    # Alertas y recomendaciones
    positions_without_protection: str = "ADVERTENCIA: Posiciones sin protección adecuada"
    critical_unprotected_positions: str = "CRÍTICO: {count} posiciones sin TP ni SL"
    unprotected_positions_message: str = "Estas posiciones están completamente desprotegidas"
    no_take_profit_message: str = "{count} posiciones sin Take Profit"
    no_stop_loss_message: str = "{count} posiciones sin Stop Loss"
    no_automatic_gains: str = "No se capturarán ganancias automáticamente"
    no_loss_protection: str = "No hay protección contra pérdidas"
    
    recommendation_title: str = "RECOMENDACIÓN"
    fix_missing_tp_sl_command: str = "Ejecuta: python src/tools/fix_missing_tp_sl.py"
    fix_missing_tp_sl_description: str = "Para configurar automáticamente TP/SL faltantes"
    
    critical_alert_pending: str = "ALERTA CRÍTICA: {count} ejecuciones pendientes"
    execution_system_problems: str = "El sistema de ejecución automática puede tener problemas"
    check_position_manager_logs: str = "Revisa los logs del position_manager"
    
    # Labels de campos
    entry_label: str = "Entry"
    current_label: str = "Current"
    tp_label: str = "TP"
    sl_label: str = "SL"
    pnl_label: str = "PnL"
    quantity_label: str = "Quantity"
    strategy_label: str = "Strategy"
    opened_label: str = "Opened"
    distance_label: str = "Distance"
    
    # Etiquetas de resumen
    total_positions_label: str = "Total posiciones"
    positions_with_tp_sl_label: str = "Posiciones con TP/SL"
    without_tp_label: str = "Sin TP configurado"
    without_sl_label: str = "Sin SL configurado"
    without_both_label: str = "Sin TP ni SL"
    pending_executions_label: str = "Ejecuciones pendientes"
    total_pnl_label: str = "PnL total actual"
    total_portfolio_label: str = "TOTAL PORTAFOLIO"
    
    # Potenciales
    potential_gain_label: str = "Ganancia potencial"
    potential_loss_label: str = "Pérdida potencial"
    tp_distance_label: str = "TP Distance"
    sl_distance_label: str = "SL Distance"
    
    # Estados de configuración
    not_configured: str = "No configurado"
    not_available: str = "N/A"
    active_status: str = "Activo"
    
    # Estadísticas del sistema
    position_manager_active: str = "Position Manager: Activo"
    monitored_positions_label: str = "Posiciones monitoreadas"
    position_cache_label: str = "Cache de posiciones"
    cache_entries_label: str = "entradas"
    tp_executed_label: str = "TP ejecutados"
    sl_executed_label: str = "SL ejecutados"

@dataclass
class AnalysisConfig:
    """📈 Configuración de análisis"""
    
    # Configuración de análisis detallado
    show_trade_details: bool = True
    show_pnl_calculations: bool = True
    show_distance_calculations: bool = True
    show_potential_gains_losses: bool = True
    show_portfolio_summary: bool = True
    
    # Configuración de resúmenes
    show_configuration_summary: bool = True
    show_protection_warnings: bool = True
    show_execution_alerts: bool = True
    show_recommendations: bool = True
    
    # Límites de display
    max_positions_detailed: int = 50
    max_missed_executions_detailed: int = 20
    max_symbols_price_check: int = 20
    
    # Configuración de ordenamiento
    sort_positions_by_entry_time: bool = True
    sort_descending: bool = True

@dataclass
class TradingMonitorConfig:
    """📊 Configuración principal del Trading Monitor"""
    
    # Configuraciones de componentes
    display_formats: DisplayFormatsConfig = field(default_factory=DisplayFormatsConfig)
    precision: PrecisionConfig = field(default_factory=PrecisionConfig)
    emojis: EmojiConfig = field(default_factory=EmojiConfig)
    alerts: AlertsConfig = field(default_factory=AlertsConfig)
    api: APIConfig = field(default_factory=APIConfig)
    messages: MessagesConfig = field(default_factory=MessagesConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    
    # Configuración general
    default_hours_back: int = 24
    enable_color_output: bool = True
    enable_detailed_logging: bool = False
    
    # Configuración de modos
    available_modes: list = field(default_factory=lambda: ['status', 'missed', 'detailed'])
    default_mode: str = 'status'
    
    def get_display_config(self) -> DisplayFormatsConfig:
        """Obtener configuración de display"""
        return self.display_formats
    
    def get_precision_config(self) -> PrecisionConfig:
        """Obtener configuración de precisión"""
        return self.precision
    
    def get_emoji_config(self) -> EmojiConfig:
        """Obtener configuración de emojis"""
        return self.emojis
    
    def get_alerts_config(self) -> AlertsConfig:
        """Obtener configuración de alertas"""
        return self.alerts
    
    def get_api_config(self) -> APIConfig:
        """Obtener configuración de API"""
        return self.api
    
    def get_messages_config(self) -> MessagesConfig:
        """Obtener configuración de mensajes"""
        return self.messages
    
    def get_analysis_config(self) -> AnalysisConfig:
        """Obtener configuración de análisis"""
        return self.analysis
    
    def update_display_formats(self, **kwargs) -> None:
        """Actualizar configuración de formatos de display"""
        for key, value in kwargs.items():
            if hasattr(self.display_formats, key):
                setattr(self.display_formats, key, value)
        self.display_formats.__post_init__()
    
    def update_precision(self, **kwargs) -> None:
        """Actualizar configuración de precisión"""
        for key, value in kwargs.items():
            if hasattr(self.precision, key):
                setattr(self.precision, key, value)
        self.precision.__post_init__()
    
    def update_emojis(self, **kwargs) -> None:
        """Actualizar configuración de emojis"""
        for key, value in kwargs.items():
            if hasattr(self.emojis, key):
                setattr(self.emojis, key, value)
        self.emojis.__post_init__()
    
    def update_alerts(self, **kwargs) -> None:
        """Actualizar configuración de alertas"""
        for key, value in kwargs.items():
            if hasattr(self.alerts, key):
                setattr(self.alerts, key, value)
    
    def update_api(self, **kwargs) -> None:
        """Actualizar configuración de API"""
        for key, value in kwargs.items():
            if hasattr(self.api, key):
                setattr(self.api, key, value)
    
    def update_messages(self, **kwargs) -> None:
        """Actualizar configuración de mensajes"""
        for key, value in kwargs.items():
            if hasattr(self.messages, key):
                setattr(self.messages, key, value)
    
    def update_analysis(self, **kwargs) -> None:
        """Actualizar configuración de análisis"""
        for key, value in kwargs.items():
            if hasattr(self.analysis, key):
                setattr(self.analysis, key, value)
    
    def disable_emojis(self) -> None:
        """Desactivar todos los emojis"""
        self.emojis.enabled = False
        self.emojis.__post_init__()
    
    def enable_emojis(self) -> None:
        """Activar todos los emojis"""
        self.emojis.enabled = True
        self.emojis.__post_init__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            'display_formats': {
                'timestamp_format': self.display_formats.timestamp_format,
                'date_format': self.display_formats.date_format,
                'detailed_timestamp_format': self.display_formats.detailed_timestamp_format,
                'main_separator_width': self.display_formats.main_separator_width,
                'section_separator_width': self.display_formats.section_separator_width,
                'subsection_separator_width': self.display_formats.subsection_separator_width,
                'detailed_separator_width': self.display_formats.detailed_separator_width,
                'monitoring_separator_width': self.display_formats.monitoring_separator_width
            },
            'precision': {
                'price_decimals': self.precision.price_decimals,
                'usdt_decimals': self.precision.usdt_decimals,
                'percentage_decimals': self.precision.percentage_decimals,
                'quantity_decimals': self.precision.quantity_decimals,
                'distance_decimals': self.precision.distance_decimals,
                'pnl_decimals': self.precision.pnl_decimals
            },
            'emojis': {
                'enabled': self.emojis.enabled,
                'monitor': self.emojis.monitor,
                'chart': self.emojis.chart,
                'clock': self.emojis.clock,
                'clipboard': self.emojis.clipboard,
                'target': self.emojis.target,
                'money': self.emojis.money,
                'refresh': self.emojis.refresh,
                'success': self.emojis.success,
                'error': self.emojis.error,
                'warning': self.emojis.warning,
                'critical': self.emojis.critical,
                'info': self.emojis.info,
                'alert': self.emojis.alert,
                'profit_green': self.emojis.profit_green,
                'loss_red': self.emojis.loss_red,
                'neutral_yellow': self.emojis.neutral_yellow,
                'trending_up': self.emojis.trending_up,
                'trending_down': self.emojis.trending_down,
                'shield': self.emojis.shield,
                'portfolio': self.emojis.portfolio,
                'rocket': self.emojis.rocket,
                'lightbulb': self.emojis.lightbulb,
                'memory': self.emojis.memory
            },
            'alerts': {
                'critical_pending_executions': self.alerts.critical_pending_executions,
                'warning_positions_without_tp': self.alerts.warning_positions_without_tp,
                'warning_positions_without_sl': self.alerts.warning_positions_without_sl,
                'critical_positions_without_both': self.alerts.critical_positions_without_both,
                'show_tp_alerts': self.alerts.show_tp_alerts,
                'show_sl_alerts': self.alerts.show_sl_alerts,
                'show_pending_execution_alerts': self.alerts.show_pending_execution_alerts,
                'show_missing_protection_alerts': self.alerts.show_missing_protection_alerts,
                'show_recommendations': self.alerts.show_recommendations,
                'max_retries': self.alerts.max_retries,
                'retry_delay_seconds': self.alerts.retry_delay_seconds
            },
            'api': {
                'request_timeout': self.api.request_timeout,
                'price_request_timeout': self.api.price_request_timeout,
                'max_retries': self.api.max_retries,
                'retry_delay': self.api.retry_delay,
                'price_cache_ttl': self.api.price_cache_ttl,
                'enable_price_cache': self.api.enable_price_cache
            },
            'analysis': {
                'show_trade_details': self.analysis.show_trade_details,
                'show_pnl_calculations': self.analysis.show_pnl_calculations,
                'show_distance_calculations': self.analysis.show_distance_calculations,
                'show_potential_gains_losses': self.analysis.show_potential_gains_losses,
                'show_portfolio_summary': self.analysis.show_portfolio_summary,
                'show_configuration_summary': self.analysis.show_configuration_summary,
                'show_protection_warnings': self.analysis.show_protection_warnings,
                'show_execution_alerts': self.analysis.show_execution_alerts,
                'show_recommendations': self.analysis.show_recommendations,
                'max_positions_detailed': self.analysis.max_positions_detailed,
                'max_missed_executions_detailed': self.analysis.max_missed_executions_detailed,
                'max_symbols_price_check': self.analysis.max_symbols_price_check,
                'sort_positions_by_entry_time': self.analysis.sort_positions_by_entry_time,
                'sort_descending': self.analysis.sort_descending
            },
            'default_hours_back': self.default_hours_back,
            'enable_color_output': self.enable_color_output,
            'enable_detailed_logging': self.enable_detailed_logging,
            'available_modes': self.available_modes,
            'default_mode': self.default_mode
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingMonitorConfig':
        """Crear configuración desde diccionario"""
        config = cls()
        
        # Actualizar display_formats
        if 'display_formats' in data:
            config.update_display_formats(**data['display_formats'])
        
        # Actualizar precision
        if 'precision' in data:
            config.update_precision(**data['precision'])
        
        # Actualizar emojis
        if 'emojis' in data:
            config.update_emojis(**data['emojis'])
        
        # Actualizar alerts
        if 'alerts' in data:
            config.update_alerts(**data['alerts'])
        
        # Actualizar api
        if 'api' in data:
            config.update_api(**data['api'])
        
        # Actualizar analysis
        if 'analysis' in data:
            config.update_analysis(**data['analysis'])
        
        # Actualizar configuración general
        for key in ['default_hours_back', 'enable_color_output', 'enable_detailed_logging', 
                   'available_modes', 'default_mode']:
            if key in data:
                setattr(config, key, data[key])
        
        return config
    
    def save_to_file(self, filepath: str) -> None:
        """Guardar configuración en archivo JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'TradingMonitorConfig':
        """Cargar configuración desde archivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

# Configuración por defecto
DEFAULT_TRADING_MONITOR_CONFIG = TradingMonitorConfig()

# Perfiles predefinidos
COMPACT_PROFILE = TradingMonitorConfig(
    display_formats=DisplayFormatsConfig(
        main_separator_width=40,
        section_separator_width=25,
        subsection_separator_width=20,
        detailed_separator_width=35,
        monitoring_separator_width=30
    ),
    precision=PrecisionConfig(
        price_decimals=2,
        percentage_decimals=1,
        distance_decimals=1
    ),
    analysis=AnalysisConfig(
        show_potential_gains_losses=False,
        show_distance_calculations=False,
        max_positions_detailed=10
    )
)

DETAILED_PROFILE = TradingMonitorConfig(
    display_formats=DisplayFormatsConfig(
        main_separator_width=80,
        section_separator_width=60,
        subsection_separator_width=50,
        detailed_separator_width=70,
        monitoring_separator_width=65
    ),
    precision=PrecisionConfig(
        price_decimals=6,
        percentage_decimals=3,
        distance_decimals=3
    ),
    analysis=AnalysisConfig(
        show_trade_details=True,
        show_pnl_calculations=True,
        show_distance_calculations=True,
        show_potential_gains_losses=True,
        max_positions_detailed=100
    )
)

NO_EMOJI_PROFILE = TradingMonitorConfig(
    emojis=EmojiConfig(enabled=False)
)

# Función para obtener configuración activa
def get_trading_monitor_config(profile: str = 'default') -> TradingMonitorConfig:
    """Obtener configuración del trading monitor según perfil"""
    profiles = {
        'default': DEFAULT_TRADING_MONITOR_CONFIG,
        'compact': COMPACT_PROFILE,
        'detailed': DETAILED_PROFILE,
        'no_emoji': NO_EMOJI_PROFILE
    }
    
    return profiles.get(profile, DEFAULT_TRADING_MONITOR_CONFIG)
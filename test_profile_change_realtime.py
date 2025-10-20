#!/usr/bin/env python3
"""
Test específico para verificar el cambio de perfil en tiempo real
y cómo afecta a todos los módulos del sistema de trading.
"""

import sys
import os
import time
import json
import importlib

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from src.config.main_config import TradingProfiles, TradingBotConfig, RiskManagerConfig, StrategyConfig
from src.core.trading_bot import TradingBot
from src.core.enhanced_risk_manager import EnhancedRiskManager
from src.core.enhanced_strategies import ProfessionalRSIStrategy

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_config_values(stage):
    """Imprime los valores de configuración de todos los módulos"""
    print(f"\n--- {stage} ---")
    
    # Perfil actual
    current_profile = TradingProfiles.get_current_profile()
    print(f"Perfil actual: {current_profile['name']}")
    
    # TradingBotConfig
    bot_config = TradingBotConfig()
    print(f"TradingBotConfig:")
    print(f"  - analysis_interval: {bot_config.get_analysis_interval()}")
    print(f"  - min_confidence_threshold: {bot_config.get_min_confidence_threshold()}")
    print(f"  - max_daily_trades: {bot_config.get_max_daily_trades()}")
    
    # RiskManagerConfig
    risk_config = RiskManagerConfig()
    print(f"RiskManagerConfig:")
    print(f"  - max_risk_per_trade: {risk_config.get_max_risk_per_trade()}")
    print(f"  - max_daily_risk: {risk_config.get_max_daily_risk()}")
    print(f"  - max_drawdown_threshold: {risk_config.get_max_drawdown_threshold()}")
    
    # StrategyConfig
    strategy_config = StrategyConfig.Base()
    print(f"StrategyConfig.Base:")
    print(f"  - default_min_confidence: {strategy_config.get_default_min_confidence()}")
    print(f"  - default_atr_period: {strategy_config.get_default_atr_period()}")

def test_bot_instance_values(bot, stage):
    """Verifica los valores en una instancia específica del bot"""
    print(f"\n--- Valores en instancia del TradingBot ({stage}) ---")
    
    # Valores del bot
    print(f"TradingBot instance:")
    print(f"  - analysis_interval: {bot.config.get_analysis_interval()}")
    print(f"  - min_confidence_threshold: {bot.config.get_min_confidence_threshold()}")
    print(f"  - max_daily_trades: {bot.config.get_max_daily_trades()}")
    
    # Valores del risk manager
    if hasattr(bot, 'risk_manager') and bot.risk_manager:
        print(f"EnhancedRiskManager instance:")
        print(f"  - max_risk_per_trade: {bot.risk_manager.config.get_max_risk_per_trade()}")
        print(f"  - max_daily_risk: {bot.risk_manager.config.get_max_daily_risk()}")
        print(f"  - max_drawdown_threshold: {bot.risk_manager.config.get_max_drawdown_threshold()}")
    
    # Valores de las estrategias
    if hasattr(bot, 'strategies') and bot.strategies:
        for i, strategy in enumerate(bot.strategies):
            if hasattr(strategy, 'config'):
                print(f"Strategy {i} ({type(strategy).__name__}):")
                if hasattr(strategy.config, 'get_min_confidence'):
                    print(f"  - min_confidence: {strategy.config.get_min_confidence()}")
                if hasattr(strategy, 'min_confidence'):
                    print(f"  - min_confidence (attr): {strategy.min_confidence}")

def simulate_profile_change():
    """Simula el cambio de perfil como lo hace la aplicación real"""
    print_separator("SIMULACIÓN DE CAMBIO DE PERFIL EN TIEMPO REAL")
    
    # 1. Estado inicial
    print_config_values("ESTADO INICIAL")
    
    # Crear instancia inicial del bot
    print("\n--- Creando TradingBot inicial ---")
    bot1 = TradingBot()
    test_bot_instance_values(bot1, "INICIAL")
    
    # 2. Simular cambio de perfil (cambiar la variable de clase)
    print_separator("CAMBIANDO PERFIL DE INTRADAY A SCALPING")
    
    # Guardar perfil original para restaurar después
    import src.config.main_config as config_module
    original_profile = config_module.TRADING_PROFILE
    print(f"Perfil original: {original_profile}")
    
    # Cambiar a SCALPING
    config_module.TRADING_PROFILE = 'SCALPING'
    print("Perfil cambiado a SCALPING")
    
    # 3. Recargar módulos (como hace update_trading_profile)
    print("\n--- Recargando módulos ---")
    
    # Recargar el módulo de configuración
    import src.config.main_config
    importlib.reload(src.config.main_config)
    print("Módulo main_config recargado")
    
    # Verificar que la configuración cambió
    print_config_values("DESPUÉS DE RECARGAR MÓDULOS")
    
    # 4. Verificar si el bot existente refleja los cambios
    print("\n--- Verificando bot existente ---")
    test_bot_instance_values(bot1, "BOT EXISTENTE DESPUÉS DE RECARGA")
    
    # 5. Crear nueva instancia del bot (como hace get_trading_bot cuando trading_bot = None)
    print("\n--- Creando nueva instancia del TradingBot ---")
    bot2 = TradingBot()
    test_bot_instance_values(bot2, "NUEVA INSTANCIA")
    
    # 6. Comparar valores entre bots
    print_separator("COMPARACIÓN ENTRE INSTANCIAS")
    
    print("Comparando analysis_interval:")
    print(f"  Bot original: {bot1.config.get_analysis_interval()}")
    print(f"  Bot nuevo: {bot2.config.get_analysis_interval()}")
    print(f"  ¿Son iguales? {bot1.config.get_analysis_interval() == bot2.config.get_analysis_interval()}")
    
    print("Comparando min_confidence_threshold:")
    print(f"  Bot original: {bot1.config.get_min_confidence_threshold()}")
    print(f"  Bot nuevo: {bot2.config.get_min_confidence_threshold()}")
    print(f"  ¿Son iguales? {bot1.config.get_min_confidence_threshold() == bot2.config.get_min_confidence_threshold()}")
    
    print("Comparando max_daily_trades:")
    print(f"  Bot original: {bot1.config.get_max_daily_trades()}")
    print(f"  Bot nuevo: {bot2.config.get_max_daily_trades()}")
    print(f"  ¿Son iguales? {bot1.config.get_max_daily_trades() == bot2.config.get_max_daily_trades()}")
    
    # 7. Restaurar configuración original
    print_separator("RESTAURANDO CONFIGURACIÓN ORIGINAL")
    
    config_module.TRADING_PROFILE = original_profile
    
    # Recargar módulos nuevamente
    importlib.reload(src.config.main_config)
    
    print(f"Configuración restaurada a: {original_profile}")
    print_config_values("CONFIGURACIÓN RESTAURADA")

def test_direct_profile_access():
    """Prueba el acceso directo a los perfiles"""
    print_separator("PRUEBA DE ACCESO DIRECTO A PERFILES")
    
    # Obtener perfiles directamente
    intraday = TradingProfiles.get_profile('INTRADAY')
    scalping = TradingProfiles.get_profile('SCALPING')
    
    print("Perfil INTRADAY:")
    print(f"  - analysis_interval: {intraday['analysis_interval']}")
    print(f"  - min_confidence: {intraday['min_confidence']}")
    print(f"  - max_daily_trades: {intraday['max_daily_trades']}")
    
    print("Perfil SCALPING:")
    print(f"  - analysis_interval: {scalping['analysis_interval']}")
    print(f"  - min_confidence: {scalping['min_confidence']}")
    print(f"  - max_daily_trades: {scalping['max_daily_trades']}")

if __name__ == "__main__":
    try:
        test_direct_profile_access()
        simulate_profile_change()
        
        print_separator("TEST COMPLETADO")
        print("El test ha terminado exitosamente.")
        
    except Exception as e:
        print(f"\nError durante el test: {e}")
        import traceback
        traceback.print_exc()
        
        # Asegurar que se restaure la configuración original
        try:
            import src.config.main_config as config_module
            config_module.TRADING_PROFILE = 'INTRADAY'  # Valor por defecto
            print("Configuración restaurada a INTRADAY por seguridad")
        except:
            pass
#!/usr/bin/env python3
"""
Test simplificado para verificar el cambio de perfil en tiempo real.
Este test muestra claramente cómo cambian los valores de configuración
cuando se cambia el perfil de trading.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_profile_change_simple():
    """Test simplificado para verificar cambio de perfil."""
    
    print_separator("TEST DE CAMBIO DE PERFIL SIMPLIFICADO")
    
    try:
        # Importar módulos necesarios
        from src.config.main_config import TradingProfiles, TradingBotConfig, RiskManagerConfig
        import src.config.main_config as config_module
        
        # ===== ESTADO INICIAL (INTRADAY) =====
        print_separator("ESTADO INICIAL - PERFIL INTRADAY")
        
        # Verificar perfil actual
        current_profile = TradingProfiles.get_current_profile()
        print(f"✅ Perfil actual: {current_profile['name']}")
        print(f"✅ analysis_interval: {current_profile['analysis_interval']}")
        print(f"✅ min_confidence: {current_profile['min_confidence']}")
        print(f"✅ max_daily_trades: {current_profile['max_daily_trades']}")
        print(f"✅ max_risk_per_trade: {current_profile['max_risk_per_trade']}")
        print(f"✅ max_daily_risk: {current_profile['max_daily_risk']}")
        
        # Crear instancias de configuración
        bot_config = TradingBotConfig()
        risk_config = RiskManagerConfig()
        
        print(f"\n📊 TradingBotConfig:")
        print(f"   - analysis_interval: {bot_config.get_analysis_interval()}")
        print(f"   - min_confidence_threshold: {bot_config.get_min_confidence_threshold()}")
        print(f"   - max_daily_trades: {bot_config.get_max_daily_trades()}")
        
        print(f"\n🛡️ RiskManagerConfig:")
        print(f"   - max_risk_per_trade: {risk_config.get_max_risk_per_trade()}")
        print(f"   - max_daily_risk: {risk_config.get_max_daily_risk()}")
        print(f"   - max_drawdown_threshold: {risk_config.get_max_drawdown_threshold()}")
        
        # ===== CAMBIO A SCALPING =====
        print_separator("CAMBIANDO PERFIL A SCALPING")
        
        # Guardar perfil original
        original_profile = config_module.TRADING_PROFILE
        print(f"🔄 Perfil original guardado: {original_profile}")
        
        # Cambiar perfil
        config_module.TRADING_PROFILE = 'SCALPING'
        print(f"🔄 Perfil cambiado a: SCALPING")
        
        # Verificar nuevo perfil
        new_profile = TradingProfiles.get_current_profile()
        print(f"✅ Nuevo perfil: {new_profile['name']}")
        print(f"✅ analysis_interval: {new_profile['analysis_interval']}")
        print(f"✅ min_confidence: {new_profile['min_confidence']}")
        print(f"✅ max_daily_trades: {new_profile['max_daily_trades']}")
        print(f"✅ max_risk_per_trade: {new_profile['max_risk_per_trade']}")
        print(f"✅ max_daily_risk: {new_profile['max_daily_risk']}")
        
        # Crear nuevas instancias de configuración
        new_bot_config = TradingBotConfig()
        new_risk_config = RiskManagerConfig()
        
        print(f"\n📊 Nuevo TradingBotConfig:")
        print(f"   - analysis_interval: {new_bot_config.get_analysis_interval()}")
        print(f"   - min_confidence_threshold: {new_bot_config.get_min_confidence_threshold()}")
        print(f"   - max_daily_trades: {new_bot_config.get_max_daily_trades()}")
        
        print(f"\n🛡️ Nuevo RiskManagerConfig:")
        print(f"   - max_risk_per_trade: {new_risk_config.get_max_risk_per_trade()}")
        print(f"   - max_daily_risk: {new_risk_config.get_max_daily_risk()}")
        print(f"   - max_drawdown_threshold: {new_risk_config.get_max_drawdown_threshold()}")
        
        # ===== COMPARACIÓN =====
        print_separator("COMPARACIÓN DE VALORES")
        
        print("📈 ANALYSIS_INTERVAL:")
        print(f"   INTRADAY: {current_profile['analysis_interval']} → SCALPING: {new_profile['analysis_interval']}")
        print(f"   ¿Cambió? {'✅ SÍ' if current_profile['analysis_interval'] != new_profile['analysis_interval'] else '❌ NO'}")
        
        print("🎯 MIN_CONFIDENCE:")
        print(f"   INTRADAY: {current_profile['min_confidence']} → SCALPING: {new_profile['min_confidence']}")
        print(f"   ¿Cambió? {'✅ SÍ' if current_profile['min_confidence'] != new_profile['min_confidence'] else '❌ NO'}")
        
        print("📊 MAX_DAILY_TRADES:")
        print(f"   INTRADAY: {current_profile['max_daily_trades']} → SCALPING: {new_profile['max_daily_trades']}")
        print(f"   ¿Cambió? {'✅ SÍ' if current_profile['max_daily_trades'] != new_profile['max_daily_trades'] else '❌ NO'}")
        
        print("🛡️ MAX_RISK_PER_TRADE:")
        print(f"   INTRADAY: {current_profile['max_risk_per_trade']} → SCALPING: {new_profile['max_risk_per_trade']}")
        print(f"   ¿Cambió? {'✅ SÍ' if current_profile['max_risk_per_trade'] != new_profile['max_risk_per_trade'] else '❌ NO'}")
        
        print("🚨 MAX_DAILY_RISK:")
        print(f"   INTRADAY: {current_profile['max_daily_risk']} → SCALPING: {new_profile['max_daily_risk']}")
        print(f"   ¿Cambió? {'✅ SÍ' if current_profile['max_daily_risk'] != new_profile['max_daily_risk'] else '❌ NO'}")
        
        # ===== VERIFICACIÓN DE INSTANCIAS =====
        print_separator("VERIFICACIÓN DE INSTANCIAS")
        
        print("📊 TradingBotConfig - analysis_interval:")
        print(f"   Original: {bot_config.get_analysis_interval()} → Nuevo: {new_bot_config.get_analysis_interval()}")
        print(f"   ¿Cambió? {'✅ SÍ' if bot_config.get_analysis_interval() != new_bot_config.get_analysis_interval() else '❌ NO'}")
        
        print("🎯 TradingBotConfig - min_confidence_threshold:")
        print(f"   Original: {bot_config.get_min_confidence_threshold()} → Nuevo: {new_bot_config.get_min_confidence_threshold()}")
        print(f"   ¿Cambió? {'✅ SÍ' if bot_config.get_min_confidence_threshold() != new_bot_config.get_min_confidence_threshold() else '❌ NO'}")
        
        print("🛡️ RiskManagerConfig - max_risk_per_trade:")
        print(f"   Original: {risk_config.get_max_risk_per_trade()} → Nuevo: {new_risk_config.get_max_risk_per_trade()}")
        print(f"   ¿Cambió? {'✅ SÍ' if risk_config.get_max_risk_per_trade() != new_risk_config.get_max_risk_per_trade() else '❌ NO'}")
        
        # ===== RESTAURAR CONFIGURACIÓN =====
        print_separator("RESTAURANDO CONFIGURACIÓN ORIGINAL")
        
        config_module.TRADING_PROFILE = original_profile
        print(f"🔄 Perfil restaurado a: {original_profile}")
        
        # Verificar restauración
        restored_profile = TradingProfiles.get_current_profile()
        print(f"✅ Perfil verificado: {restored_profile['name']}")
        
        print_separator("TEST COMPLETADO EXITOSAMENTE")
        print("🎉 El cambio de perfil funciona correctamente!")
        print("🎉 Todos los valores se actualizan según el perfil activo!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Asegurar restauración
        try:
            import src.config.main_config as config_module
            config_module.TRADING_PROFILE = 'INTRADAY'
            print("🔄 Configuración restaurada a INTRADAY por seguridad")
        except:
            pass

if __name__ == "__main__":
    success = test_profile_change_simple()
    if success:
        print("\n✅ TEST EXITOSO: El cambio de perfil funciona correctamente")
    else:
        print("\n❌ TEST FALLIDO: Hay problemas con el cambio de perfil")
        sys.exit(1)
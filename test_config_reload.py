#!/usr/bin/env python3
"""
Test específico para verificar la recarga de configuración después de cambiar el perfil.
Este test simula el proceso de cambio de perfil y verifica si los módulos leen la nueva configuración.
"""

import sys
import os
import importlib
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config_reload():
    """Test para verificar la recarga de configuración"""
    print("🔄 Test de Recarga de Configuración")
    print("=" * 50)
    
    try:
        # 1. Importar configuración inicial
        from src.config.main_config import TradingProfiles, TRADING_PROFILE
        print(f"📊 Perfil inicial: {TRADING_PROFILE}")
        
        # Obtener configuración inicial
        initial_config = TradingProfiles.get_current_profile()
        print(f"⚙️ Configuración inicial:")
        print(f"   - analysis_interval: {initial_config['analysis_interval']}")
        print(f"   - min_confidence: {initial_config['min_confidence']}")
        print(f"   - max_daily_trades: {initial_config['max_daily_trades']}")
        
        # 2. Cambiar perfil manualmente (simular cambio de archivo)
        new_profile = "SCALPING" if TRADING_PROFILE == "INTRADAY" else "INTRADAY"
        print(f"\n🔄 Cambiando perfil a: {new_profile}")
        
        # Leer el archivo actual
        config_file = "src/config/main_config.py"
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Hacer backup del contenido original
        original_content = content
        
        # Cambiar el perfil en el contenido
        import re
        pattern = r'TRADING_PROFILE\s*=\s*["\'][^"\']*["\']'
        new_line = f'TRADING_PROFILE = "{new_profile}"'
        updated_content = re.sub(pattern, new_line, content)
        
        # Escribir el archivo modificado
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Archivo modificado: TRADING_PROFILE = '{new_profile}'")
        
        # 3. Recargar el módulo de configuración
        print("\n🔄 Recargando módulo de configuración...")
        import src.config.main_config
        importlib.reload(src.config.main_config)
        
        # 4. Verificar que la configuración cambió
        from src.config.main_config import TradingProfiles, TRADING_PROFILE
        print(f"📊 Perfil después de recarga: {TRADING_PROFILE}")
        
        # Obtener nueva configuración
        new_config = TradingProfiles.get_current_profile()
        print(f"⚙️ Nueva configuración:")
        print(f"   - analysis_interval: {new_config['analysis_interval']}")
        print(f"   - min_confidence: {new_config['min_confidence']}")
        print(f"   - max_daily_trades: {new_config['max_daily_trades']}")
        
        # 5. Verificar que los valores cambiaron
        config_changed = (
            initial_config['analysis_interval'] != new_config['analysis_interval'] or
            initial_config['min_confidence'] != new_config['min_confidence'] or
            initial_config['max_daily_trades'] != new_config['max_daily_trades']
        )
        
        if config_changed:
            print("\n✅ ÉXITO: La configuración se recargó correctamente")
            print("📈 Cambios detectados:")
            if initial_config['analysis_interval'] != new_config['analysis_interval']:
                print(f"   - analysis_interval: {initial_config['analysis_interval']} → {new_config['analysis_interval']}")
            if initial_config['min_confidence'] != new_config['min_confidence']:
                print(f"   - min_confidence: {initial_config['min_confidence']} → {new_config['min_confidence']}")
            if initial_config['max_daily_trades'] != new_config['max_daily_trades']:
                print(f"   - max_daily_trades: {initial_config['max_daily_trades']} → {new_config['max_daily_trades']}")
        else:
            print("\n❌ ERROR: La configuración NO cambió después de la recarga")
        
        # 6. Probar inicialización de módulos con nueva configuración
        print("\n🧪 Probando inicialización de módulos con nueva configuración...")
        
        # Test TradingBot
        try:
            from src.core.trading_bot import TradingBot
            from src.core.paper_trader import PaperTrader
            from src.core.enhanced_risk_manager import EnhancedRiskManager
            
            # Crear instancias para verificar que usan la nueva configuración
            paper_trader = PaperTrader()
            risk_manager = EnhancedRiskManager()
            
            print(f"📊 PaperTrader balance inicial: {getattr(paper_trader, 'balance', 'N/A')}")
            print(f"🛡️ RiskManager max_risk_per_trade: {getattr(risk_manager, 'max_risk_per_trade', 'N/A')}")
            
            # Verificar que los módulos tienen la configuración correcta
            current_profile_config = TradingProfiles.get_current_profile()
            
            modules_test_results = []
            
            # Test Risk Manager
            expected_risk = current_profile_config['risk_manager']['max_risk_per_trade']
            actual_risk = getattr(risk_manager, 'max_risk_per_trade', None)
            risk_ok = abs(expected_risk - actual_risk) < 0.001 if actual_risk else False
            modules_test_results.append(("RiskManager.max_risk_per_trade", expected_risk, actual_risk, risk_ok))
            
            print(f"\n📋 Resultados de verificación de módulos:")
            for module_param, expected, actual, ok in modules_test_results:
                status = "✅" if ok else "❌"
                print(f"   {status} {module_param}: esperado={expected}, actual={actual}")
            
        except Exception as e:
            print(f"❌ Error inicializando módulos: {e}")
        
        # 7. Restaurar configuración original
        print(f"\n🔄 Restaurando configuración original...")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Recargar nuevamente para restaurar
        importlib.reload(src.config.main_config)
        print(f"✅ Configuración restaurada")
        
        return config_changed
        
    except Exception as e:
        print(f"❌ Error en test de recarga: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal del test"""
    print(f"🚀 Iniciando Test de Recarga de Configuración")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    success = test_config_reload()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST EXITOSO: La recarga de configuración funciona correctamente")
    else:
        print("💥 TEST FALLIDO: Problemas con la recarga de configuración")
    print("=" * 50)

if __name__ == "__main__":
    main()
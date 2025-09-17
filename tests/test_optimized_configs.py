#!/usr/bin/env python3
"""
Script de validación simplificado para configuraciones optimizadas
"""

import sys
import os

# Agregar el directorio src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

try:
    from config.config_manager import ConfigManager
    print("✅ ConfigManager importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ConfigManager: {e}")
    sys.exit(1)

def validate_configurations():
    """Validar todas las configuraciones optimizadas"""
    print("🔍 Iniciando validación de configuraciones optimizadas...")
    
    try:
        # Inicializar ConfigManager
        config_manager = ConfigManager()
        config_manager.initialize()
        print("✅ ConfigManager inicializado correctamente")
        
        profiles = ["RAPIDO", "AGRESIVO", "OPTIMO", "CONSERVADOR"]
        validation_results = {}
        
        for profile in profiles:
            print(f"\n📊 Validando perfil: {profile}")
            
            try:
                config = config_manager.get_consolidated_config(profile)
                
                # Verificar secciones principales
                required_sections = ['indicators', 'strategies', 'risk_manager']
                missing_sections = []
                
                for section in required_sections:
                    if section not in config:
                        missing_sections.append(section)
                
                if missing_sections:
                    print(f"❌ Secciones faltantes en {profile}: {missing_sections}")
                    validation_results[profile] = False
                    continue
                
                # Validar indicadores
                indicators = config['indicators']
                indicator_checks = []
                
                # MACD
                if 'macd_periods' in indicators:
                    macd = indicators['macd_periods']
                    if len(macd) == 3 and macd[0] < macd[1]:
                        indicator_checks.append("✅ MACD válido")
                    else:
                        indicator_checks.append("❌ MACD inválido")
                
                # RSI
                if 'rsi_period' in indicators:
                    rsi = indicators['rsi_period']
                    if 0 < rsi < 50:
                        indicator_checks.append("✅ RSI válido")
                    else:
                        indicator_checks.append("❌ RSI inválido")
                
                # Bollinger Bands
                if 'bb_period' in indicators:
                    bb = indicators['bb_period']
                    if bb > 5:
                        indicator_checks.append("✅ BB válido")
                    else:
                        indicator_checks.append("❌ BB inválido")
                
                # Validar estrategias
                strategies = config['strategies']
                strategy_checks = []
                
                # RSI levels
                if 'rsi_oversold' in strategies and 'rsi_overbought' in strategies:
                    oversold = strategies['rsi_oversold']
                    overbought = strategies['rsi_overbought']
                    if 10 < oversold < overbought < 90:
                        strategy_checks.append("✅ Niveles RSI válidos")
                    else:
                        strategy_checks.append("❌ Niveles RSI inválidos")
                
                # Confidence boost
                if 'confidence_boost_factor' in strategies:
                    boost = strategies['confidence_boost_factor']
                    if 0.5 < boost < 2.0:
                        strategy_checks.append("✅ Confidence boost válido")
                    else:
                        strategy_checks.append("❌ Confidence boost inválido")
                
                # Validar gestión de riesgo
                risk = config['risk_manager']
                risk_checks = []
                
                # Stop loss y take profit
                if 'stop_loss_percentage' in risk and 'take_profit_percentage' in risk:
                    sl = risk['stop_loss_percentage']
                    tp = risk['take_profit_percentage']
                    if 0 < sl < tp:
                        risk_checks.append("✅ SL/TP válidos")
                    else:
                        risk_checks.append("❌ SL/TP inválidos")
                
                # Riesgo por trade
                if 'max_risk_per_trade' in risk:
                    risk_per_trade = risk['max_risk_per_trade']
                    if 0 < risk_per_trade < 0.1:
                        risk_checks.append("✅ Riesgo por trade válido")
                    else:
                        risk_checks.append("❌ Riesgo por trade inválido")
                
                # Mostrar resultados
                print("  📈 Indicadores:")
                for check in indicator_checks:
                    print(f"    {check}")
                
                print("  🎯 Estrategias:")
                for check in strategy_checks:
                    print(f"    {check}")
                
                print("  🛡️ Gestión de Riesgo:")
                for check in risk_checks:
                    print(f"    {check}")
                
                # Verificar nuevos parámetros optimizados
                new_params_found = []
                
                # Nuevos parámetros de indicadores
                new_indicator_params = ['stoch_k_period', 'williams_r_period', 'cci_period', 'fibonacci_lookback']
                for param in new_indicator_params:
                    if param in indicators:
                        new_params_found.append(f"indicators.{param}")
                
                # Nuevos parámetros de estrategias
                new_strategy_params = ['volume_threshold', 'momentum_threshold', 'trend_strength_threshold']
                for param in new_strategy_params:
                    if param in strategies:
                        new_params_found.append(f"strategies.{param}")
                
                # Nuevos parámetros de riesgo
                new_risk_params = ['profit_target_multiplier', 'dynamic_sizing_enabled']
                for param in new_risk_params:
                    if param in risk:
                        new_params_found.append(f"risk_manager.{param}")
                
                if new_params_found:
                    print("  🚀 Nuevos parámetros optimizados:")
                    for param in new_params_found:
                        print(f"    ✅ {param}")
                
                # Determinar si el perfil pasó la validación
                all_checks = indicator_checks + strategy_checks + risk_checks
                failed_checks = [check for check in all_checks if "❌" in check]
                
                if not failed_checks:
                    print(f"  🎉 {profile} - VALIDACIÓN EXITOSA")
                    validation_results[profile] = True
                else:
                    print(f"  ⚠️ {profile} - {len(failed_checks)} problemas encontrados")
                    validation_results[profile] = False
                
            except Exception as e:
                print(f"❌ Error validando {profile}: {str(e)}")
                validation_results[profile] = False
        
        # Resumen final
        print("\n" + "="*60)
        print("📋 RESUMEN DE VALIDACIÓN")
        print("="*60)
        
        successful_profiles = [p for p, success in validation_results.items() if success]
        failed_profiles = [p for p, success in validation_results.items() if not success]
        
        print(f"✅ Perfiles exitosos: {len(successful_profiles)}/{len(profiles)}")
        for profile in successful_profiles:
            print(f"  🟢 {profile}")
        
        if failed_profiles:
            print(f"❌ Perfiles con problemas: {len(failed_profiles)}")
            for profile in failed_profiles:
                print(f"  🔴 {profile}")
        
        # Verificar progresión de perfiles
        print("\n🔄 Verificando progresión de perfiles...")
        
        try:
            configs = {}
            for profile in profiles:
                configs[profile] = config_manager.get_consolidated_config(profile)
            
            # Verificar progresión de sensibilidad RSI (menor período = más sensible)
            rsi_periods = {}
            for profile in profiles:
                rsi_periods[profile] = configs[profile]['indicators']['rsi_period']
            
            print("📊 Períodos RSI por perfil:")
            for profile in profiles:
                print(f"  {profile}: {rsi_periods[profile]} períodos")
            
            # Verificar que RAPIDO sea más sensible que CONSERVADOR
            if rsi_periods['RAPIDO'] <= rsi_periods['CONSERVADOR']:
                print("✅ Progresión de sensibilidad correcta (RAPIDO más sensible)")
            else:
                print("⚠️ Progresión de sensibilidad podría mejorarse")
            
        except Exception as e:
            print(f"⚠️ No se pudo verificar progresión: {str(e)}")
        
        # Resultado final
        if len(successful_profiles) == len(profiles):
            print("\n🎉 ¡TODAS LAS CONFIGURACIONES OPTIMIZADAS SON VÁLIDAS!")
            print("🚀 El sistema está listo para maximizar ganancias con las nuevas configuraciones.")
            return True
        else:
            print(f"\n⚠️ {len(failed_profiles)} perfiles necesitan ajustes adicionales.")
            return False
            
    except Exception as e:
        print(f"❌ Error crítico durante la validación: {str(e)}")
        return False

if __name__ == "__main__":
    success = validate_configurations()
    print(f"\n{'='*60}")
    if success:
        print("🏆 VALIDACIÓN COMPLETADA EXITOSAMENTE")
    else:
        print("🔧 SE REQUIEREN AJUSTES ADICIONALES")
    print("="*60)
    
    sys.exit(0 if success else 1)
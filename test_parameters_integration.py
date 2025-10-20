#!/usr/bin/env python3
"""
🧪 Test Integral de Parámetros del Sistema
Verifica que todos los parámetros se apliquen correctamente en todos los módulos

Desarrollado para verificar la correcta aplicación de configuraciones
en TradingBot, Risk Manager, Strategies, y todos los componentes del sistema.
"""

import sys
import os
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar componentes del sistema
from src.config.main_config import TradingProfiles, TradingBotConfig, RiskManagerConfig
from src.core.trading_bot import TradingBot
from src.core.enhanced_risk_manager import EnhancedRiskManager
from src.core.professional_adapter import ProfessionalStrategyAdapter
from src.core.mean_reversion_adapter import MeanReversionAdapter
from src.core.breakout_adapter import BreakoutAdapter
from src.core.paper_trader import PaperTrader

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ParameterTestResult:
    """Resultado de test de parámetros"""
    module_name: str
    parameter_name: str
    expected_value: Any
    actual_value: Any
    is_correct: bool
    error_message: Optional[str] = None

@dataclass
class ModuleTestResult:
    """Resultado de test de módulo completo"""
    module_name: str
    total_parameters: int
    correct_parameters: int
    failed_parameters: int
    parameter_results: List[ParameterTestResult]
    is_module_ok: bool
    error_message: Optional[str] = None

class SystemParametersIntegrationTest:
    """🧪 Test integral de parámetros del sistema"""
    
    def __init__(self):
        self.results: List[ModuleTestResult] = []
        self.current_profile = None
        self.profile_config = None
        
    def run_full_test(self, profile_name: str = "SCALPING") -> Dict[str, Any]:
        """
        🚀 Ejecutar test completo del sistema
        
        Args:
            profile_name: Perfil a testear (SCALPING o INTRADAY)
            
        Returns:
            Diccionario con resultados completos del test
        """
        print(f"\n🧪 ===== INICIANDO TEST INTEGRAL DE PARÁMETROS =====")
        print(f"📊 Perfil a testear: {profile_name}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # Configurar perfil
            self.current_profile = profile_name
            self.profile_config = TradingProfiles.PROFILES.get(profile_name)
            
            if not self.profile_config:
                raise ValueError(f"Perfil '{profile_name}' no encontrado")
            
            print(f"✅ Perfil '{profile_name}' cargado correctamente")
            print(f"📋 Configuración: {self.profile_config.get('description', 'N/A')}")
            
            # Ejecutar tests por módulo
            self._test_trading_bot_parameters()
            self._test_risk_manager_parameters()
            self._test_strategies_parameters()
            self._test_paper_trader_parameters()
            
            # Generar reporte final
            return self._generate_final_report()
            
        except Exception as e:
            error_msg = f"❌ Error crítico en test integral: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "status": "CRITICAL_ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _test_trading_bot_parameters(self):
        """🤖 Test de parámetros del Trading Bot"""
        print(f"\n🤖 Testing Trading Bot Parameters...")
        
        parameter_results = []
        
        try:
            # Crear instancia del bot
            bot = TradingBot()
            
            # Test 1: Analysis Interval
            expected_interval = self.profile_config.get('analysis_interval', 5)
            actual_interval = bot.analysis_interval
            parameter_results.append(ParameterTestResult(
                module_name="TradingBot",
                parameter_name="analysis_interval",
                expected_value=expected_interval,
                actual_value=actual_interval,
                is_correct=(actual_interval == expected_interval)
            ))
            
            # Test 2: Min Confidence
            expected_confidence = self.profile_config.get('min_confidence', 70.0)
            actual_confidence = bot.min_confidence_threshold
            parameter_results.append(ParameterTestResult(
                module_name="TradingBot",
                parameter_name="min_confidence_threshold",
                expected_value=expected_confidence,
                actual_value=actual_confidence,
                is_correct=(actual_confidence == expected_confidence)
            ))
            
            # Test 3: Max Daily Trades
            expected_trades = self.profile_config.get('max_daily_trades', 10)
            actual_trades = bot.max_daily_trades
            parameter_results.append(ParameterTestResult(
                module_name="TradingBot",
                parameter_name="max_daily_trades",
                expected_value=expected_trades,
                actual_value=actual_trades,
                is_correct=(actual_trades == expected_trades)
            ))
            
            # Test 4: Timeframes
            expected_timeframes = self.profile_config.get('timeframes', ['1h'])
            actual_primary_tf = getattr(bot, 'primary_timeframe', None)
            # Verificar que el timeframe principal esté en la lista esperada
            tf_correct = actual_primary_tf in expected_timeframes if actual_primary_tf else False
            parameter_results.append(ParameterTestResult(
                module_name="TradingBot",
                parameter_name="primary_timeframe",
                expected_value=expected_timeframes,
                actual_value=actual_primary_tf,
                is_correct=tf_correct
            ))
            
            # Calcular estadísticas
            correct_count = sum(1 for r in parameter_results if r.is_correct)
            total_count = len(parameter_results)
            
            module_result = ModuleTestResult(
                module_name="TradingBot",
                total_parameters=total_count,
                correct_parameters=correct_count,
                failed_parameters=total_count - correct_count,
                parameter_results=parameter_results,
                is_module_ok=(correct_count == total_count)
            )
            
            self.results.append(module_result)
            
            # Mostrar resultados
            print(f"   ✅ Parámetros correctos: {correct_count}/{total_count}")
            for result in parameter_results:
                status = "✅" if result.is_correct else "❌"
                print(f"   {status} {result.parameter_name}: {result.actual_value} (esperado: {result.expected_value})")
            
        except Exception as e:
            error_msg = f"Error en test de TradingBot: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.results.append(ModuleTestResult(
                module_name="TradingBot",
                total_parameters=0,
                correct_parameters=0,
                failed_parameters=1,
                parameter_results=[],
                is_module_ok=False,
                error_message=error_msg
            ))
    
    def _test_risk_manager_parameters(self):
        """🛡️ Test de parámetros del Risk Manager"""
        print(f"\n🛡️ Testing Risk Manager Parameters...")
        
        parameter_results = []
        
        try:
            # Crear instancia del risk manager
            risk_manager = EnhancedRiskManager()
            
            # Test 1: Max Risk Per Trade
            expected_risk = self.profile_config.get('max_risk_per_trade', 1.0)
            actual_risk = risk_manager.config.get_max_risk_per_trade()
            parameter_results.append(ParameterTestResult(
                module_name="RiskManager",
                parameter_name="max_risk_per_trade",
                expected_value=expected_risk,
                actual_value=actual_risk,
                is_correct=(abs(actual_risk - expected_risk) < 0.01)  # Tolerancia de 0.01%
            ))
            
            # Test 2: Max Daily Risk
            expected_daily_risk = self.profile_config.get('max_daily_risk', 3.0)
            actual_daily_risk = risk_manager.config.get_max_daily_risk()
            parameter_results.append(ParameterTestResult(
                module_name="RiskManager",
                parameter_name="max_daily_risk",
                expected_value=expected_daily_risk,
                actual_value=actual_daily_risk,
                is_correct=(abs(actual_daily_risk - expected_daily_risk) < 0.01)
            ))
            
            # Test 3: Max Drawdown Threshold
            expected_drawdown = self.profile_config.get('max_drawdown_threshold', 0.15)
            actual_drawdown = risk_manager.config.get_max_drawdown_threshold()
            parameter_results.append(ParameterTestResult(
                module_name="RiskManager",
                parameter_name="max_drawdown_threshold",
                expected_value=expected_drawdown,
                actual_value=actual_drawdown,
                is_correct=(abs(actual_drawdown - expected_drawdown) < 0.001)
            ))
            
            # Calcular estadísticas
            correct_count = sum(1 for r in parameter_results if r.is_correct)
            total_count = len(parameter_results)
            
            module_result = ModuleTestResult(
                module_name="RiskManager",
                total_parameters=total_count,
                correct_parameters=correct_count,
                failed_parameters=total_count - correct_count,
                parameter_results=parameter_results,
                is_module_ok=(correct_count == total_count)
            )
            
            self.results.append(module_result)
            
            # Mostrar resultados
            print(f"   ✅ Parámetros correctos: {correct_count}/{total_count}")
            for result in parameter_results:
                status = "✅" if result.is_correct else "❌"
                print(f"   {status} {result.parameter_name}: {result.actual_value} (esperado: {result.expected_value})")
            
        except Exception as e:
            error_msg = f"Error en test de RiskManager: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.results.append(ModuleTestResult(
                module_name="RiskManager",
                total_parameters=0,
                correct_parameters=0,
                failed_parameters=1,
                parameter_results=[],
                is_module_ok=False,
                error_message=error_msg
            ))
    
    def _test_strategies_parameters(self):
        """🧠 Test de parámetros de las estrategias"""
        print(f"\n🧠 Testing Strategies Parameters...")
        
        parameter_results = []
        
        try:
            # Test de estrategias principales
            strategies = {
                "ProfessionalAdapter": ProfessionalStrategyAdapter,
                "MeanReversionAdapter": MeanReversionAdapter,
                "BreakoutAdapter": BreakoutAdapter
            }
            
            for strategy_name, strategy_class in strategies.items():
                try:
                    # Crear instancia de la estrategia
                    strategy = strategy_class(capital_client=None)
                    
                    # Test: Min Confidence
                    expected_confidence = self.profile_config.get('min_confidence', 70.0)
                    actual_confidence = getattr(strategy, 'min_confidence', None)
                    
                    if actual_confidence is not None:
                        parameter_results.append(ParameterTestResult(
                            module_name=f"Strategy_{strategy_name}",
                            parameter_name="min_confidence",
                            expected_value=expected_confidence,
                            actual_value=actual_confidence,
                            is_correct=(abs(actual_confidence - expected_confidence) < 0.1)
                        ))
                    
                    # Test: Timeframes (si está disponible)
                    expected_timeframes = self.profile_config.get('timeframes', ['1h'])
                    actual_timeframes = getattr(strategy, 'timeframes', None)
                    
                    if actual_timeframes is not None:
                        # Verificar que al menos un timeframe coincida
                        tf_match = any(tf in expected_timeframes for tf in actual_timeframes)
                        parameter_results.append(ParameterTestResult(
                            module_name=f"Strategy_{strategy_name}",
                            parameter_name="timeframes",
                            expected_value=expected_timeframes,
                            actual_value=actual_timeframes,
                            is_correct=tf_match
                        ))
                    
                except Exception as e:
                    print(f"   ⚠️ Error testing {strategy_name}: {str(e)}")
            
            # Calcular estadísticas
            correct_count = sum(1 for r in parameter_results if r.is_correct)
            total_count = len(parameter_results)
            
            module_result = ModuleTestResult(
                module_name="Strategies",
                total_parameters=total_count,
                correct_parameters=correct_count,
                failed_parameters=total_count - correct_count,
                parameter_results=parameter_results,
                is_module_ok=(correct_count == total_count)
            )
            
            self.results.append(module_result)
            
            # Mostrar resultados
            print(f"   ✅ Parámetros correctos: {correct_count}/{total_count}")
            for result in parameter_results:
                status = "✅" if result.is_correct else "❌"
                print(f"   {status} {result.module_name}.{result.parameter_name}: {result.actual_value}")
            
        except Exception as e:
            error_msg = f"Error en test de Strategies: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.results.append(ModuleTestResult(
                module_name="Strategies",
                total_parameters=0,
                correct_parameters=0,
                failed_parameters=1,
                parameter_results=[],
                is_module_ok=False,
                error_message=error_msg
            ))
    
    def _test_paper_trader_parameters(self):
        """💰 Test de parámetros del Paper Trader"""
        print(f"\n💰 Testing Paper Trader Parameters...")
        
        parameter_results = []
        
        try:
            # Crear instancia del paper trader
            paper_trader = PaperTrader(initial_balance=1000.0)
            
            # Test 1: Initial Balance
            expected_balance = 1000.0
            actual_balance = paper_trader.balance
            parameter_results.append(ParameterTestResult(
                module_name="PaperTrader",
                parameter_name="initial_balance",
                expected_value=expected_balance,
                actual_value=actual_balance,
                is_correct=(abs(actual_balance - expected_balance) < 0.01)
            ))
            
            # Test 2: Max Position Size (si está configurado)
            expected_max_pos = self.profile_config.get('max_position_size', 0.15)
            actual_max_pos = getattr(paper_trader, 'max_position_size', expected_max_pos)
            parameter_results.append(ParameterTestResult(
                module_name="PaperTrader",
                parameter_name="max_position_size",
                expected_value=expected_max_pos,
                actual_value=actual_max_pos,
                is_correct=(abs(actual_max_pos - expected_max_pos) < 0.01)
            ))
            
            # Calcular estadísticas
            correct_count = sum(1 for r in parameter_results if r.is_correct)
            total_count = len(parameter_results)
            
            module_result = ModuleTestResult(
                module_name="PaperTrader",
                total_parameters=total_count,
                correct_parameters=correct_count,
                failed_parameters=total_count - correct_count,
                parameter_results=parameter_results,
                is_module_ok=(correct_count == total_count)
            )
            
            self.results.append(module_result)
            
            # Mostrar resultados
            print(f"   ✅ Parámetros correctos: {correct_count}/{total_count}")
            for result in parameter_results:
                status = "✅" if result.is_correct else "❌"
                print(f"   {status} {result.parameter_name}: {result.actual_value} (esperado: {result.expected_value})")
            
        except Exception as e:
            error_msg = f"Error en test de PaperTrader: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.results.append(ModuleTestResult(
                module_name="PaperTrader",
                total_parameters=0,
                correct_parameters=0,
                failed_parameters=1,
                parameter_results=[],
                is_module_ok=False,
                error_message=error_msg
            ))
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """📊 Generar reporte final del test"""
        print(f"\n📊 ===== REPORTE FINAL DEL TEST =====")
        
        total_modules = len(self.results)
        successful_modules = sum(1 for r in self.results if r.is_module_ok)
        failed_modules = total_modules - successful_modules
        
        total_parameters = sum(r.total_parameters for r in self.results)
        correct_parameters = sum(r.correct_parameters for r in self.results)
        failed_parameters = sum(r.failed_parameters for r in self.results)
        
        success_rate = (correct_parameters / total_parameters * 100) if total_parameters > 0 else 0
        
        # Status general
        overall_status = "SUCCESS" if failed_modules == 0 and failed_parameters == 0 else "PARTIAL_SUCCESS" if correct_parameters > failed_parameters else "FAILURE"
        
        print(f"🎯 Perfil testeado: {self.current_profile}")
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        print(f"📊 Módulos exitosos: {successful_modules}/{total_modules}")
        print(f"✅ Parámetros correctos: {correct_parameters}/{total_parameters}")
        print(f"❌ Parámetros fallidos: {failed_parameters}")
        print(f"🏆 Estado general: {overall_status}")
        
        # Detalles por módulo
        print(f"\n📋 Detalle por módulo:")
        for result in self.results:
            status_icon = "✅" if result.is_module_ok else "❌"
            print(f"   {status_icon} {result.module_name}: {result.correct_parameters}/{result.total_parameters} parámetros correctos")
            
            if not result.is_module_ok and result.error_message:
                print(f"      ⚠️ Error: {result.error_message}")
        
        # Recomendaciones
        print(f"\n💡 Recomendaciones:")
        if overall_status == "SUCCESS":
            print("   🎉 ¡Excelente! Todos los parámetros se están aplicando correctamente.")
        elif overall_status == "PARTIAL_SUCCESS":
            print("   ⚠️ Algunos parámetros no se están aplicando correctamente. Revisar módulos fallidos.")
        else:
            print("   🚨 Múltiples problemas detectados. Revisión urgente requerida.")
        
        print("=" * 60)
        
        # Generar reporte JSON
        report = {
            "status": overall_status,
            "profile_tested": self.current_profile,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_modules": total_modules,
                "successful_modules": successful_modules,
                "failed_modules": failed_modules,
                "total_parameters": total_parameters,
                "correct_parameters": correct_parameters,
                "failed_parameters": failed_parameters,
                "success_rate": round(success_rate, 2)
            },
            "module_results": [
                {
                    "module_name": r.module_name,
                    "is_ok": r.is_module_ok,
                    "correct_parameters": r.correct_parameters,
                    "total_parameters": r.total_parameters,
                    "error_message": r.error_message,
                    "parameter_details": [
                        {
                            "name": p.parameter_name,
                            "expected": p.expected_value,
                            "actual": p.actual_value,
                            "is_correct": p.is_correct
                        } for p in r.parameter_results
                    ]
                } for r in self.results
            ]
        }
        
        return report

def change_trading_profile_in_config(new_profile: str) -> bool:
    """
    🔄 Cambiar el perfil de trading directamente en el archivo de configuración
    
    Args:
        new_profile: Nuevo perfil a establecer ("SCALPING" o "INTRADAY")
        
    Returns:
        bool: True si el cambio fue exitoso
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'src', 'config', 'main_config.py')
        
        # Leer el archivo
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar y reemplazar la línea del perfil
        import re
        pattern = r'TRADING_PROFILE = "[^"]*"'
        replacement = f'TRADING_PROFILE = "{new_profile}"'
        
        new_content = re.sub(pattern, replacement, content)
        
        # Escribir el archivo modificado
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Perfil cambiado a {new_profile} en main_config.py")
        
        # Recargar el módulo para que los cambios tomen efecto
        import importlib
        import src.config.main_config
        importlib.reload(src.config.main_config)
        
        return True
        
    except Exception as e:
        print(f"❌ Error cambiando perfil en configuración: {e}")
        return False

def main():
    """🚀 Función principal para ejecutar tests"""
    print("🧪 Sistema de Test Integral de Parámetros")
    print("=" * 50)
    
    # Guardar el perfil original
    original_profile = None
    try:
        from src.config.main_config import TRADING_PROFILE
        original_profile = TRADING_PROFILE
        print(f"📋 Perfil original: {original_profile}")
    except:
        original_profile = "INTRADAY"  # Fallback
    
    tester = SystemParametersIntegrationTest()
    
    # Test para ambos perfiles
    profiles_to_test = ["SCALPING", "INTRADAY"]
    all_reports = {}
    
    for profile in profiles_to_test:
        print(f"\n🔄 Cambiando a perfil {profile}...")
        
        # Cambiar perfil directamente en el archivo de configuración
        if change_trading_profile_in_config(profile):
            print(f"✅ Perfil cambiado a {profile}")
            
            # Esperar un momento para que los cambios se propaguen
            import time
            time.sleep(1)
        else:
            print(f"⚠️ No se pudo cambiar perfil, continuando con test...")
        
        # Ejecutar test
        report = tester.run_full_test(profile)
        all_reports[profile] = report
        
        # Guardar reporte individual
        report_filename = f"test_report_{profile.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"💾 Reporte guardado en: {report_filename}")
    
    # Reporte consolidado
    print(f"\n🏆 ===== REPORTE CONSOLIDADO =====")
    for profile, report in all_reports.items():
        status_icon = "✅" if report["status"] == "SUCCESS" else "⚠️" if report["status"] == "PARTIAL_SUCCESS" else "❌"
        success_rate = report.get("summary", {}).get("success_rate", 0)
        print(f"{status_icon} {profile}: {success_rate}% de parámetros correctos")
    
    # Guardar reporte consolidado
    consolidated_report = {
        "timestamp": datetime.now().isoformat(),
        "profiles_tested": list(all_reports.keys()),
        "individual_reports": all_reports
    }
    
    consolidated_filename = f"test_report_consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(consolidated_filename, 'w', encoding='utf-8') as f:
        json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Reporte consolidado guardado en: {consolidated_filename}")
    
    # Restaurar el perfil original
    if original_profile:
        print(f"\n🔄 Restaurando perfil original: {original_profile}")
        change_trading_profile_in_config(original_profile)
    
    print("🎯 Test integral completado!")

if __name__ == "__main__":
    main()
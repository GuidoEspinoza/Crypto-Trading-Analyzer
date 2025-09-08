#!/usr/bin/env python3
"""
🎯 Script de Prueba Integral - PositionAdjuster
Prueba todas las funcionalidades del PositionAdjuster
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.position_adjuster import PositionAdjuster
from src.database.database import db_manager
from src.database.models import Trade
import traceback
from datetime import datetime

def test_position_adjuster_initialization():
    """Probar inicialización del PositionAdjuster"""
    print("\n🔍 Probando inicialización del PositionAdjuster...")
    try:
        # Probar inicialización en modo simulación
        adjuster = PositionAdjuster(config=None, simulation_mode=True)
        
        print("✅ PositionAdjuster inicializado correctamente")
        print(f"✅ Modo simulación: {adjuster.simulation_mode}")
        
        return True
    except Exception as e:
        print(f"❌ Error inicializando PositionAdjuster: {e}")
        traceback.print_exc()
        return False

def test_position_adjuster_database_methods():
    """Probar métodos de base de datos del PositionAdjuster"""
    print("\n🔍 Probando métodos de base de datos...")
    try:
        adjuster = PositionAdjuster(config=None, simulation_mode=True)
        
        # Probar obtener posiciones activas
        print("📊 Obteniendo posiciones activas...")
        active_positions = adjuster._get_active_positions()
        print(f"✅ Posiciones activas obtenidas: {len(active_positions)}")
        
        # Crear un trade de prueba si no hay ninguno
        if len(active_positions) == 0:
            print("📝 Creando trade de prueba...")
            test_trade = Trade(
                symbol="BTCUSDT",
                strategy_name="Test_Strategy",
                trade_type="BUY",
                quantity=0.001,
                entry_price=50000.0,
                entry_value=50.0,
                status="OPEN",
                entry_time=datetime.now(),
                is_paper_trade=True,
                timeframe="1h"
            )
            
            # Guardar en base de datos usando sesión directa
            with db_manager.get_db_session() as session:
                session.add(test_trade)
                session.commit()
            print("✅ Trade de prueba creado")
            
            # Verificar que se puede obtener
            active_positions = adjuster._get_active_positions()
            print(f"✅ Posiciones activas después de crear: {len(active_positions)}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando métodos de base de datos: {e}")
        traceback.print_exc()
        return False

def test_position_adjuster_tp_sl_logic():
    """Probar lógica de Take Profit y Stop Loss"""
    print("\n🔍 Probando lógica TP/SL...")
    try:
        from src.core.position_adjuster import PositionInfo
        adjuster = PositionAdjuster(config=None, simulation_mode=True)
        
        # Crear datos de prueba usando PositionInfo
        test_position = PositionInfo(
            symbol='BTCUSDT',
            entry_price=50000.0,
            current_price=52000.0,  # 4% ganancia
            quantity=0.001,
            side='BUY',
            current_tp=55000.0,
            current_sl=48000.0,
            entry_time=datetime.now(),
            unrealized_pnl=2.0,
            unrealized_pnl_pct=4.0
        )
        
        print(f"📊 Probando posición: {test_position.symbol}")
        print(f"   - Precio entrada: ${test_position.entry_price:,.2f}")
        print(f"   - Precio actual: ${test_position.current_price:,.2f}")
        print(f"   - PnL: {test_position.unrealized_pnl_pct:.2f}%")
        
        # Probar cálculo de nuevos niveles
        needs_adjustment, reason, new_tp, new_sl = adjuster._calculate_new_levels(test_position)
        print(f"✅ Necesita ajuste: {needs_adjustment}")
        if needs_adjustment:
            print(f"✅ Razón: {reason.value}")
            print(f"✅ Nuevo TP: ${new_tp:.2f}")
            print(f"✅ Nuevo SL: ${new_sl:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Error probando lógica TP/SL: {e}")
        traceback.print_exc()
        return False

import asyncio

def test_position_adjuster_monitoring():
    """Probar sistema de monitoreo"""
    print("\n🔍 Probando sistema de monitoreo...")
    try:
        adjuster = PositionAdjuster(config=None, simulation_mode=True)
        
        # Verificar que el adjuster se inicializa correctamente
        assert hasattr(adjuster, '_get_active_positions'), "PositionAdjuster should have _get_active_positions method"
        assert hasattr(adjuster, '_calculate_new_levels'), "PositionAdjuster should have _calculate_new_levels method"
        
        # Probar obtener posiciones activas (puede estar vacío)
        positions = adjuster._get_active_positions()
        assert isinstance(positions, list), "_get_active_positions should return a list"
        
        print(f"✅ Sistema de monitoreo probado - Encontradas {len(positions)} posiciones")
        return True
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")
        traceback.print_exc()
        return False

def test_position_adjuster_stats():
    """Probar estadísticas del PositionAdjuster"""
    print("\n🔍 Probando estadísticas...")
    try:
        adjuster = PositionAdjuster(config=None, simulation_mode=True)
        
        # Obtener estadísticas
        stats = adjuster.get_adjustment_stats()
        print(f"✅ Estadísticas obtenidas: {len(stats)} campos")
        print(f"   - Total ajustes: {stats['total_adjustments']}")
        print(f"   - Tasa de éxito: {stats['success_rate']:.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS INTEGRALES DEL POSITION ADJUSTER")
    print("=" * 60)
    
    tests = [
        ("Inicialización", test_position_adjuster_initialization),
        ("Métodos de base de datos", test_position_adjuster_database_methods),
        ("Lógica TP/SL", test_position_adjuster_tp_sl_logic),
        ("Sistema de monitoreo", test_position_adjuster_monitoring),
        ("Estadísticas", test_position_adjuster_stats)
    ]
    
    results = []
    
    # Ejecutar todas las pruebas
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas del PositionAdjuster pasaron!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar errores arriba.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        traceback.print_exc()
        sys.exit(1)
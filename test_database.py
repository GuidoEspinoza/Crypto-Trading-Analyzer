#!/usr/bin/env python3
"""
🧪 Script de prueba integral para la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import db_manager
from src.database.models import Trade, Portfolio, Strategy
from datetime import datetime
import traceback

def test_database_connection():
    """Probar conexión básica a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    try:
        # Probar conexión
        with db_manager.get_db_session() as session:
            print("✅ Conexión exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        traceback.print_exc()
        return False

def test_create_tables():
    """Probar creación de tablas"""
    print("\n🔍 Probando creación de tablas...")
    try:
        db_manager.create_tables()
        print("✅ Tablas creadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        traceback.print_exc()
        return False

def test_portfolio_operations():
    """Probar operaciones del portfolio"""
    print("\n🔍 Probando operaciones del portfolio...")
    try:
        # Inicializar portfolio base
        db_manager.initialize_base_portfolio()
        print("✅ Portfolio base inicializado")
        
        # Obtener resumen del portfolio
        summary = db_manager.get_portfolio_summary()
        print(f"✅ Resumen del portfolio obtenido: {len(summary)} assets")
        return True
    except Exception as e:
        print(f"❌ Error en operaciones del portfolio: {e}")
        traceback.print_exc()
        return False

def test_trade_operations():
    """Probar operaciones de trades"""
    print("\n🔍 Probando operaciones de trades...")
    try:
        # Probar get_active_trades
        active_trades = db_manager.get_active_trades(is_paper=True)
        print(f"✅ Trades activos obtenidos: {len(active_trades)} trades")
        
        # Crear un trade de prueba
        with db_manager.get_db_session() as session:
            test_trade = Trade(
                symbol="BTCUSDT",
                strategy_name="TEST",
                trade_type="BUY",
                entry_price=50000.0,
                quantity=0.001,
                entry_value=50.0,
                timeframe="1h",
                status="OPEN",
                is_paper_trade=True
            )
            session.add(test_trade)
            session.commit()
            print(f"✅ Trade de prueba creado con ID: {test_trade.id}")
            
            # Verificar que se puede obtener
            active_trades_after = db_manager.get_active_trades(is_paper=True)
            print(f"✅ Trades activos después: {len(active_trades_after)} trades")
            
            # Limpiar trade de prueba
            session.delete(test_trade)
            session.commit()
            print("✅ Trade de prueba eliminado")
            
        return True
    except Exception as e:
        print(f"❌ Error en operaciones de trades: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas de base de datos"""
    print("🧪 INICIANDO PRUEBAS INTEGRALES DE BASE DE DATOS")
    print("=" * 50)
    
    tests = [
        ("Conexión", test_database_connection),
        ("Creación de tablas", test_create_tables),
        ("Operaciones de portfolio", test_portfolio_operations),
        ("Operaciones de trades", test_trade_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas de base de datos pasaron!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
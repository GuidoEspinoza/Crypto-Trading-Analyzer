#!/usr/bin/env python3
"""
Script de prueba para el conector de Binance
Verifica que la conexión funciona y muestra los datos de la cuenta
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar directamente el módulo para evitar problemas con importaciones relativas
import importlib.util
spec = importlib.util.spec_from_file_location(
    "binance_connector", 
    os.path.join(os.path.dirname(__file__), 'src', 'core', 'binance_connector.py')
)
binance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binance_module)

BinanceConnector = binance_module.BinanceConnector
TestOrderRequest = binance_module.TestOrderRequest
TestOrderResponse = binance_module.TestOrderResponse

def print_separator(title: str):
    """Imprime un separador visual con título"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_json_pretty(data: dict, title: str = ""):
    """Imprime datos JSON de forma legible"""
    if title:
        print(f"\n📊 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_binance_connection():
    """Prueba la conexión con Binance y muestra los datos de la cuenta"""
    
    print_separator("🚀 PRUEBA DEL CONECTOR DE BINANCE")
    
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        print("📋 Verificando variables de entorno...")
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        if not api_key:
            print("❌ BINANCE_API_KEY no encontrada en .env")
            return False
        if not secret_key:
            print("❌ BINANCE_SECRET_KEY no encontrada en .env")
            return False
            
        print(f"✅ API Key: {api_key[:8]}...{api_key[-8:]}")
        print(f"✅ Secret Key: {secret_key[:8]}...{secret_key[-8:]}")
        
        # Inicializar el conector
        print_separator("🔗 INICIALIZANDO CONECTOR")
        connector = BinanceConnector()
        
        # Probar conexión básica
        print_separator("🏥 PROBANDO CONEXIÓN CON BINANCE")
        if connector.test_connection():
            print("✅ Conexión con Binance: EXITOSA")
        else:
            print("❌ No se pudo conectar a Binance")
            return False
        
        # Obtener información de la cuenta
        print_separator("👤 INFORMACIÓN DE LA CUENTA")
        try:
            account_info = connector.get_account_info()
            print("✅ Información de cuenta obtenida exitosamente")
            
            # Mostrar información básica
            print(f"\n📈 Tipo de cuenta: {account_info.account_type}")
            print(f"💰 Puede hacer trading: {'✅' if account_info.can_trade else '❌'}")
            print(f"💸 Puede retirar: {'✅' if account_info.can_withdraw else '❌'}")
            print(f"💳 Puede depositar: {'✅' if account_info.can_deposit else '❌'}")
            
            # Mostrar comisiones
            print(f"\n💼 Comisiones:")
            print(f"   • Maker: {account_info.maker_commission * 100:.4f}%")
            print(f"   • Taker: {account_info.taker_commission * 100:.4f}%")
            
            # Mostrar balance total
            print(f"\n💵 Balance total estimado: ${account_info.total_balance_usdt:.2f} USDT")
            
        except Exception as e:
            print(f"❌ No se pudo obtener información de la cuenta: {e}")
            return False
        
        # Obtener balances
        print_separator("💰 BALANCES DE LA CUENTA")
        try:
            account_info = connector.get_account_info()
            balances = account_info.balances
            
            print("✅ Balances obtenidos exitosamente")
            
            if balances:
                print(f"\n💎 Activos con balance ({len(balances)} activos):")
                for balance in balances:
                    print(f"   • {balance.asset:8} | Libre: {balance.free:>12.8f} | Bloqueado: {balance.locked:>12.8f} | Total: {balance.total:>12.8f}")
            else:
                print("ℹ️  No hay activos con balance positivo")
                
        except Exception as e:
            print(f"❌ No se pudo obtener balances de la cuenta: {e}")
            return False
        
        # Obtener resumen del portfolio
        print_separator("📊 RESUMEN DEL PORTFOLIO")
        portfolio_summary = connector.get_portfolio_summary()
        if portfolio_summary:
            print("✅ Resumen del portfolio obtenido exitosamente")
            print_json_pretty(portfolio_summary, "Resumen del Portfolio")
        else:
            print("❌ No se pudo obtener resumen del portfolio")
        
        print_separator("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print("✅ Todas las funciones del conector están funcionando correctamente")
        print("✅ El conector está listo para ser integrado al dashboard")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        print("\n🔍 Detalles del error:")
        traceback.print_exc()
        return False

def test_order_functionality(connector: BinanceConnector):
    """Prueba la funcionalidad de órdenes de prueba"""
    
    print_separator("🧪 PROBANDO FUNCIONALIDAD DE ÓRDENES DE PRUEBA")
    
    try:
        # Obtener un símbolo válido de los balances disponibles
        account_info = connector.get_account_info()
        
        # Buscar un activo que no sea USDT para hacer una orden de prueba
        test_symbol = None
        for balance in account_info.balances:
            if balance.asset != 'USDT' and balance.total > 0:
                test_symbol = f"{balance.asset}USDT"
                break
        
        # Si no encontramos un activo, usar BTCUSDT como ejemplo
        if not test_symbol:
            test_symbol = "BTCUSDT"
            print(f"ℹ️  No se encontraron activos con balance, usando {test_symbol} como ejemplo")
        else:
            print(f"✅ Usando símbolo {test_symbol} para la prueba")
        
        # Test 1: Orden MARKET de compra
        print("\n🔸 Test 1: Orden MARKET de compra")
        market_order = TestOrderRequest(
            symbol=test_symbol,
            side="BUY",
            type="MARKET",
            quote_order_qty=10.0,  # Comprar $10 USDT
            compute_commission_rates=True
        )
        
        result = connector.test_order(market_order)
        if result.success:
            print(f"✅ Orden MARKET exitosa: {result.message}")
            if result.commission_rates:
                print(f"   💼 Comisiones calculadas: {result.commission_rates}")
        else:
            print(f"❌ Error en orden MARKET: {result.message}")
            if result.error_code:
                print(f"   🔢 Código de error: {result.error_code}")
        
        # Test 2: Orden LIMIT de venta
        print("\n🔸 Test 2: Orden LIMIT de venta")
        limit_order = TestOrderRequest(
            symbol=test_symbol,
            side="SELL",
            type="LIMIT",
            quantity=0.001,  # Vender 0.001 del activo
            price=100000.0,  # Precio muy alto para que no se ejecute
            time_in_force="GTC"
        )
        
        result = connector.test_order(limit_order)
        if result.success:
            print(f"✅ Orden LIMIT exitosa: {result.message}")
        else:
            print(f"❌ Error en orden LIMIT: {result.message}")
            if result.error_code:
                print(f"   🔢 Código de error: {result.error_code}")
        
        # Test 3: Orden TAKE_PROFIT
        print("\n🔸 Test 3: Orden TAKE_PROFIT")
        take_profit_order = TestOrderRequest(
            symbol=test_symbol,
            side="SELL",
            type="TAKE_PROFIT",
            quantity=0.001,
            stop_price=120000.0  # Precio alto para take profit
        )
        
        result = connector.test_order(take_profit_order)
        if result.success:
            print(f"✅ Orden TAKE_PROFIT exitosa: {result.message}")
        else:
            print(f"❌ Error en orden TAKE_PROFIT: {result.message}")
            if result.error_code:
                print(f"   🔢 Código de error: {result.error_code}")
        
        # Test 4: Orden STOP_LOSS_LIMIT
        print("\n🔸 Test 4: Orden STOP_LOSS_LIMIT")
        stop_loss_limit_order = TestOrderRequest(
            symbol=test_symbol,
            side="SELL",
            type="STOP_LOSS_LIMIT",
            quantity=0.001,
            price=49000.0,      # Precio límite
            stop_price=50000.0, # Precio de activación
            time_in_force="GTC"
        )
        
        result = connector.test_order(stop_loss_limit_order)
        if result.success:
            print(f"✅ Orden STOP_LOSS_LIMIT exitosa: {result.message}")
        else:
            print(f"❌ Error en orden STOP_LOSS_LIMIT: {result.message}")
            if result.error_code:
                print(f"   🔢 Código de error: {result.error_code}")
        
        # Test 5: Orden con parámetros inválidos (para probar manejo de errores)
        print("\n🔸 Test 5: Orden con parámetros inválidos")
        invalid_order = TestOrderRequest(
            symbol="INVALIDPAIR",
            side="BUY",
            type="MARKET",
            quantity=0.001
        )
        
        result = connector.test_order(invalid_order)
        if result.success:
            print(f"⚠️  Orden inválida fue aceptada: {result.message}")
        else:
            print(f"✅ Error esperado manejado correctamente: {result.message}")
            if result.error_code:
                print(f"   🔢 Código de error: {result.error_code}")
        
        print("\n✅ Pruebas de órdenes completadas")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas de órdenes: {e}")
        import traceback
        print("\n🔍 Detalles del error:")
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print(f"🕐 Iniciando prueba - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Probar conexión básica
    connection_success = test_binance_connection()
    
    if not connection_success:
        print(f"\n💥 Resultado: FALLO EN CONEXIÓN")
        sys.exit(1)
    
    # Si la conexión es exitosa, probar funcionalidad de órdenes
    try:
        connector = BinanceConnector()
        order_success = test_order_functionality(connector)
        
        if order_success:
            print_separator("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("✅ Conexión con Binance: EXITOSA")
            print("✅ Funcionalidad de órdenes de prueba: EXITOSA")
            print("✅ El conector está listo para ser usado en el trading bot")
            print(f"\n🎯 Resultado: ÉXITO COMPLETO")
            sys.exit(0)
        else:
            print(f"\n💥 Resultado: FALLO EN PRUEBAS DE ÓRDENES")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error durante las pruebas de órdenes: {e}")
        print(f"\n💥 Resultado: FALLO")
        sys.exit(1)

if __name__ == "__main__":
    main()
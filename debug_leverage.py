#!/usr/bin/env python3
"""
Script para investigar apalancamiento y margen en Capital.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.capital_client import create_capital_client_from_env
import json

def main():
    print("🔍 Investigando apalancamiento y margen en Capital.com...")
    
    try:
        # Crear cliente de Capital.com
        capital_client = create_capital_client_from_env()
        
        # 1. Obtener información de mercado para XRPUSD
        print("\n1. Obteniendo información de mercado para XRPUSD...")
        markets_response = capital_client.get_markets(epics=["XRPUSD"])
        
        if not markets_response.get("success"):
            print(f"❌ Error obteniendo mercados: {markets_response.get('error')}")
            return
        
        # La respuesta contiene los mercados en marketDetails
        markets_data = markets_response.get("markets", {})
        print(f"📊 Estructura de respuesta: {json.dumps(markets_data, indent=2)[:500]}...")
        
        market_details = markets_data.get("marketDetails", [])
        
        # Buscar información específica de XRPUSD
        xrp_market = None
        for market in market_details:
            print(f"🔍 Revisando mercado: {market.get('epic', 'N/A')} - {market.get('instrumentName', 'N/A')}")
            if isinstance(market, dict) and market.get("epic") == "XRPUSD":
                xrp_market = market
                break
        
        # Si no encontramos XRPUSD, buscar cualquier mercado de XRP
        if not xrp_market:
            for market in market_details:
                epic = market.get('epic', '')
                instrument_name = market.get('instrumentName', '')
                if 'XRP' in epic or 'XRP' in instrument_name:
                    print(f"🔍 Encontrado mercado XRP alternativo: {epic}")
                    xrp_market = market
                    break
        
        if xrp_market:
            print(f"✅ Mercado XRP encontrado:")
            print(f"   - Epic: {xrp_market.get('epic', 'N/A')}")
            print(f"   - Nombre: {xrp_market.get('instrumentName', 'N/A')}")
            
            # Información de margen y apalancamiento
            instrument = xrp_market.get('instrument', {})
            margin_factor = instrument.get('marginFactor', 'N/A')
            print(f"   - Margen requerido: {margin_factor}%")
            
            # Calcular apalancamiento (100 / margin_factor)
            if isinstance(margin_factor, (int, float)) and margin_factor > 0:
                leverage = 100 / margin_factor
                print(f"   - Apalancamiento máximo: {leverage:.1f}x")
            else:
                print(f"   - Apalancamiento: N/A")
            
            # Reglas de trading
            dealing_rules = xrp_market.get('dealingRules', {})
            min_deal_size = dealing_rules.get('minDealSize', {}).get('value', 'N/A')
            max_deal_size = dealing_rules.get('maxDealSize', {}).get('value', 'N/A')
            print(f"   - Tamaño mínimo: {min_deal_size}")
            print(f"   - Tamaño máximo: {max_deal_size}")
            
            # Precio actual
            snapshot = xrp_market.get('snapshot', {})
            bid = snapshot.get('bid', 'N/A')
            offer = snapshot.get('offer', 'N/A')
            print(f"   - Precio bid: ${bid}")
            print(f"   - Precio offer: ${offer}")
            
        else:
            print("❌ No se encontró información para XRP")
            print(f"   - Mercados disponibles: {len(market_details)}")
            if market_details:
                print(f"   - Primer mercado: {market_details[0]}")
        
        # 2. Obtener posiciones actuales
        print("\n2. Obteniendo posiciones actuales...")
        positions_result = capital_client.get_positions()
        
        if positions_result.get("success"):
            positions = positions_result.get("positions", [])
            print(f"📊 Posiciones encontradas: {len(positions)}")
            
            for pos in positions:
                if pos.get("epic") == "XRPUSD":
                    print(f"\n🎯 Posición XRPUSD encontrada:")
                    print(f"   Deal ID: {pos.get('dealId')}")
                    print(f"   Dirección: {pos.get('direction')}")
                    print(f"   Tamaño: {pos.get('size')}")
                    print(f"   Precio apertura: {pos.get('openLevel')}")
                    print(f"   Precio actual: {pos.get('level')}")
                    print(f"   PnL: {pos.get('unrealisedPL')}")
                    print(f"   Margen requerido: {pos.get('requiredMargin')}")
                    
                    # Calcular apalancamiento efectivo
                    size = float(pos.get('size', 0))
                    open_price = float(pos.get('openLevel', 0))
                    required_margin = float(pos.get('requiredMargin', 0))
                    
                    if size > 0 and open_price > 0 and required_margin > 0:
                        position_value = size * open_price
                        effective_leverage = position_value / required_margin
                        
                        print(f"\n📈 Cálculos de apalancamiento:")
                        print(f"   Valor de posición: ${position_value:.2f}")
                        print(f"   Margen requerido: ${required_margin:.2f}")
                        print(f"   Apalancamiento efectivo: {effective_leverage:.1f}x")
        
        # 3. Obtener balance y calcular lo que debería permitir
        print("\n3. Calculando capacidad de trading...")
        balance_result = capital_client.get_available_balance()
        
        if balance_result.get("success"):
            available = balance_result.get("available", 0)
            print(f"💰 Balance disponible: ${available:.2f}")
            
            # Calcular 15% del balance
            fifteen_percent = available * 0.15
            print(f"📊 15% del balance: ${fifteen_percent:.2f}")
            
            # Con precio actual de XRP
            xrp_price = 2.35861  # Precio de tu posición
            
            # Sin apalancamiento
            units_no_leverage = fifteen_percent / xrp_price
            print(f"🔢 Unidades sin apalancamiento: {units_no_leverage:.2f}")
            
            # Con diferentes niveles de apalancamiento
            for leverage in [5, 10, 20, 30]:
                units_with_leverage = (fifteen_percent * leverage) / xrp_price
                print(f"🔢 Unidades con {leverage}x apalancamiento: {units_with_leverage:.2f}")
                
                if abs(units_with_leverage - 1137) < 50:  # Cercano a tu posición real
                    print(f"   ✅ ¡Este apalancamiento ({leverage}x) está cerca de tu posición real!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
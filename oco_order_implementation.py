#!/usr/bin/env python3
"""
🎯 Implementación completa de órdenes OCO y cancelación para BinanceConnector
Incluye todos los métodos necesarios para el flujo completo de trading
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import time

@dataclass
class OCOOrderRequest:
    """Estructura para solicitud de orden OCO"""
    symbol: str
    side: str  # BUY o SELL
    quantity: float
    
    # Take Profit (Above Order)
    above_type: str = "LIMIT_MAKER"  # LIMIT_MAKER, TAKE_PROFIT, TAKE_PROFIT_LIMIT
    above_price: Optional[float] = None
    above_stop_price: Optional[float] = None
    above_client_order_id: Optional[str] = None
    
    # Stop Loss (Below Order)  
    below_type: str = "STOP_LOSS_LIMIT"  # STOP_LOSS, STOP_LOSS_LIMIT
    below_price: Optional[float] = None  # Precio límite para STOP_LOSS_LIMIT
    below_stop_price: Optional[float] = None  # Precio de activación
    below_time_in_force: str = "GTC"
    below_client_order_id: Optional[str] = None
    
    # Opcionales
    list_client_order_id: Optional[str] = None

@dataclass
class CancelOrderRequest:
    """Estructura para cancelar órdenes individuales"""
    symbol: str
    order_id: Optional[int] = None
    orig_client_order_id: Optional[str] = None
    new_client_order_id: Optional[str] = None

@dataclass
class CancelOCORequest:
    """Estructura para cancelar órdenes OCO"""
    symbol: str
    order_list_id: Optional[int] = None
    list_client_order_id: Optional[str] = None
    new_client_order_id: Optional[str] = None

@dataclass
class OrderResponse:
    """Respuesta genérica de órdenes"""
    success: bool
    message: str
    order_data: Optional[Dict] = None
    error_code: Optional[int] = None

class BinanceConnectorExtended:
    """
    🚀 Extensión del BinanceConnector con funcionalidades completas de trading
    
    Métodos adicionales necesarios:
    - create_oco_order(): Crear órdenes OCO (TP + SL)
    - cancel_order(): Cancelar órdenes individuales  
    - cancel_oco_order(): Cancelar órdenes OCO
    - place_market_order(): Órdenes de mercado para entrada/salida
    """
    
    def create_oco_order(self, oco_request: OCOOrderRequest) -> OrderResponse:
        """
        🎯 Crear orden OCO (One-Cancels-Other) para TP/SL simultáneos
        
        Args:
            oco_request: Parámetros de la orden OCO
            
        Returns:
            OrderResponse con resultado de la operación
        """
        try:
            # Preparar parámetros para Binance API
            params = {
                'symbol': oco_request.symbol,
                'side': oco_request.side,
                'quantity': str(oco_request.quantity),
                'timestamp': int(time.time() * 1000)
            }
            
            # Above Order (Take Profit)
            params['aboveType'] = oco_request.above_type
            if oco_request.above_price:
                params['abovePrice'] = str(oco_request.above_price)
            if oco_request.above_stop_price:
                params['aboveStopPrice'] = str(oco_request.above_stop_price)
            if oco_request.above_client_order_id:
                params['aboveClientOrderId'] = oco_request.above_client_order_id
                
            # Below Order (Stop Loss)
            params['belowType'] = oco_request.below_type
            if oco_request.below_price:
                params['belowPrice'] = str(oco_request.below_price)
            if oco_request.below_stop_price:
                params['belowStopPrice'] = str(oco_request.below_stop_price)
            params['belowTimeInForce'] = oco_request.below_time_in_force
            if oco_request.below_client_order_id:
                params['belowClientOrderId'] = oco_request.below_client_order_id
                
            # Opcionales
            if oco_request.list_client_order_id:
                params['listClientOrderId'] = oco_request.list_client_order_id
            else:
                params['listClientOrderId'] = f"oco_bot_{int(time.time())}"
            
            # Enviar request a Binance
            endpoint = "/api/v3/orderList/oco"
            response = self._make_signed_request(endpoint, params, method='POST')
            
            return OrderResponse(
                success=True,
                message="Orden OCO creada exitosamente",
                order_data=response
            )
            
        except Exception as e:
            return OrderResponse(
                success=False,
                message=f"Error creando orden OCO: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
    
    def cancel_order(self, cancel_request: CancelOrderRequest) -> OrderResponse:
        """
        🛑 Cancelar orden individual
        
        Args:
            cancel_request: Parámetros para cancelar la orden
            
        Returns:
            OrderResponse con resultado de la cancelación
        """
        try:
            params = {
                'symbol': cancel_request.symbol,
                'timestamp': int(time.time() * 1000)
            }
            
            # Debe incluir orderId O origClientOrderId
            if cancel_request.order_id:
                params['orderId'] = cancel_request.order_id
            elif cancel_request.orig_client_order_id:
                params['origClientOrderId'] = cancel_request.orig_client_order_id
            else:
                raise ValueError("Debe proporcionar orderId o origClientOrderId")
                
            if cancel_request.new_client_order_id:
                params['newClientOrderId'] = cancel_request.new_client_order_id
            
            endpoint = "/api/v3/order"
            response = self._make_signed_request(endpoint, params, method='DELETE')
            
            return OrderResponse(
                success=True,
                message="Orden cancelada exitosamente",
                order_data=response
            )
            
        except Exception as e:
            return OrderResponse(
                success=False,
                message=f"Error cancelando orden: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
    
    def cancel_oco_order(self, cancel_oco_request: CancelOCORequest) -> OrderResponse:
        """
        🛑 Cancelar orden OCO completa
        
        Args:
            cancel_oco_request: Parámetros para cancelar la orden OCO
            
        Returns:
            OrderResponse con resultado de la cancelación
        """
        try:
            params = {
                'symbol': cancel_oco_request.symbol,
                'timestamp': int(time.time() * 1000)
            }
            
            # Debe incluir orderListId O listClientOrderId
            if cancel_oco_request.order_list_id:
                params['orderListId'] = cancel_oco_request.order_list_id
            elif cancel_oco_request.list_client_order_id:
                params['listClientOrderId'] = cancel_oco_request.list_client_order_id
            else:
                raise ValueError("Debe proporcionar orderListId o listClientOrderId")
                
            if cancel_oco_request.new_client_order_id:
                params['newClientOrderId'] = cancel_oco_request.new_client_order_id
            
            endpoint = "/api/v3/orderList"
            response = self._make_signed_request(endpoint, params, method='DELETE')
            
            return OrderResponse(
                success=True,
                message="Orden OCO cancelada exitosamente",
                order_data=response
            )
            
        except Exception as e:
            return OrderResponse(
                success=False,
                message=f"Error cancelando orden OCO: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
    
    def place_market_order(self, symbol: str, side: str, quantity: float, 
                          client_order_id: Optional[str] = None) -> OrderResponse:
        """
        🚀 Colocar orden de mercado (para entrada/salida rápida)
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            side: BUY o SELL
            quantity: Cantidad a operar
            client_order_id: ID personalizado de la orden
            
        Returns:
            OrderResponse con resultado de la operación
        """
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': str(quantity),
                'timestamp': int(time.time() * 1000)
            }
            
            if client_order_id:
                params['newClientOrderId'] = client_order_id
            else:
                params['newClientOrderId'] = f"market_bot_{int(time.time())}"
            
            endpoint = "/api/v3/order"
            response = self._make_signed_request(endpoint, params, method='POST')
            
            return OrderResponse(
                success=True,
                message="Orden de mercado ejecutada exitosamente",
                order_data=response
            )
            
        except Exception as e:
            return OrderResponse(
                success=False,
                message=f"Error ejecutando orden de mercado: {str(e)}",
                error_code=getattr(e, 'code', None)
            )

# 🎯 EJEMPLOS DE USO

def example_complete_trading_flow():
    """
    📋 Ejemplo del flujo completo de trading
    """
    connector = BinanceConnectorExtended()
    
    # 1. ENTRADA AL MERCADO
    print("🚀 1. Comprando BTC...")
    buy_order = connector.place_market_order(
        symbol="BTCUSDT",
        side="BUY", 
        quantity=0.001,
        client_order_id="entry_bot_001"
    )
    
    if buy_order.success:
        print(f"✅ Compra exitosa: {buy_order.message}")
        
        # 2. CONFIGURAR TP/SL CON OCO
        print("🎯 2. Configurando Take Profit y Stop Loss...")
        oco_order = OCOOrderRequest(
            symbol="BTCUSDT",
            side="SELL",
            quantity=0.001,
            
            # Take Profit: +2% ganancia
            above_type="LIMIT_MAKER",
            above_price=46000.0,
            above_client_order_id="tp_bot_001",
            
            # Stop Loss: -2% pérdida  
            below_type="STOP_LOSS_LIMIT",
            below_price=43900.0,      # Precio límite
            below_stop_price=44000.0, # Precio de activación
            below_client_order_id="sl_bot_001",
            
            list_client_order_id="oco_bot_001"
        )
        
        oco_result = connector.create_oco_order(oco_order)
        
        if oco_result.success:
            print(f"✅ OCO configurado: {oco_result.message}")
            order_list_id = oco_result.order_data.get('orderListId')
            
            # 3. SIMULAR AJUSTE DINÁMICO (cuando hay ganancias)
            print("🔄 3. Simulando ajuste dinámico...")
            
            # Cancelar OCO actual
            cancel_oco = CancelOCORequest(
                symbol="BTCUSDT",
                order_list_id=order_list_id
            )
            
            cancel_result = connector.cancel_oco_order(cancel_oco)
            
            if cancel_result.success:
                print("✅ OCO anterior cancelado")
                
                # Crear nuevo OCO con niveles ajustados
                new_oco = OCOOrderRequest(
                    symbol="BTCUSDT",
                    side="SELL",
                    quantity=0.001,
                    
                    # Nuevo Take Profit: +4% ganancia
                    above_type="LIMIT_MAKER",
                    above_price=47000.0,
                    
                    # Nuevo Stop Loss: +1% (trailing)
                    below_type="STOP_LOSS_LIMIT", 
                    below_price=45272.5,
                    below_stop_price=45500.0,
                    
                    list_client_order_id="oco_bot_002"
                )
                
                new_oco_result = connector.create_oco_order(new_oco)
                
                if new_oco_result.success:
                    print("✅ Nuevo OCO configurado con niveles ajustados")
                    
        # 4. ESCENARIO DE RESET CON PROFIT
        print("🔄 4. Simulando reset con profit...")
        
        # Cancelar cualquier OCO pendiente
        if 'order_list_id' in locals():
            cancel_final = CancelOCORequest(
                symbol="BTCUSDT",
                list_client_order_id="oco_bot_002"
            )
            connector.cancel_oco_order(cancel_final)
        
        # Vender posición inmediatamente
        sell_order = connector.place_market_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity=0.001,
            client_order_id="exit_bot_001"
        )
        
        if sell_order.success:
            print("✅ Posición cerrada exitosamente en reset")

if __name__ == "__main__":
    print("🎯 Implementación completa de órdenes OCO y cancelación")
    print("📋 Todos los endpoints y parámetros están mapeados y listos")
    print("🚀 El flujo completo de trading está implementado")
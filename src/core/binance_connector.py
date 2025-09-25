#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Binance Connector - Conector para API de Binance

Este módulo implementa la conexión con la API de Binance para obtener:
- Información de cuenta
- Balances de criptomonedas
- Estado de trading
- Comisiones y permisos
- Datos para el dashboard en tiempo real
"""

import os
import time
import hmac
import hashlib
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from urllib.parse import urlencode

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BinanceConfig:
    """Configuración para el conector de Binance"""
    api_key: str
    secret_key: str
    base_url: str = "https://api.binance.com"
    timeout: int = 10
    recv_window: int = 5000

@dataclass
class AccountBalance:
    """Estructura para balance de cuenta"""
    asset: str
    free: float
    locked: float
    total: float

@dataclass
class AccountInfo:
    """Estructura para información de cuenta"""
    can_trade: bool
    can_withdraw: bool
    can_deposit: bool
    account_type: str
    maker_commission: float
    taker_commission: float
    balances: List[AccountBalance]
    total_balance_usdt: float
    update_time: datetime

@dataclass
class TestOrderRequest:
    """Estructura para solicitud de orden de prueba"""
    symbol: str
    side: str  # BUY o SELL
    type: str  # MARKET, LIMIT, STOP_LOSS, TAKE_PROFIT, etc.
    quantity: Optional[float] = None
    quote_order_qty: Optional[float] = None
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: Optional[str] = None  # GTC, IOC, FOK
    new_client_order_id: Optional[str] = None
    compute_commission_rates: bool = False

@dataclass
class TestOrderResponse:
    """Estructura para respuesta de orden de prueba"""
    success: bool
    message: str
    order_data: Optional[Dict] = None
    commission_rates: Optional[Dict] = None
    error_code: Optional[int] = None

@dataclass
class ActiveOrder:
    """Estructura para rastrear órdenes activas"""
    order_id: int
    client_order_id: str
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: str = "NEW"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ActiveOCOOrder:
    """Estructura para rastrear órdenes OCO activas"""
    order_list_id: int
    list_client_order_id: str
    symbol: str
    side: str
    quantity: float
    
    # Take Profit Order
    tp_order_id: int
    tp_client_order_id: str
    tp_price: float
    
    # Stop Loss Order  
    sl_order_id: int
    sl_client_order_id: str
    sl_stop_price: float
    sl_limit_price: Optional[float] = None
    
    status: str = "EXECUTING"
    created_at: datetime = None
    position_id: Optional[str] = None  # Para mapear con posiciones
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class TradingPosition:
    """Estructura para rastrear posiciones de trading"""
    position_id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    entry_order_id: Optional[int] = None
    entry_client_order_id: Optional[str] = None
    
    # OCO asociado
    oco_order: Optional[ActiveOCOOrder] = None
    
    # Estado
    status: str = "OPEN"  # OPEN, CLOSED, PARTIAL
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class OrderResponse:
    """Respuesta genérica de órdenes con tracking"""
    success: bool
    message: str
    order_data: Optional[Dict] = None
    active_order: Optional[ActiveOrder] = None
    active_oco: Optional[ActiveOCOOrder] = None
    error_code: Optional[int] = None

class BinanceConnector:
    """
    🔗 Conector principal para la API de Binance
    
    Maneja la autenticación, requests y parsing de respuestas
    """
    
    def __init__(self, config: BinanceConfig = None):
        """Inicializar el conector con configuración"""
        if config is None:
            config = self._load_config_from_env()
        
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.config.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        # 🎯 Sistema de tracking de órdenes y posiciones
        self.active_orders: Dict[int, ActiveOrder] = {}  # order_id -> ActiveOrder
        self.active_oco_orders: Dict[int, ActiveOCOOrder] = {}  # order_list_id -> ActiveOCOOrder
        self.trading_positions: Dict[str, TradingPosition] = {}  # position_id -> TradingPosition
        self.client_order_mapping: Dict[str, int] = {}  # client_order_id -> order_id
        self.oco_client_mapping: Dict[str, int] = {}  # list_client_order_id -> order_list_id
        
        # URL base de producción
        self.base_url = self.config.base_url
        
        logger.info(f"🔗 Binance Connector inicializado - Producción: {self.base_url}")
    
    def _load_config_from_env(self) -> BinanceConfig:
        """Cargar configuración desde variables de entorno"""
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        if not api_key or not secret_key:
            raise ValueError("❌ BINANCE_API_KEY y BINANCE_SECRET_KEY deben estar configuradas en .env")
        
        return BinanceConfig(
            api_key=api_key,
            secret_key=secret_key
        )
    
    def _generate_signature(self, query_string: str) -> str:
        """Generar firma HMAC SHA256 para autenticación"""
        return hmac.new(
            self.config.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_signed_request(self, endpoint: str, params: Dict = None, method: str = 'GET') -> Dict:
        """Realizar request firmado a la API de Binance"""
        if params is None:
            params = {}
        
        # Agregar timestamp y recvWindow
        params['timestamp'] = int(time.time() * 1000)
        params['recvWindow'] = self.config.recv_window
        
        # Crear query string
        query_string = urlencode(params)
        
        # Generar firma
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        # Realizar request
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'POST':
                response = self.session.post(url, data=params, timeout=self.config.timeout)
            else:
                response = self.session.get(url, params=params, timeout=self.config.timeout)
            
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"✅ Request {method} exitoso a {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en request a {endpoint}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"❌ Error de API: {error_data}")
                except:
                    logger.error(f"❌ Response status: {e.response.status_code}")
            raise
    
    def get_account_info(self) -> AccountInfo:
        """
        📊 Obtener información completa de la cuenta
        
        Returns:
            AccountInfo: Información estructurada de la cuenta
        """
        logger.info("📊 Obteniendo información de cuenta...")
        
        try:
            data = self._make_signed_request('/api/v3/account')
            
            # Procesar balances
            balances = []
            total_balance_usdt = 0.0
            
            for balance_data in data.get('balances', []):
                asset = balance_data['asset']
                free = float(balance_data['free'])
                locked = float(balance_data['locked'])
                total = free + locked
                
                # Solo incluir balances con valor > 0
                if total > 0:
                    balance = AccountBalance(
                        asset=asset,
                        free=free,
                        locked=locked,
                        total=total
                    )
                    balances.append(balance)
                    
                    # Sumar al total en USDT (simplificado, USDT = 1:1)
                    if asset == 'USDT':
                        total_balance_usdt += total
            
            # Crear objeto AccountInfo
            account_info = AccountInfo(
                can_trade=data.get('canTrade', False),
                can_withdraw=data.get('canWithdraw', False),
                can_deposit=data.get('canDeposit', False),
                account_type=data.get('accountType', 'UNKNOWN'),
                maker_commission=float(data.get('commissionRates', {}).get('maker', 0)),
                taker_commission=float(data.get('commissionRates', {}).get('taker', 0)),
                balances=balances,
                total_balance_usdt=total_balance_usdt,
                update_time=datetime.fromtimestamp(data.get('updateTime', 0) / 1000)
            )
            
            logger.info(f"✅ Información de cuenta obtenida - Balances: {len(balances)}")
            return account_info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de cuenta: {e}")
            raise
    
    def get_balance_by_asset(self, asset: str) -> Optional[AccountBalance]:
        """
        💰 Obtener balance específico de un asset
        
        Args:
            asset: Símbolo del asset (ej: 'BTC', 'USDT')
            
        Returns:
            AccountBalance o None si no se encuentra
        """
        account_info = self.get_account_info()
        
        for balance in account_info.balances:
            if balance.asset == asset:
                return balance
        
        return None
    
    def get_usdt_balance(self) -> float:
        """
        💵 Obtener balance de USDT disponible
        
        Returns:
            float: Balance de USDT libre para trading
        """
        usdt_balance = self.get_balance_by_asset('USDT')
        return usdt_balance.free if usdt_balance else 0.0
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        📈 Obtener resumen del portfolio para el dashboard
        
        Returns:
            Dict con métricas del portfolio
        """
        logger.info("📈 Generando resumen del portfolio...")
        
        try:
            account_info = self.get_account_info()
            
            # Calcular métricas
            total_assets = len(account_info.balances)
            usdt_balance = self.get_usdt_balance()
            
            # Separar balances por tipo
            crypto_balances = [b for b in account_info.balances if b.asset != 'USDT' and b.total > 0]
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'account_status': {
                    'can_trade': account_info.can_trade,
                    'can_withdraw': account_info.can_withdraw,
                    'can_deposit': account_info.can_deposit,
                    'account_type': account_info.account_type
                },
                'balances': {
                    'usdt_available': usdt_balance,
                    'total_assets': total_assets,
                    'crypto_positions': len(crypto_balances),
                    'total_balance_usdt': account_info.total_balance_usdt
                },
                'trading_fees': {
                    'maker_commission': account_info.maker_commission,
                    'taker_commission': account_info.taker_commission
                },
                'positions': [
                    {
                        'asset': balance.asset,
                        'free': balance.free,
                        'locked': balance.locked,
                        'total': balance.total
                    }
                    for balance in crypto_balances
                ],
                'last_update': account_info.update_time.isoformat()
            }
            
            logger.info(f"✅ Resumen generado - USDT: ${usdt_balance:.2f}, Posiciones: {len(crypto_balances)}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen del portfolio: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        🔍 Probar conexión con la API de Binance
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            logger.info("🔍 Probando conexión con Binance...")
            
            # Test endpoint público primero
            response = self.session.get(f"{self.base_url}/api/v3/ping", timeout=self.config.timeout)
            response.raise_for_status()
            
            # Test endpoint con autenticación
            account_info = self.get_account_info()
            
            logger.info(f"✅ Conexión exitosa - Cuenta: {account_info.account_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
    
    def test_order(self, order_request: TestOrderRequest) -> TestOrderResponse:
        """
        🧪 Probar una orden sin ejecutarla usando /api/v3/order/test
        
        Args:
            order_request: Datos de la orden a probar
            
        Returns:
            TestOrderResponse: Resultado de la prueba
        """
        try:
            logger.info(f"🧪 Probando orden: {order_request.symbol} {order_request.side} {order_request.type}")
            
            # Preparar parámetros para la API
            params = {
                'symbol': order_request.symbol,
                'side': order_request.side,
                'type': order_request.type
            }
            
            # Agregar parámetros opcionales según el tipo de orden
            if order_request.quantity is not None:
                params['quantity'] = str(order_request.quantity)
            
            if order_request.quote_order_qty is not None:
                params['quoteOrderQty'] = str(order_request.quote_order_qty)
            
            if order_request.price is not None:
                params['price'] = str(order_request.price)
            
            if order_request.stop_price is not None:
                params['stopPrice'] = str(order_request.stop_price)
            
            if order_request.time_in_force is not None:
                params['timeInForce'] = order_request.time_in_force
            
            if order_request.new_client_order_id is not None:
                params['newClientOrderId'] = order_request.new_client_order_id
            
            if order_request.compute_commission_rates:
                params['computeCommissionRates'] = 'true'
            
            # Realizar request al endpoint de test (DEBE ser POST)
            response_data = self._make_signed_request('/api/v3/order/test', params, method='POST')
            
            logger.info(f"✅ Orden de prueba exitosa para {order_request.symbol}")
            
            return TestOrderResponse(
                success=True,
                message=f"Orden de prueba exitosa para {order_request.symbol}",
                order_data=response_data,
                commission_rates=response_data.get('commissionRates') if order_request.compute_commission_rates else None
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en request de orden de prueba: {e}"
            error_code = None
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('msg', error_msg)
                    error_code = error_data.get('code')
                except:
                    error_msg = f"HTTP {e.response.status_code}: {error_msg}"
            
            logger.error(f"❌ {error_msg}")
            
            return TestOrderResponse(
                success=False,
                message=error_msg,
                error_code=error_code
            )
            
        except Exception as e:
            error_msg = f"Error inesperado en orden de prueba: {e}"
            logger.error(f"❌ {error_msg}")
            
            return TestOrderResponse(
                success=False,
                message=error_msg
            )
    
    # 🎯 MÉTODOS DE TRACKING DE ÓRDENES Y POSICIONES
    
    def _generate_position_id(self, symbol: str, side: str) -> str:
        """Generar ID único para posición"""
        timestamp = int(time.time() * 1000)
        return f"{symbol}_{side}_{timestamp}"
    
    def _generate_client_order_id(self, prefix: str = "bot") -> str:
        """Generar client order ID único"""
        timestamp = int(time.time() * 1000)
        return f"{prefix}_{timestamp}"
    
    def create_oco_order(self, symbol: str, side: str, quantity: float,
                        tp_price: float, sl_stop_price: float, 
                        sl_limit_price: Optional[float] = None,
                        position_id: Optional[str] = None) -> OrderResponse:
        """
        🎯 Crear orden OCO con tracking completo
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            side: BUY o SELL
            quantity: Cantidad a operar
            tp_price: Precio de Take Profit
            sl_stop_price: Precio de activación del Stop Loss
            sl_limit_price: Precio límite del Stop Loss (opcional)
            position_id: ID de la posición asociada
            
        Returns:
            OrderResponse con tracking de la orden OCO
        """
        try:
            # Generar IDs únicos
            list_client_order_id = self._generate_client_order_id("oco")
            tp_client_order_id = self._generate_client_order_id("tp")
            sl_client_order_id = self._generate_client_order_id("sl")
            
            # Preparar parámetros para Binance API
            params = {
                'symbol': symbol,
                'side': side,
                'quantity': str(quantity),
                'listClientOrderId': list_client_order_id,
                
                # Take Profit (Above Order)
                'aboveType': 'LIMIT_MAKER',
                'abovePrice': str(tp_price),
                'aboveClientOrderId': tp_client_order_id,
                
                # Stop Loss (Below Order)
                'belowType': 'STOP_LOSS_LIMIT' if sl_limit_price else 'STOP_LOSS',
                'belowStopPrice': str(sl_stop_price),
                'belowClientOrderId': sl_client_order_id,
                'belowTimeInForce': 'GTC',
                
                'timestamp': int(time.time() * 1000)
            }
            
            # Agregar precio límite si se especifica
            if sl_limit_price:
                params['belowPrice'] = str(sl_limit_price)
            
            # Enviar request a Binance
            endpoint = "/api/v3/orderList/oco"
            response = self._make_signed_request(endpoint, params, method='POST')
            
            # Extraer IDs de la respuesta
            order_list_id = response['orderListId']
            orders = response['orders']
            
            # Identificar órdenes TP y SL
            tp_order_id = None
            sl_order_id = None
            
            for order in orders:
                if order['clientOrderId'] == tp_client_order_id:
                    tp_order_id = order['orderId']
                elif order['clientOrderId'] == sl_client_order_id:
                    sl_order_id = order['orderId']
            
            # Crear objeto de tracking
            oco_order = ActiveOCOOrder(
                order_list_id=order_list_id,
                list_client_order_id=list_client_order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                tp_order_id=tp_order_id,
                tp_client_order_id=tp_client_order_id,
                tp_price=tp_price,
                sl_order_id=sl_order_id,
                sl_client_order_id=sl_client_order_id,
                sl_stop_price=sl_stop_price,
                sl_limit_price=sl_limit_price,
                position_id=position_id
            )
            
            # Guardar en tracking
            self.active_oco_orders[order_list_id] = oco_order
            self.oco_client_mapping[list_client_order_id] = order_list_id
            
            logger.info(f"✅ OCO creado: {symbol} - OrderListId: {order_list_id}")
            
            return OrderResponse(
                success=True,
                message=f"Orden OCO creada exitosamente para {symbol}",
                order_data=response,
                active_oco=oco_order
            )
            
        except Exception as e:
            logger.error(f"❌ Error creando orden OCO: {e}")
            return OrderResponse(
                success=False,
                message=f"Error creando orden OCO: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
    
    def cancel_oco_order(self, order_list_id: Optional[int] = None, 
                        list_client_order_id: Optional[str] = None) -> OrderResponse:
        """
        🛑 Cancelar orden OCO con tracking
        
        Args:
            order_list_id: ID de la lista de órdenes
            list_client_order_id: Client ID de la lista de órdenes
            
        Returns:
            OrderResponse con resultado de la cancelación
        """
        try:
            # Validar parámetros
            if not order_list_id and not list_client_order_id:
                raise ValueError("Debe proporcionar order_list_id o list_client_order_id")
            
            # Obtener order_list_id si solo se tiene client_order_id
            if not order_list_id and list_client_order_id:
                order_list_id = self.oco_client_mapping.get(list_client_order_id)
                if not order_list_id:
                    raise ValueError(f"No se encontró order_list_id para {list_client_order_id}")
            
            # Preparar parámetros
            params = {
                'symbol': self.active_oco_orders[order_list_id].symbol,
                'timestamp': int(time.time() * 1000)
            }
            
            if order_list_id:
                params['orderListId'] = order_list_id
            elif list_client_order_id:
                params['listClientOrderId'] = list_client_order_id
            
            # Enviar request
            endpoint = "/api/v3/orderList"
            response = self._make_signed_request(endpoint, params, method='DELETE')
            
            # Actualizar tracking
            if order_list_id in self.active_oco_orders:
                oco_order = self.active_oco_orders[order_list_id]
                oco_order.status = "CANCELED"
                
                # Remover del tracking activo
                del self.active_oco_orders[order_list_id]
                if oco_order.list_client_order_id in self.oco_client_mapping:
                    del self.oco_client_mapping[oco_order.list_client_order_id]
                
                logger.info(f"✅ OCO cancelado: {oco_order.symbol} - OrderListId: {order_list_id}")
            
            return OrderResponse(
                success=True,
                message="Orden OCO cancelada exitosamente",
                order_data=response
            )
            
        except Exception as e:
            logger.error(f"❌ Error cancelando orden OCO: {e}")
            return OrderResponse(
                success=False,
                message=f"Error cancelando orden OCO: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
    
    def place_market_order(self, symbol: str, side: str, quantity: float,
                          position_id: Optional[str] = None) -> OrderResponse:
        """
        🚀 Colocar orden de mercado con tracking
        
        Args:
            symbol: Par de trading
            side: BUY o SELL
            quantity: Cantidad a operar
            position_id: ID de posición asociada
            
        Returns:
            OrderResponse con tracking de la orden
        """
        try:
            client_order_id = self._generate_client_order_id("market")
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': 'MARKET',
                'quantity': str(quantity),
                'newClientOrderId': client_order_id,
                'timestamp': int(time.time() * 1000)
            }
            
            # Enviar request
            endpoint = "/api/v3/order"
            response = self._make_signed_request(endpoint, params, method='POST')
            
            # Crear objeto de tracking
            order_id = response['orderId']
            active_order = ActiveOrder(
                order_id=order_id,
                client_order_id=client_order_id,
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity,
                status=response.get('status', 'FILLED')
            )
            
            # Guardar en tracking
            self.active_orders[order_id] = active_order
            self.client_order_mapping[client_order_id] = order_id
            
            logger.info(f"✅ Orden MARKET ejecutada: {symbol} {side} {quantity}")
            
            return OrderResponse(
                success=True,
                message=f"Orden de mercado ejecutada exitosamente",
                order_data=response,
                active_order=active_order
            )
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando orden MARKET: {e}")
            return OrderResponse(
                success=False,
                message=f"Error ejecutando orden de mercado: {str(e)}",
                error_code=getattr(e, 'code', None)
            )
    
    def create_trading_position(self, symbol: str, side: str, quantity: float,
                              entry_price: float, entry_order_id: int,
                              tp_price: float, sl_stop_price: float,
                              sl_limit_price: Optional[float] = None) -> TradingPosition:
        """
        📊 Crear posición de trading completa con OCO
        
        Args:
            symbol: Par de trading
            side: BUY o SELL
            quantity: Cantidad de la posición
            entry_price: Precio de entrada
            entry_order_id: ID de la orden de entrada
            tp_price: Precio de Take Profit
            sl_stop_price: Precio de Stop Loss
            sl_limit_price: Precio límite del Stop Loss
            
        Returns:
            TradingPosition: Posición creada con OCO asociado
        """
        # Generar ID único para la posición
        position_id = self._generate_position_id(symbol, side)
        
        # Crear posición
        position = TradingPosition(
            position_id=position_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            entry_order_id=entry_order_id
        )
        
        # Crear OCO para TP/SL
        oco_side = "SELL" if side == "BUY" else "BUY"
        oco_response = self.create_oco_order(
            symbol=symbol,
            side=oco_side,
            quantity=quantity,
            tp_price=tp_price,
            sl_stop_price=sl_stop_price,
            sl_limit_price=sl_limit_price,
            position_id=position_id
        )
        
        if oco_response.success:
            position.oco_order = oco_response.active_oco
            
        # Guardar posición
        self.trading_positions[position_id] = position
        
        logger.info(f"📊 Posición creada: {position_id} - {symbol} {side} {quantity}")
        
        return position
    
    def get_active_positions(self) -> List[TradingPosition]:
        """Obtener todas las posiciones activas"""
        return [pos for pos in self.trading_positions.values() if pos.status == "OPEN"]
    
    def get_active_oco_orders(self) -> List[ActiveOCOOrder]:
        """Obtener todas las órdenes OCO activas"""
        return list(self.active_oco_orders.values())
    
    def close_position_with_profit(self, position_id: str) -> OrderResponse:
        """
        💰 Cerrar posición inmediatamente con ganancia (para reset)
        
        Args:
            position_id: ID de la posición a cerrar
            
        Returns:
            OrderResponse con resultado del cierre
        """
        try:
            if position_id not in self.trading_positions:
                raise ValueError(f"Posición {position_id} no encontrada")
            
            position = self.trading_positions[position_id]
            
            # 1. Cancelar OCO si existe
            if position.oco_order:
                cancel_result = self.cancel_oco_order(
                    order_list_id=position.oco_order.order_list_id
                )
                if not cancel_result.success:
                    logger.warning(f"⚠️ No se pudo cancelar OCO: {cancel_result.message}")
            
            # 2. Ejecutar orden de mercado para cerrar
            close_side = "SELL" if position.side == "BUY" else "BUY"
            close_result = self.place_market_order(
                symbol=position.symbol,
                side=close_side,
                quantity=position.quantity,
                position_id=position_id
            )
            
            if close_result.success:
                # Actualizar estado de la posición
                position.status = "CLOSED"
                logger.info(f"💰 Posición cerrada con profit: {position_id}")
            
            return close_result
            
        except Exception as e:
            logger.error(f"❌ Error cerrando posición: {e}")
            return OrderResponse(
                success=False,
                message=f"Error cerrando posición: {str(e)}"
            )
    
    def adjust_oco_levels(self, position_id: str, new_tp_price: float,
                         new_sl_stop_price: float, 
                         new_sl_limit_price: Optional[float] = None) -> OrderResponse:
        """
        🔄 Ajustar niveles de TP/SL dinámicamente
        
        Args:
            position_id: ID de la posición
            new_tp_price: Nuevo precio de Take Profit
            new_sl_stop_price: Nuevo precio de Stop Loss
            new_sl_limit_price: Nuevo precio límite del Stop Loss
            
        Returns:
            OrderResponse con resultado del ajuste
        """
        try:
            if position_id not in self.trading_positions:
                raise ValueError(f"Posición {position_id} no encontrada")
            
            position = self.trading_positions[position_id]
            
            if not position.oco_order:
                raise ValueError(f"Posición {position_id} no tiene OCO asociado")
            
            # 1. Cancelar OCO actual
            cancel_result = self.cancel_oco_order(
                order_list_id=position.oco_order.order_list_id
            )
            
            if not cancel_result.success:
                return cancel_result
            
            # 2. Crear nuevo OCO con niveles ajustados
            oco_side = "SELL" if position.side == "BUY" else "BUY"
            new_oco_result = self.create_oco_order(
                symbol=position.symbol,
                side=oco_side,
                quantity=position.quantity,
                tp_price=new_tp_price,
                sl_stop_price=new_sl_stop_price,
                sl_limit_price=new_sl_limit_price,
                position_id=position_id
            )
            
            if new_oco_result.success:
                # Actualizar posición con nuevo OCO
                position.oco_order = new_oco_result.active_oco
                logger.info(f"🔄 OCO ajustado para posición: {position_id}")
            
            return new_oco_result
            
        except Exception as e:
            logger.error(f"❌ Error ajustando OCO: {e}")
            return OrderResponse(
                success=False,
                message=f"Error ajustando OCO: {str(e)}"
            )

# Variables globales para fácil acceso
_binance_connector = None

def get_binance_connector() -> BinanceConnector:
    """
    🔗 Obtener instancia singleton del conector de Binance
    
    Returns:
        BinanceConnector: Instancia del conector
    """
    global _binance_connector
    
    if _binance_connector is None:
        _binance_connector = BinanceConnector()
    
    return _binance_connector

def get_account_data() -> Dict[str, Any]:
    """
    📊 Función de conveniencia para obtener datos de cuenta
    
    Returns:
        Dict con información de cuenta formateada para el dashboard
    """
    connector = get_binance_connector()
    return connector.get_portfolio_summary()

def get_usdt_balance() -> float:
    """
    💵 Función de conveniencia para obtener balance de USDT
    
    Returns:
        float: Balance de USDT disponible
    """
    connector = get_binance_connector()
    return connector.get_usdt_balance()

if __name__ == "__main__":
    # Test básico del conector
    print("🔗 Probando Binance Connector...")
    
    try:
        connector = BinanceConnector()
        
        if connector.test_connection():
            print("✅ Conexión exitosa!")
            
            # Obtener información de cuenta
            account_info = connector.get_account_info()
            print(f"📊 Cuenta: {account_info.account_type}")
            print(f"💰 USDT disponible: ${connector.get_usdt_balance():.2f}")
            print(f"📈 Total de assets: {len(account_info.balances)}")
            
            # Mostrar resumen
            summary = connector.get_portfolio_summary()
            print(f"📋 Resumen generado con {summary['balances']['total_assets']} assets")
            
        else:
            print("❌ Error de conexión")
            
    except Exception as e:
        print(f"❌ Error: {e}")
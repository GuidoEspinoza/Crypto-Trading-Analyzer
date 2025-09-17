#!/usr/bin/env python3
"""
🎯 Position Adjuster - Sistema de TP/SL Ajustables
Maneja el ajuste dinámico de Take Profit y Stop Loss para posiciones activas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.config.config_manager import ConfigManager

# Inicializar configuración centralizada
try:
    config_manager = ConfigManager()
    config = config_manager.get_consolidated_config()
    if config is None:
        config = {}
except Exception as e:
    # Configuración de fallback en caso de error
    config = {
        'api': {'latency_simulation_sleep': 0.1}
    }
from src.database.database import db_manager

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)  # Solo errores críticos
logger.propagate = False  # No propagar logs al logger raíz

class AdjustmentReason(Enum):
    """Razones para ajustar TP/SL"""
    PROFIT_SCALING = "profit_scaling"  # Escalado de ganancias
    RISK_MANAGEMENT = "risk_management"  # Gestión de riesgo
    TRAILING_STOP = "trailing_stop"  # Trailing stop
    EMERGENCY_STOP = "emergency_stop"  # Stop de emergencia
    VOLATILITY_CHANGE = "volatility_change"  # Cambio de volatilidad
    PROFIT_PROTECTION = "profit_protection"  # Protección de ganancias

@dataclass
class AdjustmentResult:
    """Resultado de un ajuste de TP/SL"""
    success: bool
    symbol: str
    old_tp: float
    old_sl: float
    new_tp: float
    new_sl: float
    reason: AdjustmentReason
    timestamp: datetime
    message: str
    adjustment_count: int

@dataclass
class PositionInfo:
    """Información de una posición activa"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    side: str  # 'BUY' o 'SELL'
    current_tp: float
    current_sl: float
    entry_time: datetime
    unrealized_pnl: float
    unrealized_pnl_pct: float

class PositionAdjuster:
    """
    🎯 Gestor de ajustes dinámicos de TP/SL
    
    Funcionalidades:
    - Monitoreo continuo de posiciones activas
    - Cálculo de nuevos niveles de TP/SL basados en condiciones de mercado
    - Simulación de cancelación y recreación de órdenes OCO
    - Límite de 5 ajustes por posición
    - Logging detallado de todas las operaciones
    """
    
    def __init__(self, config=None, simulation_mode=True):
        self.config = config  # Almacenar config como atributo para tests
        self.simulation_mode = simulation_mode
        self.adjustment_counts = {}  # Contador de ajustes por posición
        # Obtener max_adjustments desde configuración centralizada
        if config and isinstance(config, dict):
            self.max_adjustments = config.get("risk_manager", {}).get("max_tp_adjustments", 3)
        else:
            self.max_adjustments = 3  # Default value
        # Obtener configuración del perfil activo o usar el config proporcionado
        if isinstance(config, dict):
            self.profile = config
        else:
            # Default profile configuration (replaced trading_profiles reference)
            self.profile = {
                'position_check_interval': 20,
                'max_tp_adjustments': 3,
                'adjustment_threshold': 0.02
            }
        
        # Configuración de intervalos - usar el valor del perfil específico
        self.monitoring_interval = config.get("trading_bot", {}).get("position_check_interval", 20)
        self.active_positions = {}
        self.adjustment_history = []
        self.is_running = False
        self.adjustment_callback = None  # Callback para notificar ajustes
        self.db_manager = db_manager  # Agregar referencia al db_manager
        
        logger.info(f"🎯 PositionAdjuster inicializado (Modo: {'Simulación' if simulation_mode else 'Real'})")
    
    def set_adjustment_callback(self, callback):
        """Establecer callback para notificar ajustes"""
        self.adjustment_callback = callback
        logger.info("📞 Callback de ajustes configurado")
    
    def update_monitoring_interval(self, new_interval: int):
        """⏱️ Actualizar intervalo de monitoreo dinámicamente"""
        if new_interval < 5:
            raise ValueError("El intervalo de monitoreo debe ser al menos 5 segundos")
        
        old_interval = self.monitoring_interval
        self.monitoring_interval = new_interval
        
        if self.adjustment_callback:
            self.adjustment_callback({
                'type': 'config_update',
                'message': f"Intervalo de monitoreo actualizado de {old_interval}s a {new_interval}s"
            })
    
    def update_max_adjustments(self, new_max: int):
        """🔄 Actualizar máximo de ajustes por posición"""
        if new_max < 1:
            raise ValueError("El máximo de ajustes debe ser al menos 1")
        
        old_max = self.max_adjustments
        self.max_adjustments = new_max
        
        if self.adjustment_callback:
            self.adjustment_callback({
                'type': 'config_update',
                'message': f"Máximo de ajustes por posición actualizado de {old_max} a {new_max}"
            })
    
    def get_current_config(self) -> Dict:
        """📋 Obtener configuración actual del position adjuster"""
        return {
            'monitoring_interval': self.monitoring_interval,
            'max_adjustments': self.max_adjustments,
            'is_monitoring': self.is_running,
            'is_paused': self.is_paused(),
            'profile_name': getattr(self.profile, 'name', 'unknown'),
            'total_positions_tracked': len(self.adjustment_counts),
            'active_positions': len(self._get_active_positions()) if self.is_running else 0
        }
    
    async def start_monitoring(self):
        """🚀 Iniciar monitoreo de posiciones
        
        IMPORTANTE: Este monitoreo funciona independientemente del límite de trades diarios.
        Los ajustes de TP/SL no cuentan como trades nuevos y pueden ejecutarse incluso
        cuando se ha alcanzado el max_daily_trades.
        """
        if self.is_running:
            logger.warning("⚠️ El monitoreo ya está activo")
            return
        
        self.is_running = True
        logger.info(f"🔄 Iniciando monitoreo de posiciones (intervalo: {self.monitoring_interval}s)")
        logger.info("📝 Los ajustes de TP/SL funcionan independientemente del límite de trades diarios")
        
        try:
            while self.is_running:
                await self._monitor_positions()
                await asyncio.sleep(self.monitoring_interval)
        except Exception as e:
            logger.error(f"❌ Error en monitoreo de posiciones: {e}")
            self.is_running = False
    
    async def stop_monitoring(self):
        """🛑 Detener monitoreo de posiciones"""
        self.is_running = False
        logger.info("🛑 Monitoreo de posiciones detenido")
    
    def pause_monitoring(self):
        """⏸️ Pausar monitoreo temporalmente"""
        if not hasattr(self, '_is_paused'):
            self._is_paused = False
        
        self._is_paused = True
        logger.info("⏸️ Monitoreo pausado temporalmente")
        
        if self.adjustment_callback:
            self.adjustment_callback({
                'type': 'monitoring_paused',
                'message': 'Monitoreo pausado temporalmente'
            })
    
    def resume_monitoring(self):
        """▶️ Reanudar monitoreo"""
        if not hasattr(self, '_is_paused'):
            self._is_paused = False
        
        self._is_paused = False
        logger.info("▶️ Monitoreo reanudado")
        
        if self.adjustment_callback:
            self.adjustment_callback({
                'type': 'monitoring_resumed',
                'message': 'Monitoreo reanudado'
            })
    
    def is_paused(self) -> bool:
        """❓ Verificar si el monitoreo está pausado"""
        return getattr(self, '_is_paused', False)
    
    async def _monitor_positions(self):
        """🔍 Monitorear posiciones activas y evaluar ajustes"""
        try:
            # Verificar si el monitoreo está pausado
            if self.is_paused():
                return
            
            # Obtener posiciones activas desde la base de datos
            positions = self._get_active_positions()
            
            if not positions:
                logger.debug("📊 No hay posiciones activas para monitorear")
                return
            
            logger.info(f"📊 Monitoreando {len(positions)} posiciones activas")
            
            for position in positions:
                # Verificar pausa antes de cada evaluación
                if self.is_paused():
                    break
                await self._evaluate_position_adjustment(position)
                
        except Exception as e:
            logger.error(f"❌ Error monitoreando posiciones: {e}")
    
    def _get_active_positions(self) -> List[PositionInfo]:
        """📋 Obtener posiciones activas desde la base de datos"""
        try:
            # Obtener trades activos desde la base de datos
            active_trades = db_manager.get_active_trades(is_paper=True)
            positions = []
            
            for trade in active_trades:
                # Simular precio actual (en producción vendría de la API)
                current_price = self._get_current_price(trade['symbol'])
                
                # Calcular PnL no realizado
                if trade['side'] == 'BUY':
                    unrealized_pnl = (current_price - trade['entry_price']) * trade['quantity']
                else:
                    unrealized_pnl = (trade['entry_price'] - current_price) * trade['quantity']
                
                unrealized_pnl_pct = (unrealized_pnl / (trade['entry_price'] * trade['quantity'])) * 100
                
                position = PositionInfo(
                    symbol=trade['symbol'],
                    entry_price=trade['entry_price'],
                    current_price=current_price,
                    quantity=trade['quantity'],
                    side=trade['side'],
                    current_tp=trade.get('take_profit_price', 0),
                    current_sl=trade.get('stop_loss_price', 0),
                    entry_time=trade['entry_time'],
                    unrealized_pnl=unrealized_pnl,
                    unrealized_pnl_pct=unrealized_pnl_pct
                )
                
                positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo posiciones activas: {e}")
            return []
    
    def _calculate_pnl(self, side: str, entry_price: float, current_price: float, size: float) -> Tuple[float, float]:
        """💰 Calcular PnL y PnL porcentual"""
        try:
            if side.upper() in ['BUY', 'LONG']:
                pnl = (current_price - entry_price) * size
            else:  # SELL, SHORT
                pnl = (entry_price - current_price) * size
            
            # Calcular PnL porcentual
            entry_value = entry_price * size
            pnl_pct = (pnl / entry_value) * 100 if entry_value > 0 else 0
            
            return pnl, pnl_pct
            
        except Exception as e:
            logger.error(f"❌ Error calculando PnL: {e}")
            return 0.0, 0.0
    
    def _get_current_price(self, symbol: str) -> float:
        """💰 Obtener precio actual del símbolo (simulado)"""
        try:
            # En modo simulación, usar precio de la base de datos + variación aleatoria
            import random
            
            # Obtener último precio conocido
            last_trade_price = db_manager.get_last_trade_for_symbol(symbol, is_paper=True)
            if last_trade_price:
                # Obtener configuración de variación de precio desde perfil
                price_variation = self.profile.get('price_simulation_variation', 0.02)  # 2% por defecto
                variation = random.uniform(-price_variation, price_variation)
                return last_trade_price * (1 + variation)
            
            # Fallback: precio base simulado desde configuración
            fallback_price = self.profile.get('simulation_fallback_price', 50000.0)
            return fallback_price
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo precio para {symbol}: {e}")
            return 0.0
    
    async def _evaluate_position_adjustment(self, position: PositionInfo):
        """🎯 Evaluar si una posición necesita ajuste de TP/SL
        
        NOTA: Los ajustes de TP/SL funcionan independientemente del límite de trades diarios.
        Solo se limitan por el número máximo de ajustes por posición (max_adjustments).
        """
        try:
            symbol = position.symbol
            
            # Verificar límite de ajustes por posición (independiente del límite de trades diarios)
            current_adjustments = self.adjustment_counts.get(symbol, 0)
            if current_adjustments >= self.max_adjustments:
                logger.debug(f"⏸️ {symbol}: Límite de ajustes por posición alcanzado ({current_adjustments}/{self.max_adjustments})")
                return
            
            # Evaluar condiciones para ajuste
            adjustment_needed, reason, new_tp, new_sl = self._calculate_new_levels_internal(position)
            
            if adjustment_needed:
                logger.info(f"🎯 {symbol}: Ajuste necesario - {reason.value}")
                logger.info(f"   📊 PnL actual: {position.unrealized_pnl_pct:+.2f}%")
                logger.info(f"   📈 TP: {position.current_tp:.2f} → {new_tp:.2f}")
                logger.info(f"   📉 SL: {position.current_sl:.2f} → {new_sl:.2f}")
                
                # Ejecutar ajuste
                result = await self._execute_adjustment(position, new_tp, new_sl, reason)
                
                if result.success:
                    # Actualizar contador
                    self.adjustment_counts[symbol] = current_adjustments + 1
                    self.adjustment_history.append(result)
                    
                    logger.info(f"✅ {symbol}: Ajuste #{current_adjustments + 1} completado")
                else:
                    logger.warning(f"❌ {symbol}: Fallo en ajuste - {result.message}")
            
        except Exception as e:
            logger.error(f"❌ Error evaluando ajuste para {position.symbol}: {e}")
    
    def _calculate_new_levels(self, position: PositionInfo, reason: AdjustmentReason = None, current_price: float = None) -> Tuple[float, float]:
        """🧮 Calcular nuevos niveles de TP/SL (versión para tests)"""
        if reason is None or current_price is None:
            # Usar la lógica original
            needs_adjustment, calc_reason, new_tp, new_sl = self._calculate_new_levels_internal(position)
            return new_tp, new_sl
        
        # Lógica específica para tests con reason y current_price
        try:
            entry_price = position.entry_price
            side = position.side
            
            if reason == AdjustmentReason.PROFIT_SCALING:
                # Escalado de ganancias
                tp_pct = self.profile.get('profit_protection_tp_pct', 0.03)
                sl_pct = self.profile.get('profit_protection_sl_pct', 0.01)
                if side.upper() in ['BUY', 'LONG']:
                    new_tp = current_price * (1 + tp_pct)
                    new_sl = entry_price * (1 + sl_pct)
                else:
                    new_tp = current_price * (1 - tp_pct)
                    new_sl = entry_price * (1 - sl_pct)
                    
            elif reason == AdjustmentReason.TRAILING_STOP:
                # Trailing stop
                tp_pct = self.profile.get('trailing_stop_tp_pct', 0.05)
                sl_pct = self.profile.get('trailing_stop_sl_pct', 0.02)
                if side.upper() in ['BUY', 'LONG']:
                    new_tp = current_price * (1 + tp_pct)
                    new_sl = current_price * (1 - sl_pct)
                else:
                    new_tp = current_price * (1 - tp_pct)
                    new_sl = current_price * (1 + sl_pct)
                    
            elif reason == AdjustmentReason.RISK_MANAGEMENT:
                # Gestión de riesgo
                tp_pct = self.profile.get('risk_management_tp_pct', 0.02)
                sl_pct = self.profile.get('risk_management_sl_pct', 0.015)
                if side.upper() in ['BUY', 'LONG']:
                    new_tp = entry_price * (1 + tp_pct)
                    new_sl = current_price * (1 - sl_pct)
                else:
                    new_tp = entry_price * (1 - tp_pct)
                    new_sl = current_price * (1 + sl_pct)
            else:
                # Valores por defecto
                new_tp = position.current_tp
                new_sl = position.current_sl
                
            return new_tp, new_sl
            
        except Exception as e:
            logger.error(f"❌ Error calculando nuevos niveles: {e}")
            return position.current_tp, position.current_sl
    
    def _calculate_new_levels_internal(self, position: PositionInfo) -> Tuple[bool, AdjustmentReason, float, float]:
        """🧮 Calcular nuevos niveles de TP/SL"""
        try:
            symbol = position.symbol
            current_price = position.current_price
            entry_price = position.entry_price
            side = position.side
            pnl_pct = position.unrealized_pnl_pct
            
            # Condición 1: Escalado de ganancias (posición ganadora > threshold%)
            profit_threshold = self.profile.get('profit_scaling_threshold', 1.0)  # 1% por defecto
            if pnl_pct > profit_threshold:
                # Mover SL más cerca para proteger ganancias
                sl_pct = self.profile.get('profit_protection_sl_pct', 0.01)
                tp_pct = self.profile.get('profit_protection_tp_pct', 0.03)
                if side == 'BUY':
                    new_sl = entry_price * (1 + sl_pct)  # SL para protección de ganancias
                    new_tp = current_price * (1 + tp_pct)  # TP para protección de ganancias
                else:
                    new_sl = entry_price * (1 - sl_pct)  # SL para protección de ganancias
                    new_tp = current_price * (1 - tp_pct)  # TP para protección de ganancias
                
                return True, AdjustmentReason.PROFIT_SCALING, new_tp, new_sl
            
            # Condición 2: Trailing Stop (posición muy ganadora)
            trailing_activation = self.profile.get('trailing_stop_activation', 2.0)  # 2% por defecto
            if pnl_pct > trailing_activation:
                # Implementar trailing stop más agresivo
                sl_pct = self.profile.get('trailing_stop_sl_pct', 0.02)  # 2% por defecto
                tp_pct = self.profile.get('trailing_stop_tp_pct', 0.05)  # 5% por defecto
                if side == 'BUY':
                    new_sl = current_price * (1 - sl_pct)  # SL dinámico
                    new_tp = current_price * (1 + tp_pct)  # TP dinámico
                else:
                    new_sl = current_price * (1 + sl_pct)  # SL dinámico
                    new_tp = current_price * (1 - tp_pct)  # TP dinámico
                
                return True, AdjustmentReason.TRAILING_STOP, new_tp, new_sl
            
            # Condición 3: Gestión de riesgo (posición perdedora < threshold%)
            risk_threshold = self.profile.get('risk_management_threshold', -1.0)
            if pnl_pct < risk_threshold:
                # Ajustar SL más conservador
                sl_pct = self.profile.get('risk_management_sl_pct', 0.015)
                tp_pct = self.profile.get('risk_management_tp_pct', 0.02)
                if side == 'BUY':
                    new_sl = current_price * (1 - sl_pct)  # SL más cerca
                    new_tp = entry_price * (1 + tp_pct)  # TP más conservador
                else:
                    new_sl = current_price * (1 + sl_pct)  # SL más cerca
                    new_tp = entry_price * (1 - tp_pct)  # TP más conservador
                
                return True, AdjustmentReason.RISK_MANAGEMENT, new_tp, new_sl
            
            # No se necesita ajuste
            return False, None, 0, 0
            
        except Exception as e:
            logger.error(f"❌ Error calculando nuevos niveles para {position.symbol}: {e}")
            return False, None, 0, 0
    
    async def _execute_adjustment(self, position: PositionInfo, new_tp: float, new_sl: float, reason: AdjustmentReason) -> AdjustmentResult:
        """⚡ Ejecutar ajuste de TP/SL (simulado)"""
        try:
            symbol = position.symbol
            
            if self.simulation_mode:
                # Simular cancelación de órdenes OCO existentes
                logger.info(f"🔄 {symbol}: Simulando cancelación de órdenes OCO existentes")
                await asyncio.sleep(config.get("api", {}).get("latency_simulation_sleep", 0.1))  # Simular latencia
                
                # Simular creación de nuevas órdenes OCO
                logger.info(f"🔄 {symbol}: Simulando creación de nuevas órdenes OCO")
                await asyncio.sleep(config.get("api", {}).get("latency_simulation_sleep", 0.1))  # Simular latencia
                
                # Actualizar en base de datos (simulado)
                success = self._update_position_levels(symbol, new_tp, new_sl)
                
                result = AdjustmentResult(
                    success=success,
                    symbol=symbol,
                    old_tp=position.current_tp,
                    old_sl=position.current_sl,
                    new_tp=new_tp,
                    new_sl=new_sl,
                    reason=reason,
                    timestamp=datetime.now(),
                    message=f"Ajuste simulado completado: TP {position.current_tp:.2f}→{new_tp:.2f}, SL {position.current_sl:.2f}→{new_sl:.2f}",
                    adjustment_count=self.adjustment_counts.get(symbol, 0) + 1
                )
                
                # Notificar ajuste mediante callback
                if success and self.adjustment_callback:
                    try:
                        self.adjustment_callback({
                            'type': 'adjustment',
                            'symbol': symbol,
                            'adjustment_type': reason.value,
                            'old_tp': position.current_tp,
                            'old_sl': position.current_sl,
                            'new_tp': new_tp,
                            'new_sl': new_sl,
                            'reason': f"TP: {position.current_tp:.2f}→{new_tp:.2f}, SL: {position.current_sl:.2f}→{new_sl:.2f}",
                            'timestamp': datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.error(f"❌ Error en callback de ajuste: {e}")
                
                return result
            
            else:
                # TODO: Implementar conexión real con Binance API
                logger.warning("⚠️ Modo real no implementado aún")
                return AdjustmentResult(
                    success=False,
                    symbol=symbol,
                    old_tp=position.current_tp,
                    old_sl=position.current_sl,
                    new_tp=new_tp,
                    new_sl=new_sl,
                    reason=reason,
                    timestamp=datetime.now(),
                    message="Modo real no implementado",
                    adjustment_count=0
                )
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando ajuste para {position.symbol}: {e}")
            return AdjustmentResult(
                success=False,
                symbol=position.symbol,
                old_tp=position.current_tp,
                old_sl=position.current_sl,
                new_tp=new_tp,
                new_sl=new_sl,
                reason=reason,
                timestamp=datetime.now(),
                message=f"Error: {str(e)}",
                adjustment_count=0
            )
    
    def _update_position_levels(self, symbol: str, new_tp: float, new_sl: float) -> bool:
        """💾 Actualizar niveles de TP/SL en base de datos (simulado)"""
        try:
            # En modo simulación, solo loggeamos el cambio
            logger.info(f"💾 {symbol}: Actualizando niveles en BD - TP: {new_tp:.2f}, SL: {new_sl:.2f}")
            # TODO: Implementar actualización real en base de datos
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando niveles para {symbol}: {e}")
            return False
    
    def get_adjustment_stats(self) -> Dict:
        """📊 Obtener estadísticas de ajustes"""
        total_adjustments = sum(self.adjustment_counts.values())
        successful_adjustments = len([r for r in self.adjustment_history if r.success])
        
        # Obtener configuración de cuántos ajustes recientes mostrar
        recent_count = self.profile.get('stats_recent_adjustments_count', 10)
        
        # Calcular estadísticas por razón de ajuste
        adjustments_by_reason = {}
        for adjustment in self.adjustment_history:
            reason = adjustment.reason.value
            if reason not in adjustments_by_reason:
                adjustments_by_reason[reason] = {'total': 0, 'successful': 0}
            adjustments_by_reason[reason]['total'] += 1
            if adjustment.success:
                adjustments_by_reason[reason]['successful'] += 1
        
        return {
            "total_positions_adjusted": len(self.adjustment_counts),
            "total_adjustments": total_adjustments,
            "successful_adjustments": successful_adjustments,
            "success_rate": (successful_adjustments / total_adjustments * 100) if total_adjustments > 0 else 0,
            "adjustments_by_symbol": dict(self.adjustment_counts),
            "adjustments_by_reason": adjustments_by_reason,
            "max_adjustments_per_position": self.max_adjustments,
            "monitoring_interval_seconds": self.monitoring_interval,
            "recent_adjustments": [{
                "symbol": r.symbol,
                "reason": r.reason.value,
                "timestamp": r.timestamp.strftime("%H:%M:%S"),
                "success": r.success,
                "old_tp": r.old_tp,
                "new_tp": r.new_tp,
                "old_sl": r.old_sl,
                "new_sl": r.new_sl
            } for r in self.adjustment_history[-recent_count:]]
        }
    
    def reset_adjustment_counts(self):
        """🔄 Resetear contadores de ajustes (para nuevo día)"""
        self.adjustment_counts.clear()
        self.adjustment_history.clear()
        logger.info("🔄 Contadores de ajustes reseteados")
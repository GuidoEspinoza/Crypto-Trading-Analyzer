"""
💰 Balance Manager - Gestión automática de balance de Capital.com
Mantiene la conexión activa y actualiza el balance periódicamente
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from src.core.capital_client import create_capital_client_from_env
from src.database.database import DatabaseManager
from src.database.models import BalanceHistory
from src.config.main_config import _get_env_float, _get_env_bool

logger = logging.getLogger(__name__)

class BalanceManager:
    """
    Gestor de balance que mantiene conexión con Capital.com y actualiza balance periódicamente
    """
    
    def __init__(self, update_interval: int = 30):
        """
        Inicializa el gestor de balance
        
        Args:
            update_interval: Intervalo en segundos para actualizar el balance (default: 30s)
        """
        self.update_interval = update_interval
        self.capital_client = None
        self.db_manager = DatabaseManager()
        self.is_running = False
        self.last_balance_update = None
        self.session_refresh_interval = 3600  # Renovar sesión cada hora
        self.last_session_refresh = None
        
        # Estado del balance actual
        self.current_balance = {
            'available': 0.0,
            'total': 0.0,
            'deposit': 0.0,
            'profit_loss': 0.0
        }
        
        logger.info(f"💰 Balance Manager initialized (update interval: {update_interval}s)")
    
    async def start(self):
        """Inicia el servicio de gestión de balance"""
        if self.is_running:
            logger.warning("⚠️ Balance Manager ya está ejecutándose")
            return
        
        logger.info("🚀 Iniciando Balance Manager...")
        
        # Conectar a Capital.com
        await self._connect_to_capital()
        
        # Obtener balance inicial
        await self._update_balance()
        
        # Iniciar tarea periódica
        self.is_running = True
        asyncio.create_task(self._periodic_update_task())
        
        logger.info("✅ Balance Manager iniciado correctamente")
    
    async def stop(self):
        """Detiene el servicio de gestión de balance"""
        logger.info("🛑 Deteniendo Balance Manager...")
        self.is_running = False
        
        if self.capital_client:
            try:
                # Cerrar sesión si es necesario
                pass  # Capital client maneja esto automáticamente
            except Exception as e:
                logger.error(f"❌ Error cerrando sesión de Capital.com: {e}")
        
        logger.info("✅ Balance Manager detenido")
    
    async def _connect_to_capital(self):
        """Establece conexión con Capital.com"""
        try:
            logger.info("🔗 Conectando a Capital.com...")
            self.capital_client = create_capital_client_from_env()
            
            # Verificar conexión obteniendo información de cuenta
            account_info = self.capital_client.get_accounts()
            if account_info:
                logger.info("✅ Conexión a Capital.com establecida correctamente")
                self.last_session_refresh = datetime.now()
            else:
                raise Exception("No se pudo obtener información de cuenta")
                
        except Exception as e:
            logger.error(f"❌ Error conectando a Capital.com: {e}")
            raise
    
    async def _refresh_session_if_needed(self):
        """Renueva la sesión si es necesario"""
        if not self.last_session_refresh:
            return
        
        time_since_refresh = datetime.now() - self.last_session_refresh
        if time_since_refresh.total_seconds() > self.session_refresh_interval:
            try:
                logger.info("🔄 Renovando sesión de Capital.com...")
                
                # Crear nueva sesión
                self.capital_client = create_capital_client_from_env()
                
                # Verificar que la nueva sesión funciona
                account_info = self.capital_client.get_accounts()
                if account_info:
                    self.last_session_refresh = datetime.now()
                    logger.info("✅ Sesión renovada correctamente")
                else:
                    raise Exception("La nueva sesión no funciona correctamente")
                    
            except Exception as e:
                logger.error(f"❌ Error renovando sesión: {e}")
                # Intentar reconectar completamente
                await self._connect_to_capital()
    
    async def _update_balance(self) -> bool:
        """
        Actualiza el balance desde Capital.com y lo guarda en la DB
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        try:
            # Renovar sesión si es necesario
            await self._refresh_session_if_needed()
            
            # Obtener balance de Capital.com
            balance_info = self.capital_client.get_available_balance()
            
            if not balance_info:
                logger.error("❌ No se pudo obtener balance de Capital.com")
                return False
            
            # Actualizar balance actual
            self.current_balance = {
                'available': balance_info.get('available', 0.0),
                'total': balance_info.get('balance', 0.0),
                'deposit': balance_info.get('deposit', 0.0),
                'profit_loss': balance_info.get('profitLoss', 0.0)
            }
            
            # Guardar en la base de datos
            await self._save_balance_to_db(balance_info)
            
            self.last_balance_update = datetime.now()
            
            logger.info(f"💰 Balance actualizado: ${self.current_balance['available']:,.2f} disponible")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando balance: {e}")
            return False
    
    async def _save_balance_to_db(self, balance_info: Dict[str, Any]):
        """Guarda el balance en la base de datos"""
        try:
            with self.db_manager.get_db_session() as session:
                balance_record = BalanceHistory(
                    available_balance=balance_info.get('available', 0.0),
                    total_balance=balance_info.get('balance', 0.0),
                    deposit=balance_info.get('deposit', 0.0),
                    profit_loss=balance_info.get('profitLoss', 0.0),
                    account_type="DEMO" if _get_env_bool("IS_DEMO", True) else "LIVE",
                    currency="USD",
                    session_active=True,
                    connection_status="CONNECTED",
                    retrieved_at=datetime.now()
                )
                
                session.add(balance_record)
                session.commit()
                
                logger.debug(f"💾 Balance guardado en DB: ${balance_info.get('available', 0.0):,.2f}")
                
        except Exception as e:
            logger.error(f"❌ Error guardando balance en DB: {e}")
    
    async def _periodic_update_task(self):
        """Tarea que actualiza el balance periódicamente"""
        logger.info(f"⏰ Iniciando actualizaciones periódicas cada {self.update_interval}s")
        
        while self.is_running:
            try:
                await asyncio.sleep(self.update_interval)
                
                if self.is_running:  # Verificar que aún estamos ejecutándose
                    success = await self._update_balance()
                    if not success:
                        logger.warning("⚠️ Falló la actualización de balance, reintentando en el próximo ciclo")
                        
            except asyncio.CancelledError:
                logger.info("🛑 Tarea de actualización periódica cancelada")
                break
            except Exception as e:
                logger.error(f"❌ Error en tarea periódica: {e}")
                # Continuar ejecutándose a pesar del error
                await asyncio.sleep(5)  # Esperar un poco antes del siguiente intento
    
    def get_current_balance(self) -> Dict[str, float]:
        """
        Obtiene el balance actual en memoria
        
        Returns:
            Dict con el balance actual
        """
        return self.current_balance.copy()
    
    def get_last_update_time(self) -> Optional[datetime]:
        """
        Obtiene el timestamp de la última actualización
        
        Returns:
            datetime de la última actualización o None si no ha habido actualizaciones
        """
        return self.last_balance_update
    
    def is_balance_fresh(self, max_age_seconds: int = 60) -> bool:
        """
        Verifica si el balance es reciente
        
        Args:
            max_age_seconds: Edad máxima en segundos para considerar el balance como fresco
            
        Returns:
            True si el balance es reciente
        """
        if not self.last_balance_update:
            return False
        
        age = datetime.now() - self.last_balance_update
        return age.total_seconds() <= max_age_seconds
    
    async def force_update(self) -> bool:
        """
        Fuerza una actualización inmediata del balance
        
        Returns:
            True si la actualización fue exitosa
        """
        logger.info("🔄 Forzando actualización de balance...")
        return await self._update_balance()


# Instancia global del gestor de balance
balance_manager = BalanceManager()


@asynccontextmanager
async def get_balance_manager():
    """Context manager para obtener el gestor de balance"""
    yield balance_manager


async def start_balance_manager():
    """Función helper para iniciar el gestor de balance"""
    await balance_manager.start()


async def stop_balance_manager():
    """Función helper para detener el gestor de balance"""
    await balance_manager.stop()


def get_current_balance_sync() -> Dict[str, float]:
    """Función síncrona para obtener el balance actual"""
    return balance_manager.get_current_balance()
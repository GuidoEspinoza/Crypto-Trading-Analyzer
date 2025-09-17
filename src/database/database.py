#!/usr/bin/env python3
"""
🗄️ Universal Trading Analyzer - Database Manager
Gestor de base de datos SQLite con SQLAlchemy optimizado y parametrizado
"""

import os
import logging
from functools import lru_cache
from typing import Generator, Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .models import Base, Trade, Portfolio, Strategy, BacktestResult, TradingSignal
from ..config.database_config import DatabaseConfig, get_database_config


class DatabaseManager:
    """
    🗄️ Gestor principal de la base de datos SQLite optimizado
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None, profile: str = "default"):
        """
        Inicializar el gestor de base de datos
        
        Args:
            config: Configuración personalizada de base de datos
            profile: Perfil de configuración (default, development, production, test)
        """
        # Usar configuración proporcionada o cargar por perfil
        self.config = config if config else get_database_config(profile)
        
        # Configurar logging
        self._setup_logging()
        
        # Configurar base de datos
        self.database_url = self.config.connection.get_database_url()
        self._setup_engine()
        self._setup_session_factory()
        
        # Cache para consultas frecuentes
        self._query_cache = {} if self.config.performance.enable_query_cache else None
        self._cache_timestamps = {} if self.config.performance.enable_query_cache else None
        
        # Crear tablas si no existen
        self.create_tables()
        
        # Inicializar portfolio base si está habilitado
        if self.config.portfolio.auto_initialize:
            self.initialize_base_portfolio()
        
        self.logger.info(f"✅ Database initialized: {self.database_url}")
    
    def _setup_logging(self):
        """
        📝 Configurar logging para el gestor de base de datos
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.config.logging.get_logging_level())
        
        # Configurar handler si no existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.config.logging.format)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Configurar logging de SQL si está habilitado
        if self.config.logging.enable_sql_logging:
            sql_logger = logging.getLogger('sqlalchemy.engine')
            sql_logger.setLevel(logging.INFO)
    
    def _setup_engine(self):
        """
        🔧 Configurar motor de base de datos
        """
        # Crear directorio si no existe (solo para SQLite)
        if self.database_url.startswith('sqlite:'):
            db_path = self.database_url.replace('sqlite:///', '')
            if db_path != ':memory:':
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Configurar argumentos de conexión
        connect_args = {}
        if self.database_url.startswith('sqlite:'):
            connect_args["check_same_thread"] = self.config.connection.check_same_thread
        
        # Crear engine con configuración optimizada
        self.engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            echo=self.config.connection.echo_sql,
            pool_size=self.config.connection.pool_size,
            max_overflow=self.config.connection.max_overflow,
            pool_timeout=self.config.connection.pool_timeout,
            pool_recycle=self.config.connection.pool_recycle,
            pool_pre_ping=self.config.performance.connection_pool_pre_ping
        )
    
    def _setup_session_factory(self):
        """
        🏭 Configurar factory de sesiones
        """
        self.SessionLocal = sessionmaker(
            autocommit=self.config.session.autocommit,
            autoflush=self.config.session.autoflush,
            expire_on_commit=self.config.session.expire_on_commit,
            bind=self.engine
        )
    
    def create_tables(self):
        """
        🏗️ Crear todas las tablas en la base de datos
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("✅ Database tables created/verified")
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error creating tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        🔗 Obtener una nueva sesión de base de datos
        
        Returns:
            Session: Nueva sesión de SQLAlchemy
        """
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        🔗 Context manager para sesiones de base de datos
        
        Yields:
            Session: Sesión de base de datos con auto-cleanup
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"❌ Database error: {e}")
            raise
        finally:
            session.close()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        ⏰ Verificar si el cache es válido
        
        Args:
            cache_key: Clave del cache
            
        Returns:
            bool: True si el cache es válido
        """
        if not self.config.performance.enable_query_cache:
            return False
            
        if cache_key not in self._cache_timestamps:
            return False
            
        cache_time = self._cache_timestamps[cache_key]
        ttl = timedelta(seconds=self.config.performance.cache_ttl_seconds)
        
        return datetime.now() - cache_time < ttl
    
    def _set_cache(self, cache_key: str, data: Any):
        """
        💾 Establecer datos en cache
        
        Args:
            cache_key: Clave del cache
            data: Datos a cachear
        """
        if self.config.performance.enable_query_cache:
            self._query_cache[cache_key] = data
            self._cache_timestamps[cache_key] = datetime.now()
    
    def _get_cache(self, cache_key: str) -> Optional[Any]:
        """
        📥 Obtener datos del cache
        
        Args:
            cache_key: Clave del cache
            
        Returns:
            Any: Datos cacheados o None
        """
        if self._is_cache_valid(cache_key):
            return self._query_cache.get(cache_key)
        return None
    
    def initialize_base_portfolio(self):
        """
        💼 Inicializar portfolio base con configuración parametrizada
        """
        try:
            with self.get_db_session() as session:
                # Verificar si ya existe portfolio base
                existing_portfolio = session.query(Portfolio).filter(
                    Portfolio.symbol == self.config.portfolio.base_currency,
                    Portfolio.is_paper == True
                ).first()
                
                if not existing_portfolio:
                    # Crear portfolio inicial con configuración parametrizada
                    initial_portfolio = Portfolio(
                        symbol=self.config.portfolio.base_currency,
                        quantity=self.config.portfolio.initial_usdt_amount,
                        avg_price=self.config.portfolio.base_price,
                        current_price=self.config.portfolio.base_price,
                        current_value=self.config.portfolio.initial_usdt_amount,
                        unrealized_pnl=0.0,
                        unrealized_pnl_percentage=0.0,
                        is_paper=True
                    )
                    
                    session.add(initial_portfolio)
                    session.commit()
                    self.logger.info(
                        f"💰 Initialized paper trading portfolio with "
                        f"${self.config.portfolio.initial_usdt_amount:,.2f} {self.config.portfolio.base_currency}"
                    )
                
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error initializing portfolio: {e}")
    
    def get_portfolio_summary(self, is_paper: bool = True) -> Dict[str, Any]:
        """
        📊 Obtener resumen del portfolio con cache
        
        Args:
            is_paper: Si es paper trading (True) o real (False)
            
        Returns:
            dict: Resumen del portfolio
        """
        cache_key = f"portfolio_summary_{is_paper}"
        
        # Intentar obtener del cache
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            self.logger.debug(f"📥 Portfolio summary from cache: {cache_key}")
            return cached_result
        
        try:
            with self.get_db_session() as session:
                portfolio_items = session.query(Portfolio).filter(
                    Portfolio.is_paper == is_paper
                ).all()
                
                total_value = sum(item.current_value or 0 for item in portfolio_items)
                total_pnl = sum(item.unrealized_pnl or 0 for item in portfolio_items)
                
                # Calcular PnL percentage basado en configuración
                initial_amount = self.config.portfolio.initial_usdt_amount
                pnl_percentage = round((total_pnl / initial_amount) * 100, 2) if initial_amount > 0 else 0
                
                result = {
                    "total_value": round(total_value, 2),
                    "total_pnl": round(total_pnl, 2),
                    "total_pnl_percentage": pnl_percentage,
                    "assets": [
                        {
                            "symbol": item.symbol,
                            "quantity": item.quantity,
                            "current_value": item.current_value,
                            "unrealized_pnl": item.unrealized_pnl
                        }
                        for item in portfolio_items
                        if item.quantity > self.config.portfolio.min_quantity_threshold
                    ]
                }
                
                # Guardar en cache
                self._set_cache(cache_key, result)
                
                return result
                
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error getting portfolio summary: {e}")
            return {"error": str(e)}
    
    def get_active_trades(self, is_paper: bool = True, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        📈 Obtener trades activos con configuración parametrizada
        
        Args:
            is_paper: Si es paper trading (True) o real (False)
            limit: Límite de resultados (usa configuración por defecto si es None)
            
        Returns:
            list: Lista de trades activos
        """
        cache_key = f"active_trades_{is_paper}_{limit}"
        
        # Intentar obtener del cache
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            self.logger.debug(f"📥 Active trades from cache: {cache_key}")
            return cached_result
        
        try:
            with self.get_db_session() as session:
                query = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper,
                    Trade.status == self.config.query.default_trade_status
                )
                
                # Aplicar ordenamiento configurado
                if hasattr(Trade, self.config.query.default_order_by):
                    order_column = getattr(Trade, self.config.query.default_order_by)
                    if self.config.query.order_direction.lower() == "desc":
                        query = query.order_by(order_column.desc())
                    else:
                        query = query.order_by(order_column.asc())
                
                # Aplicar límite
                result_limit = limit or self.config.query.max_results_limit
                active_trades = query.limit(result_limit).all()
                
                # Convertir a formato esperado
                trades_data = []
                for trade in active_trades:
                    trade_data = {
                        'id': trade.id,
                        'symbol': trade.symbol,
                        'side': trade.trade_type,
                        'quantity': trade.quantity,
                        'entry_price': trade.entry_price,
                        'current_price': trade.entry_price,
                        'stop_loss': trade.stop_loss,
                        'take_profit': trade.take_profit,
                        'pnl': trade.pnl if trade.pnl else 0.0,
                        'status': trade.status,
                        'entry_time': trade.entry_time
                    }
                    trades_data.append(trade_data)
                
                # Guardar en cache
                self._set_cache(cache_key, trades_data)
                
                return trades_data
                
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error getting active trades: {e}")
            return []
    
    def get_last_trade_for_symbol(self, symbol: str, is_paper: bool = True) -> Optional[float]:
        """
        💰 Obtener el precio del último trade para un símbolo con cache
        
        Args:
            symbol: Símbolo del activo (ej: BTCUSDT)
            is_paper: Si es paper trading (True) o real (False)
            
        Returns:
            float: Precio del último trade o None si no hay trades
        """
        cache_key = f"last_trade_{symbol}_{is_paper}"
        
        # Intentar obtener del cache
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            self.logger.debug(f"📥 Last trade price from cache: {cache_key}")
            return cached_result
        
        try:
            with self.get_db_session() as session:
                last_trade = session.query(Trade).filter(
                    Trade.symbol == symbol,
                    Trade.is_paper_trade == is_paper
                ).order_by(Trade.entry_time.desc()).first()
                
                if last_trade:
                    # Retornar exit_price si está cerrado, sino entry_price
                    price = last_trade.exit_price if last_trade.exit_price else last_trade.entry_price
                    
                    # Guardar en cache
                    self._set_cache(cache_key, price)
                    
                    return price
                else:
                    self.logger.warning(f"⚠️ No se encontraron trades para {symbol}")
                    return None
                    
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error getting last trade for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """
        🗑️ Limpiar cache de consultas
        """
        if self.config.performance.enable_query_cache:
            self._query_cache.clear()
            self._cache_timestamps.clear()
            self.logger.info("🗑️ Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas del cache
        
        Returns:
            dict: Estadísticas del cache
        """
        if not self.config.performance.enable_query_cache:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            "cached_queries": len(self._query_cache),
            "cache_keys": list(self._query_cache.keys()),
            "ttl_seconds": self.config.performance.cache_ttl_seconds
        }
    
    def close(self):
        """
        🔒 Cerrar conexiones de base de datos
        """
        if hasattr(self, 'engine'):
            self.engine.dispose()
            self.logger.info("🔒 Database connections closed")


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    🔗 Dependency para FastAPI - obtener sesión de base de datos
    
    Yields:
        Session: Sesión de base de datos
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def get_database_manager(profile: str = "default") -> DatabaseManager:
    """
    🗄️ Factory function para crear DatabaseManager con perfil específico
    
    Args:
        profile: Perfil de configuración
        
    Returns:
        DatabaseManager: Instancia configurada
    """
    return DatabaseManager(profile=profile)
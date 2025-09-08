#!/usr/bin/env python3
"""
🔄 Database Migrations - Crypto Trading Analyzer

Sistema de migraciones para gestionar cambios en la base de datos de producción.
Permite actualizar esquemas de manera segura y controlada.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from .database import DatabaseManager
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Clase base para migraciones de base de datos."""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self, db_manager: DatabaseManager) -> bool:
        """Aplicar la migración."""
        raise NotImplementedError("Subclasses must implement up()")
    
    def down(self, db_manager: DatabaseManager) -> bool:
        """Revertir la migración."""
        raise NotImplementedError("Subclasses must implement down()")

class MigrationManager:
    """Gestor de migraciones de base de datos."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migrations: List[DatabaseMigration] = []
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Crear tabla de migraciones si no existe."""
        try:
            with self.db_manager.get_db_session() as session:
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        rollback_sql TEXT
                    )
                """))
                session.commit()
                logger.info("✅ Migration table ensured")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating migration table: {e}")
            raise
    
    def register_migration(self, migration: DatabaseMigration):
        """Registrar una nueva migración."""
        self.migrations.append(migration)
        logger.info(f"📝 Registered migration: {migration.version} - {migration.description}")
    
    def get_applied_migrations(self) -> List[str]:
        """Obtener lista de migraciones ya aplicadas."""
        try:
            with self.db_manager.get_db_session() as session:
                result = session.execute(text(
                    "SELECT version FROM schema_migrations ORDER BY applied_at"
                ))
                return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting applied migrations: {e}")
            return []
    
    def get_pending_migrations(self) -> List[DatabaseMigration]:
        """Obtener migraciones pendientes de aplicar."""
        applied = set(self.get_applied_migrations())
        return [m for m in self.migrations if m.version not in applied]
    
    def apply_migration(self, migration: DatabaseMigration) -> bool:
        """Aplicar una migración específica."""
        try:
            logger.info(f"🔄 Applying migration: {migration.version}")
            
            # Aplicar la migración
            success = migration.up(self.db_manager)
            
            if success:
                # Registrar en la tabla de migraciones
                with self.db_manager.get_db_session() as session:
                    session.execute(text("""
                        INSERT INTO schema_migrations (version, description)
                        VALUES (:version, :description)
                    """), {
                        "version": migration.version,
                        "description": migration.description
                    })
                    session.commit()
                
                logger.info(f"✅ Migration {migration.version} applied successfully")
                return True
            else:
                logger.error(f"❌ Migration {migration.version} failed")
                return False
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error applying migration {migration.version}: {e}")
            return False
    
    def rollback_migration(self, migration: DatabaseMigration) -> bool:
        """Revertir una migración específica."""
        try:
            logger.info(f"⏪ Rolling back migration: {migration.version}")
            
            # Revertir la migración
            success = migration.down(self.db_manager)
            
            if success:
                # Remover de la tabla de migraciones
                with self.db_manager.get_db_session() as session:
                    session.execute(text("""
                        DELETE FROM schema_migrations WHERE version = :version
                    """), {"version": migration.version})
                    session.commit()
                
                logger.info(f"✅ Migration {migration.version} rolled back successfully")
                return True
            else:
                logger.error(f"❌ Rollback of migration {migration.version} failed")
                return False
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error rolling back migration {migration.version}: {e}")
            return False
    
    def migrate_up(self) -> bool:
        """Aplicar todas las migraciones pendientes."""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ No pending migrations")
            return True
        
        logger.info(f"🔄 Applying {len(pending)} pending migrations")
        
        for migration in pending:
            if not self.apply_migration(migration):
                logger.error(f"❌ Migration failed at: {migration.version}")
                return False
        
        logger.info("✅ All migrations applied successfully")
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Obtener estado actual de las migraciones."""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            "total_migrations": len(self.migrations),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied_versions": applied,
            "pending_versions": [m.version for m in pending],
            "last_applied": applied[-1] if applied else None
        }

# ============================================================================
# 🔄 MIGRACIONES ESPECÍFICAS
# ============================================================================

class InitialSchemaMigration(DatabaseMigration):
    """Migración inicial: crear todas las tablas base."""
    
    def __init__(self):
        super().__init__("001_initial_schema", "Create initial database schema")
    
    def up(self, db_manager: DatabaseManager) -> bool:
        """Crear esquema inicial."""
        try:
            # Crear todas las tablas definidas en models.py
            Base.metadata.create_all(db_manager.engine)
            logger.info("✅ Initial schema created")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating initial schema: {e}")
            return False
    
    def down(self, db_manager: DatabaseManager) -> bool:
        """Eliminar esquema inicial."""
        try:
            Base.metadata.drop_all(db_manager.engine)
            logger.info("✅ Initial schema dropped")
            return True
        except Exception as e:
            logger.error(f"❌ Error dropping initial schema: {e}")
            return False

class AddIndexesMigration(DatabaseMigration):
    """Migración: agregar índices para optimizar consultas."""
    
    def __init__(self):
        super().__init__("002_add_indexes", "Add performance indexes")
    
    def up(self, db_manager: DatabaseManager) -> bool:
        """Agregar índices."""
        try:
            with db_manager.get_db_session() as session:
                # Índices para trades
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_trades_symbol_status 
                    ON trades(symbol, status)
                """))
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_trades_entry_time 
                    ON trades(entry_time)
                """))
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_trades_strategy_symbol 
                    ON trades(strategy_name, symbol)
                """))
                
                # Índices para portfolio
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_portfolio_symbol_paper 
                    ON portfolio(symbol, is_paper)
                """))
                
                # Índices para signals
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_signals_symbol_time 
                    ON trading_signals(symbol, generated_at)
                """))
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_signals_strategy_type 
                    ON trading_signals(strategy_name, signal_type)
                """))
                
                session.commit()
                logger.info("✅ Performance indexes added")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding indexes: {e}")
            return False
    
    def down(self, db_manager: DatabaseManager) -> bool:
        """Remover índices."""
        try:
            with db_manager.get_db_session() as session:
                indexes = [
                    "idx_trades_symbol_status",
                    "idx_trades_entry_time",
                    "idx_trades_strategy_symbol",
                    "idx_portfolio_symbol_paper",
                    "idx_signals_symbol_time",
                    "idx_signals_strategy_type"
                ]
                
                for index in indexes:
                    session.execute(text(f"DROP INDEX IF EXISTS {index}"))
                
                session.commit()
                logger.info("✅ Performance indexes removed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error removing indexes: {e}")
            return False

# ============================================================================
# 🚀 FUNCIÓN DE INICIALIZACIÓN
# ============================================================================

def setup_database_migrations(db_manager: DatabaseManager) -> MigrationManager:
    """Configurar y registrar todas las migraciones."""
    migration_manager = MigrationManager(db_manager)
    
    # Registrar migraciones en orden
    migration_manager.register_migration(InitialSchemaMigration())
    migration_manager.register_migration(AddIndexesMigration())
    
    return migration_manager

def run_migrations(db_manager: DatabaseManager = None) -> bool:
    """Ejecutar todas las migraciones pendientes."""
    if db_manager is None:
        db_manager = DatabaseManager()
    
    migration_manager = setup_database_migrations(db_manager)
    return migration_manager.migrate_up()

def get_migration_status(db_manager: DatabaseManager = None) -> Dict[str, Any]:
    """Obtener estado de las migraciones."""
    if db_manager is None:
        db_manager = DatabaseManager()
    
    migration_manager = setup_database_migrations(db_manager)
    return migration_manager.get_migration_status()
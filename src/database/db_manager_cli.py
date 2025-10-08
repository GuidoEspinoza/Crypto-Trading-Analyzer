#!/usr/bin/env python3
"""
🛠️ Database Management CLI - Crypto Trading Analyzer

Herramienta de línea de comandos para gestionar la base de datos en producción.
Permite ejecutar migraciones, backups, limpieza y análisis de datos.
"""

import os
import sys
import argparse
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Agregar src al path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from database.database import DatabaseManager
from database.migrations import run_migrations, get_migration_status
from database.models import Trade, Portfolio, Strategy, BacktestResult, TradingSignal
from sqlalchemy import text, func
from config.main_config import DatabaseConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseCLI:
    """Interfaz de línea de comandos para gestión de base de datos."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_manager = DatabaseManager(f"sqlite:///{db_path}")
        else:
            self.db_manager = DatabaseManager()
        
        # Obtener ruta de la base de datos para backups
        self.db_file_path = self.db_manager.database_url.replace("sqlite:///", "")
    
    def migrate(self) -> bool:
        """Ejecutar migraciones pendientes."""
        print("🔄 Ejecutando migraciones...")
        try:
            success = run_migrations(self.db_manager)
            if success:
                print("✅ Migraciones completadas exitosamente")
            else:
                print("❌ Error ejecutando migraciones")
            return success
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def migration_status(self):
        """Mostrar estado de las migraciones."""
        print("📊 Estado de Migraciones")
        print("=" * 40)
        
        try:
            status = get_migration_status(self.db_manager)
            
            print(f"Total de migraciones: {status['total_migrations']}")
            print(f"Aplicadas: {status['applied_count']}")
            print(f"Pendientes: {status['pending_count']}")
            
            if status['last_applied']:
                print(f"Última aplicada: {status['last_applied']}")
            
            if status['pending_versions']:
                print("\n📋 Migraciones pendientes:")
                for version in status['pending_versions']:
                    print(f"  - {version}")
            else:
                print("\n✅ Todas las migraciones están aplicadas")
                
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
    
    def backup(self, backup_dir: str = "backups") -> bool:
        """Crear backup de la base de datos."""
        try:
            # Crear directorio de backups
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            # Nombre del archivo de backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"trading_bot_backup_{timestamp}.db"
            
            # Copiar archivo de base de datos
            shutil.copy2(self.db_file_path, backup_file)
            
            print(f"✅ Backup creado: {backup_file}")
            print(f"📁 Tamaño: {backup_file.stat().st_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    
    def restore(self, backup_file: str) -> bool:
        """Restaurar base de datos desde backup."""
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                print(f"❌ Archivo de backup no encontrado: {backup_file}")
                return False
            
            # Crear backup del archivo actual antes de restaurar
            current_backup = f"{self.db_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_file_path, current_backup)
            print(f"📁 Backup actual guardado en: {current_backup}")
            
            # Restaurar desde backup
            shutil.copy2(backup_path, self.db_file_path)
            
            print(f"✅ Base de datos restaurada desde: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error restaurando backup: {e}")
            return False
    
    def stats(self):
        """Mostrar estadísticas de la base de datos."""
        print("📊 Estadísticas de Base de Datos")
        print("=" * 40)
        
        try:
            with self.db_manager.get_db_session() as session:
                # Estadísticas de trades
                total_trades = session.query(func.count(Trade.id)).scalar()
                open_trades = session.query(func.count(Trade.id)).filter(Trade.status == "OPEN").scalar()
                closed_trades = session.query(func.count(Trade.id)).filter(Trade.status == "CLOSED").scalar()
                
                print(f"\n💰 Trades:")
                print(f"  Total: {total_trades}")
                print(f"  Abiertos: {open_trades}")
                print(f"  Cerrados: {closed_trades}")
                
                # Estadísticas de portfolio
                portfolio_items = session.query(func.count(Portfolio.id)).scalar()
                paper_positions = session.query(func.count(Portfolio.id)).filter(Portfolio.is_paper == True).scalar()
                real_positions = session.query(func.count(Portfolio.id)).filter(Portfolio.is_paper == False).scalar()
                
                print(f"\n📈 Portfolio:")
                print(f"  Total posiciones: {portfolio_items}")
                print(f"  Paper trading: {paper_positions}")
                print(f"  Trading real: {real_positions}")
                
                # Estadísticas de estrategias
                total_strategies = session.query(func.count(Strategy.id)).scalar()
                active_strategies = session.query(func.count(Strategy.id)).filter(Strategy.is_active == True).scalar()
                
                print(f"\n🧠 Estrategias:")
                print(f"  Total: {total_strategies}")
                print(f"  Activas: {active_strategies}")
                
                # Estadísticas de señales
                total_signals = session.query(func.count(TradingSignal.id)).scalar()
                recent_signals = session.query(func.count(TradingSignal.id)).filter(
                    TradingSignal.generated_at >= datetime.now() - timedelta(days=7)
                ).scalar()
                
                print(f"\n📡 Señales:")
                print(f"  Total: {total_signals}")
                print(f"  Última semana: {recent_signals}")
                
                # Estadísticas de backtests
                total_backtests = session.query(func.count(BacktestResult.id)).scalar()
                
                print(f"\n🔬 Backtests:")
                print(f"  Total: {total_backtests}")
                
                # Tamaño de archivo
                db_size = Path(self.db_file_path).stat().st_size
                print(f"\n💾 Archivo:")
                print(f"  Tamaño: {db_size / 1024:.1f} KB")
                print(f"  Ubicación: {self.db_file_path}")
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    def cleanup(self, days: int = DatabaseConfig.DATA_RETENTION_DAYS) -> bool:
        """Limpiar datos antiguos."""
        print(f"🧹 Limpiando datos anteriores a {days} días...")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.db_manager.get_db_session() as session:
                # Limpiar señales antiguas
                old_signals = session.query(TradingSignal).filter(
                    TradingSignal.generated_at < cutoff_date
                ).count()
                
                session.query(TradingSignal).filter(
                    TradingSignal.generated_at < cutoff_date
                ).delete()
                
                # Limpiar trades cerrados muy antiguos (mantener solo los últimos 90 días)
                if days > 90:
                    old_trades_cutoff = datetime.now() - timedelta(days=90)
                    old_trades = session.query(Trade).filter(
                        Trade.status == "CLOSED",
                        Trade.exit_time < old_trades_cutoff
                    ).count()
                    
                    session.query(Trade).filter(
                        Trade.status == "CLOSED",
                        Trade.exit_time < old_trades_cutoff
                    ).delete()
                else:
                    old_trades = 0
                
                session.commit()
                
                print(f"✅ Limpieza completada:")
                print(f"  Señales eliminadas: {old_signals}")
                print(f"  Trades antiguos eliminados: {old_trades}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error durante limpieza: {e}")
            return False
    
    def vacuum(self) -> bool:
        """Optimizar base de datos (VACUUM)."""
        print("🔧 Optimizando base de datos...")
        
        try:
            with self.db_manager.get_db_session() as session:
                # Obtener tamaño antes
                size_before = Path(self.db_file_path).stat().st_size
                
                # Ejecutar VACUUM
                session.execute(text("VACUUM"))
                session.commit()
                
                # Obtener tamaño después
                size_after = Path(self.db_file_path).stat().st_size
                saved = size_before - size_after
                
                print(f"✅ Optimización completada:")
                print(f"  Tamaño antes: {size_before / 1024:.1f} KB")
                print(f"  Tamaño después: {size_after / 1024:.1f} KB")
                print(f"  Espacio liberado: {saved / 1024:.1f} KB")
                
                return True
                
        except Exception as e:
            print(f"❌ Error durante optimización: {e}")
            return False
    
    def reset(self) -> bool:
        """Resetear base de datos (PELIGROSO)."""
        print("⚠️  ADVERTENCIA: Esta operación eliminará TODOS los datos")
        confirm = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ")
        
        if confirm != "CONFIRMAR":
            print("❌ Operación cancelada")
            return False
        
        try:
            # Crear backup antes del reset
            backup_success = self.backup("backups/pre_reset")
            if not backup_success:
                print("❌ No se pudo crear backup. Operación cancelada.")
                return False
            
            # Eliminar todas las tablas
            with self.db_manager.get_db_session() as session:
                session.execute(text("DROP TABLE IF EXISTS trades"))
                session.execute(text("DROP TABLE IF EXISTS portfolio"))
                session.execute(text("DROP TABLE IF EXISTS strategies"))
                session.execute(text("DROP TABLE IF EXISTS backtest_results"))
                session.execute(text("DROP TABLE IF EXISTS trading_signals"))
                session.execute(text("DROP TABLE IF EXISTS schema_migrations"))
                session.commit()
            
            # Ejecutar migraciones para recrear esquema
            migration_success = self.migrate()
            
            if migration_success:
                print("✅ Base de datos reseteada y recreada")
                return True
            else:
                print("❌ Error recreando esquema")
                return False
                
        except Exception as e:
            print(f"❌ Error durante reset: {e}")
            return False

def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="🛠️ Database Management CLI - Crypto Trading Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--db-path", 
        help="Ruta personalizada a la base de datos"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando migrate
    subparsers.add_parser("migrate", help="Ejecutar migraciones pendientes")
    
    # Comando migration-status
    subparsers.add_parser("migration-status", help="Mostrar estado de migraciones")
    
    # Comando backup
    backup_parser = subparsers.add_parser("backup", help="Crear backup de la base de datos")
    backup_parser.add_argument("--dir", default="backups", help="Directorio de backups")
    
    # Comando restore
    restore_parser = subparsers.add_parser("restore", help="Restaurar desde backup")
    restore_parser.add_argument("backup_file", help="Archivo de backup a restaurar")
    
    # Comando stats
    subparsers.add_parser("stats", help="Mostrar estadísticas de la base de datos")
    
    # Comando cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Limpiar datos antiguos")
    cleanup_parser.add_argument("--days", type=int, default=DatabaseConfig.DATA_RETENTION_DAYS, help="Días de antigüedad para limpiar")
    
    # Comando vacuum
    subparsers.add_parser("vacuum", help="Optimizar base de datos")
    
    # Comando reset
    subparsers.add_parser("reset", help="Resetear base de datos (PELIGROSO)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Crear instancia del CLI
    cli = DatabaseCLI(args.db_path)
    
    # Ejecutar comando
    try:
        if args.command == "migrate":
            cli.migrate()
        elif args.command == "migration-status":
            cli.migration_status()
        elif args.command == "backup":
            cli.backup(args.dir)
        elif args.command == "restore":
            cli.restore(args.backup_file)
        elif args.command == "stats":
            cli.stats()
        elif args.command == "cleanup":
            cli.cleanup(args.days)
        elif args.command == "vacuum":
            cli.vacuum()
        elif args.command == "reset":
            cli.reset()
        else:
            print(f"❌ Comando desconocido: {args.command}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        logger.exception("Unexpected error")

if __name__ == "__main__":
    main()
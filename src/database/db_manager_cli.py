#!/usr/bin/env python3
"""
🛠️ Database Management CLI - Crypto Trading Analyzer

Herramienta de línea de comandos optimizada para gestionar la base de datos.
Utiliza configuración parametrizada y perfiles predefinidos para máxima flexibilidad.
"""

import os
import sys
import argparse
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import time

# Agregar src al path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from database.database import DatabaseManager
from database.migrations import run_migrations, get_migration_status
from database.models import Trade, Portfolio, Strategy, BacktestResult, TradingSignal
from config.cli_config import DatabaseCLIConfig, get_cli_config, get_cli_config_from_env
from sqlalchemy import text, func

# Configurar logging dinámicamente
def setup_logging(config: DatabaseCLIConfig):
    """Configurar logging basado en configuración."""
    logging.basicConfig(
        level=getattr(logging, config.operations.log_level),
        format=config.operations.log_format
    )
    return logging.getLogger(__name__)

class DatabaseCLI:
    """Interfaz de línea de comandos optimizada para gestión de base de datos."""
    
    def __init__(self, db_path: Optional[str] = None, config: Optional[DatabaseCLIConfig] = None, profile: str = 'development'):
        # Configuración
        self.config = config or get_cli_config(profile)
        self.logger = setup_logging(self.config)
        
        # Database Manager
        db_path = db_path or self.config.default_db_path
        if db_path:
            self.db_manager = DatabaseManager(f"sqlite:///{db_path}")
        else:
            self.db_manager = DatabaseManager()
        
        # Obtener ruta de la base de datos para backups
        self.db_file_path = self.db_manager.database_url.replace("sqlite:///", "")
        
        # Estadísticas de rendimiento
        self.operation_stats = {
            'start_time': None,
            'operations_count': 0
        }
    
    def _start_operation(self, operation_name: str):
        """Iniciar seguimiento de operación."""
        self.operation_stats['start_time'] = time.time()
        self.operation_stats['operations_count'] += 1
        if self.config.performance.enable_progress_indicators:
            self.logger.info(f"Iniciando operación: {operation_name}")
    
    def _end_operation(self, operation_name: str, success: bool = True):
        """Finalizar seguimiento de operación."""
        if self.operation_stats['start_time']:
            duration = time.time() - self.operation_stats['start_time']
            status = "exitosa" if success else "fallida"
            if self.config.performance.enable_progress_indicators:
                self.logger.info(f"Operación {operation_name} {status} en {duration:.2f}s")
    
    def _print_with_emoji(self, message: str, emoji_key: str = None, level: str = "info"):
        """Imprimir mensaje con emoji opcional."""
        if emoji_key and self.config.display.use_emojis:
            emoji = getattr(self.config.display, f"emoji_{emoji_key}", "")
            message = f"{emoji} {message}"
        print(message)
        
        # Log también
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatear tamaño de archivo."""
        if self.config.display.show_file_sizes_in_kb:
            return f"{size_bytes / 1024:.{self.config.display.decimal_places}f} KB"
        return f"{size_bytes} bytes"
    
    def _get_timestamp(self) -> str:
        """Obtener timestamp formateado."""
        return datetime.now().strftime(self.config.display.date_format)
    
    def _auto_backup_if_enabled(self, operation_name: str) -> bool:
        """Crear backup automático si está habilitado."""
        if self.config.operations.enable_pre_operation_backup:
            self._print_with_emoji(f"Creando backup antes de {operation_name}...", "backup")
            return self.backup(f"auto_backup_{operation_name}")
        return True
    
    def migrate(self) -> bool:
        """Ejecutar migraciones pendientes."""
        self._start_operation("migrate")
        self._print_with_emoji("Ejecutando migraciones...", "migrate")
        
        try:
            success = run_migrations(self.db_manager)
            if success:
                self._print_with_emoji("Migraciones completadas exitosamente", "success")
            else:
                self._print_with_emoji("Error ejecutando migraciones", "error", "error")
            
            self._end_operation("migrate", success)
            return success
            
        except Exception as e:
            self._print_with_emoji(f"Error: {e}", "error", "error")
            self._end_operation("migrate", False)
            return False
    
    def migration_status(self):
        """Mostrar estado de las migraciones."""
        self._start_operation("migration_status")
        self._print_with_emoji("Estado de Migraciones", "stats")
        print(self.config.display.stats_separator)
        
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
                self._print_with_emoji("Todas las migraciones están aplicadas", "success")
            
            self._end_operation("migration_status", True)
                
        except Exception as e:
            self._print_with_emoji(f"Error obteniendo estado: {e}", "error", "error")
            self._end_operation("migration_status", False)
    
    def backup(self, backup_dir: Optional[str] = None) -> bool:
        """Crear backup de la base de datos."""
        self._start_operation("backup")
        
        try:
            # Usar directorio de configuración si no se especifica
            backup_dir = backup_dir or self.config.backup.default_backup_dir
            backup_path = self.config.backup.get_backup_path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            # Nombre del archivo de backup con timestamp
            timestamp = self._get_timestamp()
            backup_filename = self.config.backup.backup_filename_format.format(timestamp=timestamp)
            backup_file = backup_path / backup_filename
            
            # Copiar archivo de base de datos
            shutil.copy2(self.db_file_path, backup_file)
            
            # Gestión de backups antiguos
            self._cleanup_old_backups(backup_path)
            
            file_size = backup_file.stat().st_size
            self._print_with_emoji(f"Backup creado: {backup_file}", "success")
            self._print_with_emoji(f"Tamaño: {self._format_size(file_size)}", "backup")
            
            self._end_operation("backup", True)
            return True
            
        except Exception as e:
            self._print_with_emoji(f"Error creando backup: {e}", "error", "error")
            self._end_operation("backup", False)
            return False
    
    def _cleanup_old_backups(self, backup_path: Path):
        """Limpiar backups antiguos según configuración."""
        try:
            backup_files = list(backup_path.glob("*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if len(backup_files) > self.config.backup.max_backup_files:
                files_to_remove = backup_files[self.config.backup.max_backup_files:]
                for file_to_remove in files_to_remove:
                    file_to_remove.unlink()
                    self.logger.info(f"Backup antiguo eliminado: {file_to_remove}")
                    
        except Exception as e:
            self.logger.warning(f"Error limpiando backups antiguos: {e}")
    
    def restore(self, backup_file: str) -> bool:
        """Restaurar base de datos desde backup."""
        self._start_operation("restore")
        
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                self._print_with_emoji(f"Archivo de backup no encontrado: {backup_file}", "error", "error")
                self._end_operation("restore", False)
                return False
            
            # Crear backup del archivo actual antes de restaurar
            timestamp = self._get_timestamp()
            current_backup_name = self.config.backup.current_backup_format.format(
                db_path=self.db_file_path,
                timestamp=timestamp
            )
            shutil.copy2(self.db_file_path, current_backup_name)
            self._print_with_emoji(f"Backup actual guardado en: {current_backup_name}", "backup")
            
            # Restaurar desde backup
            shutil.copy2(backup_path, self.db_file_path)
            
            self._print_with_emoji(f"Base de datos restaurada desde: {backup_file}", "success")
            self._end_operation("restore", True)
            return True
            
        except Exception as e:
            self._print_with_emoji(f"Error restaurando backup: {e}", "error", "error")
            self._end_operation("restore", False)
            return False
    
    def stats(self):
        """Mostrar estadísticas de la base de datos."""
        self._start_operation("stats")
        self._print_with_emoji("Estadísticas de Base de Datos", "stats")
        print(self.config.display.stats_separator)
        
        try:
            with self.db_manager.get_db_session() as session:
                # Estadísticas de trades
                total_trades = session.query(func.count(Trade.id)).scalar()
                open_trades = session.query(func.count(Trade.id)).filter(Trade.status == "OPEN").scalar()
                closed_trades = session.query(func.count(Trade.id)).filter(Trade.status == "CLOSED").scalar()
                
                emoji_trades = self.config.display.emoji_trades if self.config.display.use_emojis else ""
                print(f"\n{emoji_trades} Trades:")
                print(f"  Total: {total_trades}")
                print(f"  Abiertos: {open_trades}")
                print(f"  Cerrados: {closed_trades}")
                
                # Estadísticas de portfolio
                portfolio_items = session.query(func.count(Portfolio.id)).scalar()
                paper_positions = session.query(func.count(Portfolio.id)).filter(Portfolio.is_paper == True).scalar()
                real_positions = session.query(func.count(Portfolio.id)).filter(Portfolio.is_paper == False).scalar()
                
                emoji_portfolio = self.config.display.emoji_portfolio if self.config.display.use_emojis else ""
                print(f"\n{emoji_portfolio} Portfolio:")
                print(f"  Total posiciones: {portfolio_items}")
                print(f"  Paper trading: {paper_positions}")
                print(f"  Trading real: {real_positions}")
                
                # Estadísticas de estrategias
                total_strategies = session.query(func.count(Strategy.id)).scalar()
                active_strategies = session.query(func.count(Strategy.id)).filter(Strategy.is_active == True).scalar()
                
                emoji_strategies = self.config.display.emoji_strategies if self.config.display.use_emojis else ""
                print(f"\n{emoji_strategies} Estrategias:")
                print(f"  Total: {total_strategies}")
                print(f"  Activas: {active_strategies}")
                
                # Estadísticas de señales (usando configuración para días recientes)
                total_signals = session.query(func.count(TradingSignal.id)).scalar()
                recent_days = self.config.operations.stats_recent_signals_days
                recent_signals = session.query(func.count(TradingSignal.id)).filter(
                    TradingSignal.generated_at >= datetime.now() - timedelta(days=recent_days)
                ).scalar()
                
                emoji_signals = self.config.display.emoji_signals if self.config.display.use_emojis else ""
                print(f"\n{emoji_signals} Señales:")
                print(f"  Total: {total_signals}")
                print(f"  Últimos {recent_days} días: {recent_signals}")
                
                # Estadísticas de backtests
                total_backtests = session.query(func.count(BacktestResult.id)).scalar()
                
                emoji_backtests = self.config.display.emoji_backtests if self.config.display.use_emojis else ""
                print(f"\n{emoji_backtests} Backtests:")
                print(f"  Total: {total_backtests}")
                
                # Tamaño de archivo
                db_size = Path(self.db_file_path).stat().st_size
                emoji_database = self.config.display.emoji_database if self.config.display.use_emojis else ""
                print(f"\n{emoji_database} Archivo:")
                print(f"  Tamaño: {self._format_size(db_size)}")
                print(f"  Ubicación: {self.db_file_path}")
            
            self._end_operation("stats", True)
                
        except Exception as e:
            self._print_with_emoji(f"Error obteniendo estadísticas: {e}", "error", "error")
            self._end_operation("stats", False)
    
    def cleanup(self, days: Optional[int] = None) -> bool:
        """Limpiar datos antiguos según configuración."""
        self._start_operation("cleanup")
        
        # Usar configuración si no se especifica días
        days = days or self.config.cleanup.default_cleanup_days
        
        # Validar días
        if days < self.config.cleanup.min_cleanup_days or days > self.config.cleanup.max_cleanup_days:
            self._print_with_emoji(
                f"Días inválidos: {days}. Debe estar entre {self.config.cleanup.min_cleanup_days} y {self.config.cleanup.max_cleanup_days}",
                "error", "error"
            )
            self._end_operation("cleanup", False)
            return False
        
        # Backup automático si está habilitado
        if not self._auto_backup_if_enabled("cleanup"):
            self._print_with_emoji("Error creando backup automático. Operación cancelada.", "error", "error")
            self._end_operation("cleanup", False)
            return False
        
        self._print_with_emoji(f"Limpiando datos anteriores a {days} días...", "cleanup")
        
        try:
            # Fechas de corte basadas en configuración
            signals_cutoff = datetime.now() - timedelta(days=min(days, self.config.cleanup.signals_retention_days))
            trades_cutoff = datetime.now() - timedelta(days=self.config.cleanup.old_trades_retention_days)
            
            with self.db_manager.get_db_session() as session:
                # Limpiar señales antiguas
                if self.config.performance.optimize_queries:
                    # Optimización: contar primero, luego eliminar en lotes
                    old_signals = session.query(TradingSignal).filter(
                        TradingSignal.generated_at < signals_cutoff
                    ).count()
                    
                    self._cleanup_in_batches(
                        session, TradingSignal, 
                        TradingSignal.generated_at < signals_cutoff,
                        "señales"
                    )
                else:
                    old_signals = session.query(TradingSignal).filter(
                        TradingSignal.generated_at < signals_cutoff
                    ).count()
                    
                    session.query(TradingSignal).filter(
                        TradingSignal.generated_at < signals_cutoff
                    ).delete()
                
                # Limpiar trades cerrados antiguos
                old_trades = session.query(Trade).filter(
                    Trade.status == "CLOSED",
                    Trade.exit_time < trades_cutoff
                ).count()
                
                if old_trades > 0:
                    if self.config.performance.optimize_queries:
                        self._cleanup_in_batches(
                            session, Trade,
                            (Trade.status == "CLOSED") & (Trade.exit_time < trades_cutoff),
                            "trades"
                        )
                    else:
                        session.query(Trade).filter(
                            Trade.status == "CLOSED",
                            Trade.exit_time < trades_cutoff
                        ).delete()
                
                session.commit()
                
                self._print_with_emoji("Limpieza completada:", "success")
                print(f"  Señales eliminadas: {old_signals}")
                print(f"  Trades antiguos eliminados: {old_trades}")
                
                self._end_operation("cleanup", True)
                return True
                
        except Exception as e:
            self._print_with_emoji(f"Error durante limpieza: {e}", "error", "error")
            self._end_operation("cleanup", False)
            return False
    
    def _cleanup_in_batches(self, session, model, filter_condition, item_type: str):
        """Limpiar datos en lotes para mejor rendimiento."""
        batch_size = self.config.performance.batch_size_cleanup
        total_deleted = 0
        
        while True:
            # Obtener IDs en lotes
            batch_ids = session.query(model.id).filter(filter_condition).limit(batch_size).all()
            
            if not batch_ids:
                break
            
            # Eliminar lote
            ids_to_delete = [row.id for row in batch_ids]
            session.query(model).filter(model.id.in_(ids_to_delete)).delete(synchronize_session=False)
            session.commit()
            
            total_deleted += len(ids_to_delete)
            
            if self.config.performance.enable_progress_indicators:
                self.logger.info(f"Eliminados {total_deleted} {item_type} hasta ahora...")
        
        return total_deleted
    
    def vacuum(self) -> bool:
        """Optimizar base de datos (VACUUM)."""
        self._start_operation("vacuum")
        
        # Backup automático si está habilitado
        if not self._auto_backup_if_enabled("vacuum"):
            self._print_with_emoji("Error creando backup automático. Operación cancelada.", "error", "error")
            self._end_operation("vacuum", False)
            return False
        
        self._print_with_emoji("Optimizando base de datos...", "optimize")
        
        try:
            with self.db_manager.get_db_session() as session:
                # Obtener tamaño antes
                size_before = Path(self.db_file_path).stat().st_size
                
                # Ejecutar VACUUM
                session.execute(text("VACUUM"))
                
                # ANALYZE si está habilitado en configuración
                if self.config.performance.vacuum_analyze_after:
                    session.execute(text("ANALYZE"))
                
                session.commit()
                
                # Obtener tamaño después
                size_after = Path(self.db_file_path).stat().st_size
                saved = size_before - size_after
                
                self._print_with_emoji("Optimización completada:", "success")
                
                if self.config.operations.vacuum_show_size_comparison:
                    print(f"  Tamaño antes: {self._format_size(size_before)}")
                    print(f"  Tamaño después: {self._format_size(size_after)}")
                    print(f"  Espacio liberado: {self._format_size(saved)}")
                    
                    if size_before > 0:
                        percentage_saved = (saved / size_before) * 100
                        print(f"  Reducción: {percentage_saved:.{self.config.display.decimal_places}f}%")
                
                self._end_operation("vacuum", True)
                return True
                
        except Exception as e:
            self._print_with_emoji(f"Error durante optimización: {e}", "error", "error")
            self._end_operation("vacuum", False)
            return False
    
    def reset(self) -> bool:
        """Resetear base de datos (PELIGROSO)."""
        self._start_operation("reset")
        
        self._print_with_emoji("ADVERTENCIA: Esta operación eliminará TODOS los datos", "warning", "warning")
        confirm_text = self.config.operations.reset_confirmation_text
        confirm = input(f"¿Estás seguro? Escribe '{confirm_text}' para continuar: ")
        
        if confirm != confirm_text:
            self._print_with_emoji("Operación cancelada", "error")
            self._end_operation("reset", False)
            return False
        
        try:
            # Crear backup antes del reset
            backup_success = self.backup(self.config.backup.pre_reset_backup_dir)
            if not backup_success:
                self._print_with_emoji("No se pudo crear backup. Operación cancelada.", "error", "error")
                self._end_operation("reset", False)
                return False
            
            self._print_with_emoji("Eliminando todas las tablas...", "reset")
            
            # Eliminar todas las tablas
            with self.db_manager.get_db_session() as session:
                # Lista de tablas a eliminar
                tables_to_drop = [
                    "trades", "portfolio", "strategies", 
                    "backtest_results", "trading_signals", "schema_migrations"
                ]
                
                for table in tables_to_drop:
                    session.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    if self.config.performance.enable_progress_indicators:
                        self.logger.info(f"Tabla {table} eliminada")
                
                session.commit()
            
            self._print_with_emoji("Recreando esquema de base de datos...", "migrate")
            
            # Ejecutar migraciones para recrear esquema
            migration_success = self.migrate()
            
            if migration_success:
                self._print_with_emoji("Base de datos reseteada y recreada", "success")
                self._end_operation("reset", True)
                return True
            else:
                self._print_with_emoji("Error recreando esquema", "error", "error")
                self._end_operation("reset", False)
                return False
                
        except Exception as e:
            self._print_with_emoji(f"Error durante reset: {e}", "error", "error")
            self._end_operation("reset", False)
            return False

def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="🛠️ Database Management CLI - Crypto Trading Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python db_manager_cli.py migrate
  python db_manager_cli.py backup
  python db_manager_cli.py restore backup_20231201_120000.db
  python db_manager_cli.py stats
  python db_manager_cli.py cleanup --days 30
  python db_manager_cli.py vacuum
  python db_manager_cli.py reset
  python db_manager_cli.py --profile production migrate
        """
    )
    
    # Argumentos globales
    parser.add_argument('--profile', '-p', 
                       choices=['development', 'production', 'testing'],
                       default='development',
                       help='Perfil de configuración a usar (default: development)')
    parser.add_argument('--config-file', '-c',
                       help='Archivo de configuración personalizado')
    parser.add_argument('--db-path',
                       help='Ruta personalizada a la base de datos')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Habilitar logging detallado')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Modo silencioso (solo errores)')
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando migrate
    subparsers.add_parser("migrate", help="Ejecutar migraciones pendientes")
    
    # Comando migration-status
    subparsers.add_parser("migration-status", help="Mostrar estado de migraciones")
    
    # Comando backup
    backup_parser = subparsers.add_parser("backup", help="Crear backup de la base de datos")
    backup_parser.add_argument("--dir", help="Directorio de backups")
    
    # Comando restore
    restore_parser = subparsers.add_parser("restore", help="Restaurar desde backup")
    restore_parser.add_argument("backup_file", help="Archivo de backup a restaurar")
    
    # Comando stats
    subparsers.add_parser("stats", help="Mostrar estadísticas de la base de datos")
    
    # Comando cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Limpiar datos antiguos")
    cleanup_parser.add_argument("--days", type=int,
                               help="Días de antigüedad para limpiar (usa configuración si no se especifica)")
    
    # Comando vacuum
    subparsers.add_parser("vacuum", help="Optimizar base de datos")
    
    # Comando reset
    subparsers.add_parser("reset", help="Resetear base de datos (PELIGROSO)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Cargar configuración
        if args.config_file:
            config = get_cli_config_from_env(args.config_file)
        else:
            config = get_cli_config(args.profile)
        
        # Ajustar nivel de logging según argumentos
        if args.quiet:
            config.operations.log_level = 'ERROR'
        elif args.verbose:
            config.operations.log_level = 'DEBUG'
        
        # Crear instancia del CLI con configuración
        cli = DatabaseCLI(db_path=args.db_path, config=config, profile=args.profile)
        
        # Ejecutar comando
        if args.command == "migrate":
            success = cli.migrate()
        elif args.command == "migration-status":
            cli.migration_status()
            success = True
        elif args.command == "backup":
            success = cli.backup(args.dir)
        elif args.command == "restore":
            success = cli.restore(args.backup_file)
        elif args.command == "stats":
            cli.stats()
            success = True
        elif args.command == "cleanup":
            success = cli.cleanup(args.days)
        elif args.command == "vacuum":
            success = cli.vacuum()
        elif args.command == "reset":
            success = cli.reset()
        else:
            cli._print_with_emoji(f"Comando desconocido: {args.command}", "error", "error")
            success = False
        
        # Mostrar estadísticas de operaciones si está habilitado
        if config.performance.enable_progress_indicators and cli.operation_stats['operations_count'] > 0:
            cli._print_with_emoji(f"Total de operaciones ejecutadas: {cli.operation_stats['operations_count']}", "stats")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if 'args' in locals() and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
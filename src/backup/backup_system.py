"""
💾 Sistema de Backup y Recuperación Automático
Protección completa de datos críticos para producción.

Desarrollado por: Experto en Trading & Programación
"""

import asyncio
import shutil
import gzip
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import hashlib
import boto3
from dataclasses import dataclass
import subprocess

@dataclass
class BackupConfig:
    """Configuración de backup."""
    name: str
    source_path: str
    backup_type: str  # 'database', 'files', 'logs', 'config'
    schedule: str  # 'hourly', 'daily', 'weekly'
    retention_days: int
    compression: bool = True
    encryption: bool = False
    cloud_sync: bool = False

@dataclass
class BackupResult:
    """Resultado de backup."""
    config_name: str
    timestamp: datetime
    success: bool
    file_path: Optional[str]
    file_size: int
    checksum: Optional[str]
    error_message: Optional[str] = None

class BackupSystem:
    """Sistema de backup automático."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path(config.get('backup_directory', 'backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuraciones de backup
        self.backup_configs = self._setup_backup_configs()
        
        # Cliente S3 para backup en la nube (opcional)
        self.s3_client = None
        if config.get('aws_access_key'):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config['aws_access_key'],
                aws_secret_access_key=config['aws_secret_key'],
                region_name=config.get('aws_region', 'us-east-1')
            )
    
    def _setup_backup_configs(self) -> List[BackupConfig]:
        """Configurar backups automáticos."""
        return [
            # Backup de base de datos
            BackupConfig(
                name="database_daily",
                source_path="postgresql://localhost:5432/trading_db",
                backup_type="database",
                schedule="daily",
                retention_days=30,
                compression=True,
                encryption=True,
                cloud_sync=True
            ),
            
            # Backup de configuraciones
            BackupConfig(
                name="config_daily",
                source_path="src/config/",
                backup_type="files",
                schedule="daily",
                retention_days=14,
                compression=True,
                encryption=False,
                cloud_sync=True
            ),
            
            # Backup de logs críticos
            BackupConfig(
                name="logs_daily",
                source_path="logs/",
                backup_type="logs",
                schedule="daily",
                retention_days=7,
                compression=True,
                encryption=False,
                cloud_sync=False
            ),
            
            # Backup de datos de trading
            BackupConfig(
                name="trading_data_hourly",
                source_path="data/trading/",
                backup_type="files",
                schedule="hourly",
                retention_days=3,
                compression=True,
                encryption=True,
                cloud_sync=True
            ),
            
            # Backup completo semanal
            BackupConfig(
                name="full_system_weekly",
                source_path="./",
                backup_type="files",
                schedule="weekly",
                retention_days=90,
                compression=True,
                encryption=True,
                cloud_sync=True
            )
        ]
    
    async def start_backup_scheduler(self):
        """Iniciar programador de backups."""
        self.logger.info("💾 Iniciando sistema de backup automático...")
        
        # Crear tareas para cada configuración
        tasks = []
        for config in self.backup_configs:
            if config.schedule == "hourly":
                task = asyncio.create_task(self._hourly_backup_loop(config))
            elif config.schedule == "daily":
                task = asyncio.create_task(self._daily_backup_loop(config))
            elif config.schedule == "weekly":
                task = asyncio.create_task(self._weekly_backup_loop(config))
            
            tasks.append(task)
        
        # Tarea de limpieza
        tasks.append(asyncio.create_task(self._cleanup_loop()))
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"❌ Error en sistema de backup: {e}")
    
    async def _hourly_backup_loop(self, config: BackupConfig):
        """Loop de backup cada hora."""
        while True:
            try:
                await self._perform_backup(config)
                await asyncio.sleep(3600)  # 1 hora
            except Exception as e:
                self.logger.error(f"❌ Error en backup horario {config.name}: {e}")
                await asyncio.sleep(300)  # Reintentar en 5 minutos
    
    async def _daily_backup_loop(self, config: BackupConfig):
        """Loop de backup diario."""
        while True:
            try:
                # Ejecutar a las 2:00 AM
                now = datetime.now()
                next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                wait_seconds = (next_run - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                await self._perform_backup(config)
                
            except Exception as e:
                self.logger.error(f"❌ Error en backup diario {config.name}: {e}")
                await asyncio.sleep(3600)  # Reintentar en 1 hora
    
    async def _weekly_backup_loop(self, config: BackupConfig):
        """Loop de backup semanal."""
        while True:
            try:
                # Ejecutar los domingos a las 1:00 AM
                now = datetime.now()
                days_until_sunday = (6 - now.weekday()) % 7
                if days_until_sunday == 0 and now.hour >= 1:
                    days_until_sunday = 7
                
                next_run = now + timedelta(days=days_until_sunday)
                next_run = next_run.replace(hour=1, minute=0, second=0, microsecond=0)
                
                wait_seconds = (next_run - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                await self._perform_backup(config)
                
            except Exception as e:
                self.logger.error(f"❌ Error en backup semanal {config.name}: {e}")
                await asyncio.sleep(3600)
    
    async def _perform_backup(self, config: BackupConfig) -> BackupResult:
        """Realizar backup según configuración."""
        self.logger.info(f"💾 Iniciando backup: {config.name}")
        
        try:
            timestamp = datetime.now()
            backup_filename = f"{config.name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            if config.backup_type == "database":
                result = await self._backup_database(config, backup_filename)
            elif config.backup_type == "files":
                result = await self._backup_files(config, backup_filename)
            elif config.backup_type == "logs":
                result = await self._backup_logs(config, backup_filename)
            else:
                raise ValueError(f"Tipo de backup no soportado: {config.backup_type}")
            
            # Sincronizar con la nube si está habilitado
            if config.cloud_sync and result.success and self.s3_client:
                await self._sync_to_cloud(result, config)
            
            self.logger.info(f"✅ Backup completado: {config.name}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en backup {config.name}: {e}")
            return BackupResult(
                config_name=config.name,
                timestamp=datetime.now(),
                success=False,
                file_path=None,
                file_size=0,
                checksum=None,
                error_message=str(e)
            )
    
    async def _backup_database(self, config: BackupConfig, filename: str) -> BackupResult:
        """Backup de base de datos PostgreSQL."""
        backup_path = self.backup_dir / f"{filename}.sql"
        
        # Comando pg_dump
        cmd = [
            "pg_dump",
            "--host=localhost",
            "--port=5432",
            "--username=postgres",
            "--dbname=trading_db",
            "--file", str(backup_path),
            "--verbose"
        ]
        
        # Ejecutar pg_dump
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"pg_dump falló: {stderr.decode()}")
        
        # Comprimir si está habilitado
        if config.compression:
            compressed_path = backup_path.with_suffix('.sql.gz')
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            backup_path.unlink()  # Eliminar archivo sin comprimir
            backup_path = compressed_path
        
        # Calcular checksum
        checksum = await self._calculate_checksum(backup_path)
        
        return BackupResult(
            config_name=config.name,
            timestamp=datetime.now(),
            success=True,
            file_path=str(backup_path),
            file_size=backup_path.stat().st_size,
            checksum=checksum
        )
    
    async def _backup_files(self, config: BackupConfig, filename: str) -> BackupResult:
        """Backup de archivos y directorios."""
        source_path = Path(config.source_path)
        
        if config.compression:
            backup_path = self.backup_dir / f"{filename}.tar.gz"
            
            # Crear archivo tar.gz
            cmd = ["tar", "-czf", str(backup_path), "-C", str(source_path.parent), source_path.name]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"tar falló: {stderr.decode()}")
        else:
            backup_path = self.backup_dir / filename
            shutil.copytree(source_path, backup_path)
        
        # Calcular checksum
        checksum = await self._calculate_checksum(backup_path)
        
        return BackupResult(
            config_name=config.name,
            timestamp=datetime.now(),
            success=True,
            file_path=str(backup_path),
            file_size=backup_path.stat().st_size,
            checksum=checksum
        )
    
    async def _backup_logs(self, config: BackupConfig, filename: str) -> BackupResult:
        """Backup específico de logs."""
        return await self._backup_files(config, filename)
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA256 de un archivo."""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _sync_to_cloud(self, result: BackupResult, config: BackupConfig):
        """Sincronizar backup con la nube (S3)."""
        if not self.s3_client or not result.file_path:
            return
        
        try:
            bucket_name = self.config.get('s3_bucket', 'trading-backups')
            key = f"backups/{config.name}/{Path(result.file_path).name}"
            
            # Subir archivo a S3
            self.s3_client.upload_file(result.file_path, bucket_name, key)
            
            self.logger.info(f"☁️ Backup sincronizado con S3: {key}")
            
        except Exception as e:
            self.logger.error(f"❌ Error sincronizando con S3: {e}")
    
    async def _cleanup_loop(self):
        """Loop de limpieza de backups antiguos."""
        while True:
            try:
                await self._cleanup_old_backups()
                await asyncio.sleep(86400)  # Cada 24 horas
            except Exception as e:
                self.logger.error(f"❌ Error en limpieza: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_backups(self):
        """Limpiar backups antiguos según retención."""
        for config in self.backup_configs:
            try:
                cutoff_date = datetime.now() - timedelta(days=config.retention_days)
                
                # Buscar archivos de backup para esta configuración
                pattern = f"{config.name}_*"
                for backup_file in self.backup_dir.glob(pattern):
                    # Extraer fecha del nombre del archivo
                    try:
                        date_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                        file_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                        
                        if file_date < cutoff_date:
                            backup_file.unlink()
                            self.logger.info(f"🗑️ Backup eliminado: {backup_file.name}")
                            
                    except (ValueError, IndexError):
                        # Si no se puede parsear la fecha, mantener el archivo
                        continue
                        
            except Exception as e:
                self.logger.error(f"❌ Error limpiando backups de {config.name}: {e}")
    
    async def restore_backup(self, backup_file: str, target_path: Optional[str] = None) -> bool:
        """Restaurar desde backup."""
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Archivo de backup no encontrado: {backup_file}")
            
            self.logger.info(f"🔄 Restaurando backup: {backup_path.name}")
            
            # Determinar tipo de backup por extensión
            if backup_path.suffix == '.sql' or backup_path.name.endswith('.sql.gz'):
                return await self._restore_database(backup_path)
            elif backup_path.suffix in ['.tar', '.gz'] or backup_path.name.endswith('.tar.gz'):
                return await self._restore_files(backup_path, target_path)
            else:
                raise ValueError(f"Tipo de backup no reconocido: {backup_path.suffix}")
                
        except Exception as e:
            self.logger.error(f"❌ Error restaurando backup: {e}")
            return False
    
    async def _restore_database(self, backup_path: Path) -> bool:
        """Restaurar base de datos desde backup."""
        try:
            # Si está comprimido, descomprimir primero
            if backup_path.name.endswith('.gz'):
                sql_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(sql_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                sql_path = backup_path
            
            # Comando psql para restaurar
            cmd = [
                "psql",
                "--host=localhost",
                "--port=5432",
                "--username=postgres",
                "--dbname=trading_db",
                "--file", str(sql_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Limpiar archivo temporal si se descomprimió
            if backup_path.name.endswith('.gz') and sql_path.exists():
                sql_path.unlink()
            
            if process.returncode != 0:
                raise Exception(f"psql falló: {stderr.decode()}")
            
            self.logger.info("✅ Base de datos restaurada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando base de datos: {e}")
            return False
    
    async def _restore_files(self, backup_path: Path, target_path: Optional[str] = None) -> bool:
        """Restaurar archivos desde backup."""
        try:
            if not target_path:
                target_path = "."
            
            # Comando tar para extraer
            cmd = ["tar", "-xzf", str(backup_path), "-C", target_path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"tar falló: {stderr.decode()}")
            
            self.logger.info("✅ Archivos restaurados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando archivos: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Listar backups disponibles."""
        backups = []
        
        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file():
                try:
                    stat = backup_file.stat()
                    backups.append({
                        'name': backup_file.name,
                        'path': str(backup_file),
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    })
                except Exception as e:
                    self.logger.error(f"❌ Error listando backup {backup_file}: {e}")
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)

async def start_backup_system(config: Dict[str, Any]):
    """Iniciar sistema de backup."""
    backup_system = BackupSystem(config)
    await backup_system.start_backup_scheduler()

if __name__ == "__main__":
    # Configuración de ejemplo
    config = {
        'backup_directory': 'backups',
        'aws_access_key': None,  # Configurar para backup en la nube
        'aws_secret_key': None,
        'aws_region': 'us-east-1',
        's3_bucket': 'trading-backups'
    }
    
    asyncio.run(start_backup_system(config))
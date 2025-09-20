"""
🔍 Sistema de Monitoreo Avanzado para Producción
Monitoreo completo de sistema, rendimiento y trading.

Desarrollado por: Experto en Trading & Programación
"""

import asyncio
import psutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import aiohttp
from pathlib import Path

@dataclass
class SystemMetrics:
    """Métricas del sistema."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]

@dataclass
class TradingMetrics:
    """Métricas de trading."""
    timestamp: datetime
    active_positions: int
    total_trades_today: int
    win_rate: float
    current_pnl: float
    drawdown: float
    sharpe_ratio: float
    profit_factor: float

@dataclass
class AlertRule:
    """Regla de alerta."""
    name: str
    condition: str
    threshold: float
    severity: str  # 'critical', 'warning', 'info'
    cooldown_minutes: int = 15
    last_triggered: Optional[datetime] = None

class AdvancedMonitor:
    """Monitor avanzado para producción."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.metrics_history: List[Dict] = []
        self.alert_rules = self._setup_alert_rules()
        self.webhook_url = config.get('webhook_url')
        
    def _setup_alert_rules(self) -> List[AlertRule]:
        """Configurar reglas de alerta."""
        return [
            AlertRule("high_cpu", "cpu_percent > 80", 80.0, "warning"),
            AlertRule("critical_cpu", "cpu_percent > 95", 95.0, "critical"),
            AlertRule("high_memory", "memory_percent > 85", 85.0, "warning"),
            AlertRule("critical_memory", "memory_percent > 95", 95.0, "critical"),
            AlertRule("high_drawdown", "drawdown > 15", 15.0, "warning"),
            AlertRule("critical_drawdown", "drawdown > 25", 25.0, "critical"),
            AlertRule("low_win_rate", "win_rate < 40", 40.0, "warning"),
            AlertRule("negative_pnl", "current_pnl < -500", -500.0, "warning"),
            AlertRule("system_overload", "load_average[0] > 4", 4.0, "critical")
        ]
    
    async def start_monitoring(self):
        """Iniciar monitoreo."""
        self.is_running = True
        self.logger.info("🔍 Iniciando monitoreo avanzado...")
        
        # Crear tareas de monitoreo
        tasks = [
            asyncio.create_task(self._system_monitoring_loop()),
            asyncio.create_task(self._trading_monitoring_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._alert_processing_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"❌ Error en monitoreo: {e}")
        finally:
            self.is_running = False
    
    async def _system_monitoring_loop(self):
        """Loop de monitoreo del sistema."""
        while self.is_running:
            try:
                metrics = self._collect_system_metrics()
                await self._process_system_alerts(metrics)
                await self._store_metrics('system', metrics.__dict__)
                
                await asyncio.sleep(30)  # Cada 30 segundos
                
            except Exception as e:
                self.logger.error(f"❌ Error en monitoreo de sistema: {e}")
                await asyncio.sleep(60)
    
    async def _trading_monitoring_loop(self):
        """Loop de monitoreo de trading."""
        while self.is_running:
            try:
                metrics = await self._collect_trading_metrics()
                await self._process_trading_alerts(metrics)
                await self._store_metrics('trading', metrics.__dict__)
                
                await asyncio.sleep(60)  # Cada minuto
                
            except Exception as e:
                self.logger.error(f"❌ Error en monitoreo de trading: {e}")
                await asyncio.sleep(120)
    
    async def _health_check_loop(self):
        """Loop de verificación de salud."""
        while self.is_running:
            try:
                health_status = await self._perform_health_checks()
                await self._store_metrics('health', health_status)
                
                if not health_status.get('overall_healthy', True):
                    await self._send_alert({
                        'type': 'health_check_failed',
                        'severity': 'critical',
                        'message': 'Sistema no saludable',
                        'details': health_status
                    })
                
                await asyncio.sleep(120)  # Cada 2 minutos
                
            except Exception as e:
                self.logger.error(f"❌ Error en health check: {e}")
                await asyncio.sleep(180)
    
    async def _alert_processing_loop(self):
        """Loop de procesamiento de alertas."""
        while self.is_running:
            try:
                # Procesar alertas pendientes
                await self._process_pending_alerts()
                
                # Limpiar alertas antiguas
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Error procesando alertas: {e}")
                await asyncio.sleep(60)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Recopilar métricas del sistema."""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage('/').percent,
            network_io=dict(psutil.net_io_counters()._asdict()),
            process_count=len(psutil.pids()),
            load_average=list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        )
    
    async def _collect_trading_metrics(self) -> TradingMetrics:
        """Recopilar métricas de trading."""
        try:
            # Aquí conectarías con tu sistema de trading
            # Por ahora, valores simulados
            return TradingMetrics(
                timestamp=datetime.now(),
                active_positions=0,  # Obtener del position manager
                total_trades_today=0,  # Obtener de la base de datos
                win_rate=0.0,  # Calcular desde trades
                current_pnl=0.0,  # Obtener del paper trader
                drawdown=0.0,  # Calcular drawdown actual
                sharpe_ratio=0.0,  # Calcular Sharpe ratio
                profit_factor=0.0  # Calcular profit factor
            )
        except Exception as e:
            self.logger.error(f"❌ Error recopilando métricas de trading: {e}")
            return TradingMetrics(
                timestamp=datetime.now(),
                active_positions=0, total_trades_today=0, win_rate=0.0,
                current_pnl=0.0, drawdown=0.0, sharpe_ratio=0.0, profit_factor=0.0
            )
    
    async def _perform_health_checks(self) -> Dict[str, Any]:
        """Realizar verificaciones de salud."""
        checks = {
            'database_connection': await self._check_database(),
            'api_endpoints': await self._check_api_endpoints(),
            'disk_space': await self._check_disk_space(),
            'memory_leaks': await self._check_memory_leaks(),
            'trading_system': await self._check_trading_system()
        }
        
        overall_healthy = all(checks.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_healthy': overall_healthy,
            'checks': checks
        }
    
    async def _check_database(self) -> bool:
        """Verificar conexión a base de datos."""
        try:
            # Implementar verificación real de DB
            return True
        except:
            return False
    
    async def _check_api_endpoints(self) -> bool:
        """Verificar endpoints de API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/health', timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def _check_disk_space(self) -> bool:
        """Verificar espacio en disco."""
        return psutil.disk_usage('/').percent < 90
    
    async def _check_memory_leaks(self) -> bool:
        """Verificar posibles memory leaks."""
        memory_percent = psutil.virtual_memory().percent
        return memory_percent < 90
    
    async def _check_trading_system(self) -> bool:
        """Verificar sistema de trading."""
        try:
            # Implementar verificaciones específicas del trading system
            return True
        except:
            return False
    
    async def _process_system_alerts(self, metrics: SystemMetrics):
        """Procesar alertas del sistema."""
        for rule in self.alert_rules:
            if await self._should_trigger_alert(rule, metrics.__dict__):
                await self._trigger_alert(rule, metrics.__dict__)
    
    async def _process_trading_alerts(self, metrics: TradingMetrics):
        """Procesar alertas de trading."""
        for rule in self.alert_rules:
            if await self._should_trigger_alert(rule, metrics.__dict__):
                await self._trigger_alert(rule, metrics.__dict__)
    
    async def _should_trigger_alert(self, rule: AlertRule, metrics: Dict) -> bool:
        """Determinar si se debe disparar una alerta."""
        # Verificar cooldown
        if rule.last_triggered:
            cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return False
        
        # Evaluar condición
        try:
            return eval(rule.condition, {"__builtins__": {}}, metrics)
        except:
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metrics: Dict):
        """Disparar una alerta."""
        rule.last_triggered = datetime.now()
        
        alert = {
            'rule_name': rule.name,
            'severity': rule.severity,
            'condition': rule.condition,
            'threshold': rule.threshold,
            'current_value': self._extract_value_from_condition(rule.condition, metrics),
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        await self._send_alert(alert)
    
    def _extract_value_from_condition(self, condition: str, metrics: Dict) -> Any:
        """Extraer valor actual de la condición."""
        try:
            # Extraer la variable de la condición
            var_name = condition.split()[0]
            return metrics.get(var_name, 'unknown')
        except:
            return 'unknown'
    
    async def _send_alert(self, alert: Dict):
        """Enviar alerta."""
        self.logger.warning(f"🚨 ALERTA {alert['severity'].upper()}: {alert}")
        
        # Enviar a webhook si está configurado
        if self.webhook_url:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(self.webhook_url, json=alert)
            except Exception as e:
                self.logger.error(f"❌ Error enviando webhook: {e}")
        
        # Guardar en archivo de alertas
        await self._save_alert_to_file(alert)
    
    async def _save_alert_to_file(self, alert: Dict):
        """Guardar alerta en archivo."""
        try:
            alerts_file = Path("logs/alerts.jsonl")
            alerts_file.parent.mkdir(exist_ok=True)
            
            with open(alerts_file, "a") as f:
                f.write(json.dumps(alert) + "\n")
        except Exception as e:
            self.logger.error(f"❌ Error guardando alerta: {e}")
    
    async def _store_metrics(self, metric_type: str, data: Dict):
        """Almacenar métricas."""
        metric_entry = {
            'type': metric_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.metrics_history.append(metric_entry)
        
        # Mantener solo las últimas 1000 métricas en memoria
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    async def _process_pending_alerts(self):
        """Procesar alertas pendientes."""
        # Implementar lógica de procesamiento de alertas pendientes
        pass
    
    async def _cleanup_old_alerts(self):
        """Limpiar alertas antiguas."""
        # Implementar limpieza de alertas antiguas
        pass
    
    def get_current_status(self) -> Dict[str, Any]:
        """Obtener estado actual del monitoreo."""
        return {
            'is_running': self.is_running,
            'metrics_collected': len(self.metrics_history),
            'active_alerts': len([r for r in self.alert_rules if r.last_triggered]),
            'last_update': datetime.now().isoformat()
        }

async def start_advanced_monitoring(config: Dict[str, Any]):
    """Iniciar monitoreo avanzado."""
    monitor = AdvancedMonitor(config)
    await monitor.start_monitoring()

if __name__ == "__main__":
    # Configuración de ejemplo
    config = {
        'webhook_url': None,  # URL del webhook para alertas
        'log_level': 'INFO'
    }
    
    asyncio.run(start_advanced_monitoring(config))
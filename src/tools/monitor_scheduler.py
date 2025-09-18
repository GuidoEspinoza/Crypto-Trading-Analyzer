#!/usr/bin/env python3
"""
📊 MONITOR EN TIEMPO REAL DEL SCHEDULER
======================================

Este script monitorea continuamente el estado del scheduler del TradingBot,
especialmente enfocado en el cierre automático PRE_RESET.

Características:
- Monitoreo en tiempo real del scheduler
- Alertas cuando se acerca la hora de cierre
- Verificación de la disponibilidad del position_manager
- Logs detallados de la ejecución
- Simulación de ejecución para testing
"""

import sys
import os
import time
import schedule
from datetime import datetime, timedelta
import threading
import signal

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

class SchedulerMonitor:
    """🔍 Monitor del scheduler del TradingBot"""
    
    def __init__(self):
        self.running = False
        self.bot = None
        self.monitor_thread = None
        self.last_check = None
        
    def initialize_bot(self):
        """🤖 Inicializar el TradingBot"""
        try:
            from src.core.trading_bot import TradingBot
            self.bot = TradingBot()
            print("✅ TradingBot inicializado exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error inicializando TradingBot: {e}")
            return False
    
    def check_scheduler_status(self):
        """📋 Verificar estado actual del scheduler"""
        try:
            jobs = schedule.get_jobs()
            
            print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - Estado del Scheduler:")
            print(f"📊 Jobs programados: {len(jobs)}")
            
            if not jobs:
                print("⚠️ NO HAY JOBS PROGRAMADOS")
                return
            
            for i, job in enumerate(jobs, 1):
                print(f"   Job {i}: {job.job_func.__name__ if hasattr(job.job_func, '__name__') else 'Unknown'}")
                print(f"   Próxima ejecución: {job.next_run}")
                
                # Calcular tiempo hasta próxima ejecución
                if job.next_run:
                    time_until = job.next_run - datetime.now()
                    hours = time_until.total_seconds() / 3600
                    
                    if hours < 1:
                        minutes = time_until.total_seconds() / 60
                        print(f"   ⏰ Tiempo restante: {minutes:.1f} minutos")
                        if minutes < 10:
                            print("   🚨 ALERTA: Ejecución en menos de 10 minutos!")
                    else:
                        print(f"   ⏰ Tiempo restante: {hours:.1f} horas")
            
            # Verificar position_manager
            if self.bot and hasattr(self.bot, 'position_manager') and self.bot.position_manager:
                print("✅ Position Manager disponible")
            else:
                print("❌ Position Manager NO disponible")
                
        except Exception as e:
            print(f"❌ Error verificando scheduler: {e}")
    
    def check_pre_reset_config(self):
        """⚙️ Verificar configuración del cierre pre-reset"""
        try:
            from src.config.global_constants import PRE_RESET_CLOSURE_CONFIG
            
            print(f"\n⚙️ Configuración PRE_RESET:")
            print(f"   Habilitado: {PRE_RESET_CLOSURE_CONFIG.get('enabled', False)}")
            print(f"   Umbral ganancia: {PRE_RESET_CLOSURE_CONFIG.get('profit_threshold_percent', 0.5)}%")
            print(f"   Hora cierre: {PRE_RESET_CLOSURE_CONFIG.get('closure_time', '10:45')}")
            
        except Exception as e:
            print(f"❌ Error verificando configuración: {e}")
    
    def simulate_pre_reset_execution(self):
        """🧪 Simular ejecución del cierre pre-reset"""
        print(f"\n🧪 SIMULANDO EJECUCIÓN PRE-RESET...")
        
        if not self.bot:
            print("❌ Bot no disponible para simulación")
            return
            
        try:
            result = self.bot.force_pre_reset_closure()
            print(f"📊 Resultado de simulación: {result}")
            
            if result.get('success', False):
                print("✅ Simulación exitosa")
            else:
                print(f"❌ Simulación falló: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"❌ Error en simulación: {e}")
    
    def monitor_loop(self):
        """🔄 Loop principal de monitoreo"""
        print("🚀 Iniciando monitoreo del scheduler...")
        
        while self.running:
            try:
                # Verificar estado cada 30 segundos
                self.check_scheduler_status()
                
                # Verificar configuración cada 5 minutos
                current_time = datetime.now()
                if not self.last_check or (current_time - self.last_check).total_seconds() > 300:
                    self.check_pre_reset_config()
                    self.last_check = current_time
                
                # Ejecutar jobs pendientes del scheduler
                schedule.run_pending()
                
                time.sleep(30)  # Esperar 30 segundos
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupción detectada, deteniendo monitor...")
                break
            except Exception as e:
                print(f"❌ Error en loop de monitoreo: {e}")
                time.sleep(10)
    
    def start_monitoring(self):
        """▶️ Iniciar monitoreo"""
        if not self.initialize_bot():
            return False
            
        # Programar el cierre pre-reset en el bot
        if self.bot:
            try:
                self.bot._schedule_pre_reset_closure()
                print("✅ Cierre pre-reset programado en el bot")
            except Exception as e:
                print(f"⚠️ Error programando cierre pre-reset: {e}")
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✅ Monitor iniciado exitosamente")
        return True
    
    def stop_monitoring(self):
        """⏹️ Detener monitoreo"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Monitor detenido")

def signal_handler(signum, frame):
    """🛑 Manejador de señales para cierre limpio"""
    print("\n🛑 Señal de interrupción recibida, cerrando monitor...")
    global monitor
    if monitor:
        monitor.stop_monitoring()
    sys.exit(0)

def interactive_menu():
    """📋 Menú interactivo para el monitor"""
    global monitor
    
    while True:
        print("\n" + "="*60)
        print("📊 MONITOR DEL SCHEDULER - MENÚ INTERACTIVO")
        print("="*60)
        print("1. 📋 Ver estado actual del scheduler")
        print("2. ⚙️ Ver configuración PRE_RESET")
        print("3. 🧪 Simular ejecución PRE_RESET")
        print("4. 🔄 Iniciar monitoreo continuo")
        print("5. 🛑 Salir")
        print("="*60)
        
        try:
            choice = input("Selecciona una opción (1-5): ").strip()
            
            if choice == '1':
                monitor.check_scheduler_status()
                
            elif choice == '2':
                monitor.check_pre_reset_config()
                
            elif choice == '3':
                monitor.simulate_pre_reset_execution()
                
            elif choice == '4':
                print("🚀 Iniciando monitoreo continuo...")
                print("💡 Presiona Ctrl+C para detener")
                monitor.start_monitoring()
                
                try:
                    # Mantener el programa corriendo
                    while monitor.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    monitor.stop_monitoring()
                    
            elif choice == '5':
                print("👋 Saliendo del monitor...")
                break
                
            else:
                print("❌ Opción inválida, intenta de nuevo")
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupción detectada, saliendo...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """🚀 Función principal"""
    global monitor
    
    print("📊 MONITOR EN TIEMPO REAL DEL SCHEDULER")
    print("="*80)
    print("🎯 Objetivo: Monitorear el cierre automático PRE_RESET")
    print("⏰ Frecuencia: Verificación cada 30 segundos")
    print("🔧 Funciones: Estado, configuración, simulación")
    print("="*80)
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crear monitor
    monitor = SchedulerMonitor()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--continuous':
            print("🚀 Modo continuo activado")
            if monitor.initialize_bot():
                monitor.start_monitoring()
                try:
                    while monitor.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    monitor.stop_monitoring()
            return
        elif sys.argv[1] == '--test':
            print("🧪 Modo de prueba activado")
            if monitor.initialize_bot():
                monitor.check_scheduler_status()
                monitor.check_pre_reset_config()
                monitor.simulate_pre_reset_execution()
            return
    
    # Inicializar bot
    if not monitor.initialize_bot():
        print("❌ No se pudo inicializar el bot, saliendo...")
        return
    
    # Mostrar menú interactivo
    interactive_menu()

if __name__ == "__main__":
    monitor = None
    main()
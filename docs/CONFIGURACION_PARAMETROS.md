# 📋 Documentación de Parámetros de Configuración

Esta documentación describe todos los parámetros disponibles en el sistema de trading y sus efectos en el comportamiento del bot.

## 🎯 Perfiles de Trading

El sistema incluye 4 perfiles predefinidos que pueden seleccionarse modificando `TRADING_PROFILE` en `config.py`:

### 🚀 RAPIDO (Ultra-Rápido)
- **Objetivo**: Máxima frecuencia de trades en timeframes cortos
- **Timeframes**: 1m, 5m, 15m
- **Intervalo de análisis**: 5 segundos
- **Trades diarios máximos**: 20
- **Posiciones concurrentes**: 8
- **Confianza mínima**: 65%

### ⚡ AGRESIVO (Balanceado)
- **Objetivo**: Balance entre velocidad y control de riesgo
- **Timeframes**: 15m, 1h, 4h
- **Intervalo de análisis**: 30 segundos
- **Trades diarios máximos**: 12
- **Posiciones concurrentes**: 5
- **Confianza mínima**: 70%

### 🛡️ OPTIMO (Conservador)
- **Objetivo**: Calidad sobre cantidad, preservación de capital
- **Timeframes**: 1h, 4h, 1d
- **Intervalo de análisis**: 60 segundos
- **Trades diarios máximos**: 8
- **Posiciones concurrentes**: 3
- **Confianza mínima**: 75%

### 🔒 CONSERVADOR (Ultra-Conservador)
- **Objetivo**: Máxima preservación de capital
- **Timeframes**: 4h, 1d
- **Intervalo de análisis**: 120 segundos
- **Trades diarios máximos**: 5
- **Posiciones concurrentes**: 2
- **Confianza mínima**: 80%

## 📊 Parámetros de Gestión de Riesgo

### Tamaños de Posición
- **max_position_size**: Tamaño máximo por posición (% del balance)
  - Rango válido: 0.01 - 1.0
  - RAPIDO: 0.15, AGRESIVO: 0.12, OPTIMO: 0.08, CONSERVADOR: 0.05

- **max_total_exposure**: Exposición total máxima (% del balance)
  - Rango válido: 0.1 - 1.0
  - RAPIDO: 0.8, AGRESIVO: 0.6, OPTIMO: 0.4, CONSERVADOR: 0.25

- **min_trade_value**: Valor mínimo por trade (USDT)
  - Rango válido: 1.0 - 1000.0
  - Todos los perfiles: 10.0

### Stop Loss y Take Profit
- **stop_loss_percentage**: Porcentaje de stop loss
  - Rango válido: 0.01 - 0.5
  - RAPIDO: 0.025, AGRESIVO: 0.03, OPTIMO: 0.035, CONSERVADOR: 0.04

- **take_profit_percentage**: Porcentaje de take profit
  - Rango válido: 0.01 - 1.0
  - RAPIDO: 0.06, AGRESIVO: 0.08, OPTIMO: 0.10, CONSERVADOR: 0.12

- **trailing_stop_activation**: Activación del trailing stop
  - Rango válido: 0.01 - 0.5
  - RAPIDO: 0.02, AGRESIVO: 0.025, OPTIMO: 0.03, CONSERVADOR: 0.035

- **trailing_stop_distance**: Distancia del trailing stop
  - Rango válido: 0.005 - 0.2
  - RAPIDO: 0.01, AGRESIVO: 0.012, OPTIMO: 0.015, CONSERVADOR: 0.018

### Circuit Breaker
- **max_consecutive_losses**: Pérdidas consecutivas antes de parar
  - Rango válido: 1 - 20
  - RAPIDO: 7, AGRESIVO: 5, OPTIMO: 4, CONSERVADOR: 3

- **circuit_breaker_cooldown_hours**: Horas de pausa tras activación
  - Rango válido: 1 - 48
  - RAPIDO: 1.5, AGRESIVO: 2, OPTIMO: 3, CONSERVADOR: 4

- **max_drawdown_threshold**: Umbral máximo de drawdown (%)
  - Rango válido: 0.05 - 0.5
  - RAPIDO: 0.12, AGRESIVO: 0.10, OPTIMO: 0.08, CONSERVADOR: 0.06

## ⚙️ Parámetros Técnicos

### Intervalos y Timeouts
- **analysis_interval**: Intervalo entre análisis (segundos)
  - Rango válido: 30 - 3600
  - Varía por perfil: 5-120 segundos

- **position_check_interval**: Intervalo de verificación de posiciones
  - Rango válido: 10 - 300
  - Todos los perfiles: 30 segundos

- **connection_timeout**: Timeout de conexión (segundos)
  - Rango válido: 5 - 120
  - Todos los perfiles: 30 segundos

### Reintentos y Delays
- **max_retries**: Número máximo de reintentos
  - Rango válido: 1 - 10
  - Todos los perfiles: 3

- **retry_delay**: Delay entre reintentos (segundos)
  - Rango válido: 0.5 - 30.0
  - Todos los perfiles: 1.0

- **max_slippage**: Slippage máximo permitido
  - Rango válido: 0.001 - 0.1
  - Todos los perfiles: 0.005

### Ajustes de Volatilidad
- **volatility_adjustment_factor**: Factor de ajuste por volatilidad
  - Rango válido: 0.5 - 3.0
  - RAPIDO: 1.5, AGRESIVO: 1.2, OPTIMO: 1.0, CONSERVADOR: 0.8

- **min_confidence_score**: Puntuación mínima de confianza
  - Rango válido: 30 - 95
  - Varía por perfil: 65-80%

## 🔧 Configuración de Monitoreo

### Intervalos de Monitoreo
- **performance_check_interval**: Verificación de rendimiento (segundos)
  - Todos los perfiles: 300 (5 minutos)

- **health_check_interval**: Verificación de salud del sistema (segundos)
  - Todos los perfiles: 60 (1 minuto)

- **metrics_update_interval**: Actualización de métricas (segundos)
  - Todos los perfiles: 30

### Manejo de Errores
- **error_recovery_attempts**: Intentos de recuperación de errores
  - Todos los perfiles: 3

- **error_cooldown_period**: Período de enfriamiento tras error (segundos)
  - Todos los perfiles: 60

## 📈 Configuración de Estrategias

### Multi-Timeframe
- **primary_weight**: Peso del timeframe principal
  - RAPIDO: 0.5, AGRESIVO: 0.6, OPTIMO: 0.7, CONSERVADOR: 0.8

- **secondary_weight**: Peso del timeframe secundario
  - RAPIDO: 0.3, AGRESIVO: 0.25, OPTIMO: 0.2, CONSERVADOR: 0.15

- **tertiary_weight**: Peso del timeframe terciario
  - RAPIDO: 0.2, AGRESIVO: 0.15, OPTIMO: 0.1, CONSERVADOR: 0.05

### Ensemble
- **min_strategy_agreement**: Acuerdo mínimo entre estrategias
  - RAPIDO: 0.6, AGRESIVO: 0.65, OPTIMO: 0.7, CONSERVADOR: 0.75

- **strategy_weights**: Pesos de las estrategias
  - Configuración específica por perfil para cada estrategia

## 🛠️ Validación de Configuración

El sistema incluye validación automática que:

1. **Verifica rangos válidos**: Todos los parámetros deben estar dentro de rangos seguros
2. **Valida consistencia**: Los parámetros deben ser consistentes entre sí
3. **Proporciona valores seguros**: Si un valor está fuera de rango, se ajusta automáticamente
4. **Registra advertencias**: Cualquier ajuste se registra en los logs

### Uso de la Validación

```python
from src.config.config import ConfigValidator

# Validar todos los perfiles
if ConfigValidator.validate_all_profiles():
    print("✅ Todos los perfiles son válidos")

# Obtener valor seguro
safe_value = ConfigValidator.get_safe_value('max_position_size', 0.25)
```

## 🚨 Recomendaciones de Uso

### Para Principiantes
- Usar perfil **CONSERVADOR** o **OPTIMO**
- Comenzar con balance pequeño
- Monitorear resultados durante al menos 1 semana

### Para Usuarios Experimentados
- Perfiles **AGRESIVO** o **RAPIDO** según tolerancia al riesgo
- Ajustar parámetros específicos según estrategia
- Usar validación antes de cambios importantes

### Para Desarrollo
- Usar perfil **RAPIDO** para pruebas rápidas
- Validar configuración después de cambios
- Revisar logs de validación regularmente

## 📝 Notas Importantes

1. **Cambios en vivo**: Algunos parámetros requieren reinicio del bot
2. **Backtesting**: Los perfiles afectan también al backtesting
3. **Paper trading**: Usar para probar nuevas configuraciones
4. **Logs**: Revisar logs de validación para detectar problemas
5. **Monitoreo**: Supervisar métricas de rendimiento regularmente

---

*Última actualización: Enero 2025*
*Para soporte técnico, revisar los logs del sistema o contactar al equipo de desarrollo.*
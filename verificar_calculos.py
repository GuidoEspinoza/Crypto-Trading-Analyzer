#!/usr/bin/env python3
import math

print('=== VERIFICACIÓN DE CÁLCULOS SIMULACION_GANANCIAS.md ===\n')

# Parámetros del perfil RÁPIDO según la tabla
trades_diarios = 25
riesgo_por_trade = 0.018  # 1.8%
win_rate = 0.58  # 58%
tp_promedio = 0.042  # 4.2%
sl_promedio = 0.018  # 1.8%

# Cálculo de ganancia diaria esperada
ganancia_por_trade_ganador = tp_promedio * riesgo_por_trade
perdida_por_trade_perdedor = sl_promedio * riesgo_por_trade

ganancia_diaria_esperada = (trades_diarios * win_rate * ganancia_por_trade_ganador) - (trades_diarios * (1-win_rate) * perdida_por_trade_perdedor)

print(f'Parámetros del perfil RÁPIDO:')
print(f'- Trades diarios: {trades_diarios}')
print(f'- Win rate: {win_rate*100}%')
print(f'- TP promedio: {tp_promedio*100}%')
print(f'- SL promedio: {sl_promedio*100}%')
print(f'- Riesgo por trade: {riesgo_por_trade*100}%')
print(f'\nGanancia por trade ganador: {ganancia_por_trade_ganador*100:.4f}%')
print(f'Pérdida por trade perdedor: {perdida_por_trade_perdedor*100:.4f}%')
print(f'Ganancia diaria esperada: {ganancia_diaria_esperada*100:.4f}%\n')

# Verificar proyecciones del escenario REALISTA
balance_inicial = 100
valores_tabla = {
    1: 100.61,
    7: 104.35,
    30: 119.42,
    180: 242.67,
    365: 588.95,
    730: 3468.12
}

print('=== VERIFICACIÓN ESCENARIO REALISTA ===\n')

for dias, valor_tabla in valores_tabla.items():
    balance_calculado = balance_inicial * ((1 + ganancia_diaria_esperada) ** dias)
    diferencia = abs(balance_calculado - valor_tabla)
    porcentaje_error = (diferencia / valor_tabla) * 100
    
    periodo = {
        1: '1 día',
        7: '1 semana',
        30: '1 mes',
        180: '6 meses',
        365: '1 año',
        730: '2 años'
    }[dias]
    
    print(f'{periodo}:')
    print(f'  Calculado: ${balance_calculado:.2f}')
    print(f'  En tabla:  ${valor_tabla:.2f}')
    print(f'  Diferencia: ${diferencia:.2f} ({porcentaje_error:.2f}% error)\n')

# Verificar consistencia entre balances
print('=== VERIFICACIÓN DE CONSISTENCIA ENTRE BALANCES ===\n')

balances = [100, 500, 1000]
valores_1año = [588.95, 2944.75, 5889.50]

print('Verificando que los porcentajes sean iguales:')
for i, balance in enumerate(balances):
    roi = (valores_1año[i] / balance - 1) * 100
    print(f'${balance} -> ${valores_1año[i]:.2f} = {roi:.2f}% ROI')

# Verificar ratios
ratio_500_100 = (valores_1año[1] / balances[1]) / (valores_1año[0] / balances[0])
ratio_1000_100 = (valores_1año[2] / balances[2]) / (valores_1año[0] / balances[0])

print(f'\nRatios (deben ser 1.0):')
print(f'Ratio $500/$100: {ratio_500_100:.6f}')
print(f'Ratio $1000/$100: {ratio_1000_100:.6f}')

# Verificar progresión temporal
print('\n=== ANÁLISIS DE PROGRESIÓN TEMPORAL ===\n')

valores = [100, 100.61, 104.35, 119.42, 242.67, 588.95, 3468.12]
periodos = ['Inicial', '1 día', '1 semana', '1 mes', '6 meses', '1 año', '2 años']
dias = [0, 1, 7, 30, 180, 365, 730]

print('Tasas diarias implícitas entre períodos:')
for i in range(1, len(valores)):
    tasa_diaria_implicita = (valores[i]/valores[i-1]) ** (1/(dias[i]-dias[i-1])) - 1
    print(f'{periodos[i-1]} -> {periodos[i]}: {tasa_diaria_implicita*100:.4f}% diario')

# Verificar si los números son realistas
print('\n=== ANÁLISIS DE REALISMO ===\n')

roi_anual = (588.95 / 100 - 1) * 100
roi_mensual_promedio = ((588.95 / 100) ** (1/12) - 1) * 100

print(f'ROI anual perfil RÁPIDO: {roi_anual:.2f}%')
print(f'ROI mensual promedio: {roi_mensual_promedio:.2f}%')
print(f'Ganancia diaria promedio: {ganancia_diaria_esperada*100:.4f}%')

if roi_anual > 1000:
    print('⚠️  ADVERTENCIA: ROI anual muy alto (>1000%)')
if roi_mensual_promedio > 50:
    print('⚠️  ADVERTENCIA: ROI mensual muy alto (>50%)')
if ganancia_diaria_esperada > 0.05:
    print('⚠️  ADVERTENCIA: Ganancia diaria muy alta (>5%)')

print('\n=== CONCLUSIONES ===\n')
print('1. Verificar si los cálculos de capitalización compuesta son correctos')
print('2. Revisar si los parámetros de trading son realistas')
print('3. Considerar factores como slippage, comisiones, y volatilidad del mercado')
print('4. Los números pueden ser demasiado optimistas para un escenario "realista"')
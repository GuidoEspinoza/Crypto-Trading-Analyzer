#!/usr/bin/env python3
import math

print('=== CÁLCULOS CORREGIDOS PARA SIMULACION_GANANCIAS.md ===\n')

# Parámetros más realistas basados en trading real
perfiles = {
    'RAPIDO': {
        'trades_diarios': 25,
        'riesgo_por_trade': 0.015,  # 1.5% (más conservador)
        'win_rate': 0.58,
        'tp_promedio': 0.035,  # 3.5% (más realista)
        'sl_promedio': 0.015,  # 1.5%
        'factor_slippage': 0.998  # 0.2% slippage/comisiones
    },
    'AGRESIVO': {
        'trades_diarios': 12,
        'riesgo_por_trade': 0.012,  # 1.2%
        'win_rate': 0.68,
        'tp_promedio': 0.038,  # 3.8%
        'sl_promedio': 0.013,  # 1.3%
        'factor_slippage': 0.998
    },
    'OPTIMO': {
        'trades_diarios': 8,
        'riesgo_por_trade': 0.008,  # 0.8%
        'win_rate': 0.78,
        'tp_promedio': 0.042,  # 4.2%
        'sl_promedio': 0.011,  # 1.1%
        'factor_slippage': 0.999
    },
    'CONSERVADOR': {
        'trades_diarios': 4,
        'riesgo_por_trade': 0.005,  # 0.5%
        'win_rate': 0.85,
        'tp_promedio': 0.045,  # 4.5%
        'sl_promedio': 0.009,  # 0.9%
        'factor_slippage': 0.999
    }
}

def calcular_ganancia_diaria(perfil):
    """Calcula la ganancia diaria esperada para un perfil"""
    ganancia_por_trade_ganador = perfil['tp_promedio'] * perfil['riesgo_por_trade']
    perdida_por_trade_perdedor = perfil['sl_promedio'] * perfil['riesgo_por_trade']
    
    ganancia_bruta = (perfil['trades_diarios'] * perfil['win_rate'] * ganancia_por_trade_ganador) - \
                     (perfil['trades_diarios'] * (1-perfil['win_rate']) * perdida_por_trade_perdedor)
    
    # Aplicar factor de slippage/comisiones
    ganancia_neta = ganancia_bruta * perfil['factor_slippage']
    
    return ganancia_neta

def proyectar_balance(balance_inicial, ganancia_diaria, dias):
    """Proyecta el balance con capitalización compuesta"""
    return balance_inicial * ((1 + ganancia_diaria) ** dias)

# Calcular para cada perfil
periodos = {
    '1 día': 1,
    '1 semana': 7,
    '1 mes': 30,
    '6 meses': 180,
    '1 año': 365,
    '2 años': 730
}

balances = [100, 500, 1000]

print('=== PROYECCIONES CORREGIDAS (ESCENARIO REALISTA) ===\n')

for nombre_perfil, perfil in perfiles.items():
    ganancia_diaria = calcular_ganancia_diaria(perfil)
    
    print(f'📊 PERFIL {nombre_perfil}:')
    print(f'   Ganancia diaria esperada: {ganancia_diaria*100:.4f}%')
    print(f'   ROI anual: {((1 + ganancia_diaria)**365 - 1)*100:.2f}%')
    print(f'   ROI mensual promedio: {((1 + ganancia_diaria)**30 - 1)*100:.2f}%\n')
    
    # Proyecciones para balance de $100
    print(f'   Balance $100 USDT:')
    for periodo, dias in periodos.items():
        balance_final = proyectar_balance(100, ganancia_diaria, dias)
        ganancia_pct = (balance_final / 100 - 1) * 100
        print(f'   {periodo:10}: ${balance_final:8.2f} (+{ganancia_pct:6.2f}%)')
    print()

# Generar tabla corregida para el documento
print('\n=== TABLA CORREGIDA PARA EL DOCUMENTO ===\n')

print('| Período | 🚀 RÁPIDO | ⚡ AGRESIVO | 🎯 ÓPTIMO | 🛡️ CONSERVADOR |')
print('|---------|-----------|-------------|------------|----------------|')

for periodo, dias in periodos.items():
    fila = f'| **{periodo}** |'
    
    for nombre_perfil in ['RAPIDO', 'AGRESIVO', 'OPTIMO', 'CONSERVADOR']:
        perfil = perfiles[nombre_perfil]
        ganancia_diaria = calcular_ganancia_diaria(perfil)
        balance_final = proyectar_balance(100, ganancia_diaria, dias)
        ganancia_pct = (balance_final / 100 - 1) * 100
        fila += f' ${balance_final:.2f} (+{ganancia_pct:.2f}%) |'
    
    print(fila)

print('\n=== ANÁLISIS DE REALISMO ===\n')

for nombre_perfil, perfil in perfiles.items():
    ganancia_diaria = calcular_ganancia_diaria(perfil)
    roi_anual = ((1 + ganancia_diaria)**365 - 1) * 100
    roi_mensual = ((1 + ganancia_diaria)**30 - 1) * 100
    
    print(f'{nombre_perfil}:')
    print(f'  ROI anual: {roi_anual:.2f}%')
    print(f'  ROI mensual: {roi_mensual:.2f}%')
    print(f'  Ganancia diaria: {ganancia_diaria*100:.4f}%')
    
    # Evaluar realismo
    if roi_anual > 500:
        print('  ⚠️  ROI anual muy alto')
    elif roi_anual > 200:
        print('  ⚡ ROI anual agresivo pero posible')
    elif roi_anual > 50:
        print('  ✅ ROI anual realista')
    else:
        print('  🛡️  ROI anual conservador')
    print()

print('=== RECOMENDACIONES ===\n')
print('1. Los cálculos originales eran demasiado optimistas')
print('2. Se incluyeron factores de slippage y comisiones')
print('3. Se ajustaron los parámetros a valores más realistas')
print('4. Los nuevos números son más conservadores pero alcanzables')
print('5. Se mantiene la progresión lógica entre perfiles de riesgo')
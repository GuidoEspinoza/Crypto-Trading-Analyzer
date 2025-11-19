# Resumen de Horarios de Trading

Este documento resume los horarios actualmente configurados para el bot, expresados en UTC y sus equivalentes en Chile para verano (CLST, UTC−3) e invierno (CLT, UTC−4).

Notas importantes:
- Algunos rangos cruzan medianoche en UTC; en Chile se observan como dos bloques entre días consecutivos.
- Los mercados de EE. UU. cambian entre EDT (UTC−4) y EST (UTC−5); se muestran ambos para precisión.
- Fuente: `src/config/time_trading_config.py` y `src/utils/market_hours.py`.

## Horarios Inteligentes (Smart Trading)

| Tipo | Horario UTC | Chile Verano (CLST) | Chile Invierno (CLT) |
|---|---|---|---|
| Principal | 11:00–02:30 (cruza medianoche) | 08:00–23:30 (cruza medianoche) | 07:00–22:30 (cruza medianoche) |
| Extendido | 09:00–02:59 (cruza medianoche) | 06:00–23:59 (cruza medianoche) | 05:00–22:59 (cruza medianoche) |
| Nocturno (Asia) | 01:00–11:00 | 22:00–08:00 (cruza medianoche) | 21:00–07:00 (cruza medianoche) |

## Sesiones de Alta Volatilidad (UTC)

| Sesión | Horario UTC | Chile Verano (CLST) | Chile Invierno (CLT) |
|---|---|---|---|
| Apertura Asiática | 22:00–02:00 (cruza medianoche) | 19:00–23:00 (día previo) | 18:00–22:00 (día previo) |
| Apertura Londres | 08:00–12:00 | 05:00–09:00 | 04:00–08:00 |
| Apertura NY | 14:30–18:30 | 11:30–15:30 | 10:30–14:30 |
| Solape Londres–NY | 13:00–17:00 | 10:00–14:00 | 09:00–13:00 |

## Horarios por Tipo de Activo

| Activo | Horario UTC | Chile Verano (CLST) | Chile Invierno (CLT) |
|---|---|---|---|
| Crypto | 24/7 | 24/7 | 24/7 |
| Índices EE. UU. (mercado cash) | EDT: 13:30–20:00 / EST: 14:30–21:00 | CLST: 10:30–17:00 (EDT) / 11:30–18:00 (EST) | CLT: 09:30–16:00 (EDT) / 10:30–17:00 (EST) |
| Commodities EE. UU. | EDT: 13:00–21:00 / EST: 14:00–22:00 | CLST: 10:00–18:00 (EDT) / 11:00–19:00 (EST) | CLT: 09:00–17:00 (EDT) / 10:00–18:00 (EST) |

### Ventanas específicas por activo (UTC)

- Índices (EU/US):
  - EU Open (DAX/UK100): 07:00–09:00
  - US Cash (NYSE/NASDAQ): 14:30–21:00
  - Solape EU–US: 13:00–17:00
- Oro (XAU):
  - Alta actividad: 13:30–16:00
  - Fijación Londres AM: 10:30–11:00
  - Fijación Londres PM: 15:00–15:30
- Petróleo WTI (CL):
  - Alta actividad: 14:00–18:00
  - Inventarios EIA (miércoles): 14:30–16:30
- Agrícolas (CBOT día): 13:30–18:30

## Observaciones

- Los horarios “cruza medianoche” implican que el rango se divide en dos tramos al observarse en hora local de Chile.
- La ejecución real del bot considera además filtros de coherencia, calidad y riesgo; estos horarios reflejan ventanas potenciales, no garantías de trade.
- En fin de semana, el perfil `SCALPING` puede operar crypto con parámetros ajustados según `SCALPING_WEEKEND_TRADING`.
- El bot tiene Forex deshabilitado por defecto y no lo incluye en resúmenes ni selección de símbolos.
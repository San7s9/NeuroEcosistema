# Resumen de resultados (generado por experimentos.py)

Semillas de prueba: [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009]. Cada celda: media ± desviación estándar entre las 10 repeticiones. Tiempos en pasos de simulación ('—' = no hubo capturas en ninguna repetición).

## Presas (rival fijo: depredadores de reglas)

| Escenario | Condición | Vida media (fracción) | Supervivencia final | Comida total | Muertes por hambre | Capturas sufridas | Energía final presas |
|---|---|---|---|---|---|---|---|
| (a) Abundancia | Red 16×16 entrenada | 0.422 ± 0.061 | 0.013 ± 0.028 | 8.8 ± 2.8 | 10.1 ± 2.2 | 4.7 ± 2.5 | 0.074 ± 0.184 |
| (a) Abundancia | Red 4×4 entrenada | 0.584 ± 0.052 | 0.180 ± 0.118 | 27.0 ± 4.6 | 7.2 ± 2.5 | 5.1 ± 2.0 | 0.262 ± 0.203 |
| (a) Abundancia | Red sin entrenar | 0.345 ± 0.070 | 0.000 ± 0.000 | 3.9 ± 1.5 | 6.3 ± 3.7 | 8.7 ± 3.7 | 0.000 ± 0.000 |
| (a) Abundancia | Reglas | 0.603 ± 0.043 | 0.167 ± 0.072 | 71.4 ± 18.6 | 9.6 ± 1.6 | 2.9 ± 1.4 | 0.572 ± 0.224 |
| (a) Abundancia | Aleatoria | 0.337 ± 0.094 | 0.007 ± 0.021 | 8.2 ± 3.7 | 6.4 ± 3.5 | 8.5 ± 3.7 | 0.030 ± 0.096 |
| (a) Abundancia | Red 16×16 sin ver depredadores | 0.396 ± 0.097 | 0.033 ± 0.047 | 22.9 ± 7.4 | 5.5 ± 3.2 | 9.0 ± 3.0 | 0.207 ± 0.292 |
| (a) Abundancia | Red 16×16 con σ = 0.04 | 0.605 ± 0.082 | 0.220 ± 0.122 | 27.5 ± 6.6 | 6.9 ± 2.5 | 4.8 ± 3.0 | 0.433 ± 0.184 |
| (b) Escasez | Red 16×16 entrenada | 0.347 ± 0.059 | 0.000 ± 0.000 | 2.5 ± 1.7 | 9.7 ± 2.4 | 5.3 ± 2.4 | 0.000 ± 0.000 |
| (b) Escasez | Red 4×4 entrenada | 0.395 ± 0.054 | 0.007 ± 0.021 | 7.1 ± 2.3 | 9.7 ± 2.5 | 5.2 ± 2.6 | 0.007 ± 0.022 |
| (b) Escasez | Red sin entrenar | 0.322 ± 0.070 | 0.000 ± 0.000 | 1.0 ± 0.7 | 7.0 ± 3.9 | 8.0 ± 3.9 | 0.000 ± 0.000 |
| (b) Escasez | Reglas | 0.468 ± 0.034 | 0.033 ± 0.035 | 14.4 ± 4.1 | 12.3 ± 1.6 | 2.2 ± 1.4 | 0.155 ± 0.192 |
| (b) Escasez | Aleatoria | 0.296 ± 0.064 | 0.000 ± 0.000 | 2.2 ± 2.0 | 7.1 ± 3.4 | 7.9 ± 3.4 | 0.000 ± 0.000 |
| (b) Escasez | Red 16×16 sin ver depredadores | 0.303 ± 0.040 | 0.000 ± 0.000 | 8.2 ± 2.8 | 8.3 ± 2.4 | 6.7 ± 2.4 | 0.000 ± 0.000 |
| (b) Escasez | Red 16×16 con σ = 0.04 | 0.436 ± 0.054 | 0.033 ± 0.047 | 9.1 ± 3.5 | 10.4 ± 2.7 | 4.1 ± 2.5 | 0.126 ± 0.202 |
| (c) Presión | Red 16×16 entrenada | 0.282 ± 0.058 | 0.007 ± 0.021 | 7.4 ± 3.1 | 5.6 ± 2.7 | 9.3 ± 2.6 | 0.001 ± 0.004 |
| (c) Presión | Red 4×4 entrenada | 0.361 ± 0.049 | 0.073 ± 0.058 | 16.8 ± 4.9 | 4.1 ± 2.3 | 9.8 ± 2.0 | 0.382 ± 0.359 |
| (c) Presión | Red sin entrenar | 0.172 ± 0.034 | 0.000 ± 0.000 | 2.9 ± 1.9 | 1.1 ± 0.9 | 13.9 ± 0.9 | 0.000 ± 0.000 |
| (c) Presión | Reglas | 0.356 ± 0.042 | 0.007 ± 0.021 | 15.2 ± 4.9 | 9.5 ± 3.0 | 5.4 ± 2.9 | 0.011 ± 0.035 |
| (c) Presión | Aleatoria | 0.194 ± 0.052 | 0.007 ± 0.021 | 5.4 ± 2.5 | 2.5 ± 1.6 | 12.4 ± 1.6 | 0.036 ± 0.115 |
| (c) Presión | Red 16×16 sin ver depredadores | 0.223 ± 0.053 | 0.007 ± 0.021 | 11.5 ± 4.2 | 2.5 ± 2.1 | 12.4 ± 2.3 | 0.019 ± 0.061 |
| (c) Presión | Red 16×16 con σ = 0.04 | 0.388 ± 0.055 | 0.093 ± 0.056 | 14.3 ± 3.2 | 3.9 ± 1.9 | 9.7 ± 2.2 | 0.256 ± 0.173 |

### Pruebas pareadas sobre la vida media de las presas

| Escenario | Comparación | Diferencia media | p (permutación pareada) |
|---|---|---|---|
| (a) Abundancia | Red 16×16 entrenada − Red sin entrenar | +0.077 | 0.0056 |
| (a) Abundancia | Red 16×16 entrenada − Red 4×4 entrenada | -0.162 | 0.0021 |
| (a) Abundancia | Red 16×16 entrenada − Reglas | -0.182 | 0.0021 |
| (a) Abundancia | Red 4×4 entrenada − Reglas | -0.020 | 0.1777 |
| (a) Abundancia | Red 16×16 entrenada − Aleatoria | +0.085 | 0.0090 |
| (a) Abundancia | Red 4×4 entrenada − Aleatoria | +0.247 | 0.0021 |
| (a) Abundancia | Red 16×16 entrenada − Red 16×16 sin ver depredadores | +0.026 | 0.4233 |
| (a) Abundancia | Red 16×16 con σ = 0.04 − Red 16×16 entrenada | +0.183 | 0.0021 |
| (a) Abundancia | Red 16×16 con σ = 0.04 − Red 4×4 entrenada | +0.021 | 0.4426 |
| (a) Abundancia | Red 16×16 con σ = 0.04 − Reglas | +0.001 | 0.9672 |
| (b) Escasez | Red 16×16 entrenada − Red sin entrenar | +0.025 | 0.2644 |
| (b) Escasez | Red 16×16 entrenada − Red 4×4 entrenada | -0.048 | 0.1249 |
| (b) Escasez | Red 16×16 entrenada − Reglas | -0.121 | 0.0021 |
| (b) Escasez | Red 4×4 entrenada − Reglas | -0.073 | 0.0061 |
| (b) Escasez | Red 16×16 entrenada − Aleatoria | +0.051 | 0.0146 |
| (b) Escasez | Red 4×4 entrenada − Aleatoria | +0.099 | 0.0055 |
| (b) Escasez | Red 16×16 entrenada − Red 16×16 sin ver depredadores | +0.044 | 0.0605 |
| (b) Escasez | Red 16×16 con σ = 0.04 − Red 16×16 entrenada | +0.089 | 0.0042 |
| (b) Escasez | Red 16×16 con σ = 0.04 − Red 4×4 entrenada | +0.041 | 0.0450 |
| (b) Escasez | Red 16×16 con σ = 0.04 − Reglas | -0.032 | 0.1339 |
| (c) Presión | Red 16×16 entrenada − Red sin entrenar | +0.110 | 0.0037 |
| (c) Presión | Red 16×16 entrenada − Red 4×4 entrenada | -0.079 | 0.0140 |
| (c) Presión | Red 16×16 entrenada − Reglas | -0.074 | 0.0040 |
| (c) Presión | Red 4×4 entrenada − Reglas | +0.006 | 0.8056 |
| (c) Presión | Red 16×16 entrenada − Aleatoria | +0.088 | 0.0037 |
| (c) Presión | Red 4×4 entrenada − Aleatoria | +0.167 | 0.0021 |
| (c) Presión | Red 16×16 entrenada − Red 16×16 sin ver depredadores | +0.059 | 0.0371 |
| (c) Presión | Red 16×16 con σ = 0.04 − Red 16×16 entrenada | +0.106 | 0.0021 |
| (c) Presión | Red 16×16 con σ = 0.04 − Red 4×4 entrenada | +0.027 | 0.1639 |
| (c) Presión | Red 16×16 con σ = 0.04 − Reglas | +0.032 | 0.0974 |

## Depredadores (rival fijo: presas de reglas)

| Escenario | Condición | Capturas | Paso 1.ª captura | Paso medio de captura | Energía final depr. | Depr. muertos de hambre | Vida media presas |
|---|---|---|---|---|---|---|---|
| (a) Abundancia | Red 16×16 entrenada | 1.1 ± 1.1 | 129.8 ± 60.9 | 160.2 ± 66.8 | 0.000 ± 0.000 | 2.0 ± 0.0 | 0.690 ± 0.072 |
| (a) Abundancia | Red 4×4 entrenada | 1.5 ± 1.2 | 100.0 ± 38.5 | 153.6 ± 27.9 | 0.000 ± 0.000 | 2.0 ± 0.0 | 0.657 ± 0.060 |
| (a) Abundancia | Red sin entrenar | 0.0 ± 0.0 | — | — | 0.002 ± 0.007 | 1.9 ± 0.3 | 0.679 ± 0.066 |
| (a) Abundancia | Reglas | 2.9 ± 1.4 | 86.6 ± 79.3 | 164.2 ± 85.1 | 0.035 ± 0.111 | 1.9 ± 0.3 | 0.603 ± 0.043 |
| (a) Abundancia | Aleatoria | 0.0 ± 0.0 | — | — | 0.000 ± 0.000 | 2.0 ± 0.0 | 0.706 ± 0.066 |
| (b) Escasez | Red 16×16 entrenada | 1.2 ± 0.8 | 130.6 ± 51.5 | 141.2 ± 52.7 | 0.000 ± 0.000 | 2.0 ± 0.0 | 0.512 ± 0.033 |
| (b) Escasez | Red 4×4 entrenada | 1.1 ± 0.9 | 99.9 ± 38.2 | 132.5 ± 27.5 | 0.000 ± 0.000 | 2.0 ± 0.0 | 0.544 ± 0.044 |
| (b) Escasez | Red sin entrenar | 0.0 ± 0.0 | — | — | 0.054 ± 0.100 | 1.3 ± 0.9 | 0.538 ± 0.055 |
| (b) Escasez | Reglas | 2.2 ± 1.4 | 65.0 ± 42.7 | 100.8 ± 51.7 | 0.044 ± 0.094 | 1.8 ± 0.4 | 0.468 ± 0.034 |
| (b) Escasez | Aleatoria | 0.0 ± 0.0 | — | — | 0.000 ± 0.000 | 2.0 ± 0.0 | 0.546 ± 0.044 |
| (c) Presión | Red 16×16 entrenada | 1.8 ± 1.5 | 105.5 ± 62.3 | 143.9 ± 52.3 | 0.034 ± 0.072 | 4.8 ± 0.4 | 0.424 ± 0.035 |
| (c) Presión | Red 4×4 entrenada | 1.6 ± 1.3 | 124.5 ± 57.8 | 139.5 ± 77.6 | 0.037 ± 0.081 | 4.6 ± 1.0 | 0.436 ± 0.055 |
| (c) Presión | Red sin entrenar | 0.1 ± 0.3 | 41.0 ± 0.0 | 41.0 ± 0.0 | 0.148 ± 0.119 | 1.4 ± 1.8 | 0.446 ± 0.032 |
| (c) Presión | Reglas | 5.4 ± 2.9 | 56.0 ± 52.0 | 156.1 ± 57.4 | 0.371 ± 0.244 | 2.9 ± 1.4 | 0.356 ± 0.042 |
| (c) Presión | Aleatoria | 0.1 ± 0.3 | 67.0 ± 0.0 | 67.0 ± 0.0 | 0.000 ± 0.000 | 5.0 ± 0.0 | 0.467 ± 0.041 |

### Pruebas pareadas sobre las capturas

| Escenario | Comparación | Diferencia media | p (permutación pareada) |
|---|---|---|---|
| (a) Abundancia | Red 16×16 entrenada − Red sin entrenar | +1.100 | 0.0332 |
| (a) Abundancia | Red 16×16 entrenada − Red 4×4 entrenada | -0.400 | 0.4986 |
| (a) Abundancia | Red 16×16 entrenada − Reglas | -1.800 | 0.0154 |
| (a) Abundancia | Red 4×4 entrenada − Reglas | -1.400 | 0.0751 |
| (a) Abundancia | Red 16×16 entrenada − Aleatoria | +1.100 | 0.0332 |
| (a) Abundancia | Red 4×4 entrenada − Aleatoria | +1.500 | 0.0151 |
| (b) Escasez | Red 16×16 entrenada − Red sin entrenar | +1.200 | 0.0080 |
| (b) Escasez | Red 16×16 entrenada − Red 4×4 entrenada | +0.100 | 1.0000 |
| (b) Escasez | Red 16×16 entrenada − Reglas | -1.000 | 0.0725 |
| (b) Escasez | Red 4×4 entrenada − Reglas | -1.100 | 0.0955 |
| (b) Escasez | Red 16×16 entrenada − Aleatoria | +1.200 | 0.0080 |
| (b) Escasez | Red 4×4 entrenada − Aleatoria | +1.100 | 0.0151 |
| (c) Presión | Red 16×16 entrenada − Red sin entrenar | +1.700 | 0.0084 |
| (c) Presión | Red 16×16 entrenada − Red 4×4 entrenada | +0.200 | 0.8432 |
| (c) Presión | Red 16×16 entrenada − Reglas | -3.600 | 0.0057 |
| (c) Presión | Red 4×4 entrenada − Reglas | -3.800 | 0.0120 |
| (c) Presión | Red 16×16 entrenada − Aleatoria | +1.700 | 0.0084 |
| (c) Presión | Red 4×4 entrenada − Aleatoria | +1.500 | 0.0043 |

## Ecosistema completo (observación adicional)

| Escenario | Condición | Vida media presas | Comida total | Capturas | Depr. muertos de hambre |
|---|---|---|---|---|---|
| (a) Abundancia | Redes vs redes | 0.499 ± 0.075 | 11.4 ± 4.7 | 1.4 ± 1.6 | 2.0 ± 0.0 |
| (a) Abundancia | Reglas vs reglas | 0.603 ± 0.043 | 71.4 ± 18.6 | 2.9 ± 1.4 | 1.9 ± 0.3 |
| (b) Escasez | Redes vs redes | 0.401 ± 0.044 | 3.4 ± 1.8 | 0.7 ± 0.8 | 1.9 ± 0.3 |
| (b) Escasez | Reglas vs reglas | 0.468 ± 0.034 | 14.4 ± 4.1 | 2.2 ± 1.4 | 1.8 ± 0.4 |
| (c) Presión | Redes vs redes | 0.414 ± 0.052 | 9.6 ± 4.5 | 2.7 ± 2.8 | 5.0 ± 0.0 |
| (c) Presión | Reglas vs reglas | 0.356 ± 0.042 | 15.2 ± 4.9 | 5.4 ± 2.9 | 2.9 ± 1.4 |

## Comportamiento: ¿búsqueda, persecución y evasión?

Coseno entre la acción y la dirección del objetivo visible (+1 = directo hacia él, −1 = directo en contra, 0 = de lado). Promedio de todos los pasos de los 3 escenarios y las 10 semillas de prueba. Rapidez = longitud de la acción (1 = velocidad máxima).

| Presa | Rapidez sin amenaza | Rapidez viendo depredador | Búsqueda (hacia planta) | Evasión (lejos del depredador) |
|---|---|---|---|---|
| Red 16×16 entrenada | 0.40 | 0.96 | -0.15 | +0.40 |
| Red 4×4 entrenada | 0.37 | 0.85 | +0.42 | +0.42 |
| Red 16×16 con σ = 0.04 | 0.32 | 0.96 | +0.39 | +0.45 |
| Red sin entrenar | 0.33 | 0.38 | -0.27 | +0.10 |
| Reglas | 0.73 | 1.00 | +0.51 | +0.71 |
| Aleatoria | 0.60 | 0.60 | -0.01 | +0.05 |

| Depredador | Rapidez media | Persecución (hacia la presa) |
|---|---|---|
| Red 16×16 entrenada | 0.98 | +0.30 |
| Red 4×4 entrenada | 0.93 | +0.27 |
| Red sin entrenar | 0.35 | -0.10 |
| Reglas | 0.79 | +0.82 |
| Aleatoria | 0.60 | +0.08 |

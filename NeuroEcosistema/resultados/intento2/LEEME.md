# Intento 2 (descartado): metabolismo corregido, pero solo 100 generaciones

Configuración igual a la final excepto `generaciones = 100` (final: 250).
Evaluación con semillas 1000-1009 (rival de reglas).

## Presa 16x16 (rival: depredadores de reglas)

| Escenario | Condición | Vida media | Comida total | Capturas |
|---|---|---|---|---|
| (a) Abundancia | Red entrenada | 0.475 | 14.8 | 6.0 |
| (a) Abundancia | Reglas | 0.603 | 71.4 | 2.9 |
| (a) Abundancia | Red sin entrenar | 0.345 | 3.9 | 8.7 |
| (b) Escasez | Red entrenada | 0.378 | 6.1 | 5.1 |
| (b) Escasez | Reglas | 0.468 | 14.4 | 2.2 |
| (b) Escasez | Red sin entrenar | 0.322 | 1.0 | 8.0 |
| (c) Presión | Red entrenada | 0.343 | 13.3 | 9.3 |
| (c) Presión | Reglas | 0.356 | 15.2 | 5.4 |
| (c) Presión | Red sin entrenar | 0.172 | 2.9 | 13.9 |

## Depredador 16x16 (rival: presas de reglas)

| Escenario | Condición | Capturas | Depredadores muertos de hambre |
|---|---|---|---|
| (a) Abundancia | Red entrenada | 0.9 | 2.0 |
| (a) Abundancia | Reglas | 2.9 | 1.9 |
| (a) Abundancia | Red sin entrenar | 0.0 | 1.9 |
| (b) Escasez | Red entrenada | 0.2 | 2.0 |
| (b) Escasez | Reglas | 2.2 | 1.8 |
| (c) Presión | Red entrenada | 2.0 | 5.0 |
| (c) Presión | Reglas | 5.4 | 2.9 |

Diagnóstico del depredador (escenario a): rapidez media 1.00 (siempre al máximo) y
alineación con la dirección de la presa visible (coseno) 0.30, contra 0.80 y 0.88 de las reglas.
No aprendió a orientarse hacia la presa.

Curvas: la aptitud media seguía subiendo en la generación 100 (presa: 0.262 -> 0.361 por
bloques de 20 generaciones; depredador: 0.038 -> 0.209). El mejor depredador llegaba a 0.77
en entrenamiento pero 0.375 en validación: los campeones con pocas generaciones dependen de
la suerte de sus 2 mapas. Decisión: entrenar 250 generaciones (ver BITACORA, decisión 5).

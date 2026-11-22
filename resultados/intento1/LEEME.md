# Intento 1 (descartado): la presa aprende a ahorrar energía en vez de comer

Configuración igual a la final, excepto `presa_costo_base = 0.0010` (final: 0.0016) y 60 generaciones (final: 100).
Con ese metabolismo una presa QUIETA sobrevive 0.7 / 0.0010 = 700 de los 800 pasos sin comer.

Evaluación del campeón (`presa_16x16.npz` de esta carpeta) con semillas 1000-1009, rival = depredadores de reglas:

| Escenario | Condición | Vida media | Comida total | Capturas | Muertes por hambre |
|---|---|---|---|---|---|
| (a) Abundancia | Red entrenada | 0.572 | 13.7 | 5.0 | 7.8 |
| (a) Abundancia | Reglas | 0.697 | 74.0 | 2.9 | 7.7 |
| (a) Abundancia | Red sin entrenar | 0.434 | 3.9 | 10.1 | 4.2 |
| (b) Escasez | Red entrenada | 0.482 | 5.0 | 4.4 | 10.3 |
| (b) Escasez | Reglas | 0.618 | 17.7 | 2.4 | 9.9 |
| (b) Escasez | Red sin entrenar | 0.432 | 1.2 | 9.5 | 5.2 |
| (c) Presión | Red entrenada | 0.320 | 8.7 | 10.9 | 3.6 |
| (c) Presión | Reglas | 0.447 | 16.1 | 5.6 | 9.1 |
| (c) Presión | Red sin entrenar | 0.195 | 2.9 | 13.9 | 0.9 |

Rapidez media de la presa entrenada (escenario a): 0.40 en general y 0.98 cuando ve un depredador
(reglas: 0.81 y 1.00). Conclusión: aprendió a HUIR pero no a BUSCAR comida, porque la aptitud
(vida + 0.02 x comida) se podía maximizar casi sin comer. Ver BITACORA, decisión 4.

# Pruebas exploratorias de la aptitud (una sola corrida, 40 generaciones)

Estas pruebas se hicieron con la configuración del intento 2 para decidir si cambiar el
criterio de aptitud. Son evidencia débil (una sola semilla de entrenamiento y menos
generaciones), por eso NO se adoptaron. Se evaluaron con las semillas 1000-1009.

## Presa con más peso para la comida (PESO_COMIDA 0.02 -> 0.10)

| Escenario | Vida media | Comida total | Capturas | Referencia (intento 2, peso 0.02, 100 gen.) |
|---|---|---|---|---|
| (a) Abundancia | 0.502 | 19.6 | 5.4 | 0.475 / 14.8 / 6.0 |
| (b) Escasez | 0.373 | 6.8 | 4.9 | 0.378 / 6.1 / 5.1 |
| (c) Presión | 0.347 | 13.8 | 9.4 | 0.343 / 13.3 / 9.3 |

Mejora pequeña e inconsistente: no justifica cambiar el criterio.

## Depredador con moldeado de recompensa (PESO_PERSECUCION 0 -> 0.5)

Premio extra por la cercanía media a la presa más cercana durante el episodio.

| Escenario | Capturas | Depredadores muertos de hambre | Referencia (intento 2, sin moldeado, 100 gen.) |
|---|---|---|---|
| (a) Abundancia | 0.7 | 2.0 | 0.9 |
| (b) Escasez | 0.7 | 2.0 | 0.2 |
| (c) Presión | 0.5 | 5.0 | 2.0 |

No mejora: el premio por "estar cerca" se puede obtener sin capturar (riesgo de comportamiento
favorecido indebidamente). Se dejó el parámetro en 0 (desactivado) pero el código se conserva
en `evolucion.py` para poder repetir la prueba.

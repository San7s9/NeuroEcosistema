# Bitácora de decisiones técnicas

Cada decisión indica el problema, las alternativas consideradas, la evidencia disponible y el criterio de selección. Las cifras salen de `resultados/resumen.md` (semillas de prueba 1000–1009) y de las carpetas `resultados/intento1` e `intento2`. "Vida media" es la fracción del episodio de 800 pasos que vive en promedio una presa.

---

## D1. Qué percibe cada agente (representación del entorno)

**Problema.** La red necesita una entrada de tamaño fijo, aunque el número de plantas, presas y depredadores cambia en cada escenario y con el tiempo.

**Decisión.** Cada agente percibe solo **el objeto más cercano de cada tipo** dentro de su radio de visión, en coordenadas relativas y normalizadas: `(dx/visión, dy/visión, cercanía = 1 − d/visión)`. Además recibe su **energía** y su **posición normalizada**, para saber dónde están las paredes.
* Presa (12 entradas): planta, depredador, obstáculo, energía y posición.
* Depredador (11 entradas): presa, **velocidad de esa presa**, obstáculo, energía y posición. No ve plantas porque no las come.

| Alternativa | Por qué se descartó |
|---|---|
| Ver el mapa completo como una rejilla de píxeles | Muchas entradas (miles), haría necesaria una red convolucional y aumentaría mucho el espacio de búsqueda de la neuroevolución. |
| Ver a los k objetos más cercanos de cada tipo | Más entradas y parámetros; con 1 vecino ya hay información suficiente para buscar, perseguir y huir. Queda como mejora (ver D9). |
| Coordenadas absolutas de los objetivos | La red tendría que aprender a restar posiciones; las relativas ya le dan la dirección. |
| Rumbo propio y velocidad propia | El movimiento no tiene inercia (la acción es la velocidad), así que no aportan información. |

**Variables excluidas a propósito:** segundo vecino más cercano, plantas para el depredador, energía de los demás agentes e identidad de los agentes.

**Evidencia (E4).** Una presa 16×16 entrenada **sin ver depredadores** (entradas 3–5 forzadas a 0) come más (22.9 contra 8.8 plantas en (a)), pero sufre casi el doble de capturas (9.0 contra 4.7). En (c) vive significativamente menos (0.223 contra 0.282, p = 0.037). En (a) la diferencia no es significativa (p = 0.42), porque hay pocos depredadores y lo que gana comiendo compensa lo que pierde por capturas. **Conclusión:** el sensor de depredador es útil exactamente donde hay presión de depredación.

**Criterio.** Mínima información suficiente para las tres conductas pedidas (búsqueda, persecución y evasión), con el mismo número de entradas en todos los escenarios. Las reglas de referencia usan **las mismas** observaciones para que la comparación sea justa.

---

## D2. Qué decide la red (salida y acción)

**Decisión.** Dos salidas con `tanh` que forman un vector de movimiento (x, y) en [−1, 1]². Su longitud se limita a 1 y se multiplica por la velocidad máxima. El costo de energía crece con el **cuadrado** de la rapidez.

| Alternativa | Por qué se descartó |
|---|---|
| Acciones discretas (8 direcciones con Softmax, como en Neurito 1) | No permite elegir la rapidez y, con eso, administrar la energía. |
| Rumbo + rapidez (2 salidas polares) | Discontinuidad del ángulo en ±180°: dos salidas muy distintas significan casi lo mismo. |

**Evidencia.** El control de la rapidez se usa de verdad. Las presas entrenadas caminan a 0.32–0.40 de su velocidad máxima cuando no hay amenaza y suben a 0.85–0.96 cuando ven un depredador (tabla de comportamiento). Sin salida continua, esa estrategia de ahorro de energía no sería posible.

---

## D3. Arquitectura de las redes

**Decisión.** Perceptrón multicapa entradas → 16 → 16 → 2, con `tanh` en todas las capas e inicialización tipo Xavier. Presa: 514 parámetros; depredador: 498. Alternativa evaluada: 4 → 4 (82 y 78 parámetros).

**Justificación previa.** Se piden dos capas ocultas. La presa debe combinar objetivos en conflicto (comer y huir, cerca de paredes u obstáculos): la primera capa puede detectar situaciones y la segunda combinarlas. Se eligió `tanh` y no ReLU porque es centrada en 0 y no deja neuronas "muertas" con pesos aleatorios. En la neuroevolución no hay gradientes, así que la saturación de `tanh` no frena el aprendizaje.

**Evidencia (E2), contraria a lo esperado.** Con el mismo presupuesto (250 generaciones, σ = 0.10), la red **pequeña 4×4 fue mejor** para la presa: 0.584 contra 0.422 en (a) (p = 0.002) y 0.361 contra 0.282 en (c) (p = 0.014). En los depredadores no hubo diferencia significativa (p ≥ 0.50). La tabla de comportamiento muestra la causa: la 16×16 **no aprendió a buscar comida** (coseno hacia la planta −0.15), mientras que la 4×4 sí (+0.42).

**Interpretación.** El problema no es la capacidad de la red, sino la **búsqueda**: ver D5 y E5. Al corregir la mutación (σ = 0.04), la 16×16 alcanza a la 4×4 (0.605 contra 0.584 en (a), p = 0.44). **Se mantiene 16×16 como arquitectura principal**, porque con un entrenamiento adecuado rinde igual o mejor y deja margen para entradas adicionales (D9).

---

## D4. Criterio que se optimiza (aptitud) y metabolismo de las presas

**Decisión final.**
* Presa: `vida media + 0.02 × plantas comidas por presa`.
* Depredador: `capturas por depredador + 0.3 × energía final media`.
* Metabolismo basal de la presa: **0.0016** por paso.

**Intento 1 (fallido, `resultados/intento1`).** Con un metabolismo de 0.0010, una presa *quieta* vivía 0.7 / 0.0010 = 700 de los 800 pasos sin comer. La red aprendió a **moverse despacio (rapidez 0.40) y huir a máxima velocidad (0.98) al ver un depredador, pero casi no comía** (13.7 plantas contra 74.0 de las reglas en (a)). La aptitud se podía maximizar ahorrando energía: un **comportamiento favorecido indebidamente**. Corrección: metabolismo de 0.0016, con el que una presa quieta solo aguanta ~437 pasos (55 % del episodio). Comer pasa a ser necesario.

**Alternativas probadas (`resultados/exploraciones.md`, 40 generaciones, una corrida):**

| Alternativa | Resultado | Decisión |
|---|---|---|
| Subir el peso de la comida a 0.10 | Mejora pequeña e inconsistente (vida en (a) 0.502 contra 0.475; en (b) 0.373 contra 0.378) | No se adoptó |
| Moldeado de recompensa del depredador: +0.5 × cercanía media a la presa | Empeoró (capturas en (c) 0.5 contra 2.0); se puede "ganar" acercándose sin capturar | No se adoptó (parámetro `PESO_PERSECUCION = 0`) |

**Qué podría favorecer indebidamente el criterio final:** que la presa se esconda en esquinas (el depredador tiene menos ángulos de ataque), que el depredador corra siempre al máximo apostando a capturas rápidas aunque muera de hambre (es lo que se observa: rapidez 0.93–0.98) o que espere quieto. El término de energía (0.3) no bastó para corregir lo segundo (ver D9).

---

## D5. Método de entrenamiento: neuroevolución y sus parámetros

**Decisión.** Algoritmo genético sobre los pesos: población de 32, 2 mapas por genoma (los mismos para toda la generación), elitismo de 4, torneo de 3, cruce uniforme (50 %), mutación gaussiana `w += N(0, σ)` y elección final del campeón entre los 5 mejores en 8 mapas de **validación**.

| Alternativa | Por qué se descartó |
|---|---|
| Aprendizaje supervisado (como en Neurito) | No hay "acción correcta" por paso. Imitar a las reglas limitaría la red a copiarlas, nunca superarlas. |
| Aprendizaje por refuerzo con gradiente (REINFORCE, PPO) | Más complejo de implementar sin bibliotecas y de explicar; la recompensa es escasa y retardada. |
| Coevolución de presas y depredadores | Ver D6. |

**Evidencia sobre el número de generaciones.** Con 60 y con 100 generaciones (`intento2`), la aptitud media de la población **seguía subiendo**. El mejor depredador llegaba a 0.77 en entrenamiento pero solo 0.375 en validación: con pocas generaciones, los campeones dependían de la suerte de sus 2 mapas. Se subió a **250 generaciones** (~15 min por modelo).

**Evidencia sobre σ (E5).** Con σ = 0.10, la mutación mueve a la red 16×16 una distancia esperada de 0.10·√514 ≈ 2.3, frente a 0.10·√82 ≈ 0.9 en la 4×4. Con **σ = 0.04** (0.04·√514 ≈ 0.9, igual que la 4×4), la presa 16×16 mejoró en los tres escenarios: (a) 0.605 contra 0.422, p = 0.002; (b) 0.436 contra 0.347, p = 0.004; (c) 0.388 contra 0.282, p = 0.002. Además aprendió a buscar comida (coseno +0.39).

**Evidencia de que los pesos cambian.** La distancia entre el mejor genoma inicial y el campeón es |Δw| = 33.1 (presa 16×16) y 33.0 (depredador 16×16). La distribución de pesos pasa de concentrada en ±0.3 a extendida en ±4 (`figuras/pesos_antes_despues.png`). Ojo: parte de ese cambio es deriva por mutación acumulada. Que la red *aprendió* lo demuestra E1 (desempeño), no el tamaño de Δw.

---

## D6. Contra quién se entrena cada especie

**Decisión.** Cada especie se entrena contra la política de **reglas** de la otra, que queda fija.

| Alternativa | Ventaja | Por qué no |
|---|---|---|
| Coevolución (las dos especies evolucionan a la vez) | Más realista; carrera armamentista | El objetivo de cada una cambia todo el tiempo, las curvas no son interpretables (aptitud relativa) y es difícil saber si una mejora es real o el rival empeoró. |
| Entrenar contra el rival aleatorio | Fácil | El rival aleatorio no persigue ni huye: no enseña a evadir ni a perseguir. |

**Evidencia.** Con rival fijo, la curva de aptitud mide progreso real (`figuras/entrenamiento.png`). Costo: en el ecosistema completo (redes contra redes), la interacción entre dos especies que nunca se vieron produce resultados distintos a los de cada experimento por separado. En (c) las presas viven más con redes contra redes (0.414) que con reglas contra reglas (0.356), porque los depredadores neuronales capturan menos (2.7 contra 5.4). En (a) y (b) pasa lo contrario: las presas neuronales comen muy poco (11.4 contra 71.4 plantas en (a)).

---

## D7. Escenarios y equilibrio del mundo

**Decisión.** Las 15 presas, la física y los costos se mantienen constantes. Solo cambian la población de depredadores, las plantas y los obstáculos:

| Escenario | Depredadores | Plantas | Rebrote por paso | Obstáculos |
|---|---|---|---|---|
| Entrenamiento | 3 | 35 | 0.015 | 2 |
| (a) Abundancia | 2 | 45 | 0.020 | 0 |
| (b) Escasez | 2 | 12 | 0.004 | 0 |
| (c) Presión | 5 | 45 | 0.020 | 4 |

El escenario de entrenamiento es **intermedio** y distinto de los tres de evaluación, para medir generalización y no memorización.

**Evidencia del ajuste.** En la primera calibración (con agentes de reglas), casi todos morían de hambre incluso en abundancia (11.3 de 15 presas en el escenario de entrenamiento), así que la evasión no importaba. Se bajaron los costos de movimiento. Con la calibración final, los escenarios producen diferencias medibles: con reglas contra reglas, la vida media es 0.603 en (a), 0.468 en (b) y 0.356 en (c). En (b) domina el hambre (12.3 muertes) y en (c) las capturas (5.4).

**Limitación reconocida.** Los depredadores mueren de hambre en casi todas las condiciones, incluso con reglas (1.9 de 2 en (a)). Un depredador a 2.3 px/paso solo gana 0.3 px/paso a una presa que huye a 2.0, y a velocidad máxima su energía (0.8) dura ~240 pasos. La persecución directa en campo abierto casi nunca se completa. Es la primera mejora propuesta (D9).

---

## D8. Diseño experimental y estadística

**Decisión.**
* Tres juegos de semillas separados: entrenamiento (generadas por la semilla 42), validación (500–507) y prueba (1000–1009).
* **Diseño pareado:** todas las condiciones se evalúan en los mismos 10 mapas. Cada mundo se genera solo con su semilla, así que el mapa 1000 es idéntico en todas las condiciones.
* **Una sola variable por comparación.** Al evaluar presas, el rival siempre son los depredadores de reglas, y al revés.
* Prueba de **permutación pareada** (cambio de signo, 20 000 permutaciones). No supone normalidad y es adecuada para n = 10.

| Alternativa | Por qué no |
|---|---|
| Prueba t | Supone normalidad; con 10 datos no se puede verificar. |
| Evaluar en las semillas de entrenamiento | Mediría memorización. |

**Evidencia.** Al ejecutar `experimentos.py` dos veces se obtiene un `resumen.md` idéntico byte a byte.

---

## D9. Qué modificaríamos primero (mejora con evidencia)

1. **Rebalancear la energía del depredador** (primera prioridad). Evidencia: muere de hambre en casi todas las condiciones (D7), corre a 0.93–0.98 de su velocidad máxima y su coseno de persecución es solo +0.30 (reglas: +0.82). Ni el término de energía ni el moldeado de recompensa lo corrigieron (D4). Propuesta: subir la energía por captura o bajar el costo de movimiento hasta que las reglas sobrevivan a la mitad de los episodios, y volver a entrenar.
2. **Ajustar σ al tamaño de la red** (ya probado en E5): usar σ = 0.04 para redes 16×16, o σ ∝ 1/√parámetros.
3. **Entrenar en varios escenarios a la vez.** La red generaliza peor a la escasez (b): incluso la mejor presa queda por debajo de las reglas en promedio (0.436 contra 0.468; diferencia no significativa, p = 0.13) y la red 4×4 pierde con significancia (p = 0.006). En el escenario de entrenamiento hay 35 plantas, y en (b) solo 12.
4. **Percibir 2 objetos de cada tipo**, para huir de dos depredadores a la vez en el escenario (c).

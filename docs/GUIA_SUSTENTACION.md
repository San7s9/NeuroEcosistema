# Guía de estudio para la sustentación

Esta guía explica **todo** el proyecto con palabras sencillas. La propuesta dice que en la sustentación te pueden pedir explicar una decisión, cambiar un parámetro en vivo, leer una gráfica o interpretar un comportamiento raro. Léela completa al menos una vez y practica las preguntas de la sección final.

---

## 1. La idea en una frase

Hay un mundo 2D con plantas, presas y depredadores. Cada agente tiene una **red neuronal** que recibe lo que el agente "ve" y devuelve **hacia dónde moverse**. Las redes empiezan con pesos al azar (se mueven sin sentido) y se **entrenan por neuroevolución**: se prueban muchas redes, se quedan las mejores y se generan nuevas copiándolas con pequeñas mutaciones. Al final medimos con experimentos si las redes entrenadas son mejores que redes sin entrenar, que agentes aleatorios y que agentes programados con reglas.

## 2. Relación con lo que ya hicimos en Neurito

| Neurito (actividades anteriores) | NeuroEcosistema (proyecto final) |
|---|---|
| Red 3 → 6 → 3 (una capa oculta) | Red 12 → 16 → 16 → 2 (dos capas ocultas) |
| Aprendizaje **supervisado**: etiquetas (comer/dormir/jugar, saltar/esperar) | **Neuroevolución**: no hay etiquetas, solo un puntaje al final del episodio |
| Retropropagación y descenso de gradiente | Selección, cruce y mutación de los pesos |
| Softmax / sigmoide para elegir una acción | `tanh` en la salida: un vector de movimiento (x, y) |
| Lección de Neurito 2.0: "precisión alta ≠ buen comportamiento en el juego" | Por eso aquí **no** medimos precisión: medimos directamente lo que importa (vivir, capturar) |

La última fila es la conexión más importante. En Neurito 2.0 vimos que una red con 86 % de precisión chocaba siempre, porque las etiquetas no eran la física del juego. En el ecosistema no existe una "respuesta correcta" en cada paso. Solo sabemos al final cuánto vivió la presa. Por eso usamos un método que optimiza directamente ese resultado.

## 3. Recorrido por el código

### `config.py`: todos los números en un lugar
Aquí están los tamaños, velocidades, costos de energía, los escenarios, la arquitectura de las redes, los parámetros del algoritmo genético y las semillas. **Si te piden "cambia un parámetro" en la sustentación, casi siempre es aquí.**

Valores clave que conviene recordar:
* Presas: velocidad máxima 2.0, visión 130 px, energía inicial 0.7, cada planta da +0.30.
* Depredadores: velocidad máxima 2.3 (**más rápidos**), visión 170 px, pero moverse rápido les cuesta más (0.0025 contra 0.0015 de la presa); cada captura da +0.45.
* El episodio dura como máximo 800 pasos.
* Escenarios: (a) 45 plantas y 2 depredadores; (b) 12 plantas que rebrotan muy lento; (c) 45 plantas, 5 depredadores y 4 obstáculos. Siempre hay 15 presas.

### `mundo.py`: la simulación
La clase `Mundo` simula **B mundos al mismo tiempo** con arreglos de NumPy. Por ejemplo, `presa_pos` tiene forma `(B, 15, 2)`: B mundos, 15 presas, coordenadas x e y. Esto permite evaluar 64 redes a la vez durante el entrenamiento.

Cada paso (`paso_simulacion`):
1. Las políticas devuelven un vector de movimiento por agente. Si su longitud pasa de 1, se recorta a 1.
2. **Movimiento:** `posición += vector × velocidad_máxima`. Las paredes y los obstáculos detienen al agente.
3. **Energía:** `energía -= costo_base + costo_mov × |vector|²`. Correr al máximo cuesta mucho más que caminar despacio. Esto obliga a **administrar la energía**.
4. **Comer:** si una presa está a menos de 9 px de una planta activa, se la come.
5. **Captura:** si un depredador está a menos de 11 px de una presa, la captura.
6. **Hambre:** quien llega a energía 0 muere.
7. **Rebrote:** las plantas comidas reaparecen en otro lugar con probabilidad `rebrote` por paso.
8. El episodio termina a los 800 pasos o cuando no quedan presas.

**Percepción (`observaciones_presas`):** 12 números por presa:
* planta más cercana: `dx/visión`, `dy/visión`, `cercanía = 1 - distancia/visión`;
* depredador más cercano: igual;
* obstáculo más cercano: dirección y cercanía;
* su energía;
* su posición normalizada en [-1, 1], para que sepa dónde están las paredes.

Si no ve nada dentro de su radio, ese grupo de entradas vale 0. Los depredadores (`observaciones_depredadores`) reciben 11 números: en lugar de ver plantas, ven la **velocidad de la presa más cercana**, que les sirve para anticipar hacia dónde va.

### `red.py`: la red neuronal
* `formas()` calcula el tamaño de cada matriz: 12×16, 16×16 y 16×2.
* Los pesos se guardan como un **vector plano** llamado *genoma* (514 números para la presa 16×16). Así el algoritmo genético puede mutarlo fácilmente.
* `desempacar()` convierte el genoma en las matrices W y los vectores b.
* `adelante()` calcula `a1 = tanh(X·W1 + b1)`, `a2 = tanh(a1·W2 + b2)` y `salida = tanh(a2·W3 + b3)`. Usa `einsum` para hacerlo con todos los mundos y agentes a la vez.
* Inicialización tipo Xavier: pesos ~ N(0, 1/√entradas) y sesgos en 0, para que las neuronas no se saturen al inicio.

Número de parámetros (pesos + sesgos):
* Presa 16×16: 12·16+16 + 16·16+16 + 16·2+2 = **514**.
* Depredador 16×16: 11·16+16 + 16·16+16 + 16·2+2 = **498**.
* Presa 4×4: 12·4+4 + 4·4+4 + 4·2+2 = **82**; depredador 4×4: **78**.

### `politicas.py`: quién decide
* `PoliticaNeuronal`: la decisión **sale de la red**. Esto demuestra la condición de aceptación ("las decisiones proceden de la salida de su red").
* `PoliticaReglasPresa`: si ve un depredador, huye en dirección contraria; si no, va a la planta más cercana; si no, deambula.
* `PoliticaReglasDepredador`: persigue a la presa más cercana apuntando a dónde estará (su posición + su velocidad × 8 pasos).
* `PoliticaAleatoria`: caminata al azar que mantiene el rumbo y lo cambia poco a poco.

**Importante:** las reglas usan **exactamente las mismas observaciones** que la red. Si las reglas tuvieran más información, la comparación no sería justa.

### `evolucion.py`: el entrenamiento
1. Se crean 32 genomas aleatorios (la población).
2. **Evaluación:** cada genoma controla a todos los agentes de su especie en 2 mapas. Los 32 genomas se prueban en los **mismos 2 mapas**, así la comparación entre ellos es justa. El rival siempre usa reglas.
3. **Aptitud (lo que se optimiza):**
   * Presa: `vida media (fracción de los 800 pasos) + 0.02 × plantas comidas por presa`.
   * Depredador: `capturas por depredador + 0.3 × energía final media`.
4. **Elitismo:** los 4 mejores pasan intactos a la siguiente generación.
5. **Torneo:** para elegir un padre se toman 3 genomas al azar y gana el de mayor aptitud.
6. **Cruce uniforme (50 %):** cada peso del hijo se copia de uno de los dos padres al azar.
7. **Mutación:** `w_hijo = w_padre + N(0, 0.1)`. **Así se modifican los pesos.**
8. Se repite durante 60 generaciones. Al final, los 5 mejores se re-evalúan en 8 mapas de validación y se queda el mejor (el *campeón*).

### `entrenar.py`, `experimentos.py` y `simulacion.py`
* `entrenar.py` guarda el modelo (`modelos/*.npz`), la aptitud por generación (`resultados/entrenamiento_*.csv`) y la configuración usada (`resultados/config_*.json`).
* `experimentos.py` corre todas las condiciones con las semillas de prueba 1000–1009, guarda los datos crudos, calcula media ± desviación, hace pruebas estadísticas y dibuja las gráficas.
* `simulacion.py` muestra todo en vivo. Al hacer clic en un agente se ven sus entradas, sus 32 neuronas ocultas (naranja = −1, azul = +1) y su salida (flecha naranja).

## 4. Conceptos que te pueden preguntar

**Pesos vs. sesgos.** Los pesos multiplican las entradas y dicen cuánto influye cada una. Los sesgos se suman y mueven el punto en que la neurona se activa. En el genoma están todos juntos y se mutan igual.

**¿Por qué tanh?** Porque la salida debe ser una dirección con signo: izquierda o derecha, arriba o abajo. `tanh` da valores en [−1, 1]. En las capas ocultas también usamos tanh porque es suave y centrada en 0, y con la neuroevolución no hay problema de gradientes que se desvanecen, porque no se calculan gradientes. Con ReLU, muchas neuronas podrían quedar "muertas" (siempre en 0) con pesos aleatorios.

**¿Por qué dos capas ocultas?** La propuesta lo exige. Además, la presa debe combinar objetivos que compiten: ir a la comida y alejarse del depredador al mismo tiempo, cerca de las paredes. La primera capa puede detectar situaciones ("depredador cerca", "planta a la derecha") y la segunda combinarlas.

**¿Por qué neuroevolución y no aprendizaje supervisado?** Para el aprendizaje supervisado necesitaríamos ejemplos de "la acción correcta" en cada situación, y no los tenemos. Si los tomáramos de las reglas, la red solo podría imitar a las reglas, nunca superarlas. La neuroevolución solo necesita un puntaje por episodio.

**¿Qué es una semilla?** Un número que inicializa el generador aleatorio. Con la misma semilla, el mapa inicial (posiciones de presas, depredadores, plantas y obstáculos) es idéntico. Así comparamos condiciones en los mismos 10 mapas.

**¿Por qué semillas distintas para entrenar, validar y probar?** Por la misma razón que en Neurito separábamos entrenamiento y prueba: si evaluamos en los mapas con los que se entrenó, podríamos medir memorización y no generalización.

**¿Qué es la prueba de permutación pareada?** Para cada semilla calculamos la diferencia entre dos condiciones (por ejemplo, red − reglas). Si de verdad no hubiera diferencia, el signo de cada diferencia sería cuestión de suerte. Entonces cambiamos los signos al azar 20 000 veces y vemos qué tan seguido sale una diferencia tan grande como la real. Ese porcentaje es el valor p. Si p < 0.05, la diferencia difícilmente es casualidad. No supone que los datos sean normales, y es apropiada porque solo hay 10 repeticiones.

---

## 5. La historia del proyecto (cuéntala así en la sustentación)

Esta historia es lo que más valora la rúbrica: decisiones, evidencia, fallos y mejoras.

1. **Calibramos el mundo con agentes de reglas.** En la primera versión casi todos morían de hambre, incluso con mucha comida (11.3 de 15 presas), así que huir no servía de nada. Bajamos los costos de movimiento hasta que los tres escenarios mostraron diferencias claras.
2. **Intento 1: la presa aprendió a "hacerse la muerta".** Entrenamos y la presa vivía más que una red sin entrenar, pero casi no comía (13.7 plantas contra 74 de las reglas). Midiendo su rapidez descubrimos que caminaba despacio (0.40) y solo corría al ver un depredador (0.98). Una presa quieta sobrevivía 700 de 800 pasos sin comer, así que la aptitud premiaba **ahorrar energía**, no buscar comida. Es justo lo que pregunta la propuesta: "¿qué comportamientos podría favorecer indebidamente el criterio?". Lo corregimos subiendo el metabolismo (0.0010 → 0.0016).
3. **Intento 2: el entrenamiento era muy corto.** Con 100 generaciones la aptitud seguía subiendo. El mejor depredador sacaba 0.77 en entrenamiento pero 0.375 en validación (tuvo suerte con sus mapas). Subimos a 250 generaciones.
4. **Probamos dos ideas que NO funcionaron:** dar más peso a la comida y premiar al depredador por acercarse a las presas. Las descartamos con datos (`resultados/exploraciones.md`).
5. **Resultado inesperado:** la red pequeña (4×4) fue mejor que la grande (16×16).
6. **Formulamos una hipótesis y la comprobamos.** La mutación suma ruido a todos los pesos. Con 514 pesos y σ = 0.10, cada mutación mueve la red ≈ 2.3, contra ≈ 0.9 con 82 pesos. Entrenamos la 16×16 con σ = 0.04 y pasó a ser la mejor presa, empatada con las reglas.

## 6. Resultados que debes saberte

**Cómo leer la "vida media":** fracción de los 800 pasos que vive en promedio una presa. 0.60 = vive en promedio 480 pasos.

| Comparación | Resultado clave | ¿Significativo? |
|---|---|---|
| E1 presa: entrenada vs sin entrenar | 0.422 vs 0.345 en (a); 0.282 vs 0.172 en (c) | Sí en (a) y (c); **no** en (b) (p = 0.26) |
| E1 depredador: entrenado vs sin entrenar | 1.1 vs 0.0 capturas en (a); 1.8 vs 0.1 en (c) | Sí en los 3 |
| E2 presa: 16×16 vs 4×4 | 0.422 vs **0.584** en (a) | Sí en (a) y (c): la pequeña gana |
| E2 depredador: 16×16 vs 4×4 | 1.1 vs 1.5 en (a) | No hay diferencia |
| E3 presa 4×4 vs reglas | 0.584 vs 0.603 en (a); 0.361 vs 0.356 en (c) | Empate en (a) y (c); pierde en (b) |
| E3 depredador vs reglas | 1.1 vs 2.9 en (a); 1.8 vs 5.4 en (c) | Las reglas ganan |
| E3 red vs aleatoria | Todas las redes ganan en los 3 escenarios | Sí (p ≤ 0.035) |
| E4 presa sin ver depredadores | Más comida (22.9 vs 8.8) pero casi el doble de capturas (9.0 vs 4.7) en (a) | Solo vive menos en (c) (p = 0.037) |
| E5 presa 16×16 con σ = 0.04 | 0.605 en (a), 0.436 en (b), 0.388 en (c) | Mejor que σ = 0.10 en los 3; empata con reglas en los 3 |

**Comportamientos aprendidos (coseno: +1 = hacia el objetivo, −1 = en contra):**
* Evasión: todas las redes entrenadas huyen (+0.40 a +0.45; reglas +0.71; sin entrenar +0.10).
* Búsqueda: la 16×16 con σ = 0.10 **no** busca comida (−0.15); la 4×4 (+0.42) y la 16×16 con σ = 0.04 (+0.39) sí.
* Persecución: débil (+0.30; reglas +0.82). Los depredadores corren casi siempre al máximo (0.98) y se mueren de hambre.
* Estrategia propia de las presas: caminar despacio (0.32–0.40) para ahorrar energía y acelerar al ver peligro. Las reglas van siempre rápido (0.73).

**La respuesta a la pregunta orientadora en 3 frases:** las redes superan siempre a las estrategias sin aprendizaje. La mejor presa iguala a las reglas (empate estadístico en los 3 escenarios) solo cuando el entorno obliga a la conducta deseada (metabolismo suficiente) y la búsqueda genética está bien ajustada (mutación proporcional al tamaño de la red). Los depredadores no llegan al nivel de las reglas porque su recompensa es escasa y el entorno los castiga por moverse.

## 7. Cómo leer cada gráfica

* **`entrenamiento.png`:** eje x = generación; eje y = aptitud media de la población. La línea gruesa es la media móvil de 10 generaciones y la delgada el valor real (con mucho ruido, porque cada generación usa mapas nuevos). Sube = la población aprende. La línea azul de la presa (16×16, σ = 0.10) se estanca más abajo: ahí se ve el problema de E2. En el depredador, la aptitud casi no sube durante ~60 generaciones en la 16×16 y ~140 en la 4×4 (nadie captura nada, todos tienen aptitud ≈ 0) y luego despega.
* **`pesos_antes_despues.png`:** histograma de los pesos. Antes están cerca de 0 (inicialización Xavier); después se reparten entre −4 y 4. Demuestra que los parámetros cambiaron. Cuidado: parte del cambio es ruido acumulado de la mutación. Que la red aprendió lo demuestra el desempeño (E1), no este histograma.
* **Gráficas de barras E1–E5:** cada grupo es un escenario; cada barra, la media de 10 repeticiones; la rayita negra, ± una desviación estándar. Si las rayitas de dos barras se traslapan mucho, probablemente la diferencia no es significativa. Para confirmarlo, mira el valor p en `resumen.md`.

## 8. Preguntas probables y cómo responderlas

**"Muéstrame que la decisión sale de la red."** Abre `politicas.py`, clase `PoliticaNeuronal`: `__call__` llama a `adelante()` y devuelve su salida. En `mundo.py`, esa salida es la que mueve al agente (`_mover`). En la simulación, haz clic en un agente: la flecha naranja es exactamente la salida de la red. Si cambias la política con `P` a "sin entrenar", el comportamiento cambia por completo.

**"¿Cómo se modifican los pesos?"** Por mutación: `hijo = padre + N(0, σ)` en `evolucion.py`, más el cruce uniforme. No hay gradientes ni retropropagación.

**"¿Qué se optimiza?"** La aptitud. Presa: vida media + 0.02 × comida por presa. Depredador: capturas por depredador + 0.3 × energía final.

**"¿Por qué la red grande fue peor?"** Por la mutación, no por falta de capacidad. Con σ fijo, la red grande recibe cambios más grandes en cada mutación y le cuesta afinar. Lo comprobamos en E5 con σ = 0.04.

**"¿Por qué los depredadores son malos?"** Tres razones con evidencia: (1) recompensa escasa (al principio casi nadie captura, la aptitud ≈ 0 para todos y la selección no tiene a quién preferir); (2) solo son 0.3 px/paso más rápidos que una presa que huye, así que perseguir en campo abierto casi nunca funciona; (3) se mueren de hambre incluso con reglas. Es un problema del diseño del entorno, y por eso es nuestra primera mejora propuesta.

**"¿Por qué no entrenaron las dos especies juntas (coevolución)?"** Porque el objetivo de cada una cambiaría todo el tiempo y no podríamos saber si una mejora es real o el rival empeoró. Con el rival fijo, cada experimento cambia una sola variable.

**"¿Qué significa p = 0.002?"** Si en realidad no hubiera diferencia, una diferencia tan grande como la observada solo aparecería por azar en 2 de cada 1000 permutaciones. Con 10 repeticiones solo hay 2¹⁰ = 1024 combinaciones de signos, así que el p mínimo posible es ≈ 2/1024 ≈ 0.002. Por eso varios resultados dan exactamente 0.0021: es el máximo de evidencia que permiten 10 repeticiones.

**"¿Por qué 10 repeticiones?"** Es suficiente para detectar las diferencias grandes con la prueba pareada y cabe en ~1 minuto de cómputo. Las diferencias pequeñas (por ejemplo, 4×4 vs reglas en (a): −0.020, p = 0.18) no se pueden distinguir con 10. Más repeticiones serían una mejora.

**"¿Qué variable cambia en cada experimento?"** E1: los pesos (entrenados o no). E2: el tamaño de las capas ocultas. E3: el tipo de política. E4: si la presa ve o no al depredador. E5: σ de la mutación. Constantes en todos: mapas (semillas 1000–1009), rival de reglas, física y escenario.

**"¿Qué cambiarías primero?"** La energía del depredador (ver arriba), con la evidencia de que muere de hambre en todas las condiciones, incluso con reglas.

**"Este resultado contradice lo esperado, ¿por qué?"** Ejemplos: la red pequeña gana (E2); ver al depredador no siempre ayuda (E4 en (a): come menos por estar huyendo); en el ecosistema completo las presas viven más en (c) con redes que con reglas, pero solo porque los depredadores neuronales cazan mal.

## 9. Si te piden cambiar un parámetro en vivo

Cambia el valor en `config.py`, guarda y vuelve a correr `uv run simulacion.py` (lo ves en vivo) o `uv run experimentos.py` (lo mides, ~1 minuto). **No hace falta volver a entrenar** para cambios del entorno: los modelos se cargan igual.

Efectos **medidos** (no supuestos) con la mejor presa (16×16, σ = 0.04) contra depredadores de reglas, escenario (a), semillas 1000–1009. Línea base: vida 0.605, capturas 4.8, comida 27.5, presas muertas de hambre 6.9.

| Cambio en `config.py` | Qué pasa (medido) | Por qué |
|---|---|---|
| `"depr_vel_max": 2.3` → `3.0` | Capturas 4.8 → 6.1; vida 0.605 → 0.538 | El depredador gana 1 px/paso a la presa que huye, en vez de 0.3. |
| `"presa_vision": 130` → `60` | Capturas 4.8 → **7.2**, pero comida 27.5 → 45.4 y vida 0.605 → 0.625 | Igual que en E4: la presa ve al depredador más tarde y lo capturan más, pero huye menos y come más. **Resultado contraintuitivo, buen ejemplo para explicar.** |
| `"captura_energia": 0.45` → `0.9` | **Nada cambia** | La energía tiene tope 1.0, y con +0.45 casi siempre ya se llega al tope. Es buen ejemplo de leer el código antes de predecir. |
| `"presa_costo_base": 0.0016` → `0.0010` | Vida 0.605 → 0.719; muertes por hambre 6.9 → 3.1 | Vuelves al metabolismo del intento 1: sobrevivir cuesta menos. |
| En `c_presion`, `"plantas": 45` → `10` | Vida 0.388 → 0.309; muertes por hambre 3.9 → 7.0 | Escasez + presión a la vez. |
| `SEMILLAS_PRUEBA` | Las medias cambian un poco; las conclusiones deberían mantenerse | Es otra muestra de mapas. |

Para cambios de la red o del entrenamiento (`OCULTAS`, `sigma`, `generaciones`, pesos de la aptitud) hay que volver a entrenar: por ejemplo, `uv run entrenar.py --especie presa --generaciones 30 --nombre prueba`, ~2 minutos. Ojo: con pocas generaciones el modelo será peor.

## 10. Guion de la demostración (5 minutos)

1. `uv run simulacion.py`. Escenario (a) con redes. Señala plantas, presas, depredadores y el panel.
2. Haz clic en una presa y explica sus 12 entradas, las 32 neuronas ocultas y la flecha de salida. Espera a que se acerque un depredador: verás que "depr. cerca" sube, las neuronas cambian de color y la flecha apunta en dirección contraria (evasión).
3. Presiona `P` hasta "sin entrenar": las presas casi no se mueven y las capturan. Luego "reglas" para comparar.
4. Presiona `3` (presión, con obstáculos) y `2` (escasez) para mostrar los escenarios.
5. Abre `resultados/figuras/entrenamiento.png` y `e5_presas_mutacion.png` y cuenta la historia de la sección 5.

"""Configuración central de NeuroEcosistema.

Todos los parámetros del mundo, de los escenarios, de las redes y del
entrenamiento están aquí. Cambiar un valor en este archivo es la única
forma de modificar un experimento, así cada resultado queda asociado a una
configuración registrada (se guarda en JSON junto con los resultados).
"""
from copy import deepcopy

# ---------------------------------------------------------------------------
# MUNDO (valores comunes a todos los escenarios)
# ---------------------------------------------------------------------------
MUNDO = {
    "ancho": 700,             # píxeles
    "alto": 560,
    "pasos_max": 800,         # duración máxima de un episodio
    # Presas
    "presa_vel_max": 2.0,     # px por paso
    "presa_radio": 6,
    "presa_vision": 130,      # radio de percepción
    "presa_energia_inicial": 0.7,
    "presa_costo_base": 0.0016,   # metabolismo por paso
    "presa_costo_mov": 0.0015,    # costo extra * (velocidad relativa)^2
    "planta_energia": 0.30,
    "radio_comer": 9,
    # Depredadores
    "depr_vel_max": 2.3,      # un poco más rápidos que las presas...
    "depr_radio": 8,
    "depr_vision": 170,
    "depr_energia_inicial": 0.8,
    "depr_costo_base": 0.0008,
    "depr_costo_mov": 0.0025,     # ...pero moverse rápido les cuesta más
    "captura_energia": 0.45,
    "radio_captura": 11,
    # Obstáculos
    "obstaculo_radio": 35,
}

# ---------------------------------------------------------------------------
# ESCENARIOS
# Solo cambian población, alimento y obstáculos. Todo lo demás es constante.
# ---------------------------------------------------------------------------
ESCENARIOS = {
    # Escenario usado para ENTRENAR (intermedio entre los tres de evaluación).
    "entrenamiento": {"presas": 15, "depredadores": 3, "plantas": 35,
                      "rebrote": 0.015, "obstaculos": 2},
    # (a) Recursos suficientes y pocos depredadores.
    "a_abundancia": {"presas": 15, "depredadores": 2, "plantas": 45,
                     "rebrote": 0.020, "obstaculos": 0},
    # (b) Escasez de alimento.
    "b_escasez": {"presas": 15, "depredadores": 2, "plantas": 12,
                  "rebrote": 0.004, "obstaculos": 0},
    # (c) Más depredadores y obstáculos.
    "c_presion": {"presas": 15, "depredadores": 5, "plantas": 45,
                  "rebrote": 0.020, "obstaculos": 4},
}
ESCENARIOS_EVALUACION = ["a_abundancia", "b_escasez", "c_presion"]

# ---------------------------------------------------------------------------
# REDES NEURONALES
# ---------------------------------------------------------------------------
ENTRADAS_PRESA = 12      # ver mundo.observaciones_presas()
ENTRADAS_DEPR = 11       # ver mundo.observaciones_depredadores()
SALIDAS = 2              # vector de movimiento (x, y) en [-1, 1]
OCULTAS = (16, 16)       # arquitectura principal: dos capas ocultas
OCULTAS_PEQUENA = (4, 4) # arquitectura alternativa para el experimento 2
ACTIVACION = "tanh"

# ---------------------------------------------------------------------------
# ENTRENAMIENTO (neuroevolución)
# ---------------------------------------------------------------------------
EVOLUCION = {
    "poblacion": 32,          # genomas por generación
    "episodios_por_genoma": 2,
    "generaciones": 250,
    "elite": 4,               # mejores que pasan intactos
    "torneo": 3,
    "sigma": 0.10,            # desviación de la mutación gaussiana
    "prob_cruce": 0.5,
    "semilla": 42,
    "finalistas": 5,          # elites re-evaluados al final
}
# Peso del alimento en la aptitud de las presas y de la energía en la de
# los depredadores (ver evolucion.py).
PESO_COMIDA = 0.02
PESO_ENERGIA_DEPR = 0.3
# Moldeado de recompensa del depredador: premio por mantenerse cerca de presas.
PESO_PERSECUCION = 0.0

# ---------------------------------------------------------------------------
# SEMILLAS
# ---------------------------------------------------------------------------
SEMILLAS_VALIDACION = list(range(500, 508))   # elegir el campeón
SEMILLAS_PRUEBA = list(range(1000, 1010))     # experimentos (nunca se entrena)


def escenario(nombre):
    """Devuelve un diccionario con el mundo + el escenario indicado."""
    cfg = deepcopy(MUNDO)
    cfg.update(ESCENARIOS[nombre])
    cfg["nombre"] = nombre
    return cfg

"""Entrenamiento por neuroevolución (algoritmo genético sobre los pesos).

¿Por qué no retropropagación como en Neurito?  Porque aquí no existe una
"respuesta correcta" por paso: solo sabemos, al final del episodio, cuánto vivió
la presa o cuántas presas capturó el depredador. La neuroevolución optimiza
directamente ese resultado sin necesitar etiquetas ni gradientes.

Ciclo de una generación:
  1. Evaluar: cada genoma controla a TODOS los agentes de su especie en
     `episodios_por_genoma` mundos. Todos los genomas de una generación se
     prueban en los MISMOS mapas (mismas semillas) -> comparación justa.
  2. Ordenar por aptitud (fitness).
  3. Elitismo: los `elite` mejores pasan sin cambios.
  4. Reproducción: el resto se crea eligiendo padres por torneo, cruzándolos
     (cruce uniforme) y mutándolos: w_hijo = w_padre + N(0, sigma).
"""
import numpy as np

import config
from mundo import Mundo
from politicas import (PoliticaNeuronal, PoliticaReglasDepredador,
                       PoliticaReglasPresa)
from red import desempacar, genoma_aleatorio


def entradas_de(especie):
    return config.ENTRADAS_PRESA if especie == "presa" else config.ENTRADAS_DEPR


def aptitud(mundo, especie, cercania_media=None):
    """Criterio que se optimiza (uno por mundo).

    Presa:       fracción del episodio que vive (media de las presas)
                 + PESO_COMIDA * plantas comidas por presa.
    Depredador:  capturas por depredador
                 + PESO_ENERGIA_DEPR * energía final media (muertos = 0)
                 + PESO_PERSECUCION * cercanía media a la presa más cercana
                   (moldeado de recompensa; 0 = desactivado).
    """
    c = mundo.cfg
    if especie == "presa":
        vida = mundo.vida_presas().mean(1) / c["pasos_max"]
        comida = mundo.presa_comida.sum(1) / c["presas"]
        return vida + config.PESO_COMIDA * comida
    capt = mundo.depr_capturas.sum(1) / c["depredadores"]
    energia = (mundo.depr_energia * mundo.depr_vivo).mean(1)
    extra = 0.0 if cercania_media is None else config.PESO_PERSECUCION * cercania_media
    return capt + config.PESO_ENERGIA_DEPR * energia + extra


def evaluar(genomas, especie, ocultas, semillas, cfg, activacion="tanh", anuladas=()):
    """Aptitud media de cada genoma en los mundos de `semillas`.

    genomas: (P, parámetros). Devuelve un arreglo (P,).
    El rival es SIEMPRE la política de reglas de la otra especie (fija), así el
    único cambio entre genomas es la propia red.
    """
    P, E = len(genomas), len(semillas)
    # mundo (p, e) = genoma p en el mapa e
    semillas_mundos = [s for _ in range(P) for s in semillas]
    mundo = Mundo(cfg, semillas_mundos)
    capas = desempacar(np.repeat(genomas, E, axis=0), entradas_de(especie),
                       ocultas, config.SALIDAS)
    red = PoliticaNeuronal(capas, activacion, anuladas)
    semilla_rival = int(semillas[0])
    if especie == "presa":
        mundo.correr(red, PoliticaReglasDepredador(semilla_rival, vision=cfg["depr_vision"]))
        return aptitud(mundo, especie).reshape(P, E).mean(1)
    # Depredador: además se acumula la cercanía a la presa más cercana en cada
    # paso (entrada 2 de su observación) para el moldeado de recompensa.
    presas = PoliticaReglasPresa(semilla_rival)
    suma, cuenta = np.zeros(mundo.B), np.zeros(mundo.B)
    while mundo.activo.any():
        obs_d = mundo.observaciones_depredadores()
        vivos = mundo.depr_vivo & mundo.activo[:, None]
        suma += (obs_d[..., 2] * vivos).sum(1)
        cuenta += vivos.sum(1)
        mundo.paso_simulacion(presas(mundo.observaciones_presas()), red(obs_d))
    cercania = suma / np.maximum(cuenta, 1)
    return aptitud(mundo, especie, cercania).reshape(P, E).mean(1)


def _torneo(rng, aptitudes, k):
    candidatos = rng.choice(len(aptitudes), size=k, replace=False)
    return candidatos[np.argmax(aptitudes[candidatos])]


def evolucionar(especie, ocultas=config.OCULTAS, parametros=None, activacion="tanh",
                anuladas=(), escenario="entrenamiento", informar=print):
    """Entrena una especie y devuelve (campeón, historial, info)."""
    p = dict(config.EVOLUCION)
    if parametros:
        p.update(parametros)
    cfg = config.escenario(escenario)
    rng = np.random.default_rng(p["semilla"])
    n_in = entradas_de(especie)

    poblacion = np.array([genoma_aleatorio(rng, n_in, ocultas, config.SALIDAS)
                          for _ in range(p["poblacion"])])
    historial = []
    mejor_inicial = None

    for g in range(p["generaciones"]):
        semillas = [int(s) for s in rng.integers(0, 1_000_000, p["episodios_por_genoma"])]
        apt = evaluar(poblacion, especie, ocultas, semillas, cfg, activacion, anuladas)
        orden = np.argsort(apt)[::-1]
        mejor = poblacion[orden[0]]
        if mejor_inicial is None:
            mejor_inicial = mejor.copy()
        historial.append({
            "generacion": g,
            "aptitud_mejor": float(apt[orden[0]]),
            "aptitud_media": float(apt.mean()),
            "aptitud_desv": float(apt.std()),
            "aptitud_peor": float(apt[orden[-1]]),
            # Evidencia de que los parámetros cambian:
            "distancia_al_inicio": float(np.linalg.norm(mejor - mejor_inicial)),
            "norma_pesos_mejor": float(np.linalg.norm(mejor)),
            "semillas": " ".join(map(str, semillas)),
        })
        informar(f"[{especie}] gen {g:3d} | mejor {apt[orden[0]]:.3f} | "
                 f"media {apt.mean():.3f} | dist. al inicio {historial[-1]['distancia_al_inicio']:.2f}")

        if g == p["generaciones"] - 1:
            break
        nueva = [poblacion[i].copy() for i in orden[:p["elite"]]]   # elitismo
        while len(nueva) < p["poblacion"]:
            a = poblacion[_torneo(rng, apt, p["torneo"])]
            if rng.random() < p["prob_cruce"]:
                b = poblacion[_torneo(rng, apt, p["torneo"])]
                hijo = np.where(rng.random(a.size) < 0.5, a, b)   # cruce uniforme
            else:
                hijo = a.copy()
            hijo = hijo + rng.normal(0, p["sigma"], a.size)        # mutación
            nueva.append(hijo)
        poblacion = np.array(nueva)

    # Elegir el campeón re-evaluando a los finalistas en semillas de validación
    # (así no gana un genoma que solo tuvo suerte en dos mapas).
    finalistas = poblacion[orden[:p["finalistas"]]]
    apt_val = evaluar(finalistas, especie, ocultas, config.SEMILLAS_VALIDACION,
                      cfg, activacion, anuladas)
    campeon = finalistas[int(np.argmax(apt_val))]
    info = {"aptitud_validacion": float(apt_val.max()),
            "aptitud_validacion_finalistas": [float(x) for x in apt_val],
            "genoma_inicial_mejor": mejor_inicial}
    informar(f"[{especie}] campeón: aptitud en validación {apt_val.max():.3f}")
    return campeon, historial, info

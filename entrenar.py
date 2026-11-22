"""Entrena una red por neuroevolución y guarda el modelo y su registro.

Ejemplos:
    uv run entrenar.py --especie presa
    uv run entrenar.py --especie depredador
    uv run entrenar.py --especie presa --ocultas 4 4 --nombre presa_4x4
    uv run entrenar.py --todo          # entrena todos los modelos del informe (6)

Genera:
    modelos/<nombre>.npz                   pesos del campeón (+ genoma inicial)
    resultados/entrenamiento_<nombre>.csv  aptitud por generación
    resultados/config_<nombre>.json        configuración completa usada
"""
import argparse
import csv
import json
import time
from pathlib import Path

import config
from evolucion import entradas_de, evolucionar
from red import Cerebro

RAIZ = Path(__file__).resolve().parent
# Entradas del sensor de depredador en la presa (para el experimento 4)
SENSOR_DEPREDADOR = (3, 4, 5)

# Modelos que usa el informe:
#   nombre -> (especie, capas ocultas, entradas anuladas, cambios a config.EVOLUCION)
MODELOS = {
    "presa_16x16": ("presa", (16, 16), (), {}),
    "depredador_16x16": ("depredador", (16, 16), (), {}),
    "presa_4x4": ("presa", (4, 4), (), {}),
    "depredador_4x4": ("depredador", (4, 4), (), {}),
    "presa_16x16_ciega": ("presa", (16, 16), SENSOR_DEPREDADOR, {}),
    # Experimento 5: mutación escalada al tamaño de la red (0.04 * raíz(514) ~ 0.1 * raíz(82))
    "presa_16x16_sigma004": ("presa", (16, 16), (), {"sigma": 0.04}),
}


def entrenar(nombre, especie, ocultas, anuladas=(), generaciones=None, semilla=None,
             extra=None):
    params = dict(extra or {})
    if generaciones:
        params["generaciones"] = generaciones
    if semilla is not None:
        params["semilla"] = semilla
    inicio = time.time()
    campeon, historial, info = evolucionar(especie, ocultas, params, anuladas=anuladas)
    duracion = time.time() - inicio

    (RAIZ / "modelos").mkdir(exist_ok=True)
    (RAIZ / "resultados").mkdir(exist_ok=True)
    cerebro = Cerebro(campeon, entradas_de(especie), ocultas, config.SALIDAS,
                      config.ACTIVACION, anuladas)
    cerebro.guardar(RAIZ / "modelos" / f"{nombre}.npz",
                    genoma_inicial=info["genoma_inicial_mejor"])

    with open(RAIZ / "resultados" / f"entrenamiento_{nombre}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(historial[0]))
        w.writeheader()
        w.writerows(historial)

    evo = dict(config.EVOLUCION, **params)
    registro = {
        "nombre": nombre, "especie": especie, "ocultas": list(ocultas),
        "entradas": entradas_de(especie), "entradas_anuladas": list(anuladas),
        "activacion": config.ACTIVACION, "evolucion": evo,
        "escenario_entrenamiento": config.escenario("entrenamiento"),
        "rival": "reglas", "peso_comida": config.PESO_COMIDA,
        "peso_energia_depr": config.PESO_ENERGIA_DEPR,
        "semillas_validacion": config.SEMILLAS_VALIDACION,
        "aptitud_validacion": info["aptitud_validacion"],
        "aptitud_validacion_finalistas": info["aptitud_validacion_finalistas"],
        "duracion_segundos": round(duracion, 1),
    }
    with open(RAIZ / "resultados" / f"config_{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)
    print(f"Guardado modelos/{nombre}.npz ({duracion:.0f} s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Entrena redes de NeuroEcosistema")
    ap.add_argument("--todo", action="store_true", help="entrena todos los modelos del informe")
    ap.add_argument("--modelos", nargs="+", choices=list(MODELOS),
                    help="entrena solo estos modelos del informe (para correr en paralelo)")
    ap.add_argument("--especie", choices=["presa", "depredador"])
    ap.add_argument("--ocultas", type=int, nargs="+", default=list(config.OCULTAS))
    ap.add_argument("--nombre")
    ap.add_argument("--generaciones", type=int)
    ap.add_argument("--semilla", type=int)
    a = ap.parse_args()

    if a.todo or a.modelos:
        for nombre in (a.modelos or MODELOS):
            esp, ocu, anu, extra = MODELOS[nombre]
            entrenar(nombre, esp, ocu, anu, a.generaciones, a.semilla, extra)
    elif a.especie:
        ocu = tuple(a.ocultas)
        nombre = a.nombre or f"{a.especie}_{'x'.join(map(str, ocu))}"
        entrenar(nombre, a.especie, ocu, (), a.generaciones, a.semilla)
    else:
        ap.print_help()

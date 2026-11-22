"""Evaluación experimental de NeuroEcosistema.

Corre cada condición en los escenarios (a), (b) y (c) con las 10 semillas de
prueba (config.SEMILLAS_PRUEBA, nunca usadas para entrenar). Como todas las
condiciones usan las MISMAS semillas, las comparaciones son pareadas: el mapa
inicial es idéntico y solo cambia la política evaluada.

Control de variables:
  * Al evaluar PRESAS, los depredadores son siempre los de reglas.
  * Al evaluar DEPREDADORES, las presas son siempre las de reglas.
  * Así el único factor que cambia es la política de la especie evaluada.

Salidas:
  resultados/datos_experimentos.csv   una fila por (condición, escenario, semilla)
  resultados/resumen.md               tablas media ± desviación y pruebas
  resultados/figuras/*.png            gráficas

Uso:  uv run experimentos.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import config
from mundo import Mundo
from politicas import (PoliticaAleatoria, PoliticaNeuronal,
                       PoliticaReglasDepredador, PoliticaReglasPresa)
from red import Cerebro, desempacar, genoma_aleatorio

RAIZ = Path(__file__).resolve().parent
RES = RAIZ / "resultados"
FIG = RES / "figuras"
SEMILLAS = config.SEMILLAS_PRUEBA
SEMILLA_RIVAL = 2024          # semilla fija de las políticas rivales/aleatorias

# Paleta categórica (orden fijo) y tintas de texto
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"
# Cada condición tiene SIEMPRE el mismo color en todas las gráficas.
COLOR_COND = {
    "presa_16x16": "#2a78d6", "depredador_16x16": "#2a78d6",
    "presa_4x4": "#eb6834", "depredador_4x4": "#eb6834",
    "reglas": "#1baf7a", "aleatoria": "#eda100", "sin_entrenar": "#e87ba4",
    "presa_16x16_ciega": "#6250d6", "presa_16x16_sigma004": "#008300",
}
NOMBRES_ESC = {"a_abundancia": "(a) Abundancia", "b_escasez": "(b) Escasez",
               "c_presion": "(c) Presión"}


# ---------------------------------------------------------------------------
# Construcción de políticas
# ---------------------------------------------------------------------------
def red_entrenada(nombre, B):
    c = Cerebro.cargar(RAIZ / "modelos" / f"{nombre}.npz")
    return PoliticaNeuronal(c.capas(B), c.activacion, c.anuladas)


def red_sin_entrenar(especie, B):
    """Una red con pesos iniciales aleatorios DISTINTA en cada repetición."""
    n_in = config.ENTRADAS_PRESA if especie == "presa" else config.ENTRADAS_DEPR
    genomas = np.array([genoma_aleatorio(np.random.default_rng(7000 + s), n_in,
                                         config.OCULTAS, config.SALIDAS) for s in SEMILLAS])
    return PoliticaNeuronal(desempacar(genomas, n_in, config.OCULTAS, config.SALIDAS))


def politica(especie, condicion, cfg):
    B = len(SEMILLAS)
    if condicion == "reglas":
        return (PoliticaReglasPresa(SEMILLA_RIVAL) if especie == "presa"
                else PoliticaReglasDepredador(SEMILLA_RIVAL, vision=cfg["depr_vision"]))
    if condicion == "aleatoria":
        return PoliticaAleatoria(SEMILLA_RIVAL + 1)
    if condicion == "sin_entrenar":
        return red_sin_entrenar(especie, B)
    return red_entrenada(condicion, B)   # nombre de un modelo en modelos/


# Condiciones de cada especie (la primera es la red principal)
CONDICIONES = {
    "presa": ["presa_16x16", "presa_4x4", "sin_entrenar", "reglas", "aleatoria",
              "presa_16x16_ciega", "presa_16x16_sigma004"],
    "depredador": ["depredador_16x16", "depredador_4x4", "sin_entrenar", "reglas",
                   "aleatoria"],
}
ETIQUETAS = {
    "presa_16x16": "Red 16×16 entrenada", "depredador_16x16": "Red 16×16 entrenada",
    "presa_4x4": "Red 4×4 entrenada", "depredador_4x4": "Red 4×4 entrenada",
    "sin_entrenar": "Red sin entrenar", "reglas": "Reglas", "aleatoria": "Aleatoria",
    "presa_16x16_ciega": "Red 16×16 sin ver depredadores",
    "presa_16x16_sigma004": "Red 16×16 con σ = 0.04",
}
METRICAS = ["vida_media_presas", "supervivencia_presas", "comida_total", "capturas",
            "presas_muertas_hambre", "depr_muertos_hambre", "energia_final_presas",
            "energia_final_depr", "t_primera_captura", "t_medio_captura", "pasos"]


def correr_todo():
    filas = []
    for especie, condiciones in CONDICIONES.items():
        for esc in config.ESCENARIOS_EVALUACION:
            cfg = config.escenario(esc)
            for cond in condiciones:
                mundo = Mundo(cfg, SEMILLAS)
                if especie == "presa":
                    m = mundo.correr(politica("presa", cond, cfg),
                                     politica("depredador", "reglas", cfg))
                else:
                    m = mundo.correr(politica("presa", "reglas", cfg),
                                     politica("depredador", cond, cfg))
                for i, s in enumerate(SEMILLAS):
                    filas.append({"especie_evaluada": especie, "condicion": cond,
                                  "escenario": esc, "semilla": s,
                                  **{k: float(m[k][i]) for k in METRICAS}})
                print(f"{especie:10s} {esc:13s} {cond:18s} "
                      f"vida={m['vida_media_presas'].mean():.3f} capt={m['capturas'].mean():.1f}")
    # Ecosistema completo: redes contra redes (observación adicional)
    for esc in config.ESCENARIOS_EVALUACION:
        cfg = config.escenario(esc)
        for cond_p, cond_d in [("presa_16x16", "depredador_16x16"), ("reglas", "reglas")]:
            m = Mundo(cfg, SEMILLAS).correr(politica("presa", cond_p, cfg),
                                            politica("depredador", cond_d, cfg))
            for i, s in enumerate(SEMILLAS):
                filas.append({"especie_evaluada": "ecosistema",
                              "condicion": "redes_vs_redes" if cond_p != "reglas" else "reglas_vs_reglas",
                              "escenario": esc, "semilla": s,
                              **{k: float(m[k][i]) for k in METRICAS}})
    return filas


# ---------------------------------------------------------------------------
# Estadística
# ---------------------------------------------------------------------------
def prueba_pareada(x, y, n=20000, semilla=0):
    """Prueba de permutación pareada (cambio de signo) sobre la media de x - y.

    Como x[i] e y[i] usan la misma semilla, se comparan por pares. Devuelve
    (diferencia media, valor p bilateral). No supone normalidad.
    """
    d = np.asarray(x) - np.asarray(y)
    d = d[~np.isnan(d)]
    if len(d) == 0 or np.allclose(d, 0):
        return 0.0, 1.0
    rng = np.random.default_rng(semilla)
    signos = rng.choice([-1, 1], size=(n, len(d)))
    nulas = np.abs((signos * d).mean(1))
    p = (np.sum(nulas >= abs(d.mean()) - 1e-12) + 1) / (n + 1)
    return float(d.mean()), float(p)


def valores(filas, especie, cond, esc, metrica):
    return np.array([f[metrica] for f in filas if f["especie_evaluada"] == especie
                     and f["condicion"] == cond and f["escenario"] == esc])


def ms(v, dec=3):
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return "—"
    return f"{v.mean():.{dec}f} ± {v.std(ddof=1) if len(v) > 1 else 0:.{dec}f}"


# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------
def _estilo(ax, titulo, ylabel):
    ax.set_title(titulo, loc="left", color=TINTA, fontsize=11)
    ax.set_ylabel(ylabel, color=TINTA2)
    ax.tick_params(colors=TINTA2)
    ax.grid(axis="y", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(REJILLA)


def grafica_barras(filas, especie, conds, metrica, ylabel, titulo, archivo):
    fig, ax = plt.subplots(figsize=(8, 4))
    escs = config.ESCENARIOS_EVALUACION
    ancho = 0.8 / len(conds)
    for j, cond in enumerate(conds):
        medias = [np.nanmean(valores(filas, especie, cond, e, metrica)) for e in escs]
        desv = [np.nanstd(valores(filas, especie, cond, e, metrica), ddof=1) for e in escs]
        x = np.arange(len(escs)) + (j - (len(conds) - 1) / 2) * ancho
        ax.bar(x, medias, ancho * 0.92, yerr=desv, color=COLOR_COND[cond], label=ETIQUETAS[cond],
               error_kw={"ecolor": TINTA2, "elinewidth": 1, "capsize": 3})
    ax.set_xticks(range(len(escs)), [NOMBRES_ESC[e] for e in escs])
    _estilo(ax, titulo, ylabel)
    ax.legend(frameon=False, fontsize=8, labelcolor=TINTA2, ncol=min(3, len(conds)),
              loc="upper center", bbox_to_anchor=(0.5, -0.1))
    fig.tight_layout()
    fig.savefig(FIG / archivo, dpi=150)
    plt.close(fig)


def grafica_entrenamiento():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, especie, ylabel in zip(axes, ["presa", "depredador"],
                                   ["Aptitud (vida + comida)", "Aptitud (capturas + energía)"]):
        for arq in ["16x16", "4x4", "16x16_sigma004"]:
            ruta = RES / f"entrenamiento_{especie}_{arq}.csv"
            if not ruta.exists():
                continue
            h = np.genfromtxt(ruta, delimiter=",", names=True, dtype=None, encoding="utf-8")
            nombre = arq.replace("x", "×").replace("_sigma004", " σ=0.04")
            y = h["aptitud_media"]
            suave = np.convolve(y, np.ones(10) / 10, mode="valid")   # media móvil de 10 gen.
            color = COLOR_COND[f"{especie}_{arq}"]
            ax.plot(h["generacion"], y, color=color, lw=0.6, alpha=0.35)
            ax.plot(h["generacion"][9:], suave, color=color, lw=2,
                    label=f"{nombre}: media de la población (media móvil 10 gen.)")
        _estilo(ax, f"Entrenamiento: {especie}", ylabel)
        ax.set_xlabel("Generación", color=TINTA2)
        ax.legend(frameon=False, fontsize=8, labelcolor=TINTA2)
    fig.tight_layout()
    fig.savefig(FIG / "entrenamiento.png", dpi=150)
    plt.close(fig)


def grafica_pesos():
    """Distribución de pesos antes (mejor genoma de la generación 0) y después."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    for ax, nombre in zip(axes, ["presa_16x16", "depredador_16x16"]):
        d = np.load(RAIZ / "modelos" / f"{nombre}.npz")
        bins = np.linspace(-4, 4, 50)
        ax.hist(d["genoma_inicial"], bins=bins, color=COLORES[0], alpha=0.6, label="Antes (gen. 0)")
        ax.hist(d["genoma"], bins=bins, color=COLORES[1], alpha=0.6, label="Después (campeón)")
        cambio = np.linalg.norm(d["genoma"] - d["genoma_inicial"])
        _estilo(ax, f"{nombre}: |Δw| = {cambio:.1f}", "Cantidad de parámetros")
        ax.set_xlabel("Valor del peso", color=TINTA2)
        ax.legend(frameon=False, fontsize=8, labelcolor=TINTA2)
    fig.tight_layout()
    fig.savefig(FIG / "pesos_antes_despues.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Resumen en Markdown
# ---------------------------------------------------------------------------
def tabla(filas, especie, conds, metricas, titulos):
    lineas = ["| Escenario | Condición | " + " | ".join(titulos) + " |",
              "|---|---|" + "---|" * len(metricas)]
    for esc in config.ESCENARIOS_EVALUACION:
        for cond in conds:
            celdas = [ms(valores(filas, especie, cond, esc, m),
                         1 if m in ("comida_total", "capturas", "t_medio_captura",
                                    "t_primera_captura", "presas_muertas_hambre",
                                    "depr_muertos_hambre") else 3) for m in metricas]
            lineas.append(f"| {NOMBRES_ESC[esc]} | {ETIQUETAS.get(cond, cond)} | " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def comparaciones(filas, especie, pares, metrica):
    lineas = ["| Escenario | Comparación | Diferencia media | p (permutación pareada) |",
              "|---|---|---|---|"]
    for esc in config.ESCENARIOS_EVALUACION:
        for a, b in pares:
            dif, p = prueba_pareada(valores(filas, especie, a, esc, metrica),
                                    valores(filas, especie, b, esc, metrica))
            lineas.append(f"| {NOMBRES_ESC[esc]} | {ETIQUETAS[a]} − {ETIQUETAS[b]} | "
                          f"{dif:+.3f} | {p:.4f} |")
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Análisis de comportamiento: ¿hay búsqueda, persecución y evasión?
# ---------------------------------------------------------------------------
def _coseno(a, b):
    na = np.linalg.norm(a, axis=-1)
    nb = np.linalg.norm(b, axis=-1)
    return (a * b).sum(-1) / np.maximum(na * nb, 1e-9)


def analisis_comportamiento():
    """Mide, paso a paso, hacia dónde apunta cada agente respecto a lo que ve.

    coseno = +1: se mueve directo hacia el objetivo; -1: directo en contra; 0: de lado.
    Presas (rival: depredadores de reglas):
      búsqueda = coseno(acción, dirección a la planta) cuando ve planta y NO ve depredador
      evasión  = coseno(acción, dirección CONTRARIA al depredador) cuando lo ve
    Depredadores (rival: presas de reglas):
      persecución = coseno(acción, dirección a la presa) cuando la ve
    Se agregan los 3 escenarios y las 10 semillas de prueba.
    """
    filas = []
    for especie, conds in (("presa", ["presa_16x16", "presa_4x4", "presa_16x16_sigma004",
                                      "sin_entrenar", "reglas", "aleatoria"]),
                           ("depredador", ["depredador_16x16", "depredador_4x4",
                                           "sin_entrenar", "reglas", "aleatoria"])):
        for cond in conds:
            acum = {k: [] for k in ("rap_libre", "rap_amenaza", "busqueda", "evasion",
                                    "rapidez", "persecucion")}
            for esc in config.ESCENARIOS_EVALUACION:
                cfg = config.escenario(esc)
                m = Mundo(cfg, SEMILLAS)
                if especie == "presa":
                    pp, pd = politica("presa", cond, cfg), politica("depredador", "reglas", cfg)
                else:
                    pp, pd = politica("presa", "reglas", cfg), politica("depredador", cond, cfg)
                while m.activo.any():
                    op, od = m.observaciones_presas(), m.observaciones_depredadores()
                    ap, ad = pp(op), pd(od)
                    if especie == "presa":
                        vivas = m.presa_viva & m.activo[:, None]
                        rap = np.minimum(np.linalg.norm(ap, axis=-1), 1)
                        amenaza = vivas & (op[..., 5] > 0)
                        libre = vivas & ~amenaza
                        busca = libre & (op[..., 2] > 0)
                        acum["rap_libre"].append(rap[libre])
                        acum["rap_amenaza"].append(rap[amenaza])
                        acum["busqueda"].append(_coseno(ap, op[..., 0:2])[busca])
                        acum["evasion"].append(_coseno(ap, -op[..., 3:5])[amenaza])
                    else:
                        vivos = m.depr_vivo & m.activo[:, None]
                        rap = np.minimum(np.linalg.norm(ad, axis=-1), 1)
                        ve = vivos & (od[..., 2] > 0)
                        acum["rapidez"].append(rap[vivos])
                        acum["persecucion"].append(_coseno(ad, od[..., 0:2])[ve])
                    m.paso_simulacion(ap, ad)
            fila = {"especie": especie, "condicion": cond}
            for k, v in acum.items():
                v = np.concatenate(v) if v else np.array([])
                if len(v):
                    fila[k] = float(v.mean())
            filas.append(fila)
            print("comportamiento", fila)
    lin = ["## Comportamiento: ¿búsqueda, persecución y evasión?", "",
           "Coseno entre la acción y la dirección del objetivo visible (+1 = directo hacia él, "
           "−1 = directo en contra, 0 = de lado). Promedio de todos los pasos de los 3 escenarios "
           "y las 10 semillas de prueba. Rapidez = longitud de la acción (1 = velocidad máxima).", "",
           "| Presa | Rapidez sin amenaza | Rapidez viendo depredador | Búsqueda (hacia planta) | Evasión (lejos del depredador) |",
           "|---|---|---|---|---|"]
    for f in filas:
        if f["especie"] == "presa":
            lin.append(f"| {ETIQUETAS[f['condicion']]} | {f['rap_libre']:.2f} | {f['rap_amenaza']:.2f} | "
                       f"{f['busqueda']:+.2f} | {f['evasion']:+.2f} |")
    lin += ["", "| Depredador | Rapidez media | Persecución (hacia la presa) |", "|---|---|---|"]
    for f in filas:
        if f["especie"] == "depredador":
            lin.append(f"| {ETIQUETAS[f['condicion']]} | {f['rapidez']:.2f} | {f['persecucion']:+.2f} |")
    return "\n".join(lin)


def escribir_resumen(filas, comportamiento=""):
    P, D = CONDICIONES["presa"], CONDICIONES["depredador"]
    mp = ["vida_media_presas", "supervivencia_presas", "comida_total",
          "presas_muertas_hambre", "capturas", "energia_final_presas"]
    tp = ["Vida media (fracción)", "Supervivencia final", "Comida total",
          "Muertes por hambre", "Capturas sufridas", "Energía final presas"]
    md_ = ["capturas", "t_primera_captura", "t_medio_captura", "energia_final_depr",
           "depr_muertos_hambre", "vida_media_presas"]
    td = ["Capturas", "Paso 1.ª captura", "Paso medio de captura", "Energía final depr.",
          "Depr. muertos de hambre", "Vida media presas"]
    texto = [
        "# Resumen de resultados (generado por experimentos.py)",
        "",
        f"Semillas de prueba: {SEMILLAS}. Cada celda: media ± desviación estándar "
        "entre las 10 repeticiones. Tiempos en pasos de simulación "
        "('—' = no hubo capturas en ninguna repetición).",
        "",
        "## Presas (rival fijo: depredadores de reglas)",
        "", tabla(filas, "presa", P, mp, tp), "",
        "### Pruebas pareadas sobre la vida media de las presas", "",
        comparaciones(filas, "presa", [("presa_16x16", "sin_entrenar"),
                                       ("presa_16x16", "presa_4x4"),
                                       ("presa_16x16", "reglas"),
                                       ("presa_4x4", "reglas"),
                                       ("presa_16x16", "aleatoria"),
                                       ("presa_4x4", "aleatoria"),
                                       ("presa_16x16", "presa_16x16_ciega"),
                                       ("presa_16x16_sigma004", "presa_16x16"),
                                       ("presa_16x16_sigma004", "presa_4x4"),
                                       ("presa_16x16_sigma004", "reglas")],
                      "vida_media_presas"), "",
        "## Depredadores (rival fijo: presas de reglas)",
        "", tabla(filas, "depredador", D, md_, td), "",
        "### Pruebas pareadas sobre las capturas", "",
        comparaciones(filas, "depredador", [("depredador_16x16", "sin_entrenar"),
                                            ("depredador_16x16", "depredador_4x4"),
                                            ("depredador_16x16", "reglas"),
                                            ("depredador_4x4", "reglas"),
                                            ("depredador_16x16", "aleatoria"),
                                            ("depredador_4x4", "aleatoria")],
                      "capturas"), "",
        "## Ecosistema completo (observación adicional)", "",
    ]
    ETIQUETAS.update({"redes_vs_redes": "Redes vs redes", "reglas_vs_reglas": "Reglas vs reglas"})
    texto.append(tabla(filas, "ecosistema", ["redes_vs_redes", "reglas_vs_reglas"],
                       ["vida_media_presas", "comida_total", "capturas", "depr_muertos_hambre"],
                       ["Vida media presas", "Comida total", "Capturas", "Depr. muertos de hambre"]))
    texto += ["", comportamiento]
    (RES / "resumen.md").write_text("\n".join(texto) + "\n", encoding="utf-8")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    filas = correr_todo()
    with open(RES / "datos_experimentos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    grafica_entrenamiento()
    grafica_pesos()
    grafica_barras(filas, "presa", ["presa_16x16", "sin_entrenar"], "vida_media_presas",
                   "Vida media (fracción del episodio)",
                   "E1 · Presas antes y después de entrenar", "e1_presas_antes_despues.png")
    grafica_barras(filas, "depredador", ["depredador_16x16", "sin_entrenar"], "capturas",
                   "Capturas por episodio",
                   "E1 · Depredadores antes y después de entrenar", "e1_depr_antes_despues.png")
    grafica_barras(filas, "presa", ["presa_16x16", "presa_4x4"], "vida_media_presas",
                   "Vida media (fracción del episodio)",
                   "E2 · Presas: arquitectura 16×16 vs 4×4", "e2_presas_arquitectura.png")
    grafica_barras(filas, "depredador", ["depredador_16x16", "depredador_4x4"], "capturas",
                   "Capturas por episodio",
                   "E2 · Depredadores: arquitectura 16×16 vs 4×4", "e2_depr_arquitectura.png")
    grafica_barras(filas, "presa", ["presa_16x16", "presa_4x4", "reglas", "aleatoria"], "vida_media_presas",
                   "Vida media (fracción del episodio)",
                   "E3 · Presas: red vs referencias", "e3_presas_referencias.png")
    grafica_barras(filas, "depredador", ["depredador_16x16", "depredador_4x4", "reglas", "aleatoria"], "capturas",
                   "Capturas por episodio",
                   "E3 · Depredadores: red vs referencias", "e3_depr_referencias.png")
    grafica_barras(filas, "presa", ["presa_16x16", "presa_16x16_ciega"], "vida_media_presas",
                   "Vida media (fracción del episodio)",
                   "E4 · ¿Importa ver al depredador?", "e4_presas_sentidos.png")
    grafica_barras(filas, "presa", ["presa_16x16", "presa_16x16_sigma004", "presa_4x4"],
                   "vida_media_presas", "Vida media (fracción del episodio)",
                   "E5 · Presas 16×16: mutación σ = 0.10 vs 0.04", "e5_presas_mutacion.png")
    escribir_resumen(filas, analisis_comportamiento())
    print("\nListo: resultados/resumen.md, resultados/datos_experimentos.csv, resultados/figuras/")

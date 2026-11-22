"""Visualización en vivo de NeuroEcosistema con Pygame.

Uso:  uv run simulacion.py

Controles
  1 / 2 / 3 / 0  escenario (a) abundancia / (b) escasez / (c) presión / entrenamiento
  P              cambia la política de las presas
  D              cambia la política de los depredadores
  ESPACIO        pausa
  N              nuevo episodio (siguiente semilla)      R  reinicia la misma semilla
  + / -          velocidad                               V  muestra/oculta la visión
  Clic           selecciona un agente para inspeccionar su red
  ESC            salir
"""
from pathlib import Path

import numpy as np
import pygame

import config
from mundo import Mundo
from politicas import (PoliticaAleatoria, PoliticaNeuronal,
                       PoliticaReglasDepredador, PoliticaReglasPresa)
from red import Cerebro, desempacar, genoma_aleatorio

RAIZ = Path(__file__).resolve().parent
ANCHO, ALTO = 1140, 640
MX, MY = 12, 64                 # esquina del mundo en la ventana
PANEL_X = 730
FONDO, MUNDO_COLOR = (247, 245, 240), (236, 242, 230)
TINTA, TINTA2 = (30, 30, 30), (90, 88, 84)
AZUL, ROJO, VERDE = (42, 120, 214), (227, 73, 72), (60, 160, 80)
GRIS, NARANJA = (160, 158, 150), (235, 104, 52)

POLITICAS = ["red", "red_4x4", "reglas", "aleatoria", "sin_entrenar"]
NOMBRES_ENTRADA = {
    "presa": ["planta dx", "planta dy", "planta cerca", "depr. dx", "depr. dy", "depr. cerca",
              "obst. ux", "obst. uy", "obst. cerca", "energía", "pos x", "pos y"],
    "depredador": ["presa dx", "presa dy", "presa cerca", "presa vx", "presa vy",
                   "obst. ux", "obst. uy", "obst. cerca", "energía", "pos x", "pos y"],
}
ESCENARIOS_TECLA = {pygame.K_1: "a_abundancia", pygame.K_2: "b_escasez",
                    pygame.K_3: "c_presion", pygame.K_0: "entrenamiento"}


def crear_politica(especie, tipo, cfg, semilla):
    # "red": mejor modelo 16x16 de cada especie (la presa con mutación σ = 0.04, E5)
    nombres = {("presa", "red"): "presa_16x16_sigma004", ("depredador", "red"): "depredador_16x16",
               ("presa", "red_4x4"): "presa_4x4", ("depredador", "red_4x4"): "depredador_4x4"}
    archivo = RAIZ / "modelos" / f"{nombres.get((especie, tipo), '')}.npz"
    if tipo in ("red", "red_4x4") and archivo.exists():
        c = Cerebro.cargar(archivo)
        return PoliticaNeuronal(c.capas(1), c.activacion, c.anuladas)
    if tipo in ("red", "red_4x4", "sin_entrenar"):
        n = config.ENTRADAS_PRESA if especie == "presa" else config.ENTRADAS_DEPR
        g = genoma_aleatorio(np.random.default_rng(semilla), n, config.OCULTAS, config.SALIDAS)
        return PoliticaNeuronal(desempacar(g[None], n, config.OCULTAS, config.SALIDAS))
    if tipo == "reglas":
        return (PoliticaReglasPresa(semilla) if especie == "presa"
                else PoliticaReglasDepredador(semilla, vision=cfg["depr_vision"]))
    return PoliticaAleatoria(semilla)


class App:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("NeuroEcosistema - Depredadores y presas")
        self.reloj = pygame.time.Clock()
        self.f = pygame.font.SysFont(None, 22)
        self.fg = pygame.font.SysFont(None, 30)
        self.fp = pygame.font.SysFont(None, 18)
        self.escenario = "a_abundancia"
        self.tipo = {"presa": "red", "depredador": "red"}
        self.semilla_idx = 0
        self.velocidad = 1
        self.pausa = False
        self.ver_vision = False
        self.seleccion = ("presa", 0)
        self.reiniciar()

    # ------------------------------------------------------------------
    def reiniciar(self):
        self.cfg = config.escenario(self.escenario)
        self.semilla = config.SEMILLAS_PRUEBA[self.semilla_idx % len(config.SEMILLAS_PRUEBA)]
        self.mundo = Mundo(self.cfg, [self.semilla])
        self.pol = {e: crear_politica(e, self.tipo[e], self.cfg, self.semilla + 1)
                    for e in ("presa", "depredador")}
        self.historia = []
        self.fin_contador = 0
        self.ultima_accion = {"presa": None, "depredador": None}
        self.ultima_obs = {"presa": None, "depredador": None}

    def paso(self):
        m = self.mundo
        op, od = m.observaciones_presas(), m.observaciones_depredadores()
        ap, ad = self.pol["presa"](op), self.pol["depredador"](od)
        self.ultima_obs = {"presa": op, "depredador": od}
        self.ultima_accion = {"presa": ap, "depredador": ad}
        m.paso_simulacion(ap, ad)
        self.historia.append((m.presa_viva.sum(), m.depr_vivo.sum()))

    # ------------------------------------------------------------------
    def eventos(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                k = ev.key
                if k == pygame.K_ESCAPE:
                    return False
                if k in ESCENARIOS_TECLA:
                    self.escenario = ESCENARIOS_TECLA[k]
                    self.reiniciar()
                elif k in (pygame.K_p, pygame.K_d):
                    e = "presa" if k == pygame.K_p else "depredador"
                    i = POLITICAS.index(self.tipo[e])
                    self.tipo[e] = POLITICAS[(i + 1) % len(POLITICAS)]
                    self.reiniciar()
                elif k == pygame.K_SPACE:
                    self.pausa = not self.pausa
                elif k == pygame.K_n:
                    self.semilla_idx += 1
                    self.reiniciar()
                elif k == pygame.K_r:
                    self.reiniciar()
                elif k in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.velocidad = min(10, self.velocidad + 1)
                elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.velocidad = max(1, self.velocidad - 1)
                elif k == pygame.K_v:
                    self.ver_vision = not self.ver_vision
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.seleccionar(ev.pos)
        return True

    def seleccionar(self, pos):
        p = np.array([pos[0] - MX, pos[1] - MY], float)
        mejor, dmin = None, 25.0
        for esp, arr, vivos in (("presa", self.mundo.presa_pos[0], self.mundo.presa_viva[0]),
                                ("depredador", self.mundo.depr_pos[0], self.mundo.depr_vivo[0])):
            for i in range(len(arr)):
                d = np.linalg.norm(arr[i] - p)
                if vivos[i] and d < dmin:
                    mejor, dmin = (esp, i), d
        if mejor:
            self.seleccion = mejor

    # ------------------------------------------------------------------
    def texto(self, msg, x, y, fuente=None, color=TINTA):
        self.pantalla.blit((fuente or self.f).render(msg, True, color), (x, y))

    def dibujar_mundo(self):
        m, c = self.mundo, self.cfg
        pygame.draw.rect(self.pantalla, MUNDO_COLOR, (MX, MY, c["ancho"], c["alto"]), border_radius=6)
        for o in m.obst[0]:
            pygame.draw.circle(self.pantalla, GRIS, (MX + o[0], MY + o[1]), c["obstaculo_radio"])
        for pos, act in zip(m.planta_pos[0], m.planta_activa[0]):
            if act:
                pygame.draw.circle(self.pantalla, VERDE, (MX + pos[0], MY + pos[1]), 4)
        esp_sel, i_sel = self.seleccion
        for esp, arr, vivos, energia, color, radio, vision in (
                ("presa", m.presa_pos[0], m.presa_viva[0], m.presa_energia[0], AZUL,
                 c["presa_radio"], c["presa_vision"]),
                ("depredador", m.depr_pos[0], m.depr_vivo[0], m.depr_energia[0], ROJO,
                 c["depr_radio"], c["depr_vision"])):
            for i, (pos, vivo) in enumerate(zip(arr, vivos)):
                if not vivo:
                    continue
                centro = (MX + pos[0], MY + pos[1])
                if self.ver_vision:
                    pygame.draw.circle(self.pantalla, (210, 214, 205), centro, vision, 1)
                pygame.draw.circle(self.pantalla, color, centro, radio)
                # barra de energía
                pygame.draw.rect(self.pantalla, (210, 210, 210), (centro[0] - 8, centro[1] - radio - 6, 16, 3))
                pygame.draw.rect(self.pantalla, TINTA2,
                                 (centro[0] - 8, centro[1] - radio - 6, int(16 * energia[i]), 3))
                if (esp, i) == (esp_sel, i_sel):
                    pygame.draw.circle(self.pantalla, NARANJA, centro, radio + 5, 2)
                    acc = self.ultima_accion[esp]
                    if acc is not None:
                        fin = (centro[0] + acc[0, i, 0] * 30, centro[1] + acc[0, i, 1] * 30)
                        pygame.draw.line(self.pantalla, NARANJA, centro, fin, 3)

    def dibujar_panel(self):
        m, c = self.mundo, self.cfg
        x = PANEL_X
        nombres = {"a_abundancia": "(a) Abundancia", "b_escasez": "(b) Escasez",
                   "c_presion": "(c) Presión", "entrenamiento": "Entrenamiento"}
        self.texto("NEUROECOSISTEMA", MX, 14, self.fg)
        self.texto(f"Escenario: {nombres[self.escenario]}   Semilla: {self.semilla}   "
                   f"Paso: {m.paso}/{c['pasos_max']}   Velocidad: x{self.velocidad}"
                   + ("   [PAUSA]" if self.pausa else ""), MX, 40, self.fp, TINTA2)
        y = 14
        self.texto(f"Presas: {self.tipo['presa'].upper()}", x, y, self.f, AZUL)
        self.texto(f"Depredadores: {self.tipo['depredador'].upper()}", x + 190, y, self.f, ROJO)
        y += 26
        filas = [
            ("Presas vivas", f"{m.presa_viva.sum()} / {c['presas']}"),
            ("Depredadores vivos", f"{m.depr_vivo.sum()} / {c['depredadores']}"),
            ("Plantas comidas", f"{int(m.presa_comida.sum())}"),
            ("Capturas", f"{int(m.depr_capturas.sum())}"),
            ("Presas muertas de hambre", f"{int(m.presa_hambre.sum())}"),
            ("Energía media presas", f"{m.presa_energia[m.presa_viva].mean():.2f}" if m.presa_viva.any() else "—"),
            ("Energía media depr.", f"{m.depr_energia[m.depr_vivo].mean():.2f}" if m.depr_vivo.any() else "—"),
        ]
        for etiqueta, valor in filas:
            self.texto(etiqueta, x, y, self.fp, TINTA2)
            self.texto(valor, x + 200, y, self.fp)
            y += 18
        # Mini-gráfica de población
        y += 6
        g = pygame.Rect(x, y, 390, 60)
        pygame.draw.rect(self.pantalla, (236, 234, 228), g, border_radius=4)
        if len(self.historia) > 1:
            h = np.array(self.historia)
            for col, color, total in ((0, AZUL, c["presas"]), (1, ROJO, max(c["depredadores"], 1))):
                pts = [(g.left + i * g.width / max(c["pasos_max"], 1),
                        g.bottom - 4 - h[i, col] / total * (g.height - 8)) for i in range(len(h))]
                pygame.draw.lines(self.pantalla, color, False, pts, 2)
        self.texto("población viva (azul presas, rojo depredadores)", x, y + 62, self.fp, TINTA2)
        self.dibujar_inspeccion(x, y + 86)
        self.texto("1/2/3/0 escenario  P/D política  ESPACIO pausa  N nueva semilla  R reiniciar",
                   MX, ALTO - 20, self.fp, TINTA2)
        self.texto("+/- velocidad  V visión  Clic: inspeccionar agente  ESC salir",
                   PANEL_X, ALTO - 20, self.fp, TINTA2)

    def dibujar_inspeccion(self, x, y):
        esp, i = self.seleccion
        vivo = (self.mundo.presa_viva if esp == "presa" else self.mundo.depr_vivo)[0, i]
        self.texto(f"AGENTE SELECCIONADO: {esp} #{i}" + ("" if vivo else " (muerto)"),
                   x, y, self.f, AZUL if esp == "presa" else ROJO)
        y += 22
        obs = self.ultima_obs[esp]
        if obs is None:
            self.texto("(inicia la simulación)", x, y, self.fp, TINTA2)
            return
        pol = self.pol[esp]
        entradas = pol.ultimas_entradas[0, i] if isinstance(pol, PoliticaNeuronal) else obs[0, i]
        # Entradas como barras horizontales centradas en 0
        for k, (nombre, v) in enumerate(zip(NOMBRES_ENTRADA[esp], entradas)):
            yy = y + k * 15
            self.texto(nombre, x, yy, self.fp, TINTA2)
            cx = x + 135
            pygame.draw.line(self.pantalla, (200, 198, 190), (cx, yy + 2), (cx, yy + 12))
            ancho = int(np.clip(v, -1, 1) * 60)
            color = AZUL if v >= 0 else NARANJA
            pygame.draw.rect(self.pantalla, color, (min(cx, cx + ancho), yy + 4, abs(ancho), 7))
            self.texto(f"{v:+.2f}", x + 200, yy, self.fp, TINTA2)
        # Activaciones ocultas y salida
        xx = x + 250
        if isinstance(pol, PoliticaNeuronal) and pol.ultimas_ocultas is not None:
            for capa, act in enumerate(pol.ultimas_ocultas):
                # 16 neuronas = 2 filas de 8; 4 neuronas = 1 fila
                self.texto(f"oculta {capa + 1}", xx, y + capa * 70, self.fp, TINTA2)
                vals = act[0, i]
                for j, v in enumerate(vals):
                    col = j % 8
                    fila = j // 8
                    t = (np.clip(v, -1, 1) + 1) / 2
                    color = (int(235 * (1 - t) + 42 * t), int(104 * (1 - t) + 120 * t),
                             int(52 * (1 - t) + 214 * t))
                    pygame.draw.rect(self.pantalla, color,
                                     (xx + col * 16, y + 16 + capa * 70 + fila * 16, 14, 14))
            self.texto("naranja = -1   azul = +1", xx, y + 145, self.fp, TINTA2)
        else:
            self.texto("(sin red: política", xx, y, self.fp, TINTA2)
            self.texto(f" {self.tipo[esp]})", xx, y + 16, self.fp, TINTA2)
        acc = self.ultima_accion[esp][0, i]
        self.texto(f"salida: ({acc[0]:+.2f}, {acc[1]:+.2f})", xx, y + 165, self.fp)
        self.texto(f"rapidez: {min(np.linalg.norm(acc), 1):.2f}", xx, y + 181, self.fp)

    # ------------------------------------------------------------------
    def ejecutar(self):
        seguir = True
        while seguir:
            seguir = self.eventos()
            if not self.pausa:
                for _ in range(self.velocidad):
                    if self.mundo.activo[0]:
                        self.paso()
            if not self.mundo.activo[0]:
                self.fin_contador += 1
                if self.fin_contador > 90:          # 3 s y pasa a la siguiente semilla
                    self.semilla_idx += 1
                    self.reiniciar()
            self.pantalla.fill(FONDO)
            self.dibujar_mundo()
            self.dibujar_panel()
            if not self.mundo.activo[0]:
                self.texto("FIN DEL EPISODIO", MX + 260, MY + 260, self.fg, TINTA)
            pygame.display.flip()
            self.reloj.tick(30)
        pygame.quit()


if __name__ == "__main__":
    App().ejecutar()

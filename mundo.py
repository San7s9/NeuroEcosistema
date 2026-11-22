"""Simulación 2D de presas, depredadores, plantas y obstáculos.

La clase `Mundo` simula B mundos independientes AL MISMO TIEMPO (vectorizado
con NumPy). Esto se usa así:
  * Entrenamiento: cada mundo prueba un genoma distinto.
  * Experimentos: cada mundo es una repetición con otra semilla.
  * Visualización: B = 1.

Reglas (en cada paso):
  1. Cada agente percibe su entorno (observaciones).
  2. Su política (red neuronal, reglas o aleatoria) devuelve un vector de
     movimiento a en [-1, 1]^2 (se limita a longitud <= 1).
  3. Se mueve a * velocidad_máxima. Las paredes y los obstáculos lo detienen.
  4. Gasta energía: costo_base + costo_mov * |a|^2.
  5. Una presa que toca una planta activa la come (+energía).
  6. Un depredador que toca una presa la captura (+energía, la presa muere).
  7. Muere de hambre quien llega a energía 0.
  8. Las plantas comidas rebrotan con cierta probabilidad en otro lugar.
El episodio termina al llegar a `pasos_max` o cuando no quedan presas.
"""
import numpy as np

SIN_TIEMPO = np.nan


def _limitar_norma(a):
    n = np.linalg.norm(a, axis=-1, keepdims=True)
    return np.where(n > 1.0, a / np.maximum(n, 1e-9), a)


def _mas_cercano(origen, destino, mascara, radio):
    """Para cada agente de `origen` busca el objetivo más cercano en `destino`.

    origen: (B, N, 2), destino: (B, M, 2), mascara: (B, M) objetivos válidos.
    Devuelve:
      obs  (B, N, 3): (dx/radio, dy/radio, cercanía = 1 - d/radio); ceros si no
           hay objetivo dentro del radio de visión.
      idx  (B, N)   : índice del objetivo más cercano.
      dist (B, N)   : distancia (inf si no hay objetivos).
    """
    B, N = origen.shape[:2]
    if destino.shape[1] == 0:
        return np.zeros((B, N, 3)), np.zeros((B, N), int), np.full((B, N), np.inf)
    delta = destino[:, None, :, :] - origen[:, :, None, :]       # B,N,M,2
    d = np.linalg.norm(delta, axis=-1)
    d = np.where(mascara[:, None, :], d, np.inf)
    idx = np.argmin(d, axis=2)
    dist = np.take_along_axis(d, idx[..., None], axis=2)[..., 0]
    vec = np.take_along_axis(delta, idx[..., None, None], axis=2)[:, :, 0, :]
    visible = (dist < radio)[..., None]
    obs = np.concatenate([vec / radio, (1 - dist / radio)[..., None]], axis=-1)
    return np.where(visible, obs, 0.0), idx, dist


class Mundo:
    def __init__(self, cfg, semillas):
        self.cfg = cfg
        self.semillas = list(semillas)
        self.B = len(self.semillas)
        self.reiniciar()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------
    def reiniciar(self):
        c, B = self.cfg, self.B
        Np, Nd, Nf, No = c["presas"], c["depredadores"], c["plantas"], c["obstaculos"]
        W, H, R = c["ancho"], c["alto"], c["obstaculo_radio"]

        self.obst = np.zeros((B, No, 2))
        self.presa_pos = np.zeros((B, Np, 2))
        self.depr_pos = np.zeros((B, Nd, 2))
        self.planta_pos = np.zeros((B, Nf, 2))
        for b, s in enumerate(self.semillas):
            # Cada mundo se genera con SU semilla: el mundo b es idéntico sin
            # importar cuántos mundos se simulen juntos.
            rng = np.random.default_rng(s)
            self.obst[b] = rng.uniform([R + 60, R + 60], [W - R - 60, H - R - 60], (No, 2))
            self.presa_pos[b] = rng.uniform([20, 20], [W - 20, H - 20], (Np, 2))
            self.depr_pos[b] = rng.uniform([20, 20], [W - 20, H - 20], (Nd, 2))
            self.planta_pos[b] = rng.uniform([15, 15], [W - 15, H - 15], (Nf, 2))
        # Generador para el rebrote de plantas (depende de todas las semillas).
        self.rng = np.random.default_rng(self.semillas)
        self.presa_pos = self._fuera_de_obstaculos(self.presa_pos, c["presa_radio"])
        self.depr_pos = self._fuera_de_obstaculos(self.depr_pos, c["depr_radio"])
        self.planta_pos = self._fuera_de_obstaculos(self.planta_pos, 4)

        self.presa_vel = np.zeros((B, Np, 2))
        self.depr_vel = np.zeros((B, Nd, 2))
        self.presa_energia = np.full((B, Np), c["presa_energia_inicial"])
        self.depr_energia = np.full((B, Nd), c["depr_energia_inicial"])
        self.presa_viva = np.ones((B, Np), bool)
        self.depr_vivo = np.ones((B, Nd), bool)
        self.planta_activa = np.ones((B, Nf), bool)

        # Registro para las métricas
        self.paso = 0
        self.activo = np.ones(B, bool)                 # mundo aún en curso
        self.pasos_episodio = np.zeros(B, int)
        self.presa_muerte = np.full((B, Np), c["pasos_max"])  # paso de muerte
        self.presa_comida = np.zeros((B, Np))
        self.presa_hambre = np.zeros((B, Np), bool)     # murió de hambre
        self.depr_capturas = np.zeros((B, Nd))
        self.depr_hambre = np.zeros((B, Nd), bool)
        self.suma_t_captura = np.zeros(B)
        self.primera_captura = np.full(B, np.nan)

    def _fuera_de_obstaculos(self, pos, radio_agente):
        """Empuja cualquier punto que quede dentro de un obstáculo hasta su borde."""
        if self.obst.shape[1] == 0:
            return pos
        R = self.cfg["obstaculo_radio"] + radio_agente
        for k in range(self.obst.shape[1]):
            c = self.obst[:, k:k + 1, :]
            delta = pos - c
            d = np.linalg.norm(delta, axis=-1, keepdims=True)
            dentro = d < R
            unit = np.where(d > 1e-6, delta / np.maximum(d, 1e-6), [1.0, 0.0])
            pos = np.where(dentro, c + unit * R, pos)
        return pos

    # ------------------------------------------------------------------
    # Percepción
    # ------------------------------------------------------------------
    def _obs_obstaculo(self, pos, vision):
        """(ux, uy) hacia el obstáculo más cercano * cercanía, y la cercanía."""
        B, N = pos.shape[:2]
        if self.obst.shape[1] == 0:
            return np.zeros((B, N, 3))
        delta = self.obst[:, None, :, :] - pos[:, :, None, :]
        d = np.linalg.norm(delta, axis=-1)
        borde = d - self.cfg["obstaculo_radio"]
        idx = np.argmin(borde, axis=2)
        b_min = np.take_along_axis(borde, idx[..., None], 2)[..., 0]
        d_min = np.take_along_axis(d, idx[..., None], 2)[..., 0]
        vec = np.take_along_axis(delta, idx[..., None, None], 2)[:, :, 0, :]
        cerca = np.clip(1 - b_min / vision, 0, 1)
        unit = vec / np.maximum(d_min, 1e-6)[..., None]
        return np.concatenate([unit * cerca[..., None], cerca[..., None]], -1)

    def _posicion_normalizada(self, pos):
        W, H = self.cfg["ancho"], self.cfg["alto"]
        return np.stack([2 * pos[..., 0] / W - 1, 2 * pos[..., 1] / H - 1], -1)

    def observaciones_presas(self):
        """12 entradas por presa:
        [0:3]  planta más cercana (dx, dy, cercanía)
        [3:6]  depredador más cercano (dx, dy, cercanía)
        [6:9]  obstáculo más cercano (ux, uy, cercanía)
        [9]    energía propia
        [10:12] posición normalizada (x, y) en [-1, 1] -> para evitar paredes
        """
        c = self.cfg
        v = c["presa_vision"]
        planta, _, _ = _mas_cercano(self.presa_pos, self.planta_pos, self.planta_activa, v)
        depr, _, _ = _mas_cercano(self.presa_pos, self.depr_pos, self.depr_vivo, v)
        obst = self._obs_obstaculo(self.presa_pos, v)
        return np.concatenate([planta, depr, obst, self.presa_energia[..., None],
                               self._posicion_normalizada(self.presa_pos)], -1)

    def observaciones_depredadores(self):
        """11 entradas por depredador:
        [0:3]  presa más cercana (dx, dy, cercanía)
        [3:5]  velocidad de esa presa / vel. máx. de presa (para anticiparla)
        [5:8]  obstáculo más cercano (ux, uy, cercanía)
        [8]    energía propia
        [9:11] posición normalizada (x, y)
        """
        c = self.cfg
        v = c["depr_vision"]
        presa, idx, dist = _mas_cercano(self.depr_pos, self.presa_pos, self.presa_viva, v)
        vel = np.take_along_axis(self.presa_vel, idx[..., None], 1) / c["presa_vel_max"]
        vel = np.where((dist < v)[..., None], vel, 0.0)
        obst = self._obs_obstaculo(self.depr_pos, v)
        return np.concatenate([presa, vel, obst, self.depr_energia[..., None],
                               self._posicion_normalizada(self.depr_pos)], -1)

    # ------------------------------------------------------------------
    # Dinámica
    # ------------------------------------------------------------------
    def _mover(self, pos, accion, vmax, radio):
        W, H = self.cfg["ancho"], self.cfg["alto"]
        vel = accion * vmax
        pos = pos + vel
        pos[..., 0] = np.clip(pos[..., 0], radio, W - radio)
        pos[..., 1] = np.clip(pos[..., 1], radio, H - radio)
        return self._fuera_de_obstaculos(pos, radio), vel

    def paso_simulacion(self, accion_presas, accion_depr):
        """Avanza un paso. Las acciones vienen de las políticas (B, N, 2)."""
        c = self.cfg
        act = self.activo[:, None]
        vp = (self.presa_viva & act)[..., None]
        vd = (self.depr_vivo & act)[..., None]
        ap = np.where(vp, _limitar_norma(accion_presas), 0.0)
        ad = np.where(vd, _limitar_norma(accion_depr), 0.0)

        # 3. Movimiento
        nuevo, vel = self._mover(self.presa_pos, ap, c["presa_vel_max"], c["presa_radio"])
        self.presa_pos = np.where(vp, nuevo, self.presa_pos)
        self.presa_vel = vel
        nuevo, vel = self._mover(self.depr_pos, ad, c["depr_vel_max"], c["depr_radio"])
        self.depr_pos = np.where(vd, nuevo, self.depr_pos)
        self.depr_vel = vel

        # 4. Gasto de energía
        self.presa_energia -= vp[..., 0] * (c["presa_costo_base"]
                                            + c["presa_costo_mov"] * (ap ** 2).sum(-1))
        self.depr_energia -= vd[..., 0] * (c["depr_costo_base"]
                                           + c["depr_costo_mov"] * (ad ** 2).sum(-1))

        # 5. Comer: cada planta la come la presa viva más cercana dentro del radio
        if self.planta_pos.shape[1]:
            d = np.linalg.norm(self.planta_pos[:, None] - self.presa_pos[:, :, None], axis=-1)
            d = np.where(vp & self.planta_activa[:, None, :], d, np.inf)
            quien = np.argmin(d, axis=1)                         # B, Nf
            comida = np.take_along_axis(d, quien[:, None], 1)[:, 0] < c["radio_comer"]
            b_idx, f_idx = np.nonzero(comida)
            p_idx = quien[b_idx, f_idx]
            np.add.at(self.presa_energia, (b_idx, p_idx), c["planta_energia"])
            np.add.at(self.presa_comida, (b_idx, p_idx), 1)
            self.planta_activa[b_idx, f_idx] = False
            np.clip(self.presa_energia, None, 1.0, out=self.presa_energia)

        # 6. Captura: cada presa la atrapa el depredador vivo más cercano
        if self.depr_pos.shape[1]:
            d = np.linalg.norm(self.presa_pos[:, None] - self.depr_pos[:, :, None], axis=-1)
            d = np.where(vd & (self.presa_viva & act)[:, None, :], d, np.inf)
            quien = np.argmin(d, axis=1)                         # B, Np
            capt = np.take_along_axis(d, quien[:, None], 1)[:, 0] < c["radio_captura"]
            b_idx, p_idx = np.nonzero(capt)
            d_idx = quien[b_idx, p_idx]
            np.add.at(self.depr_capturas, (b_idx, d_idx), 1)
            np.add.at(self.depr_energia, (b_idx, d_idx), c["captura_energia"])
            np.clip(self.depr_energia, None, 1.0, out=self.depr_energia)
            self.presa_viva[b_idx, p_idx] = False
            self.presa_muerte[b_idx, p_idx] = self.paso + 1
            n_capt = capt.sum(1)
            self.suma_t_captura += n_capt * (self.paso + 1)
            nuevas = (n_capt > 0) & np.isnan(self.primera_captura)
            self.primera_captura[nuevas] = self.paso + 1

        # 7. Muerte por hambre
        hambre_p = self.presa_viva & (self.presa_energia <= 0)
        self.presa_viva &= ~hambre_p
        self.presa_hambre |= hambre_p
        self.presa_muerte[hambre_p] = self.paso + 1
        hambre_d = self.depr_vivo & (self.depr_energia <= 0)
        self.depr_vivo &= ~hambre_d
        self.depr_hambre |= hambre_d
        np.clip(self.presa_energia, 0, None, out=self.presa_energia)
        np.clip(self.depr_energia, 0, None, out=self.depr_energia)

        # 8. Rebrote de plantas en una posición nueva
        brota = (~self.planta_activa) & (self.rng.random(self.planta_activa.shape) < c["rebrote"])
        if brota.any():
            nuevas = self.rng.uniform([15, 15], [c["ancho"] - 15, c["alto"] - 15],
                                      self.planta_pos.shape)
            nuevas = self._fuera_de_obstaculos(nuevas, 4)
            self.planta_pos = np.where(brota[..., None], nuevas, self.planta_pos)
            self.planta_activa |= brota

        # Fin de episodio
        self.paso += 1
        self.pasos_episodio[self.activo] = self.paso
        termina = (self.presa_viva.sum(1) == 0) | (self.paso >= c["pasos_max"])
        self.activo &= ~termina
        return self.activo.any()

    def correr(self, politica_presas, politica_depr):
        """Corre el episodio completo y devuelve las métricas por mundo."""
        while self.activo.any():
            self.paso_simulacion(politica_presas(self.observaciones_presas()),
                                 politica_depr(self.observaciones_depredadores()))
        return self.metricas()

    # ------------------------------------------------------------------
    # Métricas
    # ------------------------------------------------------------------
    def vida_presas(self):
        """Pasos vividos por cada presa (las vivas cuentan hasta el final)."""
        return np.where(self.presa_viva, self.pasos_episodio[:, None], self.presa_muerte)

    def metricas(self):
        T = self.cfg["pasos_max"]
        capturas = self.depr_capturas.sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            e_presa = np.where(self.presa_viva.any(1),
                               (self.presa_energia * self.presa_viva).sum(1)
                               / np.maximum(self.presa_viva.sum(1), 1), 0.0)
            e_depr = np.where(self.depr_vivo.any(1),
                              (self.depr_energia * self.depr_vivo).sum(1)
                              / np.maximum(self.depr_vivo.sum(1), 1), 0.0)
            t_medio = np.where(capturas > 0, self.suma_t_captura / np.maximum(capturas, 1), np.nan)
        return {
            "semilla": np.array(self.semillas),
            "pasos": self.pasos_episodio.copy(),
            "supervivencia_presas": self.presa_viva.mean(1),           # fracción viva al final
            "vida_media_presas": self.vida_presas().mean(1) / T,       # fracción del episodio
            "comida_total": self.presa_comida.sum(1),
            "capturas": capturas,
            "presas_muertas_hambre": self.presa_hambre.sum(1),
            "depr_muertos_hambre": self.depr_hambre.sum(1),
            "energia_final_presas": e_presa,     # media de las presas vivas (0 si no hay)
            "energia_final_depr": e_depr,        # media de los depredadores vivos
            "t_primera_captura": self.primera_captura.copy(),   # NaN si no hubo
            "t_medio_captura": t_medio,
        }

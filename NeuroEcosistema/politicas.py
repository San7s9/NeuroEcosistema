"""Políticas: funciones que convierten observaciones en movimiento.

Todas reciben obs (B, N, entradas) y devuelven acciones (B, N, 2) en [-1, 1].

* PoliticaNeuronal: la decisión sale de la red (esto es lo que se entrena).
* PoliticaReglas*:  referencia programada a mano con LA MISMA información que
                    la red (mismas observaciones), para que la comparación sea justa.
* PoliticaAleatoria: referencia sin inteligencia (camina al azar).
"""
import numpy as np

from red import adelante


class PoliticaNeuronal:
    nombre = "red"

    def __init__(self, capas, activacion="tanh", anuladas=()):
        self.capas = capas
        self.activacion = activacion
        self.anuladas = list(anuladas)
        self.ultimas_ocultas = None   # para inspeccionar la red en la simulación
        self.ultimas_salidas = None

    def __call__(self, obs):
        if self.anuladas:
            obs = obs.copy()
            obs[..., self.anuladas] = 0.0
        self.ultimas_entradas = obs
        salida, ocultas = adelante(self.capas, obs, self.activacion, devolver_ocultas=True)
        self.ultimas_ocultas, self.ultimas_salidas = ocultas, salida
        return salida


class PoliticaAleatoria:
    """Caminata aleatoria persistente: mantiene rumbo y lo cambia poco a poco.

    (Una dirección totalmente nueva en cada paso dejaría al agente quieto en
    promedio; esta versión explora el mapa, así que es una referencia más justa.)
    """
    nombre = "aleatoria"

    def __init__(self, semilla, velocidad=0.6):
        self.rng = np.random.default_rng(semilla)
        self.velocidad = velocidad
        self.angulo = None

    def __call__(self, obs):
        if self.angulo is None or self.angulo.shape != obs.shape[:2]:
            self.angulo = self.rng.uniform(0, 2 * np.pi, obs.shape[:2])
        self.angulo += self.rng.normal(0, 0.35, self.angulo.shape)
        return self.velocidad * np.stack([np.cos(self.angulo), np.sin(self.angulo)], -1)


def _unitario(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def _evitar_paredes(pos_norm, umbral=0.85):
    """Empuja hacia el centro cuando la posición normalizada pasa de ±umbral."""
    return -np.sign(pos_norm) * (np.abs(pos_norm) > umbral)


class PoliticaReglasPresa:
    """Si ve un depredador, huye; si no, va a la planta más cercana; si no, deambula."""
    nombre = "reglas"

    def __init__(self, semilla):
        self.deambular = PoliticaAleatoria(semilla, velocidad=0.5)

    def __call__(self, obs):
        planta, depr, obst = obs[..., 0:3], obs[..., 3:6], obs[..., 6:9]
        pos = obs[..., 10:12]
        paseo = self.deambular(obs)
        repulsion = -obst[..., 0:2] * 2.0 + _evitar_paredes(pos)
        huir = _unitario(-depr[..., 0:2] + repulsion)
        ir_planta = 0.8 * _unitario(planta[..., 0:2] + 0.5 * repulsion)
        ve_depr = depr[..., 2:3] > 0
        ve_planta = planta[..., 2:3] > 0
        return np.where(ve_depr, huir, np.where(ve_planta, ir_planta, paseo + 0.5 * repulsion))


class PoliticaReglasDepredador:
    """Persigue a la presa más cercana anticipando su movimiento; si no ve, deambula."""
    nombre = "reglas"

    def __init__(self, semilla, anticipacion=8.0, vision=170.0):
        self.deambular = PoliticaAleatoria(semilla, velocidad=0.5)
        self.anticipacion = anticipacion
        self.vision = vision

    def __call__(self, obs):
        presa, vel, obst = obs[..., 0:3], obs[..., 3:5], obs[..., 5:8]
        pos = obs[..., 9:11]
        paseo = self.deambular(obs)
        repulsion = -obst[..., 0:2] * 1.5 + _evitar_paredes(pos)
        # vector a la presa en píxeles + su desplazamiento esperado
        objetivo = presa[..., 0:2] * self.vision + vel * 2.0 * self.anticipacion
        perseguir = _unitario(_unitario(objetivo) + 0.3 * repulsion)
        ve = presa[..., 2:3] > 0
        return np.where(ve, perseguir, paseo + 0.5 * repulsion)

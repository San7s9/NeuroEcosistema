"""Red neuronal multicapa (MLP) escrita a mano con NumPy.

Arquitectura: entradas -> oculta 1 (tanh) -> oculta 2 (tanh) -> 2 salidas (tanh)

Los pesos de una red se guardan como un vector plano llamado "genoma". Así la
neuroevolución puede mutarlos y cruzarlos fácilmente. La función `desempacar`
convierte uno o varios genomas en matrices W y vectores b.

Para simular muchos mundos a la vez, la red trabaja "por lotes": se le pasa un
genoma por mundo (forma B x P) y las observaciones de todos los agentes de cada
mundo (forma B x N x entradas).
"""
import numpy as np

ACTIVACIONES = {
    "tanh": np.tanh,
    "relu": lambda z: np.maximum(z, 0.0),
}


def formas(entradas, ocultas, salidas):
    """Lista de (filas, columnas) de cada matriz de pesos."""
    tamanos = [entradas, *ocultas, salidas]
    return [(tamanos[i], tamanos[i + 1]) for i in range(len(tamanos) - 1)]


def num_parametros(entradas, ocultas, salidas):
    return sum(f * c + c for f, c in formas(entradas, ocultas, salidas))


def genoma_aleatorio(rng, entradas, ocultas, salidas):
    """Inicialización tipo Xavier: pesos ~ N(0, 1/entradas_de_la_capa), sesgos 0."""
    partes = []
    for f, c in formas(entradas, ocultas, salidas):
        partes.append(rng.normal(0.0, 1.0 / np.sqrt(f), f * c))
        partes.append(np.zeros(c))
    return np.concatenate(partes)


def desempacar(genomas, entradas, ocultas, salidas):
    """genomas: (B, P) -> lista de capas [(W: B x f x c, b: B x c), ...]."""
    genomas = np.atleast_2d(genomas)
    capas, i = [], 0
    for f, c in formas(entradas, ocultas, salidas):
        W = genomas[:, i:i + f * c].reshape(-1, f, c)
        i += f * c
        b = genomas[:, i:i + c]
        i += c
        capas.append((W, b))
    return capas


def adelante(capas, X, activacion="tanh", devolver_ocultas=False):
    """Propagación hacia adelante.

    X: (B, N, entradas) observaciones de N agentes en B mundos.
    Devuelve las salidas (B, N, 2) en [-1, 1] y, si se pide, las activaciones
    de cada capa oculta (para el panel de inspección de la simulación).
    """
    f = ACTIVACIONES[activacion]
    a = X
    ocultas = []
    for k, (W, b) in enumerate(capas):
        z = np.einsum("bni,bio->bno", a, W) + b[:, None, :]
        if k < len(capas) - 1:
            a = f(z)
            ocultas.append(a)
        else:
            a = np.tanh(z)  # la salida siempre es tanh: dirección en [-1, 1]
    return (a, ocultas) if devolver_ocultas else a


class Cerebro:
    """Una red concreta (un genoma) con su arquitectura. Se guarda en .npz."""

    def __init__(self, genoma, entradas, ocultas, salidas=2, activacion="tanh",
                 anuladas=()):
        self.genoma = np.asarray(genoma, dtype=float)
        self.entradas, self.ocultas = entradas, tuple(ocultas)
        self.salidas, self.activacion = salidas, activacion
        # Índices de entradas que se fuerzan a 0 (experimento de "sentidos").
        self.anuladas = tuple(int(i) for i in anuladas)
        assert self.genoma.size == num_parametros(entradas, self.ocultas, salidas)

    def capas(self, B=1):
        """Repite el mismo genoma en B mundos."""
        return desempacar(np.tile(self.genoma, (B, 1)), self.entradas,
                          self.ocultas, self.salidas)

    def guardar(self, ruta, **extra):
        np.savez(ruta, genoma=self.genoma, entradas=self.entradas,
                 ocultas=np.array(self.ocultas), salidas=self.salidas,
                 activacion=self.activacion, anuladas=np.array(self.anuladas, int),
                 **extra)

    @classmethod
    def cargar(cls, ruta):
        d = np.load(ruta, allow_pickle=False)
        return cls(d["genoma"], int(d["entradas"]),
                   tuple(int(x) for x in d["ocultas"]),
                   int(d["salidas"]), str(d["activacion"]),
                   tuple(d["anuladas"]) if "anuladas" in d else ())

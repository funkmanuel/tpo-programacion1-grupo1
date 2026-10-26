"""Armas y disparos de la entrega 2."""


import tablero
import flota


class ArmamentoError(Exception):
    """error de armamento"""
    pass


class PuntoInvalidoError(ArmamentoError):
    """punto invalido"""
    pass


class ArmaInvalidaError(ArmamentoError):
    """arma invalida"""
    pass


class SinMunicionError(ArmamentoError):
    """sin municion"""
    pass


class DisparoRepetidoError(ArmamentoError):
    """disparo repetido"""
    pass


CATALOGO_ARMAS = {
    "T": {"nombre": "torpedo", "municion": None},
    "R": {"nombre": "misil de racimo", "municion": 3},
    "C": {"nombre": "carga de profundidad", "municion": 2},
    "S": {"nombre": "sonar", "municion": 4},
    "L": {"nombre": "barrido laser", "municion": 2},
    "O": {"nombre": "onda expansiva", "municion": 1},
    "G": {"nombre": "torpedo guiado", "municion": 1},
}


def inventario_inicial():
    """municion inicial"""
    inventario = {}
    for letra, datos in CATALOGO_ARMAS.items():
        inventario[letra] = datos["municion"]
    return inventario


def validar_municion(inventario, arma):
    """chequea municion"""
    if arma not in inventario:
        raise ArmaInvalidaError("El arma no pertenece al inventario.")
    cantidad = inventario[arma]
    if cantidad is not None and cantidad <= 0:
        raise SinMunicionError("No queda municion para esa arma.")


def consumir_municion(inventario, arma):
    """resta una unidad"""
    validar_municion(inventario, arma)
    if inventario[arma] is not None:
        inventario[arma] -= 1
    return inventario


def validar_formato_punto(punto):
    """punto = 3 enteros"""
    if not isinstance(punto, (tuple, list)) or len(punto) != 3:
        raise PuntoInvalidoError("El punto debe tener tres coordenadas.")
    for coordenada in punto:
        if type(coordenada) != int:
            raise PuntoInvalidoError("Las coordenadas deben ser numeros enteros.")


def validar_punto(cubo, punto):
    """valida punto en el cubo"""
    validar_formato_punto(punto)
    if not tablero.punto_valido(punto, tablero.tamanio(cubo)):
        raise PuntoInvalidoError("El punto esta fuera del cubo.")
    return tuple(punto)


def afectar_celda(cubo, punto, flota_defensor=None, arma="T"):
    """afecta una celda"""
    if not tablero.punto_valido(punto, tablero.tamanio(cubo)):
        return "fuera_de_rango"
    punto = tuple(punto)
    estado = tablero.leer_celda(cubo, punto)
    if estado in (tablero.AGUA_MARCADA, tablero.HUNDIDO):
        return "repetido"

    if flota_defensor is not None:
        id_nave, datos = flota.buscar_nave_por_punto(flota_defensor, punto)
        if id_nave is not None:
            if arma == "L" and datos["tipo"] == "S":
                return "inmune"
            resultado = flota.registrar_impacto(flota_defensor, cubo, punto)
            if resultado["repetido"]:
                return "repetido"
            if resultado["se_hundio"]:
                return "hundido"
            return "impacto"

    if estado == tablero.AGUA:
        tablero.escribir_celda(cubo, punto, tablero.AGUA_MARCADA)
        return "agua"
    if estado in (tablero.NAVE, tablero.DETECTADO):
        tablero.escribir_celda(cubo, punto, tablero.IMPACTO)
        return "impacto"
    if estado == tablero.IMPACTO:
        return "repetido"
    raise ArmamentoError("La celda tiene un estado desconocido.")


def aplicar_puntos(cubo, puntos, flota_defensor, arma):
    """afecta varios puntos"""
    resultados = {}
    for punto in puntos:
        resultado = afectar_celda(cubo, punto, flota_defensor, arma)
        if resultado != "fuera_de_rango":
            resultados[punto] = resultado
    return cubo, resultados


def torpedo(cubo, punto, eje=None, flota_defensor=None):
    """una celda"""
    punto = validar_punto(cubo, punto)
    return aplicar_puntos(cubo, [punto], flota_defensor, "T")


def misil_racimo(cubo, punto, eje=None, flota_defensor=None):
    """punto + vecinos"""
    punto = validar_punto(cubo, punto)
    puntos = [punto]
    for vecino in tablero.vecinos_ortogonales(punto, tablero.tamanio(cubo)):
        puntos.append(vecino)
    return aplicar_puntos(cubo, puntos, flota_defensor, "R")


def carga_profundidad(cubo, punto, eje=None, flota_defensor=None):
    """recta en z"""
    punto = validar_punto(cubo, punto)
    z, x, y = punto
    puntos = []
    for z_actual in range(1, tablero.tamanio(cubo) + 1):
        puntos.append((z_actual, x, y))
    return aplicar_puntos(cubo, puntos, flota_defensor, "C")


def puntos_laser_x(n, punto):
    """recta en x"""
    z, x, y = punto
    puntos = []
    for x_actual in range(1, n + 1):
        puntos.append((z, x_actual, y))
    return puntos


def puntos_laser_y(n, punto):
    """recta en y"""
    z, x, y = punto
    puntos = []
    for y_actual in range(1, n + 1):
        puntos.append((z, x, y_actual))
    return puntos


RECORRIDOS_LASER = {"x": puntos_laser_x, "y": puntos_laser_y}


def barrido_laser(cubo, punto, eje="x", flota_defensor=None):
    """recta x o y"""
    punto = validar_punto(cubo, punto)
    if not isinstance(eje, str):
        raise ArmamentoError("El eje del laser debe ser x o y.")
    eje = eje.strip().lower()
    if eje not in RECORRIDOS_LASER:
        raise ArmamentoError("El eje del laser debe ser x o y.")
    funcion_recorrido = RECORRIDOS_LASER[eje]
    puntos = funcion_recorrido(tablero.tamanio(cubo), punto)
    return aplicar_puntos(cubo, puntos, flota_defensor, "L")


ARMAS_DISPONIBLES = {
    "T": torpedo,
    "R": misil_racimo,
    "C": carga_profundidad,
    "L": barrido_laser,
}


def disparar(cubo, arma, punto, eje="x", flota_defensor=None, inventario=None):
    """elige el arma y dispara"""
    if not isinstance(arma, str):
        raise ArmaInvalidaError("El codigo del arma debe ser texto.")
    arma = arma.strip().upper()
    if arma not in ARMAS_DISPONIBLES:
        raise ArmaInvalidaError("El arma no esta disponible en esta entrega.")
    punto = validar_punto(cubo, punto)
    if inventario is not None:
        validar_municion(inventario, arma)

    funcion_arma = ARMAS_DISPONIBLES[arma]
    cubo, resultados = funcion_arma(cubo, punto, eje, flota_defensor)
    hay_disparo_nuevo = False
    for resultado in resultados.values():
        if resultado != "repetido":
            hay_disparo_nuevo = True
    if not hay_disparo_nuevo:
        raise DisparoRepetidoError("Todas esas celdas ya fueron atacadas.")

    if inventario is not None:
        consumir_municion(inventario, arma)
    return cubo, resultados

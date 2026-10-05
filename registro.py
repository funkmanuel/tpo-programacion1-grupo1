"""Historial de la partida en memoria para la entrega 1."""


def crear_historial():
    """Devuelve una lista vacía nueva, sin recibir ni modificar datos."""
    historial = []
    return historial


def registrar_accion(historial, jugador, accion, detalle):
    """Recibe el historial y tres textos; agrega la acción y devuelve la misma lista."""
    registro = {
        "jugador": jugador,
        "accion": accion,
        "detalle": detalle,
    }

    historial.append(registro)
    return historial


def obtener_historial(historial):
    """Recibe el historial y devuelve copias de sus registros, sin modificarlo."""
    copia = []

    for registro in historial:
        copia.append(registro.copy())

    return copia

"""Historial, estadisticas y resumen en memoria para la entrega 2."""


def crear_historial():
    """lista vacia"""
    historial = []
    return historial


def registrar_accion(historial, jugador, accion, detalle):
    """agrega una accion"""
    registro = {
        "jugador": jugador,
        "accion": accion,
        "detalle": detalle,
    }
    historial.append(registro)
    return historial


def registrar_disparo(historial, jugador, arma, resultados, hundidas):
    """agrega un disparo"""
    registro = {
        "jugador": jugador,
        "accion": "disparo",
        "detalle": f"Disparo con {arma}",
        "arma": arma,
        "resultados": resultados.copy(),
        "hundidas": hundidas.copy(),
    }
    historial.append(registro)
    return historial


def registrar_sonar(historial, jugador, eje, valor, contactos):
    """agrega un sonar"""
    registro = {
        "jugador": jugador,
        "accion": "sonar",
        "detalle": f"Plano {eje} = {valor}: {len(contactos)} contactos",
        "contactos": contactos.copy(),
    }
    historial.append(registro)
    return historial


def obtener_historial(historial):
    """copia del historial"""
    copia = []
    for registro in historial:
        nuevo = registro.copy()
        if "resultados" in registro:
            nuevo["resultados"] = registro["resultados"].copy()
        if "hundidas" in registro:
            nuevo["hundidas"] = registro["hundidas"].copy()
        if "contactos" in registro:
            nuevo["contactos"] = registro["contactos"].copy()
        copia.append(nuevo)
    return copia


def calcular_estadisticas(historial, jugador):
    """stats de un jugador"""
    estadisticas = {
        "disparos": 0,
        "aciertos": 0,
        "impactos": 0,
        "agua": 0,
        "hundimientos": 0,
        "sonares": 0,
        "contactos": 0,
        "precision": 0,
    }

    for registro in historial:
        if registro["jugador"] == jugador:
            if registro["accion"] == "disparo":
                estadisticas["disparos"] += 1
                impactos = 0
                for resultado in registro.get("resultados", {}).values():
                    if resultado in ("impacto", "hundido"):
                        impactos += 1
                    if resultado == "agua":
                        estadisticas["agua"] += 1
                estadisticas["impactos"] += impactos
                if impactos > 0:
                    estadisticas["aciertos"] += 1
                estadisticas["hundimientos"] += len(registro.get("hundidas", []))
            elif registro["accion"] == "sonar":
                estadisticas["sonares"] += 1
                estadisticas["contactos"] += len(registro.get("contactos", []))

    if estadisticas["disparos"] > 0:
        estadisticas["precision"] = estadisticas["aciertos"] * 100 / estadisticas["disparos"]
    return estadisticas


def generar_resumen(historial, jugadores, ganador):
    """resumen final"""
    resumen = {"ganador": ganador, "estadisticas": {}}
    for jugador in jugadores:
        resumen["estadisticas"][jugador] = calcular_estadisticas(historial, jugador)
    return resumen

"""Historial, estadisticas, guardado de partidas y ranking."""

import csv
import json
import re

import tablero


ARCHIVO_PARTIDAS = "partidas.json"
PATRON_NOMBRE = r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,49}$"


class RegistroError(Exception):
    """Error al guardar, cargar o exportar una partida."""


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


def _validar_nombre(nombre):
    """Devuelve el nombre sin espacios en los bordes o lanza RegistroError."""
    if isinstance(nombre, str):
        nombre = nombre.strip()
        if re.match(PATRON_NOMBRE, nombre):
            return nombre
    raise RegistroError("Use hasta 50 letras sin tilde, numeros, espacios o guiones. Empiece con una letra o un numero.")


def _leer_partidas():
    """Lee las partidas guardadas y sus ganadores."""
    try:
        with open(ARCHIVO_PARTIDAS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        return {"guardadas": {}, "terminadas": {}}
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise RegistroError("El archivo de partidas no tiene un JSON valido.")
    except OSError:
        raise RegistroError("No se pudo leer el archivo de partidas.")

    if not isinstance(datos, dict) or not isinstance(datos.get("guardadas"), dict) or not isinstance(datos.get("terminadas"), dict):
        raise RegistroError("El archivo de partidas no tiene el formato esperado.")
    return datos


def _escribir_partidas(datos):
    """Guarda los datos y devuelve la ruta del archivo escrito."""
    try:
        texto = json.dumps(datos, indent=4, ensure_ascii=False)
        with open(ARCHIVO_PARTIDAS, "w", encoding="utf-8") as archivo:
            archivo.write(texto)
    except (TypeError, ValueError):
        raise RegistroError("Hay datos de la partida que no se pueden guardar.")
    except OSError:
        raise RegistroError("No se pudo escribir el archivo de partidas.")
    return ARCHIVO_PARTIDAS


def _convertir_punto(punto, n, guardar):
    """Usa una lista en el JSON y una tupla en el juego."""
    if not tablero.punto_valido(punto, n):
        raise RegistroError("Hay una coordenada invalida en los datos de la partida.")
    if guardar:
        return list(punto)
    return tuple(punto)


def _convertir_coordenadas(datos, n, guardar):
    """Copia los datos y convierte los campos de coordenadas que tienen."""
    if not isinstance(datos, dict):
        raise RegistroError("Se esperaba un diccionario en los datos de la partida.")
    copia = datos.copy()
    for campo in ("celdas", "contactos", "disparos", "pendientes"):
        if campo in datos:
            puntos = []
            for punto in datos[campo]:
                puntos.append(_convertir_punto(punto, n, guardar))
            if not guardar and campo in ("disparos", "pendientes"):
                puntos = set(puntos)
            copia[campo] = puntos

    # En el archivo cada clave de coordenada se guarda junto a su valor en una lista.
    for campo in ("impactos_por_celda", "resultados"):
        if campo in datos:
            if guardar:
                filas = []
                for punto, valor in datos[campo].items():
                    filas.append([_convertir_punto(punto, n, guardar), valor])
                copia[campo] = filas
            else:
                valores = {}
                for punto, valor in datos[campo]:
                    coordenada = _convertir_punto(punto, n, guardar)
                    valores[coordenada] = valor
                copia[campo] = valores
    return copia


def _validar_cubo(cubo, n):
    """Revisa que el cubo tenga N capas de N filas de N celdas."""
    if not isinstance(cubo, list) or len(cubo) != n:
        raise RegistroError("El tamanio del cubo no coincide con el de la partida.")
    for capa in cubo:
        if not isinstance(capa, list) or len(capa) != n:
            raise RegistroError("Hay una capa invalida en el cubo guardado.")
        for fila in capa:
            if not isinstance(fila, list) or len(fila) != n:
                raise RegistroError("Hay una fila invalida en el cubo guardado.")


def _convertir_estado(estado, guardar):
    """Prepara una copia del estado para guardarla o volver a jugar."""
    try:
        n = estado["tamanio"]
        turno = estado["turno"]
        if not tablero.tamanio_valido(n) or type(turno) != int or turno not in (0, 1):
            raise RegistroError("El tamanio o el turno de la partida es invalido.")
        jugadores = estado["jugadores"]
        if not isinstance(jugadores, list) or len(jugadores) != 2 or not isinstance(estado["historial"], list):
            raise RegistroError("Faltan los jugadores o el historial de la partida.")
        ganador = estado["ganador"]
        if not isinstance(estado["cancelada"], bool) or (ganador is not None and not isinstance(ganador, str)):
            raise RegistroError("El estado final de la partida es invalido.")

        copia = estado.copy()
        copia["jugadores"] = []
        for jugador in jugadores:
            _validar_cubo(jugador["cubo"], n)
            if not isinstance(jugador["nombre"], str) or not isinstance(jugador["es_maquina"], bool):
                raise RegistroError("Hay un jugador invalido en la partida.")
            if not isinstance(jugador["municion"], dict) or "disparos" not in jugador or "pendientes" not in jugador:
                raise RegistroError("Faltan los datos de municion o disparos del jugador.")
            nuevo_jugador = _convertir_coordenadas(jugador, n, guardar)
            nueva_flota = {}
            for id_nave, nave in jugador["flota"].items():
                nueva_flota[id_nave] = _convertir_coordenadas(nave, n, guardar)
            nuevo_jugador["flota"] = nueva_flota
            copia["jugadores"].append(nuevo_jugador)

        copia["historial"] = []
        for accion in estado["historial"]:
            if "jugador" not in accion or "accion" not in accion:
                raise RegistroError("Hay una accion invalida en el historial.")
            copia["historial"].append(_convertir_coordenadas(accion, n, guardar))
        if estado["ultimo_turno"] is not None:
            copia["ultimo_turno"] = _convertir_coordenadas(estado["ultimo_turno"], n, guardar)
    except (AttributeError, KeyError, TypeError, ValueError):
        raise RegistroError("Los datos de la partida no tienen el formato esperado.")
    return copia


def guardar_partida(estado, nombre):
    """Guarda el estado con ese nombre y devuelve la ruta. Puede lanzar RegistroError."""
    nombre = _validar_nombre(nombre)
    partida = _convertir_estado(estado, True)
    datos = _leer_partidas()
    if nombre in datos["terminadas"]:
        raise RegistroError("Ya hay una partida terminada con ese nombre.")
    datos["guardadas"][nombre] = partida
    return _escribir_partidas(datos)


def cargar_partida(nombre):
    """Devuelve el estado guardado con ese nombre o lanza RegistroError."""
    nombre = _validar_nombre(nombre)
    guardadas = _leer_partidas()["guardadas"]
    if nombre not in guardadas:
        raise RegistroError("No se encontro la partida guardada.")
    return _convertir_estado(guardadas[nombre], False)


def listar_partidas():
    """Devuelve los nombres guardados en orden alfabetico. Puede lanzar RegistroError."""
    datos = _leer_partidas()
    return sorted(datos["guardadas"])


def registrar_resultado(estado, nombre):
    """Guarda el ganador de una partida terminada con un nombre unico y devuelve la ruta.

    Al terminar una partida retomada, recibe el mismo nombre con el que se guardo.
    Puede lanzar RegistroError si falta el ganador o el nombre ya se uso.
    """
    nombre = _validar_nombre(nombre)
    if not isinstance(estado, dict):
        raise RegistroError("El estado de la partida tiene que ser un diccionario.")
    ganador = estado.get("ganador")
    if not isinstance(ganador, str) or not ganador.strip() or estado.get("cancelada"):
        raise RegistroError("La partida tiene que terminar con un ganador para entrar en el ranking.")

    datos = _leer_partidas()
    if nombre in datos["terminadas"]:
        if datos["terminadas"][nombre] != ganador:
            raise RegistroError("Ya hay otra partida terminada con ese nombre.")
        return ARCHIVO_PARTIDAS

    datos["terminadas"][nombre] = ganador
    if nombre in datos["guardadas"]:
        del datos["guardadas"][nombre]
    return _escribir_partidas(datos)


def obtener_ranking():
    """Devuelve una lista de jugadores ordenada por victorias. Puede lanzar RegistroError."""
    victorias = {}
    datos = _leer_partidas()
    for ganador in datos["terminadas"].values():
        if not isinstance(ganador, str) or not ganador.strip():
            raise RegistroError("Hay un ganador invalido en el archivo de partidas.")
        victorias[ganador] = victorias.get(ganador, 0) + 1

    ranking = []
    for jugador in sorted(victorias):
        ranking.append({"jugador": jugador, "victorias": victorias[jugador]})
    ranking.sort(key=lambda fila: fila["victorias"], reverse=True)
    return ranking


def exportar_resumen(resumen, nombre):
    """Exporta el resultado de generar_resumen a CSV. Devuelve la ruta o lanza RegistroError."""
    nombre = _validar_nombre(nombre)
    ruta = f"resumen_{nombre}.csv"
    try:
        ganador = resumen["ganador"]
        filas = [["jugador", "gano", "disparos", "aciertos", "impactos", "agua",
                  "hundimientos", "sonares", "contactos", "precision"]]
        for jugador, datos in resumen["estadisticas"].items():
            filas.append([jugador, jugador == ganador, datos["disparos"], datos["aciertos"],
                          datos["impactos"], datos["agua"], datos["hundimientos"],
                          datos["sonares"], datos["contactos"], datos["precision"]])
        with open(ruta, "w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            for fila in filas:
                escritor.writerow(fila)
    except (AttributeError, KeyError, TypeError, ValueError):
        raise RegistroError("El resumen no tiene el formato esperado.")
    except (csv.Error, OSError):
        raise RegistroError("No se pudo escribir el resumen en CSV.")
    return ruta

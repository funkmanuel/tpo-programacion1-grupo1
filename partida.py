"""Menus, turnos, maquinas y partidas guardadas de Operacion Cubo."""

import random
import re

import tablero
import flota
import armamento
import radar
import registro


class ErrorJuego(Exception):
    """Error general del juego."""
    pass


class CoordenadaInvalidaError(ErrorJuego):
    """Coordenada fuera del cubo."""
    pass


class UbicacionNaveError(ErrorJuego):
    """Error al ubicar una flota."""
    pass


def pedir_opcion(mensaje, opciones):
    """Pide una opcion hasta recibir una valida."""
    while True:
        opcion = input(mensaje).strip().upper()
        if re.fullmatch(r"[A-Z0-9]", opcion) and opcion in opciones:
            return opcion
        print("Opcion invalida. Elija una de las opciones indicadas.")


def pedir_tamanio():
    """Pide el tamanio del cubo o usa el valor por defecto."""
    while True:
        texto = input(f"Tamanio del cubo ({tablero.N_MINIMO}-{tablero.N_MAXIMO}, Enter para 8): ").strip()
        if texto == "":
            return tablero.N_POR_DEFECTO
        if re.fullmatch(r"[0-9]{1,2}", texto):
            n = int(texto)
            if tablero.tamanio_valido(n):
                return n
        print("Tamanio invalido.")


def pedir_valor(n):
    """Pide un valor entre 1 y N."""
    while True:
        texto = input(f"Valor del plano (1-{n}): ").strip()
        if re.fullmatch(r"[0-9]{1,2}", texto):
            valor = int(texto)
            if 1 <= valor <= n:
                return valor
        print("Valor invalido.")


def pedir_punto(n):
    """Pide una coordenada del cubo."""
    while True:
        texto = input("Coordenadas z,x,y: ").strip()
        punto = tablero.texto_a_punto(texto, n)
        if punto is not None:
            return punto
        print("Coordenada invalida. Ejemplo: 2,3,4.")


def pedir_tramo(n):
    """Pide dos puntos para ubicar una nave."""
    while True:
        texto = input("Desde-hasta (ejemplo 2,3,4-2,3,5; 0 para volver): ").strip()
        if texto == "0":
            return None
        tramo = tablero.texto_a_tramo(texto, n)
        if tramo is not None:
            return tramo
        print("Tramo invalido.")


def pedir_nombre_partida():
    """Pide un nombre valido para una partida.
    Devuelve el nombre o None si el usuario vuelve al menu.
    """
    while True:
        nombre = input("Nombre de la partida (hasta 50 caracteres, 0 para volver): ").strip()
        if nombre == "0":
            return None
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]{0,49}", nombre):
            return nombre
        print("Nombre invalido. Use letras sin tilde, numeros, espacios o guiones.")


def mostrar_cubo(cubo, es_rival=False):
    """Dibuja todas las capas del cubo."""
    for z in range(1, tablero.tamanio(cubo) + 1):
        print(tablero.dibujar_capa_z(cubo, z, es_rival))
    print(tablero.referencias())


def ubicacion_manual(cubo, flota_jugador):
    """Recibe el cubo y la flota del jugador para ubicar las naves.
    Devuelve ambos actualizados o None si se cancela la ubicacion.
    """
    pendientes = {}
    for letra, datos in flota.CATALOGO_NAVES.items():
        cantidad = 0
        for nave in flota_jugador.values():
            if nave["tipo"] == letra:
                cantidad += 1
        pendientes[letra] = datos["cantidad"] - cantidad

    while sum(pendientes.values()) > 0:
        texto = "Pendientes: "
        for letra, cantidad in pendientes.items():
            if cantidad > 0:
                texto += f"{letra} x{cantidad}  "
        print(texto)
        letra = pedir_opcion("Nave F/D/S/C/P/E (0 para volver): ", ["F", "D", "S", "C", "P", "E", "0"])
        if letra == "0":
            return None
        if pendientes[letra] == 0:
            print("Ya se ubicaron todas las naves de ese tipo.")
        else:
            tramo = pedir_tramo(tablero.tamanio(cubo))
            if tramo is None:
                return None
            try:
                cubo, flota_jugador = flota.ubicar_nave(cubo, flota_jugador, letra, tramo[0], tramo[1])
            except ValueError as error:
                print(error)
            else:
                pendientes[letra] -= 1
                print("Nave ubicada.")
    return cubo, flota_jugador


def ubicacion_automatica(cubo, flota_jugador=None):
    """Recibe el cubo y devuelve el cubo con la flota ubicada.
    Puede lanzar UbicacionNaveError si no encuentra una ubicacion valida.
    """
    try:
        return flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES)
    except ValueError as error:
        raise UbicacionNaveError(str(error))


def cancelar_ubicacion(cubo, flota_jugador):
    """Cancela la preparacion de la flota."""
    return None


def preparar_flota(nombre, n, es_maquina=False):
    """Recibe el nombre, el tamanio y si juega una maquina.
    Devuelve el cubo y la flota, o None si el jugador cancela.
    """
    if es_maquina:
        return ubicacion_automatica(tablero.crear_cubo(n))
    acciones = {"1": ubicacion_manual, "2": ubicacion_automatica, "0": cancelar_ubicacion}
    while True:
        print(f"\n--- Flota de {nombre} ---")
        print("1 - Ubicacion manual")
        print("2 - Ubicacion automatica")
        print("0 - Volver al menu principal")
        opcion = pedir_opcion("Opcion: ", ["1", "2", "0"])
        try:
            return acciones[opcion](tablero.crear_cubo(n), {})
        except UbicacionNaveError as error:
            print(error)
            print("Puede intentar nuevamente o volver al menu principal.")


def crear_jugador(nombre, n, es_maquina=False, dificultad="basica"):
    """Recibe nombre, tamanio y tipo de jugador. Devuelve sus datos iniciales."""
    return {
        "nombre": nombre,
        "cubo": tablero.crear_cubo(n),
        "flota": {},
        "municion": armamento.inventario_inicial(),
        "es_maquina": es_maquina,
        "dificultad": dificultad,
        "disparos": set(),
        "pendientes": set(),
    }


def nueva_partida_1v1(configuracion):
    """Recibe la configuracion y devuelve el estado de la partida. Puede lanzar ErrorJuego."""
    if not isinstance(configuracion, dict):
        raise ErrorJuego("La configuracion debe ser un diccionario.")
    n = configuracion.get("tamanio", tablero.N_POR_DEFECTO)
    if not tablero.tamanio_valido(n):
        raise ErrorJuego("Tamanio de cubo invalido.")
    return {
        "tamanio": n,
        "jugadores": [crear_jugador("Jugador 1", n), crear_jugador("Jugador 2", n)],
        "turno": 0,
        "ganador": None,
        "cancelada": False,
        "historial": registro.crear_historial(),
        "ultimo_turno": None,
    }


def nueva_partida_vs_maquina(configuracion, dificultad="basica"):
    """Recibe configuracion y dificultad. Devuelve el estado. Puede lanzar ErrorJuego."""
    if dificultad not in ("basica", "avanzada"):
        raise ErrorJuego("Dificultad invalida.")
    estado = nueva_partida_1v1(configuracion)
    estado["jugadores"][1] = crear_jugador("Maquina", estado["tamanio"], True, dificultad)
    estado["dificultad"] = dificultad
    return estado


def nueva_partida_maquina_vs_maquina(configuracion, dificultades=("basica", "avanzada")):
    """Recibe la configuracion y las dificultades de ambas maquinas.
    Devuelve el estado inicial. Puede lanzar ErrorJuego.
    """
    if not isinstance(dificultades, (list, tuple)) or len(dificultades) != 2:
        raise ErrorJuego("Las dificultades deben ser dos valores.")
    dificultad_1, dificultad_2 = dificultades
    if dificultad_1 not in ("basica", "avanzada") or dificultad_2 not in ("basica", "avanzada"):
        raise ErrorJuego("Dificultad invalida.")
    estado = nueva_partida_1v1(configuracion)
    n = estado["tamanio"]
    estado["jugadores"] = [crear_jugador("Maquina 1", n, True, dificultad_1),
                           crear_jugador("Maquina 2", n, True, dificultad_2)]
    return estado


def procesar_disparo(cubo_defensor, flota_defensor, punto, arma="T", eje="x", municion=None):
    """Procesa un disparo contra la flota defensora.

    Recibe cubo, flota, punto, arma, eje y municion.
    Devuelve el cubo, los resultados y la lista de naves hundidas.
    Puede lanzar CoordenadaInvalidaError y errores de armamento.
    """
    if not tablero.punto_valido(punto, tablero.tamanio(cubo_defensor)):
        raise CoordenadaInvalidaError("El punto no pertenece al cubo.")
    estados_anteriores = {}
    for id_nave, datos in flota_defensor.items():
        estados_anteriores[id_nave] = datos["estado"]
    cubo, resultados = armamento.disparar(cubo_defensor, arma, punto, eje, flota_defensor, municion)
    hundidas = []
    for id_nave, datos in flota_defensor.items():
        if estados_anteriores[id_nave] != "hundida" and datos["estado"] == "hundida":
            hundidas.append(datos["nombre"])
    return cubo, resultados, hundidas


def aplicar_eventos(estado, resultados, hundidas):
    """Aplica los efectos especiales de las naves alcanzadas.

    Recibe el estado del juego, los resultados del disparo y las naves hundidas.
    Si se alcanza un destructor revela una celda rival. Si se hunde una
    estacion orbital entrega municion extra al atacante.
    No devuelve datos: actualiza el estado y el historial.
    """
    atacante = estado["jugadores"][estado["turno"]]
    defensor = estado["jugadores"][1 - estado["turno"]]
    for punto, resultado in resultados.items():
        if resultado in ("impacto", "hundido"):
            id_nave, datos = flota.buscar_nave_por_punto(defensor["flota"], punto)
            if id_nave is not None and datos["tipo"] == "D":
                ocultas, metricas = radar.buscar_nave_optimizada(atacante["cubo"], atacante["flota"])
                if ocultas:
                    celda = ocultas[0]
                    tablero.escribir_celda(atacante["cubo"], celda, tablero.DETECTADO)
                    registro.registrar_accion(estado["historial"], defensor["nombre"], "evento",
                                              f"Su destructor revelo la celda rival {celda}.")
    for datos in defensor["flota"].values():
        if datos["tipo"] == "E" and datos["nombre"] in hundidas:
            for arma in ("R", "C", "L", "S"):
                atacante["municion"][arma] += 1
            registro.registrar_accion(estado["historial"], atacante["nombre"], "evento",
                                      "Estacion orbital hundida: +1 de R, C, L y S.")


def aplicar_ataque(estado, jugada):
    """Recibe el estado y la jugada. Devuelve el resultado del ataque.
    Puede lanzar errores de coordenadas o armamento.
    """
    atacante = estado["jugadores"][estado["turno"]]
    defensor = estado["jugadores"][1 - estado["turno"]]
    cubo, resultados, hundidas = procesar_disparo(
        defensor["cubo"], defensor["flota"], jugada.get("punto"),
        jugada["arma"], jugada.get("eje", "x"), atacante["municion"])
    defensor["cubo"] = cubo
    for punto, resultado in resultados.items():
        if resultado != "inmune":
            atacante["disparos"].add(punto)
        if punto in atacante["pendientes"]:
            atacante["pendientes"].remove(punto)
        id_nave, datos = flota.buscar_nave_por_punto(defensor["flota"], punto)
        if id_nave is not None and datos["tipo"] == "P" and resultado == "impacto":
            if datos["impactos_por_celda"][punto] < 2:
                atacante["pendientes"].add(punto)
    registro.registrar_disparo(estado["historial"], atacante["nombre"], jugada["arma"], resultados, hundidas)
    aplicar_eventos(estado, resultados, hundidas)
    return {"jugador": atacante["nombre"], "arma": jugada["arma"], "resultados": resultados, "hundidas": hundidas}


def aplicar_sonar(estado, jugada):
    """Recibe el estado y los datos del sonar. Devuelve los contactos.
    Puede lanzar errores de municion o de plano.
    """
    atacante = estado["jugadores"][estado["turno"]]
    defensor = estado["jugadores"][1 - estado["turno"]]
    armamento.validar_municion(atacante["municion"], "S")
    cubo, contactos = radar.sonar_plano(defensor["cubo"], jugada.get("eje"), jugada.get("valor"))
    defensor["cubo"] = cubo
    armamento.consumir_municion(atacante["municion"], "S")
    registro.registrar_sonar(estado["historial"], atacante["nombre"], jugada["eje"], jugada["valor"], contactos)
    return {"jugador": atacante["nombre"], "arma": "S", "contactos": contactos}


ACCIONES_ARMAS = {
    "T": aplicar_ataque, "R": aplicar_ataque, "C": aplicar_ataque,
    "L": aplicar_ataque, "S": aplicar_sonar,
    "O": aplicar_ataque, "G": aplicar_ataque,
}


def hay_ganador(estado):
    """Devuelve el nombre del ganador o None."""
    jugadores = estado["jugadores"]
    if flota.flota_hundida(jugadores[1]["flota"]):
        return jugadores[0]["nombre"]
    if flota.flota_hundida(jugadores[0]["flota"]):
        return jugadores[1]["nombre"]
    return None


def ejecutar_turno(estado, jugada):
    """Recibe el estado y una jugada. Devuelve el estado actualizado.
    Puede lanzar ErrorJuego y errores de armamento.
    """
    if not isinstance(jugada, dict):
        raise ErrorJuego("La jugada debe ser un diccionario.")
    if estado["ganador"] is not None or estado["cancelada"]:
        raise ErrorJuego("La partida ya termino.")
    if not estado["jugadores"][0]["flota"] or not estado["jugadores"][1]["flota"]:
        raise ErrorJuego("Primero hay que ubicar ambas flotas.")
    arma = jugada.get("arma", "T")
    if not isinstance(arma, str) or arma.strip().upper() not in ACCIONES_ARMAS:
        raise armamento.ArmaInvalidaError("El arma no esta disponible.")
    jugada = jugada.copy()
    jugada["arma"] = arma.strip().upper()
    estado["ultimo_turno"] = ACCIONES_ARMAS[jugada["arma"]](estado, jugada)
    estado["ganador"] = hay_ganador(estado)
    if estado["ganador"] is None:
        estado["turno"] = 1 - estado["turno"]
    return estado


def puntos_disponibles(estado):
    """Lista las celdas que una maquina puede atacar."""
    maquina = estado["jugadores"][estado["turno"]]
    posibles = []
    for z in range(1, estado["tamanio"] + 1):
        for x in range(1, estado["tamanio"] + 1):
            for y in range(1, estado["tamanio"] + 1):
                punto = (z, x, y)
                if punto not in maquina["disparos"] or punto in maquina["pendientes"]:
                    posibles.append(punto)
    return posibles


def elegir_punto_maquina(estado):
    """Recibe el estado y devuelve una coordenada para la maquina.
    La dificultad avanzada usa el mapa de probabilidad sin leer naves ocultas.
    Puede lanzar ErrorJuego si no quedan puntos disponibles.
    """
    maquina = estado["jugadores"][estado["turno"]]
    posibles = puntos_disponibles(estado)
    if not posibles:
        raise ErrorJuego("La maquina no tiene celdas disponibles.")
    if maquina.get("dificultad", estado.get("dificultad", "basica")) == "avanzada":
        if maquina["pendientes"]:
            return sorted(maquina["pendientes"])[0]
        defensor = estado["jugadores"][1 - estado["turno"]]
        mapa = radar.mapa_probabilidad(defensor["cubo"])
        mejor_puntaje = -1
        mejores = []
        for z, x, y in posibles:
            puntaje = mapa[z - 1][x - 1][y - 1]
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejores = [(z, x, y)]
            elif puntaje == mejor_puntaje:
                mejores.append((z, x, y))
        return mejores[random.randint(0, len(mejores) - 1)]
    return posibles[random.randint(0, len(posibles) - 1)]


def turno_maquina(estado):
    """Recibe el estado y ejecuta el turno de la maquina actual.
    Devuelve el estado actualizado. Puede lanzar ErrorJuego si no es su turno.
    """
    maquina = estado["jugadores"][estado["turno"]]
    if not maquina["es_maquina"]:
        raise ErrorJuego("El turno actual no pertenece a la maquina.")
    punto = elegir_punto_maquina(estado)
    return ejecutar_turno(estado, {"arma": "T", "punto": punto})


def pedir_ataque(n):
    """Pide la coordenada de un arma."""
    return {"punto": pedir_punto(n)}


def pedir_laser(n):
    """Pide coordenada y eje de un laser."""
    punto = pedir_punto(n)
    eje = pedir_opcion("Eje X/Y: ", ["X", "Y"]).lower()
    return {"punto": punto, "eje": eje}


def pedir_sonar(n):
    """Pide eje y valor para un sonar."""
    eje = pedir_opcion("Eje Z/X/Y: ", ["Z", "X", "Y"]).lower()
    return {"eje": eje, "valor": pedir_valor(n)}


LECTURAS_ARMAS = {
    "T": pedir_ataque, "R": pedir_ataque, "C": pedir_ataque,
    "L": pedir_laser, "S": pedir_sonar,
    "O": pedir_ataque, "G": pedir_ataque,
}


def mostrar_ultimo_turno(estado):
    """Muestra el resultado del ultimo turno."""
    ultimo = estado["ultimo_turno"]
    print(f"\n{ultimo['jugador']} uso {ultimo['arma']}.")
    if "contactos" in ultimo:
        print("Contactos detectados:", len(ultimo["contactos"]))
    for punto, resultado in ultimo.get("resultados", {}).items():
        print(punto, resultado)
    for nombre in ultimo.get("hundidas", []):
        print("Nave hundida:", nombre)


def accion_disparar(estado):
    """Permite elegir arma y efectuar un disparo."""
    atacante = estado["jugadores"][estado["turno"]]
    for letra, datos in armamento.CATALOGO_ARMAS.items():
        cantidad = atacante["municion"][letra]
        texto = "ilimitada" if cantidad is None else str(cantidad)
        print(letra, datos["nombre"], "-", texto)
    arma = pedir_opcion("Arma T/R/C/S/L/O/G: ", list(ACCIONES_ARMAS))
    armamento.validar_municion(atacante["municion"], arma)
    jugada = LECTURAS_ARMAS[arma](estado["tamanio"])
    jugada["arma"] = arma
    ejecutar_turno(estado, jugada)
    mostrar_ultimo_turno(estado)
    return True


def mostrar_capas_turno(estado):
    """Muestra las capas del cubo propio y del rival."""
    propio = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]
    print("\nCubo propio:")
    mostrar_cubo(propio["cubo"])
    print("\nCubo rival:")
    mostrar_cubo(rival["cubo"], True)


def mostrar_corte_x(estado):
    """Muestra los cortes del cubo fijando X."""
    valor = pedir_valor(estado["tamanio"])
    propio = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]
    print("Cubo propio:")
    print(tablero.dibujar_plano_x(propio["cubo"], valor, False))
    print("Cubo rival:")
    print(tablero.dibujar_plano_x(rival["cubo"], valor, True))


def mostrar_corte_y(estado):
    """Muestra los cortes del cubo fijando Y."""
    valor = pedir_valor(estado["tamanio"])
    propio = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]
    print("Cubo propio:")
    print(tablero.dibujar_plano_y(propio["cubo"], valor, False))
    print("Cubo rival:")
    print(tablero.dibujar_plano_y(rival["cubo"], valor, True))


def accion_ver_cubo(estado):
    """Muestra una vista del cubo elegida en el submenu."""
    print("1 - Capas z")
    print("2 - Corte x")
    print("3 - Corte y")
    opcion = pedir_opcion("Vista: ", ["1", "2", "3"])
    vistas = {"1": mostrar_capas_turno, "2": mostrar_corte_x, "3": mostrar_corte_y}
    vistas[opcion](estado)
    return False


def mostrar_estadisticas(estado):
    """Muestra las estadisticas de ambos jugadores."""
    for jugador in estado["jugadores"]:
        datos = registro.calcular_estadisticas(estado["historial"], jugador["nombre"])
        print(f"\n--- Estadisticas de {jugador['nombre']} ---")
        print("Disparos:", datos["disparos"], "- con acierto:", datos["aciertos"])
        print("Impactos:", datos["impactos"], "- hundimientos:", datos["hundimientos"])
        print("Sonares:", datos["sonares"], "- contactos:", datos["contactos"])
        print(f"Precision: {datos['precision']:.2f}%")


def accion_historial(estado):
    """Muestra el historial y las estadisticas."""
    for accion in registro.obtener_historial(estado["historial"]):
        print(accion["jugador"], "-", accion["detalle"])
    mostrar_estadisticas(estado)
    return False


def accion_busquedas(estado):
    """Compara los resultados y las metricas de las tres busquedas.
    La optimizada revisa las posiciones de la flota en vez de recorrer
    todas las celdas del cubo. No consume un turno.
    """
    jugador = estado["jugadores"][estado["turno"]]
    lineales, datos_lineal = radar.buscar_nave_lineal(jugador["cubo"])
    optimizadas, datos_optimizada = radar.buscar_nave_optimizada(jugador["cubo"], jugador["flota"])
    recursivas, datos_recursiva = radar.buscar_nave_recursiva(jugador["cubo"])
    print("Lineal:", datos_lineal)
    print("Optimizada:", datos_optimizada)
    print("Recursiva:", datos_recursiva)
    print("Resultados coincidentes:", set(lineales) == set(optimizadas) == set(recursivas))
    return False


def accion_recorridos(estado):
    """Permite elegir uno de los tres recorridos del cubo."""
    print("1 - Por capas")
    print("2 - Capas recursivas")
    print("3 - Octantes recursivos")
    print("4 - Serpiente")
    print("5 - Espiral")
    opcion = pedir_opcion("Recorrido: ", ["1", "2", "3", "4", "5"])
    nombres = {"1": "capas", "2": "capas_recursivo", "3": "octantes",
               "4": "serpiente", "5": "espiral"}
    jugador = estado["jugadores"][estado["turno"]]
    if opcion in ("4", "5"):
        puntos = tablero.recorrer_tablero(jugador["cubo"], nombres[opcion])
    else:
        puntos = radar.recorrer_cubo(jugador["cubo"], nombres[opcion])
    print("Cantidad de celdas recorridas:", len(puntos))
    print("Primeras diez coordenadas:", puntos[:10])
    return False


def accion_guardar_salir(estado):
    """Recibe el estado, lo guarda en JSON y termina la partida actual.
    Devuelve False. Puede lanzar RegistroError.
    """
    nombre = pedir_nombre_partida()
    if nombre is None:
        return False
    ruta = registro.guardar_partida(estado, nombre)
    estado["nombre_partida"] = nombre
    estado["guardada"] = True
    estado["cancelada"] = True
    print("Partida guardada en:", ruta)
    return False


def accion_cancelar(estado):
    """Termina la partida actual sin guardarla."""
    estado["cancelada"] = True
    return False


def realizar_turno(estado):
    """Presenta el menu de un jugador humano."""
    acciones = {
        "1": accion_disparar,
        "2": accion_ver_cubo,
        "3": accion_guardar_salir,
        "4": accion_historial,
        "5": accion_busquedas,
        "6": accion_recorridos,
        "7": accion_cancelar,
    }
    realizado = False
    while not realizado and not estado["cancelada"]:
        print("\nTurno de:", estado["jugadores"][estado["turno"]]["nombre"])
        print("1 - Disparar o usar sonar")
        print("2 - Ver el cubo")
        print("3 - Guardar y salir")
        print("4 - Historial y estadisticas")
        print("5 - Comparar busquedas")
        print("6 - Recorridos del cubo")
        print("7 - Terminar esta partida")
        opcion = pedir_opcion("Opcion: ", list(acciones))
        try:
            realizado = acciones[opcion](estado)
        except (ErrorJuego, armamento.ArmamentoError, registro.RegistroError, ValueError) as error:
            print(error)


def mostrar_resumen(estado):
    """Muestra el resultado y devuelve los datos del resumen."""
    nombres = []
    for jugador in estado["jugadores"]:
        nombres.append(jugador["nombre"])
    resumen = registro.generar_resumen(estado["historial"], nombres, estado["ganador"])
    print("\n===== RESUMEN DE LA PARTIDA =====")
    if resumen["ganador"] is None:
        print("Partida terminada sin ganador.")
    else:
        print("Ganador:", resumen["ganador"])
    mostrar_estadisticas(estado)
    return resumen


def registrar_partida_terminada(estado, resumen):
    """Recibe el estado terminado y su resumen. Registra el resultado.
    Puede lanzar RegistroError al guardar o exportar.
    """
    nombre = estado.get("nombre_partida")
    if nombre is None:
        nombre = pedir_nombre_partida()
    if nombre is not None:
        ruta = registro.registrar_resultado(estado, nombre)
        print("Resultado registrado en:", ruta)
        if pedir_opcion("Exportar resumen a CSV (S/N): ", ["S", "N"]) == "S":
            ruta = registro.exportar_resumen(resumen, nombre)
            print("Resumen exportado a:", ruta)


def menu_simulacion(estado):
    """Muestra las opciones para avanzar o detener una simulacion.
    Devuelve la cantidad de turnos, -1 para jugar hasta el final
    o 0 cuando se guarda o termina la partida.
    """
    print("\n--- Simulacion entre maquinas ---")
    print("1 - Avanzar un turno")
    print("2 - Avanzar diez turnos")
    print("3 - Jugar hasta el final")
    print("4 - Guardar y salir")
    print("5 - Terminar sin guardar")
    opcion = pedir_opcion("Opcion: ", ["1", "2", "3", "4", "5"])
    turnos = {"1": 1, "2": 10, "3": -1}
    acciones = {"4": accion_guardar_salir, "5": accion_cancelar}
    if opcion in turnos:
        return turnos[opcion]
    acciones[opcion](estado)
    return 0


def jugar_partida(estado, continuar=False):
    """Recibe el estado y ejecuta la partida hasta que termine o se guarde.
    Devuelve el estado actualizado. Cuando continua una partida guardada,
    conserva las flotas, la municion, el historial y el turno anterior.
    Puede lanzar ErrorJuego si la partida guardada no tiene ambas flotas.
    """
    if not continuar:
        for jugador in estado["jugadores"]:
            resultado = preparar_flota(jugador["nombre"], estado["tamanio"], jugador["es_maquina"])
            if resultado is None:
                estado["cancelada"] = True
                print("Preparacion cancelada.")
                return estado
            jugador["cubo"], jugador["flota"] = resultado
            registro.registrar_accion(estado["historial"], jugador["nombre"], "ubicacion", "Flota ubicada.")
        confirmacion = pedir_opcion("Ambas flotas listas. Iniciar partida S/N: ", ["S", "N"])
        estado["cancelada"] = confirmacion == "N"
    else:
        if not estado["jugadores"][0]["flota"] or not estado["jugadores"][1]["flota"]:
            raise ErrorJuego("La partida guardada no tiene ambas flotas.")
        estado["cancelada"] = False

    ambas_maquinas = estado["jugadores"][0]["es_maquina"] and estado["jugadores"][1]["es_maquina"]
    pasos = 0
    continuo = False
    while estado["ganador"] is None and not estado["cancelada"]:
        if ambas_maquinas and pasos == 0 and not continuo:
            cantidad = menu_simulacion(estado)
            if cantidad == -1:
                continuo = True
            else:
                pasos = cantidad
        if not estado["cancelada"] and (not ambas_maquinas or continuo or pasos > 0):
            jugador = estado["jugadores"][estado["turno"]]
            if jugador["es_maquina"]:
                turno_maquina(estado)
                mostrar_ultimo_turno(estado)
            else:
                realizar_turno(estado)
            if ambas_maquinas and not continuo:
                pasos -= 1

    if not estado.get("guardada", False):
        resumen = mostrar_resumen(estado)
        if estado["ganador"] is not None:
            registrar_partida_terminada(estado, resumen)
    return estado


def pedir_dificultad(nombre="Maquina"):
    """Permite elegir entre los dos niveles de una maquina."""
    print("\nDificultad de", nombre)
    print("1 - Basica (aleatoria)")
    print("2 - Avanzada (mapa de probabilidad)")
    opcion = pedir_opcion("Opcion: ", ["1", "2"])
    if opcion == "1":
        return "basica"
    return "avanzada"


def partida_uno_contra_uno():
    """Inicia una partida entre dos personas."""
    return jugar_partida(nueva_partida_1v1({"tamanio": pedir_tamanio()}))


def partida_contra_maquina():
    """Inicia una partida contra la maquina."""
    n = pedir_tamanio()
    dificultad = pedir_dificultad()
    return jugar_partida(nueva_partida_vs_maquina({"tamanio": n}, dificultad))


def partida_maquina_contra_maquina():
    """Inicia una partida entre dos maquinas."""
    n = pedir_tamanio()
    dificultad_1 = pedir_dificultad("Maquina 1")
    dificultad_2 = pedir_dificultad("Maquina 2")
    estado = nueva_partida_maquina_vs_maquina({"tamanio": n}, (dificultad_1, dificultad_2))
    return jugar_partida(estado)


def continuar_partida():
    """Lista las partidas guardadas y permite retomar una de ellas.
    Devuelve el estado de la partida o None si no hay partidas o se cancela.
    Puede lanzar RegistroError si falla la lectura del archivo JSON.
    """
    nombres = registro.listar_partidas()
    if not nombres:
        print("No hay partidas guardadas.")
        return None
    print("\nPartidas guardadas:")
    for nombre in nombres:
        print("-", nombre)
    while True:
        nombre = pedir_nombre_partida()
        if nombre is None:
            return None
        if nombre in nombres:
            estado = registro.cargar_partida(nombre)
            estado["nombre_partida"] = nombre
            return jugar_partida(estado, continuar=True)
        print("No se encontro ese nombre en la lista.")


def mostrar_ranking():
    """Muestra las victorias acumuladas por jugador."""
    ranking = registro.obtener_ranking()
    if not ranking:
        print("Todavia no hay resultados terminados.")
    else:
        print("\n===== RANKING =====")
        posicion = 1
        for datos in ranking:
            print(posicion, "-", datos["jugador"], "-", datos["victorias"], "victorias")
            posicion += 1


def salir():
    """Sale del menu principal."""
    print("Saliste del juego.")


def menu_principal():
    """Muestra el menu principal y ejecuta cada opcion."""
    acciones = {
        "1": partida_uno_contra_uno,
        "2": partida_contra_maquina,
        "3": partida_maquina_contra_maquina,
        "4": continuar_partida,
        "5": salir,
        "6": mostrar_ranking,
    }
    opcion = ""
    while opcion != "5":
        print("\n===== OPERACION CUBO =====")
        print("1 - Partida uno contra uno")
        print("2 - Partida contra la maquina")
        print("3 - Maquina contra maquina")
        print("4 - Continuar partida guardada")
        print("5 - Salir")
        print("6 - Ranking")
        opcion = pedir_opcion("Opcion: ", list(acciones))
        try:
            acciones[opcion]()
        except (ErrorJuego, armamento.ArmamentoError, registro.RegistroError, ValueError) as error:
            print("No se pudo continuar:", error)
        finally:
            if opcion != "5":
                print("Volviendo al menu principal.")


if __name__ == "__main__":
    menu_principal()

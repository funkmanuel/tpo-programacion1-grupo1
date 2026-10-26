"""Menus, turnos y victoria de los dos modos de juego de la entrega 2."""

import random
import re
import tablero
import flota
import armamento
import radar
import registro


class ErrorJuego(Exception):
    """error del juego"""
    pass


class CoordenadaInvalidaError(ErrorJuego):
    """coordenada invalida"""
    pass


class UbicacionNaveError(ErrorJuego):
    """no se pudo ubicar"""
    pass


def pedir_opcion(mensaje, opciones):
    """pide una opcion"""
    while True:
        opcion = input(mensaje).strip().upper()
        if re.match(r"^[A-Z0-9]$", opcion) and opcion in opciones:
            return opcion
        print("Opcion invalida. Elija una de las opciones indicadas.")


def pedir_tamanio():
    """pide el tamaño del cubo"""
    while True:
        texto = input(f"Tamaño del cubo ({tablero.N_MINIMO}-{tablero.N_MAXIMO}, Enter para 8): ").strip()
        if texto == "":
            return tablero.N_POR_DEFECTO
        if re.match(r"^[0-9]{1,2}$", texto):
            n = int(texto)
            if tablero.tamanio_valido(n):
                return n
        print("Tamaño invalido.")


def pedir_valor(n):
    """pide un valor 1..N"""
    while True:
        texto = input(f"Valor del plano (1-{n}): ").strip()
        if re.match(r"^[0-9]{1,2}$", texto):
            valor = int(texto)
            if 1 <= valor <= n:
                return valor
        print("Valor invalido.")


def pedir_punto(n):
    """pide un punto"""
    while True:
        texto = input("Coordenadas z,x,y: ").strip()
        punto = tablero.texto_a_punto(texto, n)
        if punto is not None:
            return punto
        print("Coordenada invalida. Ejemplo: 2,3,4.")


def pedir_tramo(n):
    """pide un tramo"""
    while True:
        texto = input("Desde-hasta (ejemplo 2,3,4-2,3,5; 0 para volver): ").strip()
        if texto == "0":
            return None
        tramo = tablero.texto_a_tramo(texto, n)
        if tramo is not None:
            return tramo
        print("Tramo invalido.")


def mostrar_cubo(cubo, es_rival=False):
    """dibuja el cubo"""
    for z in range(1, tablero.tamanio(cubo) + 1):
        print(tablero.dibujar_capa_z(cubo, z, es_rival))
    print(tablero.referencias())


def ubicacion_manual(cubo, flota_jugador):
    """ubicacion manual"""
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
    """ubicacion automatica"""
    try:
        return flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES)
    except ValueError as error:
        raise UbicacionNaveError(str(error))


def cancelar_ubicacion(cubo, flota_jugador):
    """cancela la ubicacion"""
    return None


def preparar_flota(nombre, n, es_maquina=False):
    """prepara la flota"""
    if es_maquina:
        return ubicacion_automatica(tablero.crear_cubo(n))
    acciones = {"1": ubicacion_manual, "2": ubicacion_automatica, "0": cancelar_ubicacion}
    while True:
        print(f"\n--- Flota de {nombre} ---")
        print("1 - Ubicacion manual")
        print("2 - Ubicacion automatica")
        print("0 - Volver al menu principal")
        opcion = pedir_opcion("Opcion: ", ["1", "2", "0"])
        funcion = acciones[opcion]
        try:
            return funcion(tablero.crear_cubo(n), {})
        except UbicacionNaveError as error:
            print(error)
            print("Puede intentar nuevamente o volver al menu principal.")


def crear_jugador(nombre, n, es_maquina=False):
    """crea un jugador"""
    return {
        "nombre": nombre,
        "cubo": tablero.crear_cubo(n),
        "flota": {},
        "municion": armamento.inventario_inicial(),
        "es_maquina": es_maquina,
        "disparos": set(),
        "pendientes": set(),
    }


def nueva_partida_1v1(configuracion):
    """estado 1v1"""
    if not isinstance(configuracion, dict):
        raise ErrorJuego("La configuracion debe ser un diccionario.")
    n = configuracion.get("tamanio", tablero.N_POR_DEFECTO)
    if not tablero.tamanio_valido(n):
        raise ErrorJuego("Tamaño de cubo invalido.")
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
    """estado vs maquina"""
    estado = nueva_partida_1v1(configuracion)
    estado["jugadores"][1] = crear_jugador("Maquina", estado["tamanio"], True)
    estado["dificultad"] = dificultad
    return estado


def procesar_disparo(cubo_defensor, flota_defensor, punto, arma="T", eje="x", municion=None):
    """procesa un disparo"""
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
    """eventos especiales"""
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
    """aplica un ataque"""
    atacante = estado["jugadores"][estado["turno"]]
    defensor = estado["jugadores"][1 - estado["turno"]]
    cubo, resultados, hundidas = procesar_disparo(
        defensor["cubo"], defensor["flota"], jugada.get("punto"),
        jugada["arma"], jugada.get("eje", "x"), atacante["municion"]
    )
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
    """aplica sonar"""
    atacante = estado["jugadores"][estado["turno"]]
    defensor = estado["jugadores"][1 - estado["turno"]]
    armamento.validar_municion(atacante["municion"], "S")
    cubo, contactos = radar.sonar_plano(defensor["cubo"], jugada.get("eje"), jugada.get("valor"))
    defensor["cubo"] = cubo
    armamento.consumir_municion(atacante["municion"], "S")
    registro.registrar_sonar(estado["historial"], atacante["nombre"], jugada["eje"], jugada["valor"], contactos)
    return {"jugador": atacante["nombre"], "arma": "S", "contactos": contactos}


ACCIONES_ARMAS = {
    "T": aplicar_ataque,
    "R": aplicar_ataque,
    "C": aplicar_ataque,
    "L": aplicar_ataque,
    "S": aplicar_sonar,
}


def hay_ganador(estado):
    """nombre del ganador o None"""
    jugadores = estado["jugadores"]
    if flota.flota_hundida(jugadores[1]["flota"]):
        return jugadores[0]["nombre"]
    if flota.flota_hundida(jugadores[0]["flota"]):
        return jugadores[1]["nombre"]
    return None


def ejecutar_turno(estado, jugada):
    """aplica la jugada"""
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
    funcion = ACCIONES_ARMAS[jugada["arma"]]
    estado["ultimo_turno"] = funcion(estado, jugada)
    estado["ganador"] = hay_ganador(estado)
    if estado["ganador"] is None:
        estado["turno"] = 1 - estado["turno"]
    return estado


def turno_maquina(estado):
    """turno random de la maquina"""
    maquina = estado["jugadores"][estado["turno"]]
    if not maquina["es_maquina"]:
        raise ErrorJuego("El turno actual no pertenece a la maquina.")
    posibles = []
    for z in range(1, estado["tamanio"] + 1):
        for x in range(1, estado["tamanio"] + 1):
            for y in range(1, estado["tamanio"] + 1):
                punto = (z, x, y)
                if punto not in maquina["disparos"] or punto in maquina["pendientes"]:
                    posibles.append(punto)
    if not posibles:
        raise ErrorJuego("La maquina no tiene celdas disponibles.")
    punto = posibles[random.randint(0, len(posibles) - 1)]
    return ejecutar_turno(estado, {"arma": "T", "punto": punto})


def pedir_ataque(n):
    """pide ataque"""
    return {"punto": pedir_punto(n)}


def pedir_laser(n):
    """pide laser"""
    punto = pedir_punto(n)
    eje = pedir_opcion("Eje X/Y: ", ["X", "Y"]).lower()
    return {"punto": punto, "eje": eje}


def pedir_sonar(n):
    """pide sonar"""
    eje = pedir_opcion("Eje Z/X/Y: ", ["Z", "X", "Y"]).lower()
    return {"eje": eje, "valor": pedir_valor(n)}


LECTURAS_ARMAS = {"T": pedir_ataque, "R": pedir_ataque, "C": pedir_ataque, "L": pedir_laser, "S": pedir_sonar}


def mostrar_ultimo_turno(estado):
    """muestra el ultimo turno"""
    ultimo = estado["ultimo_turno"]
    print(f"\n{ultimo['jugador']} uso {ultimo['arma']}.")
    if "contactos" in ultimo:
        print("Contactos detectados:", len(ultimo["contactos"]))
    for punto, resultado in ultimo.get("resultados", {}).items():
        print(punto, resultado)
    for nombre in ultimo.get("hundidas", []):
        print("Nave hundida:", nombre)


def accion_disparar(estado):
    """accion disparar"""
    atacante = estado["jugadores"][estado["turno"]]
    for letra in ACCIONES_ARMAS:
        cantidad = atacante["municion"][letra]
        texto = "ilimitada"
        if cantidad is not None:
            texto = str(cantidad)
        print(letra, armamento.CATALOGO_ARMAS[letra]["nombre"], "-", texto)
    arma = pedir_opcion("Arma T/R/C/L/S: ", ["T", "R", "C", "L", "S"])
    armamento.validar_municion(atacante["municion"], arma)
    funcion = LECTURAS_ARMAS[arma]
    jugada = funcion(estado["tamanio"])
    jugada["arma"] = arma
    ejecutar_turno(estado, jugada)
    mostrar_ultimo_turno(estado)
    return True


def mostrar_capas_turno(estado):
    """muestra capas"""
    propio = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]
    print("\nCubo propio:")
    mostrar_cubo(propio["cubo"])
    print("\nCubo rival:")
    mostrar_cubo(rival["cubo"], True)


def mostrar_corte_x(estado):
    """corte x"""
    valor = pedir_valor(estado["tamanio"])
    propio = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]
    print("Cubo propio:")
    print(tablero.dibujar_plano_x(propio["cubo"], valor, False))
    print("Cubo rival:")
    print(tablero.dibujar_plano_x(rival["cubo"], valor, True))


def mostrar_corte_y(estado):
    """corte y"""
    valor = pedir_valor(estado["tamanio"])
    propio = estado["jugadores"][estado["turno"]]
    rival = estado["jugadores"][1 - estado["turno"]]
    print("Cubo propio:")
    print(tablero.dibujar_plano_y(propio["cubo"], valor, False))
    print("Cubo rival:")
    print(tablero.dibujar_plano_y(rival["cubo"], valor, True))


def accion_ver_cubo(estado):
    """ver cubo"""
    print("1 - Capas z")
    print("2 - Corte x")
    print("3 - Corte y")
    opcion = pedir_opcion("Vista: ", ["1", "2", "3"])
    vistas = {"1": mostrar_capas_turno, "2": mostrar_corte_x, "3": mostrar_corte_y}
    funcion = vistas[opcion]
    funcion(estado)
    return False


def mostrar_estadisticas(estado):
    """muestra stats"""
    for jugador in estado["jugadores"]:
        datos = registro.calcular_estadisticas(estado["historial"], jugador["nombre"])
        print(f"\n--- Estadisticas de {jugador['nombre']} ---")
        print("Disparos:", datos["disparos"], "- con acierto:", datos["aciertos"])
        print("Impactos:", datos["impactos"], "- hundimientos:", datos["hundimientos"])
        print("Sonares:", datos["sonares"], "- contactos:", datos["contactos"])
        print(f"Precision: {datos['precision']:.2f}%")


def accion_historial(estado):
    """historial"""
    for accion in registro.obtener_historial(estado["historial"]):
        print(accion["jugador"], "-", accion["detalle"])
    mostrar_estadisticas(estado)
    return False


def accion_busquedas(estado):
    """compara busquedas"""
    jugador = estado["jugadores"][estado["turno"]]
    puntos_lineal, lineal = radar.buscar_nave_lineal(jugador["cubo"])
    puntos_optimizada, optimizada = radar.buscar_nave_optimizada(jugador["cubo"], jugador["flota"])
    print("Lineal:", lineal)
    print("Optimizada:", optimizada)
    print("Resultados coincidentes:", puntos_lineal == puntos_optimizada)
    return False


def accion_cancelar(estado):
    """cancelar partida"""
    estado["cancelada"] = True
    return False


def realizar_turno(estado):
    """menu del turno"""
    acciones = {
        "1": accion_disparar,
        "2": accion_ver_cubo,
        "3": accion_historial,
        "4": accion_busquedas,
        "5": accion_cancelar,
    }
    realizado = False
    while not realizado and not estado["cancelada"]:
        print("\nTurno de:", estado["jugadores"][estado["turno"]]["nombre"])
        print("1 - Disparar o usar sonar")
        print("2 - Ver el cubo")
        print("3 - Historial y estadisticas")
        print("4 - Comparar busquedas")
        print("5 - Terminar esta partida")
        opcion = pedir_opcion("Opcion: ", ["1", "2", "3", "4", "5"])
        funcion = acciones[opcion]
        try:
            realizado = funcion(estado)
        except (ErrorJuego, armamento.ArmamentoError, ValueError) as error:
            print(error)


def mostrar_resumen(estado):
    """resumen final"""
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


def jugar_partida(estado):
    """juega la partida"""
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

    while estado["ganador"] is None and not estado["cancelada"]:
        jugador = estado["jugadores"][estado["turno"]]
        if jugador["es_maquina"]:
            turno_maquina(estado)
            mostrar_ultimo_turno(estado)
        else:
            realizar_turno(estado)
    mostrar_resumen(estado)
    return estado


def partida_uno_contra_uno():
    """partida 1v1"""
    return jugar_partida(nueva_partida_1v1({"tamanio": pedir_tamanio()}))


def partida_contra_maquina():
    """partida vs maquina"""
    return jugar_partida(nueva_partida_vs_maquina({"tamanio": pedir_tamanio()}, "basica"))


def opcion_pendiente():
    """opcion de E3"""
    print("Esta opcion corresponde a la entrega 3.")


def salir():
    """salir"""
    print("Saliste del juego.")


def menu_principal():
    """menu principal"""
    acciones = {
        "1": partida_uno_contra_uno,
        "2": partida_contra_maquina,
        "3": opcion_pendiente,
        "4": opcion_pendiente,
        "5": salir,
    }
    opcion = ""
    while opcion != "5":
        print("\n===== OPERACION CUBO =====")
        print("1 - Partida uno contra uno")
        print("2 - Partida contra la maquina")
        print("3 - Maquina contra maquina (entrega 3)")
        print("4 - Continuar partida guardada (entrega 3)")
        print("5 - Salir")
        opcion = pedir_opcion("Opcion: ", ["1", "2", "3", "4", "5"])
        funcion = acciones[opcion]
        try:
            funcion()
        except (ErrorJuego, armamento.ArmamentoError, ValueError) as error:
            print("No se pudo continuar:", error)

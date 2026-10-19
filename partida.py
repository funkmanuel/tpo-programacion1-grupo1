
import random
import tablero
import flota
import armamento


class ErrorJuego(Exception):
    """Excepcion base para los errores propios del juego"""
    pass


class CoordenadaInvalidaError(ErrorJuego):
    """Indica que una coordenada no es valida"""
    pass


class DisparoRepetidoError(ErrorJuego):
    """Indica que se intenta atacar una celda ya atacada"""
    pass


class UbicacionNaveError(ErrorJuego):
    """Indica que una nave no pudo ubicarse correctamente"""
    pass


def pedir_opcion(mensaje, opciones):
    """Solicita una opcion hasta que el usuario ingrese una valida"""
    while True:
        opcion = input(mensaje).strip()

        if opcion in opciones:
            return opcion

        print("Opcion invalida.")


def pedir_tamanio():
    """Solicita un tamaño valido para el cubo"""
    while True:
        texto = input(
            f"Ingrese el tamaño del cubo "
            f"({tablero.N_MINIMO}-{tablero.N_MAXIMO}): "
        ).strip()

        if texto.isdigit():
            n = int(texto)

            if tablero.tamanio_valido(n):
                return n

        print("Tamaño invalido")


def pedir_punto(n, mensaje=None):
    """Solicita una coordenada valida dentro del cubo"""
    if mensaje is None:
        mensaje = (
            "Ingrese las coordenadas z,x,y "
            "(ejemplo: 2,3,4): "
        )

    while True:
        texto = input(mensaje).strip()

        try:
            punto = tablero.texto_a_punto(texto, n)

            if punto is None or not tablero.punto_valido(punto, n):
                raise CoordenadaInvalidaError(
                    "Coordenada invalida, use el formato z,x,y."
                )

            return tuple(punto)

        except CoordenadaInvalidaError as error:
            print(error)

        except (ValueError, TypeError, IndexError):
            print("Coordenada invalidaa, use el formato z,x,y.")


def pedir_tramo(n):
    """Solicita un tramo valido para ubicar una nave"""
    while True:
        texto = input(
            "Ingrese el tramo "
            "(ejemplo: 1,2,3-1,2,4): "
        ).strip()

        try:
            tramo = tablero.texto_a_tramo(texto, n)

            if tramo is not None:
                return tramo

        except (ValueError, TypeError, IndexError):
            pass

        print("Tramo invalido, intente nuevamente.")


def mostrar_cubo(cubo, es_rival=False):
    """Dibuja todas las capas del cubo y permite ocultar las naves rivales"""
    n = tablero.tamanio(cubo)

    print()
    print(tablero.referencias())

    for z in range(1, n + 1):
        print()
        print(tablero.dibujar_capa_z(cubo, z, es_rival))


def ubicacion_manual(cubo, flota_jugador):
    """Permite ubicar manualmente las naves que faltan sin perder las ya ubicadas"""
    n = tablero.tamanio(cubo)

    for letra, datos in flota.CATALOGO_NAVES.items():
        cantidad_actual = sum(
            1 for nave in flota_jugador.values()
            if nave["tipo"] == letra
        )

        for numero in range(
            cantidad_actual + 1,
            datos["cantidad"] + 1
        ):
            colocada = False

            while not colocada:
                print()
                print(
                    "Ubicando",
                    datos["nombre"],
                    numero,
                    "de",
                    datos["cantidad"]
                )

                mostrar_cubo(cubo)
                tramo = pedir_tramo(n)

                try:
                    try:
                        cubo, flota_jugador = flota.ubicar_nave(
                            cubo,
                            flota_jugador,
                            letra,
                            tramo[0],
                            tramo[1]
                        )

                    except (ValueError, TypeError, IndexError) as error:
                        raise UbicacionNaveError(str(error)) from error

                    colocada = True
                    print("Nave ubicada correctamente")

                except UbicacionNaveError as error:
                    print()
                    print("No se pudo ubicar la nave")
                    print(error)
                    print("Intente nuevamente con otras coordenadas")

    return cubo, flota_jugador


def ubicacion_automatica(cubo):
    """Intenta ubicar automaticamente toda la flota en el cubo"""
    try:
        return flota.ubicacion_automatica(
            cubo,
            flota.CATALOGO_NAVES
        )

    except (ValueError, TypeError, IndexError) as error:
        raise UbicacionNaveError(
            "No se pudo ubicar automaticamente toda la flota: "
            + str(error)
        ) from error


def preparar_flota(nombre, n, es_maquina=False):
    """Prepara la flota de un jugador o ubica automaticamente la de la maquina."""
    if es_maquina:
        for intento in range(5):
            cubo = tablero.crear_cubo(n)

            try:
                print("La maquina esta ubicando sus naves")
                return ubicacion_automatica(cubo)

            except UbicacionNaveError:
                print("No se pudo ubicar toda la flota. Reintentando")

        raise UbicacionNaveError(
            "La maquina no pudo ubicar toda su flota despues "
            "de varios intentos, pruebe con un cubo mas grande"
        )

    while True:
        cubo = tablero.crear_cubo(n)

        print()
        print("Preparacion de flota:", nombre)
        print("1 - Ubicacion manual")
        print("2 - Ubicacion automatica")

        opcion = pedir_opcion(
            "Seleccione una opcion: ",
            ["1", "2"]
        )

        if opcion == "1":
            try:
                return ubicacion_manual(cubo, {})

            except UbicacionNaveError as error:
                print(error)
                print("Se reiniciara la preparacion de la flota")

        else:
            try:
                resultado = ubicacion_automatica(cubo)
                print("Flota ubicada automaticamente")
                return resultado

            except UbicacionNaveError as error:
                print(error)
                print("Puede intentar nuevamente o elegir la ubicacion manual")


def procesar_disparo(cubo_defensor, flota_defensor, punto):
    """Procesa un disparo, actualiza el cubo y detecta si una nave fue hundida"""
    n = tablero.tamanio(cubo_defensor)

    if (
        not isinstance(punto, (tuple, list))
        or len(punto) != 3
        or not tablero.punto_valido(punto, n)
    ):
        raise CoordenadaInvalidaError(
            "Las coordenadas estan fuera del cubo o no son validas"
        )

    resultado = armamento.disparar(
        cubo_defensor,
        "T",
        punto
    )

    if resultado is None:
        raise CoordenadaInvalidaError(
            "No se pudo realizar el disparo"
        )

    cubo_actualizado, estado_disparo = resultado

    if estado_disparo == "repetido":
        raise DisparoRepetidoError(
            "Esa coordenada ya fue atacada"
        )

    nave_hundida = None

    if estado_disparo == "impacto":
        for nave in flota_defensor.values():
            if punto not in nave["celdas"]:
                continue

            todas_impactadas = all(
                tablero.leer_celda(cubo_actualizado, celda)
                in (tablero.IMPACTO, tablero.HUNDIDO)
                for celda in nave["celdas"]
            )

            if todas_impactadas and nave["estado"] != "hundida":
                nave["estado"] = "hundida"
                nave_hundida = nave["nombre"]

                for celda in nave["celdas"]:
                    tablero.escribir_celda(
                        cubo_actualizado,
                        celda,
                        tablero.HUNDIDO
                    )

            break

    return cubo_actualizado, estado_disparo, nave_hundida


def flota_derrotada(flota_jugador):
    """Devuelve True si todas las naves de una flota fueron hundidas"""
    if not flota_jugador:
        return False

    return all(
        nave["estado"] == "hundida"
        for nave in flota_jugador.values()
    )


def realizar_turno(atacante, cubo_defensor, flota_defensor):
    """Gestiona un turno y repite la entrada si el disparo no es valido"""
    n = tablero.tamanio(cubo_defensor)

    while True:
        print()
        print("Turno de:", atacante)

        punto = pedir_punto(n)

        try:
            cubo_actualizado, estado, nave_hundida = procesar_disparo(
                cubo_defensor,
                flota_defensor,
                punto
            )

            if estado == "agua":
                print("Agua. El disparo no impacto ninguna nave")

            elif estado == "impacto":
                print("Impacto")

                if nave_hundida is not None:
                    print("Nave hundida:", nave_hundida)

            return cubo_actualizado

        except ErrorJuego as error:
            print(error)
            print("Intente nuevamente")


def partida_uno_contra_uno():
    """Ejecuta una partida entre dos jugadores humanos hasta que haya un ganador"""
    n = pedir_tamanio()

    print()
    print("Preparacion del jugador 1")
    cubo_1, flota_1 = preparar_flota("Jugador 1", n)

    print()
    print("Preparacion del jugador 2")
    cubo_2, flota_2 = preparar_flota("Jugador 2", n)

    atacante = 1

    while True:
        if atacante == 1:
            cubo_2 = realizar_turno(
                "Jugador 1",
                cubo_2,
                flota_2
            )

            if flota_derrotada(flota_2):
                print()
                print("Victoria del Jugador 1.")
                break

            atacante = 2

        else:
            cubo_1 = realizar_turno(
                "Jugador 2",
                cubo_1,
                flota_1
            )

            if flota_derrotada(flota_1):
                print()
                print("Victoria del Jugador 2.")
                break

            atacante = 1

        print()
        print("Tablero del rival:")

        if atacante == 1:
            mostrar_cubo(cubo_2, True)
        else:
            mostrar_cubo(cubo_1, True)


def disparo_maquina(cubo_defensor, flota_defensor, disparos_realizados):
    """Selecciona una coordenada no atacada y procesa el disparo de la maquina"""
    n = tablero.tamanio(cubo_defensor)

    while True:
        punto = (
            random.randint(1, n),
            random.randint(1, n),
            random.randint(1, n)
        )

        if punto in disparos_realizados:
            continue

        try:
            resultado = procesar_disparo(
                cubo_defensor,
                flota_defensor,
                punto
            )

            disparos_realizados.add(punto)
            return resultado

        except ErrorJuego:
            disparos_realizados.add(punto)


def partida_contra_maquina():
    """Ejecuta una partida entre el usuario y la maquina hasta que haya un ganador"""
    n = pedir_tamanio()

    print()
    print("Prepara tu flota")
    cubo_jugador, flota_jugador = preparar_flota(
        "Jugador",
        n
    )

    cubo_maquina, flota_maquina = preparar_flota(
        "Maquina",
        n,
        es_maquina=True
    )

    disparos_maquina = set()
    turno_jugador = True

    while True:
        if turno_jugador:
            print()
            print("Tu turno")
            print("Tablero de la maquina:")
            mostrar_cubo(cubo_maquina, True)

            cubo_maquina = realizar_turno(
                "Jugador",
                cubo_maquina,
                flota_maquina
            )

            if flota_derrotada(flota_maquina):
                print()
                print("Ganaste la partida")
                break

        else:
            print()
            print("Turno de la maquina")

            cubo_jugador, estado, nave_hundida = disparo_maquina(
                cubo_jugador,
                flota_jugador,
                disparos_maquina
            )

            print("La maquina disparo.")

            if estado == "agua":
                print("La maquina fallo")

            elif estado == "impacto":
                print("La maquina impacto una nave")

                if nave_hundida is not None:
                    print("La maquina hundio:", nave_hundida)

            if flota_derrotada(flota_jugador):
                print()
                print("La maquina gano la partida")
                break

        turno_jugador = not turno_jugador

    print()
    print("Estado final de tu tablero:")
    mostrar_cubo(cubo_jugador)


def menu_principal():
    """Muestra el menu principal y permite elegir el modo de juego"""
    while True:
        print()
        print("================================")
        print("        OPERACION CUBO")
        print("================================")
        print("1 - Partida uno contra uno")
        print("2 - Partida contra la maquina")
        print("3 - Salir")

        opcion = pedir_opcion(
            "Seleccione una opcion: ",
            ["1", "2", "3"]
        )

        try:
            if opcion == "1":
                partida_uno_contra_uno()

            elif opcion == "2":
                partida_contra_maquina()

            elif opcion == "3":
                print("Saliste del juego")
                break

        except ErrorJuego as error:
            print()
            print("No se pudo continuar la partida:", error)


if __name__ == "__main__":
    menu_principal()

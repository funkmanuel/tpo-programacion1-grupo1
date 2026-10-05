import tablero
import flota

def pedir_opcion(mensaje, opciones):
    """
    Solicita al usuario una opcion hasta que ingrese una
    de las opciones permitidas

    Retorna la opcion ingresada por el usuario
    """
    while True:
        opcion = input(mensaje)

        if opcion in opciones:
            return opcion

        print("Opcion invalida")


def pedir_tamanio():
    """
    Solicita al usuario el tamaño del cubo y verifica que
    este dentro de los limites permitidos por tablero.py

    Retorna el tamaño valido del cubo
    """
    while True:
        texto = input(
            "Ingrese el tamaño del cubo "
            f"({tablero.N_MINIMO}-{tablero.N_MAXIMO}): "
        )

        if texto.isdigit():
            n = int(texto)

            if tablero.tamanio_valido(n):
                return n

        print("Tamaño invalido")


def mostrar_cubo(cubo):
    """
    Muestra por pantalla todas las capas del cubo
    """
    n = tablero.tamanio(cubo)

    print()
    print(tablero.referencias())

    for z in range(1, n + 1):
        print()
        print(tablero.dibujar_capa_z(cubo, z, False))

def pedir_tramo(n):
    """
    Solicita al usuario un tramo de coordenadas y verifica
    que tenga el formato y las coordenadas validas

    Retorna una tupla con el punto inicial y el punto final
    """
    while True:
        texto = input(
            "Ingrese el tramo "
            "(ejemplo: 1,2,3-1,2,4): "
        )

        tramo = tablero.texto_a_tramo(texto, n)

        if tramo is not None:
            return tramo

        print("Tramo invalido")


def ubicacion_manual(cubo, flota_jugador):
    """
    Permite ubicar manualmente todas las naves del jugador.

    La flota recibida se mantiene para evitar que se reinicien las ubicaciones anteriores. 
    Si una nueva nave ocupa una celda ya utilizada o queda contigua a otra nave, 
    se rechaza la ubicacion

    Retorna el cubo y la flota actualizados
    """
    n = tablero.tamanio(cubo)

    for letra, datos in flota.CATALOGO_NAVES.items():

        cantidad_actual = 0

        for nave in flota_jugador.values():
            if nave["tipo"] == letra:
                cantidad_actual = cantidad_actual + 1

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

                resultado = flota.ubicar_nave(
                    cubo,
                    flota_jugador,
                    letra,
                    tramo[0],
                    tramo[1]
                )

                if resultado[0] is not None:
                    colocada = True
                    print("Nave ubicada correctamente")
                else:
                    print()
                    print("No se pudo ubicar la nave")
                    print(
                        "La ubicacion puede estar ocupada, "
                        "ser invalida o estar demasiado cerca "
                        "de otra nave"
                    )
                    print("Intente nuevamente")

    return cubo, flota_jugador


def ubicacion_automatica(cubo):
    """
    Intenta ubicar automaticamente toda la flota utilizando
    la funcion de ubicacion automatica de flota.py

    Parametros:
        cubo: Cubo 3D donde se ubicara la flota

    Retorna:
        El cubo y la flota si la ubicacion fue exitosa.
        Retorna (None, None) si no fue posible
    """
    resultado = flota.ubicacion_automatica(
        cubo,
        flota.CATALOGO_NAVES
    )

    if resultado[0] is not None:
        print()
        print("Flota ubicada automaticamente")
        return resultado

    print()
    print("No se pudo ubicar automaticamente la flota")

    return None, None


def submenu_ubicacion(cubo):
    """
    Muestra el submenu relacionado con la ubicacion de naves

    Permite elegir entre ubicacion manual, ubicacion automatica,
    mostrar el tablero o volver al menu principal

    Una vez que se comienza a ubicar la flota, no se permite
    cambiar entre ubicacion manual y automatica
    """
    flota_jugador = {}
    ubicacion_realizada = False
    tipo_ubicacion = None

    while True:

        print()
        print("========== UBICACION ==========")
        print("1 - Ubicacion manual")
        print("2 - Ubicacion automatica")
        print("3 - Mostrar tablero")
        print("4 - Volver")

        opcion = pedir_opcion(
            "Seleccione una opcion: ",
            ["1", "2", "3", "4"]
        )

        if opcion == "1":

            if ubicacion_realizada:

                print()
                print(
                    "La flota ya fue ubicada "
                    "automaticamente"
                )
                print(
                    "No se puede volver a ubicar "
                    "manualmente"
                )

            else:

                cubo, flota_jugador = ubicacion_manual(
                    cubo,
                    flota_jugador
                )

                ubicacion_realizada = True
                tipo_ubicacion = "manual"

                print()
                print("Ubicacion manual finalizada")

        elif opcion == "2":

            if ubicacion_realizada:

                if tipo_ubicacion == "manual":
                    print()
                    print(
                        "La flota ya fue ubicada "
                        "manualmente"
                    )
                    print(
                        "No se puede utilizar la "
                        "ubicacion automatica"
                    )

                else:
                    print()
                    print(
                        "La flota ya fue ubicada "
                        "automaticamente"
                    )

            else:

                resultado = ubicacion_automatica(cubo)

                if resultado[0] is not None:

                    cubo = resultado[0]
                    flota_jugador = resultado[1]

                    ubicacion_realizada = True
                    tipo_ubicacion = "automatica"

        elif opcion == "3":

            mostrar_cubo(cubo)

        elif opcion == "4":

            return

def menu_principal():
    """
    Muestra el menu principal del juego

    Permite crear un nuevo tablero o salir del programa
    """
    print("================================")
    print("        OPERACION CUBO")
    print("================================")

    while True:

        print()
        print("1 - Crear nuevo tablero")
        print("2 - Salir")

        opcion = pedir_opcion(
            "Seleccione una opcion: ",
            ["1", "2"]
        )

        if opcion == "1":

            n = pedir_tamanio()

            cubo = tablero.crear_cubo(n)

            print()
            print("Tablero creado correctamente")

            submenu_ubicacion(cubo)

        elif opcion == "2":

            print()
            print("Saliste")
            break

menu_principal()


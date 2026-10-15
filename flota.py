import random
import tablero

# Catalogo oficial de naves segun las especificaciones del TPO
CATALOGO_NAVES = {
    "F": {"nombre": "Fragata", "tamanio": 2, "cantidad": 3},
    "D": {"nombre": "Destructor", "tamanio": 3, "cantidad": 2},
    "S": {"nombre": "Submarino", "tamanio": 3, "cantidad": 2},
    "C": {"nombre": "Crucero", "tamanio": 4, "cantidad": 1},
    "P": {"nombre": "Portaaviones", "tamanio": 5, "cantidad": 1},
    "E": {"nombre": "Estacion orbital", "tamanio": 8, "cantidad": 1}
}


def obtener_celdas_tramo(nave, punto_desde, punto_hasta):
    """
    Objetivo: Generar la lista de puntos que ocupa una nave a partir de sus extremos.
    Parametros:
      nave: Identificador de la nave ('F', 'D', 'S', 'C', 'P', 'E').
      punto_desde: Tupla (z, x, y) de inicio.
      punto_hasta: Tupla (z, x, y) de fin.
    Retorna:
      Lista de celdas, mensaje de error si no es valido.
    """
    z1, x1, y1 = punto_desde
    z2, x2, y2 = punto_hasta

    if nave == "E":
        # La Estacion orbital ocupa un bloque de 2x2x2
        zs = sorted([z1, z2])
        xs = sorted([x1, x2])
        ys = sorted([y1, y2])

        if (zs[1] - zs[0] != 1) or (xs[1] - xs[0] != 1) or (ys[1] - ys[0] != 1):
            raise ValueError("La estacion orbital requiere un tramo de bloque 2x2x2.")

        celdas = []
        for z in range(zs[0], zs[1] + 1):
            for x in range(xs[0], xs[1] + 1):
                for y in range(ys[0], ys[1] + 1):
                    celdas.append((z, x, y))
        return celdas

    # Naves lineales deben variar sobre un unico eje
    ejes_variables = sum([z1 != z2, x1 != x2, y1 != y2])
    if ejes_variables > 1:
        raise ValueError("La nave debe ubicarse en una linea recta sobre un solo eje.")

    z_min, z_max = sorted([z1, z2])
    x_min, x_max = sorted([x1, x2])
    y_min, y_max = sorted([y1, y2])

    celdas = []
    for z in range(z_min, z_max + 1):
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                celdas.append((z, x, y))

    tamanio_esperado = CATALOGO_NAVES[nave]["tamanio"]
    if len(celdas) != tamanio_esperado:
        raise ValueError(f"El tramo indicado ({len(celdas)} celdas) no coincide con el tamaño de '{nave}' ({tamanio_esperado} celdas).")

    return celdas


def validar_restricciones_propias(nave, celdas, n_cubo):
    """
    Objetivo: Verificar que las celdas respeten los limites del cubo y las reglas de cota Z.
    Parametros:
      nave: Tipo de nave ('F', 'D', 'S', 'C', 'P', 'E').
      celdas: Puntos a validar.
      n_cubo: Dimension N del cubo.
    Retorna:
      Mensaje de error si no cumple con la validacion de las naves.
    """
    mitad_inferior = n_cubo // 2

    for punto in celdas:
        if not tablero.punto_valido(punto, n_cubo):
            raise ValueError(f"El punto {punto} esta fuera de los limites del cubo.")

        z, x, y = punto

        # Restricciones por tipo de nave
        if nave == "S" and z > mitad_inferior:
            raise ValueError("El submarino solo puede ubicarse en la mitad inferior de Z.")
        if nave == "P" and z <= mitad_inferior:
            raise ValueError("El portaaviones solo puede ubicarse en la mitad superior de Z.")
        if nave == "C" and (z == 1 or z == n_cubo):
            raise ValueError("El crucero no puede ocupar z = 1 ni z = n.")
        if nave == "E" and (z in (1, n_cubo) or x in (1, n_cubo) or y in (1, n_cubo)):
            raise ValueError("La estacion orbital no puede tocar ninguna cara exterior del cubo.")

def validar_distancia_entre_naves(flota, celdas_nuevas):
    """
    Objetivo: Garantizar al menos una celda libre alrededor de otras naves.
    Parametros:
      flota: Estado actual de la flota.
      celdas_nuevas: Celdas de la nave propuesta.
    Retorna:
      Mensaje de error si no cumple con la validacion de la distancia entre las naves.
    """
    celdas_ocupadas = set()
    for datos_nave in flota.values():
        for celda in datos_nave.get("celdas", []):
            celdas_ocupadas.add(celda)

    for z, x, y in celdas_nuevas:
        for dz in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    vecina = (z + dz, x + dx, y + dy)
                    if vecina in celdas_ocupadas:
                        raise ValueError("No se puede ubicar ahi, debe haber al menos una celda de separacion con otras naves.")

def ubicar_nave(cubo, flota, nave, punto_desde, punto_hasta):
    """
    Objetivo: Validar y ubicar manualmente una nave actualizando el cubo y la flota.
    Parametros:
      cubo: Cubo 3D administrado por tablero.py.
      flota: Diccionario de la flota actual.
      nave: Letra de la nave ('F','D','S','C','P','E').
      punto_desde: Coordenada inicial (z, x, y).
      punto_hasta: Coordenada final (z, x, y).
    Retorna:
      cubo y flota actualizados si la ubicacion fue valida.
    """
    if nave not in CATALOGO_NAVES:
        raise ValueError(f"Tipo de nave '{nave}' no reconocido.")

    n_cubo = tablero.tamanio(cubo)
    celdas = obtener_celdas_tramo(nave, punto_desde, punto_hasta)
    validar_restricciones_propias(nave, celdas, n_cubo)
    validar_distancia_entre_naves(flota, celdas)

    # Registrar en la flota
    id_nave = f"{nave}_{len(flota) + 1}"
    flota[id_nave] = {
        "tipo": nave,
        "nombre": CATALOGO_NAVES[nave]["nombre"],
        "celdas": celdas,
        "estado": "intacta"
    }

    # Escribir en el cubo utilizando la funcion de tablero.py
    for celda in celdas:
        tablero.escribir_celda(cubo, celda, tablero.NAVE)

    return cubo, flota


def ubicacion_automatica(cubo, catalogo, semilla=None):
    """
    Objetivo: Posicionar automaticamente toda la flota respetando todas las reglas del juego.
    Parámetros:
      cubo: Cubo 3D.
      catálogo: Catalogo de naves a posicionar.
      semilla: Semilla aleatoria para testing reproducible.
    Retorna:
       cubo y flota con la flota ubicada automaticamente.
    """
    if semilla is not None:
        random.seed(semilla)

    n_cubo = tablero.tamanio(cubo)
    flota = {}
    orientaciones = ["z", "x", "y"]

    for letra, datos in catalogo.items():
        cantidad = datos["cantidad"]
        tamano = datos["tamanio"]

        for _ in range(cantidad):
            colocada = False
            intentos = 0
            while not colocada and intentos < 2000:
                intentos += 1
                if letra == "E":
                    z1 = random.randint(2, n_cubo - 2)
                    x1 = random.randint(2, n_cubo - 2)
                    y1 = random.randint(2, n_cubo - 2)
                    p_desde = (z1, x1, y1)
                    p_hasta = (z1 + 1, x1 + 1, y1 + 1)
                else:
                    orientacion = random.choice(orientaciones)
                    z1 = random.randint(1, n_cubo)
                    x1 = random.randint(1, n_cubo)
                    y1 = random.randint(1, n_cubo)

                    if orientacion == "z":
                        z2 = z1 + tamanio - 1
                        x2, y2 = x1, y1
                    elif orientacion == "x":
                        x2 = x1 + tamanio - 1
                        z2, y2 = z1, y1
                    else:
                        y2 = y1 + tamanio - 1
                        z2, x2 = z1, x1

                    p_desde = (z1, x1, y1)
                    p_hasta = (z2, x2, y2)

                try:
                    ubicar_nave(cubo, flota, letra, p_desde, p_hasta)
                    colocada = True
                except ValueError:
                    continue

            if not colocada:
                raise ValueError(f"No se pudo posicionar automaticamente la nave '{letra}' tras varios intentos.")

    return cubo, flota

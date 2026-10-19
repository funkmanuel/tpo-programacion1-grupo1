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


# Parte de la segunda entrega
def buscar_nave_por_punto(flota, punto):
    """
    Objetivo: Identificar cual nave de la flota ocupa una determinada coordenada (z, x, y).
    Parametros:
      flota: Estado de la flota.
      punto: Coordenada a consultar.
    Retorna:
      id_nave, datos_nave si se encuentra, o (None, None) si no hay nave en esa celda.
      ValueError si el punto no es una tupla de 3 elementos.
    """
    if not isinstance(punto, tuple) or len(punto) != 3:
        raise ValueError("El punto de consulta debe ser de 3 coordenadas (z, x, y).")

    for id_nave, datos in flota.items():
        if punto in datos["celdas"]:
            return id_nave, datos
    return None, None


def registrar_impacto(flota, cubo, punto):
    """
    Objetivo: Procesar el impacto de un disparo sobre una nave, actualizar sus contadores, cambiar su estado ('averiada' o 'hundida') y marcar el cubo.
    Parametros:
      flota: Estado de la flota.
      cubo: Cubo 3D administrado por tablero.py.
      punto: Coordenada impactada (z, x, y).
    Retorna:
      Informacion del resultado del disparo.
      ValueError si la coordenada de disparo esta fuera de los limites del cubo.
    """
    n_cubo = tablero.tamanio(cubo)
    if not tablero.punto_valido(punto, n_cubo):
        raise ValueError(f"El punto de disparo {punto} esta fuera de los limites del cubo (1 a {n_cubo}).")

    id_nave, datos = buscar_nave_por_punto(flota, punto)
    if not id_nave:
        return {"hubo_impacto": False}

    tipo_nave = datos["tipo"]

    # Inicializar registro de impactos si no existe
    if "impactos_por_celda" not in datos:
        datos["impactos_por_celda"] = {c: 0 for c in datos["celdas"]}

    # El portaaviones ('P') requiere 2 impactos por celda; las demas naves requieren 1
    impactos_necesarios = 2 if tipo_nave == "P" else 1

    # Incrementar impactos en la celda
    datos["impactos_por_celda"][punto] = min(
        datos["impactos_por_celda"].get(punto, 0) + 1, impactos_necesarios
    )

    celda_destruida = datos["impactos_por_celda"][punto] >= impactos_necesarios

    # Marcar en el cubo segun el estado de la celda
    if celda_destruida:
        tablero.escribir_celda(cubo, punto, tablero.AVERIADO)

    # Verificar si todas las celdas de la nave estan completamente destruidas
    todas_destruidas = all(
        datos["impactos_por_celda"][c] >= (2 if tipo_nave == "P" else 1)
        for c in datos["celdas"]
    )

    estado_anterior = datos["estado"]
    se_hundio = False
    evento_especial = None

    if todas_destruidas:
        datos["estado"] = "hundida"
        se_hundio = True
        # Actualizar todas las celdas de la nave a simbolo de HUNDIDO en el cubo
        for c in datos["celdas"]:
            tablero.escribir_celda(cubo, c, tablero.HUNDIDO)

        # La estacion orbital ('E') otorga municion extra cuando es hundida
        if tipo_nave == "E":
            evento_especial = "municion_extra"
    else:
        datos["estado"] = "averiada"

    # El Destructor ('D') al recibir impacto revela celda del oponente
    if tipo_nave == "D" and not se_hundio:
        evento_especial = "revelar_celda"

    return {
        "hubo_impacto": True,
        "id_nave": id_nave,
        "tipo_nave": tipo_nave,
        "nombre_nave": datos["nombre"],
        "estado_anterior": estado_anterior,
        "nuevo_estado": datos["estado"],
        "celda_destruida": celda_destruida,
        "se_hundio": se_hundio,
        "evento_especial": evento_especial
    }


def flota_hundida(flota):
    """
    Objetivo: Determinar si todas las naves de la flota han sido destruidas.
    Parametros:
      flota: Estado de la flota.
    Retorna:
      True si todas las naves estan hundidas, False en caso contrario.
    """
    if not flota:
        return False
    return all(datos["estado"] == "hundida" for datos in flota.values())


def obtener_naves_averiadas(flota):
    """
    Objetivo: Filtrar y devolver unicamente las naves que estan en estado 'averiada'.
    """
    return {id_n: d for id_n, d in flota.items() if d["estado"] == "averiada"}


def obtener_naves_hundidas(flota):
    """
    Objetivo: Filtrar y devolver unicamente las naves que están en estado 'hundida'.
    """
    return {id_n: d for id_n, d in flota.items() if d["estado"] == "hundida"}


def obtener_resumen_flota(flota):
    """
    Objetivo: Generar un diccionario con el conteo general de estados de las naves.
    """
    intactas = sum(1 for d in flota.values() if d["estado"] == "intacta")
    averiadas = sum(1 for d in flota.values() if d["estado"] == "averiada")
    hundidas = sum(1 for d in flota.values() if d["estado"] == "hundida")
    return {
        "intactas": intactas,
        "averiadas": averiadas,
        "hundidas": hundidas,
        "total": len(flota)
    }

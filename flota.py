import random
import tablero

# tipos de nave del TPO
CATALOGO_NAVES = {
    "F": {"nombre": "Fragata", "tamanio": 2, "cantidad": 3},
    "D": {"nombre": "Destructor", "tamanio": 3, "cantidad": 2},
    "S": {"nombre": "Submarino", "tamanio": 3, "cantidad": 2},
    "C": {"nombre": "Crucero", "tamanio": 4, "cantidad": 1},
    "P": {"nombre": "Portaaviones", "tamanio": 5, "cantidad": 1},
    "E": {"nombre": "Estacion orbital", "tamanio": 8, "cantidad": 1}
}


def obtener_celdas_tramo(nave, punto_desde, punto_hasta):
    """celdas entre desde y hasta"""
    if nave not in CATALOGO_NAVES:
        raise ValueError("Tipo de nave no reconocido.")
    for punto in (punto_desde, punto_hasta):
        if not tablero.punto_valido(punto, tablero.N_MAXIMO):
            raise ValueError("Los extremos deben ser puntos de tres enteros validos.")

    z1, x1, y1 = punto_desde
    z2, x2, y2 = punto_hasta

    if nave == "E":
        # estacion = bloque 2x2x2, no linea
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
    """limites y reglas de z"""
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
    """separacion entre naves"""
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
    """ubica una nave en el cubo"""
    if nave not in CATALOGO_NAVES:
        raise ValueError(f"Tipo de nave '{nave}' no reconocido.")

    n_cubo = tablero.tamanio(cubo)
    if not tablero.punto_valido(punto_desde, n_cubo) or not tablero.punto_valido(punto_hasta, n_cubo):
        raise ValueError("Los extremos estan fuera del cubo.")

    cantidad_actual = 0
    for datos in flota.values():
        if datos["tipo"] == nave:
            cantidad_actual += 1
    if cantidad_actual >= CATALOGO_NAVES[nave]["cantidad"]:
        raise ValueError("Ya se ubicaron todas las naves de ese tipo.")

    celdas = obtener_celdas_tramo(nave, punto_desde, punto_hasta)
    validar_restricciones_propias(nave, celdas, n_cubo)
    validar_distancia_entre_naves(flota, celdas)

    # Registrar en la flota
    id_nave = f"{nave}_{cantidad_actual + 1}"
    flota[id_nave] = {
        "tipo": nave,
        "nombre": CATALOGO_NAVES[nave]["nombre"],
        "celdas": celdas,
        "estado": "intacta",
        "impactos_por_celda": {}
    }

    # Escribir en el cubo utilizando la funcion de tablero.py
    for celda in celdas:
        flota[id_nave]["impactos_por_celda"][celda] = 0
        tablero.escribir_celda(cubo, celda, tablero.NAVE)

    return cubo, flota


def ubicacion_automatica(cubo, catalogo, semilla=None):
    """ubica toda la flota al azar"""
    n = tablero.tamanio(cubo)
    if not tablero.tamanio_valido(n):
        raise ValueError("Tamaño de cubo invalido.")
    if tablero.contar_estado(cubo, tablero.AGUA) != n ** 3:
        raise ValueError("La ubicacion automatica requiere un cubo vacio.")

    for letra, datos in catalogo.items():
        if letra not in CATALOGO_NAVES:
            raise ValueError("Tipo de nave no reconocido en el catalogo.")
        cantidad = datos["cantidad"]
        if type(cantidad) != int or cantidad < 0 or cantidad > CATALOGO_NAVES[letra]["cantidad"]:
            raise ValueError("Cantidad de naves invalida.")
        if datos["tamanio"] != CATALOGO_NAVES[letra]["tamanio"]:
            raise ValueError("Tamaño de nave invalido.")

    if semilla is not None:
        random.seed(semilla)

    orden = ["E", "P", "C", "S", "D", "F"]
    orientaciones = ["z", "x", "y"]

    for reinicio in range(30):
        cubo_nuevo = tablero.crear_cubo(n)
        flota_nueva = {}
        completa = True

        for letra in orden:
            if letra in catalogo:
                for numero in range(catalogo[letra]["cantidad"]):
                    colocada = False
                    intentos = 0
                    while not colocada and intentos < 500:
                        intentos += 1
                        if letra == "E":
                            desde = (random.randint(2, n - 2),
                                     random.randint(2, n - 2),
                                     random.randint(2, n - 2))
                            z, x, y = desde
                            hasta = (z + 1, x + 1, y + 1)
                        else:
                            tamanio = catalogo[letra]["tamanio"]
                            z = random.randint(1, n)
                            x = random.randint(1, n)
                            y = random.randint(1, n)
                            desde = (z, x, y)
                            orientacion = orientaciones[random.randint(0, 2)]
                            extremos = {
                                "z": (z + tamanio - 1, x, y),
                                "x": (z, x + tamanio - 1, y),
                                "y": (z, x, y + tamanio - 1),
                            }
                            hasta = extremos[orientacion]

                        try:
                            ubicar_nave(cubo_nuevo, flota_nueva, letra, desde, hasta)
                        except ValueError:
                            pass
                        else:
                            colocada = True

                    if not colocada:
                        completa = False
                        break
            if not completa:
                break

        if completa:
            for z in range(n):
                for x in range(n):
                    for y in range(n):
                        cubo[z][x][y] = cubo_nuevo[z][x][y]
            return cubo, flota_nueva

    raise ValueError("No se pudo ubicar la flota completa. Pruebe un cubo mas grande.")


def buscar_nave_por_punto(flota, punto):
    """nave en ese punto o None"""
    if not tablero.punto_valido(punto, tablero.N_MAXIMO):
        raise ValueError("El punto debe tener tres coordenadas enteras validas.")
    punto = tuple(punto)
    for id_nave, datos in flota.items():
        if punto in datos["celdas"]:
            return id_nave, datos
    return None, None


def registrar_impacto(flota, cubo, punto):
    """registra impacto (P lleva 2)"""
    if not tablero.punto_valido(punto, tablero.tamanio(cubo)):
        raise ValueError("El punto de disparo esta fuera del cubo.")
    punto = tuple(punto)
    id_nave, datos = buscar_nave_por_punto(flota, punto)
    if id_nave is None:
        return {"hubo_impacto": False, "repetido": False}

    if "impactos_por_celda" not in datos:
        datos["impactos_por_celda"] = {}
        for celda in datos["celdas"]:
            datos["impactos_por_celda"][celda] = 0

    impactos_necesarios = 1
    if datos["tipo"] == "P":
        impactos_necesarios = 2

    estado_anterior = datos["estado"]
    repetido = datos["impactos_por_celda"][punto] >= impactos_necesarios
    se_hundio = False
    evento_especial = None

    if not repetido:
        datos["impactos_por_celda"][punto] += 1
        tablero.escribir_celda(cubo, punto, tablero.IMPACTO)

        todas_destruidas = True
        for celda in datos["celdas"]:
            if datos["impactos_por_celda"][celda] < impactos_necesarios:
                todas_destruidas = False

        if todas_destruidas:
            datos["estado"] = "hundida"
            se_hundio = True
            for celda in datos["celdas"]:
                tablero.escribir_celda(cubo, celda, tablero.HUNDIDO)
            if datos["tipo"] == "E":
                evento_especial = "municion_extra"
        else:
            datos["estado"] = "averiada"

        if datos["tipo"] == "D":
            evento_especial = "revelar_celda"

    return {
        "hubo_impacto": not repetido,
        "repetido": repetido,
        "id_nave": id_nave,
        "tipo_nave": datos["tipo"],
        "nombre_nave": datos["nombre"],
        "estado_anterior": estado_anterior,
        "nuevo_estado": datos["estado"],
        "celda_destruida": datos["impactos_por_celda"][punto] >= impactos_necesarios,
        "se_hundio": se_hundio,
        "evento_especial": evento_especial,
    }


def flota_hundida(flota):
    """True si estan todas hundidas"""
    if not flota:
        return False
    for datos in flota.values():
        if datos["estado"] != "hundida":
            return False
    return True


def obtener_naves_averiadas(flota):
    """naves averiadas"""
    resultado = {}
    for id_nave, datos in flota.items():
        if datos["estado"] == "averiada":
            resultado[id_nave] = datos
    return resultado


def obtener_naves_hundidas(flota):
    """naves hundidas"""
    resultado = {}
    for id_nave, datos in flota.items():
        if datos["estado"] == "hundida":
            resultado[id_nave] = datos
    return resultado


def obtener_resumen_flota(flota):
    """conteo por estado"""
    resumen = {"intactas": 0, "averiadas": 0, "hundidas": 0, "total": len(flota)}
    for datos in flota.values():
        if datos["estado"] == "intacta":
            resumen["intactas"] += 1
        elif datos["estado"] == "averiada":
            resumen["averiadas"] += 1
        elif datos["estado"] == "hundida":
            resumen["hundidas"] += 1
    return resumen

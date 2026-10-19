# tablero.py - Modulo del cubo
# El cubo es una lista de listas de listas: cubo[z][x][y]
# El jugador usa valores de 1 a N, pero la lista empieza en 0 (por eso el -1)
# Este modulo no usa print ni input

import re

#Configuracion: Patron para validar un punto "3, 5, 4"

PATRON_PUNTO = r"^(\d{1,2}),(\d{1,2}),(\d{1,2})$"
N_POR_DEFECTO = 8
N_MINIMO = 5   # el portaaviones mide 5
N_MAXIMO = 15

# Estados de una celda

AGUA = "agua"
NAVE = "nave"
AGUA_MARCADA = "agua_marcada"
IMPACTO = "impacto"
HUNDIDO = "hundido"
DETECTADO = "detectado"

# Simbolo de cada estado
SIMBOLOS = {
    AGUA: "~",
    NAVE: "N",
    AGUA_MARCADA: "o",
    IMPACTO: "X",
    HUNDIDO: "#",
    DETECTADO: "?",
}




# Creacion del cubo

def tamanio_valido(n):
    """ Verifica si el tamaño del cubo está dentro de los límites permitidos """
    return n >= N_MINIMO and n <= N_MAXIMO


def crear_cubo(n):
    """ Crea el cubo 3D del tamaño indicado, inicialmente lleno de agua """
    if not tamanio_valido(n):
        return None
    cubo = []
    for z in range(0, n):
        capa = []
        for x in range(0, n):
            fila = []
            for y in range(0, n):
                fila.append(AGUA)
            capa.append(fila)
        cubo.append(capa)
    return cubo


def tamanio(cubo):
    """ Devuelve el tamaño (N) del cubo """
    return len(cubo)


# Validacion de puntos

def punto_valido(punto, n):
    """ Verifica si una coordenada (z, x, y) existe dentro de los límites del cubo """
    if len(punto) != 3:
        return False
    for valor in punto:
        if valor < 1 or valor > n:
            return False
    return True

def texto_a_punto(texto, n):
    """Convierte un texto con formato '3,5,4' a una tupla de tres números enteros"""
    texto = texto.strip()
    coincidencia = re.match(PATRON_PUNTO, texto)
    if coincidencia is None:
        return None
    z, x, y = coincidencia.groups()
    punto = (int(z), int(x), int(y))
    if not punto_valido(punto, n):
        return None
    return punto


def texto_a_tramo(texto, n):
    """ Separa el texto por el guion para obtener dos puntos (desde y hasta) """
    partes = texto.split("-")
    if len(partes) != 2:
        return None
    desde = texto_a_punto(partes[0], n)
    hasta = texto_a_punto(partes[1], n)
    if desde is None or hasta is None:
        return None
    return (desde, hasta)


def punto_a_texto(punto):
    """ Convierte una tupla de coordenadas a un texto separado por comas """
    z, x, y = punto
    return f"{z},{x},{y}"


# Leer y escribir celdas

def leer_celda(cubo, punto):
    """ Devuelve el estado actual de una celda específica del cubo """
    if not punto_valido(punto, tamanio(cubo)):
        return None
    z, x, y = punto
    return cubo[z - 1][x - 1][y - 1]


def escribir_celda(cubo, punto, estado):
    """ Modifica el estado de una celda si el punto y el estado son válidos """
    if estado not in SIMBOLOS:
        return False
    if not punto_valido(punto, tamanio(cubo)):
        return False
    z, x, y = punto
    cubo[z - 1][x - 1][y - 1] = estado
    return True


# Operaciones de matrices

def obtener_capa_z(cubo, z):
    """ Genera una copia exacta de la matriz correspondiente a la capa z """
    if z < 1 or z > tamanio(cubo):
        return None
    capa = cubo[z - 1]
    copia = []
    for x in range(0, len(capa)):
        copia.append(capa[x].copy())
    return copia


def obtener_plano_x(cubo, x):
    """ Genera la matriz del corte del cubo fijando x (filas z, columnas y) """
    n = tamanio(cubo)
    if x < 1 or x > n:
        return None
    plano = []
    for z in range(0, n):
        fila = []
        for y in range(0, n):
            fila.append(cubo[z][x - 1][y])
        plano.append(fila)
    return plano


def obtener_plano_y(cubo, y):
    """ Genera la matriz del corte del cubo fijando y (filas z, columnas x) """
    n = tamanio(cubo)
    if y < 1 or y > n:
        return None
    plano = []
    for z in range(0, n):
        fila = []
        for x in range(0, n):
            fila.append(cubo[z][x][y - 1])
        plano.append(fila)
    return plano


def transponer(matriz):
    """ Transpone una matriz (las filas pasan a columnas) """
    filas = len(matriz)
    columnas = len(matriz[0])
    resultado = []
    for j in range(0, columnas):
        nueva_fila = []
        for i in range(0, filas):
            nueva_fila.append(matriz[i][j])
        resultado.append(nueva_fila)
    return resultado


def contar_estado(cubo, estado):
    """ Cuenta la cantidad total de celdas en el cubo que tienen un estado específico """
    cantidad = 0
    n = tamanio(cubo)
    for z in range(0, n):
        for x in range(0, n):
            cantidad = cantidad + cubo[z][x].count(estado)
    return cantidad


def puntos_con_estado(cubo, estado):
    """ Busca y devuelve un conjunto con todas las coordenadas que tienen un estado particular """
    puntos = set()
    n = tamanio(cubo)
    for z in range(0, n):
        for x in range(0, n):
            for y in range(0, n):
                if cubo[z][x][y] == estado:
                    puntos.add((z + 1, x + 1, y + 1))
    return puntos


# Vecinos de una celda

DIRECCIONES_ORTOGONALES = [
    (-1, 0, 0), (1, 0, 0),
    (0, -1, 0), (0, 1, 0),
    (0, 0, -1), (0, 0, 1),
]


def vecinos_ortogonales(punto, n):
    """ Devuelve las celdas que comparten una cara con el punto, dentro del cubo """
    vecinos = []
    if not punto_valido(punto, n):
        return vecinos
    z, x, y = punto
    for dz, dx, dy in DIRECCIONES_ORTOGONALES:
        vecino = (z + dz, x + dx, y + dy)
        if punto_valido(vecino, n):
            vecinos.append(vecino)
    return vecinos


def vecinos_todos(punto, n):
    """ Devuelve todas las celdas que rodean al punto, incluidas las diagonales, dentro del cubo """
    vecinos = []
    if not punto_valido(punto, n):
        return vecinos
    z, x, y = punto
    for dz in range(-1, 2):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                vecino = (z + dz, x + dx, y + dy)
                if vecino != punto and punto_valido(vecino, n):
                    vecinos.append(vecino)
    return vecinos


# Dibujo

def completar_espacios(texto, ancho):
    """ Rellena el texto con espacios al final hasta alcanzar el ancho deseado """
    if len(texto) >= ancho:
        return texto
    return texto + " " * (ancho - len(texto))


def dibujar_capa_z(cubo, z, es_rival):
    """ Genera el texto con el formato para imprimir una capa entera por pantalla """
    capa = obtener_capa_z(cubo, z)
    if capa is None:
        return None
    n = tamanio(cubo)
    capa_transpuesta = transponer(capa) 

    ancho = len("x" + str(n))

    lineas = []
    lineas.append(f"========= CAPA z = {z} =========")

    encabezado = completar_espacios("", ancho)
    for x in range(1, n + 1):
        encabezado = encabezado + " " + completar_espacios("x" + str(x), ancho)
    lineas.append(encabezado)

    for y in range(0, n):
        linea = completar_espacios("y" + str(y + 1), ancho)
        for x in range(0, n):
            estado = capa_transpuesta[y][x]
            if es_rival and estado == NAVE:
                estado = AGUA
            linea = linea + " " + completar_espacios(SIMBOLOS[estado], ancho)
        lineas.append(linea)

    return "\n".join(lineas)


def dibujar_plano(plano, titulo, eje_columnas, es_rival):
    """ Genera el texto con el formato para imprimir un plano con z en las filas """
    n = len(plano)
    ancho = len(eje_columnas + str(n))

    lineas = []
    lineas.append(f"========= {titulo} =========")

    encabezado = completar_espacios("", ancho)
    for columna in range(1, n + 1):
        encabezado = encabezado + " " + completar_espacios(eje_columnas + str(columna), ancho)
    lineas.append(encabezado)

    for z in range(0, n):
        linea = completar_espacios("z" + str(z + 1), ancho)
        for columna in range(0, n):
            estado = plano[z][columna]
            if es_rival and estado == NAVE:
                estado = AGUA
            linea = linea + " " + completar_espacios(SIMBOLOS[estado], ancho)
        lineas.append(linea)

    return "\n".join(lineas)


def dibujar_plano_x(cubo, x, es_rival):
    """ Genera el texto para imprimir el corte del cubo fijando x """
    plano = obtener_plano_x(cubo, x)
    if plano is None:
        return None
    return dibujar_plano(plano, f"PLANO x = {x}", "y", es_rival)


def dibujar_plano_y(cubo, y, es_rival):
    """ Genera el texto para imprimir el corte del cubo fijando y """
    plano = obtener_plano_y(cubo, y)
    if plano is None:
        return None
    return dibujar_plano(plano, f"PLANO y = {y}", "x", es_rival)


def referencias():
    """ Devuelve el texto con la explicación de los símbolos usados en el tablero """
    texto = "Referencias: ~ sin explorar o agua   o agua marcada   X impacto   # hundido   ? detectado   N nave"
    return texto

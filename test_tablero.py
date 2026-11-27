import tablero


def test_crear_cubo():
    """Verifica la creacion y el tamanio del cubo"""
    cubo = tablero.crear_cubo(8)
    assert tablero.tamanio(cubo) == 8
    assert tablero.contar_estado(cubo, tablero.AGUA) == 512
    assert tablero.crear_cubo(4) == None


def test_punto_valido():
    """Verifica los limites de las coordenadas"""
    assert tablero.punto_valido((1, 1, 1), 8)
    assert tablero.punto_valido((8, 8, 8), 8)
    assert not tablero.punto_valido((0, 1, 1), 8)
    assert not tablero.punto_valido((9, 1, 1), 8)


def test_texto_a_punto():
    """Verifica la conversion de texto a coordenadas"""
    assert tablero.texto_a_punto("3, 5, 4", 8) == (3, 5, 4)
    assert tablero.texto_a_punto("3,5", 8) == None
    assert tablero.texto_a_punto("9,1,1", 8) == None


def test_escribir_y_leer_celda():
    """Verifica la lectura y escritura de una celda"""
    cubo = tablero.crear_cubo(8)
    assert tablero.escribir_celda(cubo, (1, 2, 3), tablero.NAVE)
    assert tablero.leer_celda(cubo, (1, 2, 3)) == tablero.NAVE
    assert tablero.leer_celda(cubo, (2, 2, 3)) == tablero.AGUA
    assert not tablero.escribir_celda(cubo, (0, 1, 1), tablero.NAVE)
    assert not tablero.escribir_celda(cubo, (1, 1, 1), "incorrecto")


def test_obtener_capa_z():
    """Verifica que la capa sea una copia independiente"""
    cubo = tablero.crear_cubo(8)
    capa = tablero.obtener_capa_z(cubo, 1)
    capa[0][0] = tablero.NAVE
    assert tablero.leer_celda(cubo, (1, 1, 1)) == tablero.AGUA


def test_recorridos():
    """Verifica que se recorran todas las celdas"""
    cubo = tablero.crear_cubo(5)
    for recorrido in ("serpiente", "espiral"):
        puntos = tablero.recorrer_tablero(cubo, recorrido)
        assert len(puntos) == 125
        assert len(set(puntos)) == 125
        for punto in puntos:
            assert tablero.punto_valido(punto, 5)

import pytest
import tablero
import flota
import radar


def test_busquedas():
    """Compara los resultados de las tres busquedas"""
    cubo = tablero.crear_cubo(8)
    cubo, flota_jugador = flota.ubicar_nave(cubo, {}, "F", (1, 1, 1), (1, 1, 2))
    lineal, datos_lineal = radar.buscar_nave_lineal(cubo)
    optimizada, datos_optimizada = radar.buscar_nave_optimizada(cubo, flota_jugador)
    recursiva, datos_recursiva = radar.buscar_nave_recursiva(cubo)
    assert lineal == optimizada == recursiva == [(1, 1, 1), (1, 1, 2)]
    assert datos_lineal["comparaciones"] == 512
    assert datos_optimizada["comparaciones"] == 2
    assert datos_recursiva["comparaciones"] == 512
    assert datos_recursiva["profundidad_max"] == 8


def test_busqueda_sin_naves():
    """Verifica la busqueda en un cubo vacio"""
    cubo = tablero.crear_cubo(5)
    puntos, metricas = radar.buscar_nave_recursiva(cubo)
    assert puntos == []
    assert metricas["comparaciones"] == 125


def test_sonar():
    """Verifica los contactos del sonar"""
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (1, 2, 3), tablero.NAVE)
    tablero.escribir_celda(cubo, (2, 2, 3), tablero.NAVE)
    cubo, contactos = radar.sonar_plano(cubo, "z", 1)
    assert contactos == [(1, 2, 3)]
    assert tablero.leer_celda(cubo, (1, 2, 3)) == tablero.DETECTADO
    assert tablero.leer_celda(cubo, (2, 2, 3)) == tablero.NAVE


def test_sonar_invalido():
    """Comprueba el error por plano invalido"""
    cubo = tablero.crear_cubo(8)
    with pytest.raises(ValueError):
        radar.sonar_plano(cubo, "z", 9)


def test_recorridos():
    """Verifica que se recorran todas las celdas"""
    cubo = tablero.crear_cubo(5)
    for recorrido in ("capas", "capas_recursivo", "octantes"):
        puntos = radar.recorrer_cubo(cubo, recorrido)
        assert len(puntos) == 125
        assert len(set(puntos)) == 125
        for punto in puntos:
            assert tablero.punto_valido(punto, 5)

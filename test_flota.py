import pytest
import tablero
import flota


def test_ubicar_nave():
    """Verifica la ubicacion de una nave"""
    cubo = tablero.crear_cubo(8)
    cubo, flota_jugador = flota.ubicar_nave(cubo, {}, "F", (1, 1, 1), (1, 1, 2))
    assert len(flota_jugador) == 1
    assert tablero.contar_estado(cubo, tablero.NAVE) == 2
    assert flota_jugador["F_1"]["estado"] == "intacta"


def test_ubicacion_invalida():
    """Comprueba el error por ubicacion invalida"""
    cubo = tablero.crear_cubo(8)
    with pytest.raises(ValueError):
        flota.ubicar_nave(cubo, {}, "F", (1, 1, 1), (1, 2, 2))
    assert tablero.contar_estado(cubo, tablero.NAVE) == 0


def test_distancia_entre_naves():
    """Verifica la separacion entre naves"""
    cubo = tablero.crear_cubo(8)
    cubo, flota_jugador = flota.ubicar_nave(cubo, {}, "F", (1, 1, 1), (1, 1, 2))
    with pytest.raises(ValueError):
        flota.ubicar_nave(cubo, flota_jugador, "F", (1, 2, 1), (1, 2, 2))
    assert len(flota_jugador) == 1


def test_registrar_impacto():
    """Verifica los impactos y el hundimiento"""
    cubo = tablero.crear_cubo(8)
    cubo, flota_jugador = flota.ubicar_nave(cubo, {}, "F", (1, 1, 1), (1, 1, 2))
    resultado = flota.registrar_impacto(flota_jugador, cubo, (1, 1, 1))
    assert resultado["nuevo_estado"] == "averiada"
    assert not flota.flota_hundida(flota_jugador)
    resultado = flota.registrar_impacto(flota_jugador, cubo, (1, 1, 2))
    assert resultado["se_hundio"]
    assert flota.flota_hundida(flota_jugador)
    assert tablero.contar_estado(cubo, tablero.HUNDIDO) == 2


def test_ubicacion_automatica():
    """Verifica la ubicacion automatica de la flota"""
    cubo = tablero.crear_cubo(8)
    cubo, flota_jugador = flota.ubicacion_automatica(cubo, flota.CATALOGO_NAVES, 10)
    cantidad = 0
    celdas = 0
    for datos in flota.CATALOGO_NAVES.values():
        cantidad += datos["cantidad"]
        celdas += datos["cantidad"] * datos["tamanio"]
    assert len(flota_jugador) == cantidad
    assert tablero.contar_estado(cubo, tablero.NAVE) == celdas

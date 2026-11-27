import pytest
import tablero
import armamento


def test_inventario():
    """Verifica la municion inicial"""
    inventario = armamento.inventario_inicial()
    assert inventario["T"] == None
    assert inventario["R"] == 3
    armamento.consumir_municion(inventario, "R")
    assert inventario["R"] == 2
    armamento.consumir_municion(inventario, "T")
    assert inventario["T"] == None


def test_torpedo():
    """Verifica el disparo de un torpedo"""
    cubo = tablero.crear_cubo(8)
    tablero.escribir_celda(cubo, (2, 2, 2), tablero.NAVE)
    cubo, resultados = armamento.disparar(cubo, "T", (2, 2, 2))
    assert resultados[(2, 2, 2)] == "impacto"
    assert tablero.leer_celda(cubo, (2, 2, 2)) == tablero.IMPACTO
    cubo, resultados = armamento.disparar(cubo, "T", (1, 1, 1))
    assert resultados[(1, 1, 1)] == "agua"


def test_misil_racimo():
    """Verifica las celdas afectadas por el misil"""
    cubo = tablero.crear_cubo(8)
    inventario = armamento.inventario_inicial()
    cubo, resultados = armamento.disparar(cubo, "R", (3, 3, 3), inventario=inventario)
    assert len(resultados) == 7
    assert tablero.contar_estado(cubo, tablero.AGUA_MARCADA) == 7
    assert inventario["R"] == 2


def test_disparo_repetido():
    """Comprueba el error por disparo repetido"""
    cubo = tablero.crear_cubo(8)
    armamento.disparar(cubo, "T", (1, 1, 1))
    with pytest.raises(armamento.DisparoRepetidoError):
        armamento.disparar(cubo, "T", (1, 1, 1))


def test_sin_municion():
    """Comprueba el error por falta de municion"""
    cubo = tablero.crear_cubo(8)
    inventario = armamento.inventario_inicial()
    inventario["R"] = 0
    with pytest.raises(armamento.SinMunicionError):
        armamento.disparar(cubo, "R", (3, 3, 3), inventario=inventario)
    assert tablero.contar_estado(cubo, tablero.AGUA) == 512


def test_punto_invalido():
    """Comprueba el error por coordenada invalida"""
    cubo = tablero.crear_cubo(8)
    with pytest.raises(armamento.PuntoInvalidoError):
        armamento.disparar(cubo, "T", (0, 1, 1))


def test_puntos_onda():
    """Verifica las celdas alcanzadas por la onda"""
    assert armamento.puntos_onda(8, (3, 3, 3), 0, set()) == {(3, 3, 3)}
    assert len(armamento.puntos_onda(8, (3, 3, 3), 1, set())) == 7
    assert len(armamento.puntos_onda(8, (3, 3, 3), 2, set())) == 25

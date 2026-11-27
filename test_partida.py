import pytest
import partida
import tablero
import flota


def test_nueva_partida_1v1():
    """Verifica el estado inicial de una partida"""
    estado = partida.nueva_partida_1v1({"tamanio": 8})
    assert estado["tamanio"] == 8
    assert len(estado["jugadores"]) == 2
    assert estado["turno"] == 0
    assert estado["ganador"] == None
    assert not estado["jugadores"][0]["es_maquina"]
    assert not estado["jugadores"][1]["es_maquina"]


def test_nueva_partida_vs_maquina():
    """Verifica la creacion de una partida contra la maquina"""
    estado = partida.nueva_partida_vs_maquina({"tamanio": 8}, "avanzada")
    assert estado["jugadores"][1]["es_maquina"]
    assert estado["jugadores"][1]["dificultad"] == "avanzada"


def test_nueva_partida_maquina_vs_maquina():
    """Verifica la creacion de una partida entre maquinas"""
    estado = partida.nueva_partida_maquina_vs_maquina({"tamanio": 8})
    assert estado["jugadores"][0]["es_maquina"]
    assert estado["jugadores"][1]["es_maquina"]


def test_tamanio_invalido():
    """Comprueba el error por tamanio invalido"""
    with pytest.raises(partida.ErrorJuego):
        partida.nueva_partida_1v1({"tamanio": 4})


def test_ejecutar_turno():
    """Verifica el cambio de turno y el ganador"""
    estado = partida.nueva_partida_1v1({"tamanio": 8})
    for jugador in estado["jugadores"]:
        jugador["cubo"], jugador["flota"] = flota.ubicar_nave(
            jugador["cubo"], jugador["flota"], "F", (1, 1, 1), (1, 1, 2))
    estado = partida.ejecutar_turno(estado, {"arma": "T", "punto": (1, 1, 1)})
    assert estado["turno"] == 1
    assert estado["ganador"] == None
    assert tablero.leer_celda(estado["jugadores"][1]["cubo"], (1, 1, 1)) == tablero.IMPACTO
    estado = partida.ejecutar_turno(estado, {"arma": "T", "punto": (2, 2, 2)})
    assert estado["turno"] == 0
    estado = partida.ejecutar_turno(estado, {"arma": "T", "punto": (1, 1, 2)})
    assert partida.hay_ganador(estado) == "Jugador 1"
    assert estado["ganador"] == "Jugador 1"

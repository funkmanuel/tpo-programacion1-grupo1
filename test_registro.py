import os
import pytest
import registro
import partida
import flota


def test_registrar_accion():
    """Verifica el registro y la copia del historial"""
    historial = registro.crear_historial()
    assert historial == []
    registro.registrar_accion(historial, "Jugador 1", "ubicacion", "Flota ubicada")
    assert len(historial) == 1
    assert historial[0]["jugador"] == "Jugador 1"
    copia = registro.obtener_historial(historial)
    copia[0]["detalle"] = "Otro detalle"
    assert historial[0]["detalle"] == "Flota ubicada"


def test_estadisticas():
    """Verifica las estadisticas del jugador"""
    historial = registro.crear_historial()
    registro.registrar_disparo(historial, "Jugador 1", "T", {(1, 1, 1): "impacto"}, [])
    registro.registrar_disparo(historial, "Jugador 1", "T", {(2, 2, 2): "agua"}, [])
    registro.registrar_sonar(historial, "Jugador 1", "z", 1, [(1, 1, 2)])
    datos = registro.calcular_estadisticas(historial, "Jugador 1")
    assert datos["disparos"] == 2
    assert datos["aciertos"] == 1
    assert datos["impactos"] == 1
    assert datos["precision"] == 50
    assert datos["sonares"] == 1
    assert datos["contactos"] == 1


def test_nombre_invalido():
    """Comprueba el error por nombre invalido"""
    estado = partida.nueva_partida_1v1({"tamanio": 8})
    with pytest.raises(registro.RegistroError):
        registro.guardar_partida(estado, "???")


def test_guardar_y_cargar_partida():
    """Verifica el guardado y la recuperacion de una partida"""
    estado = partida.nueva_partida_1v1({"tamanio": 8})
    for jugador in estado["jugadores"]:
        jugador["cubo"], jugador["flota"] = flota.ubicar_nave(
            jugador["cubo"], jugador["flota"], "F", (1, 1, 1), (1, 1, 2))
    estado = partida.ejecutar_turno(estado, {"arma": "T", "punto": (1, 1, 1)})

    # Usamos otro archivo para no modificar las partidas reales.
    archivo_original = registro.ARCHIVO_PARTIDAS
    numero = 1
    archivo_prueba = "partidas_prueba_1.json"
    while os.path.exists(archivo_prueba):
        numero += 1
        archivo_prueba = f"partidas_prueba_{numero}.json"
    registro.ARCHIVO_PARTIDAS = archivo_prueba
    try:
        registro.guardar_partida(estado, "Prueba")
        assert registro.listar_partidas() == ["Prueba"]
        recuperada = registro.cargar_partida("Prueba")
        assert recuperada == estado
        with pytest.raises(registro.RegistroError):
            registro.cargar_partida("No existe")
    finally:
        registro.ARCHIVO_PARTIDAS = archivo_original

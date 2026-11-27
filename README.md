# Operacion Cubo

Trabajo Practico Integrador de Programacion 1 - UADE.

## Descripcion

Juego de batalla naval en 3D desarrollado en Python. Cada jugador tiene una flota de naves ubicada dentro de un cubo y el objetivo es hundir todas las naves del rival.

## Instalacion

Hay que tener Python 3 instalado y todos los archivos .py en la misma carpeta.

Para instalar pytest, desde la terminal ejecutar:

`python -m pip install -r requirements.txt`

## Ejecucion

Desde la terminal ejecutar:

`python partida.py`

## Opciones del juego

El menu principal permite:

- Jugar uno contra uno.
- Jugar contra la maquina.
- Simular una partida entre dos maquinas.
- Continuar una partida guardada.
- Salir del juego.
- Consultar el ranking.

Durante la partida se pueden utilizar distintas armas y el sonar, consultar el tablero por capas o cortes, ver el historial y las estadisticas, comparar las busquedas, elegir recorridos del cubo y guardar el progreso o terminar la partida.

En las partidas contra la maquina se puede elegir entre dificultad basica y avanzada. En la simulacion entre dos maquinas se puede avanzar un turno, diez turnos o jugar hasta el final, ademas de guardar o terminar la partida.

Las partidas se guardan en el archivo `partidas.json` y los resumenes de las partidas terminadas se pueden exportar a CSV.

## Modulos

- `tablero.py`: manejo del cubo.
- `flota.py`: ubicacion y estado de las naves.
- `radar.py`: busquedas, sonar y recorridos.
- `armamento.py`: armas y disparos.
- `registro.py`: historial y guardado de partidas.
- `partida.py`: menus, turnos e integracion del juego.

## Pruebas unitarias

Cada modulo tiene un archivo de pruebas que comienza con `test_`. Las pruebas se realizan con pytest para verificar el funcionamiento de las funciones del juego.

Para ejecutar todas las pruebas, desde la misma carpeta ejecutar:

`python -m pytest -v`

La distribucion de tareas de cada entrega esta registrada en `docs/bitacora.md`.

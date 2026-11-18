# Operacion Cubo

Trabajo Practico Integrador de Programacion 1 - UADE.

## Descripcion

Juego de batalla naval en 3D desarrollado en Python. Cada jugador tiene una flota de naves ubicada dentro de un cubo y el objetivo es hundir todas las naves del rival.

## Ejecucion

Para ejecutar el juego hay que tener Python 3 instalado y todos los archivos .py en la misma carpeta.

Desde la terminal ejecutar:

`python partida.py`

## Opciones del juego

El menu principal permite:

- Jugar uno contra uno.
- Jugar contra la maquina.
- Simular una partida entre dos maquinas.
- Continuar una partida guardada.
- Consultar el ranking.

Durante la partida se pueden utilizar distintas armas, consultar el tablero, ver las estadisticas y guardar el progreso.

## Modulos

- `tablero.py`: manejo del cubo.
- `flota.py`: ubicacion y estado de las naves.
- `radar.py`: busquedas, sonar y recorridos.
- `armamento.py`: armas y disparos.
- `registro.py`: historial y guardado de partidas.
- `partida.py`: menus, turnos e integracion del juego.

La distribucion de tareas de cada entrega esta registrada en `docs/bitacora.md`.

import logging
from . import (
    ejecutar_consulta,
    ejecutar_escalar,
    ejecutar_mutacion,
    listar_paginado,
)

logger = logging.getLogger(__name__)

COLUMNAS = 'id_cancha, nombre, id_deporte, precio_hora, techada, activa'
COLUMNAS_C = ', '.join(f'c.{columna}' for columna in COLUMNAS.split(', '))


def listar(id_deporte=None, nombre=None, techada=None, activa=None,
           limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
    """Retorna las canchas que cumplen los filtros y el total sin paginar."""
    return listar_paginado('canchas', {
        'id_deporte = ?':       id_deporte,
        'LOWER(nombre) LIKE ?': f'%{nombre.lower()}%' if nombre else None,
        'techada = ?':          techada,
        'activa = ?':           activa,
    }, orden='id_cancha', limit=limit, offset=offset)


def obtener_por_id(id_cancha: int) -> dict:
    """Retorna la cancha con el id dado, o un dict vacio si no existe."""
    filas = ejecutar_consulta(
        f'SELECT {COLUMNAS} FROM canchas WHERE id_cancha = :id_cancha',
        {'id_cancha': id_cancha},
    )

    return filas[0] if filas else {}


def insertar(nombre: str, id_deporte: int, precio_hora: int, techada: bool, activa: bool) -> int:
    """Inserta una cancha y retorna el id generado."""
    sql = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa)
    """

    return ejecutar_mutacion(sql, {
        'nombre':      nombre,
        'id_deporte':  id_deporte,
        'precio_hora': precio_hora,
        'techada':     techada,
        'activa':      activa,
    })


def actualizar(id_cancha: int, campos: dict) -> None:
    """Actualiza solo los campos presentes en `campos`."""
    asignaciones = ', '.join(f'{columna} = :{columna}' for columna in campos)

    ejecutar_mutacion(
        f'UPDATE canchas SET {asignaciones} WHERE id_cancha = :id_cancha',
        {**campos, 'id_cancha': id_cancha},
    )


def eliminar(id_cancha: int) -> None:
    """Elimina la cancha con el id dado."""
    ejecutar_mutacion('DELETE FROM canchas WHERE id_cancha = :id_cancha', {'id_cancha': id_cancha})


def tiene_reservas(id_cancha: int) -> bool:
    """Cuenta reservas de cualquier estado: una cancha con historial no se borra."""
    total = ejecutar_escalar(
        'SELECT COUNT(*) FROM reservas WHERE id_cancha = :id_cancha',
        {'id_cancha': id_cancha},
    )

    return bool(total)


def listar_disponibles(inicio, fin, id_deporte=None, techada=None,
                       limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
    """Canchas activas sin ninguna reserva confirmada superpuesta con el intervalo.

    La condicion `inicio < :fin AND fin > :inicio` cubre los cuatro casos de
    superposicion y deja pasar las reservas consecutivas.
    """
    condiciones = ['c.activa = TRUE']
    parametros = {'inicio': inicio, 'fin': fin}

    if id_deporte is not None:
        condiciones.append('c.id_deporte = :id_deporte')
        parametros['id_deporte'] = id_deporte

    if techada is not None:
        condiciones.append('c.techada = :techada')
        parametros['techada'] = techada

    where = ' AND '.join(condiciones)

    sin_superposicion = """
        NOT EXISTS (
            SELECT 1 FROM reservas r
            WHERE r.id_cancha = c.id_cancha
              AND r.estado = 'confirmada'
              AND r.fecha_hora_inicio < :fin
              AND r.fecha_hora_fin > :inicio
        )
    """

    total = ejecutar_escalar(
        f'SELECT COUNT(*) FROM canchas c WHERE {where} AND {sin_superposicion}',
        parametros,
    ) or 0

    filas = ejecutar_consulta(
        f"""
        SELECT {COLUMNAS_C}
        FROM canchas c
        WHERE {where} AND {sin_superposicion}
        ORDER BY c.id_cancha
        LIMIT :_limit OFFSET :_offset
        """,
        {**parametros, '_limit': limit, '_offset': offset},
    )

    return filas, total

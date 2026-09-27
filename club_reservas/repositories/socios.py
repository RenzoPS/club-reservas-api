import logging
from . import (
    ejecutar_consulta,
    ejecutar_escalar,
    ejecutar_mutacion,
    listar_paginado,
)

logger = logging.getLogger(__name__)


def listar_superposiciones_socio(inicio, fin, socio, limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
    '''
    Busca superposiciones por socio. No se debe cruzar ninguna reserva sin importar la cancha o el deporte.
    '''
    parametros_base = {'inicio': inicio, 'fin': fin, 'socio': socio}
    parametros_paginacion = {**parametros_base, '_limit': limit, '_offset': offset}
    
    query = '''
    FROM club.socios a

    INNER JOIN club.reservas r
    ON a.id_socio = r.id_socio

    WHERE a.id_socio = :socio
    AND a.activo = TRUE
    AND r.estado = 'confirmada'
    AND r.fecha_hora_inicio < :fin
    AND r.fecha_hora_fin > :inicio
    '''

    total = ejecutar_escalar(
        f'SELECT COUNT(r.id_reserva) {query}',
        parametros_base,
    ) or 0

    filas = ejecutar_consulta(
        f"""
        SELECT R.*
        {query}
        order by r.id_reserva
        LIMIT :_limit OFFSET :_offset
        """,
        parametros_paginacion
    )

    return filas, total
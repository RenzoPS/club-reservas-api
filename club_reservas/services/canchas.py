import logging
from ..constants import (
    ERROR_CODE_CANCHA_CON_RESERVAS,
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_DEPORTE_NOT_FOUND,
)
from ..paginacion import paginar
from ..utils import ErrorAPI
from ..repositories import canchas as db_canchas
from ..repositories import deportes as db_deportes

logger = logging.getLogger(__name__)

RUTA = '/canchas'


def construir_cancha_dto(cancha: dict) -> dict:
    """DTO publico de una cancha. MySQL devuelve los BOOLEAN como 0/1."""
    return {
        'id_cancha':   cancha['id_cancha'],
        'nombre':      cancha['nombre'],
        'id_deporte':  cancha['id_deporte'],
        'precio_hora': cancha['precio_hora'],
        'techada':     bool(cancha['techada']),
        'activa':      bool(cancha['activa']),
    }


def listar_canchas(filtros: dict, limit: int, offset: int) -> dict:
    """Retorna las canchas que cumplen los filtros, paginadas."""
    canchas, total = db_canchas.listar(**filtros, limit=limit, offset=offset)

    return paginar([construir_cancha_dto(c) for c in canchas], total, limit, offset,
                   'canchas', RUTA, filtros)


def listar_canchas_disponibles(filtros: dict, limit: int, offset: int) -> dict:
    """Retorna las canchas activas libres durante todo el intervalo, paginadas."""
    canchas, total = db_canchas.listar_disponibles(
        inicio=filtros['inicio'],
        fin=filtros['fin'],
        id_deporte=filtros['id_deporte'],
        techada=filtros['techada'],
        limit=limit,
        offset=offset,
    )

    enlaces = {'id_deporte': filtros['id_deporte'], 'techada': filtros['techada']}

    return paginar([construir_cancha_dto(c) for c in canchas], total, limit, offset,
                   'canchas', f'{RUTA}/disponibles', enlaces)


def buscar_cancha_por_id(id_cancha: int) -> dict:
    """Busca una cancha por id. Retorna {} si no existe."""
    cancha = db_canchas.obtener_por_id(id_cancha)

    if not cancha:
        return {}

    return construir_cancha_dto(cancha)


def crear_cancha(datos: dict) -> dict:
    """Crea una cancha. El deporte asociado debe existir."""
    if not db_deportes.existe(datos['id_deporte']):
        logger.warning(f"Alta de cancha con deporte inexistente: '{datos['id_deporte']}'")

        raise ErrorAPI(
            code=ERROR_CODE_DEPORTE_NOT_FOUND,
            message='Deporte no encontrado',
            description=f"No existe un deporte con id '{datos['id_deporte']}'",
            status=404,
        )

    id_cancha = db_canchas.insertar(**datos)

    return construir_cancha_dto(db_canchas.obtener_por_id(id_cancha))


def actualizar_cancha(id_cancha: int, campos: dict) -> dict:
    """Actualiza los campos recibidos. Los omitidos conservan su valor."""
    db_canchas.actualizar(id_cancha, campos)

    return construir_cancha_dto(db_canchas.obtener_por_id(id_cancha))


def eliminar_cancha(id_cancha: int) -> None:
    """Elimina una cancha. No se permite si tiene reservas asociadas."""
    if db_canchas.tiene_reservas(id_cancha):
        logger.warning(f"Intento de eliminar la cancha '{id_cancha}' con reservas asociadas")

        raise ErrorAPI(
            code=ERROR_CODE_CANCHA_CON_RESERVAS,
            message='La cancha tiene reservas asociadas',
            description=(
                f"No se puede eliminar la cancha '{id_cancha}' porque tiene reservas. "
                f"Se puede desactivar con PATCH"
            ),
            status=409,
        )

    db_canchas.eliminar(id_cancha)

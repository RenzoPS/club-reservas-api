import logging
from ..repositories import deportes as db_deportes

logger = logging.getLogger(__name__)


def construir_deporte_dto(deporte: dict) -> dict:
    """DTO publico de un deporte."""
    return {
        'id_deporte': deporte['id_deporte'],
        'nombre':     deporte['nombre'],
    }


def listar_deportes() -> list[dict]:
    """Retorna todos los deportes precargados."""
    return [construir_deporte_dto(d) for d in db_deportes.listar()]

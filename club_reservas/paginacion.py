"""Paginacion y enlaces HATEOAS de los listados."""
from urllib.parse import urlencode

from .constants import LIMIT_DEFAULT, LIMIT_MAX, LIMIT_MIN, OFFSET_DEFAULT
from .utils import validar_entero, validar_maximo, validar_minimo

PARAMETROS_PAGINACION = {'_limit', '_offset'}


def leer_parametros_paginacion(args) -> tuple[int, int]:
    """Lee y valida _limit (1 a 100, default 10) y _offset (>= 0, default 0)."""
    limit = validar_entero(args.get('_limit', LIMIT_DEFAULT), '_limit')
    limit = validar_maximo(validar_minimo(limit, LIMIT_MIN, '_limit'), LIMIT_MAX, '_limit')

    offset = validar_minimo(validar_entero(args.get('_offset', OFFSET_DEFAULT), '_offset'), 0, '_offset')

    return limit, offset


def _enlace(path: str, limit: int, offset: int, filtros: dict) -> str:
    # Los booleanos van como true/false: urlencode los serializaria como True/False.
    parametros = {
        clave: ('true' if valor else 'false') if isinstance(valor, bool) else valor
        for clave, valor in (filtros or {}).items() if valor is not None
    }
    parametros['_limit'] = limit
    parametros['_offset'] = offset

    return f'{path}?{urlencode(parametros)}'


def paginar(items: list, total: int, limit: int, offset: int, recurso: str, path: str,
            filtros: dict | None = None) -> dict:
    """Arma la respuesta paginada. `total` es la cantidad de filas sin paginar.

    Los filtros activos viajan en los enlaces: sin eso, al cambiar de pagina
    se pierde el criterio de busqueda.
    """
    ultimo_offset = ((total - 1) // limit) * limit if total else 0

    hay_anterior = offset > 0
    hay_siguiente = offset + limit < total

    return {
        recurso: items,
        '_limit': limit,
        '_offset': offset,
        '_links': {
            '_first': _enlace(path, limit, 0, filtros),
            '_prev': _enlace(path, limit, max(offset - limit, 0), filtros) if hay_anterior else None,
            '_next': _enlace(path, limit, offset + limit, filtros) if hay_siguiente else None,
            '_last': _enlace(path, limit, ultimo_offset, filtros),
        },
    }

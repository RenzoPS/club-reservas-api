"""Acceso a datos con SQLAlchemy sin ORM: SQL a mano, ejecutado con text().

Los valores van siempre como parametros (:nombre), nunca concatenados al string.
"""
from sqlalchemy import create_engine, text

from ..constants import DB_URL

motor = create_engine(DB_URL, pool_pre_ping=True)


def fila_a_dict(fila) -> dict:
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict | None = None) -> list[dict]:
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_escalar(sql: str, parametros: dict | None = None):
    """Para los SELECT que devuelven un unico valor, como los COUNT."""
    with motor.connect() as conexion:
        return conexion.execute(text(sql), parametros or {}).scalar()


def ejecutar_mutacion(sql: str, parametros: dict | None = None) -> int:
    """Ejecuta INSERT/UPDATE/DELETE con commit. Devuelve el id generado."""
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0


def listar_paginado(tabla: str, filtros: dict, orden: str, limit: int, offset: int) -> tuple[list[dict], int]:
    """Listado con filtros opcionales y paginacion. Devuelve (pagina, total sin paginar).

    Cada clave de `filtros` es una condicion con un '?' donde va el valor, y los
    filtros en None se ignoran:

        listar_paginado('canchas', {
            'id_deporte = ?':       id_deporte,
            'LOWER(nombre) LIKE ?': f'%{nombre.lower()}%' if nombre else None,
            'activa = ?':           activa,
        }, orden='id_cancha', limit=limit, offset=offset)

    `tabla` y `orden` se interpolan, asi que solo pueden ser literales del
    codigo, nunca datos que llegaron por la request.
    """
    condiciones = []
    parametros = {}

    for indice, (condicion, valor) in enumerate(filtros.items()):
        if valor is None:
            continue

        clave = f'f{indice}'
        condiciones.append(condicion.replace('?', f':{clave}'))
        parametros[clave] = valor

    where = ('WHERE ' + ' AND '.join(condiciones)) if condiciones else ''

    total = ejecutar_escalar(f'SELECT COUNT(*) FROM {tabla} {where}', parametros) or 0

    filas = ejecutar_consulta(
        f'SELECT * FROM {tabla} {where} ORDER BY {orden} LIMIT :_limit OFFSET :_offset',
        {**parametros, '_limit': limit, '_offset': offset},
    )

    return filas, total

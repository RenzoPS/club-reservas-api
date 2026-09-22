"""Acceso a datos: motor de conexion y helpers de ejecucion.

Se usa SQLAlchemy sin ORM: el SQL se escribe a mano y se ejecuta con text().

Los valores van siempre como parametros (:nombre), nunca concatenados
al string.

    sql = 'SELECT * FROM canchas WHERE id = :id'
    ejecutar_consulta(sql, {'id': id_cancha})
"""
from sqlalchemy import create_engine, text

from ..constants import DB_URL

motor = create_engine(DB_URL, pool_pre_ping=True)


def fila_a_dict(fila) -> dict:
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict | None = None) -> list[dict]:
    """Ejecuta un SELECT y devuelve las filas como lista de dicts."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_escalar(sql: str, parametros: dict | None = None):
    """Ejecuta un SELECT que devuelve un unico valor. Util para los COUNT."""
    with motor.connect() as conexion:
        return conexion.execute(text(sql), parametros or {}).scalar()


def ejecutar_mutacion(sql: str, parametros: dict | None = None) -> int:
    """Ejecuta INSERT/UPDATE/DELETE con commit. Devuelve el id generado."""
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0

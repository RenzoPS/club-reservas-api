from . import ejecutar_consulta, ejecutar_escalar, ejecutar_mutacion, listar_paginado

def listar_reservas(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None, limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
    """
    Listado de reservas con filtros opcionales y paginado.
    """
    return listar_paginado('reservas', {
        'id_cancha = ?': id_cancha,
        'id_socio = ?': id_socio,
        'estado = ?': estado,
        'DATE(fecha_hora_inicio) >= ?': fecha_desde,
        'DATE(fecha_hora_inicio) <= ?': fecha_hasta,
    }, orden='id_reserva', limit=limit, offset=offset)


def obtener_reserva_por_id(id_reserva: int) -> dict:
    """
    Busca una reserva por su ID. Devuelve {} si no existe.
    """

    sql = """
        SELECT id_reserva, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora_aplicado, total
        FROM reservas
        WHERE id_reserva = :id_reserva
    """
    filas = ejecutar_consulta(sql, {'id_reserva': id_reserva})
    if filas:
        resultado_final = filas[0]
    else:
        resultado_final = {}
    return resultado_final


def agregar_reserva(id_socio: int, id_cancha: int, fecha_hora_inicio, fecha_hora_fin, precio_hora_aplicado: int, total: int) -> int:
    """
    Guarda una reserva.
    """
    sql = """
        INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, precio_hora_aplicado, total)
        VALUES (:id_socio, :id_cancha, :fecha_hora_inicio, :fecha_hora_fin, :precio_hora_aplicado, :total)
    """
    return ejecutar_mutacion(sql, {
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': fecha_hora_inicio,
        'fecha_hora_fin': fecha_hora_fin,
        'precio_hora_aplicado': precio_hora_aplicado,
        'total': total,
    })


def actualizar_reserva(id_reserva: int, nuevo_estado: str) -> None:
    """
    Modifica el estado de una reserva.
    """
    sql = """
        UPDATE reservas
        SET estado = :nuevo_estado
        WHERE id_reserva = :id_reserva
    """
    ejecutar_mutacion(sql, {
        'id_reserva': id_reserva,
        'nuevo_estado': nuevo_estado,
    })


def existe_superposicion_cancha(id_cancha: int, inicio, fin) -> bool:
    """
    True si esa cancha ya tiene una reserva confirmada que se superpone con [inicio, fin).
    """
    total = ejecutar_escalar(
        """
        SELECT COUNT(*) FROM reservas
        WHERE id_cancha = :id_cancha
            AND estado = 'confirmada'
            AND fecha_hora_inicio < :fin
            AND fecha_hora_fin > :inicio
        """,
        {'id_cancha': id_cancha, 'inicio': inicio, 'fin': fin},
    )

    return bool(total)


def existe_superposicion_socio(id_socio: int, inicio, fin) -> bool:
    """
    True si el socio ya tiene una reserva confirmada que se superpone con [inicio, fin).
    """
    total = ejecutar_escalar(
        """
        SELECT COUNT(*) FROM reservas
        WHERE id_socio = :id_socio
            AND estado = 'confirmada'
            AND fecha_hora_inicio < :fin
            AND fecha_hora_fin > :inicio
        """,
        {'id_socio': id_socio, 'inicio': inicio, 'fin': fin},
    )

    return bool(total)
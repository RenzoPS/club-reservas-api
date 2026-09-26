from . import ejecutar_consulta


def listar() -> list[dict]:
    """Retorna todos los deportes ordenados por id."""
    return ejecutar_consulta('SELECT id_deporte, nombre FROM deportes ORDER BY id_deporte')


def existe(id_deporte: int) -> bool:
    """Indica si existe un deporte con el id dado."""
    filas = ejecutar_consulta(
        'SELECT 1 FROM deportes WHERE id_deporte = :id_deporte',
        {'id_deporte': id_deporte},
    )

    return len(filas) > 0

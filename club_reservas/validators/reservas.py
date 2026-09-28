# validators/reservas.py
"""Validaciones específicas del dominio de reservas."""


from ..constants import (
    ERROR_CODE_INVALID_FORMAT,
    ERROR_CODE_INVALID_BODY,
)
from ..utils import (
    ErrorAPI,
    rechazar_campos_desconocidos,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_estado,
    validar_intervalo,
    validar_inicio_futuro,
    parsear_fecha,
    parsear_fecha_hora,
)


# ===============================================================
# Campos permitidos
# ===============================================================

CAMPOS_RESERVA_CREATE = {
    'id_socio',
    'id_cancha',
    'fecha_hora_inicio',
    'fecha_hora_fin',
}

CAMPOS_ESTADO = {
    'estado',
}

CAMPOS_FILTROS_RESERVA = {
    'id_cancha',
    'id_socio',
    'estado',
    'fecha_desde',
    'fecha_hasta',
    '_limit',
    '_offset',
}

# ===============================================================
# Creación de reservas
# ===============================================================

def validar_reserva_create(body: dict) -> dict:
    """
    Valida y normaliza el cuerpo de POST /reservas.

    No verifica existencia de socio/cancha ni superposiciones:
    esas validaciones requieren acceso a datos y corresponden al service.
    """
    body = validar_cuerpo_no_vacio(body, 'cuerpo')

    rechazar_campos_desconocidos(
        body,
        CAMPOS_RESERVA_CREATE,
        'cuerpo'
    )

    campos_obligatorios = CAMPOS_RESERVA_CREATE

    faltantes = campos_obligatorios - set(body.keys())

    if faltantes:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_BODY,
            message='Faltan campos obligatorios',
            description=(
                'Los campos obligatorios son: '
                + ', '.join(sorted(campos_obligatorios))
            )
        )

    id_socio = validar_entero_positivo(
        body['id_socio'],
        'id_socio'
    )

    id_cancha = validar_entero_positivo(
        body['id_cancha'],
        'id_cancha'
    )

    inicio = parsear_fecha_hora(
        body['fecha_hora_inicio'],
        'fecha_hora_inicio'
    )

    fin = parsear_fecha_hora(
        body['fecha_hora_fin'],
        'fecha_hora_fin'
    )

    # Reutiliza todas las reglas generales:
    # - inicio < fin
    # - horas en punto
    # - mismo día
    # - duración 1 a 3 horas
    # - horario 08:00 a 23:00
    horas = validar_intervalo(inicio, fin)

    # Regla exclusiva de creación de reservas:
    # el inicio debe ser posterior al momento actual.
    validar_inicio_futuro(inicio)

    return {
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': inicio,
        'fecha_hora_fin': fin,
        'horas': horas,
    }


# ===============================================================
# Estado de una reserva
# ===============================================================

def validar_estado_update(body: dict) -> str:
    """
    Valida el cuerpo de PUT /reservas/{id}/estado.
    """
    body = validar_cuerpo_no_vacio(body, 'cuerpo')

    rechazar_campos_desconocidos(
        body,
        CAMPOS_ESTADO,
        'cuerpo'
    )

    if 'estado' not in body:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_BODY,
            message='Falta el campo estado',
            description="El campo 'estado' es obligatorio"
        )

    return validar_estado(body['estado'])


# ===============================================================
# Filtros de GET /reservas
# ===============================================================

def validar_filtros_reservas(args) -> dict:
    """
    Valida los filtros propios de GET /reservas.

    La paginación (_limit y _offset) se valida por separado mediante
    paginacion.py.
    """

    rechazar_campos_desconocidos(
        args,
        CAMPOS_FILTROS_RESERVA,
        'parametros de consulta'
    )

    filtros = {}

    if args.get('id_cancha') is not None:
        filtros['id_cancha'] = validar_entero_positivo(
            args.get('id_cancha'),
            'id_cancha'
        )

    if args.get('id_socio') is not None:
        filtros['id_socio'] = validar_entero_positivo(
            args.get('id_socio'),
            'id_socio'
        )

    if args.get('estado') is not None:
        filtros['estado'] = validar_estado(
            args.get('estado')
        )

    fecha_desde = None
    fecha_hasta = None

    if args.get('fecha_desde') is not None:
        fecha_desde = parsear_fecha(
            args.get('fecha_desde'),
            'fecha_desde'
        ).date()

        filtros['fecha_desde'] = fecha_desde.isoformat()

    if args.get('fecha_hasta') is not None:
        fecha_hasta = parsear_fecha(
            args.get('fecha_hasta'),
            'fecha_hasta'
        ).date()

        filtros['fecha_hasta'] = fecha_hasta.isoformat()

    if (
        fecha_desde is not None
        and fecha_hasta is not None
        and fecha_desde > fecha_hasta
    ):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message='Rango de fechas invalido',
            description=(
                "El parametro 'fecha_desde' debe ser menor o igual "
                "que 'fecha_hasta'"
            )
        )

    return filtros


# ===============================================================
# Validación de ID de reserva
# ===============================================================

def validar_id_reserva(id_reserva) -> int:
    """
    Valida el ID utilizado en /reservas/{id}.
    """
    return validar_entero_positivo(
        id_reserva,
        'id'
    )

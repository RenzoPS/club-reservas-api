"""Validaciones específicas del dominio de reservas."""

import re
from datetime import datetime, date

from constants import (
    ERROR_CODE_INVALID_FORMAT,
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_SUPERPOSICION_CANCHA,
    ERROR_CODE_SUPERPOSICION_SOCIO,
    ERROR_CODE_TRANSICION_INVALIDA,
    ESTADO_CONFIRMADA,
    ESTADO_CANCELADA,
    ESTADO_FINALIZADA,
    ESTADOS_VALIDOS,
)
from utils import (
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
# Formato de fecha/hora
# ===============================================================

# El enunciado exige exactamente:
# YYYY-MM-DDTHH:MM:SS.ffffff-03:00
PATRON_FECHA_HORA_RESERVA = re.compile(
    r'^\d{4}-\d{2}-\d{2}'
    r'T\d{2}:\d{2}:\d{2}'
    r'\.\d{6}'
    r'-03:00$'
)


def validar_formato_fecha_hora_reserva(
    valor,
    nombre: str = 'fecha_hora'
) -> datetime:
    """
    Valida que una fecha/hora tenga exactamente el formato requerido
    por el TP y luego reutiliza parsear_fecha_hora() de utils.py.
    """
    if not isinstance(valor, str):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=(
                f"El campo '{nombre}' debe tener el formato "
                "YYYY-MM-DDTHH:MM:SS.ffffff-03:00"
            )
        )

    if not PATRON_FECHA_HORA_RESERVA.fullmatch(valor):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=(
                f"El valor '{valor}' no cumple el formato "
                "YYYY-MM-DDTHH:MM:SS.ffffff-03:00"
            )
        )

    # Reutilizamos la validación existente de utils.py.
    return parsear_fecha_hora(valor, nombre)


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

    inicio = validar_formato_fecha_hora_reserva(
        body['fecha_hora_inicio'],
        'fecha_hora_inicio'
    )

    fin = validar_formato_fecha_hora_reserva(
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


def validar_transicion_estado(
    estado_actual: str,
    estado_solicitado: str,
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime,
    ahora: datetime,
) -> bool:
    """
    Valida si una transición de estado está permitida.

    Devuelve True si la transición es válida.

    La repetición del estado actual es válida y no modifica nada.

    Reglas del TP:

        confirmada -> cancelada
            solo antes del inicio.

        confirmada -> finalizada
            cuando se alcanzó o superó el fin.

        cancelada -> cualquier otro estado
            no permitido.

        finalizada -> cualquier otro estado
            no permitido.
    """

    # Repetir el estado actual siempre es válido.
    if estado_actual == estado_solicitado:
        return True

    if estado_actual not in ESTADOS_VALIDOS:
        raise ErrorAPI(
            code=ERROR_CODE_TRANSICION_INVALIDA,
            message='Estado actual invalido',
            description=(
                f"El estado actual '{estado_actual}' no es un estado "
                "valido de reserva"
            ),
            status=409
        )

    if estado_solicitado not in ESTADOS_VALIDOS:
        raise ErrorAPI(
            code=ERROR_CODE_TRANSICION_INVALIDA,
            message='Estado solicitado invalido',
            description=(
                f"El estado solicitado '{estado_solicitado}' no es valido"
            ),
            status=409
        )

    # -----------------------------------------------------------
    # confirmada -> cancelada
    # -----------------------------------------------------------
    if (
        estado_actual == ESTADO_CONFIRMADA
        and estado_solicitado == ESTADO_CANCELADA
    ):
        if ahora >= fecha_hora_inicio:
            raise ErrorAPI(
                code=ERROR_CODE_TRANSICION_INVALIDA,
                message='No se puede cancelar la reserva',
                description=(
                    'Una reserva confirmada solo puede cancelarse '
                    'antes de su horario de inicio'
                ),
                status=409
            )

        return True

    # -----------------------------------------------------------
    # confirmada -> finalizada
    # -----------------------------------------------------------
    if (
        estado_actual == ESTADO_CONFIRMADA
        and estado_solicitado == ESTADO_FINALIZADA
    ):
        if ahora < fecha_hora_fin:
            raise ErrorAPI(
                code=ERROR_CODE_TRANSICION_INVALIDA,
                message='No se puede finalizar la reserva',
                description=(
                    'Una reserva solo puede finalizarse cuando se '
                    'alcanzó o superó su horario de finalización'
                ),
                status=409
            )

        return True

    # Cualquier otra transición es inválida.
    raise ErrorAPI(
        code=ERROR_CODE_TRANSICION_INVALIDA,
        message='Transicion de estado no permitida',
        description=(
            f"No se permite cambiar una reserva de estado "
            f"'{estado_actual}' a '{estado_solicitado}'"
        ),
        status=409
    )


# ===============================================================
# Superposiciones
# ===============================================================

def intervalos_se_superponen(
    inicio_1: datetime,
    fin_1: datetime,
    inicio_2: datetime,
    fin_2: datetime,
) -> bool:
    """
    Determina si dos intervalos se superponen.

    Los extremos son abiertos a efectos de superposición:

        18:00 - 20:00
        20:00 - 21:00

    NO se superponen.

    En cambio:

        18:00 - 20:00
        19:00 - 21:00

    sí se superponen.
    """
    return inicio_1 < fin_2 and inicio_2 < fin_1


def validar_no_superposicion(
    inicio: datetime,
    fin: datetime,
    reservas: list,
    *,
    tipo: str = 'cancha',
) -> None:
    """
    Valida que el intervalo no se superponga con ninguna reserva
    confirmada recibida.

    Esta función no consulta la BD. El service/repository debe obtener
    previamente las reservas relevantes.

    Cada elemento de `reservas` puede ser:

        - un objeto con fecha_hora_inicio / fecha_hora_fin / estado
        - un diccionario con esas claves.

    Solo se consideran reservas confirmadas.
    """

    if tipo == 'cancha':
        codigo = ERROR_CODE_SUPERPOSICION_CANCHA
        descripcion_recurso = 'la cancha'
    elif tipo == 'socio':
        codigo = ERROR_CODE_SUPERPOSICION_SOCIO
        descripcion_recurso = 'el socio'
    else:
        raise ValueError(
            "El parametro 'tipo' debe ser 'cancha' o 'socio'"
        )

    for reserva in reservas:
        estado = _obtener_campo(reserva, 'estado')

        if estado != ESTADO_CONFIRMADA:
            continue

        existente_inicio = _obtener_campo(
            reserva,
            'fecha_hora_inicio'
        )
        existente_fin = _obtener_campo(
            reserva,
            'fecha_hora_fin'
        )

        if intervalos_se_superponen(
            inicio,
            fin,
            existente_inicio,
            existente_fin
        ):
            raise ErrorAPI(
                code=codigo,
                message=f'Superposicion de reserva en {descripcion_recurso}',
                description=(
                    'El intervalo solicitado se superpone con una '
                    'reserva confirmada existente'
                ),
                status=409
            )


def _obtener_campo(objeto, campo: str):
    """
    Permite trabajar tanto con diccionarios como con objetos/modelos.
    """
    if isinstance(objeto, dict):
        return objeto[campo]

    return getattr(objeto, campo)


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
            args.get('estado'),
            'estado'
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


# ===============================================================
# Validación completa de un intervalo de consulta
# ===============================================================

def validar_intervalo_reserva(
    fecha_hora_inicio,
    fecha_hora_fin,
    *,
    exigir_futuro: bool = True,
) -> dict:
    """
    Valida un intervalo completo.

    Sirve tanto para:
        - POST /reservas
        - GET /canchas/disponibles
        - reservas recurrentes

    `exigir_futuro=True` reproduce la regla de una reserva nueva.
    """

    inicio = validar_formato_fecha_hora_reserva(
        fecha_hora_inicio,
        'fecha_hora_inicio'
    )

    fin = validar_formato_fecha_hora_reserva(
        fecha_hora_fin,
        'fecha_hora_fin'
    )

    horas = validar_intervalo(inicio, fin)

    if exigir_futuro:
        validar_inicio_futuro(inicio)

    return {
        'fecha_hora_inicio': inicio,
        'fecha_hora_fin': fin,
        'horas': horas,
    }


# ===============================================================
# Reservas recurrentes - extensión opcional
# ===============================================================

CAMPOS_RESERVA_RECURRENTES = {
    'id_socio',
    'id_cancha',
    'fecha_hora_inicio',
    'fecha_hora_fin',
    'cantidad_semanas',
}


def validar_reserva_recurrente_create(body: dict) -> dict:
    """
    Valida el cuerpo de POST /reservas/recurrentes.

    No verifica existencia de entidades ni conflictos con la BD.
    """

    body = validar_cuerpo_no_vacio(body, 'cuerpo')

    rechazar_campos_desconocidos(
        body,
        CAMPOS_RESERVA_RECURRENTES,
        'cuerpo'
    )

    faltantes = CAMPOS_RESERVA_RECURRENTES - set(body.keys())

    if faltantes:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_BODY,
            message='Faltan campos obligatorios',
            description=(
                'Los campos obligatorios son: '
                + ', '.join(sorted(CAMPOS_RESERVA_RECURRENTES))
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

    cantidad_semanas = validar_entero_positivo(
        body['cantidad_semanas'],
        'cantidad_semanas'
    )

    if cantidad_semanas < 2 or cantidad_semanas > 12:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message='Cantidad de semanas invalida',
            description=(
                "El campo 'cantidad_semanas' debe estar entre 2 y 12"
            )
        )

    intervalo = validar_intervalo_reserva(
        body['fecha_hora_inicio'],
        body['fecha_hora_fin'],
        exigir_futuro=True
    )

    return {
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': intervalo['fecha_hora_inicio'],
        'fecha_hora_fin': intervalo['fecha_hora_fin'],
        'horas': intervalo['horas'],
        'cantidad_semanas': cantidad_semanas,
    }


def generar_intervalos_recurrentes(
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime,
    cantidad_semanas: int,
) -> list[tuple[datetime, datetime]]:
    """
    Genera los intervalos semanales de una reserva recurrente.

    Ejemplo:
        15/10 -> 22/10 -> 29/10 -> ...

    La primera fecha está incluida.
    """

    from datetime import timedelta

    intervalos = []

    for semana in range(cantidad_semanas):
        desplazamiento = timedelta(weeks=semana)

        inicio = fecha_hora_inicio + desplazamiento
        fin = fecha_hora_fin + desplazamiento

        intervalos.append((inicio, fin))

    return intervalos


def validar_intervalos_recurrentes(
    intervalos: list[tuple[datetime, datetime]],
) -> None:
    """
    Valida todos los intervalos de una serie.

    Es útil antes de comenzar una operación transaccional.
    """

    for inicio, fin in intervalos:
        validar_intervalo(inicio, fin)
        validar_inicio_futuro(inicio)

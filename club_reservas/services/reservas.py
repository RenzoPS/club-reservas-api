from datetime import datetime
from ..constants import(
    ERROR_CODE_CANCHA_INACTIVA,
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_RESERVA_NOT_FOUND,
    ERROR_CODE_SOCIO_INACTIVO,
    ERROR_CODE_SOCIO_NOT_FOUND,
    ERROR_CODE_SUPERPOSICION_CANCHA,
    ERROR_CODE_SUPERPOSICION_SOCIO,
    ERROR_CODE_TRANSICION_INVALIDA,
    ESTADO_CANCELADA,
    ESTADO_CONFIRMADA,
    ESTADO_FINALIZADA,
    OFFSET_ESPERADO,
    TZ_ARG
)
from ..paginacion import paginar
from ..repositories import canchas as db_canchas
from ..repositories import reservas as db_reservas
from ..repositories import socios as db_socios
from ..utils import ErrorAPI, calcular_horas


def construir_reserva_dto(reserva: dict) -> dict:
    """
    DTO publico de una reserva.
    """
    return {
        'id_reserva':reserva['id_reserva'],
        'id_socio':reserva['id_socio'],
        'id_cancha':reserva['id_cancha'],
        'fecha_hora_inicio':reserva['fecha_hora_inicio'].strftime('%Y-%m-%dT%H:%M:%S.%f') + OFFSET_ESPERADO,
        'fecha_hora_fin': reserva['fecha_hora_fin'].strftime('%Y-%m-%dT%H:%M:%S.%f') + OFFSET_ESPERADO,
        'estado':reserva['estado'],
        'precio_hora_aplicado':reserva['precio_hora_aplicado'],
        'total':reserva['total']
    }

def listar_reservas(filtros: dict, limit: int, offset: int) -> dict:
    """
    Retorna las reservas que cumplen los filtros.
    """
    reservas, total= db_reservas.listar_reservas(**filtros, limit= limit, offset=offset)
    reservas_dto = []
    for i in reservas:
        reservas_dto.append(construir_reserva_dto(i))

    return paginar(reservas_dto, total, limit, offset, "reservas", "/reservas", filtros)

def buscar_reserva_por_id(id_reserva: int) -> dict:
    """
    Busca una reserva por id. Retorna {} si no existe.
    """
    reserva =db_reservas.obtener_reserva_por_id(id_reserva)

    if reserva:
        resultado = construir_reserva_dto(reserva)
    else:
        resultado = {}

    return resultado


def _validar_cancha_disponible_para_reserva(id_cancha: int) -> dict:
    """
    Verifica que la cancha exista y este activa. 
    """
    cancha = db_canchas.obtener_por_id(id_cancha)
    if not cancha:
        raise ErrorAPI(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{id_cancha}'",
            status=404,
        )
    if not cancha['activa']:
        raise ErrorAPI(
            code=ERROR_CODE_CANCHA_INACTIVA,
            message='Cancha inactiva',
            description=f"La cancha '{id_cancha}' esta inactiva y no admite nuevas reservas",
            status=409,
        )
    return cancha

def _validar_socio_disponible_para_reserva(id_socio: int) -> None:
    """
    Verifica que el socio exista y este activo.
    """
    socio = db_socios.obtener_por_id(id_socio)
    if not socio:
        raise ErrorAPI(
            code=ERROR_CODE_SOCIO_NOT_FOUND,
            message='Socio no encontrado',
            description=f"No existe un socio con id '{id_socio}'",
            status=404,
        )
    if not socio['activo']:
        raise ErrorAPI(
            code=ERROR_CODE_SOCIO_INACTIVO,
            message='Socio inactivo',
            description=f"El socio '{id_socio}' esta inactivo y no admite nuevas reservas",
            status=409,
        )

def _validar_sin_superposiciones(id_cancha: int, id_socio: int, inicio, fin) -> None:
    """
    Verifica disponibilidad de horario antes de guardar.
    """
    if db_reservas.existe_superposicion_cancha(id_cancha, inicio, fin):
        raise ErrorAPI(
            code=ERROR_CODE_SUPERPOSICION_CANCHA,
            message='La cancha ya esta reservada en ese horario',
            description=f"La cancha '{id_cancha}' ya tiene una reserva que se superpone con el intervalo solicitado",
            status=409,
        )

    if db_reservas.existe_superposicion_socio(id_socio, inicio, fin):
        raise ErrorAPI(
            code=ERROR_CODE_SUPERPOSICION_SOCIO,
            message='El socio ya tiene una reserva en ese horario',
            description=f"El socio '{id_socio}' tiene una reserva que se superpone con el intervalo solicitado",
            status=409,
        )

def crear_reserva(id_socio: int, id_cancha: int, fecha_hora_inicio, fecha_hora_fin) -> dict:
    """
    Crea una reserva revisando que la cancha y el socio esten libres, se calcula la tarifa y se revisa el horario. Si algo falla no se guarda nada
    """
    cancha = _validar_cancha_disponible_para_reserva(id_cancha)
    _validar_socio_disponible_para_reserva(id_socio)
    _validar_sin_superposiciones(id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin)
    horas = calcular_horas(fecha_hora_inicio, fecha_hora_fin)
    precio_hora_aplicado = cancha['precio_hora']
    total = precio_hora_aplicado * horas
    id_reserva = db_reservas.agregar_reserva(
        id_socio=id_socio,
        id_cancha=id_cancha,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        precio_hora_aplicado=precio_hora_aplicado,
        total=total,
    )
    return construir_reserva_dto(db_reservas.obtener_reserva_por_id(id_reserva))


def _validar_transicion(estado_actual: str, nuevo_estado: str, reserva: dict) -> None:
    """
    Revisa si un cambio de estado es valido en la reserva.
    """
    ahora = datetime.now(TZ_ARG).replace(tzinfo=None)

    if estado_actual == ESTADO_CONFIRMADA and nuevo_estado == ESTADO_CANCELADA:
        if ahora >= reserva['fecha_hora_inicio']:
            raise ErrorAPI(
                code=ERROR_CODE_TRANSICION_INVALIDA,
                message='No se puede cancelar la reserva',
                description='La reserva comenzo, no puede ser cancelada',
                status=409,
            )
        
    elif estado_actual == ESTADO_CONFIRMADA and nuevo_estado == ESTADO_FINALIZADA:
        if ahora < reserva['fecha_hora_fin']:
            raise ErrorAPI(
                code=ERROR_CODE_TRANSICION_INVALIDA,
                message='No se puede finalizar la reserva',
                description='Todavia no se alcanzo el horario de finalizacion',
                status=409,
            )
    else:
        raise ErrorAPI(
            code=ERROR_CODE_TRANSICION_INVALIDA,
            message='Transicion de estado no permitida',
            description=f"No se puede pasar del estado '{estado_actual}' a '{nuevo_estado}'",
            status=409,
        )


def cambiar_estado_reserva(id_reserva: int, nuevo_estado: str) -> dict:
    """
    Actualiza el estado de una reserva de ser necesario.
    """
    reserva = db_reservas.obtener_reserva_por_id(id_reserva)

    if not reserva:
        raise ErrorAPI(
            code=ERROR_CODE_RESERVA_NOT_FOUND,
            message='Reserva no encontrada',
            description=f"No existe una reserva con id '{id_reserva}'",
            status=404,
        )

    estado_actual = reserva['estado']
    if nuevo_estado != estado_actual:
        _validar_transicion(estado_actual, nuevo_estado, reserva)
        db_reservas.actualizar_reserva(id_reserva, nuevo_estado)
        reserva = db_reservas.obtener_reserva_por_id(id_reserva)
    return construir_reserva_dto(reserva)
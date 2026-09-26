"""Validacion de la entrada de canchas: forma y tipos, sin tocar la base."""
from datetime import datetime

from ..constants import FORMATO_HORA, TZ_ARG
from ..paginacion import PARAMETROS_PAGINACION
from ..utils import (
    ErrorAPI,
    parsear_fecha,
    rechazar_campos_desconocidos,
    validar_booleano,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_intervalo,
    validar_inicio_futuro,
    validar_string_no_vacio,
)
from ..constants import ERROR_CODE_INVALID_FORMAT

CAMPOS_ALTA = {'nombre', 'id_deporte', 'precio_hora', 'techada', 'activa'}
CAMPOS_EDITABLES = {'nombre', 'precio_hora', 'techada', 'activa'}
FILTROS_LISTADO = {'id_deporte', 'nombre', 'techada', 'activa'} | PARAMETROS_PAGINACION
FILTROS_DISPONIBLES = {'fecha', 'hora_inicio', 'hora_fin', 'id_deporte', 'techada'} | PARAMETROS_PAGINACION


def validar_id_cancha(id_cancha) -> int:
    return validar_entero_positivo(id_cancha, 'id_cancha')


def validar_body_nueva_cancha(body) -> dict:
    validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(body, CAMPOS_ALTA)

    return {
        'nombre':      validar_string_no_vacio(body.get('nombre'), 'nombre'),
        'id_deporte':  validar_entero_positivo(body.get('id_deporte'), 'id_deporte'),
        'precio_hora': validar_entero_positivo(body.get('precio_hora'), 'precio_hora'),
        'techada':     validar_booleano(body.get('techada', False), 'techada'),
        'activa':      validar_booleano(body.get('activa', True), 'activa'),
    }


def validar_body_patch_cancha(body) -> dict:
    """Devuelve solo los campos presentes. id_deporte no es editable."""
    validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(body, CAMPOS_EDITABLES)

    validaciones = {
        'nombre':      lambda v: validar_string_no_vacio(v, 'nombre'),
        'precio_hora': lambda v: validar_entero_positivo(v, 'precio_hora'),
        'techada':     lambda v: validar_booleano(v, 'techada'),
        'activa':      lambda v: validar_booleano(v, 'activa'),
    }

    return {campo: validar(body[campo]) for campo, validar in validaciones.items() if campo in body}


def validar_filtros_listado(args) -> dict:
    rechazar_campos_desconocidos(args, FILTROS_LISTADO, 'conjunto de parametros')

    return {
        'id_deporte': validar_entero_positivo(args['id_deporte'], 'id_deporte') if 'id_deporte' in args else None,
        'nombre':     validar_string_no_vacio(args['nombre'], 'nombre') if 'nombre' in args else None,
        'techada':    validar_booleano(args['techada'], 'techada') if 'techada' in args else None,
        'activa':     validar_booleano(args['activa'], 'activa') if 'activa' in args else None,
    }


def _combinar(fecha: datetime, hora_texto: str, nombre: str) -> datetime:
    try:
        hora = datetime.strptime(hora_texto.strip(), FORMATO_HORA).time()
    except (AttributeError, ValueError):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{hora_texto}' no cumple el formato esperado HH:MM",
        )

    return datetime.combine(fecha.date(), hora, tzinfo=TZ_ARG)


def validar_filtros_disponibles(args) -> dict:
    """Valida fecha, hora_inicio y hora_fin con las mismas reglas que una reserva nueva."""
    rechazar_campos_desconocidos(args, FILTROS_DISPONIBLES, 'conjunto de parametros')

    for obligatorio in ('fecha', 'hora_inicio', 'hora_fin'):
        if obligatorio not in args:
            raise ErrorAPI(
                code=f'required.{obligatorio}',
                message=f"Parametro requerido: '{obligatorio}'",
                description=f"El parametro '{obligatorio}' es obligatorio",
            )

    fecha = parsear_fecha(args['fecha'], 'fecha')
    inicio = _combinar(fecha, args['hora_inicio'], 'hora_inicio')
    fin = _combinar(fecha, args['hora_fin'], 'hora_fin')

    validar_intervalo(inicio, fin)
    validar_inicio_futuro(inicio, 'hora_inicio')

    return {
        'inicio':     inicio,
        'fin':        fin,
        'id_deporte': validar_entero_positivo(args['id_deporte'], 'id_deporte') if 'id_deporte' in args else None,
        'techada':    validar_booleano(args['techada'], 'techada') if 'techada' in args else None,
    }

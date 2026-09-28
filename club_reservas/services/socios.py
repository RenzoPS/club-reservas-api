
import logging
from ..constants import (
    ERROR_CODE_EMAIL_DUPLICADO,
    ERROR_CODE_SOCIO_NOT_FOUND,
)
from ..paginacion import paginar
from ..utils import ErrorAPI
from ..repositories.socios import (
    buscar_por_email,
    obtener_por_id,
    listar_socios,
    guardar_socio,
    actualizar_socio
)

logger = logging.getLogger(__name__)

RUTA = '/socios'


def construir_socio_dto(socio):
    """
    DTO publico de un socio. MySQL devuelve los BOOLEAN como 0/1.
    """
    return {
        "id_socio": socio["id_socio"],
        "nombre":   socio["nombre"],
        "email":    socio["email"],
        "activo":   bool(socio["activo"]),
    }


def servicio_crear_socio(datos_limpios):
    """
    Coordina la creación de un socio aplicando reglas de negocio.
    """
    email = datos_limpios["email"]

    socio_existente = buscar_por_email(email)
    if socio_existente:
        logger.warning(f"Alta de socio con correo ya registrado: '{email}'")

        raise ErrorAPI(
            code=ERROR_CODE_EMAIL_DUPLICADO,
            message='El correo ya esta registrado',
            description=f"Ya existe un socio con el correo '{email}'",
            status=409,
        )


    datos_limpios["activo"] = True


    socio_guardado = guardar_socio(datos_limpios)
    return construir_socio_dto(socio_guardado)


def servicio_obtener_socio_por_id(socio_id):
    """
    Busca un socio por ID. Si no existe, lanza un error 404 logico.
    """
    socio = obtener_por_id(socio_id)
    if not socio:
        raise ErrorAPI(
            code=ERROR_CODE_SOCIO_NOT_FOUND,
            message='Socio no encontrado',
            description=f"No existe un socio con id '{socio_id}'",
            status=404,
        )
    return construir_socio_dto(socio)


def servicio_listar_socios(filtros, limit=10, offset=0):
    """
    coordina la peticion de listado con filtros y paginacion.
    """
    socios, total = listar_socios(**filtros, limit=limit, offset=offset)

    return paginar([construir_socio_dto(s) for s in socios], total, limit, offset,
                   'socios', RUTA, filtros)


def servicio_actualizar_socio(socio_id, datos_a_actualizar):
    """
    Modifica parcialmente un socio respetando las validaciones de alta y la unicidad del correo.
    """

    socio_actual = obtener_por_id(socio_id)
    if not socio_actual:
        raise ErrorAPI(
            code=ERROR_CODE_SOCIO_NOT_FOUND,
            message='Socio no encontrado',
            description=f"No existe un socio con id '{socio_id}'",
            status=404,
        )


    if "email" in datos_a_actualizar:
        nuevo_email = datos_a_actualizar["email"]
        socio_con_ese_email = buscar_por_email(nuevo_email)


        if socio_con_ese_email and socio_con_ese_email["id_socio"] != socio_id:
            raise ErrorAPI(
                code=ERROR_CODE_EMAIL_DUPLICADO,
                message='El correo ya esta registrado',
                description=f"El correo '{nuevo_email}' pertenece a otro socio",
                status=409,
            )


    socio_modificado = actualizar_socio(socio_id, datos_a_actualizar)
    return construir_socio_dto(socio_modificado)

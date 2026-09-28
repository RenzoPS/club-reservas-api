
from ..paginacion import PARAMETROS_PAGINACION
from ..utils import (
    rechazar_campos_desconocidos,
    validar_booleano,
    validar_cuerpo_no_vacio,
    validar_email,
    validar_entero_positivo,
    validar_string_no_vacio,
)

# El servidor asigna activo = true en el alta, asi que el cliente no lo envia.
CAMPOS_ALTA = {"nombre", "email"}
CAMPOS_EDITABLES = {"nombre", "email", "activo"}
FILTROS_LISTADO = {"nombre", "activo"} | PARAMETROS_PAGINACION


def validar_id_socio(socio_id):
    """Valida el id usado en /socios/{id}."""
    return validar_entero_positivo(socio_id, "id_socio")


def validar_body_post(datos_entrantes):
    """
    Valida y limpia los datos para el alta de un socio (POST).
    Amoldado al estilo de nombres del grupo.
    """
    validar_cuerpo_no_vacio(datos_entrantes)
    rechazar_campos_desconocidos(datos_entrantes, CAMPOS_ALTA)

    return {
        "nombre": validar_string_no_vacio(datos_entrantes.get("nombre"), "nombre"),
        "email": validar_email(datos_entrantes.get("email")),
    }


def validar_body_patch(datos_entrantes):
    """
    Valida y limpia los datos para la actualización parcial (PATCH).
    Amoldado al estilo exacto que viste en los ejemplos del grupo.
    """
    validar_cuerpo_no_vacio(datos_entrantes)
    rechazar_campos_desconocidos(datos_entrantes, CAMPOS_EDITABLES)

    datos_limpios = {}


    if "nombre" in datos_entrantes:
        datos_limpios["nombre"] = validar_string_no_vacio(datos_entrantes["nombre"], "nombre")

    if "email" in datos_entrantes:
        datos_limpios["email"] = validar_email(datos_entrantes["email"])



    if "activo" in datos_entrantes:
        datos_limpios["activo"] = validar_booleano(datos_entrantes["activo"], "activo")


    return datos_limpios


def validar_filtros_listado(args):
    """
    Valida los filtros de GET /socios. La paginación la valida paginacion.py.
    """
    rechazar_campos_desconocidos(args, FILTROS_LISTADO, "conjunto de parametros")

    return {
        "nombre": validar_string_no_vacio(args["nombre"], "nombre") if "nombre" in args else None,
        "activo": validar_booleano(args["activo"], "activo") if "activo" in args else None,
    }


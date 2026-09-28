
from club_reservas.repositories.socios import (
    buscar_por_email,
    buscar_por_id,
    listar_socios,
    guardar_socio,
    actualizar_socio
)

def servicio_crear_socio(datos_limpios):
    """
    Coordina la creación de un socio aplicando reglas de negocio.
    """
    email = datos_limpios["email"]
    
    socio_existente = buscar_por_email(email)
    if socio_existente:
        raise ValueError("EMAIL_DUPLICATED")
        
  
    datos_limpios["activo"] = True
    
   
    socio_guardado = guardar_socio(datos_limpios)
    return socio_guardado


def servicio_obtener_socio_por_id(socio_id):
    """
    Busca un socio por ID. Si no existe, lanza un error 404 logico.
    """
    socio = buscar_por_id(socio_id)
    if not socio:
        raise KeyError("SOCIO_NOT_FOUND")
    return socio


def servicio_listar_socios(nombre=None, activo=None, limit=10, offset=0):
    """
    coordina la peticion de listado con filtros y paginacion.
    """
   
    if activo == "true": activo = True
    if activo == "false": activo = False
    
    return listar_socios(nombre, activo, limit, offset)


def servicio_actualizar_socio(socio_id, datos_a_actualizar):
    """
    Modifica parcialmente un socio respetando las validaciones de alta y la unicidad del correo.
    """
   
    socio_actual = buscar_por_id(socio_id)
    if not socio_actual:
        raise KeyError("SOCIO_NOT_FOUND")
        
   
    if "email" in datos_a_actualizar:
        nuevo_email = datos_a_actualizar["email"]
        socio_con_ese_email = buscar_por_email(nuevo_email)
        
    
        if socio_con_ese_email and socio_con_ese_email["id"] != socio_id:
            raise ValueError("EMAIL_DUPLICATED")
            
   
    socio_modificado = actualizar_socio(socio_id, datos_a_actualizar)
    return socio_modificado



from sqlalchemy import text

from club_reservas.repositories import ejecutar_consulta, ejecutar_mutacion, listar_paginado



def buscar_por_email(email_a_buscar):
    """Busca un socio por su correo en MySQL para validar duplicados."""
    sql = "SELECT id_socio AS id, nombre, email, activo FROM club.socios WHERE email = :email_param"
    resultados = ejecutar_consulta(sql, {"email_param": email_a_buscar})
    
    if resultados:
        
        socio = resultados[0]
        socio["activo"] = bool(socio["activo"])
        return socio
    return None


def buscar_por_id(socio_id):
    """Busca un socio por su identificador único en MySQL."""
    sql = "SELECT id_socio AS id, nombre, email, activo FROM club.socios WHERE id_socio = :id_param"
    resultados = ejecutar_consulta(sql, {"id_param": socio_id})
    
    if resultados:
        socio = resultados[0]
        socio["activo"] = bool(socio["activo"])
        return socio
    return None


def listar_socios(nombre=None, activo=None, limit=10, offset=0):
    """
    Filtra y pagina la lista de socios.
    Devuelve únicamente la lista de filas encontradas.
    """
  
    filas, total = listar_paginado(
        tabla='club.socios',
        filtros={
            'LOWER(nombre) LIKE ?': f'%{nombre.lower()}%' if nombre else None,
            'activo = ?': activo
        },
        orden='id_socio',
        limit=limit,
        offset=offset
    )
    
    for socio in filas:
        socio["activo"] = bool(socio["activo"])
        
    return filas



def guardar_socio(nuevo_socio):
    """Inserta un socio en la base de datos y le asigna el ID generado."""
    sql = """
        INSERT INTO club.socios (nombre, email, activo) 
        VALUES (:nombre, :email, :activo)
    """
    parametros = {
        "nombre": nuevo_socio["nombre"],
        "email": nuevo_socio["email"],
        "activo": nuevo_socio["activo"]
    }
    
    
    nuevo_id = ejecutar_mutacion(sql, parametros)
    
    nuevo_socio["id"] = nuevo_id
    return nuevo_socio


def actualizar_socio(socio_id, datos_nuevos):
    """Actualiza parcialmente al socio modificando únicamente los campos enviados."""
    partes_sql = []
    parametros = {"id": socio_id}
    
    for llave, valor in datos_nuevos.items():
        partes_sql.append(f"{llave} = :{llave}_param")
        parametros[f"{llave}_param"] = valor
        
    if not partes_sql:
        return buscar_por_id(socio_id)
        
    sql = f"UPDATE club.socios SET {', '.join(partes_sql)} WHERE id_socio = :id"
    ejecutar_mutacion(sql, parametros)
    
    return buscar_por_id(socio_id)

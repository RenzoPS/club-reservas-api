

def validar_formato_mail(mail):
    """
    Verifica que el email tenga un formato básico válido.
    """
    if not mail or "@" not in mail or "." not in mail:
        return False
    return True


def validar_body_post(datos_entrantes):
    """
    Valida y limpia los datos para el alta de un socio (POST).
    Amoldado al estilo de nombres del grupo.
    """
    
    if "nombre" not in datos_entrantes or "mail" not in datos_entrantes:
        return None, "El nombre y el email son campos obligatorios."
        
    nombre = datos_entrantes["nombre"]
    mail = datos_entrantes["email"]
    
    
    if not nombre or not str(nombre).strip():
        return None, "El nombre no puede quedar vacío."
        
    
    if not validar_formato_mail(mail):
        return None, "El correo electrónico no tiene un formato válido."
        
    
    email_limpio = str(mail).strip().lower()
    nombre_limpio = str(nombre).strip()
    
    return {
        "nombre": nombre_limpio,
        "email": email_limpio
    }, None


def validar_body_patch(datos_entrantes):
    """
    Valida y limpia los datos para la actualización parcial (PATCH).
    Amoldado al estilo exacto que viste en los ejemplos del grupo.
    """
    datos_limpios = {}
    
   
    if "nombre" in datos_entrantes:
        nombre = datos_entrantes["nombre"]
        if not nombre or not str(nombre).strip():
            return None, "El nombre no puede quedar vacío."
        datos_limpios["nombre"] = str(nombre).strip()
        
    if "mail" in datos_entrantes:
        mail = datos_entrantes["email"]
        if not validar_formato_mail(mail):
            return None, "El correo electrónico no tiene un formato válido."
        datos_limpios["mail"] = str(mail).strip().lower()
        
    
       
    if "activo" in datos_entrantes:
        activo = datos_entrantes["activo"]
        if type(activo) != bool:
            return None, "El campo activo debe ser verdadero (true) o falso (false)."
        datos_limpios["activo"] = activo

        
    return datos_limpios, None


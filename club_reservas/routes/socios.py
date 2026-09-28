

from flask import Blueprint, request, jsonify


from club_reservas.validators.socios import (
    validar_body_post,
    validar_body_patch
)

from club_reservas.services.socios import (
    servicio_crear_socio,
    servicio_obtener_socio_por_id,
    servicio_listar_socios,
    servicio_actualizar_socio
)

socios_bp = Blueprint('socios_bp', __name__)


@socios_bp.route('/socios', methods=['GET'])
def listar_socios_endpoint():
    
    nombre = request.args.get('nombre', default=None, type=str)
    activo = request.args.get('activo', default=None, type=str)
    
    
    limit = request.args.get('Limit', default=10, type=int)
    offset = request.args.get('Offset', default=0, type=int)
    
    resultado = servicio_listar_socios(nombre, activo, limit, offset)
    return jsonify(resultado), 200


@socios_bp.route('/socios', methods=['POST'])
def crear_socio_endpoint():
    datos_recibidos = request.get_json() or {}
    
  
    datos_limpios, error_validacion = validar_body_post(datos_recibidos)
    if error_validacion:
        return jsonify({"error": error_validacion}), 400
        
   
    try:
        nuevo_socio = servicio_crear_socio(datos_limpios)
        return jsonify(nuevo_socio), 201
    except ValueError as e:
        if str(e) == "EMAIL_DUPLICATED":
            return jsonify({"error": "El correo electrónico ya se encuentra registrado."}), 409
        return jsonify({"error": "Ocurrió un error inesperado"}), 500


@socios_bp.route('/socios/<int:socio_id>', methods=['GET'])
def obtener_socio_endpoint(socio_id):
    try:
        socio = servicio_obtener_socio_por_id(socio_id)
        return jsonify(socio), 200
    except KeyError:
        return jsonify({"error": f"Socio con ID {socio_id} no encontrado."}), 404



@socios_bp.route('/socios/<int:socio_id>', methods=['PATCH'])
def actualizar_socio_endpoint(socio_id):
    datos_recibidos = request.get_json() or {}
    
    
    datos_limpios, error_validacion = validar_body_patch(datos_recibidos)
    if error_validacion:
        return jsonify({"error": error_validacion}), 400
        
  
    try:
        socio_actualizado = servicio_actualizar_socio(socio_id, datos_limpios)
        return jsonify(socio_actualizado), 200
    except KeyError:
        return jsonify({"error": f"Socio con ID {socio_id} no encontrado."}), 404
    except ValueError as e:
        if str(e) == "EMAIL_DUPLICATED":
            return jsonify({"error": "El correo electrónico ya se encuentra registrado en otro usuario."}), 409
        return jsonify({"error": "Ocurrió un error inesperado"}), 500
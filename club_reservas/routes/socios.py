

from flask import Blueprint, request, jsonify

from ..paginacion import leer_parametros_paginacion

from ..validators.socios import (
    validar_body_post,
    validar_body_patch,
    validar_filtros_listado,
    validar_id_socio
)

from ..services.socios import (
    servicio_crear_socio,
    servicio_obtener_socio_por_id,
    servicio_listar_socios,
    servicio_actualizar_socio
)

socios_bp = Blueprint('socios', __name__)


@socios_bp.route('/socios', methods=['GET'])
def listar_socios_endpoint():

    limit, offset = leer_parametros_paginacion(request.args)
    filtros = validar_filtros_listado(request.args)

    resultado = servicio_listar_socios(filtros, limit, offset)
    return jsonify(resultado), 200


@socios_bp.route('/socios', methods=['POST'])
def crear_socio_endpoint():
    datos_recibidos = request.get_json(silent=True)


    datos_limpios = validar_body_post(datos_recibidos)


    nuevo_socio = servicio_crear_socio(datos_limpios)
    return jsonify(nuevo_socio), 201


@socios_bp.route('/socios/<socio_id>', methods=['GET'])
def obtener_socio_endpoint(socio_id):
    id_valido = validar_id_socio(socio_id)

    return jsonify(servicio_obtener_socio_por_id(id_valido)), 200



@socios_bp.route('/socios/<socio_id>', methods=['PATCH'])
def actualizar_socio_endpoint(socio_id):
    id_valido = validar_id_socio(socio_id)
    datos_recibidos = request.get_json(silent=True)


    datos_limpios = validar_body_patch(datos_recibidos)


    return jsonify(servicio_actualizar_socio(id_valido, datos_limpios)), 200

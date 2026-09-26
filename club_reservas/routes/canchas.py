from flask import Blueprint, jsonify, request
from ..constants import ERROR_CODE_CANCHA_NOT_FOUND
from ..paginacion import leer_parametros_paginacion
from ..utils import ErrorAPI
from ..validators.canchas import (
    validar_body_nueva_cancha,
    validar_body_patch_cancha,
    validar_filtros_disponibles,
    validar_filtros_listado,
    validar_id_cancha,
)
from ..services.canchas import (
    actualizar_cancha,
    buscar_cancha_por_id,
    crear_cancha,
    eliminar_cancha,
    listar_canchas,
    listar_canchas_disponibles,
)

canchas_bp = Blueprint('canchas', __name__)


def cancha_no_encontrada(id_cancha: int) -> ErrorAPI:
    return ErrorAPI(
        code=ERROR_CODE_CANCHA_NOT_FOUND,
        message='Cancha no encontrada',
        description=f"No existe una cancha con id '{id_cancha}'",
        status=404,
    )


@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    limit, offset = leer_parametros_paginacion(request.args)
    filtros = validar_filtros_listado(request.args)

    return jsonify(listar_canchas(filtros, limit, offset))


# Se declara antes que /canchas/<id_cancha> para que 'disponibles' no se tome como id.
@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def get_canchas_disponibles():
    limit, offset = leer_parametros_paginacion(request.args)
    filtros = validar_filtros_disponibles(request.args)

    return jsonify(listar_canchas_disponibles(filtros, limit, offset))


@canchas_bp.route('/canchas', methods=['POST'])
def post_cancha():
    datos = validar_body_nueva_cancha(request.get_json(silent=True))

    return jsonify(crear_cancha(datos)), 201


@canchas_bp.route('/canchas/<id_cancha>', methods=['GET'])
def get_cancha(id_cancha):
    id_validado = validar_id_cancha(id_cancha)
    cancha = buscar_cancha_por_id(id_validado)

    if not cancha:
        raise cancha_no_encontrada(id_validado)

    return jsonify(cancha)


@canchas_bp.route('/canchas/<id_cancha>', methods=['PATCH'])
def patch_cancha(id_cancha):
    id_validado = validar_id_cancha(id_cancha)
    campos = validar_body_patch_cancha(request.get_json(silent=True))

    if not buscar_cancha_por_id(id_validado):
        raise cancha_no_encontrada(id_validado)

    return jsonify(actualizar_cancha(id_validado, campos))


@canchas_bp.route('/canchas/<id_cancha>', methods=['DELETE'])
def delete_cancha(id_cancha):
    id_validado = validar_id_cancha(id_cancha)

    if not buscar_cancha_por_id(id_validado):
        raise cancha_no_encontrada(id_validado)

    eliminar_cancha(id_validado)

    return '', 204

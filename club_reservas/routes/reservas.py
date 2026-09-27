# api/reservas_bp.py
from flask import Blueprint, jsonify, request

from ..constants import (
    ERROR_CODE_RESERVA_NOT_FOUND,
    ERROR_CODE_INVALID_BODY,
)
from ..paginacion import leer_parametros_paginacion
from ..services import reservas as reservas_service
from ..utils import ErrorAPI
from ..validators import reservas as reservas_val

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/reservas', methods=['GET'])
def listar_reservas():
    """GET /reservas: lista paginada con filtros opcionales."""
    try:
        limit, offset = leer_parametros_paginacion(request.args)
        filtros = reservas_val.validar_filtros_reservas(request.args)

        resultado = reservas_service.listar_reservas(filtros, limit, offset)

        # Si no hay resultados, devolver 204 No Content
        if not resultado or not resultado.get('reservas'):
            return "", 204

        return jsonify(resultado), 200
    except ErrorAPI as e:
        return jsonify(e.to_dict()), e.status


@reservas_bp.route('/reservas', methods=['POST'])
def crear_reserva():
    """POST /reservas: crea una reserva en estado confirmada."""
    try:
        datos_json = request.get_json(silent=True)
        if datos_json is None:
            raise ErrorAPI(
                code=ERROR_CODE_INVALID_BODY,
                message='El cuerpo de la solicitud es inválido',
                description='Se esperaba un JSON válido',
                status=400,
            )

        datos = reservas_val.validar_reserva_create(datos_json)

        reserva = reservas_service.crear_reserva(
            datos['id_socio'],
            datos['id_cancha'],
            datos['fecha_hora_inicio'],
            datos['fecha_hora_fin'],
        )

        return jsonify(reserva), 201
    except ErrorAPI as e:
        return jsonify(e.to_dict()), e.status


@reservas_bp.route('/reservas/<int:id_reserva>', methods=['GET'])
def obtener_reserva(id_reserva):
    """GET /reservas/{id}: todos los campos de una reserva."""
    try:
        id_valido = reservas_val.validar_id_reserva(id_reserva)
        reserva = reservas_service.buscar_reserva_por_id(id_valido)

        if not reserva:
            raise ErrorAPI(
                code=ERROR_CODE_RESERVA_NOT_FOUND,
                message='Reserva no encontrada',
                description=f"No existe una reserva con id '{id_valido}'",
                status=404,
            )

        return jsonify(reserva), 200
    except ErrorAPI as e:
        return jsonify(e.to_dict()), e.status


@reservas_bp.route('/reservas/<int:id_reserva>/estado', methods=['PUT'])
def cambiar_estado(id_reserva):
    """PUT /reservas/{id}/estado: cancela o finaliza una reserva."""
    try:
        id_valido = reservas_val.validar_id_reserva(id_reserva)
        
        datos_json = request.get_json(silent=True)
        if datos_json is None:
            raise ErrorAPI(
                code=ERROR_CODE_INVALID_BODY,
                message='El cuerpo de la solicitud es inválido',
                description='Se esperaba un JSON válido',
                status=400,
            )
        
        nuevo_estado = reservas_val.validar_estado_update(datos_json)

        reservas_service.cambiar_estado_reserva(id_valido, nuevo_estado)

        return "", 204  # Sin cuerpo, solo confirmación
    except ErrorAPI as e:
        return jsonify(e.to_dict()), e.status
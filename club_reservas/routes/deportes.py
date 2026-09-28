from flask import Blueprint, jsonify
from ..services.deportes import listar_deportes

deportes_bp = Blueprint('deportes', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    """Lista los deportes precargados. No lleva paginacion."""
    return jsonify({'deportes': listar_deportes()})

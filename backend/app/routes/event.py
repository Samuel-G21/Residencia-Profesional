from flask import Blueprint
from ..controllers.event_controller import (
    get_all_cursos, get_evento_fase, get_evento_trabajadores,
    update_evento_fase, delete_evento, cancelar_evento,
    baja_trabajador, upload_scpm07, finalizar_evento
)

event_bp = Blueprint('event', __name__)
event_bp.route('/cursos', methods=['GET'])(get_all_cursos)
event_bp.route('/evento/<id_evento>', methods=['GET'])(get_evento_fase)
event_bp.route('/evento/<id_evento>/trabajadores', methods=['GET'])(get_evento_trabajadores)
event_bp.route('/evento/<id_evento>/fase', methods=['PUT'])(update_evento_fase)
event_bp.route('/evento/<id_evento>', methods=['DELETE'])(delete_evento)
event_bp.route('/evento/<id_evento>/cancelar', methods=['PUT'])(cancelar_evento)
event_bp.route('/evento/<id_evento>/finalizar', methods=['PUT'])(finalizar_evento)
event_bp.route('/evento/<id_evento>/trabajador/<ficha>/baja', methods=['PUT'])(baja_trabajador)
event_bp.route('/evento/<id_evento>/scpm07', methods=['POST'])(upload_scpm07)

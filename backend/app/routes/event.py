from flask import Blueprint
from ..controllers.event_controller import (
    get_all_cursos, get_evento_fase, get_evento_trabajadores,
    update_evento_fase, delete_evento, cancelar_evento,
    baja_trabajador, upload_scpm07, finalizar_evento, no_apto_trabajador, agregar_trabajador, upload_scpm03
)

event_bp = Blueprint('event', __name__)
event_bp.route('/cursos', methods=['GET'])(get_all_cursos)
event_bp.route('/evento/<id_evento>', methods=['GET'])(get_evento_fase)
event_bp.route('/evento/<id_evento>/trabajadores', methods=['GET'])(get_evento_trabajadores)
event_bp.route('/evento/<id_evento>/trabajador', methods=['POST'])(agregar_trabajador)
event_bp.route('/evento/<id_evento>/fase', methods=['PUT'])(update_evento_fase)
event_bp.route('/evento/<id_evento>', methods=['DELETE'])(delete_evento)
event_bp.route('/evento/<id_evento>/cancelar', methods=['PUT'])(cancelar_evento)
event_bp.route('/evento/<id_evento>/finalizar', methods=['PUT'])(finalizar_evento)
event_bp.route('/evento/<id_evento>/trabajador/<ficha>/baja', methods=['PUT'])(baja_trabajador)
event_bp.route('/evento/<id_evento>/trabajador/<ficha>/no_apto', methods=['PUT'])(no_apto_trabajador)
event_bp.route('/evento/<id_evento>/scpm07', methods=['POST'])(upload_scpm07)
event_bp.route('/evento/<id_evento>/scpm03', methods=['POST'])(upload_scpm03)


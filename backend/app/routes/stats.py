from flask import Blueprint
from ..controllers.stats_controller import get_stats

stats_bp = Blueprint('stats', __name__)
stats_bp.route('/stats', methods=['GET'])(get_stats)

"""
Rutas para la consulta de indicadores clave (KPIs) y metricas del Dashboard Estadistico.
"""
from flask import Blueprint
from ..controllers.stats_controller import get_stats

stats_bp = Blueprint('stats', __name__)

# GET /api/stats -> Calcula y retorna metricas globales de cursos, calificaciones y demografia
stats_bp.route('/stats', methods=['GET'])(get_stats)

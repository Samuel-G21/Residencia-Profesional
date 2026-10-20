"""
Rutas para la administracion y actualizacion de catalogos institucionales (CURP y STPS).
"""
from flask import Blueprint
from ..controllers.catalog_controller import update_catalog

catalog_bp = Blueprint('catalog', __name__)

# POST /api/update-catalog -> Sobrescribe el catalogo CURP.xlsx (y sincroniza BD) o STPS.xlsx
catalog_bp.route('/update-catalog', methods=['POST'])(update_catalog)

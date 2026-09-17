from flask import Blueprint
from ..controllers.catalog_controller import update_catalog

catalog_bp = Blueprint('catalog', __name__)
catalog_bp.route('/update-catalog', methods=['POST'])(update_catalog)

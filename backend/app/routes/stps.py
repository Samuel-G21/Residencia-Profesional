from flask import Blueprint

stps_bp = Blueprint('stps', __name__)

from ..controllers import stps_controller

"""
Definicion del Blueprint para exportacion de formatos STPS y SCPM-07.
Los endpoints asociados se decoran directamente en `app/controllers/stps_controller.py`.
"""
from flask import Blueprint

stps_bp = Blueprint('stps', __name__)

from ..controllers import stps_controller

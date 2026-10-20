"""
Pruebas unitarias basicas de la aplicacion Backend con Pytest.

Guia para practicantes:
Para ejecutar las pruebas localmente o en el pipeline CI/CD:
  `cd backend && pytest tests/`
"""
import pytest
import sys
import os

# Agrega el directorio raiz del backend al path para permitir importar el paquete `app`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app


@pytest.fixture
def app():
    """Crea una instancia de la aplicacion configurada en modo TESTING."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture
def client(app):
    """Proporciona un cliente HTTP simulado de Flask para realizar peticiones de prueba."""
    return app.test_client()


def test_health_check(client):
    """Verifica que el endpoint raiz ('/') responda con codigo 200 y el estado esperado."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['message'] == 'Sistema PEMEX Activo'

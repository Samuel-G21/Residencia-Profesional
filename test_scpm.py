import sys
import os

# Add backend to path so we can import from app
sys.path.append(os.path.abspath('backend'))

from app import create_app
from app.models import db
from app.models.course import Curso
from app.models.history import HistorialCapacitacion

app = create_app()

with app.app_context():
    # Setup test data
    curso = Curso(id_evento='TEST1234', nombre_evento='Test Event', fase_actual=4, tipo_curso='Ascenso')
    db.session.add(curso)
    
    t1 = HistorialCapacitacion(id_evento='TEST1234', ficha_trabajador='111', nombre_trabajador='Test Worker 1', estado='ACTIVO', calificacion=90)
    t2 = HistorialCapacitacion(id_evento='TEST1234', ficha_trabajador='222', nombre_trabajador='Test Worker 2', estado='BAJA', calificacion=0)
    t3 = HistorialCapacitacion(id_evento='TEST1234', ficha_trabajador='333', nombre_trabajador='Test Worker 3', estado='ACTIVO', calificacion=85)
    
    db.session.add_all([t1, t2, t3])
    db.session.commit()
    print("Test data created.")
    
    with app.test_client() as client:
        res = client.post('/evento/TEST1234/scpm07/export')
        print(f"SCPM-07 Export Status: {res.status_code}")
        if res.status_code == 200:
            with open('test_scpm07_output.xlsx', 'wb') as f:
                f.write(res.data)
            print("Successfully saved test_scpm07_output.xlsx")
        else:
            print("Failed to export:", res.data)
            
    # Cleanup
    db.session.delete(curso)
    db.session.delete(t1)
    db.session.delete(t2)
    db.session.delete(t3)
    db.session.commit()
    print("Test data cleaned up.")

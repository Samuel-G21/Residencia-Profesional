from app import create_app
from app.models import db
from sqlalchemy import text
app = create_app()
ctx = app.app_context()
ctx.push()
res = db.session.execute(text("SELECT SUM(CASE WHEN SUBSTRING(c.curp, 11, 1) = 'H' THEN 1 ELSE 0 END) as hombres, SUM(CASE WHEN SUBSTRING(c.curp, 11, 1) = 'M' THEN 1 ELSE 0 END) as mujeres FROM historial_capacitacion h JOIN curps c ON h.ficha_trabajador = c.ficha")).first()
print('Hombres:', res.hombres, 'Mujeres:', res.mujeres)

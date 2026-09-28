import sys
import os
import pandas as pd

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.curp import Curp

app = create_app()

def safe_str(val):
    if pd.isna(val) or val == '': return ""
    try:
        f_val = float(val)
        if f_val.is_integer(): return str(int(f_val))
        return str(val).strip()
    except:
        return str(val).strip()

with app.app_context():
    filepath = os.path.join('catalogos', 'CURP.xlsx')
    if os.path.exists(filepath):
        try:
            df = pd.read_excel(filepath)
            df.columns = df.columns.str.upper().str.strip()
            if 'FICHA' in df.columns and 'CURP' in df.columns:
                print("Limpiando curps actuales...")
                db.session.query(Curp).delete()
                
                print("Insertando nuevas curps...")
                count = 0
                for _, row in df.iterrows():
                    ficha_val = safe_str(row['FICHA'])
                    curp_val = str(row['CURP']).upper().strip()
                    if ficha_val and curp_val and curp_val != "NAN":
                        nuevo = Curp(ficha=ficha_val, curp=curp_val)
                        db.session.merge(nuevo)
                        count += 1
                
                db.session.commit()
                print(f"Éxito: {count} CURPs insertadas.")
            else:
                print("El archivo CURP.xlsx no tiene columnas FICHA y CURP.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No se encontró catalogos/CURP.xlsx")

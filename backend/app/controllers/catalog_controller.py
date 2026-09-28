from flask import request, jsonify
import os
import pandas as pd
from ..models import db
from ..models.curp import Curp

def safe_str(val):
    if pd.isna(val) or val == '': return ""
    try:
        f_val = float(val)
        if f_val.is_integer(): return str(int(f_val))
        return str(val).strip()
    except:
        return str(val).strip()

def update_catalog():
    if 'file' not in request.files or 'tipo' not in request.form:
        return jsonify({"status": "error", "message": "Falta archivo o tipo"}), 400
    
    file = request.files['file']
    tipo = str(request.form['tipo']).strip().lower()
    
    os.makedirs('catalogos', exist_ok=True)
    
    if tipo == 'curp':
        filename = 'CURP.xlsx'
        filepath = os.path.join('catalogos', filename)
        file.save(filepath)
        
        try:
            df = pd.read_excel(filepath)
            df.columns = df.columns.str.upper().str.strip()
            
            if 'FICHA' in df.columns and 'CURP' in df.columns:
                # Clear existing curps
                db.session.query(Curp).delete()
                
                # Insert new curps
                for _, row in df.iterrows():
                    ficha_val = safe_str(row['FICHA'])
                    curp_val = str(row['CURP']).upper().strip()
                    if ficha_val and curp_val and curp_val != "NAN":
                        nuevo = Curp(ficha=ficha_val, curp=curp_val)
                        db.session.merge(nuevo)
                
                db.session.commit()
                return jsonify({"status": "success", "message": "Catálogo Maestro de CURP actualizado en sistema y base de datos"}), 200
            else:
                return jsonify({"status": "error", "message": "El archivo CURP debe contener las columnas FICHA y CURP"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"Error procesando CURP: {str(e)}"}), 500
            
    elif tipo == 'stps':
        filename = 'STPS.xlsx'
        filepath = os.path.join('catalogos', filename)
        file.save(filepath)
        return jsonify({"status": "success", "message": "Catálogos STPS actualizados"}), 200
    else:
        return jsonify({"status": "error", "message": "Tipo de catálogo no soportado"}), 400

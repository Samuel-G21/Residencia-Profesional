"""
Controlador de Administracion de Catalogos Institucionales (`catalog_controller.py`).

Guia para practicantes:
Permite actualizar desde la interfaz web los archivos base ubicados en `backend/catalogos/`:
1. `tipo == 'curp'`: Guarda `CURP.xlsx` en disco y sincroniza su contenido con la tabla `curps`
   en MySQL (requiere las columnas `FICHA` y `CURP`).
2. `tipo == 'stps'`: Actualiza el archivo `STPS.xlsx` en la carpeta `catalogos/`.
Incluye funciones auxiliares de carga rapida con `openpyxl` en modo `read_only` para poblar
automaticamente el padron de CURPs en MySQL cuando se encuentra vacio.
"""
from flask import request, jsonify
from ..utils.security import error_response
import os
import math
import openpyxl
from sqlalchemy import text
from ..models import db
from ..models.curp import Curp


def safe_str(val):
    """
    Normaliza valores leidos desde Excel (ej. convierte `12345.0` a `'12345'` y `NaN` a `''`).
    Evita que Pandas/OpenPyXL agregue decimales `.0` a numeros de ficha enteros.
    """
    if val is None or (isinstance(val, float) and math.isnan(val)) or val == '':
        return ""
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return str(val).strip()
    s_val = str(val).strip()
    if s_val.endswith('.0') and s_val[:-2].isdigit():
        return s_val[:-2]
    return s_val


def load_curp_catalog(filepath=None):
    """
    Lee `catalogos/CURP.xlsx` de forma rapida usando `openpyxl` en modo `read_only`
    y devuelve un diccionario `{ficha: {'curp': curp, 'nombre': nombre}}`.
    """
    if filepath is None:
        filepath = os.path.join('catalogos', 'CURP.xlsx')
    if not os.path.exists(filepath):
        alt_path = os.path.join(os.path.dirname(__file__), '..', '..', 'catalogos', 'CURP.xlsx')
        if os.path.exists(alt_path):
            filepath = os.path.abspath(alt_path)
        else:
            return {}

    catalogo = {}
    wb = None
    try:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb['curp'] if 'curp' in wb.sheetnames else wb.worksheets[0]
        rows_iter = ws.iter_rows(values_only=True)

        ficha_idx, curp_idx, nombre_idx = 0, 1, 2
        header_found = False
        for _ in range(5):
            row = next(rows_iter, None)
            if row is None:
                break
            upper_row = [str(c).strip().upper() if c is not None else '' for c in row]
            if 'FICHA' in upper_row and 'CURP' in upper_row:
                ficha_idx = upper_row.index('FICHA')
                curp_idx = upper_row.index('CURP')
                nombre_idx = upper_row.index('NOMBRE') if 'NOMBRE' in upper_row else -1
                header_found = True
                break

        if not header_found:
            return {}

        for row in rows_iter:
            if not row or len(row) <= max(ficha_idx, curp_idx):
                continue
            ficha_val = safe_str(row[ficha_idx])
            curp_raw = row[curp_idx]
            if not ficha_val or curp_raw is None:
                continue
            curp_val = str(curp_raw).strip().upper()
            if not curp_val or curp_val == 'NAN':
                continue
            nombre_val = ""
            if 0 <= nombre_idx < len(row) and row[nombre_idx] is not None:
                nombre_val = str(row[nombre_idx]).strip().title()
            catalogo[ficha_val] = {
                "curp": curp_val[:18],
                "nombre": nombre_val
            }
    except Exception as e:
        print("Error leyendo catalogo CURP.xlsx:", e)
    finally:
        if wb is not None:
            try:
                wb.close()
            except Exception:
                pass
    return catalogo


def sync_curps_to_db(filepath=None, force_replace=False):
    """
    Sincroniza el archivo `catalogos/CURP.xlsx` hacia la tabla `curps` en la base de datos.
    - Si `force_replace=False`, solo pobla la tabla cuando tiene menos de 100 registros.
    - Realiza inserciones por lotes para poblar los ~8,600 registros en menos de 2 segundos.
    """
    try:
        if not force_replace:
            count = db.session.execute(text("SELECT COUNT(*) FROM curps")).scalar() or 0
            if count >= 100:
                return count

        catalogo = load_curp_catalog(filepath)
        if not catalogo:
            return 0

        if force_replace:
            db.session.query(Curp).delete()
            db.session.flush()

        items = [(ficha, data["curp"]) for ficha, data in catalogo.items() if ficha and data.get("curp")]
        dialect = db.engine.dialect.name if db.engine else ""

        batch_size = 1000
        if dialect == "mysql":
            for i in range(0, len(items), batch_size):
                chunk = items[i:i + batch_size]
                placeholders = ", ".join([f"(:f{j}, :c{j})" for j in range(len(chunk))])
                params = {}
                for j, (f_val, c_val) in enumerate(chunk):
                    params[f"f{j}"] = f_val
                    params[f"c{j}"] = c_val
                sql = text(
                    f"INSERT INTO curps (ficha, curp) VALUES {placeholders} "
                    f"ON DUPLICATE KEY UPDATE curp = VALUES(curp)"
                )
                db.session.execute(sql, params)
        else:
            for ficha_val, curp_val in items:
                db.session.merge(Curp(ficha=ficha_val, curp=curp_val))

        db.session.commit()
        return len(items)
    except Exception as e:
        db.session.rollback()
        print("Error sincronizando tabla curps:", e)
        return 0


def update_catalog():
    """
    Endpoint `POST /api/update-catalog`.
    Recibe `file` (archivo Excel) y `tipo` ('curp' o 'stps') mediante `multipart/form-data`.
    """
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
            catalogo = load_curp_catalog(filepath)
            if catalogo:
                total = sync_curps_to_db(filepath, force_replace=True)
                return jsonify({
                    "status": "success",
                    "message": f"Catálogo Maestro de CURP actualizado en sistema y base de datos ({total} registros)"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "El archivo CURP debe contener las columnas FICHA y CURP"
                }), 400
        except Exception as e:
            db.session.rollback()
            return error_response("Error procesando CURP: ", 500, e)

    elif tipo == 'stps':
        filename = 'STPS.xlsx'
        filepath = os.path.join('catalogos', filename)
        file.save(filepath)
        return jsonify({"status": "success", "message": "Catálogos STPS actualizados"}), 200
    else:
        return jsonify({"status": "error", "message": "Tipo de catálogo no soportado"}), 400

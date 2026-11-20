"""
Controlador de Estadisticas e Indicadores Clave para el Dashboard (`stats_controller.py`).

Guia para practicantes:
Consulta las tablas `cursos`, `historial_capacitacion` y `curps` para construir todas las
metricas que alimentan la vista `Dashboard.tsx`:
- Reinicio anual automatico: Por defecto filtra todos los indicadores y graficas por el año
  en curso (`datetime.now().year`), de modo que cada año nuevo el Dashboard inicia en cero
  sin perder los registros historicos de años anteriores (que pueden consultarse con `?anio=YYYY`).
- Totales de cursos (activos, finalizados, cancelados) y trabajadores (totales, unicos, bajas).
- Promedio general de calificaciones, conteo de aprobados (>= 8) y reprobados (< 8).
- Recomendacion automatica (`plan_accion`) segun el porcentaje de reprobacion.
- Estadistica demografica por genero (Hombres vs Mujeres) extraida del caracter 11 de la CURP
  (con sincronizacion automatica desde `catalogos/CURP.xlsx` y respaldo por nombre).
"""
from datetime import datetime
from flask import jsonify, request
from ..utils.security import error_response
from ..models import db
from sqlalchemy import text
from .catalog_controller import sync_curps_to_db, load_curp_catalog, safe_str

# Conjuntos de nombres de pila comunes para respaldo cuando un trabajador nuevo aun no tiene CURP registrada
_NOMBRES_MUJER = {
    "MARIA", "MA", "MA.", "GUADALUPE", "JUANA", "MARGARITA", "VERONICA", "ELIZABETH",
    "ALEJANDRA", "LETICIA", "GABRIELA", "PATRICIA", "ROSA", "TERESA", "ADRIANA",
    "SILVIA", "LAURA", "GRISELDA", "SANDRA", "CLAUDIA", "MARTHA", "ANA", "LUISA",
    "CARMEN", "BLANCA", "YOLANDA", "IRMA", "BEATRIZ", "NORMA", "MONICA", "JESSICA",
    "YESSICA", "PAULINA", "MAYRA", "JHOANA", "JOHANA", "YADIRA", "MARIEL", "ERIKA",
    "FLOR", "ESPERANZA", "IVETTE", "KARLA", "DIANA", "FERNANDA", "DANIELA", "PAOLA",
    "BRENDA", "WENDY", "LILIANA", "ROCIO", "SONIA", "ALICIA", "ELENA", "CECILIA",
    "MIRIAM", "NANCY", "OLGA", "LORENA", "VANESSA", "KARINA", "SOFIA", "VALERIA",
    "ANDREA", "NATALIA", "LUCIA", "ISABEL", "CONCEPCION", "LOURDES", "SUSANA",
    "ARACELI", "MARISOL", "ESTHER", "SARA", "RAQUEL", "EVA", "NOEMI", "RUTH",
    "FABIOLA", "CITLALLI", "XIMITL", "NAYELI", "ITSLI", "ITZEL", "MARIANA", "BERENICE"
}

_NOMBRES_HOMBRE = {
    "JOSE", "JUAN", "LUIS", "CARLOS", "JESUS", "ANTONIO", "MIGUEL", "ANGEL",
    "FRANCISCO", "PEDRO", "ALEJANDRO", "MANUEL", "ROBERTO", "FERNANDO", "DANIEL",
    "JORGE", "RICARDO", "EDUARDO", "JAVIER", "RAUL", "ARTURO", "SERGIO", "MARIO",
    "GERARDO", "ARMANDO", "ALBERTO", "ENRIQUE", "VICTOR", "HECTOR", "MARTIN",
    "RAFAEL", "MARCO", "OSCAR", "GUILLERMO", "SALVADOR", "GABRIEL", "RUBEN",
    "DAVID", "ALFONSO", "ANDRES", "IGNACIO", "GUSTAVO", "CESAR", "OMAR", "IVAN",
    "EDGAR", "ADRIAN", "ADOLFO", "RENE", "ISRAEL", "RAYMUNDO", "FIDEL", "JAIME",
    "SANTIAGO", "JULIAN", "HUGO", "PABLO", "ERNESTO", "HUMBERTO", "FELIPE", "DIEGO",
    "EMILIO", "JOEL", "SAMUEL", "NOE", "MOISES", "AARON", "ABRAHAM", "ISAAC",
    "CRISTIAN", "CHRISTIAN", "JONATHAN", "ERICK", "ERIC", "ALAN", "ALEXIS", "URIEL"
}


def _clasificar_genero(curp_str, nombre_completo=""):
    """
    Determina el genero ('H' o 'M') de un participante:
    1. Usa el caracter 11 de la CURP oficial (indice 10 en base 0).
    2. Si el trabajador no tiene CURP en el catalogo, infiere a partir del nombre de pila.
    """
    if curp_str:
        c_clean = str(curp_str).strip().upper()
        if len(c_clean) >= 11:
            g = c_clean[10]
            if g in ('H', 'M'):
                return g
            if g == 'X':
                return 'H'

    if nombre_completo:
        tokens = [t.strip(".,").upper() for t in str(nombre_completo).split() if t.strip(".,")]
        # En el sistema el formato es 'APELLIDO_PAT APELLIDO_MAT NOMBRE(S)'
        given_tokens = tokens[2:] if len(tokens) >= 3 else tokens
        for tok in given_tokens:
            if tok in _NOMBRES_MUJER and tok not in ("GUADALUPE",):
                return 'M'
            if tok in _NOMBRES_HOMBRE:
                return 'H'
        for tok in given_tokens:
            if tok in _NOMBRES_MUJER:
                return 'M'
        if given_tokens:
            first_given = given_tokens[0]
            if first_given.endswith('A'):
                return 'M'
            return 'H'
    return None


def get_stats():
    """
    Endpoint `GET /api/stats?anio=YYYY`.
    Retorna un objeto JSON con los KPIs y series para graficas correspondientes al año solicitado
    (por defecto el año en curso, reiniciandose automaticamente cada nuevo año).
    """
    try:
        # Garantiza que el padron de CURPs este cargado en la base de datos para la grafica de genero
        sync_curps_to_db(force_replace=False)

        anio_actual = datetime.now().year
        anio_param = request.args.get('anio', type=int)
        anio = anio_param if anio_param else anio_actual

        # Lista de años disponibles en el historial (incluyendo siempre el año actual)
        anios_rows = db.session.execute(text(
            "SELECT DISTINCT YEAR(fecha_registro) as anio "
            "FROM cursos WHERE fecha_registro IS NOT NULL ORDER BY anio DESC"
        ))
        anios_set = { int(r.anio) for r in anios_rows if r.anio is not None }
        anios_set.add(anio_actual)
        anios_set.add(anio)
        anios_disponibles = sorted(anios_set, reverse=True)

        filtro_anio_curso = "COALESCE(YEAR(fecha_registro), :anio) = :anio"
        filtro_anio_alias_c = "COALESCE(YEAR(c.fecha_registro), :anio) = :anio"
        filtro_anio_alias_cur = "COALESCE(YEAR(cur.fecha_registro), :anio) = :anio"
        params = {"anio": anio}

        # 1. Total de cursos registrados en el año
        tot_c = db.session.execute(
            text(f"SELECT COUNT(*) FROM cursos WHERE {filtro_anio_curso}"),
            params
        ).scalar() or 0

        # 2. Total de registros de participacion (capacitaciones impartidas) en el año
        tot_t = db.session.execute(text(
            f"SELECT COUNT(h.id) FROM historial_capacitacion h "
            f"JOIN cursos c ON h.id_evento = c.id_evento "
            f"WHERE {filtro_anio_alias_c}"
        ), params).scalar() or 0

        # 3. Trabajadores unicos capacitados en el año (sin duplicar fichas entre varios cursos)
        tot_unicos = db.session.execute(text(
            f"SELECT COUNT(DISTINCT h.ficha_trabajador) FROM historial_capacitacion h "
            f"JOIN cursos c ON h.id_evento = c.id_evento "
            f"WHERE {filtro_anio_alias_c}"
        ), params).scalar() or 0

        # 4. Top 5 cursos con mayor cantidad de participantes en el año
        top_rows = db.session.execute(text(
            f"SELECT c.nombre_evento, COUNT(h.id) as total_capacitados "
            f"FROM cursos c LEFT JOIN historial_capacitacion h ON c.id_evento = h.id_evento "
            f"WHERE {filtro_anio_alias_c} "
            f"GROUP BY c.id_evento, c.nombre_evento ORDER BY total_capacitados DESC LIMIT 5"
        ), params)
        top = [{"nombre_evento": r.nombre_evento, "total_capacitados": int(r.total_capacitados or 0)} for r in top_rows]

        # 5. Distribucion de cursos del año segun su fase actual (Fases 1 a 5)
        fases_rows = db.session.execute(text(
            f"SELECT fase_actual, COUNT(*) as cantidad FROM cursos "
            f"WHERE {filtro_anio_curso} GROUP BY fase_actual ORDER BY fase_actual ASC"
        ), params)
        fases_data = [{"fase_actual": r.fase_actual, "cantidad": int(r.cantidad or 0)} for r in fases_rows]

        # 6. Ultimos 5 cursos registrados en el año
        recent_rows = db.session.execute(text(
            f"SELECT nombre_evento, id_evento, fecha_registro, fase_actual "
            f"FROM cursos WHERE {filtro_anio_curso} ORDER BY fecha_registro DESC LIMIT 5"
        ), params)
        recientes = [
            {"nombre_evento": r.nombre_evento, "id_evento": r.id_evento, "fase_actual": r.fase_actual}
            for r in recent_rows
        ]

        # 7. Cursos cancelados y 8. Cursos finalizados en el año
        cancelados = db.session.execute(
            text(f"SELECT COUNT(*) FROM cursos WHERE estado = 'CANCELADO' AND {filtro_anio_curso}"),
            params
        ).scalar() or 0
        finalizados = db.session.execute(
            text(f"SELECT COUNT(*) FROM cursos WHERE estado = 'FINALIZADO' AND {filtro_anio_curso}"),
            params
        ).scalar() or 0

        # 9. Trabajadores dados de baja en el año
        bajas = db.session.execute(text(
            f"SELECT COUNT(h.id) FROM historial_capacitacion h "
            f"JOIN cursos c ON h.id_evento = c.id_evento "
            f"WHERE h.estado = 'BAJA' AND {filtro_anio_alias_c}"
        ), params).scalar() or 0

        # 10. Promedio general de calificaciones registradas en el año
        promedio = db.session.execute(text(
            f"SELECT AVG(h.calificacion) FROM historial_capacitacion h "
            f"JOIN cursos c ON h.id_evento = c.id_evento "
            f"WHERE h.calificacion IS NOT NULL AND {filtro_anio_alias_c}"
        ), params).scalar()
        promedio = float(promedio) if promedio else 0

        # 11. Conteo de reprobados (< 8) y aprobados (>= 8) en el año
        reprobados = db.session.execute(text(
            f"SELECT COUNT(h.id) FROM historial_capacitacion h "
            f"JOIN cursos c ON h.id_evento = c.id_evento "
            f"WHERE h.calificacion < 8 AND {filtro_anio_alias_c}"
        ), params).scalar() or 0
        aprobados = db.session.execute(text(
            f"SELECT COUNT(h.id) FROM historial_capacitacion h "
            f"JOIN cursos c ON h.id_evento = c.id_evento "
            f"WHERE h.calificacion >= 8 AND {filtro_anio_alias_c}"
        ), params).scalar() or 0

        # 12. Promedio de calificacion desglosado por curso en el año
        promedios_cursos_rows = db.session.execute(text(
            f"SELECT c.nombre_evento, AVG(h.calificacion) as promedio_curso "
            f"FROM cursos c JOIN historial_capacitacion h ON c.id_evento = h.id_evento "
            f"WHERE h.calificacion IS NOT NULL AND {filtro_anio_alias_c} "
            f"GROUP BY c.id_evento, c.nombre_evento"
        ), params)
        promedios_cursos = [
            {"nombre_evento": r.nombre_evento, "promedio_curso": float(r.promedio_curso) if r.promedio_curso else 0}
            for r in promedios_cursos_rows
        ]

        # Regla de negocio: Plan de accion automatico segun el indice de reprobacion del año
        reprobados_porcentaje = (reprobados / tot_t) * 100 if tot_t > 0 else 0
        if reprobados_porcentaje > 20:
            plan_accion = f"ALERTA: Alto índice de reprobación ({reprobados_porcentaje:.1f}%). Se sugiere revisar la metodología del instructor."
        elif reprobados_porcentaje > 10:
            plan_accion = f"PRECAUCIÓN: Índice de reprobación moderado ({reprobados_porcentaje:.1f}%)."
        elif reprobados > 0:
            plan_accion = f"NORMAL: Índice de reprobación bajo ({reprobados_porcentaje:.1f}%)."
        else:
            plan_accion = "EXCELENTE: Ningún trabajador reprobado."

        # 13 y 14. Hombres y Mujeres totales y desglosados por curso en el año
        participantes_rows = db.session.execute(text(f"""
            SELECT
                cur.id_evento,
                cur.nombre_evento,
                h.ficha_trabajador,
                h.nombre_trabajador,
                c.curp
            FROM cursos cur
            JOIN historial_capacitacion h ON cur.id_evento = h.id_evento
            LEFT JOIN curps c ON TRIM(h.ficha_trabajador) = TRIM(c.ficha)
            WHERE {filtro_anio_alias_cur}
            ORDER BY cur.fecha_registro DESC, cur.id_evento ASC
        """), params).fetchall()

        # Si algun participante no tuvo cruce en la tabla SQL `curps`, consultamos el catalogo en disco como respaldo
        catalogo_disco = None
        hombres = 0
        mujeres = 0
        cursos_genero_map = {}
        cursos_orden = []

        for r in participantes_rows:
            id_ev = r.id_evento
            if id_ev not in cursos_genero_map:
                cursos_genero_map[id_ev] = {
                    "id_evento": id_ev,
                    "nombre_evento": r.nombre_evento,
                    "hombres": 0,
                    "mujeres": 0
                }
                cursos_orden.append(id_ev)

            curp_val = r.curp
            if not curp_val:
                if catalogo_disco is None:
                    catalogo_disco = load_curp_catalog()
                ficha_limpia = safe_str(r.ficha_trabajador)
                if ficha_limpia in catalogo_disco:
                    curp_val = catalogo_disco[ficha_limpia].get("curp", "")

            genero = _clasificar_genero(curp_val, r.nombre_trabajador)
            if genero == 'H':
                hombres += 1
                cursos_genero_map[id_ev]["hombres"] += 1
            elif genero == 'M':
                mujeres += 1
                cursos_genero_map[id_ev]["mujeres"] += 1

        genero_por_curso = [cursos_genero_map[id_ev] for id_ev in cursos_orden]

        return jsonify({
            "status": "success",
            "data": {
                "anio": anio,
                "anio_actual": anio_actual,
                "anios_disponibles": anios_disponibles,
                "total_cursos": tot_c,
                "total_trabajadores": tot_t,
                "trabajadores_unicos": tot_unicos,
                "top_cursos": top,
                "cursos_por_fase": fases_data,
                "cursos_recientes": recientes,
                "cursos_cancelados": cancelados,
                "cursos_finalizados": finalizados,
                "trabajadores_baja": bajas,
                "promedio_general": promedio,
                "reprobados": reprobados,
                "aprobados": aprobados,
                "promedios_cursos": promedios_cursos,
                "plan_accion": plan_accion,
                "hombres": hombres,
                "mujeres": mujeres,
                "genero_por_curso": genero_por_curso
            }
        }), 200
    except Exception as e:
        return error_response("Ocurrió un error interno", 500, e)

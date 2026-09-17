from flask import jsonify
from ..models import db
from sqlalchemy import text

def get_stats():
    try:
        # 1. Total courses
        tot_c = db.session.execute(text("SELECT COUNT(*) FROM cursos")).scalar() or 0
        
        # 2. Total workers trained
        tot_t = db.session.execute(text("SELECT COUNT(*) FROM historial_capacitacion")).scalar() or 0
        
        # 3. Unique workers trained
        tot_unicos = db.session.execute(text("SELECT COUNT(DISTINCT ficha_trabajador) FROM historial_capacitacion")).scalar() or 0
        
        # 4. Top 5 courses by participation
        top_rows = db.session.execute(text("SELECT c.nombre_evento, COUNT(h.id) as total_capacitados FROM cursos c LEFT JOIN historial_capacitacion h ON c.id_evento = h.id_evento GROUP BY c.id_evento, c.nombre_evento ORDER BY total_capacitados DESC LIMIT 5"))
        top = [{"nombre_evento": r.nombre_evento, "total_capacitados": r.total_capacitados} for r in top_rows]
        
        # 5. Courses per phase
        fases_rows = db.session.execute(text("SELECT fase_actual, COUNT(*) as cantidad FROM cursos GROUP BY fase_actual ORDER BY fase_actual ASC"))
        fases_data = [{"fase_actual": r.fase_actual, "cantidad": r.cantidad} for r in fases_rows]
        
        # 6. Recent courses
        recent_rows = db.session.execute(text("SELECT nombre_evento, id_evento, fecha_registro, fase_actual FROM cursos ORDER BY fecha_registro DESC LIMIT 5"))
        recientes = [{"nombre_evento": r.nombre_evento, "id_evento": r.id_evento, "fase_actual": r.fase_actual} for r in recent_rows]
        
        # 7. Canceled courses
        cancelados = db.session.execute(text("SELECT COUNT(*) FROM cursos WHERE estado = 'CANCELADO'")).scalar() or 0
        
        # 8. Finalizados
        finalizados = db.session.execute(text("SELECT COUNT(*) FROM cursos WHERE estado = 'FINALIZADO'")).scalar() or 0
        
        # 9. Bajas
        bajas = db.session.execute(text("SELECT COUNT(*) FROM historial_capacitacion WHERE estado = 'BAJA'")).scalar() or 0
        
        # 10. Promedio general
        promedio = db.session.execute(text("SELECT AVG(calificacion) FROM historial_capacitacion WHERE calificacion IS NOT NULL")).scalar()
        promedio = float(promedio) if promedio else 0
        
        # 11. Reprobados
        reprobados = db.session.execute(text("SELECT COUNT(*) FROM historial_capacitacion WHERE calificacion < 8")).scalar() or 0
        
        # Aprobados
        aprobados = db.session.execute(text("SELECT COUNT(*) FROM historial_capacitacion WHERE calificacion >= 8")).scalar() or 0
        
        # 12. Promedios cursos
        promedios_cursos_rows = db.session.execute(text("SELECT c.nombre_evento, AVG(h.calificacion) as promedio_curso FROM cursos c JOIN historial_capacitacion h ON c.id_evento = h.id_evento WHERE h.calificacion IS NOT NULL GROUP BY c.id_evento, c.nombre_evento"))
        promedios_cursos = [{"nombre_evento": r.nombre_evento, "promedio_curso": float(r.promedio_curso) if r.promedio_curso else 0} for r in promedios_cursos_rows]
        
        # Plan de accion
        reprobados_porcentaje = (reprobados / tot_t) * 100 if tot_t > 0 else 0
        if reprobados_porcentaje > 20:
            plan_accion = f"ALERTA: Alto índice de reprobación ({reprobados_porcentaje:.1f}%). Se sugiere revisar la metodología del instructor."
        elif reprobados_porcentaje > 10:
            plan_accion = f"PRECAUCIÓN: Índice de reprobación moderado ({reprobados_porcentaje:.1f}%)."
        elif reprobados > 0:
            plan_accion = f"NORMAL: Índice de reprobación bajo ({reprobados_porcentaje:.1f}%)."
        else:
            plan_accion = "EXCELENTE: Ningún trabajador reprobado."

        return jsonify({
            "status": "success", 
            "data": {
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
                "plan_accion": plan_accion
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

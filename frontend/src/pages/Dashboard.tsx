/**
 * Vista del Dashboard Estadistico de Capacitacion (`Dashboard.tsx`).
 *
 * Guia para practicantes:
 * Consulta `GET /api/stats?anio=YYYY` (por defecto el año en curso, reiniciandose cada año) y renderiza:
 * 1. Tarjetas de indicadores clave (KPIs): Eventos registrados, finalizados, cancelados,
 *    capacitaciones totales, bajas, promedio general, aprobados y reprobados del año.
 * 2. Alerta automatica de Plan de Accion segun el indice de reprobacion anual.
 * 3. Graficas interactivas con `recharts` (Top 5 eventos, distribucion por fase, estado de
 *    cursos, estado de trabajadores, promedio por curso y distribucion de genero por curso).
 * 4. Exportacion de metricas a archivo `.csv` (`handleExportDashboard`) y captura visual de
 *    las graficas a imagen `.png` mediante `html2canvas` (`handleExportDashboardImage`).
 */
import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import html2canvas from 'html2canvas';
import Swal from 'sweetalert2';
import api from '../services/api';

const Dashboard: React.FC = () => {
  const currentCalendarYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState<number>(currentCalendarYear);

  const [stats, setStats] = useState<any>({
    anio: currentCalendarYear,
    anio_actual: currentCalendarYear,
    anios_disponibles: [currentCalendarYear],
    total_cursos: 0,
    total_trabajadores: 0,
    trabajadores_unicos: 0,
    top_cursos: [],
    cursos_por_fase: [],
    cursos_recientes: [],
    promedios_cursos: [],
    hombres: 0,
    mujeres: 0,
    genero_por_curso: []
  });

  const [loadingMessage, setLoadingMessage] = useState('');

  // Obtiene las estadisticas del año seleccionado desde el backend (por defecto el año en curso)
  const fetchStats = useCallback(async (anioToFetch: number = selectedYear) => {
    try {
      const response = await api.get('/stats', { params: { anio: anioToFetch } });
      if (response.data.status === 'success') {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    }
  }, [selectedYear]);

  useEffect(() => {
    fetchStats(selectedYear);
  }, [selectedYear, fetchStats]);

  // Genera y descarga un archivo CSV con el resumen anual de KPIs, Top 5 eventos, fases y genero por curso
  const handleExportDashboard = () => {
    const csvContent = [
      ['KPI', 'Valor'],
      ['Año del Ejercicio', selectedYear],
      ['Eventos Registrados', stats.total_cursos],
      ['Total Capacitaciones', stats.total_trabajadores],
      ['Trabajadores de Baja', stats.trabajadores_baja ?? 0],
      ['Eventos Cancelados', stats.cursos_cancelados ?? 0],
      ['Eventos Finalizados', stats.cursos_finalizados ?? 0],
      ['Promedio General', stats.promedio_general ?? 0],
      ['Trabajadores Reprobados', stats.reprobados ?? 0],
      ['Trabajadores Aprobados', stats.aprobados ?? 0],
      ['Total Hombres', stats.hombres ?? 0],
      ['Total Mujeres', stats.mujeres ?? 0],
      [],
      ['Top 5 Eventos', 'Participantes'],
      ...(stats.top_cursos || []).map((c: any) => [`"${c.nombre_evento}"`, c.total_capacitados]),
      [],
      ['Fase', 'Eventos'],
      ...(stats.cursos_por_fase || []).map((f: any) => [`Fase ${f.fase_actual}`, f.cantidad]),
      [],
      ['Evento (Distribución por Género)', 'Hombres', 'Mujeres'],
      ...(stats.genero_por_curso || []).map((g: any) => [`"${g.nombre_evento}"`, g.hombres, g.mujeres])
    ].map(e => e.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `dashboard_stats_${selectedYear}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Captura el contenedor DOM `#dashboard-charts` y lo descarga como imagen PNG
  const handleExportDashboardImage = async () => {
    const dashboardEl = document.getElementById('dashboard-charts');
    if (!dashboardEl) return;
    setLoadingMessage('Generando imagen del dashboard...');
    try {
      const canvas = await html2canvas(dashboardEl, { scale: 2 });
      const image = canvas.toDataURL("image/png", 1.0);
      const link = document.createElement('a');
      link.href = image;
      link.download = `dashboard_graficas_${selectedYear}.png`;
      link.click();
    } catch (err) {
      Swal.fire('Error', 'Error al exportar gráficas', 'error');
    } finally {
      setLoadingMessage('');
    }
  };

  const availableYears: number[] = Array.isArray(stats.anios_disponibles) && stats.anios_disponibles.length > 0
    ? stats.anios_disponibles
    : [currentCalendarYear];

  return (
    <section className="card full-width-card fade-in">
      {loadingMessage && (
        <div className="loading-overlay" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(255,255,255,0.8)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
          <div className="spinner" style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #1a3b2b', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite' }}></div>
          <div className="loading-text" style={{ marginTop: '1rem', fontWeight: 'bold' }}>{loadingMessage}</div>
        </div>
      )}

      <div className="dashboard-header" style={{ flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ marginBottom: '0.25rem' }}>Dashboard Estadístico de Capacitación ({selectedYear})</h2>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748B' }}>
            Ejercicio anual {selectedYear} — Las estadísticas se reinician automáticamente cada nuevo año.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <label htmlFor="dashboard-year-select" style={{ fontWeight: 600, fontSize: '0.9rem', color: '#1a3b2b' }}>
            Año:
          </label>
          <select
            id="dashboard-year-select"
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            style={{
              padding: '0.45rem 0.75rem',
              borderRadius: '4px',
              border: '1px solid #1a3b2b',
              fontWeight: 'bold',
              color: '#1a3b2b',
              backgroundColor: '#fff',
              cursor: 'pointer'
            }}
          >
            {availableYears.map((yr) => (
              <option key={yr} value={yr}>
                {yr === currentCalendarYear ? `${yr} (Año actual)` : yr}
              </option>
            ))}
          </select>
          <button onClick={handleExportDashboardImage} className="btn-secondary" style={{ width: 'auto', marginBottom: 0, padding: '0.5rem 1rem' }}> Exportar Gráficas (Imagen)</button>
          <button onClick={handleExportDashboard} className="btn-secondary" style={{ width: 'auto', marginBottom: 0, padding: '0.5rem 1rem' }}> Exportar CSV</button>
          <button onClick={() => fetchStats(selectedYear)} className="btn-refresh"> Actualizar</button>
        </div>
      </div>

      <div className="kpi-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem', marginTop: '1.5rem' }}>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos ({selectedYear})</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats.total_cursos}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Finalizados</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745', margin: '5px 0 0 0' }}>{stats.cursos_finalizados ?? 0}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #b38e5d' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Capacitaciones</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#b38e5d', margin: '5px 0 0 0' }}>{stats.total_trabajadores}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #dc3545' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Trab. de Baja</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#dc3545', margin: '5px 0 0 0' }}>{stats.trabajadores_baja ?? 0}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #ffc107' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Cancelados</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107', margin: '5px 0 0 0' }}>{stats.cursos_cancelados ?? 0}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #17a2b8' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Promedio Gral</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#17a2b8', margin: '5px 0 0 0' }}>{(stats.promedio_general ?? 0).toFixed(1)}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Aprobados</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745', margin: '5px 0 0 0' }}>{stats.aprobados ?? 0}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #6f42c1' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Reprobados</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#6f42c1', margin: '5px 0 0 0' }}>{stats.reprobados ?? 0}</p>
        </div>
      </div>

      {stats.plan_accion && (
        <div style={{ backgroundColor: stats.plan_accion.startsWith('ALERTA') ? '#f8d7da' : stats.plan_accion.startsWith('PRECAUCIÓN') ? '#fff3cd' : '#d4edda', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', border: '1px solid #ccc' }}>
          <h3 style={{ marginTop: 0, color: '#333' }}> Plan de Acción Recomendado (Índice de Reprobación)</h3>
          <p style={{ margin: 0, color: '#444', fontWeight: 'bold' }}>{stats.plan_accion}</p>
        </div>
      )}

      <div id="dashboard-charts" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', backgroundColor: '#fff', padding: '1rem' }}>

        {/* Gráfica 1: Top 5 Eventos (BarChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '2px solid #b38e5d', paddingBottom: '0.5rem', marginTop: 0 }}>Top 5 Eventos (Participantes)</h3>
          {stats.top_cursos && stats.top_cursos.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={stats.top_cursos} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre_evento" tick={{ fontSize: 10 }} tickFormatter={(val: string) => val.substring(0, 10) + '...'} />
                <YAxis allowDecimals={false} />
                <RechartsTooltip />
                <Bar dataKey="total_capacitados" fill="#1a3b2b" name="Participantes" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay participantes registrados en {selectedYear}.</p>
          )}
        </div>

        {/* Gráfica 2: Distribución por Fase (PieChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '2px solid #6c757d', paddingBottom: '0.5rem', marginTop: 0 }}>Distribución por Fase</h3>
          {stats.cursos_por_fase && stats.cursos_por_fase.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={stats.cursos_por_fase} dataKey="cantidad" nameKey="fase_actual" cx="50%" cy="50%" outerRadius={80} label={(entry) => `Fase ${entry.fase_actual}`}>
                  {stats.cursos_por_fase.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={['#1a3b2b', '#b38e5d', '#dc3545', '#ffc107', '#17a2b8'][index % 5]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(value, name) => [value, `Fase ${name}`]} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay datos de fases disponibles en {selectedYear}.</p>
          )}
        </div>

        {/* Gráfica 2.1: Estado de Cursos (PieChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '2px solid #ffc107', paddingBottom: '0.5rem', marginTop: 0 }}>Estado de Cursos</h3>
          {stats.total_cursos > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Activos', value: stats.total_cursos - (stats.cursos_cancelados || 0) - (stats.cursos_finalizados || 0) },
                    { name: 'Cancelados', value: stats.cursos_cancelados || 0 },
                    { name: 'Finalizados', value: stats.cursos_finalizados || 0 }
                  ]}
                  dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(entry) => entry.name}
                >
                  <Cell fill="#1a3b2b" />
                  <Cell fill="#dc3545" />
                  <Cell fill="#17a2b8" />
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay cursos registrados en {selectedYear}.</p>
          )}
        </div>

        {/* Gráfica 2.2: Estado de Trabajadores (PieChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '2px solid #dc3545', paddingBottom: '0.5rem', marginTop: '0' }}>Estado de Trabajadores</h3>
          {stats.total_trabajadores > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Activos', value: stats.total_trabajadores - (stats.trabajadores_baja || 0) },
                    { name: 'Bajas', value: stats.trabajadores_baja || 0 }
                  ]}
                  dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(entry) => entry.name}
                >
                  <Cell fill="#1a3b2b" />
                  <Cell fill="#dc3545" />
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay trabajadores registrados en {selectedYear}.</p>
          )}
        </div>

        {/* Gráfica 3: Promedio de Calificación por Curso (BarChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gridColumn: '1 / -1' }}>
          <h3 style={{ borderBottom: '2px solid #17a2b8', paddingBottom: '0.5rem', marginTop: 0 }}>Promedio de Calificación por Curso</h3>
          {stats.promedios_cursos && stats.promedios_cursos.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.promedios_cursos} margin={{ top: 10, right: 10, left: -20, bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="nombre_evento"
                  tick={{ fontSize: 10 }}
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  height={60}
                  tickFormatter={(val: string) => (val && val.length > 22 ? val.substring(0, 22) + '...' : val)}
                />
                <YAxis domain={[0, 10]} />
                <RechartsTooltip />
                <Bar dataKey="promedio_curso" fill="#17a2b8" name="Promedio" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay calificaciones registradas en {selectedYear}.</p>
          )}
        </div>

        {/* Gráfica 4: Hombres y Mujeres por Curso (BarChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gridColumn: '1 / -1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #6f42c1', paddingBottom: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h3 style={{ margin: 0 }}>Distribución por Género de Participantes por Curso</h3>
            <span style={{ fontSize: '0.9rem', fontWeight: 'bold', color: '#444' }}>
              Total ({selectedYear}): <span style={{ color: '#1a3b2b' }}>Hombres: {stats.hombres ?? 0}</span> | <span style={{ color: '#b38e5d' }}>Mujeres: {stats.mujeres ?? 0}</span>
            </span>
          </div>
          {stats.genero_por_curso && stats.genero_por_curso.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={stats.genero_por_curso} margin={{ top: 10, right: 10, left: -20, bottom: 55 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="nombre_evento"
                  tick={{ fontSize: 10 }}
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  height={65}
                  tickFormatter={(val: string) => (val && val.length > 22 ? val.substring(0, 22) + '...' : val)}
                />
                <YAxis allowDecimals={false} />
                <RechartsTooltip />
                <Legend verticalAlign="top" height={36} />
                <Bar dataKey="hombres" fill="#1a3b2b" name="Hombres" />
                <Bar dataKey="mujeres" fill="#b38e5d" name="Mujeres" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay datos de género registrados en {selectedYear}.</p>
          )}
        </div>
      </div>
    </section>
  );
};

export default Dashboard;

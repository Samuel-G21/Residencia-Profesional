import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import html2canvas from 'html2canvas';
import Swal from 'sweetalert2';
import api from '../services/api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>({
    total_cursos: 0,
    total_trabajadores: 0,
    trabajadores_unicos: 0,
    top_cursos: [],
    cursos_por_fase: [],
    cursos_recientes: []
  });

  const [loadingMessage, setLoadingMessage] = useState('');

  const fetchStats = async () => {
    try {
      const response = await api.get('/stats');
      if (response.data.status === 'success') {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleExportDashboard = () => {
    const csvContent = [
      ['KPI', 'Valor'],
      ['Eventos Registrados', stats.total_cursos],
      ['Total Capacitaciones', stats.total_trabajadores],
      ['Trabajadores de Baja', stats.trabajadores_baja],
      ['Eventos Cancelados', stats.cursos_cancelados],
      ['Eventos Finalizados', stats.cursos_finalizados ?? 0],
      ['Promedio General', stats.promedio_general],
      ['Trabajadores Reprobados', stats.reprobados],
      ['Trabajadores Aprobados', stats.aprobados],
      [],
      ['Top 5 Eventos', 'Participantes'],
      ...(stats.top_cursos || []).map((c: any) => [c.nombre_evento, c.total_capacitados]),
      [],
      ['Fase', 'Eventos'],
      ...(stats.cursos_por_fase || []).map((f: any) => [`Fase ${f.fase_actual}`, f.cantidad])
    ].map(e => e.join(",")).join("\n");
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'dashboard_stats.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportDashboardImage = async () => {
    const dashboardEl = document.getElementById('dashboard-charts');
    if (!dashboardEl) return;
    setLoadingMessage('Generando imagen del dashboard...');
    try {
      const canvas = await html2canvas(dashboardEl, { scale: 2 });
      const image = canvas.toDataURL("image/png", 1.0);
      const link = document.createElement('a');
      link.href = image;
      link.download = 'dashboard_graficas.png';
      link.click();
    } catch(err) {
      Swal.fire('Error', 'Error al exportar gráficas', 'error');
    } finally {
      setLoadingMessage('');
    }
  };

  return (
    <section className="card full-width-card fade-in">
      {loadingMessage && (
        <div className="loading-overlay" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(255,255,255,0.8)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
          <div className="spinner" style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #1a3b2b', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite' }}></div>
          <div className="loading-text" style={{ marginTop: '1rem', fontWeight: 'bold' }}>{loadingMessage}</div>
        </div>
      )}

      <div className="dashboard-header">
        <h2>Dashboard Estadístico de Capacitación</h2>
        <div>
          <button onClick={handleExportDashboardImage} className="btn-secondary" style={{ marginRight: '10px' }}>🖼️ Exportar Gráficas (Imagen)</button>
          <button onClick={handleExportDashboard} className="btn-secondary" style={{ marginRight: '10px' }}>📥 Exportar CSV</button>
          <button onClick={fetchStats} className="btn-refresh"> Actualizar</button>
        </div>
      </div>
      
      <div className="kpi-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos</h3>
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
                <XAxis dataKey="nombre_evento" tick={{fontSize: 10}} tickFormatter={(val: string) => val.substring(0, 10) + '...'} />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="total_capacitados" fill="#1a3b2b" name="Participantes" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay participantes registrados aún.</p>
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
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay datos de fases disponibles.</p>
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
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay cursos registrados aún.</p>
          )}
        </div>

        {/* Gráfica 2.2: Estado de Trabajadores (PieChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '2px solid #dc3545', paddingBottom: '0.5rem', marginTop: 0 }}>Estado de Trabajadores</h3>
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
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay trabajadores registrados aún.</p>
          )}
        </div>

        {/* Gráfica 3: Promedio de Calificación por Curso (BarChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gridColumn: '1 / -1' }}>
          <h3 style={{ borderBottom: '2px solid #17a2b8', paddingBottom: '0.5rem', marginTop: 0 }}>Promedio de Calificación por Curso</h3>
          {stats.promedios_cursos && stats.promedios_cursos.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.promedios_cursos} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre_evento" tick={{fontSize: 10}} angle={-45} textAnchor="end" />
                <YAxis domain={[0, 10]} />
                <RechartsTooltip />
                <Bar dataKey="promedio_curso" fill="#17a2b8" name="Promedio" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay calificaciones registradas aún.</p>
          )}
        </div>

        {/* Gráfica 4: Hombres y Mujeres por Curso (BarChart) */}
        <div className="dashboard-widget" style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gridColumn: '1 / -1' }}>
          <h3 style={{ borderBottom: '2px solid #6f42c1', paddingBottom: '0.5rem', marginTop: 0 }}>Distribución por Género en Cursos</h3>
          {stats.genero_por_curso && stats.genero_por_curso.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.genero_por_curso} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre_evento" tick={{fontSize: 10}} angle={-45} textAnchor="end" />
                <YAxis />
                <RechartsTooltip />
                <Legend verticalAlign="top" height={36}/>
                <Bar dataKey="hombres" fill="#1a3b2b" name="Hombres" />
                <Bar dataKey="mujeres" fill="#b38e5d" name="Mujeres" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No hay datos de género registrados aún.</p>
          )}
        </div>
      </div>
    </section>
  );
};

export default Dashboard;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import html2canvas from 'html2canvas';
import './App.css';

function App() {
  // --- Estados de Navegación ---
  const [activeView, setActiveView] = useState('generador');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // --- Estados de Fases Inteligente (NUEVO) ---
  const [currentPhase, setCurrentPhase] = useState(1);
  const [isSearching, setIsSearching] = useState(false);
  const fases = [
    "Registro / Programación",
    "Ejecución del Evento",
    "Extracción SCPM-01",
    "Integración de Expediente",
    "Cierre / Firmas"
  ];

  // --- Estados del Flujo Principal ---
  const [file, setFile] = useState(null);
  const [eventId, setEventId] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);

  // --- Estados de Selección de Documentos (NUEVO) ---
  const todasLasPlantillas = [
    '1. Cédula registro actualizado 2025 COMBIANADA.docx',
    '2. Constancias de Habilidades DC-3 2026 COMBINADA.docx',
    'SCPM-04 COMBINADA.docx',
    'SCPM-04.docx',
    'SCPM-06 COMBINADA.docx',
    '5. Carta Compromiso Instructor 2026 COMBINADA.docx',
    'FVC.docx',
    'Informe Técnico Instructor 2025.docx',
    'SCPM-05 2025.docx',
    'SCPM-07.xlsx'
  ];
  const [selectedDocs, setSelectedDocs] = useState(todasLasPlantillas);


  const handleDocSelection = (doc) => {
    setSelectedDocs(prev => 
      prev.includes(doc) ? prev.filter(d => d !== doc) : [...prev, doc]
    );
  };

  // --- Estados del Dashboard Estadístico ---
  const [stats, setStats] = useState({
    total_cursos: 0,
    total_trabajadores: 0,
    trabajadores_unicos: 0,
    top_cursos: [],
    cursos_por_fase: [],
    cursos_recientes: []
  });

  // --- Estados de Extracción PDF ---
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfStatus, setPdfStatus] = useState({ type: '', message: '' });
  const [isPdfLoading, setIsPdfLoading] = useState(false);

  // --- Estados de Catálogos ---
  const [catalogType, setCatalogType] = useState('');
  const [catalogFile, setCatalogFile] = useState(null);
  const [catalogStatus, setCatalogStatus] = useState({ type: '', message: '' });
  const [isCatalogLoading, setIsCatalogLoading] = useState(false);

  // --- Estados de Historial ---
  const [historialCursos, setHistorialCursos] = useState([]);
  
  // --- Mensaje Global de Carga ---
  const [loadingMessage, setLoadingMessage] = useState('');

  // Cargar estadísticas
  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/stats');
      if (response.data.status === 'success') {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    }
  };

  useEffect(() => {
    if (activeView === 'dashboard') {
      fetchStats();
    } else if (activeView === 'historial') {
      fetchHistorial();
    }
  }, [activeView]);

  const fetchHistorial = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/cursos');
      if (response.data.status === 'success') {
        setHistorialCursos(response.data.data);
      }
    } catch (error) {
      console.error('Error al cargar historial:', error);
    }
  };

  // --- Estados de Detalles de Evento ---
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [eventWorkers, setEventWorkers] = useState([]);
  const [scpmFile, setScpmFile] = useState(null);

  const handleVerDetalles = async (id_evento) => {
    setSelectedEventId(id_evento);
    fetchTrabajadoresEvento(id_evento);
    changeView('detalle_evento');
  };

  const fetchTrabajadoresEvento = async (id_evento) => {
    try {
      const res = await axios.get(`http://localhost:5000/api/evento/${id_evento}/trabajadores`);
      if (res.data.status === 'success') {
        setEventWorkers(res.data.data);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleCancelarEvento = async () => {
    if(!window.confirm('¿Seguro que deseas cancelar este evento?')) return;
    try {
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/cancelar`);
      if(res.data.status === 'success') {
        alert('Evento cancelado');
        fetchHistorial();
        changeView('historial');
      }
    } catch(err) {
      alert('Error cancelando evento');
    }
  };

  const handleBajaTrabajador = async (ficha) => {
    if(!window.confirm(`¿Dar de baja al trabajador con ficha ${ficha}?`)) return;
    try {
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/trabajador/${ficha}/baja`);
      if(res.data.status === 'success') {
        alert('Trabajador dado de baja');
        fetchTrabajadoresEvento(selectedEventId);
      }
    } catch(err) {
      alert('Error dando de baja al trabajador');
    }
  };

  const handleSubirSCPM07 = async (e) => {
    e.preventDefault();
    if(!scpmFile) return;
    const formData = new FormData();
    formData.append('file', scpmFile);
    setLoadingMessage('Subiendo calificaciones...');
    try {
      const res = await axios.post(`http://localhost:5000/api/evento/${selectedEventId}/scpm07`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if(res.data.status === 'success') {
        alert('Calificaciones actualizadas');
        fetchTrabajadoresEvento(selectedEventId);
      }
    } catch(err) {
      alert('Error subiendo calificaciones');
    } finally {
      setLoadingMessage('');
      setScpmFile(null);
    }
  };

  const handleDeleteEvent = async (id_evento) => {
    if (!window.confirm(`¿Estás seguro de eliminar el evento ${id_evento}? Esto borrará su historial y documentos generados.`)) {
      return;
    }
    setLoadingMessage('Eliminando evento...');
    try {
      const res = await axios.delete(`http://localhost:5000/api/evento/${id_evento}`);
      if (res.data.status === 'success') {
        fetchHistorial();
        alert('Evento eliminado correctamente.');
      }
    } catch (error) {
      alert('Error al eliminar el evento.');
    } finally {
      setLoadingMessage('');
    }
  };

  // --- NUEVO: Buscador de Fases en Base de Datos ---
  const handleSearchEvent = async (e) => {
    e.preventDefault();
    if (!eventId) {
      setStatus({ type: 'error', message: 'Escribe el ID del evento para buscar su fase actual.' });
      return;
    }

    setIsSearching(true);
    setStatus({ type: 'info', message: 'Consultando base de datos...' });

    try {
      const response = await axios.get(`http://localhost:5000/api/evento/${eventId}`);

      if (response.data.status === 'success') {
        setCurrentPhase(response.data.data.fase_actual);
        setStatus({
          type: 'success',
          message: `Proyecto encontrado: ${response.data.data.nombre_evento}`
        });
      } else if (response.data.status === 'not_found') {
        setCurrentPhase(1);
        setStatus({
          type: 'info',
          message: 'Proyecto nuevo detectado. Iniciando en Fase 1 (Registro / Programación).'
        });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Error de conexión al buscar el evento.' });
    } finally {
      setIsSearching(false);
    }
  };

  const handleUpdatePhase = async (newPhase) => {
    if (!eventId) {
      setStatus({ type: 'error', message: 'Escribe el ID del evento primero.' });
      return;
    }
    setStatus({ type: 'info', message: 'Actualizando fase...' });
    try {
      const res = await axios.put(`http://localhost:5000/api/evento/${eventId}/fase`, { fase: newPhase });
      if (res.data.status === 'success') {
        setCurrentPhase(newPhase);
        setStatus({ type: 'success', message: `Fase actualizada a ${newPhase} (${fases[newPhase - 1]})` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Error al actualizar fase.' });
    }
  };

  // --- Manejadores del Flujo Principal ---
  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!file || !eventId) {
      setStatus({ type: 'error', message: 'Selecciona el Excel extraído y escribe la Clave del Evento.' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_evento', eventId);
    formData.append('docs_seleccionados', selectedDocs.join(','));

    setIsLoading(true);
    setLoadingMessage('Generando formatos de Word en el servidor...');
    setStatus({ type: 'info', message: 'Procesando Word...' });

    try {
      const response = await axios.post('http://localhost:5000/api/generate-docs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus({ type: 'success', message: response.data.message });
      setCurrentPhase(4);
    } catch (error) {
      setStatus({ type: 'error', message: error.response?.data?.message || 'Error con el servidor.' });
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const downloadZip = async (id_evento_descarga) => {
    setLoadingMessage('Convirtiendo a PDF y empaquetando en ZIP. Esto puede tardar...');
    try {
      const response = await axios.get(`http://localhost:5000/api/download-docs/${id_evento_descarga}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Expediente_${id_evento_descarga}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setStatus({ type: 'success', message: '¡Descarga del expediente completada con éxito!' });
    } catch (error) {
      setStatus({ type: 'error', message: 'Error al descargar. Verifica que ya estén generados.' });
      alert('Error al descargar el archivo. Es posible que aún no se haya generado.');
    } finally {
      setLoadingMessage('');
    }
  };

  const handleDownload = async () => {
    if (!eventId) {
      setStatus({ type: 'error', message: 'Escribe el ID del evento para descargar el expediente.' });
      return;
    }
    await downloadZip(eventId);
  };

  // --- Manejador PDF ---
  const handlePdfExtract = async (e) => {
    e.preventDefault();
    if (!pdfFile) {
      setPdfStatus({ type: 'error', message: 'Selecciona un archivo PDF SCPM-01.' });
      return;
    }
    const formData = new FormData();
    formData.append('file', pdfFile);
    setIsPdfLoading(true);
    setLoadingMessage('Analizando PDF y extrayendo trabajadores...');
    
    try {
      const response = await axios.post('http://localhost:5000/api/extract-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Guia_Asistencia_Generada.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      const workersCount = response.headers['x-workers-count'] || 'varios';
      setPdfStatus({ type: 'success', message: `¡Extracción exitosa! Se procesaron ${workersCount} trabajadores. Excel descargado.` });
      setTimeout(() => setPdfStatus({ type: '', message: '' }), 6000);
    } catch (error) {
      setPdfStatus({ type: 'error', message: 'Error al procesar el PDF.' });
    } finally {
      setIsPdfLoading(false);
      setLoadingMessage('');
    }
  };

  // --- Manejador de Catálogos ---
  const handleCatalogUpdate = async (e) => {
    e.preventDefault();
    if (!catalogType || !catalogFile) {
      setCatalogStatus({ type: 'error', message: 'Selecciona el tipo de catálogo y sube el archivo Excel.' });
      return;
    }
    const formData = new FormData();
    formData.append('file', catalogFile);
    formData.append('tipo', catalogType);
    setIsCatalogLoading(true);
    setCatalogStatus({ type: 'info', message: 'Sobrescribiendo catálogo en el servidor...' });

    try {
      const response = await axios.post('http://localhost:5000/api/update-catalog', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCatalogStatus({ type: 'success', message: response.data.message });
      setTimeout(() => {
        setCatalogFile(null);
        setCatalogType('');
        setCatalogStatus({ type: '', message: '' });
      }, 4000);
    } catch (error) {
      setCatalogStatus({ type: 'error', message: error.response?.data?.message || 'Error al actualizar el catálogo.' });
    } finally {
      setIsCatalogLoading(false);
    }
  };

  const handleExportDashboard = () => {
    const csvContent = [
      ['KPI', 'Valor'],
      ['Eventos Registrados', stats.total_cursos],
      ['Total Capacitaciones', stats.total_trabajadores],
      ['Trabajadores de Baja', stats.trabajadores_baja],
      ['Eventos Cancelados', stats.cursos_cancelados],
      ['Promedio General', stats.promedio_general],
      ['Trabajadores Reprobados', stats.reprobados],
      [],
      ['Top 5 Eventos', 'Participantes'],
      ...(stats.top_cursos || []).map(c => [c.nombre_evento, c.total_capacitados]),
      [],
      ['Fase', 'Eventos'],
      ...(stats.cursos_por_fase || []).map(f => [`Fase ${f.fase_actual}`, f.cantidad])
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
      alert("Error al exportar gráficas");
    } finally {
      setLoadingMessage('');
    }
  };

  const changeView = (view) => {
    setActiveView(view);
    setIsMenuOpen(false);
  };

  return (
    <div className="app-container">
      {/* OVERLAY DE CARGA (NUEVO) */}
      {loadingMessage && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <div className="loading-text">{loadingMessage}</div>
        </div>
      )}

      {/* --- Cabecera Institucional --- */}
      <header className="app-header">
        <div className="header-logos">
          <img src="/logo_gob.jpg" alt="Gobierno de México" className="logo-gobierno" />
          <img src="/logo_pemex.png" alt="PEMEX" className="logo-pemex" />
        </div>
        <div className="header-content-wrapper">
          <div className="header-title">
            <h1>Sistema de Automatización</h1>
            <p>Desarrollo Humano | Refinería Tula</p>
          </div>

          <div className="header-actions dropdown-container">
            <button className="btn-menu" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              ☰ Menú de Herramientas
            </button>
            {isMenuOpen && (
              <div className="dropdown-menu">
                <button className={activeView === 'generador' ? 'active' : ''} onClick={() => changeView('generador')}>📄 Gestión de Expedientes</button>
                <button className={activeView === 'historial' ? 'active' : ''} onClick={() => changeView('historial')}>📚 Historial de Eventos</button>
                <button className={activeView === 'dashboard' ? 'active' : ''} onClick={() => changeView('dashboard')}>📊 Dashboard Estadístico</button>
                <button className={activeView === 'catalogos' ? 'active' : ''} onClick={() => changeView('catalogos')}>📁 Actualizar Catálogos</button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* --- Contenedor Principal Dinámico --- */}
      <main className="main-content">

        {/* VISTA: HISTORIAL DE EVENTOS (NUEVA) */}
        {activeView === 'historial' && (
          <section className="card full-width-card fade-in">
            <div className="dashboard-header">
              <h2>Historial de Eventos y Proyectos</h2>
              <button onClick={fetchHistorial} className="btn-refresh">🔄 Actualizar</button>
            </div>
            
            <div style={{ overflowX: 'auto', marginTop: '1.5rem' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ backgroundColor: '#1a3b2b', color: 'white' }}>
                    <th style={{ padding: '12px' }}>ID Evento</th>
                    <th style={{ padding: '12px' }}>Nombre del Proyecto</th>
                    <th style={{ padding: '12px' }}>Participantes</th>
                    <th style={{ padding: '12px' }}>Fase</th>
                    <th style={{ padding: '12px' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {historialCursos.length > 0 ? (
                    historialCursos.map((curso, idx) => (
                      <tr key={curso.id_evento} style={{ backgroundColor: idx % 2 === 0 ? '#f8f9fa' : 'white', borderBottom: '1px solid #eee' }}>
                        <td style={{ padding: '12px', fontWeight: 'bold', color: '#1a3b2b' }}>
                          {curso.id_evento}
                          {curso.estado === 'CANCELADO' && <span style={{marginLeft: '8px', color: 'red', fontSize: '0.8rem'}}>(CANCELADO)</span>}
                        </td>
                        <td style={{ padding: '12px' }}>{curso.nombre_evento}</td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <span style={{ backgroundColor: '#b38e5d', color: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.9rem', fontWeight: 'bold' }}>
                            {curso.total_participantes}
                          </span>
                        </td>
                        <td style={{ padding: '12px' }}>{fases[curso.fase_actual - 1] || `Fase ${curso.fase_actual}`}</td>
                        <td style={{ padding: '12px', display: 'flex', gap: '8px' }}>
                          <button onClick={() => handleVerDetalles(curso.id_evento)} style={{ padding: '6px 12px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem' }} title="Detalles">⚙️ Detalles</button>
                          <button 
                            onClick={() => downloadZip(curso.id_evento)} 
                            style={{ padding: '6px 12px', backgroundColor: '#1a3b2b', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem' }}
                            title="Descargar ZIP"
                          >
                            📥 ZIP
                          </button>
                          <button 
                            onClick={() => handleDeleteEvent(curso.id_evento)} 
                            style={{ padding: '6px 12px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem' }}
                            title="Eliminar Proyecto"
                          >
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" style={{ padding: '20px', textAlign: 'center', color: '#666' }}>No hay eventos registrados en el historial.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* VISTA: DETALLES DE EVENTO (NUEVA) */}
        {activeView === 'detalle_evento' && (
          <section className="card full-width-card fade-in">
            <div className="dashboard-header">
              <h2>Detalles del Evento: {selectedEventId}</h2>
              <button onClick={() => changeView('historial')} className="btn-refresh">⬅️ Volver</button>
            </div>
            
            <div style={{display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap'}}>
              <button onClick={handleCancelarEvento} style={{backgroundColor: '#dc3545', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>
                ❌ Cancelar Evento
              </button>
              <form onSubmit={handleSubirSCPM07} style={{display: 'flex', gap: '10px', alignItems: 'center', backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', border: '1px solid #ddd'}}>
                <label style={{fontWeight: 'bold'}}>Subir SCPM-07 (Calificaciones):</label>
                <input type="file" accept=".xlsx" onChange={e => setScpmFile(e.target.files[0])} />
                <button type="submit" disabled={!scpmFile} style={{backgroundColor: '#28a745', color: '#fff', padding: '8px 12px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>Subir</button>
              </form>
            </div>

            <div style={{ overflowX: 'auto', marginTop: '1.5rem' }}>
              <h3>Trabajadores Registrados</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ backgroundColor: '#1a3b2b', color: 'white' }}>
                    <th style={{ padding: '12px' }}>Ficha</th>
                    <th style={{ padding: '12px' }}>Nombre</th>
                    <th style={{ padding: '12px' }}>Estado</th>
                    <th style={{ padding: '12px' }}>Calificación</th>
                    <th style={{ padding: '12px' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {eventWorkers.map(w => (
                    <tr key={w.ficha_trabajador} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '12px' }}>{w.ficha_trabajador}</td>
                      <td style={{ padding: '12px' }}>{w.nombre_trabajador}</td>
                      <td style={{ padding: '12px', color: w.estado === 'BAJA' ? 'red' : 'green' }}>{w.estado}</td>
                      <td style={{ padding: '12px' }}>{w.calificacion ?? '-'}</td>
                      <td style={{ padding: '12px' }}>
                        {w.estado !== 'BAJA' && (
                          <button onClick={() => handleBajaTrabajador(w.ficha_trabajador)} style={{backgroundColor: '#ffc107', color: '#000', padding: '6px 12px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>Dar de Baja</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* VISTA 1: GESTIÓN DE EXPEDIENTES (ASISTENTE PASO A PASO) */}
        {activeView === 'generador' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            
            {/* PASO 1: EXTRACCIÓN */}
            <section className="card full-width-card fade-in">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ backgroundColor: '#1a3b2b', color: 'white', borderRadius: '50%', width: '35px', height: '35px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '1.2rem' }}>1</span>
                Extracción PDF a Excel (SCPM-01)
              </h2>
              <p className="card-description">
                Si aún no tienes el archivo de Excel, carga aquí el PDF oficial de asistencia (SCPM-01) para extraer la lista de trabajadores automáticamente.
              </p>
              <form onSubmit={handlePdfExtract} className="upload-form" style={{ maxWidth: '600px', backgroundColor: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', border: '1px dashed #ccc' }}>
                <input type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files[0])} className="file-input" />
                <button type="submit" disabled={isPdfLoading || !pdfFile} className="btn-primary" style={{ backgroundColor: '#b38e5d' }}>Extraer y Descargar Excel</button>
              </form>
              {pdfStatus.message && (
                <div className={`status-panel ${pdfStatus.type}`} style={{ marginTop: '1rem', maxWidth: '600px' }}>
                  <p>{pdfStatus.message}</p>
                </div>
              )}
            </section>

            {/* PASO 2: INYECCIÓN DE DATOS */}
            <section className="card full-width-card fade-in">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ backgroundColor: '#1a3b2b', color: 'white', borderRadius: '50%', width: '35px', height: '35px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '1.2rem' }}>2</span>
                Generación de Documentos y Formatos
              </h2>
              <p className="card-description">
                Sube el archivo Excel que acabas de descargar. Busca tu ID de evento, confirma en qué fase va el proyecto y selecciona qué formatos Word necesitas.
              </p>
              
              <div style={{ backgroundColor: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e9ecef', marginBottom: '1.5rem' }}>
                <div className="phase-header" style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                  <div style={{ flex: 1, minWidth: '300px' }}>
                    <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>1. ID del Evento:</label>
                    <form onSubmit={handleSearchEvent} className="search-form" style={{ display: 'flex', gap: '10px' }}>
                      <input
                        type="text"
                        placeholder="Ej. 50693032"
                        value={eventId}
                        onChange={(e) => setEventId(e.target.value)}
                        className="text-input"
                        style={{ flex: 1 }}
                      />
                      <button type="submit" disabled={isSearching || !eventId} className="btn-secondary search-btn">
                        {isSearching ? 'Buscando...' : '🔍 Buscar Fase'}
                      </button>
                    </form>
                  </div>
                </div>

                {/* BARRA DE PROGRESO INTERACTIVA */}
                <div className="stepper" style={{ marginTop: '2rem' }}>
                  {fases.map((fase, index) => (
                    <div 
                      key={index} 
                      className={`step ${currentPhase >= index + 1 ? 'completed' : ''} ${currentPhase === index + 1 ? 'current' : ''}`}
                      onClick={() => handleUpdatePhase(index + 1)}
                      style={{ cursor: 'pointer' }}
                      title="Clic para establecer esta fase manualmente"
                    >
                      <div className="step-number">{index + 1}</div>
                      <div className="step-label" style={{ fontSize: '0.8rem', textAlign: 'center' }}>{fase}</div>
                    </div>
                  ))}
                </div>
              </div>

              {status.message && (
                  <div className={`status-panel ${status.type}`} style={{ marginBottom: '1.5rem' }}>
                    <p>{status.message}</p>
                  </div>
              )}

              <form onSubmit={handleGenerate} className="upload-form">
                <div className="form-group">
                  <label>2. Archivo de Asistencia (Excel extraído):</label>
                  <input type="file" accept=".xlsx" onChange={handleFileChange} className="file-input" />
                </div>

                <div className="form-group document-selection" style={{ marginTop: '1.5rem', textAlign: 'left' }}>
                  <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>Selecciona los documentos a generar:</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '8px' }}>
                    {todasLasPlantillas.map(doc => (
                      <label key={doc} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', cursor: 'pointer' }}>
                        <input 
                          type="checkbox" 
                          checked={selectedDocs.includes(doc)}
                          onChange={() => handleDocSelection(doc)}
                        />
                        {doc.replace('.docx', '')}
                      </label>
                    ))}
                  </div>
                </div>

                <button type="submit" disabled={isLoading || selectedDocs.length === 0} className="btn-primary" style={{ marginTop: '1.5rem' }}>
                  {isLoading ? 'Inyectando Datos Oficiales...' : 'Generar Expediente (Word)'}
                </button>
              </form>
            </section>

            {/* PASO 3: DESCARGA */}
            <section className="card full-width-card fade-in">
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ backgroundColor: '#1a3b2b', color: 'white', borderRadius: '50%', width: '35px', height: '35px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '1.2rem' }}>3</span>
                Descarga del Expediente Final
              </h2>
              <p className="card-description">
                Descarga todos los documentos generados en Word y el archivo unificado en PDF dentro de un paquete ZIP. (Requiere el ID del evento).
              </p>
              <button 
                onClick={handleDownload} 
                className="btn-secondary" 
                style={{ maxWidth: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '1.1rem', padding: '1rem' }} 
                disabled={isLoading || !eventId}
              >
                📥 Descargar Expediente ZIP
              </button>
            </section>
          </div>
        )}

        {/* VISTA 2: DASHBOARD */}
        {activeView === 'dashboard' && (
          <section className="card full-width-card fade-in">
            <div className="dashboard-header">
              <h2>Dashboard Estadístico de Capacitación</h2>
              <div>
                <button onClick={handleExportDashboardImage} className="btn-secondary" style={{ marginRight: '10px' }}>🖼️ Exportar Gráficas (Imagen)</button>
                <button onClick={handleExportDashboard} className="btn-secondary" style={{ marginRight: '10px' }}>📥 Exportar CSV</button>
                <button onClick={fetchStats} className="btn-refresh">🔄 Actualizar</button>
              </div>
            </div>
            
            <div className="kpi-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats.total_cursos}</p>
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
              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #6f42c1' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Reprobados</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#6f42c1', margin: '5px 0 0 0' }}>{stats.reprobados ?? 0}</p>
              </div>
            </div>

            {stats.plan_accion && (
              <div style={{ backgroundColor: stats.plan_accion.startsWith('ALERTA') ? '#f8d7da' : stats.plan_accion.startsWith('PRECAUCIÓN') ? '#fff3cd' : '#d4edda', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', border: '1px solid #ccc' }}>
                <h3 style={{ marginTop: 0, color: '#333' }}>📋 Plan de Acción Recomendado (Índice de Reprobación)</h3>
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
                      <XAxis dataKey="nombre_evento" tick={{fontSize: 10}} tickFormatter={(val) => val.substring(0, 10) + '...'} />
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
                        {stats.cursos_por_fase.map((entry, index) => (
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
                          { name: 'Activos', value: stats.total_cursos - (stats.cursos_cancelados || 0) },
                          { name: 'Cancelados', value: stats.cursos_cancelados || 0 }
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
                      <YAxis domain={[0, 100]} />
                      <RechartsTooltip />
                      <Bar dataKey="promedio_curso" fill="#17a2b8" name="Promedio" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ color: '#666', fontStyle: 'italic' }}>No hay calificaciones registradas aún.</p>
                )}
              </div>
            </div>
          </section>
        )}

        {/* VISTA 4: CATÁLOGOS */}
        {activeView === 'catalogos' && (
           <section className="card fade-in" style={{ margin: '0 auto', maxWidth: '600px' }}>
              {/* Formulario de catálogos exacto... */}
              <h2>Administración de Catálogos</h2>
              <form onSubmit={handleCatalogUpdate} className="upload-form" style={{ marginTop: '1.5rem' }}>
                <select className="text-input" value={catalogType} onChange={(e) => setCatalogType(e.target.value)}>
                    <option value="">-- Elige una opción --</option>
                    <option value="curp">Catálogo Maestro de CURP</option>
                    <option value="stps">Catálogos STPS</option>
                </select>
                <input type="file" accept=".xlsx" onChange={(e) => setCatalogFile(e.target.files[0])} className="file-input" />
                <button type="submit" disabled={isCatalogLoading} className="btn-primary">Sobrescribir Catálogo</button>
              </form>
           </section>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} Petróleos Mexicanos (PEMEX) - Dirección de Procesos Industriales.</p>
      </footer>
    </div>
  );
}

export default App;
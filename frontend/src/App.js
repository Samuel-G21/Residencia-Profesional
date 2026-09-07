import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // --- Estados de Navegación ---
  const [activeView, setActiveView] = useState('generador');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // --- Estados de Fases Inteligente (NUEVO) ---
  const [currentPhase, setCurrentPhase] = useState(1);
  const [isSearching, setIsSearching] = useState(false);
  const fases = [
    "Planeación",
    "Análisis de situación",
    "Diseño de alto nivel",
    "Diseño detallado",
    "Preparación",
    "Implementación",
    "Evaluación"
  ];

  // --- Estados del Flujo Principal ---
  const [file, setFile] = useState(null);
  const [eventId, setEventId] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);

  // --- Estados del Dashboard Estadístico ---
  const [stats, setStats] = useState({
    total_cursos: 0,
    total_trabajadores: 0,
    top_cursos: []
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
    }
  }, [activeView]);

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
          message: 'Proyecto nuevo detectado. Iniciando en Fase 1 (Planeación).'
        });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Error de conexión al buscar el evento.' });
    } finally {
      setIsSearching(false);
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

    setIsLoading(true);
    setStatus({ type: 'info', message: 'Cruzando asistencia con Catálogos Oficiales y procesando Word...' });

    try {
      const response = await axios.post('http://localhost:5000/api/generate-docs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus({ type: 'success', message: response.data.message });
      // Al generar, forzamos la actualización de la barra para que salte a la fase 5
      setCurrentPhase(5);
    } catch (error) {
      setStatus({ type: 'error', message: error.response?.data?.message || 'Error con el servidor.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!eventId) {
      setStatus({ type: 'error', message: 'Escribe el ID del evento para descargar el expediente.' });
      return;
    }
    setStatus({ type: 'info', message: 'Empaquetando documentos en formato ZIP...' });
    try {
      const response = await axios.get(`http://localhost:5000/api/download-docs/${eventId}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Expediente_${eventId}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setStatus({ type: 'success', message: '¡Descarga del expediente completada con éxito!' });
    } catch (error) {
      setStatus({ type: 'error', message: 'Error al descargar. Verifica que ya estén generados.' });
    }
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
    setPdfStatus({ type: 'info', message: 'Procesando PDF maestro...' });

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
      setPdfStatus({ type: 'success', message: '¡Extracción exitosa! Excel descargado.' });
      setTimeout(() => setPdfStatus({ type: '', message: '' }), 4000);
    } catch (error) {
      setPdfStatus({ type: 'error', message: 'Error al procesar el PDF.' });
    } finally {
      setIsPdfLoading(false);
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

  const changeView = (view) => {
    setActiveView(view);
    setIsMenuOpen(false);
  };

  return (
    <div className="app-container">
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
                <button className={activeView === 'dashboard' ? 'active' : ''} onClick={() => changeView('dashboard')}>📊 Dashboard Estadístico</button>
                <button className={activeView === 'pdf' ? 'active' : ''} onClick={() => changeView('pdf')}>🛠️ Extracción PDF a Excel</button>
                <button className={activeView === 'catalogos' ? 'active' : ''} onClick={() => changeView('catalogos')}>📁 Actualizar Catálogos</button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* --- Contenedor Principal Dinámico --- */}
      <main className="main-content">

        {/* VISTA 1: GESTIÓN DE EXPEDIENTES */}
        {activeView === 'generador' && (
          <>
            {/* 1. MOTOR DE BÚSQUEDA Y SEGUIMIENTO */}
            <section className="card full-width-card phase-tracker">
              <div className="phase-header">
                <div style={{ flex: 1 }}>
                  <h2>Trazabilidad del Proyecto</h2>
                  <p className="card-description" style={{ marginBottom: 0 }}>Busca el ID del evento para consultar su fase actual.</p>
                </div>

                {/* BUSCADOR DE FASE */}
                <form onSubmit={handleSearchEvent} className="search-form">
                  <input
                    type="text"
                    placeholder="Ej. 50693032"
                    value={eventId}
                    onChange={(e) => setEventId(e.target.value)}
                    className="text-input"
                    style={{ width: '200px' }}
                  />
                  <button type="submit" disabled={isSearching} className="btn-secondary search-btn">
                    {isSearching ? '...' : ' Buscar Fase'}
                  </button>
                </form>
              </div>

              {/* BARRA DE PROGRESO INMUTABLE */}
              <div className="stepper" style={{ marginTop: '1.5rem' }}>
                {fases.map((fase, index) => (
                  <div key={index} className={`step ${currentPhase >= index + 1 ? 'completed' : ''} ${currentPhase === index + 1 ? 'current' : ''}`}>
                    <div className="step-number">{index + 1}</div>
                    <div className="step-label">{fase}</div>
                  </div>
                ))}
              </div>
            </section>

            {status.message && (
                <div className={`status-panel ${status.type}`} style={{ marginBottom: '1.5rem' }}>
                  <p>{status.message}</p>
                </div>
            )}

            <section className="card">
              <h2>2. Preparación de Expedientes (Fase 5)</h2>
              <p className="card-description">Sube el archivo Excel extraído para inyectar los catálogos y generar los formatos.</p>
              <form onSubmit={handleGenerate} className="upload-form">
                <div className="form-group">
                  <label>Archivo de Asistencia (Excel extraído):</label>
                  <input type="file" accept=".xlsx" onChange={handleFileChange} className="file-input" />
                </div>
                <button type="submit" disabled={isLoading} className="btn-primary">
                  {isLoading ? 'Inyectando Datos Oficiales...' : 'Generar Expediente (Word)'}
                </button>
              </form>
            </section>

            <section className="card">
              <h2>3. Cola de Impresión</h2>
              <p className="card-description">Descarga el expediente unificado en PDF y los archivos Word individuales en formato ZIP.</p>
              <button onClick={handleDownload} className="btn-secondary" disabled={isLoading || !eventId}>
                Descargar Expediente ZIP
              </button>
            </section>
          </>
        )}

        {/* VISTA 2: DASHBOARD */}
        {activeView === 'dashboard' && (
          <section className="card full-width-card fade-in">
             {/* Tu código del dashboard se mantiene exacto */}
             <div className="dashboard-header">
              <h2>Dashboard Estadístico de Capacitación</h2>
              <button onClick={fetchStats} className="btn-refresh"> Actualizar</button>
            </div>
            <div className="kpi-grid">
              <div className="kpi-card"><h3>Eventos Registrados</h3><p className="kpi-number">{stats.total_cursos}</p></div>
              <div className="kpi-card"><h3>Trabajadores Capacitados</h3><p className="kpi-number">{stats.total_trabajadores}</p></div>
            </div>
          </section>
        )}

        {/* VISTA 3: PDF A EXCEL */}
        {activeView === 'pdf' && (
           <section className="card fade-in" style={{ margin: '0 auto', maxWidth: '600px' }}>
              {/* Formulario PDF exacto... */}
              <h2>Extracción SCPM-01 a Excel</h2>
              <form onSubmit={handlePdfExtract} className="upload-form" style={{ marginTop: '1.5rem' }}>
                <input type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files[0])} className="file-input" />
                <button type="submit" disabled={isPdfLoading} className="btn-primary" style={{ backgroundColor: '#B38E5D' }}>Convertir a Excel</button>
              </form>
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
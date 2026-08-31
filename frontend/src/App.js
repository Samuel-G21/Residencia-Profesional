import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Estados para el flujo principal (Word y ZIP)
  const [file, setFile] = useState(null);
  const [eventId, setEventId] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);

  // Estados para el Dashboard Estadístico
  const [stats, setStats] = useState({
    total_cursos: 0,
    total_trabajadores: 0,
    top_cursos: []
  });

  // Estados para el Modal de Extracción PDF
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfStatus, setPdfStatus] = useState({ type: '', message: '' });
  const [isPdfLoading, setIsPdfLoading] = useState(false);

  // Cargar estadísticas
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/stats`);
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

  // --- Manejadores del Flujo Principal ---
  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!file || !eventId) {
      setStatus({ type: 'error', message: 'Selecciona un archivo y escribe la Clave del Evento.' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_evento', eventId);

    setIsLoading(true);
    setStatus({ type: 'info', message: 'Procesando documentos y guardando en base de datos...' });

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/generate-docs`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus({ type: 'success', message: response.data.message });
      fetchStats(); // Actualiza gráficas tras generar
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
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/download-docs/${eventId}`, {
        responseType: 'blob'
      });

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

  // --- Manejador para Extracción de PDF a Excel ---
  const handlePdfExtract = async (e) => {
    e.preventDefault();
    if (!pdfFile) {
      setPdfStatus({ type: 'error', message: 'Por favor, selecciona un archivo PDF.' });
      return;
    }

    const formData = new FormData();
    formData.append('file', pdfFile);

    setIsPdfLoading(true);
    setPdfStatus({ type: 'info', message: 'Procesando PDF, esto puede tomar unos segundos...' });

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/extract-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob' // Esencial para descargar el Excel directamente a la RAM
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Extraccion_Evento_${Date.now()}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setPdfStatus({ type: 'success', message: '¡Extracción exitosa! El archivo Excel se está descargando.' });

      // Limpiar y cerrar modal después de 3 segundos
      setTimeout(() => {
        setIsModalOpen(false);
        setPdfFile(null);
        setPdfStatus({ type: '', message: '' });
      }, 3000);

    } catch (error) {
      setPdfStatus({ type: 'error', message: 'Error al procesar el PDF. Revisa el formato.' });
    } finally {
      setIsPdfLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Cabecera Institucional con Botón Extra */}
      <header className="app-header">
        <div className="header-logos">
          <img src="/logo_gob.jpg" alt="Gobierno de México" className="logo-gobierno" />
          <img src="/logo_pemex.png" alt="PEMEX" className="logo-pemex" />
        </div>
        <div className="header-content-wrapper">
          <div className="header-title">
            <h1>Sistema de Automatización y Gestión de Capacitación</h1>
            <p>Capital Humano | Refineria Miguel Hidalgo</p>
          </div>

          {/* NUEVO: Botón para abrir el modal */}
          <div className="header-actions">
            <button className="btn-outline" onClick={() => setIsModalOpen(true)}>
              Herramienta PDF a Excel
            </button>
          </div>
        </div>
      </header>

      {/* Contenedor Principal */}
      <main className="main-content">
        <section className="card">
          <h2>1. Carga de Datos</h2>
          <p className="card-description">Sube el archivo con la información del evento.</p>
          <form onSubmit={handleGenerate} className="upload-form">
            <div className="form-group">
              <label>Informacion del Evento (Excel):</label>
              <input type="file" accept=".xlsx" onChange={handleFileChange} className="file-input" />
            </div>
            <div className="form-group">
              <label>Clave del Evento:</label>
              <input type="text" placeholder="Ej. 50693032" value={eventId} onChange={(e) => setEventId(e.target.value)} className="text-input" />
            </div>
            <button type="submit" disabled={isLoading} className="btn-primary">
              {isLoading ? 'Procesando Documentos...' : 'Generar Expediente (Word)'}
            </button>
          </form>
        </section>

        <section className="card">
          <h2>2. Impresión</h2>
          <p className="card-description">Descarga el expediente unificado en PDF y los archivos Word individuales en formato ZIP.</p>
          <button onClick={handleDownload} className="btn-secondary" disabled={isLoading}>
            Descargar Expediente ZIP
          </button>
          {status.message && (
            <div className={`status-panel ${status.type}`}><p>{status.message}</p></div>
          )}
        </section>

        <section className="card full-width-card">
          <div className="dashboard-header">
            <h2>3. Dashboard Estadístico de Capacitación</h2>
            <button onClick={fetchStats} className="btn-refresh" title="Actualizar métricas"> Actualizar</button>
          </div>
          <p className="card-description">Métricas consolidadas.</p>
          <div className="kpi-grid">
            <div className="kpi-card"><h3>Total de Eventos Registrados</h3><p className="kpi-number">{stats.total_cursos}</p></div>
            <div className="kpi-card"><h3>Trabajadores Capacitados</h3><p className="kpi-number">{stats.total_trabajadores}</p></div>
          </div>
          <div className="top-courses-section">
            <h3>Cursos con Mayor Demanda de Personal</h3>
            {stats.top_cursos && stats.top_cursos.length > 0 ? (
              <table className="stats-table">
                <thead><tr><th>Nombre del Evento</th><th style={{ textAlign: 'center' }}>Total Capacitados</th></tr></thead>
                <tbody>
                  {stats.top_cursos.map((item, idx) => (
                    <tr key={idx}><td>{item.nombre_evento}</td><td style={{ textAlign: 'center', fontWeight: 'bold', color: 'var(--pemex-green)' }}>{item.total_capacitados}</td></tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="no-data-text">No hay cursos registrados en el historial todavía.</p>
            )}
          </div>
        </section>
      </main>

      {/* NUEVO: Ventana Modal para Extracción PDF */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header-container">
              <h2>Extracción SCPM-01 a Excel</h2>
              <button className="close-btn" onClick={() => setIsModalOpen(false)}>✖</button>
            </div>
            <p className="modal-desc">Sube el documento PDF maestro (SCPM-01). El sistema extraerá los datos y te devolverá un formato de Excel estructurado para no depender de plataformas externas.</p>

            <form onSubmit={handlePdfExtract} className="upload-form" style={{ marginTop: '1.5rem' }}>
              <div className="form-group">
                <label>Archivo Maestro PDF:</label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setPdfFile(e.target.files[0])}
                  className="file-input"
                />
              </div>
              <button type="submit" disabled={isPdfLoading} className="btn-primary" style={{ backgroundColor: '#B38E5D' }}>
                {isPdfLoading ? 'Extrayendo Datos...' : 'Convertir a Excel'}
              </button>
            </form>

            {pdfStatus.message && (
              <div className={`status-panel ${pdfStatus.type}`} style={{ marginTop: '1.5rem' }}>
                <p>{pdfStatus.message}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* NUEVO: Pie de Página / Leyenda de Derechos Reservados */}
      <footer className="app-footer">
        <p>
          &copy; {new Date().getFullYear()} Petróleos Mexicanos (PEMEX) - Capital Humano.
          Todos los derechos reservados.
        </p>
        <p className="footer-credits">
          Sistema desarrollado como proyecto de Residencia Profesional.
        </p>
      </footer>

    </div>
  );
}

export default App;
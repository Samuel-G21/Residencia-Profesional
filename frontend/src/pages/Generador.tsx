import React, { useState } from 'react';
import Swal from 'sweetalert2';
import api from '../services/api';

const fases = [
  "Registro / Programación",
  "Ejecución del Evento",
  "Extracción SCPM-01",
  "Integración de Expediente",
  "Cierre / Firmas"
];
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
  'SCPM-03.docx',
  'SCPM-05A.xlsx'
];

const Generador: React.FC = () => {
  const [currentPhase, setCurrentPhase] = useState(1);
  const [isSearching, setIsSearching] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [fileScpm03, setFileScpm03] = useState<File | null>(null);
  const [eventId, setEventId] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [tipoCurso, setTipoCurso] = useState('Actualización');
  const [selectedDocs, setSelectedDocs] = useState<string[]>(todasLasPlantillas);
  
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfStatus, setPdfStatus] = useState({ type: '', message: '' });
  const [isPdfLoading, setIsPdfLoading] = useState(false);

  const [loadingMessage, setLoadingMessage] = useState('');

  const handleTipoCursoChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setTipoCurso(val);
  };

  const handleDocSelection = (doc: string) => {
    setSelectedDocs(prev => 
      prev.includes(doc) ? prev.filter(d => d !== doc) : [...prev, doc]
    );
  };

  const handlePdfExtract = async (e: React.FormEvent) => {
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
      const response = await api.post('/extract-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const contentDisposition = response.headers['content-disposition'];
      let fileName = `Guia de Asistencia - ${eventId || 'Generada'}.xlsx`;
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (fileNameMatch && fileNameMatch.length === 2) fileName = fileNameMatch[1];
      }
      link.setAttribute('download', fileName);
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

  const handleSearchEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eventId) {
      setStatus({ type: 'error', message: 'Escribe el ID del evento para buscar su fase actual.' });
      return;
    }

    setIsSearching(true);
    setStatus({ type: 'info', message: 'Consultando base de datos...' });

    try {
      const response = await api.get(`/evento/${eventId}`);

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

  const handleUpdatePhase = async (newPhase: number) => {
    if (!eventId) {
      setStatus({ type: 'error', message: 'Escribe el ID del evento primero.' });
      return;
    }
    setStatus({ type: 'info', message: 'Actualizando fase...' });
    try {
      const res = await api.put(`/evento/${eventId}/fase`, { fase: newPhase });
      if (res.data.status === 'success') {
        setCurrentPhase(newPhase);
        setStatus({ type: 'success', message: `Fase actualizada a ${newPhase} (${fases[newPhase - 1]})` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: 'Error al actualizar fase.' });
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !eventId) {
      setStatus({ type: 'error', message: 'Selecciona el Excel extraído y escribe la Clave del Evento.' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_evento', eventId);
    formData.append('docs_seleccionados', selectedDocs.join(','));
    formData.append('tipo_curso', tipoCurso);
    if (fileScpm03) {
      formData.append('file_scpm03', fileScpm03);
    }

    setIsLoading(true);
    setLoadingMessage('Generando formatos de Word en el servidor...');
    setStatus({ type: 'info', message: 'Procesando Word...' });

    try {
      const response = await api.post('/generate-docs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus({ type: 'success', message: response.data.message });
      setCurrentPhase(4);
    } catch (error: any) {
      setStatus({ type: 'error', message: error.response?.data?.message || 'Error con el servidor.' });
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const downloadZip = async (id_evento_descarga: string) => {
    setLoadingMessage('Convirtiendo a PDF y empaquetando en ZIP. Esto puede tardar...');
    try {
      const response = await api.get(`/download-docs/${id_evento_descarga}`, { responseType: 'blob' });
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
      Swal.fire('Error', 'Error al descargar el archivo. Es posible que aún no se haya generado.', 'error');
    } finally {
      setLoadingMessage('');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {loadingMessage && (
        <div className="loading-overlay" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(255,255,255,0.8)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
          <div className="spinner" style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #1a3b2b', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite' }}></div>
          <div className="loading-text" style={{ marginTop: '1rem', fontWeight: 'bold' }}>{loadingMessage}</div>
        </div>
      )}

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
          <input type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files?.[0] || null)} className="file-input" />
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
                  {isSearching ? 'Buscando...' : ' Buscar Fase'}
                </button>
              </form>
            </div>
          </div>

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
            <input type="file" accept=".xlsx" onChange={(e) => setFile(e.target.files?.[0] || null)} className="file-input" required />
          </div>

          <div className="form-group" style={{ marginTop: '1.5rem' }}>
            <label>2.1. Archivo SCPM-03 Lleno (Opcional, para extraer Supervisor Técnico):</label>
            <input type="file" accept=".docx" onChange={(e) => setFileScpm03(e.target.files?.[0] || null)} className="file-input" />
          </div>

          <div className="form-group document-selection" style={{ marginTop: '1.5rem', textAlign: 'left' }}>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>3. Tipo de Curso:</label>
            <select id="tipo_curso_select" className="text-input" style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc', width: '100%', marginBottom: '1rem' }} value={tipoCurso} onChange={handleTipoCursoChange}>
              <option value="Actualización">Actualización</option>
              <option value="Ascenso">Ascenso</option>
            </select>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>4. Selecciona los documentos a generar:</label>
            <div style={{ marginBottom: '1rem', display: 'flex', gap: '10px' }}>
              <button type="button" onClick={() => {
                const visibles = todasLasPlantillas.filter(doc => {
                  if (tipoCurso === 'Ascenso') return !doc.includes('SCPM-05 2025.docx');
                  return !doc.includes('SCPM-05A.xlsx');
                });
                setSelectedDocs(visibles);
              }} className="btn-secondary" style={{ padding: '5px 10px', fontSize: '0.9rem' }}>Seleccionar Todos</button>
              <button type="button" onClick={() => setSelectedDocs([])} className="btn-secondary" style={{ padding: '5px 10px', fontSize: '0.9rem' }}>Deseleccionar Todos</button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '8px' }}>
              {todasLasPlantillas.filter(doc => {
                  if (tipoCurso === 'Ascenso') return !doc.includes('SCPM-05 2025.docx');
                  return !doc.includes('SCPM-05A.xlsx');
              }).map(doc => (
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
          onClick={() => { if(eventId) downloadZip(eventId); else setStatus({ type: 'error', message: 'Escribe el ID del evento para descargar el expediente.' }); }} 
          className="btn-secondary" 
          style={{ maxWidth: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '1.1rem', padding: '1rem' }} 
          disabled={isLoading || !eventId}
        >
           Descargar Expediente ZIP
        </button>
      </section>
    </div>
  );
};

export default Generador;

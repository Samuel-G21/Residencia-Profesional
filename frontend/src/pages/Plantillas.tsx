import React, { useState } from 'react';
import Swal from 'sweetalert2';
import api from '../services/api';

const Plantillas: React.FC = () => {
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [templateStatus, setTemplateStatus] = useState({ type: '', message: '' });
  const [isTemplateLoading, setIsTemplateLoading] = useState(false);

  const handleTemplateUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!templateFile) {
      setTemplateStatus({ type: 'error', message: 'Selecciona una plantilla .docx, .xlsx, .xlsm o .xls para subir.' });
      return;
    }
    const formData = new FormData();
    formData.append('file', templateFile);
    setIsTemplateLoading(true);
    setTemplateStatus({ type: 'info', message: 'Procesando plantilla y guardando en el servidor...' });

    try {
      const response = await api.post('/upload-template', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (response.data.warning) {
        Swal.fire({
          icon: 'warning',
          title: 'Aviso sobre .xls',
          text: response.data.warning
        });
      }
      setTemplateStatus({ type: 'success', message: response.data.message });
      setTimeout(() => {
        setTemplateFile(null);
        setTemplateStatus({ type: '', message: '' });
      }, 4000);
    } catch (error: any) {
      setTemplateStatus({ type: 'error', message: error.response?.data?.message || 'Error al subir la plantilla.' });
    } finally {
      setIsTemplateLoading(false);
    }
  };

  return (
    <section className="card full-width-card fade-in">
      <h2>Gestor de Plantillas</h2>
      <p className="card-description">
        Sube nuevas plantillas de Word (.docx) o Excel (.xlsx, .xlsm, .xls) para que el sistema las pueda autocompletar.
        Para que el sistema sepa dónde colocar cada dato, debes usar las <b>etiquetas</b> que se muestran abajo.
        Sólo copia y pega la etiqueta en tu documento Word. El sistema las convertirá automáticamente.
      </p>
      
      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', marginTop: '1.5rem' }}>
        <div style={{ flex: '1 1 400px', backgroundColor: '#f8f9fa', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e9ecef' }}>
          <h3>Subir Nueva Plantilla</h3>
          <form onSubmit={handleTemplateUpload} className="upload-form" style={{ marginTop: '1rem' }}>
            <input 
              type="file" 
              accept=".docx, .xlsx, .xlsm, .xls" 
              onChange={(e) => setTemplateFile(e.target.files?.[0] || null)} 
              className="file-input" 
              style={{ marginBottom: '1rem', width: '100%' }}
            />
            <button type="submit" disabled={isTemplateLoading} className="btn-primary" style={{ width: '100%' }}>
              {isTemplateLoading ? 'Subiendo...' : 'Subir Plantilla'}
            </button>
          </form>
          {templateStatus.message && (
            <div className={`status-panel ${templateStatus.type}`} style={{ marginTop: '1rem' }}>
              <p>{templateStatus.message}</p>
            </div>
          )}
        </div>

        <div style={{ flex: '2 1 500px' }}>
          <h3>Etiquetas Disponibles (Cheatsheet)</h3>
          <p style={{ fontSize: '0.9rem', color: '#555', marginBottom: '1rem' }}>Haz clic en cualquier etiqueta para copiarla al portapapeles.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
            {[
              '[FICHA]', '[APELLIDO_PATERNO]', '[APELLIDO_MATERNO]', '[NOMBRE]', 
              '[NOMBRE_COMPLETO]', '[CURP]', '[NOMBRE_EVENTO]', '[CLAVE_EVENTO]', 
              '[DURACION]', '[NOMBRE_INSTRUCTOR]', '[FICHA_INSTRUCTOR]', 
              '[FECHA_INICIO]', '[FECHA_TERMINO]', '[DIA_INICIO]', '[MES_INICIO]', 
              '[ANIO_INICIO]', '[DIA_TERMINO]', '[MES_TERMINO]', '[ANIO_TERMINO]', 
              '[CATEGORIA]', '[NIVEL]', '[DEPARTAMENTO]', '[TIPO_CURSO]'
            ].map(tag => (
              <div 
                key={tag} 
                onClick={() => {
                  navigator.clipboard.writeText(tag);
                  Swal.fire({
                    icon: 'success',
                    title: 'Copiado',
                    text: `Etiqueta ${tag} copiada al portapapeles`,
                    timer: 1500,
                    showConfirmButton: false
                  });
                }}
                style={{
                  backgroundColor: '#e9ecef', 
                  padding: '8px 12px', 
                  borderRadius: '4px', 
                  fontFamily: 'monospace', 
                  cursor: 'pointer',
                  textAlign: 'center',
                  border: '1px solid #ccc'
                }}
                title="Clic para copiar"
              >
                {tag}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Plantillas;

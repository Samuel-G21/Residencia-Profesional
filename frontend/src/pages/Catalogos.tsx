import React, { useState } from 'react';
import api from '../services/api';

const Catalogos: React.FC = () => {
  const [catalogType, setCatalogType] = useState('');
  const [catalogFile, setCatalogFile] = useState<File | null>(null);
  const [catalogStatus, setCatalogStatus] = useState({ type: '', message: '' });
  const [isCatalogLoading, setIsCatalogLoading] = useState(false);

  const handleCatalogUpdate = async (e: React.FormEvent) => {
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
      const response = await api.post('/update-catalog', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCatalogStatus({ type: 'success', message: response.data.message });
      setTimeout(() => {
        setCatalogFile(null);
        setCatalogType('');
        setCatalogStatus({ type: '', message: '' });
      }, 4000);
    } catch (error: any) {
      setCatalogStatus({ type: 'error', message: error.response?.data?.message || 'Error al actualizar el catálogo.' });
    } finally {
      setIsCatalogLoading(false);
    }
  };

  return (
    <section className="card fade-in" style={{ margin: '0 auto', maxWidth: '600px' }}>
      <h2>Administración de Catálogos</h2>
      <form onSubmit={handleCatalogUpdate} className="upload-form" style={{ marginTop: '1.5rem' }}>
        <select className="text-input" value={catalogType} onChange={(e) => setCatalogType(e.target.value)}>
            <option value="">-- Elige una opción --</option>
            <option value="curp">Catálogo Maestro de CURP</option>
            <option value="stps">Catálogos STPS</option>
        </select>
        <input type="file" accept=".xlsx" onChange={(e) => setCatalogFile(e.target.files?.[0] || null)} className="file-input" />
        <button type="submit" disabled={isCatalogLoading} className="btn-primary">Sobrescribir Catálogo</button>
      </form>
      {catalogStatus.message && (
        <div className={`status-panel ${catalogStatus.type}`} style={{ marginTop: '1rem' }}>
          <p>{catalogStatus.message}</p>
        </div>
      )}
    </section>
  );
};

export default Catalogos;

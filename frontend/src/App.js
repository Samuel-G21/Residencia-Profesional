import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Asegúrate de tener este archivo para los estilos básicos

function App() {
  const [file, setFile] = useState(null);
  const [eventId, setEventId] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 1. Manejar la selección del archivo Excel
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // 2. Procesar y Generar los Documentos (Word)
  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!file || !eventId) {
      setStatus('⚠️ Por favor selecciona un archivo y escribe el ID del curso.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('id_evento', eventId);

    setIsLoading(true);
    setStatus('Procesando documentos en el servidor...');

    try {
      const response = await axios.post('http://localhost:5000/api/generate-docs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus(`✅ ${response.data.message}`);
    } catch (error) {
      setStatus(`❌ Error: ${error.response?.data?.message || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Descargar el ZIP final
  const handleDownload = async () => {
    if (!eventId) {
      setStatus('⚠️ Escribe el ID del evento para descargar el ZIP.');
      return;
    }

    setStatus('Empaquetando documentos, por favor espera...');

    try {
      // Configuramos axios para recibir un archivo binario (blob)
      const response = await axios.get(`http://localhost:5000/api/download-docs/${eventId}`, {
        responseType: 'blob'
      });

      // Crear un enlace temporal para forzar la descarga en el navegador
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Expediente_${eventId}.zip`);
      document.body.appendChild(link);
      link.click();

      setStatus('✅ ¡Descarga completada con éxito!');
    } catch (error) {
      setStatus('❌ Error al descargar el archivo ZIP. Verifica que el ID sea correcto.');
    }
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '0 auto' }}>
      <h1>⚙️ Sistema de Automatización PEMEX</h1>
      <p>Sube la base de datos semanal (SEM. 12.26) para generar los expedientes.</p>

      <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>

        <div>
          <label><b>1. Archivo Excel: </b></label>
          <input type="file" accept=".xlsx" onChange={handleFileChange} />
        </div>

        <div>
          <label><b>2. ID del Evento (Curso): </b></label>
          <input
            type="text"
            placeholder="Ej: 50693032"
            value={eventId}
            onChange={(e) => setEventId(e.target.value)}
          />
        </div>

        <button type="submit" disabled={isLoading} style={{ padding: '10px', backgroundColor: '#00553d', color: 'white', border: 'none', cursor: 'pointer' }}>
          {isLoading ? 'Generando...' : 'Generar Documentos (Word)'}
        </button>
      </form>

      <hr style={{ margin: '30px 0' }} />

      <h3>📥 Descarga de Expediente</h3>
      <button onClick={handleDownload} style={{ padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}>
        Descargar Archivo ZIP (con PDFs)
      </button>

      {status && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
          <strong>Estado:</strong> {status}
        </div>
      )}
    </div>
  );
}

export default App;
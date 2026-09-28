import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import api from '../services/api';

const DetalleEvento: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [eventWorkers, setEventWorkers] = useState<any[]>([]);
  const [scpmFile, setScpmFile] = useState<File | null>(null);

  useEffect(() => {
    if (id) {
      fetchTrabajadoresEvento(id);
    }
  }, [id]);

  const fetchTrabajadoresEvento = async (id_evento: string) => {
    try {
      const res = await api.get(`/evento/${id_evento}/trabajadores`);
      if (res.data.status === 'success') {
        setEventWorkers(res.data.data);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleFinalizarEvento = async () => {
    const result = await Swal.fire({
      title: '¿Finalizar Evento?',
      text: '¿Seguro que deseas finalizar este evento?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, finalizar',
      cancelButtonText: 'Cancelar'
    });
    if(!result.isConfirmed) return;
    
    try {
      const res = await api.put(`/evento/${id}/finalizar`);
      if(res.data.status === 'success') {
        Swal.fire('¡Éxito!', 'Evento finalizado', 'success');
        navigate('/historial');
      }
    } catch(err) {
      Swal.fire('Error', 'Error finalizando evento', 'error');
    }
  };

  const handleCancelarEvento = async () => {
    const result = await Swal.fire({
      title: '¿Cancelar Evento?',
      text: '¿Seguro que deseas cancelar este evento?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      confirmButtonText: 'Sí, cancelar',
      cancelButtonText: 'No'
    });
    if(!result.isConfirmed) return;
    
    try {
      const res = await api.put(`/evento/${id}/cancelar`);
      if(res.data.status === 'success') {
        Swal.fire('Cancelado', 'Evento cancelado', 'success');
        navigate('/historial');
      }
    } catch(err) {
      Swal.fire('Error', 'Error cancelando evento', 'error');
    }
  };

  const handleBajaTrabajador = async (ficha: string) => {
    const { value: motivo } = await Swal.fire({
      title: 'Dar de Baja',
      text: `¿Motivo de baja para el trabajador con ficha ${ficha}?`,
      input: 'text',
      showCancelButton: true,
      inputValidator: (value) => {
        if (!value) {
          return '¡Necesitas escribir un motivo!';
        }
      }
    });

    if (!motivo) return;

    try {
      const res = await api.put(`/evento/${id}/trabajador/${ficha}/baja`, { motivo });
      if(res.data.status === 'success') {
        Swal.fire('¡Baja exitosa!', 'Trabajador dado de baja', 'success');
        if (id) fetchTrabajadoresEvento(id);
      }
    } catch(err) {
      Swal.fire('Error', 'Error dando de baja al trabajador', 'error');
    }
  };

  const handleSubirSCPM07 = async (e: React.FormEvent) => {
    e.preventDefault();
    if(!scpmFile || !id) return;
    const formData = new FormData();
    formData.append('file', scpmFile);
    
    try {
      const res = await api.post(`/evento/${id}/scpm07`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if(res.data.status === 'success') {
        Swal.fire('¡Actualizado!', 'Calificaciones actualizadas', 'success');
        fetchTrabajadoresEvento(id);
      }
    } catch(err: any) {
      Swal.fire('Error', 'Error: ' + (err.response?.data?.message || err.message), 'error');
    } finally {
      setScpmFile(null);
    }
  };

  const handleGenerarSTPS = async () => {
    if (!id) return;
    try {
      const response = await api.post(`/evento/${id}/stps/export`, {}, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `STPS_${id}.xlsm`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      Swal.fire('Éxito', 'Archivo STPS generado y descargado correctamente.', 'success');
    } catch (error: any) {
      let msg = 'Error al generar el archivo STPS.';
      if (error.response?.data instanceof Blob) {
        try {
          const text = await error.response.data.text();
          const json = JSON.parse(text);
          msg = json.message || msg;
        } catch (e) {
          // ignore parsing error
        }
      } else if (error.response?.data?.message) {
        msg = error.response.data.message;
      }
      Swal.fire('Error', msg, 'error');
    }
  };

  const handleGenerarSCPM07 = async () => {
    if (!id) return;
    try {
      const response = await api.post(`/evento/${id}/scpm07/export`, {}, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SCPM-07_${id}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      Swal.fire('Éxito', 'Archivo SCPM-07 generado y descargado correctamente.', 'success');
    } catch (error: any) {
      let msg = 'Error al generar el archivo SCPM-07.';
      if (error.response?.data instanceof Blob) {
        try {
          const text = await error.response.data.text();
          const json = JSON.parse(text);
          msg = json.message || msg;
        } catch (e) {
          // ignore parsing error
        }
      } else if (error.response?.data?.message) {
        msg = error.response.data.message;
      }
      Swal.fire('Error', msg, 'error');
    }
  };

  const hasCalificaciones = eventWorkers.some(w => w.calificacion !== null && w.calificacion !== undefined);

  return (
    <section className="card full-width-card fade-in">
      <div className="dashboard-header">
        <h2>Detalles del Evento: {id}</h2>
        <button onClick={() => navigate('/historial')} className="btn-refresh"> Volver</button>
      </div>
      
      <div style={{display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap'}}>
        <button onClick={handleCancelarEvento} style={{backgroundColor: '#dc3545', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>
           Cancelar Evento
        </button>
        <button onClick={handleFinalizarEvento} style={{backgroundColor: '#28a745', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>
           Finalizar Evento
        </button>
        <form onSubmit={handleSubirSCPM07} style={{display: 'flex', gap: '10px', alignItems: 'center', backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', border: '1px solid #ddd'}}>
          <label style={{fontWeight: 'bold'}}>Subir SCPM-07 (Calificaciones):</label>
          <input type="file" accept=".xlsx" onChange={e => setScpmFile(e.target.files?.[0] || null)} />
          <button type="submit" disabled={!scpmFile} style={{backgroundColor: '#28a745', color: '#fff', padding: '8px 12px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>Subir</button>
        </form>
        <button 
          onClick={handleGenerarSTPS} 
          disabled={!hasCalificaciones}
          style={{backgroundColor: hasCalificaciones ? '#006B54' : '#ccc', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: hasCalificaciones ? 'pointer' : 'not-allowed'}}
        >
          Generar STPS
        </button>
        <button 
          onClick={handleGenerarSCPM07} 
          disabled={!hasCalificaciones}
          style={{backgroundColor: hasCalificaciones ? '#006B54' : '#ccc', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: hasCalificaciones ? 'pointer' : 'not-allowed'}}
        >
          Generar SCPM-07
        </button>
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
  );
};

export default DetalleEvento;

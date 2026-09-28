import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import api from '../services/api';

const fases = [
  "Registro / Programación",
  "Ejecución del Evento",
  "Extracción SCPM-01",
  "Integración de Expediente",
  "Cierre / Firmas"
];

const Historial: React.FC = () => {
  const [historialCursos, setHistorialCursos] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchHistorial = async () => {
    try {
      const response = await api.get('/cursos');
      if (response.data.status === 'success') {
        setHistorialCursos(response.data.data);
      }
    } catch (error) {
      console.error('Error al cargar historial:', error);
    }
  };

  useEffect(() => {
    fetchHistorial();
  }, []);

  const handleVerDetalles = (id_evento: string) => {
    navigate(`/evento/${id_evento}`);
  };

  const downloadZip = async (id_evento_descarga: string) => {
    try {
      const response = await api.get(`/download-docs/${id_evento_descarga}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Expediente_${id_evento_descarga}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      Swal.fire('Éxito', '¡Descarga del expediente completada con éxito!', 'success');
    } catch (error) {
      Swal.fire('Error', 'Error al descargar el archivo. Es posible que aún no se haya generado.', 'error');
    }
  };

  const handleDeleteEvent = async (id_evento: string) => {
    const result = await Swal.fire({
      title: '¿Eliminar Evento?',
      text: `¿Estás seguro de eliminar el evento ${id_evento}? Esto borrará su historial y documentos generados.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });
    if (!result.isConfirmed) return;
    
    try {
      const res = await api.delete(`/evento/${id_evento}`);
      if (res.data.status === 'success') {
        fetchHistorial();
        Swal.fire('Eliminado', 'Evento eliminado correctamente.', 'success');
      }
    } catch (error) {
      Swal.fire('Error', 'Error al eliminar el evento.', 'error');
    }
  };

  return (
    <section className="card full-width-card fade-in">
      <div className="dashboard-header">
        <h2>Historial de Eventos y Proyectos</h2>
        <button onClick={fetchHistorial} className="btn-refresh">Actualizar</button>
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
                    {curso.estado === 'FINALIZADO' && <span style={{marginLeft: '8px', color: '#28a745', fontSize: '0.8rem'}}>(FINALIZADO)</span>}
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
                        ZIP
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
                <td colSpan={5} style={{ padding: '20px', textAlign: 'center', color: '#666' }}>No hay eventos registrados en el historial.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default Historial;

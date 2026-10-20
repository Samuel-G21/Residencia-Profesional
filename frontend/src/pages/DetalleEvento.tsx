/**
 * Vista de Detalle de Evento y Administracion de Participantes (`DetalleEvento.tsx`).
 *
 * Guia para practicantes:
 * Muestra el listado de trabajadores inscritos en un evento especifico (`/evento/:id`) y permite:
 * 1. Cancelar (`PUT /api/evento/:id/cancelar`) o finalizar (`PUT /api/evento/:id/finalizar`) el curso.
 * 2. Subir el formato `SCPM-07` (.xlsx) con las calificaciones finales (`POST /api/evento/:id/scpm07`).
 * 3. Generar y descargar el formato `SCPM-07` prellenado (`POST /api/evento/:id/scpm07/export`) y
 *    el archivo de constancias `STPS_<id>.xlsm` (`POST /api/evento/:id/stps/export`), el cual se
 *    habilita unicamente cuando al menos un trabajador ya cuenta con calificacion registrada.
 * 4. Agregar manualmente un trabajador adicional al evento (`POST /api/evento/:id/trabajador`),
 *    generando automaticamente su documentacion individual.
 * 5. Dar de baja (`BAJA`) o marcar como reprobado (`NO APTO`) a cualquier participante activo.
 */
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

  // Carga la lista de trabajadores inscritos en el evento actual
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

  // Marca el evento como FINALIZADO en la base de datos
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

  // Marca el evento como CANCELADO en la base de datos
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

  // Solicita la calificacion reprobatoria y marca al trabajador como NO APTO
  const handleNoApto = async (ficha: string) => {
    const { value: calificacion } = await Swal.fire({
      title: 'No Apto',
      text: `Ingrese la calificación para el trabajador con ficha ${ficha}:`,
      input: 'number',
      showCancelButton: true,
      inputValidator: (value) => {
        if (!value) {
          return '¡Necesitas ingresar una calificación!';
        }
      }
    });

    if (!calificacion) return;

    try {
      const res = await api.put(`/evento/${id}/trabajador/${ficha}/no_apto`, { calificacion });
      if(res.data.status === 'success') {
        Swal.fire('¡Éxito!', 'Trabajador marcado como No Apto', 'success');
        if (id) fetchTrabajadoresEvento(id);
      }
    } catch(err) {
      Swal.fire('Error', 'Error marcando como No Apto', 'error');
    }
  };

  // Solicita el motivo de baja y actualiza el estado del trabajador a BAJA
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

  // Sube el archivo Excel SCPM-07 para extraer y registrar las calificaciones de los participantes
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

  // Descarga el archivo STPS_<id>.xlsm con los participantes activos y sus calificaciones
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
          // Ignorar error de parseo si el blob no contiene JSON
        }
      } else if (error.response?.data?.message) {
        msg = error.response.data.message;
      }
      Swal.fire('Error', msg, 'error');
    }
  };

  // Descarga el formato de evaluacion SCPM-07_<id>.xlsx paginado de 5 en 5 trabajadores
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
          // Ignorar error de parseo si el blob no contiene JSON
        }
      } else if (error.response?.data?.message) {
        msg = error.response.data.message;
      }
      Swal.fire('Error', msg, 'error');
    }
  };

  // Verifica si al menos un participante tiene calificacion para habilitar la exportacion STPS
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
          title={!hasCalificaciones ? "Se requiere subir SCPM-07 con calificaciones" : "Generar constancias STPS"}
          style={{backgroundColor: hasCalificaciones ? '#006B54' : '#ccc', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: hasCalificaciones ? 'pointer' : 'not-allowed'}}
        >
          Generar STPS
        </button>
        <button 
          onClick={handleGenerarSCPM07} 
          title="Generar formato SCPM-07 en blanco para calificaciones"
          style={{backgroundColor: '#006B54', color: '#fff', padding: '10px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}
        >
          Generar SCPM-07
        </button>
      </div>

      <div style={{marginTop: '1.5rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px', border: '1px solid #ddd'}}>
        <h3>Agregar Nuevo Trabajador</h3>
        <form onSubmit={async (e) => {
          e.preventDefault();
          const form = e.target as HTMLFormElement;
          const ficha = (form.elements.namedItem('ficha') as HTMLInputElement).value;
          const nombre = (form.elements.namedItem('nombre') as HTMLInputElement).value;
          const curp = (form.elements.namedItem('curp') as HTMLInputElement).value;
          const categoria = (form.elements.namedItem('categoria') as HTMLInputElement).value;
          const nivel = (form.elements.namedItem('nivel') as HTMLInputElement).value;
          const departamento = (form.elements.namedItem('departamento') as HTMLInputElement).value;
          
          if(!ficha) {
            Swal.fire('Error', 'La Ficha es requerida', 'error');
            return;
          }

          try {
            const res = await api.post(`/evento/${id}/trabajador`, { ficha, nombre, curp, categoria, nivel, departamento });
            if(res.data.status === 'success') {
              Swal.fire('¡Éxito!', 'Trabajador agregado correctamente. Su documentación ha sido generada y se incluirá en el paquete ZIP.', 'success');
              form.reset();
              fetchTrabajadoresEvento(id!);
            }
          } catch(err: any) {
            Swal.fire('Error', 'Error: ' + (err.response?.data?.message || err.message), 'error');
          }
        }} style={{display: 'flex', gap: '10px', alignItems: 'flex-end', flexWrap: 'wrap'}}>
          <div>
            <label style={{display: 'block', fontWeight: 'bold'}}>Ficha: *</label>
            <input type="text" name="ficha" required style={{padding: '8px', width: '100px'}} />
          </div>
          <div>
            <label style={{display: 'block', fontWeight: 'bold'}}>Nombre Completo:</label>
            <input type="text" name="nombre" placeholder="(Opcional)" style={{padding: '8px', width: '250px'}} />
          </div>
          <div>
            <label style={{display: 'block', fontWeight: 'bold'}}>CURP:</label>
            <input type="text" name="curp" style={{padding: '8px', width: '180px'}} />
          </div>
          <div>
            <label style={{display: 'block', fontWeight: 'bold'}}>Categoría:</label>
            <input type="text" name="categoria" style={{padding: '8px', width: '150px'}} />
          </div>
          <div>
            <label style={{display: 'block', fontWeight: 'bold'}}>Nivel:</label>
            <input type="text" name="nivel" style={{padding: '8px', width: '80px'}} />
          </div>
          <div>
            <label style={{display: 'block', fontWeight: 'bold'}}>Depto:</label>
            <input type="text" name="departamento" style={{padding: '8px', width: '150px'}} />
          </div>
          <button type="submit" style={{backgroundColor: '#007bff', color: '#fff', padding: '9px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>
            Agregar Trabajador
          </button>
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
                <td style={{ padding: '12px', color: w.estado === 'BAJA' ? 'red' : w.estado === 'NO APTO' ? 'orange' : 'green' }}>{w.estado}</td>
                <td style={{ padding: '12px' }}>{w.calificacion ?? '-'}</td>
                <td style={{ padding: '12px' }}>
                  {w.estado !== 'BAJA' && w.estado !== 'NO APTO' && (
                    <div style={{display: 'flex', gap: '8px'}}>
                      <button onClick={() => handleBajaTrabajador(w.ficha_trabajador)} style={{backgroundColor: '#ffc107', color: '#000', padding: '6px 12px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>Dar de Baja</button>
                      <button onClick={() => handleNoApto(w.ficha_trabajador)} style={{backgroundColor: '#fd7e14', color: '#fff', padding: '6px 12px', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>No Apto</button>
                    </div>
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

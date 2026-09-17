import re

path = r'C:\Users\samy2\OneDrive\Escritorio\Escuela\Escuela\TECNM CLASES\9NO SEMESTRE\frontend\src\App.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import Swal
if 'import Swal from' not in content:
    content = content.replace("import './App.css';", "import './App.css';\nimport Swal from 'sweetalert2';")

# 2. Duplicate Aprobados card
dup_card = """              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Aprobados</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745', margin: '5px 0 0 0' }}>{stats.aprobados ?? 0}</p>
              </div>
              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Aprobados</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745', margin: '5px 0 0 0' }}>{stats.aprobados ?? 0}</p>
              </div>"""

single_card = """              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Aprobados</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745', margin: '5px 0 0 0' }}>{stats.aprobados ?? 0}</p>
              </div>"""

content = content.replace(dup_card, single_card)

# 3. Add Eventos Finalizados card
eventos_card = """              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats.total_cursos}</p>
              </div>"""

finalizados_card = """              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats.total_cursos}</p>
              </div>
              <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Finalizados</h3>
                <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745', margin: '5px 0 0 0' }}>{stats.cursos_finalizados ?? 0}</p>
              </div>"""

content = content.replace(eventos_card, finalizados_card)

# 4. Refactor alerts, confirms and prompts

# handleFinalizarEvento
old_fin = """  const handleFinalizarEvento = async () => {
    if(!window.confirm('¿Seguro que deseas finalizar este evento?')) return;
    try {
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/finalizar`);
      if(res.data.status === 'success') {
        alert('Evento finalizado');
        fetchHistorial();
        changeView('historial');
      }
    } catch(err) {
      alert('Error finalizando evento');
    }
  };"""
new_fin = """  const handleFinalizarEvento = async () => {
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
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/finalizar`);
      if(res.data.status === 'success') {
        Swal.fire('¡Éxito!', 'Evento finalizado', 'success');
        fetchHistorial();
        changeView('historial');
      }
    } catch(err) {
      Swal.fire('Error', 'Error finalizando evento', 'error');
    }
  };"""
content = content.replace(old_fin, new_fin)

# handleCancelarEvento
old_canc = """  const handleCancelarEvento = async () => {
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
  };"""
new_canc = """  const handleCancelarEvento = async () => {
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
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/cancelar`);
      if(res.data.status === 'success') {
        Swal.fire('Cancelado', 'Evento cancelado', 'success');
        fetchHistorial();
        changeView('historial');
      }
    } catch(err) {
      Swal.fire('Error', 'Error cancelando evento', 'error');
    }
  };"""
content = content.replace(old_canc, new_canc)

# handleBajaTrabajador
old_baja = """  const handleBajaTrabajador = async (ficha) => {
    const motivo = window.prompt(`¿Motivo de baja para el trabajador con ficha ${ficha}?`);
    if(motivo === null) return;
    try {
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/trabajador/${ficha}/baja`, { motivo });
      if(res.data.status === 'success') {
        alert('Trabajador dado de baja');
        fetchTrabajadoresEvento(selectedEventId);
      }
    } catch(err) {
      alert('Error dando de baja al trabajador');
    }
  };"""
new_baja = """  const handleBajaTrabajador = async (ficha) => {
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
      const res = await axios.put(`http://localhost:5000/api/evento/${selectedEventId}/trabajador/${ficha}/baja`, { motivo });
      if(res.data.status === 'success') {
        Swal.fire('¡Baja exitosa!', 'Trabajador dado de baja', 'success');
        fetchTrabajadoresEvento(selectedEventId);
      }
    } catch(err) {
      Swal.fire('Error', 'Error dando de baja al trabajador', 'error');
    }
  };"""
content = content.replace(old_baja, new_baja)

# handleSubirSCPM07
old_scpm = """        alert('Calificaciones actualizadas');
        fetchTrabajadoresEvento(selectedEventId);
      }
    } catch(err) {
      alert('Error: ' + (err.response?.data?.message || err.message));
    } finally {"""
new_scpm = """        Swal.fire('¡Actualizado!', 'Calificaciones actualizadas', 'success');
        fetchTrabajadoresEvento(selectedEventId);
      }
    } catch(err) {
      Swal.fire('Error', 'Error: ' + (err.response?.data?.message || err.message), 'error');
    } finally {"""
content = content.replace(old_scpm, new_scpm)

# handleDeleteEvent
old_del = """  const handleDeleteEvent = async (id_evento) => {
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
  };"""
new_del = """  const handleDeleteEvent = async (id_evento) => {
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
    
    setLoadingMessage('Eliminando evento...');
    try {
      const res = await axios.delete(`http://localhost:5000/api/evento/${id_evento}`);
      if (res.data.status === 'success') {
        fetchHistorial();
        Swal.fire('Eliminado', 'Evento eliminado correctamente.', 'success');
      }
    } catch (error) {
      Swal.fire('Error', 'Error al eliminar el evento.', 'error');
    } finally {
      setLoadingMessage('');
    }
  };"""
content = content.replace(old_del, new_del)

# downloadZip alert
old_down = """      setStatus({ type: 'success', message: '¡Descarga del expediente completada con éxito!' });
    } catch (error) {
      setStatus({ type: 'error', message: 'Error al descargar. Verifica que ya estén generados.' });
      alert('Error al descargar el archivo. Es posible que aún no se haya generado.');
    } finally {"""
new_down = """      setStatus({ type: 'success', message: '¡Descarga del expediente completada con éxito!' });
    } catch (error) {
      setStatus({ type: 'error', message: 'Error al descargar. Verifica que ya estén generados.' });
      Swal.fire('Error', 'Error al descargar el archivo. Es posible que aún no se haya generado.', 'error');
    } finally {"""
content = content.replace(old_down, new_down)

# handleExportDashboardImage alert
old_exp = """      link.click();
    } catch(err) {
      alert("Error al exportar gráficas");
    } finally {"""
new_exp = """      link.click();
    } catch(err) {
      Swal.fire('Error', 'Error al exportar gráficas', 'error');
    } finally {"""
content = content.replace(old_exp, new_exp)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")

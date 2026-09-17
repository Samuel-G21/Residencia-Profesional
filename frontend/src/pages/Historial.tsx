import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

const Historial: React.FC = () => {
  const { data: cursos, isLoading } = useQuery({
    queryKey: ['cursos'],
    queryFn: async () => {
      const { data } = await api.get('/cursos');
      return data.data;
    }
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="card full-width-card fade-in">
      <h2>Historial de Eventos y Proyectos</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ backgroundColor: '#1a3b2b', color: 'white' }}>
            <th style={{ padding: '12px' }}>ID Evento</th>
            <th style={{ padding: '12px' }}>Nombre del Proyecto</th>
            <th style={{ padding: '12px' }}>Fase</th>
          </tr>
        </thead>
        <tbody>
          {cursos?.map((curso: any) => (
            <tr key={curso.id_evento} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '12px' }}>{curso.id_evento}</td>
              <td style={{ padding: '12px' }}>{curso.nombre_evento}</td>
              <td style={{ padding: '12px' }}>{curso.fase_actual}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Historial;

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

const Dashboard: React.FC = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const { data } = await api.get('/stats');
      return data.data;
    }
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="card full-width-card fade-in">
      <h2>Dashboard Estadistico</h2>
      <div className="kpi-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats?.total_cursos}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

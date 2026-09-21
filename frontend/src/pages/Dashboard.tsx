import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard: React.FC = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const { data } = await api.get('/stats');
      return data.data;
    }
  });

  if (isLoading) return <div>Loading...</div>;

  const genderData = [
    { name: 'Hombres', cantidad: stats?.hombres || 0 },
    { name: 'Mujeres', cantidad: stats?.mujeres || 0 }
  ];

  return (
    <div className="card full-width-card fade-in">
      <h2>Dashboard Estadístico</h2>
      <div className="kpi-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Eventos</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats?.total_cursos}</p>
        </div>
        <div className="kpi-card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #1a3b2b' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#555' }}>Total Trabajadores</h3>
          <p className="kpi-number" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1a3b2b', margin: '5px 0 0 0' }}>{stats?.total_trabajadores}</p>
        </div>
      </div>

      <div className="charts-container" style={{ marginTop: '2rem' }}>
        <h3 style={{ color: '#555', marginBottom: '1rem' }}>Participantes por Género</h3>
        <div style={{ width: '100%', height: 300, backgroundColor: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={genderData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip cursor={{fill: 'transparent'}} />
              <Legend />
              <Bar dataKey="cantidad" fill="#1a3b2b" name="Participantes" barSize={60} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

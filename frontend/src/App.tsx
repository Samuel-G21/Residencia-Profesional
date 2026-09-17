import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import Historial from './pages/Historial';
import Generador from './pages/Generador';
import './App.css';

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app-container">
          <header className="app-header">
            <div className="header-title">
              <h1>Sistema de Automatizacion</h1>
            </div>
            <nav className="header-actions">
              <Link to="/" style={{marginRight: '1rem', color: 'white'}}>Generador</Link>
              <Link to="/historial" style={{marginRight: '1rem', color: 'white'}}>Historial</Link>
              <Link to="/dashboard" style={{color: 'white'}}>Dashboard</Link>
            </nav>
          </header>
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Generador />} />
              <Route path="/historial" element={<Historial />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
};

export default App;

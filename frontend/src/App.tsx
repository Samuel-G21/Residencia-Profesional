import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Swal from 'sweetalert2';
import api from './services/api';

import Dashboard from './pages/Dashboard';
import Historial from './pages/Historial';
import Generador from './pages/Generador';
import Catalogos from './pages/Catalogos';
import Plantillas from './pages/Plantillas';
import DetalleEvento from './pages/DetalleEvento';
import Login from './pages/Login';

import './App.css';

const queryClient = new QueryClient();

// Add axios interceptor here so it works globally
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => sessionStorage.getItem('isAuthenticated') === 'true');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    const resetTimeout = () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        if (isAuthenticated) {
          handleLogout();
          Swal.fire('Sesión Cerrada', 'Tu sesión ha expirado por inactividad.', 'info');
        }
      }, 15 * 60 * 1000);
    };

    if (isAuthenticated) {
      window.addEventListener('mousemove', resetTimeout);
      window.addEventListener('keydown', resetTimeout);
      window.addEventListener('scroll', resetTimeout);
      window.addEventListener('click', resetTimeout);
      resetTimeout();
    }

    return () => {
      clearTimeout(timeout);
      window.removeEventListener('mousemove', resetTimeout);
      window.removeEventListener('keydown', resetTimeout);
      window.removeEventListener('scroll', resetTimeout);
      window.removeEventListener('click', resetTimeout);
    };
  }, [isAuthenticated]);

  const handleLogout = () => {
    sessionStorage.removeItem('isAuthenticated');
    sessionStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app-container">
          <header className="app-header">
            <div className="header-logos">
              <img src="/logo_gob.jpg" alt="Gobierno de México" className="logo-gobierno" />
              <img src="/logo_pemex.png" alt="PEMEX" className="logo-pemex" />
            </div>
            <div className="header-content-wrapper">
              <div className="header-title">
                <h1>Sistema de Automatización</h1>
                <p>Desarrollo Humano | Refinería Tula</p>
              </div>

              <div className="header-actions dropdown-container">
                <button className="btn-menu" onClick={() => setIsMenuOpen(!isMenuOpen)}>
                  ☰ Menú de Herramientas
                </button>
                {isMenuOpen && (
                  <div className="dropdown-menu">
                    <Link to="/" onClick={() => setIsMenuOpen(false)}>Gestión de Expedientes</Link>
                    <Link to="/historial" onClick={() => setIsMenuOpen(false)}>Historial de Eventos</Link>
                    <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>Dashboard Estadístico</Link>
                    <Link to="/catalogos" onClick={() => setIsMenuOpen(false)}>Actualizar Catálogos</Link>
                    <Link to="/plantillas" onClick={() => setIsMenuOpen(false)}>Gestor de Plantillas</Link>
                    <button onClick={handleLogout} style={{ color: '#dc3545', fontWeight: 'bold' }}>Cerrar Sesión</button>
                  </div>
                )}
              </div>
            </div>
          </header>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<Generador />} />
              <Route path="/historial" element={<Historial />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/catalogos" element={<Catalogos />} />
              <Route path="/plantillas" element={<Plantillas />} />
              <Route path="/evento/:id" element={<DetalleEvento />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          
          <footer className="app-footer">
            <p>&copy; {new Date().getFullYear()} Petróleos Mexicanos (PEMEX) - Desarrollo Humano.</p>
          </footer>
        </div>
      </Router>
    </QueryClientProvider>
  );
};

export default App;

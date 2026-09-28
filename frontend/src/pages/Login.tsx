import React, { useState } from 'react';
import api from '../services/api';

interface LoginProps {
  onLogin: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    try {
      const response = await api.post('/auth/login', loginForm);
      if (response.data.status === 'success') {
        sessionStorage.setItem('isAuthenticated', 'true');
        sessionStorage.setItem('token', response.data.token);
        onLogin();
      }
    } catch (error: any) {
      setLoginError(error.response?.data?.message || 'Error al iniciar sesión');
    }
  };

  return (
    <div className="app-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f4f6f8' }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ color: '#1a3b2b', marginTop: '10px' }}>Iniciar Sesión</h2>
        </div>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ fontWeight: 'bold' }}>Usuario</label>
            <input 
              type="text" 
              className="text-input" 
              style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
              value={loginForm.username} 
              onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })} 
              required 
            />
          </div>
          <div>
            <label style={{ fontWeight: 'bold' }}>Contraseña</label>
            <input 
              type="password" 
              className="text-input"
              style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
              value={loginForm.password} 
              onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} 
              required 
            />
          </div>
          {loginError && <p style={{ color: '#dc3545', fontSize: '0.9rem', margin: 0 }}>{loginError}</p>}
          <button type="submit" className="btn-primary" style={{ marginTop: '1rem', width: '100%' }}>Ingresar</button>
        </form>
      </div>
    </div>
  );
};

export default Login;

/**
 * Punto de entrada principal de la aplicacion Frontend (React + Vite).
 *
 * Guia para practicantes:
 * Monta el componente raiz `<App />` dentro del elemento `#root` definido en `index.html`.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Medicion opcional de metricas de rendimiento web (Web Vitals)
reportWebVitals();

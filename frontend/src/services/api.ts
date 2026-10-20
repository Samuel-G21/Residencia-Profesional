/**
 * Instancia centralizada de Axios para comunicarse con la API REST del Backend (Flask).
 *
 * Guia para practicantes:
 * - Toma la URL base desde la variable de entorno `VITE_API_URL` (inyectada en el build de Docker)
 *   o usa `http://localhost:5000/api` por defecto en desarrollo local.
 * - El interceptor que adjunta el token JWT (`Authorization: Bearer <token>`) se registra en `App.tsx`.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
});

export default api;

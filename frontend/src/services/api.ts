import axios from 'axios';

// The Vite server proxy will route /api traffic to the FastAPI backend backend
export const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

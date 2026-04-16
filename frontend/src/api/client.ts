import axios from 'axios';

/** Token almacenado en localStorage bajo esta clave. */
const TOKEN_KEY = 'pos_token';

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 8000,
  headers: { 'Content-Type': 'application/json' },
});

// Inyectar token en cada solicitud si existe
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Redirigir al login si el backend devuelve 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export { TOKEN_KEY };

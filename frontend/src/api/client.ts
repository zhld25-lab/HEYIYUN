import axios, { type AxiosError } from 'axios';
import { message } from 'antd';

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
});

// Attach JWT from localStorage on every request.
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    if (status === 401) {
      localStorage.removeItem('access_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (status === 403) {
      message.error(detail || '无权访问该资源');
    } else if (detail) {
      message.error(detail);
    } else {
      message.error('请求失败，请稍后重试');
    }
    return Promise.reject(error);
  },
);

export default apiClient;

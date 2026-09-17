const API_BASE = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' && window.location.port === '5173' ? 'http://localhost:8000/api' : '/api');

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('veripack_token');
  const headers = options.headers || {};

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If not FormData, default to application/json
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = 'An error occurred';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errData.message || errorMsg;
    } catch {
      errorMsg = response.statusText;
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  auth: {
    login: (email, password) =>
      request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    getMe: () => request('/auth/me'),
  },
  scans: {
    analyze: (formData) =>
      request('/scans/analyze', {
        method: 'POST',
        body: formData,
      }),
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/scans?${qs}`);
    },
    getById: (id) => request(`/scans/${id}`),
    updateRemarks: (id, inspector_remarks) =>
      request(`/scans/${id}/remarks`, {
        method: 'PATCH',
        body: JSON.stringify({ inspector_remarks }),
      }),
  },
  dashboard: {
    getStats: () => request('/dashboard/stats'),
  },
  products: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/products?${qs}`);
    },
    getById: (id) => request(`/products/${id}`),
  },
  rules: {
    list: () => request('/rules'),
    toggle: (id) => request(`/rules/${id}/toggle`, { method: 'PATCH' }),
    update: (id, data) =>
      request(`/rules/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    create: (data) =>
      request('/rules', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  reports: {
    getPdfUrl: (id, download = false) =>
      `${API_BASE}/reports/${id}/pdf?download=${download}`,
  },
  users: {
    list: () => request('/users'),
    create: (data) =>
      request('/users', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id, data) =>
      request(`/users/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },
};

export const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:8000';

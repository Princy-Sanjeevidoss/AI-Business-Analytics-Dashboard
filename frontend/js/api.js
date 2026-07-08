const API_BASE = window.location.port === '8002'
  ? window.location.origin
  : 'http://127.0.0.1:8002';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (error) {
    throw new Error(`Cannot reach API server at ${API_BASE}. Start the backend with: python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002`);
  }
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.headers.get('content-length') === '0' ? null : response.json();
}

async function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = 'login.html';
}

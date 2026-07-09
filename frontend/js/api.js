const API_BASE = window.location.protocol === 'file:'
  ? 'http://127.0.0.1:8002'
  : window.location.origin;

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const isFormData = options.body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
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
    const errorText = await response.text();
    try {
      const errorJson = JSON.parse(errorText);
      const detail = Array.isArray(errorJson.detail)
        ? errorJson.detail.map(item => item.msg || JSON.stringify(item)).join('; ')
        : errorJson.detail;
      throw new Error(detail || errorText || `Request failed with status ${response.status}`);
    } catch (parseError) {
      if (parseError instanceof SyntaxError) {
        throw new Error(errorText || `Request failed with status ${response.status}`);
      }
      throw parseError;
    }
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

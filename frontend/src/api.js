const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Não foi possível concluir a solicitação.");
  }

  return response.status === 204 ? null : response.json();
}

export function login(email, password) {
  return request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password }),
  });
}

export function register(email, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getCurrentUser(token) {
  return request("/auth/me", { headers: { Authorization: `Bearer ${token}` } });
}

export function getClient(token) {
  return request("/clients", { headers: { Authorization: `Bearer ${token}` } });
}

export function getClientFull(token, clientId) {
  return request(`/clients/${clientId}/full`, { headers: { Authorization: `Bearer ${token}` } });
}

export function getMeals(token, clientId) {
  return request(`/clients/${clientId}/meals`, { headers: { Authorization: `Bearer ${token}` } });
}

export function createMeal(token, clientId, payload) {
  return request(`/clients/${clientId}/meal`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function getDashboardSummary(token, date) {
  const query = date ? `?reference_date=${date}` : "";
  return request(`/dashboard/summary${query}`, { headers: { Authorization: `Bearer ${token}` } });
}

export function getProgress(token, startDate, endDate) {
  return request(`/progress?start_date=${startDate}&end_date=${endDate}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function createClient(token, payload) {
  return request("/clients", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function createGoal(token, clientId, description) {
  return request(`/clients/${clientId}/goal`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ description }),
  });
}

export function updateClient(token, clientId, payload) {
  return request(`/clients/${clientId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function updateGoal(token, clientId, description) {
  return request(`/clients/${clientId}/goal`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ description }),
  });
}

export function setNutritionTarget(token, payload) {
  return request("/dashboard/target", {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

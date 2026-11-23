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

export function updateMeal(token, clientId, mealId, payload) {
  return request(`/clients/${clientId}/meal/${mealId}`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function deleteMeal(token, clientId, mealId) {
  return request(`/clients/${clientId}/meal/${mealId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function createMealAnalysis(token, clientId, mealId) {
  return request(`/clients/${clientId}/meal/${mealId}/analysis`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function runMealAnalysis(token, clientId, mealId, analysisId) {
  return request(`/clients/${clientId}/meal/${mealId}/analysis/${analysisId}/run`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function completeMealAnalysis(token, clientId, mealId, analysisId, items) {
  return request(`/clients/${clientId}/meal/${mealId}/analysis/${analysisId}`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(items),
  });
}

export function confirmMealAnalysis(token, clientId, mealId, analysisId, itemIds) {
  return request(`/clients/${clientId}/meal/${mealId}/analysis/${analysisId}/confirm`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ item_ids: itemIds }),
  });
}

export async function uploadMealImage(token, clientId, mealId, file) {
  const body = new FormData();
  body.append("image", file);
  const response = await fetch(`${API_URL}/clients/${clientId}/meal/${mealId}/image`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body,
  });
  if (!response.ok) {
    const result = await response.json().catch(() => ({}));
    throw new Error(result.detail || "Não foi possível enviar a imagem.");
  }
  return response.json();
}

export async function getMealImage(token, clientId, mealId) {
  const response = await fetch(`${API_URL}/clients/${clientId}/meal/${mealId}/image`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) return null;
  return URL.createObjectURL(await response.blob());
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

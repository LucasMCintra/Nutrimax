const TOKEN_KEY = "nutrimax-access-token";

export function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

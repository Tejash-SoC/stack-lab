import axios from "axios";

// One axios instance for the whole app.
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "/api" });

// 1) Attach the access token to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 2) If the access token expired (401), get a new one with the refresh token
//    and retry the original request once. If that fails, log the user out.
let refreshing = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const isAuthCall = original?.url?.includes("/auth/");
    const refresh = localStorage.getItem("refresh");

    if (error.response?.status === 401 && !original._retry && !isAuthCall && refresh) {
      original._retry = true;
      refreshing ??= axios
        .post(`${api.defaults.baseURL}/auth/refresh/`, { refresh })
        .finally(() => (refreshing = null));
      try {
        const { data } = await refreshing;
        localStorage.setItem("access", data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.dispatchEvent(new Event("logout"));
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// Turns a DRF error response into one readable sentence.
export function errorMessage(err) {
  const data = err.response?.data;
  if (!data) return "Can't reach the server. Check that the backend is running.";
  if (typeof data === "string") return "Something went wrong on the server.";
  if (data.detail) return data.detail;
  const first = Object.entries(data)[0];
  if (!first) return "Something went wrong.";
  const [field, msgs] = first;
  return `${field}: ${Array.isArray(msgs) ? msgs[0] : msgs}`;
}

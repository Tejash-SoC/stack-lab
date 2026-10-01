import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api from "./api";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("access")));

  const logout = useCallback(() => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  }, []);

  // On page load, restore the session if a token is stored.
  useEffect(() => {
    if (!localStorage.getItem("access")) return;
    api
      .get("/auth/me/")
      .then((res) => setUser(res.data))
      .catch(logout)
      .finally(() => setLoading(false));
  }, [logout]);

  // The axios interceptor fires this when refreshing fails.
  useEffect(() => {
    window.addEventListener("logout", logout);
    return () => window.removeEventListener("logout", logout);
  }, [logout]);

  const login = async (username, password) => {
    const { data } = await api.post("/auth/login/", { username, password });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    const me = await api.get("/auth/me/");
    setUser(me.data);
  };

  const register = async (username, email, password) => {
    await api.post("/auth/register/", { username, email, password });
    await login(username, password);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

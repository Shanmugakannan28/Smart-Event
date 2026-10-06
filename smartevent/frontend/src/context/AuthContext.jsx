import { createContext, useContext, useState, useCallback } from "react";
import api from "../api";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
  });

  const save = (data) => {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
  };

  const login = useCallback(async (email, password) => save((await api.post("/auth/login", { email, password })).data), []);
  const register = useCallback(
    async (username, email, password) => save((await api.post("/auth/register", { username, email, password })).data), []);
  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  return <AuthContext.Provider value={{ token, user, login, register, logout, isAuthed: !!token }}>{children}</AuthContext.Provider>;
}

import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const isAuthCall = err.config?.url?.startsWith("/auth/login") || err.config?.url?.startsWith("/auth/register");
    if (err.response?.status === 401 && !isAuthCall) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (!location.pathname.startsWith("/login")) location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// Turn FastAPI errors (string or Pydantic list) into one readable message.
export function errMsg(err, fallback = "Something went wrong. Please try again.") {
  const d = err?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => (x.msg || "").replace(/^Value error, /, "")).join(". ");
  if (!err?.response) return "Cannot reach the server. Check that the backend is running.";
  return fallback;
}

// Banner paths from the API are relative ("/static/banners/x.svg"); external URLs are left untouched.
export const imgUrl = (u) => (!u ? "" : u.startsWith("/") ? API_URL + u : u);

export const money = (n) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
// Backend returns naive UTC timestamps; mark them as UTC so they display in local time.
export const toDate = (s) => new Date(s.endsWith("Z") ? s : s + "Z");
export const fmtDate = (s) =>
  toDate(s).toLocaleString("en-IN", { day: "numeric", month: "short", year: "numeric", hour: "numeric", minute: "2-digit" });

export default api;

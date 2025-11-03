import axios from "axios";
import { jwtDecode } from "jwt-decode";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
  headers: { "Content-Type": "application/json" },
});

function isTokenExpired(token) {
  try {
    const decoded = jwtDecode(token);
    return decoded.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) throw new Error("No refresh token");

  const res = await axios.post("http://127.0.0.1:8000/api/token/refresh/", { refresh });
  const { access } = res.data;
  localStorage.setItem("access", access);
  return access;
}

api.interceptors.request.use(
  async (config) => {
    let access = localStorage.getItem("access");

    if (access && isTokenExpired(access)) {
      access = await refreshAccessToken();
    }

    if (access) {
      config.headers.Authorization = `Bearer ${access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;

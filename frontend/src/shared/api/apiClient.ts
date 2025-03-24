import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export const login = async (username: string, password: string) => {
  const res = await API.post("/auth/login/", { username, password });
  localStorage.setItem("token", res.data.access);
  return res.data;
};

export const triggerMatch = () => API.post("/match/");
export const clearMatch = () => API.delete("/match/");

export const listImports = () => API.get("/imports/");
export const createImport = (data: any) => API.post("/imports/", data);
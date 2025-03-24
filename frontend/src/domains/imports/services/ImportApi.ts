import api from "@/shared/api/apiClient";

export const createImportJob = async (type: string) => {
  const res = await api.post("/imports/", { type });
  return res.data;
};

export const listImports = async () => {
  const res = await api.get("/imports/");
  return res.data;
};
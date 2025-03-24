import React from "react";
import ReactDOM from "react-dom/client";
import AppRoutes from "@/routes/AppRoutes";
import { AuthProvider } from "@/domains/auth/context/AuthContext";
import { ToastContainer } from "react-toastify";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <AppRoutes />
      <ToastContainer />
    </AuthProvider>
  </React.StrictMode>
);
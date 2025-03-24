import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export const useToast = () => {
  const success = (msg: string) => toast.success(msg);
  const error = (msg: string) => toast.error(msg);
  return { success, error };
};
import { useState } from "react";
import api from "@/shared/api/apiClient";
import Input from "@/shared/components/Input/Input";
import Button from "@/shared/components/botton/Button"; // Fixed path to match actual file location
import { useAuthStore } from "@/shared/stores/authStore";

const LoginForm = () => {
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await api.post("/users/login", { email, password });
    login(res.data.access_token);
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 w-96 mx-auto mt-32">
      <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <Button type="submit">Login</Button>
    </form>
  );
};

export default LoginForm;
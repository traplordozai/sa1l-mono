import { useState } from 'react';
import API from '../services/api';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post('auth/login/', form);
      localStorage.setItem('access', res.data.access);
      localStorage.setItem('refresh', res.data.refresh);
      toast.success('Logged in!');
      navigate('/dashboard');
    } catch {
      toast.error('Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input className="input" type="text" placeholder="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
      <input className="input" type="password" placeholder="Password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
      <button className="btn w-full" type="submit">Login</button>
    </form>
  );
}
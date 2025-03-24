import { useState } from 'react';
import API from '../services/api';
import { toast } from 'react-toastify';

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.post('auth/register/', form);
      toast.success('Account created!');
    } catch {
      toast.error('Registration failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input className="input" type="text" placeholder="Username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
      <input className="input" type="email" placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
      <input className="input" type="password" placeholder="Password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
      <button className="btn w-full" type="submit">Register</button>
    </form>
  );
}
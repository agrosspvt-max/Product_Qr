import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { QrCode, LogIn } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const { login, isAuthed } = useAuth();
  const nav = useNavigate();
  const [busy, setBusy] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: { email: 'admin@company.com', password: '' },
  });

  if (isAuthed) return <Navigate to="/" replace />;

  async function onSubmit(values) {
    setBusy(true);
    try {
      await login(values.email, values.password);
      toast.success('Welcome back!');
      nav('/', { replace: true });
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Login failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-slate-50 p-4">
      <div className="w-full max-w-md card p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-600 grid place-items-center text-white">
            <QrCode size={20} />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-800">Product QR</h1>
            <p className="text-xs text-slate-500">Admin Dashboard</p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input
              type="email"
              className="input"
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && <p className="text-xs text-rose-600 mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <label className="label">Password</label>
            <input
              type="password"
              className="input"
              autoComplete="current-password"
              {...register('password', { required: 'Password is required' })}
            />
            {errors.password && <p className="text-xs text-rose-600 mt-1">{errors.password.message}</p>}
          </div>

          <button className="btn-primary w-full" disabled={busy} type="submit">
            <LogIn size={16} /> {busy ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="text-xs text-slate-400 text-center">
            Default admin: admin@company.com / admin123 (change in production)
          </p>
        </form>
      </div>
    </div>
  );
}

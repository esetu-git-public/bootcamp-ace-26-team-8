import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { loginUser } from '../services/authService';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginUser(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ledger-paper flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-semibold text-ledger-ink">Welcome back</h1>
          <p className="font-body text-sm text-ledger-slate mt-2">Sign in to the loan desk.</p>
        </div>

        {location.state?.justRegistered && (
          <p className="mb-4 text-sm font-body text-ledger-moss border border-ledger-moss/40 bg-ledger-moss/5 px-3 py-2">
            Account created. You can sign in now.
          </p>
        )}

        <form onSubmit={handleSubmit} className="border border-ledger-rule bg-white p-8 space-y-5">
          <div>
            <label className="block font-mono text-xs uppercase tracking-wide text-ledger-slate mb-1">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full border border-ledger-rule px-3 py-2 font-body text-sm focus:outline-none focus:border-ledger-gold"
            />
          </div>

          <div>
            <label className="block font-mono text-xs uppercase tracking-wide text-ledger-slate mb-1">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              className="w-full border border-ledger-rule px-3 py-2 font-body text-sm focus:outline-none focus:border-ledger-gold"
            />
          </div>

          {error && <p className="text-ledger-rust text-sm font-body">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-ledger-ink text-ledger-paper py-2.5 font-mono text-xs uppercase tracking-widest hover:bg-ledger-slate transition-colors disabled:opacity-50"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

          <p className="text-center text-sm font-body text-ledger-slate">
            Need an account?{' '}
            <Link to="/register" className="text-ledger-gold hover:underline">Register</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

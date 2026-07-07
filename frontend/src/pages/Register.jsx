import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../services/authService';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirm) {
      setError("Passwords don't match.");
      return;
    }

    setLoading(true);
    try {
      await registerUser({ name: form.name, email: form.email, password: form.password });
      navigate('/login', { state: { justRegistered: true } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ledger-paper flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-semibold text-ledger-ink">Open an account</h1>
          <p className="font-body text-sm text-ledger-slate mt-2">
            Register to apply for a loan and check your risk profile.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="border border-ledger-rule bg-white p-8 space-y-5">
          <div>
            <label className="block font-mono text-xs uppercase tracking-wide text-ledger-slate mb-1">
              Full name
            </label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              required
              className="w-full border border-ledger-rule px-3 py-2 font-body text-sm focus:outline-none focus:border-ledger-gold"
            />
          </div>

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
              minLength={8}
              className="w-full border border-ledger-rule px-3 py-2 font-body text-sm focus:outline-none focus:border-ledger-gold"
            />
          </div>

          <div>
            <label className="block font-mono text-xs uppercase tracking-wide text-ledger-slate mb-1">
              Confirm password
            </label>
            <input
              type="password"
              name="confirm"
              value={form.confirm}
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
            {loading ? 'Creating account…' : 'Create account'}
          </button>

          <p className="text-center text-sm font-body text-ledger-slate">
            Already have an account?{' '}
            <Link to="/login" className="text-ledger-gold hover:underline">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

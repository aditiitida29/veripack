import React, { useState } from 'react';
import { ShieldCheck, Lock, Mail, AlertCircle, ArrowRight, UserCheck, ShoppingBag, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Login() {
  const { login } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);

  const [email, setEmail] = useState('inspector.sharma@doca.gov.in');
  const [password, setPassword] = useState('Inspector@2026');
  const [fullName, setFullName] = useState('');

  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setIsLoading(true);

    try {
      if (isRegisterMode) {
        await api.auth.getMe; // check connection
        // Call register
        const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            password,
            full_name: fullName,
            role: 'CONSUMER',
            department: 'Citizen Consumer'
          })
        });
        if (!res.ok) {
          const errJson = await res.json();
          throw new Error(errJson.detail || 'Registration failed');
        }
        setSuccessMsg('Account registered successfully! Signing in...');
        await login(email, password);
      } else {
        await login(email, password);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemo = (demoEmail, demoPassword) => {
    setIsRegisterMode(false);
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-amber-500 via-white to-emerald-600"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-14 h-14 rounded-2xl bg-amber-500 flex items-center justify-center text-doca-950 font-black shadow-lg shadow-amber-500/20">
            <ShieldCheck className="w-9 h-9 text-doca-900" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-3xl font-extrabold tracking-tight text-white">
          VeriPack
        </h2>
        <p className="mt-1 text-center text-xs font-semibold text-amber-400 tracking-wide uppercase">
          Legal Metrology Compliance Inspector
        </p>
        <p className="mt-1 text-center text-xs text-slate-400">
          Department of Consumer Affairs (DoCA) • Ministry of Consumer Affairs, Food & Public Distribution
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-800/90 py-8 px-4 shadow-2xl border border-slate-700/60 sm:rounded-2xl sm:px-10">
          {/* Sign In vs Register Toggle */}
          <div className="flex rounded-xl bg-slate-900 p-1 mb-5 text-xs font-bold text-slate-400">
            <button
              type="button"
              onClick={() => {
                setIsRegisterMode(false);
                setError('');
              }}
              className={`flex-1 py-2 rounded-lg transition ${
                !isRegisterMode ? 'bg-amber-500 text-doca-950 shadow-xs' : 'hover:text-white'
              }`}
            >
              Officer / Citizen Login
            </button>
            <button
              type="button"
              onClick={() => {
                setIsRegisterMode(true);
                setError('');
                setEmail('');
                setPassword('');
              }}
              className={`flex-1 py-2 rounded-lg transition ${
                isRegisterMode ? 'bg-amber-500 text-doca-950 shadow-xs' : 'hover:text-white'
              }`}
            >
              Register Citizen Account
            </button>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {successMsg && (
              <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
                <UserCheck className="w-4 h-4 shrink-0" />
                <span>{successMsg}</span>
              </div>
            )}

            {isRegisterMode && (
              <div>
                <label className="block text-xs font-semibold text-slate-300">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="e.g. Rahul Verma"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-300">
                Email Address
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="name@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300">
                Password
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-doca-950 bg-amber-500 hover:bg-amber-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition"
            >
              {isLoading ? (
                <span>Processing...</span>
              ) : isRegisterMode ? (
                <>
                  <span>Create Citizen Account</span>
                  <UserPlus className="w-4 h-4" />
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* 1-Click Demo Accounts Selector */}
          <div className="mt-6 pt-6 border-t border-slate-700/80">
            <p className="text-xs font-semibold text-slate-400 text-center mb-3">
              Quick 1-Click Accounts by Role
            </p>
            <div className="grid grid-cols-1 gap-2">
              {/* Citizen Consumer */}
              <button
                type="button"
                onClick={() => handleQuickDemo('consumer.rahul@gmail.com', 'Consumer@2026')}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-900/80 hover:bg-slate-700/80 border border-indigo-900/60 text-xs text-slate-300 transition flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-indigo-400">Rahul Verma (Normal Citizen Customer)</span>
                  <p className="text-[10px] text-slate-400">Scan purchases, check MRP & net qty, report violations</p>
                </div>
                <ShoppingBag className="w-4 h-4 text-indigo-400" />
              </button>

              {/* Inspector */}
              <button
                type="button"
                onClick={() => handleQuickDemo('inspector.sharma@doca.gov.in', 'Inspector@2026')}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-900/80 hover:bg-slate-700/80 border border-slate-700 text-xs text-slate-300 transition flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-emerald-400">Inspector Sharma (Enforcement Officer)</span>
                  <p className="text-[10px] text-slate-400">Upload & scan, inspect, generate reports, remarks</p>
                </div>
                <UserCheck className="w-4 h-4 text-emerald-400" />
              </button>

              {/* Super Admin */}
              <button
                type="button"
                onClick={() => handleQuickDemo('admin@doca.gov.in', 'Admin@DocA2026')}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-900/80 hover:bg-slate-700/80 border border-slate-700 text-xs text-slate-300 transition flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-amber-400">Director Verma (Super Admin)</span>
                  <p className="text-[10px] text-slate-400">Full rule configuration & officer user management</p>
                </div>
                <UserCheck className="w-4 h-4 text-amber-400" />
              </button>

              {/* Auditor / Viewer */}
              <button
                type="button"
                onClick={() => handleQuickDemo('viewer@consumeraffairs.nic.in', 'Viewer@2026')}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-900/80 hover:bg-slate-700/80 border border-slate-700 text-xs text-slate-300 transition flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-blue-400">Pooja Mehta (Auditor / Viewer)</span>
                  <p className="text-[10px] text-slate-400">Read-only audit & report download</p>
                </div>
                <UserCheck className="w-4 h-4 text-blue-400" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

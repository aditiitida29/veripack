import React from 'react';
import { ShieldCheck, LogOut, User as UserIcon, ShoppingBag } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const isConsumer = user?.role === 'CONSUMER';

  return (
    <header className="bg-doca-900 text-white shadow-md border-b-2 border-amber-500 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Ministry Header */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-amber-500 flex items-center justify-center text-doca-950 font-black shadow-inner">
            <ShieldCheck className="w-6 h-6 text-doca-900" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-extrabold tracking-tight text-white">VeriPack</span>
              <span className="text-xs bg-doca-800 text-amber-300 font-semibold px-2 py-0.5 rounded border border-doca-700">
                Legal Metrology Division
              </span>
            </div>
            <p className="text-xs text-slate-300 hidden sm:block">
              Department of Consumer Affairs (DoCA) • Legal Metrology (PC) Rules, 2011
            </p>
          </div>
        </div>

        {/* User Profile & Actions */}
        {user && (
          <div className="flex items-center space-x-4">
            <div className="text-right hidden md:block">
              <div className="text-sm font-semibold text-white flex items-center justify-end gap-1.5">
                <span>{user.full_name}</span>
                <span
                  className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${
                    user.role === 'SUPER_ADMIN'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-400/40'
                      : user.role === 'INSPECTOR'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400/40'
                      : user.role === 'CONSUMER'
                      ? 'bg-indigo-500/20 text-indigo-300 border-indigo-400/40'
                      : 'bg-blue-500/20 text-blue-300 border-blue-400/40'
                  }`}
                >
                  {user.role === 'CONSUMER' ? 'Citizen Consumer' : user.role.replace('_', ' ')}
                </span>
              </div>
              <p className="text-xs text-slate-400">{user.email}</p>
            </div>

            <button
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-900/40 text-rose-300 hover:bg-rose-900/60 border border-rose-700/50 transition"
              title="Log out of session"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

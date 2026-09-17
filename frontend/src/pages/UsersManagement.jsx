import React, { useState, useEffect } from 'react';
import { Users, Plus, Shield, Check, X, UserPlus, Mail, BadgeCheck } from 'lucide-react';
import { api } from '../services/api';

export default function UsersManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'INSPECTOR',
    badge_number: '',
    department: 'DoCA Legal Metrology Enforcement',
  });

  const loadUsers = async () => {
    try {
      const data = await api.users.list();
      setUsers(data);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.users.create(formData);
      setShowModal(false);
      setFormData({
        email: '',
        full_name: '',
        password: '',
        role: 'INSPECTOR',
        badge_number: '',
        department: 'DoCA Legal Metrology Enforcement',
      });
      loadUsers();
    } catch (err) {
      alert('Failed to create account: ' + err.message);
    }
  };

  const handleToggleActive = async (user) => {
    try {
      await api.users.update(user.id, { is_active: !user.is_active });
      loadUsers();
    } catch (err) {
      alert('Failed to update status: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
              Access Control & RBAC
            </span>
            <span className="text-xs text-slate-400">Enforcement Officers Directory</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
            Authorized Personnel Management
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage Enforcement Directors, Field Inspectors, Compliance Auditors, and Citizen Consumers.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 px-4 py-2.5 bg-doca-900 text-white rounded-xl text-xs font-bold hover:bg-doca-800 transition shadow-sm"
        >
          <UserPlus className="w-4 h-4" />
          <span>Provision User Account</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-doca-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs text-left divide-y divide-slate-200">
              <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
                <tr>
                  <th className="py-3 px-4">User Name</th>
                  <th className="py-3 px-4">Official Email</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Badge / Dept</th>
                  <th className="py-3 px-4">Active</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      {u.full_name}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-600">
                      {u.email}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          u.role === 'SUPER_ADMIN'
                            ? 'bg-amber-100 text-amber-900 border border-amber-300'
                            : u.role === 'INSPECTOR'
                            ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                            : u.role === 'CONSUMER'
                            ? 'bg-indigo-100 text-indigo-900 border border-indigo-300'
                            : 'bg-blue-100 text-blue-900 border border-blue-300'
                        }`}
                      >
                        {u.role === 'CONSUMER' ? 'Citizen Consumer' : u.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {u.badge_number || '—'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {u.is_active ? 'Active' : 'Suspended'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleToggleActive(u)}
                        className="text-xs font-bold text-doca-600 hover:text-doca-800 hover:underline"
                      >
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Provision Officer / User Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900">Provision User Account</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Smt. Neha Kapoor"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="user@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Temporary Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">System Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="CONSUMER">CITIZEN / CONSUMER</option>
                    <option value="INSPECTOR">INSPECTOR</option>
                    <option value="VIEWER">VIEWER / AUDITOR</option>
                    <option value="SUPER_ADMIN">SUPER ADMIN</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Badge / Identifier</label>
                  <input
                    type="text"
                    placeholder="DOCA-DL-109 / Citizen"
                    value={formData.badge_number}
                    onChange={(e) => setFormData({ ...formData, badge_number: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 font-semibold text-slate-600 hover:text-slate-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 font-bold bg-doca-900 text-white rounded-lg hover:bg-doca-800"
                >
                  Create Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

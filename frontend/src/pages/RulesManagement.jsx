import React, { useState, useEffect } from 'react';
import { Scale, Plus, Check, X, ShieldAlert, ToggleLeft, ToggleRight, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function RulesManagement() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'SUPER_ADMIN';

  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newRule, setNewRule] = useState({
    rule_code: '',
    name: '',
    description: '',
    legal_reference: '',
    required_field: 'general',
    category_applicability: 'ALL',
    severity: 'FAIL',
  });

  const fetchRules = async () => {
    try {
      const data = await api.rules.list();
      setRules(data);
    } catch (err) {
      console.error('Failed to load rules:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleToggle = async (ruleId) => {
    if (!isAdmin) return;
    try {
      await api.rules.toggle(ruleId);
      fetchRules();
    } catch (err) {
      alert('Failed to toggle rule: ' + err.message);
    }
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    try {
      await api.rules.create(newRule);
      setShowAddModal(false);
      setNewRule({
        rule_code: '',
        name: '',
        description: '',
        legal_reference: '',
        required_field: 'general',
        category_applicability: 'ALL',
        severity: 'FAIL',
      });
      fetchRules();
    } catch (err) {
      alert('Failed to create rule: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
              Rule Engine Administration
            </span>
            <span className="text-xs text-slate-400">Section 52 & Rule 6 Framework</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
            Legal Metrology Compliance Rules
          </h1>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Manage active statutory rules, severity thresholds (Fail vs Warning), category applicability,
            and configure regulatory amendments dynamically without codebase rewrites.
          </p>
        </div>

        {isAdmin && (
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-doca-900 text-white rounded-xl text-xs font-bold hover:bg-doca-800 transition shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Regulatory Rule</span>
          </button>
        )}
      </div>

      {!isAdmin && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-800 flex items-center gap-2">
          <span>Read-only view. Only Enforcement Admins can toggle or modify statutory rules.</span>
        </div>
      )}

      {/* Rules Table */}
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
                  <th className="py-3 px-4">Code & Field</th>
                  <th className="py-3 px-4">Statutory Reference</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-slate-50 transition">
                    <td className="py-3.5 px-4">
                      <span className="font-mono font-bold text-slate-900 block">
                        {rule.rule_code}
                      </span>
                      <span className="text-[10px] text-slate-400 font-semibold uppercase">
                        {rule.required_field}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-doca-800 max-w-[180px]">
                      {rule.legal_reference}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-[260px] leading-relaxed">
                      {rule.description}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-100 font-bold text-[10px] text-slate-700">
                        {rule.category_applicability}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          rule.severity === 'FAIL'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {rule.severity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => handleToggle(rule.id)}
                        disabled={!isAdmin}
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold transition ${
                          rule.is_active
                            ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200'
                            : 'bg-slate-200 text-slate-500 hover:bg-slate-300'
                        }`}
                      >
                        {rule.is_active ? 'Active' : 'Disabled'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Custom Rule Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900">Add Statutory Rule</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateRule} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Rule Identifier Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. LM-RULE-AMEND-2026"
                  value={newRule.rule_code}
                  onChange={(e) => setNewRule({ ...newRule, rule_code: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Rule Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. E-Commerce Unit Price Declaration"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Legal Reference Citation</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Rule 6(1)(e) Proviso / DoCA Notification 2024"
                  value={newRule.legal_reference}
                  onChange={(e) => setNewRule({ ...newRule, legal_reference: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Explains statutory requirement and mandatory condition..."
                  value={newRule.description}
                  onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Severity</label>
                  <select
                    value={newRule.severity}
                    onChange={(e) => setNewRule({ ...newRule, severity: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="FAIL">FAIL (Violation)</option>
                    <option value="WARNING">WARNING (Review Required)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Category Applicability</label>
                  <select
                    value={newRule.category_applicability}
                    onChange={(e) => setNewRule({ ...newRule, category_applicability: e.target.value })}
                    className="w-full p-2 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="ALL">All Categories</option>
                    <option value="FOOD_BEVERAGE">Food & Beverage</option>
                    <option value="ELECTRONICS">Electronics</option>
                    <option value="COSMETICS">Cosmetics</option>
                  </select>
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 font-semibold text-slate-600 hover:text-slate-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 font-bold bg-doca-900 text-white rounded-lg hover:bg-doca-800"
                >
                  Save Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

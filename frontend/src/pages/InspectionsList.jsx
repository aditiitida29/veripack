import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, ArrowRight, ClipboardList, Clock } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function InspectionsList({ onSelectInspection, onNewScan }) {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    async function fetchList() {
      setLoading(true);
      try {
        const params = {};
        if (statusFilter) params.status = statusFilter;
        if (categoryFilter) params.category = categoryFilter;
        if (searchTerm) params.search = searchTerm;

        const data = await api.scans.list(params);
        setInspections(data);
      } catch (err) {
        console.error('Failed to load inspections:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchList();
  }, [statusFilter, categoryFilter, searchTerm]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
              Inspection Registry
            </span>
            <span className="text-xs text-slate-400">Searchable Audit Trail</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
            Inspection History & Records
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Historical log of all scanned packaged commodities, automated rule audits, and statutory findings.
          </p>
        </div>

        <button
          onClick={onNewScan}
          className="flex items-center gap-2 px-4 py-2 text-xs font-black bg-amber-500 text-doca-950 rounded-xl hover:bg-amber-400 transition shadow-sm shadow-amber-500/20"
        >
          <span>Scan Product</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Inspection ID, Product Name, or Brand..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-doca-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs py-2 px-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-doca-500 bg-white"
          >
            <option value="">All Statuses</option>
            <option value="COMPLIANT">Compliant</option>
            <option value="REVIEW_REQUIRED">Review Required</option>
            <option value="NON_COMPLIANT">Non-Compliant</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs py-2 px-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-doca-500 bg-white"
          >
            <option value="">All Categories</option>
            <option value="FOOD_BEVERAGE">Food & Beverage</option>
            <option value="COSMETICS">Cosmetics</option>
            <option value="ELECTRONICS">Electronics</option>
            <option value="HOUSEHOLD">Household</option>
            <option value="GENERAL">General</option>
          </select>
        </div>
      </div>

      {/* Inspections Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-doca-600"></div>
          </div>
        ) : inspections.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-2">
            <ClipboardList className="w-10 h-10 mx-auto text-slate-300" />
            <p className="text-sm font-semibold text-slate-700">No inspections found matching criteria.</p>
            <p className="text-xs text-slate-400">Try adjusting filters or scan a new product.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs text-left divide-y divide-slate-200">
              <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
                <tr>
                  <th className="py-3 px-4">Inspection ID</th>
                  <th className="py-3 px-4">Commodity Name</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Date & Time</th>
                  <th className="py-3 px-4">Inspector</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-center">Score</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-800">
                      {insp.inspection_code}
                      {insp.is_demo && (
                        <span className="ml-1.5 text-[9px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                          DEMO
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-900 max-w-[200px] truncate">
                      {insp.product_name}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      {insp.category?.replace('_', ' ').toLowerCase()}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {insp.created_at?.slice(0, 10)}
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 font-medium">
                      {insp.inspector_name}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={insp.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-slate-800">
                      {insp.confidence_score}%
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => onSelectInspection(insp.id)}
                        className="font-bold text-doca-600 hover:text-doca-800 hover:underline"
                      >
                        Inspect
                      </button>
                      <a
                        href={api.reports.getPdfUrl(insp.id, true)}
                        download
                        className="font-bold text-slate-500 hover:text-slate-800 hover:underline"
                        title="Download PDF Report"
                      >
                        PDF
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import {
  ScanSearch,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileText,
  ArrowRight,
  TrendingUp,
  ShieldAlert,
  Layers,
  Sparkles
} from 'lucide-react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

export default function Dashboard({ onNavigateScan, onOpenInspection }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await api.dashboard.getStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to load dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-doca-600"></div>
      </div>
    );
  }

  const compliantCount = stats?.compliant_count || 0;
  const reviewCount = stats?.review_required_count || 0;
  const nonCompliantCount = stats?.non_compliant_count || 0;
  const totalScans = stats?.total_scans || 0;

  const doughnutData = {
    labels: ['Compliant', 'Review Required', 'Non-Compliant'],
    datasets: [
      {
        data: [compliantCount, reviewCount, nonCompliantCount],
        backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
        borderWidth: 2,
        borderColor: '#FFFFFF',
      },
    ],
  };

  const topViolations = stats?.top_violations || [];
  const barData = {
    labels: topViolations.map((v) =>
      v.rule_name.length > 25 ? v.rule_name.slice(0, 22) + '...' : v.rule_name
    ),
    datasets: [
      {
        label: 'Violations / Incomplete Declarations',
        data: topViolations.map((v) => v.count),
        backgroundColor: '#1E3A5F',
        borderRadius: 6,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Top Banner with Government Emblem look */}
      <div className="bg-gradient-to-r from-doca-900 to-doca-800 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-l-4 border-amber-500">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
              Central Enforcement Portal
            </span>
            <span className="text-xs text-slate-300">Rule 6 & Schedule II Monitoring</span>
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white mt-1">
            Packaged Commodities Compliance Overview
          </h1>
          <p className="text-xs text-slate-300 max-w-2xl mt-1">
            Real-time inspection analytics for mandatory declarations: MRP, Net Quantity, Dates,
            Manufacturer/Importer PIN Code address, and Consumer Care Redressal Details.
          </p>
        </div>

        <button
          onClick={onNavigateScan}
          className="flex items-center gap-2 px-5 py-3 rounded-xl font-black text-sm bg-amber-500 text-doca-950 hover:bg-amber-400 shadow-lg shadow-amber-500/20 transition transform hover:-translate-y-0.5 shrink-0"
        >
          <ScanSearch className="w-5 h-5 text-doca-950" />
          <span>Scan New Product</span>
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Scanned */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Scans
            </p>
            <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{totalScans}</h3>
            <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-doca-600" />
              <span>Inspection repository</span>
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-doca-50 flex items-center justify-center text-doca-700">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        {/* Compliant */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">
              Compliant
            </p>
            <h3 className="text-3xl font-extrabold text-emerald-600 mt-1">{compliantCount}</h3>
            <p className="text-[11px] text-slate-400 mt-1">
              {stats?.compliance_rate || 0}% overall compliance
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        {/* Review Required */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider">
              Review Required
            </p>
            <h3 className="text-3xl font-extrabold text-amber-500 mt-1">{reviewCount}</h3>
            <p className="text-[11px] text-slate-400 mt-1">Ambiguity or warning</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-500">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        {/* Non-Compliant */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-rose-700 uppercase tracking-wider">
              Non-Compliant
            </p>
            <h3 className="text-3xl font-extrabold text-rose-600 mt-1">{nonCompliantCount}</h3>
            <p className="text-[11px] text-slate-400 mt-1">Violations detected</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-50 flex items-center justify-center text-rose-600">
            <XCircle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Distribution Donut */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span>Compliance Distribution</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Ratio of Pass vs Warning vs Violations</p>
          </div>
          <div className="h-56 flex items-center justify-center my-2">
            <Doughnut
              data={doughnutData}
              options={{
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                },
              }}
            />
          </div>
        </div>

        {/* Most Common Violations Bar Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Most Frequent Non-Compliances & Violations
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Breakdown by Legal Metrology (Packaged Commodities) Rule
            </p>
          </div>
          <div className="h-56 my-2">
            <Bar
              data={barData}
              options={{
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  y: { beginAtZero: true, ticks: { stepSize: 1 } },
                },
              }}
            />
          </div>
        </div>
      </div>

      {/* Priority Flagged Cases & Recent Inspections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Flagged Cases for Enforcement Officers */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <ShieldAlert className="w-5 h-5 text-rose-600" />
            <h3 className="text-sm font-bold text-slate-900">Priority Flagged Cases</h3>
          </div>
          <p className="text-xs text-slate-500 mb-4">
            Items marked Non-Compliant requiring physical verification and legal determination.
          </p>

          <div className="space-y-3">
            {stats?.priority_cases?.length > 0 ? (
              stats.priority_cases.map((pc) => (
                <div
                  key={pc.id}
                  onClick={() => onOpenInspection(pc.id)}
                  className="p-3 rounded-xl border border-rose-200 bg-rose-50/50 hover:bg-rose-50 cursor-pointer transition flex items-center justify-between"
                >
                  <div>
                    <span className="text-[10px] font-mono font-bold text-rose-800">
                      {pc.inspection_code}
                    </span>
                    <h4 className="text-xs font-bold text-slate-900 truncate max-w-[180px]">
                      {pc.product_name}
                    </h4>
                    <span className="text-[10px] text-rose-700">
                      {pc.fail_count} critical violations
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-rose-400" />
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No flagged violations at this moment.</p>
            )}
          </div>
        </div>

        {/* Recent Scans Table */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Recent Inspections</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Latest scanned labels and automatic rule evaluations
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-xs text-left">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 font-semibold uppercase">
                  <th className="py-2.5 px-3">Inspection ID</th>
                  <th className="py-2.5 px-3">Commodity</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Score</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stats?.recent_inspections?.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50 transition">
                    <td className="py-3 px-3 font-mono font-bold text-slate-700">
                      {item.inspection_code}
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-900 max-w-[180px] truncate">
                      {item.product_name}
                    </td>
                    <td className="py-3 px-3 text-slate-500">
                      {item.category.replace('_', ' ').toLowerCase()}
                    </td>
                    <td className="py-3 px-3">
                      <StatusBadge status={item.status} size="sm" />
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-slate-700">
                      {item.confidence_score}%
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => onOpenInspection(item.id)}
                        className="text-xs font-bold text-doca-600 hover:text-doca-800 hover:underline"
                      >
                        Inspect →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

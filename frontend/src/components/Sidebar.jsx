import React from 'react';
import {
  LayoutDashboard,
  ScanSearch,
  ClipboardList,
  PackageCheck,
  Scale,
  Users,
  BookOpen,
  Info,
  ShieldCheck,
  ShoppingBag
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ currentTab, setCurrentTab }) {
  const { user } = useAuth();
  const isAdmin = user?.role === 'SUPER_ADMIN';
  const isConsumer = user?.role === 'CONSUMER';

  const navItems = isConsumer
    ? [
        { id: 'dashboard', label: 'Consumer Dashboard', icon: LayoutDashboard },
        { id: 'scan', label: 'Verify Package Label', icon: ScanSearch, highlight: true },
        { id: 'inspections', label: 'My Scanned Packages', icon: ClipboardList },
        { id: 'products', label: 'Commodities Database', icon: PackageCheck },
        { id: 'guide', label: 'Consumer Rights & Law', icon: BookOpen },
      ]
    : [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'scan', label: 'Scan Product', icon: ScanSearch, highlight: true },
        { id: 'inspections', label: 'Inspections History', icon: ClipboardList },
        { id: 'products', label: 'Product Repository', icon: PackageCheck },
        { id: 'rules', label: 'Compliance Rules', icon: Scale },
        ...(isAdmin ? [{ id: 'users', label: 'User Management', icon: Users }] : []),
        { id: 'guide', label: 'Legal Metrology Guide', icon: BookOpen },
      ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 flex-1 space-y-1">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-3 pb-2">
          {isConsumer ? 'Citizen Consumer Suite' : 'Enforcement Suite'}
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          if (item.highlight) {
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-bold text-sm transition shadow-sm ${
                  isActive
                    ? 'bg-amber-500 text-doca-950 font-extrabold shadow-amber-200'
                    : 'bg-doca-900 text-white hover:bg-doca-800'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                <span className="w-2 h-2 rounded-full bg-amber-300 animate-ping"></span>
              </button>
            );
          }

          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg font-semibold text-sm transition ${
                isActive
                  ? 'bg-doca-50 text-doca-700 border-l-4 border-doca-700 pl-2'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Icon className="w-4 h-4 text-slate-500" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Citizen / Legal Metrology Notice */}
      <div className="p-4 border-t border-slate-100 bg-slate-50 text-xs text-slate-500">
        <div className="flex items-start gap-2">
          {isConsumer ? (
            <ShieldCheck className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          ) : (
            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          )}
          <div>
            <p className="font-semibold text-slate-700">
              {isConsumer ? 'Jago Grahak Jago:' : 'Legal Reference:'}
            </p>
            <p className="text-[11px] leading-tight text-slate-500 mt-0.5">
              {isConsumer
                ? 'Check MRP, Net Qty & Expiry before purchase. Report violations to NCH 1915.'
                : 'Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011.'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

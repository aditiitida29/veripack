import React, { useState, useEffect } from 'react';
import { Package, Search, Filter, Layers, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';

export default function ProductsRepository({ onSelectInspection }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    async function loadProducts() {
      setLoading(true);
      try {
        const params = {};
        if (categoryFilter) params.category = categoryFilter;
        if (searchTerm) params.search = searchTerm;
        const data = await api.products.list(params);
        setProducts(data);
      } catch (err) {
        console.error('Failed to load products:', err);
      } finally {
        setLoading(false);
      }
    }
    loadProducts();
  }, [categoryFilter, searchTerm]);

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
            Product Catalog
          </span>
          <span className="text-xs text-slate-400">Packaged Commodities Database</span>
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
          Scanned Products Repository
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Master registry of commodities inspected under the Legal Metrology (Packaged Commodities) Rules, 2011.
        </p>
      </div>

      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Product Name or Brand..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-doca-500"
          />
        </div>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="text-xs py-2 px-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-doca-500 bg-white w-full md:w-auto"
        >
          <option value="">All Categories</option>
          <option value="FOOD_BEVERAGE">Food & Beverage</option>
          <option value="COSMETICS">Cosmetics</option>
          <option value="ELECTRONICS">Electronics</option>
          <option value="HOUSEHOLD">Household</option>
          <option value="GENERAL">General</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full p-8 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-doca-600"></div>
          </div>
        ) : products.length === 0 ? (
          <div className="col-span-full p-12 text-center text-slate-400">
            <Package className="w-10 h-10 mx-auto text-slate-300 mb-2" />
            <p className="font-semibold text-slate-700 text-sm">No products found</p>
          </div>
        ) : (
          products.map((prod) => (
            <div
              key={prod.id}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[10px] uppercase font-bold text-doca-700 bg-doca-50 px-2 py-0.5 rounded border border-doca-100">
                    {prod.category?.replace('_', ' ')}
                  </span>
                  <StatusBadge status={prod.latest_status} size="sm" />
                </div>

                <h3 className="text-sm font-black text-slate-900 leading-tight">
                  {prod.name}
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Brand: <span className="font-medium text-slate-700">{prod.brand || 'Unbranded'}</span>
                </p>
                {prod.is_imported && (
                  <span className="inline-block mt-1 text-[10px] font-bold text-amber-800 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                    Imported (Rule 6(10))
                  </span>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="font-semibold">
                  {prod.inspections_count} Inspection{prod.inspections_count === 1 ? '' : 's'}
                </span>
                <span className="text-[11px] text-slate-400">
                  {prod.created_at?.slice(0, 10)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

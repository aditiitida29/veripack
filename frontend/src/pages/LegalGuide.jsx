import React from 'react';
import { BookOpen, Scale, AlertCircle, FileText, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function LegalGuide() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
            Statutory Reference Manual
          </span>
          <span className="text-xs text-slate-400">Enforcement Officer Quick Guide</span>
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
          Legal Metrology (Packaged Commodities) Rules, 2011
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Statutory declarations framework framed under Section 52 of the Legal Metrology Act, 2009 (1 of 2010).
        </p>
      </div>

      {/* Rule 6(1) Overview */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Scale className="w-5 h-5 text-doca-700" />
          <span>Rule 6(1): Mandatory Declarations on Every Pre-Packaged Commodity</span>
        </h3>

        <div className="space-y-3 text-xs text-slate-700">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(1)(a) — Manufacturer / Packer / Importer</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              Every package must bear the name and complete address of the manufacturer, or where manufacturer is not the packer, the name and address of both. For imported commodities, the name and complete address of the importer with 6-digit Postal PIN code is mandatory.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(1)(b) — Common / Generic Commodity Name</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              The common or generic name of the commodity contained in the package. If package contains multiple items, the name and quantity of each must be specified.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(1)(c) — Net Quantity in Standard Metric Units</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              Net quantity expressed in standard metric symbols: <b>g, kg, ml, l, m, cm, mm, sq m, cu m, N, U</b>. Non-standard colloquial abbreviations such as <i>gms, kgs, ltrs, pcs</i> are technically non-compliant under Rule 12 and the Second Schedule.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(1)(d) — Month & Year of Manufacture / Packing</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              The month and year of manufacture, packing, or import (e.g. <b>08/2026</b> or <b>AUG 2026</b>).
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(1)(e) — Maximum Retail Price (MRP)</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              Retail sale price clearly indicated as <b>MRP Rs. xx.xx (inclusive of all taxes)</b> or <b>MRP ₹ xx.xx (incl. of all taxes)</b>. Omission of the phrase 'inclusive of all taxes' constitutes a violation.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(1)(n) — Consumer Grievance Redressal Contact</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              The designation, full address, telephone number, and official e-mail address of the person or office who can be contacted in case of consumer complaints. Both telephone helpline AND email are mandatory.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-bold text-doca-800">Rule 6(10) — Country of Origin for Imported Commodities</span>
            <p className="mt-1 text-slate-600 leading-relaxed">
              For all imported commodities, the name of the country of origin or manufacture/assembly must be prominently declared on the package.
            </p>
          </div>
        </div>
      </div>

      {/* Penalties under Legal Metrology Act */}
      <div className="bg-white p-6 rounded-2xl border border-rose-200 shadow-sm space-y-3 bg-rose-50/20">
        <h3 className="text-base font-bold text-rose-900 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-rose-600" />
          <span>Statutory Penalties (Section 36 of Legal Metrology Act, 2009)</span>
        </h3>
        <p className="text-xs text-slate-700 leading-relaxed">
          Whoever manufactures, packs, imports, sells, distributes, delivers, or offers for sale any pre-packaged commodity which does not conform to the declarations on the package shall be punished:
        </p>
        <ul className="text-xs text-slate-700 space-y-1.5 list-disc list-inside">
          <li><b>First Offence:</b> Fine which may extend to <b>twenty-five thousand rupees (₹ 25,000)</b>.</li>
          <li><b>Second Offence:</b> Fine which may extend to <b>fifty thousand rupees (₹ 50,000)</b>.</li>
          <li><b>Subsequent Offence:</b> Fine which may extend to <b>one lakh rupees (₹ 1,00,000)</b> or imprisonment for a term which may extend to one year, or both.</li>
        </ul>
      </div>
    </div>
  );
}

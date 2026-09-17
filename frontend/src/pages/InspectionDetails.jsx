import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  ExternalLink,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Clock,
  ShieldCheck,
  Save,
  Tag,
  Scale,
  PhoneCall,
  AlertOctagon
} from 'lucide-react';
import { api, SERVER_URL } from '../services/api';
import { useAuth } from '../context/AuthContext';
import StatusBadge from '../components/StatusBadge';
import EvidenceViewer from '../components/EvidenceViewer';

export default function InspectionDetails({ inspectionId, onBack }) {
  const { user } = useAuth();
  const isConsumer = user?.role === 'CONSUMER';

  const [inspection, setInspection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('rules');
  const [activeRuleCode, setActiveRuleCode] = useState(null);
  const [remarks, setRemarks] = useState('');
  const [isSavingRemarks, setIsSavingRemarks] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    async function loadDetail() {
      try {
        const data = await api.scans.getById(inspectionId);
        setInspection(data);
        setRemarks(data.inspector_remarks || '');
      } catch (err) {
        console.error('Failed to load inspection:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [inspectionId]);

  const handleSaveRemarks = async () => {
    setIsSavingRemarks(true);
    try {
      await api.scans.updateRemarks(inspectionId, remarks);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert('Failed to save remarks: ' + err.message);
    } finally {
      setIsSavingRemarks(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-doca-600"></div>
      </div>
    );
  }

  if (!inspection) {
    return (
      <div className="p-8 text-center space-y-4">
        <p className="text-slate-500">Inspection record not found.</p>
        <button
          onClick={onBack}
          className="text-xs font-bold text-doca-600 hover:underline"
        >
          ← Back to Inspections
        </button>
      </div>
    );
  }

  const primaryImage = inspection.image_paths && inspection.image_paths.length > 0
    ? inspection.image_paths[0]
    : null;

  const ruleResults = inspection.rule_results || [];
  const extractedFields = inspection.extracted_fields || {};
  const boundingBoxes = inspection.bounding_boxes || [];

  const pdfDownloadUrl = api.reports.getPdfUrl(inspection.id, true);
  const pdfViewUrl = api.reports.getPdfUrl(inspection.id, false);

  return (
    <div className="space-y-6">
      {/* Navigation and Top Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-2xs transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Inspections</span>
        </button>

        <div className="flex items-center gap-2">
          <a
            href={pdfViewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-900 bg-white px-3.5 py-2 rounded-xl border border-slate-300 shadow-2xs transition"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>View PDF</span>
          </a>

          <a
            href={pdfDownloadUrl}
            download
            className="flex items-center gap-1.5 text-xs font-black text-doca-950 bg-amber-500 hover:bg-amber-400 px-4 py-2 rounded-xl shadow-sm shadow-amber-500/20 transition"
          >
            <Download className="w-4 h-4 text-doca-950" />
            <span>Download Official Report</span>
          </a>
        </div>
      </div>

      {/* Main Inspection Header Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-slate-400">
                {inspection.inspection_code}
              </span>
              {inspection.is_demo && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200">
                  DEMO RECORD
                </span>
              )}
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
              {inspection.product?.name || 'Packaged Commodity'}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
              <span>Category: <b>{inspection.product?.category?.replace('_', ' ')}</b></span>
              <span>•</span>
              <span>Origin: <b>{inspection.product?.is_imported ? 'Imported' : 'Domestic'}</b></span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>{inspection.created_at?.slice(0, 19).replace('T', ' ')}</span>
              </span>
            </div>
          </div>

          <div className="flex flex-col items-end gap-1.5 shrink-0">
            <StatusBadge status={inspection.status} size="lg" />
            <span className="text-xs font-semibold text-slate-500">
              Confidence Score: <b>{inspection.confidence_score}%</b>
            </span>
          </div>
        </div>

        {/* Legal Metrology Statutory Disclaimer Banner */}
        <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-200/80 flex items-start gap-2.5 text-xs text-amber-900">
          <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <b>Statutory Notice:</b> AI-assisted preliminary assessment under Legal Metrology (Packaged
            Commodities) Rules, 2011. Final legal determination, compounding, or seizure notice must
            be made by an authorized enforcement officer under the Legal Metrology Act, 2009.
          </p>
        </div>

        {/* Quick Quantitative Summary Pill Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Passed Rules</span>
            <p className="text-lg font-black text-emerald-600">{inspection.pass_count}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Violations (Fail)</span>
            <p className="text-lg font-black text-rose-600">{inspection.fail_count}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Warnings</span>
            <p className="text-lg font-black text-amber-500">{inspection.warning_count}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-center">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Audited Rules</span>
            <p className="text-lg font-black text-slate-800">{ruleResults.length}</p>
          </div>
        </div>
      </div>

      {/* Split Screen Layout: Left Evidence Viewer | Right Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT COLUMN: Interactive Visual Evidence Canvas (7 cols) */}
        <div className="lg:col-span-7 sticky top-20">
          <EvidenceViewer
            imageUrl={primaryImage}
            boundingBoxes={boundingBoxes}
            activeRuleCode={activeRuleCode}
            onSelectBox={(item) => setActiveRuleCode(item.rule_code)}
          />
        </div>

        {/* RIGHT COLUMN: Audit Details & Declarations (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Tabs */}
          <div className="flex rounded-xl bg-slate-200/80 p-1 text-xs font-bold text-slate-600">
            <button
              onClick={() => setActiveTab('rules')}
              className={`flex-1 py-2 rounded-lg transition ${
                activeTab === 'rules' ? 'bg-white text-slate-900 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              Statutory Audit ({ruleResults.length})
            </button>
            <button
              onClick={() => setActiveTab('fields')}
              className={`flex-1 py-2 rounded-lg transition ${
                activeTab === 'fields' ? 'bg-white text-slate-900 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              Declarations
            </button>
            <button
              onClick={() => setActiveTab('ocr')}
              className={`flex-1 py-2 rounded-lg transition ${
                activeTab === 'ocr' ? 'bg-white text-slate-900 shadow-xs' : 'hover:text-slate-900'
              }`}
            >
              Raw OCR
            </button>
          </div>

          {/* TAB 1: Statutory Rule Audit */}
          {activeTab === 'rules' && (
            <div className="space-y-3 max-h-[640px] overflow-y-auto pr-1">
              {ruleResults.map((r, idx) => {
                const isSelected = activeRuleCode === r.rule_code;
                return (
                  <div
                    key={idx}
                    onClick={() => setActiveRuleCode(r.rule_code)}
                    className={`p-4 rounded-xl border-2 transition cursor-pointer ${
                      isSelected
                        ? 'border-amber-500 bg-amber-50/40 shadow-sm'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-[10px] font-bold text-slate-400">
                            {r.rule_code}
                          </span>
                          <span className="text-[10px] text-slate-500 font-semibold">
                            {r.legal_reference}
                          </span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-900 mt-0.5">
                          {r.rule_name}
                        </h4>
                      </div>
                      <StatusBadge status={r.status} size="sm" />
                    </div>

                    <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                      {r.message}
                    </p>

                    {r.evidence && (
                      <div className="mt-2.5 p-2 bg-slate-50 rounded-lg border border-slate-100 text-[11px] text-slate-700">
                        <span className="font-semibold text-slate-500">Observed: </span>
                        <span className="font-mono">{r.evidence}</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* TAB 2: Extracted Declarations Table */}
          {activeTab === 'fields' && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden text-xs">
              <table className="min-w-full divide-y divide-slate-100">
                <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-3 text-left">Declaration Field</th>
                    <th className="py-2.5 px-3 text-left">Detected Value</th>
                    <th className="py-2.5 px-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {Object.entries(extractedFields).map(([key, val]) => (
                    <tr key={key} className="hover:bg-slate-50">
                      <td className="py-2.5 px-3 font-semibold text-slate-700 capitalize">
                        {key.replace('_', ' ')}
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-900 max-w-[140px] truncate">
                        {typeof val === 'object' ? val?.value || val?.name || '—' : String(val)}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            val?.status === 'DETECTED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : val?.status === 'AMBIGUOUS'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {val?.status || 'DETECTED'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: Raw OCR Stream */}
          {activeTab === 'ocr' && (
            <div className="bg-slate-900 text-slate-200 p-4 rounded-xl border border-slate-800 text-xs font-mono max-h-[400px] overflow-y-auto whitespace-pre-wrap leading-relaxed">
              {inspection.raw_ocr_text || 'No raw OCR stream available.'}
            </div>
          )}

          {/* If Consumer: Consumer Grievance Action Card */}
          {isConsumer ? (
            <div className="bg-white p-5 rounded-xl border border-indigo-200 shadow-sm space-y-3 bg-indigo-50/30">
              <div className="flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-indigo-600 shrink-0" />
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Citizen Redressal & Complaint Action
                </h4>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                Found a non-compliant or misleading package? Under Section 36 of the Legal Metrology
                Act, 2009, consumer rights are legally protected against missing MRP, incorrect net
                weights, or missing consumer care contacts.
              </p>

              <div className="pt-2 flex flex-col sm:flex-row gap-2">
                <a
                  href="https://consumerhelpline.gov.in/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>File NCH Complaint Portal</span>
                </a>
                <a
                  href="tel:1915"
                  className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-bold border border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>Call 1915 (Toll-Free)</span>
                </a>
              </div>
            </div>
          ) : (
            /* If Officer / Inspector: Enforcement Notes Editor */
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Officer Remarks & Enforcement Notes
                </h4>
                {savedSuccess && (
                  <span className="text-[11px] text-emerald-600 font-bold">✓ Saved</span>
                )}
              </div>

              <textarea
                rows={3}
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Add inspection notes, sample batch details, or statutory show-cause recommendations..."
                className="w-full text-xs p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-doca-500 focus:outline-none"
              />

              <div className="flex justify-end">
                <button
                  onClick={handleSaveRemarks}
                  disabled={isSavingRemarks}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold bg-doca-900 text-white rounded-lg hover:bg-doca-800 transition shadow-2xs"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{isSavingRemarks ? 'Saving...' : 'Save Remarks'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

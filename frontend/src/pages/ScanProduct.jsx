import React, { useState } from 'react';
import {
  Upload,
  ScanSearch,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  FileImage,
  Layers,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  RotateCw
} from 'lucide-react';
import { api } from '../services/api';
import ImageEditor from '../components/ImageEditor';

export default function ScanProduct({ onInspectionComplete }) {
  const [selectedDemo, setSelectedDemo] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [productName, setProductName] = useState('');
  const [category, setCategory] = useState('FOOD_BEVERAGE');
  const [isImported, setIsImported] = useState(false);
  const [inspectorRemarks, setInspectorRemarks] = useState('');
  const [editingFileIndex, setEditingFileIndex] = useState(null);

  const [isScanning, setIsScanning] = useState(false);
  const [scanStep, setScanStep] = useState('');
  const [scanError, setScanError] = useState('');

  const demoScenarios = [
    {
      key: 'compliant_salt',
      title: 'Tata Pure Refined Salt',
      brand: 'Tata Consumer',
      category: 'FOOD_BEVERAGE',
      is_imported: false,
      badge: 'Compliant Benchmark',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      description: '100% statutory compliance under Rule 6(1) with all declarations present and legible.',
    },
    {
      key: 'missing_mrp_snack',
      title: 'Royal Crunch Cookies',
      brand: 'Royal Bakers',
      category: 'FOOD_BEVERAGE',
      is_imported: false,
      badge: 'Missing MRP & Email',
      badgeColor: 'bg-rose-100 text-rose-800 border-rose-300',
      description: 'Violates Rule 6(1)(e) (no retail price) and Rule 6(1)(n) (missing consumer email).',
    },
    {
      key: 'ambiguous_qty',
      title: 'Natural Protein Mix',
      brand: 'FitHealth',
      category: 'FOOD_BEVERAGE',
      is_imported: false,
      badge: 'Ambiguous OCR ("500 9")',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
      description: 'Simulates common OCR misrecognition where "500 9" triggers Review Required status.',
    },
    {
      key: 'imported_earbuds',
      title: 'Aero Wireless Buds',
      brand: 'AeroTech',
      category: 'ELECTRONICS',
      is_imported: true,
      badge: 'Import Violations',
      badgeColor: 'bg-rose-100 text-rose-800 border-rose-300',
      description: 'Violates Rule 6(10) (missing Country of Origin) and Rule 6(1)(a) (missing Importer details).',
    },
    {
      key: 'warnings_spice',
      title: 'Spice Delight Masala',
      brand: 'Spice Delight',
      category: 'FOOD_BEVERAGE',
      is_imported: false,
      badge: 'Multiple Warnings',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
      description: 'Non-standard unit symbol "gms" (Rule 12) & MRP missing "incl. of all taxes" text.',
    },
  ];

  const handleSelectDemo = (demo) => {
    setSelectedDemo(demo.key);
    setUploadedFiles([]);
    setProductName(demo.title);
    setCategory(demo.category);
    setIsImported(demo.is_imported);
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setUploadedFiles(files);
      setSelectedDemo(null);
    }
  };

  const handleProcessedImage = (modifiedFile) => {
    if (editingFileIndex !== null) {
      const updated = [...uploadedFiles];
      updated[editingFileIndex] = modifiedFile;
      setUploadedFiles(updated);
      setEditingFileIndex(null);
    }
  };

  const handleExecuteScan = async () => {
    setScanError('');
    if (!selectedDemo && uploadedFiles.length === 0) {
      setScanError('Please select a sample scenario or upload at least one packaging image.');
      return;
    }

    setIsScanning(true);
    try {
      setScanStep('Executing OpenCV image preprocessing & CLAHE contrast enhancement...');
      await new Promise((r) => setTimeout(r, 600));

      setScanStep('Running Tesseract OCR engine & localizing text bounding boxes...');
      await new Promise((r) => setTimeout(r, 700));

      setScanStep('Extracting Legal Metrology statutory declarations & normalizing units...');
      await new Promise((r) => setTimeout(r, 600));

      setScanStep('Auditing findings against Legal Metrology (PC) Rules, 2011 rule engine...');
      
      const formData = new FormData();
      if (selectedDemo) {
        formData.append('demo_key', selectedDemo);
      }
      if (uploadedFiles.length > 0) {
        uploadedFiles.forEach((file) => formData.append('files', file));
      }
      formData.append('product_name', productName);
      formData.append('category', category);
      formData.append('is_imported', isImported);
      formData.append('inspector_remarks', inspectorRemarks);

      const inspectionResult = await api.scans.analyze(formData);

      setIsScanning(false);
      if (onInspectionComplete) {
        onInspectionComplete(inspectionResult.id);
      }
    } catch (err) {
      setScanError(err.message || 'Scan evaluation failed');
      setIsScanning(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500 text-doca-950 uppercase">
              Live Enforcement Scanner
            </span>
            <span className="text-xs text-slate-500">Legal Metrology Act, 2009</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight mt-1">
            Scan Packaged Commodity
          </h1>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Upload label photographs (front, back, side panels) or choose a pre-configured demo
            scenario to automatically detect and verify mandatory statutory declarations.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 px-3 py-2 rounded-xl border border-slate-200">
          <ShieldCheck className="w-4 h-4 text-doca-700 shrink-0" />
          <span>Preliminary Assessment Decision Support</span>
        </div>
      </div>

      {scanError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <XCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{scanError}</span>
        </div>
      )}

      {/* SECTION 1: 1-Click Demo Evaluation Scenarios */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>Option A: Select Realistic Sample Product Scenario</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              High-resolution synthetic packaging labels pre-rendered to test specific legal compliance outcomes
            </p>
          </div>
          {selectedDemo && (
            <button
              onClick={() => setSelectedDemo(null)}
              className="text-xs text-doca-600 font-semibold hover:underline"
            >
              Clear selection
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {demoScenarios.map((demo) => {
            const isSelected = selectedDemo === demo.key;
            return (
              <div
                key={demo.key}
                onClick={() => handleSelectDemo(demo)}
                className={`p-4 rounded-xl border-2 cursor-pointer transition flex flex-col justify-between ${
                  isSelected
                    ? 'border-amber-500 bg-amber-50/50 shadow-md ring-2 ring-amber-400/20'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-bold text-slate-900 truncate">
                      {demo.title}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${demo.badgeColor}`}
                    >
                      {demo.badge}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {demo.description}
                  </p>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] font-semibold text-slate-400">
                  <span>{demo.category.replace('_', ' ')}</span>
                  <span className={isSelected ? 'text-amber-600 font-bold' : ''}>
                    {isSelected ? '✓ Selected' : 'Click to test'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION 2: Custom Image Upload */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Upload className="w-4 h-4 text-doca-700" />
              <span>Option B: Upload Custom Packaging Photographs</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Supports multi-image scan (front label, back panel, ingredients/declarations section, or e-commerce listing)
            </p>
          </div>
        </div>

        {/* Dropzone */}
        <label
          className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition ${
            uploadedFiles.length > 0
              ? 'border-doca-500 bg-doca-50/30'
              : 'border-slate-300 hover:border-doca-400 bg-slate-50/60'
          }`}
        >
          <input
            type="file"
            multiple
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileUpload}
            className="hidden"
          />
          <div className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center text-doca-700 mb-3 border border-slate-200">
            <FileImage className="w-6 h-6" />
          </div>
          <span className="text-sm font-bold text-slate-800">
            {uploadedFiles.length > 0
              ? `${uploadedFiles.length} file(s) selected (Click to change)`
              : 'Drag and drop packaging photos here, or browse files'}
          </span>
          <span className="text-xs text-slate-400 mt-1">
            JPG, PNG, WebP up to 15MB each
          </span>
        </label>

        {/* Uploaded File List with Rotation / Orientation controls */}
        {uploadedFiles.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Selected Packaging Images:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {uploadedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between"
                >
                  <div className="flex items-center gap-2 overflow-hidden">
                    <FileImage className="w-4 h-4 text-slate-500 shrink-0" />
                    <span className="text-xs font-semibold text-slate-800 truncate">
                      {file.name}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setEditingFileIndex(idx)}
                    className="flex items-center gap-1 text-[11px] font-bold text-doca-600 hover:text-doca-800 px-2 py-1 rounded bg-white border border-slate-200 shadow-2xs"
                  >
                    <RotateCw className="w-3 h-3" />
                    <span>Rotate / Adjust</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Active Image Editor modal if rotating */}
        {editingFileIndex !== null && (
          <ImageEditor
            imageFile={uploadedFiles[editingFileIndex]}
            onProcessedImage={handleProcessedImage}
            onCancel={() => setEditingFileIndex(null)}
          />
        )}
      </div>

      {/* SECTION 3: Product Classification & Metadata */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900">
          Inspection Metadata & Commodity Classification
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Commodity / Product Name (Optional)
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g. Pure Refined Salt"
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-doca-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Commodity Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-doca-500 focus:outline-none bg-white"
            >
              <option value="FOOD_BEVERAGE">Food & Beverage</option>
              <option value="COSMETICS">Cosmetics & Personal Care</option>
              <option value="ELECTRONICS">Electronics & Electrical</option>
              <option value="HOUSEHOLD">Household & Cleansing</option>
              <option value="GENERAL">General Packaged Commodity</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Statutory Origin
            </label>
            <div className="flex items-center gap-4 mt-2">
              <label className="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
                <input
                  type="radio"
                  name="imported"
                  checked={!isImported}
                  onChange={() => setIsImported(false)}
                  className="text-doca-600 focus:ring-doca-500"
                />
                <span>Domestic</span>
              </label>
              <label className="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
                <input
                  type="radio"
                  name="imported"
                  checked={isImported}
                  onChange={() => setIsImported(true)}
                  className="text-doca-600 focus:ring-doca-500"
                />
                <span className="font-semibold text-amber-800">Imported (Rule 6(10))</span>
              </label>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Enforcement Officer Remarks (Optional)
          </label>
          <input
            type="text"
            value={inspectorRemarks}
            onChange={(e) => setInspectorRemarks(e.target.value)}
            placeholder="e.g. Label scanned at retail market inspection under Rule 6..."
            className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-doca-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Action Bar & Scanner Progress Indicator */}
      <div className="bg-slate-900 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row items-center justify-between gap-4 text-white">
        <div>
          <h4 className="text-sm font-bold text-white">
            Ready to Verify Legal Metrology Compliance
          </h4>
          <p className="text-xs text-slate-400 mt-0.5">
            Full audit against Legal Metrology (Packaged Commodities) Rules, 2011
          </p>
        </div>

        <button
          onClick={handleExecuteScan}
          disabled={isScanning}
          className="w-full md:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-extrabold text-sm bg-amber-500 text-doca-950 hover:bg-amber-400 disabled:bg-slate-700 disabled:text-slate-400 shadow-lg shadow-amber-500/20 transition transform hover:-translate-y-0.5"
        >
          {isScanning ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-doca-950 border-t-transparent rounded-full animate-spin"></div>
              <span>Processing Inspection...</span>
            </div>
          ) : (
            <>
              <ScanSearch className="w-5 h-5 text-doca-950" />
              <span>Execute Compliance Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {/* Animated Pipeline Stage Modal when scanning */}
      {isScanning && (
        <div className="p-4 rounded-xl bg-doca-900 border border-doca-700 text-white space-y-2 animate-pulse">
          <div className="flex items-center justify-between text-xs font-mono text-amber-400">
            <span>PIPELINE EXECUTION:</span>
            <span>PROCESSING</span>
          </div>
          <p className="text-xs text-slate-200 font-semibold">{scanStep}</p>
        </div>
      )}
    </div>
  );
}

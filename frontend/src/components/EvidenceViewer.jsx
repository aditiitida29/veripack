import React, { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Eye, EyeOff, Layers } from 'lucide-react';
import { SERVER_URL } from '../services/api';

export default function EvidenceViewer({
  imageUrl,
  boundingBoxes = [],
  activeRuleCode = null,
  onSelectBox = null,
}) {
  const [zoom, setZoom] = useState(1);
  const [showBoxes, setShowBoxes] = useState(true);
  const [hoveredBox, setHoveredBox] = useState(null);
  const [imgNaturalSize, setImgNaturalSize] = useState({ width: 850, height: 600 });
  const containerRef = useRef(null);

  const fullImageUrl = imageUrl
    ? imageUrl.startsWith('http')
      ? imageUrl
      : `${SERVER_URL}/${imageUrl.replace(/^\//, '')}`
    : '';

  const handleImageLoad = (e) => {
    setImgNaturalSize({
      width: e.target.naturalWidth || 850,
      height: e.target.naturalHeight || 600,
    });
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 3.0));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="bg-slate-900 rounded-2xl overflow-hidden shadow-lg border border-slate-800 flex flex-col h-full">
      {/* Viewer Toolbar */}
      <div className="bg-slate-950/80 px-4 py-2.5 flex items-center justify-between border-b border-slate-800 text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-amber-400" />
          <span className="font-semibold text-white">Visual Evidence & Packaging Overlay</span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition ${
              showBoxes ? 'bg-doca-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
            title="Toggle Bounding Box Overlays"
          >
            {showBoxes ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            <span>{showBoxes ? 'Boxes ON' : 'Boxes OFF'}</span>
          </button>

          <div className="h-4 w-px bg-slate-700 mx-1"></div>

          <button
            onClick={handleZoomIn}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <span className="text-[11px] font-mono px-1">{Math.round(zoom * 100)}%</span>
          <button
            onClick={handleZoomOut}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleResetZoom}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition"
            title="Reset Zoom"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Canvas / Image Area */}
      <div
        ref={containerRef}
        className="relative flex-1 overflow-auto bg-slate-950/40 p-4 flex items-center justify-center min-h-[420px]"
      >
        {fullImageUrl ? (
          <div
            className="relative transition-transform duration-200 origin-center"
            style={{ transform: `scale(${zoom})` }}
          >
            <img
              src={fullImageUrl}
              alt="Packaged Commodity Evidence"
              onLoad={handleImageLoad}
              className="max-w-none rounded-lg shadow-2xl block select-none"
              style={{
                width: `${imgNaturalSize.width}px`,
                height: `${imgNaturalSize.height}px`,
              }}
            />

            {/* Overlaid Bounding Boxes */}
            {showBoxes &&
              boundingBoxes.map((item, idx) => {
                const box = item.box;
                if (!box) return null;

                const isFail = item.status === 'FAIL';
                const isWarn = item.status === 'WARNING' || item.status === 'AMBIGUOUS';
                const isPass = item.status === 'PASS';
                const isSelected = activeRuleCode === item.rule_code;

                const borderColor = isFail
                  ? 'rgba(239, 68, 68, 0.9)'
                  : isWarn
                  ? 'rgba(245, 158, 11, 0.9)'
                  : 'rgba(34, 197, 94, 0.85)';

                const bgColor = isFail
                  ? 'rgba(239, 68, 68, 0.15)'
                  : isWarn
                  ? 'rgba(245, 158, 11, 0.15)'
                  : 'rgba(34, 197, 94, 0.10)';

                return (
                  <div
                    key={idx}
                    onClick={() => onSelectBox && onSelectBox(item)}
                    onMouseEnter={() => setHoveredBox(item)}
                    onMouseLeave={() => setHoveredBox(null)}
                    className={`absolute cursor-pointer transition-all border-2 rounded ${
                      isSelected ? 'ring-4 ring-amber-400 ring-offset-2 z-30 scale-105' : 'z-10'
                    }`}
                    style={{
                      left: `${box.x}px`,
                      top: `${box.y}px`,
                      width: `${box.width}px`,
                      height: `${box.height}px`,
                      borderColor: borderColor,
                      backgroundColor: bgColor,
                    }}
                  >
                    {/* Badge on box corner */}
                    <span
                      className="absolute -top-3.5 left-0 text-[10px] font-black uppercase px-1.5 py-0.5 rounded shadow text-white"
                      style={{
                        backgroundColor: isFail ? '#DC2626' : isWarn ? '#D97706' : '#16A34A',
                      }}
                    >
                      {item.field || item.rule_code}
                    </span>
                  </div>
                );
              })}
          </div>
        ) : (
          <div className="text-center text-slate-500 py-12">
            <p>No visual evidence image available</p>
          </div>
        )}
      </div>

      {/* Footer Info / Hover Details */}
      <div className="bg-slate-900 px-4 py-2 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span> Pass
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span> Review Required
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span> Violation / Fail
          </span>
        </div>

        {hoveredBox ? (
          <div className="text-amber-300 font-medium truncate max-w-sm">
            Focus: {hoveredBox.label} ({hoveredBox.status})
          </div>
        ) : (
          <span className="text-slate-500">Click a declaration box to inspect findings</span>
        )}
      </div>
    </div>
  );
}

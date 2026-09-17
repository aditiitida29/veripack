import React, { useState } from 'react';
import { RotateCw, RotateCcw, FlipHorizontal, RefreshCw } from 'lucide-react';

export default function ImageEditor({ imageFile, onProcessedImage, onCancel }) {
  const [rotation, setRotation] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const previewUrl = imageFile ? URL.createObjectURL(imageFile) : null;

  const handleRotateRight = () => setRotation((r) => (r + 90) % 360);
  const handleRotateLeft = () => setRotation((r) => (r - 90 + 360) % 360);
  const handleFlip = () => setIsFlipped((f) => !f);

  const handleApply = () => {
    if (!imageFile) return;

    // Render transformed image to offscreen canvas to produce modified Blob
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      const isSideways = rotation === 90 || rotation === 270;
      canvas.width = isSideways ? img.height : img.width;
      canvas.height = isSideways ? img.width : img.height;

      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((rotation * Math.PI) / 180);
      if (isFlipped) ctx.scale(-1, 1);
      ctx.drawImage(img, -img.width / 2, -img.height / 2);

      canvas.toBlob((blob) => {
        if (blob) {
          const newFile = new File([blob], imageFile.name, { type: imageFile.type });
          onProcessedImage(newFile);
        }
      }, imageFile.type);
    };
    img.src = previewUrl;
  };

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-bold text-slate-800">Pre-Scan Orientation & Adjustment</h4>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleRotateLeft}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100"
            title="Rotate Left 90°"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={handleRotateRight}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100"
            title="Rotate Right 90°"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleFlip}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100"
            title="Flip Horizontal"
          >
            <FlipHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center p-4 min-h-[260px] max-h-[360px]">
        {previewUrl && (
          <img
            src={previewUrl}
            alt="Adjustable Preview"
            className="max-h-[300px] object-contain transition-transform duration-200"
            style={{
              transform: `rotate(${rotation}deg) scaleX(${isFlipped ? -1 : 1})`,
            }}
          />
        )}
      </div>

      <div className="flex items-center justify-end gap-2">
        {onCancel && (
          <button
            onClick={onCancel}
            className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900"
          >
            Cancel
          </button>
        )}
        <button
          onClick={handleApply}
          className="px-4 py-1.5 text-xs font-bold bg-doca-600 text-white rounded-lg hover:bg-doca-700 shadow-sm"
        >
          Confirm Orientation
        </button>
      </div>
    </div>
  );
}

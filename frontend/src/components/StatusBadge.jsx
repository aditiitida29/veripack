import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, MinusCircle } from 'lucide-react';

export default function StatusBadge({ status, size = 'md' }) {
  const normStatus = (status || '').toUpperCase();

  const isSmall = size === 'sm';
  const isLarge = size === 'lg';

  const baseClasses = `inline-flex items-center font-bold tracking-wide rounded-full uppercase ${
    isSmall
      ? 'px-2 py-0.5 text-xs gap-1'
      : isLarge
      ? 'px-4 py-1.5 text-sm gap-2 shadow-sm'
      : 'px-2.5 py-1 text-xs gap-1.5'
  }`;

  if (normStatus === 'COMPLIANT' || normStatus === 'PASS') {
    return (
      <span className={`${baseClasses} bg-emerald-100 text-emerald-800 border border-emerald-300`}>
        <CheckCircle2 className={isSmall ? 'w-3 h-3' : isLarge ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
        {normStatus === 'PASS' ? 'Pass' : 'Compliant'}
      </span>
    );
  }

  if (normStatus === 'REVIEW_REQUIRED' || normStatus === 'WARNING' || normStatus === 'AMBIGUOUS') {
    return (
      <span className={`${baseClasses} bg-amber-100 text-amber-800 border border-amber-300`}>
        <AlertTriangle className={isSmall ? 'w-3 h-3' : isLarge ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
        {normStatus === 'WARNING' ? 'Warning' : 'Review Required'}
      </span>
    );
  }

  if (normStatus === 'NON_COMPLIANT' || normStatus === 'FAIL') {
    return (
      <span className={`${baseClasses} bg-rose-100 text-rose-800 border border-rose-300`}>
        <XCircle className={isSmall ? 'w-3 h-3' : isLarge ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
        {normStatus === 'FAIL' ? 'Violation' : 'Non-Compliant'}
      </span>
    );
  }

  return (
    <span className={`${baseClasses} bg-slate-100 text-slate-700 border border-slate-300`}>
      <MinusCircle className={isSmall ? 'w-3 h-3' : isLarge ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
      {status || 'N/A'}
    </span>
  );
}

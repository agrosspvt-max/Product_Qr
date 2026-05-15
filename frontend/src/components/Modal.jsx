import { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Modal({ open, onClose, title, children, footer = null, widthClass = 'max-w-lg' }) {
  useEffect(() => {
    function esc(e) { if (e.key === 'Escape') onClose?.(); }
    if (open) window.addEventListener('keydown', esc);
    return () => window.removeEventListener('keydown', esc);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className={`relative bg-white rounded-xl shadow-xl w-full ${widthClass}`}>
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-200">
          <h3 className="font-semibold text-slate-800">{title}</h3>
          <button className="btn-ghost p-1" onClick={onClose}><X size={18} /></button>
        </div>
        <div className="p-5">{children}</div>
        {footer && <div className="px-5 py-3 border-t border-slate-200 flex justify-end gap-2">{footer}</div>}
      </div>
    </div>
  );
}

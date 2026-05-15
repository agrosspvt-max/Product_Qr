import { Loader2 } from 'lucide-react';
import clsx from 'clsx';

export default function Loader({ label = 'Loading...', className = '' }) {
  return (
    <div className={clsx('flex items-center gap-2 text-slate-500 text-sm', className)}>
      <Loader2 className="animate-spin" size={16} />
      <span>{label}</span>
    </div>
  );
}

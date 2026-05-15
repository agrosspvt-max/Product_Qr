import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { BatchesAPI, ProductsAPI, PresetsAPI, QuantitiesAPI } from '../services/api';
import { QrCode, Boxes, Ruler, MessageSquare, ListOrdered, ArrowRight } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import Loader from '../components/Loader';

function StatCard({ icon: Icon, label, value, accent = 'brand' }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="text-2xl font-semibold text-slate-800 mt-1">{value}</p>
        </div>
        <div className={`w-10 h-10 rounded-lg bg-${accent}-50 text-${accent}-600 grid place-items-center`}>
          <Icon size={20} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const products  = useQuery({ queryKey: ['products'], queryFn: () => ProductsAPI.list() });
  const qtys      = useQuery({ queryKey: ['quantities'], queryFn: () => QuantitiesAPI.list() });
  const presets   = useQuery({ queryKey: ['presets'], queryFn: () => PresetsAPI.list() });
  const batches   = useQuery({ queryKey: ['batches'], queryFn: BatchesAPI.list });

  const loading = products.isLoading || qtys.isLoading || presets.isLoading || batches.isLoading;
  const totalCodes = (batches.data || []).reduce((s, b) => s + (b.total_codes || 0), 0);

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="Overview of QR code generation activity"
        actions={
          <Link to="/generate" className="btn-primary">
            <QrCode size={16} /> Generate Codes
          </Link>
        }
      />

      {loading ? <Loader /> : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard icon={QrCode}        label="Total Codes Generated" value={totalCodes.toLocaleString()} />
            <StatCard icon={ListOrdered}   label="Batches"               value={(batches.data || []).length} />
            <StatCard icon={Boxes}         label="Products"              value={(products.data || []).length} />
            <StatCard icon={Ruler}         label="Quantities"            value={(qtys.data || []).length} />
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-slate-800">Recent Batches</h2>
              <Link to="/batches" className="text-sm text-brand-600 inline-flex items-center gap-1">
                View all <ArrowRight size={14} />
              </Link>
            </div>
            <div className="divide-y divide-slate-100">
              {(batches.data || []).slice(0, 6).map((b) => (
                <Link
                  key={b.id}
                  to={`/batches/${b.id}`}
                  className="flex items-center justify-between py-3 hover:bg-slate-50 -mx-2 px-2 rounded-lg"
                >
                  <div>
                    <div className="font-medium text-slate-800">{b.batch_name}</div>
                    <div className="text-xs text-slate-500">
                      {b.product_name} · {b.quantity_label} · {new Date(b.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-slate-700">{b.total_codes} codes</div>
                    <div className="text-xs text-slate-500">
                      {b.zoho_synced} synced · {b.zoho_failed} failed
                    </div>
                  </div>
                </Link>
              ))}
              {(batches.data || []).length === 0 && (
                <p className="text-sm text-slate-400 py-6 text-center">No batches yet. Start by generating codes.</p>
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
}

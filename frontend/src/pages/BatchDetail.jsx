import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Download, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

import PageHeader from '../components/PageHeader';
import Loader from '../components/Loader';
import DataTable from '../components/DataTable';
import StatusBadge from '../components/StatusBadge';
import { BatchesAPI } from '../services/api';

export default function BatchDetail() {
  const { id } = useParams();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['batch', id],
    queryFn: () => BatchesAPI.get(id),
  });

  const retry = useMutation({
    mutationFn: () => BatchesAPI.retryZoho(id),
    onSuccess: (r) => {
      toast.success(`Retried ${r.retried}: ${r.synced} synced, ${r.failed} failed`);
      qc.invalidateQueries({ queryKey: ['batch', id] });
      qc.invalidateQueries({ queryKey: ['batches'] });
    },
    onError: (e) => toast.error(e?.response?.data?.detail || 'Retry failed'),
  });

  if (isLoading || !data) return <Loader />;

  return (
    <>
      <PageHeader
        title={data.batch_name}
        subtitle={`${data.total_codes.toLocaleString()} codes · ${data.zoho_synced} synced · ${data.zoho_failed} failed`}
        actions={
          <>
            <a
              className="btn-secondary"
              href={BatchesAPI.downloadExcelUrl(data.id)}
              target="_blank" rel="noreferrer"
            >
              <Download size={16} /> Download Excel
            </a>
            <button
              className="btn-primary"
              disabled={retry.isPending || data.zoho_failed === 0}
              onClick={() => retry.mutate()}
            >
              <RefreshCw size={16} /> {retry.isPending ? 'Retrying...' : 'Retry Failed'}
            </button>
          </>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total" value={data.total_codes.toLocaleString()} />
        <StatCard label="Synced" value={data.zoho_synced} tone="emerald" />
        <StatCard label="Failed" value={data.zoho_failed} tone="rose" />
        <StatCard
          label="Manufacturing"
          value={`${String(data.manufacturing_month).padStart(2,'0')}/${data.manufacturing_year}`}
        />
      </div>

      <DataTable
        rows={data.codes}
        columns={[
          { header: 'Code',        render: (r) => <span className="font-mono text-xs">{r.code}</span> },
          { header: 'Short Token', render: (r) => <span className="font-mono text-xs">{r.short_token}</span> },
          { header: 'Short Link',  render: (r) => (
              <a className="text-brand-600 underline text-xs" href={r.short_link} target="_blank" rel="noreferrer">
                {r.short_link}
              </a>
            ),
          },
          { header: 'WhatsApp', render: (r) => (
              <a className="text-brand-600 underline text-xs" href={r.whatsapp_link} target="_blank" rel="noreferrer">
                Open
              </a>
            ),
          },
          { header: 'Zoho Status', render: (r) => <StatusBadge status={r.zoho_sync_status} /> },
          { header: 'Zoho Record', render: (r) => <span className="font-mono text-xs">{r.zoho_record_id || '—'}</span> },
          { header: 'Status',      render: (r) => <StatusBadge status={r.status} /> },
        ]}
      />
    </>
  );
}

function StatCard({ label, value, tone = 'slate' }) {
  return (
    <div className="card p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`text-2xl font-semibold mt-1 text-${tone}-700`}>{value}</p>
    </div>
  );
}

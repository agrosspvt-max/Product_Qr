import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Download, Eye } from 'lucide-react';

import PageHeader from '../components/PageHeader';
import Loader from '../components/Loader';
import DataTable from '../components/DataTable';
import { BatchesAPI } from '../services/api';

export default function Batches() {
  const { data, isLoading } = useQuery({ queryKey: ['batches'], queryFn: BatchesAPI.list });

  if (isLoading) return <Loader />;

  return (
    <>
      <PageHeader title="Batches" subtitle="All generation batches" />
      <DataTable
        rows={data || []}
        empty="No batches yet."
        columns={[
          { header: 'Batch',         render: (r) => <span className="font-medium">{r.batch_name}</span> },
          { header: 'Product',       render: (r) => r.product_name || '—' },
          { header: 'Quantity',      render: (r) => r.quantity_label || '—' },
          {
            header: 'Manufacturing',
            render: (r) => r.manufacturing_month
              ? `${String(r.manufacturing_month).padStart(2,'0')}/${r.manufacturing_year}`
              : '—',
          },
          { header: 'Total',  render: (r) => r.total_codes.toLocaleString() },
          {
            header: 'Zoho',
            render: (r) => (
              <span className="text-xs">
                <span className="text-emerald-600">{r.zoho_synced} synced</span>
                {' · '}
                <span className="text-rose-600">{r.zoho_failed} failed</span>
              </span>
            ),
          },
          { header: 'Created', render: (r) => new Date(r.created_at).toLocaleString() },
          {
            header: '',
            render: (r) => (
              <div className="flex justify-end gap-2">
                <Link to={`/batches/${r.id}`} className="btn-secondary py-1 px-2"><Eye size={14} /> View</Link>
                <a
                  className="btn-secondary py-1 px-2"
                  href={BatchesAPI.downloadExcelUrl(r.id)}
                  target="_blank"
                  rel="noreferrer"
                >
                  <Download size={14} /> Excel
                </a>
              </div>
            ),
            cellClassName: 'text-right',
          },
        ]}
      />
    </>
  );
}

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Download, QrCode } from 'lucide-react';

import PageHeader from '../components/PageHeader';
import Loader from '../components/Loader';
import StatusBadge from '../components/StatusBadge';
import { BatchesAPI, GenerateAPI, PresetsAPI, ProductsAPI, QuantitiesAPI } from '../services/api';

const MONTHS = [
  ['1','Jan'],['2','Feb'],['3','Mar'],['4','Apr'],['5','May'],['6','Jun'],
  ['7','Jul'],['8','Aug'],['9','Sep'],['10','Oct'],['11','Nov'],['12','Dec'],
];
const YEARS = (() => {
  const y = new Date().getFullYear();
  return Array.from({ length: 10 }, (_, i) => y + i - 1);
})();

export default function GenerateCodes() {
  const nav = useNavigate();
  const qc = useQueryClient();
  const [result, setResult] = useState(null);

  const products = useQuery({ queryKey: ['products','active'], queryFn: () => ProductsAPI.list(true) });
  const qtys     = useQuery({ queryKey: ['quantities','active'], queryFn: () => QuantitiesAPI.list(true) });
  const presets  = useQuery({ queryKey: ['presets','active'], queryFn: () => PresetsAPI.list(true) });

  const now = new Date();
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: {
      product_id: '',
      quantity_id: '',
      whatsapp_preset_id: '',
      manufacturing_month: String(now.getMonth() + 1),
      manufacturing_year: now.getFullYear(),
      count: 100,
    },
  });

  const mutation = useMutation({
    mutationFn: (payload) => GenerateAPI.run(payload),
    onSuccess: (data) => {
      setResult(data);
      qc.invalidateQueries({ queryKey: ['batches'] });
      toast.success(`Generated ${data.total_generated} codes (${data.zoho_synced} synced).`);
    },
    onError: (err) => {
      toast.error(err?.response?.data?.detail || 'Failed to generate codes');
    },
  });

  function onSubmit(v) {
    mutation.mutate({
      product_id: Number(v.product_id),
      quantity_id: Number(v.quantity_id),
      whatsapp_preset_id: Number(v.whatsapp_preset_id),
      manufacturing_month: Number(v.manufacturing_month),
      manufacturing_year: Number(v.manufacturing_year),
      count: Number(v.count),
    });
  }

  const count = Number(watch('count') || 0);

  return (
    <>
      <PageHeader
        title="Generate Codes"
        subtitle="Generate a new batch of unique 17-character product codes"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <form onSubmit={handleSubmit(onSubmit)} className="card p-6 lg:col-span-2 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Product</label>
              <select className="input" {...register('product_id', { required: true })}>
                <option value="">— Select product —</option>
                {(products.data || []).map(p => (
                  <option key={p.id} value={p.id}>{p.name} ({p.initials})</option>
                ))}
              </select>
              {errors.product_id && <p className="text-xs text-rose-600 mt-1">Required</p>}
            </div>
            <div>
              <label className="label">Packaging</label>
              <select className="input" {...register('quantity_id', { required: true })}>
                <option value="">— Select Packaging —</option>
                {(qtys.data || []).map(q => (
                  <option key={q.id} value={q.id}>{q.label} ({q.internal_code})</option>
                ))}
              </select>
              {errors.quantity_id && <p className="text-xs text-rose-600 mt-1">Required</p>}
            </div>

            <div>
              <label className="label">Manufacturing Month</label>
              <select className="input" {...register('manufacturing_month', { required: true })}>
                {MONTHS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Manufacturing Year</label>
              <select className="input" {...register('manufacturing_year', { required: true })}>
                {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="label">WhatsApp Preset</label>
              <select className="input" {...register('whatsapp_preset_id', { required: true })}>
                <option value="">— Select preset —</option>
                {(presets.data || []).map(p => (
                  <option key={p.id} value={p.id}>
                    {p.preset_name} — {p.whatsapp_number}{p.is_default ? ' (default)' : ''}
                  </option>
                ))}
              </select>
              {errors.whatsapp_preset_id && <p className="text-xs text-rose-600 mt-1">Required</p>}
            </div>

            <div className="sm:col-span-2">
              <label className="label">Number of Codes</label>
              <input
                type="number"
                className="input"
                min={1}
                max={100000}
                {...register('count', { required: true, min: 1, max: 100000, valueAsNumber: true })}
              />
              <p className="text-xs text-slate-400 mt-1">Max 100,000 per batch.</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <p className="text-xs text-slate-500">
              {count > 0 ? `Will generate ${count.toLocaleString()} unique codes.` : ''}
            </p>
            <button className="btn-primary" type="submit" disabled={mutation.isPending}>
              <QrCode size={16} /> {mutation.isPending ? 'Generating...' : 'Generate Codes'}
            </button>
          </div>
        </form>

        <div className="card p-6">
          <h3 className="font-semibold text-slate-800 mb-3">Result</h3>
          {!result && !mutation.isPending && (
            <p className="text-sm text-slate-400">Run a generation to see the summary here.</p>
          )}
          {mutation.isPending && <Loader label="Generating + pushing to Zoho..." />}
          {result && (
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Batch</span><span className="font-medium">{result.batch_name}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Generated</span><span>{result.total_generated} / {result.total_requested}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Zoho synced</span><StatusBadge status="SYNCED" /></div>
              <div className="flex justify-between"><span className="text-slate-500">Count synced</span><span>{result.zoho_synced}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Count failed</span><span>{result.zoho_failed}</span></div>
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <a
                  className="btn-secondary w-full"
                  href={BatchesAPI.downloadExcelUrl(result.batch_id)}
                  target="_blank"
                  rel="noreferrer"
                >
                  <Download size={16} /> Download Excel
                </a>
                <button className="btn-primary w-full" onClick={() => nav(`/batches/${result.batch_id}`)}>
                  View Batch
                </button>
              </div>
              <div className="pt-3">
                <p className="text-xs text-slate-500 mb-1">Sample codes:</p>
                <div className="space-y-1">
                  {(result.sample_codes || []).map((c) => (
                    <div key={c} className="font-mono text-xs bg-slate-50 px-2 py-1 rounded">{c}</div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

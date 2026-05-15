import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Save } from 'lucide-react';

import PageHeader from '../components/PageHeader';
import Loader from '../components/Loader';
import { SettingsAPI } from '../services/api';

export default function ZohoSettings() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['settings','zoho'], queryFn: SettingsAPI.getZoho });
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => { if (data) reset(data); }, [data, reset]);

  const save = useMutation({
    mutationFn: SettingsAPI.saveZoho,
    onSuccess: () => { toast.success('Saved'); qc.invalidateQueries({ queryKey: ['settings','zoho'] }); },
    onError: (e) => toast.error(e?.response?.data?.detail || 'Save failed'),
  });

  if (isLoading) return <Loader />;

  return (
    <>
      <PageHeader title="Zoho Settings" subtitle="OAuth credentials and module configuration" />
      <form onSubmit={handleSubmit((v) => save.mutate(v))} className="card p-6 max-w-2xl space-y-4">
        {[
          { name: 'client_id',         label: 'Client ID',         required: true },
          { name: 'client_secret',     label: 'Client Secret',     required: true, type: 'password' },
          { name: 'refresh_token',     label: 'Refresh Token',     required: true, type: 'password' },
          { name: 'organization_id',   label: 'Organization ID' },
          { name: 'api_domain',        label: 'API Domain',        required: true, placeholder: 'https://www.zohoapis.com' },
          { name: 'module_name',       label: 'Module Name',       required: true, placeholder: 'Product_QR' },
        ].map((f) => (
          <div key={f.name}>
            <label className="label">{f.label}{f.required && ' *'}</label>
            <input
              type={f.type || 'text'}
              className="input font-mono text-sm"
              placeholder={f.placeholder}
              {...register(f.name, f.required ? { required: 'Required' } : {})}
            />
            {errors[f.name] && <p className="text-xs text-rose-600 mt-1">{errors[f.name].message}</p>}
          </div>
        ))}
        <div className="pt-2">
          <button className="btn-primary" disabled={save.isPending}>
            <Save size={16} /> {save.isPending ? 'Saving...' : 'Save Zoho Settings'}
          </button>
        </div>
        <p className="text-xs text-slate-400">
          Tip: Generate a Self-Client token in <a href="https://api-console.zoho.com" className="text-brand-600 underline" target="_blank" rel="noreferrer">Zoho API Console</a> with scope
          {' '}<code>ZohoCRM.modules.ALL,ZohoCRM.settings.ALL</code> and exchange the code for a refresh token.
        </p>
      </form>
    </>
  );
}

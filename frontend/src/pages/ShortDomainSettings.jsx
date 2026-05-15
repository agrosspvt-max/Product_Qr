import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Save } from 'lucide-react';

import PageHeader from '../components/PageHeader';
import Loader from '../components/Loader';
import { SettingsAPI } from '../services/api';

export default function ShortDomainSettings() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['settings','short'], queryFn: SettingsAPI.getShortDomain });
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => { if (data) reset(data); }, [data, reset]);

  const save = useMutation({
    mutationFn: SettingsAPI.saveShortDomain,
    onSuccess: () => { toast.success('Saved'); qc.invalidateQueries({ queryKey: ['settings','short'] }); },
    onError: (e) => toast.error(e?.response?.data?.detail || 'Save failed'),
  });

  if (isLoading) return <Loader />;

  return (
    <>
      <PageHeader title="Short Domain" subtitle="Public domain used in QR redirect URLs" />
      <form onSubmit={handleSubmit((v) => save.mutate(v))} className="card p-6 max-w-xl space-y-4">
        <div>
          <label className="label">Short Domain URL</label>
          <input
            className="input font-mono"
            placeholder="https://qr.company.com"
            {...register('short_domain', {
              required: 'Required',
              pattern: { value: /^https?:\/\/[^\s]+$/, message: 'Must be a valid URL' },
            })}
          />
          {errors.short_domain && <p className="text-xs text-rose-600 mt-1">{errors.short_domain.message}</p>}
          <p className="text-xs text-slate-400 mt-2">
            Example: <code>https://qr.company.com</code>. Resulting short links:{' '}
            <code>https://qr.company.com/AB12C</code>
          </p>
        </div>
        <button className="btn-primary" disabled={save.isPending}>
          <Save size={16} /> {save.isPending ? 'Saving...' : 'Save'}
        </button>
      </form>
    </>
  );
}

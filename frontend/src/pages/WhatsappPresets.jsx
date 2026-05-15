import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Pencil, Plus, Trash2, Star } from 'lucide-react';

import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import Loader from '../components/Loader';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { PresetsAPI } from '../services/api';

export default function WhatsappPresets() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['presets','all'], queryFn: () => PresetsAPI.list() });
  const [editing, setEditing] = useState(null);
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const openCreate = () => { reset({ preset_name: '', whatsapp_number: '', is_default: false, is_active: true }); setEditing({}); };
  const openEdit = (row) => { reset({ ...row }); setEditing(row); };

  const save = useMutation({
    mutationFn: (v) => editing.id ? PresetsAPI.update(editing.id, v) : PresetsAPI.create(v),
    onSuccess: () => { toast.success('Saved'); qc.invalidateQueries({ queryKey: ['presets'] }); setEditing(null); },
    onError: (e) => toast.error(e?.response?.data?.detail || 'Save failed'),
  });
  const remove = useMutation({
    mutationFn: (id) => PresetsAPI.remove(id),
    onSuccess: () => { toast.success('Deactivated'); qc.invalidateQueries({ queryKey: ['presets'] }); },
  });
  const setDefault = useMutation({
    mutationFn: (id) => PresetsAPI.update(id, { is_default: true }),
    onSuccess: () => { toast.success('Default updated'); qc.invalidateQueries({ queryKey: ['presets'] }); },
  });

  return (
    <>
      <PageHeader
        title="WhatsApp Presets"
        subtitle="Phone numbers used for QR-link redirects"
        actions={<button className="btn-primary" onClick={openCreate}><Plus size={16} /> Add Preset</button>}
      />

      {isLoading ? <Loader /> : (
        <DataTable
          rows={data || []}
          columns={[
            { header: 'Name',   render: (r) => (
                <span className="font-medium">
                  {r.preset_name} {r.is_default && <Star size={12} className="inline text-amber-500 ml-1" />}
                </span>
              ),
            },
            { header: 'WhatsApp Number', render: (r) => <span className="font-mono">{r.whatsapp_number}</span> },
            { header: 'Status',          render: (r) => <StatusBadge status={r.is_active ? 'SYNCED' : 'FAILED'} /> },
            { header: 'Default',         render: (r) => r.is_default ? 'Yes' : 'No' },
            {
              header: '', cellClassName: 'text-right',
              render: (r) => (
                <div className="flex justify-end gap-2">
                  {!r.is_default && (
                    <button className="btn-secondary py-1 px-2" onClick={() => setDefault.mutate(r.id)}>
                      <Star size={14} /> Default
                    </button>
                  )}
                  <button className="btn-secondary py-1 px-2" onClick={() => openEdit(r)}><Pencil size={14} /></button>
                  <button className="btn-danger py-1 px-2" onClick={() => remove.mutate(r.id)}><Trash2 size={14} /></button>
                </div>
              ),
            },
          ]}
        />
      )}

      <Modal
        open={editing !== null}
        onClose={() => setEditing(null)}
        title={editing?.id ? 'Edit Preset' : 'Add Preset'}
        footer={
          <>
            <button className="btn-secondary" onClick={() => setEditing(null)}>Cancel</button>
            <button className="btn-primary" onClick={handleSubmit((v) => save.mutate(v))} disabled={save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </button>
          </>
        }
      >
        <form className="space-y-4">
          <div>
            <label className="label">Preset name</label>
            <input className="input" {...register('preset_name', { required: 'Required' })} />
            {errors.preset_name && <p className="text-xs text-rose-600 mt-1">{errors.preset_name.message}</p>}
          </div>
          <div>
            <label className="label">WhatsApp number (digits only, with country code)</label>
            <input
              className="input font-mono"
              placeholder="919999999999"
              {...register('whatsapp_number', {
                required: 'Required',
                pattern: { value: /^\d{8,15}$/, message: '8–15 digits, no + or spaces' },
              })}
            />
            {errors.whatsapp_number && <p className="text-xs text-rose-600 mt-1">{errors.whatsapp_number.message}</p>}
          </div>
          <div className="flex items-center gap-6 text-sm">
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" {...register('is_default')} className="rounded border-slate-300" />
              Default
            </label>
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" {...register('is_active')} className="rounded border-slate-300" />
              Active
            </label>
          </div>
        </form>
      </Modal>
    </>
  );
}

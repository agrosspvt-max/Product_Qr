import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Pencil, Plus, Trash2 } from 'lucide-react';

import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import Loader from '../components/Loader';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import { ProductsAPI } from '../services/api';

export default function Products() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['products','all'], queryFn: () => ProductsAPI.list() });

  const [editing, setEditing] = useState(null); // null | {} | row
  const isOpen = editing !== null;
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const openCreate = () => { reset({ name: '', initials: '', is_active: true }); setEditing({}); };
  const openEdit = (row) => { reset({ name: row.name, initials: row.initials, is_active: row.is_active }); setEditing(row); };

  const save = useMutation({
    mutationFn: (v) => editing.id ? ProductsAPI.update(editing.id, v) : ProductsAPI.create(v),
    onSuccess: () => {
      toast.success('Saved');
      qc.invalidateQueries({ queryKey: ['products'] });
      setEditing(null);
    },
    onError: (e) => toast.error(e?.response?.data?.detail || 'Save failed'),
  });

  const remove = useMutation({
    mutationFn: (id) => ProductsAPI.remove(id),
    onSuccess: () => { toast.success('Deactivated'); qc.invalidateQueries({ queryKey: ['products'] }); },
    onError: (e) => toast.error(e?.response?.data?.detail || 'Delete failed'),
  });

  return (
    <>
      <PageHeader
        title="Products"
        subtitle="Manage product list and initials"
        actions={<button className="btn-primary" onClick={openCreate}><Plus size={16} /> Add Product</button>}
      />

      {isLoading ? <Loader /> : (
        <DataTable
          rows={data || []}
          columns={[
            { header: 'Name',     render: (r) => <span className="font-medium">{r.name}</span> },
            { header: 'Initials', render: (r) => <span className="font-mono">{r.initials}</span> },
            { header: 'Status',   render: (r) => <StatusBadge status={r.is_active ? 'SYNCED' : 'FAILED'} /> },
            { header: 'Created',  render: (r) => new Date(r.created_at).toLocaleDateString() },
            {
              header: '', cellClassName: 'text-right',
              render: (r) => (
                <div className="flex justify-end gap-2">
                  <button className="btn-secondary py-1 px-2" onClick={() => openEdit(r)}><Pencil size={14} /></button>
                  <button className="btn-danger py-1 px-2" onClick={() => remove.mutate(r.id)}><Trash2 size={14} /></button>
                </div>
              ),
            },
          ]}
        />
      )}

      <Modal
        open={isOpen}
        onClose={() => setEditing(null)}
        title={editing?.id ? 'Edit Product' : 'Add Product'}
        footer={
          <>
            <button className="btn-secondary" onClick={() => setEditing(null)}>Cancel</button>
            <button className="btn-primary" onClick={handleSubmit((v) => save.mutate(v))} disabled={save.isPending}>
              {save.isPending ? 'Saving...' : 'Save'}
            </button>
          </>
        }
      >
        <form className="space-y-4" onSubmit={handleSubmit((v) => save.mutate(v))}>
          <div>
            <label className="label">Name</label>
            <input className="input" {...register('name', { required: 'Required' })} />
            {errors.name && <p className="text-xs text-rose-600 mt-1">{errors.name.message}</p>}
          </div>
          <div>
            <label className="label">Initials (2 chars)</label>
            <input
              className="input uppercase font-mono"
              maxLength={4}
              {...register('initials', {
                required: 'Required',
                pattern: { value: /^[A-Za-z0-9]{2,4}$/, message: '2–4 uppercase A-Z / 0-9' },
              })}
            />
            {errors.initials && <p className="text-xs text-rose-600 mt-1">{errors.initials.message}</p>}
          </div>
          <label className="inline-flex items-center gap-2 text-sm">
            <input type="checkbox" {...register('is_active')} className="rounded border-slate-300" />
            Active
          </label>
        </form>
      </Modal>
    </>
  );
}

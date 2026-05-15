import { useState } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Pencil, Plus, Trash2 } from "lucide-react";

import PageHeader from "../components/PageHeader";
import DataTable from "../components/DataTable";
import Loader from "../components/Loader";
import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";
import { QuantitiesAPI } from "../services/api";

export default function Quantities() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["quantities", "all"],
    queryFn: () => QuantitiesAPI.list(),
  });
  const [editing, setEditing] = useState(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  const openCreate = () => {
    reset({ label: "", internal_code: "", is_active: true });
    setEditing({});
  };
  const openEdit = (row) => {
    reset({ ...row });
    setEditing(row);
  };

  const save = useMutation({
    mutationFn: (v) =>
      editing.id
        ? QuantitiesAPI.update(editing.id, v)
        : QuantitiesAPI.create(v),
    onSuccess: () => {
      toast.success("Saved");
      qc.invalidateQueries({ queryKey: ["quantities"] });
      setEditing(null);
    },
    onError: (e) => toast.error(e?.response?.data?.detail || "Save failed"),
  });
  const remove = useMutation({
    mutationFn: (id) => QuantitiesAPI.remove(id),
    onSuccess: () => {
      toast.success("Deactivated");
      qc.invalidateQueries({ queryKey: ["quantities"] });
    },
    onError: (e) => toast.error(e?.response?.data?.detail || "Delete failed"),
  });

  return (
    <>
      <PageHeader
        title="Packaging"
        subtitle="Manage size / volume codes (must be exactly 4 chars)"
        actions={
          <button className="btn-primary" onClick={openCreate}>
            <Plus size={16} /> Add Packaging
          </button>
        }
      />

      {isLoading ? (
        <Loader />
      ) : (
        <DataTable
          rows={data || []}
          columns={[
            {
              header: "Label",
              render: (r) => <span className="font-medium">{r.label}</span>,
            },
            {
              header: "Internal Code",
              render: (r) => (
                <span className="font-mono">{r.internal_code}</span>
              ),
            },
            {
              header: "Status",
              render: (r) => (
                <StatusBadge status={r.is_active ? "SYNCED" : "FAILED"} />
              ),
            },
            {
              header: "Created",
              render: (r) => new Date(r.created_at).toLocaleDateString(),
            },
            {
              header: "",
              cellClassName: "text-right",
              render: (r) => (
                <div className="flex justify-end gap-2">
                  <button
                    className="btn-secondary py-1 px-2"
                    onClick={() => openEdit(r)}
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    className="btn-danger py-1 px-2"
                    onClick={() => remove.mutate(r.id)}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ),
            },
          ]}
        />
      )}

      <Modal
        open={editing !== null}
        onClose={() => setEditing(null)}
        title={editing?.id ? "Edit Quantity" : "Add Quantity"}
        footer={
          <>
            <button className="btn-secondary" onClick={() => setEditing(null)}>
              Cancel
            </button>
            <button
              className="btn-primary"
              onClick={handleSubmit((v) => save.mutate(v))}
              disabled={save.isPending}
            >
              {save.isPending ? "Saving..." : "Save"}
            </button>
          </>
        }
      >
        <form className="space-y-4">
          <div>
            <label className="label">Packaging (e.g. 1L, 500ml)</label>
            <input
              className="input"
              {...register("label", { required: "Required" })}
            />
            {errors.label && (
              <p className="text-xs text-rose-600 mt-1">
                {errors.label.message}
              </p>
            )}
          </div>
          <div>
            <label className="label">Internal Code (exactly 4 chars)</label>
            <input
              className="input uppercase font-mono"
              maxLength={4}
              {...register("internal_code", {
                required: "Required",
                pattern: {
                  value: /^[A-Za-z0-9]{4}$/,
                  message: "Must be exactly 4 alphanumeric chars",
                },
              })}
            />
            {errors.internal_code && (
              <p className="text-xs text-rose-600 mt-1">
                {errors.internal_code.message}
              </p>
            )}
          </div>
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              {...register("is_active")}
              className="rounded border-slate-300"
            />
            Active
          </label>
        </form>
      </Modal>
    </>
  );
}

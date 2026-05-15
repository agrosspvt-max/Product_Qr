export default function StatusBadge({ status }) {
  const map = {
    SYNCED:  'badge-green',
    PENDING: 'badge-amber',
    FAILED:  'badge-red',
    UNUSED:  'badge-slate',
    USED:    'badge-green',
  };
  const cls = map[status] || 'badge-slate';
  return <span className={cls}>{status}</span>;
}

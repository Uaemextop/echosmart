import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTenantStore } from '../../store/tenantStore';
import type { Tenant } from '../../types';

const PAGE_SIZE = 10;

export default function TenantList() {
  const { tenants, total, isLoading, fetchTenants, deleteTenant } = useTenantStore();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    const filter: Record<string, string> = {};
    if (search) filter.search = search;
    if (planFilter) filter.plan = planFilter;
    if (statusFilter) filter.status = statusFilter;
    fetchTenants(page, filter);
  }, [page, search, planFilter, statusFilter, fetchTenants]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleDelete = async (id: string) => {
    await deleteTenant(id);
    setDeleteConfirm(null);
    fetchTenants(page);
  };

  const statusBadge = (status: Tenant['status']) => {
    const cls =
      status === 'active'
        ? 'bg-green-100 text-green-700'
        : status === 'suspended'
        ? 'bg-yellow-100 text-yellow-700'
        : 'bg-red-100 text-red-700';
    return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>{status}</span>;
  };

  const planBadge = (plan: Tenant['plan']) => {
    const cls =
      plan === 'enterprise'
        ? 'bg-purple-100 text-purple-700'
        : plan === 'pro'
        ? 'bg-blue-100 text-blue-700'
        : 'bg-gray-100 text-gray-600';
    return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>{plan}</span>;
  };

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Tenants</h1>
        <button
          onClick={() => navigate('/admin/tenants/create')}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
        >
          + New Tenant
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search by name…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
        />
        <select
          value={planFilter}
          onChange={(e) => { setPlanFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
        >
          <option value="">All Plans</option>
          <option value="basic">Basic</option>
          <option value="pro">Pro</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="suspended">Suspended</option>
          <option value="deleted">Deleted</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Name', 'Plan', 'Status', 'Sensors', 'Users', 'Created', 'Actions'].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-gray-500 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading
              ? [...Array(5)].map((_, i) => (
                  <tr key={i}>
                    {[...Array(7)].map((__, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 bg-gray-100 rounded animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              : tenants.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{t.name}</td>
                    <td className="px-4 py-3">{planBadge(t.plan)}</td>
                    <td className="px-4 py-3">{statusBadge(t.status)}</td>
                    <td className="px-4 py-3 text-gray-600">{t.maxSensors}</td>
                    <td className="px-4 py-3 text-gray-600">{t.maxUsers}</td>
                    <td className="px-4 py-3 text-gray-400">
                      {new Date(t.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => navigate(`/admin/tenants/${t.id}`)}
                          className="text-blue-600 hover:underline text-xs"
                        >
                          View
                        </button>
                        <button
                          onClick={() => navigate(`/admin/tenants/${t.id}/edit`)}
                          className="text-green-600 hover:underline text-xs"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(t.id)}
                          className="text-red-500 hover:underline text-xs"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center gap-2 justify-end">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1 border rounded text-sm disabled:opacity-40"
          >
            Prev
          </button>
          <span className="text-sm text-gray-500">
            {page} / {totalPages}
          </span>
          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1 border rounded text-sm disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}

      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Delete Tenant?</h3>
            <p className="text-gray-500 text-sm">This will soft-delete the tenant. This action can be reversed by an admin.</p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setDeleteConfirm(null)} className="px-4 py-2 border rounded-lg text-sm">
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="px-4 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

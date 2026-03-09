import { useEffect, useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { alertApi, sensorApi } from '../../services/api';
import type { AlertRule, Sensor } from '../../types';

const ruleSchema = z.object({
  name: z.string().min(1, 'Name required'),
  sensor_id: z.string().optional(),
  severity: z.enum(['info', 'warning', 'critical']),
  hysteresis_count: z.coerce.number().int().min(1),
  time_window_start: z.string().optional(),
  time_window_end: z.string().optional(),
  is_active: z.boolean(),
  leaf_field: z.string().min(1, 'Field required'),
  leaf_op: z.enum(['>', '<', '>=', '<=', '==', '!=']),
  leaf_value: z.coerce.number(),
  extra_conditions: z.array(z.object({
    field: z.string(),
    op: z.enum(['>', '<', '>=', '<=', '==', '!=']),
    value: z.coerce.number(),
  })).optional(),
  logic_operator: z.enum(['AND', 'OR']),
});

type RuleForm = z.infer<typeof ruleSchema>;

export default function AlertRules() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { register, handleSubmit, reset, control, formState: { errors } } = useForm<RuleForm>({
    resolver: zodResolver(ruleSchema),
    defaultValues: { severity: 'warning', hysteresis_count: 1, is_active: true, leaf_op: '>', logic_operator: 'AND', extra_conditions: [] },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'extra_conditions' });

  const load = async () => {
    setIsLoading(true);
    try {
      const [r, s] = await Promise.all([alertApi.list(), sensorApi.list()]);
      setRules(Array.isArray(r) ? r : []);
      setSensors(Array.isArray(s) ? s : []);
    } catch { /* ignore */ }
    setIsLoading(false);
  };

  useEffect(() => { load(); }, []);

  const onSubmit = async (data: RuleForm) => {
    const allConditions = [
      { field: data.leaf_field, op: data.leaf_op, value: data.leaf_value },
      ...(data.extra_conditions || []),
    ];
    const conditions = allConditions.length === 1 ? { operator: 'AND', conditions: allConditions } : { operator: data.logic_operator, conditions: allConditions };
    const payload = {
      name: data.name,
      sensor_id: data.sensor_id || undefined,
      severity: data.severity,
      hysteresis_count: data.hysteresis_count,
      time_window_start: data.time_window_start || null,
      time_window_end: data.time_window_end || null,
      is_active: data.is_active,
      conditions,
    };
    try {
      if (editingId) {
        await alertApi.update(editingId, payload);
      } else {
        await alertApi.create(payload);
      }
      setIsOpen(false);
      setEditingId(null);
      reset();
      load();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    await alertApi.remove(id);
    setDeleteConfirm(null);
    load();
  };

  const severityBadge = (s: AlertRule['severity']) => {
    const cls = s === 'critical' ? 'bg-red-100 text-red-700' : s === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700';
    return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>{s}</span>;
  };

  return (
    <div className="p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Alert Rules</h1>
        <button
          onClick={() => { setIsOpen(true); setEditingId(null); reset(); }}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
        >
          + New Rule
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              {['Name', 'Sensor', 'Severity', 'Hysteresis', 'Active', 'Actions'].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-gray-500 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading
              ? [...Array(3)].map((_, i) => (
                  <tr key={i}>{[...Array(6)].map((__, j) => <td key={j} className="px-4 py-3"><div className="h-4 bg-gray-100 rounded animate-pulse" /></td>)}</tr>
                ))
              : rules.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{r.name}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{r.sensorId ? r.sensorId.slice(0, 8) + '…' : 'All'}</td>
                    <td className="px-4 py-3">{severityBadge(r.severity)}</td>
                    <td className="px-4 py-3 text-gray-600">{r.hysteresisCount}x</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs ${r.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                        {r.isActive ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => setDeleteConfirm(r.id)} className="text-red-500 hover:underline text-xs">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {isOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 space-y-4">
              <h3 className="text-lg font-semibold">{editingId ? 'Edit' : 'Create'} Alert Rule</h3>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rule Name</label>
                  <input {...register('name')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                  {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name.message}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sensor (optional)</label>
                  <select {...register('sensor_id')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                    <option value="">All sensors</option>
                    {sensors.map((s) => <option key={s.id} value={s.id}>{s.uuid}</option>)}
                  </select>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Field</label>
                    <input {...register('leaf_field')} placeholder="temperature" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                    {errors.leaf_field && <p className="text-xs text-red-500 mt-1">{errors.leaf_field.message}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Op</label>
                    <select {...register('leaf_op')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                      {['>', '<', '>=', '<=', '==', '!='].map((op) => <option key={op}>{op}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                    <input {...register('leaf_value')} type="number" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                  </div>
                </div>

                {fields.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Logic</label>
                    <select {...register('logic_operator')} className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                      <option>AND</option>
                      <option>OR</option>
                    </select>
                  </div>
                )}

                {fields.map((f, i) => (
                  <div key={f.id} className="grid grid-cols-3 gap-2 items-end">
                    <input {...register(`extra_conditions.${i}.field`)} placeholder="field" className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                    <select {...register(`extra_conditions.${i}.op`)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                      {['>', '<', '>=', '<=', '==', '!='].map((op) => <option key={op}>{op}</option>)}
                    </select>
                    <div className="flex gap-1">
                      <input {...register(`extra_conditions.${i}.value`)} type="number" className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                      <button type="button" onClick={() => remove(i)} className="text-red-500 text-xs px-2">✕</button>
                    </div>
                  </div>
                ))}

                <button type="button" onClick={() => append({ field: '', op: '>', value: 0 })} className="text-sm text-green-600 hover:underline">
                  + Add condition
                </button>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                    <select {...register('severity')} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                      <option value="info">Info</option>
                      <option value="warning">Warning</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Hysteresis</label>
                    <input {...register('hysteresis_count')} type="number" min="1" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Window Start</label>
                    <input {...register('time_window_start')} type="time" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Window End</label>
                    <input {...register('time_window_end')} type="time" className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                  </div>
                </div>

                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register('is_active')} className="rounded" />
                  Active
                </label>

                <div className="flex justify-end gap-3 pt-2">
                  <button type="button" onClick={() => setIsOpen(false)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
                  <button type="submit" className="px-5 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium">Save</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl space-y-4">
            <h3 className="text-lg font-semibold">Delete Rule?</h3>
            <p className="text-gray-500 text-sm">The rule will be permanently deactivated and removed from evaluation.</p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setDeleteConfirm(null)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button onClick={() => handleDelete(deleteConfirm)} className="px-4 py-2 bg-red-500 text-white rounded-lg text-sm">Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

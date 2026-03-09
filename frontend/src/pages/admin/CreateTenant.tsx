import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTenantStore } from '../../store/tenantStore';

const step1Schema = z.object({
  company_name: z.string().min(2, 'Company name required'),
  name: z.string().min(2, 'Tenant name required'),
  email: z.string().email('Valid email required'),
  password: z.string().min(8, 'Minimum 8 characters'),
});

const step2Schema = z.object({
  plan: z.enum(['basic', 'pro', 'enterprise']),
  max_sensors: z.coerce.number().int().min(1),
  max_users: z.coerce.number().int().min(1),
});

type Step1Form = z.infer<typeof step1Schema>;
type Step2Form = z.infer<typeof step2Schema>;

const planDetails = {
  basic: { label: 'Basic', price: 'Free', features: ['10 sensors', '5 users', 'Email alerts'], defaultSensors: 10, defaultUsers: 5 },
  pro: { label: 'Pro', price: '$49/mo', features: ['50 sensors', '25 users', 'Email + WhatsApp', 'Analytics'], defaultSensors: 50, defaultUsers: 25 },
  enterprise: { label: 'Enterprise', price: 'Custom', features: ['500 sensors', '200 users', 'All channels', 'Priority support', 'SLA'], defaultSensors: 500, defaultUsers: 200 },
};

export default function CreateTenant() {
  const navigate = useNavigate();
  const { createTenant } = useTenantStore();
  const [step, setStep] = useState(1);
  const [step1Data, setStep1Data] = useState<Step1Form | null>(null);
  const [step2Data, setStep2Data] = useState<Step2Form | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const form1 = useForm<Step1Form>({ resolver: zodResolver(step1Schema) });
  const form2 = useForm<Step2Form>({
    resolver: zodResolver(step2Schema),
    defaultValues: { plan: 'basic', max_sensors: 10, max_users: 5 },
  });

  const watchedPlan = form2.watch('plan');

  const onStep1Submit = (data: Step1Form) => {
    setStep1Data(data);
    setStep(2);
  };

  const onStep2Submit = (data: Step2Form) => {
    setStep2Data(data);
    setStep(3);
  };

  const onConfirm = async () => {
    if (!step1Data || !step2Data) return;
    setIsSubmitting(true);
    setError('');
    try {
      await createTenant({ ...step1Data, ...step2Data });
      navigate('/admin/tenants');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create tenant';
      setError(msg);
    }
    setIsSubmitting(false);
  };

  const steps = ['Org Info', 'Plan & Limits', 'Confirm'];

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Create New Tenant</h1>

      {/* Progress */}
      <div className="flex items-center gap-2">
        {steps.map((label, i) => (
          <div key={label} className="flex items-center gap-2 flex-1">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                i + 1 <= step ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'
              }`}
            >
              {i + 1}
            </div>
            <span className={`text-sm ${i + 1 <= step ? 'text-green-600 font-medium' : 'text-gray-400'}`}>
              {label}
            </span>
            {i < steps.length - 1 && <div className={`h-0.5 flex-1 ${i + 1 < step ? 'bg-green-400' : 'bg-gray-200'}`} />}
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {step === 1 && (
          <form onSubmit={form1.handleSubmit(onStep1Submit)} className="space-y-4">
            <h2 className="text-lg font-semibold">Organisation Information</h2>
            {(['company_name', 'name', 'email', 'password'] as const).map((field) => (
              <div key={field}>
                <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                  {field.replace('_', ' ')}
                </label>
                <input
                  {...form1.register(field)}
                  type={field === 'password' ? 'password' : field === 'email' ? 'email' : 'text'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                />
                {form1.formState.errors[field] && (
                  <p className="mt-1 text-xs text-red-500">{form1.formState.errors[field]?.message}</p>
                )}
              </div>
            ))}
            <div className="flex justify-end">
              <button type="submit" className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium">
                Next
              </button>
            </div>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={form2.handleSubmit(onStep2Submit)} className="space-y-5">
            <h2 className="text-lg font-semibold">Plan & Limits</h2>
            <div className="grid grid-cols-3 gap-3">
              {(Object.entries(planDetails) as [keyof typeof planDetails, typeof planDetails.basic][]).map(([key, p]) => (
                <label
                  key={key}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                    watchedPlan === key ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    {...form2.register('plan')}
                    value={key}
                    className="sr-only"
                    onChange={() => {
                      form2.setValue('plan', key);
                      form2.setValue('max_sensors', p.defaultSensors);
                      form2.setValue('max_users', p.defaultUsers);
                    }}
                  />
                  <p className="font-bold text-gray-900">{p.label}</p>
                  <p className="text-green-600 font-semibold text-sm mt-1">{p.price}</p>
                  <ul className="mt-2 space-y-1">
                    {p.features.map((f) => (
                      <li key={f} className="text-xs text-gray-500">✓ {f}</li>
                    ))}
                  </ul>
                </label>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Sensors</label>
                <input
                  {...form2.register('max_sensors')}
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Users</label>
                <input
                  {...form2.register('max_users')}
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
              </div>
            </div>
            <div className="flex justify-between">
              <button type="button" onClick={() => setStep(1)} className="px-4 py-2 border rounded-lg text-sm">
                Back
              </button>
              <button type="submit" className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium">
                Next
              </button>
            </div>
          </form>
        )}

        {step === 3 && step1Data && step2Data && (
          <div className="space-y-5">
            <h2 className="text-lg font-semibold">Confirm & Create</h2>
            {error && <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">{error}</div>}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
              <p><span className="font-medium">Company:</span> {step1Data.company_name}</p>
              <p><span className="font-medium">Tenant:</span> {step1Data.name}</p>
              <p><span className="font-medium">Email:</span> {step1Data.email}</p>
              <p><span className="font-medium">Plan:</span> {step2Data.plan}</p>
              <p><span className="font-medium">Max Sensors:</span> {step2Data.max_sensors}</p>
              <p><span className="font-medium">Max Users:</span> {step2Data.max_users}</p>
            </div>
            <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
              📧 A verification email will be sent to <strong>{step1Data.email}</strong> after creation.
            </div>
            <div className="flex justify-between">
              <button type="button" onClick={() => setStep(2)} className="px-4 py-2 border rounded-lg text-sm">
                Back
              </button>
              <button
                onClick={onConfirm}
                disabled={isSubmitting}
                className="px-6 py-2 bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white rounded-lg font-medium"
              >
                {isSubmitting ? 'Creating…' : 'Create Tenant'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

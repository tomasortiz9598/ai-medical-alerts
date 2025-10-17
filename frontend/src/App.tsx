import { useMemo, useState } from 'react';
import dayjs from 'dayjs';
import { useAlerts } from './hooks/useAlerts';
import { Alert } from './types';
import { FileUpload } from './components/FileUpload';
import { AlertList } from './components/AlertList';

const urgencySortOrder = ['High', 'Medium', 'Low'] as const;
type Urgency = (typeof urgencySortOrder)[number];

const determineUrgency = (alert: Alert): Urgency => {
  if (!alert.due_date) {
    return 'Low';
  }
  const dueInDays = dayjs(alert.due_date).diff(dayjs(), 'day');
  if (dueInDays <= 7) {
    return 'High';
  }
  if (dueInDays <= 30) {
    return 'Medium';
  }
  return 'Low';
};

export default function App() {
  const [clinicPolicies, setClinicPolicies] = useState('');
  const {
    mutate: generateAlerts,
    data,
    isPending,
    error,
  } = useAlerts();

  const alertsWithUrgency = useMemo(() => {
    if (!data?.alerts) return [] as (Alert & { urgency: Urgency })[];
    return data.alerts
      .map((alert) => ({ ...alert, urgency: determineUrgency(alert) }))
      .sort((a, b) =>
        urgencySortOrder.indexOf(a.urgency) - urgencySortOrder.indexOf(b.urgency)
      );
  }, [data]);

  const onSubmit = (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    if (clinicPolicies.trim().length > 0) {
      formData.append('clinic_policies', clinicPolicies);
    }
    generateAlerts(formData);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Medical Record Alert Dashboard</h1>
        <p>Upload a PDF medical record to extract actionable alerts.</p>
      </header>

      <section className="upload-section">
        <FileUpload onSubmit={onSubmit} disabled={isPending} />
        <label className="policies-label">
          Clinic SOPs (optional)
          <textarea
            value={clinicPolicies}
            onChange={(event) => setClinicPolicies(event.target.value)}
            placeholder="Add clinic rules to augment the extraction"
            rows={4}
          />
        </label>
      </section>

      {error && <p className="error">{(error as Error).message}</p>}

      <section className="alerts-section">
        <AlertList
          isLoading={isPending}
          response={data}
          alerts={alertsWithUrgency}
        />
      </section>
    </div>
  );
}

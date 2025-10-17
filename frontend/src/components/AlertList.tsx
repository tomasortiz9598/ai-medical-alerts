import { AlertResponse, Alert } from '../types';
import { AlertCard } from './AlertCard';

type Props = {
  response?: AlertResponse;
  alerts: (Alert & { urgency: 'High' | 'Medium' | 'Low' })[];
  isLoading: boolean;
};

export function AlertList({ response, alerts, isLoading }: Props) {
  if (isLoading) {
    return <p>Processing PDF...</p>;
  }

  if (!response) {
    return <p className="placeholder">Upload a PDF to see alerts.</p>;
  }

  if (alerts.length === 0) {
    return <p className="placeholder">No actionable alerts detected.</p>;
  }

  return (
    <div className="alert-list-container">
      {response?.patient_name && (
        <div className="patient-banner">
          <strong>Patient:</strong> {response.patient_name}
          {response.patient_species ? ` • ${response.patient_species}` : ''}
        </div>
      )}
      <div className="alert-list">
        {alerts.map((alert) => (
          <AlertCard key={alert.title} alert={alert} />
        ))}
      </div>
    </div>
  );
}

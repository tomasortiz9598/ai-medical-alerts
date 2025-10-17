import dayjs from 'dayjs';
import { Alert } from '../types';
import { UrgencyBadge } from './UrgencyBadge';

type Props = {
  alert: Alert & { urgency: 'High' | 'Medium' | 'Low' };
};

const formatAlertType = (value: string) =>
  value
    .toLowerCase()
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

export function AlertCard({ alert }: Props) {
  const dueDateText = alert.due_date
    ? dayjs(alert.due_date).format('MMM D, YYYY')
    : 'Date TBD';

  return (
    <article className={`alert-card urgency-${alert.urgency.toLowerCase()}`}>
      <header>
        <h3>{alert.title}</h3>
        <UrgencyBadge urgency={alert.urgency} />
      </header>
      <p className="meta">
        <strong>Type:</strong> {formatAlertType(alert.alert_type)}
      </p>
      <p className="meta">
        <strong>Due date:</strong> {dueDateText}
      </p>
      <p className="excerpt">{alert.source_excerpt}</p>
      {alert.notes && <p className="notes">Notes: {alert.notes}</p>}
      <p className="confidence">Confidence: {(alert.confidence * 100).toFixed(0)}%</p>
    </article>
  );
}

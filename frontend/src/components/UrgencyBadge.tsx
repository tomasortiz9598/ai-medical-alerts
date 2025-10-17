import clsx from 'clsx';

type Props = {
  urgency: 'High' | 'Medium' | 'Low';
};

export function UrgencyBadge({ urgency }: Props) {
  return <span className={clsx('urgency-badge', urgency.toLowerCase())}>{urgency}</span>;
}

export type AlertType =
  | 'VACCINE_EXPIRATION'
  | 'DENTAL_PROCEDURE'
  | 'ROUTINE_EXAM'
  | 'FOLLOW_UP'
  | 'OTHER';

export interface Alert {
  title: string;
  alert_type: AlertType;
  due_date?: string;
  confidence: number;
  source_excerpt: string;
  notes?: string | null;
}

export interface AlertResponse {
  patient_name?: string | null;
  patient_species?: string | null;
  alerts: Alert[];
}

export interface EventType {
  id: string;
  name: string;
  description: string;
  is_deletable: boolean;
}

export interface EventWithType {
  type: EventType;
  description: string;
  date: string;
  medical_record_filename: string;
}

export interface EventsResponse {
  events?: EventWithType[];
  total?: number;
  page?: number;
  page_size?: number;
}

export interface MedicalRecord {
  id: string;
  filename: string;
  created_time: string;
}

export interface MedicalRecordsResponse {
  medical_records?: MedicalRecord[];
}

export interface FiltersState {
  page: number;
  pageSize: number;
  eventTypeIds: string[];
  medicalRecordIds: string[];
  startDate: string;
  endDate: string;
}

export interface EventsQueryParams {
  page: number;
  page_size: number;
  event_type_ids?: string[];
  medical_record_ids?: string[];
  start_date?: string;
  end_date?: string;
}

import httpClient from "../api/client";
import type { MedicalRecord, MedicalRecordsResponse } from "../types";

export interface MedicalRecordsServiceProps {
  list: () => Promise<MedicalRecord[]>;
  upload: (file: File) => Promise<void>;
  remove: (id: string) => Promise<void>;
}

export function MedicalRecordsService() : MedicalRecordsServiceProps {
  const list = async (): Promise<MedicalRecord[]> => {
    const response = await httpClient.get<MedicalRecordsResponse>("/medical-records");
    return response.data.medical_records ?? [];
  }
  const upload = async (file: File): Promise<void> => {
    const formData = new FormData();
    formData.append("file", file);
    await httpClient.post("/medical-records", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }
  const remove = async (id: string): Promise<void> => {
    await httpClient.delete(`/medical-records/${encodeURIComponent(id)}`);
  }

  return { list, upload, remove };
}

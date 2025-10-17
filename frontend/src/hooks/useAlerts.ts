import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { AlertResponse } from '../types';

const API_URL = '/api/alerts';

export function useAlerts() {
  return useMutation<AlertResponse, Error, FormData>({
    mutationFn: async (formData: FormData) => {
      const response = await axios.post<AlertResponse>(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
  });
}

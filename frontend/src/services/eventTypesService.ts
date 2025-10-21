import httpClient from "../api/client";
import type { EventType } from "../types";

export interface EventTypesServiceProps {
  list: () => Promise<EventType[]>;
  create: (payload: { name: string; description: string }) => Promise<EventType>;
  remove: (id: string) => Promise<void>;
}

export function EventTypesService() : EventTypesServiceProps {

  const list = async (): Promise<EventType[]> => {
    const response = await httpClient.get<EventType[]>("/event-types");
    return response.data;
  }
  const create = async (payload: { name: string; description: string }): Promise<EventType> => {
    const response = await httpClient.post<EventType>("/event-types", payload);
    return response.data;
  }
  const remove = async (id: string): Promise<void> => {
    await httpClient.delete(`/event-types/${encodeURIComponent(id)}`);
  }

  return {
    list,
    create,
    remove,
  };
}

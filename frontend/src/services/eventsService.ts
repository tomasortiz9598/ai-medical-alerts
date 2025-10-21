import httpClient from "../api/client";
import type { EventsQueryParams, EventsResponse } from "../types";

export interface EventsServiceProps {
  list: (params: EventsQueryParams) => Promise<EventsResponse>;
}

export function EventsService() : EventsServiceProps {
  const list = async (params: EventsQueryParams): Promise<EventsResponse> => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === "") return;
      if (Array.isArray(value)) {
        value.forEach((entry) => {
          if (entry !== undefined && entry !== "") {
            query.append(key, String(entry));
          }
        });
      } else {
        query.append(key, String(value));
      }
    });
    const path = `/events${query.size ? `?${query.toString()}` : ""}`;
    const response = await httpClient.get<EventsResponse>(path);
    return response.data;
  }

  return { list };
}

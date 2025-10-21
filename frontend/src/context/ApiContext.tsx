import {
  createContext,
  useMemo,
  type PropsWithChildren,
} from "react";

import { EventsService, EventsServiceProps } from "../services/eventsService";
import { EventTypesService, EventTypesServiceProps } from "../services/eventTypesService";
import { MedicalRecordsService, MedicalRecordsServiceProps } from "../services/medicalRecordsService";


interface ApiContextValue {
  events: EventsServiceProps;
  eventTypes: EventTypesServiceProps;
  medicalRecords: MedicalRecordsServiceProps;
}

export const ApiContext = createContext<ApiContextValue>({
  events: EventsService(),
  eventTypes: EventTypesService(),
  medicalRecords: MedicalRecordsService(),
});

export function ApiProvider({ children }: PropsWithChildren) {
  const value = useMemo<ApiContextValue>(() => {
    const events = EventsService();
    const eventTypes = EventTypesService();
    const medicalRecords = MedicalRecordsService();

    return {
      events,
      eventTypes,
      medicalRecords,
    };
  }, []);

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

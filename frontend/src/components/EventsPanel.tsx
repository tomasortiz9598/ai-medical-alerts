import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Box, Paper, Typography } from "@mui/material";
import { ApiContext } from "../context/ApiContext";
import type { EventWithType, FiltersState } from "../types";
import EventsTable from "./EventsTable";
import { showSnackbar } from "../utils/snackbar";

interface EventsPanelProps {
  filters: FiltersState;
  onFiltersChange: (updater: (prev: FiltersState) => FiltersState) => void;
  busy: boolean;
  refreshKey: number;
}

export default function EventsPanel({
  filters,
  onFiltersChange,
  busy,
  refreshKey,
}: EventsPanelProps) {
  const { events: eventsService } = useContext(ApiContext);
  const [events, setEvents] = useState<EventWithType[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loadingInitial, setLoadingInitial] = useState<boolean>(true);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const {
    page,
    pageSize,
    eventTypeIds,
    medicalRecordIds,
    startDate,
    endDate,
  } = filters;

  useEffect(() => {
    const append = page > 1;
    if (!append) {
      setEvents([]);
    }
    setLoadingInitial(!append);
    setLoadingMore(append);

    let active = true;
    const params = {
      page,
      page_size: pageSize,
      event_type_ids: eventTypeIds,
      medical_record_ids: medicalRecordIds,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };

    eventsService
      .list(params)
      .then((response) => {
        if (!active) return;
        const retrievedEvents = response.events ?? [];
        setEvents((prevEvents) => {
          const nextEvents = append ? [...prevEvents, ...retrievedEvents] : retrievedEvents;
          setTotal((prevTotal) => {
            if (response.total !== undefined) return response.total;
            if (!append) return nextEvents.length;
            return Math.max(prevTotal, nextEvents.length);
          });
          return nextEvents;
        });
      })
      .catch((error) => {
        if (!active) return;
        console.error(error);
        showSnackbar((error as Error).message, "error");
      })
      .finally(() => {
        if (!active) return;
        setLoadingInitial(false);
        setLoadingMore(false);
      });

    return () => {
      active = false;
    };
  }, [
    endDate,
    eventTypeIds,
    eventsService,
    medicalRecordIds,
    page,
    pageSize,
    refreshKey,
    startDate,
  ]);

  const hasMore = useMemo(() => events.length < total, [events.length, total]);
  const loadedCount = events.length;
  const totalCount = Math.max(total, loadedCount);

  const handleLoadMore = useCallback(() => {
    if (!hasMore || loadingInitial || loadingMore || busy) return;
    onFiltersChange((prev) => ({ ...prev, page: prev.page + 1 }));
  }, [busy, hasMore, loadingInitial, loadingMore, onFiltersChange]);

  return (
    <Paper
      elevation={0}
      sx={{
        flex: 1,
        p: 3,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        overflow: "hidden",
        minHeight: 0,
      }}
    >
      <Typography variant="h6" sx={{ fontFamily: "inherit", mb: 2 }} fontWeight={600} gutterBottom>
        Upcoming care reminders
      </Typography>
      <Box sx={{ flexGrow: 1, minHeight: 0, display: "flex", overflow: "hidden" }}>
        <EventsTable
          events={events}
          loadingInitial={loadingInitial || busy}
          loadingMore={loadingMore || busy}
          hasMore={hasMore}
          onLoadMore={handleLoadMore}
          busy={busy}
        />
      </Box>

      <Typography variant="body2" sx={{ fontFamily: "inherit" }} color="text.secondary" textAlign="center" mt={2}>
        Showing {loadedCount} of {totalCount} reminders
      </Typography>
    </Paper>
  );
}

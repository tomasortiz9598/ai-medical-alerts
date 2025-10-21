import { useCallback, useState } from "react";
import { Button, Container, CssBaseline, Grid, ThemeProvider } from "@mui/material";

import EventsPanel from "./components/EventsPanel";
import EventTypesCard from "./components/EventTypesCard";
import MedicalRecordsCard from "./components/MedicalRecordsCard";
import DateFilterPanel from "./components/DateFilterPanel";
import LoadingRecords from "./components/LoadingRecords";
import GlobalSnackbar from "./components/GlobalSnackbar";

import type {
  FiltersState,
} from "./types";
import { theme } from "./theme";

const defaultFilters: FiltersState = {
  page: 1,
  pageSize: 15,
  eventTypeIds: [],
  medicalRecordIds: [],
  startDate: "",
  endDate: "",
};

type FiltersUpdater = Partial<FiltersState> | ((prev: FiltersState) => FiltersState);

export default function App() {
  const [filters, setFilters] = useState<FiltersState>({ ...defaultFilters });
  const [pendingCount, setPendingCount] = useState(0);
  const [overlayVisible, setOverlayVisible] = useState(false);
  const [eventsRefreshKey, setEventsRefreshKey] = useState(0);

  const updateFilters = useCallback(
    (updater: FiltersUpdater) => {
      setFilters((prev) => {
        if (typeof updater === "function") {
          return (updater as (current: FiltersState) => FiltersState)(prev);
        }
        return { ...prev, ...updater };
      });
    },
    []
  );

  const handleResetFilters = useCallback(() => {
    setFilters(() => ({ ...defaultFilters }));
  }, []);

  const beginPending = useCallback(
    (options?: { showOverlay?: boolean }) => {
      setPendingCount((prev) => prev + 1);
      if (options?.showOverlay) {
        setOverlayVisible(true);
      }
    },
    []
  );

  const endPending = useCallback(() => {
    setPendingCount((prev) => {
      const next = prev > 0 ? prev - 1 : 0;
      if (next === 0) {
        setOverlayVisible(false);
      }
      return next;
    });
  }, []);

  const busy = pendingCount > 0;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {overlayVisible && <LoadingRecords />}
      <Container
        maxWidth="xl"
        sx={{ py: 4, height: "100vh", display: "flex", flexDirection: "column", overflow: "hidden" }}
      >
        <Grid
          container
          spacing={3}
          alignItems="stretch"
          sx={{ flexGrow: 1, overflow: "hidden", minHeight: 0 }}
        >
          <Grid
            item
            xs={12}
            md={4}
            lg={3}
            display="flex"
            flexDirection="column"
            gap={3}
            sx={{ overflow: "auto", pr: { md: 1 }, minHeight: 0, height: "100%" }}
          >
            <MedicalRecordsCard
              selectedMedicalRecordIds={filters.medicalRecordIds}
              onFiltersChange={updateFilters}
              onResetFilters={handleResetFilters}
              onPendingStart={beginPending}
              onPendingEnd={endPending}
              disabled={busy}
              onAfterChange={() => {
                updateFilters((prev) => ({ ...prev, page: 1 }));
                setEventsRefreshKey((prev) => prev + 1);
              }}
            />
            <EventTypesCard
              selectedEventTypeIds={filters.eventTypeIds}
              onFiltersChange={updateFilters}
              onPendingStart={beginPending}
              onPendingEnd={endPending}
              disabled={busy}
            />
            <DateFilterPanel
              startDate={filters.startDate}
              endDate={filters.endDate}
              onChange={(partial) =>
                updateFilters((prev) => ({
                  ...prev,
                  ...partial,
                  page: 1,
                }))
              }
              disabled={busy}
            />
            <Button variant="outlined" onClick={handleResetFilters} disabled={busy}>
              Clear filters
            </Button>
          </Grid>

          <Grid
            item
            xs={12}
            md={8}
            lg={9}
            sx={{ display: "flex", flexDirection: "column", overflow: "hidden", minHeight: 0, height: "100%" }}
          >
            <EventsPanel
              filters={filters}
              onFiltersChange={updateFilters}
              busy={busy}
              refreshKey={eventsRefreshKey}
            />
          </Grid>
        </Grid>
      </Container>
      <GlobalSnackbar />
    </ThemeProvider>
  );
}

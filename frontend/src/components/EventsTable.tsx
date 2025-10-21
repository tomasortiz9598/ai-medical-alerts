import {
  Box,
  Button,
  CircularProgress,
  Skeleton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
} from "@mui/material";
import { useMemo } from "react";
import type { EventWithType } from "../types";
import { format } from "../utils/dates";

interface EventsTableProps {
  events: EventWithType[];
  loadingInitial: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  onLoadMore: () => void;
  busy: boolean;
}

export default function EventsTable({
  events,
  loadingInitial,
  loadingMore,
  hasMore,
  onLoadMore,
  busy,
}: EventsTableProps) {
  const skeletonRows = Array.from({ length: 5 });
  const animationKey = useMemo(() => Math.random().toString(36).slice(2, 8), [events, busy]);

  if (loadingInitial) {
    return (
      <TableContainer
        component={Paper}
        elevation={0}
        sx={{ flex: 1, overflowY: "auto" }}
      >
        <Table
          size="medium"
          stickyHeader
          sx={{
            minHeight: 0,
            "& .MuiTableCell-root": {
              borderBottom: "none",
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Patient file</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {skeletonRows.map((_, index) => (
              <TableRow key={`skeleton-${index}`}>
                <TableCell sx={{ width: "18%" }}>
                  <Skeleton variant="text" />
                </TableCell>
                <TableCell>
                  <Skeleton variant="text" />
                </TableCell>
                <TableCell sx={{ width: "25%" }}>
                  <Skeleton variant="text" />
                </TableCell>
                <TableCell sx={{ width: "18%" }}>
                  <Skeleton variant="rectangular" height={24} width={96} sx={{ borderRadius: 12 }} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", flex: 1 }}>
      <TableContainer
        component={Paper}
        elevation={0}
        sx={{ flex: 1, overflowY: "auto" }}
      >
        <Table
          size="medium"
          stickyHeader
          sx={{
            minHeight: 0,
            "& .MuiTableCell-root": {
              borderBottom: "none",
            },
            "& tbody tr": {
              transition: "background-color 150ms ease",
            },
            "& tbody tr:not(.events-table-load-more):hover": {
              backgroundColor: (theme) =>
                theme.palette.mode === "light"
                  ? "rgba(25, 118, 210, 0.06)"
                  : "rgba(144, 202, 249, 0.12)",
            },
            "& tbody tr:not(.events-table-load-more):focus-visible": {
              outline: (theme) => `2px solid ${theme.palette.primary.light}`,
              outlineOffset: -2,
            },
          }}
        >
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Patient file</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {events.map((event, index) => (
              <TableRow
                key={`${event.type.id}-${index}-${event.date}`}
                tabIndex={0}
                sx={{
                  "&": {
                    animation: `${animationKey}-fade-in 420ms ease ${index * 70}ms both`,
                  },
                }}
              >
                <TableCell sx={{ width: "18%" }}>{format(event.date)}</TableCell>
                <TableCell>{event.description}</TableCell>
                <TableCell sx={{ width: "25%" }}>
                  {event.medical_record_filename || "—"}
                </TableCell>
                <TableCell sx={{ width: "18%" }}>
                  <Chip
                    label={event.type.name.replace(/_/g, " ")}
                    color="primary"
                    variant="outlined"
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
            {!events.length && !loadingMore && (
              <TableRow>
                <TableCell colSpan={4} sx={{ textAlign: "center" }}>
                  <Typography variant="body2" sx={{ fontFamily: "inherit", py: 4 }} color="text.secondary">
                    No reminders found. Adjust filters or upload a patient file.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {loadingMore && (
              <TableRow>
                <TableCell colSpan={4} sx={{ textAlign: "center" }}>
                  <Box py={2} display="flex" justifyContent="center">
                    <CircularProgress size={24} />
                  </Box>
                </TableCell>
              </TableRow>
            )}
            {hasMore && (
              <TableRow className="events-table-load-more">
                <TableCell colSpan={4} sx={{ textAlign: "center", py: 2 }}>
                  <Button variant="outlined" onClick={onLoadMore} disabled={loadingMore || busy}>
                    Show more
                  </Button>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <style>{`
        @keyframes ${animationKey}-fade-in {
          0% {
            opacity: 0;
            transform: translateY(12px);
          }
          60% {
            opacity: 1;
            transform: translateY(-2px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </Box>
  );
}

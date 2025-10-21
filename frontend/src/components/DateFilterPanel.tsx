import { useCallback, useMemo } from "react";
import { IconButton, InputAdornment, Stack, TextField, Typography } from "@mui/material";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DateRangePicker, type DateRange } from "../utils/DateRangePicker";
import dayjs, { Dayjs } from "dayjs";

type DateFilterPanelProps = {
  startDate: string;
  endDate: string;
  onChange: (values: Partial<{ startDate: string; endDate: string }>) => void;
  disabled?: boolean;
};

export default function DateFilterPanel({
  startDate,
  endDate,
  onChange,
  disabled = false,
}: DateFilterPanelProps) {
  const value = useMemo<DateRange<Dayjs>>(
    () => [startDate ? dayjs(startDate) : null, endDate ? dayjs(endDate) : null],
    [startDate, endDate]
  );
  const minDate = useMemo(() => dayjs().startOf("day"), []);


  const handleChange = useCallback(
    (range: DateRange<Dayjs>) => {
      const [start, end] = range;
      if (disabled) return;
      onChange({
        startDate: start ? start.format("YYYY-MM-DD") : "",
        endDate: end ? end.format("YYYY-MM-DD") : "",
      });
    },
    [disabled, onChange]
  );

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DateRangePicker
        disabled={disabled}
        value={value}
        minDate={minDate}
        onChange={handleChange}
        renderInput={(startProps, endProps, { openStart, openEnd }) => (
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ width: "100%" }}>
            <TextField
              {...startProps}
              size="small"
              fullWidth
              label="From"
              disabled={disabled}
              inputProps={{
                ...startProps.inputProps,
                placeholder: "MM/DD/YYYY",
              }}
              InputProps={{
                ...startProps.InputProps,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      edge="end"
                      onClick={(event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        if (disabled) return;
                        openStart();
                      }}
                      disabled={disabled}
                    >
                      <CalendarTodayIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ flex: 1 }}
            />
            <Typography
              component="span"
              variant="body2"
              color="text.secondary"
              sx={{ px: 0.5 }}
            >
              /
            </Typography>
            <TextField
              {...endProps}
              size="small"
              fullWidth
              label="To"
              disabled={disabled}
              inputProps={{
                ...endProps.inputProps,
                placeholder: "MM/DD/YYYY",
              }}
              InputProps={{
                ...endProps.InputProps,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      edge="end"
                      onClick={(event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        if (disabled) return;
                        openEnd();
                      }}
                      disabled={disabled}
                    >
                      <CalendarTodayIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ flex: 1 }}
            />
          </Stack>
        )}
      />
    </LocalizationProvider>
  );
}

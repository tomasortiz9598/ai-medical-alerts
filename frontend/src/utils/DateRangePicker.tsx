import { forwardRef, useCallback, useMemo, useRef, useState } from "react";
import type { FocusEvent, KeyboardEvent } from "react";
import { alpha } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Popover from "@mui/material/Popover";
import type { TextFieldProps } from "@mui/material/TextField";
import { DateCalendar } from "@mui/x-date-pickers/DateCalendar";
import type { PickersDayProps } from "@mui/x-date-pickers/PickersDay";
import { PickersDay } from "@mui/x-date-pickers/PickersDay";
import type { Dayjs } from "dayjs";

export type DateRange<TDate> = [TDate | null, TDate | null];

type FieldType = "start" | "end";

interface DateRangePickerProps {
  value: DateRange<Dayjs>;
  onChange: (value: DateRange<Dayjs>) => void;
  renderInput: (
    startProps: TextFieldProps,
    endProps: TextFieldProps,
    pickerActions: { openStart: () => void; openEnd: () => void }
  ) => React.ReactNode;
  disabled?: boolean;
  minDate?: Dayjs;
  maxDate?: Dayjs;
  shouldDisableDate?: (date: Dayjs) => boolean;
  calendars?: number;
  reduceAnimations?: boolean;
}

interface RangePickerDayProps extends PickersDayProps<Dayjs> {
  rangeStart: Dayjs | null;
  rangeEnd: Dayjs | null;
}

const RangePickerDay = forwardRef<HTMLButtonElement, RangePickerDayProps>(
  function RangePickerDay(props, ref) {
    const { day, outsideCurrentMonth, rangeStart, rangeEnd, ...other } = props;
    const isStart = Boolean(rangeStart && day.isSame(rangeStart, "day"));
    const isEnd = Boolean(rangeEnd && day.isSame(rangeEnd, "day"));
    const isBetween =
      Boolean(rangeStart && rangeEnd) &&
      !isStart &&
      !isEnd &&
      day.isAfter(rangeStart!, "day") &&
      day.isBefore(rangeEnd!, "day");

    return (
      <PickersDay
        {...other}
        ref={ref}
        day={day}
        outsideCurrentMonth={outsideCurrentMonth}
        selected={isStart || isEnd}
        sx={(theme) => {
          const hoverBackground =
            theme.palette.mode === "light"
              ? theme.palette.primary.main
              : theme.palette.primary.light;

          const selectedStyles = {
            backgroundColor: theme.palette.primary.main,
            color: theme.palette.primary.contrastText,
            "&:hover, &:focus": {
              backgroundColor: hoverBackground,
            },
          };

          const betweenStyles = isBetween
            ? {
                borderRadius: 0,
                backgroundColor: alpha(
                  theme.palette.primary.main,
                  theme.palette.mode === "light" ? 0.2 : 0.4
                ),
                color: theme.palette.text.primary,
                "&:hover, &:focus": {
                  backgroundColor: alpha(
                    theme.palette.primary.main,
                    theme.palette.mode === "light" ? 0.3 : 0.5
                  ),
                },
              }
            : {};

          const startStyles =
            isStart && !isEnd
              ? {
                  ...selectedStyles,
                  borderRadius: "50% 0 0 50%",
                }
              : {};

          const endStyles =
            isEnd && !isStart
              ? {
                  ...selectedStyles,
                  borderRadius: "0 50% 50% 0",
                }
              : {};

          const singleDayStyles =
            isStart && isEnd
              ? {
                  ...selectedStyles,
                  borderRadius: "50%",
                }
              : {};

          return {
            ...betweenStyles,
            ...startStyles,
            ...endStyles,
            ...singleDayStyles,
          };
        }}
      />
    );
  }
);

export function DateRangePicker({
  value,
  onChange,
  renderInput,
  disabled = false,
  minDate,
  maxDate,
  shouldDisableDate,
}: DateRangePickerProps) {
  const [start, end] = value;
  const [openField, setOpenField] = useState<FieldType | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  const startInputRef = useRef<HTMLInputElement | null>(null);
  const endInputRef = useRef<HTMLInputElement | null>(null);

  const normalize = useCallback((date: Dayjs | null) => date?.startOf("day") ?? null, []);

  const openPicker = useCallback(
    (field: FieldType) => {
      if (disabled) return;
      const element = field === "start" ? startInputRef.current : endInputRef.current;
      if (!element) return;
      setAnchorEl(element);
      setOpenField(field);
    },
    [disabled]
  );

  const closePicker = useCallback(() => {
    if (anchorEl instanceof HTMLElement) {
      anchorEl.blur();
    }
    setOpenField(null);
    setAnchorEl(null);
  }, [anchorEl]);

  const handleInputFocus = useCallback(
    (field: FieldType) => (event: FocusEvent<HTMLInputElement>) => {
      event.preventDefault();
      openPicker(field);
    },
    [openPicker]
  );

  const handleInputClick = useCallback(
    (field: FieldType) => () => {
      openPicker(field);
    },
    [openPicker]
  );

  const handleInputKeyDown = useCallback(
    (field: FieldType) => (event: KeyboardEvent<HTMLInputElement>) => {
      if (["Enter", " ", "ArrowDown"].includes(event.key)) {
        event.preventDefault();
        openPicker(field);
      }
      if (event.key === "Escape") {
        event.preventDefault();
        closePicker();
      }
    },
    [closePicker, openPicker]
  );

  const isDateDisabled = useCallback(
    (candidate: Dayjs) => {
      const day = normalize(candidate);
      if (!day) return false;
      if (minDate && day.isBefore(normalize(minDate)!, "day")) return true;
      if (maxDate && day.isAfter(normalize(maxDate)!, "day")) return true;
      if (shouldDisableDate?.(day)) return true;
      if (openField === "end" && start && day.isBefore(normalize(start)!, "day")) return true;
      if (openField === "start" && end && day.isAfter(normalize(end)!, "day")) return true;
      return false;
    },
    [end, maxDate, minDate, normalize, openField, shouldDisableDate, start]
  );

  const handleCalendarChange = useCallback(
    (newValue: Dayjs | null) => {
      if (!newValue) return;
      if (isDateDisabled(newValue)) return;

      const normalizedValue = normalize(newValue);
      if (!normalizedValue) return;

      let nextStart = start ? normalize(start) : null;
      let nextEnd = end ? normalize(end) : null;
      let nextField: FieldType | null = null;

      if (openField === "start") {
        nextStart = normalizedValue;
        if (nextEnd && nextEnd.isBefore(nextStart, "day")) {
          nextEnd = nextStart;
        }
        nextField = "end";
      } else if (openField === "end") {
        nextEnd = normalizedValue;
        if (nextStart && nextEnd.isBefore(nextStart, "day")) {
          nextStart = normalizedValue;
        }
      }

      onChange([nextStart, nextEnd]);

      if (nextField) {
        openPicker(nextField);
      } else {
        closePicker();
      }
    },
    [closePicker, end, isDateDisabled, normalize, onChange, openPicker, openField, start]
  );

  const startLabel = useMemo(() => (start ? start.format("MM/DD/YYYY") : ""), [start]);
  const endLabel = useMemo(() => (end ? end.format("MM/DD/YYYY") : ""), [end]);

  const startFieldProps: TextFieldProps = {
    value: startLabel,
    onClick: handleInputClick("start"),
    onFocus: handleInputFocus("start"),
    onKeyDown: handleInputKeyDown("start"),
    inputProps: {
      readOnly: true,
      value: startLabel,
    },
    InputProps: {
      readOnly: true,
    },
    disabled,
    inputRef: (instance) => {
      startInputRef.current = instance;
    },
  };

  const endFieldProps: TextFieldProps = {
    value: endLabel,
    onClick: handleInputClick("end"),
    onFocus: handleInputFocus("end"),
    onKeyDown: handleInputKeyDown("end"),
    inputProps: {
      readOnly: true,
      value: endLabel,
    },
    InputProps: {
      readOnly: true,
    },
    disabled,
    inputRef: (instance) => {
      endInputRef.current = instance;
    },
  };

  const displayedMonth = useMemo(() => {
    if (openField === "start" && start) return start;
    if (openField === "end" && end) return end;
    return start ?? end ?? null;
  }, [end, openField, start]);

  const normalizedStart = useMemo(() => (start ? normalize(start) : null), [normalize, start]);
  const normalizedEnd = useMemo(() => (end ? normalize(end) : null), [end, normalize]);

  return (
    <>
      {renderInput(startFieldProps, endFieldProps, {
        openStart: () => openPicker("start"),
        openEnd: () => openPicker("end"),
      })}
      <Popover
        open={Boolean(openField)}
        anchorEl={anchorEl}
        onClose={closePicker}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
        transformOrigin={{ vertical: "top", horizontal: "left" }}
        disableAutoFocus
        disableEnforceFocus
        disableRestoreFocus
      >
        <Box sx={{ p: 1 }}>
          <DateCalendar
            value={
              openField === "start"
                ? start ?? null
                : openField === "end"
                  ? end ?? null
                  : null
            }
            defaultcalendarmonth={displayedMonth ?? undefined}
            onChange={handleCalendarChange}
            shouldDisableDate={isDateDisabled}
            slots={{ day: RangePickerDay }}
            slotProps={{
              day: {
                rangeStart: normalizedStart,
                rangeEnd: normalizedEnd,
              } as Partial<RangePickerDayProps>,
            }}
            disabled={disabled}
          />
        </Box>
      </Popover>
    </>
  );
}

export default DateRangePicker;

import { useCallback, useEffect, useState } from "react";
import { Alert, Snackbar } from "@mui/material";
import {
  registerSnackbarListener,
  unregisterSnackbarListener,
  type SnackbarPayload,
} from "../utils/snackbar";

interface SnackbarState extends SnackbarPayload {
  open: boolean;
  key: number;
}

const AUTO_HIDE_DURATION = 1000;

export default function GlobalSnackbar() {
  const [snackbar, setSnackbar] = useState<SnackbarState | null>(null);

  const handleClose = useCallback(() => {
    setSnackbar((prev) => (prev ? { ...prev, open: false } : null));
  }, []);

  const handleExited = useCallback(() => {
    setSnackbar((prev) => (prev && !prev.open ? null : prev));
  }, []);

  useEffect(() => {
    const listener = (payload: SnackbarPayload) => {
      setSnackbar({
        message: payload.message,
        severity: payload.severity ?? "success",
        open: true,
        key: Date.now(),
      });
    };

    registerSnackbarListener(listener);
    return () => unregisterSnackbarListener(listener);
  }, []);

  return (
    <Snackbar
      key={snackbar?.key}
      open={snackbar?.open ?? false}
      autoHideDuration={AUTO_HIDE_DURATION}
      onClose={handleClose}
      TransitionProps={{ onExited: handleExited }}
      anchorOrigin={{ vertical: "top", horizontal: "right" }}
    >
      <Alert
        onClose={handleClose}
        severity={snackbar?.severity ?? "success"}
        variant="filled"
        sx={{ width: "100%" }}
      >
        {snackbar?.message ?? ""}
      </Alert>
    </Snackbar>
  );
}

export type SnackbarSeverity = "success" | "error" | "info" | "warning";

export interface SnackbarPayload {
  message: string;
  severity?: SnackbarSeverity;
}

type SnackbarListener = (payload: SnackbarPayload) => void;

let listener: SnackbarListener | null = null;

export function registerSnackbarListener(fn: SnackbarListener) {
  listener = fn;
}

export function unregisterSnackbarListener(fn: SnackbarListener) {
  if (listener === fn) {
    listener = null;
  }
}

export function showSnackbar(
  message: string,
  severity: SnackbarSeverity = "success"
) {
  listener?.({ message, severity });
}

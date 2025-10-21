export function format(isoDateString?: string) {
  if (!isoDateString) return "";
  const date = new Date(isoDateString);
  if (Number.isNaN(date.getTime())) return isoDateString;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

import { ReadingStatus } from "../services/api";

export const READING_STATUS_OPTIONS: { value: ReadingStatus; label: string }[] =
  [
    { value: "want_to_read", label: "Want to read" },
    { value: "reading", label: "Reading" },
    { value: "finished", label: "Finished" },
    { value: "abandoned", label: "Abandoned" },
  ];

const LABELS: Record<ReadingStatus, string> = {
  want_to_read: "Want to read",
  reading: "Reading",
  finished: "Finished",
  abandoned: "Abandoned",
};

export function StatusBadge({ status }: { status: ReadingStatus }) {
  return <span className={`status-badge status-${status}`}>{LABELS[status]}</span>;
}

type Props = {
  current: number | null;
  total: number | null;
  label?: string;
};

export function ProgressBar({ current, total, label }: Props) {
  if (total == null || total <= 0) {
    if (current == null) return null;
    return (
      <span className="progress-text">
        Page <span className="tabular">{current}</span>
      </span>
    );
  }

  const value = Math.min(Math.max(current ?? 0, 0), total);
  const percent = Math.round((value / total) * 100);

  return (
    <div className="progress">
      <div
        className="progress-track"
        role="progressbar"
        aria-label={label ?? "Reading progress"}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={value}
        aria-valuetext={`${value} of ${total} pages, ${percent}%`}
      >
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <span className="progress-text">
        <span className="tabular">{value}</span> /{" "}
        <span className="tabular">{total}</span> pages
        <span className="progress-percent tabular"> · {percent}%</span>
      </span>
    </div>
  );
}
